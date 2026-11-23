# Installing and Running Data Toolkit with an AI Agent

I would like to install the following GitHub project on my local computer and run it locally.

**GitHub Repository:** https://github.com/glitter-node/data-toolkit

**Project:** Data Toolkit v1.0.0 — Stable Release

## 1. Environment inspection

First, check my computer's operating system, system architecture, Python installation status and version, existing development environment, and the tools available for installation.

Read the repository's `README.md` and `AGENTS.md`, along with the relevant operating-system installation and startup documentation, before changing anything. Check `requirements.txt`, `.env.example` if present, the application startup code, configuration modules, and the `docs/` directory so that the installation procedure matches the actual project.

Confirm the application's entry point, supported Python version, runtime dependencies, configuration requirements, persistent storage locations, and documented startup commands.

## 2. Source and dependency verification

Confirm the source version, entry point, supported formats, configuration keys, persistent paths, and dependency constraints before making changes.

## 3. Local installation

Based on the detected environment, clone or download Data Toolkit into the selected installation directory, create a dedicated Python virtual environment, and install the dependencies using `requirements.txt`.

Do not add Docker, Nginx, Apache, MariaDB, Redis, or a separate database server for a local installation unless I explicitly request a deployment that requires them.

Prepare the environment file from `.env.example` only if that file exists and the application requires it. Preserve any existing `.env` configuration. Do not overwrite existing environment variables or secrets.

Keep the default local binding and run Data Toolkit with one Uvicorn worker at `127.0.0.1:8015`. On Linux or macOS, the reference command is:

```bash
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8015 --workers 1 --lifespan on
```

Use the equivalent `.venv\Scripts\python.exe` command on Windows and open `http://127.0.0.1:8015/` in a web browser.

Use a single Uvicorn worker unless the repository explicitly documents and validates another configuration for SQLite-backed background jobs.

## 4. Basic application startup and functional verification

Verify the initial page, the `/healthz` response, and representative upload-based data processing using isolated temporary test files.

Confirm that data inspection, conversion, validation, preview, batch processing, and background-job operations work without changing or overwriting existing user files.

After the application works, review the available automatic-start mechanisms for the detected operating system.

On Windows, follow `docs/WINDOWS_AUTOSTART.md` if it exists and matches the current application.

On Linux or macOS, use an official project procedure if one exists. Do not invent a system-wide service, scheduled task, or startup configuration and do not modify system startup settings without my confirmation.

If automatic startup cannot be configured safely, provide the exact manual startup command and explain what remains to be configured.

## Requirements and Precautions

- Install Data Toolkit as a local, self-hosted Python application.
- Use Python 3.11 or later, subject to compatibility with the dependencies declared in `requirements.txt`.
- Preserve the existing Python + FastAPI + Uvicorn architecture.
- Use the documented application entry point `app.main:app`.
- Keep the default binding address `127.0.0.1` and port `8015`.
- Do not change the binding address to `0.0.0.0` or expose the application to the internet without my explicit approval and appropriate network security controls.
- Do not delete or overwrite existing project files, user documents, `.env` files, SQLite databases, generated results, or documentation without my permission.
- Use a dedicated Python virtual environment so installation does not modify unrelated Python projects or the system interpreter.
- Preserve existing `venv/`, `.venv/`, `.env`, and `data/` directories when updating an existing installation.
- Follow the installation and startup procedure appropriate for the detected operating system and architecture.
- Do not assume that `APP_PORT` automatically configures Uvicorn's listening port.
- Do not add mandatory external processing services, message brokers, or database servers.
- Do not claim unsupported operating-system behavior.
- If installation or startup fails, analyze the actual error and provide a verifiable fix.
- Do not silently retry uncertain filesystem writes, dependency changes, or configuration modifications.
- Ask for confirmation before using administrator privileges or changing system-wide services, firewall rules, startup settings, or existing system configuration.

## Application Configuration

Inspect the actual configuration implementation before creating or modifying environment variables.

Check whether `.env.example` exists and whether the application requires any additional configuration.

Do not invent configuration keys or assume that settings used by other projects are supported by Data Toolkit.

Keep local application access restricted to the loopback interface.

Identify the configured SQLite database location and background-job output directory from the source.

Preserve existing persistent data and job metadata.

Do not reset the database or delete stored job results during installation or upgrades.

Verify the application's upload-size limits, concurrency controls, job retention settings, and temporary-file handling before testing resource-intensive operations.

Do not increase limits without my approval.

## Safe Data Processing Verification

Use only isolated temporary directories and disposable test files for functional verification.

Do not process existing personal documents or production datasets without my explicit approval.

Create small representative datasets containing flat tabular records.

Include test cases for:

- CSV
- JSON
- XML
- YAML
- XLSX

Verify that the application accepts supported formats and rejects unsupported or malformed input safely.

### Inspection and preview

Confirm that:

- File upload works through the browser or documented API.
- File names and sizes are displayed correctly.
- Column inspection returns expected information.
- Preview pagination works.
- XLSX worksheet selection works where applicable.
- Invalid JSON produces an appropriate validation error.
- Unsupported nested structures are rejected according to the documented processing rules.
- Preview errors are displayed without misleading success messages.

### Conversion and transformation

Verify representative conversions between supported formats.

Confirm that:

- Output files are generated correctly.
- Column selection works.
- Column renaming works.
- Filtering works.
- Sorting works.
- Deduplication works.
- Downloaded results contain the expected records.

Do not assume that conversion between all formats is lossless.

Do not modify original test files in place.

### Validation

Verify the existing validation workflow using disposable datasets.

Test:

- Required-column validation
- Supported JSON field constraints
- Valid input
- Missing required values or fields
- Invalid field values
- JSON and CSV validation report downloads

