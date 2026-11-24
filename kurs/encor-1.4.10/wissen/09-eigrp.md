# Explaining EIGRP

Quelle: ENCOR 1.4.10 Student Guide, Seiten 86–95 (EIGRP Features, EIGRP Reliable Transport, Establishing EIGRP Neighbor Adjacency, EIGRP Metrics, EIGRP Path Selection, Explore EIGRP Load Balancing and Sharing, EIGRP for IPv6, Compare EIGRP and OSPF Routing Protocols, Configure EIGRP, Summary)

Topics: ENCOR-3.2.a (EIGRP vs. OSPF: Advanced Distance Vector vs. Link-State, Load Balancing, Pfadwahl, Metriken), Bezug zu ENCOR-3.1.a (Administrative Distance)

Ergänzungen aus eigenem Fachwissen bzw. aus dem Prüfprotokoll `research_notes/Kapitelpruefung/09-eigrp.md` (nicht im Kurs) sind mit *(Ergänzung)* markiert. OSPF-Grundlagen stehen in `wissen/07-ospf.md` und `wissen/08-ospf-opt.md`.

## Überblick und Eigenschaften

- **EIGRP** (Enhanced Interior Gateway Routing Protocol) ist eine Cisco-Entwicklung. 2013 wurde es weitgehend offengelegt (zunächst als Internet-Draft), seit 2016 beschrieben im **informational RFC 7868**. Die **Stub-Funktion** blieb proprietär; Cisco steuert die Weiterentwicklung.
- Einordnung: **Advanced Distance Vector**. Grundprinzip Distance Vector: Ein Router kennt das Netz nur so, wie es ihm die **direkten Nachbarn** melden (keine vollständige Topologiekarte wie bei OSPF/IS-IS). Von Link-State übernommen: **Hello-Protokoll** zur Nachbarerkennung und **nur Teil-Updates** bei Änderungen.
- Merkmale:
  - **Schnelle Konvergenz** durch **DUAL** (Diffusing Update Algorithm). DUAL garantiert schleifenfreie Pfade und hält **Backup-Pfade** (Feasible Successors) vorab bereit. Fällt der Primärpfad aus, wird der beste Backup sofort installiert. Gibt es keinen, fragt der Router seine Nachbarn (Query).
  - **Load Balancing** über gleich teure **und** ungleich teure Pfade (einzigartig unter den gängigen IGPs).
  - **Classless**: Maske pro Präfix → VLSM und diskontinuierliche Netze möglich.
  - **Multi-Address-Family**: früher auch IPX/AppleTalk (heute veraltet), heute IPv4 und IPv6 über **protokollabhängige Module (PDMs)**; außerdem Verteilung von Dial-Plan-Informationen (Cisco Unified CM) und Performance-Routing über **SAF** (Service Advertisement Framework).
  - **Bandbreitensparend**: keine periodischen Updates. Updates sind **partial** (enthalten nur die Änderung) und **bounded** (gehen nur an Router, die die Änderung betrifft).
  - Multicast **224.0.0.10** (IPv6: **FF02::A**) und Unicast, **kein Broadcast** → Endgeräte werden nicht belastet.
- *(Ergänzung)* Administrative Distanz: **90** intern, **170** extern, **5** für Summary-Routen.

## Transport: RTP und Pakettypen

- EIGRP läuft **direkt über IP**, **Protokollnummer 88** (zum Vergleich: TCP 6, UDP 17, OSPF 89).
- **RTP** (Reliable Transport Protocol) ist der EIGRP-eigene Transport: garantierte, **geordnete** Zustellung, Multicast und Unicast gemischt. Nur bestimmte Pakete werden zuverlässig verschickt und brauchen ein ACK.
- *(Ergänzung, RFC 7868)* Fehlt das ACK eines Nachbarn auf ein Multicast-Paket, wird es per **Unicast** an diesen Nachbarn wiederholt; nach dem Retry-Limit wird die Nachbarschaft zurückgesetzt.

