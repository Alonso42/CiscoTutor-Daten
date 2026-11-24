# Introducing Network Programmability Protocols

Quelle: ENCOR 1.4.10 Student Guide, Seiten 279–292 (Intro 278, Summary Challenge 293 und Answer Key 294 nicht ausgewertet)

Topics: ENCOR-6.2 (JSON), ENCOR-6.3 (Datenmodellierung/YANG), ENCOR-4.6 (NETCONF/RESTCONF konfigurieren und verifizieren), ENCOR-6.5 (REST-Antwortcodes), ENCOR-6.7 (Agent vs. agentless: Chef, Puppet, Ansible, SaltStack), ENCOR-6.1 (Python on-box/Guestshell)

Hinweis: Python-Beispiele im Kurs sind teils Python 2 (`print x`, `<type 'str'>`, `u'ios-xe'`). Alle Beispiele unten sind Python 3 und wurden mit Python 3.15 ausgeführt.

## Configuration-Management-Tools (S. 279)

Ziel: wiederkehrende manuelle Abläufe (VLAN überall anlegen, Firewall-Regeln ändern) automatisieren. Die Tools stammen aus DevOps (Server/Cloud), Netzwerkunterstützung kam erst später dazu.

Vorteile: Provisionierung und Deployment automatisieren, keine Programmierkenntnisse nötig, Software-Praktiken nutzbar (Versionskontrolle, Design Patterns, Tests), weniger manuelle Eingriffe, vorhersehbarere Ergebnisse.

| Tool | Sprache | Anweisungsformat | Agent | Besonderheit |
|---|---|---|---|---|
| Puppet | Ruby (Puppet-DSL) | Manifests | agent-basiert (Pull vom Puppet-Server) | ältestes Tool (2005), deklarativ |
| Chef | Ruby (+ Erlang im Server) | Recipes, gebündelt in Cookbooks | agent-basiert | Kurs: prozedural – Schritte in definierter Reihenfolge |
| Ansible | Python | Playbooks (Plays → Tasks), YAML | agentless (Push über SSH, NETCONF, REST-API …) | 2012, seit 2015 Red Hat |
| SaltStack (Salt) | Python | Module (Execution-/State-Module) | mit Agent (Minion) und ohne (salt-ssh) | 2011, eventgesteuert, modular |

- **Deklarativ** = Zielzustand beschreiben, das Tool kümmert sich um das „Wie“ (Puppet, letztlich alle Tools). **Prozedural/imperativ** = Schrittfolge vorgeben (Kurs ordnet Chef so ein).
- **Agent-basiert** heißt: auf jedem verwalteten Gerät muss ein Software-Agent laufen. Auf Routern/Switches ist das oft unmöglich → Proxy-Geräte nötig, höhere Einstiegshürde.
- **Agentless** (Ansible): niedrigste Einstiegshürde, kann jedes Gerät über eine vorhandene Schnittstelle ansprechen (SSH/CLI, NETCONF, REST, sogar SNMP).
- Playbook-Hierarchie: Playbook → eine oder mehrere Plays → einzelne Tasks (rufen Module auf).

## Entwicklung des Gerätemanagements (S. 280)

### SNMP
- Ende der 1980er entwickelt, gut für Monitoring (up/down, Zähler) und einfache Änderungen.
- `get-request` liest eine MIB-Variable vom Agenten (Gerät), `set-request` schreibt sie.
- **MIB** = hierarchisches Datenmodell für SNMP. Viele herstellerspezifische MIBs/Erweiterungen → hat sich nie für Konfigurationsmanagement durchgesetzt.
- Schwächen: SNMPv1/v2c nur einfache, unverschlüsselte Sicherheit (Community-Strings); nicht für Echtzeit; wenige beschreibbare MIBs; Konfiguration schwer wiederholbar oder zurückrollbar; kaum Bibliotheken für Programmiersprachen; skaliert schlecht. Google kündigte 2015 an, SNMP fürs Monitoring bis 2017 abzuschalten.

### CLI
- Zugriff über Konsole, Telnet, SSH; seit >20 Jahren De-facto-Standard für Konfiguration.
- Für Menschen gebaut, nicht für Maschinen: unstrukturierter Text, kein gemeinsames Datenmodell, fehleranfällig, nicht modular/wiederholbar. Automatisierung nur mit Expect-Skripten und eigenen Parsern.
- Bleibt wichtig für Troubleshooting, soll aber fürs Konfigurationsmanagement abgelöst werden.

### Anforderungen an moderne Programmierschnittstellen
- Einfach nutzbare Schnittstellen (Tools, Bibliotheken)
- Client-seitige Validierung/Fehlerprüfung (anhand des Modells, bevor das Gerät die Daten sieht)
- **Trennung von Konfigurations- und Betriebsdaten (operational state)**
- Eingebautes Backup/Restore, mehrere Konfigurationen, Änderungen vorbereiten und als **Transaktion** anwenden
- Menschen- und maschinenlesbar (JSON, XML)
- Mehrere Transporte (HTTP, SSH, TLS), mehrere Encodings (XML, JSON), offene APIs (REST, RESTCONF, NETCONF, gRPC), **modellgetrieben**.

