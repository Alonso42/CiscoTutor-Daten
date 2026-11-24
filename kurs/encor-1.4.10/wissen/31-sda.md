# Examining the Cisco SD-Access Solution

Quelle: ENCOR 1.4.10 Student Guide, Seiten 349–357 (348 Intro, 358 Summary Challenge und 359 Answer Key nicht ausgewertet)

Topics: ENCOR-1.3.a (SD-Access: Control- und Data-Plane-Elemente – Hauptthema), ENCOR-1.3.b (traditionelles Campus-Netz im Zusammenspiel mit SD-Access), ENCOR-2.3.a (LISP allgemein), ENCOR-2.3.b (VXLAN allgemein), ENCOR-5.4.d (TrustSec als Policy Plane – nur SD-Access-spezifische Aspekte; TrustSec-Grundlagen stehen in Kapitel 29).

Ergänzungen, die nicht im Kurs stehen, sind mit *(Ergänzung)* markiert. Quellen dafür: Cisco SD-Access Solution Design Guide (CVD), Cisco Catalyst Center SD-Access Configuration Guide 2.3.x, RFC 7348 (VXLAN), RFC 9300/9301 (LISP, ersetzen RFC 6830/6833), IETF draft-smith-vxlan-group-policy (VXLAN-GPO).

### Produktname

| Alter Name (im Kurs) | Aktueller Name |
|---|---|
| Cisco DNA Center | Cisco Catalyst Center (seit 2023) |
| Cisco SD-Access / "Cisco Networking SD-Access" | Cisco SD-Access (in Catalyst Center: SD-Access-Fabric) |
| Security Group Tag | Scalable Group Tag (gleiches Konzept, SGT) |
| APIC-EM | abgekündigt, Vorgänger von DNA Center |

## Warum SD-Access (Seite 349)

Probleme klassischer Campus-Netze:
- **Netzbetrieb**: manuelle Box-für-Box-Konfiguration, fehleranfällig, langsam, kaum Vor-/Nachvalidierung. Einzelne Switches brauchen Stunden, Batches Wochen.
- **Sicherheit**: Segmentierung nur mit VLANs/VRFs und ACLs (IP/MAC-basiert, schwer zu pflegen); rollenbasierte Zugriffe nur mit End-to-End-TrustSec.
- **Operations**: viele Tools (LAN, WAN, DC getrennt), langsame Fehlerbehebung, wenig Sicht auf Endpunkte und Flows.
- **Wired/Wireless**: getrennte Policies, komplexes IP-Adressschema und DHCP, Host-Mobilität nur durch gestreckte VLANs.
- **Topologien**: Layer-2-Access (Looped Triangle/Square) erfordert STP-Tuning (Root/Priority passend zu HSRP/VRRP-Active, Root Guard usw.). VSS/StackWise/vPC (Multichassis-EtherChannel) entschärfen das. Routed Access ist einfacher, löst aber Mobilität nicht.

SD-Access löst: Host-Mobilität **ohne** gestreckte VLANs, Segmentierung **ohne** MPLS, rollenbasierte Policy **ohne** manuelles End-to-End-TrustSec, gemeinsame Policy für wired/wireless, Konsistenz über Campus/Branch.

Vorteile laut Kurs:
- Gestreckte Subnetze über das Overlay (ein Subnetz auf vielen Edge-Switches), Underlay ist Routed Access mit ECMP statt STP.
- Lokales Switching des WLAN-Verkehrs an der Edge (Anycast Gateway) statt Hairpin über den WLC.
- Catalyst Center als Single Pane of Glass (Automation, Kontext-Sicht, Troubleshooting).
- Jeder Dienst/jede Policy an jedem Port.
- Zwei Segmentierungsebenen: VN (=VRF) und SGT, für LAN und WLAN.
- Nahtlose Mobilität, Policy folgt dem Benutzer.

## Overview: Overlay, Underlay, Rollen (Seite 350)

**Overlay** = logische Topologie über einem beliebigen physischen Underlay, meist mit Kapselung (Tunnel). Beispiele: GRE/mGRE, MPLS, VPLS, IPsec, DMVPN, CAPWAP, LISP, OTV, DFA, ACI. Routingprotokolle wie OSPF/EIGRP/BGP sind KEINE Overlays.

**Underlay**: physische Switches/Router der Fabric, IP-Erreichbarkeit per Routingprotokoll zwischen allen Fabric-Knoten (Loopbacks = RLOCs). Endbenutzer-Subnetze sind NICHT Teil des Underlays. Empfohlen: gut designtes Layer-3-Fundament bis zur Access-Schicht.

**Overlay (Fabric)**: Virtualisierung durch Kapselung von Benutzerverkehr in IP-Tunnel, die an den Fabric-Grenzen beginnen/enden: Border (Ein-/Ausgang), Edge (wired), Fabric AP (wireless). Außerhalb der Fabric bleibt Virtualisierung mit VRF-Lite oder MPLS VPN erhalten. Mehrere Overlays (VNs) über einem Underlay = Mandantenfähigkeit. Endgeräte wissen nichts vom Overlay.