| Paket | Zweck | Zustellung | Zuverlässig |
|---|---|---|---|
| Hello | Nachbarn entdecken und halten; ACK-Nummer 0 | Multicast | nein |
| Update | Routen verteilen | Multicast bei neuer Route / nach Konvergenz; **Unicast** beim Synchronisieren mit einem **neuen** Nachbarn | ja |
| Query | Ersatzpfad erfragen, wenn kein FS existiert (Route **active**) | Multicast | ja |
| Reply | Antwort auf eine Query | Unicast an den Absender der Query | ja |
| ACK | bestätigt Update, Query, Reply; ist ein Hello **ohne Daten mit ACK-Nummer ≠ 0** | Unicast | nein |
| Request | gezielte Informationsanfrage (Route-Server-Anwendungen) | Uni- oder Multicast | nein |

- Hello und ACK werden selbst **nicht** bestätigt.
- **Passive** Route = keine Neuberechnung läuft (Normalzustand). **Active** Route = der Router sucht gerade einen neuen Successor, weil der bisherige ungültig ist.

### Drei Tabellen

| Tabelle | Inhalt |
|---|---|
| Neighbor Table | Nachbarn mit **Primäradresse** und lokalem Interface (*(Ergänzung)* plus Hold Time, Uptime, SRTT, RTO, Q Cnt) |
| Topology Table | alle von Nachbarn gemeldeten Ziele; je Ziel die Liste der meldenden Nachbarn mit deren gemeldeter Metrik (RD) und der eigenen Gesamtmetrik über diesen Nachbarn (FD) |
| Routing Table | nur die besten Routen (Successor), Code `D` (intern) bzw. `D EX` (extern) |

- **Successor** = Pfad mit der kleinsten Metrik; wird in die RIB eingetragen und an die Nachbarn weitergemeldet.
- **Feasible Successor (FS)** = bester schleifenfreier Backup-Pfad; steht nur in der Topology Table, nicht in der RIB (außer bei Unequal-Cost-Load-Balancing). Ermöglicht sofortige Umschaltung.
- Im Dual-Stack gibt es **je Protokoll (PDM)** eine eigene Neighbor- und Topology-Tabelle.

### Ablauf beim Start (Kursabbildung, eigene Darstellung siehe Bild 02)

1. R1 kommt hoch und sendet Hellos auf allen EIGRP-Interfaces.
2. R2 antwortet mit einem Hello und schickt gleich seine **komplette Routinginformation** als Update (Unicast). Updates dürfen parallel zur Nachbarerkennung laufen, **bestätigt** werden dürfen sie aber erst, wenn die Nachbarschaft steht.
3. Ist die Nachbarschaft fertig, bestätigt R1 das Update mit einem **ACK**.
4. R1 übernimmt die Einträge in seine Topology Table.
5. R1 schickt seine eigenen Routen als Update an R2.
6. R2 bestätigt mit ACK → beide sind konvergiert.

## Nachbarschaft (Adjacency)

Bedingungen, damit eine Nachbarschaft entsteht (alles steht im Hello):

| Parameter | Bemerkung |
|---|---|
| **AS-Nummer** | muss gleich sein; nur Router derselben AS werden Nachbarn |
| **K-Werte** | müssen gleich sein; Mismatch verhindert/zerstört die Nachbarschaft, selbst wenn der abweichende Wert gar nicht genutzt wird |
| **Gemeinsames Subnetz** | Quelle aller EIGRP-Pakete ist die **Primäradresse** des Interfaces → keine Nachbarschaft über Secondary-Adressen |
| **Authentifizierung** | Methode und Schlüssel müssen passen; ohne Auth akzeptiert EIGRP jeden Router mit gültigem Hello (Sicherheitsrisiko, daher empfohlen) |

- **Nicht** nötig: gleiche Hello-/Hold-Timer (Unterschied zu OSPF), gleiche Router-ID.
- *(Ergänzung)* Default-Timer: **Hello 5 s / Hold 15 s** (LAN, Punkt-zu-Punkt, schnelle Links), **60 s / 180 s** auf Multipoint-NBMA-Interfaces ≤ T1. Jeder Router teilt seine Hold Time im Hello mit; der Nachbar verwendet genau diesen Wert. Erhöht man das Hello-Intervall, passt sich die Hold Time **nicht** automatisch an.
  ```
  interface Gi0/0
   ip hello-interval eigrp 100 10
   ip hold-time eigrp 100 30
  ```