## Datenformate (S. 281)

| Format | Endung | Struktur | typischer Einsatz |
|---|---|---|---|
| XML | .xml | `<tag>wert</tag>`, verschachtelte Tags | Maschine-zu-Maschine, XSL-Transformation, XML-Schema; NETCONF |
| JSON | .json | `{ }` Objekte, `[ ]` Arrays, `"key": value` | Server ↔ Webseite, REST/RESTCONF, Konfigurationsdateien |
| YAML | .yaml/.yml | Einrückung, `key: value`, `- ` für Listenelemente | Konfigurationsdateien, Ansible-Playbooks |

Gemeinsame Konzepte: Objekt mit Attributen, Key-Value-Paare (Key meist links vom Doppelpunkt), Werte: String, Zahl, Boolean, Array/Liste, verschachteltes Objekt. Jede Information lässt sich in jedem Format darstellen. Wahl: was das System/API verlangt; wenn alles geht, was man selbst am besten beherrscht.

### YAML
- Am besten für Menschen les- und schreibbar. Dokumentbeginn optional mit `---`.
- **Einrückung definiert die Struktur** – Whitespace ist signifikant. Üblich: 2 Leerzeichen pro Ebene. **Tabs sind verboten.**
- `key: value` (Doppelpunkt + Leerzeichen), keine Anführungszeichen nötig (Typ wird erraten), keine Kommas am Zeilenende.
- Listen: `- element` auf gleicher Einrückung.
- JSON ist (weitgehend, ab YAML 1.2 praktisch vollständig) eine Teilmenge von YAML → ein YAML-Parser liest JSON.

```yaml
---
user:
  name: john
  location:
    city: Austin
    state: TX
  roles:
    - admin
    - user
```

### JSON
- Aus JavaScript abgeleitet, sprachunabhängiges Textformat (RFC 8259).
- Objekt `{ }` mit `"name": wert`-Paaren, durch **Kommas** getrennt, **kein Komma nach dem letzten Element**.
- Keys immer Strings in **doppelten** Anführungszeichen. String-Werte ebenfalls in doppelten Anführungszeichen.
- Werttypen: string, number (ohne Anführungszeichen, keine führenden Nullen, kein Hex), object, array, `true`/`false`, `null` (alles klein).
- Keine Kommentare erlaubt.
- Whitespace außerhalb von Strings ist bedeutungslos (nur für Menschen). Innerhalb von Strings zählt er: `"john"` ≠ `"j o h n"`.
- Ein JSON-Text muss nicht mit `{` beginnen: auch ein Array oder ein einzelner Wert wie `100`, `true` oder `"Hello"` ist gültig (ein String aber nur mit Anführungszeichen).

### XML
- Markup-Sprache (wie HTML), erste Version 1998. Optionaler Prolog `<?xml version="1.0" encoding="UTF-8"?>`.
- Elemente `<key>value</key>`; Start- und End-Tag müssen exakt gleich heißen, **case-sensitive** (`<tag></TAG>` ist ungültig; `<tag>` und `<TAG>` sind verschiedene Elemente). Konvention: Kleinbuchstaben.
- Listen = wiederholte Elemente (`<roles>admin</roles><roles>user</roles>`).
- Whitespace: signifikant innerhalb von Inhalten (`<t1>John Wayne</t1>` ≠ `<t1>JohnWayne</t1>`), insignifikant zwischen Tags.
- **Namespaces** lösen Namenskonflikte (z. B. `<table>` als HTML-Tabelle vs. Möbel): `xmlns:prefix="URI"` im Start-Tag, dann `<prefix:tag>`. Die URI muss nur eindeutig sein, nicht abrufbar. Default-Namespace: `xmlns="URI"` ohne Präfix.
- JSON/YAML nutzen Namespaces selten – Ausnahme RESTCONF/YANG-JSON: Membernamen werden mit dem Modulnamen qualifiziert (`"ietf-interfaces:interfaces"`).

## JSON verstehen (S. 282)

- JSON-Objekt ↔ Python-Dictionary. Wer Dictionaries versteht, versteht JSON.
- Nexus (NX-OS) kann Show-Ausgaben als JSON liefern: `show hostname | json`, `show vlan brief | json` – jeder Wert bekommt einen beschreibenden Key, ideal für Skripte.
- **JSON Schema** beschreibt und validiert JSON-Objekte (Typ, `minimum`/`maximum`, `enum`, `required`) → client-seitige Validierung vor dem Senden an das Gerät. Für Netzwerk-APIs wenig verbreitet (dort übernimmt YANG diese Rolle).

### Python-Modul json

| Funktion | Richtung | Ergebnis |
|---|---|---|
| `json.dumps(obj, indent=4)` | Python → JSON-**String** | `str` (dump **s**tring) |
| `json.loads(text)` | JSON-String → Python | dict/list/str/int/float/bool/None |
| `json.dump(obj, f)` / `json.load(f)` | mit Dateiobjekt | schreibt/liest Datei |

