# Exploring the Working Principles of the Cisco Catalyst SD-WAN Solution

Quelle: ENCOR 1.4.10 Student Guide, Seiten 361–371 (360 Intro, 372 Summary Challenge und 373 Answer Key nicht ausgewertet)

Topics: ENCOR-1.2.a (SD-WAN Control- und Data-Plane-Elemente – Hauptthema), ENCOR-1.2.b (Vorteile und Grenzen von SD-WAN), ENCOR-6.4 (REST-API des SD-WAN Managers – nur Randthema). Cloud OnRamp (SaaS/Multicloud/Colocation) steht in Kapitel 02 und wird hier nicht wiederholt.

Ergänzungen, die nicht im Kurs stehen, sind mit *(Ergänzung)* markiert. Quellen dafür: Cisco Catalyst SD-WAN Design Guide (CVD), Cisco Catalyst SD-WAN Systems and Interfaces / Routing / Policies Configuration Guides (IOS XE 17.x, Manager 20.x), Cisco Catalyst SD-WAN Command Reference.

### Produktnamen (alt → neu)

| Alter Name (Viptela-Ära) | Aktueller Name | Plane |
|---|---|---|
| vManage | Cisco Catalyst SD-WAN Manager | Management |
| vSmart | Cisco Catalyst SD-WAN Controller | Control |
| vBond | Cisco Catalyst SD-WAN Validator | Orchestration |
| vEdge (Viptela-OS) / cEdge (IOS XE SD-WAN) | WAN Edge (Router) | Data |
| vAnalytics | Cisco Catalyst SD-WAN Analytics | Analytics (optional) |

Der Kurs mischt beide Benennungen (z. B. "list of Cisco vSmart controllers" auf der Orchestration-Plane-Seite). In der Prüfung können beide Varianten vorkommen.

## Warum SDN für das WAN (Seite 361)

Treiber: mehr SaaS/IaaS/Cloud, mobile und IoT-Geräte, steigende Sicherheitsanforderungen, Anwendungen brauchen Priorisierung/Optimierung.

Klassisches WAN: mehrere MPLS-Leitungen oder MPLS + Internet/LTE im **Active/Backup**; Internet-/SaaS-Verkehr wird zentral über Rechenzentrum/Hub ausgeleitet (Backhaul). Probleme:
- zu wenig Bandbreite, hohe Bandbreitenkosten (MPLS teuer)
- Applikationsausfälle, schlechte SaaS-Performance (Umweg über DC)
- komplexer Betrieb, komplexe Cloud-Anbindung, lange Bereitstellungszeiten
- Policy-Änderungen mühsam (Box für Box), kaum Applikations-Sichtbarkeit, schwer abzusichern

SDN-Prinzip: Control Plane von der Forwarding-(Data-)Plane trennen und zentralisieren → Automatisierung, zentrales Provisioning, Monitoring, Troubleshooting. Catalyst SD-WAN wendet das auf das WAN an: ein **softwarebasiertes, virtuelles IP-Fabric-Overlay** über beliebigen Transporten (**Underlay**: Internet, MPLS, Metro Ethernet, LTE/4G/5G). Das Underlay liefert nur Paketzustellung; Overlay = verschlüsselte Tunnel zwischen den WAN Edges.

Eigenschaften laut Kurs: multitenant, cloud-delivered, stark automatisiert, sicher, skalierbar, application-aware, umfangreiche Analytics.

Vorteile:
- **Zentrales Netz- und Policy-Management** → weniger Change-Aufwand, schnellere Rollouts
- **Transportunabhängigkeit**: MPLS + günstiges Breitband (beliebige Kombination) **active/active** → mehr Kapazität, weniger Kosten
- Overlay reicht bis Rechenzentrum, Branch und Cloud
- Flexibles Deployment durch getrennte Control und Data Plane
- Sicherheit: starke Verschlüsselung, End-to-End-Segmentierung, Zertifikats-Identität für Router und Controller (Zero-Trust), Control-Plane-Schutz, Application Firewall, Einbindung von Cisco Umbrella/Firewalls
- nahtlose Public-Cloud-Anbindung
- Application Visibility & Recognition, application-aware Policies mit Echtzeit-SLA-Durchsetzung
- dynamische Optimierung von SaaS-Applikationen
- Analytics (Troubleshooting, Forecasting, Kapazitätsplanung)

