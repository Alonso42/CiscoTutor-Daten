# Kapitel 08 – Optimizing OSPF (Kursseiten 75–82)

## OSPF-Kosten (S. 75)
- Metrik = Kosten, kleiner ist besser. Cisco: cost = Referenzbandbreite / Interface-Bandbreite (bps), Ergebnis ganzzahlig, minimal 1.
- Default-Referenz 10^8 (100 Mbps). Defaults: 64k Serial 1562, T1 64, Ethernet 10, FE/GE/10GE/100GE alle 1 → keine Unterscheidung oberhalb 100 Mbps.
- Link-Kosten sind 16 Bit → max. 65535 pro Link. Referenz 10^11 (100 Gbps): 100G=1, 10G=10, T1 = 64766, langsamere Links landen auf 65535 (Verlust der Differenzierung unten).
- Pfadkosten = Summe der Kosten aller ausgehenden Links bis zum Ziel. SPF-Baum mit sich selbst als Wurzel; jeder Router eigene Sicht auf gleiche LSDB. Nicht-kürzeste Pfade werden verworfen (anders als EIGRP-Feasible-Successor). Bei Topologieänderung läuft Dijkstra neu.

## Discovery 8: OSPF Tuning (S. 76)
- Topologie: HQ1/HQ2/GW in Area 0 (172.16.123.0/25, GW DR wegen RID 3.3.3.3, HQ2 BDR, HQ1 DROTHER), DIST in Area 1 (zu HQ1 und HQ2, DIST DR wegen höchster RID 4.4.4.4), BR in Area 2 (Priority 0 → DROTHER, HQ2 DR, "No backup designated router"). BR = ASBR, redistribute connected → vier O E2 10.x [110/20].
- `show ip protocols`: "It is an autonomous system boundary router", "Redistributing External Routes from connected", "Maximum path: 4", "Passive Interface(s):", "Incoming update filter list ... is not set".
- passive-interface: unterdrückt OSPF-Pakete ein/aus; Netz wird weiter annonciert. `passive-interface default` + `no passive-interface e0/0`. Beim default-Befehl geht Adjazenz kurz down (Log FULL→DOWN), danach LOADING→FULL.
- default-information originate: Typ-5-LSA 0.0.0.0/0, Router wird ASBR. Ohne `always` nur, wenn eigene Default-Route existiert. Optionen: always, metric, metric-type, route-map. Default: E2, Metrik 1, Tag 1 (im Lab). Wird nicht in Stub-Areas geflutet.
- `show ip route 0.0.0.0` auf DIST: "type extern 2, forward metric 20" – forward metric = Kosten zum ASBR. ECMP, wenn Typ (E2), Metrik und forward metric gleich.
- traceroute vom Router selbst: process-switched → per-packet Lastverteilung sichtbar (probe 8).
- Static-Route weg auf GW → Default verschwindet aus OSPF; mit `always` bleibt sie (Black-Hole-Risiko, ICMP unreachable).
- `auto-cost reference-bandwidth 10000` (Mbps) auf ALLEN Routern; Warnung "Please ensure reference bandwidth is consistent across all routers". Ethernet 10 Mbps → Kosten 1000.
- Loopback GW 192.168.3.3 von DIST: vorher 21 (10+10+1), nachher 2001 (1000+1000+1), ECMP über HQ1/HQ2.
- `ip ospf cost 500` auf DIST e0/0 (Richtung HQ1): 1–65535, überschreibt Berechnung. Danach 192.168.3.3 = 1501 via HQ1; Default forward metric 1500 via HQ1 (kein ECMP mehr). 192.168.1.1 (HQ1 Lo) = 501; 192.168.2.2 = 1001 via HQ2; 172.16.25.0/28 = 2000 via HQ2; 192.168.5.5 = 2001 via HQ2; 172.16.123.0/25 = 1500 via HQ1. E2-Routen 10.x bleiben via HQ2 [110/20] (forward metric zu BR via HQ2 = 2000 < 2500).
- Alternativ Kosten über `bandwidth` beeinflussen (wirkt auch auf andere Protokolle/QoS).

