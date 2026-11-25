import json
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest
from fast_corpus.training import validate_training


class TrainingValidationTests(unittest.TestCase):
    def setUp(self):
        self.row = {'question': 'What is the example?', 'answer': 'An example.', 'evidence': 'Example evidence.', 'source_url': 'https://example.test/source', 'source_date': '2026-11-25', 'split': 'train'}

    def validate(self, rows, evaluation=None, sources=None):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'data.jsonl'
            path.write_text(''.join(json.dumps(row) + '\n' for row in rows))
            return validate_training(path, evaluation, sources)

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

    def test_evidence_is_checked_against_validated_snapshot(self):
        text = 'Example evidence. More information.'
        page = {'url': self.row['source_url'], 'title': 'Example', 'crawled_at': '2026-11-25T10:00:00+00:00', 'content_type': 'text/html', 'sha256': sha256(text.encode()).hexdigest(), 'text': text}
        self.assertEqual(self.validate([self.row], sources=[page])['issues'], [])
        altered = dict(self.row, evidence='not in the source')
        self.assertTrue(any('evidence not found' in issue for issue in self.validate([altered], sources=[page])['issues']))
        self.assertTrue(any('evidence not found' in issue for issue in self.validate([self.row], sources=[])['issues']))

    def test_missing_fields_and_invalid_dates_are_reported(self):
        issues = self.validate([{}, dict(self.row, source_date='not-a-date')])['issues']
        self.assertTrue(any('question' in issue for issue in issues))
        self.assertTrue(any('source_date' in issue for issue in issues))


if __name__ == '__main__':
    unittest.main()
