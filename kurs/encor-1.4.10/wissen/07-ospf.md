# Implementing OSPF

Quelle: ENCOR 1.4.10 Student Guide, Seiten 62–71 (Describe OSPF, OSPF Process, OSPF Neighbor Adjacencies, Building a Link-State Database, OSPF LSA Types, Compare Single-Area and Multiarea OSPF, OSPF Area Structure, OSPF Network Types, Discovery 7 „Implement Multiarea OSPF“, Summary)

Topics: ENCOR-3.2.a (Link-State vs. Distance-Vector), ENCOR-3.2.b (OSPFv2/v3: Neighbor Adjacency, Netztypen, Area-Typen, Summarization, Filtering – hier: Adjacency, Netztypen, Areas, LSAs)

Ergänzungen aus eigenem Fachwissen bzw. aus dem Prüfprotokoll (nicht im Kurs) sind mit *(Ergänzung)* markiert. Wo Kurs und RFC/IOS abweichen, siehe „Fehler/Ungenauigkeiten im Kurs“.

## Grundprinzip Link-State

- OSPF (Open Shortest Path First) ist ein offener Standard, ein Link-State-IGP und der klassische Nachfolger von RIP. Stärken: schnelle Konvergenz, Skalierbarkeit durch Areas.
- **Link** = ein Router-Interface. **State** = Beschreibung dieses Interfaces und seiner Beziehung zu Nachbarn (IP-Adresse, Maske, Netztyp, angeschlossene Router, Kosten).
- Arbeitsweise in fünf Schritten:
  1. Nachbarn per Hello-Paketen finden und Nachbarschaften (Adjacencies) bilden.
  2. Statt Routingtabellen werden **LSAs** (Link-State Advertisements) ausgetauscht.
  3. LSAs werden an **alle** OSPF-Router der Area geflutet (nicht nur an direkte Nachbarn).
  4. Alle LSAs zusammen bilden die **LSDB** (Link-State-Datenbank, topologische Datenbank). Innerhalb einer Area ist sie auf allen Routern identisch.
  5. Jeder Router rechnet mit dem **SPF-Algorithmus (Dijkstra)** mit sich selbst als Wurzel die kürzesten Wege und trägt sie in die Routingtabelle ein.
- LSAs werden **sofort bei einer Änderung** gesendet, zusätzlich periodisch aufgefrischt (**alle 30 Minuten**, LSRefreshTime).
- Hierarchie mit zwei Ebenen:
  - **Autonomous System (AS)** bzw. Routing-Domain: alle Netze unter gemeinsamer Verwaltung mit gemeinsamer Routing-Strategie.
  - **Areas**: zusammenhängende Gruppen von Netzen innerhalb des AS.
- **Area 0 = Backbone**: muss existieren und zusammenhängend sein. Jede andere Area hängt direkt an Area 0. Außerhalb des AS liegen externe Routing-Domains (z. B. EIGRP, Internet), die über einen ASBR angebunden werden.

## OSPF-Prozess und Router-ID

- Start: `router ospf <process-id>` (Router, L3-Switches, Firewalls). Die Prozess-ID ist **nur lokal** relevant. Nachbarn dürfen unterschiedliche IDs nutzen (z. B. R1 Prozess 1, R2 Prozess 10 → Nachbarschaft kommt trotzdem zustande).
- Mehrere Prozesse auf einem Router sind möglich (z. B. Zusammenschluss zweier Firmen mit je eigener OSPF-Domain, MPLS-Provider). Routen zwischen Prozessen werden **nur per Redistribution** ausgetauscht. Best Practice: Prozess-ID 1 (bzw. 2 für einen zweiten Prozess), das erleichtert Automatisierung.
- **Router-ID (RID)**: 32-Bit-Wert im IPv4-Format. Muss im AS eindeutig sein, muss aber keine gültige oder erreichbare Adresse sein. Kennzeichnet den Erzeuger jeder LSA.
- Auswahl beim Start des Prozesses:
  1. Manuell mit `router-id x.x.x.x` (Best Practice),
  2. sonst höchste IP-Adresse eines **aktiven Loopbacks**,
  3. sonst höchste IP-Adresse eines **aktiven physischen Interfaces**.
