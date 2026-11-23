# Architecture

Repository: https://github.com/glitter-node/data-toolkit

Browser HTML, CSS, and JavaScript are served by FastAPI/Uvicorn. `/api/inspect` and `/api/convert` parse uploaded bytes and return preview or conversion results. The conversion engine uses CSV/JSON standard libraries, defusedxml, PyYAML safe_load, and openpyxl. A flat row model is shared across formats; nested structures are rejected.

SQLite `data/jobs.sqlite3` stores job states and token hashes. `/api/jobs` executes conversion in a process-local asyncio task; completed outputs are stored under `data/output`. An in-process semaphore limits active jobs, cancellation is cooperative, and startup changes interrupted jobs to failed and removes expired terminal jobs and results. There is no operating-system worker isolation or automatic job resumption after restart.

Default localhost port: 8015. The application entry point is `app.main:app`; Uvicorn should run with one worker. The `.env` `APP_PORT` setting is application configuration metadata and does not configure Uvicorn's listening port. Reverse proxy target: `127.0.0.1:8015`.
