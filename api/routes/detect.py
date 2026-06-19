"""POST /detect — proxy camera frames to ML service and store result."""
import os
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()
ML_URL = os.getenv("ML_SERVICE_URL", "http://ml:8001")


class DetectRequest(BaseModel):
    image_base64: str
    camera_id: str = "unknown"
    location: str = ""
    vehicle_type: str = "unknown"
    junction_name: str = "No Junction"


@router.post("")
async def detect(req: DetectRequest):
    """Forward frame to ML service, return detection + CIS score."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{ML_URL}/detect",
                json=req.model_dump(),
            )
            resp.raise_for_status()
            return resp.json()
    except httpx.ConnectError:
        raise HTTPException(503, "ML service unavailable")
    except httpx.HTTPStatusError as e:
        raise HTTPException(e.response.status_code, "ML service error")
