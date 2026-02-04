import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os

# ==========================
# TELEGRAM
# ==========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)

# ==========================
# RSI FUNCTION
# ==========================
def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# ==========================
# DATA DOWNLOAD
# ==========================
btc = yf.download("BTC-USD", period="2y", interval="1d")
sp  = yf.download("^GSPC", period="2y", interval="1d")

# ==========================
# RSI BERECHNUNG
# ==========================
btc["RSI_D"] = rsi(btc["Close"])
sp["RSI_D"]  = rsi(sp["Close"])

btc_w = btc.resample("W").last()
sp_w  = sp.resample("W").last()

btc_w["RSI_W"] = rsi(btc_w["Close"])
sp_w["RSI_W"]  = rsi(sp_w["Close"])

btc_rsi_d = btc["RSI_D"].iloc[-1]
btc_rsi_w = btc_w["RSI_W"].iloc[-1]

sp_rsi_d  = sp["RSI_D"].iloc[-1]
sp_rsi_w  = sp_w["RSI_W"].iloc[-1]

# ==========================
# EMA + DCA SCORE (S&P 500)
# ==========================
sp["EMA50"]  = sp["Close"].ewm(span=50).mean()
sp["EMA200"] = sp["Close"].ewm(span=200).mean()

cond_rsi   = sp_rsi_d < 40
cond_ema50 = sp["Close"].iloc[-1] < sp["EMA50"].iloc[-1]
cond_ema200= sp["Close"].iloc[-1] < sp["EMA200"].iloc[-1]

dca_score = sum([cond_rsi, cond_ema50, cond_ema200])

if dca_score == 3:
    dca_signal = "🟢 STRONG BUY"
elif dca_score == 2:
    dca_signal = "🟡 DCA BUY"
else:
    dca_signal = "🔴 NO BUY"

# ==========================
# MESSAGE (IMMER SENDEN)
# ==========================
message = f"""
📊 RSI & DCA REPORT

🟠 Bitcoin
• Daily RSI: {btc_rsi_d:.1f}
• Weekly RSI: {btc_rsi_w:.1f}

📉 S&P 500
• Daily RSI: {sp_rsi_d:.1f}
• Weekly RSI: {sp_rsi_w:.1f}

📈 DCA SCORE
• Score: {dca_score}/3
• Signal: {dca_signal}
"""

send_telegram_message(message)

print("Telegram Nachricht gesendet ✅")
