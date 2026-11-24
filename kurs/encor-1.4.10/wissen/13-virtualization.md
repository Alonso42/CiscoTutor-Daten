# Introducing Virtualization Protocols and Techniques

Quelle: ENCOR 1.4.10 Student Guide, Seiten 128–135 (135 = Summary-Video; Summary Challenge und Answer Key nicht ausgewertet)
Topics: ENCOR-2.1.a (Hypervisor Typ 1/2), ENCOR-2.1.b (Virtual Machine), ENCOR-2.1.c (Virtual Switching), ENCOR-2.2.a (VRF), ENCOR-2.2.b (GRE/IPsec-Tunneling)

Hinweis: Abschnitte mit "(Ergänzung)" stehen nicht im Kurs, sondern stammen aus Cisco-Doku/RFCs bzw. dem Prüfprotokoll (Hypervisor-Typen, Container, NFV, Multi-AF-VRF-Syntax, Route Leaking, GRE-Keepalives, Rekursion, MTU/MSS, GRE-Headerformat).

## 1. Server-Virtualisierung (S. 128)

### Ausgangslage
- Klassisch: ein Betriebssystem pro physischem Server und eine Anwendung pro Betriebssystem → stabil (keine Kompatibilitätsprobleme), aber teuer. Viele Anwendungen = viele Server.
- Kursbeispiel Collaboration: früher lief Cisco Unified CM auf eigener Hardware mit gehärtetem Linux; ein Server = ein Cluster-Knoten.
- Ohne Virtualisierung greift das OS direkt auf alle Ressourcen zu (CPU, RAM, Storage, NICs).
- Unterauslastung: Ein Server läuft oft mit < 20 % CPU → ca. 80 % liegen brach; jeder zusätzliche Server kostet Platz, Strom, Kühlung und Verwaltung.
- Konsolidierung (Kursgrafik): E-Mail 20 % + Web 40 % + Datenbank 10 % auf drei Servern → zusammen 70 % auf einem Host mit Hypervisor. Zwölf und mehr VMs auf einem Host sind üblich.

### Hypervisor
- Softwareschicht zwischen Hardware und Betriebssystemen; schlankes OS plus Software, um VMs anzulegen, zu ändern, zu löschen und zu verschieben. Der Kurs nutzt VMware ESXi (vSphere).
- Aufgaben: Hardware-Ressourcen aufteilen (CPU, RAM, Disk, Netzwerk), Verbindung VM↔VM und VM↔außen herstellen, VMs voneinander trennen.
- Die Komponente, die Anweisungen einer VM an die echte Hardware weiterreicht, heißt **Virtual Machine Monitor (VMM)**.
- Ein Hypervisor verwaltet nur VMs, keine Anwendungen innerhalb der VMs.
- Vorteile: einheitliche virtuelle Hardware (Server verschiedener Hersteller sehen für das Gast-OS gleich aus), unabhängige Ressourceneinheiten, mehrere (auch verschiedene) Betriebssysteme gleichzeitig, schnellere Bereitstellung, bessere Auslastung.

### Hypervisor-Typen und Container (Ergänzung, ENCOR 2.1.a)
| Modell | Was liegt unter der Workload? | Beispiel |
|---|---|---|
| Typ 1 (bare metal, native) | Hypervisor direkt auf der Hardware | VMware ESXi, Microsoft Hyper-V, KVM |
| Typ 2 (hosted) | Hypervisor als Anwendung auf einem Host-OS | VirtualBox, VMware Workstation/Fusion |
| Container | kein Hypervisor; gemeinsamer Kernel des Host-OS, nur App + Bibliotheken | Docker auf Linux |
- Typ 1 ist im Rechenzentrum Standard (wenig Overhead, besser isoliert); Typ 2 typisch für Labor/Laptop.
- Container sind klein und starten in Sekunden, teilen sich aber den Kernel → ein Linux-Host kann keine Windows-Container mit eigenem Kernel betreiben; Isolation schwächer als bei VMs.

