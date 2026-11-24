# Exploring Cisco Switching Paths

Quelle: ENCOR 1.4.10 Student Guide, Seiten 21–27 (inkl. Discovery 1 „Investigate the CAM“ und Discovery 2 „Analyze Cisco Express Forwarding“)

Topics: ENCOR-3.1.a (L2-Switching, CAM/TCAM, MAC-Tabelle), ENCOR-3.2.a (RIB/FIB/CEF, Adjacency, AD), ENCOR-5.2.b (Punts/CPU-Pfad), ENCOR-1.4 (QoS-Queues im Switch-Pipeline-Bezug)

## Layer-2-Switch-Betrieb

### Vom Hub zum Switch
- Hub: geteiltes Medium, alle Hosts teilen die Bandbreite, CSMA/CD regelt den Zugriff, nur Half-Duplex. Kollision → alle warten (Backoff). Jeder Frame (auch fehlerhafte) erreicht alle Hosts.
- Switch = Multiport-Bridge: jeder Port ist ein eigenes LAN-Segment und eine eigene **Kollisionsdomäne** → kein Wettbewerb ums Medium → **Full-Duplex** möglich (gleichzeitig senden und empfangen).
- Ein Switch prüft Frames auf Fehler (FCS) und regeneriert nur fehlerfreie Frames (gilt für Store-and-Forward; Cut-Through-Switches leiten vor FCS-Prüfung weiter).
- Weiterleitungsentscheidung anhand der **Ziel-MAC**.

### MAC-Adresstabelle (CAM)
- CAM-Tabelle = MAC-Adresstabelle = Forwarding Table.
- Lernen: Switch liest die **Quell-MAC** jedes eingehenden Frames und speichert **MAC + Eingangsport + VLAN** (falls noch nicht vorhanden; ändert sich der Port, wird der Eintrag aktualisiert = MAC-Move).
- Einträge können auch statisch konfiguriert werden (`mac address-table static <mac> vlan <id> interface <if>`), statische Einträge altern nicht.
- Lookup-Schlüssel ist **MAC + VLAN**: eine MAC, die nur in VLAN 20 gelernt wurde, ist für einen Frame in VLAN 1 „unbekannt“.
- Weiterleitung:
  - Ziel-MAC bekannt (exakter Treffer in diesem VLAN) → nur aus dem zugehörigen Port.
  - Ziel-MAC liegt am selben Port, über den der Frame kam → Frame wird verworfen (gefiltert).
  - Ziel-MAC unbekannt → **Unknown Unicast Flooding**: alle Ports des VLANs außer dem Eingangsport.
  - Broadcast und Multicast → per Default geflutet (Multicast ohne IGMP Snooping).
- Beispiel aus dem Kurs (eigene Darstellung): CAM enthält …1111 Port 1 VLAN 1, …2222 Port 2, …5555 Port 5, …6666 Port 6, …4444 Port 4 (alle VLAN 1) und …3333 Port 3 VLAN 20. Frame für …5555 auf Port 1 → nur Port 5. Broadcast auf Port 1 (VLAN 1) → Ports 2, 4, 5, 6 (nicht 1 = Eingang, nicht 3 = anderes VLAN).

### Switch-Pipeline: Queues, CAM, TCAM, QoS
- Eingehender Frame → **Ingress-Queue** (ein Port kann mehrere Queues mit unterschiedlicher Priorität haben).
- Drei Fragen pro Frame:
  1. Wohin? → **L2-Forwarding-Table (CAM)**, MAC als Index.
  2. Überhaupt weiterleiten? → **ACLs** (auch MAC-ACLs), in der **TCAM**, ein einziger Lookup.
  3. Wie? → **QoS**: Klassifizierung, Priorisierung, Rate-Limiting – ebenfalls TCAM, ein Lookup.
- Danach kommt der Frame in eine **Egress-Queue** des Ausgangsports; welche Queue, bestimmt QoS (wichtiger Verkehr zuerst).
- CAM- und TCAM-Lookups laufen **parallel**; viele Switches haben mehrere TCAMs (z. B. Ingress-ACL, Egress-ACL, QoS). Deshalb kostet das Aktivieren von ACLs/QoS auf Catalyst-Switches keine Forwarding-Performance.

