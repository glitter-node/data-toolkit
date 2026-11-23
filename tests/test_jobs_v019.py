import tempfile
from pathlib import Path
from unittest.mock import patch
from app.core import jobs


def test_job_lifecycle_and_access():
    with tempfile.TemporaryDirectory() as folder, patch.object(jobs.settings, 'data_dir', Path(folder)):
        identifier, token = jobs.create('result.json')
        assert jobs.get(identifier, 'incorrect') is None
        job = jobs.get(identifier, token)
        assert job is not None
        assert job['progress'] == 0
        assert jobs.delete(identifier, token) is False
        assert jobs.transition(identifier, 'queued', 'running')
        jobs.progress(identifier, 25)
        job = jobs.get(identifier, token)
        assert job is not None
        assert job['progress'] == 25
        jobs.result_size(identifier, 42)
        assert jobs.transition(identifier, 'running', 'completed')
        job = jobs.get(identifier, token)
        assert job is not None
        assert job['progress'] == 100
        assert job['result_size'] == 42
        assert jobs.delete(identifier, token) is True
        assert jobs.get(identifier, token) is None


def test_cleanup_keeps_active_jobs():
    with tempfile.TemporaryDirectory() as folder, patch.object(jobs.settings, 'data_dir', Path(folder)), patch.object(jobs.settings, 'job_ttl_seconds', 0):
        identifier, token = jobs.create('result.csv')
        jobs.cleanup()
        assert jobs.get(identifier, token) is not None
        jobs.update(identifier, 'failed', 'test error')
        jobs.cleanup()
        assert jobs.get(identifier, token) is None