- OSPF kennt keine AS-Nummer im Paket; die OSPF-Prozess-ID ist nur lokal bedeutsam.
- **passive-interface**: Unterdrückt Hellos und verarbeitet auch eingehende EIGRP-Pakete nicht → **keine Nachbarschaft** auf dem Interface; das Netz des Interfaces wird aber weiter annonciert.
- AS-Nummer: hat keine globale Bedeutung (anders als bei BGP). Empfehlung im Kurs: dieselbe Nummer wie die eigene BGP-AS oder einheitlich **1**. Mehrere EIGRP-AS sind nur in Sonderfällen sinnvoll (z. B. DMVPN).
- Router-ID: viel weniger wichtig als bei OSPF; Anzeige mit `show ip protocols`. *(Ergänzung)* Auswahl: manuell (`eigrp router-id`), sonst höchste Loopback-IPv4-Adresse, sonst höchste aktive Interface-IPv4-Adresse. Doppelte Router-IDs können dazu führen, dass externe Routen verworfen werden.

## Metrik

### K-Werte und Komponenten

| K-Wert | Komponente | Bedeutung | Default |
|---|---|---|---|
| K1 | Bandwidth | **kleinste** Bandbreite auf dem Pfad (kbit/s) | 1 |
| K2 | Load | schlechteste Auslastung auf dem Pfad (x/255) | 0 |
| K3 | Delay | **Summe** der Interface-Delays auf dem Pfad (in Zehner-µs) | 1 |
| K4 | Reliability | Zuverlässigkeit 0–255 (255 = 100 %) | 0 |
| K5 | Reliability-Koeffizient | zweiter Reliability-Faktor im Term K5/(Reliability + K4) | 0 |

- Achtung: Der Kurs ordnet K5 in Tabelle und Text der **MTU** zu – das ist falsch (siehe Fehlerabschnitt).
- In Updates übertragen werden: minimale Bandbreite, kumulierter Delay, Load, Reliability, **MTU** und **Hop Count**. MTU und Hop Count gehen **nie** in die Metrik ein. (Kurs: MTU diene nur als Tiebreaker, wenn wegen zu vieler gleich teurer Pfade welche verworfen werden – höchste minimale MTU gewinnt.)
- K-Werte stehen im Hello, müssen also domänenweit gleich sein. Ändern nur auf Empfehlung von Cisco; Load und Reliability werden nicht empfohlen.

### Klassische Formel

Allgemein: Metrik = 256 × [K1·BW + (K2·BW)/(256 − Load) + K3·Delay] × [K5/(Reliability + K4)], wobei der letzte Faktor bei **K5 = 0** entfällt (= 1).

Mit Default-K-Werten:

**Metrik = 256 × ( 10^7 / kleinste Bandbreite in kbit/s + Summe Delay in µs / 10 )**

- Beide Terme werden **ganzzahlig abgeschnitten**.
- Bandbreite: Engpass des Pfades (ausgehende Interfaces). Delay: Summe aller ausgehenden Interfaces bis zum Ziel inklusive des Ziel-LANs.
- Faktor **256**: EIGRP übernahm die 24-Bit-Metrik von IGRP und skalierte sie auf **32 Bit**.
- Werte ansehen mit `show interfaces`:
  ```
  HQ# show interfaces Serial0/0/0
    MTU 1500 bytes, BW 1544 Kbit/sec, DLY 20000 usec,
       reliability 255/255, txload 1/255, rxload 1/255
  ```
- K-Werte prüfen: `show ip protocols` (Zeile `Metric weight K1=1, K2=0, K3=1, K4=0, K5=0`).

### Rechenbeispiele (mit Python nachgerechnet)

Typische Default-Delays: GigabitEthernet 10 µs, FastEthernet 100 µs, Ethernet 1000 µs, T1-Serial 20000 µs.

