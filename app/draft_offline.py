from __future__ import annotations
from typing import List, Tuple
from app.tools.retriever import Chunk


def cite(ch: Chunk) -> str:
    if ch.page is not None:
        return f"(Source: {ch.doc_id} p.{ch.page})"
    return f"(Source: {ch.doc_id})"


def offline_onepager(query: str, hits: List[Tuple[int, Chunk]]) -> str:
    # A grounded “draft” without an LLM: evidence + structured scaffold
    lines = []
    lines.append("Summary:")
    lines.append(f"- This section addresses: {query}")
    lines.append("- Evidence indicates the following key points:\n")

    lines.append("Key Findings:")
    for score, ch in hits[:3]:
        snippet = ch.text.strip()
        if len(snippet) > 300:
            snippet = snippet[:300].rstrip() + "..."
        lines.append(f"- {snippet} {cite(ch)}")

    lines.append("\nLimitations:")
    lines.append(
        "- This draft is extractive (no generation). It only surfaces evidence from your local sources."
    )
    lines.append(
        "- If retrieval misses relevant passages, the draft will be incomplete."
    )

    return "\n".join(lines)
