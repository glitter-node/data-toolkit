from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_soft3d_stylesheet_loaded():
    html = (ROOT / "app/templates/index.html").read_text(encoding="utf-8")
    assert '<link rel="stylesheet" href="/static/css/soft3d.css">' in html
    assert html.index("/static/css/app.css") < html.index("/static/css/soft3d.css")


def test_soft3d_theme_depth_and_accessibility():
    css = (ROOT / "app/static/css/soft3d.css").read_text(encoding="utf-8")
    for item in ("--elevation-high", "--recessed", "--button-shadow", "body.dark", "body.warm", ".result-placeholder", ".workspace .action-panel", "prefers-reduced-motion"):
        assert item in css
    assert "@import" not in css
