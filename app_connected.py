import streamlit as st
import pandas as pd
from forecast_utils import forecast_all_tickers  # <- Your forecasting logic here

st.set_page_config(page_title="ETF 7-Day Forecast", layout="wide")

st.title("📊 7-Day Forecast for ETFs")
st.markdown("This app shows 7-day predicted closing prices, volatility, and trading signals for selected ETFs.")

# Load and forecast
@st.cache_data
def load_forecast():
    df = pd.read_csv("combined_etf_data_features.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    forecast_df = forecast_all_tickers(df)
    return forecast_df

df = load_forecast()

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
