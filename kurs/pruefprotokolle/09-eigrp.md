# Kapitelprüfung 09-eigrp

Geprüft: 122 Fragen (slg-ei-001 bis 122), alle einzeln, und die Lektion (8 Seiten, jede Tabellenzelle). Entfernt: keine. Verbleibend: 122.
pruefen.ps1 -Kapitel 09-eigrp (ohne -Mischen): OK.

## Metriken nachgerechnet (alle stimmen)
- Gi direkt 2816, FE direkt 28160, 10M direkt 281600, T1 direkt 2169856 (10^7/1544 = 6476 abgeschnitten).
- Gi+Gi-LAN 3072, FE+Gi-LAN 28416, T1+Gi-LAN 2170112, 3x FE + Gi-LAN 33536, 10M+Gi-LAN 281856 (Q111).
- Q036: delay 100 auf Gi0/0 ergibt (10 + 101) x 256 = 28416, gleich wie über R3, also ECMP. Stimmt.
- Q037: bandwidth 500000 > FE-Engpass, Metrik bleibt 28416. Stimmt.
- Q122: Wide Metric für Gi direkt 655360 + 655360 = 1310720, / rib-scale 128 = 10240. Stimmt.
- Variance/FC: Q049/050 (FS = A, C; nach Ausfall C), Q064 (variance 10), Q065 (nur X), Q066 (X+Y), Q067/068 (A+B, C nur in all-links), Q117 (R2+R3). Alle stimmen.

## Korrekturen
| ID | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-ei-022 | Die richtige Option war auffällig lang | Gekürzt auf „No adjacency forms, because the K values do not match“ | Stil |
| slg-ei-018 | Die richtige Option war auffällig lang. Laut Quellen können je nach Version auch interne Routen verworfen werden. | Option gekürzt und allgemeiner formuliert, Erklärung ergänzt | https://www.cisco.com/c/en/us/support/docs/ip/enhanced-interior-gateway-routing-protocol-eigrp/18685-eigrp-dup-id.html ; https://networklessons.com/eigrp/eigrp-router-id |
| slg-ei-055 | Die richtige Option war auffällig lang | Gekürzt | Stil |
| slg-ei-063 | Q/R waren als „pending“ beschrieben. Cisco beschreibt sie als „query/reply packet was sent to this destination“. | Paare korrigiert, „r“ in der Erklärung ergänzt | https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_eigrp/command/ire-cr-book/ire-s1.html (Field-Tabelle show eigrp address-family topology) |
| slg-ei-069 | Die richtige Option war am längsten | Gekürzt (Aussage bleibt korrekt) | https://www.cisco.com/c/en/us/support/docs/ip/enhanced-interior-gateway-routing-protocol-eigrp/13677-19.html |
| slg-ei-085 | Szenario „router eigrp 100“ + address-family AS 200 ist nicht belegbar. IOS parst eine Zahl nach „router eigrp“ als AS (Classic Mode); nur WORD ergibt den Named Mode. | Szenario auf „router eigrp CORP“ / AS 200 umgestellt, Optionen und Erklärung neu (der Name ist lokal, die AS muss passen, Named und Classic sind kompatibel) | https://www.cisco.com/c/en/us/support/docs/ip/enhanced-interior-gateway-routing-protocol-eigrp/200156-Configure-EIGRP-Named-Mode.html |
| slg-ei-098 | Die richtige Option war deutlich länger | Gekürzt | Stil; Q-Cnt-Definition: https://www.cisco.com/E-Learning/bulk/public/tac/cim/cib/using_cisco_ios_software/cmdrefs/show_ip_eigrp_neighbors.htm |
| slg-ei-103 | Die richtige Option war deutlich länger | Gekürzt | Stil |
| slg-ei-104 | Die richtige Option war deutlich länger | Gekürzt, Inhalt gleich (OSPF-LSA-Refresh 30 min) | Stil |
| slg-ei-106 | Erklärung „eindeutig, aber nie gleich“ war unklar | Umformuliert | – |
| slg-ei-112 | „Ab 10 Gbit/s“ war falsch: bei 10G ist der Term noch 1 | „Oberhalb von 10 Gbit/s“ | Rechnung |
| Lektion S.4 | Gleicher Fehler „Ab 10 Gbit/s ... wird 0“ | „Oberhalb von 10 Gbit/s“ | Rechnung |
| Lektion S.1 | „ohne Neuberechnung“ war ungenau, da DUAL lokal rechnet | „ohne Rückfrage bei den Nachbarn (mit FS)“ | – |

