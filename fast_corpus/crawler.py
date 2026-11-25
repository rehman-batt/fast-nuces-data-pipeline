"""A bounded crawler that fails closed when robots policy cannot be checked."""
from collections import deque
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
import json
import logging
import posixpath
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from urllib.robotparser import RobotFileParser
from xml.etree import ElementTree

LOG = logging.getLogger(__name__)
USER_AGENT = "FASTCorpusBot/0.1 (+https://example.org/contact; replace before use)"
BLOCKED = {"script", "style", "nav", "footer", "header", "noscript", "svg"}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
BREAKS = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "tr", "section", "article"}


def normalize(url, base=None):
    try:
        parts = urlsplit(urljoin(base or url, url))
        if parts.scheme.lower() not in {"http", "https"} or not parts.hostname or parts.username or parts.password:
            return None
        host = parts.hostname.lower()
        port = parts.port
        if port and not ((parts.scheme.lower() == "https" and port == 443) or (parts.scheme.lower() == "http" and port == 80)):
            host += f":{port}"
        return urlunsplit((parts.scheme.lower(), host, parts.path or "/", parts.query, ""))
    except ValueError:
        # Invalid ports, malformed IPv6 literals, and other invalid URLs are
        # ordinary untrusted page content and must not terminate a crawl.
        return None


def sitemap_urls(raw, base):
    """Extract scoped candidates from a bounded sitemap URL set."""
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("Sitemap document types and entities are not supported")
    try:
        root = ElementTree.fromstring(raw)
    except ElementTree.ParseError as exc:
        raise ValueError("Invalid sitemap XML") from exc
    if root.tag != "{http://www.sitemaps.org/schemas/sitemap/0.9}urlset":
        raise ValueError("Only sitemap URL sets are supported")
    for node in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
        if node.text:
            url = normalize(node.text.strip(), base)
            if url:
                yield url


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.in_title = False
        self.title = []
        self.parts = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag == "title":
            self.in_title = True
        if self.skip:
            if tag not in VOID_TAGS:
                self.skip += 1
            return
        classes = set((attrs.get("class") or "").split())
        if tag in BLOCKED or "breadcrumb" in classes:
            if tag not in VOID_TAGS:
                self.skip = 1
            return
        if tag in BREAKS:
            self.parts.append("\n")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if self.skip:
            self.skip -= 1
            return
        if tag in BREAKS:
            self.parts.append("\n")

    def handle_data(self, data):
        if self.in_title:
            self.title.append(data.strip())
        elif not self.skip:
            self.parts.append(data)

    def text(self):
        lines = [re.sub(r"\s+", " ", line).strip() for line in "".join(self.parts).replace("\ufeff", "").splitlines()]
        return "\n".join(line for line in lines if line)


