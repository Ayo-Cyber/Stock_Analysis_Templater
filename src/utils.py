import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import datetime

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

        # if DEBUG:
        #     st.write("Raw Uploaded Data Preview:")
        #     st.dataframe(df.head())

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

def fetch_clean_news_details(ticker_symbol: str, max_articles: int = 5):
    """
    Fetch and display clean stock news for a given ticker symbol using Streamlit.
    """
    ticker = yf.Ticker(ticker_symbol)
    news_data = ticker.news

    if not news_data:
        st.warning(f"No news articles found for {ticker_symbol.upper()}.")
        return

    st.markdown(f"### 📰 Latest News for **{ticker_symbol.upper()}**")

    for i, article in enumerate(news_data[:max_articles], 1):
        content = article.get("content", {})

        title = content.get("title", "No Title")
        summary = content.get("summary", "No Summary Available")
        url = content.get("clickThroughUrl", {}).get("url", "")
        image_url = content.get("thumbnail", {}).get("originalUrl", "")
        provider = content.get("provider", {}).get("displayName", "Unknown Source")
        pub_date = content.get("pubDate", "No Date Provided")

        with st.container():
            if image_url:
                st.image(image_url, width=600, caption=title)
            st.markdown(f"**{i}. [{title}]({url})**")
            st.markdown(f"📝 {summary}")
            st.markdown(f"**Source:** {provider} | 🗓️ Published: {pub_date}")
            st.markdown("---")


