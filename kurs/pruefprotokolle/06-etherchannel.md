# Prüfprotokoll 06-etherchannel

Geprüft: 111 Fragen (slg-ec-001 bis slg-ec-111), außerdem die Lektion (7 Seiten mit allen Tabellenzellen). Nach der Prüfung bleiben 111 Fragen, keine wurde entfernt. `pruefen.ps1 -Kapitel 06-etherchannel` meldet OK.

## Korrekturen
| ID | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-ec-054 | Laut Frage ist src-dst-ip der Default auf Catalyst 9000. Falsch: Auf dem Catalyst 9300 (IOS XE 17.x) ist der Default src-mac. | Die Frage gilt jetzt konkret für einen Cat9300 ohne Konfiguration. Richtig ist src-mac (Index 0). Die Erklärung ist neu geschrieben. | https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-9/configuration_guide/lyr2/b_179_lyr2_9300_cg/configuring_etherchannels.html ; Command Reference 17.9: "The default value is src-mac" |
| slg-ec-039 | In der Erklärung stand src-dst-ip als häufiger Default. | Neu: "Default plattformabhängig (Catalyst 9300: src-mac)". | wie oben |
| slg-ec-055 | Die Ausgabe zeigte die Member als (I). Der Cat9300-Leitfaden sagt aber: Kommt vom Partner keine LACP-Antwort, werden die Ports suspendiert. Ob I oder s erscheint, hängt also von Plattform und Version ab. Das widerspricht slg-ec-056/062/071, in denen ein Partner ohne LACP zu (s) führt. | Die Frage nennt keine Member-Flags mehr, nur noch "Po1 stays down (SD), no member bundled". In der Erklärung steht, dass je nach Plattform I oder s erscheint. | Cat9300 Config Guide (s. o.); TAC-Doku 220367 |
| slg-ec-087 | Die Erklärung war unpräzise. | Die IOS-Fehlermeldung "Command rejected ... Invalid etherchnl mode" wird genannt. | community.cisco.com/t5/switching/cisco-3130-g/td-p/2052037 (Community), Cat9300 CR: "Do not configure an EtherChannel in both the PAgP and LACP modes" |
| Lektion Seite 5 | Im Text stand "meist Default src-dst-ip". | Neu: "Default plattformabhängig, auf Catalyst 9300 src-mac". | wie 054 |

## Belegt (ohne Änderung), Auswahl
- 009: LACP aus 802.3ad, später 802.1AX, Standardwissen.
- 010/080/011/014: LACP wählt zuerst nach System Priority, dann System-ID (MAC), dann Port Priority, dann Portnummer. Der niedrigere Wert gewinnt, und die Port Priorities des kontrollierenden Switches gelten (Cat9300 Config Guide + CR).
- 012/013/014: system-priority und port-priority haben den Default 32768 und den Bereich 1–65535. Syntax `lacp system-priority` (global) und `lacp port-priority` (Interface) (Cat9300 CR 17.9).
- 015/016/034/089: `lacp max-bundle` 1–8 am Port-channel. 16 Ports sind möglich, davon 8 aktiv und 8 hot-standby. Flag H gibt es nur bei LACP (CR 17.9).
- 017: Ziel-MAC 0180.c200.0002 (TAC 220367).
- 030: `errdisable recovery cause channel-misconfig`, Default-Intervall 300 s (Cisco Tech Note 69980 errdisable-recovery).
- 058: Die Meldung "suspended: LACP currently not enabled on the remote port" ist bestätigt (TAC 220367).
- 066/084: `port-channel min-links` mit Bereich 2–8 am Port-channel (Cat9300 Config Guide). Flag M steht in der Flag-Legende (Lab).
- 068: `show lacp sys-id` (Config Guide, TAC 220367).
- 076/036/071: Unterschiedliche STP-Kosten verhindern das Bündeln nicht ("Ports with different spanning-tree path costs can form an EtherChannel..."). Die Kosten des Port-channel richten sich nach der Gesamtbandbreite.
- 081: `lacp rate fast` sendet jede Sekunde statt alle 30 s, Timeout 3 x 1 s bzw. 3 x 30 s (CR + TAC 220367).
- 082: `channel-protocol {lacp | pagp}` ist ein Interface-Befehl und dient nur zur Einschränkung (CR 17.9).
- 085: Bei L2 legt `channel-group` den Port-channel automatisch an (CR 17.9).
- 031/032: PAgP verwendet silent, wenn non-silent nicht angegeben ist (Config Guide).
- PBR 096/097/105/109: `set ip default next-hop` greift nur, wenn es keine explizite Route gibt. Mehrere Next Hops werden der Reihe nach versucht ("tried in turn"). `set ip next-hop` nutzt zuerst Policy Routing und danach die Routing-Tabelle (IOS IP Routing CR, iri-cr-s1).
- 098: Ein Next Hop muss adjazent sein ("must be the address of an adjacent router"). Ist er nicht adjazent, schlägt PBR fehl und das Paket wird normal geroutet (Cisco Community KB "PBR is not working with a non-adjacent next-hop router"). Für entfernte Next Hops gibt es `recursive`.
- 110/097: verify-availability mit track: Fällt das Objekt aus, "policy routing fails and unicast routing will route the packet" (CR).
- 100: "No match clause in the route map indicates all packets" (PBR Config Guide XE 16).
- 093/102/103/107: `ip policy` gilt für eingehende Pakete, `ip local policy` für vom Gerät erzeugte Pakete (PBR Config Guide).
- 099/101: Ein deny (in der Route-Map oder per ACL-deny) bedeutet: kein Policy Routing, sondern normales Forwarding (PBR Config Guide: "normal forwarding algorithm is used").
- 104: `match length` und `match ip address` sind PBR-Kriterien (PBR Config Guide).
- Topic ENCOR-3.2.d ("Describe policy-based routing") für PBR ist plausibel und wird im Bestand (repo-src/daten_fragen.json) genauso verwendet.

