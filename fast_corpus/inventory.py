"""Historical crawl recovery and summaries of local inventory events."""
from collections import Counter
import json
from pathlib import Path

from .crawler import normalize


def import_pages(source, output):
    """Recover collected page observations only; do not infer past failures."""
    source, output = Path(source), Path(output)
    if source.resolve() == output.resolve():
        raise ValueError('Source and inventory output must differ')
    events = []
    with source.open(encoding='utf-8') as stream:
        for number, line in enumerate(stream, 1):
            try:
                row = json.loads(line)
                url = normalize(row['url'])
                if not url or not isinstance(row['crawled_at'], str) or not isinstance(row['sha256'], str):
                    raise ValueError('invalid required fields')
                if row.get('content_type') not in ('text/html', 'application/xhtml+xml'):
                    raise ValueError('not an HTML crawl record')
                events.append({'event': 'collected', 'url': url, 'at': row['crawled_at'], 'content_type': row['content_type'], 'sha256': row['sha256'], 'output': str(source), 'origin': 'historical_import', 'source_line': number})
            except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
                raise ValueError(f'Invalid HTML page record at line {number}') from exc
    if not events:
        raise ValueError('No HTML page records found')
    payload = ''.join(json.dumps(event, ensure_ascii=False) + '\n' for event in events)
    if output.exists():
        if output.read_text(encoding='utf-8') == payload:
            return len(events)
        raise FileExistsError(f'Inventory already exists: {output}')
    with output.open('x', encoding='utf-8') as stream:
        stream.write(payload)
    return len(events)


def report(paths):
    """Report event and unique URL counts; type counts are observed URL/type pairs."""
    events, observed = Counter(), set()
    discovered, collected, attempted = set(), set(), set()
    historical, completed = 0, 0
    for path in paths:
        with Path(path).open(encoding='utf-8') as stream:
            for number, line in enumerate(stream, 1):
                try:
                    row = json.loads(line)
                    event, url = row['event'], row['url']
                    if not isinstance(event, str) or not isinstance(url, str):
                        raise ValueError('invalid event or URL')
                except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
                    raise ValueError(f'Invalid inventory record in {path} at line {number}') from exc
                events[event] += 1
                if event == 'discovered': discovered.add(url)
                if event == 'attempted': attempted.add(url)
                if event == 'collected':
                    collected.add(url)
                    if row.get('origin') == 'historical_import': historical += 1
                if event in ('response', 'collected'):
                    observed.add((url, row.get('content_type') or 'unknown'))
                if event == 'run_finished': completed += 1
    types = Counter(kind for _, kind in observed)
    return {'files': len(paths), 'completed_run_events': completed, 'historical_collected_events': historical, 'unique_discovered_urls': len(discovered), 'unique_attempted_urls': len(attempted), 'unique_collected_urls': len(collected), 'observed_url_content_types': dict(sorted(types.items())), 'event_counts': dict(sorted(events.items()))}
