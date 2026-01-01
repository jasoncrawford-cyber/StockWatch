import pandas as pd

WIKI_SP500 = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

def to_yahoo_symbol(sym: str) -> str:
    # Yahoo uses "-" where S&P list uses "." (e.g., BRK.B -> BRK-B)
    return sym.replace(".", "-").strip()

def fetch_sp500_universe() -> pd.DataFrame:
    tables = pd.read_html(WIKI_SP500)
    df = tables[0].copy()

    # Columns usually include: Symbol, Security, GICS Sector
    df = df[["Symbol", "Security", "GICS Sector"]].dropna()
    df["YahooSymbol"] = df["Symbol"].map(to_yahoo_symbol)
    df = df.drop_duplicates(subset=["YahooSymbol"]).reset_index(drop=True)
    return df
