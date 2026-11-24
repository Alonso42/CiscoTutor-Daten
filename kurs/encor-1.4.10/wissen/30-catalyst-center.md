# Exploring Cisco Catalyst Center – Network Automation and Management

Quelle: ENCOR 1.4.10 Student Guide, Seiten 334–345 (333 Intro, 346 Summary Challenge und 347 Answer Key nicht ausgewertet)

Topics: ENCOR-4.5 (Catalyst Center Workflows für Konfiguration, Monitoring, Management inkl. AI-gestützter Workflows – Hauptthema), ENCOR-6.4 (APIs von Catalyst Center: Intent API, Adapter, SDKs, Events), ENCOR-1.3.a (SD-Access: Policy-Typen, LAN Automation als Underlay-Automatisierung).

Ergänzungen, die nicht im Kurs stehen, sind mit *(Ergänzung)* markiert. Quellen dafür: Cisco Catalyst Center User Guide / Administrator Guide 2.3.x, Cisco Catalyst Center Platform (Intent API) Dokumentation auf developer.cisco.com, Cisco Network Plug and Play Solution Guide.

### Produktname

| Alter Name | Aktueller Name |
|---|---|
| Cisco DNA Center (DNAC) | Cisco Catalyst Center (seit Release 2.3.7, 2023) |
| Cisco DNA Assurance | Catalyst Center Assurance / AIOps |
| Cisco DNA Advantage/Essentials Lizenz | Cisco Catalyst Advantage/Essentials |
| Stealthwatch | Cisco Secure Network Analytics |

Der Kurs mischt beide Namen (z. B. „Cisco DNA Center“ in Fließtexten, URLs, Screenshots). Inhaltlich identisch.

## Lösungsüberblick (S. 334)

- Catalyst Center = zentrales Netzwerk-Managementsystem/Controller für Campus und Branch (wired + wireless, IT + OT) mit einer Konsole. Nutzt AI/ML für Automatisierung und Assurance.
- Betrieb: dedizierte physische Appliance oder virtuell (VMware ESXi, AWS).
- Nutzen: schnellere Inbetriebnahme (automatisiertes Provisioning, Zero-Touch), Routine-Automatisierung, weniger Ausfälle durch AI-Insights/Predictive Analytics, Prozessautomatisierung über APIs und Ökosystem, Einblick in Applikations-/Endbenutzer-Erlebnis, Zero-Trust-Sicherheit, Nachhaltigkeit (PoE-/Energie-Analytics, Smart Buildings).
- Integrationen: Cisco ISE (Authentifizierung, Policy), ThousandEyes, Cisco Spaces, ServiceNow (ITSM), Webex/Microsoft Teams, Apple/Samsung/Intel (Client-Analytics), Umbrella, Secure Network Analytics, Talos.
- Zero Trust: Authentifizierung + Autorisierung via ISE; Makro-Segmentierung (Virtual Networks/VRF) und Mikro-Segmentierung (SGT/Gruppen); AI Endpoint Analytics (Endpunkt-Klassifizierung, Trust Score); Software- und Konfigurations-Compliance.
- Key Features (Liste): SWIM, PnP, Network/Client Health Dashboards, Workflows, Machine Reasoning Engine (MRE), Application 360, Device 360 und Client 360, Wireless 3D Analyzer, AI-enhanced RRM, Group-based Policy/Segmentierung, AI Endpoint Analytics, Rogue Management + aWIPS, PoE Analytics, integriertes Ökosystem, APIs.

## Funktionsbereiche (S. 335)

Catalyst Center ist Controller und Analytics-Plattform im Zentrum von Intent-Based Networking (IBN). Fähigkeiten: Visibility, Observability, Insights, Automation, Zero Trust, Programmability.

Klassische Komponenten (Menüs):

| Bereich | Aufgabe |
|---|---|
| Design | Standorthierarchie (Karten, Gebäude, Etagen), Network Settings (AAA, DHCP, DNS, NTP …), Credentials, Image Repository (SWIM), Templates, Network Profiles |
| Policy | Benutzer-/Geräteprofile, Gruppen, Segmentierung, Zugriffs-/Applikations-Policies (SD-Access) |
| Provision | Policy-basierte Automatisierung: Inventory, PnP, Fabric-Domänen, Gerät an Site zuweisen, Templates ausrollen |
| Assurance | Health, Issues, Trends, 360-Sichten, Troubleshooting (AIOps) |
| Platform | Offene APIs, Adapter, SDKs, Events („360-Grad-Erweiterbarkeit“) |

Neue Fähigkeiten (Personas):

| Persona | Inhalt |
|---|---|
| NetOps | Automatisierung, Erstellen/Pflegen des Netzes; von manuell über AI-assistiert bis selektiv autonom |
| SecOps | AI-gestützte Sicherheit: Endpunkte klassifizieren, Policies durchsetzen, Zero Trust |
| AIOps | AI-gestützte Visibility/Observability/Insights/Troubleshooting für User, Apps, Infrastruktur |
| DevOps | APIs, SDKs, Closed-Loop-Integrationen ins Ökosystem |

## NetOps, Intent-Based Networking und Design (S. 336)

### NetOps
- Überträgt DevOps-Ideen (Automatisierung, Orchestrierung, Virtualisierung) auf den Netzbetrieb; Tools wie Ansible, Puppet, Chef wurden dafür erweitert. NetOps ist auch eine Kultur-/Denkweise, nicht nur Technik.
- Closed Loop mit ITSM (z. B. ServiceNow): Catalyst Center kann offene Tickets automatisch schließen, wenn der Fehler behoben ist.
- NetOps-Tools (Auswahl): Inventory-Updates/EoX/Credential-Status, Discovery-Verbesserungen, granularer Software-Upgrade-Workflow, CLI-Template-Compliance, RMA für modulare Switches/Fabric, AP-Refresh, Learn Device Configuration, UDN, 6-GHz-Radio-Konfiguration, Lizenztrends.