### Underlay-Varianten

| | Manuelles Underlay | Automatisiertes Underlay (LAN Automation) |
|---|---|---|
| Voraussetzung | IP-Erreichbarkeit Edge↔Border↔Control Plane; L2 oder L3 (L3 empfohlen); beliebiges IGP (IS-IS empfohlen) | Standard-PnP-Bootstrap; Geräte neu/gelöscht; globaler "Underlay"-Adresspool |
| Zu beachten | MTU (Fabric-Header +50 Byte), Latenz RTT ≤ 100 ms (laut Kurs; Cisco-Quellen nennen 100 ms als Empfehlung für Catalyst Center ↔ Geräte bzw. ISE ↔ Fabric-Geräte, 200 ms als Maximum Catalyst Center ↔ Geräte) | PnP-Vorbereitung (Seed-Device), 100 % vorgegeben (nicht anpassbar) |

Warum IS-IS: Nachbarschaft ohne IP-Abhängigkeit (läuft direkt auf Layer 2, CLNS), Peering über Loopbacks möglich, behandelt IPv4/IPv6/Nicht-IP gleich, leicht zu automatisieren. LAN Automation erzeugt ein IS-IS-Routed-Access-Design und kann auch Underlay-Multicast konfigurieren (Details zu LAN Automation: Kapitel 30).

*(Ergänzung)* MTU: Catalyst Center/LAN Automation setzt im Underlay `system mtu 9100`; Cisco empfiehlt Jumbo Frames end-to-end, damit 1500-Byte-Clientframes plus VXLAN-Overhead nicht fragmentiert/verworfen werden. Mindestens 1550 Byte wären rechnerisch nötig.

```
! manuelles Underlay (Ausschnitt, Ergänzung)
system mtu 9100
interface Loopback0
 ip address 10.255.0.11 255.255.255.255
 ip router isis
router isis
 net 49.0001.0102.5500.0011.00
 is-type level-2-only
 metric-style wide
 passive-interface Loopback0
```

### Solution-Komponenten (Kursabbildung "Fabric Roles")

- **Catalyst Center Automation** (im Kurs: Cisco DNA Automation / Network Control Platform NCP): GUI, Intent-basierte Automation, Kontext-Austausch.
- **Catalyst Center Assurance** (Network Data Platform NDP): Datensammlung/Analyse von Endpunkt-zu-Applikation-Flows und Fabric-Zustand.
- **Identity Services**: NAC/ISE – dynamische Zuordnung Endpunkt→Gruppe, Policy-Definition.
- **Control Plane Node**: Map-System (Endpunkt↔Gerät).
- **Border Node**: verbindet externe L3-Netze mit der Fabric (z. B. Core).
- **Edge Node**: verbindet wired Endpunkte (z. B. Access-Switch).
- **Intermediate Node**: reiner Underlay-Router/Switch zwischen Fabric-Knoten; nicht fabric-aware, routet nur IP-Pakete (muss die größere MTU tragen).
- **Fabric WLC**: verbindet APs/Wireless-Endpunkte mit der Fabric (Control Plane).

## Fabric-Komponenten im Detail (Seite 351)

### Edge Node (≈ Access-Switch, Layer-3-Access)
- **Endpoint Registration**: erkannter Endpunkt → lokale EID-Tabelle → LISP **Map-Register** an Control Plane Node (füllt HTDB).
- **User→VN-Mapping**: Endpunkt landet über VLAN (statisch oder dynamisch per 802.1X/MAB) in einem VN; zusätzlich SGT-Zuweisung.
- **Anycast Layer-3-Gateway**: identische SVI (gleiche IP UND gleiche MAC) auf allen Edges eines Host Pools → optimale Weiterleitung, Mobilität ohne Gateway-Wechsel. Ähnlich HSRP/VRRP, aber auf allen Edges gleichzeitig aktiv.
- **LISP-Forwarding**: statt Routing-Lookup fragt die Edge beim Map-Resolver nach dem RLOC der Ziel-EID. Antwort → LISP Map-Cache → in CEF/Hardware. Kann nicht aufgelöst werden → Verkehr zum (externen/Default-)Border (Global Routing Table bzw. PETR).
- **Solicit-Map-Request (SMR)**: Erhält eine Edge Verkehr für einen Endpunkt, der nicht (mehr) lokal ist, schickt sie ein SMR an die sendende Edge, damit diese ihren Cache per neuem Map-Request aktualisiert (Fall Host-Umzug).
- **VXLAN Encap/Decap**: Edge = VTEP; Ziel-RLOC wird äußere Ziel-IP. Endpunkt kann umziehen, ohne seine Adresse zu ändern.