Typabbildung: object↔dict, array↔list (Tuple wird zu Array), string↔str, number↔int/float, true/false↔True/False, null↔None. Dict-Keys werden beim Dump zu Strings (`{1: 'x'}` → `{"1": "x"}`).

APIs liefern **JSON-Strings**. Ein String, der wie ein Dict aussieht, ist keiner: Indexzugriff `data['os']` auf den String erzeugt `TypeError: string indices must be integers, not 'str'`. Lösung: `json.loads()`. Zum Senden umgekehrt `json.dumps()`. Bei `requests` liefert `response.json()` direkt das Python-Objekt.

```python
>>> import json
>>> json.dumps({'a': None, 'b': False})
'{"a": null, "b": false}'
>>> json.loads('{"vlan": 10, "up": true}')
{'vlan': 10, 'up': True}
>>> json.loads("{'a': 1}")
json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
>>> json.loads('{"enabled": True}')
json.decoder.JSONDecodeError: Expecting value: line 1 column 13 (char 12)
>>> json.loads('{"a":1, "a":2}')      # doppelter Key: letzter gewinnt
{'a': 2}
>>> json.loads('{"mtu": "1500"}')['mtu'] + 1
TypeError: can only concatenate str (not "int") to str
>>> json.dumps({'b': 1, 'a': 2}, sort_keys=True)
'{"a": 2, "b": 1}'
```

Verschachtelter Zugriff (RESTCONF-Antwort, IETF-Modell):
```python
d = json.loads(resp_text)
d['ietf-interfaces:interface']['ietf-ip:ipv4']['address'][0]['ip']   # '10.13.0.1'
```
Typische Fehler: Liste wie Dict indizieren (`TypeError: list indices must be integers or slices, not str`), Index zu groß (`IndexError`), fehlender Key (`KeyError`; `dict.get()` liefert stattdessen `None`).

## Discovery 29: JSON in Python, Guestshell (S. 283)

- **Guestshell**: virtualisierte Linux-Umgebung (Container) auf IOS XE, getrennt vom Host-OS; führt Python-Skripte und Linux-Apps aus, auch für Day-0-Provisionierung.
- Befehle: `guestshell enable` (Container starten; nutzt im Kurs die Management-VRF; auf vielen Plattformen muss vorher `iox` konfiguriert sein), `guestshell run python` bzw. `guestshell run python3` (Interpreter direkt), `guestshell` (Bash-Shell im Container, Prompt `[guestshell@guestshell ~]$`, Home `/home/guestshell`), `exit` zurück zur IOS-CLI.
- Python-Modul **`cli`** in der Guestshell: `cli.cli("show ip interface brief")` gibt die Ausgabe als String zurück, `cli.clip()` druckt sie, `cli.execute()` für einen einzelnen EXEC-Befehl, `cli.configure([...])` für Konfiguration.
- Übliche Alternative, um Code aufs Gerät zu bringen: `copy` von TFTP/FTP/HTTP-Server.
- Lab-Ablauf: Dict anlegen → `type()` = dict → `json.dumps(neighbor, indent=4)` → Ergebnis ist `str` → `json.loads()` → wieder dict.

## Model-Driven Programmability Stack (S. 284)

Frühe Geräte-APIs waren RPC-Wrapper um CLI-Befehle (unstrukturiert) oder proprietäre APIs mit unvollständiger Abdeckung. Lösung: modellbasierte APIs.

Datenmodelle beantworten: Wie ist ein VLAN-Objekt aufgebaut? Welcher Bereich ist gültig? Sind Leerzeichen im Namen erlaubt? String oder Integer? **Modelle werden nicht übertragen** – übertragen werden XML/JSON-Dokumente, die dem Modell entsprechen.

| Schicht | Beispiele |
|---|---|
| Apps | eigene Anwendungen |
| Bindings | SDKs / Bibliotheken (z. B. YDK, ncclient) |
| Protokolle | NETCONF, RESTCONF, gRPC (gNMI) |
| Encoding | XML, JSON, Google Protocol Buffers (GPB) |
| Transport | SSH, TLS, HTTP(S), HTTP/2 |
| Modelle | YANG-Datenmodelle |

- Die App arbeitet nur mit dem Modell; Protokoll/Encoding/Transport sind austauschbar. Der Server nutzt dasselbe Modell für alle Protokolle.
- REST wird nicht separat geführt: REST auf einem modellierten Gerät = RESTCONF.
- XML/JSON: selbstbeschreibend (lesbar), hierarchisch, von vielen Sprachen parsbar.

API-Vergleich (Kursabbildung):

| | CLI | SNMP | REST | NETCONF/RESTCONF | gRPC |
|---|---|---|---|---|---|
| Schema | keins | SMIv2 | XML/JSON-Schema | YANG | Protocol Buffer |
| Inhalt | proprietär | MIBs | XSD/JSD | YANG-Module | Services/Messages |
| Payload | Text | ASN.1 BER | XML/JSON | XML/JSON | binär |
| Protokoll | Telnet/SSH | SNMP | REST (HTTP) | RESTCONF/NETCONF | HTTP/2 |

