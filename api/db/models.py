"""SQLAlchemy ORM models matching the PostGIS schema."""
from datetime import datetime
from geoalchemy2 import Geometry
from sqlalchemy import Column, String, Float, Boolean, Integer, Text, DateTime
from db.session import Base


class Violation(Base):
    __tablename__ = "violations"

    id                  = Column(String(20), primary_key=True)
    latitude            = Column(Float, nullable=False)
    longitude           = Column(Float, nullable=False)
    location            = Column(Text)
    vehicle_number      = Column(String(30))
    vehicle_type        = Column(String(30))
    violation_type      = Column(Text)
    offence_code        = Column(Text)
    created_datetime    = Column(DateTime(timezone=True))
    closed_datetime     = Column(DateTime(timezone=True))
    police_station      = Column(String(60))
    junction_name       = Column(String(120))
    data_sent_to_scita  = Column(Boolean, default=False)
    validation_status   = Column(String(20))
    cis_score           = Column(Float)
    geom                = Column(Geometry("POINT", srid=4326))


class Hotspot(Base):
    __tablename__ = "hotspots"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    cluster_id      = Column(Integer)
    centroid_lat    = Column(Float)
    centroid_lng    = Column(Float)
    violation_count = Column(Integer)
    avg_cis_score   = Column(Float)
    top_violation   = Column(Text)
    police_station  = Column(Text)
    computed_at     = Column(DateTime(timezone=True), default=datetime.utcnow)
    geom            = Column(Geometry("POINT", srid=4326))
