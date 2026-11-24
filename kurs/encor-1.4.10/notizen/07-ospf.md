# Notizen Kapitel "Implementing OSPF" (Kursseiten 62–71)

## 62 Describe OSPF
- Link-State-IGP, offener Standard, Nachfolger von RIP: schnelle Konvergenz, skaliert.
- Link = Router-Interface, State = Beschreibung (IP, Maske, Netztyp, Nachbarn).
- Ablauf: Hellos -> Nachbarschaft; LSAs statt Routing-Tabellen; LSAs an alle Router der Area geflutet; aus allen LSAs = LSDB; SPF (Dijkstra) -> kürzeste Pfade in die Routing-Tabelle.
- LSAs sofort bei Änderung, zusätzlich periodisch alle 30 min.
- Alle Router einer Area haben identische LSDB.
- Hierarchie: AS (Domain, gemeinsame Verwaltung) -> Areas (zusammenhängende Netze). Backbone = Area 0, muss zusammenhängend sein; alle anderen Areas hängen an Area 0.

## 63 OSPF Process / Router-ID
- `router ospf <process-id>`: Prozess-ID nur lokal relevant, Nachbarn dürfen verschiedene IDs haben. Mehrere Prozesse möglich (Fusion, MPLS-SP), Austausch nur per Redistribution. Best Practice: Prozess 1.
- Router-ID: 32 Bit, IP-Format, muss nicht erreichbar/gültig sein, muss im AS eindeutig sein.
- Wahl beim Prozessstart: 1. `router-id x.x.x.x`, 2. höchste IP aktiver Loopback, 3. höchste IP aktiver physischer Interfaces.
- RID ändert sich nicht automatisch (neues höheres Interface) – erst nach Reload/`clear ip ospf process`. Unerwartete RID-Änderung kann Features stören.
- Best Practice: Loopback anlegen, gleiche IP als router-id; sequentielle /32-Loopbacks (z. B. 10.255.255.X).

## 64 Neighbor Adjacencies
- Hellos an 224.0.0.5 auf allen OSPF-Interfaces. Bidirektional, wenn eigene RID in Neighbor-Liste des empfangenen Hellos.
- Muss passen: Area-ID, Hello/Dead, Authentifizierung, gleiches Subnetz + Maske, Stub-Flag.
- Hello-Inhalt: RID, Hello/Dead, Neighbors, Area-ID, Priority (8 Bit), DR/BDR-IP, Auth-Daten, Stub-Flag.
- Default Multiaccess: Hello 10 s, Dead 4x = 40 s.
- MTU-Mismatch: Nachbar wird erkannt, aber DB-Austausch scheitert (DBD), Logmeldungen.

## 65 LSDB-Aufbau
- Pakettypen: 1 Hello, 2 DBD (LSA-Header), 3 LSR, 4 LSU (komplette LSAs, Flooding), 5 LSAck.
- DBD-Austausch mit Master/Slave; Slave bestätigt durch Echo der DBD-Sequenznummer. Sequenznummer der LSA = Aktualität.
- IP-Protokoll 89, kein TCP/UDP -> eigene Bestätigung (LSAck).
- Header: Version (2 = IPv4, 3 = OSPFv3), Typ, Länge, RID, Area-ID, Checksum, Auth-Typ (none/cleartext/MD5), Auth.
- Kursfehler: LSAck sei "leer" (enthält real die LSA-Header der bestätigten LSAs); LSA-Header enthalte "cost of the link" (stimmt so nicht).

## 66 LSA-Typen
- LSA-Header 20 Byte, Feld Link-State-ID.
- Typ 1 Router LSA: jeder Router pro Area, nur in der Area; LSID = RID des Erzeugers.
- Typ 2 Network LSA: DR auf Multiaccess, in der Area; LSID = Interface-IP des DR.
- Typ 3 Summary LSA: ABR beschreibt Netze einer Area in einer anderen; LSID = Zielnetz. Summarization nicht per Default.
- Typ 4 ASBR Summary: ABR, sagt wie man zum ASBR kommt; LSID = RID des ASBR.
- Typ 5 AS External: ASBR, überall außer Spezial-Areas; LSID = externes Netz.
- Typ 6 MOSPF, Typ 7 NSSA-External, Typ 8/9 OSPFv3 (Link-LSA, Intra-Area-Prefix), 10/11 Opaque.

