import io
import requests
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="THETA Project Data Explorer",
    layout="wide",
)

st.title("THETA Project – Data Explorer")
st.markdown(
    """
This app lets you explore the **THETA project dataset** (and other tabular datasets) using
interactive filters and simple queries.

- Use the sidebar to choose how to load the data (from URL, upload, or local CSV).
- Then use the automatically generated filters to subset the data.
- You can also build quick summaries and download the filtered subset.
"""
)

@st.cache_data(show_spinner=True)
def load_from_url(url: str) -> pd.DataFrame:
    resp = requests.get(url)
    resp.raise_for_status()
    # Try to detect delimiter (comma or tab)
    content = resp.content.decode("utf-8", errors="ignore")
    # Simple heuristic for delimiter
    sep = "," if content.count(",") >= content.count("\t") else "\t"
    return pd.read_csv(io.StringIO(content), sep=sep)

@st.cache_data(show_spinner=True)
def load_from_file(uploaded_file) -> pd.DataFrame:
    return pd.read_csv(uploaded_file)

def build_filters(df: pd.DataFrame):
    st.sidebar.header("Filters")
    st.sidebar.markdown("These controls are generated automatically from column types.")

    filter_masks = []

    # Optional free-text search across all string columns
    search_text = st.sidebar.text_input("Free text search (string columns)", "")
    if search_text:
        search_lower = search_text.lower()
        str_cols = df.select_dtypes(include=["object", "string"]).columns
        if len(str_cols) > 0:
            mask = df[str_cols].apply(
                lambda col: col.astype(str).str.lower().str.contains(search_lower, na=False)
            ).any(axis=1)
            filter_masks.append(mask)

    for col in df.columns:
        col_data = df[col]
        col_dtype = col_data.dtype

        with st.sidebar.expander(f"{col}", expanded=False):
            # Categorical / string columns
            if col_dtype == "object" or str(col_dtype).startswith("category"):
                n_unique = col_data.nunique(dropna=True)
                if n_unique <= 40:
                    options = ["(no filter)"] + sorted(col_data.dropna().unique().astype(str).tolist())
                    selected = st.multiselect(
                        "Select values",
                        options[1:],  # don't show "(no filter)" in choices
                        default=[],
                        key=f"{col}_multiselect",
                    )
                    if selected:
                        mask = col_data.astype(str).isin(selected)
                        filter_masks.append(mask)
                else:
                    val = st.text_input(
                        "Contains (case-insensitive substring)",
                        "",
                        key=f"{col}_contains",
                    )
                    if val:
                        mask = col_data.astype(str).str.contains(val, case=False, na=False)
                        filter_masks.append(mask)

            # Numeric columns
            elif pd.api.types.is_numeric_dtype(col_dtype):
                min_val = float(col_data.min())
                max_val = float(col_data.max())
                if not math.isfinite(min_val) or not math.isfinite(max_val):
                    continue
                range_min, range_max = st.slider(
                    "Range",
                    min_value=min_val,
                    max_value=max_val,
                    value=(min_val, max_val),
                    key=f"{col}_slider",
                )
                mask = col_data.between(range_min, range_max)
                filter_masks.append(mask)

            # Boolean columns
            elif pd.api.types.is_bool_dtype(col_dtype):
                choice = st.selectbox(
                    "Filter",
                    ["(no filter)", "True only", "False only"],
                    key=f"{col}_bool",
                )
                if choice == "True only":
                    filter_masks.append(col_data == True)
                elif choice == "False only":
                    filter_masks.append(col_data == False)

    if filter_masks:
        combined_mask = filter_masks[0]
        for m in filter_masks[1:]:
            combined_mask = combined_mask & m
        return df[combined_mask]
    else:
        return df

def main():
    st.sidebar.title("Data source")

    load_mode = st.sidebar.radio(
        "How do you want to load the data?",
        ("From URL", "Upload CSV"),
    )

    df = None

    if load_mode == "From URL":
        st.sidebar.markdown(
            "Paste a direct CSV/TSV download link (e.g. from the Figshare **Download** button)."
        )
        default_url = st.sidebar.text_input(
            "Data URL",
            value="",
            help="Use the Figshare 'Download' link for the THETA dataset or a local CSV URL.",
        )
        if default_url:
            try:
                df = load_from_url(default_url)
            except Exception as e:
                st.error(f"Could not load data from URL: {e}")
    else:
        uploaded = st.sidebar.file_uploader("Upload a CSV file", type=["csv", "tsv"])
        if uploaded is not None:
            df = load_from_file(uploaded)

    if df is None:
        st.info("Load a dataset from the sidebar to begin exploring.")
        return

    st.success(f"Loaded dataset with {df.shape[0]:,} rows and {df.shape[1]} columns.")

    # Basic info
    with st.expander("Dataset preview & info", expanded=True):
        st.write("**First 50 rows:**")
        st.dataframe(df.head(50), use_container_width=True)
        st.write("**Column summary:**")
        st.write(pd.DataFrame({
            "dtype": df.dtypes.astype(str),
            "n_unique": df.nunique()
        }))

    filtered_df = build_filters(df)

    st.subheader("Filtered data")
    st.caption(f"Showing {filtered_df.shape[0]:,} of {df.shape[0]:,} rows.")
    st.dataframe(filtered_df, use_container_width=True, height=500)

    # Simple groupby summaries
    st.subheader("Quick summaries")
    if filtered_df.shape[0] > 0:
        group_col = st.selectbox(
            "Group by (optional)",
            ["(none)"] + list(filtered_df.columns),
        )
        if group_col != "(none)":
            numeric_cols = filtered_df.select_dtypes(include="number").columns.tolist()
            if numeric_cols:
                agg_func = st.selectbox(
                    "Aggregation",
                    ["mean", "median", "sum", "count"],
                )
                if agg_func == "count":
                    summary = filtered_df.groupby(group_col).size().reset_index(name="count")
                else:
                    summary = getattr(filtered_df.groupby(group_col)[numeric_cols], agg_func)().reset_index()
                st.write("**Summary table:**")
                st.dataframe(summary, use_container_width=True)
            else:
                st.info("No numeric columns to summarise.")
        else:
            st.caption("Select a column to group by if you want a quick summary.")

    # Download filtered subset
    st.subheader("Download filtered data")
    csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download filtered subset as CSV",
        data=csv_bytes,
        file_name="theta_filtered_subset.csv",
        mime="text/csv",
    )

if __name__ == "__main__":
    import math  # needed inside build_filters
    main()