## YANG (S. 285)

- **YANG** = Yet Another Next Generation, Datenmodellierungssprache der IETF: YANG 1.0 RFC 6020 (2010), YANG 1.1 RFC 7950 (2016).
- Beschreibt, was konfiguriert und überwacht werden kann und welche Aktionen (RPCs) möglich sind – **Konfigurations- und Zustandsdaten**.
- Ursprünglich für NETCONF entworfen, aber **protokollunabhängig** (RESTCONF, gNMI). YANG definiert keinen Transport.
- Eigenschaften: lesbar, hierarchisch (Baum), wiederverwendbare Typen (`typedef`) und Gruppen (`grouping`/`uses`), Erweiterung über `augment`, formale Constraints (`range`, `length`, `pattern`, `must`, `mandatory`), Module/Submodule, Versionierung über `revision`.
- YANG-Module sind für NETCONF/RESTCONF, was MIBs für SNMP sind.
- Schema-Baum (Modell) vs. Daten-Baum (Instanz, als XML oder JSON kodiert).
- Fehler in CLI/API (z. B. `speed` auf Loopback nicht vorhanden) = Verstoß gegen das Modell.

### Bausteine
| Statement | Bedeutung | JSON-Abbild |
|---|---|---|
| `module` | eigenständige Top-Level-Hierarchie, hat `namespace` und `prefix` | Präfix der Membernamen |
| `container` | gruppiert Knoten, hat selbst keinen Wert (`presence` macht ihn bedeutungstragend) | Objekt `{}` |
| `leaf` | genau ein Wert, keine Kinder, braucht `type` | `"name": wert` |
| `leaf-list` | Folge von Werten gleichen Typs (z. B. erlaubte VLANs) | Array von Werten `[10,20]` |
| `list` | Folge von Einträgen mit mehreren Leaves, identifiziert über `key` | Array von Objekten |
| `typedef` | eigener, wiederverwendbarer Datentyp | – |
| `grouping` / `uses` | wiederverwendbare Knotengruppe / deren Einbindung | – |
| `augment` | fügt Knoten in ein anderes Modul ein | Membername mit anderem Modulpräfix |
| `config false` | Zustands-/Betriebsdaten (read-only) | – |
| `import` / `include` | anderes Modul / Submodul einbinden | – |

- `list`-Key: muss eindeutig sein; **Pflicht, wenn die Liste Konfiguration ist** (`config true`), optional bei reinen Zustandslisten (RFC 7950, 7.8.2).
- Built-in-Typen u. a. `int8…int64`, `uint8…uint64`, `decimal64`, `string`, `boolean`, `enumeration`, `empty`, `union`, `leafref`, `identityref`. Es gibt **keinen Typ `int`**.
- `range` ist Unterstatement von `type`: `type uint16 { range "1..4094"; }`.

```yang
list vlan {
  key "id";
  leaf id   { type uint16 { range "1..4094"; } }
  leaf name { type string; }
}
leaf hostname { type string; mandatory true; config true; }
leaf-list allowed-vlans { type uint16; }
container system { container services { container snmp { presence "Enables SNMP"; } } }
```

Tree-Darstellung (pyang -f tree): `+--rw` = Konfiguration, `+--ro` = Zustand, `*` = list/leaf-list, `[name]` = Key, `?` = optionaler Leaf.
```
module: ietf-interfaces
  +--rw interfaces
     +--rw interface* [name]
        +--rw name        string
        +--rw enabled?    boolean
```
Werkzeuge: pyang, **Cisco YANG Suite** (Nachfolger des veralteten YANG Explorer), NETCONF `<get-schema>` (RFC 6022) zum Abruf der Modelle vom Gerät.

## Arten von YANG-Modellen (S. 286)

| Kategorie | Herausgeber | Beispiel | Eigenschaft |
|---|---|---|---|
| Industriestandard | IETF, OpenConfig, (ITU …) | ietf-interfaces, ietf-ip, openconfig-interfaces | herstellerneutral, Basisfunktionen |
| Cisco Common | Cisco | gemeinsame Modelle über IOS XE/XR/NX-OS (z. B. OTV) | Cisco-weit |
| Cisco plattformspezifisch / native | Cisco | Cisco-IOS-XE-native | volle Funktionalität einer Plattform |

- **Native** (Cisco-IOS-XE-native): jede CLI-Zeile ist modelliert → vollständige Abdeckung inkl. CDP, MOP, negotiation, EIGRP.
- **IETF**: Standardorganisation (beaufsichtigt vom IAB der Internet Society), formaler Prozess; Interface-Modell enthält nur Basisdaten (Name, Typ, enabled, IP/Maske, Beschreibung), keine Herstellerfeatures.
- **OpenConfig**: von Google gestartete, informelle Gruppe von Netzbetreibern ohne formale Governance. Modelle enthalten **config- und state-Container im selben Modell** (Konfiguration + Betriebsdaten wie oper-status, Zähler). IPv4-Adressen eines Interfaces stehen unter `subinterfaces` (auch ohne echte Subinterfaces).
- In der OpenConfig-JSON-Ausgabe sind Zähler wie `"in-octets": "407081366"` Strings: RFC 7951 kodiert 64-Bit-Integer (int64/uint64) und decimal64 als JSON-Strings.
- IETF-Ausgabe zeigt `"ietf-ip:ipv4"` innerhalb von `"ietf-interfaces:interface"`: Knoten aus einem anderen Modul (augment) werden mit dessen Modulnamen qualifiziert.

