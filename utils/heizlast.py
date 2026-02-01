"""
Heizlastberechnung aus Teilverbrauch und Außentemperatur.

Methode: Lineare Extrapolation des gemessenen Verbrauchs
auf die Norm-Außentemperatur (nach DIN EN 12831).

Formel:
    Heizlast_Norm [kW] = Q_heiz / (t_mess * 24) * (T_innen - T_Norm) / (T_innen - T_avg)

Dabei:
    Q_heiz      = Heizenergieverbrauch im Messzeitraum [kWh]
    t_mess      = Dauer des Messzeitraums [Tage]
    T_innen     = Raumtemperatur (Standard: 20°C)
    T_Norm      = Norm-Außentemperatur des Standorts [°C]
    T_avg       = Mittlere Außentemperatur im Messzeitraum [°C]
"""

# Spezifischer Heizwärmebedarf nach Baujahr [W/m²]
# Untere und obere Schätzung
HEIZLAST_NACH_BAUJAHR = {
    (0, 1918): (150, 170),
    (1919, 1948): (130, 160),
    (1949, 1957): (130, 150),
    (1958, 1968): (120, 140),
    (1969, 1978): (100, 130),
    (1979, 1983): (90, 120),
    (1984, 1994): (70, 100),
    (1995, 2001): (50, 75),
    (2002, 2009): (40, 60),
    (2010, 2015): (30, 50),
    (2016, 2099): (25, 45),
}

# Norm-Außentemperaturen nach Region (vereinfacht, nach DIN/TS 12831)
# Schlüssel: erste 1-2 Ziffern der PLZ → T_Norm [°C]
NORM_AUSSENTEMPERATUR = {
    "01": -14, "02": -14, "03": -13, "04": -14, "06": -14, "07": -14,
    "08": -15, "09": -15,  # Sachsen, Thüringen, Sachsen-Anhalt
    "10": -14, "12": -14, "13": -14, "14": -14, "15": -14, "16": -14,
    "17": -12, "18": -12, "19": -12,  # Berlin, Brandenburg, MV
    "20": -12, "21": -12, "22": -12, "23": -12, "24": -12, "25": -10,
    "26": -10, "27": -10, "28": -10, "29": -12,  # Hamburg, SH, Niedersachsen Nord
    "30": -12, "31": -12, "32": -12, "33": -12, "34": -12, "35": -12,
    "36": -12, "37": -12, "38": -14, "39": -14,  # Niedersachsen, Hessen Nord
    "40": -10, "41": -10, "42": -10, "44": -10, "45": -10, "46": -10,
    "47": -10, "48": -10, "49": -10,  # NRW
    "50": -10, "51": -10, "52": -10, "53": -10, "54": -12, "55": -10,
    "56": -10, "57": -12, "58": -12, "59": -12,  # NRW, RLP
    "60": -12, "61": -12, "63": -12, "64": -12, "65": -10, "66": -12,
    "67": -10, "68": -10, "69": -10,  # Hessen, Saarland, RLP
    "70": -12, "71": -12, "72": -14, "73": -12, "74": -12, "75": -14,
    "76": -12, "77": -12, "78": -16, "79": -12,  # Baden-Württemberg
    "80": -16, "81": -16, "82": -16, "83": -16, "84": -16, "85": -16,
    "86": -16, "87": -18, "88": -16, "89": -16,  # Bayern Süd
    "90": -16, "91": -16, "92": -18, "93": -18, "94": -18, "95": -16,
    "96": -16, "97": -12, "98": -14, "99": -14,  # Bayern, Thüringen
    "43": -10,  # NRW
}


def get_norm_temperature(plz: str) -> float:
    """Norm-Außentemperatur für eine PLZ ermitteln."""
    prefix2 = plz[:2]
    if prefix2 in NORM_AUSSENTEMPERATUR:
        return NORM_AUSSENTEMPERATUR[prefix2]
    # Fallback: Mittelwert Deutschland
    return -12.0


def get_heizlast_schaetzung_baujahr(baujahr: int, wohnflaeche: float) -> dict:
    """Grobe Heizlast-Schätzung nur aus Baujahr und Wohnfläche."""
    for (von, bis), (w_min, w_max) in HEIZLAST_NACH_BAUJAHR.items():
        if von <= baujahr <= bis:
            return {
                "min_kw": round(w_min * wohnflaeche / 1000, 2),
                "max_kw": round(w_max * wohnflaeche / 1000, 2),
                "spezifisch_min": w_min,
                "spezifisch_max": w_max,
            }
    # Fallback für unbekanntes Baujahr
    return {
        "min_kw": round(50 * wohnflaeche / 1000, 2),
        "max_kw": round(100 * wohnflaeche / 1000, 2),
        "spezifisch_min": 50,
        "spezifisch_max": 100,
    }


def berechne_heizlast(
    gasverbrauch_kwh: float,
    tage: int,
    mittlere_aussentemperatur: float,
    plz: str,
    wohnflaeche: float,
    baujahr: int,
    t_innen: float = 20.0,
    warmwasser_anteil: float = 0.12,
) -> dict:
    """
    Berechne die Norm-Heizlast aus dem gemessenen Gasverbrauch.

    Parameter:
        gasverbrauch_kwh: Gasverbrauch im Messzeitraum [kWh]
        tage: Anzahl der Messtage
        mittlere_aussentemperatur: Mittlere Außentemperatur im Zeitraum [°C]
        plz: Postleitzahl (5-stellig)
        wohnflaeche: Wohnfläche [m²]
        baujahr: Baujahr des Gebäudes
        t_innen: Innentemperatur [°C], Standard 20°C
        warmwasser_anteil: Warmwasseranteil am Gasverbrauch (0-1), Standard 12%

    Rückgabe:
        Dictionary mit Berechnungsergebnissen
    """
    t_norm = get_norm_temperature(plz)

    # Warmwasseranteil abziehen
    q_heiz = gasverbrauch_kwh * (1 - warmwasser_anteil)

    # Mittlere Heizleistung im Messzeitraum [kW]
    stunden = tage * 24
    if stunden == 0:
        return {"error": "Messzeitraum darf nicht 0 Tage sein."}

    p_heiz_mess = q_heiz / stunden

    # Temperaturdifferenz im Messzeitraum
    delta_t_mess = t_innen - mittlere_aussentemperatur
    if delta_t_mess <= 0:
        return {"error": "Die Außentemperatur muss unter der Innentemperatur liegen."}

    # Temperaturdifferenz bei Norm-Außentemperatur
    delta_t_norm = t_innen - t_norm

    # Extrapolation auf Norm-Außentemperatur
    heizlast_norm = p_heiz_mess * (delta_t_norm / delta_t_mess)

    # Spezifische Heizlast
    spezifisch = heizlast_norm * 1000 / wohnflaeche if wohnflaeche > 0 else 0

    # Vergleich mit Baujahr-Schätzung
    schaetzung = get_heizlast_schaetzung_baujahr(baujahr, wohnflaeche)

    return {
        "heizlast_kw": round(heizlast_norm, 2),
        "heizlast_spezifisch_w_m2": round(spezifisch, 1),
        "mittlere_heizleistung_kw": round(p_heiz_mess, 2),
        "norm_aussentemperatur": t_norm,
        "heizenergie_kwh": round(q_heiz, 1),
        "schaetzung_baujahr": schaetzung,
        "empfehlung_waermepumpe_kw": round(heizlast_norm * 1.1, 1),  # 10% Sicherheit
    }