Confirm that validation failures are distinguishable from server errors.

### Batch processing

Use multiple small disposable input files.

Confirm that:

- Batch upload succeeds.
- Supported files are processed.
- The resulting ZIP archive is downloadable.
- The archive contains the expected converted outputs.
- `report.json` records processing results.
- Invalid files produce appropriate file-level failures.

Do not run large batch jobs during initial installation verification.

### Background jobs

Verify the documented background-job workflow.

Confirm that:

- A job can be created.
- The job status can be inspected.
- The job access token is required where documented.
- Completed results can be downloaded.
- Unauthorized result access is rejected.
- Cancellation requests follow the documented cooperative cancellation behavior.
- Temporary and expired results follow the configured cleanup policy.

Do not attempt to forcibly terminate active conversion threads.

Do not assume queued or running jobs will resume after an application restart.

Do not expose access tokens in public logs or reports.

## 5. Interface verification

Verify the existing interface without changing its implementation.

Supported languages:

- Korean (`ko`) — default and fallback
- English (`en`)
- Japanese (`ja`)
- Simplified Chinese (`zh-CN`)

Confirm that the application initially displays Korean when no prior locale preference is stored.

Verify that changing the language updates visible labels, workflow messages, and supported error messages.

Confirm that the selected language persists after a page reload.

Do not treat an existing browser locale preference as a failure of the default-language configuration.

Verify the supported appearance modes:

- System
- Light
- Dark
- Warm

Confirm that theme selection persists and that controls remain readable and accessible.

Check responsive layout behavior at representative desktop and mobile viewport widths.

Verify that language and theme controls do not overlap or break into individual characters.

## 6. Security verification

Preserve the application's existing security middleware and Content Security Policy.

Inspect `app/security.py` and the actual application response headers.

Confirm that the main application uses its documented strict same-origin CSP.

Do not add inline scripts, inline styles, inline event handlers, or unnecessary external dependencies.

FastAPI documentation routes may use a separate CSP configuration with dynamically computed script hashes.

Do not replace or weaken either CSP without reviewing the actual source and browser console results.

If a reverse proxy is configured, check for duplicate or conflicting CSP headers.

Verify the existing upload filename restrictions, supported extensions, empty-file handling, upload-size limits, and protected result downloads.

The application does not provide general user-account authentication.

Do not expose the local installation to untrusted networks without additional authentication and resource controls.

Do not describe background-job access tokens as general user authentication.

## Automated testing

After installing the dependencies, run the repository's automated tests:

```bash
python -m pytest -v
```

Check Python module compilation:

```bash
python -m compileall -q app
```

If Node.js is already installed and the repository contains JavaScript files requiring syntax verification, run the appropriate checks without installing Node.js solely for this purpose unless necessary and approved.

Do not modify or weaken tests merely to obtain a passing result.

If tests fail, report the actual failure and determine whether the cause is an environment dependency, a configuration problem, or an application defect.

Clearly distinguish automated test results from browser verification and production security assessment.

## 7. Optional automatic startup

Configure automatic startup only after the application has passed the required installation and functional checks.

### Windows

Read `docs/WINDOWS_AUTOSTART.md` before changing startup settings.

If the documented procedure uses Windows Task Scheduler, follow that procedure and preserve existing scheduled tasks.

Request confirmation before creating or modifying a scheduled task.

Do not configure the application to run with unnecessary administrator privileges.

### Linux

Check whether the repository provides an official startup or service procedure.

If no documented procedure exists, do not invent or install a system-wide service without my confirmation.

Provide the verified manual startup command instead.

### macOS

Check for documented macOS startup support.

Do not create LaunchAgents, LaunchDaemons, or other persistent startup configuration without my confirmation.

If no supported procedure exists, provide the manual startup command.

## 8. Troubleshooting and final installation report

If the application does not start, inspect the actual error before making changes.

Check:

- Python interpreter version
- Virtual environment activation
- Installed dependencies
- Application import errors
- Missing configuration
- SQLite availability
- Persistent storage permissions
- Port `8015` conflicts
- Uvicorn startup logs
- File upload and processing errors
- Browser console and network requests

Do not change the application port automatically to work around a conflict.

Do not delete existing SQLite data or generated files to resolve an error.

Do not silently change package versions or application code.

Explain the proposed correction and request approval when it affects existing configuration or data.

## Post-Installation Verification

After completing the installation, provide a numbered summary containing:

1. **Operating system and architecture:** Detected operating system, version, and processor architecture.
2. **Installation directory:** Actual Data Toolkit project location.
3. **Python environment:** Python version and dedicated virtual environment path.
4. **Application URL:** `http://127.0.0.1:8015/`.
5. **Application verification:** Browser accessibility, `/healthz` response, and application version.
6. **Data processing:** Inspection, preview, conversion, validation, batch processing, and result downloads using temporary files.
7. **Background jobs:** Job creation, status, token authorization, cancellation behavior where safely testable, and result download.
8. **UI verification:** Korean default locale, language switching, theme selection, and responsive layout.
9. **Security verification:** CSP, security headers, upload restrictions, and local-only network binding.
10. **Automatic startup:** Configured mechanism, verification status, or remaining manual steps.
11. **Automated tests:** Actual test counts, failures, skipped tests, and any unresolved issues.
12. **Remaining verification:** Steps that could not be tested and the reasons.

Clearly distinguish successfully verified steps from unverified or incomplete steps.

Base all installation, configuration, troubleshooting, and startup guidance on the repository's actual source and documentation.

Do not claim that a service is running, an endpoint is accessible, or a test has passed unless it has been verified.

---

**Data Toolkit v1.0.0 — Local-first, self-hosted structured-data processing with Python, FastAPI, and Uvicorn.**
