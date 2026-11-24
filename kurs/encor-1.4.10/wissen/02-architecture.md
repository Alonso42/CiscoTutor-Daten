# Examining Cisco Enterprise Network Architecture

Quelle: ENCOR 1.4.10 Student Guide, Seiten 12–17 (11 Intro, 18 Summary Challenge und 19 Answer Key nicht ausgewertet)

Topics: ENCOR-1.1.a (Enterprise-Netzdesign: Two-/Three-Tier, Fabric, Cloud – Hauptthema), ENCOR-1.1.b (Hochverfügbarkeit: Redundanz, FHRP, EtherChannel, Perpetual PoE), ENCOR-1.2.a (SD-WAN – hier nur Cloud OnRamp). SD-Access-Details stehen in Kapitel 31, SD-WAN-Komponenten in Kapitel 32, FHRP/SSO/StackWise Virtual in Kapitel 11.

Ergänzungen, die nicht im Kurs stehen, sind mit *(Ergänzung)* markiert. Quellen dafür: Cisco Campus LAN and Wireless LAN Design Guide (CVD), Catalyst 9300 Interface and Hardware Configuration Guide (PoE), Cisco Catalyst SD-WAN Cloud OnRamp Configuration Guide, IEEE 802.3-Standards.

## Cisco Enterprise Architecture Model (Seite 12)

Das Modell teilt das Unternehmensnetz in **funktionale Module**. Vorteile:
- Fehler bleiben im Modul isoliert.
- Änderungen/Upgrades lassen sich modulweise und kontrolliert einführen.
- Dienste wie Security und QoS werden ebenfalls modular umgesetzt.

| Modul | Inhalt | Beispiele |
|---|---|---|
| **Enterprise Campus** | festes Gelände (ein Gebäude oder Gebäudegruppe), dreistufig Access/Distribution/Core, plus **Data Center Submodule** | Universität, Industriegelände |
| **Enterprise Edge** | Verbindung nach außen; Vermittler zwischen Campus (Anbindung über den **Core**) und den anderen Modulen | Internet Edge (ein oder mehrere ISPs), Terminierung von Remote-Access- und Site-to-Site-VPN, WAN Edge (eingekaufte WAN-Dienste: MPLS, Metro Ethernet, SONET) |
| **Service Provider Edge** | Verbindung zwischen Hauptstandort und entfernten Standorten; Funktionen/Features werden durch die **Service-Verträge** (SLAs) mit den Providern bestimmt | ISP-Internet, MPLS-Provider, Metro-Ethernet-Provider |
| **Remote Locations** | geografisch entfernte Teile des Unternehmens | Branch Offices, Teleworker, **entferntes Rechenzentrum** |

Data Center Submodule (im Campus):
- zentralisiert Server für interne Nutzer: Application, File, E-Mail, DNS
- beherbergt typischerweise Netzwerk-Management (Monitoring, Logging, Troubleshooting)
- intern als **Spine-Leaf**-Architektur aufgebaut

Kursabbildung: Main Office (Access/Distribution/Core + Data Center) → Enterprise Edge mit Internet Edge (Firewalls, Server) und WAN Edge (Router zu Metro-Ethernet- und MPLS-Provider) → Service Provider Edge (ISP, WAN-Provider-Wolken) → Remote Locations (Remote Worker, Branch Offices).

### Design-Ziele (die vier „Self-“-Eigenschaften)

| Eigenschaft | Bedeutung | Beispiele (Seite 14) |
|---|---|---|
| **Self-healing** | dauerhaft verfügbar | redundante Komponenten und Verbindungen, RF-Störungen erkennen und abmildern, Geräte entfernen ohne Unterbrechung |
| **Self-defending** | schützt Organisation und Nutzer | Basisschutz im Wired-Netz, erweitert durch **TrustSec**-Segmentierung; Rogue-Device-Erkennung im WLAN |
| **Self-optimizing** | passt sich an Anforderungen jenseits der Basis-Standards an | z. B. geschäftskritische Apps auf Smartphones bekommen Vorrang auf dem knappen Funkmedium |
| **Self-aware** | Veränderung durch Einblick in die Netzaktivität | Application Visibility mit **NetFlow** und **NBAR**, Wireless **Hyperlocation** und Analytics für ortsbezogene Dienste |

Reihenfolge-Logik im Kurs: Resilienz → Verteidigung (Störungen vermeiden) → Optimierung → Einblick.

