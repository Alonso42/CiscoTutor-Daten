# Discovering the Basics of Python Programming

Quelle: ENCOR 1.4.10 Student Guide, Seiten 269–275 (Intro 268, Summary Challenge 276 und Answer Key 277 nicht ausgewertet)

Topics: ENCOR-6.1 (Interpret basic Python components and scripts)

Hinweis: Viele Kursbeispiele sind noch in Python-2-Syntax (`print x`, `<type 'str'>`, `144 / 12 → 12`). Alle Beispiele unten sind Python 3 und wurden mit Python 3.15 ausgeführt.

## Python-Grundlagen (Describe Python Concepts)

- **Interpretiert**: Quelltext wird vom Interpreter direkt ausgeführt, kein separater Compile-Schritt durch den Benutzer. Intern erzeugt Python Bytecode (.pyc, siehe unten).
- **Niedrige Einstiegshürde**, englisch-ähnliche Syntax, vielseitig (Backend-, Web-, Automatisierungs-Apps).
- **Verfügbar** auf praktisch allen Linux-Distributionen und auf Cisco-Plattformen wie **NX-OS** (Nexus) – Skripte sind daher portabel zwischen Server, Workstation und Switch.
- **Python 3** ist die aktuelle, gepflegte Version; **Python 2 ist End-of-Life** (seit 1.1.2020). Python 3 ist nicht abwärtskompatibel (u. a. `print()` ist eine Funktion, `/` liefert float).
- **Dynamisch typisiert**: Variablen werden nicht deklariert; `hostname = 'Router_1'` legt die Variable an. Ein Name kann später auf einen Wert anderen Typs zeigen.

### Zwei Arten, Code auszuführen
1. **Interaktiver Interpreter (Python-Shell)**: `python` bzw. `python3` im Linux-Terminal oder auf der Nexus-CLI. Prompt `>>>`, Fortsetzungs-Prompt `...` (nach Zeile mit Doppelpunkt; Block mit Leerzeile beenden). Beenden mit `exit()`, `quit()` oder **Ctrl+D**. Ideal zum schnellen Testen; kein Editor/IDE nötig.
   - Der Interpreter zeigt den Wert eines Ausdrucks automatisch an (`>>> 5*8` → `40`). In einem Skript passiert das NICHT – dort braucht man `print()`.
   - Variablenname allein zeigt die **Repräsentation** (repr): Anführungszeichen und Escape-Sequenzen sichtbar (`'WELCOME\nR1'`). `print()` rendert den String (`\n` wird zum Zeilenumbruch).
2. **Skript**: Datei mit Endung `.py` in beliebigem Editor (im Lab VS Code, `code datei.py`), Start mit `python3 skript.py`.

### Hilfsfunktionen
| Funktion | Ergebnis |
|---|---|
| `help(obj)` | eingebettete Doku/Docstrings, z. B. `help(str.upper)` |
| `dir(obj)` | Liste der Attribute und Methoden; ohne Argument: Namen im aktuellen Scope |
| `type(obj)` | Datentyp, Python 3: `<class 'str'>` |
| `len(obj)` | Anzahl Zeichen/Elemente/Schlüssel |

Namen mit doppelten Unterstrichen (`__add__` …) sind interne „Dunder“-Methoden.

### Idiomatisches Python (PEP 8)
- **PEP 8** = offizieller Style Guide (Lesbarkeit, Einheitlichkeit, „pythonic“).
- Einzeiliger Kommentar: `#` bis Zeilenende. Mehrzeilig: mehrere `#`-Zeilen oder ein Triple-Quote-String (`'''...'''`/`"""..."""`, als Docstring).
- Einrückung bestimmt Blöcke; PEP 8 empfiehlt **4 Leerzeichen** pro Ebene, keine Tab/Space-Mischung (Python 3: `TabError` bei inkonsistenter Mischung).

### Datentypen-Überblick
| Typ | Beispiel | veränderbar? |
|---|---|---|
| str | `'R1'`, `"R1"`, `'''R1'''` | nein |
| int | `24` | nein |
| float | `2.5`, `10 / 2` → `5.0` | nein |
| bool | `True`, `False` | nein |
| list | `['s1', 's2']` | ja |
| dict | `{'os': '7.2'}` | ja |
| tuple | `('s1', 's2')`, `(10,)` – `(10)` ist nur int | nein |
| NoneType | `None` | – |

Umwandlung: `int('42')` → 42, `int(9.99)` → 9 (abschneiden), `int('10.5')` → ValueError, `str(42)` → `'42'`, `float('3')` → 3.0, `bool('')` → False.

