import math

import pydeck as pdk
import streamlit as st
from pyproj import Transformer

EARTH_RADIUS_KM = 6371.0088
MIN_VERTEX_COUNT = 12
MAX_VERTEX_COUNT = 10_000


def create_circle(
    latitude: float,
    longitude: float,
    radius_km: float,
    vertex_spacing_m: float,
) -> tuple[dict, int, float]:
    if not -90 <= latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90 degrees.")
    if not -180 <= longitude <= 180:
        raise ValueError("Longitude must be between -180 and 180 degrees.")
    if not math.isfinite(radius_km) or radius_km <= 0:
        raise ValueError("Radius must be a positive, finite number.")
    if radius_km >= math.pi * EARTH_RADIUS_KM:
        raise ValueError("Radius must be less than half the Earth's circumference.")
    if not math.isfinite(vertex_spacing_m) or vertex_spacing_m <= 0:
        raise ValueError("Vertex spacing must be a positive, finite number.")

    angular_distance = radius_km / EARTH_RADIUS_KM
    circumference_m = (
        2 * math.pi * EARTH_RADIUS_KM * 1000 * math.sin(angular_distance)
    )
    vertex_count = max(MIN_VERTEX_COUNT, math.ceil(circumference_m / vertex_spacing_m))
    if vertex_count > MAX_VERTEX_COUNT:
        raise ValueError(
            f"This spacing would create {vertex_count:,} vertices. "
            f"Increase the spacing so the circle has no more than {MAX_VERTEX_COUNT:,} vertices."
        )

    center_lat = math.radians(latitude)
    center_lon = math.radians(longitude)
    coordinates = []

    for index in range(vertex_count):
        bearing = 2 * math.pi * index / vertex_count
        vertex_lat = math.asin(
            math.sin(center_lat) * math.cos(angular_distance)
            + math.cos(center_lat) * math.sin(angular_distance) * math.cos(bearing)
        )
        vertex_lon = center_lon + math.atan2(
            math.sin(bearing) * math.sin(angular_distance) * math.cos(center_lat),
            math.cos(angular_distance) - math.sin(center_lat) * math.sin(vertex_lat),
        )
        longitude_degrees = (math.degrees(vertex_lon) + 180) % 360 - 180
        coordinates.append([longitude_degrees, math.degrees(vertex_lat)])

    coordinates.append(coordinates[0])
    feature = {
        "type": "Feature",
        "properties": {
            "center": [longitude, latitude],
            "radius_km": radius_km,
            "vertex_count": vertex_count,
            "vertex_spacing_m": circumference_m / vertex_count,
        },
        "geometry": {"type": "Polygon", "coordinates": [coordinates]},
    }
    return feature, vertex_count, circumference_m / vertex_count


def create_output_vertices(
    feature: dict,
    coordinate_system: str,
    zone: int | None = None,
    hemisphere: str | None = None,
) -> list[dict]:
    transformer = None
    if coordinate_system == "UTM":
        if zone is None or hemisphere not in {"N", "S"}:
            raise ValueError("Select a valid UTM zone and hemisphere.")
        epsg = (32600 if hemisphere == "N" else 32700) + zone
        transformer = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)

    ring = feature["geometry"]["coordinates"][0][:-1]
    vertices = []

    for index, (vertex_longitude, vertex_latitude) in enumerate(ring, start=1):
        if coordinate_system == "UTM":
            if not -80 <= vertex_latitude <= 84:
                raise ValueError("UTM is valid between 80°S and 84°N.")
            x, y = transformer.transform(vertex_longitude, vertex_latitude)
        else:
            x, y = vertex_longitude, vertex_latitude
        vertices.append(
            {
                "vertex": index,
                "longitude": vertex_longitude,
                "latitude": vertex_latitude,
                "x": x,
                "y": y,
                "z": 0,
            }
        )

    return vertices


def format_xyz(vertices: list[dict], coordinate_system: str) -> str:
    precision = 3 if coordinate_system == "UTM" else 8
    return "".join(
        f"{vertex['x']:.{precision}f} {vertex['y']:.{precision}f} 0\n"
        for vertex in vertices
    )


