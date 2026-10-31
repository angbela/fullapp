import streamlit as st
import pandas as pd
from rectpack import newPacker
import matplotlib.pyplot as plt
from pathlib import Path
import sys
sys.path.insert(0, str((Path(__file__).parent / ".packages").resolve()))

st.set_page_config(layout="wide")

@st.cache_data
def load_default_excel(excel_path: Path) -> pd.DataFrame:
    try:
        df = pd.read_excel(excel_path)
        if "Quantity" not in df.columns:
            df["Quantity"] = 1
        return df
    except Exception:
        return pd.DataFrame({"ID": ["A", "B", "C"], "Width": [10, 15, 20], "Length": [5, 7, 9], "Quantity": [1, 2, 1]})

def example_rectangles_df() -> pd.DataFrame:
    data = [
        {"ID": 1, "Length": 15, "Width": 18, "Quantity": 1},
        {"ID": 2, "Length": 12, "Width": 28, "Quantity": 6},
        {"ID": 3, "Length": 5, "Width": 14, "Quantity": 3},
        {"ID": 4, "Length": 12, "Width": 15, "Quantity": 1},
        {"ID": 5, "Length": 6, "Width": 11, "Quantity": 2},
        {"ID": 6, "Length": 7, "Width": 18, "Quantity": 4},
        {"ID": 7, "Length": 8, "Width": 42, "Quantity": 3},
        {"ID": 8, "Length": 3, "Width": 36, "Quantity": 3},
        {"ID": 9, "Length": 5, "Width": 5, "Quantity": 12},
        {"ID": 10, "Length": 4, "Width": 7, "Quantity": 6},
        {"ID": 11, "Length": 4, "Width": 12, "Quantity": 22},
        {"ID": 12, "Length": 4, "Width": 3, "Quantity": 44},
        {"ID": 13, "Length": 4, "Width": 26, "Quantity": 1},
        {"ID": 14, "Length": 12, "Width": 37, "Quantity": 3},
        {"ID": 15, "Length": 5, "Width": 12, "Quantity": 1},
        {"ID": 16, "Length": 6, "Width": 18, "Quantity": 11},
        {"ID": 17, "Length": 3, "Width": 12, "Quantity": 32},
        {"ID": 18, "Length": 3, "Width": 3, "Quantity": 47},
        {"ID": 19, "Length": 15, "Width": 24, "Quantity": 4},
        {"ID": 20, "Length": 18, "Width": 37, "Quantity": 3},
        {"ID": 21, "Length": 14, "Width": 40, "Quantity": 4},
        {"ID": 22, "Length": 16, "Width": 33, "Quantity": 1},
        {"ID": 23, "Length": 10, "Width": 35, "Quantity": 1},
        {"ID": 24, "Length": 12, "Width": 47, "Quantity": 3},
        {"ID": 25, "Length": 11, "Width": 42, "Quantity": 2},
        {"ID": 26, "Length": 5, "Width": 3, "Quantity": 14},
        {"ID": 27, "Length": 5, "Width": 42, "Quantity": 1},
        {"ID": 28, "Length": 5, "Width": 19, "Quantity": 1},
        {"ID": 29, "Length": 2, "Width": 3, "Quantity": 5},
        {"ID": 30, "Length": 2, "Width": 12, "Quantity": 1},
        {"ID": 31, "Length": 6, "Width": 40, "Quantity": 1},
        {"ID": 32, "Length": 6, "Width": 30, "Quantity": 3},
        {"ID": 33, "Length": 6, "Width": 24, "Quantity": 3},
        {"ID": 34, "Length": 4, "Width": 13, "Quantity": 1},
        {"ID": 35, "Length": 14, "Width": 24, "Quantity": 2},
        {"ID": 36, "Length": 18, "Width": 26, "Quantity": 1},
        {"ID": 37, "Length": 13, "Width": 39, "Quantity": 2},
        {"ID": 38, "Length": 16, "Width": 40, "Quantity": 2},
        {"ID": 39, "Length": 10, "Width": 42, "Quantity": 1},
        {"ID": 40, "Length": 4, "Width": 6, "Quantity": 18},
        {"ID": 41, "Length": 4, "Width": 20, "Quantity": 1},
        {"ID": 42, "Length": 2, "Width": 16, "Quantity": 3},
        {"ID": 43, "Length": 6, "Width": 42, "Quantity": 2},
        {"ID": 44, "Length": 6, "Width": 20, "Quantity": 2},
        {"ID": 45, "Length": 14, "Width": 30, "Quantity": 2},
        {"ID": 46, "Length": 11, "Width": 45, "Quantity": 3},
        {"ID": 47, "Length": 5, "Width": 22, "Quantity": 1},
        {"ID": 48, "Length": 6, "Width": 23, "Quantity": 1},
    ]
    return pd.DataFrame(data)

