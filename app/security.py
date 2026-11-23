import base64
import hashlib
import re

from starlette.middleware.base import BaseHTTPMiddleware

MAIN_CSP = (
    "default-src 'none'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'; "
    "form-action 'self'; script-src 'self'; script-src-attr 'none'; "
    "style-src 'self'; style-src-elem 'self'; style-src-attr 'none'; "
    "img-src 'self' blob: data:; font-src 'self'; connect-src 'self'; "
    "media-src 'none'; worker-src 'none'; manifest-src 'self'"
)


def docs_csp(html: str) -> str:
    hashes = [
        "'sha256-" + base64.b64encode(hashlib.sha256(script.encode('utf-8')).digest()).decode('ascii') + "'"
        for script in re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
        if script.strip()
    ]
    return '; '.join((
        "default-src 'none'",
        "base-uri 'self'",
        "object-src 'none'",
        "frame-ancestors 'none'",
        "form-action 'self'",
        "script-src 'self' https://cdn.jsdelivr.net " + ' '.join(hashes),
        "script-src-attr 'none'",
        "style-src 'self' https://cdn.jsdelivr.net https://fonts.googleapis.com 'unsafe-inline'",
        "img-src 'self' https://fastapi.tiangolo.com data:",
        "font-src 'self' https://fonts.gstatic.com data:",
        "connect-src 'self'",
        "media-src 'none'",
        "worker-src 'none'",
    ))


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers.setdefault('Content-Security-Policy', MAIN_CSP)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=(), payment=()'
        response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
        response.headers['Cross-Origin-Resource-Policy'] = 'same-origin'
        return response
