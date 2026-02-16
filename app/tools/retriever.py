from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict
import re

from pypdf import PdfReader


@dataclass
class Chunk:
    doc_id: str
    source_path: str
    page: int | None
    chunk_id: int
    text: str


def _read_pdf(path: Path) -> List[Tuple[int, str]]:
    """Return list of (page_number_1indexed, text)."""
    reader = PdfReader(str(path))
    pages: List[Tuple[int, str]] = []
    for i, page in enumerate(reader.pages):
        txt = page.extract_text() or ""
        # normalize whitespace a bit
        txt = re.sub(r"\s+", " ", txt).strip()
        if txt:
            pages.append((i + 1, txt))
    return pages


def _read_text(path: Path) -> str:
    txt = path.read_text(encoding="utf-8", errors="ignore")
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


def chunk_text(text: str, *, chunk_size: int = 900, overlap: int = 150) -> List[str]:
    """
    Very simple character-based chunker.
    Good enough for MVP. We'll improve later.
    """
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be > overlap")

    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
        if start < 0:
            start = 0
        if end == n:
            break
    return chunks


def build_chunks(sources_dir: Path) -> List[Chunk]:
    chunks: List[Chunk] = []
    sources_dir = sources_dir.resolve()

    supported = {".pdf", ".txt", ".md"}
    files = [
        p
        for p in sources_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in supported
    ]

    if not files:
        raise FileNotFoundError(
            f"No supported files found in {sources_dir} (pdf/txt/md)."
        )

    for f in sorted(files):
        doc_id = f.stem

        if f.suffix.lower() == ".pdf":
            page_texts = _read_pdf(f)
            chunk_id = 0
            for page_num, page_txt in page_texts:
                for piece in chunk_text(page_txt):
                    chunks.append(
                        Chunk(
                            doc_id=doc_id,
                            source_path=str(f),
                            page=page_num,
                            chunk_id=chunk_id,
                            text=piece,
                        )
                    )
                    chunk_id += 1
        else:
            txt = _read_text(f)
            chunk_id = 0
            for piece in chunk_text(txt):
                chunks.append(
                    Chunk(
                        doc_id=doc_id,
                        source_path=str(f),
                        page=None,
                        chunk_id=chunk_id,
                        text=piece,
                    )
                )
                chunk_id += 1

    return chunks


def _tokenize(s: str) -> List[str]:
    # lowercase, keep alphanumerics, split
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return [t for t in s.split() if len(t) > 1]


def score_chunk(query: str, chunk_text: str) -> int:
    """
    Simple lexical score: counts overlap of query tokens with chunk tokens.
    MVP approach; later we can add embeddings.
    """
    q = _tokenize(query)
    if not q:
        return 0
    chunk_tokens = set(_tokenize(chunk_text))
    return sum(1 for t in q if t in chunk_tokens)


def retrieve(
    query: str, chunks: List[Chunk], *, top_k: int = 5
) -> List[Tuple[int, Chunk]]:
    scored: List[Tuple[int, Chunk]] = []
    for ch in chunks:
        s = score_chunk(query, ch.text)
        if s > 0:
            scored.append((s, ch))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_k]
