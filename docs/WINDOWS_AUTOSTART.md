# Windows Auto-Start

Repository: https://github.com/glitter-node/data-toolkit

Optional current-user Task Scheduler setup for Windows 10/11. This is documentation, not an automatically registered task. No administrator elevation, WSL2, Docker, or machine-wide PowerShell policy change is required.

## Verify local installation

In PowerShell, change to the extracted project directory and verify:

```powershell
Set-Location (Read-Host "Enter the full path to the Data Toolkit project")
Test-Path .\app\main.py
Test-Path .\requirements.txt
Test-Path .\.venv\Scripts\python.exe
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8015 --workers 1 --lifespan on
```

Open http://127.0.0.1:8015/ and http://127.0.0.1:8015/healthz. Stop the foreground process before configuring a task.

## Task Scheduler

Create a task named `Data Toolkit - Current User` with trigger **At log on** for the current user. Set **Run only when user is logged on**, without highest privileges. Action **Start a program**:

- Program: absolute path to `.venv\Scripts\python.exe`
- Arguments: `-m uvicorn app.main:app --host 127.0.0.1 --port 8015 --workers 1 --lifespan on`
- Start in: absolute project root, without quotes

Set **Do not start a new instance**, disable the maximum runtime limit, and optionally retry failed starts up to three times. This starts after user sign-in, not before login. It does not detect an unrelated process already bound to port 8015. Never overwrite an existing task or `.env` automatically.

Keep the single-worker setting because job metadata and results use the local SQLite-backed, in-process job implementation. This document only describes an optional current-user task; it does not authorize or perform task creation.

## Diagnose and remove

Check Task Scheduler History and verify port ownership if startup fails. To disable auto-start, disable or delete the named task in Task Scheduler; do not delete project files, `.env`, or `data/`.
