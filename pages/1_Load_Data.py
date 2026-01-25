import os
import streamlit as st
import polars as pl
from src.state import ensure_state
from src.io import read_df

st.set_page_config(page_title="Load Data", layout="wide")
# ensure_state()

st.title("Load Data")

if "df" not in st.session_state:
    st.session_state.df = pl.DataFrame()
    st.write("No dataset loaded.")

@st.cache_data
def load_csv(data: bytes) -> pl.DataFrame:
    return pl.read_csv(data, infer_schema_length=10000)

uploaded = st.file_uploader("Upload CSV", type="csv")

#read file: uploaded.upload_url

if uploaded :
    st.write(uploaded)
    st.session_state.df = load_csv(uploaded.getvalue())

if not st.session_state.df.is_empty() :
    st.dataframe(st.session_state.df, use_container_width=True)