- Die RID ändert sich **nicht automatisch**, wenn später ein Interface mit höherer IP dazukommt. Ein nachträglich gesetzter `router-id`-Befehl wirkt erst nach `clear ip ospf process` oder Reload (IOS meldet „Reload or use clear ip ospf process command, for this to take effect“).
- Ein RID-Wechsel setzt **alle Adjazenzen** zurück und erzeugt neue LSAs. Ein ungeplanter Reload kann ohne feste RID eine andere RID ergeben, was Features mit RID-Bezug stören kann.
- Hat kein Interface im Zustand up/up eine IP-Adresse und ist keine RID konfiguriert, startet der Prozess nicht (*(Ergänzung)* Meldung `%OSPF-4-NORTRID`; Abhilfe: router-id setzen oder ein Interface mit IP hochbringen).
- Kollidiert ein konfigurierter router-id-Wert mit der RID eines anderen lokalen OSPF-Prozesses, wird der Befehl abgelehnt.
- Best Practice: Loopback anlegen und dieselbe Adresse als router-id setzen, z. B. fortlaufend `10.255.255.X/32`. Vorteile von Loopbacks: unabhängig vom Zustand physischer Medien, fester Quell-/Identitätspunkt für Syslog, SNMP, Telefonie-Server oder Sicherheitsrichtlinien.

```
interface Loopback0
 ip address 10.255.255.1 255.255.255.255
router ospf 1
 router-id 10.255.255.1
```

## Nachbarschaften (Hello-Protokoll)

- Hellos gehen auf allen OSPF-Interfaces an **224.0.0.5** (AllSPFRouters). OSPF läuft direkt in IP, **Protokollnummer 89**.
- Bidirektionale Kommunikation besteht, sobald ein Router seine **eigene RID in der Neighbor-Liste** des empfangenen Hellos sieht.
- Inhalt eines Hello-Pakets: Router-ID, Hello-/Dead-Intervall, Liste der Nachbarn, Area-ID, Router-Priority (8 Bit), DR- und BDR-Adresse, Authentifizierungsdaten, Stub-Area-Flag (Options-Feld).
- Muss bei beiden Nachbarn übereinstimmen: **Area-ID, Hello-/Dead-Intervall, Authentifizierung (Typ + Schlüssel), Subnetz und Maske** (Maske wird auf Point-to-Point-Links ignoriert *(Ergänzung, RFC 2328 10.5)*), **Stub-Flag**.
- Default-Timer auf Broadcast-/Point-to-Point-Netzen: Hello **10 s**, Dead **40 s** (4 × Hello). Dead-Intervall = Zeit ohne Hello, nach der der Nachbar als down gilt.
- **MTU-Mismatch**: Die Nachbarn sehen sich (Hellos klappen), aber der Datenbankaustausch per DBD scheitert. Der Router mit der kleineren MTU meldet (`debug ip ospf adj`) `Nbr <rid> has larger interface MTU` und verwirft das DBD; je nach IOS-Version meldet der Router mit der größeren MTU `Nbr <rid> has smaller interface MTU` (Cisco Tech Note 116119). Hänger in EXSTART/EXCHANGE. Abhilfe: MTU angleichen (*(Ergänzung)* notfalls `ip ospf mtu-ignore`).

Typische Logmeldungen *(Ergänzung, Cisco Tech Notes)*:
```
OSPF: Mismatched hello parameters from 172.16.12.2
OSPF: Dead R 40 C 30, Hello R 10 C 5         (R = received, C = configured)
OSPF: Rcv pkt from 172.16.12.2 : Mismatch Authentication type
%OSPF-4-ERRRCV: Received invalid packet: mismatch area ID
```

## Aufbau der LSDB – Pakettypen

| Typ | Paket | Aufgabe |
|---|---|---|
| 1 | Hello | Nachbarn entdecken und halten, DR/BDR-Wahl |
| 2 | DBD (Database Description) | Zusammenfassung der LSDB: nur LSA-Header |
| 3 | LSR (Link-State Request) | fehlende oder neuere LSAs gezielt anfordern |
| 4 | LSU (Link-State Update) | komplette LSAs übertragen, Flooding |
| 5 | LSAck | Bestätigung empfangener LSAs (enthält die LSA-Header) |