## Strings (String Data Types)

- Folge von Zeichen in einfachen oder doppelten Anführungszeichen. **Ohne Anführungszeichen** ist es ein Name/Objektverweis → `hostname = R1` ergibt `NameError: name 'R1' is not defined`.
- **Immutable**: `hostname[4] = '3'` → `TypeError: 'str' object does not support item assignment`.
- Leerer String `''` ist falsy, jeder nicht leere String (auch `'False'`, `' '`) truthy.
- **Verkettung** mit `+` (kein automatisches Leerzeichen): `ipaddr + ' ' + mask` → `'10.1.10.1 255.255.255.0'`. `'Vlan' + 10` → TypeError → `'Vlan' + str(10)`. Wiederholung: `'-' * 5` → `'-----'`, `'5' * 3` → `'555'`.

### Indizes und Slicing
```python
intf = 'GigabitEthernet0/1'
intf[0]     # 'G'
intf[-1]    # '1'
intf[-3:]   # '0/1'
intf[:2] + intf[-3:]   # 'Gi0/1'
'nexus'[1:3]           # 'ex'   (stop exklusiv)
'10.1.10.1'[::-1]      # '1.01.1.01'
```
Index außerhalb → `IndexError: string index out of range` (bei Slices kein Fehler).

### String-Methoden (geben NEUE Objekte zurück, Original bleibt)
| Methode | Beispiel → Ergebnis |
|---|---|
| `upper()`/`lower()` | `'nxos1'.upper()` → `'NXOS1'` |
| `replace(a, b[, n])` | `'00:11:22:33:44:55'.replace(':', '.')` → `'00.11.22.33.44.55'` |
| `startswith()`/`endswith()` | `'10.1.1.1'.startswith('10')` → `True` |
| `format()` | `'10.{}.1.1'.format('200')` → `'10.200.1.1'`; `'{1}-{0}'.format('a','b')` → `'b-a'` |
| f-String | `f'{name.lower()} has {len(ip)}'` |
| `split(sep)` | `'10.4.8.1'.split('.')` → `['10', '4', '8', '1']`; ohne Argument: an Whitespace |
| `join()` | `'.'.join(['10','4'])` → `'10.4'` |
| `strip()` | entfernt Whitespace/`\n` an beiden Enden |
| `find()` | Index oder **-1** |
| `index()` | Index oder **ValueError: substring not found** |
| `isalnum()`/`isalpha()`/`isdigit()` | bool; `'R1-core'.isalnum()` → False, `'10.0'.isdigit()` → False |

Zwei Fragen bei jeder Methode: Was gibt sie zurück (Typ)? Ändert sie das Original? (`hostname.upper()` ohne Zuweisung ändert nichts; `list.sort()` ändert die Liste und gibt `None` zurück.)

## Zahlen (Numbers Data Types)

```python
7 + 2   # 9
7 / 2   # 3.5   (Python 3: immer float; 144 / 12 → 12.0)
7 // 2  # 3     (Floor-Division; -7 // 2 → -4)
7 % 2   # 1     (Rest)
7 ** 2  # 49    (Potenz, rechtsassoziativ: 2 ** 3 ** 2 → 512)
```
Rangfolge: `**` > `*` `/` `//` `%` > `+` `-` > Vergleiche/`in`/`is` > `not` > `and` > `or`. Beispiel `2 + 3 * 4 ** 2` → 50.

## Booleans und Bedingungen (Boolean Data Types)

- Werte `True`/`False`; Operatoren `and` (alle wahr), `or` (mindestens einer wahr), `not` (Umkehrung).
- `True or False and False` → True (and zuerst; links-nach-rechts gelesen käme fälschlich False heraus); `not 1 == 2` → True.

| Operator-Typ | Operatoren |
|---|---|
| Vergleich | `==` `!=` `>` `<` `>=` `<=` (verkettbar: `1 < 2 < 3`) |
| Logisch | `and` `or` `not` |
| Membership | `in`, `not in` (bei dict: nur Schlüssel) |
| Identität | `is`, `is not` (z. B. `x is None`) |

- String-Vergleiche sind lexikografisch: `'10' < '9'` → True. Vor numerischem Vergleich `int()`.
- `in`/`==` sind case-sensitive.
- **Truthiness**: falsy sind `''`, `0`, `0.0`, `[]`, `{}`, `()`, `None`; alles andere truthy. `if hostname:` prüft nur, ob ein Wert gesetzt ist.

