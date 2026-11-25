from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from fast_corpus.manifest import create_manifest


class ManifestTests(unittest.TestCase):
    def test_records_input_hash_and_protects_existing_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, output = Path(tmp) / 'input.jsonl', Path(tmp) / 'manifest.json'
            source.write_bytes(b'example')
            with patch('fast_corpus.manifest.git_state', return_value={'commit': 'abc', 'dirty': False}):
                record = create_manifest([source], output, ['chunk_size=1200'])
            self.assertEqual(record['inputs'][0]['sha256'], sha256(b'example').hexdigest())
            self.assertEqual(record['inputs'][0]['bytes'], 7)
            self.assertEqual(record['settings']['chunk_size'], '1200')
            self.assertEqual(json.loads(output.read_text())['git']['commit'], 'abc')
            with self.assertRaises(FileExistsError):
                create_manifest([source], output)

    def test_rejects_duplicate_settings_and_input_output_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'input'
            source.write_text('content')
            with self.assertRaises(ValueError):
                create_manifest([source], Path(tmp) / 'output', ['k=1', 'k=2'])
            with self.assertRaises(ValueError):
                create_manifest([source], source)
            self.assertEqual(source.read_text(), 'content')


if __name__ == '__main__':
    unittest.main()
