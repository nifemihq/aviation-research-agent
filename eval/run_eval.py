import os
from app.draft_offline import offline_onepager

import time
import json
from pathlib import Path

from app.tools.retriever import build_chunks, retrieve
from app.writer import draft_onepager

def llm_enabled() -> bool:
    return os.getenv("USE_LLM", "0") == "1"  # default OFF

def has_citation(text: str) -> bool:
    return "(Source:" in text

def llm_enabled() -> bool:
    return os.getenv("USE_LLM", "1") == "1"

def main():
    cases_path = Path("eval/cases.jsonl")
    sources_dir = Path("data/sources")

    chunks = build_chunks(sources_dir)

    results = []

    with cases_path.open() as f:
        for line in f:
            case = json.loads(line)
            query = case["query"]

            start = time.time()

            hits = retrieve(query, chunks, top_k=5)
            evidence = [ch.text for _, ch in hits]

            # print("LLM enabled?", llm_enabled())
            if llm_enabled():
                 output = draft_onepager(query, evidence)
            else:
                output = offline_onepager(query, hits)

            latency = time.time() - start

            result = {
                "query": query,
                "latency_sec": round(latency, 2),
                "has_citation": has_citation(output),
                "output_length": len(output),
            }

            print(result)
            results.append(result)

    # summary
    avg_latency = sum(r["latency_sec"] for r in results) / len(results)
    citation_rate = sum(r["has_citation"] for r in results) / len(results)

    print("\n=== SUMMARY ===")
    print("Avg latency:", round(avg_latency, 2))
    print("Citation rate:", round(citation_rate * 100, 1), "%")


if __name__ == "__main__":
    main()
