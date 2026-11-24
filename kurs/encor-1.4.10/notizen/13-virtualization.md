# Kapitel 13: Introducing Virtualization Protocols and Techniques (Kursseiten 128–134)

## 128 Server Virtualization
- Klassisch: ein OS pro physischem Server, eine Anwendung pro OS → stabil, aber teuer, schlecht ausgelastet (Beispiel: CUCM 7.x auf MCS 7800 mit gehärtetem Linux, 1 Server = 1 Cluster-Knoten).
- Ohne Virtualisierung: OS greift direkt auf alle Ressourcen zu (z. B. alle 4 Kerne).
- Virtualisierung: Softwareschicht (Hypervisor) zwischen Hardware und OS. Hypervisor = schlankes OS + Software zum Erstellen/Verwalten der VMs. Kurs nutzt VMware ESXi (vSphere).
- VM bekommt vCPU, RAM, Disk, vNIC – Gast-OS merkt nichts von der Virtualisierung. Hypervisor reicht Anfragen an die physischen Ressourcen weiter.
- Ausnahme vNIC: hängt nicht direkt am physischen Port, sondern an einem vSwitch; vSwitch hat Uplinks zu den physischen NICs.
- Vorteile: einheitliche virtuelle Hardware (Server verschiedener Hersteller sehen fürs OS gleich aus), Aufteilung in unabhängige Ressourceneinheiten, mehrere (auch verschiedene) OS gleichzeitig; Konsolidierung, bessere Auslastung, Ressourcenteilung, schnellere Bereitstellung.
- Unterauslastung: z. B. CUCM < 20 % CPU → 80 % ungenutzt; mehr Server = mehr Platz, Strom, Kühlung, Management. 12+ Server auf einer Hardware nicht ungewöhnlich.
- Rechenbeispiel: 24 Kerne (2×12). 24 VMs à 1 vCPU möglich; braucht eine App 20 vCPUs und die anderen je 2 → nur 3 VMs (20+2+2). Collaboration-Apps: physische Ressourcen nicht überbuchen.
- Hypervisor = Abstraktionsschicht, steuert Hardware, verwaltet VMs (create/modify/destroy/move); nur für VMs, nicht für Anwendungen. Komponente, die Befehle der VM an die Hardware weitergibt: Virtual Machine Monitor (VMM).
- Hypervisor-Aufgaben: Ressourcen partitionieren, Konnektivität VM↔VM und VM↔extern, Trennung der VMs.
- UC-Virtualisierung ab ESXi 4.0 / UC 8.0; aktuell meist ab ESXi 5.0; Hyper-V, Xen, KVM für Collaboration nicht unterstützt (Kurs).
- VM = logischer Container mit allen Ressourcen; CPU/RAM = Anteil der Host-Ressourcen; Disk = speziell formatierte Datei; vNIC = vom Hypervisor simulierte Komponente. Identifier (z. B. MAC) in der VM-Konfigurationsdatei einstellbar.
- Zugriff: vSphere Client (Windows) bzw. VMware Host Client direkt auf Host; vCenter für zentrale Verwaltung; vMotion, Distributed Switch, Load Balancing, CPU-Kompatibilität brauchen vCenter. vCenter als physischer Server oder VM; ab vSphere 5.0 Linux-Appliance.

## 129 Need for Network Virtualization
- Network virtualization = logisch isolierte Partitionen über gemeinsamer physischer Infrastruktur; jede Partition wie eigenes Netz (Privacy, Security, Policies, Service Level, eigenes Routing).
- Policies zentral am VPN-Perimeter durchgesetzt → Nutzer hinzufügen/entfernen ohne Policy-Änderung; Vorteil mehrerer Netze ohne deren OPEX.
- Szenarien: Gastzugang (nur Internet), Partnerzugang (Internet + Teil interner Ressourcen), IT als Service Provider (Retail-Kiosk, Hotspot).
- Architektur, drei Komponenten: Access Control (Authentisierung/Autorisierung am Edge, Zuordnung zu Segment/VLAN), Path Isolation (Overlay, getrennte logische Pfade), Services Edge (zentrale Policy-Durchsetzung zwischen Partitionen / zu gemeinsamen Diensten).
- Path-Isolation-Mechanismen: dynamische ACLs, VRF-Lite + GRE, MPLS VPN. MPLS-VPN-Vorteil: dynamisches Any-to-Any ohne viele P2P-Tunnel.

