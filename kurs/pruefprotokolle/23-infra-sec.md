# Prüfprotokoll 23-infra-sec (Checker)

Geprüft: 144 Fragen (slg-is-001 … 144), Lektion (7 Seiten, alle Tabellenzellen), Wissensdatei, 7 SVGs.
Ergebnis pruefen.ps1 (ohne -Mischen): OK – 144 Fragen (single 90, multi 15, luecke 10, zuordnung 13, cli 16; Schwierigkeit 32/74/38).

## Wildcard-Rechnungen (alle nachgerechnet, korrekt)
009 (/27 → 0.0.0.31), 010 (32–47 = 0.0.15.255; 0.0.16.255 nicht zusammenhängend → .32.x und .48.x), 011 (8–11 = 0.0.3.255; 0.0.4.255 und 0.0.11.255 keine Blöcke), 012 (50 außerhalb 32–47), 013 (0.0.0.254 → ungerade Adressen; IOS-Normalisierung lässt .1 stehen), 014 (255.255.255.0 als Wildcard → Adresse wird zu 0.0.0.0, matcht x.x.x.0 → 172.20.5.0), 016 (1. und 3. Oktett geprüft → 10.77.5.9), 073, 102, 106, 107 (/29 → 0.0.0.7), 117, Lektion S. 2, SVG 02 (172.16.32.0 0.0.31.255 = /19, 32–63).

## Korrekturen
| ID | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-is-030 | Frage nannte „outbound ACL on the LAN interface“ – dort hätte der Client-Verkehr nie die Quelle 10.1.1.0/24, die Frage war doppelt fehlerhaft/mehrdeutig | „inbound ACL on the LAN interface“ | Logik der ACL-Richtung (Doc 23602) |
| slg-is-047 | Erklärung behauptete, die Extended-ACL mit Ziel „any“ filtere „nicht zu viel“ – sie sperrt PC2 aber für alle Ziele über den Router | Erklärung umformuliert (mit konkretem Ziel ließe sie sich auf Internetverkehr beschränken) | – |
| slg-is-081 | Distraktor „police cir 50 pps … violate-action drop“ nicht sicher ungültig (pps-/violate-Syntax plattformabhängig) | ersetzt durch eindeutig falsches „police rate 50 pps conform-action transmit exceed-action transmit“, Erklärung ergänzt | – |
| Wissen §4 | „DHCP-Relay“ als Beispiel für geblockten Verkehr falsch (DHCP-Discover hat Quelle 0.0.0.0) | „Telnet/SSH zum Router“ | – |
| Wissen §8 | Bc-Formel ohne Quellenhinweis | Quelle (250 ms) und Hinweis, dass 1500-Byte-Minimum aus Kursausgaben stammt | https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/qos_mqc/configuration/xe-16-12/qos-mqc-xe-16-12-book/qos-pkt-policing.html |

Entfernt: keine.

## Gezielt belegte Writer-Markierungen
- 025 (nicht existierende ACL → alles passiert): „If an access list is referenced by name in a command, but the access list does not exist, all packets pass.“ – https://www.cisco.com/en/US/docs/ios/sec_data_plane/configuration/guide/sec_ip_entry_numbrng.html ; für nummerierte ACLs Community-Konsens (sehr alte IOS-Versionen verhielten sich anders). Beibehalten.
- 033 (established spoofbar, nur ACK/RST): Standardverhalten, keine Sitzungstabelle. Beibehalten.
- 059–061, 111, 127, 139 (Default-Bc): Cisco: Default-Burst = 250 ms bei der CIR (CIR/8 × 0,25 = CIR/32 Byte), Beispiel 100 Mbps → 3125000 Byte (ASR1k MQC Guide oben). 1500-Byte-Minimum durch die Kursausgaben belegt (8000/12000 bps → bc 1500); IOS-Command-Reference nennt 1500 als Default-Normal-Burst (https://www.cisco.com/c/en/us/td/docs/ios/qos/command/reference/qos_book/qos_n1.html). Rechnungen: 300000/32 = 9375, 100000/32 = 3125, 64000/32 = 2000, 50000/32 = 1562,5 → 1562, 8000/32 = 250 → 1500. Beibehalten.
- 063 (deny in CoPP-ACL → nächste Klasse): MQC-Klassifizierung – deny = „kein Match“, weiter mit der nächsten Klasse (Cisco-QoS-Guide-Formulierung „the ACL being processed is skipped, and the next ACL is processed“, Community/cisco-nsp). Beibehalten.
- 066 (Cat9k system-cpp-policy): Ab Werk installiert, nicht löschbar, Klassen nicht änderbar, Raten anpassbar – https://www.cisco.com/c/en/us/support/docs/switches/catalyst-9300-switch/221841-troubleshoot-control-plane-operations-on.html und Cat9300 CoPP Config Guide. Beibehalten.
- 088 (Interface-ACL vor CoPP): Eingehende Interface-Features (iACL) werden vor der Control-Plane-Policy ausgewertet (Cisco Control Plane Security Overview, Community). Option formuliert vorsichtig („interface ACL or another filter … before CoPP“). Beibehalten.
- 013/016 (nicht zusammenhängende Wildcards): nachgerechnet, korrekt.
- 023 (U.U.U): ACL-deny → ICMP unreachable (admin. prohibited), IOS-Ratenbegrenzung der Unreachables → Punkte. Beibehalten.
- 077/115/133 (resequence): Syntax „ip access-list resequence access-list-name starting-sequence-number increment“ – Sequenznummern-Guide oben. Default 10/+10, Einträge ohne Nummer +10 am Ende (026, 044, 076). Beibehalten.
- 027 (no access-list 101 <Zeile> löscht ganze ACL): Doc 23602 „the entire ACL is deleted“ – https://www.cisco.com/c/en/us/support/docs/security/ios-firewall/23602-confaccesslists.html . Nummernbereiche (001–003, 116) ebenfalls dort.

## Lektion / Bilder
- Lektion: alle Tabellenzellen und Abläufe korrekt, keine Änderung.
- SVGs 01–07: alle wohlgeformt ([xml] OK), Inhalte korrekt (02: /19-Rechnung geprüft). Keine Änderung.

## Unsichere Punkte
- 018/026/017: IOS kann Host-Einträge in Standard-ACLs in der Anzeige umsortieren (Doc 23602); die Fragen folgen den Kurs-Lab-Ausgaben, bei denen bei Überlappung die Reihenfolge erhalten bleibt. Beibehalten.
- 1500-Byte-Minimum des Default-Bc ist plattformabhängig; im Kurs-Lab (IOS) beobachtet.
- 052/105/071/097: Einordnung nach Kursdefinition (Services Plane, Catch-all-Ergebnisse).
