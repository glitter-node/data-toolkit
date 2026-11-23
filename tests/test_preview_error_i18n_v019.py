from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_preview_error_translations():
    for locale in ('ko', 'en', 'ja', 'zh-CN'):
        source = (ROOT / 'app/static/js/i18n/locales' / f'{locale}.js').read_text()
        for key in ('invalidJsonPosition', 'invalidJson', 'invalidFlatArray', 'fileValid', 'fileInvalid'):
            assert f'"{key}"' in source


def test_preview_error_state_and_file_sizes():
    source = (ROOT / 'app/static/js/app.js').read_text()
    assert 'function showError()' in source
    assert 'fileStates.set(selected,"fileInvalid")' in source
    assert 'fileStates.set(selected,"fileValid")' in source
    assert 'window.dataToolkitFormatSize(item.size)' in source
    assert 'document.getElementById("previewEmpty").hidden=true' in source
