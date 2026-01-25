import streamlit as st
import polars as pl
from src.state import ensure_state
from src.io import read_df
from src.profiling import schema_overview, numeric_summary, top_values
from src.features import apply_features

st.set_page_config(page_title="Columns", layout="wide")
ensure_state()
st.title("Columns")

if st.session_state.df.is_empty():
    st.info("Load a dataset first in **Load Data**.")
    st.stop()

df = st.session_state.df
st.dataframe(df.describe())


# @st.cache_data(show_spinner=False)
# def load_df(cache_key: str, dataset) -> pl.DataFrame:
#     return read_df(dataset)

# df = load_df(st.session_state.df_cache_key, st.session_state.dataset)
# df = read_df(st.session_state.dataset)
# df2 = apply_features(df, st.session_state.features)


# schema_df = schema_overview(df2)
# st.dataframe(schema_df.to_pandas(), use_container_width=True)

# st.divider()
# col = st.selectbox("Pick a column", options=df2.columns)

# dtype = df2.schema[col]
# st.write(f"**dtype:** `{dtype}`")

# if pl.datatypes.is_numeric(dtype):
#     st.json(numeric_summary(df2, col))
# else:
#     tv = top_values(df2, col, top_n=20)
#     st.dataframe(tv.to_pandas(), use_container_width=True)
