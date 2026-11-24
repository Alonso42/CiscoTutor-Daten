# Kapitelprüfung 19-services

Geprüft: 143 Fragen (fragen/19-services.json), Lektion (8 Seiten, alle Tabellenzellen/Stufen), Wissensdatei wissen/19-services.md, 10 SVGs (bilder/19-services, alle als [xml] wohlgeformt, Beschriftungen inhaltlich korrekt).
Ergebnis pruefen.ps1 (ohne -Mischen): OK, 143 Fragen (single 91, multi 14, cli 19, zuordnung 11, luecke 8; Schwierigkeit 33/82/28).

## Belege (gezielt geprüfte Punkte des Writers)
| IDs | Aussage | Ergebnis | Quelle |
|---|---|---|---|
| 004 | `ntp master` ohne Wert = Stratum 8 | bestätigt ("When enabled, the default stratum is 8") | https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/bsm/command/bsm-cr-book/bsm-cr-n1.html |
| 011, 012, 024 | access-group peer/serve/serve-only/query-only; `prefer` | bestätigt | wie oben |
| 023 | `ntp update-calendar` / `clock calendar-valid` | gängige IOS-Befehle, konsistent mit Command Reference (Abschnitt nicht vollständig geladen) | wie oben |
| 139 | kein Sync auf unsynchronisierte Quelle / Falseticker | konsistent mit RFC 5905 (Selection/Clustering) | https://www.rfc-editor.org/rfc/rfc5905 |
| 031–033, 044–046 | BMCA-Reihenfolge Priority1 → Class → Accuracy → Variance → Priority2 → Identity; Priority 0–255, Default 128 | bestätigt | https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-10/configuration_guide/lyr2/b_1710_lyr2_9300_cg/configuring_precision_time_protocol__ptp_.html |
| 037, 039, 040, 041, 047 | Boundary wird GM ohne bessere Clock; nur PTP-VLAN verarbeitet, Default Native VLAN; L3 nur IPv4 UDP (IPv6 nicht unterstützt); show ptp parent; `no ptp enable` | bestätigt | wie oben |
| 042, 140 | Boundary Clock verwirft fremde Domäne | nicht wörtlich im C9300-Guide gefunden; konsistent mit IEEE 1588 (Domänen isoliert) und Cisco-TS-Dokument (falsche Domäne = Sync-Fehler) – belassen | https://www.cisco.com/c/en/us/support/docs/switches/catalyst-9300-series-switches/221062-troubleshoot-precision-time-protocol-pt.html |
| 043, 045 | HW-Zeitstempel; Announce für BMCA | IEEE 1588 Standardwissen, konsistent mit Cisco-Guide | wie oben |
| 061 | logging trap Default informational | bestätigt (STIG/CIS: informational ist Default und erscheint nicht in der Config) | https://stigviewer.com/stig/cisco_ios_xe_router_ndm/2023-05-05/finding/V-215837 |
| 069 | `*` vor Zeitstempel = Zeit nicht autoritativ | konsistent mit Cisco `show clock` Referenz (* = not authoritative, . = authoritative aber NTP nicht synchron) | https://www.cisco.com/E-Learning/bulk/public/tac/cim/cib/using_cisco_ios_software/cmdrefs/show_clock.htm |
| 063, 064 | Console-Last / `logging source-interface`, `logging origin-id` | Cisco-Standardbefehle, korrekt | – |
| 071, 083 | Counter64 erst ab SNMPv2 (SMIv2), 32-bit-Wrap bei 10G ≈ 3,4 s | bestätigt (RFC 2578 Counter64; Rechnung 2^32·8/10^10) | https://www.rfc-editor.org/rfc/rfc2578 |
| 073–076 | `snmp-server community .. ro 10`, `snmp-server host .. version 2c ..`, `snmp-server group .. v3 priv`, `snmp-server user .. v3 auth sha .. priv aes 128 ..` | bestätigt | https://www.cisco.com/c/en/us/support/docs/switches/catalyst-9500-series-switches/224891-configure-snmpv2c-v3-on-catalyst-9000.html ; https://www.cisco.com/en/US/docs/ios-xml/ios/snmp/configuration/15-0s/nm-snmp-encrypt-snmp-support.html |
| 080 | GetNext/GetBulk/Set/Inform | RFC 3416 | https://www.rfc-editor.org/rfc/rfc3416 |
| 087 | ICMP im Zielport = Typ·256 + Code (Echo Request 2048) | gestützt durch NetFlow-v9-Feldbeschreibungen (ICMP_TYPE = type*256+code) und Cisco-Cache-Beispiele (0800) | https://docs.progress.com/bundle/progress-flowmon-flow-standards-specification/page/topics/Flowmon-standards-specification/NetFlow-v9.html ; https://seclists.org/basics/2004/Aug/93 |
| 088 | ToS 0xC0 → DSCP 48 CS6 | Rechnung korrekt | – |
| 090, 091 | Inactive 15 s, Active 1800 s | bestätigt (FNF Command Reference) | https://www3-realm.cisco.com/en/US/docs/ios-xml/ios/fnetflow/command/fnf-cr-book.pdf |
| 094 | v9 Template nötig | RFC 3954 | https://www.rfc-editor.org/rfc/rfc3954 |
| 095, 141 | ein Ziel pro Exporter, mehrere Exporter pro Monitor | bestätigt (Cisco Community/FNF-Guides) | https://community.cisco.com/t5/network-management/flexible-netflow-multiple-exporters/td-p/3329890 |
| 108 | `export-protocol ipfix`; Default v9 | bestätigt | https://cisco.com/go/q200fnf |
| 093 | IPFIX = RFC 7011 auf Basis v9 | bestätigt | https://www.rfc-editor.org/rfc/rfc7011 |
| 102, 106 | `show flow exporter statistics`; getrennte IPv4/IPv6-Monitore | FNF-Standard, korrekt | – |
| 114, 143 | Labels alphanumerisch sortiert | bestätigt (Beispiel: 120 vor 13) | https://www.cisco.com/c/en/us/support/docs/ios-nx-os-software/ios-xe-16/216091-best-practices-and-useful-scripts-for-ee.html |
| 115, 116 | sync yes: Policy vor Befehl, Exit-Status entscheidet; sync no + skip yes: Befehl nicht ausgeführt | bestätigt | https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/eem/command/eem-cr-book/eem-cr-e1.html |
| 121, 138 | maxrun Default 20 s, Keyword im event-Befehl | bestätigt | eem-cr-e1 / eem-cr-e2 |
| 118, 119, 129, 117, 122 | `event timer watchdog time`, `cron cron-entry`, `event track N state down`, `event syslog pattern`, `event none` | Syntax bestätigt | https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/eem/command/eem-cr-book/eem-cr-e2.html |
| 120 | `action .. syslog msg` | korrekt | – |
| 135 | `event manager directory user policy` + `event manager policy` | korrekt (EEM Command Reference) | – |

