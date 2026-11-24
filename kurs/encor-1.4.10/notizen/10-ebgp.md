# Notizen Kapitel "Exploring EBGP" (Kursseiten 99–105)

## 99 Interdomain Routing with BGP
- AS = Netze/Router unter einer gemeinsamen technischen Verwaltung (gleiche Routing-Policy); rechtliches Eigentum egal.
- AS-Nummern: urspr. 16 Bit; später 32 Bit (4-Byte-ASN) wegen Erschöpfung. IANA vergibt öffentliche ASNs.
  - Kurs: public 1–64511, private 64512–65535. **Korrektur (eigenes Wissen, RFC 6996/7300/5398):** privat 64512–65534; 65535 reserviert; 64496–64511 Dokumentation; privat 4-Byte 4200000000–4294967294.
- IGP (RIP, OSPF, EIGRP) innerhalb eines AS, EGP (BGP) zwischen AS.
- BGP über TCP Port 179 → keine eigene Retransmission/Fehlerkorrektur nötig.
- Eigenschaften: Reliability (nach initialem Volltausch nur inkrementelle/triggered Updates, Keepalives), Scalability (>600k Internetrouten, TCP-Sliding-Window statt One-for-one-Window wie OSPF/EIGRP), Stability (gebündelte Updates, langsamere Konvergenz, Dämpfung flappender Routen).
  - Kurs nennt TCP-Window "65,576 bytes" – Tippfehler, max. Window ohne Scaling 65.535 Byte.
- Path Vector: AS-Pfad (Liste der AS bis zum Ziel) + Netze am Ende + Attribute (Next Hop, Origin ...).
- Loop-Schutz: Update mit eigener ASN im AS_PATH wird verworfen.
- Hop-by-hop-Paradigma: Ein AS kann nur beeinflussen, wohin es selbst Traffic schickt, nicht wie das Nachbar-AS weiterroutet. Ein AS gibt nur seinen eigenen Best Path weiter (keine Alternativen).
- Beispiel: AS 65010 sieht über AS 65020 nur dessen besten Pfad (65020 65030 65060).
- Design-Ziele: Skalierbarkeit, sichere Nachbarschaft (Authentifizierung), enge Filter (Multihomed-Kunde darf ISP-Routen nicht an anderen ISP geben = kein Transit), Policies für ein- und ausgehenden Traffic.

## 100 BGP Operations
- Tabellen: Neighbor table (explizit konfigurierte Nachbarn, TCP-Sessions), BGP table (alle gelernten Pfade, "BGP forwarding/topology database"), IP routing table (Best Path wird angeboten, AD entscheidet).
- AD eBGP 20, iBGP 200.
- 4 Nachrichtentypen: OPEN, KEEPALIVE, UPDATE, NOTIFICATION. (Eigenes Wissen: ROUTE-REFRESH Typ 5, RFC 2918.)
- Ablauf: TCP → OPEN von beiden → KEEPALIVE als Bestätigung → Established.
- OPEN: Version (BGP4), eigene ASN (wird geprüft – falsch → Session beendet), Hold Time (kleinerer Wert von beiden wird genutzt), BGP Router-ID (32 Bit), optionale Parameter (TLV, z. B. Capabilities/Authentifizierung).
- Router-ID: manuell (bgp router-id), sonst höchste Loopback-IP, sonst höchste aktive Interface-IP.
- KEEPALIVE: nur Header; Hold Time 0 → keine Keepalives.
- UPDATE: anfangs volle Tabelle, danach inkrementell. Ein Update = ein Satz Pfadattribute; Felder Withdrawn Routes, Path Attributes, NLRI.
- NOTIFICATION: bei Fehler, Error Code/Subcode/Data; Verbindung wird sofort geschlossen.

## 101 Neighbor Relationships
- BGP speaker = jeder Router mit BGP; BGP peer/neighbor = konfigurierter Partner.
- iBGP: gleiches AS (oft auch nicht direkt verbunden). eBGP: verschiedene AS (Kunde–ISP, ISP–ISP, CE–PE bei MPLS).
- eBGP-Voraussetzungen: verschiedene ASN, Nachbar definiert + TCP-Session, per Default direkt verbunden.

## 102 Path Selection
- BGP wählt genau einen Best Path nach Policy, nicht nach Bandbreite/Delay; kein Load Balancing per Default.
- Nicht-beste Pfade bleiben in der BGP-Tabelle als Backup.
- Reihenfolge (Kurs): Weight hoch → Local Pref hoch → lokal originiert (Next Hop 0.0.0.0) → kürzester AS_PATH → Origin niedrig (i < e < ?) → MED niedrig → eBGP vor iBGP → niedrigste IGP-Metrik zum Next Hop → ältester eBGP-Pfad → niedrigste Router-ID → niedrigste Nachbar-IP.
- Beispiel: 7 Pfade, Weight alle 0, Local Pref 4×200 → nur diese vier gehen weiter.

