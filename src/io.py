from __future__ import annotations
import os
import streamlit as st
import polars as pl
import pandas as pd

SUPPORTED = (".csv", ".parquet")

@st.cache_data
def read_df(data) -> pd.DataFrame:
    return pd.read_csv(data)

# def maybe_convert_to_parquet(path: str, out_dir: str = "artifacts") -> str:
#     """
#     If CSV, convert to Parquet once for faster reload later.
#     Returns new path (parquet) or original path if already parquet.
#     """
#     os.makedirs(out_dir, exist_ok=True)
#     ext = os.path.splitext(path.lower())[1]
#     if ext != ".csv":
#         return path

#     df = read_df(path)
#     base = os.path.splitext(os.path.basename(path))[0]
#     out_path = os.path.join(out_dir, f"{base}.parquet")
#     df.write_parquet(out_path)
#     return out_path
