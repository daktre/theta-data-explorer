import streamlit as st
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# Basic app config
# --------------------------------------------------
st.set_page_config(
    page_title="THETA Data Explorer",
    layout="wide"
)

st.title("THETA Data Explorer")
st.caption(
    "Settlement-, household-, and individual-level data from the "
    "Towards Health Equity and Transformative Action on Tribal Health (THETA) project."
)

# --------------------------------------------------
# Data loading
# --------------------------------------------------
DATA_DIR = Path("data")

@st.cache_data
def load_csv(filename):
    return pd.read_csv(DATA_DIR / filename)

settlement_df = load_csv("theta_settlement.csv")
household_df  = load_csv("theta_household.csv")
individual_df = load_csv("theta_individual.csv")

# --------------------------------------------------
# Helper: generic filtering
# --------------------------------------------------
def apply_filters(df):
    filtered_df = df.copy()

    with st.sidebar:
        st.markdown("### Filters")

        for col in df.columns:

            # Skip columns that are entirely missing
            if df[col].dropna().empty:
                continue

            # Skip very wide text columns
            if df[col].dtype == "object" and df[col].nunique() > 50:
                continue

            # Categorical / string columns
            if df[col].dtype == "object":
                options = sorted(df[col].dropna().unique())
                selected = st.multiselect(
                    f"{col}",
                    options,
                    default=options
                )
                filtered_df = filtered_df[filtered_df[col].isin(selected)]

            # Numeric columns
            elif pd.api.types.is_numeric_dtype(df[col]):
                min_val = df[col].min()
                max_val = df[col].max()

                # Skip constants (min == max)
                if pd.isna(min_val) or pd.isna(max_val) or min_val == max_val:
                    continue

                selected = st.slider(
                    f"{col}",
                    float(min_val),
                    float(max_val),
                    (float(min_val), float(max_val))
                )
                filtered_df = filtered_df[
                    (filtered_df[col] >= selected[0]) &
                    (filtered_df[col] <= selected[1])
                ]

    return filtered_df

# --------------------------------------------------
# Tabs
# --------------------------------------------------
tab_settlement, tab_household, tab_individual, tab_about = st.tabs(
    ["Settlements", "Households", "Individuals", "About"]
)

# --------------------------------------------------
# Settlements tab
# --------------------------------------------------
with tab_settlement:
    st.subheader("Settlements")
    st.info(
        "Each row represents one settlement (village). "
        "Variables here describe village-level context and characteristics."
    )

    filtered = apply_filters(settlement_df)

    st.write(f"**Rows shown:** {len(filtered)}")
    st.dataframe(filtered, use_container_width=True)

    st.download_button(
        "Download filtered settlement data (CSV)",
        filtered.to_csv(index=False),
        file_name="theta_settlement_filtered.csv",
        mime="text/csv"
    )

# --------------------------------------------------
# Households tab
# --------------------------------------------------
with tab_household:
    st.subheader("Households")
    st.info(
        "Each row represents one household. "
        "Households are linked to settlements using `deidentified_village`."
    )

    filtered = apply_filters(household_df)

    st.write(f"**Rows shown:** {len(filtered)}")
    st.dataframe(filtered, use_container_width=True)

    st.download_button(
        "Download filtered household data (CSV)",
        filtered.to_csv(index=False),
        file_name="theta_household_filtered.csv",
        mime="text/csv"
    )

# --------------------------------------------------
# Individuals tab
# --------------------------------------------------
with tab_individual:
    st.subheader("Individuals")
    st.info(
        "Each row represents one individual. "
        "Individuals are linked to households using `fulcrum_id_parent`."
    )

    filtered = apply_filters(individual_df)

    st.write(f"**Rows shown:** {len(filtered)}")
    st.dataframe(filtered, use_container_width=True)

    st.download_button(
        "Download filtered individual data (CSV)",
        filtered.to_csv(index=False),
        file_name="theta_individual_filtered.csv",
        mime="text/csv"
    )

# --------------------------------------------------
# About tab
# --------------------------------------------------
with tab_about:
    st.markdown(
        """
        ### About this app

        This app provides a public interface for exploring the
        THETA project datasets at three levels:
        settlements, households, and individuals.

        The CSV files used here are created from the datasets
    	archived on Figshare. 
        """
    )