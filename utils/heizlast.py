"""
Heizlastberechnung aus Teilverbrauch und Außentemperatur.

Methode: Heizgradtage-basierte Extrapolation mit Grundlast-Trennung.

Modell:
    Der Gasverbrauch wird über Heizgradtage (HGT) auf die
    Norm-Außentemperatur extrapoliert. Die Grundlast (Warmwasser)
    wird dabei über die Personenzahl geschätzt oder automatisch
    aus Nicht-Heiztagen abgeleitet.

    Q_tag = a + b * max(0, T_heizgrenze - T_aussen)
    a = Grundlast/Warmwasser [kWh/Tag]
    b = Wärmeverlustkennwert [kWh/(Tag*K)]

    Heizlast_Norm = b * (T_innen - T_norm) / 24 [kW]

Heizgradtage (HGT):
    HGT = Summe(max(0, T_heizgrenze - T_aussen_tag)) fuer alle Tage
"""

# Typischer Warmwasserverbrauch pro Person und Tag [kWh]
# ca. 35 Liter/Person/Tag, dT=35K, -> ~1.4 kWh thermisch
# Mit Verlusten Speicher/Zirkulation: ~3 kWh/Person/Tag (Brennstoffenergie)
WW_KWH_PRO_PERSON_TAG = 3.0

# Spezifischer Heizwaermebedarf nach Baujahr [W/m2]
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

# Norm-Aussentemperaturen nach Region (vereinfacht, nach DIN/TS 12831)
NORM_AUSSENTEMPERATUR = {
    "01": -14, "02": -14, "03": -13, "04": -14, "06": -14, "07": -14,
    "08": -15, "09": -15,
    "10": -14, "12": -14, "13": -14, "14": -14, "15": -14, "16": -14,
    "17": -12, "18": -12, "19": -12,
    "20": -12, "21": -12, "22": -12, "23": -12, "24": -12, "25": -10,
    "26": -10, "27": -10, "28": -10, "29": -12,
    "30": -12, "31": -12, "32": -12, "33": -12, "34": -12, "35": -12,
    "36": -12, "37": -12, "38": -14, "39": -14,
    "40": -10, "41": -10, "42": -10, "44": -10, "45": -10, "46": -10,
    "47": -10, "48": -10, "49": -10,
    "50": -10, "51": -10, "52": -10, "53": -10, "54": -12, "55": -10,
    "56": -10, "57": -12, "58": -12, "59": -12,
    "60": -12, "61": -12, "63": -12, "64": -12, "65": -10, "66": -12,
    "67": -10, "68": -10, "69": -10,
    "70": -12, "71": -12, "72": -14, "73": -12, "74": -12, "75": -14,
    "76": -12, "77": -12, "78": -16, "79": -12,
    "80": -16, "81": -16, "82": -16, "83": -16, "84": -16, "85": -16,
    "86": -16, "87": -18, "88": -16, "89": -16,
    "90": -16, "91": -16, "92": -18, "93": -18, "94": -18, "95": -16,
    "96": -16, "97": -12, "98": -14, "99": -14,
    "43": -10,
}


def get_norm_temperature(plz):
    """Norm-Aussentemperatur fuer eine PLZ ermitteln."""
    prefix2 = plz[:2]
    if prefix2 in NORM_AUSSENTEMPERATUR:
        return NORM_AUSSENTEMPERATUR[prefix2]
    return -12.0


def get_heizlast_schaetzung_baujahr(baujahr, wohnflaeche):
    """Grobe Heizlast-Schaetzung nur aus Baujahr und Wohnflaeche."""
    for (von, bis), (w_min, w_max) in HEIZLAST_NACH_BAUJAHR.items():
        if von <= baujahr <= bis:
            return {
                "min_kw": round(w_min * wohnflaeche / 1000, 2),
                "max_kw": round(w_max * wohnflaeche / 1000, 2),
                "spezifisch_min": w_min,
                "spezifisch_max": w_max,
            }
    return {
        "min_kw": round(50 * wohnflaeche / 1000, 2),
        "max_kw": round(100 * wohnflaeche / 1000, 2),
        "spezifisch_min": 50,
        "spezifisch_max": 100,
    }


def berechne_heizgradtage(daily_temps, t_heizgrenze):
    """
    Heizgradtage aus Tagesmitteltemperaturen berechnen.

    HGT = Summe(max(0, T_heizgrenze - T_aussen_tag))
    """
    hgt = 0.0
    heiztage = 0

    for day, temp in sorted(daily_temps.items()):
        if temp < t_heizgrenze:
            hgt += (t_heizgrenze - temp)
            heiztage += 1

    return {
        "hgt": round(hgt, 1),
        "heiztage": heiztage,
        "alle_tage": len(daily_temps),
    }


