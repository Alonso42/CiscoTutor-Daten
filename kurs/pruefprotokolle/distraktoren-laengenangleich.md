# Prüfung Distraktoren-Längenangleich (2026-11-24)

Quelle: patch1.json, patch2.json, patch3.json (234 Einträge, 152 Fragen-IDs in 02–10; patch3 ersetzt bei slg-os-033/slg-os-113 jeweils den patch2-Text von Option 2 – aktueller Dateistand = patch3).

Vorgehen: Für jede ID Frage, alle Optionen (richtig markiert), Erklärung gegen den aktuellen Stand der Fragen-Datei gelesen; jeder geänderte Distraktor auf "eindeutig falsch" und "keine Mehrdeutigkeit" geprüft. Kein Browser, keine Webrecherche nötig (alle Fälle fachlich eindeutig).

## Ergebnis

- Geprüft: 152 Fragen / 232 geänderte Optionen (230 Distraktoren + 2 gekürzte richtige Optionen).
- Gekürzte richtige Optionen:
  - slg-ar-005 "IEEE 802.3bz" – korrekt (2.5/5GBASE-T, Multigigabit über Cat5e/Cat6).
  - slg-os-081 "Cost = reference bandwidth 100 Mbps / 1.544 Mbps = 64 (truncated)" – korrekt (100/1,544 = 64,77 → 64).
- Korrigiert: 1

| ID | Option | Alt (Patch) | Neu | Grund |
|---|---|---|---|---|
| slg-sw-033 | 1 | It is dropped until ARP completes, then cached for later packets | It is queued until the next EIGRP update fills the fast-switching cache | Teilweise vertretbar: Fehlt der ARP-Eintrag, verwirft IOS beim Process Switching tatsächlich oft das auslösende Paket (Erklärung nennt selbst "ggf. ARP"). Neue Formulierung ist eindeutig falsch. |

Alle übrigen Distraktoren sind eindeutig falsch und machen die Frage nicht mehrdeutig. Grenzfälle bewusst belassen:
- slg-ar-021 Opt 0 (gestackte Distribution): dort wird kein GLBP genutzt (ein logisches Gateway), also keine GLBP-Lastverteilung – falsch.
- slg-ec-034 Opt 0 (Speed/Duplex-Konsistenz): kann PAgP ebenfalls – als "nur LACP" falsch.
- slg-ec-042 Opt 1 (mehr Member-Links): bei dst-mac auf eine Gateway-MAC hilft das nicht – Erklärung deckt das ab.
- slg-os-050 Opt 2 (Unicast-Hellos): auch bei point-to-point gehen Hellos an 224.0.0.5 – falsch.

## Prüfskript

`tools/pruefen.ps1 -Kapitel 03-switching-paths` → OK – keine Formatfehler (34 Fragen).
Datei UTF-8 ohne BOM, Top-Level-Array, nur gezielte Textersetzung.
