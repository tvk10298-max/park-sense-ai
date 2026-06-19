"""
Congestion Impact Score (CIS) Algorithm
Score range: 0 – 100
Higher = more congestion impact
"""
from typing import Tuple

# Vehicle weight — heavier / larger = more road blocked
VEHICLE_WEIGHTS = {
    "TANKER":         1.00,
    "PRIVATE BUS":    0.95,
    "LGV":            0.85,
    "MAXI-CAB":       0.80,
    "VAN":            0.70,
    "GOODS AUTO":     0.65,
    "CAR":            0.60,
    "PASSENGER AUTO": 0.50,
    "MOTOR CYCLE":    0.35,
    "SCOOTER":        0.30,
    "MOPED":          0.25,
}

# Location weight — junction / main road = higher impact
JUNCTION_KEYWORDS = ["junction", "signal", "crossing", "circle", "btm", "btp"]
MAIN_ROAD_KEYWORDS = ["main road", "main", "highway", "outer ring", "inner ring", "flyover"]

# Violation type multiplier
VIOLATION_MULTIPLIERS = {
    "NO PARKING":               1.10,
    "WRONG PARKING":            1.00,
    "PARKING IN A MAIN ROAD":   1.15,
    "PARKING NEAR ROAD CROSSING": 1.20,
    "PARKING ON FOOTPATH":      0.90,
}


def _location_weight(junction_name: str) -> float:
    name = (junction_name or "").lower()
    if any(k in name for k in JUNCTION_KEYWORDS):
        return 1.0
    if any(k in name for k in MAIN_ROAD_KEYWORDS):
        return 0.80
    if name and name != "no junction":
        return 0.65
    return 0.45


def _duration_weight(duration_minutes: float) -> float:
    if duration_minutes <= 0:
        return 0.40   # unknown duration → moderate
    if duration_minutes < 15:
        return 0.30
    if duration_minutes < 60:
        return 0.55
    if duration_minutes < 240:
        return 0.75
    return 1.00       # parked > 4 hours


def _density_weight(nearby_count: int) -> float:
    if nearby_count == 0:
        return 0.30
    if nearby_count < 3:
        return 0.50
    if nearby_count < 10:
        return 0.70
    return 1.00


def compute_cis_score(
    vehicle_type: str,
    junction_name: str,
    violation_type: str = "WRONG PARKING",
    duration_minutes: float = 0.0,
    nearby_count: int = 0,
    return_breakdown: bool = False,
) -> float | Tuple[float, dict]:
    """
    Weighted formula:
      CIS = 100 × (0.30×vehicle + 0.30×location + 0.20×duration + 0.20×density) × violation_mult
    """
    vw  = VEHICLE_WEIGHTS.get(vehicle_type.upper(), 0.50)
    lw  = _location_weight(junction_name)
    dw  = _duration_weight(duration_minutes)
    dew = _density_weight(nearby_count)

    # Extract first violation type if list-like string
    vt = violation_type.strip('[]"').split('","')[0].strip('"').upper()
    vm = max(VIOLATION_MULTIPLIERS.get(vt, 1.0) for vt in
             [vt] + [v.upper() for v in violation_type.replace('"', '').strip("[]").split(",")])

    raw = (0.30 * vw) + (0.30 * lw) + (0.20 * dw) + (0.20 * dew)
    score = min(100.0, raw * vm * 100)

    if return_breakdown:
        return score, {
            "vehicle_weight":   round(vw, 2),
            "location_weight":  round(lw, 2),
            "duration_weight":  round(dw, 2),
            "density_weight":   round(dew, 2),
            "violation_mult":   round(vm, 2),
        }
    return score
