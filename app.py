import streamlit as st
from datetime import date
import plotly.graph_objects as go

from src.utils import (
    load_data_from_file,
    load_data_from_ticker,
    fetch_clean_news_details  
)

from src.plot_models import (
    plot_moving_average,
    plot_macd,
    plot_rsi,
    plot_line_chart,
    plot_candlestick_chart,
    plot_volume_chart,
)

# Set page config
st.set_page_config(page_title="Stock Analyzer")
st.title("📊 Stock Data Analyzer")

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a page to navigate:", ["📈 Data Preview", "⚙️ Core Analysis", "📰 Stock News"])

# --- Visualizations Page ---
if page == "📈 Data Preview":
    mode = st.radio("Select data input method", ["📁 Upload File", "🔍 Search by Ticker"])

    # --- FILE UPLOAD MODE ---
    if mode == "📁 Upload File":
        uploaded_file = st.file_uploader("Upload stock data (CSV or Excel)", type=["csv", "xls", "xlsx"])
        stock_name_input = st.text_input("Optional: Enter a stock name or label")
        date_column = st.text_input("Enter the date column name (e.g., 'Date')")

        if uploaded_file and date_column:
            result = load_data_from_file(uploaded_file, stock_name_input, date_column)
            if result:
                st.session_state['data'] = result['data']
                st.session_state['stock_name'] = result['name']
                st.success(f"✅ Loaded data for {result['name']}")
                st.dataframe(result['data'].head())

    # --- TICKER SEARCH MODE ---
    elif mode == "🔍 Search by Ticker":
        ticker = st.text_input("Enter a stock ticker symbol (e.g., AAPL, MSFT)")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date(2022, 1, 1))
        with col2:
            end_date = st.date_input("End Date", value=date.today())

        if st.button("Fetch Data") and ticker:
            result = load_data_from_ticker(ticker, start_date, end_date)
            if result:
                st.session_state['data'] = result['data']
                st.session_state['stock_name'] = result['name']
                st.success(f"✅ Fetched data for {result['name']} from Yahoo Finance")
                st.dataframe(result['data'].head())

    # --- Shared Visualization Section ---
    if 'data' in st.session_state and 'stock_name' in st.session_state:
        df = st.session_state['data']
        stock_name = st.session_state['stock_name']

        st.subheader("📈 Visualizations")
        viz_type = st.selectbox("Select a chart type", ["Line Chart", "Candlestick Chart", "Volume Chart"])

        if viz_type == "Line Chart":
            price_col = st.selectbox("Select price type", ["Close", "Open", "High", "Low"])
            plot_line_chart(df, stock_name, price_col)

        elif viz_type == "Candlestick Chart":
            plot_candlestick_chart(df, stock_name)

        elif viz_type == "Volume Chart":
            plot_volume_chart(df, stock_name)

# --- Core Analysis Page ---
elif page == "⚙️ Core Analysis":
    if 'data' in st.session_state and 'stock_name' in st.session_state:
        df = st.session_state['data']
        stock_name = st.session_state['stock_name']

        st.subheader("🧮 Core Technical Analysis")
        analysis_type = st.selectbox("Select an analysis type", ["Moving Average", "RSI", "MACD"])

        # --- Moving Average ---
        if analysis_type == "Moving Average":
            ma_type = st.selectbox("Select Moving Average Type", ["SMA", "EMA"])
            window = st.slider("Select Window Size", min_value=5, max_value=200, value=20, step=1)
            plot_moving_average(df, stock_name, ma_type, window)

        # --- RSI ---
        elif analysis_type == "RSI":
            period = st.slider("RSI Period", min_value=5, max_value=50, value=14, step=1)
            plot_rsi(df, stock_name, period)

        # --- MACD ---
        elif analysis_type == "MACD":
            short_window = st.slider("MACD Short Window", min_value=5, max_value=50, value=12, step=1)
            long_window = st.slider("MACD Long Window", min_value=50, max_value=200, value=26, step=1)
            signal_window = st.slider("MACD Signal Window", min_value=5, max_value=50, value=9, step=1)
            plot_macd(df, stock_name, short_window, long_window, signal_window)

# --- Stock News Page ---
elif page == "📰 Stock News":
    st.subheader("📰 Latest Stock News")
    
    # Enter ticker symbol
    ticker_symbol = st.text_input("Enter a stock ticker symbol (e.g., AAPL, MSFT)")

    if ticker_symbol:
        fetch_clean_news_details(ticker_symbol.upper())  

# --- Footer ---
st.markdown("_____")
st.markdown("Made with ❤️ by Atunrase Ayomide .")