Ablauf nach der Nachbarfindung:
1. Beide Router tauschen DBDs. Jeder LSA-Header enthält u. a. Typ, Link-State-ID, Advertising Router und **Sequenznummer** (= Aktualität). Die Router handeln **Master/Slave** aus (höhere RID = Master). DBDs des Masters bestätigt der Slave, indem er die DBD-Sequenznummer zurückspiegelt.
2. Jeder vergleicht die Header mit der eigenen LSDB. Fehlt eine LSA oder ist die eigene älter, folgt ein **LSR**.
3. Der Nachbar antwortet mit einem **LSU** mit den vollständigen LSAs.
4. Der Empfänger bestätigt mit **LSAck**.

Da OSPF kein TCP nutzt, sorgt es selbst für Zuverlässigkeit: Unbestätigte LSAs werden nach dem Retransmit-Intervall (Default **5 s**) erneut gesendet. *(Ergänzung)* Bestätigungen können gebündelt (delayed ack) oder implizit erfolgen (RFC 2328 13.5).

**OSPF-Paket-Header** (für alle fünf Typen gleich, direkt nach dem IP-Header mit Protokoll 89):

| Feld | Bedeutung |
|---|---|
| Version | 2 = OSPFv2 (IPv4), 3 = OSPFv3 (IPv6, mit Address-Families auch IPv4) |
| Type | Pakettyp 1–5 |
| Packet Length | Länge in Byte |
| Router ID | RID des Absenders |
| Area ID | Area, aus der das Paket stammt |
| Checksum | Fehlererkennung |
| Authentication Type | 0 none, 1 Klartext, 2 MD5 (kryptografisch) |
| Authentication | Auth-Daten |
| Data | paketspezifischer Inhalt |

*(Ergänzung)* Das ist der OSPFv2-Header (24 Byte). Der OSPFv3-Header (16 Byte, RFC 5340 A.3.1) hat keine Authentifizierungsfelder, sondern eine **Instance ID**; Authentifizierung läuft dort über IPsec bzw. den Authentication Trailer (RFC 7166).

## Neighbor-States

| State | Bedeutung | Typische Hänger |
|---|---|---|
| Down | noch kein Hello empfangen | Interface/IP/Area falsch |
| Attempt | nur NBMA: Unicast-Hellos an statischen Nachbarn | – |
| Init | Hello empfangen, eigene RID fehlt darin | einseitige Kommunikation (ACL, Filter) |
| 2-Way | eigene RID im Hello → bidirektional; DR/BDR-Wahl am Ende dieser Phase | zwischen DROTHERs normaler Endzustand |
| ExStart | Master/Slave und Start-Sequenznummer aushandeln | MTU-Mismatch |
| Exchange | DBDs tauschen | MTU-Mismatch |
| Loading | LSR/LSU; Request-List und Retransmission-List | beschädigte LSAs |
| Full | LSDB synchron, volle Adjazenz | – |

Debug-Beispiel (`debug ip ospf adj`, gekürzt, eigene Darstellung):
```
OSPF-1 ADJ Et0/1: 2 Way Communication to 5.5.5.5, state 2WAY
OSPF-1 ADJ Et0/1: Backup seen event before WAIT timer
OSPF-1 ADJ Et0/1: DR/BDR election
OSPF-1 ADJ Et0/1: Send DBD to 5.5.5.5 seq 0x1A2B opt 0x52 flag 0x7 len 32
OSPF-1 ADJ Et0/1: NBR Negotiation Done. We are the SLAVE
OSPF-1 ADJ Et0/1: Send LS REQ to 5.5.5.5 length 36
OSPF-1 ADJ Et0/1: Rcv LS UPD from 5.5.5.5 length 140
OSPF-1 ADJ Et0/1: Synchronized with 5.5.5.5, state FULL
```
DBD-Flag 0x7 = I (Init) + M (More) + MS (Master). BackupSeen: Ein BDR wurde schon gesehen, der Router muss nicht die volle Wait-Zeit (= Dead-Intervall) abwarten.

