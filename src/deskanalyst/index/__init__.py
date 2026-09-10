from __future__ import annotations

import json
from pathlib import Path

from deskanalyst.index.chunk import chunk_text
from deskanalyst.index.clean import html_to_text


def build_chunks(data_dir: str | Path, size: int, overlap: int) -> int:
    """Clean + chunk every filing under data_dir/filings/, write data_dir/chunks.jsonl."""
    data_dir = Path(data_dir)
    filings_dir = data_dir / "filings"
    if not filings_dir.exists():
        raise FileNotFoundError(
            f"No filings at {filings_dir}. Run `python -m deskanalyst.ingest` first."
        )

    out_path = data_dir / "chunks.jsonl"
    total = 0
    preview: str | None = None

    with out_path.open("w", encoding="utf-8") as out:
        for html_path in sorted(filings_dir.rglob("*.html")):
            meta_path = html_path.with_suffix(".json")
            meta = (
                json.loads(meta_path.read_text(encoding="utf-8"))
                if meta_path.exists()
                else {}
            )
            text = html_to_text(html_path.read_text(encoding="utf-8", errors="ignore"))
            pieces = chunk_text(text, size=size, overlap=overlap)

            for i, piece in enumerate(pieces):
                record = {
                    "chunk_id": f"{meta.get('ticker', '?')}_{html_path.stem}_{i:04d}",
                    "ticker": meta.get("ticker"),
                    "form": meta.get("form"),
                    "filing_date": meta.get("filing_date"),
                    "accession": meta.get("accession"),
                    "source_file": str(html_path.relative_to(data_dir)),
                    "index": i,
                    "text": piece,
                }
                out.write(json.dumps(record) + "\n")
                if preview is None:
                    preview = piece[:300]
                total += 1

            print(f"  {html_path.name}: {len(pieces)} chunks")

    print(f"\nWrote {total} chunks to {out_path}")
    if preview:
        print("\nFirst chunk preview:\n" + preview + " ...")
    return total
