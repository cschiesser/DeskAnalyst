from __future__ import annotations

from deskanalyst.config import REPO_ROOT, load_config
from deskanalyst.index import build_chunks


def main() -> None:
    cfg = load_config()
    retrieval = cfg["retrieval"]
    build_chunks(
        data_dir=REPO_ROOT / cfg["data_dir"],
        size=retrieval["chunk_size"],
        overlap=retrieval["chunk_overlap"],
    )


if __name__ == "__main__":
    main()
