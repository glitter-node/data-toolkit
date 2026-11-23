import unittest
from app.services.engine import to_rows, transform, export, DataError

class EngineTests(unittest.TestCase):
    def test_csv_json(self):
        cols, rows = to_rows(b"id,name\n1,Alice\n2,Bob\n", "test.csv")
        self.assertEqual(len(rows), 2)
        self.assertIn(b"Alice", export(cols, rows, "json"))

    def test_filter(self):
        cols, rows = to_rows(b"id,name\n1,Alice\n2,Bob\n", "test.csv")
        _, result = transform(cols, rows, {"filters": [{"column": "name", "operator": "eq", "value": "Bob"}]})
        self.assertEqual(len(result), 1)

    def test_nested_rejected(self):
        with self.assertRaises(DataError):
            to_rows(b'[{"nested":{"x":1}}]', "test.json")

if __name__ == "__main__":
    unittest.main()
