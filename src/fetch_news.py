import requests
from datetime import datetime, timedelta, timezone

GDELT_DOC = "https://api.gdeltproject.org/api/v2/doc/doc"

MARKET_KEYWORDS = [
    "earnings", "guidance", "forecast", "revenue", "profit", "margin",
    "acquisition", "acquire", "merger", "buyout", "takeover",
    "SEC", "DOJ", "FTC", "lawsuit", "settlement",
    "FDA", "approval", "clinical", "trial",
    "upgrade", "downgrade", "price target", "rating",
    "buyback", "share repurchase", "dividend",
    "IPO", "spin-off", "spinoff", "layoffs", "restructuring",
    "contract", "partnership", "deal",
]

def _ts(dt: datetime) -> str:
    return dt.strftime("%Y%m%d%H%M%S")

def build_market_query(company_name: str, ticker: str) -> str:
    """
    Hard-filter on:
      - company/ticker
      - CNN/Fox domains
      - market-relevant keyword group
    """
    kw = " OR ".join([f'"{k}"' for k in MARKET_KEYWORDS])
    domains = "(domain:cnn.com OR domain:foxnews.com)"
    entity = f'("{company_name}" OR {ticker})'
    market = f"({kw})"
    return f"{entity} {domains} {market}"

def fetch_cnn_fox_market_headlines(
    company_name: str,
    ticker: str,
    days: int = 3,
    max_items: int = 25,
) -> list[dict]:
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=days)
    query = build_market_query(company_name, ticker)

    params = {
        "query": query,
        "mode": "artlist",
        "format": "json",
        "sort": "datedesc",
        "maxrecords": str(min(max_items, 250)),
        "startdatetime": _ts(start),
        "enddatetime": _ts(now),
    }

    r = requests.get(GDELT_DOC, params=params, timeout=25)
    if r.status_code != 200:
        return []

    js = r.json() or {}
    articles = js.get("articles", []) or []

    out = []
    for a in articles[:max_items]:
        out.append({
            "title": a.get("title") or "",
            "domain": a.get("domain") or "",
            "seendate": a.get("seendate") or "",
            "url": a.get("url") or "",
        })
    return out
