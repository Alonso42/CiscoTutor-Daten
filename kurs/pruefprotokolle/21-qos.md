# Kapitelprüfung 21-qos

Geprüft: 130 Fragen (slg-qs-001 … 130), Lektion `lektionen/21-qos.json` (6 Seiten inkl. aller Tabellenzellen), Wissensdatei `wissen/21-qos.md`, 9 SVGs in `bilder/21-qos/`.
Ergebnis `pruefen.ps1 -Kapitel 21-qos` (ohne -Mischen): OK – 130 Fragen (single 85, multi 14, luecke 8, zuordnung 11, cli 12; Schwierigkeit 31/67/32).

## Nachgerechnet (alle korrekt)
- AF-Formel 8x+2y: AF23=22, AF32=28=011100, AF33=30, AF13=14, AF43=38, AF41=34 → IPP 4.
- ToS = DSCP×4: 0x68=104→26 AF31; 0x28=40→10 AF11; 0x60=96→24 CS3; 0xB8=EF; 0x88=AF41; 0xC0=CS6; 0x48=AF21; Wireshark-DSCP 0x2e=46 EF; 101110=46.
- Class Selector 8/24/48; EF 46.
- Token Bucket: Tc = 8000/64000 = 125 ms; Bc = 10 Mbps × 10 ms = 100 000 bit (=12 500 Byte); CIR 8 Mbps × 10 ms = 80 000 bit.
- trTCM CIR 10/PIR 15, 12 Mbps → exceed.
- bandwidth remaining percent 50 nach priority percent 30 auf 100 Mbps → 35 Mbps.
- Serialization 1500 Byte @ 1 Mbps = 12 ms.
- WRED MPD 10 → 10 % an der Max-Schwelle.

## Gezielt belegt (Writer-Markierungen)
- 014/084 Conditional Trust bzw. Cat9k-Default-Trust: Catalyst 9000 vertraut DSCP standardmäßig ("for all incoming packets DSCP is trusted by default"); Shaping egress-only. https://www.cisco.com/c/en/us/products/collateral/switches/catalyst-9000/white-paper-c11-742388.html ; Cisco Live BRKENS-2096 (all ports trust L2/L3 by default) https://www.ciscolive.com/c/dam/r/ciscolive/emea/docs/2023/pdf/BRKENS-2096.pdf ; Conditional Trust via CDP: https://www.cisco.com/c/en/us/support/docs/switches/catalyst-9200-series-switches/222225-configure-autoqos-on-catalyst-9000-switc.html
- 052/092/106 LLQ: implizite Policer der Priority-Klasse nur bei Stau, Überschuss ohne Stau erlaubt: https://www.cisco.com/c/en/us/support/docs/quality-of-service-qos/qos-packet-marking/10100-priorityvsbw.html
- 043/069/091/125 Queuing (priority/bandwidth/shape) nur in Output-Policies, Policing/Marking beidseitig; service-policy braucht input|output: Cisco IOS XE "Applying QoS Features Using the MQC" https://cisco.com/go/qosmqc ; erste passende Klasse gewinnt (ebd.).
- 070 eine Policy pro Interface und Richtung: MQC-Grundregel (u. a. Cisco-Plattformdoku "only one policy map per interface per direction"); Kombination per hierarchischer Policy.
- 056–058/128 WRED: MPD-Default 10, Drop-Wahrscheinlichkeit 1/MPD an Max-Threshold, darüber alle, `random-detect dscp-based`: https://www3-realm.cisco.com/en/US/docs/ios/12_2/qos/configuration/guide/qcfwred.html
- 021–030/082/098/101/112/118 DSCP/ECN: RFC 2474, 2597 (AF-Tabelle), 3246 (EF 46), 3168 (ECN = untere 2 Bit), 4594.
- 044–046/104/114 Token Bucket/srTCM/trTCM: RFC 2697, 2698 (CIR/PIR, conform/exceed/violate = green/yellow/red).
- 076/077/095/109 IntServ (RFC 1633, RSVP, State pro Flow) / DiffServ (RFC 2475).
- 078–080/116 Verzögungsarten, G.114 (≤150 ms one-way).
- CLI 119–124, 126–129: Syntax `class-map match-any`, `match dscp ef`, `priority percent 20`, `bandwidth remaining percent 40`, `police cir 2000000 conform-action transmit exceed-action drop`, `shape average 50000000` (bps), `set dscp af41`, `show policy-map interface <if>`, `random-detect dscp-based`, `match protocol http` – gültige IOS-XE-MQC-Syntax.

## Korrekturen
- Fragen: keine (alle Antworten, Distraktoren, Erklärungen fachlich korrekt und eindeutig).
- `bilder/21-qos/03-tos-byte.svg`: Beschriftung "Drop-Precedence-Bits" spannte über Bit 4–2; korrigiert auf "AF: Drop-Precedence (Bit 4–3)" + Bit 2 "AF: 0"; "IPP = DSCP ÷ 8 (abgerundet)" ergänzt. Wohlgeformt geprüft.
- `wissen/21-qos.md`: Beispielausgabe `show policy-map interface` war inkonsistent (offered rate 1,18 Mbps < Priority-Rate 2 Mbps, trotzdem Drop-Rate); auf 2,18 Mbps offered / 180 kbps drop geändert und Hinweis ergänzt, dass 20 % = 2000 kbps einen 10-Mbps-Parent-Shaper voraussetzt.

## Entfernt
- keine

## Unsichere Punkte
- Voice-Bandbreite 30–128 kbps, Video-Verlust 0,1–1 % sind Kurswerte (ältere/neuere SRND nennen leicht andere Bereiche); Fragen 004/102 sind ausdrücklich als "course lists" formuliert.
- 069/091 gelten für Router (IOS XE); einige Switch-Plattformen haben abweichende Ingress-Queuing-Fähigkeiten – Fragen nennen "router".
