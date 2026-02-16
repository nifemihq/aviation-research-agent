import time
from app.telemetry import log_event

from app.exporter import save_markdown

from pathlib import Path
from rich import print

from app.tools.retriever import build_chunks, retrieve
from app.writer import draft_onepager

import uuid
run_id = str(uuid.uuid4())

def format_citation(ch) -> str:
    if ch.page is not None:
        return f"[{ch.doc_id} p.{ch.page} chunk#{ch.chunk_id}]"
    return f"[{ch.doc_id} chunk#{ch.chunk_id}]"


def main():
    print("[bold green]Aviation Research Agent (MVP)[/bold green]")

    sources_dir = Path("data/sources")
    chunks = build_chunks(sources_dir)
    print(f"Loaded {len(chunks)} chunks from {sources_dir}")
    log_event("sources_loaded", {"num_chunks": len(chunks)})

    query = input("\nAsk a question: ").strip()
    if not query:
        print("[yellow]No question entered.[/yellow]")
        return

    start = time.time()
    log_event("query_received", {"query": query})

    requested_top_k = 5
    hits = retrieve(query, chunks, top_k=requested_top_k)

    if not hits:
        log_event(
            "retrieval_empty", {"query": query, "requested_top_k": requested_top_k}
        )
        print("[red]No relevant passages found in your local sources.[/red]")
        print(
            "Tip: add more docs to data/sources/ or ask a question using keywords in your docs."
        )
        return

    log_event(
        "retrieval_done",
        {
            "query": query,
            "requested_top_k": requested_top_k,
            "num_hits": len(hits),
            "citations": [
                {
                    "doc_id": ch.doc_id,
                    "page": ch.page,
                    "chunk_id": ch.chunk_id,
                    "score": score,
                }
                for score, ch in hits
            ],
        },
    )

    evidence_texts = [ch.text for _, ch in hits]
    print("\n[bold yellow]Generating one-pager draft...[/bold yellow]\n")

    try:
        draft = draft_onepager(query, evidence_texts)
    except Exception as e:
        log_event("generation_failed", {"query": query, "error": str(e)})
        raise

    print("[bold green]=== ONE-PAGER DRAFT ===[/bold green]\n")
    print(draft)

    out_path = save_markdown(query, draft)
    print(f"\n[bold cyan]Saved to:[/bold cyan] {out_path}")
    log_event("export_saved", {"query": query, "path": out_path})


    latency = round(time.time() - start, 3)

    log_event(
        "response_ready",
        {
            "query": query,
            "latency_sec": latency,
            "output_length": len(draft),
        },
    )
    log_event("config", {"run_id": run_id, "mode": "llm", "model": "gemini-2.0-flash"})

if __name__ == "__main__":
    main()