### Host Pools
- Pro Host Pool eine SVI (IP/Maske) auf jeder Edge.
- Dynamic-EID-Mapping kündigt den Pool pro LISP Instance-ID an; Host-spezifische Registrierung (/32, /128, MAC) ermöglicht Mobilität.
- Zuweisung dynamisch (Authentifizierung) oder statisch (pro Port).

### Border Node (Gateway zwischen Fabric-Site und externem Netz)
Typen:
| Typ | Zweck |
|---|---|
| Internal Border | Gateway zu **bekannten** Netzen mit definierter Prefixliste (Shared Services, DC); importiert/registriert diese Präfixe in die Fabric |
| External Border | Gateway zu **unbekannten** Zielen (Rest des Unternehmens, Internet) = Gateway of last resort, realisiert als LISP Proxy-ETR (PxTR) |
| Anywhere Border | Kombination aus internal + external |

*(Ergänzung)* In der Catalyst-Center-GUI wird der Typ heute über Optionen beim Border-Handoff gewählt (u. a. "Default to all Virtual Networks" für den Default-/External-Border); die Begriffe internal/external/anywhere sind in Design Guides und Prüfung weiter üblich.

Funktionen:
- **EID-Subnetze nach außen annoncieren**: per BGP (bevorzugt). EID-Präfixe stehen nur in der Routing-Tabelle des Borders; innerhalb der Fabric erfolgt der Zugriff über den Control Plane Node.
- **Fabric-Exit**: externer Border = Default für Edges (LISP PxTR).
- **LISP Instance → VRF**: Virtualisierung nach außen erhalten (VRF-Lite).
- **Policy Mapping**: SGT nach außen weitergeben – per SXP an TrustSec-fähige Geräte oder per Inline Tagging (Cisco Metadata, CMD) auf der Handoff-Verbindung.

### Control Plane Node
- LISP **Map-Server (MS)** + **Map-Resolver (MR)** auf demselben Knoten.
- Host Tracking Database (HTDB): EID ↔ Fabric-Edge-RLOC.
- MS: füllt HTDB aus Map-Register-Nachrichten. MR: beantwortet Map-Requests der Edges.
- Kann mit Border kombiniert (collocated) oder dediziert sein; 2–6 Knoten für Resilienz (laut Kurs), Border und Edges registrieren sich bei allen CP Nodes → gleiche Plattform wählen.

### Drei Ebenen
| Ebene | Technik |
|---|---|
| Control Plane | LISP |
| Data Plane | VXLAN (VXLAN-GPO) |
| Policy Plane | Cisco TrustSec (SGT, SGACL, SXP) |

Unterschiede zu klassischen Overlays: L2- UND L3-Overlay, Mobilität mit Anycast Gateway, VRF + SGT im Data Plane, automatische VTEPs, keine Topologieeinschränkungen (nur IP-Erreichbarkeit).

LISP verlagert Zielinformationen aus den Routing-Tabellen in ein zentrales Mapping-System (wie DNS) → kleinere Tabellen, weniger CPU. LISP-Data-Plane kann nur L3 → SD-Access nutzt VXLAN.

## Control Plane mit LISP (Seite 352)

Grundidee: klassische IP-Adresse = Identität + Ort. LISP trennt **EID** (Endpoint Identifier, wer) und **RLOC** (Routing Locator, wo; Loopback des Fabric-Knotens). Umzug: EID bleibt, nur RLOC ändert sich. Analogie DNS: DNS löst Namen→IP, LISP löst EID→RLOC.

- Pull-Modell (wie DNS) statt Push (wie BGP): Knoten fragen bei Bedarf → skalierbarer, mit Caching.
- Map-and-Encapsulate: Pakete an eine EID werden an den zuständigen RLOC gekapselt.
- Offener Standard (*(Ergänzung)* RFC 9300/9301), dynamische Tunnel ohne Vorkonfiguration der Endpunkte, Multihoming, Interworking LISP↔Nicht-LISP.

### LISP-Rollen
| Rolle | Aufgabe |
|---|---|
| ITR (Ingress Tunnel Router) | empfängt Pakete von lokalen Hosts, kapselt zu entfernten LISP-Sites (oder nativ zu Nicht-LISP) |
| ETR (Egress Tunnel Router) | empfängt gekapselte Pakete aus dem Core, entkapselt, liefert an lokale EIDs; registriert EID-Präfixe beim MS |
| xTR | ITR + ETR auf einem Gerät (Fabric Edge) |
| MS (Map-Server) | nimmt Map-Register der ETRs an, speichert Mapping-Datenbank |
| MR (Map-Resolver) | nimmt Map-Requests der ITRs an |
| PITR (Proxy-ITR) | zieht Verkehr von Nicht-LISP-Sites an und kapselt ihn zu LISP-Sites |
| PETR (Proxy-ETR) | erlaubt LISP-EIDs, Nicht-LISP-Ziele zu erreichen |
| PxTR | PITR + PETR (= External Border) |
| ALT | Alternative Topology: BGP-über-GRE-Overlay zur Aggregation von EID-Präfixen (in SD-Access nicht genutzt) |

