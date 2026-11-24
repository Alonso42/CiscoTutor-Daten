# Prüfprotokoll 05-stp

Geprüft: 140 Fragen (slg-st-001 bis -141, ohne -006) + Lektion (8 Seiten, alle Tabellenzellen).
Ergebnis: 6 Fragen korrigiert, 1 entfernt, 139 verbleibend. pruefen.ps1 (ohne -Mischen): OK.

## Quellen
- Q1: Cat9300 17.9 Layer 2 CG, Configuring STP: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-9/configuration_guide/lyr2/b_179_lyr2_9300_cg/configuring_spanning_tree_protocol.html
  (Default-Modus Rapid PVST+, Prio 0–61440/4096, Port-Prio 0–240/16, Timerbereiche Hello 1–10/FD 4–30/MaxAge 6–40, root primary 24576 bzw. 4096 unter Root, Abbruch wenn <1, secondary 28672, Extended System ID 4+12 Bit, Kostenwerte lang, long = Default)
- Q2: Cat9300 17.9, Optional STP Features: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-9/configuration_guide/lyr2/b_179_lyr2_9300_cg/configuring_optional_spanning_tree_features.html
  (BPDU Guard global nur PortFast-operativ / Interface unabhängig; BPDU Filter global vs. Interface; loopguard default; Root Guard und Loop Guard nicht gleichzeitig)
- Q3: Cat9300 17.9, MSTP: https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-9/configuration_guide/lyr2/b_179_lyr2_9300_cg/configuring_multiple_spanning_tree_protocol.html
  (Name max. 32 Zeichen, case sensitive; Revision 0–65535; Region = Name+Revision+Mapping; IST/Instanz 0; Region als virtuelle Bridge; M-Records; MST immer long; Port-Prio 0–240/16; Kosten 1–200000000; Link-Type aus Duplex)
- Q4: Troubleshoot MST on Catalyst 9000: https://www.cisco.com/c/en/us/support/docs/lan-switching/stp/218351-troubleshoot-mst-on-catalyst-9000-switch.html
  (show current/pending, abort, exit übernimmt, Digest, Bound(PVST), Prio-Anzeige "16385 (16384 sysid 1)", IST einzige BPDU-Instanz)
- Q5: Understand RSTP 802.1w: https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/24062-146.html
  (BPDU jede Hello-Time von jeder Bridge, 3 verpasste Hellos, Version 2, TC nur Nonedge->Forwarding, Flush außer Empfangsport, Sync, P2P/Shared aus Duplex, Alternate/Backup, Legacy-Kompatibilität pro Port)
- Q6: STP Topology Changes (Doc 12013): https://www3-realm.cisco.com/en/US/tech/tk389/tk621/technologies_tech_note09186a0080094797.shtml
  (TC-Bit Max Age + Forward Delay = 35 s; Aging auf Forward Delay verkürzt)
- Q7: PVID inconsistency (Doc 24063): https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/24063-pvid-inconsistency-24063.html
  (SSTP 0100.0ccc.cccd getaggt für Nicht-VLAN-1; VLAN 1 an IEEE-Adresse untagged im Native VLAN; show spanning-tree inconsistentports)
- Q8: Root Guard (Doc 10588): https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/10588-74.html (root-inconsistent = effektiv Listening, automatische Erholung)
- Q9: Loop Guard (Doc 10596): https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/10596-84.html (guard loop / loopguard default, Root/Alternate-Ports, exklusiv zu Root Guard, Erholung bei BPDU)
- Q10: Errdisable Recovery: https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/69980-errdisable-recovery.html (errdisable recovery cause bpduguard, Logtexte BLOCK_BPDUGUARD / ERR_DISABLE)
- Q11: switchport host (IOS XE 3SE CR): https://www3-realm.cisco.com/en/US/docs/ios-xml/ios/interface/command/ir-xe-3se-3850-cr-book_chapter_01101.html
- BPDU-Versionen 0/2/3: IEEE 802.1 Dokumente, z. B. https://grouper.ieee.org/groups/802/1/files/public/docs1999/rstp_migration05.pdf, Wireshark STP-Dissector https://www.wireshark.org/docs/dfref/s/stp.html

