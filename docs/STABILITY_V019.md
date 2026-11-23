# v0.1.9 stability and regression checks

## UI

- Keep the four existing tabs. Verify that History hides the workspace and transform panel, and returning to Convert restores them.
- Test Light, Dark, and Warm with keyboard-only navigation and at viewport widths of 375, 768, and 1440 pixels.
- Verify disabled controls remain legible, focus is visible, and the Back to top control is hidden near the top.
- Confirm language changes update dynamic status messages and the chosen language survives reload.

## Uploads and processing

- File names must be simple leaf names with a supported extension. Empty files, oversized uploads, and unsupported extensions return client errors.
- Single-file upload is bounded by MAX_UPLOAD_MB. Batch count and aggregate bytes are bounded by MAX_BATCH_FILES and MAX_BATCH_TOTAL_MB.
- Conversion and validation return client errors for malformed inputs. Batch archives contain report.json with per-file outcomes.
- Background output is first written to a temporary file and published atomically. Cancelled or failed jobs must not leave downloadable results.
- Completed and expired jobs require their original access token. Restart recovery marks interrupted jobs as failed.

## Deployment

1. Install requirements into the active Python environment.
2. Run `python -m pytest -v` and `node --check app/static/js/app.js`.
3. Restart Uvicorn and verify `/healthz`.
4. Check Convert, Validate, Batch, and Job history in the browser.
5. Check i18n and static asset cache refresh after deployment.

## Limitations

Automated Python tests do not replace end-to-end browser testing or concurrent production load testing. Confirm those separately before a stable release.
