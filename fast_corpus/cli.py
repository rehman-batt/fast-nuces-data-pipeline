import argparse
import logging
from .crawler import Crawler
from .prepare import prepare


def main():
    parser = argparse.ArgumentParser(description="Collect and prepare a public FAST-NUCES corpus")
    commands = parser.add_subparsers(dest="command", required=True)
    crawl = commands.add_parser("crawl", help="Crawl allowed HTML pages, respecting robots.txt")
    crawl.add_argument("--seed", default="https://www.nu.edu.pk/")
    crawl.add_argument("--host", action="append", default=[], help="Allowed hostname; repeat to add hosts")
    crawl.add_argument("--user-agent", required=True, help="Bot name and contact URL or email")
    crawl.add_argument("--exclude-path", action="append", default=[], help="Exclude a path prefix; repeat to add exclusions")
    crawl.add_argument("--sitemap", action="append", default=[], help="Optional sitemap URL; repeat to add URL sets")
    crawl.add_argument("--limit", type=int, default=30)
    crawl.add_argument("--delay", type=float, default=2.0)
    crawl.add_argument("--output", default="data/pages.jsonl")
    prep = commands.add_parser("prepare", help="Deduplicate and chunk collected pages")
    prep.add_argument("--input", default="data/pages.jsonl")
    prep.add_argument("--output", default="data/chunks.jsonl")
    prep.add_argument("--chunk-size", type=int, default=1200)
    prep.add_argument("--overlap", type=int, default=150)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        if args.command == "crawl":
            count = Crawler(args.host or ["www.nu.edu.pk"], args.user_agent, args.delay, excluded_paths=args.exclude_path).crawl(args.seed, args.output, args.limit, args.sitemap)
            print(f"Collected {count} pages to {args.output}")
        else:
            pages, chunks = prepare(args.input, args.output, args.chunk_size, args.overlap)
            print(f"Prepared {chunks} chunks from {pages} unique pages to {args.output}")
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