## Korrekturen
| ID | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-st-015 | Richtige Option sagte "nonedge ports", Cisco-Doku formuliert "alle Ports außer dem Empfangsport"; Distraktor "inkl. Edge-Ports" damit nicht sauber falsch | Optionen neutral: "all its other ports, but not on Gi0/1" vs. "all ports, including Gi0/1"; Erklärung angepasst | Q5 |
| slg-st-037 | Herkunft lange Methode | Erklärung ergänzt: aus IEEE 802.1t, in 802.1D-2004 übernommen | Q1 |
| slg-st-043 | Erklärung ließ offen, dass long auf Cat9k Default ist | Ergänzt: auf Catalyst 9000 ist long Default, alle Switches gleich | Q1, Q4 |
| slg-st-056 | Erklärung verwies auf Lab-Debug, das in der Frage nicht vorkommt | Ersetzt durch "(2 x Forward Delay)" | – |
| slg-st-061 | "accepted" unsicher (IOS könnte Timer-Relationen prüfen, z. B. FD 4 bei MaxAge 20) | Umformuliert: "within the configurable ranges" | Q1 |
| slg-st-117 | Option "show spanning-tree interface ... portfast" zeigt nicht den globalen BPDU-Guard-Default → zweite richtige Antwort nicht sauber | Ersetzt durch "show running-config \| include portfast"; Erklärung angepasst | Q2 |
| slg-st-136 | Distraktor "show spanning-tree blockedports" listet ggf. auch inkonsistente (blockierte) Ports → mehrdeutig | Distraktor ersetzt durch "show spanning-tree root" | Q7 |

## Entfernt
| ID | Grund |
|---|---|
| slg-st-127 | Vorrang BPDU Filter vor BPDU Guard am selben Interface nur in Foren/Labs (networklessons, Cisco Community) belegt, keine offizielle Cisco-Doku gefunden |

## Lektion
- Seite 3: lange Methode als 802.1t/802.1D-2004 bezeichnet, Hinweis "auf Catalyst 9000 Default lang" ergänzt, Tabellenkopf angepasst (Werte 100/19/4/2 und 2.000.000/200.000/20.000/2.000 bestätigt, Q1).
- Seite 6: Default-Modus auf Catalyst 9000 IOS-XE = Rapid PVST+ ergänzt (Q1). Kurs nennt PVST+ (älteres Verhalten).
- Seiten 5 und 8 (Proposal/Agreement, 3 Hellos, TC-Verhalten, Root/Loop Guard, BPDU Guard/Filter global vs. Interface, Recovery) gegen Q2, Q5, Q8, Q9 geprüft: korrekt.
- Übrige Seiten (Wahlkriterien, States, Varianten, MST-Region) korrekt.

## Geprüft ohne Änderung (besonders markierte)
- 008 (SSTP-Adresse getaggt) korrekt (Q7). 012/013 (Aging auf FD, TC 35 s) korrekt (Q6). 019 (3 Hellos = 6 s) korrekt (Q5). 078 (P2p Edge) korrekt laut Cisco Community/Command Reference. 082 (Version 2) korrekt (Q5). 088 (case sensitive) korrekt (Q3). 106 (28674) konsistent mit Q4-Ausgabeformat. 118/119 korrekt (Q2). 120 Logtexte korrekt (Q10; auf Cat6500 mit "-SP-"). 122 (show interfaces status err-disabled) korrekt (Q10). 125/126 korrekt (Q2). 136–140 korrekt (Q2, Q7, Q9).
- 027–031 root primary/secondary-Werte korrekt (Q1). 102 Port-Prio 16er-Schritte (Q1/Q3).

## Unsichere Punkte
- 096: Begründung "Mapping-Änderung im MST-Modus löst Neuberechnung aus" stammt aus dem Kurs; Cisco-Doku nennt nur, dass MST-Parameter vor dem Moduswechsel konfiguriert werden können (Q4). Fachlich plausibel (geänderter Digest = Regionsgrenze), belassen.
- 060: "Nicht-Root nutzt Root-Timer" gilt für PVST+ (Frage nennt PVST+), bei RSTP sendet jede Bridge im eigenen Hello-Takt.
- Course-Notizen nennen "Cisco-MST bis 16 Instanzen" (Cat9k-Troubleshooting-Doc: 16), Cat9300-CG nennt 65 – in keiner Frage verwendet.
