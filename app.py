import streamlit as st

# --- App Config ---
st.set_page_config(page_title="ETF Forecast Dashboard", layout="wide")

import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime

# --- Load Data ---
@st.cache_data
def load_data():
    prices = pd.read_csv("future_prices.csv", parse_dates=["Date"])
    signals = pd.read_csv("signals.csv", parse_dates=["Date"])
    volatility = pd.read_csv("volatility.csv", parse_dates=["Date"])
    history = pd.read_csv("historical_prices.csv", parse_dates=["Date"])
    return prices, signals, volatility, history

pred_prices, pred_signals, pred_volatility, hist_prices = load_data()

st.title("📈 ETF Forecast Dashboard")

# --- ETF Selector ---
tickers = sorted(pred_prices["Ticker"].unique())
selected_ticker = st.selectbox("Select an ETF:", tickers)

# --- Filter Data ---
hist = hist_prices[hist_prices["Ticker"] == selected_ticker].copy()
pred = pred_prices[pred_prices["Ticker"] == selected_ticker].copy()
signals = pred_signals[pred_signals["Ticker"] == selected_ticker].copy()
vols = pred_volatility[pred_volatility["Ticker"] == selected_ticker].copy()

# --- Price Chart ---
st.subheader(f"Price History & Forecast: {selected_ticker}")
if not hist.empty:
    hist_trimmed = hist.sort_values("Date").tail(60)[["Date", "Close"]].rename(columns={"Close": "Price"})
    pred_trimmed = pred[["Date", "Predicted_Price"]].rename(columns={"Predicted_Price": "Price"})
    price_chart_data = pd.concat([hist_trimmed, pred_trimmed])
    price_chart_data["Type"] = ["Historical"] * len(hist_trimmed) + ["Forecast"] * len(pred_trimmed)

    fig = px.line(price_chart_data, x="Date", y="Price", color="Type",
                  title=f"{selected_ticker} Price Trend",
                  markers=True)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning(f"No historical price data available for {selected_ticker}.")

# --- Signals ---
st.subheader("📍 Investment Signals (Next 7 Days)")
signal_map = {1: "Buy 📈", 0: "Hold ⏸️", -1: "Sell 🔻"}
signals["Signal_Text"] = signals["Signal"].map(signal_map)
st.dataframe(signals[["Date", "Signal_Text"]].rename(columns={"Signal_Text": "Signal"}), use_container_width=True)

# --- Volatility Forecast ---
st.subheader("🔄 Predicted Volatility (Next 7 Days)")
st.dataframe(vols.rename(columns={"Predicted_Volatility": "Volatility"}), use_container_width=True)

# --- Footer ---
st.markdown("---")
st.caption("Developed as part of ETF Capstone Project | Forecasts are model-based and for educational purposes only.")