| Pfad | 10^7/BW | ΣDelay/10 | Metrik |
|---|---|---|---|
| Gi direkt | 10 | 1 | **2816** |
| FastEthernet direkt | 100 | 10 | **28160** |
| Ethernet 10 Mbit/s direkt | 1000 | 100 | **281600** |
| T1 direkt (1544 kbit/s) | 6476 (6476,68 abgeschnitten) | 2000 | **2169856** |
| Gi-Link + Gi-LAN beim Nachbarn | 10 | 2 | **3072** |
| FE-Link + Gi-LAN beim Nachbarn | 100 | 11 | **28416** |
| T1-Link + Gi-LAN beim Nachbarn | 6476 | 2001 | **2170112** |
| 10G direkt (10 µs) | 1 | 1 | **512** |
| 40G direkt (10 µs) | 0 | 1 | **256** |
| 100G direkt (10 µs) | 0 | 1 | **256** |

→ Oberhalb von 10 Gbit/s wird der Bandbreitenterm 0, und weil der kleinste konfigurierbare Delay 10 µs beträgt, sind 40G, 100G und EtherChannel-Bündel nicht mehr unterscheidbar.

### Pfadmanipulation

- Befehle im Interface-Modus: `bandwidth <kbit/s>` und `delay <Zehner-µs>` (`delay 100` = 1000 µs).
- **Delay ändern ist die empfohlene Methode**: Delay ist der einzige kumulative Parameter und wirkt immer. Eine Bandbreitenänderung wirkt nur, wenn das Interface dadurch zum Engpass wird, und beeinflusst zusätzlich QoS und Monitoring/Telemetrie.

### Wide Metrics

- Problem der klassischen Metrik: Links schneller als 1 Gbit/s (bzw. 10G und Bündel) werden nicht korrekt skaliert → ungewolltes ECMP.
- **EIGRP Wide Metrics** (Named Mode): **64-Bit**-Metrik, Zeitangaben in **Pikosekunden**, Skalierungskonstante **65536**, unterstützt Bandbreiten bis ca. **4,2 Tbit/s**. Zusätzlicher Koeffizient **K6** (Default 0) für Extended Attributes (z. B. Jitter, Energie) bzw. künftige Nutzung.
- Formeln (Default-K-Werte): Metrik = K1·Throughput + K3·Latency
  - Throughput = 10^7 · 65536 / BW (kbit/s)
  - Latency = Delay (ps) · 65536 / 10^6. Der Delay kommt bis 1 Gbit/s aus dem Interface-Delay. Für schnellere Interfaces wird er aus der Bandbreite abgeleitet: Delay (ps) = 10^13 / BW (kbit/s), also 1G = 10 µs, 10G = 1 µs, 500G = 20 ns (Kompatibilitätstabelle in RFC 7868). Damit ist dort Latency = 10^7 · 65536 / BW.
  - Beispiel Gi direkt: 655360 + 655360 = **1310720**; geteilt durch rib-scale 128 = **10240** in der RIB. 10G direkt: 65536 + 65536 = **131072** (RIB 1024).
- Die RIB fasst nur 32 Bit → `metric rib-scale <1-255>` (Default **128**) teilt die Metrik herunter. Ändern löscht alle EIGRP-Routen in der RIB und trägt sie neu ein.

## Pfadwahl mit DUAL

- **Advertised Distance (AD) / Reported Distance (RD)**: die Metrik, die ein Nachbar für das Ziel meldet (seine eigene FD).
- **Feasible Distance (FD)**: eigene End-to-End-Metrik = RD des Nachbarn + Kosten zum Nachbarn.
- Die kleinste FD ergibt den **Successor**. Die Route wird der RIB angeboten und installiert, sofern keine Quelle mit kleinerer **Administrative Distance** (z. B. statische Route) existiert. Die FD wird die Routing-Metrik.
- **Feasibility Condition (FC)**: Ein Nachbar ist **Feasible Successor**, wenn **RD < FD des aktuellen Successors**. Begründung: Ist der Nachbar näher am Ziel als man selbst, kann sein Pfad nicht über einen selbst zurücklaufen.
- Advertised Distance (EIGRP) nicht mit **Administrative Distance** verwechseln (beide werden „AD“ abgekürzt).

Kursbeispiel (Router C, Ziel 10.1.1.0/24, Kosten C→A = C→B = 1000):