def berechne_heizlast(
    gasverbrauch_kwh,
    daily_temps,
    plz,
    wohnflaeche,
    baujahr,
    personen=0,
    t_innen=20.0,
    t_heizgrenze=15.0,
    eta=1.0,
    messdauer_tage=None,
):
    """
    Berechne die Heizlast aus Gasverbrauch und Tagesmitteltemperaturen.

    Methode: Heizgradtage-basiert mit Grundlast-Trennung.

    Parameter:
        gasverbrauch_kwh: Gasverbrauch im Messzeitraum [kWh] (Brennstoffenergie)
        daily_temps: Dict {Datum: Tagesmitteltemperatur}
        plz: Postleitzahl
        wohnflaeche: Wohnflaeche [m2]
        baujahr: Baujahr des Gebaeudes
        personen: Anzahl Personen im Haushalt (0=automatisch schaetzen)
        t_innen: Innentemperatur [C]
        t_heizgrenze: Heizgrenztemperatur [C]
        eta: Anlagen-Jahresnutzungsgrad (1.0 = kWh-Eingabe/Nutzwaerme)
        messdauer_tage: Exakter Messzeitraum in Tagen (Dezimalwert, z.B. 2.0)
                        Wenn None, wird len(daily_temps) als Fallback verwendet.
    """
    if not daily_temps:
        return {"error": "Keine Temperaturdaten vorhanden."}

    kalendertage = len(daily_temps)
    if kalendertage == 0:
        return {"error": "Messzeitraum darf nicht 0 Tage sein."}

    # Exakter Messzeitraum: vom Nutzer angegeben oder Fallback auf Kalendertage
    tage = messdauer_tage if messdauer_tage is not None and messdauer_tage > 0 else float(kalendertage)
    if tage <= 0:
        return {"error": "Messzeitraum darf nicht 0 Tage sein."}

    t_norm = get_norm_temperature(plz)

    # Nutzwaerme aus Brennstoffverbrauch
    q_nutz = gasverbrauch_kwh * eta

    # Heizgradtage berechnen (aus Kalendertagen der Wetterdaten)
    hgt_data = berechne_heizgradtage(daily_temps, t_heizgrenze)
    hgt_kalendertage = hgt_data["hgt"]
    heiztage_kalender = hgt_data["heiztage"]
    nicht_heiztage_kalender = kalendertage - heiztage_kalender

    # HGT auf exakten Messzeitraum normieren
    # Wenn z.B. 3 Kalendertage aber nur 2.0 Messtage: HGT * (2.0/3)
    hgt_faktor = tage / kalendertage if kalendertage > 0 else 1.0
    hgt = round(hgt_kalendertage * hgt_faktor, 1)
    heiztage = round(heiztage_kalender * hgt_faktor, 1)
    nicht_heiztage = round(nicht_heiztage_kalender * hgt_faktor, 1)

    if hgt <= 0:
        return {
            "error": (
                "Keine Heiztage im Zeitraum "
                "(alle Tage ueber {}C). "
                "Waehle einen kaelteren Zeitraum oder erhoehe die Heizgrenze."
            ).format(t_heizgrenze)
        }

    # Warmwasser-/Grundlast-Trennung (basierend auf exaktem Messzeitraum)
    if personen > 0:
        # Personen-basierte WW-Schaetzung (beste Methode)
        q_ww_tag = personen * WW_KWH_PRO_PERSON_TAG
        q_ww_gesamt = q_ww_tag * tage
        q_heiz = max(0, q_nutz - q_ww_gesamt)
        warmwasser_kwh = q_ww_gesamt
        warmwasser_anteil = round(q_ww_gesamt / q_nutz * 100, 1) if q_nutz > 0 else 0
        grundlast_methode = "personen"
    elif nicht_heiztage_kalender >= 3:
        # Nicht-Heiztage als Proxy
        q_ww_gesamt = q_nutz * nicht_heiztage_kalender / kalendertage
        q_heiz = q_nutz - q_ww_gesamt
        warmwasser_kwh = q_ww_gesamt
        warmwasser_anteil = round(q_ww_gesamt / q_nutz * 100, 1) if q_nutz > 0 else 0
        grundlast_methode = "automatisch"
    else:
        # Fallback: pauschal 12%
        warmwasser_anteil = 12.0
        q_heiz = q_nutz * 0.88
        warmwasser_kwh = q_nutz * 0.12
        grundlast_methode = "pauschal"

    # Waermeverlustkennwert b [kWh/(Kd)]
    b = q_heiz / hgt if hgt > 0 else 0

    # Heizlast bei Norm-Aussentemperatur
    delta_t_norm = t_innen - t_norm
    heizlast_norm = b * delta_t_norm / 24

    # Mittlere Heizleistung (ueber exakten Messzeitraum)
    p_heiz_mittel = q_heiz / (tage * 24) if tage > 0 else 0

    # Mittlere Temperatur (aus Kalendertagen)
    heiz_temps = [t for d, t in daily_temps.items() if t < t_heizgrenze]
    t_avg_heiztage = sum(heiz_temps) / len(heiz_temps) if heiz_temps else 0
    t_avg_alle = sum(daily_temps.values()) / kalendertage if kalendertage > 0 else 0

    # Spezifische Heizlast
    spezifisch = heizlast_norm * 1000 / wohnflaeche if wohnflaeche > 0 else 0

    # Baujahr-Schaetzung
    schaetzung = get_heizlast_schaetzung_baujahr(baujahr, wohnflaeche)

    # Sensitivitaetsanalyse
    sensitivitaet = berechne_sensitivitaet(
        q_nutz=q_nutz, daily_temps=daily_temps, tage=tage,
        t_innen=t_innen, t_norm=t_norm, wohnflaeche=wohnflaeche,
        messdauer_tage=tage,
    )

    # Zeitraum-Warnung
    warnungen = []
    if tage < 7:
        warnungen.append(
            "Kurzer Messzeitraum ({} Tage). "
            "Empfohlen sind mindestens 7 Tage fuer zuverlaessige Ergebnisse.".format(
                round(tage, 1) if tage != int(tage) else int(tage)
            )
        )
    if t_avg_alle > 10:
        warnungen.append(
            "Hohe Durchschnittstemperatur ({} C). "
            "Kältere Zeitraeume (unter 5C) liefern genauere Ergebnisse.".format(t_avg_alle)
        )
    if nicht_heiztage > heiztage and nicht_heiztage > 5:
        warnungen.append(
            "{} von {} Tagen lagen ueber der Heizgrenze ({}C) "
            "und wurden nicht fuer die Heizlast beruecksichtigt.".format(
                round(nicht_heiztage, 1), round(tage, 1), t_heizgrenze
            )
        )

    return {
        "heizlast_kw": round(heizlast_norm, 2),
        "heizlast_spezifisch_w_m2": round(spezifisch, 1),
        "mittlere_heizleistung_kw": round(p_heiz_mittel, 2),
        "norm_aussentemperatur": t_norm,
        "heizenergie_kwh": round(q_heiz, 1),
        "nutzwaerme_kwh": round(q_nutz, 1),
        "warmwasser_kwh": round(warmwasser_kwh, 1),
        "warmwasser_anteil_pct": warmwasser_anteil,
        "grundlast_methode": grundlast_methode,
        "waermeverlustkennwert_b": round(b, 3),
        "heizgradtage": hgt,
        "heizgradtage_kalendertage": hgt_kalendertage,
        "heiztage": round(heiztage, 1),
        "nicht_heiztage": round(nicht_heiztage, 1),
        "heizgrenze": t_heizgrenze,
        "t_avg_heiztage": round(t_avg_heiztage, 1),
        "t_avg_alle": round(t_avg_alle, 1),
        "schaetzung_baujahr": schaetzung,
        "empfehlung_waermepumpe_kw": round(heizlast_norm * 1.1, 1),
        "sensitivitaet": sensitivitaet,
        "eta": eta,
        "messdauer_tage": round(tage, 2),
        "kalendertage": kalendertage,
        "warnungen": warnungen,
    }


