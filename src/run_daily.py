from universe import fetch_sp500_universe
from fetch_prices import fetch_history_batch
from fetch_news import fetch_cnn_fox_market_headlines
from score import compute_features, score_from_features, score_news
from write_outputs import write_data_json

# Tune these if you hit rate limits
CHUNK_SIZE = 100       # yfinance batch size
TOP_NEWS = 80          # only fetch news for top N by price score
NEWS_DAYS = 3          # lookback window for news
MAX_HEADLINES = 25     # max headlines per ticker

def main():
    uni = fetch_sp500_universe()
    tickers = uni["YahooSymbol"].tolist()

    price_map = fetch_history_batch(
        tickers,
        period="1y",
        interval="1d",
        chunk_size=CHUNK_SIZE,
    )

    rows = []
    for _, r in uni.iterrows():
        t = r["YahooSymbol"]
        df = price_map.get(t)
        if df is None or df.empty:
            continue

        f = compute_features(df)
        base_score, reasons = score_from_features(f)
        if not f:
            continue

        rows.append({
            "ticker": t,
            "company": r["Security"],
            "sector": r["GICS Sector"],
            **f,
            "base_score": float(base_score),
            "news_score": 0.0,
            "score": float(base_score),
            "reasons": reasons,
            "headlines": [],
        })

    # Price-first ranking
    rows.sort(key=lambda x: x["base_score"], reverse=True)

    # Add CNN/Fox market-news score for top N
    for row in rows[:TOP_NEWS]:
        headlines = fetch_cnn_fox_market_headlines(
            company_name=row["company"],
            ticker=row["ticker"],
            days=NEWS_DAYS,
            max_items=MAX_HEADLINES,
        )
        ns, used = score_news(headlines)
        row["news_score"] = float(ns)
        row["headlines"] = used
        row["score"] = float(max(0.0, min(100.0, row["base_score"] + ns)))
        row["reasons"] = row["reasons"] + [f"CNN/Fox market-news score: {ns:+.1f}"]

    # Final ranking
    rows.sort(key=lambda x: x["score"], reverse=True)

    write_data_json(rows, out_path="docs/data.json")

if __name__ == "__main__":
    main()