| Nachbar | RD | FD | Rolle |
|---|---|---|---|
| A (Gi0/0) | 1000 | 2000 | Successor → RIB, Metrik 2000 via Gi0/0 |
| B (Gi0/1) | 1500 | 2500 | Feasible Successor (1500 < 2000) |

### Verhalten bei Ausfall

1. Successor fällt weg oder meldet eine schlechtere Metrik.
2. FS vorhanden → sofort installieren, **ohne Rückfrage** bei den Nachbarn (lokale DUAL-Berechnung), Route bleibt **passive**.
3. Kein FS → Route wird **active**, **Queries** an alle Nachbarn. Jeder Nachbar antwortet mit seiner Metrik, fragt seinerseits weiter oder meldet *(Ergänzung)* „unreachable“. Erst wenn alle Replies da sind, wird ein neuer Successor gewählt.
4. *(Ergänzung)* Bleiben Replies aus: **Stuck in Active (SIA)**. Active Timer Default 3 Minuten; nach der Hälfte wird per SIA-Query nachgefragt, ohne Antwort wird die Nachbarschaft zurückgesetzt. Stub-Router und Summarization begrenzen die Query-Ausbreitung.
- Neuberechnung kostet CPU und Zeit; DUAL prüft deshalb zuerst immer die FS.

## Load Balancing und Traffic Sharing

### Equal-Cost (ECMP)

- Default: bis zu **4** gleich teure Pfade in der RIB. `maximum-paths <n>` (Wertebereich plattformabhängig, im Beispiel 1–16); `maximum-paths 1` schaltet Load Balancing ab. Load Balancing erfolgt laut Kurs pro Konversation (Flow), nicht pro Paket.
  ```
  HQ(config)# router eigrp 100
  HQ(config-router)# maximum-paths ?
    <1-16>  Number of paths
  ```

### Unequal-Cost mit variance

- `variance <1-128>`, Default **1** (= nur gleich teure Pfade). Ein weiterer Pfad wird genutzt, wenn **beide** Bedingungen erfüllt sind:
  1. seine Metrik ist **kleiner** als variance × FD des Successors, und
  2. er ist **Feasible Successor** (RD < FD).
- Kursbeispiel 1: HQ–Branch mit 6-Mbit/s-MPLS (primär) und T1-Backup, Kostenverhältnis knapp 4:1 → `variance 4` bezieht den Backup ein.
- Kursbeispiel 2 (Router E zu Net X, Kosten E–B 20, B–A 10, E–C 10, C–A 10, E–D 20, D–A 25):

| Pfad | Metrik | RD | FS? | variance 2 (< 40) | variance 3 (< 60) |
|---|---|---|---|---|---|
| E-C-A | 20 | 10 | Successor | ja | ja |
| E-B-A | 30 | 10 | ja (10 < 20) | ja | ja |
| E-D-A | 45 | 25 | **nein** (25 > 20) | nein | nein, trotz Metrik < 60 |

### Traffic Sharing

- `traffic-share balanced` (**Default**): Verteilung im Verhältnis der Metriken (schlechterer Pfad bekommt weniger). Kursbeispiel mit variance 3 und den Pfaden E-C-A (20) und E-B-A (30): Verhältnis 30/20 = 1,5. Cisco rundet das Verhältnis auf eine ganze Zahl ab (Cisco 13677), hier also 1:1. Bei z. B. 50/20 = 2,5 wäre es 2:1 (zwei Teile über den besseren Pfad, einer über den schlechteren).
- `traffic-share min across-interfaces`: Traffic nur über den Pfad mit der kleinsten Metrik, die anderen zulässigen Pfade stehen aber **trotzdem in der RIB** → schnellere Umschaltung.
  ```
  router eigrp 1
   variance 3
   traffic-share min across-interfaces
  ```

## EIGRP für IPv6