## Unsichere Punkte
- slg-ec-087: Dass IOS den gemischten Modus ablehnt ("Invalid etherchnl mode"), ist nur über die Cisco Community belegt, nicht über einen Config Guide. Das Verhalten ist plausibel und bekannt. Die Frage bleibt drin.
- slg-ec-098: Das Verhalten bei einem nicht adjazenten Next Hop ist nur über die Cisco Community KB belegt. Der Command Reference nennt nur die Pflicht zur Adjazenz.
- slg-ec-062/071/092 und die Lektionstabelle: Ob ein Port ohne LACP-Partner I oder s zeigt, hängt von der Plattform ab (standalone mode vs. suspend). Die Fragen beziehen sich auf das Lab bzw. den Cat9300-Leitfaden (suspended) und sind so in sich konsistent.
- slg-ec-049: Der Begriff "hash polarization" stammt eher aus der CEF-Welt, wird aber für EtherChannel genauso verwendet.

## Wissen & Bilder (Checker, 2026-11-24)

Geprüft: encor-1.4.10/wissen/06-etherchannel.md sowie 9 SVGs in bilder/06-etherchannel. Alle SVGs sind wohlgeformt, UTF-8 ohne BOM, haben <title> als erstes Kind und keinen Text außerhalb der viewBox (nach der Korrektur).

Quellen:
- E1: Cat9300 17.9 Configuring EtherChannels: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-9/configuration_guide/lyr2/b_179_lyr2_9300_cg/configuring_etherchannels.html
- E2: Understanding EtherChannel Load Balancing (TN 12023): https://www.cisco.com/c/en/us/support/docs/lan-switching/etherchannel/12023-4.html
- E3: Errdisable Recovery (TN 69980): https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/69980-errdisable-recovery.html
- E4: standalone-disable / I vs. s: Cisco Community, z. B. https://community.cisco.com/t5/switching/when-should-lacp-in-passive-mode-cause-ports-to-become-suspended/m-p/4637700 (nur Community)

Belegt (ohne Änderung): Default load-balance src-mac, min-links 2–8, max-bundle 1–8, LACP-Prioritäten 32768 / 1–65535, lacp rate fast 1 s statt 30 s, bis 16 LACP-Ports (8 aktiv + 8 Standby), PAgP max. 8 Ports, Allowed-VLAN-Konsistenz (E1). Ohne `non-silent` gilt silent, für auto und desirable (E1: „If you do not specify non-silent … silent mode is assumed“). Damit ist der offene Punkt PAgP-Default geklärt; die Wissensdatei war bereits korrekt. errdisable recovery channel-misconfig 300 s (E3). PBR-Abschnitt stimmt mit den im Fragenprotokoll belegten Quellen überein.

Korrekturen in der Wissensdatei:
| Stelle | Problem | Änderung | Quelle |
|---|---|---|---|
| Lastverteilung „3 Links → 2:1:1“ | Falsch: Catalyst verteilt 8 Hash-Werte, 3 Links ergeben 3:3:2 | Korrigiert. Verhältnisse für 5/6/7 Links ergänzt. Hinweis, dass das Bitmodell eine Vereinfachung ist. Neuer Kursfehler 9 | E2 |
| I vs. s (offener Punkt) | Die Ursache war unklar | Geklärt: `port-channel standalone-disable` entscheidet. Aktiv → `s`, sonst `I`. Der Default hängt von Plattform und Release ab. Der Cat9300-CG beschreibt Suspend | E1, E4 |
| Discovery-6-Begründung (offener Punkt) | Unsicher formuliert | Präzisiert: Die Allowed-VLAN-Regel gilt laut E1 für die Member eines Switches. LACP vergleicht keine VLAN-Listen mit dem Partner. Eine Abweichung zwischen den Switches kostet nur VLAN-11-Verkehr. Das SD im Lab ist so nicht belegbar und wohl eine noch laufende Neuverhandlung oder eine lokale Inkonsistenz | E1 |
| min-links | Bereich fehlte | `<2–8>` | E1 |
| EtherChannel Guard | Log ergänzt | `%SPANTREE-2-CHNL_MISCFG: Detected loop due to etherchannel misconfiguration of …` | E3 |

Bilder:
| Datei | Problem | Änderung |
|---|---|---|
| 06-buckets.svg | Zeigte 3 Links als 2:1:1 (4 Werte) | Neu gezeichnet: 8 Hash-Werte (0–7), 4 Links je 2 Werte (1:1:1:1), 3 Links 3:3:2. 6-Link-Hinweis mit 2:2:1:1:1:1 |
| 05-hash-xor.svg | Eine Zeile ragte über die viewBox hinaus. Hinweis auf das vereinfachte Modell fehlte | Zeile gekürzt, Fußnote „Vereinfachtes Kursmodell – intern 8 Hash-Werte“ ergänzt. XOR-Beispiele nachgerechnet, alle korrekt |
| übrige 7 | Inhaltlich korrekt (Modi-Matrix, LACP-Wahl mit max-bundle 4, Konsistenzregeln, Flags, Lab-Topologie, PBR) | – |

Fragen: Es ist keine geprüfte Frage als falsch aufgefallen. slg-ec-038 („einige Links tragen mehr“) passt zu 3:3:2. slg-ec-043/044 nutzen ausdrücklich das „simple XOR model“. slg-ec-055/071 sind mit der I/s-Klärung vereinbar.