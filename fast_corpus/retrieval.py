"""Small in-memory BM25 baseline for source-linked chunks."""
from collections import Counter
import json
import math
import re


def tokenize(text):
    words = re.findall(r'[^\W_]+', text.casefold(), flags=re.UNICODE)
    # A deliberately small English plural normalization, not a full stemmer.
    return [word[:-1] if len(word) > 4 and word.endswith('s') and not word.endswith(('ss', 'us', 'is')) else word for word in words]


class Retriever:
    def __init__(self, chunks):
        self.chunks = list(chunks)
        self.tokens = [Counter(tokenize(c['text'])) for c in self.chunks]
        self.lengths = [sum(counts.values()) for counts in self.tokens]
        self.avg_length = sum(self.lengths) / len(self.lengths) if self.lengths else 0
        self.df = Counter(term for counts in self.tokens for term in counts)

    def search(self, query, limit=5):
        if limit < 1:
            raise ValueError('limit must be positive')
        terms = set(tokenize(query))
        results = []
        total = len(self.chunks)
        for chunk, counts, length in zip(self.chunks, self.tokens, self.lengths):
            score = 0.0
            for term in terms:
                freq = counts.get(term, 0)
                if freq:
                    idf = math.log(1 + (total - self.df[term] + 0.5) / (self.df[term] + 0.5))
                    norm = freq + 1.5 * (0.25 + 0.75 * length / self.avg_length)
                    score += idf * freq * 2.5 / norm
            if score > 0:
                results.append({'score': score, 'chunk': chunk})
        return sorted(results, key=lambda row: (-row['score'], row['chunk']['id']))[:limit]


def load_jsonl(path):
    with open(path, encoding='utf-8') as handle:
        return [json.loads(line) for line in handle if line.strip()]


def evaluate(retriever, questions, limit=5, scope="pilot"):
    indexed_urls = {source['url'] for chunk in retriever.chunks for source in chunk.get('sources', [{'url': chunk['url']}])}
    if scope not in {'pilot', 'indexed'}:
        raise ValueError('scope must be pilot or indexed')
    results, excluded = [], []
    for case in questions:
        expected = set(case['expected_urls'])
        present = bool(expected & indexed_urls)
        if scope == 'pilot' and case['pilot_status'] != 'in_corpus':
            excluded.append(case['id'])
            continue
        if not present:
            if scope == 'pilot':
                raise ValueError(f"Expected source missing from index for {case['id']}")
            excluded.append(case['id'])
            continue
        found = retriever.search(case['question'], limit)
        urls = {source['url'] for item in found for source in item['chunk'].get('sources', [{'url': item['chunk']['url']}])}
        results.append({'id': case['id'], 'hit': bool(expected & urls), 'retrieved_urls': sorted(urls)})
    return {'scope': scope, 'eligible': len(results), 'excluded': excluded, 'hits': sum(row['hit'] for row in results), 'top_k': limit, 'results': results}