### CAM vs. TCAM
| | CAM | TCAM |
|---|---|---|
| Vorkommen | jeder Switch | Multilayer-Switches, Router |
| Inhalt | MAC → Port (+VLAN) | ACL, QoS, L3-Prefixe (CEF), weitere Infos für höhere Schichten |
| Vergleich | binär, exakter Treffer | ternär (0, 1, X = „egal“) → Masken/Prefixe |
| Einsatz | L2-Forwarding | L3-Switching, Policies |
- Beide liegen in schnellem Speicher; Multilayer-Switches forwarden mit ASICs „wire speed“, die Tabellen werden in Hardware programmiert.
- TCAM-Ressourcen werden auf Catalyst-Switches über SDM-Templates aufgeteilt (`show sdm prefer`; Templatewechsel erst nach Reload wirksam). Auslastung auf Catalyst 9000 z. B. mit `show platform hardware fed switch active fwd-asic resource tcam utilization`.

### Discovery 1 – CAM untersuchen (Lab-Erkenntnisse)
Topologie: Switch1 mit PC1 (Et0/1), PC2 (Et0/2), PC3 (Et0/3), Uplink Et1/1 zu Switch2. Subnetz 10.1.1.0/24.
- Broadcast-Ping (`ping` erweitert, Ziel 10.1.1.255) aus privilegiertem Modus – damit alle Hosts antworten und der Switch alle MACs lernt (der erweiterte Ping ist nur im privilegierten Modus verfügbar; der Kurs sagt zusätzlich, Broadcast-Pings seien aus User EXEC nicht erlaubt – nicht offiziell belegt).
- Befehle:
```
show mac address-table
show mac address-table interface ethernet 1/1
show mac address-table address <mac>
show mac address-table vlan <id>
show mac address-table dynamic
show mac address-table count
show mac address-table aging-time
show cdp neighbors
(config)# mac address-table aging-time 600
(config)# mac address-table aging-time 600 vlan 10
clear mac address-table dynamic [address <mac> | interface <if> | vlan <id>]
```
- Gekürzte Beispielausgabe (eigene):
```
Vlan    Mac Address       Type        Ports
----    -----------       --------    -----
   1    aabb.cc00.0300    DYNAMIC     Et0/1
   1    aabb.cc00.0400    DYNAMIC     Et0/2
   1    aabb.cc00.0500    DYNAMIC     Et0/3
   1    aabb.cc00.0600    DYNAMIC     Et1/1
   1    aabb.cc00.0700    DYNAMIC     Et1/1
Total Mac Addresses for this criterion: 5
```
  Mehrere MACs auf einem Port → dahinter hängt ein weiterer Switch (Uplink/Trunk) oder ein Hub/AP/IP-Phone; prüfbar mit `show cdp neighbors`.
- **Aging**: Default 300 s (5 min). Nicht gehörte (stale) Einträge werden entfernt, weil die CAM nicht unendlich groß ist. `aging-time 0` deaktiviert das Altern (Catalyst; Bereich sonst 10–1000000 s).
- **ARP-Timeout** Default 4 Stunden (14400 s). Ist CAM-Aging (5 min) viel kürzer als ARP-Timeout, kann bei Hosts, die lange nur empfangen (oder bei asymmetrischem Routing), Unknown Unicast Flooding entstehen: Router hat noch ARP-Eintrag, Switch hat die MAC schon vergessen → flutet. Gegenmittel: CAM-Aging erhöhen bzw. ARP-Timeout senken.
- CAM-Einträge lassen sich **nicht summarisieren** (anders als IP-Prefixe): 1000 Geräte = 1000 Einträge pro Switch. Ist die CAM voll, können neue MACs nicht gelernt werden → Frames an diese Ziele werden geflutet (Switch verhält sich für sie wie ein Hub; Angriffsmuster: MAC Flooding, Gegenmittel Port Security). Strukturelle Lösung: L2-Domänen durch Routing verkleinern.
- **MAC-Move/MAC-Flapping**: dieselbe MAC wird abwechselnd an zwei Ports gelernt (typisch L2-Loop oder doppelt angebundener Host). Log z. B. `%SW_MATM-4-MACFLAP_NOTIF`.

