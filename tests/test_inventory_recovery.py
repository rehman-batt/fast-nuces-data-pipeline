import json
from pathlib import Path
import tempfile
import unittest

from fast_corpus.inventory import import_pages, report


class RecoveryTests(unittest.TestCase):
    def test_import_is_idempotent_and_retains_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'pages'; output = Path(tmp) / 'events'
            source.write_text(json.dumps({'url':'https://example.test/a', 'crawled_at':'2026-01-01T00:00:00+00:00', 'content_type':'text/html', 'sha256':'abc'}) + '\n')
            self.assertEqual(import_pages(source, output), 1)
            self.assertEqual(import_pages(source, output), 1)
            row = json.loads(output.read_text())
            self.assertEqual(row['origin'], 'historical_import')
            self.assertEqual(row['source_line'], 1)
            summary = report([output])
            self.assertEqual(summary['unique_collected_urls'], 1)
            self.assertEqual(summary['historical_collected_events'], 1)
            self.assertEqual(summary['unique_discovered_urls'], 0)
            self.assertEqual(summary['observed_url_content_types'], {'text/html': 1})
            source.write_text(source.read_text().replace('/a', '/b'))
            with self.assertRaises(FileExistsError): import_pages(source, output)
            self.assertEqual(json.loads(output.read_text()), row)

    def test_invalid_input_does_not_create_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'pages'; output = Path(tmp) / 'events'
            source.write_text('{"url": "https://example.test/"}\n')
            with self.assertRaisesRegex(ValueError, 'line 1'): import_pages(source, output)
            self.assertFalse(output.exists())

    def test_report_deduplicates_urls_and_includes_unknown_types(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / 'events'
            rows = [{'event':'response', 'url':'https://example.test/', 'content_type':None}, {'event':'response', 'url':'https://example.test/', 'content_type':None}]
            f.write_text(''.join(json.dumps(r)+'\n' for r in rows))
            self.assertEqual(report([f])['observed_url_content_types'], {'unknown': 1})