## LSA-Typen

Jede LSA hat einen **20-Byte-LSA-Header**; ein Feld davon ist die **Link-State-ID (LSID)**, deren Bedeutung vom Typ abhängt.

| Typ | Name | Erzeuger | Flooding-Bereich | Link-State-ID | Route |
|---|---|---|---|---|---|
| 1 | Router LSA | jeder Router, je Area | nur eigene Area | RID des Erzeugers | O |
| 2 | Network LSA | DR eines Multiaccess-Segments | nur eigene Area | Interface-IP des DR | O |
| 3 | Summary LSA | ABR | in andere Areas | Zielnetz | O IA |
| 4 | ASBR Summary LSA | ABR | Areas, in denen der ASBR nicht liegt | RID des ASBR | – |
| 5 | AS External LSA | ASBR | ganze Domain außer Stub/NSSA | externes Netz | O E1/E2 |
| 6 | Multicast OSPF | – (in IOS nicht unterstützt) | – | – | – |
| 7 | NSSA External | ASBR in einer NSSA | nur die NSSA (ABR übersetzt in Typ 5) | externes Netz | O N1/N2 |
| 8, 9 | OSPFv3: Link-LSA, Intra-Area-Prefix-LSA | | | | |
| 9–11 | OSPFv2: Opaque (link-, area-, AS-weit) | | | | |

- Typ 1 und 2 beschreiben die Topologie einer Area und verlassen sie nie. Der ABR übersetzt das Wissen in Typ-3-LSAs für andere Areas. Summarization ist **nicht** Default, sie muss auf dem ABR konfiguriert werden.
- Typ 4 braucht man, damit Router in anderen Areas den ASBR (Erzeuger der Typ-5-LSAs) erreichen: Der ABR erzeugt sie mit der RID des ASBR.
- Auf reinen Point-to-Point-Links gibt es keinen DR, also auch keine Typ-2-LSA.

## Single-Area vs. Multiarea

| | Single-Area | Multiarea |
|---|---|---|
| LSAs pro Router | viele (alle Typ 1/2 der gesamten Domain) | nur die eigene Area im Detail |
| SPF | jede Änderung → SPF auf allen Routern | SPF-Berechnung auf die Area begrenzt |
| Routingtabelle | groß | kleiner, wenn am ABR zusammengefasst wird |
| Flooding | überall | Typ 1/2 bleiben in der Area |

- Aus Konfigurationssicht gibt es Router mit **Single-Area-Konfiguration** (interne Router, Backbone-Router, ASBR in genau einer Area) und mit **Multiarea-Konfiguration** (ABRs, ASBRs in mehreren Areas).
- Multiarea verlangt mehr Planungs- und Troubleshooting-Wissen.

## Area-Struktur und Router-Rollen

- Zweistufig: **Backbone (Area 0)** transportiert IP-Pakete schnell zwischen den Areas. **Normale (Nicht-Backbone-)Areas** gruppieren Nutzer/Ressourcen, meist nach Funktion oder Standort.
- Zwei Nicht-Backbone-Areas dürfen nicht direkt miteinander Routen austauschen. **Inter-Area-Verkehr läuft immer über Area 0** (z. B. Area 1 → Area 0 → Area 2).
- **Area-ID**: 32 Bit, dezimal oder gepunktet, beide Formen gleichwertig. Area 0 = 0.0.0.0, Area 14 = 0.0.0.14, Area 300 = 0.0.1.44 (300 = 1 × 256 + 44).
- Größe: so wenig Router pro Area wie sinnvoll, Areas mit instabilen Links eher klein. Ein Router sollte in **höchstens drei Areas** sein, ein ABR idealerweise in zwei (Area 0 + eine weitere).

| Rolle | Definition |
|---|---|
| Backbone-Router | mindestens ein Interface in Area 0 |
| Interner Router | alle Interfaces in einer Area; nur eine LSDB |
| ABR | Interfaces in mehreren Areas, eine davon Area 0; je Area eine LSDB; trennt Flooding-Bereiche, Ort der Inter-Area-Summarization, grenzt Spezial-Areas ab; zählt auch als Backbone-Router |
| ASBR | bringt externe Routen ins OSPF-AS: Redistribution (anderes Protokoll, statische Routen, anderes OSPF-AS) oder `default-information originate` |

