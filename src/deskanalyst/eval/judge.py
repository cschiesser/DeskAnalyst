from __future__ import annotations

from anthropic import Anthropic

JUDGE_MODEL = "claude-haiku-4-5-20251001"


def _yes_no(prompt: str) -> bool:
    client = Anthropic()
    resp = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=5,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text").strip().upper()
    return text.startswith("YES")


def judge_faithfulness(answer: str, context: str) -> bool:
    """Is every factual claim in the answer supported by the retrieved sources?"""
    prompt = (
        "Grade whether an answer is fully supported by the given sources. Reply with only "
        "YES or NO. YES if every factual claim in the ANSWER is supported by the SOURCES, "
        "otherwise NO.\n\n"
        f"SOURCES:\n{context}\n\nANSWER:\n{answer}"
    )
    return _yes_no(prompt)


def judge_correctness(answer: str, reference: str, question: str) -> bool:
    """Does the answer capture the key facts of the reference answer?"""
    prompt = (
        "Grade whether a candidate answer matches the reference answer for a question. "
        "Reply with only YES or NO. YES if the candidate captures the key facts of the "
        "reference (wording may differ), otherwise NO.\n\n"
        f"QUESTION: {question}\n\nREFERENCE:\n{reference}\n\nCANDIDATE:\n{answer}"
    )
    return _yes_no(prompt)