### if / elif / else
```python
switch = 'catalyst 3850'
if 'catalyst' in switch:
    switch_type = 'catalyst'
elif 'nexus' in switch:
    switch_type = 'nexus'
else:
    switch_type = 'unknown'
print(switch_type)   # catalyst
```
- Kopfzeilen enden mit `:`; Blöcke einheitlich eingerückt.
- `elif` optional und mehrfach; `else` optional, nur am Ende, ohne Bedingung – läuft, wenn keine vorherige Bedingung wahr war.
- Nur der **erste** wahre Zweig läuft, dann wird die Kette verlassen. Zwei getrennte `if` werden beide geprüft.

### Schleifen (ergänzt, im Kurs in Beispielen verwendet)
- `for x in sequenz:` iteriert über Listen, Strings, `dict.items()`, `range()`.
- `range(stop)`, `range(start, stop, step)`: `range(2, 10, 3)` → 2, 5, 8; `range(10, 0, -3)` → 10, 7, 4, 1.
- `while bedingung:` – ohne Änderung der Bedingung Endlosschleife.
- `break` beendet die Schleife, `continue` springt zum nächsten Durchlauf, `pass` ist eine leere Anweisung. Schleifenvariable behält danach den letzten Wert.

## Skripte schreiben und ausführen (Script Writing and Execution)

```python
#!/usr/bin/env python3

def vlan_exists(vlan_id):
    vlans_list = [1, 5, 10, 20]
    return vlan_id in vlans_list

if __name__ == '__main__':
    vlans = [5, 8, 10, 15, 20]
    for vlan in vlans:
        print(vlan, vlan_exists(vlan))
```
Ausgabe: `5 True`, `8 False`, `10 True`, `15 False`, `20 True`.

- **Shebang** (`#!/usr/bin/env python3`): optional, `#!` müssen die ersten zwei Zeichen der Datei sein. Für Python ist die Zeile ein Kommentar; beim direkten Start wertet das Betriebssystem sie aus und startet den genannten Interpreter. `env` sucht den Interpreter im PATH. Nötig, wenn man das Skript direkt (`./skript.py`) startet; zusätzlich `chmod +x skript.py` (sonst „Permission denied“). Ohne Shebang führt bash die Datei als Shell-Skript aus → Fehler wie `import: command not found`. `which python3` zeigt, welcher Interpreter im PATH liegt.
- **Entry Point** `if __name__ == '__main__':` optional; bei direktem Start ist `__name__ == '__main__'`, beim Import der Modulname → Block läuft dann nicht (Code auf oberster Ebene läuft aber trotzdem). Ohne Entry Point läuft der Code von oben nach unten – auch beim Import.
- Funktionen: `def name(param, opt=default):` + eingerückter Rumpf; `return` beendet die Funktion sofort; ohne `return` → `None`.
- **Bytecode**: Python übersetzt intern in Bytecode; für **importierte Module** legt Python 3 `.pyc`-Dateien in `__pycache__/` ab (z. B. `helpers.cpython-312.pyc`). Das direkt gestartete Hauptskript wird nicht gecacht.
- Module: `import json` (Standardbibliothek); ohne Import → `NameError: name 'json' is not defined`.

## Code analysieren (Analyzing the Code)

Vier Schwerpunkte: Zugriff auf Listen (Index) und Dictionaries (Schlüssel), Datentypen kennen, Variablen-Scope, Einrückung bei Bedingungen/Schleifen.

### Verschachtelte Objekte
```python
neighbors = ['s1', 's2', 's3']
facts = {'hostname': 'cisco', 'os': '7.0.2', 'neighbors': neighbors}
facts['neighbors'][1]        # 's2'  (Schlüssel, dann Index)
type(facts)                  # <class 'dict'>
type(facts['neighbors'])     # <class 'list'>
```
Mit `type()` Schritt für Schritt prüfen, ob als Nächstes ein Schlüssel (dict) oder ein Index (list) nötig ist. `len(facts)` → 3 (Anzahl Schlüssel). `'os' in facts` → True, `'cisco' in facts` → False.

### Variablen-Scope
```python
ipaddr = '10.1.10.1'    # global
mask = '24'             # global

def get_ip(ip):         # ip ist lokal
    print(ip, mask, ipaddr)

if __name__ == '__main__':
    ipaddr = '200.100.1.1'   # überschreibt die GLOBALE Variable
    get_ip(ipaddr)           # 200.100.1.1 24 200.100.1.1
    print(ip)                # NameError: name 'ip' is not defined
```
- Globale Variablen stehen meist oben im Skript und sind überall lesbar.
- Der Block unter dem Entry Point hat **keinen eigenen Scope** – Variablen dort sind global.
- Parameter und in einer Funktion zugewiesene Variablen sind **lokal**; sie verdecken gleichnamige globale Variablen (`x = 20` in f() lässt globales `x = 10` unverändert).
- Lesen vor Zuweisen derselben Variable in der Funktion → `UnboundLocalError` (Lösung `global` oder Parameter/return).