## Control Plane und Data Plane
- In L3-Geräten sind Control Plane und Data Plane weitgehend unabhängig (verteilte Architektur).
- **Control Plane**: Routingprotokolle (OSPF, EIGRP, BGP …) laufen auf dem **Route Processor (RP)**; baut RIB, FIB, Adjacency; berechnet rekursive Routen.
- **Data Plane**: Interfacemodule mit eigenem Microcode-Prozessor/ASICs und Switching Fabric leiten die meisten Pakete weiter.
- Zusammenspiel:
  - interne Daten- und Steuerkreise für Forwarding und Control verwalten,
  - Routing-/Forwarding-Infos aus L2/L3-Protokollen und Konfiguration extrahieren und an die Interfacemodule übertragen,
  - Statistiken (Traffic-Zähler) von den Modulen zum RP sammeln,
  - bestimmte Pakete von den Interfacemodulen an den RP weiterreichen (Punts: Control-Traffic, Ausnahmepakete).
- (Management Plane = SSH, SNMP, Syslog usw. – im Kurs hier nicht vertieft.)

## Cisco-Switching-Mechanismen

### Process Switching
- Langsamste Methode, **jedes Paket** durch die CPU, alle Entscheidungen in Software.
- Ablauf: L2-Header entfernen, Ziel in der Routingtabelle nachschlagen (ggf. rekursiv), ARP-Cache bzw. ARP-Request, neuen L2-Header bauen inkl. CRC, senden.
- CPU-intensivste Methode; nur noch letzter Ausweg / Troubleshooting.

### Fast Switching (Route Caching)
- Erstes Paket **zu einem Ziel** wird process-switched; danach entsteht ein **Fast-Switching-Cache-Eintrag pro Ziel** (Ziel → Ausgangsinterface + fertiger L2-Header).
- Folgepakete zum gleichen Ziel: im Interrupt-Code sofort verarbeitet, kein rekursiver Lookup, vorgefertigter L2-Header (kein ARP-Lookup).
- Ziel nicht im Cache → wieder process-switched + neuer Cache-Eintrag.
- „Bedarfsgesteuert“ (demand-based): Cache entsteht erst durch Traffic. Anzeigen (klassisches IOS): `show ip cache`.
- Historisch, durch CEF abgelöst.

### Cisco Express Forwarding (CEF)
- **Topologiebasiert**: FIB und Adjacency-Tabelle werden **vorab** aus Routing- und ARP/ND-Tabelle gebaut, unabhängig von Traffic. Auch das erste Paket wird per CEF geschaltet.
- Default-Switching-Modus auf aktuellen IOS/IOS-XE-Geräten, schnellste Methode, weniger CPU-Last als Fast/Process.
- Auf Multilayer-Switches/Hardware-Routern werden FIB/Adjacency in TCAM/ASIC programmiert; auf Software-Routern bzw. bei zentralem CEF läuft CEF auf der CPU des RP (trotzdem schneller als Fast Switching, aber nicht „Hardware“).
- Einschränkungen: manche Features sind nicht CEF-kompatibel; selten kann CEF die Performance verschlechtern – Beispiel **CEF-Polarisation** bei lastverteilten L3-Pfaden.

### Ablauf bei EIGRP-gelernter Route (Process/Fast)
1. EIGRP-Update → Eintrag in der Routingtabelle.
2. Erstes Paket: nicht im Fast-Cache → Process Switching, rekursiver Lookup, ggf. ARP.
3. Cache-Eintrag wird angelegt.
4. Folgepakete zum selben Ziel: fast-switched.

## CEF im Detail

