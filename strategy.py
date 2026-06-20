def get_signal(price, ema50, ema200, rsi, structure):
    score = 0

    if ema50 > ema200:
        score += 40
    else:
        score -= 40

    if structure == "BULLISH":
        score += 30
    elif structure == "BEARISH":
        score -= 30

    if rsi < 30:
        score += 20
    elif rsi > 70:
        score -= 20

    if score >= 50:
        return "BUY", abs(score)
    elif score <= -50:
        return "SELL", abs(score)
    else:
        return "WAIT", abs(score)