### Intent-Based Networking (IBN)
- Früher: Operator übersetzt Absicht („diese Server sollen von diesen Branches erreichbar sein“) manuell in VLAN-, Subnetz- und ACL-Konfiguration jedes Geräts („Human Middleware“, CLI/Skripte, „hoffentlich passt es“).
- IBN: Operator formuliert das gewünschte Ergebnis (Intent), ein Controller übersetzt es in Policies/Konfiguration und prüft laufend, ob das Netz es erfüllt. Intent kann auch Betriebsregeln sein, z. B. „nur Golden Images im Netz“.
- Drei Bausteine:
  1. **Translation** – Intent erfassen (GUI, Modell wie YANG/JSON/XML, definierte Syntax) und in ein einheitliches, modellbasiertes Policy-Modell überführen; bei Migration vorhandene Hosts und Policies automatisch entdecken.
  2. **Activation** – Policies in die relevanten Domänen (Campus, WAN, DC, Branch) verteilen, Gerätekonfiguration ableiten, Konsistenz prüfen und per standardisierten APIs (NETCONF/YANG, REST) programmieren.
  3. **Assurance** – kontextbasierte Datenanalyse: prüft, dass der Intent umgesetzt wurde und dauerhaft erreicht wird.
- Assurance-Aspekte: **Continuous Verification** (vor, während, nach Deployment; Telemetrie), **Insights and Visibility** (Analytics, ML/AI, Korrelation, Prognosen, Anomalien), **Corrective Actions** (Closed Loop: Abweichungen per Activation korrigieren – automatisch oder als Empfehlung an den Operator).
- Nur Controller-basierte Plattform mit offenen APIs kann Intent mit Applikationen/Systemen außerhalb des Netzes austauschen.

### Hierarchisches Design – Design-Workflow
Empfohlene Reihenfolge:
1. Hierarchie erstellen (Areas, Buildings, Floors)
2. Globale Network Settings (AAA, DHCP, DNS, NTP …)
3. Golden Image festlegen
4. Templates erstellen
5. Network Profiles definieren (Templates an Profile)
6. Profile/Geräte Standorten zuweisen

### Network Hierarchy
- Wurzel: **Global** (existiert per Default).
- **Area** (Site): keine physische Adresse (z. B. „United States“), größtes Element, enthält Sub-Areas und Buildings.
- **Building**: physische Adresse + Breiten-/Längengrad Pflicht, enthält Floors; kann KEINE Areas enthalten.
- **Floor**: nur innerhalb von Buildings (Cubicles, Wiring Closets, Floor Plans, AP-Platzierung).

### Network Settings
- Standardisierte Parametersätze: AAA (ISE/andere), PAN, DHCP, DNS, Syslog, SNMP, NTP, Zeitzone, MOTD.
- AAA: Netzwerkgeräte-Authentifizierung per RADIUS oder TACACS+; Client/Endpoint-AAA separat konfigurierbar (Kurs: nur RADIUS; nicht web-belegt); laut Kurs pro Catalyst Center nur EINE ISE-Deployment (Stand des Kurses; neuere Releases ggf. abweichend – nicht als Prüfungsfakt verwenden). Andere AAA-Server nur für Basisfunktionen.
- Vererbung: Global → Area → Building → Floor. Auf jeder Ebene überschreibbar (Override). Vererbungssymbol zeigt geerbte Werte; fehlt es, ist der Wert überschrieben. Site-Settings wirken auch auf alle Unter-Sites.
- Device Credentials: CLI, SNMP, HTTP(S). CLI-Credentials müssen vorab auf dem Gerät existieren und übereinstimmen; SNMP-Credentials kann Catalyst Center nach dem Hinzufügen pushen; HTTPS nur für NFVIS-Compute-Geräte. Global definierte Credentials werden von Sub-Sites geerbt; site-spezifische möglich.

### SWIM im Design
- Image Repository = Teil von Design. Compliance-Policy nach Geräterolle, Site oder beidem. Day-0 (Onboarding) und Day-N (Upgrade).
- Speichert Images, SMUs, Subpackages, ROMMON-Images.
- Integrity Verification: Checksumme beim Import gegen **KGV-Datei** (Known Good Values) von Cisco.
- Golden Image/SMU = validiertes, standardisiertes Image pro Gerätetyp; zusätzlich pro Rolle (ALL, Access, Border Router, Core, Distribution, Unknown).
- Import: lokal hochladen oder von cisco.com/URL laden.

### CLI Templates (Überblick)
- Interaktiver Editor; Create/Edit/Delete, Fehlervalidierung, Simulation, Versionierung, interaktive Befehle, Variablen, Makros.
- Template-Engine: **Apache Velocity** *(Ergänzung: aktuelle Releases unterstützen zusätzlich Jinja2)*.
- Regular Templates (Day-0 oder Day-N) und Composite (sequenziell, aus committeten Regular Templates).

### Network Profiles
- Typen je Gerätefamilie: Assurance, Firewall, Routing, Switching, Wireless (abhängig von Version).
- Ein Profil wirkt erst, wenn es einer Site zugewiesen ist. Pro Site nur EIN Profil je Typ (z. B. ein Switching-Profil); verschiedene Typen gleichzeitig möglich. Zweites Switching-Profil → Hinweis zum Ersetzen.

## SecOps, Automation, PnP-Grundlagen, Policies (S. 337)

