"""
Week 1 pipeline: API -> Python -> SQLite

Pulls current weather for a few cities from Open-Meteo (free, no API key)
and stores it in weather.db. Run it multiple times and watch rows pile up.
Only uses Python's standard library, so nothing to install.
"""

import json
import sqlite3
import urllib.request
from datetime import datetime, timezone

DB_FILE = "weather.db"

# Add your own cities here: (name, latitude, longitude)
CITIES = [
    ("Hyderabad", 17.385, 78.4867),
    ("Mumbai", 19.076, 72.8777),
    ("Toronto", 43.6532, -79.3832),
    ("Vancouver", 49.2827, -123.1207),
    ("New York", 40.7128, -74.006),
    ("Lakewood", 40.0821, -74.2097),
]

API_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude={lat}&longitude={lon}"
    "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation"
)


def extract(city, lat, lon):
    """EXTRACT: call the API and return the raw JSON."""
    url = API_URL.format(lat=lat, lon=lon)
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def transform(city, raw):
    """TRANSFORM: pick the fields we care about and shape them into a row."""
    current = raw["current"]
    return (
        city,
        current["temperature_2m"],
        current["relative_humidity_2m"],
        current["wind_speed_10m"],
        current["precipitation"],
        current["time"],  # when the reading was observed (API time)
        datetime.now(timezone.utc).isoformat(timespec="seconds"),  # when we fetched it
    )


def load(conn, rows):
    """LOAD: write rows into the database."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS readings (
            city          TEXT NOT NULL,
            temperature_c REAL,
            humidity_pct  REAL,
            wind_kmh      REAL,
            precipitation_mm REAL,
            observed_at   TEXT NOT NULL,
            fetched_at    TEXT NOT NULL,
            UNIQUE (city, observed_at)
        )
        """
    )
    # INSERT OR IGNORE + UNIQUE means re-running never creates duplicates.
    # Data engineers call this being "idempotent". It matters a lot.
    before = conn.total_changes
    conn.executemany(
        "INSERT OR IGNORE INTO readings VALUES (?, ?, ?, ?, ?, ?,?)", rows
    )
    conn.commit()
    return conn.total_changes - before


def main():
    rows = []
    for city, lat, lon in CITIES:
        try:
            raw = extract(city, lat, lon)
            rows.append(transform(city, raw))
            print(f"fetched {city}")
        except Exception as e:  # keep going if one city fails
            print(f"FAILED {city}: {e}")

    conn = sqlite3.connect(DB_FILE)
    inserted = load(conn, rows)
    print(f"\n{inserted} new rows inserted ({len(rows) - inserted} already existed)\n")

    print("Latest readings in the database:")
    print(f"{'city':<12}{'temp C':>8}{'humid %':>9}{'wind km/h':>11}{'rain mm':>9}  observed_at")
    for r in conn.execute(
        "SELECT city, temperature_c, humidity_pct, wind_kmh, observed_at, precipitation_mm "
        "FROM readings ORDER BY observed_at DESC, city LIMIT 10"
    ):
        print(f"{r[0]:<12}{r[1]:>8}{r[2]:>9}{r[4]:>11}  {r[5]}")

    total = conn.execute("SELECT COUNT(*) FROM readings").fetchone()[0]
    print(f"\nTotal rows in weather.db: {total}")
    conn.close()


if __name__ == "__main__":
    main()
