# Arbeitsanleitung: Ein Kurskapitel → Akademie-Lektion + Liga-Fragen (CiscoTutor)

Projektordner (PROJ): C:\Users\fernando.lino\AppData\Local\Claude-Data\anthropicpbc.claude_fnn82j28hfe8t\scratch-workspaces\435bf197-4cf5-4b57-9fa2-f1e0508e7615\ed706fc7-9b99-4dfb-8253-60e699bed3ab\scratch-2026-11-24-a84aa9

Ziel: Der Nutzer lernt mit der App für die Prüfung CCNP ENCOR 350-401 (aktuelle Version v1.2). Gesamtziel ~5000 Fragen (1132 existieren schon). Pro Kapitel ca. 100–150 Fragen – aber NUR gute, nicht-redundante Fragen. Lieber 90 starke als 150 mit Füllstoff. Keine Fakten erfinden.

## 1. Kurs lesen (nur Writer)
- Browser: Claude in Chrome. Erst `tabs_context_mcp` aufrufen (ohne createIfEmpty), dann den Tab "Cisco Learning Network Space - Reader" benutzen. KEINE neuen Tabs öffnen, den Tab NICHT schließen, nichts außer Blättern im Reader anklicken.
- Seite anspringen: per `find` das Textfeld "Gehe zu Seite" suchen, triple_click, Seitenzahl tippen, Return, 2 s warten. Nächste Seite: per `find` den "nächste Seite"-Link (Pfeil rechts unten neben "Seite X / 381") – alternativ wieder über das Feld.
- Seitentext steht in einem iframe. Lesen per javascript_tool:
  `window.__t=document.querySelector('iframe').contentDocument.body.innerText.replace(/[ \t]*\n[\s]*/g,'\n'); window.__t.length+' | '+window.__t.slice(0,900)`
  danach `window.__t.slice(900,1800)`, `window.__t.slice(1800,2700)` usw. (Ausgaben werden nach ~1000 Zeichen abgeschnitten – daher in 900er-Stücken, mehrere Aufrufe in einem browser_batch).
- Prüfe nach jedem Sprung anhand der ersten Zeile, dass du auf der richtigen Seite bist.
- "Answer Key"-Seiten und "Summary Challenge"-Seiten NICHT lesen. Discovery-/Lab-Seiten lesen (gut für Szenario- und Show-Output-Fragen).

## 2. Wissensbasis (wird ins Git eingecheckt und für spätere App-Arbeit wiederverwendet)
- Schreibe PROJ\encor-1.4.10\wissen\<datei>.md – eine VOLLSTÄNDIGE, strukturierte Wissenszusammenfassung des Kapitels in EIGENEN Worten (Deutsch, Fachbegriffe/Befehle englisch). Aufbau: `# Kapiteltitel` · `Quelle: ENCOR 1.4.10 Student Guide, Seiten X–Y` · `Topics: ...` · je Kursabschnitt `## Abschnitt` mit allen Fakten, Defaults, Befehlen (Codeblöcke), typischen show-Ausgaben (eigene, gekürzte Beispiele) und Troubleshooting-Hinweisen · `## Fehler/Ungenauigkeiten im Kurs` (mit korrekter Aussage + Quelle) · `## Bilder` (Liste der SVGs aus Schritt 2b mit einem Satz, was jedes zeigt).
- Keine wörtlichen Kursabsätze (höchstens einzelne Fachbegriffe/Befehle), keine Kurs-Wissensfragen/Antworten. Ziel: Jemand kann aus dieser Datei allein die Lektion und neue Fragen bauen.
- Falls schon eine Datei PROJ\encor-1.4.10\notizen\<datei>.md existiert, diese als Ausgangspunkt nehmen.

