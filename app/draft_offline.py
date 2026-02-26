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
        "what evidence does NOT cover"
    )

    return "\n".join(lines)


if __name__ == "__main__":
    from pathlib import Path
    from rich import print

    from app.tools.retriever import build_chunks, retrieve
    from app.exporter import save_markdown

    print("[bold green]Aviation Research Agent (OFFLINE)[/bold green]")

    sources_dir = Path("data/sources")
    chunks = build_chunks(sources_dir)
    print(f"Loaded {len(chunks)} chunks from {sources_dir}")

    query = input("\nAsk a question: ").strip()
    if not query:
        print("[yellow]No question entered.[/yellow]")
        raise SystemExit(0)

    hits = retrieve(query, chunks, top_k=5)
    if not hits:
        print("[red]No relevant passages found in your local sources.[/red]")
        raise SystemExit(0)

    draft = offline_onepager(query, hits)

    print("\n[bold green]=== OFFLINE ONE-PAGER ===[/bold green]\n")
    print(draft)

    out_path = save_markdown(query, draft)
    print(f"\n[bold cyan]Saved to:[/bold cyan] {out_path}")
