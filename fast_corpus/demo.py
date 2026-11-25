"""Run a fully synthetic, offline preparation and retrieval demonstration."""
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from .prepare import prepare
from .retrieval import Retriever, load_jsonl


def run_demo(query='How do I submit an application?'):
    documents = [
        ('https://example.invalid/admissions', 'Admissions', 'Applicants submit an application through the example online portal.'),
        ('https://example.invalid/library', 'Library', 'The example library offers quiet study spaces and digital books.'),
    ]
    with TemporaryDirectory() as tmp:
        pages, chunks = Path(tmp) / 'pages.jsonl', Path(tmp) / 'chunks.jsonl'
        with pages.open('w', encoding='utf-8') as out:
            for url, title, text in documents:
                record = {'url': url, 'title': title, 'text': text, 'sha256': sha256(text.encode()).hexdigest(), 'content_type': 'text/html', 'crawled_at': '2026-01-01T00:00:00+00:00'}
                out.write(json.dumps(record) + '\n')
        prepare(pages, chunks)
        return Retriever(load_jsonl(chunks)).search(query, limit=2)


def main():
    print('Synthetic offline demonstration: no FAST data or live website requests.')
    for item in run_demo():
        chunk = item['chunk']
        print(f"\nSource: {chunk['url']}\nPassage: {chunk['text']}\nScore: {item['score']:.3f}")
    print('\nThis is retrieval only; no language model generated an answer.')


if __name__ == '__main__':
    main()