- SecOps: proaktive Security-Scans, automatisierte PSIRT-Advisories, Bug-Scans (AI Network Analytics), AI Endpoint Analytics (welche Endpunkte, wie authentifizieren, welche Policy), Umbrella-Policies aus Catalyst Center ausrollen, Talos-Integration (Verbindungen zu Low-Reputation-Sites), IP-basierte Endpunkt-Klassifizierung, Extended Node Onboarding mit Essentials-Lizenz, Allowed AP List in Rogue/aWIPS.
- Automation-Nutzen: zentrale Verwaltung, Deployment in Minuten statt Tagen, geringere Kosten (Policy-Provisioning, Guided Remediation), Cloud-Services nutzen.
- PnP-Motivation: Vorab-Staging per Konsole teuer, langsam, fehleranfällig. PnP: Installateur vor Ort braucht keine CLI-Kenntnisse, Admin verwaltet zentral; Router (ISR/ASR, Catalyst 8000), Switches (Catalyst), APs.
- PnP-Komponenten: **PnP Agent** (in Cisco-Gerät eingebettet, findet Server per DHCP/DNS/…, spricht PnP-Protokoll über HTTPS), **PnP Server** (Catalyst Center, verteilt Images und Konfigurationen), **PnP Protocol** (Transport-Bindings und Schemata, HTTPS).
- Catalyst Center = SDN-Controller mit **Northbound REST APIs** und mehreren **Southbound-Protokollen** (Greenfield und Brownfield).
- SWIM-Automatisierung: Intent-basierte Upgrades (Standardisierung), Pre-/Post-Checks, Patching (SMUs wie Images verwaltet).
- SD-Access-Policy-Typen:

| Policy | Frage | Inhalt |
|---|---|---|
| Access Control | Wer darf auf was zugreifen? | Permit/Deny zwischen Gruppen (group-to-group) |
| Application | Wie wird Verkehr behandelt? | QoS, Application Caching |
| Traffic Copy | Welcher Verkehr wird überwacht? | SPAN für bestimmte Gruppen/Verkehr |

## AIOps (S. 338)

- AIOps nutzt Cisco AI Network Analytics: **Machine Learning, Machine Reasoning, Visual Analytics** → weniger Rauschen, schnellere Erkennung und Behebung.
- Visibility über Linsen: Geografie, Hierarchie, Topologie, Site/Building/Floor.
- Observability: Device-, Client-, Application-Health über KPIs → AI-basierte Issue-Erkennung und Root-Cause-Analyse; MRE (Kurs: „30 Jahre“, später „35 Jahre“ Cisco-Erfahrung).
- Insights: Trends/Änderungen über Zeit, systemgenerierte Issues für abnormales Verhalten.
- Tools: Catalyst Center Insights, AI-enhanced RRM Simulator, Wireless Client/AP Troubleshooting, Troubleshooting nicht gemanagter Geräte, Global Assurance Event Viewer, Intel Connectivity Analytics, Wireless Maps.

## DevOps / Platform (S. 339)

- DevOps-Tools: Dashboard für Splunk Enterprise, neue APIs, Rogue-AP-API.
- Platform = offenes, erweiterbares System; Nutzen: Business und IT verbinden, Betrieb straffen, heterogene (Fremd-)Netze verwalten, Innovation.
- „360-Grad-Erweiterbarkeit“ – vier Richtungen:

| Richtung *(Begriffe Ergänzung)* | Kurs-Begriff | Zweck / Beispiele |
|---|---|---|
| Northbound | Intent-based APIs (REST) | Apps/Skripte liefern Intent, holen Insights: Assurance, Path Trace, Command Runner, Template Programmer, Network Inventory/Discovery/Tagging, SDA, Topology, PnP, SWIM, NFV/Wireless Provisioning |
| Westbound | Process adapters (Integration API) | ITSM (ServiceNow), IPAM (Infoblox, BlueCat), Reporting (Tableau) |
| Eastbound | *(Ergänzung)* Events & Notifications | Webhooks, E-Mail, Syslog, SNMP-Trap an externe Systeme bei Events/Issues |
| Southbound | SDKs (Multivendor SDK) | Device Packs für Fremdhersteller-Geräte; Level-1-Operationen: Discovery, Inventory, Topology, Availability/Health, Command Runner |
| (seitlich im Kurs) | Domain adapters | Andere Domänen-Controller: Meraki Dashboard, Stealthwatch (Secure Network Analytics), DC, WAN, Security |

Hinweis: Im Kursbild sitzen Process Adapters links und Domain Adapters („X-Domain Integration“) rechts. Cisco-Entwicklerdoku nennt Eastbound = Events & Notifications, Westbound = Integration (ITSM/IPAM). Für die Prüfung: Northbound = Intent API (REST/JSON), Southbound = Gerätezugriff (CLI/SSH, SNMP, NETCONF, HTTPS, Streaming Telemetry) bzw. Multivendor SDK.

*(Ergänzung)* Intent API:
- Basis-Pfad `https://<cc>/dna/intent/api/v1/...`, z. B. `GET /dna/intent/api/v1/network-device`.
- Token: `POST /dna/system/api/v1/auth/token` mit HTTP Basic Auth → JSON `{"Token": "..."}`; danach Header `X-Auth-Token`. Token ist 60 Minuten gültig.
- Lang laufende Aufgaben (z. B. Discovery, Template-Deploy) antworten asynchron mit `taskId` (HTTP 202); Status über `GET /dna/intent/api/v1/task/{taskId}` abfragen.

## Inventory (S. 340)

Workflow: Credential Sets definieren → Geräte entdecken/manuell hinzufügen → Netzwerkhierarchie definieren → Geräte Sites zuweisen.

