import streamlit as st
import yfinance as yf
import requests
import openai

openai.api_key = st.secrets["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"]
NEWS_API_KEY = st.secrets["9ec01c49764b48708c6b3bc27ac66bb7"]

def get_news(stock_name):
    url = f"https://newsapi.org/v2/everything?q={stock_name}&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    articles = response.json().get("articles", [])[:3]
    return [a["title"] for a in articles]

def analyze_stock(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="7d")
    price = stock.info.get("currentPrice", "unknown")
    news = get_news(ticker)

    prompt = f"""
    The stock {ticker} is currently priced at ${price}. 
    Here is the 7-day trend data: {hist['Close'].to_list()}.
    And here are recent headlines: {news}.
    
    Based on this info, should I BUY, SELL, or HOLD? Justify your answer in a few lines.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]

st.title("📈 AI Investment Advisor")
ticker = st.text_input("Enter a stock symbol (e.g., AAPL, TSLA)")

if st.button("Analyze"):
    if ticker:
        with st.spinner("Analyzing..."):
            result = analyze_stock(ticker)
        st.success("Analysis Complete!")
        st.write(result)
    else:
        st.warning("Please enter a stock symbol.")