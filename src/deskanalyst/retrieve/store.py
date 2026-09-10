from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from deskanalyst.retrieve.embed import embed_texts

EMB_FILE = "embeddings.npy"
META_FILE = "meta.jsonl"


def _read_jsonl(path: Path) -> list[dict]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(ln) for ln in lines if ln.strip()]


def build_index(data_dir: str | Path) -> int:
    """Embed every chunk in chunks.jsonl and save the index under data/index/."""
    data_dir = Path(data_dir)
    chunks_path = data_dir / "chunks.jsonl"
    if not chunks_path.exists():
        raise FileNotFoundError(
            f"No chunks at {chunks_path}. Run `python -m deskanalyst.index` first."
        )

    records = _read_jsonl(chunks_path)
    texts = [r["text"] for r in records]
    print(f"Embedding {len(texts)} chunks (first run downloads the model)...")
    vectors = embed_texts(texts, show_progress=True).astype("float32")

    index_dir = data_dir / "index"
    index_dir.mkdir(parents=True, exist_ok=True)
    np.save(index_dir / EMB_FILE, vectors)
    with (index_dir / META_FILE).open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    print(f"Saved index for {len(records)} chunks to {index_dir}")
    return len(records)


def load_index(data_dir: str | Path):
    data_dir = Path(data_dir)
    index_dir = data_dir / "index"
    vectors = np.load(index_dir / EMB_FILE)
    records = _read_jsonl(index_dir / META_FILE)
    return vectors, records


def search(query: str, data_dir: str | Path, k: int = 5) -> list[tuple[float, dict]]:
    """Return the k chunks most similar in meaning to the query."""
    vectors, records = load_index(data_dir)
    q = embed_texts([query]).astype("float32")[0]
    scores = vectors @ q  # cosine similarity (vectors are normalized)
    top = np.argsort(scores)[::-1][:k]
    return [(float(scores[i]), records[i]) for i in top]