- Credentials je Gerätetyp: Netzwerkgeräte CLI + SNMP (NETCONF für Catalyst 9800 WLC); Compute (NFVIS) CLI, SNMP, HTTP(S). Mehrere Credential-Sets möglich; Discovery probiert alle Sets durch, bis eines passt.
- Hierarchie kann aus Cisco Prime Infrastructure importiert werden.
- Site-Zuweisung bringt AAA, Domain/DNS, DHCP, NTP etc. auf das Gerät.

### Discovery
- Methoden: **CDP** (Seed-IP), **LLDP** (Seed-IP), **IP Address Range** (bis 4096 Geräte, Ausschlussbereiche möglich – z. B. CPE von Fremden, schützt Credentials).
- CDP/LLDP-Level = Hop-Anzahl ab Seed, Default **16**; bei großen Netzen kleiner setzen.
- Catalyst Center muss Geräte erreichen können.
- Bevorzugte Management-IP mit „Loopback verwenden“:
  1. genau ein Loopback → dessen IP
  2. mehrere Loopbacks → höchste Loopback-IP
  3. kein Loopback → Ethernet-Interface mit höchster IP (Subinterfaces ignoriert)
  4. kein Ethernet → Serial-Interface mit höchster IP
  Später im Inventory änderbar.

### Inventory-Ansicht
- Device Name (Details, Config ähnlich `show running-config`, Interfaces, Stack; **Command Runner** für show-Befehle; **View 360** → Device 360).
- Reachability: Reachable, Connecting, Authentication Failed, Unreachable (oft fehlende/falsche Credentials → neue Discovery mit korrekten Credentials).
- Last Sync Status: Managed, Partial Collection Failure (Info-Icon), Unreachable, Wrong Credentials (Credentials nach dem Hinzufügen geändert), In Progress.
- Site: ggf. „Unassigned“ → manuell zuweisen.
- Hinzufügen: Provision > Network Devices > Inventory > Add Device (+), oder CSV-Bulk-Import.
- Actions: Edit (Mgmt-IP, Credentials, Settings), Resync (sofort, max. **40** Geräte gleichzeitig), Reboot, Delete (nur wenn nicht einer Site zugewiesen; Admin-Rechte).
- Polling: Kurs: Default alle **25 Minuten**, Maximum **24 Stunden**; laut User Guide 2.3.7 ist der Default inzwischen **24 Stunden** (API 2.3.7: 25–1440 min einstellbar); ~500 Geräte ≈ 20 Minuten; nur in den letzten 24 h aktive Geräte angezeigt.
- Topology-Ansicht (Expand/Collapse All, Link anklicken → Interface/IP-Details, Filter). Device Tags: Gerät kann mehrere Tags haben, Tag mehrere Geräte.

### Device Controllability (Default: aktiviert)
Konfiguriert beim Discovery/zur Laufzeit, falls nicht vorhanden:
- SNMP-Credentials und SNMP-Trap-Receiver
- NETCONF-Credentials
- IP Device Tracking (IPDT)
- Certificate Trustpoint (Controller-Zertifikat)
- Cisco TrustSec Credentials
- Wireless Network Assurance
Deaktiviert → nichts davon wird konfiguriert. Telemetrie (Syslog-Server, NetFlow-Collector) gehört zur Telemetry-Konfiguration. Produkttelemetrie (Nutzungsdaten an Cisco) ist per Default an, abschaltbar.

Verhalten bei Site-Wechsel (S. 345):
| Situation | Aktion |
|---|---|
| Discovery | SNMP- und NETCONF-Credentials setzen, falls nicht vorhanden |
| Erste erfolgreiche Inventory-Collection | IPDT und Controller-Zertifikat |
| Gerät in Global (Default nach Add) | SNMP-/Syslog-/NetFlow-Settings NICHT geändert |
| Global → Site | Settings der neuen Site werden gesetzt |
| Site A → Site B | Settings von Site B ersetzen die alten |
| Aus Site entfernt | Settings bleiben auf dem Gerät |
| Aus Catalyst Center gelöscht | bleiben per Default; optional entfernen |
| Controllability war aus, wird eingeschaltet | bereits zugewiesene Settings werden NICHT nachträglich gepusht |

## Konfigurationsmanagement (S. 341)

- Catalyst Center synchronisiert Konfigurationen regelmäßig, speichert sie (Config-Archiv) → bei **RMA** auf Ersatzgerät übertragbar.
- Templates via GUI oder API anwendbar. Templates dürfen globale Settings (AAA, DHCP) oder SD-Access-Konfiguration NICHT überschreiben – sie ergänzen nur, was Catalyst Center nicht selbst konfiguriert.
- **Model Config Editor** (Tools > Model Config Editor): modellbasierte, GUI-gesteuerte Anpassungen von Cisco Validated Designs, plattformunabhängig; Workflow: Design erstellen → Network Profile → per Provision ausrollen. Wireless-Typen: AAA RADIUS Attributes, Advanced SSID, CleanAir, Event Driven RRM, Flex, Dot11ax, Global IPv6, Multicast, RRM FRA, RRM General.

### Compliance
- Erkennt Intent-Abweichungen und Out-of-Band-Änderungen.
- Automatisch (reagiert auf Traps/Notifications aus Inventory, SWIM …), manuell, geplant (täglich **23:00 Uhr** für Geräte ohne Prüfung in den letzten **7 Tagen**).
- Typen: Startup vs. Running Config, Software Image, Critical Security (PSIRT), Network Profile, Fabric (SDA), Application Visibility, Model Config, CLI Template, EoX, Network Settings, Umbrella.