def normalize_table(value, base_df):
    if isinstance(value, pd.DataFrame):
        return value.copy()
    if isinstance(value, list):
        if len(value) == 0:
            return pd.DataFrame(columns=list(base_df.columns) if isinstance(base_df, pd.DataFrame) else None)
        if isinstance(value[0], dict):
            return pd.DataFrame(value)
    if isinstance(value, dict):
        keys = set(value.keys())
        if {"edited_rows", "added_rows", "deleted_rows"}.issubset(keys):
            df = base_df.copy() if isinstance(base_df, pd.DataFrame) else pd.DataFrame()
            for idx_str, changes in value.get("edited_rows", {}).items():
                try:
                    idx = int(idx_str)
                except Exception:
                    continue
                for k, v in changes.items():
                    if idx < len(df.index):
                        df.at[idx, k] = v
            for row in value.get("added_rows", []):
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            drops = []
            for idx_str in value.get("deleted_rows", []):
                try:
                    drops.append(int(idx_str))
                except Exception:
                    pass
            if drops:
                df = df.drop([i for i in drops if i in df.index], errors="ignore")
                df = df.reset_index(drop=True)
            return df
        vals = list(value.values())
        if all(isinstance(v, dict) for v in vals):
            return pd.DataFrame.from_dict(value, orient="index").reset_index(drop=True)
        return pd.DataFrame(value)
    return pd.DataFrame(value)

def run_packing(bin_w, bin_h, df):
    items = []
    index_map = []
    # Use row index + 1 as the fallback row ID if ID is missing
    for r_idx, row in df.iterrows():
        try:
            q = int(row.get("Quantity", 1))
        except Exception:
            q = 1
        try:
            w = float(row["Width"])
            l = float(row["Length"])
        except Exception:
            continue
        
        # Check if ID exists and is not empty/NaN
        raw_id = row.get("ID")
        if pd.isna(raw_id) or str(raw_id).strip() == "":
            base_id = str(r_idx + 1)
        else:
            base_id = str(raw_id)
            
        for i in range(q):
            items.append((w, l))
            # Always use the base_id without suffix as requested
            index_map.append(base_id)
                
    packer = newPacker()
    for idx, (w, l) in enumerate(items):
        # We pass idx as the rid to retrieve it later from the results
        packer.add_rect(w, l, rid=idx)
    packer.add_bin(bin_w, bin_h, count=float("inf"))
    packer.pack()
    
    placements = []
    bins_data = []
    for b_idx, abin in enumerate(packer):
        bin_list = []
        for r in abin:
            # rectpack returns the rid we passed during add_rect
            idx = r.rid
            item_id = index_map[idx] if idx < len(index_map) else str(idx)
            placements.append(
                {
                    "Bin": b_idx + 1,
                    "ItemID": item_id,
                    "X": r.x,
                    "Y": r.y,
                    "Width": r.width,
                    "Length": r.height,
                }
            )
            bin_list.append(
                {"rid": item_id, "x": r.x, "y": r.y, "width": r.width, "height": r.height}
            )
        bins_data.append(bin_list)
    res = pd.DataFrame(placements)
    return res, bins_data

def draw_bin(bin_index, bin_w, bin_h, items):
    fig, ax = plt.subplots()
    ax.set_title(f"Bin {bin_index + 1}")
    ax.set_xlim(0, bin_w)
    ax.set_ylim(0, bin_h)
    ax.set_aspect("equal", "box")
    for rect in items:
        if hasattr(rect, "x"):
            x, y, w, h, rid = rect.x, rect.y, rect.width, rect.height, rect.rid
        else:
            x, y, w, h, rid = rect["x"], rect["y"], rect["width"], rect["height"], rect["rid"]
        ax.add_patch(plt.Rectangle((x, y), w, h, fill=False, edgecolor="r"))
        ax.text(x + w / 2, y + h / 2, f"{rid}", ha="center", va="center", color="b", fontsize=8)
    return fig

st.title("2D Bin Packing")
excel_path = Path(__file__).parent / "gas.xlsx"

