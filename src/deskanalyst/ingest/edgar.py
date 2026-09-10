from __future__ import annotations

import time
from dataclasses import dataclass

import requests

from deskanalyst.config import get_sec_user_agent

TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
ARCHIVE_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{acc_nodash}/{doc}"

# SEC asks for no more than ~10 requests/second; we stay well under that.
_MIN_INTERVAL = 0.2


@dataclass
class Filing:
    ticker: str
    cik: int
    form: str
    filing_date: str
    accession: str
    primary_document: str
    url: str


class EdgarClient:
    """Minimal client for the SEC EDGAR submissions + archive endpoints."""

    def __init__(self, user_agent: str | None = None):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent or get_sec_user_agent()})
        self._last_request = 0.0
        self._ticker_map: dict[str, int] | None = None

    def _get(self, url: str) -> requests.Response:
        wait = _MIN_INTERVAL - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)
        resp = self.session.get(url, timeout=30)
        self._last_request = time.monotonic()
        resp.raise_for_status()
        return resp

    def _ticker_to_cik(self) -> dict[str, int]:
        if self._ticker_map is None:
            rows = self._get(TICKERS_URL).json().values()
            self._ticker_map = {r["ticker"].upper(): int(r["cik_str"]) for r in rows}
        return self._ticker_map

    def cik_for(self, ticker: str) -> int:
        try:
            return self._ticker_to_cik()[ticker.upper()]
        except KeyError:
            raise ValueError(f"Ticker not found on EDGAR: {ticker}")

    def list_filings(
        self, ticker: str, forms: list[str], since: str | None = None
    ) -> list[Filing]:
        """Recent filings for a ticker, filtered by form type and (optional) date."""
        cik = self.cik_for(ticker)
        recent = self._get(SUBMISSIONS_URL.format(cik=cik)).json()["filings"]["recent"]
        wanted = {f.upper() for f in forms}

        filings: list[Filing] = []
        for form, fdate, acc, doc in zip(
            recent["form"],
            recent["filingDate"],
            recent["accessionNumber"],
            recent["primaryDocument"],
        ):
            if form.upper() not in wanted or not doc:
                continue
            if since and fdate < since:
                continue
            acc_nodash = acc.replace("-", "")
            filings.append(
                Filing(
                    ticker=ticker.upper(),
                    cik=cik,
                    form=form.upper(),
                    filing_date=fdate,
                    accession=acc,
                    primary_document=doc,
                    url=ARCHIVE_URL.format(cik=cik, acc_nodash=acc_nodash, doc=doc),
                )
            )
        return filings

    def download(self, filing: Filing) -> str:
        return self._get(filing.url).text
