import json
from pathlib import Path
import tempfile
import unittest
from fast_corpus.training import validate_training


class TrainingValidationTests(unittest.TestCase):
    def setUp(self):
        self.row = {'question': 'What is the example?', 'answer': 'An example.', 'evidence': 'Example evidence.', 'source_url': 'https://example.test/source', 'source_date': '2026-11-25', 'split': 'train'}

    def validate(self, rows, evaluation=None):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'data.jsonl'
            path.write_text(''.join(json.dumps(row) + '\n' for row in rows))
            return validate_training(path, evaluation)

    def test_valid_record_and_split_leakage(self):
        self.assertEqual(self.validate([self.row])['issues'], [])
        second = dict(self.row, question='Different question', split='validation')
        self.assertTrue(any('multiple splits' in issue for issue in self.validate([self.row, second])['issues']))

    def test_duplicate_and_evaluation_overlap_are_reported(self):
        evaluation = [{'question': self.row['question'], 'expected_urls': [self.row['source_url']]}]
        issues = self.validate([self.row, self.row], evaluation)['issues']
        self.assertTrue(any('duplicate question' in issue for issue in issues))
        self.assertTrue(any('question overlaps' in issue for issue in issues))
        self.assertTrue(any('source overlaps' in issue for issue in issues))

    def test_missing_fields_and_invalid_dates_are_reported(self):
        issues = self.validate([{}, dict(self.row, source_date='not-a-date')])['issues']
        self.assertTrue(any('question' in issue for issue in issues))
        self.assertTrue(any('source_date' in issue for issue in issues))


if __name__ == '__main__':
    unittest.main()
