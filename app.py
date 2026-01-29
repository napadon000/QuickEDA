import streamlit as st
from src.state import ensure_state
import pandas as pd
from pandas.api.types import (
    is_numeric_dtype,
    is_object_dtype,
    is_string_dtype,
    is_datetime64_any_dtype,
)
import io
import plotly.express as px
import missingno as msno
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Auto EDA (Local)", layout="wide")
ensure_state()

st.title("Auto EDA")

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame()
    st.write("No dataset loaded.")

@st.cache_data
def load_csv(data: bytes) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(data))

uploaded = st.file_uploader("Upload CSV", type="csv")

def load_cols_once(df: pd.DataFrame):
    """Initialize columns + defaults ONCE per uploaded file."""
    st.session_state.pool_cols = df.columns.tolist()

    st.session_state.cat_cols = [
        c for c, t in df.dtypes.items() if is_object_dtype(t) or is_string_dtype(t)
    ]
    st.session_state.num_cols = [c for c, t in df.dtypes.items() if is_numeric_dtype(t)]
    st.session_state.date_cols = [
        c for c, t in df.dtypes.items() if is_datetime64_any_dtype(t)
    ]
    st.session_state.target = None

    # Initialize widget states to match defaults
    st.session_state.target_select = st.session_state.target
    st.session_state.cat_cols_select = st.session_state.cat_cols.copy()
    st.session_state.num_cols_select = st.session_state.num_cols.copy()
    st.session_state.date_cols_select = st.session_state.date_cols.copy()

def update_target():
    target = st.session_state.target_select
    # allow None
    if target is None or target in st.session_state.pool_cols:
        st.session_state.target = target
    else:
        st.session_state.target = None

def update_cat_cols():
    cat_cols = st.session_state.cat_cols_select
    # prevent overlap with num/date/target
    target_set = {st.session_state.target} if st.session_state.target else set()
    if not (set(cat_cols) & set(st.session_state.num_cols)) \
       and not (set(cat_cols) & set(st.session_state.date_cols)) \
       and not (set(cat_cols) & target_set):
        st.session_state.cat_cols = cat_cols
    else:
        # revert widget to last valid
        st.session_state.cat_cols_select = st.session_state.cat_cols.copy()

def update_num_cols():
    num_cols = st.session_state.num_cols_select
    target_set = {st.session_state.target} if st.session_state.target else set()
    if not (set(num_cols) & set(st.session_state.cat_cols)) \
       and not (set(num_cols) & set(st.session_state.date_cols)) \
       and not (set(num_cols) & target_set):
        #check if column is numeric with using try convert to numeric
        try :
            #look for only new col
            for col in set(num_cols) - set(st.session_state.num_cols):
                pd.to_numeric(st.session_state.df[col])
        except Exception:
            st.session_state.num_cols_select = st.session_state.num_cols.copy()
            st.write("Error: One or more selected columns cannot be converted to numeric.")
            return
        #convert all to numberic for state df
        for col in set(num_cols) - set(st.session_state.num_cols):
            st.session_state.df[col] = pd.to_numeric(st.session_state.df[col])
        st.session_state.num_cols = num_cols
    else:
        st.session_state.num_cols_select = st.session_state.num_cols.copy()

def update_date_cols():
    date_cols = st.session_state.date_cols_select
    target_set = {st.session_state.target} if st.session_state.target else set()
    if not (set(date_cols) & set(st.session_state.cat_cols)) \
       and not (set(date_cols) & set(st.session_state.num_cols)) \
       and not (set(date_cols) & target_set):
        #check if column is date with using try convert to datetime
        try :
            #look for only new col
            for col in set(date_cols) - set(st.session_state.date_cols):
                pd.to_datetime(st.session_state.df[col])
        except Exception:
            st.session_state.date_cols_select = st.session_state.date_cols.copy()
            st.write("Error: One or more selected columns cannot be converted to datetime.")
            return
        #convert all to datetime for state df
        for col in set(date_cols) - set(st.session_state.date_cols):
            st.session_state.df[col] = pd.to_datetime(st.session_state.df[col], utc=True)
        st.session_state.date_cols = date_cols
    else:
        st.session_state.date_cols_select = st.session_state.date_cols.copy()