### Trends und Zukunftsanforderungen

- **Skalierbarkeit** über die Lebensdauer.
- **Multigigabit**: APs mit 802.11ac Wave 2 brauchen mehr als 1 Gbit/s. **IEEE 802.3bz** definiert **2.5 und 5 Gbit/s** über vorhandene Kupferverkabelung (Cat5e/Cat6) → Cisco Catalyst Multigigabit, ohne neue Verkabelung.
- **PoE** für Geräte mit hohem Bedarf (Beleuchtung, Kameras, VDI-Terminals, Remote-Access-Switches, APs): **Cisco UPOE = 60 W pro Port**. Access-Switches sollen **Perpetual PoE** bieten (Strom bleibt während Switch-Upgrade/Reboot). Catalyst 9000 Access ist Perpetual-PoE-fähig und laut Kurs „bereit für 100 W“.
- **Compliance**: Plattformen mit Zertifizierungen und **MACsec**; Analysedaten über **NetFlow** bereitstellen.
- **IoT/IoE**: **TrustSec** und andere Segmentierungs-/Virtualisierungstechniken.
- **Bandbreite** verdoppelt sich mehrfach über die Lebenszeit → Aggregation von 10 → 40 → 100 Gbit/s einplanen.
- Plattformen mit **Langlebigkeit** wählen statt nur den heutigen Bedarf zu decken.

*(Ergänzung)* PoE-Stufen (Leistung am Switch-Port/PSE):

| Standard | Name | max. PSE-Leistung |
|---|---|---|
| IEEE 802.3af | PoE | 15,4 W |
| IEEE 802.3at | PoE+ | 30 W |
| Cisco UPOE / 802.3bt Type 3 | UPOE | 60 W |
| Cisco UPOE+ / 802.3bt Type 4 | UPOE+ | 90 W |

*(Ergänzung)* Perpetual PoE vs. Fast PoE auf Catalyst 9000:
- **Perpetual PoE** (`power inline port perpetual-poe-ha`): Strom bleibt beim Soft-Reload/Upgrade des Switches ununterbrochen erhalten.
- **Fast PoE** (`power inline port poe-ha`): Nach einem Stromausfall des Switches wird PoE sofort nach Wiederkehr der Versorgung geliefert, ohne auf das vollständige Booten von IOS XE zu warten (laut Cisco UPOE+-Deployment-Guide innerhalb von ca. 25 s; der Switch merkt sich die zuletzt gelieferte Leistung). Fast PoE wirkt nur, wenn auch Perpetual PoE konfiguriert ist. Perpetual PoE gilt auch bei Crash und Software-Upgrade (Ausnahme: MCU-Firmware-Upgrade).

```
Switch(config)# interface GigabitEthernet1/0/10
Switch(config-if)# power inline port perpetual-poe-ha
Switch(config-if)# power inline port poe-ha
Switch# show power inline
Module   Available     Used     Remaining
          (Watts)     (Watts)    (Watts)
------   ---------   --------   ---------
1           445.0      440.6         4.4
Interface Admin  Oper       Power   Device              Class Max
--------- ------ ---------- ------- ------------------- ----- ----
Gi1/0/1   auto   on         30.0    AP-Floor1           4     60.0
Gi1/0/12  auto   power-deny 0.0     n/a                 n/a   60.0
```
`power-deny` = Gerät erkannt, aber das PoE-Budget reicht nicht.

### Cisco Networking (Roadmap)

- Zentraler Controller mit offenen APIs: **Cisco DNA Center** (heute **Catalyst Center**) automatisiert Konfiguration und Management gemäß Intent, über GUI oder vorhandene Orchestrierungssysteme.
- **SD-Access** ist das Fundament: Onboarding, sichere Segmentierung, IoT-Integration, Gastzugang; Policy für Nutzer/Geräte über **eine Fabric** für Wired und Wireless.
- **SD-WAN**: sichere, cloudbasierte, programmierbare Architektur; verwaltet über **vManage** (heute SD-WAN Manager); Overlay verbindet Rechenzentren, Branches, Campus und Colocation.

## Campus LAN Design Fundamentals (Seite 13)

- LAN = Infrastruktur für ein Stockwerk/Gebäude; Campus = mehrere LANs auf kleinem Gebiet. Der Campus verbindet am **Core** zu WAN- und Internet-Edge.

