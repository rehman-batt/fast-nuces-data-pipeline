from email.message import Message
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest

from fast_corpus.crawler import Crawler


class Response(BytesIO):
    def __init__(self, data, kind=None):
        super().__init__(data)
        self.headers = Message()
        if kind: self.headers['Content-Type'] = kind


class RawCollectionTests(unittest.TestCase):
    def test_html_and_pdf_saved_exactly_with_provenance_and_deduplication(self):
        with tempfile.TemporaryDirectory() as tmp:
            html = b'<p>Home</p><iframe src="/a.pdf"></iframe><a href="/b.pdf">same</a>'
            pdf = b'%PDF-1.7 test'
            crawler = Crawler(['example.test'], 'TestBot/1.0 (contact: test@example.test)', assets_dir=Path(tmp)/'assets')
            crawler.permitted = lambda url: True
            crawler.request = lambda url: Response(html, 'text/html') if url.endswith('/') else Response(pdf, 'application/pdf')
            output = Path(tmp)/'pages'
            self.assertEqual(crawler.crawl('https://example.test/', output, 10), 1)
            events = [json.loads(x) for x in Path(str(output)+'.inventory.jsonl').read_text().splitlines()]
            assets = [x for x in events if x['event'] == 'asset_saved']
            self.assertEqual(len(assets), 3)
            self.assertEqual(len(list((Path(tmp)/'assets').iterdir())), 2)
            self.assertEqual((Path(tmp)/'assets'/sha256(pdf).hexdigest()).read_bytes(), pdf)
            self.assertEqual([a['signature'] for a in assets[1:]], ['pdf', 'pdf'])
            self.assertEqual({a['url'] for a in assets[1:]}, {'https://example.test/a.pdf', 'https://example.test/b.pdf'})

    def test_unknown_saved_and_oversized_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            crawler = Crawler(['example.test'], 'TestBot/1.0 (contact: test@example.test)', assets_dir=Path(tmp)/'assets', max_asset_bytes=4)
            crawler.permitted = lambda url: True
            crawler.request = lambda url: Response(b'12345')
            output = Path(tmp)/'pages'
            crawler.crawl('https://example.test/', output, 1)
            events = [json.loads(x) for x in Path(str(output)+'.inventory.jsonl').read_text().splitlines()]
            self.assertTrue(any(e['event']=='skipped' and e['reason']=='size_limit' for e in events))
            self.assertFalse((Path(tmp)/'assets').exists())
            crawler.request = lambda url: Response(b'1234')
            output = Path(tmp)/'pages2'
            crawler.crawl('https://example.test/', output, 1)
            events = [json.loads(x) for x in Path(str(output)+'.inventory.jsonl').read_text().splitlines()]
            asset = next(e for e in events if e['event']=='asset_saved')
            self.assertIsNone(asset['content_type'])
            self.assertEqual(asset['signature'], 'unknown')

    def test_existing_corrupt_asset_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = b'%PDF-1.7 test'
            assets = Path(tmp)/'assets'; assets.mkdir()
            destination = assets/sha256(data).hexdigest(); destination.write_bytes(b'corrupt')
            crawler = Crawler(['example.test'], 'TestBot/1.0 (contact: test@example.test)', assets_dir=assets)
            with self.assertRaises(ValueError): crawler.save_asset('https://example.test/a', data, 'application/pdf')
            self.assertEqual(destination.read_bytes(), b'corrupt')
