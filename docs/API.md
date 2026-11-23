# API

Repository: https://github.com/glitter-node/data-toolkit

The API accepts uploaded files as `multipart/form-data`. Supported input and output format names are `csv`, `json`, `xml`, `yaml`, and `xlsx`. The service does not implement general user authentication. Background-job endpoints use the job-specific token returned when the job is created.

## Service endpoints

### `GET /healthz`

Returns `{"status":"ok","version":"1.0.0"}`.

### `GET /api/formats`

Returns `{"formats":["csv","json","xml","yaml","xlsx"]}`.

## Upload and processing endpoints

All upload endpoints validate the filename, supported extension, non-empty content, and configured per-file size limit. Invalid input, malformed options, unsupported formats, and parser/validation errors normally return `422` with a JSON `detail` message. Oversized files or batches return `413`.

### `POST /api/inspect` and `POST /api/preview`

Form fields:

- `file`: required upload.
- `page`: optional integer, default `1`, range `1`–`100000`.
- `page_size`: optional integer, default `25`, range `1`–`100`.
- `sheet`: optional XLSX worksheet name. An unknown worksheet is rejected.

Both routes return the same JSON structure containing `format`, `columns`, `row_count`, `preview`, `page`, `page_size`, `page_count`, `sheets`, `sheet`, and `file_size`. XLSX uses cached worksheet values and supports explicit worksheet selection.

### `POST /api/convert` and `POST /api/transform`

Form fields:

- `file`: required upload.
- `output_format`: optional output format, default `json`.
- `options`: optional JSON object, default `{}`.

The two routes have the same behavior and return converted bytes as an attachment named `result.<output_format>`, with `Cache-Control: no-store`.

`options` supports column selection, renaming, filtering, sorting, and deduplication:

```json
{"columns":["id","name"],"rename":{"name":"full_name"},"filters":[{"column":"id","operator":"eq","value":"1"}],"sort":{"column":"id","descending":false},"deduplicate":true}
```

Filter operators are `eq`, `ne`, `contains`, `empty`, and `not_empty`. The browser interface exposes these controls in the Convert workflow.

### `POST /api/validate`

Form fields:

- `file`: required upload.
- `required`: JSON array of required column names, default `[]`.
- `schema`: JSON validation schema, default `{}`. This is the public alias for the implementation parameter `validation_schema`.

The response contains `valid`, `columns`, `row_count`, `issues`, `issue_count`, `truncated`, `summary`, and `schema_fields`. Supported schema rules include field types, required/unique/nullable flags, length and numeric bounds, enumerations, and bounded regular-expression patterns. Validation issues are returned in the response and are distinct from transport failures.

### `POST /api/validate/report`

Accepts the same `file`, `required`, and `schema` fields as `/api/validate`, plus `report_format`, which must be `json` or `csv` and defaults to `json`. Returns an attachment named `validation-report.<report_format>` with `Cache-Control: no-store`.

### `POST /api/batch`

Form fields are repeated `files`, optional `output_format` (default `json`), and optional JSON `options`. The configured file-count and total-size limits apply. The response is a ZIP attachment named `data-toolkit-batch.zip`; it contains successful outputs and `report.json`. File-level failures are recorded in the report rather than aborting the whole archive.

## Background jobs

### `POST /api/jobs`

Accepts `file`, `output_format`, and `options` with the same meanings as `/api/convert`. Returns `202` and a job token:

```json
{"id":"<job-id>","token":"<job-token>","state":"queued"}
```

Store the token securely. It is required for subsequent job operations.

### `GET /api/jobs/{job_id}`

Requires the `X-Job-Token` header. Unauthorized ID/token pairs return `404`. Authorized responses include `state`, `progress`, `filename`, `result_size`, `error`, timestamps, `expires_at`, and `download_available`.

### `POST /api/jobs/{job_id}/cancel`

Requires `X-Job-Token`. Queued or running jobs are cooperatively cancelled. A running worker thread cannot be forcibly interrupted; a result is not published when cancellation is observed.

### `GET /api/jobs/{job_id}/events`

Requires the job token as the `token` query parameter. Returns a short-lived Server-Sent Events stream with `status` events containing job metadata. It ends at `completed`, `failed`, or `cancelled`, or after its polling window.

### `GET /api/jobs/{job_id}/download`

Requires `X-Job-Token` or the `token` query parameter. Returns the completed result as an attachment. It returns `409` until completion and `410` when the result has expired or is missing; unauthorized ID/token pairs return `404`.

### `DELETE /api/jobs/{job_id}`

Requires `X-Job-Token`. Completed, failed, or cancelled jobs can be deleted with their stored result. Active jobs return `409` and must be cancelled first; unauthorized ID/token pairs return `404`.

Job metadata is stored in `data/jobs.sqlite3` and results in `data/output`. Startup performs interrupted-job recovery and retention cleanup. Jobs are not automatically resumed after restart, and no global unauthenticated job listing exists.
