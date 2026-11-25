import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

try:
    import pypdf  # noqa: F401
except ImportError:
    pypdf = None

from fast_corpus.pdf import extract_pdf
from fast_corpus.prepare import prepare


@unittest.skipUnless(pypdf, 'install the pdf extra to test PDF extraction')
class PdfTests(unittest.TestCase):
    def test_page_provenance_and_empty_page(self):
        fixture = Path(__file__).parent / 'fixtures' / 'sample.pdf'
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'pages.jsonl'
            count = extract_pdf(fixture, 'https://www.nu.edu.pk/sample.pdf', output)
            rows = [json.loads(line) for line in output.read_text().splitlines()]
            self.assertEqual(count, 2)
            self.assertEqual([row['page'] for row in rows], [1, 2])
            self.assertIn('Synthetic admissions information', rows[0]['text'])
            self.assertFalse(rows[0]['needs_ocr_review'])
            self.assertTrue(rows[1]['needs_ocr_review'])
            self.assertTrue(all(row['url'] == 'https://www.nu.edu.pk/sample.pdf' for row in rows))
            with self.assertRaises(FileExistsError):
                extract_pdf(fixture, 'https://www.nu.edu.pk/sample.pdf', output)

    def test_pdf_page_can_be_prepared_with_provenance(self):
        fixture = Path(__file__).parent / 'fixtures' / 'sample.pdf'
        with tempfile.TemporaryDirectory() as tmp:
            pages, chunks = Path(tmp) / 'pages.jsonl', Path(tmp) / 'chunks.jsonl'
            extract_pdf(fixture, 'https://www.nu.edu.pk/sample.pdf', pages)
            count, total = prepare(pages, chunks)
            self.assertEqual((count, total), (1, 1))
            row = json.loads(chunks.read_text())
            self.assertEqual(row['source_page'], 1)
            self.assertEqual(row['content_type'], 'application/pdf')
            self.assertIn('source_timestamp', row)
            self.assertEqual(row['timestamp_kind'], 'processed_at')

    def test_optional_ocr_is_flagged_and_excluded_from_preparation(self):
        fixture = Path(__file__).parent / 'fixtures' / 'sample.pdf'
        with tempfile.TemporaryDirectory() as tmp:
            output, chunks = Path(tmp) / 'pages', Path(tmp) / 'chunks'
            with patch('fast_corpus.pdf.shutil.which', return_value='/fake/tool'), patch('fast_corpus.pdf.subprocess.run', side_effect=[SimpleNamespace(stdout=''), SimpleNamespace(stdout='recognized text')]) as run:
                extract_pdf(fixture, 'https://www.nu.edu.pk/sample.pdf', output, ocr=True)
            rows = [json.loads(line) for line in output.read_text().splitlines()]
            self.assertEqual(rows[0]['extraction_method'], 'native')
            self.assertEqual(rows[1]['extraction_method'], 'ocr')
            self.assertTrue(rows[1]['needs_ocr_review'])
            self.assertEqual(run.call_count, 2)
            self.assertEqual(prepare(output, chunks), (1, 1))
            self.assertNotIn('recognized text', chunks.read_text())

    def test_ocr_tool_failure_does_not_leave_partial_output(self):
        fixture = Path(__file__).parent / 'fixtures' / 'sample.pdf'
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'pages'
            with patch('fast_corpus.pdf.shutil.which', return_value='/fake/tool'), patch('fast_corpus.pdf.subprocess.run', side_effect=OSError('unavailable')):
                with self.assertRaisesRegex(ValueError, 'OCR failed'):
                    extract_pdf(fixture, 'https://www.nu.edu.pk/sample.pdf', output, ocr=True)
            self.assertFalse(output.exists())

    def test_ocr_requires_tools_and_pdf_page_limit(self):
        fixture = Path(__file__).parent / 'fixtures' / 'sample.pdf'
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'pages'
            with patch('fast_corpus.pdf.shutil.which', return_value=None):
                with self.assertRaisesRegex(ValueError, 'requires pdftoppm and tesseract'):
                    extract_pdf(fixture, 'https://www.nu.edu.pk/sample.pdf', output, ocr=True)
            with self.assertRaisesRegex(ValueError, 'page limit'):
                extract_pdf(fixture, 'https://www.nu.edu.pk/sample.pdf', output, max_pages=1)
            self.assertFalse(output.exists())

    def test_rejects_invalid_pdf_and_oversized_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'invalid.pdf'
            source.write_bytes(b'not a pdf')
            with self.assertRaises(ValueError):
                extract_pdf(source, 'https://www.nu.edu.pk/test.pdf', Path(tmp) / 'out')
            with self.assertRaisesRegex(ValueError, 'size limit'):
                extract_pdf(source, 'https://www.nu.edu.pk/test.pdf', Path(tmp) / 'out', max_bytes=2)