def main() -> None:
    st.set_page_config(page_title="Circle Generator", page_icon="⭕", layout="centered")
    st.title("Circle Vertex Generator")
    st.write(
        "Create a circle and download its vertices as X, Y, Z rows in a `.xyz` file."
    )

    coordinate_system = st.selectbox(
        "Coordinate system",
        ["Latitude/longitude (decimal degrees)", "UTM (meters)"],
    )

    with st.form("circle_inputs"):
        st.subheader("Circle settings")
        if coordinate_system == "Latitude/longitude (decimal degrees)":
            latitude = st.number_input(
                "Center latitude (degrees)",
                min_value=-90.0,
                max_value=90.0,
                value=0.0,
                step=0.1,
            )
            longitude = st.number_input(
                "Center longitude (degrees)",
                min_value=-180.0,
                max_value=180.0,
                value=0.0,
                step=0.1,
            )
            zone = None
            hemisphere = None
        else:
            x_input = st.number_input(
                "Center X / easting (m)",
                min_value=100_000.0,
                max_value=900_000.0,
                value=500_000.0,
                step=100.0,
            )
            y_input = st.number_input(
                "Center Y / northing (m)",
                min_value=0.0,
                max_value=10_000_000.0,
                value=5_000_000.0,
                step=100.0,
            )
            zone_col, hemisphere_col = st.columns(2)
            zone = zone_col.number_input(
                "UTM zone", min_value=1, max_value=60, value=31, step=1
            )
            hemisphere = hemisphere_col.selectbox("Hemisphere", ["N", "S"])
            latitude = longitude = None

        radius_km = st.number_input(
            "Radius (km)", min_value=0.001, value=1.0, step=0.1, format="%.3f"
        )
        vertex_spacing_m = st.number_input(
            "Maximum vertex spacing along the edge (m)",
            min_value=0.1,
            value=100.0,
            step=10.0,
        )
        st.caption("The circle uses at least 12 evenly spaced vertices for a smooth outline.")
        submitted = st.form_submit_button("Generate circle", type="primary")

    if not submitted:
        return

    try:
        if coordinate_system == "UTM (meters)":
            epsg = (32600 if hemisphere == "N" else 32700) + zone
            to_geographic = Transformer.from_crs(
                f"EPSG:{epsg}", "EPSG:4326", always_xy=True
            )
            longitude, latitude = to_geographic.transform(x_input, y_input)
            if not math.isfinite(latitude) or not math.isfinite(longitude):
                raise ValueError("The entered UTM coordinate is invalid.")
            if not -80 <= latitude <= 84:
                raise ValueError("UTM is valid between 80°S and 84°N.")

        feature, vertex_count, actual_spacing_m = create_circle(
            latitude, longitude, radius_km, vertex_spacing_m
        )
        vertices = create_output_vertices(
            feature,
            "UTM" if coordinate_system == "UTM (meters)" else "Geographic",
            zone,
            hemisphere,
        )
    except ValueError as error:
        st.error(str(error))
        return

    if coordinate_system == "UTM (meters)":
        output_x_label, output_y_label = "Easting", "Northing"
        output_crs = f"UTM zone {zone}{hemisphere} (EPSG:{epsg})"
    else:
        output_x_label, output_y_label = "Longitude", "Latitude"
        output_crs = "decimal degrees"

    vertex_data = [
        {
            **vertex,
            "label": str(vertex["vertex"]),
            "position": [vertex["longitude"], vertex["latitude"]],
        }
        for vertex in vertices
    ]

    st.subheader("Circle preview")
    st.pydeck_chart(
        pdk.Deck(
            layers=[
                pdk.Layer(
                    "GeoJsonLayer",
                    data=feature,
                    get_fill_color=[40, 130, 220, 70],
                    get_line_color=[20, 90, 170, 230],
                    get_line_width=2,
                    line_width_min_pixels=2,
                    pickable=True,
                ),
                pdk.Layer(
                    "ScatterplotLayer",
                    data=vertex_data,
                    get_position="position",
                    get_radius=25,
                    get_fill_color=[220, 45, 45, 230],
                    get_line_color=[255, 255, 255, 255],
                    line_width_min_pixels=1,
                    stroked=True,
                    pickable=True,
                ),
                pdk.Layer(
                    "TextLayer",
                    data=vertex_data,
                    get_position="position",
                    get_text="label",
                    get_size=12,
                    get_color=[20, 20, 20, 255],
                    get_pixel_offset=[0, -12],
                    get_alignment_baseline="bottom",
                    pickable=True,
                ),
            ],
            initial_view_state=pdk.ViewState(
                latitude=latitude,
                longitude=longitude,
                zoom=max(1, min(15, 15 - math.log2(radius_km))),
                pitch=0,
            ),
            tooltip={
                "html": (
                    "<b>Vertex {vertex}</b><br/>"
                    f"{output_x_label}: {{x}}<br/>"
                    f"{output_y_label}: {{y}}<br/>Z: {{z}}"
                )
            },
        ),
        width="stretch",
    )

    st.caption(
        f"{vertex_count:,} vertices; actual edge spacing is approximately "
        f"{actual_spacing_m:,.2f} m. Output coordinates: {output_crs}."
    )
    table_rows = [
        {
            "Vertex": vertex["vertex"],
            f"X ({output_x_label})": vertex["x"],
            f"Y ({output_y_label})": vertex["y"],
            "Z": vertex["z"],
        }
        for vertex in vertices
    ]
    st.dataframe(table_rows, hide_index=True, width="stretch")

    st.download_button(
        "Download .xyz",
        data=format_xyz(
            vertices, "UTM" if coordinate_system == "UTM (meters)" else "Geographic"
        ),
        file_name="circle.xyz",
        mime="text/plain",
    )


if __name__ == "__main__":
    main()
