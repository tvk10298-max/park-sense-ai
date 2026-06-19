"""GET /violations — paginated, filtered list of parking violations."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime

from db.session import get_db
from db.models import Violation

router = APIRouter()


@router.get("")
async def list_violations(
    station:      Optional[str] = Query(None, description="Police station name"),
    vehicle_type: Optional[str] = Query(None),
    from_date:    Optional[datetime] = Query(None),
    to_date:      Optional[datetime] = Query(None),
    status:       Optional[str] = Query(None, description="approved|rejected|processing"),
    limit:        int = Query(100, le=1000),
    offset:       int = Query(0),
    db:           AsyncSession = Depends(get_db),
):
    conditions = []
    if station:      conditions.append(Violation.police_station == station)
    if vehicle_type: conditions.append(Violation.vehicle_type == vehicle_type)
    if from_date:    conditions.append(Violation.created_datetime >= from_date)
    if to_date:      conditions.append(Violation.created_datetime <= to_date)
    if status:       conditions.append(Violation.validation_status == status)

    stmt = (
        select(Violation)
        .where(and_(*conditions))
        .order_by(Violation.created_datetime.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()

    return {
        "total": len(rows),
        "offset": offset,
        "limit": limit,
        "data": [
            {
                "id":              r.id,
                "latitude":        r.latitude,
                "longitude":       r.longitude,
                "vehicle_type":    r.vehicle_type,
                "violation_type":  r.violation_type,
                "police_station":  r.police_station,
                "junction_name":   r.junction_name,
                "cis_score":       r.cis_score,
                "created_datetime":str(r.created_datetime),
                "validation_status": r.validation_status,
            }
            for r in rows
        ],
    }
