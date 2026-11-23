import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ('ko', 'en', 'ja', 'zh-CN')


def catalogs():
    output = {}
    for language in LOCALES:
        path = ROOT / 'app/static/js/i18n/locales' / f'{language}.js'
        source = path.read_text(encoding='utf-8')
        match = re.search(r'= (\{.*\});\s*$', source, re.DOTALL)
        assert match, language
        output[language] = json.loads(match.group(1))
    return output


def test_default_korean_and_script_order():
    html = (ROOT / 'app/templates/index.html').read_text(encoding='utf-8')
    runtime = (ROOT / 'app/static/js/i18n/index.js').read_text(encoding='utf-8')
    app = (ROOT / 'app/static/js/app.js').read_text(encoding='utf-8')
    assert 'const fallback = "ko"' in runtime
    assert 'window.DataToolkitI18n.getLocale()' in app
    assert '<option value="ko" selected>' in html
    assert html.index('/static/js/i18n/locales/ko.js') < html.index('/static/js/i18n/index.js') < html.index('/static/js/app.js')


def test_locale_key_parity():
    data = catalogs()
    expected = {group: set(values) for group, values in data['ko'].items()}
    for language in LOCALES:
        assert {group: set(values) for group, values in data[language].items()} == expected
        for values in data[language].values():
            assert all(isinstance(value, str) and value.strip() for value in values.values())


def test_i18n_no_inline_code_and_valid_js():
    html = (ROOT / 'app/templates/index.html').read_text(encoding='utf-8')
    for script in re.findall(r'<script\b([^>]*)>(.*?)</script\s*>', html, re.I | re.S):
        assert 'src=' in script[0]
        assert not script[1].strip()
    for path in (ROOT / 'app/static/js/i18n').rglob('*.js'):
        subprocess.run(['node', '--check', str(path)], check=True, capture_output=True)


def test_localized_controls_and_status():
    html = (ROOT / 'app/templates/index.html').read_text(encoding='utf-8')
    app = (ROOT / 'app/static/js/app.js').read_text(encoding='utf-8')
    runtime = (ROOT / 'app/static/js/i18n/index.js').read_text(encoding='utf-8')
    assert 'id="status" role="status" data-i18n="ready"' in html
    assert 'statusTranslation="ready"' in app
    assert 'if(statusTranslation)' in app
    assert 'data-i18n-placeholder' in runtime
    assert 'data-i18n="topShort"' in html
    for key in ('themeSystem', 'themeLight', 'themeDark', 'themeWarm', 'filterEquals', 'sortAscending', 'historyDownload', 'historyDelete'):
        assert f'data-i18n="{key}"' in html
    catalogs_by_locale = catalogs()
    for language in LOCALES:
        assert all(key in catalogs_by_locale[language]['controls'] for key in ('themeSystem', 'topShort', 'filterEquals', 'sortAscending'))


def test_static_asset_cache_busting():
    from app.asset_version import version_assets
    html = '<script src="/static/js/app.js" defer></script><link href="/static/css/app.css" rel="stylesheet">'
    rendered = version_assets(html)
    assert re.search(r'/static/js/app\.js\?v=[0-9a-f]{16}', rendered)
    assert re.search(r'/static/css/app\.css\?v=[0-9a-f]{16}', rendered)
    assert version_assets(html) == rendered
