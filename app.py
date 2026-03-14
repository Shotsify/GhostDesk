import streamlit as st
import pandas as pd
import requests
from io import StringIO

st.set_page_config(page_title="Kairos Ghost Desk", layout="wide")
st.title("Kairos Ghost Desk")

st.subheader("COT Data — NQ Positioning")

try:
    url = "https://publicreporting.cftc.gov/resource/gpe5-46if.csv?$limit=50000&$where=market_and_exchange_names=%27NASDAQ-100%20Consolidated%20-%20CHICAGO%20MERCANTILE%20EXCHANGE%27&$order=report_date_as_yyyy_mm_dd%20DESC"

    response = requests.get(url)
    df = pd.read_csv(StringIO(response.text))

    st.write("Status code:", response.status_code)
    st.write("Rows returned:", len(df))
    st.write("Columns:", list(df.columns))
    st.dataframe(df.head(5))

except Exception as e:
    st.error(f"Error: {e}")
