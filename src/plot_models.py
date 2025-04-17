import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DEBUG = True  # Set this to False to disable debug prints

def plot_line_chart(df: pd.DataFrame, stock_name: str, price_type='Close'):
    if price_type not in df.columns:
        st.error(f"'{price_type}' column not found in data.")
        return

    if DEBUG:
        st.write(f"Plotting {price_type} for {stock_name}")
        st.write("Data Preview:")
        st.dataframe(df[[price_type]].head())

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df[price_type], mode='lines', name=price_type))
    fig.update_layout(
        title=f"{stock_name} - {price_type} Price Over Time",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True, theme="streamlit")

def plot_volume_chart(df: pd.DataFrame, stock_name: str):
    if 'Volume' not in df.columns:
        st.warning("Volume column not found in data.")
        return

    if DEBUG:
        st.write(f"Plotting Volume for {stock_name}")
        st.dataframe(df[['Volume']].head())

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume'))
    fig.update_layout(
        title=f"{stock_name} - Trading Volume",
        xaxis_title="Date",
        yaxis_title="Volume",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True, theme="streamlit")

def plot_candlestick_chart(df: pd.DataFrame, stock_name: str):
    required_cols = ['Open', 'High', 'Low', 'Close']
    if not all(col in df.columns for col in required_cols):
        st.error("Candlestick chart requires Open, High, Low, and Close columns.")
        return

    if DEBUG:
        st.write(f"Plotting Candlestick for {stock_name}")
        st.dataframe(df[required_cols].head())

    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Candlestick'
    )])
    fig.update_layout(
        title=f"{stock_name} - Candlestick Chart",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_dark"
    )


    st.plotly_chart(fig, use_container_width=True, theme="streamlit")

# --- RSI Calculation ---
def calculate_rsi(df: pd.DataFrame, period: int = 14):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def plot_rsi(df: pd.DataFrame, stock_name: str, period: int):
    rsi = calculate_rsi(df, period)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=rsi, mode='lines', name=f"RSI ({period})"))
    fig.update_layout(
        title=f"{stock_name} - RSI ({period})",
        xaxis_title="Date",
        yaxis_title="RSI",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")

# --- MACD Calculation ---
def calculate_macd(df: pd.DataFrame, short_window: int, long_window: int, signal_window: int):
    short_ema = df['Close'].ewm(span=short_window, adjust=False).mean()
    long_ema = df['Close'].ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    
    return macd, signal

def plot_macd(df: pd.DataFrame, stock_name: str, short_window: int, long_window: int, signal_window: int):
    macd, signal = calculate_macd(df, short_window, long_window, signal_window)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=macd, mode='lines', name=f"MACD ({short_window}-{long_window})"))
    fig.add_trace(go.Scatter(x=df.index, y=signal, mode='lines', name=f"Signal ({signal_window})", line=dict(dash='dash')))
    fig.update_layout(
        title=f"{stock_name} - MACD ({short_window}-{long_window})",
        xaxis_title="Date",
        yaxis_title="MACD",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")


def plot_moving_average(df : pd.DataFrame, stock_name: str, ma_type: str, window: int):
    if ma_type == "SMA":
        df[f"SMA_{window}"] = df['Close'].rolling(window=window).mean()
        ma_col = f"SMA_{window}"
    elif ma_type == "EMA":
        df[f"EMA_{window}"] = df['Close'].ewm(span=window, adjust=False).mean()
        ma_col = f"EMA_{window}"
    else:
        st.error("Invalid Moving Average type selected.")
        return

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close Price'))
    fig.add_trace(go.Scatter(x=df.index, y=df[ma_col], mode='lines', name=f"{ma_type} ({window})"))
    fig.update_layout(
        title=f"{stock_name} - {ma_type} ({window})",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")