import streamlit as st
import polars as pl
from src.state import ensure_state
from src.io import read_df
from src.features import apply_features, save_features, load_features

st.set_page_config(page_title="Feature Lab", layout="wide")
st.title("Feature Lab (Safe Derived Features)")

if "df" not in st.session_state:
    st.session_state.df = pl.DataFrame()

if st.session_state.df.is_empty():
    st.info("Load a dataset first in **Load Data**.")
    st.stop()

st.dataframe(st.session_state.df, use_container_width=True)

if st.button("Test") :
    st.session_state.df = st.session_state.df.with_columns([(pl.col("Fare") * pl.col("PassengerId")).alias("A_t_B")])
    st.success("Feature created: A_t_B = Fare * PassengerId")
    st.rerun()
