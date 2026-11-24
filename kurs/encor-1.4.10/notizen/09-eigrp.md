# Notizen Kapitel "Explaining EIGRP" (Kursseiten 86–95)

## Features (S. 86)
- Cisco-Entwicklung, seit 2013 weitgehend offen (informational RFC 7868); Stub-Teile bleiben proprietär.
- Advanced Distance Vector: Wissen über das Netz kommt von direkten Nachbarn; Hello-Protokoll und partielle Updates ähneln Link-State.
- DUAL: schnelle Konvergenz, loop-free, Backup-Routen (Feasible Successor) vorgehalten; ohne Backup -> Query an Nachbarn.
- Equal- und Unequal-Cost Load Balancing.
- Classless (Maske pro Ziel) -> VLSM, diskontinuierliche Netze.
- Multi-AF (früher IPX/AppleTalk, heute IPv4/IPv6; auch SAF/Dial-Plan-Verteilung).
- Keine periodischen Updates; "partial" (nur Änderungen) und "bounded" (nur an betroffene Router). Multicast 224.0.0.10 / Unicast, kein Broadcast.

## RTP und Pakete (S. 87)
- Direkt über IP, Protokollnummer 88. RTP = garantierte, geordnete Zustellung, Multicast und Unicast gemischt.
- Drei Tabellen: Neighbor (Primäradresse + Interface), Topology (alle Ziele, je Nachbar die advertised metric + eigene Metrik), Routing.
- Successor = beste Route (RIB + an Nachbarn annonciert); Feasible Successor = loop-freie Backup-Route, nicht in RIB.
- Ablauf: Hello -> Hello zurück; Updates dürfen parallel laufen, ACK aber erst nach abgeschlossener Nachbarschaft; Update -> ACK in beide Richtungen.
- Hello: Multicast, ACK-Nummer 0, unzuverlässig.
- Update: Multicast bei neuer Route/Konvergenz, Unicast bei Synchronisation mit neuem Nachbarn; zuverlässig.
- Query: zuverlässig, Multicast; wenn kein FS vorhanden (Route active).
- Request: Unicast oder Multicast, unzuverlässig (Route-Server-Anwendungen).
- Reply: zuverlässig, Unicast an den Query-Absender.
- ACK: Hello ohne Daten mit ACK-Nummer ≠ 0, Unicast; bestätigt Update/Query/Reply. Hello und ACK werden nicht bestätigt.
- Passive = keine Neuberechnung; Active = Router sucht neuen Successor.

## Nachbarschaft (S. 88)
- Müssen passen: AS-Nummer, K-Werte, gemeinsames Subnetz (nur Primäradressen sind Quelle -> keine Nachbarschaft über Secondary), Authentifizierung.
- Hello-Timer dürfen abweichen (anders als OSPF). OSPF-Prozess-ID nur lokal.
- passive-interface: keine Hellos -> keine Nachbarschaft, eingehende EIGRP-Pakete werden ebenfalls nicht verarbeitet.
- AS-Empfehlung: BGP-AS oder 1; mehrere AS z. B. bei DMVPN.
- Router-ID weniger wichtig als bei OSPF, sichtbar mit show ip protocols.

## Metrik (S. 89)
- K1 Bandbreite (kleinste auf dem Pfad, kbit/s), K2 Load, K3 Delay (Summe, in 10 µs), K4/K5 Reliability-bezogen (0–255, 255 = 100 %).
- Default K1 = K3 = 1, K2 = K4 = K5 = 0 -> Metrik = 256 * (10^7/BWmin + Summe Delay/10). K5 = 0 -> Reliability-Term entfällt (= 1).
- Faktor 256: IGRP-Metrik (24 Bit) auf 32 Bit erweitert.
- K-Werte stehen im Hello -> Mismatch verhindert/zerstört Nachbarschaft, auch wenn Wert ungenutzt.
- show interfaces zeigt BW, DLY, reliability, txload/rxload.
- Pfadmanipulation: besser delay ändern (kumulativ), Bandbreite wirkt nur wenn Engpass und beeinflusst QoS/Monitoring.
- Wide Metrics: Problem klassisch bei > 1G (Delay min. 10 µs); 64-Bit-Metrik, Zeit in Pikosekunden, Konstante 65536, K6 neu (Zukunft); metric rib-scale bringt Wert in 32-Bit-RIB, Änderung ersetzt alle EIGRP-RIB-Routen.
- MTU und Hop Count werden übertragen, aber nicht in der Metrik verwendet.

