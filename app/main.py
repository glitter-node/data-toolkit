import asyncio
import json
import re
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, Response, FileResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html, get_swagger_ui_oauth2_redirect_html
from app.security import SecurityHeadersMiddleware, docs_csp
from app.asset_version import version_assets
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse
from app.core.config import settings
from app.core import jobs
from app.services.engine import DataError
from app.services.validation import report_bytes
from app.services.operations import inspect_data, validate_data, convert_data, batch_data

TASKS = {}
SEMAPHORE = asyncio.Semaphore(settings.max_concurrent_jobs)

async def read_file(file):
    limit = settings.max_upload_mb * 1024 * 1024
    data = await file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(413, "File too large")
    if not data:
        raise HTTPException(422, "Empty files are not supported")
    return data

def validate_filename(filename):
    name = filename or ""
    if not name or len(name) > 255 or any(ord(char) < 32 for char in name) or "/" in name or "\\" in name:
        raise HTTPException(422, "Invalid filename")
    if not re.fullmatch(r"[a-zA-Z0-9]+", name.rsplit(".", 1)[-1]) or name.rsplit(".", 1)[-1].lower() not in {"csv", "json", "xml", "yaml", "yml", "xlsx"}:
        raise HTTPException(422, "Unsupported file type")
    return name

async def validated_file(file):
    name = validate_filename(file.filename)
    return await read_file(file), name

def options_json(value):
    try:
        parsed = json.loads(value)
        if not isinstance(parsed, dict):
            raise ValueError("Options must be an object")
        return parsed
    except (ValueError, TypeError) as exc:
        raise HTTPException(422, str(exc)) from exc

def respond_error(exc):
    raise HTTPException(422, str(exc)[:500]) from exc

@asynccontextmanager
async def lifespan(app):
    jobs.recover()
    jobs.cleanup()
    yield
    tasks = list(TASKS.values())
    for task in tasks:
        task.cancel()
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan, docs_url=None, redoc_url=None)
app.add_middleware(SecurityHeadersMiddleware)

@app.get("/docs", include_in_schema=False)
async def swagger_docs():
    if app.openapi_url is None:
        return Response(status_code=404)
    response = get_swagger_ui_html(openapi_url=app.openapi_url, title=f"{app.title} - Swagger UI", oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url, init_oauth=app.swagger_ui_init_oauth, swagger_ui_parameters=app.swagger_ui_parameters)
    response.headers["Content-Security-Policy"] = docs_csp(response.body.decode("utf-8"))
    return response

@app.get("/redoc", include_in_schema=False)
async def redoc_docs():
    if app.openapi_url is None:
        return Response(status_code=404)
    response = get_redoc_html(openapi_url=app.openapi_url, title=f"{app.title} - ReDoc")
    response.headers["Content-Security-Policy"] = docs_csp(response.body.decode("utf-8"))
    return response

@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def swagger_oauth_redirect():
    response = get_swagger_ui_oauth2_redirect_html()
    response.headers["Content-Security-Policy"] = docs_csp(response.body.decode("utf-8"))
    return response