- Rollen kombinierbar (ABR + ASBR). Auch Firewalls (z. B. ASA) können ASBR sein und eine Internet-Default-Route ins AS bringen.
- Interne Router einer Nicht-Backbone-Area kennen andere Areas nur als **O IA**-Routen und schicken den Verkehr zum nächsten ABR. Bei zwei gleich teuren ABRs ergibt sich ECMP.

Konfigurationshinweise:
```
router ospf 1
 network 0.0.0.0 255.255.255.255 area 2   ! alle Interfaces in Area 2 (interner Router)
 passive-interface GigabitEthernet0/1      ! keine Hellos, Netz wird weiter annonciert
```

## OSPF-Netztypen

| Netztyp | DR/BDR | Hello/Dead | Nachbarn | mehr als 2 Router | Default auf |
|---|---|---|---|---|---|
| point-to-point | nein | 10/40 | dynamisch (Multicast) | nein | Serial (HDLC/PPP), P2P-Subinterfaces |
| broadcast | ja | 10/40 | dynamisch | ja | Ethernet |
| non-broadcast (NBMA) | ja | 30/120 | statisch (`neighbor`), Unicast | ja | Frame Relay physisch/Multipoint |
| point-to-multipoint | nein | 30/120 | dynamisch | ja | – (manuell) |
| point-to-multipoint non-broadcast | nein | 30/120 | statisch | ja | – (Cisco-Erweiterung) |
| loopback | – | – | – | – | Loopback |

- Ändern mit `ip ospf network <typ>` im Interface.
- Point-to-Multipoint behandelt das Segment als Sammlung von P2P-Links; jede Interface-Adresse erscheint bei den Nachbarn als /32-Host-Route.
- Loopbacks werden standardmäßig als **/32** annonciert, egal welche Maske konfiguriert ist. Mit `ip ospf network point-to-point` am Loopback wird die echte Maske (z. B. /24) annonciert.
- Nachbarn mit unterschiedlichen Netztypen scheitern oft schon an den Timern (10 vs. 30 s).
- Wird nur das Hello-Intervall geändert, setzt IOS das Dead-Intervall automatisch auf das Vierfache.

## DR/BDR

- Auf Broadcast- und NBMA-Segmenten würde ein Full Mesh **n(n−1)/2** Adjazenzen ergeben, und jeder Router würde alle Adjazenzen annoncieren. Lösung: ein **Designated Router (DR)** als zentraler Punkt plus **Backup DR (BDR)**.
- Alle Router bilden FULL nur mit DR und BDR. Zwischen zwei DROTHERs bleibt der Zustand **2-WAY** (normal, kein Fehler). Beispiel n = 5: 4 + 3 = 7 Adjazenzen statt 10.
- Flooding: DROTHERs senden Updates an **224.0.0.6** (AllDRouters = DR + BDR), der DR flutet sie an **224.0.0.5** an alle. Der BDR hört mit, flutet aber nicht; er übernimmt bei Ausfall. Auf NBMA läuft das per Unicast.
- Wahl: höchste **Priority** (0–255, Default 1), bei Gleichstand höchste **RID**. Priority 0 = nie DR/BDR. Gesetzt **pro Interface** mit `ip ospf priority <0-255>`.
- Die Wahl ist **nicht präemptiv**: Ein später startender Router mit höherer Priority/RID wird nicht automatisch DR. Fällt der DR aus, wird der BDR zum DR und ein neuer BDR wird gewählt. Neuwahl erzwingen: `clear ip ospf process` (auf den betroffenen Routern).
- Der DR erzeugt die Typ-2-LSA des Segments.

## Discovery 7: Multiarea OSPF (Labwissen)