## Belegt (bestätigt)
- 009 RTP: Unicast-Retransmit an den Nachbarn ohne ACK, Reset nach dem Retry-Limit (RFC 7868).
- 014/015/023–027: Hello/Hold 5/15 bzw. 60/180 (Multipoint ≤ T1). Die Hold Time steht im Hello und passt sich nicht automatisch an. Syntax: ip hello-interval eigrp <AS> <s> / ip hold-time eigrp <AS> <s>. https://www.cisco.com/c/en/us/support/docs/ip/enhanced-interior-gateway-routing-protocol-eigrp/16406-eigrp-toc.html ; Cisco-Kurs- und Networklessons-Seiten
- 016: Keine Peers über Secondary-Adressen, Pakete kommen von der Primäradresse (16406-eigrp-toc).
- 020: Router-ID = höchste Loopback-Adresse, sonst höchste Interface-Adresse (18685-eigrp-dup-id).
- 040: Max. Hops Default 100. Command Reference: 1–255; das alte Whitepaper nennt noch 220. Die Frage nennt nur den Default.
- 046/122: Ändert man rib-scale, werden alle EIGRP-RIB-Routen gelöscht und neu eingetragen. Default 128, K6 und Pikosekunden. https://www.cisco.com/en/US/docs/ios-xml/ios/iproute_eigrp/configuration/xe-3sg/ire-cfg-eigrp.html
- 058/059/060: Ohne Route antwortet der Nachbar mit unreachable. Active Timer 3 min, SIA-Query nach der Hälfte (90 s), mehrere Community- und Cisco-Quellen.
- 074/075/087/089: topology base (variance, maximum-paths, redistribute, distance), af-interface (hello, hold, auth, passive), AF (network, router-id). Quelle: 200156-Configure-EIGRP-Named-Mode.
- 081: Für EIGRPv6 müssen Nachbarn kein gemeinsames globales Präfix haben (Cisco IPv6-Routing-Präsentation).
- 083: Named-Mode-IPv6-AF: alle IPv6-Interfaces nehmen sofort teil, Ausnahme per shutdown unter af-interface (Cisco Named-Mode-Material und Community).
- 093: Eine Subnetzmaske im network-Befehl wird in eine Wildcard umgewandelt (Cisco-NetAcad-Seite).
- 099: Feldbedeutungen Hold/SRTT/RTO/Q Cnt (Cisco-Cmdref show ip eigrp neighbors).
- 109: auto-summary ist seit 15.0(1)M / IOS-XE 2.5 per Default aus (Command Reference, zitiert im Cisco-Community-Thread 3900-router).
- 069/073: traffic-share min [across-interfaces] installiert alle Pfade, Traffic läuft nur über den Pfad mit der minimalen Metrik (13677-19).

## Unsichere Punkte
- 040: Das Maximum von 255 wird nur in der Erklärung nicht genannt, also unkritisch. Das alte Whitepaper (220) widerspricht der Command Reference (255).
- 076/082: Auf älterem IOS musste der ipv6-router-eigrp-Prozess zusätzlich mit „no shutdown“ aktiviert werden. Das ist in den Optionen nicht enthalten, die Antworten bleiben eindeutig.
- 070: „maximum-paths 1“ als Abschaltung habe ich aus Standardwissen und Kursnotizen übernommen und nicht eigens auf cisco.com nachgeschlagen. Der Distraktor 0 ist im aktuellen Wertebereich nicht zulässig.