## 103 Path Attributes
- Well-known mandatory: ORIGIN, AS_PATH, NEXT_HOP.
- Well-known discretionary: LOCAL_PREF, ATOMIC_AGGREGATE.
- Optional transitive: AGGREGATOR, COMMUNITY (unbekannt → trotzdem weitergeben, Partial-Bit setzen).
- Optional non-transitive: MED (unbekannt → ohne Attribut weitergeben).
  - Kurs-Fehler: Im Abschnitt Nontransitive steht "optional transitive attribute" – gemeint non-transitive.
  - Kurs-Ungenauigkeit: "Each router modifies the next-hop attribute" – gilt für eBGP; iBGP lässt Next Hop per Default unverändert.
- Origin: network/aggregate → i; Redistribution → ?; e = EGP (obsolet).
- Weight: Cisco-lokal, nicht propagiert, 0–65535, lokal originiert 32768, sonst 0, höher besser. Beispiel R1: Weight 200 via R2, 150 via R4 → R2.
- Local Pref: AS-weit, nicht an eBGP gesendet, Default 100, höher besser; für Exit-Wahl mit mehreren Edge-Routern.
- AS_PATH: beim Originieren leer, ASN wird beim Verlassen des AS vorangestellt, Ursprungs-AS ganz rechts; kürzer besser; Loop-Schutz.
- MED ("BGP metric"): beeinflusst eingehenden Traffic aus Nachbar-AS, niedriger besser, wird nur innerhalb des empfangenden AS weitergegeben, nicht an das nächste AS; per Default nur bei Pfaden aus demselben Nachbar-AS verglichen; Nachbar kann ignorieren/überschreiben.

## 104 Discovery 11 Single-Homed eBGP
- Topologie: SP1 AS 1 (Lo0 10.0.3.1/24; E0/1 192.168.1.10, E0/2 192.168.2.10), R1 AS 100 (Lo0 10.0.1.1/24, E0/1 192.168.1.11), R2 AS 200 (Lo0 10.0.2.1/24, E0/2 192.168.2.11).
- R1: router bgp 100 / bgp log-neighbor-changes / network 10.0.1.0 mask 255.255.255.0 / neighbor 192.168.1.10 remote-as 1.
- SP1: router bgp 1; neighbor 192.168.1.11 remote-as 100; neighbor 192.168.2.11 remote-as 200; network 10.0.3.0 mask 255.255.255.0.
- Nur ein BGP-Prozess pro Router.
- Log: %BGP-5-ADJCHANGE: neighbor x Up.
- network-Befehl: originiert Präfix nur bei exaktem Match (Präfix + Maske) in der RIB; ohne mask → klassenbezogene Maske. Steuert nicht, wo BGP läuft (das tun neighbor-Befehle).
- show ip bgp summary: Router-ID 10.0.3.1 (Loopback), Table version, Spalten Neighbor V AS MsgRcvd MsgSent TblVer InQ OutQ Up/Down State/PfxRcd; Zahl in State/PfxRcd = Established + Anzahl Präfixe.
- show ip bgp neighbors: "external link", BGP state = Established, hold time 180, keepalive 60, Capabilities (Route refresh, Four-octets ASN, IPv4 Unicast).
- State Active = versucht Verbindung aufzubauen, noch nicht etabliert.
- show ip bgp: Status *, >, i, r, s, d, h ...; Origin i/e/?; lokal: Next Hop 0.0.0.0, Weight 32768. Auf R1: 10.0.2.0/24 Path "1 200 i", 10.0.3.0/24 Path "1 i"; empfangene Weight 0.
- show ip route: B 10.0.1.0/24 [20/0] via 192.168.1.11.
- Kurs-Tippfehler: "Network 10.0.1.2.0/24" (gemeint 10.0.2.0/24); erste show ip route-Ausgabe zeigt "2 subnets" bei 4 Subnetzen.

## Ergänzungen aus eigenem Wissen (für Fragen markiert)
- FSM: Idle → Connect → (Active) → OpenSent → OpenConfirm → Established.
- Default Timer Cisco: Keepalive 60, Hold 180; eBGP TTL 1, iBGP TTL 255.
- iBGP-Split-Horizon: iBGP-gelernte Routen nicht an andere iBGP-Peers.
- default-originate, Single-/Dual-/Multihomed-Begriffe, asdot-Notation, always-compare-med, RIB-failure.
