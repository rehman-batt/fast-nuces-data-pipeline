"""Deduplicate pages and produce source-linked retrieval chunks."""
import json
from pathlib import Path
import re


def prepare(source, destination, chunk_size=1200, overlap=150):
    if chunk_size < 1 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Require chunk_size > overlap >= 0")
    if Path(source).resolve() == Path(destination).resolve():
        raise ValueError("Input and output must be different files")
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    seen, pages, chunks = set(), 0, 0
    with open(source, encoding="utf-8") as src, destination.open("w", encoding="utf-8") as out:
        for line in src:
            page = json.loads(line)
            text = re.sub(r"[ \t]+", " ", page["text"]).strip()
            if not text or page["sha256"] in seen:
                continue
            seen.add(page["sha256"])
            pages += 1
            start, index = 0, 0
            while start < len(text):
                end = min(start + chunk_size, len(text))
                if end < len(text):
                    boundary = text.rfind(" ", start + chunk_size // 2, end)
                    if boundary > start:
                        end = boundary
                chunk = {"id": f"{page['sha256']}:{index}", "url": page["url"], "title": page["title"], "crawled_at": page["crawled_at"], "text": text[start:end].strip()}
                out.write(json.dumps(chunk, ensure_ascii=False) + "\n")
                chunks += 1
                index += 1
                if end == len(text):
                    break
                start = max(start + 1, end - overlap)
    return pages, chunks