Grenzen/Herausforderungen *(Ergänzung)*:
- Internet-Transporte haben keine garantierten SLAs – SD-WAN misst und weicht aus, kann aber schlechte Leitungen nicht "reparieren".
- Abhängigkeit von Controllern, Zertifikaten und Lizenzen (Smart Account, Abonnement); Validator muss öffentlich erreichbar sein.
- IPsec-Overhead (MTU/MSS beachten), Hardware-Kryptoleistung begrenzt Durchsatz.
- NAT-Typen: sitzen beide Seiten hinter symmetrischem NAT, kommt kein direkter Tunnel zustande (Umweg über Hub nötig).
- Full-Mesh skaliert für Edges mit vielen TLOCs nicht beliebig (viele BFD-Sessions) → Topologie per Control Policy begrenzen.
- Lernkurve/neues Betriebsmodell (Templates/Configuration Groups, Policies).

## Komponenten und Planes (Seite 362)

Rollen sind getrennt → skalierbar und effizient. Routing-Prinzipien wie im Internet, aber virtualisiert. Trennung Control/Data Plane → läuft über jeden Transport.

| Plane | Komponente | Aufgabe |
|---|---|---|
| Orchestration | SD-WAN Validator (vBond) | Erst-Authentifizierung, Orchestrierung der Verbindungen, NAT-Traversal |
| Management | SD-WAN Manager (vManage) | GUI, Day 0/1/2, Templates, Policies, Monitoring, Software-Upgrades, REST-API |
| Control | SD-WAN Controller (vSmart) | OMP, verteilt Routen/TLOCs/Keys/Policies, setzt Control Policies durch |
| Data | WAN Edge (physisch oder virtuell, z. B. Catalyst 8000V) | IPsec-Tunnel, Forwarding, Durchsetzen von Data-/AAR-Policies |

- Control Plane = Regeln, wie Verkehr durch das Overlay läuft; Data Plane = transportiert die Pakete.
- Manager = "single pane of glass" für Day 0 (Onboarding), Day 1 (Konfiguration), Day 2 (Betrieb/Monitoring); zentrale Software-Installation und -Upgrades einzeln oder als Bulk.

## Orchestration Plane – SD-WAN Validator (Seite 363)

- Zero-Touch-Deployment und Sicherheitsvalidierung beim Onboarding.
- **Erster Kontaktpunkt**: führt die initiale Authentifizierung durch (Zertifikate, Zero-Trust, **Allow-List-Modell**: nur autorisierte Seriennummern/Zertifikate dürfen Control-Verbindungen aufbauen).
- Verteilt an die WAN Edges die Liste der **SD-WAN Controller und des SD-WAN Managers** (Orchestrierung zwischen Management-, Control- und Data-Plane).
- **NAT-Traversal**: lernt private (pre-NAT) und public (post-NAT) IP/Port der Geräte → arbeitet wie ein **STUN-Server**.
- Muss eine **öffentliche IP oder 1:1-NAT** haben, damit alle (v. a. reine Internet-)Sites ihn erreichen; mit DNS-Namen ermöglicht das Zero-Touch.
- Hochverfügbar auslegen: **Ist der Validator down, kann kein neues Gerät dem Overlay beitreten** (bestehende Verbindungen laufen weiter – *(Ergänzung)*). On-prem ist der Kunde für Resilienz verantwortlich.
- Single- oder Multitenant-Betrieb.

*(Ergänzung)* Details Onboarding:
- Control-Verbindungen zum Validator sind immer **DTLS** (UDP). Zu Manager und Controller DTLS (Default) oder TLS (TCP) konfigurierbar. Default-Basisport UDP **12346** (DTLS); bei Port-Hopping werden weitere Ports in 20er-Schritten (12366, 12386, 12406, 12426) probiert.
- Die Verbindung WAN Edge → Validator ist nur vorübergehend: Nach Erhalt der Controller-/Manager-Liste wird sie abgebaut.
- Allow-List der WAN Edges (Seriennummern/Chassis-IDs) kommt aus dem Cisco Plug and Play Connect Portal (Smart Account) in den Manager, der sie an Validator und Controller verteilt. Ein Gerät, das nicht darin steht oder im Manager auf "invalid" gesetzt ist, wird abgewiesen.
- Hardware-Edges haben eine Geräte-Identität im TPM/SUDI-Chip (signiertes Zertifikat); virtuelle Edges nutzen ein OTP/Token.
- Prüfung bei der Authentifizierung u. a.: Zertifikatskette (Root-CA), Seriennummer auf Allow-List, **organization-name** identisch.
- Ablauf: (1) Edge erhält per PnP/ZTP oder Bootstrap-Konfiguration Validator-Adresse und Org-Name → (2) DTLS zum Validator, gegenseitige Authentifizierung → (3) Validator nennt Controller und Manager, teilt beiden Seiten die Edge-Adresse mit → (4) Edge baut DTLS/TLS zu Manager (Konfiguration) und zu Controllern (OMP) auf → (5) Edge erhält per OMP Routen/TLOCs/Keys und baut IPsec + BFD zu anderen Edges auf.