### Flaches vs. hierarchisches Netz

- **Flat Network**: alles über L2-Switches verbunden, **keine Subnetze**, alle teilen sich die Bandbreite und sind in **einer Broadcast-Domäne**. Jeder Broadcast kostet CPU-Zeit auf jedem Gerät; bei Hunderten Hosts schlechte Leistung.
- **Segmentierung** mit L3-Gerät (Router/L3-Switch): Broadcasts enden am L3-Gerät.
- Gutes Design: Netz lässt sich **verdoppeln** ohne große Designänderungen; neue Komponenten (WAN-Link, Etage, Gebäude, Filiale) erfordern Änderungen **nur an direkt angeschlossenen Geräten**.

### Schichten (wie beim OSI-Modell: Schichten vereinfachen)

Jede Schicht hat eigene Funktionen → passende Systeme/Features pro Schicht; modular, erleichtert Implementierung und Troubleshooting.

| Schicht | Aufgabe |
|---|---|
| **Access** | Nutzerzugang; Switch-Ports für Workstations/Server. Im WAN: Zugang für Teleworker/Remote-Sites über WAN-Technik |
| **Distribution** | aggregiert Wiring Closets, segmentiert Workgroups, isoliert Netzprobleme; aggregiert auch WAN-Verbindungen am Campus-Rand; policy-basierte Konnektivität |
| **Core** (= **Backbone**) | Hochgeschwindigkeits-Backbone, Pakete so schnell wie möglich vermitteln; hohe Verfügbarkeit, schnelle Anpassung, Skalierbarkeit, schnelle Konvergenz |

### Routed vs. Switched Access

| | Layer-2-Access (switched/bridged) | Layer-3-Access (routed) |
|---|---|---|
| VLAN-Terminierung (Gateway) | Distribution | Access-Switch |
| Uplinks Access–Distribution | L2-Trunks; STP blockiert (im Looped-Design) etwa die Hälfte | geroutete Links, alle Geräte nehmen am Routing teil |
| Kosten | traditionell, günstiger | aufwändigere Planung |
| VLAN über mehrere Access-Switches | möglich, aber **nicht empfohlen** | **nicht möglich** – jedes VLAN ist lokal |
| Herausforderung | STP-Blocking, Schleifen | Verkehrstrennung (z. B. Gast vs. intern) muss geplant werden |

*(Ergänzung)* Bei Routed Access werden beide Uplinks per **ECMP** (Equal-Cost Multipath, CEF-Lastverteilung) genutzt; Voraussetzung sind gleiche IGP-Kosten. Verkehrstrennung im gerouteten Netz erfolgt über Pfadisolation, z. B. **VRF-Lite** oder SD-Access (Virtual Networks). Cisco empfiehlt für Access-Switches im Routed Access z. B. **EIGRP stub** bzw. OSPF-Stub-Bereiche und Summarization an der Distribution.

```
! Access-Switch, Routed Access – Uplink als L3-Port
interface GigabitEthernet1/0/49
 no switchport
 ip address 10.0.1.2 255.255.255.252
 ip ospf network point-to-point
!
router eigrp 100
 eigrp stub connected summary
```
Typische Routing-Tabelle (zwei gleichwertige Pfade):
```
O*E2  0.0.0.0/0 [110/1] via 10.0.1.1, 2d01h, GigabitEthernet1/0/49
                [110/1] via 10.0.2.1, 2d01h, GigabitEthernet1/0/50
```

## Traditional Multilayer Campus Layer Design (Seite 14)

- Das Modell gilt auf Campus- oder Gebäudeebene; teilt in physische, logische und funktionale Bereiche.
- **Keine festen Regeln** für den physischen Aufbau: oft drei physische Stufen, kleiner Campus zwei Stufen (**Collapsed Core** = Core und Distribution in einem physischen Switch), große Netze vier oder mehr Stufen (wenn Größe, Verkabelung oder Geografie einen erweiterten Core verlangen). Hierarchie ≠ physische Topologie; entscheidend ist die **Rolle** jedes Elements.

### Access Layer

- Hier hängen Endgeräte (PCs, Drucker, Kameras) am Wired-Netz.
- Geräte, die das Netz **eine Ebene weiter** verlängern: **IP-Telefone** und **Wireless APs**.
- Wegen der vielen Gerätetypen, Dienste und dynamischen Konfigurationsmechanismen **eine der funktionsreichsten Schichten**.
- Die vier Self-Eigenschaften werden hier am Access-Layer konkret (siehe Tabelle oben).

