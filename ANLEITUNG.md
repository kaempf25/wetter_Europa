# BEDIENUNGSANLEITUNG
# Heizlastrechner – AK Energy Consulting
# Komplett-Anleitung für Verwaltung und Änderungen

Stand: Februar 2026

---

## Inhaltsverzeichnis

1. [Überblick: Wie hängt alles zusammen?](#1-überblick)
2. [Wo liegt das Projekt auf meinem Mac?](#2-wo-liegt-das-projekt)
3. [Terminal öffnen und zum Projekt navigieren](#3-terminal-öffnen)
4. [Änderungen mit Claude Code vornehmen](#4-änderungen-mit-claude)
5. [Änderungen manuell vornehmen (ohne Claude)](#5-änderungen-manuell)
6. [Wie kommen Änderungen auf die Webseite?](#6-änderungen-live-schalten)
7. [Render.com verwalten](#7-rendercom)
8. [WordPress/Elementor: iFrame verwalten](#8-wordpress)
9. [Wichtige Dateien und was sie tun](#9-dateien)
10. [Häufige Änderungen – Schritt für Schritt](#10-beispiele)
11. [Problemlösung](#11-probleme)
12. [Wichtige Links und Zugänge](#12-links)

---

## 1. Überblick

### Wie hängt alles zusammen?

Der Heizlastrechner besteht aus mehreren Bausteinen:

```
┌─────────────────────────────────────────────────────────────┐
│                    IHR MAC (iCloud Drive)                    │
│                                                             │
│   Ordner: HEIZLAST-RECHNER                                 │
│   Hier liegen alle Dateien (Code, Bilder, Daten)           │
│   Sie bearbeiten die Dateien hier (mit Claude oder manuell)│
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ "git push" (hochladen)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      GITHUB.COM                             │
│                                                             │
│   Repository: kaempf25/wetter_Europa                        │
│   Speichert alle Versionen des Codes                        │
│   Dient als Brücke zwischen Ihrem Mac und dem Server        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ automatisch (bei jedem Push)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                     RENDER.COM                              │
│                                                             │
│   URL: https://heizlastberechnung.onrender.com              │
│   Hier läuft die App. Render holt sich den Code von GitHub  │
│   und startet den Rechner als Webseite.                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ eingebettet per iFrame
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              IHRE WORDPRESS-SEITE                            │
│                                                             │
│   ak-energyconsulting.de (auf Strato)                       │
│   Zeigt den Rechner in einem iFrame an                      │
│   Muss nur geändert werden, wenn sich die Render-URL ändert │
└─────────────────────────────────────────────────────────────┘
```

### Der Ablauf bei jeder Änderung (Kurzfassung):

1. Sie ändern etwas am Code (auf Ihrem Mac)
2. Sie laden die Änderung zu GitHub hoch ("git push")
3. Render.com erkennt das automatisch und aktualisiert die App (dauert 1-2 Minuten)
4. Die WordPress-Seite zeigt automatisch die neue Version

**Wichtig:** An WordPress müssen Sie bei normalen Änderungen NICHTS anfassen. WordPress zeigt immer automatisch die aktuelle Version von Render.

---

## 2. Wo liegt das Projekt?

Das Projekt liegt auf Ihrem Mac in der **iCloud**:

```
iCloud Drive / HEIZLAST-RECHNER
```

Der vollständige technische Pfad lautet:

```
/Users/andy/Library/Mobile Documents/com~apple~CloudDocs/HEIZLAST-RECHNER
```

**Tipp:** Im Finder finden Sie es unter **iCloud Drive → HEIZLAST-RECHNER**.

Durch die iCloud wird das Projekt automatisch gesichert und ist auch von anderen Apple-Geräten aus zugänglich.

---

## 3. Terminal öffnen und zum Projekt navigieren

Das Terminal ist die Kommandozeile auf Ihrem Mac. Darüber steuern Sie Git und Claude.

### Terminal öffnen

**Methode 1 (Spotlight):**
1. Drücken Sie gleichzeitig `Cmd + Leertaste`
2. Es erscheint das Spotlight-Suchfeld
3. Tippen Sie: `Terminal`
4. Drücken Sie `Enter`

**Methode 2 (Finder):**
1. Öffnen Sie den Finder
2. Gehen Sie zu: Programme → Dienstprogramme → Terminal
3. Doppelklicken Sie auf Terminal

### Zum Projektordner navigieren

Wenn das Terminal offen ist, sehen Sie eine Zeile wie:

```
andy@Andys-Mac-mini ~ %
```

Tippen Sie jetzt folgenden Befehl und drücken Sie `Enter`:

```
cd ~/Library/Mobile\ Documents/com~apple~CloudDocs/HEIZLAST-RECHNER
```

**Erklärung:**
- `cd` = "change directory" = Ordner wechseln
- `~` = Ihr Home-Verzeichnis (/Users/andy)
- Die Backslashes `\` vor den Leerzeichen sind nötig, weil Ordnernamen mit Leerzeichen im Terminal besonders geschrieben werden müssen

### Prüfen, ob Sie im richtigen Ordner sind

Tippen Sie:

```
ls
```

Sie sollten diese Dateien sehen:

```
ANLEITUNG.md        app.py              data/
requirements.txt    scripts/            static/
templates/          utils/
```

Wenn Sie das sehen, sind Sie im richtigen Ordner.

---

## 4. Änderungen mit Claude Code vornehmen

Claude Code ist ein KI-Assistent, der direkt in Ihrem Terminal arbeitet. Sie beschreiben auf Deutsch, was Sie ändern möchten, und Claude erledigt den Rest.

### Schritt 1: Terminal öffnen und zum Projekt navigieren

(Siehe Kapitel 3 oben)

```
cd ~/Library/Mobile\ Documents/com~apple~CloudDocs/HEIZLAST-RECHNER
```

### Schritt 2: Neueste Version holen

Bevor Sie etwas ändern, holen Sie immer die neueste Version:

```
git pull
```

Falls die Meldung "Already up to date." kommt, ist alles aktuell.

### Schritt 3: Claude Code starten

```
claude
```

Es erscheint der Claude-Prompt. Sie können jetzt lostippen.

**Falls Claude Code nicht installiert ist:**
```
npm install -g @anthropic-ai/claude-code
```

**Falls npm nicht installiert ist:**
Installieren Sie zuerst Node.js von https://nodejs.org (die LTS-Version herunterladen und installieren), dann den Befehl oben wiederholen.

### Schritt 4: Ihre Änderung beschreiben

Tippen Sie einfach auf Deutsch, was Sie möchten. Beispiele:

```
Ändere den Titel von "Heizlastrechner" zu "Wärmepumpen-Rechner"
```

```
Füge ein Feld für die Gebäudeart hinzu (Einfamilienhaus, Mehrfamilienhaus, Reihenhaus)
```

```
Die Erklärung zur Zustandszahl soll kürzer sein
```

```
Ändere die grüne Farbe im Logo auf #1B8C4A
```

```
Füge unten einen Link zu meiner Webseite ak-energyconsulting.de ein
```

Claude bearbeitet die Dateien automatisch und zeigt Ihnen, was geändert wurde.

### Schritt 5: Änderungen hochladen

Wenn Claude fertig ist, sagen Sie:

```
Bitte committe und pushe die Änderungen
```

Claude macht dann automatisch drei Dinge:
1. **git add** – Merkt die geänderten Dateien vor
2. **git commit** – Speichert die Änderung mit einer Beschreibung
3. **git push** – Lädt alles zu GitHub hoch

### Schritt 6: Warten und prüfen

Nach dem Push:
1. Warten Sie 1-2 Minuten (Render baut die App neu)
2. Öffnen Sie im Browser: **https://heizlastberechnung.onrender.com**
3. Drücken Sie `Cmd + Shift + R` (erzwingt Neuladen ohne Cache)
4. Ihre Änderung sollte sichtbar sein

### Schritt 7: Claude beenden

Drücken Sie `Cmd + C` oder tippen Sie:

```
/exit
```

---

## 5. Änderungen manuell vornehmen (ohne Claude)

Für kleine Änderungen (z.B. einen Text korrigieren) brauchen Sie nicht unbedingt Claude.

### Schritt 1: Terminal öffnen und zum Projekt navigieren

```
cd ~/Library/Mobile\ Documents/com~apple~CloudDocs/HEIZLAST-RECHNER
```

### Schritt 2: Neueste Version holen

```
git pull
```

### Schritt 3: Datei im Texteditor öffnen

**Mit TextEdit (auf jedem Mac vorhanden):**
```
open -a TextEdit templates/index.html
```

**Mit VS Code (falls installiert – empfohlen für Code):**
```
code templates/index.html
```

**Direkt im Finder:** Navigieren Sie zu iCloud Drive → HEIZLAST-RECHNER → templates → index.html, Rechtsklick → "Öffnen mit" → TextEdit

### Schritt 4: Änderung machen und speichern

Machen Sie Ihre Änderung und speichern Sie mit `Cmd + S`.

**Tipp:** Mit `Cmd + F` können Sie in TextEdit nach einem Text suchen.

### Schritt 5: Änderung hochladen (3 Befehle im Terminal)

Zurück im Terminal, geben Sie nacheinander ein:

**Befehl 1 – Dateien vormerken:**
```
git add .
```
(Punkt am Ende nicht vergessen! Der Punkt bedeutet "alle geänderten Dateien".)

**Befehl 2 – Änderung beschreiben:**
```
git commit -m "Hier kurz beschreiben, was Sie geändert haben"
```
(Der Text in Anführungszeichen ist die Beschreibung. Z.B. "Telefonnummer im Footer geändert".)

**Befehl 3 – Hochladen:**
```
git push
```

### Schritt 6: Warten und prüfen

1-2 Minuten warten, dann https://heizlastberechnung.onrender.com neu laden (`Cmd + Shift + R`).

---

## 6. Wie kommen Änderungen auf die Webseite?

### Der automatische Weg (nach git push):

```
Sie pushen auf GitHub
        ↓ (sofort)
GitHub informiert Render.com
        ↓ (automatisch)
Render installiert Pakete & startet App neu (~1-2 Min.)
        ↓ (automatisch)
heizlastberechnung.onrender.com zeigt neue Version
        ↓ (automatisch, per iFrame)
ak-energyconsulting.de zeigt neue Version
```

**Sie müssen nichts weiter tun als `git push`!**

### Falls es nicht automatisch klappt:

1. Gehen Sie auf https://dashboard.render.com
2. Loggen Sie sich mit GitHub ein
3. Klicken Sie auf "Heizlastberechnung"
4. Klicken Sie oben rechts auf **"Manual Deploy"** → **"Deploy latest commit"**

---

## 7. Render.com verwalten

### Was ist Render.com?

Render.com ist der Server, auf dem der Heizlastrechner läuft. Ihr Strato-Hosting kann nur PHP (WordPress), aber der Rechner braucht Python. Deshalb läuft er auf Render.

### Einloggen

1. Öffnen Sie: **https://dashboard.render.com**
2. Klicken Sie auf **"Log in"** → **"GitHub"**
3. Sie werden mit Ihrem GitHub-Account (kaempf25) eingeloggt
4. Klicken Sie auf **"Heizlastberechnung"**

### Status prüfen

Oben auf der Seite sehen Sie den Status:
- **"Live"** (grüner Punkt) = Alles läuft. App ist erreichbar.
- **"Building"** (gelber Punkt) = App wird gerade aktualisiert. 1-2 Minuten warten.
- **"Deploy failed"** (roter Punkt) = Fehler. Siehe "Logs ansehen".

### Logs ansehen (bei Fehlern)

1. Im Render-Dashboard auf **"Heizlastberechnung"** klicken
2. Unten sehen Sie den Bereich **"Logs"**
3. Rote Zeilen = Fehlermeldungen
4. Diese Fehlermeldungen können Sie kopieren und Claude zeigen:
   ```
   Ich habe diesen Fehler auf Render: [Fehlertext hier einfügen]
   ```

### Manuell neu deployen

Falls die automatische Erkennung nicht funktioniert:
1. Klicken Sie oben rechts auf **"Manual Deploy"**
2. Wählen Sie **"Deploy latest commit"**

### Kostenlose Instanz: Einschlaf-Verhalten

Die kostenlose Render-Instanz ("Free Tier"):
- **Schläft nach 15 Minuten ohne Besucher ein**
- **Erster Aufruf nach dem Einschlafen dauert ca. 50 Sekunden** (Kaltstart)
- Danach läuft sie normal schnell, solange Besucher kommen
- Für **~7 $/Monat** können Sie auf "Starter" upgraden → App ist immer sofort erreichbar

**Kostenloser Workaround gegen das Einschlafen:**
Richten Sie bei https://uptimerobot.com (kostenlos) einen Monitor ein, der alle 14 Minuten `https://heizlastberechnung.onrender.com` aufruft. Dann schläft die App nie ein.

---

## 8. WordPress/Elementor: iFrame verwalten

### Wann muss ich in WordPress etwas ändern?

**Fast nie.** Der iFrame zeigt automatisch immer die aktuelle Version der App von Render.

Sie müssen nur in WordPress rein, wenn Sie:
- Die **Höhe** des Rahmens ändern wollen (z.B. wenn der Rechner zu viel oder zu wenig Platz hat)
- Die **Render-URL** sich ändert (z.B. wenn Sie den Service umbenennen)
- Die **Seite** verschieben oder löschen wollen

### iFrame bearbeiten

1. Öffnen Sie: **https://ak-energyconsulting.de/wp-admin**
2. Loggen Sie sich ein
3. Gehen Sie links auf **"Seiten"**
4. Finden Sie die Seite mit dem Heizlastrechner und klicken Sie **"Bearbeiten"**
5. Klicken Sie auf **"Mit Elementor bearbeiten"**
6. Klicken Sie auf den **Bereich, wo der Rechner angezeigt wird** (das HTML-Widget)
7. Links erscheint ein Textfeld mit dem HTML-Code
8. Der aktuelle Code sieht so aus:

```html
<iframe
  src="https://heizlastberechnung.onrender.com"
  width="100%"
  height="2200"
  style="border:none; max-width:900px; margin:0 auto; display:block;"
  title="Heizlastrechner - AK Energy Consulting">
</iframe>
```

9. Machen Sie Ihre Änderung
10. Klicken Sie unten links auf **"Aktualisieren"**

### Höhe anpassen

Falls der Rechner zu viel oder zu wenig weißen Platz hat, ändern Sie nur die Zahl nach `height=`:
- Standard: `height="2200"`
- Mehr Platz (wenn unten abgeschnitten): `height="2800"`
- Weniger Platz (wenn zu viel Weißraum): `height="1800"`

---

## 9. Wichtige Dateien und was sie tun

### Ordnerstruktur

```
HEIZLAST-RECHNER/
│
├── app.py                    ← Das Herzstück: Der Flask-Server
│                                Nimmt Eingaben entgegen, ruft Wetterdaten ab,
│                                gibt Ergebnisse zurück
│
├── requirements.txt          ← Liste der Python-Pakete (flask, numpy, gunicorn etc.)
│                                Render installiert diese automatisch
│
├── ANLEITUNG.md              ← Diese Bedienungsanleitung
│
├── templates/
│   └── index.html            ← Die komplette Webseite
│                                HTML (Struktur), CSS-Verweise, JavaScript (Logik)
│                                *** HIER ändern Sie Texte, Überschriften, Felder ***
│
├── static/
│   ├── style.css             ← Das Aussehen: Farben, Abstände, Schriftgrößen,
│   │                            Rahmen, Hintergründe
│   └── logo.svg              ← Das Logo als Vektorgrafik (SVG)
│                                Kann in jedem Browser beliebig groß angezeigt werden
│
├── utils/
│   ├── heizlast.py           ← Die Berechnungslogik:
│   │                            Heizgradtage, Wärmeverlustkennwert, Heizlast,
│   │                            Warmwasser-Trennung, Sensitivitätsanalyse
│   │
│   ├── dwd.py                ← Wetterdaten-Abruf:
│   │                            Holt Temperaturdaten von Bright Sky API (kostenlos)
│   │                            Bright Sky ist ein Spiegel der DWD-Daten
│   │
│   └── geo.py                ← PLZ-Zuordnung:
│                                Findet die nächste DWD-Wetterstation zur PLZ
│                                Berechnet die Entfernung (Haversine-Formel)
│
├── data/
│   ├── plz_coordinates.json  ← 8.298 deutsche Postleitzahlen mit Koordinaten
│   │                            (Breitengrad, Längengrad)
│   └── dwd_stations.json     ← 1.507 DWD-Wetterstationen mit Koordinaten
│
└── scripts/
    └── parse_dwd_stations.py ← Hilfsskript (wurde einmal benutzt, um die Stationsliste
                                 zu erstellen. Wird im Normalbetrieb nicht gebraucht.)
```

### Was ändere ich wo? (Schnellreferenz)

| Ich will...                                  | Welche Datei?                          |
|----------------------------------------------|----------------------------------------|
| Einen Text auf der Seite ändern              | `templates/index.html`                 |
| Den Seitentitel ändern                       | `templates/index.html` (Zeile 6 + 13) |
| Eine Farbe oder Schriftgröße ändern          | `static/style.css`                     |
| Das Logo austauschen                         | `static/logo.svg`                      |
| Die Berechnung ändern                        | `utils/heizlast.py`                    |
| Ein neues Eingabefeld hinzufügen             | `templates/index.html` UND `app.py`    |
| Eine neue Python-Bibliothek verwenden        | `requirements.txt`                     |
| Die Norm-Außentemperaturen ändern            | `utils/heizlast.py`                    |
| Die Baujahr-Richtwerte ändern                | `utils/heizlast.py`                    |
| Den iFrame auf WordPress anpassen            | WordPress → Elementor (siehe Kap. 8)   |

---

## 10. Häufige Änderungen – Schritt für Schritt

### Beispiel 1: Einen Text ändern

**Aufgabe:** Den Untertitel ändern.

**Mit Claude (empfohlen):**
```
cd ~/Library/Mobile\ Documents/com~apple~CloudDocs/HEIZLAST-RECHNER
git pull
claude
```
Dann tippen:
```
Ändere den Untertitel zu: Kostenlose Heizlastberechnung für Ihr Gebäude
```
Wenn Claude fertig ist:
```
Bitte committe und pushe die Änderungen
```
Fertig. 1-2 Minuten warten, Seite neu laden.

**Manuell:**
1. `templates/index.html` öffnen
2. `Cmd + F` → nach dem alten Text suchen
3. Text ersetzen, speichern (`Cmd + S`)
4. Im Terminal:
   ```
   git add . && git commit -m "Untertitel geändert" && git push
   ```

### Beispiel 2: Logo austauschen

1. Erstellen/besorgen Sie das neue Logo (am besten als SVG oder PNG)
2. Benennen Sie es `logo.svg` (oder `logo.png`)
3. Kopieren Sie es in den Ordner `HEIZLAST-RECHNER/static/` (per Finder: einfach reinziehen, alte Datei ersetzen)
4. Falls PNG statt SVG:
   - Öffnen Sie `templates/index.html`
   - Ersetzen Sie alle Stellen `logo.svg` durch `logo.png` (es gibt 2 Stellen)
5. Im Terminal:
   ```
   cd ~/Library/Mobile\ Documents/com~apple~CloudDocs/HEIZLAST-RECHNER
   git add . && git commit -m "Neues Logo" && git push
   ```

### Beispiel 3: Ein neues Feature mit Claude

**Aufgabe:** Ölverbrauch als Alternative zu Gas hinzufügen.

```
cd ~/Library/Mobile\ Documents/com~apple~CloudDocs/HEIZLAST-RECHNER
git pull
claude
```

Dann tippen:
```
Füge eine Option hinzu, damit man auch Ölverbrauch (in Litern) statt Gasverbrauch eingeben kann. Heizöl hat einen Brennwert von ca. 10 kWh pro Liter.
```

Claude bearbeitet alle nötigen Dateien (HTML, Python, evtl. CSS). Dann:

```
Bitte committe und pushe die Änderungen
```

### Beispiel 4: Rechner lokal auf dem Mac testen (vor dem Hochladen)

Falls Sie eine Änderung erst testen wollen, bevor sie online geht:

```
cd ~/Library/Mobile\ Documents/com~apple~CloudDocs/HEIZLAST-RECHNER
python3 app.py
```

Dann öffnen Sie im Browser: **http://127.0.0.1:5000**

Mit `Ctrl + C` im Terminal stoppen Sie den lokalen Server wieder.

**Hinweis:** Dafür müssen Python 3 und die Pakete installiert sein:
```
pip3 install flask requests numpy
```

---

## 11. Problemlösung

### "Die Seite zeigt die alte Version"

1. **Browser-Cache leeren:** Drücken Sie `Cmd + Shift + R` (harter Reload)
2. **Render-Status prüfen:** Gehen Sie auf https://dashboard.render.com → "Heizlastberechnung" → Status muss "Live" sein
3. **Falls "Building":** Einfach warten (1-2 Min.)
4. **Falls "Failed":** Logs lesen (rote Zeilen), Fehler an Claude zeigen

### "git push funktioniert nicht"

**Fehlermeldung "rejected":**
Jemand (oder Claude in einer anderen Session) hat Änderungen gemacht, die Sie noch nicht haben. Lösung:
```
git pull
git push
```

**Fehlermeldung "not a git repository":**
Sie sind im falschen Ordner. Navigieren Sie zuerst zum Projekt:
```
cd ~/Library/Mobile\ Documents/com~apple~CloudDocs/HEIZLAST-RECHNER
```

### "claude: command not found"

Claude Code ist nicht installiert. Installieren Sie es:
```
npm install -g @anthropic-ai/claude-code
```

Falls auch `npm` nicht gefunden wird: Installieren Sie Node.js von https://nodejs.org

### "Die App auf Render zeigt einen Fehler"

1. Gehen Sie auf https://dashboard.render.com
2. Klicken Sie auf "Heizlastberechnung"
3. Scrollen Sie runter zu den **Logs**
4. Suchen Sie nach roten Zeilen – das sind Fehlermeldungen
5. Kopieren Sie die Fehlermeldung
6. Starten Sie Claude und sagen Sie:
   ```
   Ich habe diesen Fehler auf Render: [Fehlertext einfügen]
   ```

### "Render schläft immer ein (erster Aufruf dauert 50 Sekunden)"

Das ist normales Verhalten im kostenlosen Plan. Optionen:

**Option A – Upgrade (~7 $/Monat):**
Auf Render → "Heizlastberechnung" → "Upgrade your instance" → "Starter" wählen

**Option B – Kostenloser Workaround (UptimeRobot):**
1. Gehen Sie auf https://uptimerobot.com und erstellen Sie ein kostenloses Konto
2. Klicken Sie auf "Add New Monitor"
3. Monitor Type: "HTTP(s)"
4. URL: `https://heizlastberechnung.onrender.com`
5. Monitoring Interval: 5 Minutes
6. Speichern
UptimeRobot pingt die App alle 5 Minuten an und hält sie so wach.

### "Ich habe aus Versehen etwas kaputt gemacht"

Git speichert jede Version. Sie können jederzeit zurück.

**Letzte Änderung rückgängig machen (am einfachsten mit Claude):**
```
cd ~/Library/Mobile\ Documents/com~apple~CloudDocs/HEIZLAST-RECHNER
claude
```
Dann sagen:
```
Mache die letzte Änderung rückgängig
```

**Manuell – Alle Versionen anzeigen:**
```
git log --oneline
```
Ausgabe z.B.:
```
c5c203b Bedienungsanleitung hinzufügen
d4c1d80 gunicorn zu requirements.txt
0f9444c Logo und Erklärungen verbessert
f522ac3 V2: Heizgradtage, Sensitivitätsanalyse
```

Zu einer bestimmten Version zurückkehren (z.B. eine einzelne Datei):
```
git checkout f522ac3 -- templates/index.html
git commit -m "index.html auf Version f522ac3 zurückgesetzt"
git push
```

---

## 12. Wichtige Links und Zugänge

| Was                        | URL / Zugang                                           |
|----------------------------|--------------------------------------------------------|
| **App live**               | https://heizlastberechnung.onrender.com                |
| **WordPress-Admin**        | https://ak-energyconsulting.de/wp-admin                |
| **Render Dashboard**       | https://dashboard.render.com (Login mit GitHub)        |
| **GitHub Repository**      | https://github.com/kaempf25/wetter_Europa              |
| **Strato Kundencenter**    | https://www.strato.de/apps/CustomerService             |
| **Bright Sky API (Doku)**  | https://brightsky.dev                                  |
| **DWD Open Data**          | https://opendata.dwd.de                                |

### Projekt-Pfad auf dem Mac

```
~/Library/Mobile Documents/com~apple~CloudDocs/HEIZLAST-RECHNER
```

Im Finder: **iCloud Drive → HEIZLAST-RECHNER**

### Schnellstart-Befehle (zum Kopieren)

```bash
# Zum Projektordner navigieren:
cd ~/Library/Mobile\ Documents/com~apple~CloudDocs/HEIZLAST-RECHNER

# Neueste Version holen:
git pull

# Claude starten:
claude

# Lokalen Test-Server starten:
python3 app.py

# Änderungen hochladen (nach manueller Bearbeitung):
git add . && git commit -m "Beschreibung" && git push
```

---

## Zusammenfassung: Der Standard-Workflow

```
1. Terminal öffnen           (Cmd + Leertaste → "Terminal" → Enter)
2. Zum Projekt navigieren    cd ~/Library/Mobile\ Documents/com~apple~CloudDocs/HEIZLAST-RECHNER
3. Aktualisieren             git pull
4. Claude starten            claude
5. Änderung beschreiben      "Bitte ändere den Titel zu ..."
6. Hochladen lassen          "Committe und pushe die Änderungen"
7. 1-2 Minuten warten        (Render baut automatisch neu)
8. Im Browser prüfen         https://heizlastberechnung.onrender.com (Cmd+Shift+R)
```

Bei Fragen einfach Claude fragen – auf Deutsch, in ganzen Sätzen.
