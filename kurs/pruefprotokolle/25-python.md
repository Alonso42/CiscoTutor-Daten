# Prüfprotokoll Kapitel 25-python

Datum: 2026-11-24 · Checker · Python 3.15.2 (lokal, Snippets isoliert im Scratchpad mit `python -I`, Timeout 2 s)

## Umfang
- Fragen geprüft: 140 (single 92, multi 15, cli 11, zuordnung 12, luecke 10)
- Davon per Ausführung geprüft: 130
  - 84 Code-Snippets aus dem Fragetext automatisch ausgeführt (inkl. 042 Endlosschleife: TIMEOUT nach 2 s, wie erwartet)
  - Zusätzlich jede Option aller Code-multi-Fragen (093, 096, 097, 099, 102, 103, 106, 107), Optionen von 070, alle CLI-Lösungen mit Code (111–115, 117, 118), alle Zuordnungen mit Ausdrücken (121, 122, 123, 124, 126, 129) und die luecke-Ausdrücke (131, 140)
  - 024 im echten REPL (`python -i`): Ausgabe `'WELCOME\nR1'`; 130: Prompts `>>>` / `...` bestätigt
  - 087: Import-Test mit zwei Dateien → nur `A`; 086/136: `__pycache__\helpers.cpython-315.pyc` entsteht nur für das importierte Modul
- Nicht-Code-Fragen (083–085, 088–091, 095, 098, 104, 105, 108–110, 116, 119, 120, 125, 127, 128, 132–139) gegen docs.python.org geprüft.
- Wissensdatei: alle Code-Beispiele ausgeführt (Slicing, Arithmetik, Rangfolge, Umwandlung, String-Methoden, range, if/elif, vlan_exists-Skript, verschachtelte Dicts, Scope-Beispiel inkl. NameError, json.dumps) – alle Ergebnisse stimmen.
- Lektion: alle 8 Seiten und jede Tabellenzelle geprüft.
- Bilder: 10 SVGs inhaltlich geprüft, alle wohlgeformt (`[xml]`), UTF-8 ohne BOM, `<title>` erstes Kind.

## Korrekturen
| ID / Datei | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-py-026 | `False or True and False` ergibt auch von links nach rechts gelesen False – die Frage testet die Rangfolge nicht, Erklärung („käme man fälschlich auf False“) sinnlos | Snippet → `print(True or False and False)`, richtig = True (Index 2), Erklärung neu | https://docs.python.org/3/reference/expressions.html#operator-precedence |
| slg-py-070 | Erklärung „bei der letzten Option …“ meinte die dritte Option (str('Vlan' + vlan)); bei gemischten Antworten sowieso nicht positionsfest | Erklärung nennt jede falsche Option inhaltlich | Ausführung |
| slg-py-083 | Shebang wertet nicht die Shell, sondern das Betriebssystem (execve) aus | Optionen 1/3 „The shell runs …“ → „The OS runs …“, Erklärung angepasst | https://docs.python.org/3/tutorial/appendix.html#executable-python-scripts |
| slg-py-099 | Distraktor `def get_info():` allein erzeugt ebenfalls einen Fehler (IndentationError, Unterklasse von SyntaxError) → nicht eindeutig | Option → `def get_info(): pass` (gültig), Erklärung ergänzt | Ausführung |
| slg-py-130 | Frage „Anzeige“, aber exit()/help() sind Eingaben | „Ordne jede Anzeige bzw. Eingabe …“ | – |
| lektionen/25-python.json S. 4 | gleiches Rangfolge-Beispiel wie 026 | → `True or False and False` gleich True | wie 026 |
| lektionen/25-python.json S. 6 | „sagt der Shell“ | „sagt dem Betriebssystem“ | wie 083 |
| wissen/25-python.md | Rangfolge-Beispiel (wie 026); Shebang „einziger #-Zeile, die kein Kommentar für die Shell ist“ ungenau | Beispiel ersetzt; Shebang-Satz: `#!` = erste zwei Zeichen, für Python Kommentar, Betriebssystem wertet aus | Tutorial Appendix 16.1.2 |
| bilder/04-operatoren.svg | gleiches Rangfolge-Beispiel | → `True or False and False → True or False → True` | wie 026 |
| bilder/02-indizes.svg | Hinweiszeile vermutlich breiter als 800 px | gekürzt | – |
| alle 10 SVGs | Code-Einrückung (führende Leerzeichen) wird in SVG standardmäßig zusammengefasst → Python-Einrückung im Bild unsichtbar | `xml:space="preserve"` am Wurzelelement | SVG 1.1 §10.15 |

## Entfernt
keine

## Bestätigt (Auswahl Dokumentation)
- `__pycache__/modul.cpython-XY.pyc`, das direkt gestartete Skript wird nie gecacht; `__name__ == "__main__"` bei Direktstart, Modulname beim Import: https://docs.python.org/3/tutorial/modules.html
- Shebang `#!/usr/bin/env python3` als erste zwei Zeichen, `chmod +x`, `#` = Kommentar: https://docs.python.org/3/tutorial/appendix.html
- `**` rechtsassoziativ, Rangfolge or < and < not < Vergleiche < + < * < unär < **, Vergleichsverkettung: https://docs.python.org/3/reference/expressions.html
- UnboundLocalError ⊂ NameError, IndentationError ⊂ SyntaxError, TabError ⊂ IndentationError (lokal per issubclass geprüft)

## Unsichere Punkte / Hinweise
- Distraktor-Doppeldeutigkeit geprüft: keine weiteren Optionen mit gleicher Ausgabe gefunden (z. B. 049: andere Schlüsselreihenfolge = andere Ausgabe; 102: `'012'` druckt dieselben Zeichen, ist korrekt als richtig markiert).
- 095: Seit Python 3.13 beendet im neuen REPL auch `exit`/`quit` ohne Klammern – die Antwortoptionen bleiben eindeutig (logout()/end weiterhin ungültig).
- 085: `import: command not found` ist der typische Fall; auf Systemen mit ImageMagick ist `import` ein Programm (andere Fehlermeldung). Erklärung sagt „Fehler wie …“, daher belassen.
- Kursbezogene Aussagen in „Fehler/Ungenauigkeiten im Kurs“ (Seitenzahlen, Lab-Details) konnten ohne Kurszugriff nicht gegengeprüft werden.
- pruefen.ps1 -Kapitel 25-python: OK (140 Fragen, Schwierigkeit 37/74/29).
