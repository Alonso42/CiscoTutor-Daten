# Examining Wireless Deployment Options

Quelle: ENCOR 1.4.10 Student Guide, Seiten 150–156 (Intro 149, Summary Challenge 157 und Answer Key 158 nicht verwendet)

Topics: ENCOR-LEGACY-WLAN (Wireless ist im ENCOR-Blueprint v1.2 kein eigenes Prüfungsthema mehr; Grundlagen zu WLC-Architekturen und AP-Modi sind CCNA-Stoff)

> Aktualitätshinweis: Der Kurs beschreibt teilweise AireOS-Begriffe (AP-Manager-Interface, Mobility Express, Cisco Prime, Cisco DNA Center, CMX). AireOS-Controller (3504, 5520, 8540) und Mobility Express sind End-of-Sale/End-of-Life (letzter AireOS-Zweig 8.10). Aktuelle Cisco-Plattformen: **Catalyst 9800** (Appliance 9800-L/-40/-80, virtuell **9800-CL** privat oder Public Cloud, **Embedded Wireless Controller (EWC)** auf Catalyst-9000-Switches für SD-Access bzw. auf Catalyst-9100-APs als Nachfolger von Mobility Express) und **Cisco Meraki** (Cloud-Management). Cisco DNA Center heißt heute **Catalyst Center**, CMX wurde durch **Cisco Spaces** abgelöst.

## Wireless Deployment Overview

Fünf Bereitstellungsmodelle:

| Modell | Typischer Einsatz | Kernidee |
|---|---|---|
| Autonomous | Hotspot, sehr kleine Firma, wenige APs | Jeder AP eigenständig konfiguriert und verwaltet, günstig, einfach |
| Centralized (Unified, Local Mode) | Campus, großer Standort | Lightweight APs an Switches, CAPWAP-Tunnel zum zentralen WLC, Client-Daten laufen über den WLC |
| FlexConnect | Branch/Remote Office mit wenigen APs, WLC nur zentral | AP wird zentral gesteuert, Daten wahlweise zentral (CAPWAP zum WLC) oder lokal am AP-Ethernet ausgeleitet |
| SD-Access Wireless | Campus mit SD-Access-Fabric | Wireless in die Fabric integriert, gruppenbasierte Policy statt VLAN-zentriert, Automatisierung über Catalyst Center (früher DNA Center) |
| Cloud-managed | Verteilte Standorte, schlanke IT | Controller/Management in der Cloud: Meraki oder 9800-CL in der Cloud; zentrale Installation, skaliert von klein bis groß, senkt Betriebs- und Personalkosten |

## Autonomous AP Deployment

- Jeder AP und sein WLAN sind eigenständige Einheiten ohne Wissen über andere APs (jeder AP = unabhängige Zelle). "Network of convenience", nicht geschäftskritisch.
- Sinnvoll für sehr kleine Umgebungen (Kurs: grob bis ca. 5 APs), z. B. kleines Büro, Laden, Lobby, Lager; Geräte mit geringen Anforderungen (Handscanner, einfache Monitoring-Geräte).
- Früher die einzige Option; heute kleiner Anteil neuer Installationen.
- **Vorteile:** geringe CapEx, passt zu wenigen APs pro Standort, lokale Funktionen für kleine Netze (lokaler RADIUS/Benutzerdatenbank, DHCP), einfache dynamische Kanalwahl.
- **Grenzen:**
  - Jeder AP einzeln verwaltet → Konfigurationsinkonsistenzen, einzelne Software-Upgrades, schlecht skalierbar.
  - Nur Basisfunktionen: kein dynamisches RRM, keine Rogue-Erkennung/-Abwehr, kein wIPS, kein Guest Access (im Sinne einer zentralen Gastlösung).
  - Kein schnelles, sicheres Roaming über Subnetzgrenzen. **WDS (Wireless Domain Services)** verteilt Roaming-Credentials nur zwischen APs im **selben Subnetz**.