## 130 Path Isolation Overview
- Ziel: Skalierbarkeit, Resilienz, Sicherheit erhalten/verbessern.
- Hierarchisches Netz = L2- und L3-Domänen; beide virtualisieren und aufeinander abbilden: device virtualization + data path virtualization.
- Device virtualization: VLANs (L2), VRF (L3). VRF = eigene Routing-Tabelle, Forwarding-Tabelle, Interfaces; Routingprotokolle OSPF, EIGRP, BGP, RIPv2 je VRF. VRF ≈ virtueller Router im Gerät.
- Data path virtualization: Hop-by-Hop: VRF-Lite End-to-End bzw. EVN mit 802.1Q/VNET-Tag. Multihop: VRF-Lite oder EVN + GRE/mGRE; MPLS VPN (Labels).
- VRF-Lite + 802.1Q: Campus, eigenes IGP (OSPF/EIGRP). VRF-Lite + GRE/mGRE: über L3-Domäne ohne Virtualisierung bzw. SP-WAN außerhalb eigener Kontrolle.
- MPLS: große Unternehmen, > 32 virtuelle Netze pro Gerät, Traffic Engineering, Fast Reroute, skalierbares Full Mesh.
- Zwei Ebenen virtualisieren: Control Plane (Protokolle, Datenbanken, Topologiebild) und Forwarding Plane (Forwarding-Tabellen aus der Control Plane).
- Virtualisierung je OSI-Schicht: VLAN-aware aber eine Routing-Tabelle = nur L2 virtualisiert (z. B. Wiring Closet reicht). Virtuelle Firewall: L2–L4 (+ ggf. L7).
- Kursungenauigkeit: "The VRF is defined as a networking device…" – eine VRF ist kein Gerät, sondern eine Instanz in einem Gerät.

## 131 Introducing VRF
- VRF = Routing-Tabelle + abgeleitete Forwarding-Tabelle + Interfaces + Regeln/Routingprotokolle.
- VRF-Lite-Vorteile: echte Trennung von Routing und Forwarding (kein Verkehr zwischen VRFs ohne explizite Konfiguration); einfachere Verwaltung/Fehlersuche, keine Loops im globalen Table durch Overlay; alternative Default-Routen pro VRF (z. B. Gäste direkt ins Internet ohne Proxy, global Default als Blackhole gegen Wurm-Scans).
- VLAN→VRF-Mapping: SVI am Distribution-Switch in VRF legen; gleiches Prinzip für Tunnel-Interfaces.

## 132 Discovery 15 VRF-Lite (Lab)
- Topologie: CUST-A-SITE1/2 und CUST-B-SITE1/2 an ISP (Et0/0, Et0/1 → A; Et0/2, Et0/3 → B). Kunden nutzen OSPF ohne VRF; VRFs nur auf ISP.
- Lab nutzt LEGACY-Syntax: `ip vrf CUST-A`, Interface `ip vrf forwarding CUST-A` → Meldung "% Interface Ethernet0/0 IPv4 disabled and address(es) removed due to enabling VRF CUST-A" → IP neu setzen.
- `show ip vrf`: Name, Default RD (<not set>), Interfaces. `show ip vrf interfaces`: Interface, IP, VRF, Protocol.
- Globale `show ip route` danach leer; `show ip route vrf CUST-A connected`.
- `ping vrf CUST-A 172.16.1.17` – ping ohne vrf nutzt globale Tabelle.
- `router ospf 100 vrf CUST-A`, `router-id 0.0.0.100`; `router ospf 200 vrf CUST-B`; eindeutige Prozess-ID je VRF; Router-ID manuell empfohlen.
- `show ip ospf neighbor` zeigt Nachbarn aller Prozesse; `show ip protocols vrf CUST-A`; `show ip route vrf CUST-A ospf` (O IA 10.0.1.x via ...).
- Ping CUST-A → CUST-B scheitert = Isolation.
- Kursfehler: Ausgabe bei `ping 10.0.2.50` zeigt "Sending ... to 10.0.2.49"; bei `ping 10.0.1.49` steht "to 10.0.1.50" (Copy-Paste). `show ip protocols vrf` zeigt "It is an area border router" bei nur 1 Area (IOL-Ausgabe, verwirrend).
- VRF-Komponenten im Lab: RIB, CEF-FIB, eigene Routingprotokoll-Instanz. VRF ohne MPLS = VRF-Lite.

