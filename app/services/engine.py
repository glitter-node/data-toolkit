# pylint: disable=cell-var-from-loop

import csv
import io
import json
import re
from xml.etree import ElementTree as ET
from defusedxml import ElementTree as SafeET
import yaml
from openpyxl import Workbook, load_workbook

FORMATS = {"csv", "json", "xml", "yaml", "xlsx"}

class DataError(ValueError):
    pass

def detect(name):
    suffix = name.rsplit(".", 1)[-1].lower()
    if suffix in ("yml", "yaml"):
        return "yaml"
    if suffix not in FORMATS:
        raise DataError("Unsupported input format")
    return suffix

def to_rows(data, name, max_rows=100000, max_columns=500, sheet_name=None):
    kind = detect(name)
    if kind == "csv":
        raw = data.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(raw, newline=""))
        if not reader.fieldnames or None in reader.fieldnames:
            raise DataError("Invalid CSV header")
        columns = list(reader.fieldnames)
        rows = []
        for row in reader:
            if None in row:
                raise DataError("Inconsistent CSV column count")
            rows.append({c: row.get(c) for c in columns})
            if len(rows) > max_rows:
                raise DataError("Row limit exceeded")
    elif kind == "xlsx":
        book = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
        try:
            sheet = book[sheet_name] if sheet_name is not None and sheet_name in book.sheetnames else book.active
            if sheet_name is not None and sheet_name not in book.sheetnames:
                raise DataError("Unknown worksheet")
            if sheet is None:
                raise DataError("No active worksheet")
            iterator = sheet.iter_rows(values_only=True)
            headers = next(iterator, None)
            if not headers:
                raise DataError("Empty worksheet")
            columns = [str(v) if v is not None else "" for v in headers]
            rows = []
            for values in iterator:
                rows.append({c: v for c, v in zip(columns, values)})
                if len(rows) > max_rows:
                    raise DataError("Row limit exceeded")
        finally:
            book.close()
    else:
        if kind == "json":
            obj = json.loads(data.decode("utf-8-sig"))
        elif kind == "yaml":
            obj = yaml.safe_load(data.decode("utf-8-sig"))
        else:
            root = SafeET.fromstring(data)
            obj = [{child.tag: child.text for child in row} for row in root]
        if not isinstance(obj, list) or any(not isinstance(row, dict) for row in obj):
            raise DataError("Expected an array of flat objects")
        rows = obj
        columns = list(dict.fromkeys(k for row in rows for k in row))
    if len(columns) > max_columns:
        raise DataError("Column limit exceeded")
    if len(set(columns)) != len(columns) or not all(columns):
        raise DataError("Duplicate or empty column name")
    if len(rows) > max_rows:
        raise DataError("Row limit exceeded")
    if any(isinstance(v, (dict, list, set)) for row in rows for v in row.values()):
        raise DataError("Nested values require explicit flattening")
    return columns, rows

def transform(columns, rows, options):
    selected = options.get("columns") or columns
    if not isinstance(selected, list) or len(set(selected)) != len(selected) or any(c not in columns for c in selected):
        raise DataError("Invalid columns")
    result = [{c: row.get(c) for c in selected} for row in rows]
    filters = options.get("filters", [])
    if not isinstance(filters, list) or len(filters) > 20:
        raise DataError("Invalid filters")
    for rule in filters:
        col = rule.get("column")
        op = rule.get("operator")
        val = str(rule.get("value", ""))
        if col not in selected or op not in ("eq", "ne", "contains", "empty", "not_empty"):
            raise DataError("Invalid filter")
        def matches(row):
            actual = "" if row.get(col) is None else str(row[col])
            return {"eq": lambda: actual == val, "ne": lambda: actual != val, "contains": lambda: val in actual, "empty": lambda: actual == "", "not_empty": lambda: actual != ""}[op]()
        result = [row for row in result if matches(row)]
    if options.get("deduplicate"):
        seen = set()
        unique = []
        for row in result:
            key = json.dumps(row, sort_keys=True, ensure_ascii=False, default=str)
            if key not in seen:
                seen.add(key)
                unique.append(row)
        result = unique
    sort = options.get("sort")
    if sort:
        col = sort.get("column")
        if col not in selected:
            raise DataError("Invalid sort column")
        result.sort(key=lambda row: (row.get(col) is None, str(row.get(col) or "")), reverse=bool(sort.get("descending")))
    return selected, result

def export(columns, rows, kind):
    if kind not in FORMATS:
        raise DataError("Unsupported output format")
    if kind == "csv":
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
        return stream.getvalue().encode("utf-8-sig")
    if kind == "json":
        return json.dumps(rows, ensure_ascii=False, indent=2, default=str).encode("utf-8")
    if kind == "yaml":
        return yaml.safe_dump(json.loads(json.dumps(rows, default=str)), allow_unicode=True, sort_keys=False).encode("utf-8")
    if kind == "xml":
        root = ET.Element("rows")
        for row in rows:
            item = ET.SubElement(root, "row")
            for column in columns:
                if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", column):
                    raise DataError("XML requires valid element names")
                ET.SubElement(item, column).text = "" if row.get(column) is None else str(row[column])
        return ET.tostring(root, encoding="utf-8", xml_declaration=True)
    book = Workbook(write_only=True)
    sheet = book.create_sheet("Data")
    sheet.append(columns)
    for row in rows:
        values = []
        for c in columns:
            value = row.get(c)
            if isinstance(value, str) and value.startswith(("=", "+", "-", "@", "\\t", "\\r")):
                value = "'" + value
            values.append(value)
        sheet.append(values)
    stream = io.BytesIO()
    book.save(stream)
    return stream.getvalue()