Topologie (eigene Zusammenfassung):
- R1 = ABR mit RID später 1.1.1.1.
  - Et0/1 172.16.145.1/29, **Area 0**, gemeinsames Ethernet mit R4 (.4, RID 4.4.4.4, Lo0 192.168.4.1/24) und R5 (.5, RID 5.5.5.5). R4/R5 sind vorkonfiguriert.
  - S2/0 172.16.12.1/30, **Area 1**, serielle P2P-Verbindung zu R2 (S0/0 .2, Lo0 192.168.2.1/24).
  - Et0/0 172.16.13.1/30, **Area 2**, Ethernet-WAN zu R3 (.2, Lo0 192.168.3.1/24).

Konfiguration:
```
R1(config)# router ospf 1
R1(config-router)# network 172.16.145.0 0.0.0.7 area 0
R1(config-router)# network 172.16.12.0 0.0.0.3 area 1
R1(config-router)# network 172.16.13.0 0.0.0.3 area 2

R2(config)# router ospf 2
R2(config-router)# network 172.16.12.0 0.0.0.3 area 1
R2(config-router)# network 192.168.2.0 0.0.0.255 area 1

R3(config)# router ospf 3
R3(config-router)# network 172.16.13.2 0.0.0.0 area 2     ! genau ein Interface
R3(config)# interface Loopback0
R3(config-if)# ip ospf 3 area 2                           ! Interface-Methode
```
- Logik des network-Befehls: Interface-IP und network-Adresse werden jeweils mit der Wildcard ODER-verknüpft; sind die Ergebnisse gleich, gehört das Interface in die Area. Ein Interface gehört nur zu einer Area. *(Ergänzung)* `ip ospf <pid> area <a>` hat Vorrang vor network-Befehlen.
- Ohne Loopback und ohne router-id wählte R1 zunächst 172.16.145.1 als RID (höchste Interface-IP). `router-id 1.1.1.1` wirkt erst nach `clear ip ospf process`.

Wichtige show-Befehle und was man darin sieht:
```
R1# show ip protocols
 Routing Protocol is "ospf 1"
  Router ID 1.1.1.1
  It is an area border router
  Number of areas in this router is 3. 3 normal 0 stub 0 nssa
  Maximum path: 4
  Routing Information Sources:  Gateway  Distance  Last Update
  Distance: (default is 110)

R1# show ip ospf neighbor
Neighbor ID  Pri  State        Dead Time  Address         Interface
4.4.4.4        1  FULL/BDR     00:00:35   172.16.145.4    Ethernet0/1
5.5.5.5        1  FULL/DR      00:00:38   172.16.145.5    Ethernet0/1
2.2.2.2        0  FULL/  -     00:00:33   172.16.12.2     Serial2/0
```
- `FULL/ -` = Point-to-Point (keine DR-Wahl, Priority 0 in der Ausgabe). Dead Time zählt rückwärts und springt bei jedem Hello zurück.
- `show ip ospf interface <if>`: Area, „Attached via Network Statement“ bzw. „Attached via Interface Enable“, Network Type und Cost (LOOPBACK 1, POINT_TO_POINT 64 auf T1-Serial, BROADCAST 10 auf 10-Mbit-Ethernet), State (DR/BDR/DROTHER/POINT_TO_POINT), Priority, DR/BDR, „Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5“, Neighbor Count / Adjacent neighbor count.
- `show ip ospf interface brief`: Kurzübersicht je Interface (Area, Cost, State, Nachbarn).
- `show ip route ospf` auf R5:
```
O IA  172.16.12.0/30 [110/74] via 172.16.145.1     ! 10 + 64
O IA  172.16.13.0/30 [110/20] via 172.16.145.1     ! 10 + 10
O IA  192.168.2.1/32 [110/75] via 172.16.145.1     ! 10 + 64 + 1, Loopback als /32
O IA  192.168.3.1/32 [110/21] via 172.16.145.1
O     192.168.4.0/24 [110/11] via 172.16.145.4     ! R4-Loopback mit p2p-Netztyp
```
- `show ip ospf route`: getrennte Listen für Intra-Area- und Inter-Area-Routen sowie die Router-Path-List (z. B. ABR 1.1.1.1 mit Kosten).
- *(Ergänzung)* `show ip ospf border-routers`: zeigt erreichbare ABRs/ASBRs.

