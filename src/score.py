import numpy as np
import pandas as pd
from vadersentiment.vaderSentiment import SentimentIntensityAnalyzer
from fetch_news import MARKET_KEYWORDS

analyzer = SentimentIntensityAnalyzer()

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / (loss.replace(0, np.nan))
    return 100 - (100 / (1 + rs))

def compute_features(df: pd.DataFrame) -> dict:
    close = df["Close"].dropna()
    if len(close) < 210:
        return {}

    last = close.iloc[-1]

    ret_20 = last / close.iloc[-21] - 1
    ret_60 = last / close.iloc[-61] - 1

    ma50 = close.rolling(50).mean().iloc[-1]
    ma200 = close.rolling(200).mean().iloc[-1]
    above_50 = 1.0 if last > ma50 else 0.0
    above_200 = 1.0 if last > ma200 else 0.0

    rsi14 = float(rsi(close, 14).iloc[-1])
    vol20 = close.pct_change().rolling(20).std().iloc[-1]

    return {
        "close": float(last),
        "ret_20": float(ret_20),
        "ret_60": float(ret_60),
        "above_50": float(above_50),
        "above_200": float(above_200),
        "rsi14": float(rsi14),
        "vol20": float(vol20),
    }

def _cap(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def score_from_features(f: dict) -> tuple[float, list[str]]:
    if not f:
        return 0.0, ["insufficient price history"]

    # Price score: 0..100 (roughly)
    momentum_component = 50 * _cap((f["ret_20"] * 2.0 + f["ret_60"]), -0.5, 0.5)   # -25..25
    trend_component = 10 * (f["above_50"] + f["above_200"])                         # 0..20

    # RSI sweet spot: 50-70
    if 50 <= f["rsi14"] <= 70:
        rsi_component = 15.0
    elif 40 <= f["rsi14"] < 50:
        rsi_component = 7.0
    elif 70 < f["rsi14"] <= 80:
        rsi_component = 6.0
    else:
        rsi_component = -8.0

    # Volatility penalty
    vol_penalty = -20.0 * _cap((f["vol20"] - 0.02) / 0.05, 0.0, 1.0)               # 0..-20

    raw = 50 + momentum_component + trend_component + rsi_component + vol_penalty
    score = _cap(raw, 0.0, 100.0)

    reasons = [
        f"20d return: {f['ret_20']*100:.1f}%",
        f"60d return: {f['ret_60']*100:.1f}%",
        f"Above MA50: {'yes' if f['above_50'] else 'no'}; MA200: {'yes' if f['above_200'] else 'no'}",
        f"RSI(14): {f['rsi14']:.1f}",
        f"Vol(20d): {f['vol20']*100:.2f}%",
    ]
    return score, reasons

def extract_keyword_hits(text: str) -> list[str]:
    t = (text or "").lower()
    hits = []
    for k in MARKET_KEYWORDS:
        if k.lower() in t:
            hits.append(k)
    return hits[:6]

def score_news(headlines: list[dict]) -> tuple[float, list[dict]]:
    """
    Returns:
      news_score: roughly -10..+10
      used_headlines: headlines with keyword hits, enriched with sentiment + hits
    """
    used = []
    compounds = []

    for h in headlines or []:
        title = (h.get("title") or "").strip()
        if not title:
            continue

        hits = extract_keyword_hits(title)
        if not hits:
            continue  # enforce "market-relevant" only

        comp = analyzer.polarity_scores(title)["compound"]  # -1..1
        compounds.append(comp)

        used.append({
            **h,
            "sentiment": float(comp),
            "keyword_hits": hits,
        })

    if not compounds:
        return 0.0, []

    avg = float(np.mean(compounds))           # -1..1
    score = float(np.clip(avg * 10.0, -10.0, 10.0))

    # Small confidence bump if multiple relevant headlines
    bump = min(2.0, 0.4 * len(used))          # up to +2
    score = float(np.clip(score + bump, -10.0, 10.0))

    return score, used
