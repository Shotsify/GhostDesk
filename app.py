import streamlit as st
import requests
import pytz
from datetime import datetime, timedelta

st.set_page_config(page_title="Kairos Ghost Desk", layout="wide")
st.title("Kairos Ghost Desk")

API_KEY = st.secrets["FINNHUB_API_KEY"]

et = pytz.timezone("America/New_York")
today = datetime.now(et)
monday = today - timedelta(days=today.weekday())
friday = monday + timedelta(days=4)
date_from = monday.strftime("%Y-%m-%d")
date_to = friday.strftime("%Y-%m-%d")

st.subheader("Economic Calendar — Raw API Response")
st.caption(f"Week of {date_from} to {date_to} (ET)")

url = f"https://finnhub.io/api/v1/calendar/economic?from={date_from}&to={date_to}&token={API_KEY}"
st.write("Requesting URL:", url.replace(API_KEY, "***"))

response = requests.get(url)
st.write("Status code:", response.status_code)
st.write("Raw response:", response.json())
