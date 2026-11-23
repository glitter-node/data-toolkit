import hashlib
import re
from pathlib import Path

STATIC_ROOT = Path(__file__).parent / "static"
ASSET_PATTERN = re.compile(r'(?P<prefix>(?:src|href)="/static/)(?P<path>[^"?]+\.(?:js|css))(?P<suffix>")')


def version_assets(html):
    def replace(match):
        path = STATIC_ROOT / match.group("path")
        if not path.is_file() or not path.resolve().is_relative_to(STATIC_ROOT.resolve()):
            return match.group(0)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
        return f'{match.group("prefix")}{match.group("path")}?v={digest}{match.group("suffix")}'

    return ASSET_PATTERN.sub(replace, html)