- Gleiche Mechanismen (DUAL, Hello, Metrik, Load Balancing, drei Tabellen), aber **getrennt** konfiguriert und verwaltet (eigenes PDM, eigene Tabellen).
- **Kein network-Befehl** (Classic): Aktivierung direkt am Interface mit `ipv6 eigrp <AS>`.
- Nachbarschaften und **Next Hop** verwenden **Link-Local-Adressen**. Hellos/Updates an **FF02::A**. *(Ergänzung)* Nachbarn brauchen kein gemeinsames globales Präfix.
- Voraussetzungen: `ipv6 unicast-routing` und eine **32-Bit-Router-ID** (dotted decimal). Manuell nötig, wenn der Router keine IPv4-Adresse hat.
- Älteres IOS (Classic): Der `ipv6 router eigrp`-Prozess startet im Zustand shutdown und braucht `no shutdown`.

```
Router(config)# ipv6 unicast-routing
Router(config)# ipv6 router eigrp 100
Router(config-rtr)# eigrp router-id 1.1.1.1
Router(config-rtr)# no shutdown
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ipv6 address 2001:DB8:1::1/64
Router(config-if)# ipv6 eigrp 100
```

- *(Ergänzung)* Im Named Mode (`address-family ipv6 unicast autonomous-system <AS>`) nehmen alle IPv6-Interfaces automatisch teil; ausnehmen mit `shutdown` unter `af-interface`.

## EIGRP vs. OSPF

| Kriterium | EIGRP | OSPF |
|---|---|---|
| Einrichtung | einfach | aufwendiger |
| Design | flexibel, keine Areas | starr (Areas, Backbone Area 0) |
| Skalierung | mittlere bis große Netze | große Netze |
| CPU, Speicher, Bandbreite | sparsamer | aufwendiger |
| Herstellerunterstützung | überwiegend Cisco (wenige Linux-basierte Router) | praktisch alle |
| Load Balancing | Equal und Unequal | nur Equal |
| Backup | FS vorberechnet | neue SPF-Berechnung |
| IPv6 | EIGRP für IPv6 (Classic oder Named) | OSPFv3 (auch mit Address Families) |

- Erste Frage: Unterstützen alle Layer-3-Geräte das Protokoll? Reines Cisco-Netz → oft EIGRP; Multivendor → meist OSPF.
- Konvergenz (Kursdiagramm, Konvergenzzeit über 1000–5000 Routen): EIGRP **mit** FS am schnellsten (unter ca. 1,5 s), OSPF mit getunten Timern knapp dahinter, EIGRP **ohne** FS steigt linear stark an (bis ca. 6 s), OSPF mit Default-Timern am langsamsten (ca. 6–6,5 s). Aussage: In kleinen/mittleren Netzen konvergiert EIGRP auch ohne Design gut, in großen Netzen bestimmt das Design (FS, Summarization, Stubs) die Konvergenzzeit.
- Beide Protokolle flächendeckend parallel zu betreiben, ist Ressourcenverschwendung; bei gleichem Präfix gewinnt EIGRP intern (AD 90) gegen OSPF (AD 110).

## Konfiguration

### Classic Mode (Autonomous-System-Konfiguration)

- `router eigrp <AS 1-65535>`; die AS muss auf allen Routern gleich sein.
- `network <Netz> [Wildcard]`: aktiviert EIGRP auf allen Interfaces, deren Adresse im Bereich liegt, und nimmt deren Netze in die Updates auf. Ohne Wildcard gilt das klassenbezogene Netz. Eine eingegebene Subnetzmaske wird von IOS in eine Wildcard umgewandelt.
- Viele Parameter liegen im Interface-Modus (Hello/Hold, Split Horizon, Authentifizierung, Summary) → Konfiguration ist verteilt.

Kurs-Topologie: Branch (LAN 10.1.1.0/24, Gi0/0 192.168.1.1) – HQ (Gi0/0 192.168.1.2, LAN 172.16.1.0/24), AS 100.

```
Branch(config)# router eigrp 100
Branch(config-router)# network 10.0.0.0
Branch(config-router)# network 192.168.1.0

HQ(config)# router eigrp 100
HQ(config-router)# network 172.16.1.0 0.0.0.255
HQ(config-router)# network 192.168.1.0 0.0.0.255
```

- *(Ergänzung)* `auto-summary` ist seit IOS 15.0(1)M / IOS-XE 2.5 per Default aus.

### Named Mode (Multi-AF-Modus)