### Einrückung
Verschachtelte if/elif-Blöcke: Die Einrückungsebene bestimmt, zu welchem Block eine Zeile gehört. Ein um eine Ebene verschobenes `if` ändert die Logik komplett (wird z. B. unabhängig vom elif-Ergebnis geprüft).

## Discovery 28: Write and Troubleshoot Python Scripts

Umgebung: Ubuntu-Workstation, VS Code, Verzeichnis `~/files/lab5`. Befehle: `cd`, `code datei.py` (öffnet/erzeugt in VS Code), `python datei.py`; Terminal in VS Code: Ctrl+Shift+`.

**Task 1** – `welcome.py` mit einer Zeile `print("Welcome to the world of Cisco Network Programmability!")`, Ausführung `python welcome.py`.

**Task 2** – `python-intro.py`: drei Dictionaries `facts_1..3` (Schlüssel `os`, `fqdn`, `location`, `vlans_list`, `neighbors`) und ein Dictionary `facts = {'sw1': facts_1, 'sw2': facts_2, 'sw3': facts_3}`.
```python
print(facts['sw1'])                         # ganzes Dictionary von sw1
for vlan in facts['sw2']['vlans_list']:     # 1, 10, 20
    print(vlan)
print(facts['sw2']['neighbors'][1])         # sw3 (zweiter Nachbar)
print(facts['sw3']['neighbors'][0])         # sw1 (erster Nachbar)
```
Mit Python 3.7+ druckt `print(facts['sw1'])` die Schlüssel in Einfügereihenfolge: `{'os': '7.2', 'fqdn': 'cisco.com', 'location': 'sjc', 'vlans_list': [1, 5, 10], 'neighbors': ['sw2', 'sw3']}`.

**Task 3** – `simulator.py` debuggen und verbessern:
1. Fehler: fehlender Doppelpunkt nach `def get_interface_info()` (Zeile 14) → Python 3 meldet `SyntaxError: expected ':'` mit Caret unter der Stelle.
2. Best Practices: Fehlerbehandlung mit `try/except Exception as e:` und `print(f"Error fetching data: {e}")`, `return None`; Hauptlogik in `def main()` und unter `if __name__ == "__main__": main()`; lesbare Ausgabe mit `print(json.dumps(interface_info, indent=4))` (erfordert `import json`). `json.dumps` erzeugt JSON-Text (doppelte Anführungszeichen, `true`/`false`).

### Fehlermeldungen (Troubleshooting)
| Fehler | Typischer Auslöser |
|---|---|
| SyntaxError | fehlender `:`; Python-2-`print x` („Missing parentheses in call to 'print'“) |
| IndentationError | `expected an indented block` nach `:`; `unexpected indent` |
| NameError | Tippfehler, Variable nicht definiert, Modul nicht importiert, lokale Variable außerhalb der Funktion |
| UnboundLocalError | lokale Variable gelesen, bevor sie in der Funktion zugewiesen wurde |
| TypeError | `'5' + 3`, Zuweisung an String/Tupel-Element |
| KeyError | falscher/case-falscher Dictionary-Schlüssel (`'vlan_list'` statt `'vlans_list'`) |
| IndexError | Index ≥ Länge |
| ValueError | `int('10.5')`, `str.index()` ohne Treffer |
| AttributeError | Methode existiert nicht (`'R1'.uppercase()`) |

Traceback von unten lesen: letzte Zeile = Fehlertyp + Detail, darüber Datei/Zeile. Syntax- und Einrückungsfehler treten vor der Ausführung auf, alle anderen erst zur Laufzeit.

## Fehler/Ungenauigkeiten im Kurs

1. **Python-2-Syntax in einem Python-3-Kapitel**: `print banner`, `print iplist[1]`, `print vlan, vlan_exists(vlan)`, `print 'Function 1: ', ip` sind in Python 3 SyntaxErrors; korrekt `print(...)`. (Python-3-Doku, „What's New In Python 3.0“: print is a function.)
2. **`type('1.1.1.1')` zeigt `<type 'str'>`** – das ist Python-2-Ausgabe; Python 3 zeigt `<class 'str'>`. Ebenso `<type 'list'>`/`<type 'dict'>` auf S. 274.
3. **`144 / 12` → `12`** (S. 271): in Python 3 ist das Ergebnis `12.0`; `/` ist immer echte Division (PEP 238).
4. **`dir('hostname')`-Ausgabe** enthält `decode` und `__getslice__` – Methoden von Python-2-Strings, die es in Python 3 nicht gibt.
5. **Datentyp-Tabelle (S. 269)**: „Numbers = Integers“ unterschlägt float; „Booleans = Values and operators“ und „Files = Objects used by Python“ sind ungenau (bool ist ein Typ mit zwei Werten; Datei-Objekte entstehen mit `open()`).
6. **Mehrzeilige Kommentare „mit Delimiter“**: Python hat keine eigene Mehrzeilen-Kommentar-Syntax; üblich sind mehrere `#`-Zeilen oder Triple-Quote-Strings (Docstrings) (PEP 8, PEP 257).
7. **Scope-Beispiel (S. 274)**: `ipaddr = '200.100.1.1'` unter dem Entry Point wird in der Grafik als „Local variables“ beschriftet – laut Kurstext selbst (und tatsächlich) ist es eine globale Variable; deshalb zeigt die Funktion 200.100.1.1. Außerdem Tippfehler `'Main 1: '. ipaddr` (Punkt statt Komma) und `vendor -- 'cisco'` (statt `==`).
8. **Execute-Note**: Ein Skript „mit der Anweisung cisco“ zu starten setzt Shebang, `chmod +x` und PATH bzw. `./cisco` voraus.
9. **.pyc-Aussage**: Python 3 legt .pyc nicht „im selben Verzeichnis wie das Skript“ ab, sondern in `__pycache__/`, und nur für importierte Module, nicht für das direkt gestartete Skript (PEP 3147).
10. **„Python 3 drastically changed the language to address security issues“**: Hauptgrund für Python 3 war das Bereinigen von Designfehlern (Unicode-Strings, print, Integer-Division), nicht primär Sicherheit.
11. **Lab Task 2**: Schritt 2–4 verwenden den Schlüssel `vlan_list`, das Endskript `vlans_list` – mischt man beides, entsteht `KeyError`. Die gezeigte Ausgabe-Reihenfolge des Dictionarys entspricht nicht Python 3.7+ (Einfügereihenfolge).
12. **Lab Task 3**: Die Fehlermeldung zeigt keine Fehlerzeile (`SyntaxError: expected ':'` fehlt). Die gezeigte `json.dumps`-Ausgabe enthält ein Komma nach `"enabled": true,` – json.dumps erzeugt kein solches Trailing-Komma. Die Ausgabe von Schritt 3 (`print(dict)`) ist im JSON-Stil (`true`) dargestellt; ein Python-Dictionary würde `True` und einfache Anführungszeichen zeigen. Der `try`-Block umschließt nur `return interface_data` und „parst“ kein JSON.
13. **Quizfrage S. 271** („three operators valid“): `@` ist seit Python 3.5 ebenfalls ein gültiger Operator (Matrix-Multiplikation, PEP 465).

