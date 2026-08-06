#!/usr/bin/env python3
import logging
import os
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.core.inference import generate_architecture, preload_model, run_startup_smoke_test
from backend.core.response_builder import build_response, response_to_explain_payload

logger = logging.getLogger(__name__)

app = FastAPI()

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "").strip()

if FRONTEND_ORIGIN:
    allowed_origins = [origin.strip() for origin in FRONTEND_ORIGIN.split(",") if origin.strip()]
else:
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExplainRequest(BaseModel):
    text: str = Field(..., min_length=1)


@app.on_event("startup")
async def preload_inference_model() -> None:
    preload_model()
    run_startup_smoke_test()
    print("MODEL READY")


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}


@app.post("/explain")
async def explain(request: ExplainRequest):
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Provide non-empty 'text' in request body")

    started_at = time.perf_counter()
    try:
        architecture, raw_output = generate_architecture(text)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Model inference failed: {exc}") from exc

    duration_ms = int((time.perf_counter() - started_at) * 1000)

    # Security analysis is part of the canonical pipeline; degrade gracefully.
    try:
        response = build_response(
            architecture,
            raw_model_output=raw_output,
            duration_ms=duration_ms,
            provider="gemma",
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Security analysis failed: %s", exc)
        response = build_response(
            architecture,
            raw_model_output=raw_output,
            duration_ms=duration_ms,
            provider="gemma",
            run_security=False,
        )

    return response_to_explain_payload(response)