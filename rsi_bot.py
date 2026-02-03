import yfinance as yf
import requests
import os
import pandas as pd

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

# ==========================
# DATA
# ==========================
btc = yf.download("BTC-USD", period="6mo", interval="1d", progress=False)
sp = yf.download("^GSPC", period="6mo", interval="1d", progress=False)

# ==========================
# RSI
# ==========================
btc["RSI_D"] = rsi(btc["Close"])
sp["RSI_D"]  = rsi(sp["Close"])

btc_weekly = btc["Close"].resample("W").last()
sp_weekly  = sp["Close"].resample("W").last()

btc_rsi_w = rsi(btc_weekly).iloc[-1]
sp_rsi_w  = rsi(sp_weekly).iloc[-1]

btc_rsi_d = btc["RSI_D"].iloc[-1]
sp_rsi_d  = sp["RSI_D"].iloc[-1]

# ==========================
# EMA & DCA SCORE (SP500)
# ==========================
sp["EMA50"]  = sp["Close"].ewm(span=50).mean()
sp["EMA200"] = sp["Close"].ewm(span=200).mean()

cond_rsi    = sp_rsi_d < 40
cond_ema50  = sp["Close"].iloc[-1] < sp["EMA50"].iloc[-1]
cond_ema200 = sp["Close"].iloc[-1] < sp["EMA200"].iloc[-1]

score = int(cond_rsi) + int(cond_ema50) + int(cond_ema200)

if score == 3:
    signal = "🟢 STRONG BUY"
elif score == 2:
    signal = "🟡 DCA BUY"
else:
    signal = "🔴 NO BUY"

# ==========================
# MESSAGE
# ==========================
message = (
    f"📊 RSI & DCA REPORT\n\n"
    f"BTC\n"
    f"• Daily RSI: {btc_rsi_d:.1f}\n"
    f"• Weekly RSI: {btc_rsi_w:.1f}\n\n"
    f"S&P 500\n"
    f"• Daily RSI: {sp_rsi_d:.1f}\n"
    f"• Weekly RSI: {sp_rsi_w:.1f}\n\n"
    f"DCA Score: {score}/3\n"
    f"Signal: {signal}"
)

send(message)
