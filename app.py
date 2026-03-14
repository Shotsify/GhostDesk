import streamlit as st
import pandas as pd
import requests
from io import StringIO

st.set_page_config(page_title="Kairos Ghost Desk", layout="wide")
st.title("Kairos Ghost Desk")

st.subheader("COT — NQ Nasdaq-100 Consolidated Positioning")

try:
    url = "https://publicreporting.cftc.gov/resource/gpe5-46if.csv?$limit=50000&$where=market_and_exchange_names=%27NASDAQ-100%20Consolidated%20-%20CHICAGO%20MERCANTILE%20EXCHANGE%27&$order=report_date_as_yyyy_mm_dd%20DESC"
    response = requests.get(url)
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
        d_delta = d_net - d_net_prev
        st.metric("Net Position", f"{d_net:,}", delta=f"{d_delta:,}")
        st.write(f"Long: {d_long:,} | Short: {d_short:,}")

    with col2:
        st.markdown("**Asset Manager / Institutional**")
        a_long = int(latest["asset_mgr_positions_long"])
        a_short = int(latest["asset_mgr_positions_short"])
        a_net = a_long - a_short
        a_net_prev = int(prev["asset_mgr_positions_long"]) - int(prev["asset_mgr_positions_short"])
        a_delta = a_net - a_net_prev
        st.metric("Net Position", f"{a_net:,}", delta=f"{a_delta:,}")
        st.write(f"Long: {a_long:,} | Short: {a_short:,}")

    with col3:
        st.markdown("**Leveraged Funds**")
        l_long = int(latest["lev_money_positions_long"])
        l_short = int(latest["lev_money_positions_short"])
        l_net = l_long - l_short
        l_net_prev = int(prev["lev_money_positions_long"]) - int(prev["lev_money_positions_short"])
        l_delta = l_net - l_net_prev
        st.metric("Net Position", f"{l_net:,}", delta=f"{l_delta:,}")
        st.write(f"Long: {l_long:,} | Short: {l_short:,}")

    st.divider()
    st.markdown("**Last 8 Weeks — Net Positioning**")

    hist = df.head(8).copy()
    hist["Dealer Net"] = hist["dealer_positions_long_all"].astype(int) - hist["dealer_positions_short_all"].astype(int)
    hist["Asset Mgr Net"] = hist["asset_mgr_positions_long"].astype(int) - hist["asset_mgr_positions_short"].astype(int)
    hist["Lev Funds Net"] = hist["lev_money_positions_long"].astype(int) - hist["lev_money_positions_short"].astype(int)
    hist["Date"] = hist["report_date_as_yyyy_mm_dd"].dt.strftime("%b %d")
    hist = hist[["Date", "Dealer Net", "Asset Mgr Net", "Lev Funds Net"]].set_index("Date")

    st.dataframe(hist, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