### Tabellen
- Jedes Routingprotokoll hat seine eigene RIB (bzw. Topologie-/Datenbank). Pro Ziel kommt die beste Route in die globale RIB (IP-Routingtabelle). Konkurrieren Protokolle um dasselbe Prefix (gleiche Prefixlänge), entscheidet die **Administrative Distance** (Vertrauenswürdigkeit; kleiner = besser).
- Default-AD (allgemeines Wissen): connected 0, static 1, eBGP 20, EIGRP intern 90, OSPF 110, IS-IS 115, RIP 120, EIGRP extern 170, iBGP 200.
- In `show ip route` steht `[AD/Metrik]`, z. B. `D 192.168.110.0/24 [90/307200] via 10.10.10.2`.
- **FIB**: aus der IP-Routingtabelle abgeleitet, für maximalen Lookup-Durchsatz organisiert. In der TCAM nach Spezifität sortiert (spezifischste zuerst) → erster Treffer = **Longest Match**. Jede Änderung der RIB wird sofort einmal in die FIB übernommen; kein Cache, der durch Pakete entsteht. Next Hops sind bereits rekursiv aufgelöst.
- TCAM voll → **Wildcard-Eintrag** leitet nicht programmierte Ziele an die L3-Engine (Software) → funktioniert, aber langsam, höhere CPU-Last.
- **Adjacency-Tabelle**: aus ARP (IPv4) bzw. Neighbor Discovery (IPv6); enthält pro Next Hop den vorberechneten L2-Rewrite-Header (Ziel-MAC, Quell-MAC, Ethertype). Wird befüllt, sobald Nachbarn entdeckt werden. Adjacency-Tabelle voll → TCAM-Eintrag zeigt auf die L3-Engine.
- Kursdiagramm (eigene Beschreibung): EIGRP-Topologie 10.0.0.0/8 via 172.16.1.2 → IP-Routingtabelle (EIGRP 10.0.0.0/8 via 172.16.1.2; connected 172.16.1.0/24 Ethernet0) → FIB 10.0.0.0/8 mit Adjacency-Pointer 172.16.1.2 → Adjacency 172.16.1.2 mit L2-Header aus ARP-Cache (MAC des Next Hops).

### Spezielle FIB-/Adjacency-Einträge (aus Lab + Ergänzung)
| Eintrag | Bedeutung |
|---|---|
| `attached` | direkt angeschlossenes Prefix bzw. aufgelöster Host im angeschlossenen Netz |
| `receive` | Adresse des Routers selbst (Interface-IP, Netz- und Broadcastadresse des Subnetzes, 224.0.0.0/24, 255.255.255.255) → Paket geht an die CPU |
| `drop` | wird in der Data Plane verworfen (z. B. 0.0.0.0/8, 127.0.0.0/8, 224.0.0.0/4 ohne Multicast-Routing, 240.0.0.0/4) |
| `no route` | kein Eintrag, z. B. 0.0.0.0/0 ohne Default-Route |
| glean | angeschlossenes Subnetz, Ziel-MAC noch unbekannt → Paket an CPU, ARP wird ausgelöst |
| null | Route auf Null0 → verwerfen |
| punt | Paket muss an die CPU (Feature nicht in CEF unterstützt) |
| incomplete | Adjacency angelegt, L2-Info (ARP/ND) noch nicht aufgelöst |

### Ausnahmepakete (Punts an die L3-Engine/CPU)
- IP-Header-Optionen
- ablaufende TTL (z. B. Traceroute → ICMP Time Exceeded von der CPU)
- Weiterleitung an Tunnel-Interface (plattformabhängig)
- nicht unterstützte Encapsulation (ein- oder ausgehend)
- Paket > MTU des Ausgangsinterfaces, Fragmentierung nötig
- außerdem: Pakete an den Router selbst (receive), glean, kein Platz in TCAM/Adjacency

### CEF-Modi
- **Central CEF**: FIB + Adjacency nur auf dem RP, RP forwardet. Nötig, wenn Linecards kein CEF können oder Features nicht dCEF-kompatibel sind.
- **Distributed CEF (dCEF)**: Linecards haben identische Kopien von FIB + Adjacency und forwarden selbst; RP entlastet. Synchronisation per **IPC**. Global: `ip cef distributed`.
- dCEF-Update-Ablauf (Routing-Update):
  1. Paket landet im Input-Buffer der Ingress-Linecard; Forwarding-Engine erkennt Routing-Information, Pointer in die VOQ (Virtual Output Queue) Richtung RP.
  2. Linecard fragt beim Scheduler an, bekommt Grant, Paket geht über die Fabric zum RP.
  3. RP aktualisiert die Routingtabelle, flutet ggf. Link-State-Infos, berechnet rekursive Routen (IGP + EGP).
  4. RP schickt FIB-Updates an alle Linecards (gedrosselt, falls nötig). RP hält eine Kopie jeder Linecard-FIB → neue Linecard bekommt sie beim Aktivwerden.
  5. Neuer L2-Nachbar: Linecard meldet L2-Info an RP → RP aktualisiert Adjacency auf RP und allen Linecards.
- dCEF-Datenpaket: Rx-Linecard schlägt in FIB nach → VOQ der Ziel-Linecard → Scheduler-Grant → Fabric → Tx-Linecard puffert, setzt L2-Header, ggf. Replikation pro Port, sendet. Datenpakete erreichen den RP normalerweise nicht (Ausnahme: Punts).

