"""Validate, deduplicate and prepare source-linked retrieval chunks."""
import json
import os
from pathlib import Path
import re
import tempfile
from .schema import validate_page


def _read_page(line, line_number):
    try:
        return validate_page(json.loads(line))
    except (ValueError, TypeError) as exc:
        raise ValueError(f'Invalid record at line {line_number}: {exc}') from exc


def prepare(source, destination, chunk_size=1200, overlap=150):
    if chunk_size < 1 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Require chunk_size > overlap >= 0")
    if Path(source).resolve() == Path(destination).resolve():
        raise ValueError("Input and output must be different files")
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    pages = chunks = 0
    try:
        with open(source, encoding='utf-8') as src:
            sources_by_hash = {}
            for number, line in enumerate(src, start=1):
                page = _read_page(line, number)
                if not page['text'].strip():
                    continue
                source_info = {'url': page['url'], 'title': page['title'], 'source_timestamp': page['timestamp'], 'timestamp_kind': page['timestamp_kind'], 'source_page': page['page'], 'content_type': page['content_type']}
                sources = sources_by_hash.setdefault(page['sha256'], [])
                if source_info not in sources:
                    sources.append(source_info)
            src.seek(0)
            seen = set()
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=destination.parent, delete=False) as out:
                temp_path = Path(out.name)
                for number, line in enumerate(src, start=1):
                    page = _read_page(line, number)
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
                        primary = sources_by_hash[page['sha256']][0]
                        chunk = {'id': f"{page['sha256']}:{index}", **primary, 'sources': sources_by_hash[page['sha256']], 'text': text[start:end].strip()}
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
