import argparse
import logging
from .crawler import Crawler
from .prepare import prepare
from .pdf import extract_pdf
from .retrieval import Retriever, evaluate, load_jsonl
from .training import validate_training
from .manifest import create_manifest
import json


def main():
    parser = argparse.ArgumentParser(description="Collect and prepare a public FAST-NUCES corpus")
    commands = parser.add_subparsers(dest="command", required=True)
    crawl = commands.add_parser("crawl", help="Crawl allowed HTML pages, respecting robots.txt")
    crawl.add_argument("--seed", default="https://www.nu.edu.pk/")
    crawl.add_argument("--host", action="append", default=[], help="Allowed hostname; repeat to add hosts")
    crawl.add_argument("--user-agent", required=True, help="Bot name and contact URL or email")
    crawl.add_argument("--allow-missing-robots", action="store_true", help="Allow a host only when robots.txt specifically returns HTTP 404")
    crawl.add_argument("--exclude-path", action="append", default=[], help="Exclude a path prefix; repeat to add exclusions")
    crawl.add_argument("--sitemap", action="append", default=[], help="Optional sitemap URL; repeat to add URL sets")
    crawl.add_argument("--limit", type=int, default=30)
    crawl.add_argument("--max-attempts", type=int, default=100, help="Maximum page fetch attempts")
    crawl.add_argument("--max-queued", type=int, default=1000, help="Maximum queued page URLs")
    crawl.add_argument("--delay", type=float, default=2.0)
    crawl.add_argument("--output", default="data/pages.jsonl")
    prep = commands.add_parser("prepare", help="Deduplicate and chunk collected pages")
    prep.add_argument("--input", default="data/pages.jsonl")
    prep.add_argument("--output", default="data/chunks.jsonl")
    prep.add_argument("--chunk-size", type=int, default=1200)
    prep.add_argument("--overlap", type=int, default=150)
    pdf = commands.add_parser("extract-pdf", help="Extract an authorized local PDF into page records")
    pdf.add_argument("--input", required=True)
    pdf.add_argument("--source-url", required=True)
    pdf.add_argument("--output", required=True)
    pdf.add_argument("--max-bytes", type=int, default=10_000_000, help="Maximum input PDF bytes")
    pdf.add_argument("--max-pages", type=int, default=100, help="Maximum PDF pages")
    pdf.add_argument("--ocr", action="store_true", help="OCR pages with no native text; requires pdftoppm and tesseract")
    search = commands.add_parser("search", help="Search prepared chunks with BM25")
    search.add_argument("--input", default="data/chunks.jsonl")
    search.add_argument("--query", required=True)
    search.add_argument("--limit", type=int, default=5)
    evaluation = commands.add_parser("evaluate", help="Measure source retrieval on development questions")
    evaluation.add_argument("--input", default="data/chunks.jsonl")
    evaluation.add_argument("--questions", default="evaluation/questions.jsonl")
    evaluation.add_argument("--scope", choices=("pilot", "indexed"), default="pilot", help="Score original pilot cases or all cases with indexed sources")
    evaluation.add_argument("--limit", type=int, default=5)
    validation = commands.add_parser("validate-training", help="Validate model-neutral training examples")
    validation.add_argument("--input", required=True)
    validation.add_argument("--source-pages", help="Optional JSONL snapshot used to verify exact evidence text")
    validation.add_argument("--evaluation", default="evaluation/questions.jsonl")
    manifest = commands.add_parser("manifest", help="Record hashes and environment for a local run")
    manifest.add_argument("--input", action="append", required=True, help="Input file; repeat for multiple files")
    manifest.add_argument("--output", required=True)
    manifest.add_argument("--setting", action="append", default=[], help="Non-secret key=value run setting; repeat as needed")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        if args.command == "crawl":
            count = Crawler(args.host or ["www.nu.edu.pk"], args.user_agent, args.delay, excluded_paths=args.exclude_path, allow_missing_robots=args.allow_missing_robots).crawl(args.seed, args.output, args.limit, args.sitemap, args.max_attempts, args.max_queued)
            print(f"Collected {count} pages to {args.output}")
        elif args.command == "manifest":
            create_manifest(args.input, args.output, args.setting)
            print(f"Wrote run manifest to {args.output}")
        elif args.command == "validate-training":
            result = validate_training(args.input, load_jsonl(args.evaluation), load_jsonl(args.source_pages) if args.source_pages else None)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            if result['issues']:
                parser.exit(1)
        elif args.command == "search":
            print(json.dumps(Retriever(load_jsonl(args.input)).search(args.query, args.limit), ensure_ascii=False, indent=2))
        elif args.command == "evaluate":
            print(json.dumps(evaluate(Retriever(load_jsonl(args.input)), load_jsonl(args.questions), args.limit, args.scope), ensure_ascii=False, indent=2))
        elif args.command == "extract-pdf":
            pages = extract_pdf(args.input, args.source_url, args.output, max_bytes=args.max_bytes, ocr=args.ocr, max_pages=args.max_pages)
            print(f"Extracted {pages} PDF pages to {args.output}")
        else:
            pages, chunks = prepare(args.input, args.output, args.chunk_size, args.overlap)
            print(f"Prepared {chunks} chunks from {pages} unique pages to {args.output}")
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