### Distribution Layer

- **Service- und Control-Grenze** zwischen Access und Core (beide sind „Spezial-Schichten“).
- Wichtig: Verfügbarkeit, schnelle Pfadwiederherstellung, Load Balancing, QoS.
- Hochverfügbarkeit durch **doppelte Pfade** Access→Distribution und Distribution→Core; **L3 Equal-Cost Load Sharing** nutzt beide Uplinks zum Core.
- Routing und Paketmanipulation; **Routing-Grenze** zwischen Access und Core; **Redistributionspunkt** zwischen Routing-Domänen bzw. Grenze zwischen statischem und dynamischem Routing.
- Kontrollierte Routing-Entscheidungen und Filterung → policy-basierte Konnektivität, QoS.
- **Summarization** der Access-Routen (bessere Routing-Performance); bietet manchen Netzen eine **Default Route** an Access-Router, spricht dynamische Protokolle Richtung Core.
- Mischung aus L2- und Multilayer-Switching; isoliert Probleme, damit sie den Core nicht erreichen.
- Terminiert üblicherweise die **VLANs** der Access-Switches; setzt Policies (QoS, Security, Traffic Loading, Routing) um.
- Gateway-Redundanz per **FHRP** (HSRP, GLBP, VRRP): Ausfall/Entfernen eines Distribution-Knotens ohne Auswirkung auf das Default Gateway der Endgeräte.

```
! Summarization an der Distribution (Beispiele)
router ospf 1
 area 10 range 10.10.0.0 255.255.0.0
!
interface TenGigabitEthernet1/1/1
 ip summary-address eigrp 100 10.10.0.0 255.255.0.0
```

### Core Layer

- Backbone und Aggregationspunkt aller Schichten und Module; hohe Redundanz, schnelle Anpassung.
- „Einfachster, aber kritischster“ Teil: sehr wenige Dienste, **always-on**.
- Ziel: nahezu sofortige Wiederherstellung bei Ausfall **jeder** Komponente (Switch, Supervisor, Line Card, Glasfaser); Hardware-/Software-Upgrades ohne Unterbrechung.
- **Keine komplexen Policies**, **keine direkt angeschlossenen Nutzer oder Server**, minimale Control-Plane-Konfiguration, hochverfügbare Geräte mit passender physischer Redundanz.
- Verbindet Endgeräte mit Rechen- und Speicherdiensten im Data Center und mit anderen Bereichen/Diensten.

*(Ergänzung)* Cisco empfiehlt zwischen Distribution und Core **geroutete Punkt-zu-Punkt-Links** (kein STP, Ausfall wird per Link-Down sofort erkannt, ECMP-Pfad wird aus der FIB entfernt). `ip ospf network point-to-point` spart DR/BDR-Wahl und Type-2-LSAs.

### Wann braucht man einen Core?

- Campus in einem Gebäude oder in benachbarten Gebäuden mit ausreichend Glasfaser → Core kann in die Distribution-Switches **kollabiert** werden.
- Ohne Core müssen Distribution-Switches **voll vermascht** werden: viel Verkabelung, steigende Routing-Komplexität (mehr Nachbarn).
- Formel (jeder Block mit 2 verbundenen Switches): **Links = B × (N − 2)**, B = Zahl der Blöcke, N = Zahl aller Distribution-Switches.

| Blöcke B | Switches N | Links | zusätzlich gegenüber vorher |
|---|---|---|---|
| 2 | 4 | 4 | +4 |
| 3 | 6 | 12 | +8 |
| 4 | 8 | 24 | +12 |
| 5 | 10 | 40 | +16 |
| 6 | 12 | 60 | +20 |

- Eigener Core: Wachstum ohne Umbau der Distribution-Blöcke, des Data Centers usw.; wichtig bei mehr Blöcken, größerer Fläche, mehr Komplexität.
- Hauptzweck eines separaten Cores: **Skalierbarkeit** und **weniger Risiko bei Moves/Adds/Changes**. Wenn routinemäßig Core-Geräte umkonfiguriert werden müssen, fehlt Modularität → Core und Distribution physisch trennen.
- *(Ergänzung)* Mit Core: jeder Distribution-Switch braucht nur Links zu den (z. B. zwei) Core-Switches → 2 × N Links, linear statt quadratisch. Der Cisco Campus Design Guide zählt Distributions als Einheiten: N × 2 Links mit Core statt N × (N − 1) / 2 im Full Mesh (andere Zählweise als die Kursformel, gleiche Aussage).

