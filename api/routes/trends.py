"""GET /trends — violation aggregates by time, type, station."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Literal

from db.session import get_db

router = APIRouter()


@router.get("")
async def get_trends(
    group_by: Literal["month", "week", "day", "hour"] = "month",
    station: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    trunc = {
        "month": "month", "week": "week",
        "day": "day", "hour": "hour"
    }[group_by]

    station_filter = "AND police_station = :station" if station else ""

    sql = text(f"""
        SELECT
            DATE_TRUNC('{trunc}', created_datetime) AS period,
            violation_type,
            vehicle_type,
            COUNT(*) AS count,
            AVG(COALESCE(cis_score, 40)) AS avg_cis
        FROM violations
        WHERE created_datetime IS NOT NULL
          {station_filter}
        GROUP BY period, violation_type, vehicle_type
        ORDER BY period DESC, count DESC
        LIMIT 500
    """)

    params = {"station": station} if station else {}
    result = await db.execute(sql, params)
    rows = result.fetchall()

    return {
        "group_by": group_by,
        "data": [
            {
                "period":         str(r.period),
                "violation_type": r.violation_type,
                "vehicle_type":   r.vehicle_type,
                "count":          r.count,
                "avg_cis":        round(r.avg_cis or 0, 2),
            }
            for r in rows
        ],
    }
