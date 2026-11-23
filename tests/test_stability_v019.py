import asyncio
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import pytest
from fastapi import HTTPException
from app.main import read_file, validate_filename
from app.core import jobs

@pytest.mark.parametrize('name', ['../data.csv', 'folder/data.json', 'file.exe', '', 'bad\nname.csv'])
def test_reject_unsafe_filenames(name):
    with pytest.raises(HTTPException) as exc:
        validate_filename(name)
    assert exc.value.status_code == 422

@pytest.mark.parametrize('name', ['data.csv', 'data.JSON', '한글.xlsx'])
def test_accept_supported_filenames(name):
    assert validate_filename(name) == name

def test_reject_empty_upload():
    class EmptyFile:
        async def read(self, limit):
            return b''
    with pytest.raises(HTTPException) as exc:
        asyncio.run(read_file(EmptyFile()))
    assert exc.value.status_code == 422

def test_reject_oversized_upload():
    class LargeFile:
        async def read(self, limit):
            return b'x' * limit
    with patch('app.main.settings.max_upload_mb', 1):
        with pytest.raises(HTTPException) as exc:
            asyncio.run(read_file(LargeFile()))
    assert exc.value.status_code == 413

def test_expired_job_result_removed(tmp_path):
    with patch.object(jobs.settings, 'data_dir', tmp_path), patch.object(jobs.settings, 'job_ttl_seconds', 0):
        identifier, token = jobs.create('result.json')
        jobs.transition(identifier, 'queued', 'running')
        jobs.transition(identifier, 'running', 'completed')
        output = tmp_path / 'output'
        output.mkdir()
        (output / (identifier + '.bin')).write_bytes(b'abc')
        jobs.cleanup()
        assert not (output / (identifier + '.bin')).exists()
        assert jobs.get(identifier, token) is None
