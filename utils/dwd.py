"""
DWD Open Data Anbindung.

Lädt Tagesmitteltemperaturen von der Bright Sky API (DWD-Spiegel).
Bright Sky ist kostenlos, braucht keinen API-Key und hat CORS-Support.

API-Doku: https://brightsky.dev/docs/
"""

import requests
from datetime import datetime, timedelta


BRIGHTSKY_URL = "https://api.brightsky.dev/weather"


def get_temperature_data(lat: float, lon: float, date_from: str, date_to: str) -> dict:
    """
    Tagesmitteltemperaturen von Bright Sky (DWD-Daten) abrufen.

    Parameter:
        lat: Breitengrad der Wetterstation
        lon: Längengrad der Wetterstation
        date_from: Startdatum (YYYY-MM-DD)
        date_to: Enddatum (YYYY-MM-DD)

    Rückgabe:
        Dictionary mit Temperaturdaten und Statistiken
    """
    # Bright Sky liefert stündliche Daten, wir aggregieren zu Tagesmitteln
    all_daily_temps = {}

    # Bright Sky limitiert auf ~10 Tage pro Request, also aufteilen
    dt_from = datetime.strptime(date_from, "%Y-%m-%d")
    dt_to = datetime.strptime(date_to, "%Y-%m-%d")

    current = dt_from
    while current <= dt_to:
        chunk_end = min(current + timedelta(days=9), dt_to)

        params = {
            "lat": lat,
            "lon": lon,
            "date": current.strftime("%Y-%m-%dT00:00:00"),
            "last_date": chunk_end.strftime("%Y-%m-%dT23:59:59"),
        }

        try:
            resp = requests.get(BRIGHTSKY_URL, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            return {"error": f"DWD-Datenabruf fehlgeschlagen: {str(e)}"}

        for entry in data.get("weather", []):
            ts = entry.get("timestamp", "")
            temp = entry.get("temperature")
            if temp is not None and ts:
                day = ts[:10]
                if day not in all_daily_temps:
                    all_daily_temps[day] = []
                all_daily_temps[day].append(temp)

        current = chunk_end + timedelta(days=1)

    if not all_daily_temps:
        return {"error": "Keine Temperaturdaten für den Zeitraum gefunden."}

    # Tagesmittel berechnen
    daily_means = {}
    for day, temps in sorted(all_daily_temps.items()):
        daily_means[day] = round(sum(temps) / len(temps), 1)

    temperatures = list(daily_means.values())
    avg_temp = sum(temperatures) / len(temperatures)
    min_temp = min(temperatures)
    max_temp = max(temperatures)

    return {
        "daily_means": daily_means,
        "avg_temperature": round(avg_temp, 1),
        "min_temperature": round(min_temp, 1),
        "max_temperature": round(max_temp, 1),
        "num_days": len(daily_means),
    }