### Template-Typen
| | Day-0 | Day-N |
|---|---|---|
| Wann | nur beim ersten Kontakt via PnP (Onboarding) | laufende Änderungen / Provisioning |
| Übertragung | als eine Datei, in Running-Config kopiert | zeilenweise gepusht |
| Interaktive Befehle | nein | ja |
| Ablage | Projekt „Onboarding Configuration“ | beliebiges Projekt |
Day-0 kann minimal sein (nur sichere Erreichbarkeit). Day-N: Regular oder Composite.

### Template-Erstellung (5 Schritte)
1. **Projekt** anlegen (Ordner; nur Name Pflicht; Templates nur innerhalb eines Projekts).
2. **Template** anlegen: Regular oder Composite; Device Type + Software Type Pflicht, optional Version/Tags → Kompatibilität.
3. **Inhalt** im Code-Editor (Syntax-Highlighting): Befehle laufen immer im Global Configuration Mode (kein `enable`/`conf t` nötig).
4. **Variablen** im Form Editor: Required (Default an), Not a Variable (an das Gerät durchreichen), Field Name, Tooltip, Default Value, Instructional Text, Data Type (String, Integer, IP Address, MAC Address), Display Type (Text Field, Single Select, Multi Select), Max Characters (nur String).
5. **Save und Commit** – nur committete Templates sind anwendbar und in Composite nutzbar; jede Änderung → neue Versionsnummer, optional Commit Note.

Spezielle Syntax:
```
#MODE_ENABLE
show running-config
#MODE_END_ENABLE

#INTERACTIVE
crypto key generate rsa general-keys<IQ>yes/no<R>no
#ENDS_INTERACTIVE

#MODE_ENABLE
#INTERACTIVE
commands<IQ>interactive question<R>response
#ENDS_INTERACTIVE
#MODE_END_ENABLE

<MLTCMD>banner motd ^
Zeile 2
^</MLTCMD>
```
- `<IQ>` = erwartete Interactive Question (Text vom Gerät), `<R>` = Antwort.
- Interaktive Befehle nur in Day-N-Templates.
- Ohne `<MLTCMD>` wird zeilenweise gesendet.
- Blocklisted Commands: Befehle, die Catalyst-Center-Anwendungen selbst verwalten → Warnung im Template.

*(Ergänzung)* Velocity-Syntax:
```
hostname $hostname
#set( $mgmtVlan = 99 )
#if( $role == "access" )
 spanning-tree portfast default
#end
#foreach( $port in [1..24] )
interface GigabitEthernet1/0/$port
 switchport access vlan $dataVlan
#end
```
Jinja2-Pendant: `hostname {{ hostname }}`, `{% for p in ports %} … {% endfor %}`, `{% if … %} … {% endif %}`.

## Onboarding mit PnP und LAN Automation (S. 342)

- PnP-Agent startet, wenn **keine Startup-Config** vorhanden ist; findet Server, lädt Image und Konfiguration.
- Komponenten: PnP Agent, PnP Server (Catalyst Center), PnP Protocol (HTTP, HTTPS, XMPP; HTTPS/XML-basiertes offenes Schema), **PnP Connect** (optional; Cloud-Redirect), **PnP Helper/Installer App** (optional; Bootstrap laden, Troubleshooting).
- Eigenschaften: simple (Zero-Touch, GUI, mehrere Discovery-Wege), secure (**SUDI**-basierte Geräteauthentifizierung, CA-basierte Serverauthentifizierung, HTTPS für Image/Config, Admin wählt Gerät beim Claim), consistent (Router, Switches, APs).

### Server-Discovery-Reihenfolge
1. **DHCP Option 60/43**: Gerät sendet Option 60 mit „ciscopnp“; DHCP-Server antwortet mit **Option 43** (Controller-IP). 
2. **DNS**: Domain aus DHCP, Lookup `pnpserver.<domain>`.
3. **Cloud Redirect / PnP Connect**: `devicehelper.cisco.com`; erst Trust-Pool-Bundle laden.
4. *(manuell)* USB-Bootstrap (`router-confg`/`router.cfg`/`ciscortr.cfg`) – nicht für APs.
5. *(manuell)* Cisco Installer App (iPhone/iPad/Android).

*(Ergänzung)* Option 43 ASCII-Format für IOS-XE-PnP:
```
ip dhcp pool PNP
 network 10.10.10.0 255.255.255.0
 default-router 10.10.10.1
 domain-name example.local
 dns-server 10.1.1.53
 option 43 ascii "5A1N;B2;K4;I10.1.1.100;J80"
```
`5A1N` = PnP-Typ/Version, `B2` = IPv4, `K4` = HTTP (`K5` = HTTPS), `I` = Server-IP, `J` = Port. Bei APs (CAPWAP) wird Option 43 anders (TLV f1) für die WLC-Discovery genutzt.
DNS-Variante: A-Record `pnpserver.example.local` → Catalyst-Center-IP.
*(Ergänzung)* PnP auf einem Gerät stoppen: `pnpa service discovery stop`.

### PnP Connect (Cloud, Day-0)
1. Controller-Profil in PnP Connect (Smart Account) anlegen.
2. Bestellung über Cisco Commerce Workspace mit Smart Account + **NETWORK-PNP-LIC** → automatische Registrierung.
3. Seriennummer + PID im Smart Account.
4. Catalyst Center als Controller im Smart Account registrieren.
5. Catalyst Center synchronisiert Geräte (Quelle „Smart Account“).
6. Claim + Site-Zuordnung.
7. Gerät bootet, fragt PnP Connect, wird zu Catalyst Center umgeleitet, identifiziert sich per Seriennummer, wird provisioniert.

