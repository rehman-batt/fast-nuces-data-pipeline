"""Extract local PDF pages, with optional OCR for pages without native text."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory

from .crawler import normalize


def _ocr_page(source, page_number, directory):
    prefix = Path(directory) / f'page-{page_number}'
    try:
        subprocess.run(['pdftoppm', '-f', str(page_number), '-l', str(page_number), '-r', '200', '-png', '-singlefile', str(source), str(prefix)], check=True, capture_output=True, timeout=60)
        result = subprocess.run(['tesseract', str(prefix) + '.png', 'stdout', '-l', 'eng'], check=True, capture_output=True, text=True, timeout=120)
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError(f'OCR failed on page {page_number}: {exc}') from exc


def extract_pdf(source, url, destination, max_bytes=10_000_000, ocr=False, max_pages=100):
    """Write page records; OCR output is explicitly flagged for human review."""
    try:
        from pypdf import PdfReader
        from pypdf.errors import PdfReadError
    except ImportError as exc:
        raise ValueError("PDF support requires installing the pdf extra: pip install -e '.[pdf]'") from exc
    url = normalize(url)
    if not url:
        raise ValueError('A valid HTTP(S) source URL is required')
    if max_bytes < 1 or max_pages < 1:
        raise ValueError('PDF size and page limits must be positive')
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError('Input and output must be different files')
    if source.stat().st_size > max_bytes:
        raise ValueError('PDF exceeds size limit')
    if ocr and (not shutil.which('pdftoppm') or not shutil.which('tesseract')):
        raise ValueError('OCR requires pdftoppm and tesseract on PATH')
    created = False
    try:
        reader = PdfReader(source, strict=True)
        if reader.is_encrypted:
            raise ValueError('Encrypted PDF is not supported')
        if len(reader.pages) > max_pages:
            raise ValueError('PDF exceeds page limit')
        document_hash = sha256(source.read_bytes()).hexdigest()
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('x', encoding='utf-8') as out, TemporaryDirectory() as tmp:
            created = True
            for index, page in enumerate(reader.pages, start=1):
                text = (page.extract_text() or '').strip()
                method = 'native'
                if not text and ocr:
                    text = _ocr_page(source, index, tmp)
                    method = 'ocr'
                record = {'url': url, 'page': index, 'processed_at': datetime.now(timezone.utc).isoformat(), 'content_type': 'application/pdf', 'document_sha256': document_hash, 'sha256': sha256(text.encode()).hexdigest(), 'text': text, 'extraction_method': method, 'needs_ocr_review': method == 'ocr' or not bool(text)}
                out.write(json.dumps(record, ensure_ascii=False) + '\n')
        return len(reader.pages)
    except PdfReadError as exc:
        if created:
            destination.unlink(missing_ok=True)
        raise ValueError('Invalid or unreadable PDF') from exc
    except Exception:
        if created:
            destination.unlink(missing_ok=True)
        raise