### Virtuelle Maschine (S. 128)
- Logischer Container mit allem, was ein OS braucht: vCPU, vRAM, Disk, vNIC (und z. B. Grafikadapter).
- CPU/RAM sind Anteile der Host-Ressourcen; die virtuelle Festplatte ist eine speziell formatierte Datei auf dem Datastore; die vNIC ist eine vom Hypervisor simulierte Komponente.
- Das Gast-OS merkt nicht, dass es virtualisiert ist, hat aber keine volle Kontrolle über die Hardware.
- Jede VM hat eigene Identität: MAC-Adresse (in der VM-Konfigurationsdatei einstellbar), IP-Adresse, CPU-, RAM- und Plattenanteil.

### vNIC und vSwitch (S. 128, ENCOR 2.1.c)
- Ausnahme zum "direkten Durchreichen": Die vNIC hängt nicht an einem physischen Port, sondern an einem **virtuellen Switch** im Host; der vSwitch hat **Uplinks** zu den physischen NICs (meist 802.1Q-Trunks zum physischen Switch).
- VMs in derselben Port Group/VLAN auf demselben Host tauschen Frames direkt im vSwitch aus, ohne den Uplink. Zwischen VLANs ist ein Router (L3) nötig.
- (Ergänzung) Standard vSwitch = pro Host konfiguriert; Distributed vSwitch = zentral über vCenter für viele Hosts; Cisco-Varianten historisch Nexus 1000V.

### Sizing (Rechenbeispiel, S. 128)
- Host mit 2 × 12 Kernen = 24 Kerne. Ohne Überbuchung (Collaboration-Vorgabe: physische Ressourcen nicht überbuchen): 24 VMs mit je 1 vCPU, **oder** eine VM mit 20 vCPU + zwei VMs mit je 2 vCPU (20 + 2 + 2 = 24) – mehr nicht.

### Verwaltung
- Einzelner Host: vSphere Client (früher Windows-Programm) bzw. VMware Host Client im Browser.
- Zentral: **vCenter Server** verwaltet viele Hosts und VMs; Voraussetzung für vMotion, Distributed Switch, Lastverteilung und CPU-Kompatibilitätsfunktionen. vCenter läuft als physischer Server oder als VM; ab vSphere 5.0 auch als Linux-Appliance.
- Kurs (UC-spezifisch, Stand des Kursmaterials): UC-Virtualisierung ab ESXi 4.0 / UC 8.0; Hyper-V, Xen, KVM seien für Collaboration nicht unterstützt.

### NFV (Ergänzung)
- Network Functions Virtualization: Netzfunktionen als VNF auf Standard-x86-Hardware, z. B. Catalyst 8000V (Router), ASAv (Firewall), Catalyst 9800-CL (WLC); Cisco NFVIS (Linux/KVM-basiert) hostet VNFs auf ENCS, UCS oder C8300-uCPE.

## 2. Bedarf für Netzwerkvirtualisierung (S. 129)
- Netzwerkvirtualisierung = logisch isolierte Partitionen über einer gemeinsamen physischen Infrastruktur. Jede Partition verhält sich wie ein eigenes Netz: eigene Sicherheit, Policies, Service Level und eigenes Routing.
- Policies werden zentral am Rand der Partition (VPN-Perimeter) durchgesetzt → Nutzer hinzufügen/entfernen erfordert keine Policy-Änderung; Vorteil mehrerer Netze ohne deren Betriebskosten (OPEX).
- Szenarien: Gastzugang (nur Internet, keinerlei Zugriff auf interne Ressourcen), Partnerzugang (Internet plus Teil der internen Ressourcen), IT als Service Provider für mehrere "Kunden" (z. B. Kiosk/Hotspot im Handel), mandantenfähige Netze.
- Architektur aus drei Komponenten:

