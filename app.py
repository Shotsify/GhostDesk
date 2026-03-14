import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import StringIO
import pytz
from datetime import datetime
import yfinance as yf
import numpy as np

st.set_page_config(page_title="Kairos Ghost Desk", layout="wide")
st.title("Kairos Ghost Desk")

et = pytz.timezone("America/New_York")
today = datetime.now(et)
st.caption(f"Last loaded: {today.strftime('%A, %B %d %Y — %I:%M %p ET')}")

# --- COT DATA ---
st.subheader("COT — NQ Nasdaq-100 Consolidated Positioning")

try:
    url = "https://publicreporting.cftc.gov/resource/gpe5-46if.csv?$limit=50000&$where=market_and_exchange_names=%27NASDAQ-100%20Consolidated%20-%20CHICAGO%20MERCANTILE%20EXCHANGE%27&$order=report_date_as_yyyy_mm_dd%20DESC"
    response = requests.get(url, timeout=30)
    df = pd.read_csv(StringIO(response.text))
    df["report_date_as_yyyy_mm_dd"] = pd.to_datetime(df["report_date_as_yyyy_mm_dd"])
    df = df.sort_values("report_date_as_yyyy_mm_dd", ascending=False).reset_index(drop=True)
    latest = df.iloc[0]
    prev = df.iloc[1]
    report_date = latest["report_date_as_yyyy_mm_dd"].strftime("%B %d, %Y")
    st.caption(f"Report date: {report_date} (released Friday, 3:30pm ET)")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Dealer / Intermediary**")
        d_long = int(latest["dealer_positions_long_all"])
        d_short = int(latest["dealer_positions_short_all"])
        d_net = d_long - d_short
        d_net_prev = int(prev["dealer_positions_long_all"]) - int(prev["dealer_positions_short_all"])
        st.metric("Net Position", f"{d_net:,}", delta=f"{d_net - d_net_prev:,}")
        st.write(f"Long: {d_long:,} | Short: {d_short:,}")
    with col2:
        st.markdown("**Asset Manager / Institutional**")
        a_long = int(latest["asset_mgr_positions_long"])
        a_short = int(latest["asset_mgr_positions_short"])
        a_net = a_long - a_short
        a_net_prev = int(prev["asset_mgr_positions_long"]) - int(prev["asset_mgr_positions_short"])
        st.metric("Net Position", f"{a_net:,}", delta=f"{a_net - a_net_prev:,}")
        st.write(f"Long: {a_long:,} | Short: {a_short:,}")
    with col3:
        st.markdown("**Leveraged Funds**")
        l_long = int(latest["lev_money_positions_long"])
        l_short = int(latest["lev_money_positions_short"])
        l_net = l_long - l_short
        l_net_prev = int(prev["lev_money_positions_long"]) - int(prev["lev_money_positions_short"])
        st.metric("Net Position", f"{l_net:,}", delta=f"{l_net - l_net_prev:,}")
        st.write(f"Long: {l_long:,} | Short: {l_short:,}")

    st.divider()

    hist = df.head(16).copy()
    hist["Dealer Net"] = hist["dealer_positions_long_all"].astype(int) - hist["dealer_positions_short_all"].astype(int)
    hist["Asset Mgr Net"] = hist["asset_mgr_positions_long"].astype(int) - hist["asset_mgr_positions_short"].astype(int)
    hist["Lev Funds Net"] = hist["lev_money_positions_long"].astype(int) - hist["lev_money_positions_short"].astype(int)
    hist = hist.sort_values("report_date_as_yyyy_mm_dd", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist["report_date_as_yyyy_mm_dd"], y=hist["Asset Mgr Net"], name="Asset Manager", line=dict(color="#3B8BD4", width=2)))
    fig.add_trace(go.Scatter(x=hist["report_date_as_yyyy_mm_dd"], y=hist["Lev Funds Net"], name="Leveraged Funds", line=dict(color="#EF9F27", width=2)))
    fig.add_trace(go.Scatter(x=hist["report_date_as_yyyy_mm_dd"], y=hist["Dealer Net"], name="Dealer", line=dict(color="#888780", width=1.5, dash="dot")))
    fig.add_hline(y=0, line_color="rgba(255,255,255,0.2)", line_width=1)
    fig.update_layout(
        title="16-Week Net Positioning Trend",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Net Contracts"),
        height=380
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Last 8 Weeks — Net Positioning**")
    table = df.head(8).copy()
    table["Dealer Net"] = table["dealer_positions_long_all"].astype(int) - table["dealer_positions_short_all"].astype(int)
    table["Asset Mgr Net"] = table["asset_mgr_positions_long"].astype(int) - table["asset_mgr_positions_short"].astype(int)
    table["Lev Funds Net"] = table["lev_money_positions_long"].astype(int) - table["lev_money_positions_short"].astype(int)
    table["Date"] = table["report_date_as_yyyy_mm_dd"].dt.strftime("%b %d")
    table = table[["Date", "Dealer Net", "Asset Mgr Net", "Lev Funds Net"]].set_index("Date")
    st.dataframe(table, use_container_width=True)

except Exception as e:
    st.error(f"COT Error: {e}")

# --- ECONOMIC CALENDAR ---
st.divider()
st.subheader("Weekly Red Folder Events")

# --- ET CLOCK ---
st.divider()
st.subheader("Current Time — Eastern")

now_et = datetime.now(et)
hour = now_et.hour % 12
minute = now_et.minute
second = now_et.second

import math
hour_angle = math.radians((hour * 30) + (minute * 0.5) - 90)
minute_angle = math.radians((minute * 6) + (second * 0.1) - 90)
second_angle = math.radians((second * 6) - 90)

cx, cy, r = 100, 100, 80

def hand(angle, length, width, color):
    x = cx + length * math.cos(angle)
    y = cy + length * math.sin(angle)
    return f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>'

hour_marks = ""
for i in range(12):
    a = math.radians(i * 30)
    x1 = cx + 70 * math.cos(a)
    y1 = cy + 70 * math.sin(a)
    x2 = cx + 78 * math.cos(a)
    y2 = cy + 78 * math.sin(a)
    w = 3 if i % 3 == 0 else 1.5
    hour_marks += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#888780" stroke-width="{w}"/>'

svg = f"""
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#444" stroke-width="2"/>
  {hour_marks}
  {hand(hour_angle, 45, 4, "#ffffff")}
  {hand(minute_angle, 60, 2.5, "#ffffff")}
  {hand(second_angle, 65, 1, "#EF9F27")}
  <circle cx="{cx}" cy="{cy}" r="4" fill="#EF9F27"/>
  <text x="{cx}" y="{cy + 100}" text-anchor="middle" fill="#888780" font-size="13" font-family="sans-serif">{now_et.strftime("%I:%M:%S %p ET")}</text>
</svg>
"""

col_clock, col_spacer = st.columns([1, 4])
with col_clock:
    st.markdown(svg, unsafe_allow_html=True)
try:
    import xml.etree.ElementTree as ET
    ff_url = "https://nfs.faireconomy.media/ff_calendar_thisweek.xml"
    ff_response = requests.get(ff_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    root = ET.fromstring(ff_response.content)

    events = []
    for event in root.findall("event"):
        country = event.findtext("country", "").strip()
        impact = event.findtext("impact", "").strip()
        if country != "USD" or impact != "High":
            continue
        title = event.findtext("title", "").strip()
        date = event.findtext("date", "").strip()
        time_et = event.findtext("time", "").strip()
        forecast = event.findtext("forecast", "").strip()
        previous = event.findtext("previous", "").strip()
        events.append({
            "Event": title,
            "Date": date,
            "Time (ET)": time_et,
            "Forecast": forecast,
            "Previous": previous
        })

    if not events:
        st.info("No high impact USD events this week.")
    else:
        ff_df = pd.DataFrame(events)
        st.dataframe(ff_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Calendar Error: {e}")
# --- SEASONAL TENDENCIES ---
st.divider()
st.subheader("NQ Seasonal Tendencies")
st.caption("Calculated from NQ futures price history via Yahoo Finance (NQ=F)")

@st.cache_data(ttl=86400)
def load_seasonal_data():
    ticker = yf.Ticker("NQ=F")
    raw = ticker.history(period="20y")
    raw.index = pd.to_datetime(raw.index)
    raw = raw[["Close"]].copy()
    raw["Return"] = raw["Close"].pct_change()
    raw["Month"] = raw.index.month
    raw["Week"] = raw.index.isocalendar().week.astype(int)
    raw["Year"] = raw.index.year
    return raw

try:
    with st.spinner("Loading seasonal data..."):
        raw = load_seasonal_data()

    now = datetime.now()
    current_month = now.month
    current_week = now.isocalendar()[1]
    years_5 = now.year - 5
    years_10 = now.year - 10
    years_15 = now.year - 15

    month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    def monthly_avg(data, start_year):
        subset = data[data["Year"] >= start_year]
        monthly = subset.groupby(["Year","Month"])["Return"].sum().reset_index()
        avg = monthly.groupby("Month")["Return"].mean() * 100
        pct_pos = monthly.groupby("Month")["Return"].apply(lambda x: (x > 0).mean() * 100)
        return avg, pct_pos

    avg_5m, pos_5m = monthly_avg(raw, years_5)
    avg_10m, pos_10m = monthly_avg(raw, years_10)
    avg_15m, pos_15m = monthly_avg(raw, years_15)

    months = list(range(1, 13))
    fig_m = go.Figure()
    fig_m.add_trace(go.Bar(x=month_names, y=[avg_15m.get(m, 0) for m in months], name="15Y Avg", marker_color="#4a4a4a", opacity=0.7))
    fig_m.add_trace(go.Bar(x=month_names, y=[avg_10m.get(m, 0) for m in months], name="10Y Avg", marker_color="#888780", opacity=0.85))
    fig_m.add_trace(go.Bar(x=month_names, y=[avg_5m.get(m, 0) for m in months], name="5Y Avg", marker_color="#3B8BD4"))
    fig_m.add_vline(x=current_month - 1, line_color="#EF9F27", line_width=2, annotation_text="Now", annotation_position="top")
    fig_m.add_hline(y=0, line_color="rgba(255,255,255,0.2)", line_width=1)
    fig_m.update_layout(
        title="Monthly Seasonal Returns — 5Y / 10Y / 15Y",
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Avg Return %"),
        height=380
    )
    st.plotly_chart(fig_m, use_container_width=True)

    st.markdown("**Monthly Detail — Current Month Highlighted**")
    month_table = pd.DataFrame({
        "Month": month_names,
        "5Y Avg %": [f"{avg_5m.get(m, 0):.2f}%" for m in months],
        "5Y Pos": [f"{pos_5m.get(m, 0):.0f}%" for m in months],
        "10Y Avg %": [f"{avg_10m.get(m, 0):.2f}%" for m in months],
        "10Y Pos": [f"{pos_10m.get(m, 0):.0f}%" for m in months],
        "15Y Avg %": [f"{avg_15m.get(m, 0):.2f}%" for m in months],
        "15Y Pos": [f"{pos_15m.get(m, 0):.0f}%" for m in months],
    })
    st.dataframe(
        month_table.style.apply(
            lambda row: ["background-color: rgba(59,139,212,0.2)" if row.name == current_month - 1 else "" for _ in row],
            axis=1
        ),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    def weekly_avg(data, start_year):
        subset = data[data["Year"] >= start_year]
        weekly = subset.groupby(["Year","Week"])["Return"].sum().reset_index()
        avg = weekly.groupby("Week")["Return"].mean() * 100
        pct_pos = weekly.groupby("Week")["Return"].apply(lambda x: (x > 0).mean() * 100)
        return avg, pct_pos

    avg_5w, pos_5w = weekly_avg(raw, years_5)
    avg_10w, pos_10w = weekly_avg(raw, years_10)
    avg_15w, pos_15w = weekly_avg(raw, years_15)

    weeks = sorted(avg_15w.index.tolist())
    fig_w = go.Figure()
    fig_w.add_trace(go.Scatter(x=weeks, y=[avg_15w.get(w, 0) for w in weeks], name="15Y Avg", line=dict(color="#4a4a4a", width=1.5)))
    fig_w.add_trace(go.Scatter(x=weeks, y=[avg_10w.get(w, 0) for w in weeks], name="10Y Avg", line=dict(color="#888780", width=1.5)))
    fig_w.add_trace(go.Scatter(x=weeks, y=[avg_5w.get(w, 0) for w in weeks], name="5Y Avg", line=dict(color="#3B8BD4", width=2)))
    fig_w.add_vline(x=current_week, line_color="#EF9F27", line_width=2, annotation_text="Now", annotation_position="top right")
    fig_w.add_hline(y=0, line_color="rgba(255,255,255,0.2)", line_width=1)
    fig_w.update_layout(
        title="Weekly Seasonal Returns — 5Y / 10Y / 15Y",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Week of Year"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Avg Return %"),
        height=380
    )
    st.plotly_chart(fig_w, use_container_width=True)

    st.markdown("**Weekly Detail — Current Week & Surrounding 4 Weeks**")
    week_range = range(max(1, current_week - 4), min(53, current_week + 5))
    week_table = pd.DataFrame({
        "Week": list(week_range),
        "5Y Avg %": [f"{avg_5w.get(w, 0):.2f}%" for w in week_range],
        "5Y Pos": [f"{pos_5w.get(w, 0):.0f}%" for w in week_range],
        "10Y Avg %": [f"{avg_10w.get(w, 0):.2f}%" for w in week_range],
        "10Y Pos": [f"{pos_10w.get(w, 0):.0f}%" for w in week_range],
        "15Y Avg %": [f"{avg_15w.get(w, 0):.2f}%" for w in week_range],
        "15Y Pos": [f"{pos_15w.get(w, 0):.0f}%" for w in week_range],
    })
    st.dataframe(
        week_table.style.apply(
            lambda row: ["background-color: rgba(59,139,212,0.2)" if row["Week"] == current_week else "" for _ in row],
            axis=1
        ),
        use_container_width=True,
        hide_index=True
    )

except Exception as e:
    st.error(f"Seasonal Error: {e}")
