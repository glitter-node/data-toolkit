import csv
import io
import json
import unittest
from types import SimpleNamespace
from app.services.operations import validate_data
from app.services.validation import report_bytes
from app.services.engine import DataError

SETTINGS = SimpleNamespace(max_rows=1000, max_columns=100)

class ValidationV018Tests(unittest.TestCase):
    def test_schema_and_details(self):
        schema = {'fields': {'id': {'type': 'integer', 'required': True, 'unique': True}, 'email': {'type': 'email', 'required': True}}}
        result = validate_data(b'id,email\n1,a@example.com\n1,broken\nx,\n', 'data.csv', SETTINGS, schema=schema)
        self.assertFalse(result['valid'])
        self.assertIn('duplicate', [x['code'] for x in result['issues']])
        self.assertIn('invalid_type', [x['code'] for x in result['issues']])
        self.assertEqual(result['issue_count'], len(result['issues']))
    def test_missing_column(self):
        result = validate_data(b'id\n1\n', 'data.csv', SETTINGS, ['name'])
        self.assertEqual(result['issues'][0]['code'], 'missing_column')
    def test_reports(self):
        result = validate_data(b'id\n\"\"\n', 'data.csv', SETTINGS, ['id'])
        self.assertIn('issues', json.loads(report_bytes(result, 'json')))
        self.assertEqual(list(csv.DictReader(io.StringIO(report_bytes(result, 'csv').decode('utf-8-sig'))))[0]['code'], 'required_empty')
    def test_invalid_schema(self):
        with self.assertRaises(DataError):
            validate_data(b'id\n1\n', 'data.csv', SETTINGS, schema={'fields': {'id': {'type': 'unknown'}}})
    def test_numeric_bounds(self):
        result = validate_data(b'amount\n2\n8\n', 'data.csv', SETTINGS, schema={'fields': {'amount': {'type': 'number', 'min': 3, 'max': 7}}})
        self.assertEqual({x['code'] for x in result['issues']}, {'min', 'max'})

if __name__ == '__main__':
    unittest.main()
