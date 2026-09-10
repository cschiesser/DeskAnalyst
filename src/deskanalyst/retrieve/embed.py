from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer

# Small, fast, runs on CPU. First use downloads ~90 MB.
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def embed_texts(texts: list[str], show_progress: bool = False):
    """Turn texts into normalized embedding vectors (numpy array, one row per text)."""
    return _model().encode(
        texts,
        batch_size=32,
        show_progress_bar=show_progress,
        normalize_embeddings=True,  # makes cosine similarity == dot product
        convert_to_numpy=True,
    )
