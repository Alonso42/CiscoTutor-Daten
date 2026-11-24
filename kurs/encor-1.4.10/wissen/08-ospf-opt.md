# Optimizing OSPF

Quelle: ENCOR 1.4.10 Student Guide, Seiten 75–82 (OSPF Cost, Discovery 8 „Implement OSPF Tuning“, OSPF Route Summarization, OSPF Route Filtering Tools, Discovery 9 „Apply OSPF Optimization“, Compare OSPFv2 and OSPFv3, Discovery 10 „Implement OSPFv3“, Summary)

Topics: ENCOR-3.2.b (OSPFv2/v3: Kosten, Summarization, Filtering, Default-Routing, OSPFv3 mit Address-Families), Bezug zu ENCOR-3.2.a (SPF/Link-State)

Ergänzungen aus eigenem Fachwissen bzw. aus dem Prüfprotokoll (nicht im Kurs) sind mit *(Ergänzung)* markiert. Grundlagen (LSA-Typen, Areas, DR/BDR) stehen in `wissen/07-ospf.md`.

## OSPF-Kosten

- Metrik von OSPF = **Kosten** (cost). Kleiner ist besser. Der RFC schreibt keine Formel vor; Cisco rechnet:

  **cost = Referenzbandbreite / Interface-Bandbreite** (beide in bit/s), ganzzahlig **abgeschnitten**, Minimum **1**.
- Default-Referenzbandbreite: **10^8 bit/s = 100 Mbit/s**.

| Interface | Bandbreite | Kosten (Ref. 100 Mbit/s) | Ref. 10 Gbit/s (10000) | Ref. 100 Gbit/s (100000) |
|---|---|---|---|---|
| Serial 56/64 kbit/s | 64 kbit/s | 1562 | 65535 (gekappt) | 65535 (gekappt) |
| T1 | 1,544 Mbit/s | 64 | 6476 | 64766 |
| Ethernet | 10 Mbit/s | 10 | 1000 | 10000 |
| Fast Ethernet | 100 Mbit/s | 1 | 100 | 1000 |
| Gigabit Ethernet | 1 Gbit/s | 1 | 10 | 100 |
| 10 Gigabit Ethernet | 10 Gbit/s | 1 | 1 | 10 |
| 100 Gigabit Ethernet | 100 Gbit/s | 1 | 1 | 1 |

- Problem: Mit der Default-Referenz kosten alle Links ab 100 Mbit/s gleich (1). OSPF kann dann schnelle Links nicht mehr unterscheiden.
- Lösung: `auto-cost reference-bandwidth <Mbit/s>` (Bereich 1–4294967, Default 100) unter `router ospf`. **Auf allen Routern gleich setzen**, sonst rechnen Router mit unterschiedlichen Maßstäben (IOS warnt: „Please ensure reference bandwidth is consistent across all routers“).
- Grenze: Link-Kosten sind ein **16-Bit-Feld**, max. **65535** pro Link. Bei sehr hoher Referenz landen langsame Links am Maximum und sind untereinander nicht mehr unterscheidbar (Kursaussage, Kappung auf 65535).
- Manuell: `ip ospf cost <1-65535>` im Interface überschreibt die Berechnung. Alternativ über den Befehl `bandwidth <kbit/s>` (wirkt aber auch auf EIGRP, QoS usw.).
- Kosten wirken nur in **Senderichtung** (ausgehendes Interface).

## SPF-Berechnung

- Jeder Router stellt sich selbst als **Wurzel** eines Shortest-Path-Baums auf und berechnet die kumulierten Kosten zu allen Zielen. Alle Router einer Area haben dieselbe LSDB, aber jeder hat seinen eigenen Baum.
- **Pfadkosten = Summe der Kosten aller ausgehenden Interfaces** vom Router bis zum Zielnetz (einschließlich des Ziel-Interfaces).
- Es bleiben nur die besten Pfade. Gleich teure Pfade (ECMP) werden installiert, Default **maximum-paths 4**. Anders als EIGRP (Feasible Successor) hält OSPF keine vorgerechneten Backup-Pfade; bei einer Topologieänderung läuft SPF neu.