## Management Plane – SD-WAN Manager (Seite 364)

- Single pane of glass Day 0/1/2, Echtzeit-Alarme, zentrales Provisioning, Standardisierung der Konfiguration, einfache Bereitstellung und Änderung, programmatische APIs.
- Web-GUI mit **RBAC**; single- und multitenant.
- Zentrale Provisionierung, zentrale Policies, **Device Configuration Templates**, Monitoring/Troubleshooting.
- Zentrale Software-Upgrades für alle Fabric-Elemente: WAN Edges, Validator, Controller, Manager selbst.
- APIs für DevOps; Performance-Statistiken exportieren (externe Systeme, SD-WAN Analytics).
- Hochverfügbarkeit: einzelner Manager oder **Cluster mit mindestens drei Managern** (empfohlen für große Netze: Redundanz + Lastverteilung).
- Der Manager ist **nicht** im Datenpfad und verteilt **keine Routen** – fällt er aus, laufen Control und Data Plane weiter, nur Management/Monitoring/Änderungen fehlen *(Ergänzung, folgt aus der Architektur)*.

*(Ergänzung)* Konfigurationsmodelle im Manager:
- **Feature Templates** (Bausteine: System, VPN, Interface, OMP, BFD …) → zusammengesetzt zu **Device Templates**, die an Geräte angehängt werden (attach); Variablen pro Gerät (z. B. system-ip, site-id) per CSV.
- **CLI Templates** (komplette Konfig als Text).
- **Configuration Groups** (ab Manager 20.12 / IOS XE 17.12 der empfohlene Workflow, ersetzen schrittweise Feature Templates) und **Policy Groups**.

## Control Plane – SD-WAN Controller (Seite 365)

- Scale-out-Control-Plane: Fabric Discovery, verteilt Control-Plane-Informationen zwischen den Edges, verteilt **Data-Plane- und Application-Aware-Routing-Policies** an die Edges, setzt **Control Policies** (Service Chaining, Multitopologie, Multihop) selbst durch, reduziert Komplexität, hochresilient.
- **OMP** zwischen Controllern untereinander und zwischen Controller und Edges.
- Verteilt: Service-Side-(LAN-)Erreichbarkeit, Transport-IP-Adressen, **IPsec-Schlüssel**, Site-IDs usw.
- Arbeitet wie ein **BGP Route Reflector**: Edges senden Updates an den Controller, der reflektiert sie an alle anderen → jede Edge kennt alle Tunnelendpunkte und Prefixe, ohne Control-Kanäle zu allen anderen Edges.
- Control Policies wirken auf OMP-Informationen auf dem Controller: Service Chaining (z. B. Firewall in den Pfad), Topologien (Hub-and-Spoke, Partial Mesh, Full Mesh).
- Löst das **n²-Problem** großer IPsec-Netze (bei IKE-Full-Mesh braucht jeder Router eine Control-Beziehung zu jedem anderen; n·(n−1)/2 Peerings). Mit Controllern: linear (jede Edge nur zu wenigen Controllern).
- Controller oft geografisch verteilt; cloud-delivered redundant in der Cisco-Cloud; on-prem → Kunde verantwortlich.
- Der Controller leitet **keinen Datenverkehr** weiter.

*(Ergänzung)*: Pro Transport baut eine Edge standardmäßig Control-Verbindungen zu bis zu **2 Controllern** auf (max-control-connections). Fällt die Verbindung zu allen Controllern aus, behalten die Edges dank **OMP Graceful Restart** die zuletzt gelernten Routen/Keys und forwarden weiter (Default-Timer 43 200 s = 12 h).

## Data Plane – WAN Edge (Seite 366)

