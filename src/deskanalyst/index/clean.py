from __future__ import annotations

import re

from bs4 import BeautifulSoup


def html_to_text(html: str) -> str:
    """Strip HTML/formatting from a filing and return readable plain text."""
    soup = BeautifulSoup(html, "lxml")

    # drop code/style blocks entirely
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    # collapse runs of spaces/tabs, drop blank lines
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines)
