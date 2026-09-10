from __future__ import annotations

import argparse

from deskanalyst.config import REPO_ROOT, load_config
from deskanalyst.generate.answer import answer_question


def main() -> None:
    cfg = load_config()
    data_dir = REPO_ROOT / cfg["data_dir"]

    parser = argparse.ArgumentParser(
        description="Ask a question and get a cited answer from the filings."
    )
    parser.add_argument("--query", required=True, help="Your question.")
    parser.add_argument("--k", type=int, default=6, help="How many chunks to ground on.")
    args = parser.parse_args()

    answer, results = answer_question(args.query, data_dir, k=args.k)

    print("\n" + answer + "\n")
    print("Sources used:")
    for score, rec in results:
        print(f"  - {rec['ticker']} {rec['form']} {rec['filing_date']}  (score {score:.3f})")


if __name__ == "__main__":
    main()