- Sichere Data Plane mit anderen Edges (IPsec), sichere Control Plane zu den Controllern (OMP über DTLS/TLS), setzt Data- und AAR-Policies um, exportiert Statistiken/Alarme/Events an den Manager.
- Klassisches Routing auf der Service-Seite: OSPFv2/v3, BGP, EIGRP, RIPv2, plus **VRRP** (FHRP, auch pro VLAN) – für LAN-Erreichbarkeit und Brownfield-Integration mit Nicht-SD-WAN-Sites.
- Onboarding: voll Zero-Touch (**ZTP** oder **Cisco PnP**) oder mit administrativer Freigabe; Zero-Touch nutzt signierte Zertifikate im **TPM** als Geräteidentität.
- Formfaktoren: physisch (ISR 1000/4000, Catalyst 8000 Edge (8200/8300/8500), ASR 1000, Catalyst 8200 uCPE) und virtuell (Catalyst 8000V in AWS/Azure, NFV auf ENCS 5000 / CSP mit KVM oder ESXi).
- Edges ver- und entschlüsseln den Applikationsverkehr zwischen Sites.

## Programmatic APIs (Seite 367)

- **REST-API** über den Webserver des SD-WAN Managers: steuern, konfigurieren, überwachen.
- HTTPS, Methoden GET (lesen), PUT (ändern), POST (anlegen), DELETE (löschen), Authentifizierung/Autorisierung, Bulk-Calls, Python-Skripte.
- Anwendungsfälle: Templates automatisiert attachen/detachen, Policies dynamisch ändern, Drittanbieter-Monitoring integrieren.
- REST: zustandslos (stateless), Client-Server, cachebar; einfacher als RPC/SOAP/WSDL; kein formaler Standard, aber Konventionen (HTTP, Ressourcen als Substantive, gängige Datenformate wie JSON).
- DevNet: developer.cisco.com/sdwan (Doku, Sandboxes, Beispielcode).

*(Ergänzung)*: Basis-URL `https://<manager>/dataservice/...`, z. B. `GET /dataservice/device` (Geräteliste). Login per `POST /j_security_check` (Formfelder j_username/j_password) → Session-Cookie **JSESSIONID**; für ändernde Calls zusätzlich **X-XSRF-TOKEN** aus `GET /dataservice/client/token`.

## Analytics (Seite 368)

- **Cloud-basierte** Analytics-Engine, **optional**, **Opt-in**, Daten werden **anonymisiert**.
- Funktionen: Fabric-Telemetrie, Kapazitätsprognosen, SLA-Verletzungstrends, Anomalieerkennung bei Auslastung, Application **QoE**, **Carrier Grading**.
- Dashboard zeigt standardmäßig die **letzten 24 Stunden**, Drill-down auf andere Zeiträume, einzelne Carrier/Tunnel/Applikationen.
- **QoE-Score 0–10** (0 schlechteste, 10 beste), aus **Latenz, Verlust, Jitter**, pro Applikation angepasst.
- Mehrwert: Visibility (inkl. korrelierter Daten anderer Netze, Cross-Customer-Benchmarking), Forecasting (Bandbreitenbedarf in **3–6 Monaten**), What-if-Szenarien (Kosten/Performance/Verfügbarkeit), Recommendations (Machine Learning, z. B. AAR-Policy-Vorschläge, Provider-Empfehlung je Standort).

## Terminologie (Seite 369)

### OMP – Overlay Management Protocol
- Zentrales Protokoll des Fabrics, **TCP-basiert**, erweiterbar, vereint alle Control-Plane-Funktionen.
- Läuft **innerhalb** der zertifikatsauthentifizierten **DTLS/TLS-Control-Verbindungen** zwischen Edges und Controllern sowie zwischen Controllern (Full Mesh).
- Edges müssen nicht mit allen Controllern peeren.
- Startet automatisch, sobald die DTLS/TLS-Verbindung steht. Peering über die **System-IPs**; nur **eine OMP-Session** pro Edge–Controller-Paar, auch wenn mehrere DTLS/TLS-Verbindungen (mehrere Transporte) bestehen.
- Austausch: Prefixe, Next-Hops (TLOCs), **Crypto Keys**, Policies → Edges bauen IPsec **ohne IKE** auf. Kein OSPF/EIGRP/BGP über die Tunnel nötig. Zentrale Data-/AAR-Policies (im Manager definiert) werden per OMP verteilt.
- Address Families und Routenattribute (ähnlich BGP).

### Transport- vs. Service-Seite
- **Transport Side**: Edge-Interface zum Underlay, **immer VPN 0**; Control-Traffic läuft über die OMP-Sessions; Datenverkehr wird getunnelt und verschlüsselt (außer bei Split-Tunneling/DIA).
- **Service Side**: Interfaces zum Benutzer-/Kundennetz; Verkehr wird unverändert (as is) weitergeleitet; Service-VPNs.