class TableParser(HTMLParser):
    """Preserve table rows, cells, and spans without guessing merged headers."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables = []
        self.depth = 0
        self.table = None
        self.row = None
        self.cell = None
        self.caption = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.depth += 1
            if self.depth == 1:
                self.table = {"caption": "", "rows": []}
            return
        if self.depth != 1:
            return
        attrs = dict(attrs)
        if tag == "caption":
            self.caption = []
        elif tag == "tr":
            self.row = []
        elif tag in {"td", "th"} and self.row is not None:
            def span(name):
                try:
                    value = int(attrs.get(name) or 1)
                    return value if 1 <= value <= 100 else 1
                except ValueError:
                    return 1
            self.cell = {"header": tag == "th", "rowspan": span("rowspan"), "colspan": span("colspan"), "parts": []}
        elif tag == "br" and self.cell is not None:
            self.cell["parts"].append(" ")

    def handle_data(self, data):
        if self.depth != 1:
            return
        if self.cell is not None:
            self.cell["parts"].append(data)
        elif self.caption is not None:
            self.caption.append(data)

    def handle_endtag(self, tag):
        if tag == "table":
            if self.depth == 1 and self.table is not None:
                if self.table["rows"]:
                    self.tables.append(self.table)
                self.table = None
            if self.depth:
                self.depth -= 1
            return
        if self.depth != 1:
            return
        if tag in {"td", "th"} and self.cell is not None and self.row is not None:
            parts = self.cell.pop("parts")
            self.cell["text"] = re.sub(r"\s+", " ", "".join(parts)).strip()
            self.row.append(self.cell)
            self.cell = None
        elif tag == "tr" and self.row is not None:
            if self.row:
                self.table["rows"].append(self.row)
            self.row = None
        elif tag == "caption" and self.caption is not None:
            self.table["caption"] = re.sub(r"\s+", " ", "".join(self.caption)).strip()
            self.caption = None


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Crawler:
    def __init__(self, hosts, user_agent, delay=2.0, timeout=20, max_bytes=2_000_000, excluded_paths=(), allow_missing_robots=False):
        if not user_agent.strip() or "example.org/contact" in user_agent:
            raise ValueError("Provide a descriptive user agent with your contact information")
        if delay < 1:
            raise ValueError("Delay must be at least 1 second")
        self.hosts = {h.lower() for h in hosts}
        if any(not path.startswith('/') or '?' in path or '#' in path for path in excluded_paths):
            raise ValueError("Excluded paths must begin with / and omit query and fragment")
        self.excluded_paths = tuple(excluded_paths)
        self.allow_missing_robots = allow_missing_robots
        self.ua, self.delay, self.timeout, self.max_bytes = user_agent, delay, timeout, max_bytes
        self.opener = build_opener(NoRedirect())
        self.robots = {}
        self.last_request = {}

    def allowed_host(self, url):
        parts = urlsplit(url)
        return parts.hostname in self.hosts and parts.port in (None, 80, 443)

    def in_scope(self, url):
        if not self.allowed_host(url):
            return False
        path = posixpath.normpath(unquote(urlsplit(url).path or '/'))
        return not any(path.startswith(prefix) for prefix in self.excluded_paths)

    def request(self, url):
        origin = (urlsplit(url).scheme, urlsplit(url).netloc)
        wait = self.delay - (time.monotonic() - self.last_request.get(origin, 0))
        if wait > 0:
            time.sleep(wait)
        self.last_request[origin] = time.monotonic()
        return self.opener.open(Request(url, headers={"User-Agent": self.ua, "Accept": "text/html,application/xhtml+xml"}), timeout=self.timeout)

    def permitted(self, url):
        parts = urlsplit(url)
        origin = f"{parts.scheme}://{parts.netloc}"
        if origin not in self.robots:
            parser = RobotFileParser()
            robots_url = origin + "/robots.txt"
            try:
                with self.request(robots_url) as response:
                    raw = response.read(self.max_bytes + 1)
                    if len(raw) > self.max_bytes:
                        raise ValueError("robots.txt exceeds size limit")
                    parser.parse(raw.decode("utf-8", "replace").splitlines())
                self.robots[origin] = parser
            except HTTPError as exc:
                if exc.code == 404 and self.allow_missing_robots:
                    LOG.warning("robots.txt returned 404; explicit missing-file policy enabled for %s", origin)
                    parser.parse([])
                    self.robots[origin] = parser
                else:
                    LOG.warning("Cannot verify %s (%s); skipping host", robots_url, exc)
                    self.robots[origin] = None
            except (URLError, TimeoutError, OSError, ValueError) as exc:
                LOG.warning("Cannot verify %s (%s); skipping host", robots_url, exc)
                self.robots[origin] = None
        parser = self.robots[origin]
        return parser is not None and parser.can_fetch(self.ua, url)

    def crawl(self, seed, output, limit, sitemaps=(), max_attempts=100, max_queued=1000):
        """Write a new pages file and companion log without overwriting runs."""
        if not normalize(seed) or not self.in_scope(normalize(seed)):
            raise ValueError("Seed must be an HTTP(S) URL on an allowed host")
        if limit < 1 or max_attempts < 1 or max_queued < 1:
            raise ValueError("Page, attempt and queue limits must be positive")
        output = Path(output)
        log_path = Path(str(output) + ".log")
        output.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation protects prior runs; create both files before requests.
        with output.open("x", encoding="utf-8") as out:
            try:
                handler = logging.FileHandler(log_path, mode="x", encoding="utf-8")
            except Exception:
                # The empty file was just created by this run.
                output.unlink()
                raise
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
            previous_level = LOG.level
            LOG.setLevel(logging.INFO)
            LOG.addHandler(handler)
            try:
                count = self._crawl(seed, out, limit, sitemaps, max_attempts, max_queued)
                LOG.info("Run finished: collected %s pages", count)
                return count
            finally:
                LOG.removeHandler(handler)
                LOG.setLevel(previous_level)
                handler.close()

    def _crawl(self, seed, out, limit, sitemaps=(), max_attempts=100, max_queued=1000):
        seed = normalize(seed)
        if not seed or not self.in_scope(seed):
            raise ValueError("Seed must be an HTTP(S) URL on an allowed host")
        if limit < 1:
            raise ValueError("Page limit must be positive")
        if max_attempts < 1 or max_queued < 1:
            raise ValueError("Attempt and queue limits must be positive")
        queue, seen, queued, count, attempts = deque([seed]), set(), {seed}, 0, 0
        for sitemap in sitemaps:
            sitemap = normalize(sitemap, seed)
            if not sitemap or not self.in_scope(sitemap) or not self.permitted(sitemap):
                LOG.warning("Sitemap skipped by scope or robots: %s", sitemap)
                continue
            try:
                with self.request(sitemap) as response:
                    raw = response.read(self.max_bytes + 1)
                    if len(raw) > self.max_bytes:
                        raise ValueError("Sitemap exceeds size limit")
                for target in sitemap_urls(raw, sitemap):
                    if self.in_scope(target) and target not in queued and len(queue) < max_queued:
                        queue.append(target)
                        queued.add(target)
            except HTTPError as exc:
                if exc.code == 429 or 500 <= exc.code <= 599:
                    raise ValueError(f"Sitemap request returned HTTP {exc.code}; stopping") from exc
                LOG.warning("Sitemap unavailable: %s: %s", sitemap, exc)
            except (URLError, TimeoutError, OSError, ValueError) as exc:
                LOG.warning("Sitemap unavailable: %s: %s", sitemap, exc)
        while queue and count < limit and attempts < max_attempts:
            url = queue.popleft()
            queued.discard(url)
            if url in seen:
                continue
            seen.add(url)
            if not self.in_scope(url) or not self.permitted(url):
                LOG.info("Skipped by scope or robots: %s", url)
                continue
            attempts += 1
            try:
                with self.request(url) as response:
                    kind = response.headers.get_content_type()
                    if kind not in {"text/html", "application/xhtml+xml"}:
                        LOG.info("Skipped content type %s: %s", kind, url)
                        continue
                    raw = response.read(self.max_bytes + 1)
                    if len(raw) > self.max_bytes:
                        LOG.warning("Page too large: %s", url)
                        continue
                    charset = response.headers.get_content_charset() or "utf-8"
                    try:
                        html = raw.decode(charset, "replace")
                    except LookupError:
                        html = raw.decode("utf-8", "replace")
            except HTTPError as exc:
                if exc.code in (301, 302, 303, 307, 308) and exc.headers.get("Location"):
                    target = normalize(exc.headers["Location"], url)
                    if target and self.in_scope(target) and target not in seen and target not in queued and len(queue) < max_queued:
                        queue.appendleft(target)
                        queued.add(target)
                else:
                    LOG.warning("HTTP %s: %s", exc.code, url)
                    if exc.code == 429 or 500 <= exc.code <= 599:
                        LOG.warning("Stopping after server error or rate limit")
                        break
                continue
            except (URLError, TimeoutError, OSError) as exc:
                LOG.warning("Fetch failed: %s: %s", url, exc)
                continue
            parser = PageParser()
            parser.feed(html)
            table_parser = TableParser()
            table_parser.feed(html)
            text = parser.text()
            for link in parser.links:
                target = normalize(link, url)
                if target and self.in_scope(target) and target not in seen and target not in queued and len(queue) < max_queued:
                    queue.append(target)
                    queued.add(target)
            if not text:
                LOG.info("Skipped empty page: %s", url)
                continue
            record = {"url": url, "title": " ".join(parser.title), "crawled_at": datetime.now(timezone.utc).isoformat(), "content_type": kind, "sha256": sha256(text.encode()).hexdigest(), "text": text, "tables": table_parser.tables}
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
            LOG.info("Collected %s (%s/%s)", url, count, limit)
        return count
