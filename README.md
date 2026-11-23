# Data Toolkit v1.0.0

**Local-first, self-hosted structured-data conversion, validation, preview, and batch processing.**

Data Toolkit is a self-hosted web application built with Python, FastAPI, Uvicorn, Jinja2, openpyxl, PyYAML, and defusedxml.

It provides a browser-based workspace for converting, validating, inspecting, and processing structured data while keeping application execution and data processing under the control of the host.

**Repository:** https://github.com/glitter-node/data-toolkit

**Version:** 1.0.0  
**Release type:** First stable release  
**Platform:** Linux, Windows, macOS  
**Python:** 3.11 or later  
**License:** MIT

The application is designed for local or self-hosted deployment. It does not require Docker, Redis, MariaDB, or an external cloud service for its core functionality.

## Features

### Data conversion

Convert structured data between the following formats:

- CSV
- JSON
- XML
- YAML
- XLSX

Supported conversion options include column selection, column renaming, filtering, sorting, and deduplication.

The conversion engine operates on flat tabular data. Nested structured values are intentionally rejected rather than silently flattened.

### Data preview

Inspect uploaded files before processing.

- File-by-file preview
- Column inspection
- Paginated rows
- Configurable preview page size
- XLSX worksheet selection
- Selected file names and sizes
- Individual file removal

Preview errors are displayed separately from the file-list status. The Workspace provides a concise file status, while the Results panel presents detailed errors and available location information.

### Data validation

Validate uploaded datasets using required-column rules and optional JSON field constraints.

Validation capabilities include:

- Required-column checks
- Field constraint validation
- Missing-value detection through supported rules
- Validation issue details
- Downloadable JSON and CSV reports

See [Validation documentation](docs/V0.1.9_VALIDATION.md).

### Batch processing

Process multiple supported files through the browser.

Batch conversion provides a downloadable ZIP archive containing converted outputs and a `report.json` processing report.

Batch processing may buffer output in memory and is subject to host resource limits.

### Background jobs

Background conversion is supported through asynchronous job endpoints.

- SQLite-backed job metadata
- Job status inspection
- Token-protected job access
- Result downloads
- Cancellation requests
- Result retention and cleanup

Queued or running jobs are not automatically resumed after an application restart. Running thread-based conversions cannot be forcibly interrupted; cancellation prevents result publication when the cancellation state is observed.

Job concurrency is limited by an in-process semaphore rather than operating-system-level resource isolation.

See [Background jobs](docs/V0.1.9_JOBS.md).

## Web interface

The application includes four primary workflows:

| Workflow    | Description                                                       |
| ----------- | ----------------------------------------------------------------- |
| Convert     | Convert files and apply transformation options                    |
| Validate    | Validate data and download issue reports                          |
| Batch       | Process multiple files and download results                       |
| Job history | Inspect known background jobs using their job ID and access token |

The interface provides a responsive Workspace and Results layout, file selection through drag-and-drop or the native file picker, accessible controls, and a Back to top button.

### Themes

Four appearance modes are supported:

- System
- Light
- Dark
- Warm

The interface uses layered surfaces and soft depth effects defined in `app/static/css/soft3d.css`.

Theme selection is persisted in the browser.

See [Themes](docs/THEMES.md).

### Internationalization

Supported interface languages:

- Korean (`ko`) — default and fallback
- English (`en`)
- Japanese (`ja`)
- Simplified Chinese (`zh-CN`)

The selected language is persisted using the browser storage key `dataToolkit.locale`.

Translation resources and key parity requirements are described in [Internationalization](docs/I18N.md).

## Requirements

- Python 3.11 or later
- Python `sqlite3` standard library
- Dependencies listed in `requirements.txt`
- A supported modern web browser

The application uses SQLite for background job metadata.

Dependency compatibility should be verified in the target environment before production deployment.

