# Kapitelprüfung 16-wlan-ap (Examining Wireless AP Operation)

Datum: 2026-11-24 · Checker · WebSearch/WebFetch (kein Browser)

Geprüft: 110 Fragen (slg-wa-001 … 110), Lektion (6 Seiten inkl. aller Tabellenzellen), Wissensdatei, 9 SVGs.
Ergebnis: 108 Fragen verbleiben (single 73, multi 10, luecke 8, cli 10, zuordnung 7; S1 27 / S2 51 / S3 30). `pruefen.ps1 -Kapitel 16-wlan-ap` → OK. Alle 9 SVGs `[xml]`-wohlgeformt.

## Hauptquellen
- RFC 5415 (CAPWAP): https://www.rfc-editor.org/rfc/rfc5415 – Zustände Discovery → DTLS Setup → Join → Image Data → Configure → Data Check → Run; Echo Request als Keepalive; AC Descriptor (Active/Max WTPs), AC Name.
- Cisco 119286 (LAP not joining WLC): https://www.cisco.com/c/en/us/support/docs/wireless/5500-series-wireless-controllers/119286-lap-notjoin-wlc-tshoot.html – Discovery Reply mit System Name + Excess Capacity; P/S/T → Master → Least Loaded (excess capacity, Gleichstand: erster Antwortender); Mobility Peers bleiben über Reboot gespeichert; "Regulatory Domain Mismatch … not allowed to join"; WLC-Zeit muss im Gültigkeitszeitraum des AP-Zertifikats liegen; "AP Authorization failure".
- Cisco 221056 (AP Join Process 9800): https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9120axe-access-point/221056-understand-the-ap-join-process-with-the.html – Option 43/52, DNS CISCO-CAPWAP-CONTROLLER, Zustandsfolge, Backup Primary/Secondary im AP Join Profile (Priorität 4/5 nach P/S/T).
- Cisco 218396 (9800 AP Join TS): `show wireless stats ap join summary` (Status, letzter Disconnect-Grund, Phase).
- 9800 17.14 Config Guide AP Joining/Priority: https://www.cisco.com/c/en/us/td/docs/wireless/controller/9800/17-14/config-guide/b_wl_17_14_cg/m_set_ap_priority.html – Priorität 1–4, Default 1, `ap name <ap> priority <n>`.
- AireOS Failover Priority (Cisco-Guide-Spiegel ManualsLib): `config network ap-priority {enable|disable}`, `config ap priority {1|2|3|4} <AP>`, Default 1.
- AireOS Timer: Primary Discovery Timeout 30–3600 s, Default 120 s (Cisco-Guide-Spiegel manualshive; 7.5 Command Reference); Retransmit Count Default 5 (3–8), Interval Default 3 s (2–5) (mrncciew); Heartbeat 30 s (Cisco Community).
- 9800 HA SSO (220277): https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/220277-configure-high-availability-sso-on-catal.html – `redun-management interface Vlan39 chassis 1 address … chassis 2 address …`, `show redundancy`, `show chassis rmi`, eine WMI-IP für das Paar, gleiche SW-Version.
- AireOS HA DG 7.5: https://www.cisco.com/en/US/docs/wireless/controller/technotes/7.5/High_Availability_DG.html – AP SSO ab 7.3, Client SSO ab 7.5 (Clients nach Auth+DHCP), HA-SKU wird beim ersten Pairing Standby.
- 9800 Sniffer (217057): https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/217057-configure-access-point-in-sniffer-mode-o.html – AiroPeek-Header, 9800 leitet per UDP src 5555 / dst 5000 weiter, Wireshark Decode As PEEKREMOTE.
- AireOS→9800 Feature Matrix: https://www.cisco.com/c/en/us/td/docs/wireless/controller/technotes/8-8/AireOS_Cat_9800_Feature_Comparison_Matrix.html – Flex+Bridge ab 17.1.1s, OEAP ab 17.2.1, Sniffer/Monitor/Bridge, AP/Client SSO; **kein** Eintrag zu Rogue Detector Mode.
- Universal AP Priming (Cisco-Guide-Auszüge): GPS + MCC, SSID des AP im gleichen WLAN, WPA2-PSK empfohlen (manche Android ohne 802.1X), NDP im verschlüsselten Beacon-Teil, früher anders geprimte APs → manuell (nach Reset/Unprime).
- FlexConnect-Guides (7.2 cg_flexconnect, EMob 7.3 DG): Standalone-Zustände, Web-Auth: bestehende Clients bleiben, Beacons enden bei 0 Clients.
- RRM Off-Channel: Cisco 214393 (ca. 80 ms alle 3–20 s), 7.2 RRM-Guide (≤ 60 ms).
- Master Controller auf 9800: Cisco Community ("no master controller equivalent", Option 43/DNS/Priming).
- `ip forward-protocol udp 5246` + `ip helper-address`: mrncciew "WLC discovery via broadcast"; IOS-Default-Liste von helper-address (TFTP, DNS, Time, NetBIOS, TACACS, BOOTP) enthält 5246 nicht.

