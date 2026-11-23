from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_workspace_summary_and_result_detail_are_separate():
    source = (ROOT / "app/static/js/app.js").read_text()
    assert 'statusKey("fileInvalid");document.getElementById("resultState")' in source
    assert 'error.textContent=`${t().failed}: ${message}`' in source
    assert 'getFileState:index=>fileStates.get(index)' in source
    assert 'dataToolkit:fileStateChanged' in source

def test_responsive_header_labels_do_not_wrap():
    css = (ROOT / "app/static/css/app.css").read_text()
    assert '.header-settings label>span{white-space:nowrap' in css
    assert '.header-settings{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))' in css
