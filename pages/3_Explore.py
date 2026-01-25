import streamlit as st
import polars as pl
import plotly.express as px
from src.state import ensure_state
from src.io import read_df
from src.profiling import histogram, top_values
from src.features import apply_features

st.set_page_config(page_title="Explore", layout="wide")
ensure_state()
st.title("Explore")

if not st.session_state.df:
    st.info("Load a dataset first in **Load Data**.")
    st.stop()

# @st.cache_data(show_spinner=False)
# def load_df(cache_key: str, path: str) -> pl.DataFrame:
#     return read_df(path)

# df = load_df(st.session_state.df_cache_key, st.session_state.dataset_path)
df = read_df(st.session_state.dataset)
df2 = apply_features(df, st.session_state.features)

st.subheader("Univariate")
col = st.selectbox("Column", options=df2.columns, key="explore_col")

dtype = df2.schema[col]
if pl.datatypes.is_numeric(dtype):
    bins = st.slider("Bins", 10, 120, 40)
    h = histogram(df2, col, bins=bins).to_pandas()
    fig = px.bar(h, x="bin_left", y="count")
    st.plotly_chart(fig, use_container_width=True)
else:
    topn = st.slider("Top N", 5, 50, 20)
    tv = top_values(df2, col, top_n=topn).to_pandas()
    fig = px.bar(tv, x=col, y="len")
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Bivariate (Scatter)")
num_cols = [c for c, t in df2.schema.items() if pl.datatypes.is_numeric(t)]
if len(num_cols) >= 2:
    x = st.selectbox("X", num_cols, index=0)
    y = st.selectbox("Y", num_cols, index=1)
    sample_n = st.slider("Sample points", 1000, 30000, 7000, step=1000)

    pdf = df2.select([x, y]).drop_nulls().sample(n=min(sample_n, df2.height)).to_pandas()
    fig2 = px.scatter(pdf, x=x, y=y)
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Need at least 2 numeric columns for scatter.")
