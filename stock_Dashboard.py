from pickle import FALSE
import streamlit as st, pandas as pd, numpy as np, yfinance as yf
import plotly.express as px

st.title('Stock Dashboard')
ticker = st.sidebar.text_input('Ticker')
start_date = st.sidebar.date_input('Start Date')
end_date = st.sidebar.date_input('End Date')

data = yf.download(ticker,start=start_date, end=end_date)


# Flatten MultiIndex if present
if isinstance(data.columns, pd.MultiIndex):
    data.columns = [col[0] for col in data.columns]

# Pick column to plot
y_col = "Adj Close" if "Adj Close" in data.columns else "Close"

# Plot chart
fig = px.line(data, x=data.index, y=y_col, title=f"{ticker} {y_col} Price")
st.plotly_chart(fig, use_container_width=True)

pricing_data, fundametal_data, news = st.tabs(["Pricing Data", "Fundamental Data", "Top 10 News"])

# 📊 Price Movements Section under Pricing Data
with pricing_data:
    st.header("📊 Price Movements")

    # Download stock data
    data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False)

    # Handle Adj Close safely (works for both normal and MultiIndex data)
    try:
        if isinstance(data.columns, pd.MultiIndex):
            adj_close = data["Adj Close"][ticker]
        else:
            adj_close = data["Adj Close"]
    except KeyError:
        st.error("⚠️ 'Adj Close' not found in data. Try setting auto_adjust=True in yf.download.")
        st.stop()

    # Copy original data
    data2 = data.copy()

    # Add % Change column
    data2["% Change"] = adj_close.pct_change()

    # Show last 10 rows of price data
    st.write(data2.tail(10))

    # Calculate Annual Return
    daily_return = data2["% Change"].mean()
    annual_return = (1 + daily_return) ** 252 - 1 if daily_return is not None else 0

    # Show Annual Return
    st.metric(label="📈 Annual Return", value=f"{annual_return:.2%}")

    # Standard deviation (volatility)
    daily_std = data2["% Change"].std()
    annual_volatility = daily_std * (252 ** 0.5) if daily_std is not None else 0
    st.metric(label="📊 Annual Volatility (Std Dev)", value=f"{annual_volatility:.2%}")

    # Risk-adjusted return (Sharpe Ratio)
    sharpe_ratio = annual_return / annual_volatility if annual_volatility != 0 else 0
    st.metric(label="⚖️ Sharpe Ratio (Risk-Adjusted Return)", value=f"{sharpe_ratio:.2f}")


from alpha_vantage.fundamentaldata import FundamentalData

    

 # Sidebar ticker input
ticker = st.sidebar.text_input("Enter Stock Ticker", "MSFT")

 # Your Alpha Vantage API Key
key = "OW1639L639L63B5UCYYL"

# Initialize FundamentalData
fd = FundamentalData(key, output_format="pandas")

# Fundamentals section
with st.container():
     st.header("📊 Fundamentals")

try:
        # Balance Sheet
        st.subheader("📑 Balance Sheet")
        balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
        bs = balance_sheet.T[2:]
        bs.columns = list(balance_sheet.T.iloc[0])
        st.write(bs)

        # Income Statement
        st.subheader("💰 Income Statement")
        income_statement = fd.get_income_statement_annual(ticker)[0]
        is1 = income_statement.T[2:]
        is1.columns = list(income_statement.T.iloc[0])
        st.write(is1)

        # Cash Flow Statement
        st.subheader("💵 Cash Flow Statement")
        cash_flow = fd.get_cash_flow_annual(ticker)[0]
        cf = cash_flow.T[2:]
        cf.columns = list(cash_flow.T.iloc[0])
        st.write(cf)

except Exception as e:
        st.error(f"⚠️ Could not fetch fundamentals: {e}")

from stocknews import StockNews  # type: ignore
with news:
    st.header(f'News of {ticker}')
    sn = StockNews(ticker , save_news=FALSE)
    df_news = sn.read_rss()
    for i in range(10):
        st.subheader(f'News {i+1}')
        st.write(df_news['published'][i])
        st.write(df_news['summary'][i])
        title_sentiment = df_news['sentiment_title'][i]
        st.write(f'Title Sentiment {title_sentiment}')
        news_sentiment = df_news['sentiment_summary'][i]
        st.write(f'News Sentiment {news_sentiment}')

