import yfinance as yf
import pandas as pd
import numpy as np
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

# =========================
# DAILY RSI
# =========================
btc["RSI_D"] = rsi(btc["Close"])
sp["RSI_D"]  = rsi(sp["Close"])

btc_rsi_d = float(btc["RSI_D"].dropna().iloc[-1])
sp_rsi_d  = float(sp["RSI_D"].dropna().iloc[-1])

# =========================
# WEEKLY RSI
# =========================
btc_weekly = btc["Close"].resample("W").last()
sp_weekly  = sp["Close"].resample("W").last()

btc_rsi_w = float(rsi(btc_weekly).dropna().iloc[-1])
sp_rsi_w  = float(rsi(sp_weekly).dropna().iloc[-1])

# =========================
# EMA + DCA SCORE (SP500)
# =========================
sp["EMA50"]  = sp["Close"].ewm(span=50).mean()
sp["EMA200"] = sp["Close"].ewm(span=200).mean()

cond_rsi   = sp_rsi_d < 40
cond_ema50 = sp["Close"].iloc[-1] < sp["EMA50"].iloc[-1]
cond_ema200= sp["Close"].iloc[-1] < sp["EMA200"].iloc[-1]

dca_score = sum([cond_rsi, cond_ema50, cond_ema200])

# =========================
# MESSAGE
# =========================
now = datetime.now().strftime("%d.%m.%Y %H:%M")

msg = (
    f"📊 *Market Update* ({now})\n\n"
    f"🟠 *Bitcoin*\n"
    f"• RSI Daily: `{btc_rsi_d:.1f}`\n"
    f"• RSI Weekly: `{btc_rsi_w:.1f}`\n\n"
    f"🔵 *S&P 500*\n"
    f"• RSI Daily: `{sp_rsi_d:.1f}`\n"
    f"• RSI Weekly: `{sp_rsi_w:.1f}`\n\n"
    f"📈 *DCA Score (SP500)*: `{dca_score}/3`\n"
)

send_telegram(msg)
