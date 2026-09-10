from __future__ import annotations

import json
from pathlib import Path

from deskanalyst.ingest.edgar import EdgarClient, Filing


def ingest_companies(
    tickers: list[str],
    forms: list[str],
    since: str | None,
    data_dir: str | Path,
) -> list[Filing]:
    """Download and cache filings under data_dir/filings/<TICKER>/."""
    data_dir = Path(data_dir)
    client = EdgarClient()
    downloaded: list[Filing] = []

    for ticker in tickers:
        print(f"[{ticker}] resolving filings...")
        filings = client.list_filings(ticker, forms=forms, since=since)
        print(f"[{ticker}] found {len(filings)} filings")

        out_dir = data_dir / "filings" / ticker.upper()
        out_dir.mkdir(parents=True, exist_ok=True)

        for f in filings:
            stem = f"{f.form}_{f.filing_date}_{f.accession.replace('-', '')}"
            html_path = out_dir / f"{stem}.html"
            if html_path.exists():
                continue  # already cached
            html_path.write_text(client.download(f), encoding="utf-8")
            (out_dir / f"{stem}.json").write_text(
                json.dumps(vars(f), indent=2), encoding="utf-8"
            )
            print(f"  saved {html_path.name}")
            downloaded.append(f)

    return downloaded
