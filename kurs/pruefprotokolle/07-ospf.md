# Prüfprotokoll Kapitel 07-ospf

- Geprüft: 132 Fragen (slg-os-001 … 132), Lektion (8 Seiten, alle Tabellenzellen), Notizen gegengelesen
- Korrigiert: 11 Fragen + 1 Lektionsseite. Entfernt: 0. Verbleibend: 132
- pruefen.ps1 -Kapitel 07-ospf (ohne -Mischen): OK. Verteilung: single 80, multi 16, cli 13, zuordnung 13, luecke 10; Schwierigkeit 31/70/31

## Korrekturen

| ID | Problem | Änderung | Quelle |
|---|---|---|---|
| 002 | In der Erklärung stand, jede LSA werde „explizit per LSAck“ bestätigt. RFC 2328 erlaubt auch implizite Bestätigung, und LSAcks werden gebündelt | Erklärung präzisiert | RFC 2328 Abschn. 13.5 – https://www.rfc-editor.org/rfc/rfc2328.txt |
| 013 | Die Aussage „retries automatically“ ist so nicht belegt. Cisco nennt %OSPF-4-NORTRID und als Abhilfe: router-id setzen oder ein Interface mit IP hochbringen | Antwortoption und Erklärung umformuliert | https://community.cisco.com/t5/networking-knowledge-base/unable-to-allocate-ospf-router-id/ta-p/3128225 |
| 018 | 6 Optionen, das Format für multi erlaubt 4–5 | Distraktor „Interface priority“ entfernt, Index angepasst (0,2,4) | Format laut Anleitung |
| 025 | Der Logtext lautet bei Cisco „mismatch area ID“, nicht „mismatched“ | Wortlaut angepasst | https://www.cisco.com/c/en/us/support/docs/ip/open-shortest-path-first-ospf/6154-19.html |
| 026 | Der Debugtext lautet bei Cisco „Mismatch Authentication type …“ | Wortlaut angepasst | Cisco Community, OSPF mismatched authentication type – https://community.cisco.com/t5/routing/ospf-mismatched-authentication-type/td-p/549846 |
| 046 | Der exakte Debugtext „Backup seen event before WAIT timer“ ließ sich im Web nicht belegen | Frage auf das RFC-Ereignis BackupSeen umformuliert (hängt nicht mehr vom Wortlaut ab), Erklärung mit RFC-Definition | RFC 2328 Abschn. 9.1/9.2 (Wait Timer = RouterDeadInterval, BackupSeen) |
| 073 | Widersprüchlich: R6 hätte „nur Interfaces in Area 2“ und gleichzeitig einen Link in Area 1 | Formulierung präzisiert (übrige Interfaces in Area 2, keins in Area 0) | – |
| 096 | „Alte LSAs bleiben bis zum Ausaltern“ ist für den Eintrag in Routing Information Sources nicht sauber belegbar | Option und Erklärung abgeschwächt (der veraltete Eintrag bleibt eine Zeit lang) | Labbeobachtung aus dem Kurs |
| 109 | „Nothing changes“ ist nicht exakt: Die Summary-Kosten sind das Maximum der Komponenten (RFC 2328), die Metrik kann sich also beim Flappen ändern | Antwortoption umformuliert, Erklärung ergänzt | RFC 2328 Abschn. 3.5 |
| 121 | 6 Optionen bei multi | Distraktor „Interface OSPF cost“ entfernt, Index angepasst (0,3,4) | RFC 2328 A.3.2 |
| 127 | Wortlaut der Meldungen nicht wie bei Cisco | „Mismatch Authentication type“, „Received invalid packet: mismatch area ID“ | wie 025/026 |
| Lektion S. 1 | „bestätigt jede LSA mit LSAck“ war zu absolut | präzisiert (normalerweise LSAck, Retransmit nach 5 s) | RFC 2328 13.5, App. C |

## Belege für die markierten Punkte (unverändert korrekt)

