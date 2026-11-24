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

## Wissen & Bilder

Geprüft: `encor-1.4.10/wissen/09-eigrp.md` (jede Faktenaussage) und die 9 SVGs in `bilder/09-eigrp/`. Alle Metrik-Beispiele mit Python (`python -I`) nachgerechnet: 2816, 28160, 281600, 2169856 (10^7/1544 = 6476,68), 3072, 28416, 2170112, 512 (10G), 256 (40G/100G), Wide Gi 1310720 / 128 = 10240. Alle stimmen.

### Korrekturen Wissensdatei
| Stelle | Problem | Änderung | Quelle |
|---|---|---|---|
| Wide Metrics, Latency | Formel für Interfaces > 1 Gbit/s „10^7·65536/10/BW“ war um den Faktor 10 falsch (10G ergäbe 6553 statt 65536) | Delay (ps) = 10^13/BW (kbit/s): 1G 10 µs, 10G 1 µs, 500G 20 ns, also Latency = 10^7·65536/BW. Beispiel 10G = 131072 (RIB 1024) ergänzt | RFC 7868 (Konstanten EIGRP_BANDWIDTH 10^7, EIGRP_DELAY_PICO 10^6, EIGRP_WIDE_SCALE 65536, Kompatibilitätstabelle) https://www.rfc-editor.org/rfc/rfc7868.html |
| Traffic Sharing | Das Beispiel nannte die Pfade 20 und 50 (2,5 → 2:1), obwohl E-B-A im selben Kursbeispiel 30 hat (der Fehlerabschnitt nennt 30/20) | Auf 30/20 = 1,5 → abgerundet 1:1 korrigiert, 50/20 nur noch als Zusatzbeispiel | Cisco 13677 („round down to the nearest integer“) https://www.cisco.com/c/en/us/support/docs/ip/enhanced-interior-gateway-routing-protocol-eigrp/13677-19.html |
| Überblick | „Seit 2013 … RFC 7868“: der RFC stammt aus 2016 | 2013 offengelegt (Draft), RFC 7868 seit 2016 | RFC 7868 (May 2016) |
| Named Mode | Der Satz „Ein Name aus Ziffern ist nicht die AS-Nummer“ widersprach der Ergänzung direkt dahinter (eine Zahl nach router eigrp wird als AS geparst) | Umformuliert: Name ist lokal, AS steht in der address-family; nur ein Wort ergibt Named Mode | Cisco 200156 (Named Mode) |
| Fehlertabelle MTU-Tiebreaker | Beleglage präzisiert | RFC 7868: „Not used in metric calculation“; Labortest ipspace.net ohne MTU-Einfluss; keine Cisco-Doku | https://blog.ipspace.net/2010/06/eigrp-mtu-metric/ |
| Fehlertabelle variance | „Cisco dokumentiert kleiner als“ war zu pauschal | Cisco 13677 ist uneinheitlich (Einleitung „less than“, Beispiel „less than or equal to 40“); Regel „kleiner als“ beibehalten | Cisco 13677 |

Bestätigt (Auszug): Wide Metrics 64 Bit, Pikosekunden, bis ca. 4,2 Tbit/s, K6 Default 0 (Extended Attributes: Jitter, Energy), rib-scale Default 128, nur Named Mode (Cisco EIGRP Config Guide https://www.cisco.com/en/US/docs/ios-xml/ios/iproute_eigrp/configuration/xe-3sg/ire-cfg-eigrp.html); klassische Formel mit K5/(REL+K4) (RFC 7868); Hello 5 s/Hold 15 s, NBMA 60/180 s; Syntax `show eigrp address-family {ipv4 | ipv6} [vrf] [AS] neighbors`, AF ist Pflicht (https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_eigrp/command/ire-cr-book/ire-s1.html); CEF per-destination als Default (13677).

### Bilder
- Alle 9 SVGs sind wohlgeformt ([xml]) und als UTF-8 ohne BOM gespeichert. Ein Skript hat geprüft, ob Text über die viewBox hinausragt, ob sich Texte überlappen und ob Text Linien oder Rechteckkanten schneidet. Kein Text ragt hinaus, kein Text überlappt einen anderen. Die gemeldeten Text-Linien-Treffer sind Fehlalarme: In 07-variance treffen sie die Knotenbeschriftungen (die Linien liegen unter den gefüllten Kreisen), in 01-merkmale die Verbindungslinien (sie enden unter den gefüllten Kästen).
- `01-merkmale.svg`: „Seit 2013 informational RFC 7868“ → „2013 offengelegt, RFC 7868 (2016, informational)“.
- `09-modi.svg`: „Name ist lokal, auch eine Zahl ≠ AS“ war falsch, denn eine Zahl nach `router eigrp` ist Classic Mode. Korrigiert auf „Name lokal, AS in der address-family“. Außerdem war `address-family ipv4 unicast autonomous-system 100` auf zwei Zeilen umbrochen, was wie zwei Befehle aussah. Jetzt steht der Befehl in einer Zeile, dazu kommt `exit-af-interface` vor `topology base`.
- 02–08: inhaltlich korrekt (Werte in 05/06/07 nachgerechnet).

### Fragen
Kein Widerspruch zu den geprüften Fragen. Keine Frage liegt genau auf der variance-Grenze. slg-ei-040, 043, 044, 112 und 122 passen zur korrigierten Wide-Metric-Darstellung.