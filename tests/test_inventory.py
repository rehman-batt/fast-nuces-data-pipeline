import json
from email.message import Message
from io import BytesIO
from pathlib import Path
import tempfile
import unittest
from urllib.error import HTTPError

from fast_corpus.crawler import Crawler, PageParser


class Response(BytesIO):
    def __init__(self, body=b'', kind=None):
        super().__init__(body)
        self.headers = Message()
        if kind:
            self.headers['Content-Type'] = kind


class InventoryTests(unittest.TestCase):
    def test_discovery_types_failures_and_unattempted(self):
        crawler = Crawler(['example.test'], 'TestBot/1.0 (contact: test@example.test)')
        crawler.permitted = lambda url: True
        def request(url):
            if url.endswith('/'):
                return Response(b'<p>home</p><a href="/doc">doc</a><a href="/unknown">unknown</a><a href="/bad">bad</a><a href="/later">later</a><a href="https://outside.test/">outside</a>', 'text/html')
            if url.endswith('/doc'):
                return Response(b'%PDF', 'application/pdf')
            if url.endswith('/unknown'):
                return Response(b'unknown')
            raise HTTPError(url, 404, 'missing', Message(), None)
        crawler.request = request
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'pages.jsonl'
            self.assertEqual(crawler.crawl('https://example.test/', output, 10, max_attempts=4), 1)
            rows = [json.loads(line) for line in Path(str(output) + '.inventory.jsonl').read_text().splitlines()]
        self.assertTrue(any(r['event'] == 'collected' and r['url'].endswith('/') for r in rows))
        self.assertTrue(any(r['event'] == 'response' and r['content_type'] == 'application/pdf' for r in rows))
        self.assertTrue(any(r['event'] == 'skipped' and r['reason'] == 'unknown_content_type' for r in rows))
        self.assertTrue(any(r['event'] == 'http_error' and r['http_status'] == 404 for r in rows))
        self.assertTrue(any(r['event'] == 'not_attempted' and r['reason'] == 'attempt_limit' for r in rows))
        self.assertTrue(any(r['event'] == 'skipped' and r['reason'] == 'out_of_scope' for r in rows))

    def test_embedded_document_references_are_discovered(self):
        parser = PageParser()
        parser.feed('<iframe src="/one.pdf"></iframe><embed src="/two.pdf"><object data="/three.pdf"></object>')
        self.assertEqual(parser.links, ["/one.pdf", "/two.pdf", "/three.pdf"])

    def test_existing_inventory_is_not_overwritten(self):
        crawler = Crawler(['example.test'], 'TestBot/1.0 (contact: test@example.test)')
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'pages'
            inventory = Path(str(output) + '.inventory.jsonl')
            inventory.write_text('previous')
            with self.assertRaises(FileExistsError):
                crawler.crawl('https://example.test/', output, 1)
            self.assertEqual(inventory.read_text(), 'previous')
            self.assertFalse(output.exists())
            self.assertFalse(Path(str(output) + '.log').exists())