| Komponente | Wo | Aufgabe |
|---|---|---|
| Access Control | Branch, Campus (Rand) | Gerät/Benutzer authentisieren und autorisieren, einer Partition zuordnen (VLAN, ACL), Unbefugte abweisen |
| Path Isolation | WAN, MAN, Campus | Verkehr über die L3-Infrastruktur getrennt halten (VRF, GRE, MPLS), L3-Pfade auf VLANs an Access und Services Edge abbilden |
| Services Edge | Data Center, Internet Edge, Campus | Zugang zu gemeinsamen und dedizierten Diensten, Policy pro Partition, isolierte Anwendungsumgebungen |
- Path-Isolation-Mechanismen laut Kurs: dynamische ACLs, VRF-Lite + GRE, MPLS VPN (Vorteil MPLS: dynamisches Any-to-Any ohne viele Punkt-zu-Punkt-Tunnel).

## 3. Path Isolation (S. 130)
- Ziel: Skalierbarkeit, Ausfallsicherheit und Sicherheit des nicht segmentierten Netzes erhalten oder verbessern.
- Ein hierarchisches Netz besteht aus L2- und L3-Domänen → beide virtualisieren und aufeinander abbilden:
  - **Device Virtualization**: im Gerät – L2 per VLAN, L3 per VRF.
  - **Data Path Virtualization**: die Verbindungen zwischen Geräten.
- VRF = Instanz in einem L3-Gerät mit eigener Routing-Tabelle, Forwarding-Tabelle und zugewiesenen Interfaces; Routingprotokolle (OSPF, EIGRP, BGP, RIPv2) pro VRF → "virtuelle Router" im selben Switch/Router. Ziel: L2-VLAN auf ein L3-VPN mit eigener Control Plane abbilden.

### Data Path Virtualization
| Abstand der VRFs | Technik | Trennung auf der Leitung | Typischer Einsatz |
|---|---|---|---|
| direkt verbunden (Hop-by-Hop) | VRF-Lite End-to-End, EVN | 802.1Q-Tag bzw. VNET-Tag pro VRF | Campus unter eigener Kontrolle mit OSPF/EIGRP als IGP |
| mehrere Hops über IP (Multihop) | VRF-Lite oder EVN + GRE/mGRE | ein Tunnel pro VRF | über einen nicht virtualisierten L3-Bereich oder ein Provider-WAN |
| Multihop | MPLS VPN | MPLS-Label | große Unternehmen, > 32 virtuelle Netze pro Gerät, Traffic Engineering, Fast Reroute, skalierbares Full Mesh |

### Zwei Ebenen pro Gerät
- **Control Plane**: Protokolle, Datenbanken, Tabellen für Topologie und Weiterleitungsentscheidungen – jedes virtuelle Netz braucht sein eigenes Topologiebild.
- **Forwarding Plane**: die Weiterleitungstabellen, die die Control Plane aufbaut – pro virtuellem Netz eine eigene.
- Virtualisierung je OSI-Schicht: Ein Gerät kann VLAN-aware sein, aber nur eine Routing-Tabelle haben → nur L2 virtualisiert (reicht z. B. im Wiring Closet). Eine virtuelle Firewall braucht L2-, L3- und L4-Virtualisierung plus eigene Dienste pro Kontext.

## 4. VRF und VRF-Lite (S. 131)
- Eine VRF besteht aus: IP-Routing-Tabelle, daraus abgeleiteter Forwarding-Tabelle (CEF-FIB), Interfaces, die diese Tabelle nutzen, und Regeln/Routingprotokollen, die bestimmen, was hineinkommt.
- VRF ohne MPLS = **VRF-Lite**.
- Vorteile:
  - echte Trennung von Routing und Forwarding: zwischen VRFs fließt nichts, solange es nicht ausdrücklich konfiguriert wird (Route Leaking) → zusätzliche Sicherheit; überlappende Adressen in verschiedenen VRFs möglich.
  - einfachere Verwaltung und Fehlersuche, da eigene Tabellen; das Overlay erzeugt keine Probleme (z. B. Routing-Schleifen) in der globalen Tabelle.
  - **alternative Default-Routen** pro VRF: z. B. Gäste direkt ins Internet ohne Web-Proxy-Konfiguration im Browser, während die globale Default-Route ins Leere zeigt (Blackhole), um Wurm-Scans auf unbekannte Ziele sichtbar zu machen.
