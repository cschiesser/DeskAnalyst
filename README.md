# DeskAnalyst

> Ask analyst questions about SEC filings and get answers and cited back to the source.

![status](https://img.shields.io/badge/status-Phase%201%20complete-green)
![python](https://img.shields.io/badge/python-3.11+-blue)
![license](https://img.shields.io/badge/license-MIT-green)

---

## What it is

DeskAnalyst is a retrieval-augmented (RAG) system over public company filings. It downloads a
company's SEC filings (10-K / 10-Q / 8-K), turns them into a searchable index, and answers
natural-language questions with a written response whose every claim is cited back to the
filing it came from — and which is built to say "not in the filings" rather than invent an
answer.

It runs entirely on **public data**, so it's safe to share openly, and it mirrors the kind of
reading-and-summarizing work a fundamental research analyst does every day.

> **Data & compliance note.** This repository uses only publicly available data. It is *not*
> intended for material non-public information (MNPI), internal research, or client data.
> Before adapting it to any non-public data or running it in a professional setting, follow
> your firm's data-handling and approved-tooling policy.

---

## What works today

- **Grounded, cited answers** — the model answers only from retrieved filing excerpts and tags
  each claim with its source, e.g. `[AAPL 10-K 2024-11-01]`.
- **Semantic search over filings** — dense embeddings find the most relevant passages by
  *meaning*, not keyword overlap.
- **Reproducible pipeline** — one command per stage, driven by a single config file.
- **Evaluation harness** — measures retrieval and answer quality against a hand-labeled gold
  set, with a baseline for comparison (see [Evaluation](#evaluation)).

Single-company Q&A works end to end today. Cross-company comparison, an agentic planner, and
richer retrieval are on the [Roadmap](#roadmap).

---

## How it works

```
SEC EDGAR ──▶ clean + chunk ──▶ embed + index ──▶ semantic search ──▶ cited answer
 (ingest)       (index)          (retrieve)         (retrieve)         (generate · Claude)
                                        │                                    │
                                        └──────────── evaluation ────────────┘
                                         recall@k · faithfulness · correctness
```

1. **Ingest** — resolve a ticker to its SEC CIK, list its filings, and download each one,
   caching locally (a descriptive `User-Agent` is required by EDGAR).
2. **Index** — strip the filing HTML to plain text and split it into overlapping chunks,
   each tagged with its source filing.
3. **Retrieve** — embed every chunk with a local model, and answer a query by finding the
   chunks whose embeddings are closest to the query's.
4. **Generate** — hand the top chunks and the question to Claude, which writes a cited answer
   using only that context.
5. **Evaluate** — score the whole thing on a gold set.

---

## Evaluation

Scored on a 20-question hand-labeled gold set (`eval/datasets/apple_gold.jsonl`). Each item
has a question, a distinctive phrase a relevant chunk should contain, and a short reference
answer. Recall@k is a string match of that phrase in the top-k retrieved chunks; faithfulness
and correctness are graded by an LLM judge. The **baseline** answers the same questions from
randomly chosen chunks, to show the retrieval is doing real work.

| Metric | Baseline (random) | DeskAnalyst |
|---|---|---|
| Retrieval recall@5 | 0.30 | 0.85 |
| Faithfulness | 0.30 | 0.85 |
| Answer correctness | 0.25 | 0.90 |

*(n = 20, k = 5.)* Faithfulness and correctness are LLM-judged on a small set, so treat them
as indicative rather than definitive. Reproduce with `python -m deskanalyst.eval`.

---

## Tech stack

- **Ingestion:** `requests` against the SEC EDGAR REST endpoints
- **Parsing:** BeautifulSoup + lxml
- **Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2`), run locally on CPU
- **Search:** NumPy cosine similarity (brute-force fine at this corpus size)
- **Answer generation & LLM judge:** Anthropic Claude (Haiku)
- **Config & tooling:** PyYAML, python-dotenv, pytest, ruff

---

## Repository structure

```
DeskAnalyst/
├── README.md
├── pyproject.toml
├── .env.example
├── configs/
│   └── default.yaml
├── data/                         # gitignored cached filings + built index
├── eval/
│   └── datasets/
│       └── apple_gold.jsonl      # hand-labeled Q&A gold set
├── src/deskanalyst/
│   ├── config.py                 # loads config + .env
│   ├── ingest/                   # download filings from SEC EDGAR
│   ├── index/                    # clean HTML + chunk
│   ├── retrieve/                 # embeddings + semantic search
│   ├── generate/                 # cited answer synthesis (Claude)
│   ├── eval/                     # gold-set evaluation + LLM judge
│   └── agent/ tools/ api/ ui/    # placeholders (see Roadmap)
└── tests/
```

---

## Getting started

```bash
git clone https://github.com/cschiesser/DeskAnalyst.git
cd DeskAnalyst

python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Configuration

Copy the environment template and add your own credentials:

```bash
cp .env.example .env
```

Then edit `.env` and set:

- `SEC_USER_AGENT` — your name + email. SEC EDGAR requires a contact string on every request.
- `ANTHROPIC_API_KEY` — your own key from https://console.anthropic.com (pay-as-you-go; used
  only for the answer and evaluation steps).

### Run the pipeline

```bash
python -m deskanalyst.ingest --tickers AAPL                                  # 1. download filings
python -m deskanalyst.index                                                  # 2. clean + chunk
python -m deskanalyst.retrieve --build                                       # 3. embed + build index
python -m deskanalyst.retrieve --query "What are Apple's risk factors?"      # 4. semantic search
python -m deskanalyst.generate --query "What are Apple's risk factors?"      # 5. cited answer
python -m deskanalyst.eval                                                    # 6. evaluate
```

---

## Roadmap

**Phase 2 — better retrieval + agentic**
- Hybrid retrieval (dense + BM25) with a cross-encoder reranker
- Agentic decomposition (LangGraph): split a question into sub-queries and route to tools
- Tools: numeric/table extraction, price lookup, cross-company comparator
- Multi-quarter diffing (track how a metric or the risk narrative changes over time)
- Ingest earnings-call transcripts and price data

**Phase 3 — extensions**
- Multimodal figure/table extraction from filings
- Expose retrieval + tools as an MCP server
- Transcript tone/sentiment signal vs. subsequent returns (research module)
- FastAPI service + Streamlit UI

---

## License

MIT see [LICENSE](LICENSE).