- Konfiguration: im Wesentlichen SSID, Security-Methode und Sendeleistung (damit das Signal nicht in Nachbarflächen oder auf den Parkplatz reicht).
- Autonome APs lassen sich in Lightweight-(CAPWAP-)APs umwandeln (anderes Image) – eine Migration zu Controller-basiert ist möglich.

### Datenfluss autonom
- **Wireless → Wired:** AP wandelt 802.11 in 802.3 und gibt den Frame an den Access-Switch. Deshalb galt WLAN früher als bloße Erweiterung des LANs.
- **Wireless → Wireless, gleicher AP, gleiches Subnetz:** Verkehr bleibt im AP, belastet den Switch nicht.
- **Gleicher AP, verschiedene VLANs:** AP routet nicht; Verkehr geht ins LAN bis zum Router und zurück zum AP.
- **Clients an verschiedenen APs:** immer über die kabelgebundene Infrastruktur (Switch), selbst bei gleichem Switch und gleichem WLAN. AP-zu-AP-Funk nur für Spezialfälle (Gebäude-zu-Gebäude-Bridge).
- Designfolge: Clients in verschiedenen VLANs brauchen einen Router; zu große VLANs → viel Broadcast; kleinere VLANs empfohlen, aber Last aufs LAN beachten.

## Centralized (Unified) WLC Deployment

- Ein WLC konfiguriert, steuert und verwaltet viele **Lightweight APs**. APs arbeiten nicht eigenständig.
- **Split-MAC:** Der AP übernimmt die zeitkritischen (real-time) 802.11-MAC-Funktionen, der WLC alle nicht zeitkritischen.
  - AP (real-time): Beacons, Probe Responses, ACKs/Retransmissions, Frame-Queuing und -Priorisierung, 802.11-Verschlüsselung/Entschlüsselung, Umwandlung in CAPWAP.
  - WLC (non-real-time): Authentication, **Association/Reassociation** (Roaming), Security-/QoS-Policies, RRM, Rogue-Management, Client-Datenbank, 802.11-zu-802.3-Bridging.
- WLC kennt alle APs → Nachbarschaftswissen: **Self-Healing** (Nachbar-APs erhöhen Leistung bei AP-Ausfall), **Load Balancing** (Clients auf Nachbar-AP verschieben).
- Geeignet für: Enterprise-Campus, große Produktion, Krankenhäuser, Hochschulen, viel Customizing, **VoWLAN mit Roaming**, On-Prem-Management, Indoor/Outdoor, Mesh.
- **Vorteile:** zentrales Management/Troubleshooting (niedrige TCO), konsistente Konfiguration, RRM, High Availability (AP- und Client-SSO), Rogue Detection, wIPS, Identity Networking/RADIUS CoA/ISE, nahtloses Roaming für Voice und Daten, Location Services, Guest Access, Mesh, großer Funktionsumfang.
- **Grenzen:** sämtlicher Client-Verkehr läuft zum WLC; schlechte Nutzung von LAN/WAN, wenn Ressourcen verteilt sind; WLC kann Engpass werden; ohne Redundanz Single Point of Failure.
- Gegenmaßnahmen: WLC nahe an den APs (wenige schnelle Switches oder effizientes WAN, z. B. MPLS), ausreichend dimensionierte Links, Primary/Secondary(/Tertiary) WLC konfigurieren, konsistente Konfiguration auf allen WLCs; bei 9800 SSO-HA-Paar.

