import unittest
from fast_corpus.retrieval import Retriever, evaluate


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.chunks = [
            {'id': 'a', 'url': 'https://example.test/fees', 'text': 'tuition fee for computing', 'sources': [{'url': 'https://example.test/fees'}]},
            {'id': 'b', 'url': 'https://example.test/apply', 'text': 'submit admission application online', 'sources': [{'url': 'https://example.test/apply'}]},
        ]

    def test_search_ranks_matching_source_and_excludes_no_match(self):
        search = Retriever(self.chunks)
        self.assertEqual(search.search('application online')[0]['chunk']['id'], 'b')
        self.assertEqual(search.search('unrelatedxyz'), [])

    def test_singular_query_matches_plural_document(self):
        search = Retriever([{'id': 'c', 'url': 'https://example.test/test', 'text': 'calculators are prohibited'}])
        self.assertEqual(search.search('calculator')[0]['chunk']['id'], 'c')

    def test_evaluation_counts_only_indexed_cases(self):
        cases = [
            {'id': '1', 'question': 'tuition fee', 'expected_urls': ['https://example.test/fees'], 'pilot_status': 'in_corpus'},
            {'id': '2', 'question': 'missing', 'expected_urls': ['https://example.test/missing'], 'pilot_status': 'not_in_corpus'},
        ]
        result = evaluate(Retriever(self.chunks), cases, 1)
        self.assertEqual((result['hits'], result['eligible']), (1, 1))
        cases[1]['pilot_status'] = 'in_corpus'
        with self.assertRaisesRegex(ValueError, 'missing from index'):
            evaluate(Retriever(self.chunks), cases, 1)


if __name__ == '__main__':
    unittest.main()
