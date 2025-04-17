import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

DEBUG = True  # Set this to False to disable debug prints

@st.cache_data
def load_data_from_file(file, stock_name=None, date_column=None):
    """
    Load stock data from an uploaded file (CSV/Excel).
    """
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file)
        else:
            st.error("Unsupported file type. Please upload a CSV or Excel file.")
            return None

        if DEBUG:
            st.write("Raw Uploaded Data Preview:")
            st.dataframe(df.head())

        if date_column and date_column in df.columns:
            df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
            df.dropna(subset=[date_column], inplace=True)
            df.set_index(date_column, inplace=True)

        stock_label = stock_name if stock_name else file.name.rsplit('.', 1)[0]

        return {"name": stock_label, "data": df}

    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None


def _flatten_columns(df):
    """
    Flattens MultiIndex columns in a DataFrame if present.
    """
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

@st.cache_data
def load_data_from_ticker(ticker, start_date, end_date):
    """
    Load stock data from Yahoo Finance using a ticker and date range.
    Automatically flattens column MultiIndex if needed.
    """
    try:
        df = yf.download(ticker, start=start_date, end=end_date)
        if df.empty:
            st.warning("No data returned for the selected range. Please check the ticker or dates.")
            return None

        # Fix MultiIndex columns if needed
        df = _flatten_columns(df)

        return {"name": ticker.upper(), "data": df}

    except Exception as e:
        st.error(f"Error fetching data from Yahoo Finance: {e}")
        return None


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