### CAPWAP
- Control And Provisioning of Wireless Access Points, offener IETF-Standard (**RFC 5415**, Binding für 802.11: RFC 5416). Nachfolger von Cisco LWAPP.
- **UDP 5246 = Control** (Discovery, Join, Konfiguration, Firmware-Download, Statistiken, Security-Durchsetzung, Client-Zugang/Mobility), **UDP 5247 = Data** (gekapselte Client-Frames).
- Control-Kanal ist immer **DTLS-verschlüsselt**; Data-DTLS ist optional (bei Cisco je nach Plattform/Lizenz konfigurierbar).
- Ziel-Port auf WLC-Seite 5246/5247, AP nutzt einen zufälligen Quellport.
- Zwei Betriebsarten laut RFC: **Split MAC** (Centralized/Local Mode) und **Local MAC** (FlexConnect-ähnlich, Bridging am AP).
- AP-Discovery des WLC (CCNA-Wissen): Layer-2-Broadcast im gleichen Subnetz, zuvor gespeicherte/geprimte WLC-Adressen, **DHCP Option 43**, DNS-Name **CISCO-CAPWAP-CONTROLLER.<domain>**, statisch per AP-CLI. Danach Join-Request/Response (DTLS), ggf. Image-Download, Konfiguration.
- DHCP Option 43 (Cisco-APs, Typ 0xF1): `f1` + Länge (4 × Anzahl WLCs, hex) + IP-Adressen in Hex. Ein WLC 192.168.10.5 → `f104c0a80a05`.

```
ip dhcp pool AP-VLAN10
 network 192.168.10.0 255.255.255.0
 default-router 192.168.10.1
 option 43 hex f104c0a80a05
```

### Datenfluss Centralized (AP im Local Mode)
- Jeder Client-Frame wird am AP in CAPWAP gekapselt (für jedes WLAN) und zum WLC gesendet: Quelle AP-IP/zufälliger Port → Ziel WLC (AireOS: AP-Manager- bzw. Management-Interface; 9800: Wireless Management Interface) UDP 5247. Rückweg umgekehrt. Client-VLAN und WLAN stecken unsichtbar in der Nutzlast.
- AP-Switchport: **Access-Port** im AP-Management-VLAN genügt (Client-VLANs existieren nur am WLC).
- WLC entkapselt, wendet Policy an (QoS, ACL), gibt das Paket als 802.3 im VLAN-Interface des Clients aus (Interface kann weitere ACLs haben). WLC-Uplink typischerweise Trunk (bzw. LAG/Port-Channel).
- **Ziel im LAN oder Client an anderem WLC:** kein direkter WLC-zu-WLC-Datenpfad, auch nicht in derselben Mobility Group. Verkehr geht zum VLAN-Gateway (Router). Der Last-Hop-Router fragt per ARP, der zweite WLC antwortet als **ARP-Proxy** für seinen Client, empfängt 802.3, wandelt in 802.11, kapselt in CAPWAP und schickt zum AP.
- **Zwei Clients am selben WLC, verschiedene APs, gleiches Subnetz:** WLC re-kapselt direkt in CAPWAP zum Ziel-AP; der Frame erreicht den Switch hinter dem WLC nicht.
- **Verschiedene VLANs am selben WLC:** WLC routet nicht → 802.3 ins VLAN des Quell-Clients → Router → zurück.
- **Beide Clients am selben AP:** trotzdem erst zum WLC (Haarnadel/Hairpin), damit QoS, Security, Bandbreitenlimits und Sichtbarkeit greifen.
- Mobility-Group-Mitglieder tauschen Client-MACs nur für Roaming aus, nicht für Datenweiterleitung (Ausnahme: Anchor/Foreign-Tunnel, z. B. Guest Anchor).
- Design: AP-zu-WLC- und WLC-zu-WLC-Links für diese Pfade dimensionieren.

## FlexConnect Deployment