### PnP-Workflow in Catalyst Center
1. Day-0-Template (im Projekt **Onboarding Configuration**; ohne Credentials/Site-Settings, die kommen automatisch)
2. Network Profile (Design > Network Profiles > Add Profile; Gerätetyp, Onboarding Template)
3. Day-0-Template(s) dem Profil zuweisen (mehrere möglich: generisch + gerätespezifisch; Day-N-Tab wird erst beim Provisioning angewendet)
4. Sites dem Profil zuweisen
5. PnP-Gerät hinzufügen (optional: einzeln oder Bulk-CSV mit Serial, PID, Name; „pre-provisioned“ vs. „unclaimed“)
6. Gerät claimen (Site, Variablen, Intent)

Gerätezustände: **Unclaimed** → (Claim) **Planned** (noch keine Kommunikation) → (Gerät bootet, kontaktiert Server) Onboarding → **Provisioned** (im Inventory).

### LAN Automation (SD-Access-Underlay)
- Phasen: Plan → Design (Sites, Services, Credentials, globaler IP-Pool, LAN-Automation-Pool) → Discover (Seed-Geräte) → Provision (Start/Stop).
- Start: temporäre Konfiguration auf Seed; Seed wird **DHCP-Server in VLAN 1 mit Option 43** → neue Geräte bekommen IP und PnP-Profil, werden entdeckt, Image-Upgrade, Grundkonfiguration.
- Stop: permanente Konfiguration, alle Punkt-zu-Punkt-Links → **Layer 3** (Reihenfolge Tier 3 Access → Tier 2 Distribution → Tier 1 Core), temporäre Konfig aufräumen; kurzzeitige Unterbrechung und STP-Topologieänderung möglich. *(Ergänzung: Underlay-Routing per IS-IS.)*
- Reichweite: Kurs: **zwei Hops** ab Seed; tatsächlich einstellbarer Discovery Level (je nach Release bis 3 bzw. 5) (2- und 3-Tier-Campus); größere Netze in mehreren Läufen mit wechselndem Seed. Gerät 3 Hops unter dem Primary wird nicht verlinkt.
- Nur Links zwischen Geräten der aktuellen Session werden L3; zu früh gestoppt → In-Progress-Geräte löschen, neue Session, Gerät auf Werkseinstellung, reload.
- Vorteile: Zero-Touch, End-to-End-Topologie, Resilienz, Security, Compliance.

## SWIM (S. 343)

- Lebenszyklus (über klassisches NMS hinaus, das nur Distribute/Activate kann): Golden Image identifizieren → Geräte wählen → Change Request erstellen → genehmigen → **Precheck** → **Distribute** → **Activate** → **Post-Deploy Validation** → CR schließen.
- Image Repository: zentrale Ablage, Images je Gerätefamilie, Anzahl Geräte pro Image, Download von Cisco oder lokaler Upload.
- Golden Image = Tag „optimal für Gerätefamilie/-typ/Rolle/Site“ → Image-Compliance; Abweichung → Status „Needs Update“ (Outdated).
- Image-Status: **Suggested** (von Cisco empfohlen), **Latest** (neuestes Release), „Suggested, Latest“.
- Image Distribution Server: bis zu **3** externe (SFTP …) unter System > Settings > Device Settings > Image Distribution Servers (Host, Root Location, User, Passwort, Port); pro Site zuweisbar unter Design > Network Settings.
- **SMU**: Fix für ein Base Image, ggf. ohne Reboot; Teil der Compliance (Golden SMU). Golden SMU setzt Golden Base Image voraus; Kurs: nur ein Golden SMU je Base Image; hat das Gerät schon das Base Image, wird nur das SMU installiert.
- Online mit cisco.com (Credentials in System Settings) → Images werden Gerätefamilien automatisch zugeordnet; offline → manuell zuordnen.
- Verifikation: Checksumme vs. **KGV-Datei**; Status „verified“. KGV initial vom Admin, danach automatisch alle **7 Tage**.
- ROMMON: immer neueste Version (nicht wählbar), braucht cisco.com, nur zusammen mit Base Image, **zwei Reboots** (ROMMON, dann Image – Kursangabe, nicht web-belegt; User Guide 2.3.7: cisco.com-Konfiguration Pflicht, ROMMON-Datei wird automatisch geladen). Neuere Plattformen (ISR 4400) haben ROMMON im Image.
- Upgrade: Inventory > Actions > Update OS Image; „Now“ oder „Later“ (Zeitplan); Checkbox für ROMMON.
- Status-Schritte: ROMMON-Distribution, Flash-Precheck, Base-Image-Distribution, ROMMON-Activation, Base-Image-Activation, Pre-/Post-Checks (z. B. Spanning Tree Summary, CDP Neighbors, Interface, Config Register, Startup Config).

## Assurance – Features und Use Cases (S. 344)

Herausforderungen → Lösung: reaktiv → proaktiv/prädiktiv; viele Daten → Actionable Insights; schwer isolierbar → schnelle Isolation; viele Klicks → Root Cause + Guided Remediation; starre Tools → skalierbar, resilient, sicher, erweiterbar.

### Architektur
- **Data Collection and Ingestion** (Streaming, Echtzeit): Netzwerktelemetrie (SNMP, NetFlow, Syslog, Streaming Telemetry; Quellen FW, LB, WLC, Sensor) + Kontextdaten (LDAP, AAA, Topologie, Location, DNS, DHCP, Inventory, Policy, ITSM).
- **Data Correlation and Analysis**.
- **Data Visualization and Action**: Datenbanken + APIs; offen: Collector/Analytics Pipeline SDKs, Time-Series-Analyse, Graph-Datenmodelle + REST-APIs, System Management Portal.
- Intern (Kursbild): NCP (Network Controller Platform, Automation) und NDP (Network Data Platform, Analytics-Engine); Cloud: Kairos (Cloud-AI/ML-Engine).