- `router eigrp <Name>` → `address-family ipv4|ipv6 unicast|vrf <vrf> autonomous-system <AS>` → `network ...`.
- Der Name ist nur lokal bedeutsam und **nicht** die AS-Nummer; die AS steht in der address-family. *(Ergänzung)* Nach `router eigrp` wird eine reine Zahl als AS (Classic) geparst, nur ein Wort ergibt den Named Mode. Named und Classic sind zueinander kompatibel, entscheidend ist die AS.
- Vorteile: alles an einer Stelle, mehrere AFs und VRFs in einem Prozess, klare Gültigkeitsbereiche, neue Features (z. B. Wide Metrics) nur hier.
- *(Ergänzung)* Untermodi: `af-interface` (Hello, Hold, Auth, passive), `topology base` (variance, maximum-paths, redistribute, distance).

```
HQ(config)# router eigrp CompanyABC
HQ(config-router)# address-family ipv4 unicast autonomous-system 100
HQ(config-router-af)# network 172.16.1.0 0.0.0.255
HQ(config-router-af)# network 192.168.1.0 0.0.0.255
```

### Verifikation

| Classic | Named | Zeigt |
|---|---|---|
| `show ip eigrp interfaces` | `show eigrp address-family ipv4 interfaces` | Interfaces mit EIGRP, Peers je Interface |
| `show ip eigrp neighbors` | `show eigrp address-family ipv4 neighbors` | Nachbarn, Hold, Uptime, SRTT, RTO, Q Cnt; hilft bei Transportproblemen |
| `show ip eigrp topology [all-links]` | `show eigrp address-family ipv4 topology` | Topology Table: passive/active, Anzahl Successors, FD; `all-links` zeigt auch Pfade, die die FC nicht erfüllen |
| `show ip protocols` | | K-Werte, Router-ID, variance, maximum-paths |

Beispiel (eigene, gekürzte Ausgabe):
```
R1# show ip eigrp topology
P 10.9.9.0/24, 1 successors, FD is 3072
        via 10.1.12.2 (3072/2816), GigabitEthernet0/0
        via 10.1.13.3 (28416/2816), GigabitEthernet0/1
```
Lesart: `(FD/RD)`; der zweite Eintrag ist FS, weil RD 2816 < FD 3072. *(Ergänzung)* Code-Spalte: P passive, A active, U update, Q query, R reply, r reply status.

### Troubleshooting-Hinweise

- Keine Nachbarschaft: AS, K-Werte, Subnetz (Primäradresse), Authentifizierung, passive-interface, ACL gegen IP-Protokoll 88 bzw. 224.0.0.10 prüfen.
- Route fehlt in der RIB, ist aber in der Topology Table: andere Quelle mit kleinerer AD.
- Unequal-Cost-Pfad wird trotz ausreichender variance nicht genutzt: Er ist kein FS.
- Ungewolltes ECMP zwischen 10G/40G/Bündeln: klassische Metrik → Wide Metrics (Named Mode).

## Fehler/Ungenauigkeiten im Kurs

