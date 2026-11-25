from email.message import Message
from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest

from fast_corpus.crawler import Crawler
from fast_corpus.inventory import resume_frontier


class Response(BytesIO):
    def __init__(self, data):
        super().__init__(data)
        self.headers = Message(); self.headers['Content-Type'] = 'text/html'


class ResumeTests(unittest.TestCase):
    def test_frontier_carries_over_queue_limits_and_avoids_attempts(self):
        with tempfile.TemporaryDirectory() as tmp:
            crawler = Crawler(['example.test'], 'TestBot/1.0 (contact: test@example.test)')
            crawler.permitted = lambda url: True
            fetched = []
            def request(url):
                fetched.append(url)
                return Response(b'<p>home</p><a href="/a">a</a><a href="/b">b</a><a href="/c">c</a>')
            crawler.request = request
            first = Path(tmp)/'first'
            crawler.crawl('https://example.test/', first, 1, max_queued=1)
            first_inventory = Path(str(first)+'.inventory.jsonl')
            candidates, seen = resume_frontier([first_inventory])
            self.assertEqual(candidates, ['https://example.test/a', 'https://example.test/b', 'https://example.test/c'])
            second = Path(tmp)/'second'
            crawler.crawl('https://example.test/', second, 1, max_queued=1, initial_urls=candidates, previously_attempted=seen)
            second_inventory = Path(str(second)+'.inventory.jsonl')
            pending, seen = resume_frontier([first_inventory, second_inventory])
            self.assertEqual(pending, ['https://example.test/b', 'https://example.test/c'])
            self.assertEqual(fetched, ['https://example.test/', 'https://example.test/a'])

    def test_invalid_inventory_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'bad'; path.write_text('{bad json}\n')
            with self.assertRaisesRegex(ValueError, 'line 1'): resume_frontier([path])
