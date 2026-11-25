"""Validate a model-neutral, source-grounded training manifest."""
import json
from datetime import date
from .crawler import normalize


def validate_training(path, evaluation_questions=None):
    seen_questions = {}
    source_splits = {}
    issues = []
    counts = {'train': 0, 'validation': 0}
    eval_questions = {' '.join(row['question'].split()).casefold() for row in (evaluation_questions or [])}
    eval_sources = {normalize(url) for row in (evaluation_questions or []) for url in row['expected_urls']}
    with open(path, encoding='utf-8') as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError('record must be an object')
                for field in ('question', 'answer', 'evidence', 'source_url', 'source_date', 'split'):
                    if not isinstance(row.get(field), str) or not row[field].strip():
                        raise ValueError(f'{field} must be a non-empty string')
                if row['split'] not in counts:
                    raise ValueError('split must be train or validation')
                url = normalize(row['source_url'])
                if not url:
                    raise ValueError('invalid source_url')
                try:
                    if date.fromisoformat(row['source_date']).isoformat() != row['source_date']:
                        raise ValueError('not canonical')
                except ValueError as exc:
                    raise ValueError('source_date must be YYYY-MM-DD') from exc
                question = ' '.join(row['question'].split()).casefold()
                if question in seen_questions:
                    issues.append(f'line {line_number}: duplicate question (line {seen_questions[question]})')
                else:
                    seen_questions[question] = line_number
                if question in eval_questions:
                    issues.append(f'line {line_number}: question overlaps development evaluation')
                if url in eval_sources:
                    issues.append(f'line {line_number}: source overlaps development evaluation')
                previous = source_splits.setdefault(url, row['split'])
                if previous != row['split']:
                    issues.append(f'line {line_number}: source appears in multiple splits')
                counts[row['split']] += 1
            except (json.JSONDecodeError, ValueError, TypeError) as exc:
                issues.append(f'line {line_number}: {exc}')
    if not sum(counts.values()):
        issues.append('no valid examples')
    return {'counts': counts, 'issues': issues}