- 006 LSAck = Liste von LSA-Headern: RFC 2328 A.3.6 „The body of both packets is simply a list of LSA headers“. 064: LSA-Header 20 Byte (A.4.1)
- 115 DBD-Flags I/M/MS: RFC 2328 A.3.3. 0x7 = I+M+MS ist plausibel und entspricht der Cisco-Debugausgabe
- 021 „Mismatched hello parameters from …“ / „Dead R x C y, Hello R x C y“: Cisco Tech Note 12151 (https://www.cisco.com/c/en/us/support/docs/ip/open-shortest-path-first-ospf/12151-trouble-main.html). R = received, C = configured
- 019/020 „Nbr … has larger interface MTU“: Der Router mit der kleineren MTU bleibt in EXSTART, der andere in EXCHANGE. ip ospf mtu-ignore: Tech Note 13684 (https://www.cisco.com/c/en/us/support/docs/ip/open-shortest-path-first-ospf/13684-12.html) und die OSPF-Command-Reference (ospf-i1)
- 024 Maske wird auf p2p/Virtual Links ignoriert: RFC 2328 10.5. Timer-Mismatch führt zum Verwerfen, das E-Bit muss passen (relevant für 022, 052, 103)
- 030 ATTEMPT nur bei NBMA: RFC 2328 10.1
- 041/042 Priority 0–255, Default 1, 0 = nicht wählbar. 097 Retransmit-Intervall Default 5 s. 049/052 Hello 10 (Ethernet) / 30 (nonbroadcast). 023/090 Dead = 4 × Hello: Cisco IOS OSPF Command Reference (https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_ospf/command/iro-cr-book/ospf-i1.html)
- 081–083: Referenzbandbreite in Mbit/s, 1–4294967, Default 100. 100000/56 = 1785 (abgeschnitten): Command Reference ospf-a1 (https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_ospf/command/iro-cr-book/ospf-a1.html)
- 092: ip ospf area hat Vorrang vor network area („will supersede the effects of the network area command“), laut Cisco OSPFv2 Interface Mode Config Guide (iro-imode-ospfv2)
- 099–107, 116/117: Stub/Totally Stubby, der ABR erzeugt den Default automatisch. NSSA erzeugt den Default nicht automatisch (area X nssa default-information-originate nötig), NSSA no-summary schon. default-information originate ohne always braucht eine Default-Route in der RIB: Cisco Tech Note 13692 (https://www.cisco.com/c/en/us/support/docs/ip/open-shortest-path-first-ospf/13692-21.html), area stub muss auf allen Routern der Area konfiguriert sein (ospf-a1)
- 059/060: Übersetzte Typ-5-LSAs haben den Translator-ABR als Advertising Router: RFC 3101 Abschn. 3.2
- 063: Intra-Area-Prefix-LSA 0x2009, Link-LSA 0x0008 link-lokal, Router-/Network-LSAs ohne Adressen: RFC 5340 Abschn. 2.8, 4.4.3
- 110: distribute-list in filtert nur die RIB, die LSA bleibt in der LSDB: Cisco Community KB „Can I use distribute-list in/out with OSPF“
- 051/124: Loopback wird als /32 annonciert, mit point-to-point die echte Maske: Cisco OSPF FAQ (9237-9)
- 014: Ein router-id-Wert, der mit einem anderen lokalen Prozess kollidiert, schlägt fehl (ipspace.net, OSPF Router ID Selection, zitiert Cisco-Doku)
- 044: n = 5: DR 4 + BDR 3 = 7 Adjazenzen, Full Mesh n(n-1)/2 = 10 (Rechnung)
- 131: show ip ospf border-routers

## Unsichere Punkte / Hinweise

- RFC 3101 2.4 verlangt, dass NSSA-ABRs immer einen Default erzeugen. Cisco IOS weicht davon ab (kein Default ohne default-information-originate). Fragen und Lektion folgen Cisco, das ist für ENCOR maßgeblich.
- 113: Das Spaltenformat „Nbrs F/C“ von „show ip ospf interface brief“ ist bei Cisco für OSPFv3 dokumentiert, für IPv4 nur aus Erfahrung bzw. dem Kurs belegt.
- 095: Die Ausgabe von „show ip ospf route“ (Intra-area Router Path List) stammt aus dem Kurs-Lab, eine Cisco-Doku dazu wurde nicht gefunden. Die Antwort hängt nicht vom genauen Wortlaut ab.
- 048: Dass ein bisheriger DR/BDR mit Priority 0 seine Rolle sofort verliert, ist durch das Kurs-Lab und RFC 2328 9.4 belegt (Priority 0 ist nicht wählbar).


## Nachtrag (Checker 08-ospf-opt)
- slg-os-109: Erklärung zur Summary-Metrik präzisiert: Cisco IOS Default 'compatible rfc1583' = niedrigste Komponentenkosten (RFC 1583 Abschn. 3.5), RFC 2328 bzw. 'no compatible rfc1583' = höchste. Quelle: Cisco OSPF Command Reference 'compatible rfc1583', RFC 1583/2328 Abschn. 3.5.