## Korrekturen
| ID/Datei | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-sv-017 | Poll 64–1024 s ist Cisco-Default, nicht allgemeines NTP (RFC 5905 MAXPOLL 17) | Frage auf "By default, a Cisco IOS NTP client ..." präzisiert | RFC 5905; bsm-cr-n1 (`ntp server minpoll/maxpoll`) |
| slg-sv-040 | Erklärung nur "laut Kurs" | durch Cisco-Beleg ersetzt (nur IPv4/UDP, IPv6 nicht unterstützt) | C9300 17.10 PTP Guide |
| wissen/19-services.md | Tippfehler "FNR" statt FNF (2x); Ergänzung C9300-PTP-Fakten (Default e2etransparent, global per Default aus, L3 nur IPv4, Priority1 255); Hinweis, dass Ciscos C9300-Guide selbst den Domain-Bereich-Widerspruch enthält | korrigiert/ergänzt | C9300 17.10 PTP Guide |
| lektionen/19-services.json | "v2c brachte GetBulk/Informs/64-bit" → "SNMPv2 (in der Praxis v2c)"; "laut Kurs Default" → Default (belegt) | präzisiert | RFC 3416/2578; C9300 Guide |

## Entfernt
keine

## Unsichere Punkte (belassen)
- 042/140: "Boundary Clock verwirft Pakete fremder Domäne" nicht wörtlich in Cisco-Doku gefunden, aber IEEE-1588-konform und kursbasiert.
- 028: "NTP ~1 ms im LAN" – Cisco-/Kursaussage; RFC 5905 nennt bessere Werte für moderne Hosts, unter den Optionen bleibt 1 ms eindeutig die beste.
- Wissen Fehler #8 (1,5 % Exportvolumen) bestätigt durch Cisco IOS NetFlow Data Export Guide (https://www.cisco.com/en/US/docs/ios-xml/ios/netflow/configuration/15-2s/cfg-nflow-data-expt.html).
