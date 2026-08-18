"""
Atlas HTTP API.

Thin transport layer between HTTP clients and the Atlas application boundary.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse


app = FastAPI(
    title="Atlas Engineering Intelligence Platform",
    version="0.1.0",
    description="Atlas Engineering Intelligence Platform API",
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "Atlas",
        "status": "online",
        "version": "0.1.0",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "healthy",
    }


@app.get("/ready")
def ready() -> JSONResponse:
    return JSONResponse(
        content={
            "status": "ready",
        }
    )