Beispiel (eigene Werte, wie in der Kursabbildung aufgebaut): R1 hat Links zu R2 (Kosten 10) und R3 (Kosten 20); R2–R4 = 10, R3–R4 = 10; LANs: R2 = 4, R3 = 2, R4 = 10.

| Ziel | bester Weg | Kosten | Alternative |
|---|---|---|---|
| R2-LAN | R1 → R2 | 10 + 4 = 14 | über R3/R4: 20 + 10 + 10 + 4 = 44 |
| R3-LAN | R1 → R3 | 20 + 2 = 22 | über R2/R4: 10 + 10 + 10 + 2 = 32 |
| R4-LAN | R1 → R2 → R4 | 10 + 10 + 10 = 30 | über R3: 20 + 10 + 10 = 40 |

## Discovery 8: OSPF Tuning (Labwissen)

Topologie (eigene Zusammenfassung):
- **Area 0**: Segment 172.16.123.0/25 mit HQ1 (.1), HQ2 (.2) und GW (.3). GW hat Eth0/1 209.165.200.226/27 zum Internet.
- **Area 1**: DIST mit zwei Links: Eth0/0 zu HQ1 (172.16.14.0/28) und Eth0/1 zu HQ2 (172.16.24.0/28). HQ1 und HQ2 sind ABRs.
- **Area 2**: HQ2 Eth0/2 zu BR (172.16.25.0/28). BR ist ASBR und redistributiert vier externe Netze (Loopbacks 10.x/24, `redistribute connected`).
- Loopbacks /32: HQ1 192.168.1.1, HQ2 192.168.2.2, GW 192.168.3.3, DIST 192.168.4.4, BR 192.168.5.5. RIDs x.x.x.x (1.1.1.1 … 5.5.5.5).
- DR-Lage: Area-0-Segment GW DR (höchste RID 3.3.3.3), HQ2 BDR, HQ1 DROTHER. DIST ist DR auf seinen Links (RID 4.4.4.4). Auf HQ2–BR hat BR Priority 0 → HQ2 DR, „No backup designated router on this network“.
- Alle Links sind 10-Mbit/s-Ethernet (Kosten 10 bei Default-Referenz).

### Passive Interfaces
- `passive-interface <if>`: keine OSPF-Pakete senden und empfangenen ignorieren → keine Nachbarschaft, das Netz wird **weiter annonciert**. Sinnvoll für LAN-/Benutzerports und Loopbacks.
- `passive-interface default` macht alle Interfaces passiv, auch die Uplinks. Ausnahme mit `no passive-interface Ethernet0/0`. Im Lab fällt die Adjazenz kurz (Log FULL → DOWN) und kommt nach `no passive-interface` über LOADING → FULL zurück.
- Kontrolle: `show ip protocols` listet „Passive Interface(s)“.

### Default-Route per OSPF
- `default-information originate` auf dem Uplink-Router (GW) erzeugt eine **Typ-5-LSA 0.0.0.0/0**. Der Router wird dadurch zum **ASBR**.
- Ohne `always` nur, wenn der Router selbst eine Default-Route in der Routingtabelle hat (z. B. statisch zum ISP). Mit `always` immer – fällt der Uplink aus, entsteht ein **Black Hole** (Pakete laufen zu GW und werden verworfen bzw. mit ICMP unreachable beantwortet).
- Optionen: `always`, `metric <n>`, `metric-type 1|2`, `route-map <name>` (bedingte Annonce). Default: E2, Metrik 1 (im Lab Tag 1).
- Die Default-Route wird in alle Areas außer Stub-/NSSA-Areas geflutet (dort Typ 5 gesperrt).