### Campus-Größen

| Design | Merkmale |
|---|---|
| **High-Density Large Campus** | mehrere Distribution-Schichten an einem Core; dichte Access-Anforderungen; > **15.000** Wired- und Wireless-Nutzer/Geräte; hochverfügbar, NetFlow, Netzvirtualisierung/Segmentierung. Auch bei geringerer Dichte wählbar, wenn Business Continuity oder erweiterte Funktionen gefordert sind. Ab **drei oder mehr** verbundenen Distributions (oder gemeinsamem Standort) → **Layer-3-LAN-Core**. |
| **Medium-Density Campus** | **eine** Distribution-Schicht, eigenständig oder als **Collapsed Core** (ggf. an weitere Distribution, Dienste oder einen WAN-Router eines groß gewordenen Remote-Standorts); Hunderte Ports; wenige Gruppen von je **≤ 50 APs**; typische Business-Continuity-Anforderungen |
| **Small-Site Campus** | **ein Access-Switch oder ein Switch-Stack**; Dutzende Ports; **< 25 APs**; Kosten minimieren |

## Campus Distribution Layer Design (Seite 15)

Drei Modelle: **Traditional**, **Simplified**, **Software-Defined Access**.

### Traditional

- L2 vom Access zur Distribution, dort die L3-Grenze; **zwei eigenständige Distribution-Switches**.
- **Loop-free** (VLAN auf einen Wiring Closet/Uplink-Paar beschränkt) oder **looped** (VLAN überspannt mehrere Access-Switches).
- Empfehlung: VLAN auf einen Wiring Closet beschränken → keine Schleifen, die STP blockieren muss (STP-Fehler sind häufige Ausfallursache). Nachteil: weniger Flexibilität.
- Gateway-Redundanz per FHRP (gleiche virtuelle MAC und IP pro VLAN). **HSRP und VRRP** am häufigsten, aber Hosts senden nur über **einen** Uplink; Verteilung der VLANs auf beide Uplinks erfordert Zusatzkonfiguration pro Distribution-Switch.
- **GLBP** verteilt Hosts auf mehrere Uplinks, aber **nur in nicht geschleiften Topologien** sinnvoll.
- Für Sub-Sekunden-Konvergenz müssen FHRP-Timer getunt werden → **CPU-Last**.
- Looped Design (wenn eine Anwendung dasselbe VLAN in mehreren Closets braucht): STP blockiert Links → weniger Bandbreite, langsamere Konvergenz, mehr Fehlkonfigurationsrisiko.
- *(Ergänzung)* STP bleibt auch im Loop-free-Design aktiv – als Schutz gegen Fehlverkabelung.

### Simplified

- Mehrere physische Switches als **ein logischer Switch**: Switch-Stack oder **VSS** (auf Catalyst 9000 heute **StackWise Virtual**), weniger bevorzugt: ein einzelner hochredundanter Chassis-Switch.
- Access per **EtherChannel** mit zwei Uplinks (dual-homed, *(Ergänzung)* = Multichassis EtherChannel, **MEC**) → alle Uplinks aktiv, STP-Abhängigkeit minimal – **auch wenn VLANs mehrere Access-Switches überspannen**.
- Lastverteilung über bis zu **8 Links**; mehrere Links im Bündel sind besser als Einzellinks.
- **Kein FHRP** nötig: Default Gateway auf **einer logischen Schnittstelle**, Resilienz durch die Distribution-Switches.
- Schnellere Konvergenz: EtherChannel-Failover im **Sub-Sekunden**-Bereich, kein Warten auf STP.
- Logisch **Hub-and-Spoke** → einfacheres Design und Troubleshooting; effizienteres **IP Multicast** (ein logischer DR pro Access-VLAN).
- Weniger Geräte zu verwalten.

```
Access# show etherchannel summary
Group  Port-channel  Protocol    Ports
------+-------------+-----------+--------------------------
1      Po1(SU)         LACP      Gi1/0/49(P)  Gi1/0/50(P)
! SU = Layer 2, in use; P = gebündelt
```