EIDs stehen im DNS, sind im Transportnetz nicht geroutet. RLOCs sind im Underlay geroutet. Hosts kennen keine RLOCs, RLOCs (Core) kennen keine Hosts.

*(Ergänzung)* LISP-Control-Nachrichten nutzen UDP 4342 (Map-Request/-Register/-Reply), die LISP-Data-Plane UDP 4341. SD-Access nutzt nur die LISP-Control-Plane; neuere Versionen (LISP Pub/Sub) halten TCP-Sessions (Port 4342) zwischen Edge/Border und CP Node (`show lisp session`).

### Ablauf Registrierung und Auflösung
1. Endpunkt verbindet sich mit Edge → Edge sendet **Map-Register** (EID → eigener RLOC) an CP Node → HTDB.
2. Host in Branch will zu 10.2.2.2 → Branch-Edge sendet **Map-Request** an CP Node (MR).
3. CP Node antwortet per **Proxy-Reply** (Map-Reply mit RLOC 2.1.2.1). SD-Access-Besonderheit: Im klassischen LISP leitet der MS den Request an den ETR weiter, und der ETR antwortet selbst.
4. Branch-Edge speichert Mapping im Map-Cache und kapselt.

### Paketweg Edge→Edge (Beispiel aus dem Kurs, eigene Werte)
- Quelle 10.1.0.1 an Edge RLOC 1.1.1.1, Ziel 10.2.2.2 an Edge RLOC 2.1.2.1.
- Map-Cache-Treffer → VXLAN: äußerer IP-Header 1.1.1.1 → 2.1.2.1, innerer 10.1.0.1 → 10.2.2.2.
- Ziel-Edge entfernt VXLAN-Header, stellt zu.

### Border→Edge
- Internet-Host 192.3.0.1 → Border (RLOC 4.4.4.4) → Map-Cache/Request → VXLAN 4.4.4.4 → 2.1.2.1, innen 192.3.0.1 → 10.2.2.2.

### Host-Mobilität (Dynamic EID Migration)
- Host 10.2.1.10 an Edge 12.1.1.1: Edge legt Einträge an (EID-Pool-Route, /32 lokal, Route über LISP0) und registriert per **Map-Register** (Kurs schreibt fälschlich "map-request").
- Host zieht zu Edge 12.2.2.1 → neue Edge registriert → HTDB aktualisiert → CP Node benachrichtigt alte Edge 12.1.1.1, den Eintrag zu entfernen (sie zeigt dann auf den neuen Ort).
- Kommunikation mit DC 10.10.10.0/24 (hinter Border 12.0.0.1) läuft danach über die neue Edge; Host behält IP und Gateway.

### SD-Access-LISP vs. klassisches LISP
| Fähigkeit | Klassisches LISP | SD-Access |
|---|---|---|
| Layer-2-Erweiterung | nein | MAC-zu-IP-Binding, L2-Overlays |
| Virtuelle Netze | nur L3 (VRF) | L3 (VRF) und L2 (über VXLAN) |
| Fast Roaming | nein | Roaming bei gleicher IP (Kurs: "< 50 ms" – in Cisco-Dokumentation nicht belegt) |
| Wireless | nein | AP-Onboarding, Wireless Guest, VXLAN am AP |

Layer-2-Flooding (Layer 2 Extension): für Nicht-IP-/Broadcast-abhängige Endpunkte, ähnlich VPLS (Point-to-Multipoint), benötigt Underlay-Multicast; pro Host Pool aktivierbar.

## Data Plane mit VXLAN (Seite 353)

- LISP-Kapselung trägt nur L3 (verwirft Ethernet-Header) und hat kein Feld für SGT → SD-Access nutzt VXLAN.
- VXLAN (RFC 7348): L2-Frames über L3-Netz (MAC-in-IP/UDP), erhält den Original-Ethernet-Header; L2- und L3-Overlays.
- Vorteile ggü. VLAN: 24-Bit VNI → ~16 Mio. Segmente (statt 4094 VLANs), flexible Platzierung, alle Pfade nutzbar (L3-Routing, ECMP statt STP-Blocking).
- OTV vs. VXLAN: OTV für L2-DCI zwischen Rechenzentren (ARP-Caching, IS-IS-Control-Plane, Broadcast-Reduktion); VXLAN ursprünglich innerhalb eines DC.