```
GW(config)# ip route 0.0.0.0 0.0.0.0 209.165.200.225
GW(config)# router ospf 1
GW(config-router)# default-information originate

DIST# show ip route 0.0.0.0
Routing entry for 0.0.0.0/0, supernet
  Known via "ospf 1", distance 110, metric 1, candidate default path
  Tag 1, type extern 2, forward metric 20
  * 172.16.14.1 ...   172.16.24.2 ...       ! ECMP über HQ1 und HQ2
```
- **forward metric** = Kosten bis zum ASBR. Bei E2-Routen bleibt die Metrik überall gleich (hier 1); gibt es mehrere Wege, entscheidet die forward metric. ECMP nur, wenn Typ (E2), Metrik und forward metric gleich sind.
- Traceroute vom Router selbst wird prozessgeswitcht, daher sieht man per-Paket-Lastverteilung über beide Wege (plattformabhängig).

### Kosten anpassen
- `auto-cost reference-bandwidth 10000` auf **allen fünf Routern** → Ethernet (10 Mbit/s) kostet 1000.
- DIST → GW-Loopback 192.168.3.3: vorher 10 + 10 + 1 = **21**, nachher 1000 + 1000 + 1 = **2001**, beide Male ECMP über HQ1 und HQ2.
- `ip ospf cost 500` auf DIST Eth0/0 (Richtung HQ1):

| Ziel von DIST | Kosten | Weg |
|---|---|---|
| 192.168.3.3 (GW) | 500 + 1000 + 1 = 1501 | nur HQ1 (über HQ2 2001) |
| 192.168.1.1 (HQ1) | 501 | HQ1 |
| 192.168.2.2 (HQ2) | 1001 | HQ2 |
| 172.16.123.0/25 | 1500 | HQ1 |
| 172.16.25.0/28 | 2000 | HQ2 |
| 192.168.5.5 (BR) | 2001 | HQ2 |
| 0.0.0.0/0 (E2) | Metrik 1, forward metric 1500 | nur HQ1 |
| 10.x/24 von BR (E2) | Metrik 20, forward metric 2000 | HQ2 (über HQ1 wären es 2500) |

## Route Summarization

- Ziel: weniger Routen, kleinere LSDB, weniger LSA-Flooding und weniger SPF-Läufe in anderen Areas. Topologieänderungen bleiben lokal: Fällt ein Teilnetz weg, merkt die übrige Domain nichts, solange die Summary bestehen bleibt.
- Wo:
  - **ABR** fasst die Intra-Area-Netze (aus Typ 1/2) einer Area zu einer **Typ-3-LSA** zusammen: `area <area-id> range <netz> <maske> [advertise | not-advertise] [cost <0-16777215>]`. Die Area-ID ist die Area, **in der die Teilnetze liegen**.
  - **ASBR** fasst redistributierte externe Netze zu einer **Typ-5-LSA** (bzw. Typ 7) zusammen: `summary-address <netz> <maske> [not-advertise] [tag <t>] [nssa-only]`.
- Summarization ist **nie automatisch** und nur an ABR/ASBR möglich (innerhalb einer Area nicht, alle brauchen dieselbe LSDB).
- Voraussetzung: zusammenhängende Adressvergabe pro Area (gutes Adressierungskonzept).
- Die Summary wird nur annonciert, solange **mindestens ein Teilnetz** im Bereich existiert.
- **Metrik der Summary**: Cisco IOS ist per Default `compatible rfc1583` und nutzt die **niedrigsten** Kosten der Teilnetze (RFC 1583 3.5). RFC 2328 (3.5/12.4.3) verlangt die **höchsten**; in IOS mit `no compatible rfc1583` (auf allen Routern gleich setzen). Mit `cost` lässt sich ein fester Wert erzwingen.
- Der summierende Router legt eine **Discard-Route nach Null0** an („is a summary, Null0“). Pakete an nicht existierende Teilnetze im Bereich werden verworfen, statt einer weniger spezifischen Route (z. B. Default) zu folgen → verhindert Schleifen.
- Nachteile: Summary hat nur **eine Metrik**; bei mehreren ABRs/ASBRs evtl. **suboptimales Routing**. Eine spezifischere Route aus anderer Quelle gewinnt immer per **Longest Match**.

## Route-Filtering-Werkzeuge

Grundsatz: In OSPF brauchen alle Router einer Area dieselbe LSDB. Die meisten Filter **entfernen nichts aus der LSDB**, sondern verhindern nur, dass eine Route in die lokale Routingtabelle kommt; andere Router sind davon nicht betroffen. Echte LSA-Filter gibt es nur an Area-Grenzen (ABR) bzw. bei der Redistribution (ASBR).

