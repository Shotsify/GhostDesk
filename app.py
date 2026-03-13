import streamlit as st
import finnhub
from datetime import datetime, timedelta
import pandas as pd
import pytz

# --- Config ---
st.set_page_config(page_title="Kairos Ghost Desk", layout="wide")
st.title("Kairos Ghost Desk")

# --- Finnhub Client ---
client = finnhub.Client(api_key=st.secrets["FINNHUB_API_KEY"])

# --- Date Range: Current Week Monday to Friday (ET) ---
et = pytz.timezone("America/New_York")
today = datetime.now(et)
monday = today - timedelta(days=today.weekday())
friday = monday + timedelta(days=4)

date_from = monday.strftime("%Y-%m-%d")
date_to = friday.strftime("%Y-%m-%d")

# --- Fetch Economic Calendar ---
st.subheader("Economic Calendar — High Impact Events")
st.caption(f"Week of {date_from} to {date_to} (ET)")

try:
    calendar = client.economic_calendar()
    events = calendar.get("economicCalendar", [])

    if not events:
        st.warning("No calendar data returned.")
    else:
        df = pd.DataFrame(events)

        # Filter high impact only
        df = df[df["impact"] == 3]

        # Filter to current week
        df["time"] = pd.to_datetime(df["time"])
        df = df[(df["time"] >= monday.replace(tzinfo=None)) & 
                (df["time"] <= friday.replace(tzinfo=None) + timedelta(days=1))]

        # Filter USD events only
        df = df[df["country"] == "US"]

        # Select and rename columns
        df = df[["time", "event", "actual", "estimate", "prev"]].copy()
        df.columns = ["Time (ET)", "Event", "Actual", "Estimate", "Previous"]
        df["Time (ET)"] = df["Time (ET)"].dt.strftime("%a %b %d %H:%M")

        if df.empty:
            st.info("No high impact USD events this week.")
        else:
            st.dataframe(df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error fetching calendar data: {e}")
```