## NETCONF (S. 287–288)

- IETF-Protokoll für Konfigurationsmanagement: RFC 4741 (2006), aktuell **RFC 6241** (2011); SSH-Transport RFC 6242, TLS RFC 7589.
- Eigenschaften: Trennung Konfiguration/Zustand, mehrere Datastores, **Transaktionen** (alles oder nichts), client-seitige Validierung (dank YANG), Filter für selektiven Abruf, Client/Server, **sitzungsorientiert und stateful** (REST/RESTCONF sind stateless).
- **Port 830/TCP**, SSH-Subsystem `netconf`: `ssh -p 830 cisco@csr1kv -s netconf`.
- Payload immer **XML**.

### Schichten
| Schicht | Inhalt |
|---|---|
| Content | Konfigurations-/Zustandsdaten (XML nach YANG-Modell) |
| Operations | `<get>`, `<get-config>`, `<edit-config>`, `<copy-config>`, `<delete-config>`, `<lock>`, `<unlock>`, `<commit>`, `<validate>`, `<close-session>`, `<kill-session>` |
| Messages | `<rpc>`, `<rpc-reply>` (enthält `<data>`, `<ok/>` oder `<rpc-error>`), `<notification>` |
| Secure Transport | SSH (Pflicht), TLS; SOAP/BEEP gelten als veraltet |

### Operationen
| Operation | Zweck |
|---|---|
| `<get>` | running-Konfiguration **und** Zustandsdaten |
| `<get-config>` | nur Konfiguration aus einem angegebenen Datastore (`<source>`) |
| `<edit-config>` | ganze oder Teilkonfiguration in Ziel-Datastore laden (`<target>`) |
| `<copy-config>` | ganzen Datastore durch anderen ersetzen/erzeugen (z. B. running → startup) |
| `<delete-config>` | Datastore löschen – **nicht running** |
| `<lock>`/`<unlock>` | ganzen Datastore exklusiv sperren (gegen andere NETCONF-Clients, CLI, SNMP), kurzlebig |
| `<close-session>` | Sitzung ordentlich beenden |
| `<kill-session>` | fremde Sitzung erzwungen beenden |
| `<commit>` | candidate → running (Capability :candidate) |
| `<discard-changes>` | uncommitted Änderungen im candidate verwerfen |
| `<validate>` | Konfiguration prüfen (Capability :validate) |

`operation`-Attribut in `<edit-config>`: **merge** (Default über `<default-operation>`), **replace**, **create** (Fehler `data-exists`, falls vorhanden), **delete** (Fehler `data-missing`, falls nicht vorhanden), **remove** (löscht, kein Fehler wenn nicht vorhanden). `<default-operation>`: merge | replace | none. `<error-option>`: stop-on-error (Default), continue-on-error, rollback-on-error (Capability).

### Datastores
| Datastore | Beschreibung |
|---|---|
| running | aktive Konfiguration, immer vorhanden, einziger Pflicht-Datastore |
| candidate | Arbeitsbereich, wird per `<commit>` aktiv; Capability `urn:ietf:params:netconf:capability:candidate:1.0`; IOS XR nutzt ihn standardmäßig, IOS XE optional (`netconf-yang feature candidate-datastore`) |
| startup | wird beim Booten geladen; Änderungen an running landen dort **nicht automatisch** → `<copy-config>` running → startup |

### Session-Ablauf
1. Client verbindet sich zum SSH-Subsystem netconf (Port 830).
2. Server sendet `<hello>` mit allen Capabilities und `<session-id>`.
3. Client sendet `<hello>` mit seinen Capabilities (mind. base).
4. Client sendet `<rpc message-id="101">` mit Operation und Inhalt; Filter `type="subtree"` (immer verfügbar) oder `type="xpath"` (Capability :xpath).
5. Server antwortet `<rpc-reply message-id="101">` (gleiche message-id) mit `<data>`, `<ok/>` oder `<rpc-error>`.
6. `<close-session>`.

Framing: base:1.0 → jede Nachricht endet mit `]]>]]>`. Kündigen beide Seiten `urn:ietf:params:netconf:base:1.1` an, gilt **chunked framing** (`\n#<länge>\n…\n##\n`).