### Distribute-List
- Wendet eine ACL, Prefix-List oder Route-Map auf Routing-Updates an: eingehend, ausgehend oder bei der Redistribution.
- Bei OSPF: `distribute-list <acl> in` (bzw. `distribute-list prefix <name> in`, `distribute-list route-map <name> in`) filtert nur, was SPF **in die eigene RIB** schreibt. Die LSA bleibt in der LSDB, wird weiter geflutet; ein ABR erzeugt im Lab trotzdem weiter die Typ-3-LSA für das gefilterte Netz. Auf Transitroutern droht ein **Black Hole** (Nachbarn schicken Verkehr, der Router hat keine Route).
- `distribute-list … out` wirkt bei OSPF nur auf dem **ASBR** für redistributierte Routen.
- Ausgehende Interface-ACLs filtern keinen vom Router selbst erzeugten Verkehr (also auch keine eigenen OSPF-Pakete). Eine eingehende ACL könnte OSPF-Pakete nur komplett verwerfen (Adjazenz fällt), aber keine einzelnen Routen filtern – dafür braucht es die Distribute-List.

```
access-list 1 deny 192.168.4.0 0.0.0.255
access-list 1 permit any
router ospf 1
 distribute-list 1 in
```

### Prefix-Lists
- Vorteile gegenüber ACLs: prüfen **Präfix und Präfixlänge**, werden intern als **Baum** ausgewertet (schneller als sequenzielle ACL), haben **Sequenznummern** (einfügen/löschen einzelner Zeilen; ohne Angabe automatisch in Fünferschritten 5, 10, 15 …), am Ende **implizites deny**.
- Syntax: `ip prefix-list <name> [seq n] permit|deny <netz>/<len> [ge x] [le y]`.
- Ohne ge/le muss die Länge **exakt** passen (10.0.0.0/16 trifft 10.0.0.0/16, aber nicht 10.1.0.0/16 oder 10.0.1.0/24).
- `ge` = Mindestlänge, `le` = Höchstlänge; Regel: len < ge ≤ le ≤ 32. Nur `le` → von len bis le; nur `ge` → von ge bis 32.
- „Alles erlauben“ am Ende: `permit 0.0.0.0/0 le 32`.

| Eintrag | trifft | trifft nicht |
|---|---|---|
| 10.0.0.0/16 | nur 10.0.0.0/16 | 10.0.1.0/24 |
| 10.0.0.0/8 ge 24 le 24 | jedes /24 in 10/8 | 10.1.0.0/16, 10.1.1.0/25 |
| 172.16.0.0/16 ge 17 | 172.16.5.0/24 | 172.16.0.0/16 |
| 0.0.0.0/0 le 32 | alles | – |
| 0.0.0.0/0 | nur die Default-Route | alles andere |

```
R1(config)# ip prefix-list PFL seq 5 permit 10.10.11.0/24
R1(config)# ip prefix-list PFL seq 10 permit 10.10.12.0/24
R1# show ip prefix-list
ip prefix-list PFL: 2 entries
   seq 5 permit 10.10.11.0/24
   seq 10 permit 10.10.12.0/24
```

### Route-Maps
- Wie ACLs mit Namen statt Nummer, aber mächtiger: `match` (Bedingung) und `set` (Aktion, z. B. Metrik, Metrik-Typ, Next Hop).
- Abarbeitung **von oben nach unten** nach Sequenznummer; der **erste Treffer** entscheidet, danach Ende. `permit` + Treffer → Route wird verwendet/redistributiert (mit set-Änderungen); `deny` + Treffer → Route wird verworfen. Kein Treffer bis zum Ende → **implizites deny**.
- Mehrere Werte in **einer** match-Zeile = logisches **ODER** (`match ip address ACL1 ACL2 ACL3`). Mehrere match-Zeilen = logisches **UND**. Eine Sequenz ohne match trifft alles.
- Sequenznummern: Ohne Angabe bekommt eine neue Route-Map die **10**. Existiert genau ein Eintrag, wird dieser bearbeitet; bei mehreren Einträgen verlangt IOS eine Nummer. `no route-map NAME` ohne Nummer löscht die **ganze** Map.
- Einsatz: Filtern/Markieren bei Redistribution, Policy-Based Routing (PBR), BGP-Policies.

