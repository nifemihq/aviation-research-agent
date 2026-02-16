from pathlib import Path
from rich import print

from app.tools.retriever import build_chunks, retrieve
from app.writer import draft_onepager


def format_citation(ch) -> str:
    if ch.page is not None:
        return f"[{ch.doc_id} p.{ch.page} chunk#{ch.chunk_id}]"
    return f"[{ch.doc_id} chunk#{ch.chunk_id}]"


def main():
    print("[bold green]Aviation Research Agent (MVP)[/bold green]")

    sources_dir = Path("data/sources")
    chunks = build_chunks(sources_dir)
    print(f"Loaded {len(chunks)} chunks from {sources_dir}")

    query = input("\nAsk a question: ").strip()
    if not query:
        print("[yellow]No question entered.[/yellow]")
        return

    hits = retrieve(query, chunks, top_k=5)

    if not hits:
        print("[red]No relevant passages found in your local sources.[/red]")
        print(
            "Tip: add more docs to data/sources/ or ask a question using keywords in your docs."
        )
        return

    print("\n[bold]Top retrieved snippets (grounding evidence):[/bold]\n")
    for score, ch in hits:
        print(f"[cyan]Score {score}[/cyan] {format_citation(ch)}")
        print(ch.text)
        print("-" * 80)

    # Collect texts only
    evidence_texts = [ch.text for _, ch in hits]
    print("\n[bold yellow]Generating one-pager draft...[/bold yellow]\n")

    draft = draft_onepager(query, evidence_texts)
    print("[bold green]=== ONE-PAGER DRAFT ===[/bold green]\n")
    print(draft)


if __name__ == "__main__":
    main()
