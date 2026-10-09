"""Barvium aggregate counter; launch with uvicorn app:app --no-access-log.
A VPS and TLS-terminating reverse proxy are needed for production usage.
"""
import os
import sqlite3
from pathlib import Path
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, ConfigDict

DB_PATH = Path(os.environ.get("BARVIUM_DB", "barvium-counts.sqlite3"))
app = FastAPI(title="Barvium opt-in installation counter", docs_url=None, redoc_url=None)

class InstallEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event: str
    version: str

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as db:
        db.execute("CREATE TABLE IF NOT EXISTS counters (version TEXT PRIMARY KEY, count INTEGER NOT NULL)")

@app.post("/v1/install", status_code=204)
def install(body: InstallEvent):
    if body.event != "install_completed" or body.version not in {"0.3.0-dev"}:
        raise HTTPException(status_code=422, detail="Invalid event or version")
    init_db()
    with sqlite3.connect(DB_PATH, timeout=15) as db:
        db.execute("INSERT INTO counters(version, count) VALUES (?, 1) "
                   "ON CONFLICT(version) DO UPDATE SET count=count+1", (body.version,))
    return Response(status_code=204)

# No public counts endpoint or request/IP/user-agent logging in application code.