```
route-map WAN-FILTER deny 10
 match ip address prefix-list WAN-LINKS
 match ip route-source R1-ID          ! UND: Präfix passt UND LSA-Erzeuger = RID aus ACL R1-ID
route-map WAN-FILTER permit 20        ! ohne match: alles andere erlauben
router ospf 1
 distribute-list route-map WAN-FILTER in
```
`match ip route-source` prüft bei OSPF die **RID des LSA-Erzeugers** (Advertising Router), nicht die Next-Hop-Adresse.

## Discovery 9: OSPF-Optimierung (Labwissen)

Topologie (eigene Zusammenfassung):
- R1 = ABR: Eth0/0 zu R4 (172.16.14.0/25, **Area 0**), Eth0/1 zu R2 (172.16.12.0/30, **Area 1**), Eth0/2 zu R3 (172.16.13.0/30, **Area 2**). R1 Lo0 192.168.1.1/24.
- R2: Lo0 192.168.2.1/24 und acht Loopbacks 192.168.16.0/24 bis 192.168.23.0/24.
- R3 = ASBR mit vier externen Netzen 10.33.4.0/24 bis 10.33.7.0/24, Lo0 192.168.3.1/24.
- R4 = ASBR mit statischen Routen ins Internet (198.51.100.0/24, 192.0.2.0/24) und Default-Route per OSPF, Lo0 192.168.4.1/24.

Summarization:
```
R1(config-router)# area 1 range 192.168.16.0 255.255.248.0      ! 8 × /24 → /21
R1# show ip route | include Null0
O     192.168.16.0/21 is a summary, 00:00:12, Null0
R4# show ip route ospf
O IA  192.168.16.0/21 [110/21] via 172.16.14.1                ! eine Route statt acht

R3(config-router)# summary-address 10.33.4.0 255.255.252.0      ! 4 × /24 → /22
R3: O 10.33.4.0/22 is a summary, Null0
R1/R4: O E2 10.33.4.0/22 [110/20] – nur noch eine Typ-5-LSA
```
- `show ip ospf` auf R1 zeigt u. a. „Area ranges are 192.168.16.0/21 Active(11) Advertise“ (Zahl in Klammern = Metrik der Summary).

Filter-Varianten im Lab:

| Werkzeug | Ort | betrifft | Wirkung im Lab |
|---|---|---|---|
| `area 1 filter-list prefix FROM_R2 out` | ABR | Typ 3 | 192.168.2.0/24 aus Area 1 erscheint in **keiner** anderen Area |
| `area 0 filter-list prefix FROM_R2 in` | ABR | Typ 3 | fehlt nur in Area 0, Area 2 sieht es weiter; R1 selbst behält die Route (intra-area) |
| `area 2 range 192.168.3.0 255.255.255.0 not-advertise` | ABR | Typ 3 | „192.168.3.0/24 Passive DoNotAdvertise“, wirkt wie filter-list out |
| `distribute-list 1 in` / `prefix` / `route-map` | jeder Router | nur RIB | LSA bleibt in der LSDB; R1 erzeugt weiter Typ 3 für R2/R3 |
| `summary-address 10.33.33.0 255.255.255.0 not-advertise` | ASBR | Typ 5 | Typ-5-LSA verschwindet aus der LSDB aller Router |

- Prefix-List für filter-list: `ip prefix-list FROM_R2 deny 192.168.2.0/24` + `ip prefix-list FROM_R2 permit 0.0.0.0/0 le 32`. Danach `clear ip ospf process`. `show ip ospf` zeigt „Area-filter FROM_R2 out“.
- `area X filter-list … out` = Präfixe **aus** Area X heraus in alle anderen Areas filtern; `in` = Präfixe **in** Area X hinein filtern.
- `show ip protocols` zeigt aktive Distribute-Lists: „Incoming update filter list for all interfaces is 1“ bzw. „(prefix-list) R4-LOOP“ bzw. „(route-map) WAN-FILTER“.
- Neues externes Netz 10.33.33.0/24 auf R3: Typ-5 „Metric Type: 2, Metric: 20, Forward Address: 0.0.0.0“; auf R1 „type extern 2, forward metric 10“.

