import json
from pathlib import Path
import unittest
from urllib.parse import urlsplit


class EvaluationSetTests(unittest.TestCase):
    def test_question_records_are_well_formed_and_unique(self):
        path = Path(__file__).resolve().parent.parent / 'evaluation' / 'questions.jsonl'
        rows = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
        self.assertGreaterEqual(len(rows), 10)
        self.assertEqual(len({row['id'] for row in rows}), len(rows))
        self.assertEqual(len({row['question'] for row in rows}), len(rows))
        self.assertEqual({row['audience'] for row in rows}, {'prospective', 'current'})
        for row in rows:
            with self.subTest(id=row['id']):
                self.assertTrue(row['question'].strip())
                self.assertTrue(row['evidence_goal'].strip())
                self.assertIn(row['pilot_status'], {'in_corpus', 'not_in_corpus'})
                self.assertTrue(row['expected_urls'])
                for url in row['expected_urls']:
                    self.assertEqual(urlsplit(url).scheme, 'https')
                    self.assertEqual(urlsplit(url).hostname, 'www.nu.edu.pk')


if __name__ == '__main__':
    unittest.main()