- Erweiterung der Centralized-Architektur für Branch/Remote Offices. AP wird über WAN vom zentralen WLC gesteuert; kein WLC pro Filiale nötig.
- Kurs: geeignet für kleine bis mittlere Filialen, bis etwa 50 APs pro Standort (Richtwert des Kurses).
- **Central switching:** Daten per CAPWAP über WAN zum WLC (wie Local Mode).
- **Local switching:** Daten werden am AP-Ethernet ins lokale VLAN gebridged (WLAN-zu-VLAN-Mapping pro AP/Gruppe). AP-Switchport dann meist **Trunk**, Native VLAN = AP-Management-VLAN.
- **Split Tunneling:** Entscheidung nach Ziel – Firmenziele zentral, lokale Ziele lokal; vermeidet unnötigen WAN-Hin-und-Rückweg.
- **Central authentication** (WLC/ RADIUS über WLC) vs. **local authentication** (AP selbst bzw. direkt zum RADIUS).
- Use Cases: Einzelhandel, Restaurantketten, kleine Lager, Enterprise-Filialen; Migration weg von autonomen APs hin zu zentralem Management.
- **Vorteile:** viele Vorteile der zentralen Architektur, Hochverfügbarkeit/WLAN-Survivability bei WLC-Ausfall, schnelles sicheres Roaming in der Filiale (VoWLAN), dynamische VLAN-/ACL-Zuweisung pro User, flexible Optionen, WLC nur im Rechenzentrum, effiziente WAN-Nutzung (nur gewünschter Verkehr wird getunnelt), skaliert auf viele Filialen.
- **WAN-Anforderungen (Kurs/Cisco):** RTT < **300 ms** für Daten, < **100 ms** für Voice; WAN-MTU mindestens **500 Byte**. Cisco empfiehlt zudem mindestens 12,8 kbps WAN-Bandbreite pro AP (9800 FlexConnect Branch Deployment Guide). Für Roaming wird ein standortweites VLAN benötigt.
- Boot: AP muss den WLC zunächst erreichen, um die Konfiguration zu laden (Join + Konfig: einige zehn kbps für 5–6 s). Danach CAPWAP-Control-Keepalives, typisch ca. **0,35 kbps pro AP**.
- **Connected Mode** (WLC erreichbar): Authentifizierung zentral am WLC (sofern nicht Local Auth konfiguriert); lokal geswitchte WLANs bleiben lokal.
- **Standalone Mode** (WLC nicht erreichbar):
  - Bestehende Clients auf **lokal geswitchten** WLANs bleiben verbunden; neue Clients können sich weiter anmelden, wenn die Authentifizierung lokal möglich ist (Open, PSK, oder 802.1X mit lokalem/Backup-RADIUS bzw. Local EAP, in der FlexConnect Group/Flex Profile konfiguriert).
  - Clients auf **zentral geswitchten** WLANs werden getrennt; Reassoziation erst wenn der WLC wieder erreichbar ist.
  - Zentral authentifizierte WLANs: keine neuen Clients (keine zentrale Auth möglich), bestehende lokal geswitchte Sessions bleiben.
- **FlexConnect Groups (AireOS) / Flex Profile + Site Tag (9800):** gruppieren APs eines Standorts; teilen Schlüssel für Fast Roaming (CCKM/OKC/PMK-Caching), Backup-RADIUS-Server und Local Auth für Standalone, VLAN-Mappings, effizientes AP-Image-Upgrade (ein AP lädt über WAN, die anderen holen lokal).

9800-Konfiguration (Tag-Modell, Beispiel):
```
wireless profile policy PP-BRANCH
 no central switching
 vlan 20
 no shutdown
wireless tag site ST-BRANCH1
 flex-profile FP-BRANCH1
 no local-site
ap 00aa.bbcc.ddee
 site-tag ST-BRANCH1
 policy-tag PT-BRANCH
```
- `no local-site` im Site Tag = APs arbeiten im FlexConnect-Modus; `no central switching` in der Policy = Local Switching (Syntax mit Leerzeichen, analog `central authentication`, `central dhcp`, `central association`). Ein Local-Mode-AP, der einen Site Tag ohne Local Site erhält, rebootet und kommt im FlexConnect-Modus zurück.

## Cloud-Managed Meraki