### Discovery 2 – CEF analysieren (Lab-Erkenntnisse)
Topologie: HQ Et0/0 10.10.10.1/30 ↔ BR1 Et0/0 10.10.10.2/30; HQ-LAN Et0/1 192.168.100.1/24; BR1-LAN Et0/1 192.168.110.1/24.
- Befehle:
```
show ip cef
show ip cef 192.168.110.0 255.255.255.0 [detail]
show ip cef exact-route <src> <dst>
show adjacency [detail | summary]
show ip arp
show ip route
show ip interface ethernet 0/0 | include CEF
(config)# ip cef            ! Default an
(config)# no ip cef         ! global aus → "%IPv4 CEF not running"
(config-if)# no ip route-cache cef   ! CEF pro Interface aus (Fallback Fast Switching)
(config)# ipv6 cef / ipv6 unicast-routing
show ipv6 cef / show ipv6 neighbors
```
- Ohne Traffic: FIB enthält alle connected Prefixe sowie receive/drop-Einträge; `show adjacency` ist leer (keine ARP-Einträge).
- `ping 10.10.10.2` → `.!!!!` (80 %): erstes Paket geht verloren, weil ARP erst aufgelöst wird. Danach: Adjacency `IP Ethernet0/0 10.10.10.2(7)` und neuer FIB-Eintrag `10.10.10.2/32 attached Ethernet0/0`.
- EIGRP aktiviert (`router eigrp 1`, `network 0.0.0.0`) → `D 192.168.110.0/24 [90/307200] via 10.10.10.2` → FIB-Eintrag `192.168.110.0/24 10.10.10.2 Ethernet0/0`; Adjacency-Tabelle unverändert (ARP unverändert, gleicher Next Hop).
- `show ip interface` zeigt „IP CEF switching is enabled“; nach `no ip route-cache cef`: „IP CEF switching is disabled“, „IP route-cache flags are Fast, No CEF“.
- IPv4-CEF ist per Default global aktiv (`ip cef`). Für IPv6: `ipv6 unicast-routing` schaltet das IPv6-Forwarding ein, CEF für IPv6 wird mit `ipv6 cef` (bzw. `ipv6 cef distributed`) aktiviert; Voraussetzung laut Cisco: IPv4-CEF (`ip cef` bzw. `ip cef distributed`) ist vorher global aktiv. (Ob `ipv6 cef` automatisch mit `ipv6 unicast-routing` erscheint, ist plattform-/releaseabhängig – im Zweifel `show ipv6 cef` prüfen.)

### Load Sharing und Polarisation (Ergänzung, allgemeines CEF-Wissen)
- Mehrere gleichwertige Routen in der RIB → CEF verteilt per Hash (Load Sharing).
- **Per-Destination** (Default): Hash über Quell-/Ziel-IP (optional Ports) → alle Pakete eines Flows nehmen denselben Pfad, keine Umsortierung; bei wenigen Flows ungleich.
- **Per-Packet** (`ip load-sharing per-packet` am Interface): Round Robin, bessere Auslastung, aber Paket-Reordering (schlecht für TCP, VoIP).
- `show ip cef exact-route <src> <dst>` zeigt, welchen Pfad ein bestimmtes Quell-Ziel-Paar nimmt.
- **Polarisation**: Alle Router nutzen denselben Hash; Router der zweiten Ebene bekommen nur Traffic, der schon „sortiert“ ist, und nutzen nur einen ihrer Pfade. Abhilfe: Algorithmus `universal` mit routerindividueller ID (`ip cef load-sharing algorithm universal <id>`), Ports in den Hash aufnehmen (`include-ports`), abwechselnd unterschiedliche Hash-Eingaben je Ebene.
- Details (Cisco Tech Note 116376 / CEF Load-Balancing Guide): `universal` ist in aktuellen IOS-Versionen der Default und mischt eine 32-Bit-Universal-ID (beim Boot zufällig, per `<id>` fest einstellbar) in den Hash. Laut Tech Note wirkt die Unique-ID auf Hardware-Plattformen (Cat6500) bei gerader Pfadanzahl nicht. `include-ports [source] [destination]` nimmt L4-Ports in den Hash; laut Config Guide gilt das für software-geswitchte Pakete, Hardware kann anders entscheiden. Per-Packet wird z. B. auf ASR 1000 nicht unterstützt.