# Initialize session state for input defaults if not present
if "input_bin_w" not in st.session_state:
    st.session_state.input_bin_w = 10.0
if "input_bin_h" not in st.session_state:
    st.session_state.input_bin_h = 10.0
if "input_df" not in st.session_state:
    st.session_state.input_df = pd.DataFrame([{"ID": "", "Length": None, "Width": None, "Quantity": None}] * 3)
if "editor_key" not in st.session_state:
    st.session_state.editor_key = 0

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Load Example"):
            st.session_state.input_bin_w = 81.0
            st.session_state.input_bin_h = 22.0
            st.session_state.input_df = example_rectangles_df()
            st.session_state.editor_key += 1
            st.rerun()
    with c2:
        if st.button("Reset Input"):
            st.session_state.input_bin_w = 10.0
            st.session_state.input_bin_h = 10.0
            st.session_state.input_df = pd.DataFrame([{"ID": "", "Length": None, "Width": None, "Quantity": None}] * 3)
            st.session_state.editor_key += 1
            st.rerun()

    with st.form("input_form"):
        st.subheader("Input")
        bin_w = st.number_input("Bin Width", min_value=1.0, value=st.session_state.input_bin_w)
        bin_h = st.number_input("Bin Length", min_value=1.0, value=st.session_state.input_bin_h)
        
        # Use a dynamic key to force refresh when "Load Example" is clicked
        editor_key = f"rect_table_{st.session_state.editor_key}"
        table_val = st.data_editor(
            st.session_state.input_df, 
            num_rows="dynamic", 
            key=editor_key, 
            use_container_width=True
        )
        
        submitted = st.form_submit_button("Pack")
        if submitted:
            # When using st.form, the data_editor value is in the session state under its key
            table = st.session_state.get(editor_key)
            if table is None or (isinstance(table, pd.DataFrame) and len(table) == 0):
                st.error("Please provide at least one rectangle.")
            else:
                df_table = normalize_table(table, st.session_state.input_df)
                for col in ["Width", "Length", "Quantity"]:
                    if col in df_table.columns:
                        df_table[col] = pd.to_numeric(df_table[col], errors='coerce')
                df_table = df_table.fillna({"Quantity": 1})
                res, bins_data = run_packing(bin_w, bin_h, df_table)
                st.session_state["pack_res"] = res
                st.session_state["pack_bins"] = bins_data
                st.session_state["pack_bin_w"] = bin_w
                st.session_state["pack_bin_h"] = bin_h
                st.session_state["page"] = 1
                st.session_state["bins_per_page"] = max(1, len(bins_data))

if "pack_bins" in st.session_state and st.session_state["pack_bins"] is not None:
    res = st.session_state["pack_res"]
    bins = st.session_state["pack_bins"]
    bin_w = st.session_state["pack_bin_w"]
    bin_h = st.session_state["pack_bin_h"]
    st.subheader("Placements")
    st.dataframe(res, use_container_width=True)
    csv = res.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", data=csv, file_name="placements.csv", mime="text/csv")
    if len(bins) == 0:
        st.info("No bins")
    else:
        cols_per_row = st.number_input("Columns", min_value=1, max_value=4, value=1, key="cols_per_row")
        if "bins_per_page" not in st.session_state:
            st.session_state["bins_per_page"] = max(1, len(bins))
        page_size = st.number_input("Bins per page", min_value=1, max_value=max(1, len(bins)), value=st.session_state["bins_per_page"], key="bins_per_page")
        total_pages = (len(bins) + int(page_size) - 1) // int(page_size)
        if "page" not in st.session_state:
            st.session_state.page = 1
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Prev"):
                st.session_state.page = max(1, st.session_state.page - 1)
        with c2:
            st.write(f"Page {st.session_state.page} / {total_pages}")
        with c3:
            if st.button("Next"):
                st.session_state.page = min(total_pages, st.session_state.page + 1)
        start = (st.session_state.page - 1) * int(page_size)
        end = min(start + int(page_size), len(bins))
        subset = bins[start:end]
        for r in range(0, len(subset), int(cols_per_row)):
            row_bins = subset[r:r + int(cols_per_row)]
            cols = st.columns(len(row_bins))
            for idx, abin in enumerate(row_bins):
                with cols[idx]:
                    fig = draw_bin(start + r + idx, bin_w, bin_h, abin)
                    st.pyplot(fig, use_container_width=True)
else:
    st.info("Set inputs and click Pack to see results.")
