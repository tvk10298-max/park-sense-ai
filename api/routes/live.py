"""WebSocket /live — streams new violations to dashboard in real time."""
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select, text
from db.session import AsyncSessionLocal
from db.models import Violation

router = APIRouter()

# Track connected clients
connected: list[WebSocket] = []


@router.websocket("/live")
async def live_feed(ws: WebSocket):
    await ws.accept()
    connected.append(ws)
    try:
        # Send last 20 violations on connect
        async with AsyncSessionLocal() as db:
            stmt = (
                select(Violation)
                .order_by(Violation.created_datetime.desc())
                .limit(20)
            )
            result = await db.execute(stmt)
            rows = result.scalars().all()

        for r in reversed(rows):
            await ws.send_text(json.dumps({
                "type":           "violation",
                "id":             r.id,
                "latitude":       r.latitude,
                "longitude":      r.longitude,
                "vehicle_type":   r.vehicle_type,
                "violation_type": r.violation_type,
                "police_station": r.police_station,
                "cis_score":      r.cis_score or 40,
                "created":        str(r.created_datetime),
            }))

        # Keep alive — ping every 30s
        while True:
            await asyncio.sleep(30)
            await ws.send_text(json.dumps({"type": "ping"}))

    except WebSocketDisconnect:
        connected.remove(ws)


async def broadcast_violation(violation_dict: dict):
    """Call this after a new violation is inserted to push it live."""
    dead = []
    for ws in connected:
        try:
            await ws.send_text(json.dumps({"type": "violation", **violation_dict}))
        except Exception:
            dead.append(ws)
    for ws in dead:
        connected.remove(ws)
