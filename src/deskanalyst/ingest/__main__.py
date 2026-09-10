from __future__ import annotations

import argparse

from deskanalyst.config import REPO_ROOT, load_config
from deskanalyst.ingest import ingest_companies


def main() -> None:
    cfg = load_config()
    parser = argparse.ArgumentParser(description="Download SEC EDGAR filings.")
    parser.add_argument("--tickers", nargs="+", default=cfg.get("companies"))
    parser.add_argument("--forms", nargs="+", default=cfg["ingest"]["filing_types"])
    parser.add_argument("--since", default=cfg["ingest"].get("since"))
    args = parser.parse_args()

    ingest_companies(
        tickers=args.tickers,
        forms=args.forms,
        since=args.since,
        data_dir=REPO_ROOT / cfg["data_dir"],
    )


if __name__ == "__main__":
    main()
