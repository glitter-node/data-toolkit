from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_theme_options():
    html = (ROOT / 'app/templates/index.html').read_text()
    for theme in ('system', 'light', 'dark', 'warm'):
        assert f'<option value="{theme}" data-i18n="theme{theme.title()}">' in html


def test_theme_assets():
    css = (ROOT / 'app/static/css/app.css').read_text()
    js = (ROOT / 'app/static/js/app.js').read_text()
    assert 'body.warm{' in css
    assert '--accent:#a96d48' in css
    assert 'function applyTheme(theme)' in js
    assert 'dataToolkit.theme' in js
