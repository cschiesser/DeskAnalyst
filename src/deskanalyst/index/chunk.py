from __future__ import annotations


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    """Split text into overlapping chunks of ~`size` words (overlap in words).

    Smaller chunks = more precise retrieval but less context per chunk.
    Overlap keeps a sentence that straddles a boundary from being lost.
    """
    words = text.split()
    if not words:
        return []

    step = max(1, size - overlap)
    chunks: list[str] = []
    for start in range(0, len(words), step):
        window = words[start : start + size]
        if not window:
            break
        chunks.append(" ".join(window))
        if start + size >= len(words):
            break
    return chunks
