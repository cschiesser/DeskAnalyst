from __future__ import annotations

import json
import random
from pathlib import Path

from deskanalyst.eval.judge import judge_correctness, judge_faithfulness
from deskanalyst.generate.answer import _format_context, answer_from_results
from deskanalyst.retrieve.store import load_index, search


def _read_jsonl(path: str | Path) -> list[dict]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [json.loads(ln) for ln in lines if ln.strip()]


def _retrieve(mode: str, query: str, data_dir, records: list[dict], k: int):
    if mode == "system":
        return search(query, data_dir, k=k)
    # baseline: pick random chunks, to show the embeddings actually add value
    picks = random.sample(records, min(k, len(records)))
    return [(0.0, r) for r in picks]


def evaluate(data_dir, gold_path, k: int, mode: str) -> dict:
    random.seed(0)  # reproducible baseline
    gold = _read_jsonl(gold_path)
    _, records = load_index(data_dir)

    recall_hits = recall_total = 0
    faith_hits = 0
    corr_hits = corr_total = 0

    for row in gold:
        q = row["question"]
        results = _retrieve(mode, q, data_dir, records, k)
        joined = "\n".join(r["text"].lower() for _, r in results)

        mc = (row.get("must_contain") or "").lower()
        if mc:
            recall_total += 1
            if mc in joined:
                recall_hits += 1

        answer = answer_from_results(q, results)
        if judge_faithfulness(answer, _format_context(results)):
            faith_hits += 1

        ref = row.get("reference_answer")
        if ref:
            corr_total += 1
            if judge_correctness(answer, ref, q):
                corr_hits += 1

        print(f"  [{mode}] {q[:55]}")

    n = len(gold)
    return {
        "n": n,
        "recall": recall_hits / recall_total if recall_total else None,
        "faithfulness": faith_hits / n if n else None,
        "correctness": corr_hits / corr_total if corr_total else None,
    }