`requirements.txt` remains the portable installation input. The checked local
environment also has a Linux-only CPython 3.11 resolution record in
[`requirements-linux-py311.lock`](requirements-linux-py311.lock); it is not a
universal lock file for Windows or macOS. See
[`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md) for the corresponding
dependency inventory and its verification limits.

## Installation

### Linux

```bash
git clone https://github.com/glitter-node/data-toolkit.git
cd data-toolkit
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8015 --workers 1 --lifespan on
```

### Windows PowerShell

Run the following commands from the extracted project directory:

```powershell
py -3.11 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8015 --workers 1 --lifespan on
```

### macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8015 --workers 1 --lifespan on
```

### Access the application

Open:

http://127.0.0.1:8015/

Health check:

```bash
curl -fsS http://127.0.0.1:8015/healthz
```

The `.env` file is optional. `APP_PORT` does not automatically configure Uvicorn's listening port.

## Updating an existing installation

Before upgrading:

1. Back up the existing application directory.
2. Preserve `.env`, `venv/` or `.venv/`, and `data/`.
3. Stop the running Uvicorn service.
4. Extract the updated source files into the existing project directory.
5. Install or update Python dependencies as required.
6. Restart the application.
7. Verify `/healthz`, the browser interface, and primary workflows.

Do not overwrite or remove persistent job data during a source update.

The existing development alias `uvi8015` remains compatible when configured for the same application entry point and port.

## API

The application exposes endpoints for inspection, preview, conversion, transformation, validation, batch processing, and background jobs.

| Endpoint                     | Purpose                         |
| ---------------------------- | ------------------------------- |
| `GET /api/formats`           | Supported format names          |
| `GET /healthz`               | Application health              |
| `POST /api/inspect`          | Inspect uploaded data           |
| `POST /api/preview`          | Preview uploaded data           |
| `POST /api/convert`          | Convert structured data         |
| `POST /api/transform`        | Apply transformation operations |
| `POST /api/validate`         | Validate uploaded data          |
| `POST /api/validate/report`  | Download JSON or CSV issue report |
| `POST /api/batch`            | Process multiple files          |
| `POST /api/jobs`             | Create a background job         |
| `GET /api/jobs/{id}`         | Inspect a token-authorized job  |
| `POST /api/jobs/{id}/cancel` | Request job cancellation        |
| `GET /api/jobs/{id}/events`  | Stream token-authorized status  |
| `GET /api/jobs/{id}/download`| Download a completed result    |
| `DELETE /api/jobs/{id}`      | Delete a finished job           |

Additional job status, event-stream, and download operations are described in the API documentation.

The conversion endpoint accepts a JSON `options` form field for supported transformation settings.

See [API documentation](docs/API.md).

## Data handling and limitations

Data Toolkit is intended for flat tabular data processing.

Important limitations include:

- Nested objects and arrays are not automatically flattened.
- XML input supports simple row-based documents such as `<rows><row><field>value</field></row></rows>`.
- XML element names must be valid identifiers.
- CSV input is decoded as UTF-8 with an optional BOM.
- XLSX processing uses worksheet cached values and does not preserve formulas or styling.
- Cross-format conversion is not guaranteed to be lossless.
- Background jobs do not automatically resume after application restarts.
- Running thread-based tasks cannot be forcibly interrupted.
- Batch output may be buffered in memory.
- There is no operating-system-level CPU or memory sandbox.
- Job history does not provide an unauthenticated global listing.

Application-generated job results are stored under `data/output`.

## Security

The application uses a strict same-origin Content Security Policy and security response headers.

The main application interface keeps executable JavaScript in separate static files and does not require inline application scripts or styles.

FastAPI documentation routes use a separate CSP configuration with dynamically computed inline-script SHA-256 hashes.

Background job access is protected through job-specific access tokens.

**The application does not provide general user-account authentication.**

For deployment on untrusted networks, configure additional access controls and resource protections.

Recommended deployment safeguards include:

- HTTPS
- Reverse-proxy request size limits
- Authentication or network-level access restrictions
- Appropriate request and concurrency limits
- Protected application data directories
- Secure handling of job access tokens
- Controlled log retention

Job access tokens may appear in event-stream or download URLs and can be recorded in reverse-proxy logs.

See [Security documentation](docs/SECURITY.md).

## Reverse proxy

A reference self-hosted deployment can expose the application through an HTTPS reverse proxy.

Example mapping:

| Public endpoint                   | Local upstream          |
| --------------------------------- | ----------------------- |
| `https://data-toolkit.glitter.kr` | `http://127.0.0.1:8015` |

This mapping is an example of the intended deployment configuration and is not an independent verification of a live deployment.

The application can also be used entirely through localhost without a reverse proxy.

## Static assets and search-engine files

The application serves its favicon, `robots.txt`, and `sitemap.xml` from `app/static/` at root URLs.

See [Search engine files](docs/SEARCH_ENGINE_FILES.md).

## Testing

Run the automated test suite:

```bash
python -m pytest -v
```

Check Python module compilation:

```bash
python -m compileall -q app
```

The automated suite covers conversion, validation, preview, background jobs, internationalization, security headers, UI stability, themes, and related regression cases.

A passing test suite does not constitute a comprehensive security audit.

## Documentation

| Document                                           | Purpose                                             |
| -------------------------------------------------- | --------------------------------------------------- |
| [AGENTS.md](AGENTS.md)                             | Project and development guidance                    |
| [Architecture](docs/ARCHITECTURE.md)               | Application structure                               |
| [API](docs/API.md)                                 | API usage and contracts                             |
| [Security](docs/SECURITY.md)                       | Security architecture and deployment considerations |
| [AI installation guide](docs/AI_INSTALL_GUIDE.md)  | Reusable installation workflow for coding agents    |
| [Changelog](CHANGELOG.md)                          | Verified release and maintenance history            |
| [Themes](docs/THEMES.md)                           | Theme palettes and UI appearance                    |
| [Internationalization](docs/I18N.md)               | Localization and translation requirements           |
| [Validation](docs/V0.1.9_VALIDATION.md)            | Validation features                                 |
| [Background jobs](docs/V0.1.9_JOBS.md)             | Job processing                                      |
| [Preview](docs/V0.1.6_PREVIEW.md)                  | Preview capabilities                                |
| [Windows Auto-Start](docs/WINDOWS_AUTOSTART.md)    | Windows startup configuration                       |
| [Stability checks](docs/STABILITY_V019.md)         | v0.1.9 stabilization history                        |
| [Search engine files](docs/SEARCH_ENGINE_FILES.md) | Public static assets                                |

Historical version numbers in documentation filenames identify the development stage when those features were introduced. They do not indicate the current application version.

## Release history

### v1.0.0 — First stable release

Version 1.0.0 promotes the stabilized v0.1.9 application baseline to the first stable release.

The release includes structured-data conversion, validation, batch processing, previews, SQLite-backed background jobs, internationalization, multiple themes, and security-header improvements.

The v1.0.0 release is intended to preserve existing v0.1.9 API behavior and stored job metadata without introducing a breaking migration.

### Earlier development versions

Versions v0.1.0 through v0.1.9 introduced the application's initial conversion engine, browser workflows, preview capabilities, validation rules, background processing, interface refinements, and stability improvements.

Detailed historical release entries should be maintained in `CHANGELOG.md`.

## License

Original project source is distributed under the **MIT License**.

Third-party dependencies retain their respective licenses.

See [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

---

**Data Toolkit v1.0.0 — Self-hosted structured-data processing with Python, FastAPI, and Uvicorn.**