## Pfadwahl (S. 90)
- Getrennte Neighbor-/Topology-Tabellen je Protokoll (Dual Stack).
- AD/RD = Metrik des Nachbarn; FD = RD + Kosten zum Nachbarn = eigene End-to-End-Metrik.
- Kleinste FD -> Successor -> RIB (wenn keine bessere administrative Distanz).
- Feasibility Condition: RD < FD des aktuellen Successors.
- Successor weg: FS vorhanden -> sofort, ohne Neuberechnung; sonst active + DUAL-Berechnung (Queries).
- Advertised Distance nicht mit Administrative Distance verwechseln.

## Load Balancing (S. 91)
- maximum-paths (Default 4, Bereich plattformabhängig, z. B. 1–16), 1 = aus.
- Unequal-Cost: variance (Default 1, 1–128); zulässig, wenn Metrik < variance * beste FD UND FS.
- traffic-share balanced (Default): Verteilung proportional zu Metriken; traffic-share min across-interfaces: nur bester Pfad nutzt Traffic, FS trotzdem in RIB (schnellere Konvergenz).

## IPv6 (S. 92)
- Getrennt konfiguriert/verwaltet; kein network-Befehl, Aktivierung am Interface (ipv6 eigrp <AS>).
- Nachbarschaft und Next Hop über Link-Local; Multicast FF02::A.
- Benötigt ipv6 unicast-routing, Router-ID (32 Bit, dotted decimal).
- Kurs: Prozess standardmäßig shutdown (no shutdown nötig).

## Vergleich OSPF (S. 93)
- EIGRP: einfach, flexibles Design, effizient, Equal+Unequal LB; OSPF: komplexer, starr (Areas), für sehr große Netze, Multivendor.
- Konvergenz: EIGRP gut auch ohne Design, in großen Netzen wird Design wichtig.

## Konfiguration (S. 94)
- Classic: router eigrp <AS 1–65535>, network <Netz> [wildcard]; Maske wird zur Wildcard korrigiert. Interface-Parameter (Hello, Split Horizon, Auth, Summary) im Interface-Modus.
- Named: router eigrp <Name> -> address-family ipv4|ipv6 unicast|vrf ... autonomous-system <AS> -> network. Zahl als Name ≠ AS.
- Vorteile Named: alles an einer Stelle, mehrere AFs/VRFs, klare Scopes, neue Features.
- Verifikation: show ip eigrp interfaces|neighbors|topology [all-links]; named: show eigrp address-family ... .

## Kursfehler / Auffälligkeiten
- Tabelle S. 89: K5 = "MTU" – falsch, K5 ist ein Reliability-Koeffizient; der Kurs sagt selbst später, MTU werde nie in der Metrik verwendet.
- S. 89: "delay microseconds" – der Interface-Befehl delay arbeitet in Zehn-Mikrosekunden-Einheiten.
- S. 92: Router-ID für IPv6 "immer manuell" – nötig nur, wenn keine IPv4-Adresse auf dem Router existiert.
- S. 93: Tabelle "Classic für IPv4, Named für IPv6" – irreführend, beide Modi können IPv6.
- S. 91: "maximum-paths muss auf beiden Seiten gleich sein" – keine Anforderung, ist eine lokale Entscheidung.
- S. 91: Traffic-Share-Rechnung 30/20 = "3/2 = 1" (abgerundet) und widersprüchlich "per conversation" vs. "one packet".
