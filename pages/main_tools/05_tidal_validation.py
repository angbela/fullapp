import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Model vs Measurement Validation",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Model vs Measurement Validation")

st.caption(
    "Paste measurement and model data below. "
    "Model values will be linearly interpolated to the "
    "measurement timestamps before calculating RMSE."
)


# ============================================================
# DATA PARSER
# ============================================================

def parse_pasted_data(text):
    """
    Parse data in the format:

    2/12/1993 00:00    -0.344375
    2/12/1993 00:15    -0.349063
    2/12/1993 00:30    -0.348588

    The separator can be TAB or multiple spaces.
    """

    lines = text.strip().splitlines()

    records = []

    for line_number, line in enumerate(lines, start=1):

        line = line.strip()

        if not line:
            continue

        # ----------------------------------------------------
        # First try TAB separation
        # ----------------------------------------------------

        if "\t" in line:

            parts = line.split("\t")

            if len(parts) >= 2:

                timestamp = parts[0].strip()
                value = parts[-1].strip()

            else:
                continue

        else:

            # ------------------------------------------------
            # Handle multiple spaces
            #
            # Timestamp itself contains one space:
            # 2/12/1993 00:00
            #
            # Therefore we split on 2+ spaces.
            # ------------------------------------------------

            parts = line.split()

            if len(parts) < 3:
                continue

            timestamp = parts[0] + " " + parts[1]
            value = parts[2]

        # ----------------------------------------------------
        # Convert
        # ----------------------------------------------------

        try:

            timestamp = pd.to_datetime(
                timestamp,
                dayfirst=True,
                errors="raise"
            )

            value = float(value)

            records.append(
                {
                    "Time": timestamp,
                    "Value": value
                }
            )

        except Exception:

            st.warning(
                f"Could not parse line {line_number}: `{line}`"
            )

    if not records:

        return pd.DataFrame(
            columns=["Time", "Value"]
        )

    df = pd.DataFrame(records)

    df = df.sort_values("Time")

    # Remove duplicate timestamps
    df = df.drop_duplicates(
        subset="Time",
        keep="first"
    )

    return df


# ============================================================
# INTERPOLATION
# ============================================================

def interpolate_model(measurement, model):

    # Measurement timestamps are the reference
    measurement_times = measurement["Time"]

    # Only keep measurement points inside model range
    valid_mask = (
        (measurement_times >= model["Time"].min()) &
        (measurement_times <= model["Time"].max())
    )

    aligned = measurement.loc[
        valid_mask
    ].copy()

    if aligned.empty:
        return aligned

    # Convert timestamps to integer nanoseconds
    model_x = (
        model["Time"]
        .astype("int64")
        .to_numpy()
    )

    model_y = (
        model["Value"]
        .to_numpy()
    )

    measurement_x = (
        aligned["Time"]
        .astype("int64")
        .to_numpy()
    )

    # Linear interpolation
    aligned["Model"] = np.interp(
        measurement_x,
        model_x,
        model_y
    )

    aligned = aligned.rename(
        columns={
            "Value": "Measurement"
        }
    )

    # Error
    aligned["Error"] = (
        aligned["Model"]
        - aligned["Measurement"]
    )

    aligned["Absolute_Error"] = (
        aligned["Error"].abs()
    )

    aligned["Squared_Error"] = (
        aligned["Error"] ** 2
    )

    return aligned


# ============================================================
# INPUT
# ============================================================

st.header("1. Paste Data")

col1, col2 = st.columns(2)


with col1:

    st.subheader("📍 Measurement")

    measurement_text = st.text_area(
        "Paste measurement data",
        height=350,
        placeholder=(
            "2/12/1993 00:00\t-0.344375\n"
            "2/12/1993 00:15\t-0.349063\n"
            "2/12/1993 00:30\t-0.348588\n"
            "2/12/1993 00:45\t-0.397647"
        ),
        key="measurement_text"
    )


