# Prüfprotokoll Kapitel 22-analysis (Using Network Analysis Tools)

Datum: 2026-11-24 · Checker
Geprüft: 150 Fragen (slg-an-001 … 150), Lektion (7 Seiten inkl. aller Tabellenzellen), Wissensdatei, 9 SVGs ([xml]-Prüfung + Inhalt).
Ergebnis: 149 Fragen, `pruefen.ps1 -Kapitel 22-analysis` → OK (single 98, luecke 10, zuordnung 12, multi 14, cli 15; Schwierigkeit 1:40 / 2:74 / 3:35).

## Korrekturen

| ID/Datei | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-an-106 | Option „delay down 15 up 60“ – laut Syntax `delay {up s [down s] \| [up s] down s}` steht up vor down | Option → „delay up 60 down 15“; Erklärung präzisiert (threshold beim Tracking nur für Track-Listen) | https://cisco.com/en/US/docs/ios-xml/ios/ipapp/command/D_through_H.html , https://www.cisco.com/en/US/docs/ios-xml/ios/ipapp/configuration/15-s/iap-eot.html |
| lektionen/22-analysis.json (IP-SLA-Seite) | „delay down/up“ | → „delay up … down …“ | wie oben |
| wissen/22-analysis.md | Tracking-Beispiel `delay down 10 up 30` | → `delay up 30 down 10` + Syntaxhinweis | wie oben |
| wissen/22-analysis.md | udp-jitter-Defaults: Klärung Kurs (10 Byte) vs. Cisco | Defaults 10 Pakete / 20 ms / 32 Byte mit Beleg; Hinweis, dass Fließtext einiger Cisco-Guides (10 Byte, 10 ms) der eigenen Default-Tabelle widerspricht; Fehlerliste Punkt 5 ergänzt | https://www.cisco.com/en/US/docs/ios-xml/ios/ipsla/configuration/15-2s/sla_udp_jitter.html (Table 1); ME3400-Guide-Beispielausgabe „Packet Interval/Number of packets: 20/10“ |
| wissen/22-analysis.md | Lab-Folgerung „* * * ab Hop 1 → R4 ohne Route“ als Fakt formuliert, widerspricht eigener Fehlerliste Punkt 7 | als Kursaussage/unsicher markiert | – |
| wissen/22-analysis.md | ERSPAN-Beispiel MTU 1464 | Hinweis: Wert plattformabhängig (Cat9300-Guide zeigt 1500, mtu-Default 9000) | Cat9300 17.9 ERSPAN Guide |
| bilder/06-traceroute.svg | „* * * ab Hop 1 → schon 1. Router ohne Route“ (unsichere Regel) | ersetzt durch „2 Hops pendeln bis TTL 30 → Routing-Schleife“ | – |
| bilder/07-ip-sla.svg | `delay down 10 up 30` | → `delay up 30 down 10` | wie slg-an-106 |

## Entfernt

| ID | Grund |
|---|---|
| slg-an-139 | „MTU: 1464“ in show monitor session – Ursache (GRE/ERSPAN-Overhead) nicht sauber belegt; Wert plattformabhängig (Cat9k 1500/9000), und das ERSPAN-`mtu` steuert laut IOS-XE-Guides die Truncation, wodurch Distraktor „truncates … 1464“ nicht eindeutig falsch ist. |

## Gezielt belegte Writer-Markierungen (ohne Änderung)

- 005–011 Methoden (top-down, bottom-up, divide & conquer, follow-the-path, compare, swap): Standard Cisco-Press-TSHOOT-Methodik, Fragen eindeutig.
- 025 „Largest“ = größter zusammenhängender freier Block: korrekt.
- 026/037/038 Duplex-Mismatch: Half-Seite late collisions, Full-Seite CRC/runts (Cisco NIC-Compatibility-Doc 10561); Late collision = nach 512 Bit-Zeiten = 64 Byte (Doc 12768) → 030 korrekt.
- 027 giants, 031 input errors = runts, giants, no buffer, CRC, frame, overrun, ignored (show interfaces-Referenz) korrekt; 032 korrekt.
- 048 Regex-Punkt = beliebiges Zeichen; „10.1.1.1“ matcht „10.1.101.1“ – nachgerechnet.
- 052 ARP beim ersten Echo (Doc 12778: „encapsulation failed“ solange kein ARP-Eintrag); 064 Router beantwortet Pings best-effort/niedrige Priorität (Doc 12778).
- 069/070/075 traceroute-Zeichen A, H, N, U, *, Q (Doc 12778) korrekt; 066/072 UDP ab 33434, 3 Probes/TTL korrekt; 071/073/074 korrekt.
- 055 Ping-Defaults 5 / 100 Byte / 2 s / 0xABCD / DF aus (Doc 12778) korrekt; 060 Record max. 9 Hops (40 Byte Options) korrekt.
- 081 mehrere Debug-Conditions = ODER (12.2 Debug Command Reference „at least one of the conditions“).
- 092 ohne start-time → pending, Default life 3600 s (IP SLA Command Ref ip sla schedule) → 099, 114 korrekt.
- 095–097 udp-jitter 10 Pakete / 20 ms Default (s. o.).
- 098, 108, 112 One-Way braucht NTP, udp-jitter braucht Responder (UDP 1967) – korrekt.
- 101/105 reachability = up bei OK + OverThreshold, state = nur OK (Enhanced Object Tracking Guide, Table „State vs Reachability“).
- 102/103/104/109/113 korrekt (icmp-echo … source-interface gültige Syntax).
- 118–123, 127, 128 SPAN/RSPAN: Cat9300 17.9 SPAN Guide – Ports/VLANs nicht mischbar, Default both, encapsulation replicate inkl. BPDU/L2-Protokolle, ingress = Injektion vom Sniffer, filter vlan für Trunk-Quellen, Ziel ≠ Quelle, RSPAN-VLAN auf allen Switches, Überbuchung bei both. https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-9/configuration_guide/nmgmt/b_179_nmgmt_9300_cg/configuring_span_and_rspan.html
- 135–137, 140, 141 ERSPAN: ID + Ziel-IP gleich, Ziel-IP lokal, origin = GRE-Quell-IP, keine Kopie von lokal erzeugtem ERSPAN-GRE, Ports oder VLANs; Sessions standardmäßig shut (no shutdown nötig). https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-9/configuration_guide/nmgmt/b_179_nmgmt_9300_cg/configuring_erspan.html
- 142–146, 150 EPC: DRAM-Puffer, privileged EXEC, start nötig, circular überschreibt Älteste, Filter/Limits.

## Unsichere Punkte (belassen)

- slg-an-020 (Interrupt > 10 %) und 019 sind Kurs-Faustwerte, als „course guideline“ formuliert.
- slg-an-034 „show platform“ für Reload-Analyse ist Kursempfehlung (in der Praxis eher show version/crashinfo/show tech); unter den Optionen eindeutig die beste.
- udp-jitter-Defaults sind in Cisco-Dokus inkonsistent (Fließtext 10 Byte/10 ms vs. Tabelle 32 Byte/20 ms); Fragen nutzen nur 10 Pakete/20 ms, die von Tabelle, Command Reference und Beispielausgaben gestützt werden.