- VLAN-zu-VRF-Abbildung: einfach das SVI des VLANs (am Distribution-Switch) in die VRF legen; ebenso Tunnel-Interfaces.

### Syntax (Legacy wie im Lab vs. Multi-AF – Ergänzung)
| Schritt | Legacy (`ip vrf`, nur IPv4) | Multi-AF (`vrf definition`) |
|---|---|---|
| VRF anlegen | `ip vrf CUST-A` | `vrf definition CUST-A` + `address-family ipv4` (und/oder `ipv6`) |
| Interface zuweisen | `ip vrf forwarding CUST-A` | `vrf forwarding CUST-A` |
| danach | IP-Adresse neu eingeben | IP-Adresse neu eingeben |
| Übersicht | `show ip vrf`, `show ip vrf interfaces` | `show vrf` |
- Beim Zuweisen entfernt IOS die IP-Adresse: `% Interface Ethernet0/0 IPv4 disabled and address(es) removed due to enabling VRF CUST-A`.
- Ein Route Distinguisher (RD) ist für reines VRF-Lite nicht nötig (`Default RD <not set>`).
- Route Leaking (Ergänzung): `ip route vrf GUEST 0.0.0.0 0.0.0.0 203.0.113.1 global` – Route steht in der VRF-Tabelle, der Next Hop wird in der globalen Tabelle aufgelöst.

## 5. Discovery 15 – VRF-Lite (S. 132)
- Topologie: ISP-Router in der Mitte; Kunde A (CUST-A-SITE1 an Et0/0, CUST-A-SITE2 an Et0/1) und Kunde B (CUST-B-SITE1 an Et0/2, CUST-B-SITE2 an Et0/3).
  - Transfernetze: 172.16.1.16/28 (A-SITE1 .17, ISP .18), 172.16.2.16/28 (A-SITE2 .17, ISP .18), 172.16.1.32/28 (B-SITE1 .33, ISP .34), 172.16.2.32/28 (B-SITE2 .33, ISP .34) – dieselben ISP-Adressen kommen in beiden Kunden-VRFs paarweise vor.
  - Kunde A: Site 1 Loopbacks 10.0.1.49/32 und 10.0.1.17/28 (Area 1), Site 2 10.0.1.50/32 und 10.0.1.33/28 (Area 2); Kunde B analog 10.0.2.x. Transfernetze in Area 0 (OSPFv2).
  - Nur der ISP-Router hat VRFs; die Kundenrouter fahren normales OSPF ohne VRF.
```
ip vrf CUST-A
ip vrf CUST-B
interface Ethernet0/0
 ip vrf forwarding CUST-A
 ip address 172.16.1.18 255.255.255.240
router ospf 100 vrf CUST-A
 router-id 0.0.0.100
 network 172.16.0.0 0.0.255.255 area 0
router ospf 200 vrf CUST-B
 router-id 0.0.0.200
 network 172.16.0.0 0.0.255.255 area 0
```
- Pro VRF ein eigener OSPF-Prozess mit eindeutiger Prozess-ID; Router-ID manuell setzen (sonst wählt jeder Prozess selbst, ggf. doppelt). Ein globaler `router ospf 1` erfasst keine VRF-Interfaces.
- Verifikation:
```
ISP# show ip vrf
Name        Default RD   Interfaces
CUST-A      <not set>    Et0/0
                         Et0/1
CUST-B      <not set>    Et0/2
                         Et0/3
ISP# show ip vrf interfaces            ! Interface, IP, VRF, Protocol
ISP# show ip route                     ! global: leer (alle Interfaces in VRFs)
ISP# show ip route vrf CUST-A ospf
O IA  10.0.1.16/28 [110/11] via 172.16.1.17, Ethernet0/0
O IA  10.0.1.32/28 [110/11] via 172.16.2.17, Ethernet0/1
ISP# show ip protocols vrf CUST-A       ! Router-ID, Netze, Nachbarn des Prozesses
ISP# show ip ospf neighbor             ! Nachbarn aller Prozesse
ISP# ping vrf CUST-A 10.0.1.49
```
- `ping`/`traceroute` ohne `vrf` nutzen die globale Tabelle → schlagen fehl, obwohl die Route in der VRF existiert.
- Ping von Kunde A zu einem Netz von Kunde B scheitert: In VRF CUST-A gibt es keine Route → genau die gewünschte Isolation.
- Kunden-Routen erscheinen als O IA, weil die Kundennetze in Area 1/2 liegen und die Kundenrouter ABRs sind.