## 67/68 Single- vs Multiarea, Area-Struktur
- Single-Area: viele LSAs pro Router, große Tabellen, jede Änderung flutet überall.
- Multiarea: SPF auf Area begrenzt, Flooding nur innerhalb Area, kleinere Tabellen mit Summarization (nicht automatisch, ABR).
- Direkte Verbindung zwischen zwei Nicht-Backbone-Areas nicht erlaubt; Interarea-Verkehr über Area 0.
- Area-ID 32 Bit, dezimal oder dotted (Area 300 = 0.0.1.44).
- Rollen: Backbone-Router (mind. ein Interface in Area 0), Internal (alle Interfaces in einer Area), ABR (mehrere Areas, LSDB je Area, Summarization, Spezialarea-Festlegung, muss an Area 0), ASBR (redistribute oder default-information originate). ABR + ASBR gleichzeitig möglich.
- Best Practice: Router höchstens in 3 Areas, ABR idealerweise 2.
- `network 0.0.0.0 255.255.255.255 area X` = alle Interfaces; passive-interface unterdrückt Hellos, Netz wird weiter annonciert.
- Interarea-Routen: O IA.

## 69 Netztypen
| Typ | DR/BDR | Hello | dyn. Nachbarn | >2 Router |
|---|---|---|---|---|
| point-to-point | nein | 10 | ja | nein |
| broadcast | ja | 10 | ja | ja |
| nonbroadcast | ja | 30 | nein | ja |
| point-to-multipoint | nein | 30 | ja | ja |
| p2mp nonbroadcast | nein | 30 | nein | ja |
| loopback | – | – | – | – |
- Serial/P2P-Subinterfaces: p2p; Ethernet: broadcast; Frame Relay physisch/multipoint: nonbroadcast; P2MP: Interface-IPs als /32; Loopback als /32 annonciert.
- `ip ospf network <typ>`.

