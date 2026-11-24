# Kapitelprüfung 03-switching-paths (Checker, 2026-11-24)

Geprüft: 116 Fragen (slg-sw-035…116 einzeln neu geprüft, slg-sw-001…034 gegengelesen – früheres Protokoll batch09.md), Wissensdatei `wissen/03-switching-paths.md`, Lektion (8 Seiten, jede Tabellenzelle), 8 SVGs in `bilder/03-switching-paths/`.
Struktur: `fragen/03-switching-paths.json` ist ein flaches Array (116 Objekte, keine Verschachtelung). `pruefen.ps1 -Kapitel 03-switching-paths` (ohne -Mischen): OK.
Verteilung: single 77, multi 9, cli 13, zuordnung 9, luecke 8 · Schwierigkeit 1:24 / 2:64 / 3:28.

## Korrekturen
| ID / Datei | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-sw-090 | Behauptung „IPv6-CEF wird automatisch mit ipv6 unicast-routing aktiviert“ nicht belegbar; Cisco-Guide behandelt `ipv6 cef` als eigenen Schritt mit `ip cef` als Voraussetzung | Lücke umgebaut: Voraussetzung für `ipv6 cef` ist `ip cef` (richtig = Index 1, Option „ip cef“), Erklärung neu | https://www.cisco.com/en/US/docs/ios-xml/ios/ipv6/configuration/15-0sy/ip6-addrg-bsc-con.html |
| slg-sw-108 | Erklärung: „Broadcast-Pings nur aus privilegiertem Modus erlaubt“ – nicht offiziell belegt (belegt ist nur: Extended Ping nur privilegiert) | Satz ersetzt durch Extended-Ping-Aussage | https://www.cisco.com/c/en/us/support/docs/ip/routing-information-protocol-rip/13730-ext-ping-trace.html |
| wissen (CEF-Lab) | gleiche IPv6-CEF-Aussage | korrigiert: `ipv6 unicast-routing` = Forwarding, `ipv6 cef` separat, `ip cef` Voraussetzung, Auto-Aktivierung plattformabhängig | wie 090 |
| wissen (Discovery 1) | Broadcast-Ping-Aussage | als Kursaussage markiert, belegte Extended-Ping-Aussage ergänzt | wie 108 |
| wissen (Load Sharing) | Ergänzung | universal = Default mit 32-Bit-ID (Boot zufällig, konfigurierbar), Unique-ID-Einschränkung bei gerader Pfadzahl (HW), include-ports gilt für Software-Switching, Per-Packet nicht auf ASR 1000 | https://www.cisco.com/c/en/us/support/docs/ip/express-forwarding-cef/116376-technote-cef-00.html ; https://www.cisco.com/en/US/docs/ios-xml/ios/ipswitch_cef/configuration/15-0sy/isw-cef-load-balancing.html |
| lektion Seite 8 (Tabelle) | „verhindert Polarisation“ zu absolut (Tech Note: Unique-ID wirkt bei gerader Pfadzahl auf HW nicht) | „mindert Polarisation“ | 116376 |

## Entfernt
keine

## Belege zu den vom Writer markierten Fragen
- 037, 053, 054 (Filtern am Eingangsport, MAC-Move, clear dynamic): Standard-Bridging-Verhalten, konsistent mit Cisco MATM-Doku; ok.
- 047, 048, 113 (aging-time 0 deaktiviert, per-VLAN-Aging, Bereich 0/10–1000000, Default 300): Catalyst-IOS-Command-Refs (4500/2960: „Enter 0 to disable aging“, optional `vlan`). Cat9k-Command-Reference online nicht vollständig abrufbar (Seite abgeschnitten) – Verhalten ist auf IOS-XE identisch, aber nur indirekt belegt.
- 049 (%SW_MATM-4-MACFLAP_NOTIF, Format/Ursachen): https://www.cisco.com/c/en/us/support/docs/switches/catalyst-9300-series-switches/223094-understand-mac-flapping-notifications.html und https://www.cisco.com/c/en/us/support/docs/ip/syslog/221140-troubleshoot-mac-address-flap-notificati.html (L2-Loop; inkonsistent gebündelte Links ≈ NIC-Team ohne EtherChannel).
- 051, 055, 056, 109 (Flooding-Regeln, static-Syntax, count, address): Standard-Syntax, ok.
- 057 (SDM erst nach Reload): Catalyst-SDM-Doku („cannot take effect until the next reload“); ok.
- 058 (show platform hardware fed switch active fwd-asic resource tcam utilization): https://www.cisco.com/c/en/us/support/docs/switches/catalyst-9300-series-switches/217714-understand-ipv4-hardware-resources-on-ca.html ; ok.
- 062 (TCAM Wert+Maske): ok.
- 068 (Fast-Switching-Skalierung): ok.
- 079–084, 112 (ECMP, per-destination Default, per-packet Reordering/VoIP, `ip load-sharing per-destination|per-packet` am Interface, `show ip cef exact-route <src> <dst>`, universal + ID gegen Polarisation): CEF Load-Balancing Guide (s. o.), Tech Note 116376, IP Switching Command Reference.
- 085, 116 (Encap-String Ziel-MAC/Quell-MAC/0x0800): ok.
- 086, 087, 088, 103 (glean, incomplete, null, punt): https://www.cisco.com/c/en/us/support/docs/ip/express-forwarding-cef/17812-cef-incomp.html (Null = verwerfen, Punt = nicht unterstütztes Feature an höhere Switching-Ebene, Glean = angeschlossenes Subnetz ohne L2-Info, incomplete = ARP nicht auflösbar).
- 089 (IPv6 Adjacency aus ND / show ipv6 neighbors): ok.
- 093 (`ip cef distributed`): IP Switching Command Reference, https://www.cisco.com/en/US/docs/ios/ipswitch/command/reference/isw_i1.html
- 104, 110 (Null0-Summary vs. Default, QoS classify/police): ok.

## SVGs
Alle 8 wohlgeformt (`[xml]` ok), `<title>` erstes Kindelement, Inhalt fachlich geprüft – keine Fehler gefunden, keine Änderung.

## Unsichere Punkte
- Cat9k-spezifische Belege für aging-time 0 / per-VLAN-Aging und `show mac address-table count` (per-VLAN-Ausgabe) nur über ältere Catalyst-IOS-Doku.
- slg-sw-091 (`IP route-cache flags are Fast, No CEF`): Lab-Ausgabe (IOL); auf aktuellen IOS-XE-Plattformen gibt es Fast Switching praktisch nicht mehr – Frage bezieht sich ausdrücklich auf die gezeigte Ausgabe, daher belassen.