### VXLAN-GPO-Header (Group Policy Option)
```
Outer Ethernet (14 B, +4 bei 802.1Q) | Outer IP (20 B, Src/Dst = RLOCs) | UDP (8 B) | VXLAN-GPO (8 B) | Original Ethernet-Frame
UDP: Src-Port = Hash über innere L2/L3/L4-Header (Entropie für ECMP), Dst-Port = 4789
VXLAN-GPO: Flags (8 Bit, inkl. G-Bit) | Group Policy ID (16 Bit = SGT) | VNI (24 Bit) | Reserved (8 Bit)
```
- Overhead ≈ 50 Byte (14+20+8+8) ohne 802.1Q-Tag im äußeren Header.
- 16 vormals reservierte Bit tragen das SGT → bis ~64.000 SGTs.
- VNI identifiziert das VN: L3-VNI ↔ VRF (Routing zwischen Subnetzen im VN), L2-VNI ↔ VLAN/Host Pool (Bridging im Subnetz).
- VTEP = Fabric Edge/Border (und für Wireless der Fabric AP); LISP liefert die Endpoint→VTEP-Zuordnung.

| Fähigkeit | LISP-Header | VXLAN-GPO |
|---|---|---|
| SGT | kein Feld | im Group-Policy-Feld |
| L3-Erweiterung (VRF) | ja | ja (VRF→L3-VNI) |
| L2-Erweiterung | nein | ja (VLAN→L2-VNI) |
| Wireless | nein | AP↔Edge per VXLAN |

*(Ergänzung)* VXLAN-GPO ist eine Erweiterung (IETF-Draft draft-smith-vxlan-group-policy), keine neue "Version" von VXLAN; Standard-VXLAN-Geräte ignorieren die Policy-Felder.

## Policy Plane mit TrustSec (Seite 354)

Zwei Ebenen:
- **Makro-Segmentierung**: Virtual Network = VRF. Endpunkte in verschiedenen VNs können standardmäßig NICHT kommunizieren (getrennte Routing-Tabellen). Im Data Plane: VNI; im Control Plane: LISP Instance-ID; am Border: Mapping auf VRF (z. B. VRF-Lite). Inter-VN-Verkehr nur über externes Gerät (Fusion Router/Firewall) mit Route Leaking.
- **Mikro-Segmentierung**: Scalable Groups (SGT) innerhalb eines VN; Regeln per SGACL in der ISE-Policy-Matrix; unabhängig von IP/VLAN/Topologie. SGT = 16-Bit-Wert, von ISE bei Anmeldung zugewiesen.

Gruppenzuweisung: dynamisch (802.1X, MAB, WebAuth → SGT als RADIUS-AV-Pair an die Edge) oder statisch (VLAN→SGT, Subnetz→SGT, Port-Profile→SGT, L2-Port→SGT, L3-Interface→SGT).

Durchsetzung (laut Kurs):
- Border Node: Nord-Süd-Verkehr (User → DC).
- Edge Node: Ost-West-Verkehr innerhalb der Fabric (User↔User).
- TrustSec filtert am **Egress** (Ziel-seitig): Quell-SGT steht im Paket, Ziel-SGT kennt das Ziel-Gerät.
- Verlässt Verkehr die Fabric, wird der VXLAN-Header entfernt → SGT geht verloren, außer per SXP (IP→SGT-Bindings, ISE kann auch selbst SXP-Speaker sein) oder Inline-Tagging (CMD) am Handoff.

| | Klassisches TrustSec | SD-Access Policy |
|---|---|---|
| SGT-Weitergabe | hop-by-hop Inline oder SXP | im VXLAN-GPO-Header |
| VN-Integration | nein | VN + SGT-fähige Firewalls |
| Access Control | ja | ja |
| QoS (App) | nein | App-basierte QoS-Policy |
| Traffic Copy | nein | Quell/Ziel-basierte Copy-Policy (ERSPAN) |

## Rolle von ISE und Catalyst Center (Seite 355)

ISE: Authentifizierung/Onboarding, liefert Attribute VLAN/Host-Pool, SGT, SGACL; AAA (RADIUS, TACACS+), Profiling, Visibility, Makro- und Mikro-Segmentierung. SGTs werden zentral in ISE definiert.

Integration Catalyst Center ↔ ISE: **pxGrid** + **REST-APIs** (ERS). Policies werden in Catalyst Center (Policy-Workflow) erstellt und in ISE geschrieben. Kommunikation mit der **PAN** (Primary Administration Node); PAN meldet alle weiteren Nodes (PSN, MnT, pxGrid). Konfigänderungen auf PAN → Sync an andere Nodes. Authentifizierungen laufen über **PSN**, Logging über **MnT**.

Deployment: Standalone oder verteilt; empfohlen mind. 2 Nodes mit allen Personas. Edges senden RADIUS an PSN(s); im verteilten Modell ordnet Catalyst Center Edges den PSNs zu.

Catalyst Center: Herz der Automation; SD-Access als Applikationspaket. Vier Workflows:
| Workflow | Inhalt |
|---|---|
| Design | Global Settings, Site-Profile, DNS/DHCP, IP-Pools, SWIM, PnP, User Access |
| Policy | VNs, Zuordnung Gruppen→VN, Gruppen-Policies (Contracts) |
| Provision | Geräte, Fabric Sites, CP/Border/Edge-Rollen, Fabric Wireless, Transit, externe Anbindung |
| Assurance | Health-Dashboards, 360-Grad-Sicht, Path Trace, Issues, Sensor-Tests |