def berechne_sensitivitaet(q_nutz, daily_temps, tage, t_innen, t_norm, wohnflaeche, messdauer_tage=None):
    """
    Sensitivitaetsanalyse: Berechne Heizlast-Bandbreite fuer verschiedene
    Heizgrenzen und Warmwasseranteile.
    """
    varianten = []
    delta_t_norm = t_innen - t_norm
    kalendertage = len(daily_temps)
    mess_tage = messdauer_tage if messdauer_tage is not None and messdauer_tage > 0 else float(kalendertage)
    hgt_faktor = mess_tage / kalendertage if kalendertage > 0 else 1.0

    for label_hg, t_hg in [("14", 14.0), ("15", 15.0), ("16", 16.0)]:
        hgt_data = berechne_heizgradtage(daily_temps, t_hg)
        hgt = hgt_data["hgt"] * hgt_faktor  # Auf exakten Messzeitraum normieren

        if hgt > 0:
            for ww_pct in [8, 12, 18]:
                q_heiz = q_nutz * (1 - ww_pct / 100)
                b_var = q_heiz / hgt
                hl = b_var * delta_t_norm / 24
                varianten.append({
                    "heizgrenze": int(t_hg),
                    "warmwasser_pct": ww_pct,
                    "heizlast_kw": round(hl, 2),
                    "spezifisch_w_m2": round(hl * 1000 / wohnflaeche, 1) if wohnflaeche > 0 else 0,
                })

    if not varianten:
        return {"min_kw": 0, "max_kw": 0, "varianten": []}

    alle_kw = [v["heizlast_kw"] for v in varianten]
    return {
        "min_kw": round(min(alle_kw), 2),
        "max_kw": round(max(alle_kw), 2),
        "varianten": varianten,
    }
