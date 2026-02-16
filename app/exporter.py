from __future__ import annotations
from pathlib import Path
from datetime import datetime


def save_markdown(query: str, draft: str, *, out_dir: str = "outputs") -> str:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = (
        "".join(ch if ch.isalnum() or ch in "-_ " else "_" for ch in query)[:50]
        .strip()
        .replace(" ", "_")
    )
    filename = f"{ts}_{safe}.md"
    path = Path(out_dir) / filename

    content = f"""# One-Pager Draft

**Query:** {query}

---

{draft}
"""
    path.write_text(content, encoding="utf-8")
    return str(path)