## OSPFv2 vs. OSPFv3

| | OSPFv2 | OSPFv3 klassisch | OSPFv3 mit Address-Families |
|---|---|---|---|
| Befehl | `router ospf <id>` | `ipv6 router ospf <id>` | `router ospfv3 <id>` |
| Routet | IPv4 | nur IPv6 | IPv4 **und** IPv6 |
| Transport | IPv4 | IPv6 (Link-Local) | IPv6 (Link-Local), auch für die IPv4-AF |
| Peering mit OSPFv2 | – | nein | nein |

- Gemeinsam: Pakettypen 1–5, SPF, Kosten, Areas, DR/BDR, Router-ID 32 Bit. *(Ergänzung)* OSPFv3 nutzt FF02::5/FF02::6, Next Hops sind FE80-Link-Local-Adressen, Aktivierung pro Interface statt network-Befehl, Authentifizierung über IPsec bzw. Trailer.
- Address-Family-Unterstützung ab IOS 15.1(3)S / 15.2(1)T. Ältere Software und Fremdgeräte setzen das **AF-Bit** nicht → mit ihnen bildet sich für die IPv4-AF keine Nachbarschaft; sie nehmen nicht an der IPv4-AF teil.
- Jede AF ist eine eigene Instanz mit eigenen Nachbarschaften: Instance-ID **0** für IPv6 Unicast, **64** für IPv4 Unicast (RFC 5838: 0–31 IPv6 UC, 64–95 IPv4 UC).

### OSPFv3-LSAs

| Typ (Code) | Name | Inhalt |
|---|---|---|
| 1 (0x2001) | Router | Links des Routers, keine Präfixe; Bits B = ABR, E = ASBR, V = Virtual-Link-Endpunkt |
| 2 (0x2002) | Network | Transitnetz vom DR, keine Präfixe |
| 3 (0x2003) | Inter-Area-Prefix | Präfix aus anderer Area (vom ABR) |
| 4 (0x2004) | Inter-Area-Router | Ort eines ASBR in anderer Area |
| 5 (0x4005) | AS-External | externe Präfixe |
| 7 (0x2007) | NSSA | externe Präfixe in NSSA |
| 8 (0x0008) | Link | Link-Local-Adresse + Präfixe, nur auf dem Link gültig |
| 9 (0x2009) | Intra-Area-Prefix | Präfixe eines Routers (Ref-lstype 0x2001) oder Transitnetzes (0x2002) |

Topologie und Adressen sind damit getrennt: Typ 1/2 beschreiben nur den Graphen, Präfixe stehen in Typ 9 (und 8).

## Discovery 10: OSPFv3 (Labwissen)

Topologie (eigene Zusammenfassung): R1 = ABR. Eth0/0 zu R4 (172.16.14.0/24 bzw. /25 in den Ausgaben, 2001:DB8:0:14::/64, **Area 0**), Ser2/0 zu R2 (172.16.12.0/30, 2001:DB8:0:12::/64, **Area 1**), Eth0/1 zu R3 (172.16.13.0/30, 2001:DB8:0:13::/64, **Area 2**). Loopbacks: R1 192.168.1.1/24 + 2001:DB8:0:11::1/64, Lo1 209.165.201.1/32 + 2001:DB8:209:165::1/64 (Internet-Simulation); R2 2001:DB8:0:22::1/64 + 16 Netze 2001:DB8:0:220::/64 bis 2001:DB8:0:22F::/64; R3 2001:DB8:0:33::1/64; R4 2001:DB8:0:44::1/64. R2/R3/R4 sind mit beiden AFs vorkonfiguriert.

