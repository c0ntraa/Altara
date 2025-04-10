import streamlit as st
import yfinance as yf
import requests
from openai import OpenAI
from openai import RateLimitError
import time

# Set up the OpenAI client with your API key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
NEWS_API_KEY = st.secrets["NEWS_API_KEY"]

# Set Streamlit page config and title
st.set_page_config(page_title="NeuroTrade", page_icon="🧠", layout="centered")
st.title("🧠 NeuroTrade")
st.markdown("### Your AI-Powered Stock Advisor")

def get_news(stock_name):
    url = f"https://newsapi.org/v2/everything?q={stock_name}&sortBy=publishedAt&language=en&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    articles = response.json().get("articles", [])[:3]
    return [a["title"] for a in articles]

def analyze_stock(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="7d")
    close_prices = [round(p, 2) for p in hist['Close'].tolist()][-3:]  # limit to 3 most recent
    price = stock.info.get("currentPrice", "unknown")
    news = get_news(ticker)
    short_news = [headline[:100] for headline in news]  # cap headline length

    prompt = f"""
    Stock: {ticker}
    Current price: ${price}
    3-day trend: {close_prices}
    Recent news headlines:
    - {short_news[0]}
    - {short_news[1]}
    - {short_news[2]}

    Based on the price trend and news sentiment, should I BUY, SELL, or HOLD this stock?
    Respond concisely and include a reason.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except RateLimitError:
        return "⚠️ Too many requests to OpenAI. Please wait a moment and try again."

# Streamlit UI
ticker = st.text_input("Enter a stock symbol (e.g., AAPL, TSLA)")

if st.button("Analyze"):
    if ticker:
        with st.spinner("Analyzing with NeuroTrade AI..."):
            result = analyze_stock(ticker)
        st.success("Analysis Complete!")
        st.markdown("### AI Recommendation")
        st.write(result)
    else:
        st.warning("Please enter a valid stock symbol.")