import streamlit as st
import requests
import pandas as pd
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

st.subheader("Economic Calendar — High Impact Events")
st.caption(f"Week of {date_from} to {date_to} (ET)")

try:
    url = f"https://finnhub.io/api/v1/calendar/economic?token={API_KEY}"
    response = requests.get(url)
    data = response.json()

    events = data.get("economicCalendar", [])

    if not events:
        st.warning("No calendar data returned.")
    else:
        df = pd.DataFrame(events)
        st.write("Raw data sample:", df.head())

except Exception as e:
    st.error(f"Error: {e}")
