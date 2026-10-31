# FullApp Marine Toolkit

This project combines Streamlit tools in one multipage app. **Home** is a
separate landing page; tools are grouped under **Main Tools** and
**Under Development** in the sidebar and on the landing page.

| Tool | Original source |
| --- | --- |
| ERA5 Toolkit | [angbela/era5-data-request](https://github.com/angbela/era5-data-request) |
| Directional Fetch Analyzer | [angbela/fetch](https://github.com/angbela/fetch) |
| Wave Hindcasting | [angbela/hindcasting](https://github.com/angbela/hindcasting) |
| Tidal Analysis | [angbela/tidal-tide](https://github.com/angbela/tidal-tide) |
| Tidal Validation | [angbela/tidal-validation2](https://github.com/angbela/tidal-validation2) |

The sidebar also has an **Under Development** section with these additional tools:

| Tool | Original source |
| --- | --- |
| 2D Bin Packing | [angbela/2d-bin-packing-problem](https://github.com/angbela/2d-bin-packing-problem) |
| Directional Extreme Rose Plot | [angbela/data-maxima-extreme-rose-plot](https://github.com/angbela/data-maxima-extreme-rose-plot) |
| Mesh Vertex Redistribution | [angbela/vertex-redistribution](https://github.com/angbela/vertex-redistribution) |
| Circle Vertex Generator | [angbela/circle-vertex](https://github.com/angbela/circle-vertex) |
| Bed Elevation Trend Analysis | [angbela/trend-analysis](https://github.com/angbela/trend-analysis) |

## Run locally

Install the project dependencies and start the root app entrypoint:

```powershell
uv sync
uv run streamlit run app.py
```

Or, after installing the project, launch it with:

```powershell
uv run fullapp
```

The main page entrypoint is `app.py`. Main tool pages and their assets are in
`pages/main_tools/`; development pages are in `pages/under_development/`.
Dependencies are declared in `pyproject.toml` and pinned in `uv.lock`.

For Streamlit Community Cloud, select this repository's root `app.py` as the
app file. Community Cloud detects the root `uv.lock` for dependencies. Keep
credentials in Streamlit secrets or environment variables; do not commit
`.streamlit/secrets.toml`.

The fetch analyzer uses the bundled coastline dataset in
`pages/main_tools/data/coastline`.
The ERA5 downloader requires a valid CDS API key, entered in the ERA5 page.

## Usage and licensing

The hosted tools are intended to be publicly accessible at no charge. Third-party
packages have their own license terms, and this repository does not grant a
license to reuse its source code. Most direct dependencies in the current lockfile
declare permissive licenses; `rtide` 1.0 is an exception: its Business Source
License 1.1 permits free personal and academic use, while commercial use requires
a paid license. Check dependency and data-service terms for your intended use.