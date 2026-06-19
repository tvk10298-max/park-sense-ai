"""GET /predictions — 7-day forecast per police station."""
import json, os
from fastapi import APIRouter

router = APIRouter()

@router.get("")
def get_predictions(station: str = None):
    path = "/app/data/predictions.json"
    if not os.path.exists(path):
        return {"predictions": [], "message": "Model not trained yet"}
    with open(path) as f:
        data = json.load(f)
    if station:
        data = [d for d in data if d["police_station"] == station]
    # Sort by predicted violations descending
    data = sorted(data, key=lambda x: -x["predicted_violations"])
    return {"count": len(data), "predictions": data[:100]}
