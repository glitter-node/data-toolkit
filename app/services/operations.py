import io
import json
import re
import zipfile
from app.services.engine import DataError, detect, export, to_rows, transform

def inspect_data(data, name, settings, page=1, page_size=25, sheet_name=None):
    if not isinstance(page, int) or page < 1 or page > 100000:
        raise DataError("Invalid page")
    if not isinstance(page_size, int) or not 1 <= page_size <= 100:
        raise DataError("Invalid page size")
    sheets = []
    if detect(name) == "xlsx":
        from openpyxl import load_workbook
        book = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
        try:
            sheets = list(book.sheetnames)
            if sheet_name is None:
                sheet_name = book.active.title if book.active else None
        finally:
            book.close()
    cols, rows = to_rows(data, name, settings.max_rows, settings.max_columns, sheet_name=sheet_name)
    start = (page - 1) * page_size
    return {"format": detect(name), "columns": cols, "row_count": len(rows),
            "preview": rows[start:start + page_size], "page": page, "page_size": page_size,
            "page_count": max(1, (len(rows) + page_size - 1) // page_size),
            "sheets": sheets, "sheet": sheet_name, "file_size": len(data)}

def validate_data(data, name, settings, required=None, schema=None):
    from app.services.validation import validate_structure
    return validate_structure(data, name, settings, required, schema)

def convert_data(data, name, kind, options, settings):
    if not isinstance(options, dict):
        raise DataError("Options must be an object")
    cols, rows = to_rows(data, name, settings.max_rows, settings.max_columns)
    cols, rows = transform(cols, rows, options)
    rename = options.get("rename", {})
    if not isinstance(rename, dict) or any(c not in cols for c in rename):
        raise DataError("Invalid rename map")
    names = [rename.get(c, c) for c in cols]
    if any(not isinstance(c, str) or not c or len(c) > 200 for c in names) or len(set(names)) != len(names):
        raise DataError("Invalid output columns")
    output = export(names, [{rename.get(c,c): row.get(c) for c in cols} for row in rows], kind)
    if len(output) > settings.max_upload_mb * 1024 * 1024 * 4:
        raise DataError("Output too large")
    return output

def batch_data(files, kind, options, settings):
    if not files or len(files) > settings.max_batch_files:
        raise DataError("Invalid batch count")
    result = io.BytesIO()
    report = []
    with zipfile.ZipFile(result, 'w', zipfile.ZIP_DEFLATED) as archive:
        for index, (name, content) in enumerate(files, 1):
            try:
                output = convert_data(content, name, kind, options, settings)
                stem = re.sub(r'[^a-zA-Z0-9_-]', '_', name.rsplit('.', 1)[0])[:60] or 'data'
                target = f'{index:03d}_{stem}.{kind}'
                archive.writestr(target, output)
                report.append({"source": name, "status": "completed", "output": target})
            except Exception as exc:
                report.append({"source": name, "status": "failed", "error": str(exc)[:250]})
        archive.writestr('report.json', json.dumps(report, ensure_ascii=False, indent=2))
    return result.getvalue()
