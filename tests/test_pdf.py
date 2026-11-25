import json
from pathlib import Path
import tempfile
import unittest

try:
    import pypdf  # noqa: F401
except ImportError:
    pypdf = None

from fast_corpus.pdf import extract_pdf


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

    def test_rejects_invalid_pdf_and_oversized_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'invalid.pdf'
            source.write_bytes(b'not a pdf')
            with self.assertRaises(ValueError):
                extract_pdf(source, 'https://www.nu.edu.pk/test.pdf', Path(tmp) / 'out')
            with self.assertRaisesRegex(ValueError, 'size limit'):
                extract_pdf(source, 'https://www.nu.edu.pk/test.pdf', Path(tmp) / 'out', max_bytes=2)
