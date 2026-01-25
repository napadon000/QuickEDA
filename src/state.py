import streamlit as st

def ensure_state():
    # if "dataset_path" not in st.session_state:
    #     st.session_state.dataset_path = None
    if "dataset" not in st.session_state:
        st.session_state.dataset = None
    if "df_cache_key" not in st.session_state:
        st.session_state.df_cache_key = None
    if "features" not in st.session_state:
        # list of feature definitions (safe JSON-ish dicts)
        st.session_state.features = []
    if "filters" not in st.session_state:
        # simple filters: dict[col] = (op, value)
        st.session_state.filters = {}