### VPNs (Segmente, entsprechen VRFs)
- **VPN 0** = Transport-VPN: Control-Traffic (DTLS/TLS) zu Controllern/Validator, WAN-Transport-Interfaces mit Tunnel-Interface. Auf vEdges anfangs alle Interfaces außer Management, alle deaktiviert. WAN-Interfaces müssen hier konfiguriert werden, sonst keine Control Plane.
- **VPN 512** = Management-VPN, **Out-of-Band-Management**, standardmäßig konfiguriert und aktiv.
- **Service-VPNs**: jede andere Nummer (Benutzersegmente), mit Interfaces zu lokalen Netzen, Routing (BGP, OSPFv2/v3, EIGRP, RIPv2), VRRP, QoS, Shaping, Policing.
- *(Ergänzung/Korrektur)* Gültig für Service-VPNs laut Segmentation Configuration Guide (IOS XE 17.x): **1–65525 ohne 512**; Nummern darüber nutzt das System intern (z. B. 65528–65530 für Loopbacks/SIG-Tracker/Speedtest) (der Kurs schreibt pauschal "1–65535").
- *(Ergänzung)* Auf IOS-XE-Edges: VPN 0 = globale Routing-Tabelle, VPN 512 = VRF `Mgmt-intf`, Service-VPN n = `vrf definition n`. Im Data Plane trägt jedes Paket ein **VPN-Label**, damit die Gegenseite das Segment zuordnen kann.

### Route-Reflector-Prinzip
Klassisch: Full-Mesh-IGP/BGP oder Routing über Overlay-Tunnel (GRE, MPLS). SD-WAN zentralisiert: alle Service-Prefixe einer Edge → Controller → reflektiert an andere Edges. Controller nur Control Plane, kein Datenverkehr.

### TLOC – Transport Locator
- Beschreibt, wie eine Edge an einen WAN-Transport angebunden ist; ähnlich einem **Next Hop**.
- Eindeutig durch das **3-Tupel (System-IP, Color, Encapsulation)**.
- Zusätzlich: **private** IP/Port (am Interface, pre-NAT) und **public** IP/Port (post-NAT, vom Validator ermittelt). Ohne NAT identisch. "Private" kann trotzdem eine öffentlich routbare Adresse sein, "public" kann RFC-1918 sein.
- Encapsulation: **IPsec** oder **GRE**.
- Warum System-IP statt Interface-IP: Interface-IPs ändern sich (DHCP, Kartentausch) – die System-IP bleibt fest.
- Beispiel: Edge 1.1.1.1 mit (1.1.1.1, metro-ethernet, ipsec) auf 184.168.0.69 und (1.1.1.1, biz-internet, ipsec) auf 75.1.1.1 → zwei TLOCs.

### OMP-Routentypen (Edge → Controller)
| Typ | Inhalt | Attribute |
|---|---|---|
| **OMP routes** (vRoutes, Service-Side-Routen) | lokal gelernte Prefixe (connected, static, OSPF, BGP, EIGRP, RIPv2), in OMP redistribuiert | TLOC (≈ BGP Next Hop), origin, origin metric, originator, preference, site ID, tag, VPN |
| **TLOC routes** | TLOCs der WAN-Transporte | private/public IP, carrier, preference, site ID, tag, weight, **Encryption Key** |
| **Service routes** | Netzwerkdienste (Firewall, IPS, WAN-Optimierung) für Service Insertion | originator System-IP, TLOC, VPN-IDs/Labels |

Eine OMP-Route wird nur installiert, wenn ihr TLOC **aktiv** ist (BFD-Session up).

### System-IP, Organization-Name, Site-ID
- **System-IP**: eindeutiger Identifier eines OMP-Endpunkts, 32-Bit-IPv4-Notation, logisch ein Loopback "system" in VPN 0, ähnlich Router-ID; nicht dasselbe wie ein konfiguriertes Loopback; muss nicht geroutet werden. Empfehlung: als Router-ID für OSPF/BGP verwenden; ist manuell eine andere Router-ID konfiguriert, hat diese Vorrang.
- **Organization-Name**: **case-sensitive**, auf allen Geräten identisch, muss zum Namen in den Zertifikaten passen (OU) – sonst schlägt die Authentifizierung fehl.
- **Site-ID**: numerische Standortkennung; auf jeder Edge konfiguriert; **nicht eindeutig** – alle Geräte desselben Standorts teilen sie (gleiche Site-ID = gleicher Ort). *(Ergänzung)* Edges mit gleicher Site-ID bauen untereinander standardmäßig keine IPsec/BFD-Tunnel auf (änderbar mit `allow-same-site-tunnels`); Site-ID wird in Control Policies (site-lists) verwendet.

