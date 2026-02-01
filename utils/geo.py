"""
Geo-Mapping: PLZ → nächste DWD-Wetterstation.

Verwendet Haversine-Distanz für die Berechnung.
"""

import json
import math
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _haversine(lat1, lon1, lat2, lon2):
    """Haversine-Distanz in km zwischen zwei Koordinaten."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class GeoMapper:
    def __init__(self):
        self._plz_coords = None
        self._stations = None

    @property
    def plz_coords(self):
        if self._plz_coords is None:
            path = os.path.join(DATA_DIR, "plz_coordinates.json")
            with open(path, "r") as f:
                self._plz_coords = json.load(f)
        return self._plz_coords

    @property
    def stations(self):
        if self._stations is None:
            path = os.path.join(DATA_DIR, "dwd_stations.json")
            with open(path, "r") as f:
                self._stations = json.load(f)
        return self._stations

    def get_plz_coordinates(self, plz: str) -> tuple:
        """Koordinaten für eine PLZ zurückgeben."""
        plz = plz.strip().zfill(5)
        coords = self.plz_coords.get(plz)
        if coords:
            return tuple(coords)
        return None

    def find_nearest_station(self, plz: str) -> dict:
        """Nächste DWD-Wetterstation für eine PLZ finden."""
        coords = self.get_plz_coordinates(plz)
        if coords is None:
            return None

        lat, lon = coords
        best = None
        best_dist = float("inf")

        for station in self.stations:
            dist = _haversine(lat, lon, station["lat"], station["lon"])
            if dist < best_dist:
                best_dist = dist
                best = station

        if best:
            return {
                "station_id": best["id"],
                "station_name": best["name"],
                "distance_km": round(best_dist, 1),
                "lat": best["lat"],
                "lon": best["lon"],
            }
        return None


# Singleton-Instanz
geo_mapper = GeoMapper()
