import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
from pydantic import BaseModel, ValidationError, field_validator, model_validator
from typing import Optional

DEBUG = True  # Set this to False to disable debug prints

REQUIRED_COLUMNS = ["Open", "High", "Low"]
ALTERNATIVE_CLOSE_COLUMNS = ["Close", "Adj Close", "Price"]

class StockDataModel(BaseModel):
    Open: float
    High: float
    Low: float
    Close: Optional[float] = None
    Price: Optional[float] = None

    class Config:
        extra = "ignore"

    @field_validator('*', mode='before')
    @classmethod
    def ensure_numeric(cls, v):
        if isinstance(v, str):
            v = v.replace(",", "").replace("!", "").replace("$", "")
        if v is None or v == "":
            return None
        try:
            return float(v)
        except ValueError:
            raise ValueError(f"Value '{v}' is not convertible to float.")

    @model_validator(mode='after')
    def check_close_or_price(cls, values):
        if values.Close is None and values.Price is None:
            raise ValueError("At least one of 'Close' or 'Price' must be present.")
        return values



def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace(r"[^\d\.-]", "", regex=True)
        try:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        except Exception as e:
            if DEBUG:
                st.warning(f"Could not convert column {col}: {e}")
    return df


def validate_stock_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = clean_dataframe(df)

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")

    # Rename Adj Close → Price to simplify validation
    for alt_col in ["Adj Close"]:
        if alt_col in df.columns and "Price" not in df.columns:
            df.rename(columns={alt_col: "Price"}, inplace=True)

    if not any(col in df.columns for col in ALTERNATIVE_CLOSE_COLUMNS):
        raise ValueError("At least one of the following columns must exist: Close, Adj Close, Price")

    for index, row in df.iterrows():
        try:
            StockDataModel(**row.to_dict())
        except ValidationError as ve:
            raise ValueError(f"Row {index} failed validation:\n{ve}")

    return df


@st.cache_data
def load_data_from_file(file, stock_name=None, date_column=None):
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file)
        else:
            st.error("Unsupported file type. Please upload a CSV or Excel file.")
            return None

        if date_column and date_column in df.columns:
            df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
            df.dropna(subset=[date_column], inplace=True)
            df.set_index(date_column, inplace=True)

        df = validate_stock_dataframe(df)

        stock_label = stock_name if stock_name else file.name.rsplit('.', 1)[0]
        return {"name": stock_label, "data": df}

    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None


def _flatten_columns(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


@st.cache_data
def load_data_from_ticker(ticker, start_date, end_date):
    try:
        df = yf.download(ticker, start=start_date, end=end_date)
        if df.empty:
            st.warning("No data returned for the selected range. Please check the ticker or dates.")
            return None

        df = _flatten_columns(df)
        df = validate_stock_dataframe(df)

        return {"name": ticker.upper(), "data": df}

    except Exception as e:
        st.error(f"Error fetching data from Yahoo Finance: {e}")
        return None


def fetch_clean_news_details(ticker_symbol: str, max_articles: int = 5):
    try:
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
    except Exception as e:
        st.error(f"Error fetching news: {e}")
