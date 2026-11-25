import json
from email.message import Message
from io import BytesIO
from urllib.error import HTTPError
from urllib.robotparser import RobotFileParser
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from fast_corpus.crawler import Crawler, PageParser, normalize, sitemap_urls
from fast_corpus.prepare import prepare


class PipelineTests(unittest.TestCase):
    def test_normalize_and_scope(self):
        self.assertEqual(normalize('/admissions#top', 'https://WWW.NU.EDU.PK/'), 'https://www.nu.edu.pk/admissions')
        self.assertIsNone(normalize('javascript:alert(1)'))
        crawler = Crawler(['www.nu.edu.pk'], 'ExampleBot/1.0 (contact: team@example.com)')
        self.assertFalse(crawler.allowed_host('https://www.nu.edu.pk.evil.test/'))
        self.assertFalse(crawler.allowed_host('https://www.nu.edu.pk:8443/'))

    def test_malformed_urls_are_ignored(self):
        for url in ('https://www.nu.edu.pk:bad/path', 'https://[invalid/path',
                    'https://www.nu.edu.pk:99999/path'):
            with self.subTest(url=url):
                self.assertIsNone(normalize(url))

    def test_sitemap_urlset_and_invalid_xml(self):
        xml = b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://www.nu.edu.pk/a</loc></url><url><loc>javascript:bad</loc></url></urlset>'
        self.assertEqual(list(sitemap_urls(xml, 'https://www.nu.edu.pk/')), ['https://www.nu.edu.pk/a'])
        for raw in (b'<broken', b'<!DOCTYPE x><urlset/>'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                list(sitemap_urls(raw, 'https://www.nu.edu.pk/'))

    def test_sitemap_discovery_obeys_host_scope(self):
        class Response(BytesIO):
            def __init__(self, content):
                super().__init__(content)
                self.headers = Message()
                self.headers['Content-Type'] = 'text/html'
        crawler = Crawler(['www.nu.edu.pk'], 'ExampleBot/1.0 (contact: team@example.com)')
        crawler.permitted = lambda url: True
        fetched = []
        def request(url):
            fetched.append(url)
            if url.endswith('/sitemap.xml'):
                return Response(b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://www.nu.edu.pk/a</loc></url><url><loc>https://evil.test/</loc></url></urlset>')
            return Response(('<p>' + url + '</p>').encode())
        crawler.request = request
        with tempfile.TemporaryDirectory() as tmp:
            count = crawler.crawl('https://www.nu.edu.pk/', Path(tmp) / 'out.jsonl', 5, ['/sitemap.xml'])
        self.assertEqual(count, 2)
        self.assertEqual(fetched, ['https://www.nu.edu.pk/sitemap.xml', 'https://www.nu.edu.pk/', 'https://www.nu.edu.pk/a'])

    def test_crawl_deduplicates_discovered_links(self):
        class Response(BytesIO):
            def __init__(self, content):
                super().__init__(content)
                self.headers = Message()
                self.headers['Content-Type'] = 'text/html; charset=utf-8'

        crawler = Crawler(['www.nu.edu.pk'], 'ExampleBot/1.0 (contact: team@example.com)')
        crawler.permitted = lambda url: True
        fetched = []
        def request(url):
            fetched.append(url)
            if url.endswith('/'):
                return Response(b'<p>Home</p><a href="/a">A</a><a href="/a#top">Again</a><a href="https://www.nu.edu.pk:bad/">Bad</a>')
            return Response(b'<p>Page A</p>')
        crawler.request = request
        with tempfile.TemporaryDirectory() as tmp:
            count = crawler.crawl('https://www.nu.edu.pk/', Path(tmp) / 'out.jsonl', 10)
        self.assertEqual(count, 2)
        self.assertEqual(fetched, ['https://www.nu.edu.pk/', 'https://www.nu.edu.pk/a'])

    def test_excluded_paths_never_fetched_even_via_redirect(self):
        class Response(BytesIO):
            def __init__(self, content):
                super().__init__(content)
                self.headers = Message()
                self.headers['Content-Type'] = 'text/html'
        crawler = Crawler(['www.nu.edu.pk'], 'ExampleBot/1.0 (contact: team@example.com)', excluded_paths=['/private'])
        fetched = []
        robots = RobotFileParser()
        robots.parse(['User-agent: *', 'Disallow: /blocked'])
        crawler.robots['https://www.nu.edu.pk'] = robots
        def request(url):
            fetched.append(url)
            if url.endswith('/'):
                return Response(b'<p>Home</p><a href="/private/file">Private</a><a href="/%70rivate/hidden">Encoded</a><a href="/blocked">Robots</a><a href="/redirect">Redirect</a><a href="https://evil.test/">External</a>')
            headers = Message()
            headers['Location'] = '/private/file'
            raise HTTPError(url, 302, 'redirect', headers, None)
        crawler.request = request
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(crawler.crawl('https://www.nu.edu.pk/', Path(tmp) / 'pages', 10), 1)
        self.assertEqual(fetched, ['https://www.nu.edu.pk/', 'https://www.nu.edu.pk/redirect'])

    def test_page_attempts_are_bounded_after_failures(self):
        class Response(BytesIO):
            def __init__(self, content):
                super().__init__(content)
                self.headers = Message()
                self.headers['Content-Type'] = 'text/html'
        crawler = Crawler(['www.nu.edu.pk'], 'ExampleBot/1.0 (contact: team@example.com)')
        crawler.permitted = lambda url: True
        calls = []
        def request(url):
            calls.append(url)
            if url.endswith('/'):
                return Response(b'<p>Home</p><a href="/a">A</a><a href="/b">B</a>')
            raise TimeoutError('simulated timeout')
        crawler.request = request
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(crawler.crawl('https://www.nu.edu.pk/', Path(tmp) / 'pages', 10, max_attempts=2), 1)
        self.assertEqual(len(calls), 2)

    def test_rate_limit_stops_following_requests(self):
        class Response(BytesIO):
            def __init__(self, content):
                super().__init__(content)
                self.headers = Message()
                self.headers['Content-Type'] = 'text/html'
        for code in (429, 503):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as tmp:
                crawler = Crawler(['www.nu.edu.pk'], 'ExampleBot/1.0 (contact: team@example.com)')
                crawler.permitted = lambda url: True
                calls = []
                def request(url):
                    calls.append(url)
                    if url.endswith('/'):
                        return Response(b'<p>Home</p><a href="/a">A</a><a href="/b">B</a>')
                    raise HTTPError(url, code, 'error', Message(), None)
                crawler.request = request
                crawler.crawl('https://www.nu.edu.pk/', Path(tmp) / 'pages', 10)
                self.assertEqual(len(calls), 2)

    def test_oversized_page_is_skipped(self):
        class Response(BytesIO):
            def __init__(self):
                super().__init__(b'x' * 21)
                self.headers = Message()
                self.headers['Content-Type'] = 'text/html'
        crawler = Crawler(['www.nu.edu.pk'], 'ExampleBot/1.0 (contact: team@example.com)', max_bytes=20)
        crawler.permitted = lambda url: True
        crawler.request = lambda url: Response()
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(crawler.crawl('https://www.nu.edu.pk/', Path(tmp) / 'pages', 2), 0)

    def test_request_pacing_is_per_origin(self):
        crawler = Crawler(['www.nu.edu.pk'], 'ExampleBot/1.0 (contact: team@example.com)', delay=2)
        crawler.opener.open = Mock(return_value=None)
        with patch('fast_corpus.crawler.time.monotonic', side_effect=[10, 10, 10.5, 12]), patch('fast_corpus.crawler.time.sleep') as sleep:
            crawler.request('https://www.nu.edu.pk/a')
            crawler.request('https://www.nu.edu.pk/b')
        sleep.assert_called_once_with(1.5)
        self.assertEqual(crawler.opener.open.call_count, 2)

    def test_parser_removes_navigation_and_keeps_content(self):
        parser = PageParser()
        parser.feed('<title>FAST</title><nav>Menu</nav><h1>Admissions</h1><p>Apply now</p><script>bad()</script><a href="/fees">Fees</a>')
        self.assertEqual(parser.title, ['FAST'])
        self.assertNotIn('Menu', parser.text())
        self.assertNotIn('bad()', parser.text())
        self.assertIn('Admissions', parser.text())
        self.assertEqual(parser.links, ['/fees'])

    def test_prepare_deduplicates_and_preserves_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = Path(tmp) / 'pages.jsonl', Path(tmp) / 'chunks.jsonl'
            page = {'url': 'https://www.nu.edu.pk/a', 'title': 'A', 'crawled_at': 'today', 'sha256': 'abc', 'text': 'alpha beta gamma delta epsilon'}
            src.write_text(json.dumps(page) + '\n' + json.dumps(page) + '\n', encoding='utf-8')
            pages, count = prepare(src, dst, 15, 3)
            rows = [json.loads(line) for line in dst.read_text().splitlines()]
            self.assertEqual(pages, 1)
            self.assertGreater(count, 1)
            self.assertTrue(all(row['url'] == page['url'] for row in rows))
            self.assertEqual(len({row['id'] for row in rows}), count)

    def test_invalid_chunk_options(self):
        with self.assertRaises(ValueError):
            prepare('unused', 'unused2', 10, 10)

    def test_robots_failure_is_closed(self):
        crawler = Crawler(['www.nu.edu.pk'], 'ExampleBot/1.0 (contact: team@example.com)')
        def failure(_):
            raise OSError('unavailable')
        crawler.request = failure
        self.assertFalse(crawler.permitted('https://www.nu.edu.pk/'))


if __name__ == '__main__':
    unittest.main()