### Colors
- Color = Typ des WAN-Transports, Teil des TLOC. Vordefiniert: 3g, biz-internet, blue, bronze, custom1–3, default, gold, green, lte, metro-ethernet, mpls, private1–private6, public-internet, red, silver.
- **Private Colors**: mpls, metro-ethernet, private1–6 (Annahme: kein NAT). **Alle anderen sind public** (biz-internet, public-internet, lte, 3g, gold, …).
- Wirkung auf Edge↔Edge und Edge↔Controller:
  - private ↔ private → **private** IP/Port
  - private ↔ public (gemischt) → **public** IP/Port
  - public ↔ public → **public** IP/Port
- Private Colors dürfen auch im öffentlichen Netz genutzt werden, wenn kein NAT dazwischen ist.
- Pro Edge nur ein Tunnel-Interface mit Color `default`. Auf Controllern ist eine Color konfigurierbar, hat aber keine TLOC-Bedeutung (Controller haben keine TLOCs) – sie steuert nur die public/private-Adresswahl.
- Tunnel zwischen verschiedenen Colors sind möglich, sofern IP-Erreichbarkeit besteht. Standard: jede Edge versucht jeden TLOC über jeden Transport (auch andere Colors).
- **restrict**: Tunnel/BFD nur zu TLOCs **gleicher Color**; typisch auf privaten Transporten (MPLS), damit kein Versuch Richtung Internet-TLOCs. Beispiel: ohne restrict 2×2 TLOCs → 4 Sessions; mit restrict auf mpls → mpls↔mpls und inet↔inet.
- Beispiel aus dem Kurs: Controller privat 10.100.100.10, per NAT/Firewall als 64.100.100.10 veröffentlicht, Controller-Color public → Edges (MPLS privat 10.20.10.5, INET 64.10.10.5) erreichen ihn über beide Transporte unter 64.100.100.10.

### NAT-Traversal
Jeder Controller/jede Edge kann unbemerkt hinter NAT stehen. Der Validator agiert als **STUN-Server**: Geräte erfahren ihre übersetzte IP/Port und verteilen sie mit ihren TLOCs. *(Ergänzung)*: Full-Cone-NAT ist unkritisch; sitzen beide Edges hinter **symmetrischem NAT**, ist kein direkter Tunnel möglich.

### BFD
- Auf WAN Edges **automatisch gestartet, nicht abschaltbar**; läuft zwischen allen Edges **in den IPsec-Tunneln** über alle Transporte.
- **Echo-Modus**: Empfänger schickt die Pakete unverarbeitet zurück.
- Zweck: **Path Liveness** und Qualitätsmessung (**Loss, Latency, Jitter**) für **Application-Aware Routing**.
- *(Ergänzung)* Defaults: hello-interval 1 s, multiplier 7 (pro Color); AAR poll-interval 600 000 ms (10 min), app-route multiplier 6.

### Application-Aware Routing *(Ergänzung, im Kurs nur erwähnt)*
- **SLA-Class** = Schwellwerte für Loss (%), Latency (ms), Jitter (ms).
- AAR-Policy: ordnet Verkehr (Applikation, DSCP, Prefix) einer SLA-Class zu, optional bevorzugte Color. Erfüllt ein Tunnel die SLA nicht mehr, wird der Verkehr auf einen konformen Tunnel verschoben. Erfüllt kein Tunnel die SLA, wird über die verfügbaren Tunnel weitergeleitet (mit `strict` stattdessen verworfen; `fallback-to-best-path` wählt den besten).
- Zentral im Manager definiert, vom Controller per OMP an die Edges verteilt, auf den Edges durchgesetzt.

### Policies *(Ergänzung)*
| Policy | Wo definiert | Wo wirksam | Wirkt auf |
|---|---|---|---|
| Centralized **Control** Policy | Manager | **Controller** | OMP-Routen/TLOCs (Topologie: Hub-and-Spoke, Service Chaining, Pfadpräferenz) |
| Centralized **Data** Policy | Manager | Controller verteilt per OMP → **Edge** | Datenpakete (5-Tupel, DSCP, App) pro VPN/Site-List: NAT/DIA, Service Chaining, Drop, Traffic Engineering |
| **App-Route** (AAR) Policy | Manager | Edge | Pfadwahl nach SLA |
| **Localized** Policy | Manager, per Device Template | Edge | ACLs, QoS, Route-Policies, lokal |