## 6. GRE (S. 133)
- Tunnelprotokoll: kapselt beliebige L3-Pakete (IPv4, IPv6, historisch IPX/AppleTalk) in IP; transportiert auch Multicast → Routingprotokolle (OSPF, EIGRP) können über den Tunnel laufen.
- **IP-Protokoll 47**. Keine Verschlüsselung, keine starke Sicherheit, zustandslos, keine Flusskontrolle.
- Drei Header-Rollen: **Passenger** (das transportierte Paket, z. B. IPv4/IPv6), **Carrier** (GRE-Header), **Transport/Delivery** (neuer äußerer IP-Header).
- Overhead: 20 Byte neuer IP-Header + 4 Byte GRE-Basisheader = **mindestens 24 Byte**. Optionale Felder je 4 Byte: Checksum (C-Bit, RFC 2784), Key (K-Bit) und Sequence Number (S-Bit) erst mit RFC 2890.
- GRE-Basisheader (Ergänzung, RFC 2784): C-Bit, Reserved0, Version (0), **Protocol Type** (EtherType des Passagiers, z. B. 0x0800 IPv4, 0x86DD IPv6).
- RFCs: 1701 (GRE), 1702 (GRE over IPv4), 2784 (heutiger Standard), 2890 (Key/Sequence-Erweiterung).
- Mit IPsec kombiniert (GRE over IPsec) für Vertraulichkeit, Integrität und Authentisierung; meist Hub-and-Spoke über unsichere WANs, um die Tunnelzahl pro Router klein zu halten. GRE liefert dabei Multicast/Routingprotokolle, IPsec den Schutz.

### MTU und MSS (Rechnen!)
| Kapselung | Overhead | `ip mtu` (bei 1500 außen) | `ip tcp adjust-mss` (MTU − 40) |
|---|---|---|---|
| GRE ohne Optionen | 24 Byte | 1476 | 1436 |
| GRE + Key | 28 Byte | 1472 | 1432 |
| GRE + Key + Checksum + Sequence | 36 Byte | 1464 | 1424 |
| GRE over IPsec (übliche Empfehlung) | variabel | 1400 | 1360 |
- 40 = 20 Byte IP- + 20 Byte TCP-Header. Zu große Pakete mit DF-Bit werden verworfen; wenn ICMP "fragmentation needed" gefiltert ist, scheitert Path MTU Discovery (typisch: Ping geht, große Downloads hängen).
- Kurs: MTU muss auf beiden Seiten passen. GRE selbst handelt keine MTU aus; zwingend wird es, wenn OSPF über den Tunnel läuft (OSPF prüft die MTU im DBD-Austausch → Mismatch hängt in EXSTART/EXCHANGE).

