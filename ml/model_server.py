"""
ParkSense AI — ML Service
Exposes YOLO detection and CIS scoring as a FastAPI microservice.
"""
import os
import base64
import logging
from io import BytesIO
from typing import Optional

import numpy as np
from PIL import Image
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from utils.cis import compute_cis_score
from utils.detector import ParkingDetector

logging.basicConfig(level=os.getenv("LOG_LEVEL", "info").upper())
logger = logging.getLogger(__name__)

app = FastAPI(title="ParkSense ML Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model once at startup
detector: Optional[ParkingDetector] = None

@app.on_event("startup")
async def startup():
    global detector
    model_path = os.getenv("ML_MODEL_PATH", "/app/models/best.pt")
    detector = ParkingDetector(model_path)
    logger.info("YOLO model loaded: %s", model_path)


# ── Request / Response schemas ─────────────────────────────────────────────────

class DetectRequest(BaseModel):
    image_base64: str          # base64-encoded JPEG/PNG frame
    camera_id: str = "unknown"
    location: str = ""
    vehicle_type: str = "unknown"
    junction_name: str = "No Junction"

class ViolationResult(BaseModel):
    detected: bool
    confidence: float
    bbox: list[float]          # [x1, y1, x2, y2] normalised 0-1
    vehicle_type: str

class DetectResponse(BaseModel):
    camera_id: str
    violations: list[ViolationResult]
    cis_score: float
    violation_count: int

class CISRequest(BaseModel):
    vehicle_type: str
    junction_name: str
    violation_type: str = "WRONG PARKING"
    duration_minutes: float = 0.0
    nearby_violation_count: int = 0

class CISResponse(BaseModel):
    cis_score: float
    breakdown: dict


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": detector is not None}


@app.post("/detect", response_model=DetectResponse)
async def detect_violations(req: DetectRequest):
    """Detect illegally parked vehicles in a CCTV frame."""
    if detector is None:
        raise HTTPException(503, "Model not loaded")

    try:
        img_bytes = base64.b64decode(req.image_base64)
        image = Image.open(BytesIO(img_bytes)).convert("RGB")
        img_array = np.array(image)
    except Exception as e:
        raise HTTPException(400, f"Invalid image: {e}")

    results = detector.detect(img_array)

    # Compute CIS for the worst detection
    cis = 0.0
    if results:
        cis = compute_cis_score(
            vehicle_type=req.vehicle_type,
            junction_name=req.junction_name,
            violation_type="WRONG PARKING",
            duration_minutes=0,
            nearby_count=len(results),
        )

    return DetectResponse(
        camera_id=req.camera_id,
        violations=results,
        cis_score=round(cis, 2),
        violation_count=len(results),
    )


@app.post("/cis", response_model=CISResponse)
def score_violation(req: CISRequest):
    """Compute Congestion Impact Score for a known violation record."""
    score, breakdown = compute_cis_score(
        vehicle_type=req.vehicle_type,
        junction_name=req.junction_name,
        violation_type=req.violation_type,
        duration_minutes=req.duration_minutes,
        nearby_count=req.nearby_violation_count,
        return_breakdown=True,
    )
    return CISResponse(cis_score=round(score, 2), breakdown=breakdown)