## Route Summarization (S. 77)
- Weniger Routen, weniger LSA-Flooding, Topologieänderungen lokal, weniger SPF in anderen Areas.
- ABR fasst Typ-3 zusammen (intra-area Routen aus Typ 1/2 einer Area), ASBR fasst Typ-5 zusammen.
- Braucht zusammenhängende Adressvergabe pro Area. Nachteile: mögliche suboptimale Pfade bei mehreren ABR/ASBR, Summary hat nur eine Metrik; spezifischere Route wird per Longest Match bevorzugt.

## Route Filtering Tools (S. 78)
- Die meisten Filter entfernen nichts aus der LSDB, nur aus der lokalen RIB; andere Router unbeeinflusst.
- distribute-list: ACL/Prefix-List/Route-Map auf Updates; in/out/Redistribution. OSPF: `distribute-list in` filtert nur, was SPF in die eigene RIB schreibt.
- Prefix-List: Vorteile – Präfix + Präfixlänge, Baumstruktur (schneller als sequentielle ACL), Sequenznummern (Default-Schritt 5? → Kurs: "default sequence number", eigenes Wissen: 5, 10, 15), implizites deny am Ende. Ohne ge/le muss Maskenlänge exakt passen.
- Route-Map: match/set, top-down, erste Übereinstimmung gewinnt, implizites deny. Mehrere Kriterien in EINER match-Zeile = OR, mehrere match-Zeilen = AND. Ohne Sequenznummer: neue Route-Map → 10. `no route-map NAME` ohne Nummer löscht die ganze Map. Einsatz: Redistribution, PBR, BGP.

## Discovery 9: OSPF Optimization (S. 79)
- R1 ABR (Area 0 zu R4, Area 1 zu R2, Area 2 zu R3), R2 Loopbacks 192.168.16–23.0/24, R3 ASBR mit 10.33.4–7.0/24 extern, R4 ASBR mit Default (Internet).
- `area 1 range 192.168.16.0 255.255.248.0` (=/21). Syntax: `area id range addr mask [advertise|not-advertise] [cost c]`. Summary nur, wenn mind. ein Subnetz im Bereich existiert. Kosten der Summary laut Kurs = niedrigste Kosten der Komponenten (IOS-Default `compatible rfc1583`, RFC 1583 Abschn. 3.5: Minimum). RFC 2328 Abschn. 3.5/12.4.3: Maximum; in IOS per `no compatible rfc1583` (Checker-Prüfung). Null0-Route "192.168.16.0/21 is a summary, Null0" auf dem ABR.
- R3/R4 sehen O IA 192.168.16.0/21 [110/21]; Typ-3 nur noch für .16.0 in Area 0.
- Null0 verhindert Schleifen: Paket an unbekanntes Subnetz im Summary-Bereich wird verworfen statt Default-Route.
- ASBR: `summary-address 10.33.4.0 255.255.252.0` (=/22). Syntax: `summary-address addr mask [not-advertise] [tag t] [nssa-only]`. R3 erhält O 10.33.4.0/22 Null0; andere sehen ein O E2 10.33.4.0/22 [110/20], ein Typ-5.
- Filtering-Arten: (1) `area X filter-list prefix NAME in|out` (Typ-3 am ABR), (2) `area range ... not-advertise` (Typ-3), (3) `distribute-list in` (nur RIB, Typ-3/5 Routen), (4) `summary-address ... not-advertise` (Typ-5 am ASBR).
- filter-list out: filtert Präfixe AUS der Area hinaus (in alle anderen Areas). in: filtert Präfixe IN die Area hinein. Prefix-list FROM_R2: `deny 192.168.2.0/24`, `permit 0.0.0.0/0 le 32`. `clear ip ospf process`. `show ip ospf` → "Area-filter FROM_R2 out", "Area ranges are 192.168.16.0/21 Active(11) Advertise".
- `area 0 filter-list prefix FROM_R2 in` → nicht in Area 0, aber weiter in Area 2. R1 selbst behält Route (intra-area).
- `area 2 range 192.168.3.0 255.255.255.0 not-advertise` → "192.168.3.0/24 Passive DoNotAdvertise"; wirkt wie filter-list out.
- distribute-list 1 in (ACL deny 192.168.4.0 0.0.0.255, permit any) auf R1: Typ-1-LSA von R4 noch in LSDB, Route nicht in RIB; R2/R3 bekommen weiter Typ-3 192.168.4.0 (ABR erzeugt Typ-3 trotzdem!). show ip protocols: "Incoming update filter list for all interfaces is 1" / "(prefix-list) R4-LOOP" / "(route-map) WAN-FILTER".
- `distribute-list prefix R4-LOOP in`; `distribute-list route-map WAN-FILTER in`. Route-map deny 10 mit `match ip address prefix-list WAN-LINKS` + `match ip route-source R1-ID` (ACL permit 1.1.1.1 = RID des LSA-Erzeugers) → AND; permit 20 leer erlaubt Rest.
- distribute-list out bei OSPF nur auf ASBR für redistributed routes.
- Neues Loopback 10.33.33.1/24 auf R3 → Typ-5 "Metric Type 2, Metric 20, Forward Address 0.0.0.0"; R1: "type extern 2, forward metric 10". `summary-address 10.33.33.0 255.255.255.0 not-advertise` → Typ-5 verschwindet aus LSDB aller Router.