## 7. Discovery 16 – GRE-Tunnel (S. 134)
- Topologie: R1 – R2 – R3 – R4 in Reihe. R1: Et0/0 10.10.1.1 (zu R2 10.10.1.2), Et0/1 172.16.1.1/24, Lo0 172.16.11.1. R4: Et0/0 10.10.3.2, Et0/1 172.16.4.1/24, Lo0 172.16.14.1. R2/R3 (Lo0 10.10.12.1 bzw. 10.10.13.1) sprechen EIGRP nur für 10.0.0.0/8; R1 und R4 haben eine statische Route 10.0.0.0/8 Richtung Transit.
- Transit-Router kennen 172.16.0.0/16 nicht → ohne Tunnel keine Verbindung zwischen den 172.16-Netzen.
```
R1(config)# interface Tunnel0
R1(config-if)# ip address 172.16.99.1 255.255.255.0
R1(config-if)# tunnel source 10.10.1.1          ! oder Interface/Loopback
R1(config-if)# tunnel destination 10.10.3.2
! tunnel mode gre ip ist Default
R4: ip address 172.16.99.2 255.255.255.0, tunnel source 10.10.3.2, tunnel destination 10.10.1.1
```
- Minimal: `tunnel source` + `tunnel destination` (+ IP-Adresse für das Tunnelnetz). Source/Destination müssen spiegelbildlich und gegenseitig erreichbar sein; Loopbacks als Endpunkte möglich.
- Ohne Keepalives ist das Line Protocol **up**, sobald die Quelle up ist und eine Route zum Tunnelziel existiert – auch wenn die Gegenseite falsch oder gar nicht konfiguriert ist.
```
R4# show interface Tunnel0
Tunnel0 is up, line protocol is up
  Hardware is Tunnel
  Internet address is 172.16.99.2/24
  MTU 17916 bytes, BW 100 Kbit/sec, DLY 50000 usec      ! MTU-Wert IOL-spezifisch
  Keepalive not set
  Tunnel source 10.10.3.2, destination 10.10.1.1
  Tunnel protocol/transport GRE/IP
```
- Weitere Kontrolle: `show ip interface brief tunnel 0`; `show ip route` zeigt 172.16.99.0/24 connected via Tunnel0.
- OSPF über den Tunnel (`router ospf 1`, `router-id 0.0.0.4`, `network 172.16.0.0 0.0.255.255 area 0`): Nachbar auf Tunnel0 im Zustand `FULL/  -` (Netzwerktyp point-to-point, keine DR-Wahl, Priorität 0 angezeigt).
```
R1# show ip route ospf
O  172.16.4.0/24 [110/1010] via 172.16.99.2, Tunnel0
O  172.16.14.1/32 [110/1001] via 172.16.99.2, Tunnel0
```
- Kostenrechnung: Tunnel-Default-Bandbreite 100 kbit/s (aktuelles IOS/IOS XE; sehr alte IOS-Versionen vor ca. 2007 nutzten 9 kbit/s → OSPF-Kosten 11111; der Wert ist nur eine Metrik, keine Drosselung, per `bandwidth` am Tunnel änderbar) → 100 000 kbit/s / 100 kbit/s = **1000**; + Ethernet 10 Mbit/s (IOL) = 10 → 1010; + Loopback 1 → 1001. Die Loopback erscheint als /32 (OSPF-Netzwerktyp loopback), obwohl sie als /24 konfiguriert ist.
- Traceroute von R1 zu 172.16.14.1 zeigt **einen** Hop: die Tunnel-IP von R4 (172.16.99.2), weil das Port-Unreachable vom Eingangs-Interface (Tunnel0 von R4) kommt; R2/R3 sind unsichtbar (Prüfprotokoll).

### GRE-Erweiterungen und Fehlerbilder (Ergänzung)
- Keepalives: `keepalive 10 3` (Default-Periode 10 s, 3 Retries, standardmäßig aus) → Line Protocol geht down, wenn die Gegenseite nicht antwortet. Funktioniert auch, wenn die Gegenseite selbst keine Keepalives konfiguriert hat (sie reflektiert die Pakete einfach).
- `tunnel key <n>`: muss beidseitig gleich sein; Mismatch fällt ohne Keepalives nicht auf (Line Protocol bleibt up, Verkehr geht verloren).
- **Rekursives Routing**: Wird das Tunnelziel über den Tunnel selbst gelernt (z. B. weil OSPF auch die Underlay-Netze über den Tunnel annonciert), meldet IOS `%TUN-5-RECURDOWN: Tunnel0 temporarily disabled due to recursive routing` und der Tunnel flappt. Abhilfe: Underlay nicht ins Tunnel-IGP aufnehmen, spezifische statische Route zum Tunnelziel, getrennte Routing-Prozesse.
- VRF und Tunnel: `tunnel vrf X` legt fest, in welcher Tabelle Source/Destination aufgelöst werden (Underlay); `vrf forwarding Y` am Tunnelinterface legt fest, zu welcher VRF der getunnelte Verkehr gehört (Overlay).
- mGRE (multipoint GRE) + NHRP = Basis von DMVPN (Kapitel 14).

