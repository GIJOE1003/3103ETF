import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn.ensemble import RandomForestRegressor

# List of features used for forecasting
feature_cols = [
    'Close', 'Volatility7', 'MA5', 'Close_MA5_diff', 'SMA20',
    'SMA50', 'SMA200', 'EMA20', 'EMA50', 'EMA200',
    'ATR7', 'ATR7_pct'
]

def update_features(df, close_value):
    df = df.copy()
    df.loc[df.index[-1], 'Close'] = close_value

    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['Close_MA5_diff'] = (df['Close'] - df['MA5']) / df['MA5'] * 100
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    df['SMA200'] = df['Close'].rolling(window=200).mean()
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()

    df['Return'] = df['Close'].pct_change().fillna(0.0)
    df['Volatility7'] = df['Return'].rolling(window=7).std().fillna(0.0)
    df['PrevClose'] = df['Close'].shift(1)
    df['TR'] = df[['High', 'Low', 'PrevClose']].apply(
        lambda x: max(x[1] - x[2], abs(x[1] - x[0]), abs(x[2] - x[0])), axis=1)
    df['ATR7'] = df['TR'].rolling(window=7).mean()
    df['ATR7_pct'] = df['ATR7'] / df['Close'] * 100

    return df

def get_next_trading_days(start_date, n_days=7):
    future_dates = []
    date = start_date + timedelta(days=1)
    while len(future_dates) < n_days:
        if date.weekday() < 5:  # Skip Saturday (5) and Sunday (6)
            future_dates.append(date)
        date += timedelta(days=1)
    return future_dates

def forecast_ticker(df, ticker):
    df_ticker = df[df['Ticker'] == ticker].sort_values(by="Date").dropna(subset=feature_cols)
    if len(df_ticker) < 200:
        return []

    X = df_ticker[feature_cols]
    y = df_ticker['Close']
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    history = df_ticker.iloc[-200:].copy()
    results = []
    prev_close = history.iloc[-1]['Close']
    last_date = history['Date'].max()
    future_dates = get_next_trading_days(last_date, n_days=7)
    future_returns = []

    for date in future_dates:
        last_row = history.iloc[-1:].copy()
        last_row['Date'] = date
        last_row['High'] = last_row['Close'] * 1.01
        last_row['Low'] = last_row['Close'] * 0.99

        history = pd.concat([history, last_row], ignore_index=True)
        history = update_features(history, last_row['Close'].values[0])

        recent_input = history.iloc[-1:][feature_cols]
        predicted_close = model.predict(recent_input)[0]
        simulated_return = (predicted_close - prev_close) / prev_close
        future_returns.append(simulated_return)
        history.loc[history.index[-1], 'Close'] = predicted_close
        prev_close = predicted_close

        total_returns = history['Return'].dropna().tolist()[-6:] + future_returns[-1:]
        predicted_volatility7 = np.std(total_returns) if len(total_returns) >= 2 else 0.0
        signal = 1 if simulated_return > 0.02 else -1 if simulated_return < -0.02 else 0

        results.append({
            'Ticker': ticker,
            'ETF Name': ETF_Names.get(ticker, ticker),
            'Date': date,
            'Predicted_Close': predicted_close,
            'Predicted_Return': simulated_return,
            'Predicted_Volatility7': predicted_volatility7,
            'Signal': signal
        })

    return results

def forecast_all_tickers(df):
    tickers = df['Ticker'].unique()
    all_results = []
    for ticker in tickers:
        all_results.extend(forecast_ticker(df, ticker))
    return pd.DataFrame(all_results)