- Controller-/Managementfunktion als Software in der Public Cloud (Meraki Dashboard im Browser). Wireless "Network as a Service" für Organisationen mit vielen Standorten, wenig IT-Personal, Fokus auf Einfachheit; Funktionsumfang trotzdem für große Unternehmen geeignet.
- Use Cases: Mittelstand und verteilte Standorte, Filialen ohne IT vor Ort, Organisationen, die bereits Cloud-Dienste nutzen.
- **Vorteile:** Zero-Touch Provisioning (Minuten statt Tage), Single Pane of Glass für Campus und Multisite, BYOD-Erkennung und Policies, Location Analytics, Application Visibility and Control, RF-Optimierung mit Echtzeit-Spektrumanalyse (Auto RF), dedizierter Security-Radio (Scanning aller Kanäle auf Interferenz/Angriffe), Firmware-Upgrades über das Web (planbar, verschiebbar).
- **Grenzen (Kurs):** Organisation muss Cloud akzeptieren, weniger Customizing als On-Prem-WLC, eine Architektur = weniger Flexibilität, standortweites VLAN für (Voice-)Roaming, begrenzte Integration mit Drittanbietern. (Kursaussage "kein Layer-3-Roaming" ist veraltet – siehe Fehler.)
- **Datenfluss:** APs bauen selbstständig eine sichere Verbindung zur Meraki Cloud auf, registrieren sich und laden die Konfiguration. **Out-of-Band-Management**: nur Managementdaten laufen durch die Cloud, **Nutzerverkehr bleibt lokal**.
- Bei Cloud-Ausfall läuft das Netz weiter: Authentifizierung, Firewall-Regeln, Weiterleitung mit voller Leitungsrate; nur Management (Reports, Konfigurationsänderungen) fällt aus.
- Aktuell: Cisco-Wi-Fi-7-APs der CW917x-Serie sind "unified" und können wahlweise mit Meraki Dashboard oder Catalyst 9800 betrieben werden; Catalyst-Wireless kann im Meraki Dashboard überwacht werden.

## Catalyst 9800 Deployment Options

- IOS-XE-basierte Wireless Controller (Nachfolger von AireOS). Merkmale: Hochverfügbarkeit (SSO), nahtlose Software-Updates (Hot/Cold Patching/SMUs, Rolling AP Upgrade), eingebaute Sicherheit (Secure Boot, Image Signing, Runtime Defenses, Trustworthy Hardware), überall einsetzbar (On-Prem, Private/Public Cloud, embedded im Switch), Management per GUI, CLI, NETCONF/YANG, Catalyst Center; Model-Driven Telemetry, offene APIs.
- **Appliances:**
  - **9800-L**: fest, klein/mittel.
  - **9800-40**: fest, mittel/groß.
  - **9800-80**: modular, optionale 100G-Uplinks, sehr groß/Campus.
  - Skalierung (Datenblatt, gerundet): 9800-L bis 250 APs (mit Performance-Lizenz 500), 9800-40 bis 2000 APs, 9800-80 bis 6000 APs.
