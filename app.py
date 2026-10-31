import streamlit as st

st.set_page_config(page_title="FullApp Marine Toolkit", page_icon="🌊", layout="wide")

st.markdown(
    """
    <style>
        :root {
            color-scheme: light;
            --app-ink: #183247;
            --app-muted: #587184;
            --app-accent: #087e8b;
            --app-border: #d7e3eb;
            --app-page-start: #f8fbfd;
            --app-page-end: #f1f6f9;
            --app-sidebar: #eaf1f6;
            --app-selected: #d5e9ec;
            --app-selected-ink: #075e69;
            --app-hover-shadow: 0 4px 12px rgb(24 50 71 / 12%);
        }

        @media (prefers-color-scheme: dark) {
            :root {
                color-scheme: dark;
                --app-ink: #e6f0f5;
                --app-muted: #afc1cc;
                --app-accent: #56c5ca;
                --app-border: #334753;
                --app-page-start: #111b22;
                --app-page-end: #17242d;
                --app-sidebar: #14212a;
                --app-selected: #23434b;
                --app-selected-ink: #c4f1ed;
                --app-hover-shadow: 0 4px 14px rgb(0 0 0 / 28%);
            }
        }

        .stApp {
            font-family: "Segoe UI", "Aptos", "Helvetica Neue", sans-serif;
        }

        section.main > div.block-container {
            padding-top: 2.25rem;
            padding-bottom: 3rem;
        }

        [data-testid="stAppViewContainer"] {
            background: linear-gradient(
                180deg,
                var(--app-page-start) 0%,
                var(--app-page-end) 100%
            );
        }

        [data-testid="stSidebar"] {
            background-color: var(--app-sidebar);
            border-right: 1px solid var(--app-border);
        }

        [data-testid="stSidebarNav"] a {
            border-radius: 0.65rem;
            margin: 0.1rem 0.35rem;
            transition: background-color 140ms ease, color 140ms ease;
        }

        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background-color: var(--app-selected);
            color: var(--app-selected-ink);
            font-weight: 650;
        }

        h1, h2, h3 {
            color: var(--app-ink) !important;
            letter-spacing: -0.025em;
        }

        h1 {
            font-size: clamp(2rem, 3.2vw, 2.8rem);
            font-weight: 700;
        }

        h2 {
            font-size: clamp(1.45rem, 2.3vw, 1.9rem);
            font-weight: 650;
        }

        h3 {
            font-size: 1.2rem;
            font-weight: 620;
        }

        [data-testid="stMarkdownContainer"] p,
        [data-testid="stCaptionContainer"] {
            color: var(--app-muted);
        }

        .stButton > button,
        [data-testid="stDownloadButton"] > button {
            border-radius: 0.7rem;
            font-weight: 600;
            transition: transform 140ms ease, box-shadow 140ms ease;
        }

        .stButton > button:hover,
        [data-testid="stDownloadButton"] > button:hover {
            transform: translateY(-1px);
            box-shadow: var(--app-hover-shadow);
        }

        [data-testid="stAlert"],
        [data-testid="stDataFrame"] {
            border-radius: 0.85rem;
            overflow: hidden;
        }

        .st-key-home-tool-grid [class*="-tool-card-"] {
            position: relative;
            min-height: 7.25rem;
            box-sizing: border-box;
            border-color: var(--app-border);
            border-radius: 1rem;
            cursor: pointer;
            transition:
                border-color 150ms ease,
                box-shadow 150ms ease,
                transform 150ms ease;
        }

        .st-key-home-tool-grid [class*="-tool-card-"]:hover {
            border-color: var(--app-accent);
            box-shadow: var(--app-hover-shadow);
            transform: translateY(-2px);
        }

        .st-key-home-tool-grid [data-testid="stPageLink-NavLink"] {
            display: block;
            min-height: 1.8rem;
            color: var(--app-ink);
            font-size: 1.12rem;
            font-weight: 650;
            text-decoration: none;
        }

        .st-key-home-tool-grid
            [data-testid="stElementContainer"]:has([data-testid="stPageLink-NavLink"]) {
            position: static;
        }

        .st-key-home-tool-grid [data-testid="stPageLink-NavLink"]::after {
            content: "";
            position: absolute;
            inset: 0;
            z-index: 1;
        }

        .st-key-home-tool-grid [data-testid="stPageLink-NavLink"]:focus-visible::after {
            border: 3px solid var(--app-accent);
            border-radius: 1rem;
        }

        .st-key-home-tool-grid [data-testid="stPageLink-NavLink"]:hover {
            color: var(--app-accent);
        }

        .st-key-home-tool-grid [data-testid="stCaptionContainer"] {
            font-size: 0.94rem;
            line-height: 1.5;
        }

        @media (prefers-reduced-motion: reduce) {
            *,
            *::before,
            *::after {
                transition-duration: 0.01ms !important;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def home() -> None:
    st.title("Unified Analysis Toolkit")
    st.info(
        "These tools are intended to be publicly accessible at no charge. "
        "Third-party libraries have separate license terms: RTide 1.0 allows "
        "free personal and academic use, but commercial use requires a paid "
        "license. Check the applicable software and data-service terms for "
        "your intended use. Provided as-is, without warranty."
    )
    def render_tool_cards(
        tools: list[tuple[str, str, str]],
        key_prefix: str,
    ) -> None:
        for row_start in range(0, len(tools), 2):
            columns = st.columns(2, gap="medium")
            for card_index, (column, (path, title, description)) in enumerate(
                zip(columns, tools[row_start : row_start + 2]),
                start=row_start,
            ):
                with column:
                    with st.container(
                        key=f"{key_prefix}-tool-card-{card_index}",
                        border=True,
                    ):
                        st.page_link(path, label=title)
                        st.caption(description)

    main_tools = [
        (
            "pages/main_tools/01_era5_toolkit.py",
            "ERA5 Toolkit",
            "Request climate reanalysis data or extract NetCDF files.",
        ),
        (
            "pages/main_tools/02_fetch_analyzer.py",
            "Directional Fetch Analyzer",
            "Estimate directional fetch from a location to the nearest coastline.",
        ),
        (
            "pages/main_tools/03_wave_hindcasting.py",
            "Wave Hindcasting",
            "Analyze wind extremes and estimate waves from wind conditions.",
        ),
        (
            "pages/main_tools/04_tidal_analysis.py",
            "Tidal Analysis",
            "Explore harmonic and response-based tidal analysis workflows.",
        ),
        (
            "pages/main_tools/05_tidal_validation.py",
            "Tidal Validation",
            "Compare measured and modeled water levels across timestamps.",
        ),
    ]

    development_tools = [
        (
            "pages/under_development/01_2d_bin_packing.py",
            "2D Bin Packing",
            "Arrange rectangular items efficiently within fixed-size bins.",
        ),
        (
            "pages/under_development/02_directional_rose_plot.py",
            "Directional Extreme Rose Plot",
            "Visualize directional time-series data and annual extremes.",
        ),
        (
            "pages/under_development/03_vertex_redistribution.py",
            "Mesh Vertex Redistribution",
            "Redistribute mesh vertices from DXF geometry for analysis.",
        ),
        (
            "pages/under_development/04_circle_vertex.py",
            "Circle Vertex Generator",
            "Generate a circle and export its vertices in geographic or UTM coordinates.",
        ),
        (
            "pages/under_development/05_trend_analysis.py",
            "Bed Elevation Trend Analysis",
            "Compare trend models and project bed elevation changes.",
        ),
    ]

    with st.container(key="home-tool-grid"):
        st.markdown("### Main Tools")
        render_tool_cards(main_tools, "main")
        st.markdown("### Under Development")
        st.caption("These tools are still being developed and may change.")
        render_tool_cards(development_tools, "development")


page = st.navigation(
    {
        "": [
            st.Page(home, title="Home", icon="🏠", default=True),
        ],
        "Main Tools": [
            st.Page("pages/main_tools/01_era5_toolkit.py", title="ERA5 Toolkit"),
            st.Page(
                "pages/main_tools/02_fetch_analyzer.py",
                title="Directional Fetch Analyzer",
            ),
            st.Page("pages/main_tools/03_wave_hindcasting.py", title="Wave Hindcasting"),
            st.Page("pages/main_tools/04_tidal_analysis.py", title="Tidal Analysis"),
            st.Page(
                "pages/main_tools/05_tidal_validation.py",
                title="Tidal Validation",
            ),
        ],
        "Under Development": [
            st.Page(
                "pages/under_development/01_2d_bin_packing.py",
                title="2D Bin Packing",
            ),
            st.Page(
                "pages/under_development/02_directional_rose_plot.py",
                title="Directional Extreme Rose Plot",
            ),
            st.Page(
                "pages/under_development/03_vertex_redistribution.py",
                title="Mesh Vertex Redistribution",
            ),
            st.Page(
                "pages/under_development/04_circle_vertex.py",
                title="Circle Vertex Generator",
            ),
            st.Page(
                "pages/under_development/05_trend_analysis.py",
                title="Bed Elevation Trend Analysis",
            ),
        ],
    }
)
page.run()