## Bilder

- `bilder/25-python/01-datentypen.svg` – Tabelle der Datentypen mit Beispiel, type()-Ausgabe und Merkmal, dazu Typumwandlung und falsy-Werte.
- `bilder/25-python/02-indizes.svg` – String 'Gi0/1' mit positiven und negativen Indizes und Slicing-Beispielen.
- `bilder/25-python/03-str-methoden.svg` – wichtige String-Methoden als Eingabe → Rückgabe.
- `bilder/25-python/04-operatoren.svg` – arithmetische Operatoren mit 7 und 2 und die Operator-Rangfolge mit Rechenbeispielen.
- `bilder/25-python/05-if-elif-else.svg` – Code-Beispiel und Flussdiagramm einer if/elif/else-Kette.
- `bilder/25-python/06-schleifen.svg` – for, while, range() sowie break/continue als Ablauf 1-2-(3)-4-(5).
- `bilder/25-python/07-skript.svg` – Aufbau eines Skripts (Shebang, Kommentar, import, def, Entry Point) und Ausführung im Terminal.
- `bilder/25-python/08-scope.svg` – globaler vs. lokaler Scope am Kursbeispiel mit Ausgabe und NameError.
- `bilder/25-python/09-verschachtelt.svg` – Zugriff facts['sw2']['neighbors'][1] über dict → dict → list.
- `bilder/25-python/10-fehler.svg` – Fehlertypen mit Auslöser und Lösung sowie wie man einen Traceback liest.
