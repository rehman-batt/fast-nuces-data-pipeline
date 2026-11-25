import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from fast_corpus.pdf import extract_pdf
from fast_corpus.prepare import prepare


@unittest.skipUnless(importlib.util.find_spec('pypdf') and shutil.which('pdftoppm') and shutil.which('tesseract'), 'requires pypdf, pdftoppm and tesseract')
class OcrIntegrationTests(unittest.TestCase):
    def test_real_engine_reads_synthetic_scan_and_keeps_it_unreviewed(self):
        fixture = Path(__file__).parent / 'fixtures' / 'scanned-synthetic.pdf'
        with tempfile.TemporaryDirectory() as tmp:
            output, chunks = Path(tmp) / 'pages.jsonl', Path(tmp) / 'chunks.jsonl'
            self.assertEqual(extract_pdf(fixture, 'https://example.invalid/synthetic.pdf', output, ocr=True), 1)
            record = json.loads(output.read_text())
            self.assertEqual(record['extraction_method'], 'ocr')
            self.assertTrue(record['needs_ocr_review'])
            self.assertIn('OCR', record['text'].upper())
            self.assertEqual(prepare(output, chunks), (0, 0))
            self.assertEqual(chunks.read_text(), '')


if __name__ == '__main__':
    unittest.main()
