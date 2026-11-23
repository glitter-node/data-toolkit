from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_hidden_sections_and_focus_states():
    css = (ROOT / 'app/static/css/soft3d.css').read_text(encoding='utf-8')
    assert '.workspace-grid[hidden]' in css
    assert 'display:none!important' in css
    assert 'summary:focus-visible' in css
    assert 'prefers-reduced-motion:reduce' in css


def test_all_tabs_and_accessible_controls():
    html = (ROOT / 'app/templates/index.html').read_text(encoding='utf-8')
    for tab in ('convert', 'validate', 'batch', 'history'):
        assert f'data-tab="{tab}"' in html
    assert 'aria-live="polite"' in html
    assert 'id="backToTop"' in html


def test_no_inline_script_or_style_added():
    html = (ROOT / 'app/templates/index.html').read_text(encoding='utf-8')
    assert '<script src=' in html
    assert '<script>' not in html
    assert ' style=' not in html