with col2:

    st.subheader("🖥️ Model")

    model_text = st.text_area(
        "Paste model data",
        height=350,
        placeholder=(
            "2/12/1993 00:00\t-0.370000\n"
            "2/12/1993 00:02\t-0.370000\n"
            "2/12/1993 00:04\t-0.370000\n"
            "2/12/1993 00:06\t-0.370000"
        ),
        key="model_text"
    )


# ============================================================
# RUN BUTTON
# ============================================================

run_validation = st.button(
    "🚀 Run Validation",
    type="primary",
    use_container_width=True
)


if not run_validation:

    st.info(
        "Paste both datasets and click **Run Validation**."
    )

    st.markdown(
        """
        ### Accepted format

        You can copy directly from Excel:

        ```text
        2/12/1993 00:00    -0.344375
        2/12/1993 00:15    -0.349063
        2/12/1993 00:30    -0.348588
        ```

        A **TAB** between timestamp and value is preferred,
        but multiple spaces also work.

        ### Alignment method

        The app uses:

        **Measurement timestamps → interpolate Model**

        Therefore the two datasets do **not** need matching
        timestamps or the same number of records.
        """
    )

    st.stop()


# ============================================================
# VALIDATE INPUT
# ============================================================

if not measurement_text.strip():

    st.error(
        "Please paste the measurement data."
    )

    st.stop()


if not model_text.strip():

    st.error(
        "Please paste the model data."
    )

    st.stop()


# ============================================================
# PARSE DATA
# ============================================================

measurement = parse_pasted_data(
    measurement_text
)

model = parse_pasted_data(
    model_text
)


# ============================================================
# CHECK PARSING
# ============================================================

if measurement.empty:

    st.error(
        "Could not parse any valid measurement data."
    )

    st.stop()


if model.empty:

    st.error(
        "Could not parse any valid model data."
    )

    st.stop()


# ============================================================
# DATA OVERVIEW
# ============================================================

st.header("2. Data Overview")

col1, col2 = st.columns(2)


with col1:

    st.subheader("Measurement")

    st.write(
        f"Records: **{len(measurement):,}**"
    )

    st.write(
        f"Start: **{measurement['Time'].min()}**"
    )

    st.write(
        f"End: **{measurement['Time'].max()}**"
    )


with col2:

    st.subheader("Model")

    st.write(
        f"Records: **{len(model):,}**"
    )

    st.write(
        f"Start: **{model['Time'].min()}**"
    )

    st.write(
        f"End: **{model['Time'].max()}**"
    )


# ============================================================
# INTERPOLATION
# ============================================================

aligned = interpolate_model(
    measurement,
    model
)


# ============================================================
# NO OVERLAP
# ============================================================

if aligned.empty:

    st.error(
        """
        ❌ No overlapping time period was found.

        The measurement timestamps must overlap the model
        time range for interpolation.
        """
    )

    st.stop()


# ============================================================
# RECORD COUNTS
# ============================================================

excluded_count = (
    len(measurement)
    - len(aligned)
)


# ============================================================
# METRICS
# ============================================================

measured = (
    aligned["Measurement"]
    .to_numpy()
)

modeled = (
    aligned["Model"]
    .to_numpy()
)

error = (
    modeled
    - measured
)


# RMSE
rmse = np.sqrt(
    np.mean(error ** 2)
)


# MAE
mae = np.mean(
    np.abs(error)
)


# Bias
bias = np.mean(
    error
)


# Correlation
if len(aligned) > 1:

    correlation = np.corrcoef(
        measured,
        modeled
    )[0, 1]

else:

    correlation = np.nan


# R²
ss_res = np.sum(
    (measured - modeled) ** 2
)

ss_tot = np.sum(
    (measured - np.mean(measured)) ** 2
)

if ss_tot != 0:

    r_squared = (
        1
        - ss_res / ss_tot
    )

else:

    r_squared = np.nan


# ============================================================
# RESULTS
# ============================================================

st.header("3. Validation Results")

m1, m2, m3, m4, m5 = st.columns(5)


m1.metric(
    "RMSE",
    f"{rmse:.6f}"
)

m2.metric(
    "MAE",
    f"{mae:.6f}"
)