## Fehler/Ungenauigkeiten im Kurs
1. **Fast Switching „cached in hardware“** (Seite 24, Aufzählung): Der Fast-Switching-Cache liegt im Hauptspeicher und wird im Interrupt-Code der CPU genutzt, nicht in Hardware. Außerdem ist er **pro Ziel** (Zielprefix/-adresse), nicht pro Flow. Korrekt: „Erstes Paket zu einem Ziel über die CPU, Folgepakete per Cache-Lookup im Interrupt-Kontext“. Quelle: Cisco „How to Choose the Best Router Switching Path for Your Network“ (cisco.com, Doc-ID 13706).
2. **CEF „all packets are switched by using hardware“** (Seite 24) und „data packets are never sent to the RP“ (Seite 25): absolut formuliert. Bei Software-Routern/zentralem CEF läuft CEF auf der RP-CPU; Ausnahmepakete (receive, glean, TTL, Optionen, Fragmentierung) gehen immer an die CPU – der Kurs nennt das selbst wenige Absätze später. Quelle: Cisco IOS XE „Cisco Express Forwarding Overview“ Config Guide.
3. **FIB als „Cisco Express Forwarding Cache“** (Abbildung Seite 25): Die FIB ist kein Cache im Sinne eines bedarfsgesteuerten Route-Caches; sie spiegelt die RIB vollständig. Quelle: wie 2.
4. **„When the CAM table is full, the switch acts as a hub by forwarding all new frames“** (Discovery 1): Geflutet werden Frames an Ziel-MACs, die nicht gelernt werden konnten; bekannte Einträge funktionieren weiter. Präziser: unbekannte Ziele werden geflutet.
5. **Discovery-1-Ausgabe**: „Sending 10000, 1500-byte ICMP Echos“ bei Repeat Count 10 – Tippfehler (müsste 10 sein); die Antworten stammen außerdem von 10.1.1.3–.5, obwohl die Tabelle nur PC1–PC3 (.1–.3) nennt (weitere Hosts hinter Switch2). In der Tabelle steht die MAC einmal als `aabb.cc00.3000` (vermutlich `…0300`).
6. **„Adjacency table is derived from the ARP table“**: gilt für IPv4/Ethernet; bei IPv6 aus Neighbor Discovery, bei Point-to-Point-Interfaces entstehen Adjacencies ohne ARP.
7. **„Cisco Express Forwarding supports load balancing, but the device may adversely affect performance“** (Discovery 2, Hinweis): unklar formuliert; gemeint ist vermutlich, dass Per-Packet-Load-Sharing Reordering verursachen kann bzw. Polarisation die Verteilung verschlechtert.

## Bilder
- `bilder/03-switching-paths/01-cam-lernen.svg` – Switch lernt Quell-MACs (MAC+Port+VLAN), Known Unicast vs. Broadcast/Unknown Unicast im VLAN, Port im anderen VLAN bleibt außen vor.
- `bilder/03-switching-paths/02-pipeline.svg` – Switch-Pipeline: Ingress-Queue → paralleler CAM-/TCAM-Lookup (Forwarding, ACL, QoS) → Egress-Queue nach QoS.
- `bilder/03-switching-paths/03-cp-dp.svg` – Control Plane (Routingprotokolle, RIB auf dem RP) vs. Data Plane (FIB/Adjacency, Forwarding), inkl. Punt-Pfad.
- `bilder/03-switching-paths/04-switching.svg` – Process vs. Fast vs. CEF: welche Pakete die CPU sieht.
- `bilder/03-switching-paths/05-cef-tab.svg` – Protokoll-RIBs → AD → IP-Routingtabelle → FIB (Longest Match) + Adjacency aus ARP/ND.
- `bilder/03-switching-paths/06-dcef.svg` – dCEF: RP mit Master-FIB, Linecards mit FIB-Kopien, IPC-Synchronisation, Datenpfad über die Fabric.
- `bilder/03-switching-paths/07-cef-lab.svg` – Lab HQ–BR1: FIB-/Adjacency-Inhalt vor/nach Ping und nach EIGRP.
- `bilder/03-switching-paths/08-loadshare.svg` – Per-Destination vs. Per-Packet Load Sharing und CEF-Polarisation in zwei Ebenen.