| Stelle | Kursaussage | Richtig | Quelle |
|---|---|---|---|
| S. 89, Tabelle und Text | K5 = MTU | K5 ist ein **Reliability-Koeffizient** (Term K5/(Reliability + K4)). Die MTU geht nie in die Metrik ein, was der Kurs selbst weiter unten sagt | RFC 7868 Kap. 5.6; Prüfprotokoll |
| S. 89 | `delay microseconds` als Interface-Befehl | Der Befehl `delay` arbeitet in **Zehner-µs** (`delay 100` = 1000 µs); `show interfaces` zeigt µs | Cisco Command Reference `delay` |
| S. 89, Grafik Wide Metrics | K6 sei eingeführt worden, um Interfaces über 1 Gbit/s zu unterstützen | Die hohen Bandbreiten lösen 64-Bit-Metrik, Pikosekunden und Konstante 65536. **K6** ist ein zusätzlicher Koeffizient für Extended Attributes/künftige Nutzung (Default 0); der Fließtext des Kurses sagt das auch so | Cisco EIGRP Wide Metrics Configuration Guide |
| S. 89 | MTU als Tiebreaker bei zu vielen gleich teuren Pfaden | Nicht belegt: RFC 7868 sagt nur, die MTU werde übertragen, aber nicht für die Metrik verwendet. Ein Labortest (ipspace.net 2010) fand keinen MTU-Einfluss auf die Pfadwahl; Cisco-Doku dazu fehlt. Prüfungsrelevant: MTU wird übertragen, geht aber nicht in die Metrik ein | RFC 7868 (Vector Metric/Wide-Metric-TLV: „Not used in metric calculation“); blog.ipspace.net/2010/06/eigrp-mtu-metric/ |
| S. 91 | maximum-paths muss auf beiden Seiten gleich sein | Keine Bedingung; maximum-paths ist eine lokale Entscheidung über die eigene RIB | Prüfprotokoll |
| S. 91 | Pfade mit Metrik „less than or equal to“ variance × FD | Die Regel lautet „kleiner als“ variance × FD (Cisco 13677, Einleitung). Cisco selbst ist uneinheitlich: Das Rechenbeispiel derselben Seite schreibt „less than or equal to 40“. Der Kurs schreibt an anderer Stelle selbst „less than“. Fragen sollten nicht genau auf der Grenze liegen | Cisco 13677 (Load Balancing) |
| S. 91 | Traffic-Share-Rechnung 30/20 = 3/2 = 1 und „per conversation“ vs. „one packet“ | 30/20 = 1,5 (abgerundet 1); das Verhältnis gibt die Gewichtung der Flows an, nicht einzelne Pakete; widersprüchlich formuliert | eigene Rechnung |
| S. 92 | IPv6 braucht **immer** eine manuelle Router-ID | Nur nötig, wenn der Router keine IPv4-Adresse hat | Prüfprotokoll |
| S. 92 | Ein FS werde „in die Topology Table eingetragen“, wenn RD < FD | Alle gelernten Pfade stehen in der Topology Table; die FC entscheidet nur über den FS-Status | RFC 7868 |
| S. 93, Tabelle | „Classic für IPv4, Named für IPv6“ | Beide Modi beherrschen IPv4 und IPv6 | Cisco Named-Mode-Doku |
| S. 93 | Konvergenzdiagramm wird als „Design/kein Design“ erklärt | Die Kurven unterscheiden EIGRP **mit/ohne Feasible Successors** und OSPF mit Default-/getunten Timern | Kursabbildung |
| S. 94 | `show eigrp address-family neighbors` | Die Address Family muss angegeben werden: `show eigrp address-family ipv4 neighbors` (bzw. ipv6) | Cisco EIGRP Command Reference |

## Bilder

Ordner `bilder/09-eigrp/`:

- `01-merkmale.svg` – EIGRP-Merkmale rund um DUAL: Advanced Distance Vector, RTP/Protokoll 88, Multicast, partial/bounded Updates, classless, Multi-AF, Load Balancing.
- `02-start.svg` – Nachbarerkennung und Synchronisation zweier Router als Sequenzdiagramm (Hello, Unicast-Update, ACK erst nach fertiger Nachbarschaft).
- `03-pakete.svg` – Die sechs Pakettypen mit Zweck, Uni-/Multicast und Zuverlässigkeit plus die drei Tabellen.
- `04-nachbarn.svg` – Was für eine Nachbarschaft passen muss (AS, K-Werte, Subnetz/Primäradresse, Auth) und was nicht (Timer, Router-ID); passive-interface.
- `05-metrik.svg` – Klassische Metrikformel mit K-Werten, Rechenbeispiele und Grenze oberhalb 10 Gbit/s; delay in Zehner-µs.
- `06-fd-rd.svg` – Successor/Feasible Successor am Kursbeispiel (Router C, A und B), FD = RD + Linkkosten, Feasibility Condition.
- `07-variance.svg` – Unequal-Cost-Load-Balancing mit variance am Beispiel E→Net X: Bedingungen Metrik < variance × FD UND FS.
- `08-dual-ablauf.svg` – DUAL-Entscheidung bei Ausfall: FS vorhanden → passive, sonst active mit Query/Reply und SIA.
- `09-modi.svg` – Classic vs. Named Mode mit Befehlsstruktur und show-Befehlen, inkl. IPv6-Besonderheiten.
