from __future__ import annotations

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "default.yaml"

load_dotenv(REPO_ROOT / ".env")


def load_config(path: str | Path | None = None) -> dict:
    """Load the YAML config (defaults to configs/default.yaml)."""
    path = Path(path) if path else DEFAULT_CONFIG_PATH
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_sec_user_agent() -> str:
    """Return the SEC User-Agent, or fail loudly if it's missing/placeholder."""
    ua = os.getenv("SEC_USER_AGENT", "").strip()
    if not ua or "your-name" in ua or "your@email" in ua:
        raise RuntimeError(
            "SEC_USER_AGENT is not set. Copy .env.example to .env and set a real "
            "contact string, e.g. 'DeskAnalyst Colin Schiesser colin@example.com'. "
            "EDGAR blocks requests without a descriptive User-Agent."
        )
    return ua