Klassische Konfiguration auf R1:
```
ipv6 unicast-routing
ipv6 router ospf 1
 router-id 1.1.1.1                 ! Pflicht, wenn keine aktive IPv4-Adresse existiert
interface Ethernet0/0
 ipv6 ospf 1 area 0                ! kein network-Befehl
interface Loopback0
 ipv6 ospf 1 area 0
 ipv6 ospf network point-to-point  ! sonst als /128 annonciert
```
- Prozess-ID 1–65535. Interface braucht IPv6 (globale Adresse oder `ipv6 enable` für Link-Local).
- `show ipv6 ospf neighbor`: Spalte „Interface ID“ statt Adresse. Next Hops in `show ipv6 route ospf` sind FE80::x.
- Routing-Codes: O (intra), OI (inter-area), OE1/OE2 (extern), ON1/ON2 (NSSA).

Migration auf Address-Families:
```
R1(config)# router ospfv3 1          ! übernimmt die ipv6-router-ospf-Konfiguration
R1(config-router)# address-family ipv6 unicast   ! wird automatisch angelegt
R1(config)# interface Ethernet0/0
R1(config-if)# ospfv3 1 ipv6 area 0
R1(config-if)# ospfv3 1 ipv4 area 0  ! IPv4-AF, Interface braucht eine IPv4-Adresse
R1(config)# router ospfv3 1
R1(config-router)# address-family ipv4 unicast
```
- router-id global unter `router ospfv3` (auch je AF möglich). `passive-interface`, `default-information originate`, `area range`, `summary-prefix` werden **je AF** konfiguriert. Pro Interface nur ein Prozess je AF.
- Prüfen: `show ospfv3 neighbor` (beide AFs), `show ospfv3 interface` (Instance ID 0 bzw. 64, Hello 10/Dead 40), `show ospfv3 database`, `show ip route ospfv3` (IPv4-Routen aus OSPFv3). `show ip route ospf` und `show ip ospf database` zeigen nur OSPFv2 und bleiben leer.

Optimierung je AF:
```
router ospfv3 1
 address-family ipv6 unicast
  area 1 range 2001:DB8:0:220::/60        ! 16 × /64 → /60, auf anderen Routern OI
  default-information originate           ! → OE2 ::/0 tag 1
 address-family ipv4 unicast
  default-information originate           ! → O*E2 0.0.0.0/0
interface Serial2/0
 ospfv3 1 ipv6 cost 200                   ! nur IPv6-AF
```
- Auf dem ASBR fasst `summary-prefix <präfix>/<len>` externe IPv6-Routen zusammen.
- Effekt der AF-Kosten: R4 → 2001:DB8:0:22::/64 vorher 10 + 64 + 1 = **75**, nachher 10 + 200 + 1 = **211**; der IPv4-Weg bleibt bei 75 (Serial-Kosten IPv4 weiter 64).
- Timer je AF: `ospfv3 1 ipv6 hello-interval <s>`, `ospfv3 1 ipv6 dead-interval <s>`.

## Troubleshooting-Hinweise

| Symptom | Ursache | Prüfen |
|---|---|---|
| Links ≥ 100 Mbit/s alle Kosten 1 | Default-Referenz | `show ip ospf interface` (Cost), auto-cost überall setzen |
| unerwartet asymmetrische Pfade | Referenzbandbreite/`ip ospf cost` nur auf einer Seite | Kosten wirken nur ausgehend |
| Default-Route fehlt | Originator hat selbst keine Default-Route, Area ist Stub/NSSA | `show ip route 0.0.0.0`, `always` (Black-Hole-Risiko) |
| Summary fehlt | kein Teilnetz im Bereich vorhanden, falsche Area-ID in `area range` | `show ip ospf` (Area ranges) |
| Route fehlt nur auf einem Router | `distribute-list in` | `show ip protocols`, LSA in `show ip ospf database` vorhanden |
| IPv4 über OSPFv3 ohne Nachbarn | AF-Bit fehlt (alte Software), keine IPv4-Adresse am Interface, IPv6 nicht aktiv | `show ospfv3 neighbor`, `show ospfv3 interface` |
| OSPFv3 startet nicht | keine Router-ID (keine IPv4-Adresse) | `router-id` setzen |

