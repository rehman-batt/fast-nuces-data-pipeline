"""Validate, deduplicate and prepare source-linked retrieval chunks."""
import json
import os
from pathlib import Path
import re
import tempfile
from .schema import validate_page


def prepare(source, destination, chunk_size=1200, overlap=150):
    if chunk_size < 1 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Require chunk_size > overlap >= 0")
    if Path(source).resolve() == Path(destination).resolve():
        raise ValueError("Input and output must be different files")
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    seen, pages, chunks = set(), 0, 0
    temp_path = None
    try:
        with open(source, encoding='utf-8') as src, tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=destination.parent, delete=False) as out:
            temp_path = Path(out.name)
            for line_number, line in enumerate(src, start=1):
                try:
                    page = validate_page(json.loads(line))
                except (ValueError, TypeError) as exc:
                    raise ValueError(f'Invalid record at line {line_number}: {exc}') from exc
                text = re.sub(r'[ \t]+', ' ', page['text']).strip()
                if not text or page['sha256'] in seen:
                    continue
                seen.add(page['sha256'])
                pages += 1
                start, index = 0, 0
                while start < len(text):
                    end = min(start + chunk_size, len(text))
                    if end < len(text):
                        boundary = text.rfind(' ', start + chunk_size // 2, end)
                        if boundary > start:
                            end = boundary
                    chunk = {'id': f"{page['sha256']}:{index}", 'url': page['url'], 'title': page['title'], 'source_timestamp': page['timestamp'], 'timestamp_kind': page['timestamp_kind'], 'source_page': page['page'], 'content_type': page['content_type'], 'text': text[start:end].strip()}
                    out.write(json.dumps(chunk, ensure_ascii=False) + '\n')
                    chunks += 1
                    index += 1
                    if end == len(text):
                        break
                    start = max(start + 1, end - overlap)
        os.replace(temp_path, destination)
        temp_path = None
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
    return pages, chunks
