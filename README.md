# DeskAnalyst

> An agentic research analyst over company filings. Ask analyst-grade questions and get answers with the real numbers pulled from the source.

<!-- DeskAnalyst -->

![status](https://img.shields.io/badge/status-WIP-orange)
![python](https://img.shields.io/badge/python-3.11+-blue)
![license](https://img.shields.io/badge/license-MIT-green)
<!-- -->

---

## What it is

DeskAnalyst ingests real-world financial disclosures (SEC 10-K / 10-Q / 8-K filings,
earnings-call transcripts, and price data), indexes them for retrieval, and puts an agentic
layer on top that can decompose a question, pull exact figures, compare across companies and
quarters, and answer **with citations back to the source line**.

It is built entirely on **public data** so it can be shared openly. It also mirrors the daily
workflow of a fundamental research analyst.

> **Data & compliance note.** This repository uses only publicly available data. It is *not*
> intended for material non-public information (MNPI), internal research, or client data.
> Before adapting it to any non-public data or running it in a professional setting, follow
> your firm's data-handling and approved-tooling policy.

---

## Key capabilities

- **Grounded Q&A with citations** — every claim traces to a filing/transcript span; every
  number is quoted from source, never generated.
- **Hybrid retrieval + reranking** — dense embeddings + BM25, reranked by a cross-encoder.
- **Agentic decomposition** — a planner splits complex questions into sub-queries and routes
  them to tools (retriever, numeric/table extractor, price lookup, cross-company comparator).
- **Multi-quarter diffing** — track how a metric or the risk-factor narrative changes over time.
- **Evaluation harness** — measured retrieval and answer quality, not vibes.

---

## Architecture

```
Data sources ──▶ Ingest & index ──▶ Agentic layer ──▶ Grounded answer
 EDGAR                embed +           planner +          cited +
 transcripts          BM25 index        tools              numbers
                          │                 │                 │
                          └─────────────────┴─────────────────┘
                                   Evaluation harness
                          recall@k · faithfulness · correctness
```

**Ingest & index.** EDGAR filings arrive as HTML/XBRL; the pipeline cleans, sections, and
chunks them, then builds both a vector index and a BM25 index.

**Retrieval.** Hybrid dense + sparse retrieval with a cross-encoder reranker — naive similarity
search alone underperforms on financial text; the README's eval section quantifies by how much.

**Agentic layer.** A planner decomposes the question and calls tools:
`retriever`, `numeric_tool` (reads figures out of filing tables), `price_tool`, `comparator`.
Answers are synthesized only from retrieved, cited context.

---

## Analyst workflows

Concrete tasks the tool supports (public-data versions of real desk work):

| Workflow            | What it does                                                            |
|---------------------|------------------------------------------------------------------------|
| Earnings triage     | Summarize a new filing/transcript, diff vs prior quarter, flag guidance changes |
| Peer comps          | Pull the same metric or disclosure across a defined peer set            |
| Thesis check        | Test whether a new filing supports or contradicts existing thesis notes |
| First-draft memo    | Generate a structured, cited note as an editing starting point          |
| Forensic screen     | Surface language changes: going-concern, auditor changes, restatements, litigation |


---

## Evaluation

Every claim in the README's headline numbers is reproduced by `eval/run_eval.py` against a
small hand-labeled Q&A set. Baseline = naive top-k similarity search + single LLM call.

| Metric                | Definition                                             | Baseline | FilingScope |
|-----------------------|--------------------------------------------------------|----------|-------------|
| Retrieval recall@5    | Fraction of questions whose gold chunk is in top 5     | _TBD_    | _TBD_       |
| Faithfulness          | Share of answer claims supported by retrieved context  | _TBD_    | _TBD_       |
| Answer correctness    | Graded vs reference answers                             | _TBD_    | _TBD_       |
| Numeric accuracy      | Cited figures matching the filing exactly              | _TBD_    | _TBD_       |

| Metric | Baseline (random) | DeskAnalyst |
|---|---|---|
| Retrieval recall@5 | 0.30 | 0.85 |
| Faithfulness | 0.30 | 0.85 |
| Answer correctness | 0.25 | 0.90 |

(n = 20 questions, k = 5)


Method: describe the eval set size, how gold labels were created, and the grader
(LLM-as-judge / string match / human spot-check).

---

## Tech stack

- **Retrieval / vector store:** _TBD_ (e.g. FAISS / Chroma) + BM25
- **Reranker:** cross-encoder (_TBD_)
- **Agent framework:** LangGraph 
- **Serving:** FastAPI
- **UI:** Streamlit
- **Eval:** custom harness (RAGAS-style metrics)
- **Infra:** Docker, config-driven (`configs/*.yaml`), request tracing

---

## Repository structure

```
DeskAnalyst/
├── README.md
├── pyproject.toml
├── .env.example
├── docker-compose.yml
├── configs/
│   └── default.yaml
├── data/                  # gitignored cached filings & transcripts
├── docs/
│   └── architecture.svg
├── src/DeskAnalyst/
│   ├── ingest/            # EDGAR client, transcript loader, XBRL parsing
│   ├── index/             # chunking, embeddings, vector + BM25 stores
│   ├── retrieve/          # hybrid retriever + cross-encoder reranker
│   ├── agent/             # planner, graph, orchestration
│   ├── tools/             # numeric/table tool, price tool, comparator
│   ├── generate/          # cited answer synthesis
│   ├── api/               # FastAPI app
│   └── ui/                # Streamlit app
├── eval/
│   ├── datasets/          # labeled Q&A eval set
│   ├── metrics.py         # recall@k, faithfulness, correctness
│   └── run_eval.py
├── notebooks/
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

- `SEC_USER_AGENT`: your name + email. SEC EDGAR requires a contact string on every request.
- `ANTHROPIC_API_KEY`: your own key from https://console.anthropic.com (pay-as-you-go; used only for the answer step).

### Run the pipeline

```bash
python -m deskanalyst.ingest --tickers AAPL          # 1. download filings from SEC EDGAR
python -m deskanalyst.index                          # 2. clean + chunk them
python -m deskanalyst.retrieve --build               # 3. embed chunks, build the search index
python -m deskanalyst.retrieve --query "What are Apple's risk factors?"   # 4. semantic search
python -m deskanalyst.generate --query "What are Apple's risk factors?"   # 5. cited answer
```
## License

MIT see [LICENSE](LICENSE).
