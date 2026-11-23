import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

from fastapi.testclient import TestClient
from app.main import app
from app.core import jobs

pytest.importorskip("sse_starlette")

def test_job_api_authorization_and_download():
    with tempfile.TemporaryDirectory() as folder, patch.object(jobs.settings, 'data_dir', Path(folder)):
        with TestClient(app) as client:
            identifier, token = jobs.create('result.json')
            url = f'/api/jobs/{identifier}'
            assert client.get(url).status_code == 404
            assert client.get(url, headers={'X-Job-Token': token}).json()['progress'] == 0
            assert client.delete(url, headers={'X-Job-Token': token}).status_code == 409
            jobs.transition(identifier, 'queued', 'running')
            output = Path(folder) / 'output'
            output.mkdir()
            (output / f'{identifier}.bin').write_bytes(b'{}')
            jobs.result_size(identifier, 2)
            jobs.transition(identifier, 'running', 'completed')
            response = client.get(url + '/download', headers={'X-Job-Token': token})
            assert response.status_code == 200
            assert response.content == b'{}'
            assert client.delete(url, headers={'X-Job-Token': token}).json()['deleted']
            assert not (output / f'{identifier}.bin').exists()


def test_validation_alias():
    with TestClient(app) as client:
        response = client.post('/api/validate', files={'file': ('test.csv', b'id\n1\n', 'text/csv')}, data={'schema': '{"fields":{"id":{"type":"integer"}}}'})
        assert response.status_code == 200
