# ENCOR 1.4.10 – Wissensbasis, Lektionen und Fragen für CiscoTutor

Erarbeitet aus dem Cisco-Kurs „Implementing and Operating Cisco Enterprise Network Core Technologies (ENCOR) 1.4.10 – Student Learning Guide“, ausgerichtet auf die Prüfung **ENCOR 350-401 v1.2**.
Alle Texte und Bilder sind **eigene Formulierungen bzw. eigene Zeichnungen** – keine Kopien aus dem Kurs. Fakten wurden gegen Cisco-Dokumentation/RFCs geprüft (Protokolle in `../research_notes/Kapitelpruefung/`).

> Privat halten: Das Material ist eng an einem lizenzierten Kurs ausgerichtet. Nicht ins öffentliche Daten-Repo spiegeln, ohne das zu prüfen.

## Ordner

| Ordner | Inhalt | Format |
|---|---|---|
| `wissen/` | Wissenszusammenfassung je Kapitel (Grundlage für spätere Lektionen/Fragen) | Markdown |
| `bilder/<kapitel>/` | Eigene Lernbilder, die das Wissen der Kursabbildungen vermitteln | SVG |
| `lektionen/` | Akademie-Lektionen (App-Format wie `daten/lektionen.json`) | JSON-Array |
| `fragen/` | Liga-Fragen (App-Format wie `daten/fragen.json`) | JSON-Array |
| `notizen/` | Ältere Arbeitsnotizen (werden durch `wissen/` ersetzt) | Markdown |
| `KAPITELPLAN.md` | Status je Kapitel | Markdown |

## Werkzeuge (`../tools/`)

- `pruefen.ps1 -Kapitel <name> [-Mischen]` – Formatprüfung (IDs, Antwortindizes, Optionenzahl, CLI-Bausteine, Zuordnungen, Längen-Bias, Lektionsdiagramme); `-Mischen` mischt Antwortpositionen.
- `ANLEITUNG-KAPITEL.md` – Arbeitsanleitung je Kapitel (Writer + Checker).

## Einbindung in die App

Fragen/Lektionen sind im selben Schema wie `daten/fragen.json` bzw. `daten/lektionen.json` und können vom Generator (`tools/daten_veroeffentlichen.sh`) zusammengeführt werden. Topic-IDs folgen dem ENCOR-v1.2-Blueprint; Wireless (nicht mehr in v1.2) ist als `ENCOR-LEGACY-*` markiert.