### Health Insights
- Dashboards: **Overall Health, Device (Network) Health, Client Health, Application Health**.
- 360-Sichten: **Device 360, Client 360, Application 360** mit Drill-down; Time Travel der KPIs (Stunden, 24 h, 7 Tage).
- *(Ergänzung)* Health Score 1–10: Poor 1–3 (rot), Fair 4–7 (orange), Good 8–10 (grün); Geräte-Score = niedrigster KPI-Subscore (CPU, Memory, Link-Errors …).

### Issues
- Priorität **P1–P4** (P1 am schwersten), vordefiniert, anpassbar.
- Quellen: **Syslog-basiert**, **Threshold-basiert** (Telemetrie-Schwellen), **AI-driven** (AI Network Analytics, meist Cloud nötig).
- Dashboards Open, Resolved, Ignored; Time Travel bis **14 Tage**.
- Guided Remediation: Wie viele Geräte betroffen, wie oft, wann zuletzt; Zeitlinie der KPIs; MRE ermittelt Root Cause mit Knowledge Base (Kurs: 35 Jahre Cisco-Expertise) und schlägt Schritte/Korrekturaktionen vor.

### AI Network Analytics
- Cloud-Datenplattform (deidentifizierte Daten) für ML-Modelle + Machine-Reasoning-Inference-Engine.
- Intelligent Issue Detection: **AI-Driven Baselining**, **AI-Driven Anomaly Detection**.
- Trends and Insights: Trend Deviations, AP Performance Advisories.
- Comparative Benchmarking: AP-Vergleiche in Heatmaps, Peer Comparisons, Network Comparisons.
- Fokus Wireless (Client Onboarding, Application Experience). On-prem only: nur „excessive onboarding time“ (Kursangabe, nicht web-belegt).

### Troubleshooting-Tools
- **Path Trace**: Pfad von Quelle zu Ziel bis auf Portebene inkl. ACL/QoS → wo und warum Probleme.
- **Intelligent Capture**: Wireless-Pakete erfassen/decodieren (automatisch oder manuell).
- **Time Travel**: vergangenen Zustand ansehen statt Problem reproduzieren.
- Predictive Behavior (Baselining, Cloud).
- **Sensor Tests**: APs als Sensoren testen Onboarding/Performance proaktiv.
- Apple-iOS-/Samsung-Client-Analytics (Client 360).
- Closed-Loop-Vision Self-Healing: aktuell nur Empfehlungen, keine automatische Ausführung.

Use Cases Wireless: Onboarding (Association, Auth, IP, Onboarding Time), Connected Experience (Roaming, Interferenz, Throughput), Coverage/Capacity, AP-/WLC-Monitoring (CPU, Memory, AP Flapping), Applications (Throughput, QoS); Spectrum Analysis.

## Assurance-Implementierungsworkflow (S. 345)

1. Appliance installieren + Updates
2. Device Credentials (auf Geräten konfigurieren UND in Catalyst Center definieren)
3. + 4. (beliebige Reihenfolge) Geräte hinzufügen (Discover, Add, PnP, Import) und Site-Hierarchie designen
5. Prüfen: Geräte im Inventory, Collection läuft (Last Sync Status **Managed**)
6. Geräte Sites zuweisen (pusht Settings/Credentials, wenn Device Controllability an)
7. (optional) Integrationen ISE, CMX, IPAM
8. Telemetrie-Profile konfigurieren/ausrollen
9. (empfohlen) AI Network Analytics aktivieren
10. (empfohlen) MRE Knowledge Base aktualisieren
→ Gerät bereit für Assurance (Day 2).

### Plattform-Optionen (DN3, 3. Generation)
| SKU | Basis | Gesamtgeräte | Netzwerkgeräte | APs | Sensoren | Endpunkte |
|---|---|---|---|---|---|---|
| DN-SW-APL (Virtual) | VM | 5000 | 2000 | 4000 | 600 | 25.000 |
| DN3-HW-APL | UCS C220 M6, 32 Cores | 5000 | 2000 | 4000 | 600 | 25.000 |
| DN3-HW-APL-L | UCS C220 M6, 56 Cores | 8000 | 4000 | 6000 | 800 | 40.000 |
| DN3-HW-APL-XL | UCS C480 M6, 80 Cores | 18.000 | 8000 | 13.000 | 1600 | 100.000 |

### Credentials für Discovery
- Mindestens **eine CLI- und eine SNMP-Credential**.
- CLI: SSHv2 und Telnet (Reihenfolge festlegbar); Account mit **Privilege 15** oder Enable-Passwort.
- SNMP: v2c oder v3; **Read-Zugriff** genügt für Discovery.
- HTTP/HTTPS: Compute-Geräte (NFVIS) / Geräte ohne CLI.
- NETCONF: WLCs (Catalyst 9800), Port definieren *(Ergänzung: Default 830)*.
- Assurance funktioniert laut Kurs **nicht über NAT** (nicht web-belegt); Latenz bevorzugt ≤ **100 ms**, maximal **200 ms**.
- WLC über Management-IP entdecken, nicht Service-Port.

*(Ergänzung)* Minimal-Vorbereitung eines IOS-XE-Geräts:
```
hostname ACC-SW1
ip domain name example.local
crypto key generate rsa modulus 2048
ip ssh version 2
username dnac privilege 15 secret <pw>
line vty 0 15
 transport input ssh
 login local
snmp-server community RO-CC RO
netconf-yang
```

### Hinzufügen-Methoden
Discovery (CDP/LLDP/IP-Range), manuell (Hostname/IP + SNMP + CLI), CSV-Import, PnP, Export aus Prime Infrastructure (CSV).

