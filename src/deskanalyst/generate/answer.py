from __future__ import annotations

from pathlib import Path

from anthropic import Anthropic

from deskanalyst.retrieve.store import search

# Cheapest / fastest model; fine for synthesizing an answer from provided context.
MODEL = "claude-haiku-4-5-20251001"

SYSTEM = (
    "You are a financial research assistant. Answer the user's question using ONLY the "
    "excerpts from SEC filings provided below. After each claim, cite its source using the "
    "tag shown above that excerpt, e.g. [AAPL 10-K 2024-11-01]. If the excerpts do not "
    "contain enough to answer, say so plainly. Never invent numbers or facts."
)


def _format_context(results: list[tuple[float, dict]]) -> str:
    blocks = []
    for _score, rec in results:
        tag = f"[{rec['ticker']} {rec['form']} {rec['filing_date']}]"
        blocks.append(f"{tag}\n{rec['text']}")
    return "\n\n---\n\n".join(blocks)


def answer_from_results(
    query: str, results: list[tuple[float, dict]], model: str = MODEL
) -> str:
    """Have Claude write a cited answer from an already-retrieved set of chunks."""
    context = _format_context(results)
    user = (
        f"Question: {query}\n\n"
        f"Excerpts from filings:\n\n{context}\n\n"
        "Answer using only these excerpts, with an inline citation after each claim."
    )
    client = Anthropic()  # reads ANTHROPIC_API_KEY from the environment / .env
    resp = client.messages.create(
        model=model,
        max_tokens=1000,
        system=SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(block.text for block in resp.content if block.type == "text")


def answer_question(
    query: str, data_dir: str | Path, k: int = 6, model: str = MODEL
) -> tuple[str, list[tuple[float, dict]]]:
    """Retrieve the top-k chunks and have Claude write a cited answer from them."""
    results = search(query, data_dir, k=k)
    return answer_from_results(query, results, model=model), results
