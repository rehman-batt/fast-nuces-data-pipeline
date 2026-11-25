"""Validation and normalization of collected HTML and PDF page records."""
from datetime import datetime
from hashlib import sha256
from .crawler import normalize


def validate_page(record):
    if not isinstance(record, dict):
        raise ValueError('record must be an object')
    url = normalize(record.get('url', ''))
    if not url:
        raise ValueError('url must be an HTTP(S) URL')
    text = record.get('text')
    if not isinstance(text, str):
        raise ValueError('text must be a string')
    digest = record.get('sha256')
    if digest != sha256(text.encode('utf-8')).hexdigest():
        raise ValueError('sha256 does not match text')
    content_type = record.get('content_type')
    if content_type not in ('text/html', 'application/xhtml+xml', 'application/pdf'):
        raise ValueError('unsupported content_type')
    timestamp = record.get('crawled_at') or record.get('processed_at')
    try:
        parsed = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            raise ValueError('timestamp must include timezone')
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError('invalid or missing timezone-aware timestamp') from exc
    page = record.get('page')
    if content_type == 'application/pdf' and (type(page) is not int or page < 1):
        raise ValueError('PDF page must be a positive integer')
    title = record.get('title') or url
    if not isinstance(title, str):
        raise ValueError('title must be a string')
    return {'url': url, 'title': title, 'timestamp': timestamp, 'timestamp_kind': 'crawled_at' if record.get('crawled_at') else 'processed_at', 'page': page, 'text': text, 'sha256': digest, 'content_type': content_type}
