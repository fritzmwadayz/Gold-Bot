import pandas as pd
import yfinance as yf
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from strategy import get_signal


#def fetch_ohlc(symbol: str = "GC=F", interval: str = "1h", periods: int = 250) -> pd.DataFrame:
#    """Fetch OHLC data. yfinance uses period string, not candle count."""
#    # Map candle count to yfinance period string
#    if interval == "5m":
#        period = "5d"
#    elif interval == "15m":
#        period = "5d"
#    elif interval == "1h":
#        period = "10d"
#    else:
#        period = "10d"

#    ticker = yf.Ticker(symbol)
#    df = ticker.history(period=period, interval=interval)
#    return df

def fetch_ohlc(symbol: str = "GC=F", interval: str = "1h") -> pd.DataFrame:
    """Fetch OHLC data from yfinance."""
    # Need more history for 200+ candles at 1h
    # Gold trades ~23h/day, so ~23 candles/day
    # 15 days = ~345 candles (safe margin above 200)
    period_map = {
        "5m": "5d",
        "15m": "5d", 
        "1h": "15d",
        "1d": "300d",
    }
    period = period_map.get(interval, "15d")
    
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval=interval)
    
    print(f"[analyzer] Fetched {len(df)} candles ({interval}, {period})")
    return df


def run_analysis(symbol: str = "GC=F") -> dict | None:
    """
    Run full analysis and return signal dict with trade plan.
    Returns None if no actionable signal (WAIT).
    """
    try:
        df = fetch_ohlc(symbol, interval="1h")
        if df.empty or len(df) < 200:
            print("[analyzer] Not enough data")
            return None

        # Indicators
        df["ema50"] = EMAIndicator(df["Close"], window=50).ema_indicator()
        df["ema200"] = EMAIndicator(df["Close"], window=200).ema_indicator()
        df["rsi"] = RSIIndicator(df["Close"], window=14).rsi()

        latest = df.iloc[-1]

        # Structure: compare last 2 highs and lows
        last_highs = df["High"].tail(5).tolist()
        last_lows = df["Low"].tail(5).tolist()

        if last_highs[-1] > last_highs[-2] and last_lows[-1] > last_lows[-2]:
            structure = "BULLISH"
        elif last_highs[-1] < last_highs[-2] and last_lows[-1] < last_lows[-2]:
            structure = "BEARISH"
        else:
            structure = "RANGING"

        # Support / Resistance
        support = df["Low"].tail(50).min()
        resistance = df["High"].tail(50).max()

        # Get signal from strategy
        signal, confidence = get_signal(
            latest["Close"],
            latest["ema50"],
            latest["ema200"],
            latest["rsi"],
            structure,
        )

        # Build trade plan
        trade_plan = None
        if signal == "BUY":
            entry = support + (resistance - support) * 0.3
            sl = support - 10
            tp = resistance
            rr = abs(tp - entry) / abs(entry - sl)
            trade_plan = {
                "entry": round(entry, 2),
                "sl": round(sl, 2),
                "tp": round(tp, 2),
                "rr": round(rr, 2),
            }
        elif signal == "SELL":
            entry = resistance - (resistance - support) * 0.3
            sl = resistance + 10
            tp = support
            rr = abs(tp - entry) / abs(entry - sl)
            trade_plan = {
                "entry": round(entry, 2),
                "sl": round(sl, 2),
                "tp": round(tp, 2),
                "rr": round(rr, 2),
            }

        if signal == "WAIT":
            return None  # Only send BUY/SELL

        return {
            "symbol": symbol,
            "price": round(latest["Close"], 2),
            "signal": signal,
            "confidence": confidence,
            "indicators": {
                "ema50": round(latest["ema50"], 2),
                "ema200": round(latest["ema200"], 2),
                "rsi": round(latest["rsi"], 2),
            },
            "structure": structure,
            "support": round(support, 2),
            "resistance": round(resistance, 2),
            "trade_plan": trade_plan,
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
        }

    except Exception as e:
        print(f"[analyzer] Error: {e}")
        return None