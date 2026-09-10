from __future__ import annotations

import argparse

from deskanalyst.config import REPO_ROOT, load_config
from deskanalyst.eval import evaluate


def _fmt(x) -> str:
    return "n/a" if x is None else f"{x:.2f}"


def main() -> None:
    cfg = load_config()
    data_dir = REPO_ROOT / cfg["data_dir"]
    default_gold = REPO_ROOT / "eval" / "datasets" / "apple_gold.jsonl"

    parser = argparse.ArgumentParser(description="Evaluate retrieval + answer quality.")
    parser.add_argument("--k", type=int, default=cfg["retrieval"].get("rerank_top_k", 5))
    parser.add_argument("--gold", default=str(default_gold))
    args = parser.parse_args()

    print("Running SYSTEM (semantic search)...")
    system = evaluate(data_dir, args.gold, args.k, mode="system")
    print("Running BASELINE (random chunks)...")
    baseline = evaluate(data_dir, args.gold, args.k, mode="baseline")

    print("\nResults (paste into README):\n")
    print("| Metric | Baseline (random) | DeskAnalyst |")
    print("|---|---|---|")
    print(f"| Retrieval recall@{args.k} | {_fmt(baseline['recall'])} | {_fmt(system['recall'])} |")
    print(f"| Faithfulness | {_fmt(baseline['faithfulness'])} | {_fmt(system['faithfulness'])} |")
    print(f"| Answer correctness | {_fmt(baseline['correctness'])} | {_fmt(system['correctness'])} |")
    print(f"\n(n = {system['n']} questions, k = {args.k})")


if __name__ == "__main__":
    main()
