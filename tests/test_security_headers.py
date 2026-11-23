import base64
import hashlib
import re
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.security import MAIN_CSP, docs_csp


def test_main_page_strict_csp():
    with TestClient(app) as client:
        for path in ('/', '/healthz', '/static/css/app.css', '/favicon.ico'):
            response = client.get(path)
            assert response.status_code == 200
            assert response.headers['content-security-policy'] == MAIN_CSP
            assert response.headers['x-content-type-options'] == 'nosniff'
            assert response.headers['x-frame-options'] == 'DENY'
            assert response.headers['cross-origin-opener-policy'] == 'same-origin'
            assert response.headers['cross-origin-resource-policy'] == 'same-origin'


def test_docs_hashes_and_headers():
    with TestClient(app) as client:
        for path in ('/docs', '/redoc', '/docs/oauth2-redirect'):
            response = client.get(path)
            assert response.status_code == 200
            policy = response.headers['content-security-policy']
            assert policy == docs_csp(response.text)
            assert "'unsafe-eval'" not in policy
            for script in re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>', response.text, re.DOTALL | re.IGNORECASE):
                if script.strip():
                    digest = base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
                    assert "'sha256-" + digest + "'" in policy


def test_main_html_has_no_inline_executable_code():
    html = (
        Path(__file__).resolve().parents[1]
        / "app/templates/index.html"
    ).read_text(encoding="utf-8")

    scripts = re.findall(
        r"<script\b([^>]*)>(.*?)</script\s*>",
        html,
        re.IGNORECASE | re.DOTALL,
    )

    for attributes, content in scripts:
        assert re.search(
            r"""\bsrc\s*=\s*["']/static/js/[^"']+["']""",
            attributes,
            re.IGNORECASE,
        )
        assert not content.strip()

    assert not re.search(
        r"""\son[a-z]+\s*=""",
        html,
        re.IGNORECASE,
    )

    assert not re.search(
        r"""\sstyle\s*=""",
        html,
        re.IGNORECASE,
    )