## Fehler/Ungenauigkeiten im Kurs

1. **S. 75, Darstellung:** Die Referenzbandbreite 10^11 erscheint als „1011“ (Formatierungsfehler, gemeint 10^11 bit/s = 100 Gbit/s).
2. **S. 79 (Discovery 9), Summary-Kosten:** Der Kurs nennt die niedrigsten Kosten der Teilnetze, ohne Einordnung. Das ist das IOS-Default-Verhalten (`compatible rfc1583`, RFC 1583 3.5). RFC 2328 (3.5) verlangt die höchsten Kosten; IOS mit `no compatible rfc1583`. Quelle: Cisco IOS OSPF Command Reference (`compatible rfc1583`), RFC 1583/2328.
3. **S. 79, Begriff:** Die ABR-Summary fasst laut Kurs „interarea (type 1 and type 2 LSAs)“-Routen zusammen. Typ 1/2 beschreiben **Intra-Area**-Routen; daraus entstehen am ABR Typ-3-Summaries.
4. **S. 80, RIB:** Ältere Geräte ohne AF-Unterstützung würden die IPv4-OSPFv3-Routen nicht „in der IPv6 RIB“ installieren – gemeint ist die **IPv4-RIB**. Außerdem bilden sie für die IPv4-AF schon keine Nachbarschaft (Cisco OSPFv3 Address Families Config Guide, RFC 5838).
5. **S. 81 (Discovery 10), Adressen:** Job Aid/Topologie nennen 172.16.14.x/24 für R1–R4, die Ausgaben zeigen /25.
6. **S. 76 (neu, Präzisierung):** Die Default-Route per Typ-5-LSA wird laut Kurs in alle Areas „außer Stub-Areas“ geflutet. Typ 5 erreicht auch **NSSA** und Totally-NSSA-Areas nicht (dort gibt es ggf. eine eigene Typ-7- oder Typ-3-Default-Route).
7. **Unsicher:** Die Kappung berechneter Kosten über 65535 auf 65535 ist nur durch den Kurs belegt. Der Wert in „Active(11)“ bei `show ip ospf` ist in der Cisco-Doku nicht beschrieben, in den Laborausgaben entspricht er der Summary-Metrik.

## Bilder

- `bilder/08-ospf-opt/01-kosten.svg` – Kostenformel, Wirkung der Referenzbandbreite (100 vs. 10000 vs. 100000) und die 16-Bit-Grenze von 65535.
- `bilder/08-ospf-opt/02-spf-baum.svg` – SPF-Baum aus Sicht von R1 mit Link-Kosten und der Ergebnistabelle (14/22/30) inklusive verworfener Alternativen.
- `bilder/08-ospf-opt/03-tuning-lab.svg` – Discovery 8: DIST mit zwei ABRs, Kosten nach auto-cost und ip ospf cost 500, E2-Routen mit forward metric.
- `bilder/08-ospf-opt/04-default.svg` – default-information originate mit und ohne always, ASBR-Rolle, E2-Default und Black-Hole-Fall.
- `bilder/08-ospf-opt/05-summary.svg` – ABR-Summary (area range, Typ 3) und ASBR-Summary (summary-address, Typ 5) mit Null0-Discard-Route und Kostenregel.
- `bilder/08-ospf-opt/06-filter.svg` – Wo welche Filter wirken: filter-list in/out, range not-advertise, summary-address not-advertise, distribute-list in (nur RIB).
- `bilder/08-ospf-opt/07-prefix-rm.svg` – Prefix-List-Logik mit ge/le-Beispielen und Route-Map-Auswertung (ODER in einer Zeile, UND über Zeilen, implizites deny).
- `bilder/08-ospf-opt/08-ospfv3.svg` – OSPFv2, klassisches OSPFv3 und OSPFv3 mit Address-Families im Vergleich, Instance-IDs und AF-Bit.
- `bilder/08-ospf-opt/09-v3-lab.svg` – Discovery 10: Topologie mit IPv4/IPv6-Präfixen, /60-Range in Area 1 und AF-spezifische Kosten (75 vs. 211).
