from __future__ import annotations

import argparse

from deskanalyst.config import REPO_ROOT, load_config
from deskanalyst.retrieve.store import build_index, search


def main() -> None:
    cfg = load_config()
    data_dir = REPO_ROOT / cfg["data_dir"]

    parser = argparse.ArgumentParser(description="Build or query the chunk index.")
    parser.add_argument("--build", action="store_true", help="Embed all chunks and build the index.")
    parser.add_argument("--query", type=str, help="Search the index with a question.")
    parser.add_argument("--k", type=int, default=cfg["retrieval"].get("rerank_top_k", 5))
    args = parser.parse_args()

    if args.build:
        build_index(data_dir)

    if args.query:
        results = search(args.query, data_dir, k=args.k)
        print(f"\nTop {len(results)} results for: {args.query}\n")
        for rank, (score, rec) in enumerate(results, 1):
            snippet = rec["text"][:220].replace("\n", " ")
            print(f"[{rank}] score={score:.3f}  {rec['ticker']} {rec['form']} {rec['filing_date']}")
            print(f"    {snippet} ...\n")

    if not args.build and not args.query:
        parser.error('Give me something to do: --build and/or --query "your question"')


if __name__ == "__main__":
    main()