## SD-Access Wireless (Seite 356)

Unified Wireless (CUWN, zentral): AP ↔ WLC CAPWAP-Tunnel für Control UND Daten; Mobility Anchor/Guest-Anchor mit EoIP (bzw. CAPWAP) zum DMZ-WLC; einfache IP-Planung, aber Hairpin aller Daten über den WLC.

Fabric Wireless:
- **Fabric WLC**: wie bisher AP-Image/Konfig, RRM, Client-Session-Management, Mobilität; ZUSÄTZLICH registriert er Client-MAC (L2-EID) mit SGT und L2-VNI im HTDB des CP Node und meldet Roaming-Updates (neuer RLOC). Nimmt NICHT am Datenpfad teil. Steht meist außerhalb der Fabric (Shared Services/DC, Global Routing Table).
- **Fabric AP**: Local Mode, muss **direkt** an einer Fabric Edge (laut CVD alternativ an einem Extended Node) hängen; CAPWAP-Control zum WLC; Daten per **VXLAN zur Edge**; wandelt 802.11 → 802.3, trägt L2-VNI und SGT in VXLAN; wendet SSID-Policies, AVC, QoS an. APs liegen in einem gemeinsamen Overlay-Pool im **INFRA_VN** (auf Global Routing Table gemappt → kein Route Leaking nötig für CAPWAP zum WLC). AP-WLC-Latenz < 20 ms RTT (CVD), kein FlexConnect/WLC über WAN für Fabric-Modus.
- **Fabric in a Box**: CP + Border + Edge auf einem Gerät (Einzelswitch, Hardware-Stack oder StackWise Virtual, z. B. Catalyst 9300/9400); Resilienz über die Redundanz dieser Plattform. Laut CVD ist auch "Dual Fabric in a Box" unterstützt, aber nur zu nutzen, wenn die Verkabelung es erzwingt.

### Abläufe
WLC zur Fabric: in Catalyst Center provisionieren → zur Fabric hinzufügen → WLC bekommt Credentials für sichere Verbindung zum CP Node. Border annonciert WLC-Management-Subnetz in die Fabric und Fabric-Präfixe zum WLC-Netz.

AP-Join:
1. AP-Pool in Catalyst Center; Macro/Autoconf auf den Edges vorbereitet.
2. AP bootet, Edge erkennt AP per CDP, setzt Port in AP-VLAN (nur ohne Port-Authentifizierung).
3. AP bekommt IP per DHCP im Overlay; Edge registriert AP als "speziellen" wired Host (EID) beim CP.
4. AP findet WLC klassisch und joint (Local Mode).
5. WLC prüft Fabric-Fähigkeit, fragt CP nach RLOC des AP → AP ist "fabric-enabled".
6. WLC registriert AP (L2-LISP, Proxy-Registrierung) mit Metadaten; CP benachrichtigt Edge; Edge baut VXLAN-Tunnel-Interface zum AP (`show access-tunnel summary`).

Client-Onboarding:
1. Client authentifiziert an Fabric-SSID; WLC fragt ISE, erhält SGT; WLC programmiert AP mit L2-VNI + SGT (kennt AP-RLOC).
2. WLC registriert Client-MAC (L2) mit SGT beim CP (Proxy für die Edge).
3. CP benachrichtigt Edge → MAC in L2-Forwarding-Tabelle, Edge holt Policy (SGACL) von ISE.
4. DHCP: AP kapselt in VXLAN mit L2-VNI → Edge mappt auf VLAN/SVI → DHCP im Overlay (Relay wie bei wired).
5. DHCP-Snooping (oder ARP bei statischer IP) löst Registrierung der Client-IP (L3-EID) durch die **Edge** aus.

Client-Roaming zwischen Edges:
1. Client roamt zu AP2 an Edge 2; AP meldet WLC.
2. WLC programmiert AP2 (SGT, RLOC) und aktualisiert MAC-Eintrag im CP mit neuem RLOC.
3. CP benachrichtigt Edge 2 (MAC → Tunnel) und Edge 1 (Cleanup). (Der Kurs nennt zusätzlich den Border; das Cisco-Tech-Dokument 220427 zum Roaming-Ablauf nennt nur die beiden Edges.)
4. Edge 2 aktualisiert IP-Eintrag beim ersten Verkehr. Roaming ist L2, weil Anycast Gateway überall gleich ist → gleiche IP.

Datenfluss Wireless: AP entfernt 802.11-Header → fügt 802.3/VXLAN/Underlay-IP hinzu (SGT + L2-VNI) → Edge A entkapselt, mappt L2-VNI→VLAN/L2 Instance, Lookup beim CP, kapselt zu Edge B → Edge B setzt Policy durch.

## Traditionelles Campus und SD-Access (Seite 357)