## 2b. Lernbilder (SVG)
- Für jede Kursabbildung mit Lerninhalt (Topologien, Abläufe, Header-Formate, Tabellen-Grafiken, Zustandsautomaten): Abbildung im Reader per Screenshot ansehen (`computer` screenshot, ggf. `zoom`) und verstehen, WAS sie vermittelt.
- Dann ein EIGENES Bild zeichnen, das dasselbe Wissen vermittelt: PROJ\encor-1.4.10\bilder\<datei>\NN-kurzname.svg (Dateiname insgesamt max. 18 Zeichen, sonst Windows-Pfadlimit 260 überschritten). Nicht abpausen oder Cisco-Layout/Icons/Logos/Farben nachbauen – eigenes, schlichtes Design: weißer Hintergrund, viewBox z. B. "0 0 800 450", Schrift font-family="sans-serif", Geräte als einfache Formen (Router = Kreis mit Pfeilen/„R“, Switch = Rechteck mit „SW“, PC = kleines Rechteck), klare Beschriftungen (Deutsch, Fachbegriffe englisch), Farben aus der App-Palette (#39c86a grün, #4a9cff blau, #b08aff lila, #ffd23f gelb, #ff6b6b rot, Text #222). Mit <title> als erstem Kindelement (Bildtitel).
- Jedes SVG muss wohlgeformtes XML sein (prüfen: `[xml](Get-Content -Raw -Encoding utf8 <pfad>)` darf nicht fehlschlagen). Als UTF-8 ohne BOM speichern (Write-Tool).
- Typisch 4–10 Bilder pro Kapitel. In der Wissensdatei unter `## Bilder` auflisten.

## 2c. (alt) Notizen
- Die Wissensdatei ersetzt die bisherigen Notizen. Keine längeren wörtlichen Passagen aus dem Kurs. Keine Kurs-Wissensfragen übernehmen.

## 3. Dubletten vermeiden, Erklärungen wiederverwenden
- Bestand: PROJ\repo-src\daten_fragen.json (1132 Fragen) und alle Dateien in PROJ\encor-1.4.10\fragen\. Vor dem Schreiben die Fragen zu deinen Topics/Stichworten ansehen (PowerShell: ConvertFrom-Json, nach topic/Stichwort filtern). Keine Frage stellen, die inhaltlich schon existiert. Wo eine bestehende Erklärung exakt passt, darfst du sie übernehmen.

## 4. Fragen schreiben → PROJ\encor-1.4.10\fragen\<datei>.json
JSON-Array, UTF-8 ohne BOM. Frage und Optionen ENGLISCH (wie in der Prüfung), "erklaerung" DEUTSCH, 1–3 Sätze, erklärt das Warum (nicht nur ein Wort).
Felder: id (Präfix aus dem Auftrag + laufende Nummer, z. B. "slg-st-001"), topic, schwierigkeit (1 leicht/2 mittel/3 schwer), typ, frage, erklaerung, plus je Typ:
- single: optionen (4), richtig (Index, 0-basiert)
- multi: optionen (4–5), richtig (Array, mind. 2 Indizes)
- luecke: frage mit "___", optionen (4), richtig (Index)
- zuordnung: paare [[links, rechts], ...] (3–4 Paare; rechte Seiten müssen eindeutig unterscheidbar sein, keine zwei gleichen/austauschbaren)
- cli: bausteine (Lösungstokens + 2–4 Ablenker), loesung (Tokens in Reihenfolge); Frage nennt den Modus/Kontext (Deutsch ok)
Mischung pro Kapitel etwa: 60 % single, 12 % multi, 10 % cli, 10 % zuordnung, 8 % luecke. Schwierigkeit etwa 25 % / 50 % / 25 %.
Qualität:
- Genau eine vertretbare Antwort (bei multi: genau die markierten). Distraktoren plausibel, aber eindeutig falsch. Richtige Option NICHT länger/vollständiger als die anderen – pruefen.ps1 meldet "Laengen-Bias", wenn die richtige Option >30 % länger ist als jeder Distraktor. Lösung: Distraktoren gleich detailliert formulieren (mit plausiblen, aber falschen Details) oder die richtige Option kürzen. Ein Kapitel ist erst fertig, wenn pruefen.ps1 OK meldet.
- Viele Szenario-, Troubleshooting-, Show-Output- und Rechenfragen (Prüfungsstil), nicht nur Definitionen.
- Defaults, Timer, Zahlen, Befehlssyntax nur, wenn du sie sicher kennst bzw. belegt hast (aktuelles IOS-XE).
Topic-IDs: ENCOR v1.2 Blueprint (https://learningcontent.cisco.com/documents/marketing/exam-topics/350-401-ENCORE-v1.2.pdf). Bestehende IDs im Format "ENCOR-3.1.c" verwenden. Themen, die in v1.2 nicht mehr vorkommen (z. B. Wireless), mit "ENCOR-LEGACY-<thema>" taggen.

## 5. Lektion (Akademie) → PROJ\encor-1.4.10\lektionen\<datei>.json
JSON-Array mit EINEM Objekt: {"id","titel","topics":[...],"seiten":[{"text": "...", "diagramm": {...}}]}. 5–8 Seiten, Deutsch, erklärt wie es funktioniert. Möglichst jede Seite mit Lernbild:
- {"typ":"topologie","knoten":[{"id","label","x":"0.1","y":"0.5","art":"pc|router|switch|server|cloud"}],"kanten":[{"von","nach","label","farbe":"39c86a"}],"schritte":[{"von","nach","farbe":"ffd23f","text"}]} (x/y als Strings 0–1; schritte = animierter Ablauf)
- {"typ":"tabelle","kopf":[...],"zeilen":[[...],...]}
- {"typ":"ablauf","stufen":["...","..."]}
Beispiele: PROJ\encor-1.4.10\lektionen\04-campus-lan.json und PROJ\repo-src\daten_lektionen.json.

## 6. Formatprüfung
PowerShell im PROJ: `& ./tools/pruefen.ps1 -Kapitel <datei> -Mischen` (mischt Antwortpositionen, prüft Format/IDs). Achtung PowerShell 5.1: beim Schreiben von JSON immer `ConvertTo-Json -InputObject @($arr) -Depth 10` und `[IO.File]::WriteAllText(pfad, json, (New-Object Text.UTF8Encoding $false))` – sonst wird das Array verschachtelt. Am einfachsten: Dateien direkt mit dem Write-Tool schreiben. Fehler beheben, bis "OK".

## 7. Faktencheck (nur Checker)
JEDE Frage einzeln: markierte Antwort korrekt? Alle Distraktoren wirklich falsch? Erklärung korrekt? Eindeutig? CLI gültig? Paare korrekt und nicht vertauschbar? Topic passend? Websuche gegen cisco.com (Config Guides, Command References IOS-XE 17.x), RFCs, Cisco Press ist PFLICHT für alle Zahlen, Defaults, Timer, Befehlssyntax, Protokolldetails – nicht nur Gedächtnis. Lektion ebenso (jede Tabellenzelle).
Klare Fehler direkt in den Dateien korrigieren (Array-Struktur und IDs behalten; bei geändertem richtig-Index anpassen). Nicht belegbare/zweifelhafte Fragen lieber umformulieren oder entfernen. Danach `& ./tools/pruefen.ps1 -Kapitel <datei>` (ohne -Mischen) → muss "OK" sein.
Schreibe ein Prüfprotokoll nach PROJ\research_notes\Kapitelpruefung\<datei>.md: geprüft N, korrigiert/entfernt (id, Problem, Änderung, Quelle-URL), unsichere Punkte.

## Antwort an den Koordinator (kurz, Deutsch)
Anzahl Fragen (nach Typ/Schwierigkeit), Lektionsseiten, Besonderheiten, bei Checker: Zahl der Korrekturen/Entfernungen mit IDs.
