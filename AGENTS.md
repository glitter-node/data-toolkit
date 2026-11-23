# Data Toolkit Agent Instructions

Current project release: **Data Toolkit v1.0.0 — Stable Release**.

The historical version headings and documentation filenames identify when features or rules were introduced. They do not override the current v1.0.0 release requirements.

Apply the current implementation, configuration, API contracts, and security policies defined in the source.

## Core project rules

- Preserve the Python 3.11+ / FastAPI / Uvicorn architecture.
- Maintain the self-hosted, local-first application design.
- Preserve the MIT License and third-party license notices.
- Keep the existing root-level `app/`, `tests/`, and `docs/` structure.
- Do not introduce a duplicate `src/app/` source tree.
- Keep HTML `lang="en"`.
- Keep CSS and JavaScript in separate external files.
- Do not add inline styles, inline scripts, or inline event handlers.
- Keep source-code messages and identifiers in English.
- Do not add unnecessary code comments.
- Preserve existing API contracts and SQLite data compatibility.
- Preserve `.env`, virtual environments, and persistent `data/` contents during upgrades.
- Document new features, endpoints, configuration changes, and limitations.
- Do not claim tests, deployment checks, or security audits that have not been performed.

## Application architecture

Maintain the existing application architecture:

- Python for application logic and structured-data processing.
- FastAPI for HTTP APIs, validation, and application routing.
- Uvicorn as the ASGI server.
- Jinja2 for server-rendered HTML templates.
- SQLite for persistent background-job metadata.
- openpyxl for XLSX processing.
- PyYAML for YAML processing.
- defusedxml for XML parsing.

Keep the application operational without mandatory Docker, Redis, MariaDB, or external cloud services.

Do not introduce additional infrastructure dependencies without a documented architectural requirement.

Keep the existing application entry point:

`app.main:app`

The reference development server listens on `127.0.0.1:8015`.

Do not assume that `APP_PORT` automatically configures the Uvicorn listening port.

## Structured-data processing

Preserve support for the existing structured-data formats:

- CSV
- JSON
- XML
- YAML
- XLSX

Maintain the flat tabular data model.

Do not silently flatten nested objects or arrays.

Preserve the documented limitations of each format:

- CSV uses UTF-8 with optional BOM.
- XML supports simple row-based structured documents.
- XML output must use valid element names.
- XLSX processing uses cached worksheet values.
- XLSX conversion does not guarantee preservation of formulas or styling.
- Cross-format conversion is not guaranteed to be lossless.

Preserve the existing conversion operations:

- Column selection
- Column renaming
- Filtering
- Sorting
- Deduplication

Do not change transformation semantics without updating tests and API documentation.

## Data inspection and preview

Preserve the existing inspection and preview functionality.

- File-by-file inspection and preview
- Column information
- Paginated preview rows
- Configurable page size
- XLSX worksheet selection
- File name and file-size display
- Individual file removal
- Multiple-file selection

Maintain explicit validation of preview parameters and supported file formats.

Do not silently select another worksheet or substitute unsupported preview options.

### Preview error presentation

Keep the Workspace and Results panel responsibilities separate.

**Workspace:**

- Display selected files and file sizes.
- Display concise file-level status.
- Use short localized status labels.
- Avoid duplicating detailed parser errors.

**Results panel:**

- Display the selected file's detailed preview result.
- Display localized parsing or validation errors.
- Include available line, column, or other location information.
- Keep errors associated with the selected file.

Do not suppress useful backend error details or replace them with misleading success states.

Preserve the existing error-response behavior for invalid input.

## Data validation

Preserve the Validate workflow and existing validation API.

Maintain support for:

- Required-column validation
- Optional JSON field constraints
- Field-level validation issues
- Downloadable JSON issue reports
- Downloadable CSV issue reports

Do not introduce incompatible schema behavior without documenting the migration.

Keep validation failures distinguishable from application or transport failures.

Refer to `docs/V0.1.9_VALIDATION.md` for the historical validation feature specification.

## Batch processing

Preserve the existing batch conversion workflow.

- Accept supported uploaded data files.
- Process multiple files through the existing API.
- Generate downloadable ZIP results.
- Include the processing report as `report.json`.
- Report file-level processing failures.
- Preserve supported output formats and transformation behavior.