Default ohne Control Policy: **Full Mesh** (alle Routen/TLOCs an alle).

### Fabric-Operation / Sicherheit
Secure Fabric: Routing-Advertisements, L3-Segmentierung per VRF/VPN, Peer-to-Peer-Verbindungen mit Authentifizierung und Verschlüsselung, Policies für Routing und Daten. Transport-Links werden automatisch erkannt und der Verkehr zwischen Sites automatisch verschlüsselt; Schlüssel werden über die sichere Controller-Session verteilt (RSA- und Zertifikatsinfrastruktur) → keine tausenden paarweisen Keys, Schutz gegen Angriffe von der Transportseite.

## Cisco IOS XE und IOS XE SD-WAN (Seite 370)

- Ein Image **universalk9** für beide Betriebsarten ab **Release 17.2.x** auf ASR 1000, ISR 1000, ISR 4000, IR1101, Catalyst 8000 Edge, Catalyst 8000V. (Vorher separates IOS-XE-SD-WAN-Image, 16.x.)
- **Autonomous Mode** (Default) = klassisches IOS XE; **Controller Mode** = SD-WAN.
- Umschalten im privileged EXEC:
```
Router# controller-mode enable     ! -> Controller Mode (SD-WAN)
Router# controller-mode disable    ! -> Autonomous Mode
```
| Von → Nach | Verhalten |
|---|---|
| Autonomous → Controller | NVRAM und Startup-Config gelöscht (wie `write erase`), auch Zertifikate; Day-0-Zustand; vorherige Running-Config wird im **bootflash** gesichert, nicht automatisch wiederhergestellt |
| Controller → Autonomous | Controller-Datenbank (YANG-basierte Konfig) bleibt erhalten für späteres Zurückwechseln; IOS-Konfig wird nicht wiederhergestellt (Startup leer) → manuell aus Backup |

- Autonomous → Controller → Autonomous: IOS-Konfig weg, manuell restaurieren.
- Controller → Autonomous → Controller: ursprüngliche Controller-Konfig bleibt erhalten.

*(Ergänzung)* Im Controller Mode:
```
Router# config-transaction
Router(config)# system
Router(config-system)# system-ip 10.255.0.11
Router(config-system)# site-id 110
Router(config-system)# organization-name "ACME-WAN"
Router(config-system)# vbond 203.0.113.10
Router(config-system)# exit
Router(config)# sdwan
Router(config-sdwan)# interface GigabitEthernet1
Router(config-interface-GigabitEthernet1)# tunnel-interface
Router(config-tunnel-interface)# encapsulation ipsec
Router(config-tunnel-interface)# color mpls restrict
Router(config-tunnel-interface)# commit
```
Dazu ein `interface Tunnel1` mit `tunnel source GigabitEthernet1` und `tunnel mode sdwan`. Änderungen erst mit **commit** aktiv (Transaktionsmodell).

Show-Befehle (IOS XE SD-WAN):
- `show sdwan control connections` – DTLS/TLS-Verbindungen zu Validator/Manager/Controllern (Peer-Typ, System-IP, Site-ID, State up)
- `show sdwan control local-properties` – eigene System-IP, Org-Name, Zertifikatsstatus, public/private IP je TLOC
- `show sdwan omp peers`, `show sdwan omp routes`, `show sdwan omp tlocs`
- `show sdwan bfd sessions` – BFD-Sessions je TLOC-Paar (Color lokal/remote, State, Uptime)
- `show sdwan app-route stats` – Loss/Latency/Jitter je Tunnel
(Auf vEdge/Viptela OS jeweils ohne `sdwan`, z. B. `show control connections`.)

Beispiel (gekürzt, eigenes Beispiel):
```
Edge1# show sdwan bfd sessions
SYSTEM IP     SITE ID  STATE  SOURCE TLOC COLOR  REMOTE TLOC COLOR  ENCAP
10.255.0.21   120      up     mpls               mpls               ipsec
10.255.0.21   120      up     biz-internet       biz-internet       ipsec
```

## Flexible Controller-Deployment (Seite 371)

