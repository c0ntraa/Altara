import streamlit as st
import yfinance as yf
import requests
from openai import OpenAI
import time

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
NEWS_API_KEY = st.secrets["NEWS_API_KEY"]
ASSISTANT_ID = st.secrets["ASSISTANT_ID"]  # store your assistant ID here

st.set_page_config(page_title="NeuroTrade", page_icon="🧠", layout="centered")
st.title("🧠 NeuroTrade")
st.markdown("### Your AI-Powered Stock Advisor")

def get_news(stock_name):
    url = f"https://newsapi.org/v2/everything?q={stock_name}&sortBy=publishedAt&language=en&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    articles = response.json().get("articles", [])[:3]
    return [a["title"] for a in articles]

def build_prompt(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="7d")
    price = stock.info.get("currentPrice", "unknown")
    close_prices = [round(p, 2) for p in hist['Close'].tolist()][-3:]
    news = get_news(ticker)
    headlines = "\\n- " + "\\n- ".join([n[:100] for n in news])
    
    return f"""
    Stock: {ticker}
    Current price: ${price}
    3-day trend: {close_prices}
    Recent news headlines:
    {headlines}
    
    Should I Buy, Sell, or Hold? Respond with a short recommendation and brief reasoning.
    """

def ask_assistant(prompt):
    thread = client.beta.threads.create()
    
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID,
    )

    # Wait until run completes
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run_status.status == "completed":
            break
        elif run_status.status in ["failed", "cancelled", "expired"]:
            return "⚠️ Assistant failed to generate a response."
        time.sleep(1)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return messages.data[0].content[0].text.value

# Streamlit UI
ticker = st.text_input("Enter a stock symbol (e.g., AAPL, TSLA)")

if st.button("Analyze"):
    if ticker:
        with st.spinner("Asking NeuroTrade AI..."):
            prompt = build_prompt(ticker)
            result = ask_assistant(prompt)
        st.success("Analysis Complete!")
        st.markdown("### AI Recommendation")
        st.write(result)
    else:
        st.warning("Please enter a valid stock symbol.")