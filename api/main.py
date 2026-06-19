"""
ParkSense AI — Backend API
FastAPI application with REST + WebSocket endpoints.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.session import engine, Base
from routes import violations, hotspots, enforcement, trends, live, detect, predictions


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables if they don't exist (migrations handle prod)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="ParkSense AI API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(violations.router,  prefix="/violations",  tags=["Violations"])
app.include_router(hotspots.router,    prefix="/hotspots",    tags=["Hotspots"])
app.include_router(enforcement.router, prefix="/enforcement", tags=["Enforcement"])
app.include_router(trends.router,      prefix="/trends",      tags=["Trends"])
app.include_router(detect.router,      prefix="/detect",      tags=["Detection"])
app.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
app.include_router(live.router,                               tags=["Live"])

@app.get("/health")
def health():
    return {"status": "ok", "service": "parksense-api"}