### Software-Defined Access

- Behebt die L2-Grenzen des Routed-Access-Designs, indem auf ein bestehendes **Layer-3-Access-Netz** eine **Fabric** gelegt wird – automatisiert durch SD-Access.
- **Overlay** (virtuelle Netze) über **Underlay** (physisches Netz) → alternative Topologien.
- Zusätzlich software-definierte Segmentierung und Policy nach **Benutzeridentität und Gruppenzugehörigkeit**, integriert mit **Cisco TrustSec**.
- *(Ergänzung)* Gateway: **Anycast Gateway** auf allen Fabric Edges (gleiche IP/MAC), daher weder FHRP noch STP im Underlay.

## Fabric and Cloud Enterprise Design (Seite 16)

### Cloud-Deployment-Modelle (nach Eigentum der Infrastruktur)

| Modell | Merkmal |
|---|---|
| **Private** | exklusiv für eine Organisation, kein öffentlicher Zugang; meist on-premises, kann aber **ausgelagert** werden |
| **Public** | Drittanbieter, meist als Dienst, öffentlich zugänglich, Abo-Gebühr |
| **Hybrid** | Mischung aus mindestens zwei Modellen, oft Private + Public |
| **Community** | von mehreren Organisationen mit ähnlichen Anforderungen zum gemeinsamen Nutzen; Beispiel: gemeinsamer Disaster-Recovery-Standort |

Auswahlfaktoren: **Sicherheitsbedenken, Deployment-Komplexität, Kosten**. Die passende Konnektivität hängt vom Deployment-Modell ab.

### Cloud-Konnektivität (drei Optionen)

| Option | Beschreibung |
|---|---|
| **Direct Connect** | private Verbindung zur Public Cloud statt VPN-Tunnel über das Internet |
| **MPLS Direct Connect** | über MPLS zu einem **Direct Connect Partner** (z. B. **Megaport**), der seinerseits per Direct Connect beim Cloud-Anbieter angebunden ist – z. B. wenn die eigene Region kein Direct Connect hat |
| **Cloud OnRamp** | Cisco-SD-WAN-Funktion, die die Anbindung on-prem → Cloud vereinfacht und automatisiert |

Vorteile Direct Connect: **Security** (kein öffentliches Internet), **Reliability** (eigene Kontrolle über Zuverlässigkeitsmechanismen), **Speed**.
*(Ergänzung)* Produktnamen: AWS **Direct Connect**, Microsoft Azure **ExpressRoute**, Google **Cloud Interconnect**.

### Cloud OnRamp – Nutzen

| Nutzen | Inhalt |
|---|---|
| **Multicloud Automation** | SD-WAN-Erweiterung in die Cloud direkt aus der Branch automatisieren – über Internet, Interconnect-Provider oder Colocation |
| **Unified Security** | Segmentierungs-Policy erweitern; Security on-prem oder cloud-delivered (**SASE**) |
| **Consumption Flexibility** | Cisco-, Cloud- und Colocation-Ressourcen bei Bedarf orchestrieren/bereitstellen |
| **Optimal Application Experience** | Sicht auf App-Performance zwischen Cloud und on-prem |

Ziel: Security und Application Experience in der Cloud wie on-prem, mit einheitlicher Policy über alle großen Cloud-Anbieter.

### Cloud OnRamp – fünf Use Cases (laut Kurs)

1. **Cloud Interconnect**: SD-WAN über Provider wie **Megaport** und **Equinix** an die Cloud; automatisiert die Anbindung an einen MPLS-Direct-Connect-Partner.
2. **Cloud Hub** (Google Cloud): Site-to-Cloud zu Workloads in Google Cloud und **Site-to-Site über Googles globales Backbone**, beides aus vManage automatisiert. DevOps definieren Traffic-Profile in der **Google Cloud Service Directory**; vManage zieht die App-Metadaten automatisch und NetOps setzen sie in Policies um. Vorteile: fertiges globales Netz, Management aus vManage, End-to-End-Sicht, Policy-Automatisierung für eigene Cloud-Apps.
3. **Cloud OnRamp for Multicloud**: z. B. AWS – vManage deployt automatisch **zwei SD-WAN-Edge-Virtual-Router** in einer **Transit-VPC** und ein **AWS Transit Gateway**; **IPsec**-Tunnel zwischen den virtuellen Routern und dem TGW werden automatisch gebaut. Ähnlich für Azure und Google Cloud.
4. **Cloud OnRamp for SaaS**: Echtzeit-Probes über alle möglichen Pfade zur SaaS-App; Pfadwahl nach Latenz und Verlust (Kurs nennt auch Jitter). *(Ergänzung)* Ergebnis ist ein vQoE-Score 0–10.
5. **Secure SD-WAN**: Integration mit **Cisco Umbrella** – DNS-Layer Security, Secure Web Gateway (SWG), Cloud-delivered Firewall, Cloud Access Security Broker (CASB), Threat Intelligence über **Cisco Talos**.