DR/BDR im Lab (Segment 172.16.145.0/29):
- Ausgangslage: alle Priority 1 → R5 (höchste RID) DR, R4 BDR, R1 DROTHER.
- R5 Et0/0 shutdown → nach Ablauf des Dead-Intervalls (40 s) wird R4 DR, R1 BDR. R5 kommt zurück → nur DROTHER (nicht präemptiv).
- R1 bekommt Priority 100, dann `clear ip ospf process` auf R4 (dem DR): R1 wird DR, weil er als BDR nachrückt, nicht direkt wegen der Priority. Neuer BDR wird R5.
- R4 und R5 mit Priority 0 → R1 DR, R4 und R5 DROTHER, zwischen R4 und R5 bleibt 2WAY/DROTHER.

MTU-Mismatch im Lab: R3 `ip mtu 1400`, R1 1500. R3 meldet „Nbr 1.1.1.1 has larger interface MTU“ und bleibt in EXSTART, R1 pendelt zwischen INIT und EXCHANGE. Fix: MTU angleichen.

Timer im Lab: `ip ospf hello-interval 5` und `ip ospf dead-interval 30` nur auf R1 (S2/0) → Nachbarschaft zu R2 fällt nach Ablauf des Dead-Timers („Dead timer expired“), `debug ip ospf hello` zeigt die Mismatched-Hello-Meldung. Nach gleicher Konfiguration auf R2 wieder FULL. Defaults: Broadcast/P2P 10/40, NBMA/P2MP 30/120.

## Troubleshooting-Checkliste

| Symptom | Ursache prüfen | Befehle |
|---|---|---|
| kein Nachbar | Area-ID, Timer, Auth, Subnetz/Maske, Stub-Flag, passive-interface, ACL auf 224.0.0.5 | `show ip ospf interface`, `debug ip ospf hello` |
| Hänger INIT | einseitiger Empfang | ACLs, `debug ip ospf adj` |
| Hänger EXSTART/EXCHANGE | MTU-Mismatch | `show interface`, Logmeldung „larger interface MTU“ |
| 2WAY zwischen DROTHERs | normal | – |
| falscher DR | Wahl nicht präemptiv, Priority je Interface | `show ip ospf neighbor`, `clear ip ospf process` |
| Router-ID doppelt | Adjazenz-/LSA-Probleme, Log „Detected router with duplicate router ID“ *(Ergänzung)* | `show ip ospf`, router-id setzen |
| Loopback als /32 | Netztyp LOOPBACK | `ip ospf network point-to-point` |

## Fehler/Ungenauigkeiten im Kurs

