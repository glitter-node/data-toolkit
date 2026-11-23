# Security

Repository: https://github.com/glitter-node/data-toolkit

## Deployment boundary

The default deployment binds Uvicorn to `127.0.0.1:8015` and is intended for a trusted local user. The application has no general user-account authentication. A reverse proxy may provide HTTPS, authentication, request limits, and network policy, but those controls are outside this application and must be configured separately. Do not expose the application directly to the public internet.

Job access tokens are scoped to an individual background job. They are not equivalent to application authentication. Status, event, download, and deletion operations require the token; the download and event-stream implementations also accept a token query parameter, which can be recorded in browser history or proxy logs. Protect and redact these values.

## Upload and resource controls

Application-level controls include supported-extension and safe-filename checks, rejection of empty files, a per-file upload limit, batch file-count and total-size limits, row and column limits, a two-job in-process semaphore, and bounded validation issue storage. Batch and conversion data may be buffered in memory. There is no operating-system CPU/memory sandbox, container isolation, per-user quota, or memory isolation guarantee.

XML input uses `defusedxml`; YAML uses `safe_load`; XLSX uses cached worksheet values and does not execute formulas. Spreadsheet formula-like output text is escaped. Large or adversarial inputs can still consume host resources, so use reverse-proxy limits and a trusted deployment boundary. Schema patterns are length-limited and reject several high-risk constructs, but this is not a substitute for a full resource-exhaustion assessment.

Cancellation is cooperative. A running thread-based conversion cannot be forcibly interrupted. Cancelled jobs do not publish results when cancellation is observed. Queued or running jobs are marked failed during startup recovery rather than resumed. Completed, failed, and cancelled job metadata and output are cleaned up at startup after the configured retention period; cleanup is not a continuously scheduled task.

## Content Security Policy and headers

The main application uses the `MAIN_CSP` deny-by-default policy in `app/security.py`: same-origin scripts, styles, images, fonts, and connections are allowed; inline scripts, inline styles, event-handler attributes, `eval`, framing, workers, and media are disallowed. The middleware also sets `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, `Cross-Origin-Opener-Policy`, and `Cross-Origin-Resource-Policy`.

FastAPI documentation routes (`/docs`, `/redoc`, and `/docs/oauth2-redirect`) use a separate dynamically calculated CSP. It permits the generated script hashes, documentation CDN assets, and documentation-only inline CSS required by FastAPI's generated pages. Do not apply the main application CSP indiscriminately to these routes. Reverse proxies must avoid adding a conflicting second CSP policy.

The application does not set HSTS; HTTPS and HSTS remain reverse-proxy responsibilities. No independent security audit or public-deployment certification is claimed.

## Operational guidance

For localhost use, keep the default binding and run one Uvicorn worker. For reverse-proxy use, add HTTPS, authentication or network access controls, request and upload limits, suitable concurrency/resource controls, protected `data/` permissions, secure token handling, and log redaction. Preserve `.env`, SQLite files, and stored outputs during upgrades. These recommendations do not represent a completed production deployment test.