### Wireless Over-the-Top (OTT)
- Klassisches CUWN, Fabric dient nur als Transport für CAPWAP. Bestehende Non-Fabric-WLCs und -APs werden weiterverwendet (der Kurs sagt "beliebige Hardware/Software"; konkrete Unterstützung über die Kompatibilitätsmatrix prüfen).
- Einsatz: Migrationsschritt (erst wired migrieren, getrennte Teams, Kaufzyklen) oder Dauerlösung.
- Ablauf: WLC außerhalb der Fabric; Border annonciert WLC-Management-Subnetz in die Fabric und Fabric-Präfixe nach außen; APs im Overlay an Edges (ein AP-Subnetz), als wired Clients im HTDB; SSIDs auf WLC-Dynamic-Interfaces/VLANs; Border annonciert Wireless-Client-Subnetze in die Fabric; CAPWAP AP→WLC, an der Edge in VXLAN gekapselt bis zum Border, dort entkapselt, weiter zum WLC.
- Wireless-Clients sind **außerhalb** der Fabric; Verkehr wired-Fabric-Host ↔ Wireless-Client läuft über den Border. Kein Fabric-Vorteil (keine SGT im VXLAN, kein Anycast Gateway, Hairpin über WLC).
- Kapselung bei OTT: CAPWAP trägt Control- UND Datenverkehr (im Fabric zusätzlich in VXLAN). Bei Fabric-Wireless: CAPWAP nur Control.

### Anbindung klassischer Netze *(Ergänzung, im Kurs nur angerissen)*
- **IP-Based Transit** (L3-Handoff): Border ↔ externes Gerät per VRF-Lite (802.1Q-Subinterfaces/SVIs pro VN) und eBGP pro VRF. Catalyst Center automatisiert die Border-Seite, die Gegenseite (Fusion Device) wird manuell konfiguriert. SGT geht im Data Plane verloren (→ SXP oder Inline-Tagging).
- **SD-Access Transit**: verbindet mehrere Fabric Sites mit LISP/VXLAN end-to-end über ein Transit-Control-Plane-Paar; erhält VN und SGT im Header (setzt passende MTU und geringe Latenz voraus, typischerweise Metro/Campus-Verbindungen).
- (früher: SD-WAN Transit – Handoff an Catalyst SD-WAN mit VPN/SGT-Erhalt).
- **Fusion Router/Fusion Device**: externer Router/L3-Switch/Firewall, der Routen zwischen VN-VRFs und Global Routing Table (Shared Services: DHCP, DNS, ISE, WLC) leakt; damit erreichen Fabric-Endpunkte gemeinsame Dienste und VNs untereinander (kontrolliert).
- **Layer-2-Handoff** (L2 Border): Border bridged einen Fabric-Host-Pool (L2-VNI) auf ein klassisches VLAN; Hosts im alten VLAN und in der Fabric teilen sich ein Subnetz; Gateway ist das Fabric Anycast Gateway → altes Gateway (SVI/HSRP) im Legacy-Netz muss entfernt werden. Zweck: schrittweise Migration ohne Re-IP.
- **Extended Node**: nicht-fabric-fähiger Switch (Catalyst IE, Digital Building, kompakte Catalyst) per 802.1Q-Trunk/Port-Channel an einer Edge; kein VXLAN/LISP auf dem Extended Node, die Edge übernimmt Gateway/Policy; Onboarding per PnP in INFRA_VN. Policy Extended Node (z. B. IE3400) kann zusätzlich SGACL durchsetzen.

## Typische show-Befehle *(Ergänzung, IOS-XE 17.x, Ausgaben gekürzt/eigene Werte)*

```
Edge# show lisp session
Sessions for VRF default, total: 2, established: 2
Peer                  State      Up/Down     In/Out    Users
10.255.0.1:4342       Up         1w2d        3021/2780  6
10.255.0.2:4342       Up         1w2d        2988/2771  6

Edge# show lisp instance-id 4099 ipv4 map-cache
LISP IPv4 Mapping Cache for LISP 0 EID-table vrf CAMPUS (IID 4099), 3 entries
0.0.0.0/0, uptime: 1w2d, expires: never, via static-send-map-request
  Negative cache entry, action: send-map-request
10.10.20.15/32, uptime: 00:04:11, expires: 23:55:48, via map-reply, complete
  Locator      Uptime    State  Pri/Wgt
  10.255.0.22  00:04:11  up       10/10

Edge# show lisp instance-id 4099 ipv4 database
LISP ETR IPv4 Mapping Database for LISP 0 EID-table vrf CAMPUS (IID 4099), LSBs: 0x1
10.10.20.37/32, dynamic-eid CAMPUS-IPV4, inherited from default locator-set rloc_...
  Locator      Pri/Wgt  Source     State
  10.255.0.21   10/10   cfg-intf   site-self, reachable

CP# show lisp site
CP# show lisp instance-id 4099 ipv4 server

Edge# show access-tunnel summary      ! VXLAN-Tunnel zu den Fabric APs
Edge# show device-tracking database   ! lokal gelernte Endpunkte (SISF)
Border# show ip route vrf CAMPUS
Border# show bgp vpnv4 unicast all summary
```
Troubleshooting-Hinweise:
- Endpunkt nicht erreichbar → `show lisp ... database` an der Quell-/Ziel-Edge (registriert?), `show lisp site` am CP (Registrierung vorhanden, von welchem RLOC?), Map-Cache an der Quell-Edge.
- Große Pakete gehen verloren, kleine nicht → MTU im Underlay zu klein (VXLAN +50 Byte).
- Fabric AP bleibt "non-fabric" → AP nicht direkt an Edge, nicht im AP-Pool/INFRA_VN, WLC nicht in Fabric oder Latenz zu hoch.
- Kein Zugriff auf DHCP/DNS aus einem VN → fehlendes Route Leaking am Fusion Device.

