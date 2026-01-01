import yfinance as yf
import pandas as pd

def fetch_history_batch(
    tickers: list[str],
    period: str = "1y",
    interval: str = "1d",
    chunk_size: int = 100,
) -> dict[str, pd.DataFrame]:
    """
    Batch download to reduce calls.
    Returns dict: ticker -> dataframe with Open/High/Low/Close/Volume
    """
    out: dict[str, pd.DataFrame] = {}

    for i in range(0, len(tickers), chunk_size):
        chunk = tickers[i:i + chunk_size]

        data = yf.download(
            tickers=" ".join(chunk),
            period=period,
            interval=interval,
            auto_adjust=True,
            group_by="ticker",
            threads=True,
            progress=False,
        )

        if data is None or data.empty:
            continue

        # Single ticker comes back without MultiIndex
        if isinstance(data.columns, pd.Index):
            t = chunk[0]
            df = data.dropna()
            if not df.empty:
                out[t] = df
            continue

        # MultiIndex: (TICKER, FIELD)
        for t in chunk:
            if t not in data.columns.get_level_values(0):
                continue
            df = data[t].dropna()
            if not df.empty:
                out[t] = df

    return out
