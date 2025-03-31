import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="ETF 7-Day Forecast", layout="wide")

st.title("📊 7-Day Forecast for ETFs")
st.markdown("This app shows 7-day predicted closing prices, volatility, and trading signals for selected ETFs.")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("7_day_forecast_all_tickers.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# Ticker selection
tickers = sorted(df['Ticker'].unique())
selected_ticker = st.selectbox("Select an ETF ticker", tickers)

# Filter data
df_ticker = df[df['Ticker'] == selected_ticker]

# Display forecast table
st.subheader(f"📅 Forecast for {selected_ticker}")
st.dataframe(df_ticker[['Date', 'Predicted_Close', 'Predicted_Return', 'Predicted_Volatility7', 'Signal']])

# Line chart of predicted close prices
st.subheader("📈 Predicted Close Price")
st.line_chart(df_ticker.set_index("Date")["Predicted_Close"])

# Line chart of predicted volatility
st.subheader("⚡ Predicted Volatility (7-day)")
st.line_chart(df_ticker.set_index("Date")["Predicted_Volatility7"])

# Signal summary
signal_counts = df_ticker['Signal'].value_counts().rename({-1: 'Sell', 0: 'Hold', 1: 'Buy'})
st.subheader("🔁 Signal Breakdown")
st.bar_chart(signal_counts)
