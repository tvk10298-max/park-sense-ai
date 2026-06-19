# ParkSense AI — Step-by-Step Setup Guide

## Prerequisites

Install these on your machine before starting:

| Tool | Version | Install |
|---|---|---|
| Python | 3.11+ | python.org |
| Node.js | 20+ | nodejs.org |
| Docker Desktop | latest | docker.com |
| Git | any | git-scm.com |
| VS Code | any | code.visualstudio.com |

---

## Step 1 — Clone the repo

```bash
git clone https://github.com/YOUR_ORG/parksense-ai.git
cd parksense-ai
```

---

## Step 2 — Create your .env file

```bash
cp .env.example .env
```

Open `.env` and fill in:

```env
DB_PASSWORD=choose_a_strong_password
SECRET_KEY=any_32_char_random_string
VITE_MAPBOX_TOKEN=              # leave blank to use free OpenStreetMap
```

Everything else works as-is for local development.

---

## Step 3 — Add the violation CSV

Copy your Bengaluru violation CSV into the data folder:

```bash
cp /path/to/jan_to_may_violations.csv data/jan_to_may_violations.csv
```

---

## Step 4 — Start all services with Docker

```bash
docker compose up --build
```

This starts:
- **db**       — PostGIS on port 5432
- **redis**    — Cache on port 6379
- **ml**       — ML service on port 8001
- **api**      — FastAPI backend on port 8000
- **frontend** — React dashboard on port 3000
- **nginx**    — Reverse proxy on port 80

Wait ~60 seconds for all services to become healthy.

---

## Step 5 — Load the CSV data into PostGIS

Open a new terminal while Docker is running:

```bash
# Enter the api container
docker exec -it parksense_api bash

# Run the loader (inside the container)
python scripts/load_csv.py
```

Expected output:
```
Loading data/jan_to_may_violations.csv …
Rows read: 298,450
Inserted 298,450 / 298,450
Done. 298,450 rows loaded.
```

---

## Step 6 — Open the dashboard

Go to **http://localhost:3000** in your browser.

You should see:
- 🗺 Heatmap tab — Bengaluru violation density (Upparpet, Shivajinagar highlighted)
- 📈 Trends tab   — Monthly/weekly charts
- 👮 Enforcement  — Priority station list with CIS scores

---

## Step 7 — Check API docs

Go to **http://localhost:8000/docs** to see all REST endpoints:

| Endpoint | Description |
|---|---|
| GET /violations | Paginated violation list |
| GET /hotspots | Top spatial clusters by CIS |
| GET /enforcement/priority | Officer deployment recommendations |
| GET /trends | Violation trends over time |
| POST /detect | Send camera frame for detection |
| WS /live | WebSocket live violation stream |

---

## Step 8 — Set up ML model (after training)

Once YOLO training is complete:

```bash
# Copy your trained weights into the ml/models folder
cp /path/to/runs/detect/train/weights/best.pt ml/models/best.pt

# Restart the ML service
docker compose restart ml
```

Until the model file exists, the ML service runs in **mock mode**
(returns empty detections — all other features work normally).

---

## Development without Docker (per service)

If you want to run a single service locally for faster iteration:

### API only
```bash
cd api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --port 8000 --reload
```

### ML service only
```bash
cd ml
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn model_server:app --port 8001 --reload
```

### Frontend only
```bash
cd frontend
npm install
VITE_API_URL=http://localhost:8000 npm run dev
```

---

## Folder structure

```
parksense-ai/
├── .env.example              # Copy to .env and fill in secrets
├── .gitignore
├── docker-compose.yml        # Starts all 4 services
│
├── data/                     # Put your CSV here
│   └── jan_to_may_violations.csv
│
├── ml/                       # ML detection service (port 8001)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── model_server.py       # FastAPI entry point
│   ├── models/               # Place best.pt here after training
│   ├── notebooks/            # Jupyter training notebooks
│   └── utils/
│       ├── cis.py            # Congestion Impact Score algorithm
│       └── detector.py       # YOLO wrapper
│
├── api/                      # Backend REST API (port 8000)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py               # FastAPI entry point
│   ├── db/
│   │   ├── session.py        # SQLAlchemy async engine
│   │   └── models.py         # ORM models
│   ├── routes/
│   │   ├── violations.py     # GET /violations
│   │   ├── hotspots.py       # GET /hotspots
│   │   ├── enforcement.py    # GET /enforcement/priority
│   │   ├── trends.py         # GET /trends
│   │   ├── detect.py         # POST /detect
│   │   └── live.py           # WS /live
│   ├── scripts/
│   │   └── load_csv.py       # One-time CSV importer
│   └── tests/
│
├── frontend/                 # React dashboard (port 3000)
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       └── pages/
│           ├── Dashboard.jsx  # Leaflet heatmap + live feed
│           ├── Trends.jsx     # Chart.js trend charts
│           └── Enforcement.jsx # Priority deployment panel
│
└── infra/
    ├── nginx/
    │   └── nginx.conf
    └── scripts/
        └── init_db.sql       # PostGIS schema, auto-run on DB first boot
```

---

## Troubleshooting

**Port already in use:**
```bash
docker compose down && docker compose up --build
```

**DB not ready error:**
```bash
# Wait 30s then retry — PostGIS takes time to init
docker compose restart api
```

**Heatmap is empty:**
Make sure Step 5 (CSV load) completed successfully.
Check: `docker exec -it parksense_db psql -U parksense -c "SELECT COUNT(*) FROM violations;"`
Expected: 298450

**ML in mock mode:**
Normal until you place `best.pt` in `ml/models/`. All other features work.
