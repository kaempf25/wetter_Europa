"""
Download and parse the DWD weather station list for daily climate data (kl/recent).

Strategy:
1. Try direct download from DWD opendata server
2. Fall back to Bright Sky API to collect all DWD observation stations

Writes filtered results (bis_datum >= 2024) to JSON.
"""

import json
import sys
import requests


OUTPUT = "/home/user/wetter_Europa/data/dwd_stations.json"

DWD_URL = (
    "https://opendata.dwd.de/climate_environment/CDC/"
    "observations_germany/climate/daily/kl/recent/"
    "KL_Tageswerte_Beschreibung_Stationen.txt"
)


def try_direct_download():
    """Try downloading directly from DWD opendata server."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; weather-script/1.0)"}
    resp = requests.get(DWD_URL, timeout=30, headers=headers)
    resp.raise_for_status()
    text = resp.content.decode("latin-1")
    lines = text.splitlines()

    # Parse dash line to get column boundaries
    dash_line = lines[1]
    col_ends = []
    in_dash = False
    start = 0
    for i, ch in enumerate(dash_line):
        if ch == "-" and not in_dash:
            in_dash = True
            start = i
        elif ch != "-" and in_dash:
            in_dash = False
            col_ends.append((start, i))
    if in_dash:
        col_ends.append((start, len(dash_line)))

    stations = []
    for line in lines[2:]:
        if not line.strip():
            continue

        def col(idx, line=line):
            s, e = col_ends[idx]
            if idx == len(col_ends) - 1:
                return line[s:].strip()
            return line[s:e].strip()

        station_id = col(0).zfill(5)
        von_datum = col(1)
        bis_datum = col(2)
        elevation = int(col(3))
        lat = float(col(4))
        lon = float(col(5))
        name = col(6)
        state = col(7)

        year = int(bis_datum[:4])
        if year < 2024:
            continue

        stations.append({
            "id": station_id,
            "name": name,
            "lat": lat,
            "lon": lon,
            "elevation": elevation,
            "state": state,
            "from": von_datum,
            "to": bis_datum,
        })

    return stations


# German state lookup based on coordinates (rough bounding boxes)
# This is used as a fallback when the state is not available from the API
GERMAN_STATES_BBOX = [
    ("Schleswig-Holstein", 53.35, 55.06, 7.87, 11.31),
    ("Mecklenburg-Vorpommern", 53.11, 54.69, 10.59, 14.41),
    ("Niedersachsen", 51.30, 53.89, 6.65, 11.60),
    ("Bremen", 53.01, 53.23, 8.48, 8.99),
    ("Hamburg", 53.39, 53.74, 9.73, 10.33),
    ("Brandenburg", 51.36, 53.56, 11.27, 14.77),
    ("Berlin", 52.34, 52.68, 13.09, 13.76),
    ("Sachsen-Anhalt", 51.00, 53.04, 10.56, 13.19),
    ("Nordrhein-Westfalen", 50.32, 52.53, 5.87, 9.46),
    ("Hessen", 49.39, 51.66, 7.77, 10.24),
    ("Thüringen", 50.20, 51.65, 9.88, 12.65),
    ("Sachsen", 50.17, 51.69, 11.87, 15.04),
    ("Rheinland-Pfalz", 48.97, 50.94, 6.11, 8.51),
    ("Saarland", 49.11, 49.64, 6.36, 7.41),
    ("Baden-Württemberg", 47.53, 49.79, 7.51, 10.50),
    ("Bayern", 47.27, 50.56, 8.98, 13.84),
]


def guess_state(lat, lon):
    """Guess German state from coordinates (rough approximation)."""
    for name, lat_min, lat_max, lon_min, lon_max in GERMAN_STATES_BBOX:
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return name
    return ""


def try_brightsky():
    """
    Use the Bright Sky API to collect all DWD observation stations.
    We query at a grid of points across Germany with large max_dist to cover all stations.
    Then deduplicate by dwd_station_id.
    """
    print("Querying Bright Sky API for DWD stations...")

    # Grid points across Germany to ensure we catch all stations
    grid_points = []
    for lat in [47.5, 48.5, 49.5, 50.5, 51.5, 52.5, 53.5, 54.5]:
        for lon in [6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5, 14.5]:
            grid_points.append((lat, lon))

    seen_ids = set()
    raw_stations = {}

    for lat, lon in grid_points:
        try:
            resp = requests.get(
                "https://api.brightsky.dev/sources",
                params={"lat": lat, "lon": lon, "max_dist": 200000},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            for src in data.get("sources", []):
                sid = src.get("dwd_station_id")
                obs_type = src.get("observation_type")

                # Only include historical observation stations (these are the DWD climate stations)
                if not sid or obs_type not in ("historical", "recent"):
                    continue

                if sid in raw_stations:
                    # Update if this record has a more recent last_record
                    existing = raw_stations[sid]
                    if src.get("last_record", "") > existing.get("last_record", ""):
                        raw_stations[sid] = src
                else:
                    raw_stations[sid] = src

        except Exception as e:
            print(f"  Warning: query at ({lat},{lon}) failed: {e}")

    print(f"  Found {len(raw_stations)} unique DWD stations from Bright Sky")

    stations = []
    for sid, src in raw_stations.items():
        station_id = str(sid).zfill(5)
        name = src.get("station_name", "")
        lat = src.get("lat")
        lon = src.get("lon")
        elevation = src.get("height")

        first_record = src.get("first_record", "")
        last_record = src.get("last_record", "")

        # Parse dates: "2024-01-01T00:00:00+00:00" -> "20240101"
        von_datum = first_record[:10].replace("-", "") if first_record else ""
        bis_datum = last_record[:10].replace("-", "") if last_record else ""

        # Filter: bis_datum year >= 2024
        if len(bis_datum) >= 4:
            year = int(bis_datum[:4])
            if year < 2024:
                continue
        else:
            continue

        if lat is not None:
            lat = round(float(lat), 4)
        if lon is not None:
            lon = round(float(lon), 4)
        if elevation is not None:
            elevation = int(float(elevation))

        state = guess_state(lat, lon) if lat and lon else ""

        stations.append({
            "id": station_id,
            "name": name,
            "lat": lat,
            "lon": lon,
            "elevation": elevation,
            "state": state,
            "from": von_datum,
            "to": bis_datum,
        })

    return stations


def main():
    stations = None

    # Try direct DWD download first
    try:
        print("Attempting direct DWD download...")
        stations = try_direct_download()
        print(f"Direct download succeeded: {len(stations)} stations")
    except Exception as e:
        print(f"Direct download failed: {e}")

    # Fall back to Bright Sky API
    if not stations:
        try:
            stations = try_brightsky()
            print(f"Bright Sky succeeded: {len(stations)} stations")
        except Exception as e:
            print(f"Bright Sky failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    stations.sort(key=lambda s: s["id"])

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(stations, f, ensure_ascii=False, indent=2)

    print(f"\nWrote {len(stations)} stations to {OUTPUT}")
    for s in stations[:5]:
        print(f"  {s}")
    print(f"  ... and {len(stations) - 5} more")


if __name__ == "__main__":
    main()