## 133 Introducing GRE
- Tunnelprotokoll, transportiert IP, (historisch IPX, AppleTalk), Multicast → Routingprotokolle über Tunnel.
- IP-Protokoll 47; keine Verschlüsselung.
- Overhead: 20 Byte neuer IP-Header (Delivery Header) + 4 Byte GRE-Header = mind. 24 Byte. GRE-Header: Flags, Protocol Type; optional Checksum, Key, Sequence Number.
- GRE + IPsec für Authentisierung/Vertraulichkeit/Integrität; GRE over IPsec meist Hub-and-Spoke.
- RFC 1701, 1702, 2784.
- Header: Passenger (IPv4/IPv6), Carrier (GRE), Transport (IP).
- Stateless, keine Flow Control, keine starke Sicherheit.
- MTU ggf. mit `ip mtu` anpassen; Kurs: "muss auf beiden Seiten passen" (eher Empfehlung).

## 134 Discovery 16 GRE (Lab)
- R1 (Et0/0 10.10.1.1, Et0/1 172.16.1.1, Lo0 172.16.11.1) – R2 – R3 – R4 (Et0/0 10.10.3.2, Et0/1 172.16.4.1, Lo0 172.16.14.1). R2/R3: EIGRP für 10/8. R1/R4: statische 10.0.0.0/8.
- Tunnel0: R1 172.16.99.1/24, R4 172.16.99.2/24. `interface tunnel0`, `ip address`, `tunnel source 10.10.1.1`, `tunnel destination 10.10.3.2`; `tunnel mode gre ip` ist Default.
- Minimal: Source + Destination (+ IP-Subnetz für Tunnel). Symmetrisch erreichbare Adressen, Loopbacks möglich.
- Line protocol up, sobald Route zum Tunnelziel existiert (ohne Keepalive).
- Verifikation: `show ip interface brief tunnel 0`, `show interface tunnel 0` (Hardware is Tunnel, MTU 17916 (IOL), BW 100 Kbit/sec, DLY 50000 usec, Keepalive not set, Tunnel source/destination, Tunnel protocol/transport GRE/IP), `show ip route` (172.16.99.0/24 connected via Tunnel0).
- Transit R2/R3 kennen 172.16/16 nicht – sehen nur 10.10.1.1 ↔ 10.10.3.2.
- OSPF über Tunnel: `router ospf 1`, `router-id 0.0.0.4`, `network 172.16.0.0 0.0.255.255 area 0` → Nachbar auf Tunnel0, `FULL/ -`, Pri 0 (point-to-point). Routen: 172.16.4.0/24 [110/1010], 172.16.14.1/32 [110/1001] via 172.16.99.2 (Tunnelkosten 1000 = 100 Mbit Ref / 100 Kbit).

## Eigenes Wissen (nicht im Kurs, für Fragen genutzt)
- Hypervisor Typ 1/2, Container, NFV, `vrf definition`/`address-family ipv4`, `show vrf`, Route Leaking, Keepalives (`keepalive 10 3`), Recursive Routing, `ip mtu 1400` / `ip tcp adjust-mss 1360`, `tunnel vrf`, `tunnel key`, GRE-Protocol-Type 0x0800.
