import streamlit as st
import pandas as pd
import requests
import yfinance as yf
from datetime import datetime, timedelta

# Fonction pour récupérer le prix du SOL

def get_sol_price():
    url = "https://api.coingecko.com/api/v3/coins/solana/market_chart?vs_currency=usd&days=2&interval=daily"
    response = requests.get(url).json()
    price = round(response["prices"][-1][1], 2)
    price_24h_ago = round(response["prices"][-2][1], 2)
    price_change = round(((price - price_24h_ago) / price_24h_ago) * 100, 2)
    timestamp = datetime.now().strftime("%d/%m/%Y à %H:%M:%S")
    return price, price_24h_ago, price_change, timestamp

# Fonction pour récupérer les indicateurs techniques

def get_technical_indicators():
    data = yf.download("SOL-USD", period="60d", interval="1d")
    if data.empty:
        return "Donnée indisponible", "Donnée indisponible", "Donnée indisponible", "Donnée indisponible"
    rsi = round(float(100 - (100 / (1 + (data["Close"].diff().where(data["Close"].diff() > 0, 0).rolling(14).mean() / data["Close"].diff().where(data["Close"].diff() < 0, 0).abs().rolling(14).mean()))).iloc[-1]), 2)
    macd = round(float((data["Close"].ewm(span=12, adjust=False).mean() - data["Close"].ewm(span=26, adjust=False).mean()).iloc[-1]), 2)
    mm20 = round(float(data["Close"].rolling(window=20).mean().iloc[-1]), 2)
    mm50 = round(float(data["Close"].rolling(window=50).mean().iloc[-1]), 2)
    return rsi, macd, mm20, mm50

# Fonction pour récupérer les indicateurs de volatilité

def get_volatility_indicators():
    data = yf.download("SOL-USD", period="60d", interval="1d")
    if data.empty:
        return "Donnée indisponible", "Donnée indisponible", "Donnée indisponible"
    atr = round(float(data["High"].subtract(data["Low"]).rolling(window=14).mean().iloc[-1]), 2)
    bollinger_band_width = round(float((data["Close"].rolling(window=20).std().iloc[-1]) * 2), 2)
    volatility_24h = round(float(data["Close"].pct_change().std() * 100), 2)
    return atr, bollinger_band_width, f"{volatility_24h}%"

# Fonction pour récupérer les volumes de trading SOL/USDC

def get_trading_volume():
    url = "https://api.coingecko.com/api/v3/coins/solana/market_chart?vs_currency=usd&days=30&interval=daily"
    response = requests.get(url).json()
    volume_data = response["total_volumes"][-30:]
    dates, volumes = [], []
    for day in volume_data:
        date = datetime.utcfromtimestamp(day[0] / 1000).strftime("%d/%m")
        if date not in dates:
            dates.append(date)
            volumes.append(round(day[1] / 1e6, 2))
    volume_avg_7d = round(sum(volumes[-7:]) / 7, 2)
    volume_avg_30d = round(sum(volumes) / 30, 2)
    return dates[-7:], volumes[-7:], volume_avg_7d, volume_avg_30d

# Streamlit App
st.title("📊 Dashboard SOL/USDC")

# Récupération des données
sol_price, sol_price_24h_ago, sol_price_change, sol_timestamp = get_sol_price()
rsi, macd, mm20, mm50 = get_technical_indicators()
dates, volumes, volume_avg_7d, volume_avg_30d = get_trading_volume()
atr, bollinger_band_width, volatility_24h = get_volatility_indicators()

# Section Variation du Prix et Tendance
st.subheader("📉 Variation du Prix et Tendance")
st.metric(label=f"Prix actuel du SOL (USD) au {sol_timestamp}", value=f"{sol_price}$")
st.write(f"Prix il y a 24h : {sol_price_24h_ago}$")
st.write(f"Le prix a {'📈 augmenté' if sol_price_change > 0 else '📉 diminué'} de {sol_price_change}% en 24h.")

# Section Indicateurs Techniques Clés
st.subheader("📊 Indicateurs Techniques Clés")
technical_df = pd.DataFrame({
    "Indicateur": ["RSI", "MACD", "Moyenne Mobile 20j", "Moyenne Mobile 50j"],
    "Valeur": [rsi, macd, mm20, mm50]
})
st.dataframe(technical_df)
st.write("💡 **Analyse :**")
st.write(f"- RSI ({rsi}) indique un marché {'suracheté' if rsi > 70 else 'survendu' if rsi < 30 else 'neutre'}.")
st.write(f"- MACD ({macd}) {'confirme une tendance haussière' if macd > 0 else 'suggère une tendance baissière'}.")
st.write(f"- MM20 ({mm20}) et MM50 ({mm50}) indiquent {'une tendance haussière' if mm20 > mm50 else 'une tendance baissière'}.")

# Section Volume de Transaction
st.subheader("📊 Indicateurs de Volume de Transaction SOL/USDC")
volume_df = pd.DataFrame({
    "Date": dates,
    "Volume (Millions USD)": volumes
})
st.dataframe(volume_df)
st.write(f"**Volume moyen sur 7 jours** : {volume_avg_7d}M$")
st.write(f"**Volume moyen sur 30 jours** : {volume_avg_30d}M$")
st.write("🔗 [Voir plus de données sur l’agrégateur](https://www.coingecko.com/en/coins/solana)")
st.write(f"💡 **Analyse :** Le volume de trading est en {'📈 hausse' if volume_avg_7d > volume_avg_30d else '📉 baisse'} par rapport à la moyenne 7 jours.")

# Section Volatilité et Placement de LP
st.subheader("⚡ Indicateurs de Volatilité pour Placement de LP")
volatility_df = pd.DataFrame({
    "Indicateur": ["ATR (14j)", "Bollinger Band Width", "Volatilité 24h (%)"],
    "Valeur": [atr, bollinger_band_width, volatility_24h]
})
st.dataframe(volatility_df)
st.write("💡 **Recommandation LP :**")
st.write(f"- Une volatilité élevée ({volatility_24h}) suggère une range plus large pour une LP durable.")
st.write(f"- Les bandes de Bollinger ({bollinger_band_width}) indiquent {'un marché instable' if bollinger_band_width > 25 else 'un marché stable'}.")
st.write(f"- ATR ({atr}) suggère {'une plage étendue pour minimiser les rebalancements' if atr > 5 else 'une plage plus serrée pour optimiser le rendement'}. ")
