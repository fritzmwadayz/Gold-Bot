import MetaTrader5 as mt5
import pandas as pd
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from strategy import get_signal

if not mt5.initialize():
    print("MT5 connection failed")
    quit()

symbol = "XAUUSD"

rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 250)

df = pd.DataFrame(rates)

df["ema50"] = EMAIndicator(df["close"], window=50).ema_indicator()
df["ema200"] = EMAIndicator(df["close"], window=200).ema_indicator()
df["rsi"] = RSIIndicator(df["close"], window=14).rsi()

latest = df.iloc[-1]

last_highs = df["high"].tail(5).tolist()
last_lows = df["low"].tail(5).tolist()

if last_highs[-1] > last_highs[-2] and last_lows[-1] > last_lows[-2]:
    structure = "BULLISH"
elif last_highs[-1] < last_highs[-2] and last_lows[-1] < last_lows[-2]:
    structure = "BEARISH"
else:
    structure = "RANGING"

support = df["low"].tail(50).min()
resistance = df["high"].tail(50).max()

print("\n===== GOLD ANALYSIS =====")

print(f"Current Price: {latest['close']:.2f}")
print(f"EMA 50: {latest['ema50']:.2f}")
print(f"EMA 200: {latest['ema200']:.2f}")
print(f"RSI: {latest['rsi']:.2f}")
print(f"Support: {support:.2f}")
print(f"Resistance: {resistance:.2f}")

print(f"Structure: {structure}")

if latest["ema50"] > latest["ema200"]:
    trend = "BULLISH"
else:
    trend = "BEARISH"

print(f"Trend: {trend}")

signal, confidence = get_signal(
    latest["close"],
    latest["ema50"],
    latest["ema200"],
    latest["rsi"],
    structure
)

print(f"Signal: {signal}")
print(f"Confidence: {confidence}%")

print("\n===== TRADE PLAN =====")

if signal == "BUY":
    entry = support + (resistance - support) * 0.3
    sl = support - 10
    tp = resistance

    rr = abs(tp - entry) / abs(entry - sl)

    print(f"Entry: {entry:.2f}")
    print(f"Stop Loss: {sl:.2f}")
    print(f"Take Profit: {tp:.2f}")
    print(f"Risk/Reward: {rr:.2f}")

elif signal == "SELL":
    entry = resistance - (resistance - support) * 0.3
    sl = resistance + 10
    tp = support

    rr = abs(tp - entry) / abs(entry - sl)

    print(f"Entry: {entry:.2f}")
    print(f"Stop Loss: {sl:.2f}")
    print(f"Take Profit: {tp:.2f}")
    print(f"Risk/Reward: {rr:.2f}")

else:
    print("No trade setup (WAIT signal)")

mt5.shutdown()