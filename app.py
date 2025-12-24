import streamlit as st
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# App configuration
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
# Explicit filter whitelists (CRITICAL)
# --------------------------------------------------
# These are intentionally conservative.
# More can be added later, deliberately.

SETTLEMENT_FILTER_COLS = [
    "deidentified_village"
]

HOUSEHOLD_FILTER_COLS = [
    "deidentified_village"
]

INDIVIDUAL_FILTER_COLS = [
    "sex",
    "age"
]

# --------------------------------------------------
# Filter helper (deterministic, empty-safe)
# --------------------------------------------------
def apply_filters(df, label, filter_cols):
    filtered_df = df.copy()

    st.markdown("#### Filters")

    for col in filter_cols:
        if col not in df.columns:
            continue

        if df[col].dropna().empty:
            continue

        # Categorical filters
        if df[col].dtype == "object":
            options = sorted(df[col].dropna().unique())
            selected = st.multiselect(
                col,
                options,
                default=options,
                key=f"{label}_{col}"
            )

            if selected:
                filtered_df = filtered_df[filtered_df[col].isin(selected)]

        # Numeric filters
        elif pd.api.types.is_numeric_dtype(df[col]):
            min_val = df[col].min()
            max_val = df[col].max()

            if pd.isna(min_val) or pd.isna(max_val) or min_val == max_val:
                continue

            selected = st.slider(
                col,
                float(min_val),
                float(max_val),
                (float(min_val), float(max_val)),
                key=f"{label}_{col}"
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
    st.info("Each row represents one settlement (village).")

    with st.expander("Filters", expanded=False):
        filtered = apply_filters(
            settlement_df,
            label="settlement",
            filter_cols=SETTLEMENT_FILTER_COLS
        )

    st.write(f"Rows shown: {len(filtered)}")
    st.dataframe(filtered, width="stretch")

# --------------------------------------------------
# Households tab
# --------------------------------------------------
with tab_household:
    st.subheader("Households")
    st.info("Each row represents one household.")

    with st.expander("Filters", expanded=False):
        filtered = apply_filters(
            household_df,
            label="household",
            filter_cols=HOUSEHOLD_FILTER_COLS
        )

    st.write(f"Rows shown: {len(filtered)}")
    st.dataframe(filtered, width="stretch")

# --------------------------------------------------
# Individuals tab
# --------------------------------------------------
with tab_individual:
    st.subheader("Individuals")
    st.info("Each row represents one individual.")

    with st.expander("Filters", expanded=False):
        filtered = apply_filters(
            individual_df,
            label="individual",
            filter_cols=INDIVIDUAL_FILTER_COLS
        )

    st.write(f"Rows shown: {len(filtered)}")
    st.dataframe(filtered, width="stretch")

# --------------------------------------------------
# About tab
# --------------------------------------------------
with tab_about:
    st.markdown(
        """
        ### About this app

        This app provides a public, exploratory interface for engaging with
        the THETA project datasets at three distinct levels of analysis:
        settlements, households, and individuals.

        The datasets used here from the THETA datasets archived on Figshare.
        """
    )