- **Embedded Wireless Controller (EWC) auf Catalyst 9000 Switch** (z. B. 9300): Software-Paket auf dem Switch, nur für **SD-Access** (APs nur im Fabric Mode); Topologien: 9300 als kombinierter Border/Control Plane oder **Fabric in a Box**. Kurs: bis 200 APs/4000 Clients pro Switch, max. zwei Instanzen pro Standort → 400 APs/8000 Clients. Vorteile: Catalyst-Funktionen (Segmentierung, ETA) für WLAN, 802.11ax, L2-Roaming ohne gespannte VLANs, kein Guest Anchor nötig, SSO im Stack.
- **EWC auf Catalyst 9100 AP** (nicht im Kurs, aktueller Nachfolger von Mobility Express): ein AP übernimmt die Controller-Funktion für kleine Standorte (bis ca. 100 APs je nach Modell), APs switchen lokal (FlexConnect-ähnlich).
- **9800-CL (Cloud/virtuell):** VM auf x86 – Private Cloud: VMware ESXi, KVM, Cisco NFVIS auf ENCS (Branch-Optimierung). Scale-Templates in einem Paket, Auswahl beim Instanziieren: **Small** 1000 APs/10.000 Clients, **Medium** 3000/32.000, **Large** 6000/64.000. Bis ca. 1,5 Gbps im zentralen Modus laut Kurs; aktuelles Datenblatt: bis 2,1 Gbps (Low-Throughput-Profil ohne SR-IOV), High-Throughput-Profile nur auf ESXi/KVM (daher für Centralized nur kleine Datenlast; große Datenmengen eher FlexConnect). Modi: Centralized, FlexConnect, Fabric. Bootstrap-Wizard.
- **Public Cloud (Kurs: AWS):** IaaS über AWS Marketplace, Instanz in einer VPC, nur mit (managed) **VPN** zum Standort, nur **FlexConnect mit Local Switching** (zentrale Authentifizierung), laut Kurs bis 3000 APs/32.000 Clients (aktuelles Datenblatt: bis 6000 APs/64.000 Clients); Deployment per CloudFormation-Template (empfohlen) oder EC2-Konsole. Inzwischen auch Google Cloud und Microsoft Azure unterstützt.
- Vorteile Virtualisierung: Hardware-Unabhängigkeit, Ressourcenteilung über Hypervisor, VM-Mobilität zwischen Servern/Standorten.

## Cisco Mobility Express (veraltet)

- Virtueller WLC auf einem 802.11ac-Wave-2-Aironet-AP (AireOS-basiert). **End-of-Sale/End-of-Life**; Nachfolger: EWC auf Catalyst-9100-APs.
- APs laufen standardmäßig mit CAPWAP-Image; für die Controller-Funktion muss das ME-Image installiert sein.
- **Primary AP** (früher "Master AP"): betreibt den virtuellen WLC und bedient gleichzeitig Clients; je nach Modell bis 100 APs/2000 Clients.
- **Subordinate APs:** nur Client-Service, müssen nicht Wave 2 sein.
- Kurs: **alle APs im selben VLAN** (Design-Empfehlung; laut Cisco Community können APs in anderen Subnetzen per DHCP Option 43 dennoch joinen – nicht offiziell belegt, daher nicht als harte Regel verwenden).
- Vorteile: einfache Einrichtung (Minuten), Management per Mobile App, Web-UI, Cisco Prime oder DNA Center; keine Controller-/AP-Lizenz-, keine Abo-Kosten; APs später an physischen WLC migrierbar.
- Funktionen: zentrale Authentifizierung + lokales Switching, Open/WPA2-PSK/WPA2-Enterprise, Guest-WLAN mit CWA/LWA und internen/externen Splash Pages, L2-Roaming ohne Mobility Groups, automatisches Failover auf neuen Primary AP.
- Over-the-Air-Setup: Primary AP bootet, sendet SSID **CiscoAirProvision** (kann bis 10 min dauern), Laptop verbinden, Browser zu **mobilityexpress.cisco** → Setup-Wizard.

## Designentscheidungen nach Standorttyp (eigene Zusammenfassung)

| Situation | Empfehlung |
|---|---|
| Ein Café/Shop, 1–3 APs, kein Budget für Controller | Autonomous oder Cloud (Meraki) |
| Großer Campus, VoWLAN, viel Customizing, On-Prem | Centralized mit 9800-40/-80 (SSO-HA) |
| Viele kleine Filialen, WLC nur im RZ, WAN < 300 ms RTT | FlexConnect mit Local Switching (9800 im RZ oder 9800-CL) |
| Verteilte Standorte, kaum IT, Cloud akzeptiert | Meraki |
| Kleiner SD-Access-Standort/Fabric in a Box | EWC auf Catalyst 9300 |
| Kleiner Standort ohne SD-Access, Controller ohne extra Hardware | EWC auf Catalyst-9100-AP (früher Mobility Express) |
| Kein Rechenzentrum, Controller in AWS/Azure/GCP | 9800-CL Public Cloud, VPN, FlexConnect Local Switching |