| Modell | Hosting | Verantwortung |
|---|---|---|
| **Cisco-cloud-hosted** (Cisco CloudOps, **empfohlen**) | AWS oder Azure, single/multi zone | Cisco: Provisionierung, Zertifikate, Skalierung/Redundanz, Backups, Snapshots, Disaster Recovery; Kunde bekommt Admin-Zugang zum Manager (Templates, Control-/Data-Policies) |
| **MSP/Partner-hosted** | private Cloud des Partners oder AWS/Azure | MSP/Partner: Provisionierung, Backups, DR |
| **On-premises** (privates RZ/Private Cloud) | eigenes RZ | Kunde: Provisionierung, Backups, DR, Resilienz; typisch Banken/Behörden (Security/Compliance) |

Default bei Cisco-Cloud: je 1 Manager, Validator, Controller in der Primärregion + zusätzlicher Validator und Controller in einer Sekundär-/Backup-Region. Ein MSP kann Kunden mit jedem der Modelle betreuen.

## Fehler/Ungenauigkeiten im Kurs

1. **Service-VPN-Bereich**: Kurs nennt "VPN 1-65535 (512 reserved)". Korrekt: Service-VPNs **1–65525 ohne 512**; 0 und 512 sind Transport/Management, Nummern oberhalb 65525 intern reserviert (Cisco Catalyst SD-WAN Segmentation Configuration Guide IOS XE 17.x: "Range: 1 to 65525, excluding 512").
2. **Alte Namen**: Orchestration-Plane-Liste spricht von "vSmart controllers" und Seite 362 von "Cisco SD-WAN solution" – aktuell SD-WAN Controller/Catalyst SD-WAN.
3. **Color-Liste** inkonsistent: einmal "private1, private2", an anderer Stelle "private1–6"; Schreibweise "Metro Ethernet"/"public internet" statt der CLI-Keywords `metro-ethernet`/`public-internet`; "3G" heißt in der CLI `3g`.
4. **BFD und Stromausfall**: Der Kurs behauptet, BFD erkenne Ausfälle durch Stromausfall oder Spannungsabfall. Gemeint sind wohl "Blackout/Brownout" im Netzwerksinn (Totalausfall bzw. Qualitätsverschlechterung eines Pfads). BFD misst Pfad-Erreichbarkeit und -Qualität, nicht die Stromversorgung.
5. **Templates**: Der Kurs nennt nur Device Templates; seit Manager 20.12/IOS XE 17.12 sind **Configuration Groups** der empfohlene Weg (Release Notes Catalyst SD-WAN Manager 20.12).
6. **NFV-Plattformen**: ENCS 5000 und CSP 2100/5000 sind End-of-Sale; aktueller Weg für uCPE ist Catalyst 8200 uCPE bzw. Catalyst 8000V.
7. "VPN 0 enthält zunächst alle Interfaces, deaktiviert" beschreibt das Verhalten von vEdge (Viptela OS); auf IOS-XE-Edges entspricht VPN 0 der globalen Tabelle.
8. Tippfehler im Kurs: "control panel traffic" (gemeint control plane), "callled", "notaion".

## Bilder

Ordner: encor-1.4.10\bilder\32-sdwan\
- `01-planes.svg` – Vier Planes (Orchestration, Management, Control, Data) mit Komponenten (neue/alte Namen) und Verbindungsarten.
- `02-onboarding.svg` – Onboarding-Ablauf einer WAN Edge: PnP → Validator (DTLS, Auth, STUN) → Manager/Controller → OMP → IPsec/BFD.
- `03-omp-routes.svg` – OMP-Route-Reflector-Prinzip mit den drei Routentypen (OMP, TLOC, Service routes) und Inhalten.
- `04-tloc.svg` – TLOC-3-Tupel am Beispiel einer Edge mit zwei Transporten (metro-ethernet, biz-internet).
- `05-colors.svg` – Entscheidungstabelle public/private Color und Wirkung von `restrict` auf BFD-Sessions.
- `06-nat-stun.svg` – Public/Private-IP-Beispiel: Controller hinter NAT, Edge mit MPLS und Internet.
- `07-vpns.svg` – Transport-Seite (VPN 0), Management (VPN 512), Service-VPNs mit gültigen Bereichen und IOS-XE-Entsprechung.
- `08-modes.svg` – universalk9: Autonomous vs. Controller Mode und was beim Wechsel mit der Konfiguration passiert.
- `09-deploy.svg` – Drei Controller-Deployment-Modelle und Verantwortlichkeiten.
