import io
import json
import unittest
import zipfile
from types import SimpleNamespace
from app.services.operations import batch_data, convert_data, inspect_data, validate_data

SETTINGS = SimpleNamespace(max_rows=1000, max_columns=100, preview_rows=10, max_batch_files=10, max_upload_mb=50)

class OperationsTests(unittest.TestCase):
    def test_inspect(self):
        result = inspect_data(b"id,name\n1,Alice\n", "sample.csv", SETTINGS)
        self.assertEqual(result["row_count"], 1)

    def test_rename(self):
        result = convert_data(b"id,name\n1,Alice\n", "sample.csv", "json", {"rename":{"name":"label"}}, SETTINGS)
        self.assertEqual(json.loads(result)[0]["label"], "Alice")

    def test_validation(self):
        result = validate_data(b"id,name\n1,\n", "sample.csv", SETTINGS, ["name"])
        self.assertFalse(result["valid"])

    def test_batch(self):
        result = batch_data([("a.csv", b"id\n1\n"), ("b.csv", b"id\n2\n")], "json", {}, SETTINGS)
        with zipfile.ZipFile(io.BytesIO(result)) as archive:
            self.assertEqual(len([n for n in archive.namelist() if n.endswith(".json")]), 3)

if __name__ == "__main__":
    unittest.main()