*(Ergänzung)* Cisco nennt außerdem **Cloud OnRamp for Colocation** (SD-WAN-Hub in einer Colocation nahe den Cloud-Anbietern).

## Summary (Seite 17)

Vier Module (Campus, Enterprise Edge, Service Provider Edge, Remote Locations); der Campus besteht aus Core, Distribution und Access mit je eigener Funktion.

## Fehler/Ungenauigkeiten im Kurs

1. **„Hot Standby Routing Protocol“** (Seite 15) – korrekt: **Hot Standby Router Protocol** (RFC 2281; Seite 14 schreibt es richtig).
2. **„four further models“** (Seite 17) – gemeint sind die vier **Module** des Enterprise-Architecture-Modells.
3. **„half of the uplinks are blocked“** bei Layer-2-Access (Seite 13) gilt nur für das **looped** Design (VLANs über mehrere Access-Switches). Im loop-free Design (VLAN pro Access-Switch, L3 zwischen den Distribution-Switches) blockiert STP keinen Uplink (Seite 15 und Cisco Campus Design Guide).
4. **„ready for 100W per port“** (Seite 12) – der höchste PoE-Standard IEEE 802.3bt Type 4 bzw. Cisco UPOE+ liefert **90 W** am Port (Cisco Catalyst 9000 PoE Configuration Guide).
5. **Cloud OnRamp for SaaS**: Kurs nennt Latenz, Verlust **und Jitter**; laut Cisco Configuration Guide wird der vQoE-Score aus **Verlust und Latenz** berechnet.
6. Veraltete Produktnamen: **VSS** (auf Catalyst 9000 ersetzt durch StackWise Virtual), **Cisco DNA Center** (heute Catalyst Center), **vManage** (heute Catalyst SD-WAN Manager).
7. Kurs listet „Secure SD-WAN“ als Cloud-OnRamp-Use-Case und lässt **Cloud OnRamp for Colocation** weg; bei Cisco ist Umbrella-Integration ein eigenes Security-Feature, Colocation ein offizieller OnRamp-Use-Case (Cisco Catalyst SD-WAN Cloud OnRamp Configuration Guide).

## Bilder

- `bilder/02-architecture/01-module.svg` – Die vier Module der Enterprise Architecture mit Submodulen (Internet Edge, WAN Edge, Data Center) und Beispielen.
- `bilder/02-architecture/02-flat-hier.svg` – Flaches Netz mit einer Broadcast-Domäne vs. hierarchisches Netz, in dem L3 die Broadcasts begrenzt.
- `bilder/02-architecture/03-layers.svg` – Access, Distribution und Core mit ihren typischen Aufgaben; Collapsed Core als Variante.
- `bilder/02-architecture/04-l2-vs-l3.svg` – Layer-2-Access vs. Routed Access: Lage der L2/L3-Grenze, STP-Blocking vs. ECMP.
- `bilder/02-architecture/05-fullmesh.svg` – Vollvermaschung ohne Core mit Formel B × (N − 2) und Tabelle vs. Stern mit Core.
- `bilder/02-architecture/06-dist-model.svg` – Traditional (loop-free/looped), Simplified (logischer Switch + MEC) und SD-Access im Vergleich.
- `bilder/02-architecture/07-sizes.svg` – Campus-Größen Small/Medium/Large mit Kennzahlen.
- `bilder/02-architecture/08-cloud.svg` – Cloud-Deployment-Modelle und die drei Anbindungsoptionen (Direct Connect, MPLS Direct Connect, Cloud OnRamp).
- `bilder/02-architecture/09-onramp.svg` – Die Cloud-OnRamp-Use-Cases (Interconnect, Cloud Hub, Multicloud, SaaS, Secure SD-WAN).
