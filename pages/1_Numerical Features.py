import os
import streamlit as st
import pandas as pd
from src.state import ensure_state
from src.io import read_df
import plotly.express as px
import matplotlib.pyplot as plt

ensure_state()

num_cols = st.session_state.num_cols
df = st.session_state.df

st.set_page_config("Numerical Features",layout="wide")

#df.describe
st.dataframe(df[num_cols].describe(percentiles=[0.1,0.25, 0.5, 0.75,0.9]).T)

st.header("Histograms")
cols = st.columns(3)
for i, col in enumerate(num_cols):
    # fig = px.histogram(df, x=col, nbins=50, title=f"{col}")
    # # st.plotly_chart(fig, use_container_width=True)
    fig, ax = plt.subplots()
    ax.hist(df[col], bins=30)
    ax.set_title(col)
    cols[i % 3].pyplot(fig)
    # cols[i % 3].plotly_chart(fig, use_container_width=True)