Capabilities-Beispiele: `urn:ietf:params:netconf:base:1.0`, `…:base:1.1`, `…:capability:writable-running:1.0`, `…:capability:candidate:1.0`, `…:capability:xpath:1.0`, `…:capability:validate:1.0`, `…:capability:rollback-on-error:1.0`, `…:capability:confirmed-commit:1.0`, dazu Modul-Capabilities (`http://cisco.com/ns/yang/Cisco-IOS-XE-native?module=Cisco-IOS-XE-native&revision=…`). Herstellerspezifische erkennt man an Namespaces wie `http://cisco.com/ns/yang/`, `urn:cisco:params:xml:ns:yang`, `http://tail-f.com/ns`.

Beispiel `<get>` mit Subtree-Filter (native Modell):
```xml
<rpc message-id="101" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <get>
    <filter type="subtree">
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface><GigabitEthernet><name>1</name></GigabitEthernet></interface>
      </native>
    </filter>
  </get>
</rpc>
```

### NETCONF und YANG
- NETCONF (RFC 6241): Protokoll, Session-Management, RPCs, Datastores. YANG (RFC 6020/7950): Sprache für Datenmodelle und RPCs, heute allgemeine Interface-Definitionssprache (NSO, OpenDaylight, YDK).
- NETCONF entstand vor YANG; frühe Implementierungen nutzten CLI-Text als Payload.
- System-Modell: Agent (NETCONF-Server auf dem Gerät) ↔ Manager (Client: NSO, ncclient, ODL).
- Zuordnung: Management-Info (Definition) = YANG-Modelle; Payload = XML-Inhalt; Services = NETCONF-Operationen; Remote Operations = RPC (`<rpc>`, `<rpc-reply>`, `<rpc-error>`); Transport = SSH/TLS.

### ncclient (Python)
```python
from ncclient import manager
with manager.connect(host='10.10.10.5', port=830, username='cisco', password='cisco',
                     hostkey_verify=False) as m:
    print(m.server_capabilities)
    r = m.get_config(source='running', filter=('subtree', flt))
    m.edit_config(target='running', config=cfg_xml)
```
Methoden entsprechen direkt den NETCONF-Operationen.

### IOS XE aktivieren und prüfen
Pflicht laut Cisco Programmability Configuration Guide: Benutzer mit privilege 15 und `netconf-yang`. `aaa new-model` ist optional – wenn aktiv, dann zusammen mit `aaa authentication login default local` und `aaa authorization exec default local` (oder AAA-Server). Legacy-NETCONF ggf. mit `no netconf legacy` abschalten. `netconf-yang feature candidate-datastore` schaltet den candidate-Datastore ein (NETCONF/RESTCONF werden dabei neu gestartet, laufende Sessions gehen verloren).
```
aaa new-model                               ! optional
aaa authentication login default local
aaa authorization exec default local
username cisco privilege 15 secret cisco
netconf-yang
!
show netconf-yang status      ! enabled, SSH-Port 830, candidate-datastore
show netconf-yang sessions
show platform software yang-management process   ! confd, ncsshd, nginx … running
```

## Discovery 30: NETCONF über SSH (S. 289)
- `ssh -p 830 cisco@csr1kv -s netconf` → Server-Hello mit hunderten Capabilities (inkl. base:1.1).
- Client-Hello per Copy/Paste senden, danach `<get>` auf `netconf-state/schemas` (RFC 6022) → Liste verfügbarer YANG-Schemas; einzelne Schemas mit `<get-schema>`.
- Erkenntnis: Handarbeit über SSH ist fehleranfällig (Framing!) → in der Praxis ncclient/YDK.

## REST (S. 290)

- REST (Representational State Transfer), Roy Fielding 2000. Client/Server, **stateless**: jede Anfrage steht für sich.
- Wie Webbrowsing: Client schickt HTTP-Methode + URL (+ Body), Server antwortet mit JSON/XML.
- Für einen API-Call braucht man: Methode, vollständige URL, ggf. Body, Header, Authentifizierung (Basic Auth `Authorization: Basic base64(user:pass)` oder Token).
- Header: **Content-Type** = Format des gesendeten Bodys, **Accept** = gewünschtes Format der Antwort.

| CRUD | HTTP | Eigenschaft |
|---|---|---|
| Create | POST | nicht safe, nicht idempotent |
| Read | GET | safe (ändert nichts), idempotent |
| Update (ersetzen) | PUT | idempotent, ganze Ressource |
| Update (teilweise) | PATCH | nur Änderungen |
| Delete | DELETE | idempotent |

Statuscodes:
| Code | Bedeutung |
|---|---|
| 200 OK | Erfolg, Antwort mit Body (z. B. GET) |
| 201 Created | neue Ressource angelegt (POST, PUT-Neuanlage) |
| 202 Accepted | angenommen, Verarbeitung noch nicht fertig (asynchron) |
| 204 No Content | Erfolg ohne Body (PATCH, PUT-Ersetzen, DELETE, RPC ohne Output) |
| 400 Bad Request | Syntax/Payload fehlerhaft |
| 401 Unauthorized | Authentifizierung fehlt/falsch |
| 403 Forbidden | verstanden, aber verweigert (keine Berechtigung) |
| 404 Not Found | Ressource/URI existiert nicht |
| 405 Method Not Allowed | Methode für die Ressource nicht erlaubt |
| 409 Conflict | z. B. POST auf bereits existierende Ressource |
| 415 Unsupported Media Type | Content-Type wird nicht unterstützt |
| 500 Internal Server Error | Fehler auf dem Server |
| 501 Not Implemented | Funktion nicht implementiert |

