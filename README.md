# S&P 500 Daily Stock Signals (CNN + Fox via GDELT)

This repo generates a daily "signals" ranking for S&P 500 stocks using:
- Price trend/momentum features (Yahoo Finance via yfinance)
- CNN + Fox News headlines (GDELT) filtered by market-relevant keywords
- Simple explainable scoring (not investment advice)

## How it works
- A GitHub Action runs daily
- It updates `docs/data.json`
- GitHub Pages hosts the site from `/docs`

## Setup
1) Create a repo and add all files in this project.
2) Enable GitHub Pages:
   - Repo → Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main` / Folder: `/docs`
3) The workflow runs on a schedule and can be run manually via "Run workflow".

## Notes
- Educational only. Not financial advice.
- yfinance can be rate-limited; if you hit issues, reduce `CHUNK_SIZE` or universe size.
- News is from CNN/Fox domains via GDELT and filtered by keywords; it will miss some relevant stories.
