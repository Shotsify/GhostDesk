import streamlit as st
import pandas as pd
import cot_reports as cot

st.set_page_config(page_title="Kairos Ghost Desk", layout="wide")
st.title("Kairos Ghost Desk")

st.subheader("COT Data — Raw Pull")

try:
    df = cot.cot_year(2026, cot_report_type="traders_in_financial_futures_futonly")
    st.write("Columns:", list(df.columns))
    st.write("Shape:", df.shape)
    nq = df[df["Market and Exchange Names"].str.contains("NASDAQ", case=False, na=False)]
    st.write("NQ rows found:", len(nq))
    st.dataframe(nq.head(5))
except Exception as e:
    st.error(f"Error: {e}")