1. **S. 65, LSAck:** Der Kurs nennt die LSAck-Pakete inhaltslos und behauptet, jede LSA werde explizit bestätigt. Laut RFC 2328 A.3.6 enthält ein LSAck eine Liste von **LSA-Headern** der bestätigten LSAs; Bestätigungen können gebündelt oder implizit erfolgen (RFC 2328 13.5).
2. **S. 65, DBD/LSA-Header:** Der Kurs zählt die Kosten des Links zum LSA-Header. Der 20-Byte-LSA-Header enthält LS Age, Options, LS Type, Link-State-ID, Advertising Router, Sequenznummer, Checksum und Length, **keine Kosten** (RFC 2328 A.4.1). Kosten stehen im LSA-Body.
3. **S. 66, LSA-Typen 8/9:** Der Kurs ordnet 8/9 nur OSPFv3 zu. In OSPFv2 ist Typ 9 die link-lokale Opaque-LSA (9/10/11 Opaque, RFC 5250); Typ 8 (External Attributes) wird in OSPFv2 nicht genutzt.
4. **S. 70, Anzahl Adjazenzen:** „wächst exponentiell“ ist falsch, sie wächst **quadratisch**: n(n−1)/2.
5. **S. 70, Priority:** Der Kurs spricht davon, die OSPF-Priority „global“ zu setzen. `ip ospf priority` ist ein **Interface**-Befehl und gilt je Segment.
6. **S. 70, Ausgaben:** Tippfehler „FULL/BR“ statt FULL/BDR. Auf dem R1–R3-Link erscheint R3 später als DR, obwohl das Debug davor R1 als DR und R3 als BDR zeigt. In Task 5 ist R1 wieder DROTHER mit Priority 1 und R5 DR/R4 BDR – passt nicht zum vorher konfigurierten Stand (Priority 100/0).
7. **S. 64, MTU-Abbildung (neu):** Die Logzeilen nennen den Nachbarn 192.168.1.2, die Topologie nutzt aber 10.1.1.0/24. Die Meldung „has smaller interface MTU“ auf dem Router mit der größeren MTU ist dagegen korrekt: Cisco Tech Note 116119 zeigt beide Varianten („Nbr … has larger interface MTU“ auf dem Router mit der kleineren MTU, „Nbr … has smaller interface MTU“ auf dem mit der größeren). Entscheidend für den Hänger ist, dass der Router mit der kleineren MTU die DBDs verwirft (RFC 2328 10.6).
8. **S. 68, ABR-Eigenschaften (neu, Präzisierung):** Der Kurs schreibt dem ABR die Festlegung einer Spezial-Area (z. B. Stub) zu. Der Area-Typ muss auf **allen** Routern der Area konfiguriert werden, weil das Stub-Flag im Hello übereinstimmen muss; nur `no-summary` gehört allein auf den ABR (Cisco OSPF Command Reference, `area stub`).
9. **Lücke:** Area-Typen (Stub, Totally Stubby, NSSA, Totally NSSA) behandelt der Kurs kaum (nur Stub-Flag und Typ 7). Für die Prüfung *(Ergänzung)*: Stub und NSSA blocken Typ 4 und 5; Stub/Totally Stubby erzeugen am ABR automatisch eine Default-Route; eine NSSA bekommt unter Cisco IOS nur mit `area X nssa default-information-originate` eine Default-Route (Totally NSSA mit `no-summary` automatisch). RFC 3101 (Abschn. 2.4) verlangt dagegen, dass NSSA-ABRs immer einen Default (Typ 7, bei no-summary Typ 3) in die NSSA erzeugen; maßgeblich für ENCOR ist das Cisco-Verhalten.
10. **Summary-Kosten (Querverweis 08-ospf-opt):** Cisco IOS ist per Default `compatible rfc1583` und gibt einer Summary die **niedrigsten** Kosten der Teilnetze (RFC 1583 3.5). RFC 2328 verlangt die **höchsten**; in IOS mit `no compatible rfc1583`.

## Bilder

- `bilder/07-ospf/01-ls-ablauf.svg` – Link-State-Ablauf in fünf Schritten (Hello → LSA-Flooding → LSDB → SPF → Routingtabelle) und die AS/Area-Hierarchie.
- `bilder/07-ospf/02-rid-wahl.svg` – Prozess-ID nur lokal (Prozess 1 und 10 werden Nachbarn) und die Reihenfolge der Router-ID-Wahl mit Hinweis auf clear ip ospf process.
- `bilder/07-ospf/03-hello.svg` – Felder des Hello-Pakets, die Felder, die übereinstimmen müssen, und der MTU-Fall (Hello ok, DBD scheitert).
- `bilder/07-ospf/04-dbd-ablauf.svg` – Datenbanksynchronisation DBD → LSR → LSU → LSAck plus OSPF-Paket-Header mit Protokoll 89.
- `bilder/07-ospf/05-states.svg` – Neighbor-State-Maschine von Down bis Full mit typischen Hängern (INIT, EXSTART/EXCHANGE, 2-WAY normal).
- `bilder/07-ospf/06-lsa-typen.svg` – Welche LSA-Typen wo entstehen und wie weit sie geflutet werden (ASBR in Area 1, ABR, Area 0).
- `bilder/07-ospf/07-rollen.svg` – Router-Rollen (Backbone, intern, ABR, ASBR) in einem Multiarea-Design mit Inter-Area-Verkehr über Area 0.
- `bilder/07-ospf/08-dr-bdr.svg` – Physisch vs. Adjazenz vs. Synchronisation auf einem Multiaccess-Segment, Multicast-Adressen und DR-Wahl nach Priority/RID.
- `bilder/07-ospf/09-lab-topo.svg` – Discovery 7: R1 als ABR für Area 0/1/2 und die Kostenrechnung der O-IA-Routen auf R5.