app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    html = (Path(__file__).parent / "templates" / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(version_assets(html), headers={"Cache-Control": "no-cache, must-revalidate"})

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(Path(__file__).parent / "static" / "favicon.ico", media_type="image/x-icon")

@app.get("/robots.txt", include_in_schema=False)
async def robots():
    return FileResponse(Path(__file__).parent / "static" / "robots.txt", media_type="text/plain; charset=utf-8")

@app.get("/sitemap.xml", include_in_schema=False)
async def sitemap():
    return FileResponse(Path(__file__).parent / "static" / "sitemap.xml", media_type="application/xml")

@app.get("/healthz")
async def health():
    return {"status": "ok", "version": "1.0.0"}

@app.get("/api/formats")
async def formats():
    return {"formats": ["csv", "json", "xml", "yaml", "xlsx"]}

@app.post("/api/inspect")
async def inspect(file: UploadFile = File(...), page: int = Form(1), page_size: int = Form(25), sheet: str = Form("")):
    try:
        return await asyncio.to_thread(inspect_data, *(await validated_file(file)), settings, page, page_size, sheet or None)
    except (ValueError, TypeError, UnicodeError, KeyError, OSError) as exc:
        respond_error(exc)

@app.post("/api/preview")
async def preview(file: UploadFile = File(...), page: int = Form(1), page_size: int = Form(25), sheet: str = Form("")):
    return await inspect(file, page, page_size, sheet)

@app.post("/api/validate")
async def validate(file: UploadFile = File(...), required: str = Form("[]"), validation_schema: str = Form("{}", alias="schema")):
    try:
        return await asyncio.to_thread(validate_data, *(await validated_file(file)), settings, json.loads(required), json.loads(validation_schema))
    except (ValueError, TypeError, UnicodeError, KeyError, OSError) as exc:
        respond_error(exc)

@app.post("/api/validate/report")
async def validation_report(file: UploadFile = File(...), required: str = Form("[]"), validation_schema: str = Form("{}", alias="schema"), report_format: str = Form("json")):
    try:
        result = await asyncio.to_thread(validate_data, *(await validated_file(file)), settings, json.loads(required), json.loads(validation_schema))
        output = report_bytes(result, report_format)
        return Response(output, media_type="application/octet-stream", headers={"Content-Disposition": f'attachment; filename="validation-report.{report_format}"', "Cache-Control": "no-store"})
    except (ValueError, TypeError, UnicodeError, KeyError, OSError) as exc:
        respond_error(exc)

@app.post("/api/convert")
async def convert(file: UploadFile = File(...), output_format: str = Form("json"), options: str = Form("{}")):
    try:
        result = await asyncio.to_thread(convert_data, *(await validated_file(file)), output_format, options_json(options), settings)
        return Response(result, media_type="application/octet-stream", headers={"Content-Disposition": f'attachment; filename="result.{output_format}"', "Cache-Control": "no-store"})
    except (ValueError, TypeError, UnicodeError, KeyError, OSError) as exc:
        respond_error(exc)

@app.post("/api/transform")
async def transform(file: UploadFile = File(...), output_format: str = Form("json"), options: str = Form("{}")):
    return await convert(file, output_format, options)

@app.post("/api/batch")
async def batch(files: list[UploadFile] = File(...), output_format: str = Form("json"), options: str = Form("{}")):
    if not files or len(files) > settings.max_batch_files:
        raise HTTPException(413, "Too many files")
    payload = []
    total = 0
    for file in files:
        data, name = await validated_file(file)
        total += len(data)
        if total > settings.max_batch_total_mb * 1024 * 1024:
            raise HTTPException(413, "Batch too large")
        payload.append((name, data))
    try:
        output = await asyncio.to_thread(batch_data, payload, output_format, options_json(options), settings)
        return Response(output, media_type="application/zip", headers={"Content-Disposition": 'attachment; filename="data-toolkit-batch.zip"', "Cache-Control": "no-store"})
    except (ValueError, TypeError, UnicodeError, KeyError, OSError) as exc:
        respond_error(exc)

@app.post("/api/jobs", status_code=202)
async def create_job(file: UploadFile = File(...), output_format: str = Form("json"), options: str = Form("{}")):
    if output_format not in ("csv", "json", "xml", "yaml", "xlsx"):
        raise HTTPException(422, "Unsupported format")
    parsed = options_json(options)
    data, name = await validated_file(file)
    job_id, token = jobs.create("result." + output_format)
    async def worker():
        try:
            async with SEMAPHORE:
                if not jobs.transition(job_id, "queued", "running"):
                    return
                jobs.progress(job_id, 25)
                result = await asyncio.to_thread(convert_data, data, name, output_format, parsed, settings)
                folder = settings.data_dir / "output"
                folder.mkdir(parents=True, exist_ok=True)
                jobs.progress(job_id, 85)
                temporary = folder / (job_id + ".tmp")
                destination = folder / (job_id + ".bin")
                try:
                    temporary.write_bytes(result)
                    if jobs.get(job_id, token)["state"] != "running":
                        return
                    temporary.replace(destination)
                finally:
                    temporary.unlink(missing_ok=True)
                jobs.result_size(job_id, len(result))
                if not jobs.transition(job_id, "running", "completed"):
                    (folder / (job_id + ".bin")).unlink(missing_ok=True)
        except asyncio.CancelledError:
            jobs.transition(job_id, "running", "cancelled")
            jobs.transition(job_id, "queued", "cancelled")
            raise
        except Exception as exc:
            jobs.update(job_id, "failed", str(exc)[:500])
        finally:
            if jobs.get(job_id, token)["state"] != "completed":
                (settings.data_dir / "output" / (job_id + ".bin")).unlink(missing_ok=True)
                (settings.data_dir / "output" / (job_id + ".tmp")).unlink(missing_ok=True)
            TASKS.pop(job_id, None)
    TASKS[job_id] = asyncio.create_task(worker())
    return {"id": job_id, "token": token, "state": "queued"}

def authorized(job_id, token):
    job = jobs.get(job_id, token)
    if job is None:
        raise HTTPException(404, "Job not found")
    return job

def job_public(job):
    return {"id": job["id"], "state": job["state"], "progress": job["progress"], "filename": job["filename"], "result_size": job["result_size"], "error": job["error"], "created": job["created"], "updated": job["updated"], "finished": job["finished"], "expires_at": (job["finished"] or job["created"]) + settings.job_ttl_seconds if job["state"] in ("completed", "failed", "cancelled") else None, "download_available": job["state"] == "completed" and (settings.data_dir / "output" / (job["id"] + ".bin")).is_file()}

@app.get("/api/jobs/{job_id}")
async def job_status(job_id: str, x_job_token: str = Header("")):
    job = authorized(job_id, x_job_token)
    return job_public(job)

@app.post("/api/jobs/{job_id}/cancel")
async def cancel_job(job_id: str, x_job_token: str = Header("")):
    job = authorized(job_id, x_job_token)
    if job["state"] in ("queued", "running"):
        jobs.transition(job_id, job["state"], "cancelled")
        task = TASKS.get(job_id)
        if task:
            task.cancel()
    return {"id": job_id, "state": authorized(job_id, x_job_token)["state"]}

@app.get("/api/jobs/{job_id}/events")
async def job_events(job_id: str, token: str = ""):
    authorized(job_id, token)
    async def events():
        for _ in range(120):
            job = authorized(job_id, token)
            yield {"event": "status", "data": json.dumps(job_public(job))}
            if job["state"] in ("completed", "failed", "cancelled"):
                break
            await asyncio.sleep(1)
    return EventSourceResponse(events())

@app.get("/api/jobs/{job_id}/download")
async def job_download(job_id: str, token: str = "", x_job_token: str = Header("")):
    job = authorized(job_id, x_job_token or token)
    if job["state"] != "completed":
        raise HTTPException(409, "Job not completed")
    path = settings.data_dir / "output" / (job_id + ".bin")
    if not path.is_file():
        raise HTTPException(410, "Result expired")
    return FileResponse(path, media_type="application/octet-stream", filename=job["filename"], headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})

@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str, x_job_token: str = Header("")):
    result = jobs.delete(job_id, x_job_token)
    if result is None:
        raise HTTPException(404, "Job not found")
    if result is False:
        raise HTTPException(409, "Cancel the active job before deleting it")
    return {"id": job_id, "deleted": True}