## Korrigiert
| ID | Problem | Änderung |
|---|---|---|
| wa-003 | "SSID must use WPA2-PSK" – Cisco nennt WPA2-PSK als Empfehlung (Android ohne 802.1X), nicht als harte Pflicht | Frage auf "recommended" umformuliert, Optionen vereinheitlicht, Erklärung angepasst |
| wa-005 | Erklärung unvollständig | Hinweis Reset/Unprime vor erneutem manuellem Priming |
| wa-023 | Ohne helper-address wäre auch Option 43 von einem entfernten DHCP-Server nicht erreichbar → mehrdeutig | Stamm: Router ist lokaler DHCP-Server |
| wa-031 | Distraktor/Lösung "Firewall drops UDP 5246" widerspricht "APs discover the WLC" (Discovery nutzt ebenfalls 5246) | Option ersetzt durch "AP authorization is on and the AP MACs are not listed" (Cisco 119286), Erklärung angepasst |
| wa-037 | Distraktor "9800 enables master option automatically on the active unit" heikel (9800 meldet sich laut Community/CSCvt22075 in Discovery-Antworten stets als Master) | Distraktor ersetzt durch "per SSID in the WLAN profile" |
| wa-039 | Least-Loaded nach Excess Capacity hängt von Kapazität ab; "two empty WLCs" ohne gleiche Kapazität nicht eindeutig | Stamm: "Two identical, empty WLCs" |
| wa-054 | Globale Aktivierung der Priorität ist AireOS-spezifisch (9800-Guide zeigt keinen globalen Schalter) | Stamm mit "AireOS:" gekennzeichnet |
| wa-075 | CLI-Lösung enthält "chassis" und "address" je zweimal, Bausteine nur einmal (Konvention im Bestand: Duplikate in Bausteinen) | zweites "chassis"/"address" in bausteine ergänzt |
| wa-083 | "etwa 50 ms" nur Kurs/Forum; Cisco nennt ≤ 60 ms bzw. ~80 ms | Erklärung: "einige Millisekunden (ca. 50–80 ms)", RRM-Monitor-Intervall 180 s |
| wa-084 | 13 s / 10 s nicht offiziell belegbar | Stamm ohne Zahlen ("more often in 5 GHz"), Zahlen nur als Kursbeispiel in Erklärung |
| wa-089 | "sniffer-mode AP forwards … UDP port 5000" – beim 9800 leitet der WLC weiter (src 5555/dst 5000), Cisco-Anleitung decodiert auf Port 5555 | Frage auf "Which protocol must be selected with Decode As?" umgestellt (PEEKREMOTE), Ports in Erklärung korrekt |

