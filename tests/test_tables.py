import json
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest
from fast_corpus.prepare import prepare
from fast_corpus.tables import table_passages


def cell(text, header=False, rowspan=1, colspan=1):
    return {'text': text, 'header': header, 'rowspan': rowspan, 'colspan': colspan}


class TableChunkTests(unittest.TestCase):
    def test_headers_colspans_and_rowspans_remain_with_values(self):
        table = {'caption': 'Fees', 'rows': [
            [cell('Program', True, rowspan=2), cell('Fee', True, colspan=2)],
            [cell('Local', True), cell('International', True)],
            [cell('BS', rowspan=2), cell('100'), cell('200')],
            [cell('150'), cell('250')],
        ]}
        rows = list(table_passages([table], 500))
        self.assertEqual(len(rows), 2)
        self.assertIn('Program: BS', rows[1][2])
        self.assertIn('Fee / Local: 150', rows[1][2])
        self.assertIn('Fee / International: 250', rows[1][2])

    def test_distinct_tables_with_same_text_keep_correct_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, output = Path(tmp) / 'pages', Path(tmp) / 'chunks'
            text = 'Fees'
            base = {'title': 'Fees', 'crawled_at': '2026-11-25T10:00:00+00:00', 'content_type': 'text/html', 'sha256': sha256(text.encode()).hexdigest(), 'text': text}
            rows = []
            for url, value in [('https://www.nu.edu.pk/a', '100'), ('https://www.nu.edu.pk/b', '200')]:
                rows.append(dict(base, url=url, tables=[{'caption': '', 'rows': [[cell('Fee', True)], [cell(value)]]}]))
            source.write_text(''.join(json.dumps(row) + '\n' for row in rows))
            prepare(source, output)
            chunks = [json.loads(line) for line in output.read_text().splitlines()]
            tables = [chunk for chunk in chunks if chunk['kind'] == 'table_row']
            self.assertEqual(len(tables), 2)
            self.assertEqual(len({chunk['id'] for chunk in tables}), 2)
            self.assertEqual([chunk['sources'][0]['url'] for chunk in tables], [row['url'] for row in rows])
            self.assertTrue(all(len(chunk['sources']) == 1 for chunk in tables))

    def test_text_chunks_are_bounded_and_overlap(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, output = Path(tmp) / 'pages', Path(tmp) / 'chunks'
            text = 'abcdefghijklmnopqrstuvwxyz'
            page = {'url': 'https://www.nu.edu.pk/a', 'title': 'A', 'crawled_at': '2026-11-25T10:00:00+00:00', 'content_type': 'text/html', 'sha256': sha256(text.encode()).hexdigest(), 'text': text}
            source.write_text(json.dumps(page) + '\n')
            prepare(source, output, chunk_size=10, overlap=3)
            chunks = [json.loads(line)['text'] for line in output.read_text().splitlines()]
            self.assertTrue(all(len(chunk) <= 10 for chunk in chunks))
            self.assertEqual(chunks[0][-3:], chunks[1][:3])

    def test_table_chunks_include_provenance_and_respect_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, output = Path(tmp) / 'pages', Path(tmp) / 'chunks'
            text = 'Fees and values'
            page = {'url': 'https://www.nu.edu.pk/fees', 'title': 'Fees', 'crawled_at': '2026-11-25T10:00:00+00:00', 'content_type': 'text/html', 'sha256': sha256(text.encode()).hexdigest(), 'text': text, 'tables': [{'caption': 'Fees', 'rows': [[cell('Program', True), cell('Fee', True)], [cell('BS'), cell('100')]]}]}
            source.write_text(json.dumps(page) + '\n')
            prepare(source, output, chunk_size=100, overlap=0)
            rows = [json.loads(line) for line in output.read_text().splitlines()]
            table = next(row for row in rows if row['kind'] == 'table_row')
            self.assertIn('Program: BS', table['text'])
            self.assertIn('Fee: 100', table['text'])
            self.assertEqual(table['sources'][0]['url'], page['url'])
            self.assertTrue(all(len(row['text']) <= 100 for row in rows))
            output.write_text('previous')
            with self.assertRaisesRegex(ValueError, 'exceeds chunk size'):
                prepare(source, output, chunk_size=10, overlap=0)
            self.assertEqual(output.read_text(), 'previous')


if __name__ == '__main__':
    unittest.main()
