import yfinance as yf
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

btc = yf.download("BTC-USD", period="3mo", interval="1d")
sp = yf.download("^GSPC", period="3mo", interval="1d")

btc_rsi = rsi(btc["Close"]).iloc[-1]
sp_rsi = rsi(sp["Close"]).iloc[-1]

message = (
    f"📊 Daily RSI\n\n"
    f"BTC: {btc_rsi:.1f}\n"
    f"S&P500: {sp_rsi:.1f}"
)

send(message)