def features_info(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a detailed DataFrame with comprehensive column information
    """
    info_df = pd.DataFrame({
        'Column': df.columns,
        'Non-Null Count': df.count().values,
        'Null Count': df.isnull().sum().values,
        'Unique Values': [df[col].nunique() for col in df.columns],
        'Dtype': df.dtypes.values,
        'First Value': [df[col].dropna().iloc[0] if df[col].dropna().shape[0] > 0 else None for col in df.columns],
    })

    # Add percentage columns
    info_df['Non-Null %'] = (info_df['Non-Null Count'] / len(df) * 100).round(2)
    info_df['Null %'] = (info_df['Null Count'] / len(df) * 100).round(2)

    return info_df

# --- Load file ONLY when it changes ---
if uploaded:
    data = uploaded.getvalue()
    file_id = (uploaded.name, uploaded.size, hash(data))

    if st.session_state.get("file_id") != file_id:
        st.session_state.file_id = file_id
        st.session_state.df = load_csv(data)
        load_cols_once(st.session_state.df)

# --- UI ---
if not st.session_state.df.empty:
    df = st.session_state.df
    st.dataframe(df, use_container_width=True)
    st.write(f'rows: {df.shape[0]}, columns: {df.shape[1]}')
    st.write(f'duplicate rows: {df.duplicated().sum()}')
    st.dataframe(features_info(df), use_container_width=True)


    # helper sets
    pool = set(st.session_state.pool_cols)
    target_set = {st.session_state.target} if st.session_state.target else set()

    # TARGET options: allow None + any column not already in cat/num/date
    target_options = [None] + sorted(list(pool - set(st.session_state.cat_cols) - set(st.session_state.num_cols) - set(st.session_state.date_cols)))

    st.selectbox(
        "Select Target Column (for classification)",
        options=target_options,
        key="target_select",
        on_change=update_target,
    )

    # Recompute after potential target change
    pool = set(st.session_state.pool_cols)
    target_set = {st.session_state.target} if st.session_state.target else set()

    cat_options = sorted(list(pool - set(st.session_state.num_cols) - set(st.session_state.date_cols) - target_set))
    num_options = sorted(list(pool - set(st.session_state.cat_cols) - set(st.session_state.date_cols) - target_set))
    date_options = sorted(list(pool - set(st.session_state.cat_cols) - set(st.session_state.num_cols) - target_set))

    st.multiselect(
        "Select Categorical Columns",
        options=cat_options,
        default=st.session_state.cat_cols,
        key="cat_cols_select",
        on_change=update_cat_cols,
    )

    st.multiselect(
        "Select Numerical Columns",
        options=num_options,
        default=st.session_state.num_cols,
        key="num_cols_select",
        on_change=update_num_cols,
    )

    st.multiselect(
        "Select Date Columns",
        options=date_options,
        default=st.session_state.date_cols,
        key="date_cols_select",
        on_change=update_date_cols,
    )

    if st.session_state.target:
        #plot bar betwen ratio between classes
        st.write("Target value counts:")
        target_counts = df[st.session_state.target].value_counts()
        st.bar_chart(target_counts)
        fig = px.bar(
            x=target_counts.index.astype(str),
            y=target_counts.values,
            labels={"x": st.session_state.target, "y": "Count"},
            title="Target Value Counts"
        )
        st.plotly_chart(fig, use_container_width=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        df.isnull(),
        cbar=False,
        yticklabels=False,
        cmap='viridis',
    )
    ax.set_title("Missing Values Heatmap")

    st.pyplot(fig)
    # fig,ax = plt.subplots(figsize=(12,6))
    # msno.matrix(df, ax=ax)
    # st.pyplot(fig)
    # Optional: show current state
    # st.write("target:", st.session_state.target)
    # st.write("cat_cols:", st.session_state.cat_cols)
    # st.write("num_cols:", st.session_state.num_cols)
    # st.write("date_cols:", st.session_state.date_cols)
