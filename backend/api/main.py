#!/usr/bin/env python3
import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.core.inference import generate_architecture, preload_model, run_startup_smoke_test
from backend.security.security_analyzer import analyze_architecture_security
from backend.security.threat_detector import calculate_attack_surface, detect_threats

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


@app.on_event("startup")
async def preload_inference_model() -> None:
    preload_model()
    run_startup_smoke_test()
    print("MODEL READY")


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}


@app.post("/explain")
async def explain(payload: dict):
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Invalid request body")

    text = payload.get("text")
    if not isinstance(text, str) or not text.strip():
        raise HTTPException(status_code=400, detail="Provide non-empty 'text' in request body")

    try:
        architecture, raw_output = generate_architecture(text)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Model inference failed: {exc}") from exc

    # Security analysis integration
    security_result = None
    try:
        nodes = architecture.get("nodes", [])
        edges = architecture.get("edges", [])

        # Run security analysis
        analysis = analyze_architecture_security(nodes, edges)

        # Run threat detection
        threats_result = detect_threats(nodes, edges)

        # Calculate attack surface
        attack_surface = calculate_attack_surface(nodes, edges)

        # Assemble security response object
        security_result = {
            "security_score": analysis["security_score"],
            "risk_level": analysis["risk_level"],
            "missing_components": analysis["missing_components"],
            "recommendations": analysis["recommendations"],
            "threats": threats_result["threats"],
            "node_threats": threats_result.get("node_threats", {}),
            "edge_threats": threats_result.get("edge_threats", {}),
            "attack_surface": attack_surface,
            "security_summary": analysis["security_summary"],
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("Security analysis failed: %s", exc)
        security_result = None

    return {"architecture": architecture, "raw_model_output": raw_output, "security": security_result}