Maintain resource controls and upload-size validation.

Do not claim that batch processing is memory-isolated.

Document any changes to buffering, concurrency, or output generation.

## Background jobs

Preserve SQLite-backed background processing and the existing job API contracts.

Maintain:

- Job creation
- Job status inspection
- Job-specific access tokens
- Token-protected result downloads
- Progress and status reporting
- Cancellation requests
- Retention and cleanup behavior

Do not expose a global unauthenticated job listing.

Do not expose job results without the required access token.

Queued or running jobs are not automatically resumed after an application restart unless an explicit recovery design is implemented.

Cancellation is cooperative. Running thread-based work cannot be forcibly interrupted.

Do not publish cancelled results when cancellation is observed.

Preserve existing job metadata and stored results during upgrades.

Avoid introducing concurrent database writes or multiple-worker behavior without reviewing SQLite and job execution consistency.

Refer to `docs/V0.1.9_JOBS.md` for the historical background-job implementation.

## Web interface

Preserve the existing primary navigation:

- Convert
- Validate
- Batch
- Job history

Maintain the Workspace and Results layout.

Preserve the responsive interface, accessible controls, keyboard focus behavior, and file upload interactions.

Do not regress the following behavior:

- Drag-and-drop file selection
- Native file picker
- Multiple-file display
- File removal
- Disabled actions when required input is missing
- Selected-file preview
- Operation controls within the Workspace
- Responsive card stacking
- Back to top behavior
- Reduced-motion accessibility preferences

### Responsive layout

Keep language and theme labels on a single line.

Prevent labels from breaking into individual characters at narrow viewport widths.

Allow header controls to wrap or stack as complete groups when space is insufficient.

Do not introduce horizontal page overflow or inaccessible controls.

## Themes

Preserve the four appearance modes:

- System
- Light
- Dark
- Warm

Maintain theme selection persistence.

Preserve operating-system color scheme behavior for System mode.

Keep theme-specific colors, borders, shadows, and contrast in external stylesheets.

Maintain the Soft 3D visual treatment without excessive shadowing or reduced readability.

Keep `app/static/css/soft3d.css` loaded after the base application stylesheet.

Do not add inline CSS to implement theme behavior.

Preserve visible keyboard focus states and reduced-motion support.

Refer to `docs/THEMES.md`.

## Internationalization

Preserve the four supported locales:

- `ko`
- `en`
- `ja`
- `zh-CN`

Korean is the default and fallback locale.

Maintain translation-key parity across all locale resources.

Do not hardcode new user-facing messages in JavaScript or HTML when a translation key is required.

Keep source message identifiers and fallback strings in English.

Preserve the browser storage key:

`dataToolkit.locale`

Localize user-facing validation errors, preview errors, status labels, and workflow messages.

Do not translate API field names, protocol identifiers, or internal configuration keys.

Refer to `docs/I18N.md`.

## Security

Preserve the existing security middleware and Content Security Policy defined in `app/security.py`.

Keep the main application compatible with a strict same-origin CSP.

Do not introduce:

- Inline executable JavaScript
- Inline CSS
- Inline event handlers
- Unnecessary third-party script dependencies
- `unsafe-inline` or `unsafe-eval` exceptions without explicit security review

FastAPI documentation routes use a separate CSP configuration with dynamically computed inline-script SHA-256 hashes.

Do not apply the main application CSP indiscriminately to documentation routes.

Avoid duplicate or conflicting CSP headers from reverse proxies.

Preserve the existing security response headers and origin restrictions.

### File upload security

Keep data processing upload-based.

Do not add arbitrary server filesystem access.

Preserve:

- Supported file extension validation
- Safe filename validation
- Empty upload rejection
- Upload-size limits
- Input parsing restrictions
- Safe output handling
- Protected job results

Do not allow user-controlled filenames to escape intended application storage directories.

Do not weaken XML parsing protections.

### Authentication and access control

The application does not provide general user-account authentication.

Do not describe job access tokens as equivalent to full application authentication.

Preserve token-based authorization for background-job resources.

Avoid logging access tokens or exposing them unnecessarily.

For public deployment, document the requirement for additional authentication, request limits, HTTPS, and network-level protections.