Lektion (16-wlan-ap.json): Seite 1 "empfohlen WPA2-PSK"; Seite 3 Least-Loaded als freie Kapazität (statt nur "relativ") + Join-Fehler Regulatory Domain Mismatch/AP-Autorisierung; Seite 6 Off-Channel "ca. 50–80 ms, Monitor-Intervall 180 s", Rogue Detector "AireOS" statt "beim 9800 entfallen", Sniffer mit AiroPeek/PEEKREMOTE.

Wissensdatei: WPA2-PSK als Empfehlung; Priming nur Lightweight, Reset vor Neu-Priming; Least-Loaded = excess capacity (119286) neben Kurs-Relativlast; Join-Troubleshooting mit Cisco-Logmeldungen; Rogue Detector 9800-Aussage entschärft (nicht belegt); Sniffer-Ports 5555→5000 und Weiterleitung über 9800; Off-Channel-Zeiten mit Quellen; Fehlerliste Punkt 7 angepasst.

SVGs: 01-priming "SSID (WPA2-PSK empf.)"; 04-capwap-fsm "Control-Kanal … (ab DTLS Setup verschlüsselt)" statt "immer DTLS" (Discovery ist unverschlüsselt); 08-apmodi Rogue Detector "(AireOS)" statt "(9800: entfallen)". Übrige SVGs inhaltlich korrekt (Join-Order, Least-Load-Tabelle nachgerechnet, Heartbeat/Timer, HA-Modelle, Mesh/AWPP).

## Entfernt
| ID | Grund |
|---|---|
| wa-088 | "Rogue detector mode is not supported on the Catalyst 9800" – in Cisco-Doku (Config Guides 17.14/26.x, Feature Matrix) nicht belegbar |
| wa-110 | Dublette zu slg-wd-059 (Kapitel 15): gleiche Kernaussage (zentral geswitchter Filialverkehr läuft zweimal über das WAN) |

## Rechenfragen nachgerechnet
- wa-038: WLC-A 200/250 = 80 % (50 frei), WLC-B 1000/2000 = 50 % (1000 frei) → WLC-B, beide Maßstäbe identisch. OK.
- wa-039 / SVG 05: AP1 Gleichstand → erster Antwortender; AP2 → WLC2 (0 vs 1); AP3 Gleichstand; AP4 → weniger belasteter. OK (gleiche Kapazität jetzt im Stamm).
- Wissens-Beispiel 10/50 vs 3/6: relativ 20 % vs 50 %, frei 40 vs 3 → gleiches Ergebnis.

## Belegte Writer-Markierungen (ohne Änderung)
010–012 (forward-protocol udp 5246 + helper-address), 015 (`domain-name` im DHCP-Pool = Option 15), 020 (Option 60), 022 (AC Name, Active/Max WTPs – RFC 5415 / 119286), 024–029 (DTLS, Zustandsfolge, Image Data, Uhrzeit/Zertifikat, MIC, Echo), 030 (Regulatory Domain Mismatch), 032 (`show wireless stats ap join summary`), 042 (`ap name … controller primary <name> <ip>`), 043 (`config network master-base enable`), 055 (`config network ap-priority enable`), 061/062 (`capwap backup primary <name> <ip>` im AP Join Profile), 074 (`show redundancy`), 075 (RMI-Syntax), 087 (Rogue Detector am Trunk), 103 (Flex+Bridge).

## Unsichere Punkte
- Master Controller auf 9800 (wa-037, wa-043-Erklärung): nur über Cisco Community belegt ("kein Äquivalent"); offizielle Doku nennt das Feature schlicht nicht.
- Heartbeat 30 s und Fast Heartbeat 1–10 s: nur Community/allgemeines Wissen, kein offizieller Guide-Treffer im Volltext.
- AP-Fallback-Unterbrechung 12–30 s, Off-Channel 13 s/10 s, HA-SKU-Beispiel 5508 50→500: Kurszahlen.
- Monitor-Submodi RFID/wIPS (wa-093): als Kursaussage gekennzeichnet.