Tools: cURL (CLI), Postman (GUI), Python `requests` (`requests.get(url, auth=(u, p), headers=h, verify=False)`; `r.status_code`, `r.text`, `r.json()`).

## RESTCONF (S. 291–292)

- **RFC 8040** (Januar 2017): HTTP-basiertes Protokoll für den Zugriff auf YANG-modellierte Daten in NETCONF-Datastore-Konzepten. „NETCONF ohne SSH, dafür HTTP(S) und JSON“.
- **HTTPS (TCP 443)**, Encoding **XML oder JSON** (RFC 7951 = JSON-Kodierung von YANG). Media-Types: `application/yang-data+json`, `application/yang-data+xml`. IOS XE antwortet ohne Accept-Header mit XML.
- Stateless, Ressourcen-orientiert, URIs folgen direkt aus dem YANG-Modell.
- Root-Discovery: `GET /.well-known/host-meta` → Link auf `/restconf`.
- API-Ressource `{+restconf}` mit `data` (kombinierte Konfig- + Zustandsdaten, Pflicht), `operations` (RPCs/Actions, optional), `yang-library-version` (Pflicht-Leaf, Revision von ietf-yang-library).

### URI-Aufbau
```
https://<host>/restconf/data/<modul>:<container>/<knoten>/<liste>=<key>/<leaf>
https://csr1kv/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet=1/ip
https://csr1kv/restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet1
https://sw1/restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet1%2F0%2F1
POST https://csr1kv/restconf/operations/<modul>:<rpc>
```
- Erstes Element mit Modulname qualifiziert, Listen-Keys mit `=`, mehrere Keys durch Komma, `/` in Key-Werten als `%2F` kodieren.
- Query-Parameter: `depth` (1..65535 oder unbounded, Default unbounded; Zielknoten = Tiefe 1, `depth=1` liefert also nur den Zielknoten ohne Kinder), `fields`, `content=config|nonconfig|all`, `with-defaults`.

### Methoden ↔ NETCONF
| RESTCONF | NETCONF | Typische Antwort |
|---|---|---|
| GET | `<get>` / `<get-config>` | 200 |
| POST | `<edit-config>` operation=create bzw. RPC aufrufen | 201 (Ressource) / 204 bzw. 200 (RPC) / 409 wenn vorhanden |
| PUT | `<edit-config>` operation=replace (bzw. create) | 201 neu / 204 ersetzt |
| PATCH | `<edit-config>` operation=merge | 204 |
| DELETE | `<edit-config>` operation=delete | 204 / 404 wenn nicht vorhanden (IOS XE, Kurs-Lab) |

- Nicht unterstützt (vs. NETCONF): Locking, candidate-Datastore/Commit, startup-Datastore, validate, confirmed commit.
- PUT ersetzt die gesamte Zielressource: nicht im Body enthaltene Attribute gehen verloren (Lab: PUT einer Sekundäradresse scheitert, weil die Primäradresse fehlt). Für Änderungen meist **PATCH**.

### IOS XE aktivieren und prüfen
```
aaa new-model
aaa authentication login default local
aaa authorization exec default local
username cisco privilege 15 secret cisco
ip http secure-server
ip http authentication local
restconf
!
show platform software yang-management process   ! nginx muss running sein
```
Probleme: 401 → Credentials/AAA/privilege 15; Zertifikatsfehler im Client bei Self-Signed-Zertifikat (`verify=False` bzw. `curl -k`); Port 830 ist NETCONF, nicht RESTCONF.

### Discovery 31 (Lab)
- Browser: `https://csr1kv/restconf/` → XML der Root-Ressource. Weiter mit `/data/Cisco-IOS-XE-native:native`, `/interface`, `/GigabitEthernet=1`, `?fields=name`, `/ip`.
- VS Code REST Client (`restconf.http`) → Code-Snippet für Python requests. Fehler 1: SSL-Verifikation (Self-Signed) → `verify=False`. Fehler 2: Authentifizierung → `HTTPBasicAuth('cisco','cisco')`. JSON statt XML: Header `'Accept': 'application/yang-data+json'`.
- POST auf existierendes GigabitEthernet1 scheitert (POST überschreibt nicht), POST Loopback1 klappt. DELETE Loopback1 → **204**, nochmal DELETE → **404**.
- PUT vs. PATCH: PATCH = merge, ändert nur die angegebenen Attribute.

