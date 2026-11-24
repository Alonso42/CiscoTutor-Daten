# Kapitelprüfung 26-programmability

Geprüft: 146 Fragen (fragen/26-programmability.json), Lektion (7 Seiten inkl. aller Tabellenzellen), Wissensdatei, 10 SVGs.
Ergebnis pruefen.ps1 (ohne -Mischen): OK. Alle 10 SVGs mit [xml] wohlgeformt.

## Methode
- Alle Python-/JSON-Snippets (035–039, 041–045, 050, 052–054, 022, 025–029, 032, 034) lokal mit `python -I` (3.15) ausgeführt bzw. mit json.loads geprüft – alle markierten Antworten stimmen.
- RFC-Belege per WebFetch: RFC 8040, 6241, 6242, 7951, 7950 (7.8.2 via IETF-Mailingliste zitiert), RFC 9110 (Sekundärquellen).
- Cisco IOS XE 17.12 Programmability Configuration Guide (NETCONF, Guest Shell), Cisco-Blogs zu YANG Suite.
- ENCOR v1.2 Blueprint (PDF): 4.6 = Configure and verify NETCONF and RESTCONF; 6.1 Python; 6.2 JSON; 6.3 YANG; 6.5 REST-Codes; 6.7 agent vs. agentless; 5.3 REST API security; 4.1 SNMP.

## Korrekturen
| ID | Problem | Änderung | Quelle |
|---|---|---|---|
| 030 | Erklärung bezog sich auf Positionen („erste/zweite…“), passte nach Mischen nicht zur Optionsreihenfolge | Erklärung positionsunabhängig formuliert | eigene Ausführung/JSON-Schema-Semantik |
| 114 | „aaa new-model“ als Pflicht markiert; laut Cisco optional | Auf „Choose two“ umgebaut (netconf-yang + privilege-15-User), Distraktor „restconf“ statt aaa new-model | https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/prog/configuration/1712/b_1712_programmability_cg/m_1712_prog_yang_netconf.html |
| 126 | Distraktor 409 Conflict ist nach RFC 8040 Abschn. 7 (data-missing → 409) vertretbar → nicht eindeutig | Frage auf IOS-XE-Verhalten präzisiert, Distraktor durch 201 Created ersetzt | RFC 8040; Kurs-Lab |
| 144 | „first nesting level“ unscharf; RFC 8040 4.8.2: Zielknoten = Tiefe 1 | Option „Only the target node is returned, without its children“, Erklärung ergänzt | https://www.rfc-editor.org/rfc/rfc8040 |
| 053, 105, 134 | CLI-Bausteine in mehreren gültigen Reihenfolgen möglich (Keyword-Argumente/SSH-Optionen) | Reihenfolge im Fragetext vorgegeben | – |
| 009 | reine SNMP-Frage | Topic ENCOR-6.3 → ENCOR-4.1 | Blueprint v1.2 |
| 037, 039, 043, 044, 050, 054 | reine Python-Semantik (TypeError, Indexing, List Comprehension, dict-Reihenfolge) | Topic ENCOR-6.2 → ENCOR-6.1 | Blueprint v1.2 |
| 131 | Basic Auth = REST-API-Security | Topic ENCOR-6.5 → ENCOR-5.3 | Blueprint v1.2 |
| Lektion S. 6/7 | aaa new-model als Pflicht genannt | als optional formuliert | Cisco Prog. Guide 17.12 |
| Wissen | NETCONF-Aktivierung: aaa optional, `no netconf legacy`, candidate-datastore-Neustart ergänzt; depth=1-Semantik; DELETE-404 als IOS-XE-Verhalten markiert | ergänzt | Cisco Prog. Guide; RFC 8040 |
| 10-uri.svg | IETF-Key „Gi1“ – Key ist der volle Interfacename | „/interface=Loopback0/enabled“ (Schrift 12, passt in Kasten) | RFC 8343/IOS XE |

## Entfernt
Keine.

## Gezielt belegt (Writer-Markierungen)
054 (Py 3.7+ Einfügereihenfolge, ausgeführt), 071 (RFC 7950 7.8.2), 074/085 (RFC 7951 Abschn. 4 / 6.1), 077/081 (pyang-Tree-Notation RFC 8340), 080 (YANG Suite Nachfolger YANG Explorer, Cisco-Blog), 089–092 (RFC 6241 7.2), 101 (RFC 6241 8.1: Server MUSS Session bei session-id im Client-Hello beenden), 103/104 (RFC 6242 4.1/4.2: Hello immer mit ]]>]]>, danach chunked bei beidseitig base:1.1, Framing-Fehler → Session-Ende), 106/107 (RFC 6241 Abschn. 6 / 8.9), 109, 112 (`netconf-yang feature candidate-datastore`, Cisco Guide 17.12), 113/153 (show netconf-yang sessions; show platform software yang-management process mit confd/ncsshd/nginx), 115 (ncclient get_config), 118 (Capability-URN vs. XML-Namespace), 125 (RFC 9110 9.2.2), 131 (Base64), 137 (RFC 8040 3.5.3, Beispiel mit %2F), 143 (RFC 8040 3.6: 204 ohne Body), 145 (4.8.1 content=config|nonconfig|all, Default all), 146 (3.1 host-meta, rel restconf), 152 (3.3.3 yang-library-version mandatory), 156 (RFC 6241 8.3.4.2 discard-changes).

## Unsichere Punkte
- 126: RFC 8040 mappt data-missing auf 409; IOS XE (Kurs-Lab) liefert 404 – Frage deshalb explizit auf IOS XE bezogen.
- 123 / Wissen: „IOS XE antwortet ohne Accept-Header mit XML“ – aus Kurs-Lab/Praxis, nicht in Cisco-Guide nachgelesen.
- 058: Rückgabe von cli.cli() als String nur über Cisco-Blog/Community belegt (offizielle CLI-Python-Module-Seite nicht abgerufen).
- 007/Lektion: Salt „Module, eventgesteuert“ (Kursformulierung); Salt nutzt dafür State-Dateien (SLS) und Execution/State-Module – belassen.
