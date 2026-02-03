"""
Heizlastrechner - Flask Web-App

Berechnet die Heizlast eines Gebaeudes aus:
- Gasverbrauch ueber einen beliebigen Zeitraum
- Wetterdaten der naechsten DWD-Station (via Bright Sky)
- Wohnflaeche, Baujahr, Personenzahl
"""

from datetime import date, datetime

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
    """Naechste Wetterstation fuer eine PLZ finden."""
    plz = request.args.get("plz", "").strip()
    if not plz or len(plz) != 5:
        return jsonify({"error": "Bitte eine gueltige 5-stellige PLZ eingeben."}), 400

    station = geo_mapper.find_nearest_station(plz)
    if not station:
        return jsonify({"error": "Keine Wetterstation fuer PLZ {} gefunden.".format(plz)}), 404

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
            return jsonify({"error": "Feld '{}' fehlt.".format(field)}), 400

    plz = str(data["plz"]).strip().zfill(5)
    datum_von = data["datum_von"]
    datum_bis = data["datum_bis"]

    # Datetime mit Uhrzeit parsen (Format: "YYYY-MM-DDTHH:MM" oder "YYYY-MM-DD")
    try:
        if "T" in datum_von:
            dt_von = datetime.strptime(datum_von, "%Y-%m-%dT%H:%M")
        else:
            dt_von = datetime.strptime(datum_von, "%Y-%m-%d")
        if "T" in datum_bis:
            dt_bis = datetime.strptime(datum_bis, "%Y-%m-%dT%H:%M")
        else:
            dt_bis = datetime.strptime(datum_bis, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Ungueltiges Datumsformat."}), 400

    now = datetime.now()
    if dt_bis > now:
        dt_bis = now
    if dt_von > dt_bis:
        return jsonify({"error": "Das Startdatum liegt nach dem Enddatum."}), 400
    if dt_von > now:
        return jsonify({"error": "Das Startdatum liegt in der Zukunft."}), 400

    # Exakte Messdauer in Tagen (Dezimalwert)
    messdauer_tage = (dt_bis - dt_von).total_seconds() / 86400.0
    if messdauer_tage <= 0:
        return jsonify({"error": "Der Messzeitraum muss groesser als 0 sein."}), 400

    # Datum-only Strings fuer die DWD-API (braucht nur Tage)
    datum_von_api = dt_von.strftime("%Y-%m-%d")
    datum_bis_api = dt_bis.strftime("%Y-%m-%d")

    try:
        gasverbrauch = float(data["gasverbrauch"])
        wohnflaeche = float(data["wohnflaeche"])
        baujahr = int(data["baujahr"])
    except (ValueError, TypeError):
        return jsonify({"error": "Ungueltige Zahlenwerte."}), 400

    # Optionale erweiterte Parameter
    personen = int(data.get("personen", 0) or 0)
    t_heizgrenze = float(data.get("heizgrenze", 15.0) or 15.0)
    brennwert = float(data.get("brennwert", 11.2) or 11.2)
    zustandszahl = float(data.get("zustandszahl", 0.95) or 0.95)
    eta = float(data.get("eta", 1.0) or 1.0)
    einheit = data.get("einheit", "kwh")

    # Gas-Umrechnung
    if einheit == "m3":
        gasverbrauch_kwh = gasverbrauch * brennwert * zustandszahl
    else:
        gasverbrauch_kwh = gasverbrauch

    # Naechste Wetterstation finden
    station = geo_mapper.find_nearest_station(plz)
    if not station:
        return jsonify({"error": "Keine Wetterstation fuer PLZ {} gefunden.".format(plz)}), 404

    # Temperaturdaten abrufen (API braucht nur Datum ohne Uhrzeit)
    temp_data = get_temperature_data(
        station["lat"], station["lon"], datum_von_api, datum_bis_api
    )
    if "error" in temp_data:
        return jsonify(temp_data), 500

    daily_temps = temp_data.get("daily_means", {})

    # Temperaturdaten auf tatsaechlichen Messzeitraum begrenzen
    # Die Bright Sky API liefert manchmal einen zusaetzlichen Tag
    daily_temps = {
        day: temp for day, temp in daily_temps.items()
        if datum_von_api <= day <= datum_bis_api
    }

    # Heizlast berechnen
    result = berechne_heizlast(
        gasverbrauch_kwh=gasverbrauch_kwh,
        daily_temps=daily_temps,
        plz=plz,
        wohnflaeche=wohnflaeche,
        baujahr=baujahr,
        personen=personen,
        t_heizgrenze=t_heizgrenze,
        eta=eta,
        messdauer_tage=messdauer_tage,
    )

    if "error" in result:
        return jsonify(result), 400

    # Zusaetzliche Infos anhaengen
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
        "messdauer_tage": round(messdauer_tage, 2),
        "gasverbrauch_kwh": round(gasverbrauch_kwh, 1),
        "gasverbrauch_roh": gasverbrauch,
        "einheit": einheit,
        "wohnflaeche": wohnflaeche,
        "baujahr": baujahr,
        "personen": personen,
        "brennwert": brennwert,
        "zustandszahl": zustandszahl,
        "eta": eta,
        "heizgrenze": t_heizgrenze,
    }
    result["daily_temps"] = daily_temps

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