## Fehler/Ungenauigkeiten im Kurs
- S. 130: "The VRF is defined as a networking device …" – eine VRF ist kein Gerät, sondern eine Routing-/Forwarding-Instanz innerhalb eines Geräts (siehe S. 131 im selben Kurs).
- S. 132: Ping-Ausgaben vertauscht (Copy-Paste): Bei `ping 10.0.2.50` steht "Sending … to 10.0.2.49", bei `ping 10.0.1.49` steht "to 10.0.1.50".
- S. 132: `show ip protocols vrf` auf dem ISP-Router zeigt "It is an area border router", obwohl der ISP nur in Area 0 ist (IOL-Eigenheit, verwirrend).
- S. 133: "GRE-Header enthält Flags inkl. Checksum/Key/Sequence" – nach RFC 2784 gibt es nur das C-Bit; K und S kommen erst mit RFC 2890 (Prüfprotokoll, Korrektur slg-vr-102).
- S. 133: "MTU muss auf beiden Seiten passen" – keine GRE-Anforderung, sondern Empfehlung; zwingend nur, wenn z. B. OSPF über den Tunnel die MTU prüft.
- S. 128: vSphere Client für Windows als "ausgereiftere" Zugriffsmethode – veraltet: Der Windows-(C#-)Client wurde mit vSphere 6.5 eingestellt, heute HTML5-vSphere-Client bzw. Host Client im Browser. **(neu gefunden)**
- S. 128: Aussagen zur UC-Virtualisierung (nur ESXi, Hyper-V/Xen/KVM nicht unterstützt) spiegeln den Stand des Kursmaterials; Cisco hat die unterstützten Plattformen für Collaboration inzwischen erweitert – nicht prüfungsrelevant, nicht als ENCOR-Fakt verwenden. **(neu gefunden, Unsicherheit)**
- Prüfprotokoll: Traceroute durch den Tunnel zeigt die Tunnel-IP 172.16.99.2 des Ziel-Routers als einzigen Hop, nicht die Loopback-Adresse (Korrektur slg-vr-097).

## Bilder
- `bilder/13-virtualization/01-hypervisor.svg` – Klassischer Server vs. Typ-1-, Typ-2-Hypervisor und Container als Schichtenmodell.
- `bilder/13-virtualization/02-konsolid.svg` – Konsolidierung 20 % + 40 % + 10 % = 70 % und vCPU-Sizing 20 + 2 + 2 = 24.
- `bilder/13-virtualization/03-vswitch.svg` – VMs mit vNICs am vSwitch, Uplink als 802.1Q-Trunk, lokale Zustellung im selben VLAN.
- `bilder/13-virtualization/04-netvirt.svg` – Drei Komponenten Access Control, Path Isolation, Services Edge.
- `bilder/13-virtualization/05-pathiso.svg` – Hop-by-Hop (802.1Q) vs. Multihop (GRE, MPLS) für VRF-Trennung.
- `bilder/13-virtualization/06-vrf-lite.svg` – Discovery-15-Topologie mit zwei Kunden-VRFs und OSPF-Prozessen am ISP.
- `bilder/13-virtualization/07-gre-header.svg` – GRE-Kapselung: Transport-IP, GRE-Header, Passagier, mit Byte-Angaben und optionalen Feldern.
- `bilder/13-virtualization/08-gre-lab.svg` – Discovery-16-Topologie: Tunnel R1–R4 über R2/R3, äußerer und innerer Header.
- `bilder/13-virtualization/09-gre-mtu.svg` – MTU/MSS-Rechnung für GRE-Varianten.
- `bilder/13-virtualization/10-gre-fehler.svg` – Typische GRE-Fehler: Rekursion, fehlende Keepalives, Key-Mismatch, MTU.
