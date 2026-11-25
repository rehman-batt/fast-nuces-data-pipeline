"""Extract text from a local, authorized PDF with page-level provenance."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

from .crawler import normalize


def extract_pdf(source, url, destination, max_bytes=10_000_000):
    """Write one record per PDF page; empty text is flagged for manual review."""
    try:
        from pypdf import PdfReader
        from pypdf.errors import PdfReadError
    except ImportError as exc:
        raise ValueError("PDF support requires installing the pdf extra: pip install -e '.[pdf]'") from exc
    url = normalize(url)
    if not url:
        raise ValueError("A valid HTTP(S) source URL is required")
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError("Input and output must be different files")
    if source.stat().st_size > max_bytes:
        raise ValueError("PDF exceeds size limit")
    try:
        reader = PdfReader(source, strict=True)
        if reader.is_encrypted:
            raise ValueError("Encrypted PDF is not supported")
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('x', encoding='utf-8') as out:
            for index, page in enumerate(reader.pages, start=1):
                text = (page.extract_text() or '').strip()
                record = {'url': url, 'page': index, 'processed_at': datetime.now(timezone.utc).isoformat(), 'content_type': 'application/pdf', 'sha256': sha256(text.encode()).hexdigest(), 'text': text, 'needs_ocr_review': not bool(text)}
                out.write(json.dumps(record, ensure_ascii=False) + '\n')
        return len(reader.pages)
    except PdfReadError as exc:
        raise ValueError('Invalid or unreadable PDF') from exc
