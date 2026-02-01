"""
Heizlastrechner - Flask Web-App

Berechnet die Heizlast eines Gebäudes aus:
- Gasverbrauch über einen beliebigen Zeitraum
- Wetterdaten der nächsten DWD-Station
- Wohnfläche und Baujahr
"""

from flask import Flask, render_template, request, jsonify
from utils.geo import geo_mapper
from utils.dwd import get_temperature_data
from utils.heizlast import berechne_heizlast, get_heizlast_schaetzung_baujahr

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/station", methods=["GET"])
def api_station():
    """Nächste Wetterstation für eine PLZ finden."""
    plz = request.args.get("plz", "").strip()
    if not plz or len(plz) != 5:
        return jsonify({"error": "Bitte eine gültige 5-stellige PLZ eingeben."}), 400

    station = geo_mapper.find_nearest_station(plz)
    if not station:
        return jsonify({"error": f"Keine Wetterstation für PLZ {plz} gefunden."}), 404

    return jsonify(station)


@app.route("/api/berechnen", methods=["POST"])
def api_berechnen():
    """Heizlast berechnen."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Keine Daten empfangen."}), 400

    # Eingaben validieren
    required = ["plz", "datum_von", "datum_bis", "gasverbrauch", "wohnflaeche", "baujahr"]
    for field in required:
        if field not in data or data[field] in (None, ""):
            return jsonify({"error": f"Feld '{field}' fehlt."}), 400

    plz = str(data["plz"]).strip().zfill(5)
    datum_von = data["datum_von"]
    datum_bis = data["datum_bis"]

    try:
        gasverbrauch = float(data["gasverbrauch"])
        wohnflaeche = float(data["wohnflaeche"])
        baujahr = int(data["baujahr"])
    except (ValueError, TypeError):
        return jsonify({"error": "Ungültige Zahlenwerte."}), 400

    einheit = data.get("einheit", "kwh")
    # Umrechnung m³ Gas → kWh (Brennwert ca. 11.2 kWh/m³, Zustandszahl ca. 0.95)
    if einheit == "m3":
        gasverbrauch_kwh = gasverbrauch * 11.2 * 0.95
    else:
        gasverbrauch_kwh = gasverbrauch

    # Nächste Wetterstation finden
    station = geo_mapper.find_nearest_station(plz)
    if not station:
        return jsonify({"error": f"Keine Wetterstation für PLZ {plz} gefunden."}), 404

    # Temperaturdaten abrufen
    temp_data = get_temperature_data(
        station["lat"], station["lon"], datum_von, datum_bis
    )
    if "error" in temp_data:
        return jsonify(temp_data), 500

    # Heizlast berechnen
    result = berechne_heizlast(
        gasverbrauch_kwh=gasverbrauch_kwh,
        tage=temp_data["num_days"],
        mittlere_aussentemperatur=temp_data["avg_temperature"],
        plz=plz,
        wohnflaeche=wohnflaeche,
        baujahr=baujahr,
    )

    if "error" in result:
        return jsonify(result), 400

    # Zusätzliche Infos anhängen
    result["station"] = station
    result["temperatur"] = {
        "mittelwert": temp_data["avg_temperature"],
        "minimum": temp_data["min_temperature"],
        "maximum": temp_data["max_temperature"],
        "tage": temp_data["num_days"],
    }
    result["eingaben"] = {
        "plz": plz,
        "datum_von": datum_von,
        "datum_bis": datum_bis,
        "gasverbrauch_kwh": round(gasverbrauch_kwh, 1),
        "wohnflaeche": wohnflaeche,
        "baujahr": baujahr,
    }
    result["daily_temps"] = temp_data.get("daily_means", {})

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
