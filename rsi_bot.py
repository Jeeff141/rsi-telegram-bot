import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

# =========================
# TELEGRAM
# =========================
BOT_TOKEN = "DEIN_BOT_TOKEN"
CHAT_ID = "DEINE_CHAT_ID"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

# =========================
# RSI FUNCTION
# =========================
def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# =========================
# DATA
# =========================
btc = yf.download("BTC-USD", period="6mo", interval="1d", progress=False)
sp  = yf.download("^GSPC", period="6mo", interval="1d", progress=False)

# 👉 EXPLIZIT Close Series erzwin