### Site-Hierarchie
- Import aus Prime Infrastructure ≥ 3.1 (CSV), Ekahau-Projekt, CMX-Sync.
- Properties pro Ebene: AAA, DHCP, DNS, Syslog, SNMP-Trap, NTP, Zeitzone, MOTD; Credentials (CLI/SSH + Enable, SNMPv2/v3, HTTP(S)); Golden Images pro Site; Vererbung Global → Site → Building → Floor.
- APs: Floor Maps hinzufügen, APs positionieren.

### Telemetrie
Design > Network Settings > Telemetry: SNMP Traps, Syslogs, NetFlow, Wired Endpoint Data Collection (IPDT), Wireless Controller/AP/Client Health.

### AI Network Analytics aktivieren
- System Settings; anonymisierte Event-Daten von WLCs + Hierarchie an Kairos (AWS).
- Regionen: US East (`api.use1.prd.kairos.ciscolabs.com`), Europe Central (`api.euc1.prd.kairos.ciscolabs.com`).
- Nur **ausgehend TCP 443**, TLS 1.2, gegenseitige Zertifikatsauthentisierung; Enrollment mit Customer ID + One-Time Onboarding Key; Proxy möglich (von Catalyst Center geerbt); DNS-Auflösung nötig.
- Lizenz: **Cisco Catalyst Advantage**.
- Betroffene Features: AI-Driven Issues, Network Trends, Network Heatmap, Site Comparison, Peer Comparison.

### MRE Knowledge Base
- Knowledge Packs = Schritt-für-Schritt-Workflows (Root Cause, Security Issues), cloud-gehostet, von Cisco-Experten gepflegt; automatisch täglich oder manuell aktualisieren.

## Fehler/Ungenauigkeiten im Kurs

1. **MRE-Erfahrung**: S. 338 „30 Jahre“, S. 344 „35 Jahre“ Cisco-Erfahrung – widersprüchlich; keine Prüfungsrelevanz, Fragen vermeiden die Zahl.
2. **Appliance-Größen (S. 345)**: Fließtext sagt „entry-level scales to 5000 devices“, die Tabelle zeigt 5000 *kombinierte* Geräte, davon max. 2000 Netzwerkgeräte. Korrekt: 5000 gesamt (wired+wireless), 2000 Netzwerk-Infrastrukturgeräte (Cisco Catalyst Center Data Sheet DN3).
3. **„Catalyst 9800 Switches“ (S. 345)**: Catalyst 9800 ist die Wireless-LAN-Controller-Familie, keine Switch-Familie. Korrekt: NETCONF für Catalyst 9800 WLCs (bzw. Catalyst 9000 Switches mit Embedded Wireless Controller).
4. **LAN-Automation-Linkliste (S. 342)**: „Discovered device 1 to Peer device“ steht doppelt; laut Bild ist der dritte Link Discovered Device 1 ↔ Discovered Device 2.
5. **Templates nur Velocity (S. 336/341)**: veraltet – Catalyst Center unterstützt seit Release 2.1.x zusätzlich **Jinja2** (Catalyst Center User Guide, „Create Templates to Automate Device Configuration Changes“).
6. **„Cisco DNA Center“** taucht noch an vielen Stellen auf (S. 334, 336, 339, 340, 343, 344, 345) – aktueller Name Cisco Catalyst Center.
7. **Reachability „Authentication Failed“ (S. 340)**: Kurs beschreibt es als „verbunden, kann Gerätetyp nicht bestimmen“; gemeint ist, dass die Anmeldung (Credentials) fehlschlug – Fragen dazu vermieden.
8. **Bild PnP-Workflow (S. 341)**: Beschriftung „Provisioning (day-0) Push“ – Push-Provisioning betrifft Day-N; Day-0 wird vom Gerät per PnP gezogen (Pull).
9. Tippfehler „Catatyst“, „efficency“ ohne inhaltliche Relevanz.

## Bilder

Ordner `encor-1.4.10/bilder/30-catalyst-center/`:
- `01-funktionen.svg` – Funktionsbereiche Design/Policy/Provision/Assurance/Platform mit Beispielen und den Personas NetOps/SecOps/AIOps/DevOps.
- `02-ibn-bloecke.svg` – IBN-Kreislauf Translation → Activation → Assurance mit Closed Loop und Vergleich „Human Middleware“ vs. Controller.
- `03-hierarchie.svg` – Netzwerkhierarchie Global → Area → Building → Floor mit Vererbung/Override von Network Settings.
- `04-api-360.svg` – 360-Grad-Erweiterbarkeit: Northbound Intent API, Westbound Adapter, Eastbound Events, Southbound Geräteprotokolle/SDK.
- `05-inventory.svg` – Inventory-Workflow, Discovery-Methoden und Regel zur Wahl der Management-IP.
- `06-pnp-discov.svg` – PnP-Discovery-Kette DHCP 43 → DNS pnpserver → Cloud Redirect und Gerätezustände Unclaimed/Planned/Provisioned.
- `07-templates.svg` – Day-0 vs. Day-N Templates, Template-Workflow Projekt → Template → Inhalt → Variablen → Commit.
- `08-swim.svg` – SWIM-Lebenszyklus vom Golden Image über Prechecks, Distribution, Activation bis Post-Checks.
- `09-assurance.svg` – Assurance-Architektur: Datenquellen → Korrelation/Analyse → Health, Issues P1–P4, 360-Sichten, Cloud-AI.
- `10-lan-auto.svg` – LAN Automation: Seed als DHCP-Server mit Option 43 in VLAN 1, Zwei-Hop-Grenze, L2→L3-Umwandlung.
