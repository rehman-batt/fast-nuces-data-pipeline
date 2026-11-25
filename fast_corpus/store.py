"""Build and query a local, source-linked SQLite full-text snapshot."""
from datetime import datetime, timezone
from contextlib import closing
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
from urllib.parse import urlsplit

SCHEMA_VERSION = '1'


def _validate_chunk(row):
    if not isinstance(row, dict):
        raise ValueError('chunk must be an object')
    for key in ('id', 'text', 'url', 'title', 'source_timestamp', 'timestamp_kind', 'content_type'):
        if not isinstance(row.get(key), str) or not row[key].strip():
            raise ValueError(f'{key} must be a non-empty string')
    if row['timestamp_kind'] not in ('crawled_at', 'processed_at'):
        raise ValueError('invalid timestamp_kind')
    if row.get('kind', 'text') not in ('text', 'table_row'):
        raise ValueError('unsupported chunk kind')
    if row.get('kind') == 'table_row' and any(type(row.get(key)) is not int or row[key] < 0 for key in ('table_index', 'row_index')):
        raise ValueError('table chunks require non-negative table_index and row_index')
    if row.get('needs_ocr_review', False) is not False:
        raise ValueError('unreviewed OCR cannot be indexed')
    def validate_source(source):
        if not isinstance(source, dict):
            raise ValueError('source must be an object')
        for key in ('url', 'title', 'source_timestamp', 'timestamp_kind', 'content_type'):
            if not isinstance(source.get(key), str) or not source[key].strip():
                raise ValueError(f'source {key} must be a non-empty string')
        if source.get('needs_ocr_review', False) is not False:
            raise ValueError('unreviewed OCR source cannot be indexed')
        parts = urlsplit(source['url'])
        if parts.scheme not in ('http', 'https') or not parts.hostname or parts.username or parts.password:
            raise ValueError('source URL must be HTTP(S) without credentials')
        try:
            parsed = datetime.fromisoformat(source['source_timestamp'].replace('Z', '+00:00'))
            if parsed.tzinfo is None:
                raise ValueError('missing timezone')
        except ValueError as exc:
            raise ValueError('source timestamp must be timezone-aware') from exc
        if source['timestamp_kind'] not in ('crawled_at', 'processed_at'):
            raise ValueError('invalid source timestamp_kind')
        if source['content_type'] not in ('text/html', 'application/xhtml+xml', 'application/pdf'):
            raise ValueError('unsupported source content type')
        page = source.get('source_page')
        if source['content_type'] == 'application/pdf' and (type(page) is not int or page < 1):
            raise ValueError('PDF source page must be a positive integer')
    validate_source(row)
    sources = row.get('sources')
    if not isinstance(sources, list) or not sources:
        raise ValueError('sources must be a non-empty list')
    for source in sources:
        validate_source(source)
    fields = ('url', 'title', 'source_timestamp', 'timestamp_kind', 'source_page', 'content_type')
    if not any(all(source.get(key) == row.get(key) for key in fields) for source in sources):
        raise ValueError('primary source metadata must appear in sources')
    return row


def build_store(source, destination, replace=False):
    """Atomically replace a store after every input chunk validates."""
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError('input and store paths must differ')
    if not replace and destination.exists():
        raise ValueError('store already exists; use --replace to rebuild')
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, filename = tempfile.mkstemp(prefix='.fast-store-', suffix='.sqlite', dir=destination.parent)
    os.close(fd)
    temp_path = Path(filename)
    digest, count = sha256(), 0
    connection = None
    try:
        connection = sqlite3.connect(temp_path)
        connection.execute('CREATE TABLE chunks (id TEXT PRIMARY KEY, payload TEXT NOT NULL)')
        connection.execute("CREATE VIRTUAL TABLE chunk_fts USING fts5(id UNINDEXED, text, tokenize='porter unicode61')")
        connection.execute('CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
        with source.open('rb') as handle:
            for number, raw in enumerate(handle, 1):
                digest.update(raw)
                try:
                    row = _validate_chunk(json.loads(raw.decode('utf-8')))
                    payload = json.dumps(row, ensure_ascii=False, sort_keys=True)
                    connection.execute('INSERT INTO chunks(id, payload) VALUES (?, ?)', (row['id'], payload))
                    connection.execute('INSERT INTO chunk_fts(id, text) VALUES (?, ?)', (row['id'], row['text']))
                except (ValueError, TypeError, UnicodeError, sqlite3.IntegrityError) as exc:
                    raise ValueError(f'invalid chunk at line {number}: {exc}') from exc
                count += 1
        if count == 0:
            raise ValueError('input contains no chunks')
        info = {'schema_version': SCHEMA_VERSION, 'input_sha256': digest.hexdigest(), 'input_name': source.name, 'chunk_count': str(count), 'created_at': datetime.now(timezone.utc).isoformat(), 'search': 'sqlite-fts5-porter'}
        connection.executemany('INSERT INTO metadata(key, value) VALUES (?, ?)', info.items())
        connection.commit()
        connection.close()
        connection = None
        if replace:
            os.replace(temp_path, destination)
        else:
            os.link(temp_path, destination)
        return info
    finally:
        if connection is not None:
            connection.close()
        temp_path.unlink(missing_ok=True)


def _open_readonly(path):
    path = Path(path).resolve()
    if not path.is_file():
        raise ValueError('store does not exist')
    return sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)


def store_info(path):
    with closing(_open_readonly(path)) as connection:
        info = dict(connection.execute('SELECT key, value FROM metadata'))
    if info.get('schema_version') != SCHEMA_VERSION:
        raise ValueError('unsupported store schema version')
    return info


def search_store(path, query, limit=5):
    if not isinstance(query, str) or len(query) > 2000:
        raise ValueError('query must be text of at most 2000 characters')
    if limit < 1 or limit > 100:
        raise ValueError('limit must be between 1 and 100')
    if not Path(path).is_file():
        raise ValueError('store does not exist')
    terms = list(dict.fromkeys(re.findall(r'[^\W_]+', query.casefold(), flags=re.UNICODE)))
    if not terms:
        return []
    if len(terms) > 50:
        raise ValueError('query has more than 50 distinct terms')
    expression = ' OR '.join(f'"{term}"' for term in terms)
    with closing(_open_readonly(path)) as connection:
        schema = connection.execute("SELECT value FROM metadata WHERE key='schema_version'").fetchone()
        if not schema or schema[0] != SCHEMA_VERSION:
            raise ValueError('unsupported store schema version')
        rows = connection.execute('SELECT chunks.payload, bm25(chunk_fts) AS rank FROM chunk_fts JOIN chunks ON chunks.id = chunk_fts.id WHERE chunk_fts MATCH ? ORDER BY rank ASC, chunks.id ASC LIMIT ?', (expression, limit)).fetchall()
    return [{'score': -score, 'chunk': json.loads(payload)} for payload, score in rows]
