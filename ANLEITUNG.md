# Bedienungsanleitung: Heizlastrechner verwalten und aktualisieren

## Inhaltsverzeichnis

1. [Überblick: Wie hängt alles zusammen?](#1-überblick-wie-hängt-alles-zusammen)
2. [Änderungen am Code vornehmen (mit Claude)](#2-änderungen-am-code-vornehmen-mit-claude)
3. [Änderungen manuell vornehmen (ohne Claude)](#3-änderungen-manuell-vornehmen-ohne-claude)
4. [Render.com: Deployment verwalten](#4-rendercom-deployment-verwalten)
5. [WordPress/Elementor: iFrame anpassen](#5-wordpresselementor-iframe-anpassen)
6. [Wichtige Dateien und was sie tun](#6-wichtige-dateien-und-was-sie-tun)
7. [Häufige Änderungen (Beispiele)](#7-häufige-änderungen-beispiele)
8. [Problemlösung](#8-problemlösung)

---

## 1. Überblick: Wie hängt alles zusammen?

```
[Ihr Computer]
     |
     | (Code bearbeiten & hochladen)
     v
[GitHub]  ──────────────────────────> [Render.com]
(Code-Speicher)    (automatisch)      (Server, führt App aus)
                                           |
                                           | (iFrame)
                                           v
                                      [WordPress-Seite]
                                      ak-energyconsulting.de
```

**Der Ablauf bei jeder Änderung:**

1. Sie ändern den Code (lokal auf Ihrem Mac oder über Claude)
2. Die Änderung wird zu **GitHub** hochgeladen ("push")
3. **Render.com** erkennt den neuen Code automatisch und aktualisiert die App
4. Die **WordPress-Seite** zeigt automatisch die neue Version (weil der iFrame auf Render zeigt)

**Wichtig:** Sie müssen nichts an WordPress ändern, wenn sich nur der Rechner ändert. WordPress zeigt immer die aktuelle Version von Render an.

---

## 2. Änderungen am Code vornehmen (mit Claude)

### 2a. Claude Code öffnen

1. Öffnen Sie das **Terminal** auf Ihrem Mac:
   - Drücken Sie `Cmd + Leertaste` (Spotlight-Suche)
   - Tippen Sie `Terminal`
   - Drücken Sie `Enter`

2. Navigieren Sie zum Projektordner:
   ```
   cd ~/wetter_Europa
   ```
   (Falls der Ordner woanders liegt, passen Sie den Pfad an)

3. Starten Sie Claude Code:
   ```
   claude
   ```
   (Falls Claude Code nicht installiert ist: `npm install -g @anthropic-ai/claude-code`)

4. Claude meldet sich. Sie können jetzt in natürlichem Deutsch Ihre Wünsche beschreiben.

### 2b. Claude eine Änderung beschreiben

Tippen Sie einfach auf Deutsch, was Sie möchten. Beispiele:

- `"Ändere den Titel von Heizlastrechner zu Wärmepumpen-Rechner"`
- `"Füge ein Feld für die Gebäudeart hinzu (Einfamilienhaus, Mehrfamilienhaus)"`
- `"Die Erklärung zur Zustandszahl soll kürzer sein"`
- `"Ändere die Farbe des Logos von grün auf blau"`

Claude wird die Dateien automatisch bearbeiten.

### 2c. Änderungen auf GitHub hochladen

Nach der Änderung sagen Sie Claude:

```
"Bitte committe und pushe die Änderungen"
```

Claude macht dann automatisch:
1. `git add` (Dateien vormerken)
2. `git commit` (Änderung beschreiben)
3. `git push` (zu GitHub hochladen)

### 2d. Render aktualisiert sich automatisch

Sobald der Code auf GitHub ist, erkennt Render.com das innerhalb von 1-2 Minuten und baut die App neu. Sie müssen nichts tun.

**Prüfen:** Öffnen Sie https://heizlastberechnung.onrender.com und laden Sie die Seite neu (`Cmd + R`).

---

## 3. Änderungen manuell vornehmen (ohne Claude)

Falls Sie eine kleine Änderung selbst machen möchten (z.B. einen Text ändern):

### 3a. Terminal öffnen und zum Projekt navigieren

```
cd ~/wetter_Europa
```

### 3b. Neueste Version vom Server holen

```
git pull
```

### 3c. Datei bearbeiten

Öffnen Sie die gewünschte Datei mit einem Texteditor. Auf dem Mac:

```
open -a TextEdit templates/index.html
```

Oder mit VS Code (falls installiert):
```
code templates/index.html
```

Machen Sie Ihre Änderung und speichern Sie die Datei (`Cmd + S`).

### 3d. Änderung hochladen (3 Befehle)

Im Terminal, nacheinander eingeben:

```
git add .
```
(Punkt am Ende nicht vergessen! Merkt alle geänderten Dateien vor.)

```
git commit -m "Kurze Beschreibung der Änderung"
```
(Beschreiben Sie in Anführungszeichen, was Sie geändert haben.)

```
git push
```
(Lädt die Änderung zu GitHub hoch.)

### 3e. Warten und prüfen

Render baut die App in 1-2 Minuten neu. Danach: https://heizlastberechnung.onrender.com neu laden.

---

## 4. Render.com: Deployment verwalten

### Einloggen

1. Öffnen Sie https://dashboard.render.com
2. Loggen Sie sich mit Ihrem GitHub-Konto ein
3. Klicken Sie auf **"Heizlastberechnung"**

### Status prüfen

- **"Live"** (grün) = App läuft normal
- **"Building"** = App wird gerade aktualisiert (1-2 Min. warten)
- **"Failed"** (rot) = Fehler beim Bauen (siehe Logs)

### Manuell neu deployen

Falls die automatische Erkennung nicht funktioniert:
1. Klicken Sie oben rechts auf **"Manual Deploy"**
2. Wählen Sie **"Deploy latest commit"**

### Logs ansehen (bei Fehlern)

1. Im Render-Dashboard auf **"Heizlastberechnung"** klicken
2. Unten sehen Sie die **Logs** (Protokoll)
3. Rote Zeilen = Fehler. Den Fehlertext können Sie Claude zeigen.

### Wichtig: Free-Tier-Verhalten

Die kostenlose Render-Instanz:
- **Schläft nach 15 Minuten Inaktivität ein**
- **Erster Aufruf nach dem Einschlafen dauert ~50 Sekunden** (Kaltstart)
- Danach läuft sie normal schnell
- Für ~7$/Monat können Sie auf "Starter" upgraden (immer an)

---

## 5. WordPress/Elementor: iFrame anpassen

### Wann muss ich in WordPress etwas ändern?

**Meistens: Nie.** Der iFrame zeigt automatisch immer die aktuelle Version der App.

Sie müssen nur in WordPress rein, wenn Sie:
- Die **Höhe** des iFrames ändern wollen
- Die **Seite** verschieben wollen
- Die **Render-URL** sich ändert

### iFrame bearbeiten

1. Öffnen Sie https://ak-energyconsulting.de/wp-admin
2. Gehen Sie zu **"Seiten"** → finden Sie die Seite mit dem Rechner
3. Klicken Sie **"Mit Elementor bearbeiten"**
4. Klicken Sie auf den **iFrame-Bereich** (das HTML-Widget)
5. Bearbeiten Sie den Code:

```html
<iframe
  src="https://heizlastberechnung.onrender.com"
  width="100%"
  height="2200"
  style="border:none; max-width:900px; margin:0 auto; display:block;"
  title="Heizlastrechner - AK Energy Consulting">
</iframe>
```

6. Klicken Sie **"Aktualisieren"**

### Höhe anpassen

Falls der Rechner zu viel oder zu wenig Platz hat, ändern Sie den Wert `height="2200"`:
- Mehr Platz: `height="2500"`
- Weniger Platz: `height="1800"`

---

## 6. Wichtige Dateien und was sie tun

```
wetter_Europa/
├── app.py                    ← Herzstück: Flask-Server, nimmt Anfragen entgegen
├── requirements.txt          ← Liste der benötigten Python-Pakete
│
├── templates/
│   └── index.html            ← Die komplette Webseite (HTML + JavaScript)
│                                HIER ändern Sie Texte, Felder, Layout
│
├── static/
│   ├── style.css             ← Aussehen (Farben, Abstände, Schriftgrößen)
│   └── logo.svg              ← Das Logo (als Vektorgrafik)
│
├── utils/
│   ├── heizlast.py           ← Berechnung: Heizgradtage, Heizlast, Sensitivität
│   ├── dwd.py                ← Wetterdaten von Bright Sky API abrufen
│   └── geo.py                ← PLZ → Wetterstation zuordnen
│
└── data/
    ├── plz_coordinates.json  ← Alle 8.298 deutschen PLZ mit Koordinaten
    └── dwd_stations.json     ← Alle 1.507 DWD-Wetterstationen
```

### Was ändere ich wo?

| Ich will... | Datei |
|---|---|
| Einen Text auf der Seite ändern | `templates/index.html` |
| Eine Farbe oder Schriftgröße ändern | `static/style.css` |
| Das Logo austauschen | `static/logo.svg` |
| Die Berechnung ändern | `utils/heizlast.py` |
| Ein neues Eingabefeld hinzufügen | `templates/index.html` UND `app.py` |
| Den Titel ändern | `templates/index.html` (Zeile 6 und im `<h1>`) |

---

## 7. Häufige Änderungen (Beispiele)

### Beispiel 1: Einen Text ändern

Angenommen, Sie wollen den Untertitel ändern.

**Mit Claude:**
```
"Ändere den Untertitel zu: Kostenlose Heizlastberechnung für Ihr Gebäude"
```

**Manuell:**
1. Öffnen Sie `templates/index.html`
2. Suchen Sie nach dem alten Text (Cmd+F)
3. Ersetzen Sie ihn
4. Speichern, dann im Terminal:
   ```
   git add . && git commit -m "Untertitel geändert" && git push
   ```

### Beispiel 2: Logo austauschen

1. Erstellen Sie ein neues Logo als SVG oder PNG
2. Benennen Sie es `logo.svg` (oder `logo.png`)
3. Legen Sie es in den Ordner `static/`
4. Falls PNG statt SVG: In `templates/index.html` alle `logo.svg` durch `logo.png` ersetzen
5. Hochladen:
   ```
   git add . && git commit -m "Neues Logo" && git push
   ```

### Beispiel 3: Neue Berechnung / Feature

Sagen Sie Claude einfach auf Deutsch, was Sie wollen:
```
"Füge eine Option hinzu, damit man auch Ölverbrauch statt Gas eingeben kann"
```

Claude wird alle nötigen Dateien anpassen (HTML, Python, CSS).

---

## 8. Problemlösung

### "Die Seite zeigt die alte Version"

1. Browser-Cache leeren: `Cmd + Shift + R` (harter Reload)
2. Prüfen Sie auf Render, ob der Build durchgelaufen ist (Status "Live")
3. Falls "Failed": Logs auf Render prüfen, Fehler an Claude zeigen

### "git push funktioniert nicht"

Mögliche Ursache: Jemand anders hat Änderungen gemacht.
```
git pull
git push
```

### "Die App auf Render zeigt einen Fehler"

1. Gehen Sie auf https://dashboard.render.com
2. Klicken Sie auf "Heizlastberechnung"
3. Schauen Sie in die Logs (unten)
4. Kopieren Sie die roten Fehlerzeilen
5. Zeigen Sie sie Claude: `"Ich habe diesen Fehler auf Render: [Fehler einfügen]"`

### "Render schläft immer ein (langsamer erster Aufruf)"

Das ist normal im Free-Tier. Optionen:
- **Upgrade auf Starter** (~7$/Monat): Klicken Sie auf Render auf "Upgrade your instance"
- **Kostenloser Workaround**: Einen kostenlosen Uptime-Monitor einrichten (z.B. UptimeRobot.com), der alle 14 Minuten die URL aufruft und so die App wach hält

### "Ich habe aus Versehen etwas kaputt gemacht"

Git speichert jede Version. Zurück zur letzten funktionierenden Version:
```
git log --oneline
```
(Zeigt alle Versionen. Merken Sie sich den Code der gewünschten Version, z.B. `d4c1d80`)

```
git checkout d4c1d80 -- templates/index.html
git commit -m "index.html zurückgesetzt"
git push
```

Oder einfach Claude bitten: `"Mache die letzte Änderung rückgängig"`

---

## Zusammenfassung: Der Standard-Workflow

```
1.  Terminal öffnen
2.  cd ~/wetter_Europa
3.  claude                          (Claude Code starten)
4.  "Bitte ändere X..."            (Änderung beschreiben)
5.  "Committe und pushe"           (Hochladen)
6.  1-2 Minuten warten             (Render baut neu)
7.  Browser öffnen und prüfen      (heizlastberechnung.onrender.com)
```

Das war's. Bei Fragen einfach Claude fragen.