## OSPFv2 vs OSPFv3 (S. 80)
- `router ospf` (v2, IPv4-Transport), `ipv6 router ospf` (klassisches OSPFv3, nur IPv6, Peering über Link-Local), `router ospfv3` (AF-Modell, IPv4+IPv6, Transport IPv6 Link-Local; kein Peering mit OSPFv2).
- AF-Feature ab 15.1(3)S / 15.2(1)T; ältere/Fremdgeräte setzen AF-Bit nicht → keine Nachbarschaft für IPv4-AF. (Kursfehler: "IPv6 RIB" statt IPv4 RIB.)

## Discovery 10: OSPFv3 (S. 81)
- `ipv6 unicast-routing` nötig. `ipv6 router ospf 1` (process-id 1–65535), `router-id` 32 Bit Pflicht wenn keine aktive IPv4-Adresse, sonst startet Prozess nicht. Kein network-Befehl: `ipv6 ospf 1 area 0` im Interface. Interface braucht IPv6 (Adresse oder `ipv6 enable`).
- Loopback wird als /128 annonciert, `ipv6 ospf network point-to-point` → /64.
- Neighbor-Ausgabe: Spalte "Interface ID" statt Adresse; Next-Hops FE80::x.
- Ohne Summary: R1 als ABR sieht alles intra-area (O). OI = inter-area, OE1/OE2 extern.
- LSDB: Router (1, mit Bits B für ABR), Net (2), Inter Area Prefix (3), Inter Area Router (4), Link (8, link-local scope: Link-Local-Adresse + Präfixe des Links), Intra Area Prefix (9, Ref-lstype 0x2001 Router / 0x2002 Network). Präfixe als prefix/length, Default ::/0.
- Migration: `router ospfv3 1` übernimmt klassische Konfig → `address-family ipv6 unicast` automatisch; router-id global (auch pro AF möglich); passive-interface pro AF.
- Interface neu: `ospfv3 1 ipv6 area 0`, `ospfv3 1 ipv4 area 0`; IPv4-AF braucht IPv4-Adresse am Interface; nur ein Prozess pro AF pro Interface.
- `show ospfv3 neighbor` zeigt beide AFs; `show ip route ospfv3` für IPv4-Routen aus OSPFv3 (show ip route ospf zeigt nichts → OSPFv2). `show ip ospf database` zeigt nichts.
- `show ospfv3 interface`: IPv4-AF Instance ID 64, IPv6-AF Instance ID 0; Hello 10/Dead 40.
- Optimierung: `area 1 range 2001:DB8:0:220::/60` (16 /64 → /60), `summary-prefix` am ASBR (IPv6), `default-information originate` pro AF → O*E2 0.0.0.0/0 und OE2 ::/0 tag 1.
- `ospfv3 1 ipv6 cost 200` nur für IPv6-AF; IPv4 bleibt 64. R4 → 2001:DB8:0:22::/64: 10+64+1=75, danach 10+200+1=211.
- Timer: `ospfv3 1 ipv6 hello-interval x`, `dead-interval`.

## Kursfehler/Unstimmigkeiten
- S. 75: 10^11 als "1011" dargestellt (Formatierung).
- S. 79: "summary of all the interarea (type 1 and type 2 LSAs) routes" – gemeint intra-area Routen.
- S. 80: IPv4-OSPFv3-Routen in "IPv6 RIB" – richtig IPv4 RIB.
- S. 81: Job Aid R1/R4 172.16.14.x/24, Ausgaben zeigen /25.
