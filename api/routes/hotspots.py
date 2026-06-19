"""GET /hotspots — top violation clusters with CIS scores."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.session import get_db

router = APIRouter()

@router.get("")
async def get_hotspots(
    limit: int = 200,
    db: AsyncSession = Depends(get_db),
):
    sql = text("""
        SELECT
            police_station,
            AVG(latitude)  AS centroid_lat,
            AVG(longitude) AS centroid_lng,
            COUNT(*)       AS violation_count,
            AVG(COALESCE(cis_score, 40)) AS avg_cis_score,
            MODE() WITHIN GROUP (ORDER BY violation_type) AS top_violation
        FROM violations
        WHERE latitude IS NOT NULL
          AND longitude IS NOT NULL
          AND validation_status = 'approved'
        GROUP BY police_station
        ORDER BY violation_count DESC
        LIMIT :limit
    """)

    result = await db.execute(sql, {"limit": limit})
    rows = result.fetchall()

    data = [
        {
            "cluster_id":      i,
            "centroid_lat":    round(r.centroid_lat, 6),
            "centroid_lng":    round(r.centroid_lng, 6),
            "violation_count": r.violation_count,
            "avg_cis_score":   round(r.avg_cis_score or 40, 2),
            "top_violation":   r.top_violation,
            "police_station":  r.police_station,
        }
        for i, r in enumerate(rows)
    ]

    return {"count": len(data), "hotspots": data}
