import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from fast_corpus.store import build_store, search_store, store_info


def chunk(identifier, url, text):
    source = {'url': url, 'title': 'Example', 'source_timestamp': '2026-11-25T00:00:00+00:00', 'timestamp_kind': 'crawled_at', 'source_page': None, 'content_type': 'text/html'}
    return {'id': identifier, **source, 'sources': [source], 'text': text, 'kind': 'text'}


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / 'chunks.jsonl'
        self.store = self.root / 'store.sqlite'
        self.rows = [chunk('a', 'https://example.test/apply', 'Submit an application online.'), chunk('b', 'https://example.test/test', 'Calculators are not allowed.')]
        self.write_rows(self.rows)

    def tearDown(self):
        self.tmp.cleanup()

    def write_rows(self, rows):
        self.source.write_text(''.join(json.dumps(row) + '\n' for row in rows), encoding='utf-8')

    def test_persistent_search_and_snapshot_metadata(self):
        info = build_store(self.source, self.store)
        self.assertEqual(info['chunk_count'], '2')
        self.assertEqual(info['input_sha256'], hashlib.sha256(self.source.read_bytes()).hexdigest())
        self.assertEqual(store_info(self.store), info)
        result = search_store(self.store, 'calculator', 1)
        self.assertEqual(result[0]['chunk']['id'], 'b')
        self.assertEqual(result[0]['chunk']['sources'][0]['url'], 'https://example.test/test')
        self.assertEqual(search_store(self.store, '" OR :', 5), [])

    def test_bad_input_never_replaces_existing_store(self):
        build_store(self.source, self.store)
        before = self.store.read_bytes()
        for rows in ([self.rows[0], self.rows[0]], [dict(self.rows[0], sources=[])], [dict(self.rows[0], source_timestamp='2020-01-01T00:00:00+00:00')], [dict(self.rows[0], needs_ocr_review=True)], [dict(self.rows[0], kind='table_row')], [dict(self.rows[0], sources=[dict(self.rows[0]['sources'][0], needs_ocr_review=True)])]):
            with self.subTest(rows=rows):
                self.write_rows(rows)
                with self.assertRaises(ValueError):
                    build_store(self.source, self.store, replace=True)
                self.assertEqual(self.store.read_bytes(), before)
                self.assertEqual(search_store(self.store, 'application')[0]['chunk']['id'], 'a')

    def test_rebuild_requires_explicit_replace(self):
        build_store(self.source, self.store)
        before = self.store.read_bytes()
        self.write_rows([self.rows[1]])
        with self.assertRaisesRegex(ValueError, 'already exists'):
            build_store(self.source, self.store)
        self.assertEqual(self.store.read_bytes(), before)
        self.assertEqual(build_store(self.source, self.store, replace=True)['chunk_count'], '1')
        self.assertEqual(search_store(self.store, 'calculator')[0]['chunk']['id'], 'b')

    def test_invalid_and_empty_input_or_missing_store(self):
        self.source.write_text('{invalid json}\n')
        with self.assertRaisesRegex(ValueError, 'line 1'):
            build_store(self.source, self.store)
        self.source.write_text('')
        with self.assertRaisesRegex(ValueError, 'no chunks'):
            build_store(self.source, self.store)
        with self.assertRaisesRegex(ValueError, 'does not exist'):
            search_store(self.store, 'application')
        with self.assertRaisesRegex(ValueError, 'does not exist'):
            search_store(self.store, '')
        self.assertFalse(self.store.exists())


if __name__ == '__main__':
    unittest.main()