## Fehler/Ungenauigkeiten im Kurs

- **Meraki "No Layer 3 roaming"** ist veraltet: Meraki MR unterstützt Layer-3-Roaming (verteilt zwischen APs oder über einen MX-Concentrator). Quelle: Meraki Documentation, "Layer 3 Roaming" (documentation.meraki.com/MR/Client_Addressing_and_Bridging).
- **"Cisco CMX Location Analytics"** bei Meraki: Meraki hat eine eigene Location-Analytics-Funktion; CMX war ein separates On-Prem-Produkt und ist durch Cisco Spaces abgelöst.
- **"Cisco DNA Center"** heißt seit 2023 Catalyst Center.
- **Mobility Express** und AireOS-WLCs (AP-Manager-Interface, Cisco Prime) sind End-of-Life; Nachfolger EWC auf Catalyst-9100-APs bzw. Catalyst 9800 (Wireless Management Interface statt AP-Manager).
- **9800-CL Public Cloud nur AWS**: inzwischen auch Google Cloud Platform und Microsoft Azure unterstützt (Cisco 9800-CL Deployment Guides).
- **FlexConnect "AP übernimmt die Authentifizierung"** bei WLC-Ausfall: gilt für Open/PSK automatisch; 802.1X-Neuanmeldungen nur, wenn Local Auth (Local EAP) oder Backup-RADIUS in FlexConnect Group/Flex Profile konfiguriert ist (Cisco FlexConnect Feature Matrix).
- Kurs nennt EWC nur für den Switch; EWC auf Catalyst-9100-APs fehlt. (Ein Non-SD-Access-Modus des EWC auf Catalyst-9000-Switches existierte kurzzeitig, letzter Release 17.3.x, End of Support – Cisco "EWC on Catalyst Switches (Non-SD-Access) Deployment Guide".)
- **9800-CL-Durchsatz/Public-Cloud-Skalierung**: Kurswerte (1,5 Gbps, 3000 APs in der Public Cloud) sind älter; aktuelles 9800-CL-Datenblatt: bis 2,1 Gbps (Low Profile), Public Cloud bis 6000 APs/64.000 Clients.

## Bilder

- `bilder/15-wlan-deploy/01-modelle.svg` – Die fünf Deployment-Modelle nebeneinander mit Ort des Controllers und Datenpfad.
- `bilder/15-wlan-deploy/02-autonom.svg` – Datenflüsse in autonomen Netzen: Wireless→Wired, gleicher AP, verschiedene APs.
- `bilder/15-wlan-deploy/03-splitmac.svg` – Aufgabenteilung Split-MAC zwischen AP und WLC und der CAPWAP-Tunnel mit UDP 5246/5247.
- `bilder/15-wlan-deploy/04-zentral.svg` – Centralized-Datenpfade: gleicher AP (Hairpin über WLC), anderer AP, Client an anderem WLC über Router.
- `bilder/15-wlan-deploy/05-flex.svg` – FlexConnect Central vs. Local Switching sowie Verhalten im Connected- und Standalone-Mode.
- `bilder/15-wlan-deploy/06-meraki.svg` – Meraki Out-of-Band-Management: Management in der Cloud, Nutzerdaten bleiben lokal.
- `bilder/15-wlan-deploy/07-c9800.svg` – Catalyst-9800-Formfaktoren (Appliance, EWC, 9800-CL privat/öffentlich) mit Einsatzbereich.
- `bilder/15-wlan-deploy/08-mobexp.svg` – Mobility Express/EWC auf AP: Primary AP mit virtuellem WLC und Subordinate APs im gleichen VLAN.
- `bilder/15-wlan-deploy/09-design.svg` – Entscheidungsbaum: welches Deployment für welchen Standorttyp.