m3.metric(
    "Bias",
    f"{bias:.6f}"
)

m4.metric(
    "Correlation R",
    f"{correlation:.4f}"
)

m5.metric(
    "R²",
    f"{r_squared:.4f}"
)


st.write("")


c1, c2, c3 = st.columns(3)


c1.metric(
    "Measurement Records",
    f"{len(measurement):,}"
)

c2.metric(
    "Compared Records",
    f"{len(aligned):,}"
)

c3.metric(
    "Excluded Records",
    f"{excluded_count:,}"
)


if excluded_count > 0:

    st.warning(
        f"{excluded_count:,} measurement records were "
        "outside the model time range and were excluded."
    )


# ============================================================
# ALIGNMENT TABLE
# ============================================================

st.header("4. Aligned Data")

st.caption(
    "Model values shown here are interpolated values at "
    "the exact measurement timestamps."
)

display_data = aligned[
    [
        "Time",
        "Measurement",
        "Model",
        "Error"
    ]
].copy()

st.dataframe(
    display_data,
    use_container_width=True,
    height=400
)


# ============================================================
# TIME SERIES
# ============================================================

st.header("5. Time-Series Comparison")

fig, ax = plt.subplots(
    figsize=(12, 5)
)

ax.plot(
    aligned["Time"],
    aligned["Measurement"],
    label="Measurement",
    linewidth=1.5
)

ax.plot(
    aligned["Time"],
    aligned["Model"],
    label="Model (Interpolated)",
    linewidth=1.5
)

ax.set_xlabel(
    "Time"
)

ax.set_ylabel(
    "Value"
)

ax.set_title(
    "Model vs Measurement"
)

ax.legend()

ax.grid(
    True,
    alpha=0.3
)

fig.autofmt_xdate()

st.pyplot(
    fig,
    use_container_width=True
)

plt.close(fig)


# ============================================================
# SCATTER
# ============================================================

st.header("6. Scatter Plot")

fig, ax = plt.subplots(
    figsize=(7, 7)
)

ax.scatter(
    measured,
    modeled,
    alpha=0.6
)


# 1:1 line
min_value = min(
    measured.min(),
    modeled.min()
)

max_value = max(
    measured.max(),
    modeled.max()
)

ax.plot(
    [min_value, max_value],
    [min_value, max_value],
    linestyle="--",
    label="1:1"
)


ax.set_xlabel(
    "Measurement"
)

ax.set_ylabel(
    "Model"
)

ax.set_title(
    f"Model vs Measurement\n"
    f"RMSE = {rmse:.6f}, R² = {r_squared:.4f}"
)

ax.legend()

ax.grid(
    True,
    alpha=0.3
)

st.pyplot(
    fig,
    use_container_width=False
)

plt.close(fig)


# ============================================================
# ERROR TIME SERIES
# ============================================================

st.header("7. Error Time Series")

fig, ax = plt.subplots(
    figsize=(12, 4)
)

ax.plot(
    aligned["Time"],
    aligned["Error"],
    linewidth=1
)

ax.axhline(
    0,
    linestyle="--",
    linewidth=1
)

ax.set_xlabel(
    "Time"
)

ax.set_ylabel(
    "Model - Measurement"
)

ax.set_title(
    "Validation Error"
)

ax.grid(
    True,
    alpha=0.3
)

fig.autofmt_xdate()

st.pyplot(
    fig,
    use_container_width=True
)

plt.close(fig)


# ============================================================
# DOWNLOAD
# ============================================================

st.header("8. Download")

download_data = aligned[
    [
        "Time",
        "Measurement",
        "Model",
        "Error",
        "Absolute_Error",
        "Squared_Error"
    ]
].copy()

download_data["Time"] = (
    download_data["Time"]
    .dt.strftime("%d/%m/%Y %H:%M:%S")
)

csv_data = download_data.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="⬇️ Download Aligned Validation CSV",
    data=csv_data,
    file_name="model_measurement_validation.csv",
    mime="text/csv",
    use_container_width=True
)