from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_name: str = "Data Toolkit"
    app_host: str = "127.0.0.1"
    app_port: int = 8015
    data_dir: Path = Path("data")
    max_upload_mb: int = 50
    max_batch_files: int = 10
    max_batch_total_mb: int = 200
    max_rows: int = 100000
    max_columns: int = 500
    preview_rows: int = 100
    job_ttl_seconds: int = 3600
    max_concurrent_jobs: int = 2

settings = Settings()