## 70 Discovery 7 (Multiarea)
- Topologie: R1 = ABR; Et0/1 172.16.145.1/29 Area 0 (R4 .4, R5 .5, preconfigured RID 4.4.4.4/5.5.5.5), S2/0 172.16.12.1/30 Area 1 zu R2 (S0/0 .2, Lo0 192.168.2.1/24), Et0/0 172.16.13.1/30 Area 2 zu R3 (.2, Lo0 192.168.3.1/24). R4 Lo0 192.168.4.1/24.
- R1: router ospf 1, network 172.16.145.0 0.0.0.7 area 0 / 172.16.12.0 0.0.0.3 area 1 / 172.16.13.0 0.0.0.3 area 2. R2: router ospf 2. R3: router ospf 3, `network 172.16.13.2 0.0.0.0 area 2`, Lo0 per `ip ospf 3 area 2`.
- network-Befehl: OR von Wildcard mit Interface-IP und mit network-IP, Vergleich. Interface nur in einer Area.
- router-id nachträglich -> Meldung "Reload or use clear ip ospf process". R1 hatte zunächst RID 172.16.145.1 (höchste Interface-IP, kein Loopback).
- Ohne eine IP auf up/up-Interface startet OSPF nicht (Fehler), Retry bei neuer IP/Interface up. router-id-Konflikt mit anderem lokalem Prozess -> Befehl schlägt fehl.
- RID-Wechsel = Reset aller Adjazenzen, neue LSAs.
- show ip protocols: Router ID, "Number of areas ... normal/stub/nssa", Maximum path 4, Distance 110, Routing Information Sources.
- show ip ospf neighbor: Neighbor ID, Pri, State (FULL/-, FULL/DR, FULL/BDR, FULL/DROTHER, 2WAY/DROTHER), Dead Time (Countdown), Address, Interface.
- show ip ospf interface: Area, "Attached via Network Statement" / "Interface Enable", Network Type (LOOPBACK Cost 1, POINT_TO_POINT Cost 64, BROADCAST Cost 10), State, Priority, DR/BDR, "Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5", Neighbor Count/Adjacent.
- R5 show ip route ospf: O IA 172.16.12.0/30 [110/74], 172.16.13.0/30 [110/20], 192.168.2.1/32 [110/75], 192.168.3.1/32 [110/21]; O 192.168.4.0/24 [110/11]. Loopback-Netze als /32 -> `ip ospf network point-to-point` am Loopback.
- show ip ospf route: Intra-/Inter-Area-Listen, Router-Path-List "i 1.1.1.1 [10] ... ABR, Area 0".
- Neighbor-States: Down, Init, 2-Way (DR/BDR-Wahl am Ende), ExStart (Master/Slave, initiale Seq), Exchange (DBD), Loading (LSR/LSU, Request-/Retransmission-List), Full.
- debug ip ospf adj: "Backup seen event before WAIT timer", "Elect BDR/DR", "Send DBD ... flag 0x7", "NBR Negotiation Done. We are the MASTER" (höhere RID = Master), "Send LS REQ", "Rcv LS UPD", "Synchronized ... state FULL".
- DR/BDR: auf broadcast + NBMA; DROTHER -> DR/BDR an 224.0.0.6, DR -> alle an 224.0.0.5; NBMA unicast. Höchste Priority, dann höchste RID. Priority 0–255, Default 1, 0 = nie DR/BDR. Nicht präemptiv. DR-Ausfall: BDR wird DR, neue BDR-Wahl. BDR hört mit, flutet nicht.
- Lab: R5 DR, R4 BDR, R1 DROTHER; R5 shut -> nach Dead 40 s R4 DR, R1 BDR; R5 zurück -> DROTHER. R1 priority 100 + clear auf R4 -> R1 DR (wegen BDR-Promotion, nicht wegen Priority), R5 BDR. R4/R5 priority 0 -> R1 DR, beide DROTHER, untereinander 2WAY.
- MTU: R3 ip mtu 1400 vs 1500 -> R3 "Nbr 1.1.1.1 has larger interface MTU", R3 EXSTART, R1 pendelt INIT -> EXCHANGE. Fix: MTU angleichen.
- Timer: broadcast/p2p 10/40, sonst 30/120; nur Hello geändert -> Dead = 4x. `ip ospf hello-interval 5`, `ip ospf dead-interval 30` nur auf R1 -> "Dead timer expired", nach Angleichen auf R2 FULL. `debug ip ospf hello`.
- show ip ospf neighbor detail auf p2p: DR/BDR 0.0.0.0, Priority 0.

## Kursfehler / Ungenauigkeiten
- S. 65: LSAck "Empty" – falsch, enthält LSA-Header. "cost of the link" im LSA-Header – falsch.
- S. 66: Typ 9 in OSPFv2 ist Opaque link-local; Kurs nennt 8/9 nur für OSPFv3.
- S. 70: "number of adjacencies increases exponentially" – real quadratisch (n(n-1)/2).
- S. 70: R1-Ausgabe "FULL/BR" (Tippfehler), R3 erscheint später als DR auf R1–R3-Link, obwohl Debug R1 = DR, R3 = BDR zeigt (inkonsistent). Task 5 zeigt R1 wieder als DROTHER mit Priority 1 und R5 DR/R4 BDR – passt nicht zu vorherigen Schritten.
- S. 70: "Setting the OSPF interface priority globally" – Priority ist per Interface.
- Area-Typen (Stub/Totally Stubby/NSSA) im Kurs kaum behandelt (nur Stub-Flag, Typ 7).
