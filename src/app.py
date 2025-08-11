from pathlib import Path
import pandas as pd
import sys, traceback
import streamlit as st

try:
    from optimizer_core import (
    load_catalog, BasketParams, build_basket, save_params
    )

    _IMPORT_OK = True
except Exception as e:
    _IMPORT_OK = False
    _IMPORT_ERR = e
    _IMPORT_TB = traceback.format_exc()

st.set_page_config(page_title="Efficient Shopping Optimizer", layout="wide")

st.title("Efficient Shopping Optimizer")


if not _IMPORT_OK:
    st.error("Failed to import optimizer_core. See details below.")
    st.code(_IMPORT_TB, language="python")
    st.stop()

# --- Dataset path hardcoded
CSV = Path("data/eso_new_ver1.csv")

try:
    df = load_catalog(CSV)
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()
except Exception as e:
    st.exception(e)
    st.stop()


with st.sidebar:
    st.header("Preferences")
    budget = st.slider("Budget ($)", 5, 200, 40, 1)
    max_items = st.slider("Max items", 1, 50, 15, 1)
    allow_multiples = st.checkbox("Allow multiple units per item", value=True)
    qty_cap = st.number_input(
        "Max 100g units per item",
        min_value=1,
        max_value=50,
        value=10,
        step=1,
        disabled=not allow_multiples,
        help="When enabled, each item can be added up to this many 100g units."
    )

    cats = sorted(df["category"].dropna().unique().tolist())
    classes = sorted(df["classification"].dropna().unique().tolist())
    inc_cats = st.multiselect("Include categories", cats)
    inc_class = st.multiselect("Include classifications", classes)

    exclude_items = st.multiselect("Exclude items", sorted(df["item_name"].unique().tolist()))

    st.header("Scoring weights")
    wP = st.slider("Protein weight (+)", 0.0, 3.0, 1.0, 0.1)
    wFi = st.slider("Fiber weight (+)",   0.0, 3.0, 0.3, 0.1)
    wC = st.slider("Carbs penalty (−)",  0.0, 3.0, 0.1, 0.1)
    wF = st.slider("Fat penalty (−)",    0.0, 3.0, 0.2, 0.1)

    run = st.button("Run Optimizer", type="primary")

st.divider()
st.caption("Set your preferences in the sidebar, then click **Run Optimizer**.")

# --- Results
if run:
    # Apply optional exclusions before building params
    df_run = df.copy()
    if exclude_items:
        df_run = df_run[~df_run["item_name"].isin(exclude_items)]

    params = BasketParams(
        budget=budget,
        max_items=max_items,
        include_categories=inc_cats or None,
        include_classes=inc_class or None,
        wP=wP,
        wFi=wFi,
        wC=wC,
        wF=wF,
        allow_multiples=allow_multiples,
        max_qty_per_item=int(qty_cap),
    )

    basket_df, summary = build_basket(df_run, params)

    if basket_df.empty:
        st.info("No solution within budget/filters—try raising budget or removing filters.")
    else:
        # Summary panel
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Items", summary.get("items", 0))
        c2.metric("Total $", f"{summary.get('spent_$', 0):.2f}")
        c3.metric("Protein (g)", summary.get("protein_g", 0))
        c4.metric("Fiber (g)", summary.get("fiber_g", 0))
        c5.metric("Calories", summary.get("calories_kcal", 0))

        st.dataframe(
            basket_df[[
                "item_name","category","classification","qty_100g","line_cost_$",
                "protein_g","fiber_g","fat_g","carbs_g","calories_kcal"
            ]],
            use_container_width=True,
        )

        # Download
        csv = basket_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data=csv, file_name="optimizer_result.csv", mime="text/csv")