## Fehler/Ungenauigkeiten im Kurs

1. Seite 350: "Cisco DNA Assurance: Data collectors (for example, Neighbor Discovery Protocol [NDP])" – NDP steht hier für **Network Data Platform** (Analytics-Komponente von DNA Center), nicht für das IPv6 Neighbor Discovery Protocol. Quelle: Cisco SD-Access Solution Overview / DNA Center Architektur (NCP = Network Control Platform, NDP = Network Data Platform).
2. Seite 352, Host Mobility Schritt 2: "fabric edge sends a map-request to the control plane to update the host tracking database" – die Registrierung erfolgt per **Map-Register**; Map-Request dient der Auflösung. Quelle: RFC 9301, SD-Access Design Guide.
3. Seite 353: "VXLAN-GPO is the latest version of VXLAN" – VXLAN-GPO ist eine Erweiterung (IETF draft-smith-vxlan-group-policy), keine neue Version von RFC 7348.
4. Seite 353, Abbildung: "UPD Header" (Tippfehler für UDP).
5. Seite 356: Fabric APs als "802.11ac Wave 1 und Wave 2" – veraltet; aktuelle Fabric-APs sind Wi-Fi-6/6E/7-Modelle (Catalyst 9100/CW916x), Wave-1-APs werden in aktuellen Releases nicht mehr unterstützt.
6. Durchgehend "Cisco DNA Center" → heute **Catalyst Center**; Content-Review-Frage erwähnt APIC-EM (abgekündigt).
7. Seite 349: Satz "STP as the solution is routed access" ist verstümmelt; gemeint: kein STP im Underlay, weil Routed Access mit ECMP.
8. Seite 351: "LISP can only tunnel Layer 3 traffic" – gilt für die klassische LISP-Data-Plane (RFC 6830/9300); LISP-Control-Plane kann in SD-Access sehr wohl MAC-EIDs (L2) verwalten.
9. *(Checker)* Nicht belegbare Kursangaben: Fast Roaming "< 50 ms" und "RTT ≤ 100 ms" als Underlay-Anforderung zwischen Fabric-Knoten finden sich nicht im SD-Access CVD (dieser verweist für Latenzen auf das Catalyst-Center-Datenblatt; belegt sind 20 ms RTT AP↔WLC). Beim Inter-Switch-Roaming nennt Cisco (Tech-Dokument 220427) als vom CP benachrichtigte Knoten nur Roam-to- und Roam-from-Edge.

## Bilder

Ordner `encor-1.4.10/bilder/31-sda/`:
- `01-under-over.svg` – Underlay (geroutete Fabric-Knoten mit RLOC-Loopbacks) vs. Overlay (VNs/Host Pools über VXLAN-Tunneln), Endgeräte sehen nur das Overlay.
- `02-rollen.svg` – Fabric-Rollen-Topologie: Catalyst Center, ISE, Control Plane Node, Border (internal/external), Intermediate, Edge, Fabric WLC, Fabric AP, Extended Node.
- `03-border.svg` – Border-Typen internal/external/anywhere mit bekannten vs. unbekannten Netzen.
- `04-lisp-ablauf.svg` – LISP-Ablauf Map-Register → Map-Request → Proxy Map-Reply → VXLAN-Kapselung mit Beispieladressen.
- `05-mobility.svg` – Host-Umzug zwischen Edges: neues Map-Register, Benachrichtigung der alten Edge, SMR.
- `06-vxlan-hdr.svg` – VXLAN-GPO-Header mit Feldgrößen, UDP 4789, SGT- und VNI-Feld, 50 Byte Overhead.
- `07-segment.svg` – Makro- (VN/VRF) vs. Mikro-Segmentierung (SGT/SGACL) mit Policy-Matrix.
- `08-wireless.svg` – SD-Access Wireless: CAPWAP-Control zum WLC, VXLAN-Daten AP→Edge, WLC-Registrierung im CP; Vergleich mit OTT.
- `09-handoff.svg` – Border-Handoff: IP-Transit (VRF-Lite + eBGP) zum Fusion Router mit Shared Services, Layer-2-Handoff zum Legacy-VLAN.