## Fehler/Ungenauigkeiten im Kurs
1. S. 281: Als gültige JSON-Dokumente wird `Hello World!` ohne Anführungszeichen genannt. Korrekt: Ein JSON-String braucht doppelte Anführungszeichen (`"Hello World!"`); `100` und `true` sind gültig (RFC 8259, Abschnitt 2 und 7).
2. S. 281: „RESTCONF is a subset of NETCONF“. Korrekt: RESTCONF ist ein eigenes HTTP-basiertes Protokoll (RFC 8040), das einen Teil der NETCONF-Funktionen auf YANG-Daten abbildet.
3. S. 282/283: Python-2-Syntax (`print type(facts)`, `<type 'str'>`, `u'ios-xe'`). Python 3: `print(type(facts))` → `<class 'str'>`; Fehlermeldung `string indices must be integers, not 'str'`.
4. S. 282: JSON-Schema für VLAN mit `"maximum": 4096`. Gültige VLAN-IDs sind 1–4094 (0 und 4095 reserviert, IEEE 802.1Q). Außerdem enthält das Beispiel ein Komma nach dem letzten Property und typografische Anführungszeichen → kein gültiges JSON.
5. S. 285: YANG-List-Beispiel `type int; range 1..4094;`. YANG hat keinen Typ `int`, und `range` ist Unterstatement von `type`: `type uint16 { range "1..4094"; }` (RFC 7950, 9.2).
6. S. 285: BGP-AS-Nummern 0–65535 als Beispiel; seit 4-Byte-ASNs (RFC 6793) reicht der Bereich bis 4294967295.
7. S. 287: Client-Hello mit `urn:ietf:params:xml:ns:netconf:base:1.0` als Capability. Korrekt: Capability-URN `urn:ietf:params:netconf:base:1.0` (die xml:ns-Form ist der XML-Namespace).
8. S. 287: „Alle Nachrichten müssen mit `]]>]]>` enden“. Gilt nur für base:1.0; bei base:1.1 auf beiden Seiten wird chunked framing verwendet (RFC 6242, Abschnitt 4).
9. S. 287: SOAP als NETCONF-Transport. SSH ist Pflicht (RFC 6241/6242), TLS optional (RFC 7589); SOAP- und BEEP-Transport sind historisch.
10. S. 290: Nexus-REST-Beispiel `"mtu" : "default" "speed" : "auto"` ohne Kommas → ungültiges JSON.
11. S. 290: Postman als „Google Chrome application“ – die Chrome-App ist eingestellt; Postman ist heute eine eigenständige Desktop-/Web-Anwendung.
12. S. 291/292: Verweise auf RESTCONF-Drafts und Media-Types `application/yang.api+json` / `application/yang.data+json`; S. 292 behauptet sogar, RESTCONF sei noch kein RFC. Korrekt: RFC 8040 (2017) mit `application/yang-data+json` bzw. `+xml`; IOS XE unterstützt RESTCONF seit 16.x voll.
13. S. 292: „POST oder PUT erzeugt die Ressource und ersetzt vorhandenen Inhalt“. Korrekt: POST erzeugt nur neue Ressourcen und liefert bei existierender Ressource **409 Conflict** (RFC 8040, 4.4.1); nur PUT ersetzt. Das Lab selbst zeigt das Scheitern des POST.
14. S. 288: Tabelle „Configuration can be CLI (1.0) or YANG (1.1)“ ist irreführend: NETCONF base:1.0/1.1 unterscheiden sich im Framing/Details, nicht im Payload-Typ; YANG 1.1 ist eine Version der Modellierungssprache.

## Bilder
- `bilder/26-programmability/01-stack.svg` – Model-Driven-Programmability-Stack: Apps, Bindings, Protokolle, Encoding, Transport, Modelle mit Beispielen.
- `bilder/26-programmability/02-api.svg` – Vergleich CLI, SNMP, REST, NETCONF/RESTCONF, gRPC nach Schema, Inhalt, Payload, Protokoll; Schwächen von SNMP/CLI und Anforderungen an moderne APIs.
- `bilder/26-programmability/03-formate.svg` – Dieselben Benutzerdaten in YAML, JSON und XML nebeneinander mit den wichtigsten Syntaxregeln.
- `bilder/26-programmability/04-json-py.svg` – Abbildung JSON ↔ Python mit json.loads/json.dumps und typische Fehler.
- `bilder/26-programmability/05-yang.svg` – YANG-Statements container, list mit key, leaf, leaf-list, config false und ihr JSON-Abbild.
- `bilder/26-programmability/06-modelle.svg` – Native vs. IETF vs. OpenConfig: Herausgeber, Umfang, Besonderheiten, JSON-Ausschnitte.
- `bilder/26-programmability/07-netconf.svg` – NETCONF-Schichten (Content, Operations, Messages, Transport) und Datastores running/candidate/startup.
- `bilder/26-programmability/08-session.svg` – Ablauf einer NETCONF-Sitzung über SSH 830: hello-Austausch, rpc, rpc-reply, close-session, Framing.
- `bilder/26-programmability/09-rest.svg` – CRUD ↔ HTTP-Methode ↔ NETCONF-Operation und typische Statuscodes.
- `bilder/26-programmability/10-uri.svg` – Aufbau einer RESTCONF-URI und Aktivierung auf IOS XE.
