import io
from types import SimpleNamespace
import pytest
from openpyxl import Workbook
from app.services.operations import inspect_data
from app.services.engine import DataError

SETTINGS = SimpleNamespace(max_rows=100000, max_columns=500)

def test_preview_pagination():
    data = b'id,name\n1,A\n2,B\n3,C\n'
    result = inspect_data(data, 'input.csv', SETTINGS, 2, 2)
    assert result['row_count'] == 3
    assert result['page_count'] == 2
    assert result['preview'] == [{'id': '3', 'name': 'C'}]
    assert result['file_size'] == len(data)

def test_worksheet_selection():
    workbook = Workbook()
    first = workbook.active
    assert first is not None
    first.title = 'First'
    first.append(['id'])
    first.append([1])
    second = workbook.create_sheet('Second')
    second.append(['name'])
    second.append(['Hello'])
    output = io.BytesIO()
    workbook.save(output)
    result = inspect_data(output.getvalue(), 'input.xlsx', SETTINGS, 1, 25, 'Second')
    assert result['sheets'] == ['First', 'Second']
    assert result['sheet'] == 'Second'
    assert result['columns'] == ['name']
    assert result['preview'] == [{'name': 'Hello'}]

def test_invalid_preview_options():
    with pytest.raises(DataError):
        inspect_data(b'id\n1\n', 'input.csv', SETTINGS, 0, 25)
    with pytest.raises(DataError):
        inspect_data(b'id\n1\n', 'input.csv', SETTINGS, 1, 101)
