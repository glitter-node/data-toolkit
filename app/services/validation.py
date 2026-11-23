import csv
import io
import json
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from app.services.engine import DataError, to_rows

TYPES = {'string', 'integer', 'number', 'boolean', 'date', 'datetime', 'email'}

def check_schema(schema):
    if not isinstance(schema, dict):
        raise DataError('Schema must be an object')
    fields = schema.get('fields', {})
    if not isinstance(fields, dict) or len(fields) > 500:
        raise DataError('Invalid schema fields')
    for name, rule in fields.items():
        if not isinstance(name, str) or not name or not isinstance(rule, dict):
            raise DataError('Invalid field rule')
        if rule.get('type', 'string') not in TYPES:
            raise DataError('Unsupported field type')
        if any(key in rule and type(rule[key]) is not bool for key in ('required', 'unique', 'nullable')):
            raise DataError('Invalid boolean constraint')
        for key in ('min_length', 'max_length'):
            if key in rule and (type(rule[key]) is not int or rule[key] < 0):
                raise DataError('Invalid length constraint')
        for key in ('min', 'max'):
            if key in rule:
                try:
                    Decimal(str(rule[key]))
                except (InvalidOperation, ValueError):
                    raise DataError('Invalid numeric constraint') from None
        if 'enum' in rule and (not isinstance(rule['enum'], list) or len(rule['enum']) > 1000 or any(isinstance(x, (dict, list)) for x in rule['enum'])):
            raise DataError('Invalid enum constraint')
        if 'pattern' in rule:
            pattern = rule['pattern']
            if not isinstance(pattern, str) or len(pattern) > 200 or re.search(r'\(\?|\\[1-9]|\{\d{4,}', pattern):
                raise DataError('Unsupported pattern')
            try:
                re.compile(pattern)
            except re.error:
                raise DataError('Invalid pattern') from None
    if schema.get('allow_extra', True) not in (True, False):
        raise DataError('Invalid allow_extra')
    return fields

def typed(value, kind):
    if kind == 'string':
        return isinstance(value, str)
    if kind == 'integer':
        return isinstance(value, int) and not isinstance(value, bool) or isinstance(value, str) and bool(re.fullmatch(r'[+-]?\d+', value.strip()))
    if kind == 'number':
        if isinstance(value, bool):
            return False
        try:
            return Decimal(str(value)).is_finite()
        except (InvalidOperation, ValueError):
            return False
    if kind == 'boolean':
        return isinstance(value, bool) or isinstance(value, str) and value.strip().lower() in ('true', 'false', '1', '0', 'yes', 'no')
    if kind in ('date', 'datetime'):
        if not isinstance(value, str):
            return False
        try:
            datetime.fromisoformat(value) if kind == 'datetime' else datetime.strptime(value, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    if kind == 'email':
        return isinstance(value, str) and bool(re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', value))
    return False

def validate_structure(data, name, settings, required=None, schema=None, max_issues=1000):
    required = required or []
    if not isinstance(required, list) or any(not isinstance(x, str) or not x for x in required) or len(required) > 500:
        raise DataError('Invalid required columns')
    schema = schema or {}
    fields = check_schema(schema)
    columns, rows = to_rows(data, name, settings.max_rows, settings.max_columns)
    issues = []
    totals = {'error': 0, 'warning': 0}
    def add(row, column, code, message, severity='error'):
        totals[severity] += 1
        if len(issues) < max_issues:
            issues.append({'row': row, 'column': column, 'code': code, 'severity': severity, 'message': message})
    mandatory = set(required) | {key for key, rule in fields.items() if rule.get('required')}
    for column in sorted(mandatory):
        if column not in columns:
            add(None, column, 'missing_column', 'Missing required column')
    if schema.get('allow_extra') is False:
        for column in columns:
            if column not in fields:
                add(None, column, 'unexpected_column', 'Unexpected column')
    uniques = {key: set() for key, rule in fields.items() if rule.get('unique')}
    for index, row in enumerate(rows, 2):
        for column in mandatory:
            if column in columns and row.get(column) in (None, ''):
                add(index, column, 'required_empty', 'Required value is empty')
        for column, rule in fields.items():
            if column not in columns:
                continue
            value = row.get(column)
            if value is None or value == '':
                if value is None and rule.get('nullable') is False and column not in mandatory:
                    add(index, column, 'null_value', 'Null value is not allowed')
                continue
            kind = rule.get('type', 'string')
            if not typed(value, kind):
                add(index, column, 'invalid_type', f'Expected {kind}')
                continue
            value_text = str(value)
            if 'min_length' in rule and len(value_text) < rule['min_length']:
                add(index, column, 'min_length', 'Value is too short')
            if 'max_length' in rule and len(value_text) > rule['max_length']:
                add(index, column, 'max_length', 'Value is too long')
            if 'enum' in rule and value not in rule['enum'] and value_text not in [str(v) for v in rule['enum']]:
                add(index, column, 'enum', 'Value is not in allowed choices')
            if 'pattern' in rule and re.fullmatch(rule['pattern'], value_text) is None:
                add(index, column, 'pattern', 'Value does not match pattern')
            if kind in ('integer', 'number'):
                number = Decimal(value_text)
                if 'min' in rule and number < Decimal(str(rule['min'])):
                    add(index, column, 'min', 'Value is below minimum')
                if 'max' in rule and number > Decimal(str(rule['max'])):
                    add(index, column, 'max', 'Value exceeds maximum')
            if column in uniques:
                if value_text in uniques[column]:
                    add(index, column, 'duplicate', 'Duplicate value')
                uniques[column].add(value_text)
    return {'valid': totals['error'] == 0, 'columns': columns, 'row_count': len(rows), 'issues': issues, 'issue_count': sum(totals.values()), 'truncated': sum(totals.values()) > len(issues), 'summary': totals, 'schema_fields': len(fields)}

def report_bytes(result, fmt):
    if fmt == 'json':
        return json.dumps(result, ensure_ascii=False, indent=2).encode('utf-8')
    if fmt == 'csv':
        out = io.StringIO(newline='')
        writer = csv.DictWriter(out, fieldnames=['row', 'column', 'code', 'severity', 'message'])
        writer.writeheader()
        writer.writerows(result['issues'])
        return ('\ufeff' + out.getvalue()).encode('utf-8')
    raise DataError('Unsupported report format')
