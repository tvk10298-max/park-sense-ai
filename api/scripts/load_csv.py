"""
Load the Bengaluru violation CSV into PostGIS.
Run once: python scripts/load_csv.py

Place the CSV at: data/jan_to_may_violations.csv
"""
import os
import sys
import json
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

CSV_PATH = os.getenv("CSV_PATH", "data/jan_to_may_violations.csv")

conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432"),
    dbname=os.getenv("DB_NAME", "parksense"),
    user=os.getenv("DB_USER", "parksense"),
    password=os.getenv("DB_PASSWORD", "changeme"),
)
conn.autocommit = False
cur = conn.cursor()

print(f"Loading {CSV_PATH} …")
df = pd.read_csv(CSV_PATH, low_memory=False)
print(f"Rows read: {len(df):,}")

# Normalise columns that must exist
required = ["id", "latitude", "longitude", "vehicle_type",
            "violation_type", "created_datetime", "police_station"]
for col in required:
    if col not in df.columns:
        print(f"ERROR: missing column '{col}'")
        sys.exit(1)

# Drop rows with no coordinates
df = df.dropna(subset=["latitude", "longitude"])

# Build insert rows
rows = []
for _, r in df.iterrows():
    rows.append((
        str(r.get("id", "")),
        float(r["latitude"]),
        float(r["longitude"]),
        str(r.get("location", ""))[:500] if pd.notna(r.get("location")) else None,
        str(r.get("vehicle_number", "")) if pd.notna(r.get("vehicle_number")) else None,
        str(r.get("vehicle_type", "")) if pd.notna(r.get("vehicle_type")) else None,
        str(r.get("violation_type", "")) if pd.notna(r.get("violation_type")) else None,
        str(r.get("offence_code", "")) if pd.notna(r.get("offence_code")) else None,
        str(r.get("created_datetime", "")) if pd.notna(r.get("created_datetime")) else None,
        str(r.get("closed_datetime", "")) if pd.notna(r.get("closed_datetime")) else None,
        str(r.get("police_station", "")) if pd.notna(r.get("police_station")) else None,
        str(r.get("junction_name", "")) if pd.notna(r.get("junction_name")) else None,
        bool(r.get("data_sent_to_scita", False)),
        str(r.get("validation_status", "")) if pd.notna(r.get("validation_status")) else None,
    ))

SQL = """
    INSERT INTO violations (
        id, latitude, longitude, location, vehicle_number, vehicle_type,
        violation_type, offence_code, created_datetime, closed_datetime,
        police_station, junction_name, data_sent_to_scita, validation_status,
        geom
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        ST_SetSRID(ST_MakePoint(%s, %s), 4326)
    )
    ON CONFLICT (id) DO NOTHING
"""

# Add lat/lng again for geom at end of each row
rows_with_geom = [r + (r[2], r[1]) for r in rows]   # lon, lat order for ST_MakePoint

BATCH = 5000
total = 0
for i in range(0, len(rows_with_geom), BATCH):
    batch = rows_with_geom[i:i+BATCH]
    cur.executemany(SQL, batch)
    conn.commit()
    total += len(batch)
    print(f"  Inserted {total:,} / {len(rows_with_geom):,}", end="\r")

print(f"\nDone. {total:,} rows loaded.")
cur.close()
conn.close()
