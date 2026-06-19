"""GET /enforcement/priority — ranked stations needing deployment."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from db.session import get_db

router = APIRouter()


@router.get("/priority")
async def enforcement_priority(
    top_n: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """
    Ranks police stations by:
      priority_score = avg_cis * log(violation_count)
    Returns top N stations with recommended officer count and peak hours.
    """
    sql = text("""
        SELECT
            police_station,
            COUNT(*)                           AS violation_count,
            AVG(COALESCE(cis_score, 40))       AS avg_cis,
            AVG(COALESCE(cis_score, 40)) * LN(COUNT(*) + 1) AS priority_score,
            EXTRACT(HOUR FROM created_datetime) AS peak_hour
        FROM violations
        WHERE validation_status = 'approved'
          AND police_station IS NOT NULL
        GROUP BY police_station, EXTRACT(HOUR FROM created_datetime)
        ORDER BY priority_score DESC
        LIMIT :top_n
    """)

    result = await db.execute(sql, {"top_n": top_n})
    rows = result.fetchall()

    recommendations = []
    for r in rows:
        count = r.violation_count
        # Simple heuristic: 1 officer per 5000 violations, min 1, max 8
        officers = max(1, min(8, round(count / 5000)))
        recommendations.append({
            "police_station":       r.police_station,
            "violation_count":      count,
            "avg_cis_score":        round(r.avg_cis or 0, 2),
            "priority_score":       round(r.priority_score or 0, 2),
            "recommended_officers": officers,
            "peak_hour":            int(r.peak_hour or 9),
        })

    return {"recommendations": recommendations}
