import streamlit as st
from src.state import ensure_state
import polars as pl

st.set_page_config(page_title="Auto EDA (Local)", layout="wide")
ensure_state()

st.title("Auto EDA ")

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
    df = st.session_state.df
    st.dataframe(df, use_container_width=True)

    target = st.selectbox("Select Target Column (for classification)", options=df.columns+[None])

    # @st.cache_data
    # cat_cols = st.multiselect("Select Categorical Columns", options= , default=[c for c, t in df.schema.items() if pl.datatypes.is_utf8(t)])


    # #select ignore by exluding target
    # # ignore = st.multiselect("Select Columns to Ignore", options=[x for x in df.columns if x != target])
