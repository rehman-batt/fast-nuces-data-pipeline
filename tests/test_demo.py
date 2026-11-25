import unittest
from fast_corpus.demo import run_demo


class DemoTests(unittest.TestCase):
    def test_offline_demo_retrieves_synthetic_admissions_source(self):
        results = run_demo()
        self.assertTrue(results)
        self.assertEqual(results[0]['chunk']['url'], 'https://example.invalid/admissions')
        self.assertIn('application', results[0]['chunk']['text'])


if __name__ == '__main__':
    unittest.main()