Refer to `docs/SECURITY.md`.

## API compatibility

Preserve the existing documented API endpoints, including:

- `GET /healthz`
- `POST /api/inspect`
- `POST /api/preview`
- `POST /api/convert`
- `POST /api/transform`
- `POST /api/validate`
- `POST /api/batch`
- `POST /api/jobs`
- `POST /api/jobs/{id}/cancel`

Preserve existing job status, event-stream, and download operations.

Maintain compatibility with the JSON `options` form field used by conversion workflows.

Do not rename request fields, response fields, or endpoint paths without an explicit compatibility plan.

Document any new endpoint or changed response contract in `docs/API.md`.

## Static assets

Preserve the existing static asset organization.

Keep application HTML, CSS, JavaScript, and localization resources separate.

Preserve favicon, `robots.txt`, and `sitemap.xml` routing.

Maintain static asset cache-busting behavior.

Do not require a frontend build tool unless the project architecture explicitly changes.

Refer to `docs/SEARCH_ENGINE_FILES.md`.

## Runtime and deployment

Keep local execution supported on Linux, Windows, and macOS.

The reference application entry point is:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8015 --lifespan on
```

Preserve the existing deployment model.

Do not introduce mandatory containers, external queues, or database servers.

For production deployment:

- Keep the application bound to a trusted interface.
- Use HTTPS and appropriate reverse-proxy access controls.
- Preserve application data and configuration.
- Enforce upload and request limits.
- Review security headers and CSP interaction.
- Verify job access controls.
- Restart the application after source updates.

The reference reverse-proxy mapping is:

`https://data-toolkit.glitter.kr` → `http://127.0.0.1:8015`

Do not treat configuration examples as proof of deployment.

## Testing and verification

Run the complete automated test suite before publishing a release:

```bash
python -m pytest -v
```

Check Python module compilation:

```bash
python -m compileall -q app
```

Preserve and extend regression coverage for:

- Conversion and transformation
- Validation and issue reports
- File inspection and preview
- Preview pagination
- XLSX worksheet selection
- Batch processing
- Background-job authorization
- Cancellation and cleanup
- Filename and upload security
- CSP and security headers
- Internationalization and translation parity
- Theme behavior
- Responsive layout
- Workspace and Results error separation
- UI accessibility and stability

Add regression tests for fixes that change observable behavior.

Do not weaken existing tests merely to make them pass.

Report actual test results, including failures or skipped tests.

A passing automated test suite does not constitute a security audit or complete browser compatibility certification.

## Versioning and release management

Current stable version: `1.0.0`.

Keep the application version consistent across:

- FastAPI application metadata
- `/healthz` response
- Browser-visible version
- `README.md`
- `AGENTS.md`
- Release documentation

Preserve historical version references in development documentation when they identify the original feature or implementation stage.

Do not replace historical version numbers indiscriminately.

Record new releases and significant changes in `CHANGELOG.md`.

Use the Git tag format:

`vMAJOR.MINOR.PATCH`

The first stable release tag is:

`v1.0.0`

Do not publish a release tag until the release source and required verification steps are complete.

## Documentation

Maintain the following project documentation where present:

- `README.md`
- `AGENTS.md`
- `CHANGELOG.md`
- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `docs/SECURITY.md`
- `docs/THEMES.md`
- `docs/I18N.md`
- `docs/WINDOWS_AUTOSTART.md`
- `docs/SEARCH_ENGINE_FILES.md`

Preserve historical implementation documents, including:

- `docs/V0.1.6_PREVIEW.md`
- `docs/V0.1.9_VALIDATION.md`
- `docs/V0.1.9_JOBS.md`
- `docs/STABILITY_V019.md`

Historical filenames do not need to be renamed solely because the application version changes.

Keep the README focused on the current stable application.

Use CHANGELOG for chronological release history.

Keep architecture, API, security, and deployment documentation synchronized with actual source behavior.

## License

Preserve the MIT License for original project source.

Retain third-party dependency license notices.

Refer to `THIRD_PARTY_LICENSES.md`.

Do not remove license attribution or introduce incompatible licensing changes without explicit approval.

---

**Data Toolkit v1.0.0 — Stable Release**

Maintain compatibility, security, portability, and documented behavior while developing future versions.
