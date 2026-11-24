# Introducing APIs in Cisco Catalyst Center and Cisco Catalyst SD-WAN Manager

Quelle: ENCOR 1.4.10 Student Guide, Seiten 374–379 (380 Summary Challenge und 381 Answer Key nicht gelesen)
Topics: ENCOR-6.4 (APIs für Catalyst Center und SD-WAN Manager), ENCOR-6.5 (REST-Statuscodes und Payload interpretieren), ENCOR-5.3 (REST-API-Sicherheit)

Der Abschnitt ist im Kurs als Selbststudium markiert. Er ergänzt Kapitel 26 (REST/RESTCONF/HTTP-Grundlagen), 30 (Catalyst Center) und 32 (SD-WAN). Diese Datei vertieft vor allem: SDN-API-Richtungen, OpenFlow/NETCONF/OpFlex, Statuscodes inkl. 206/415/501/503/504, API-Sicherheit (TLS + Basic Auth, Rechte), Intent-API-Domänen, Python-Workflow Token → Request → taskId, SD-WAN-Login und Collections, Bulk-APIs.

## 1. Application Programming Interfaces und SDN-Architektur (S. 375)

- API = Code/Schnittstelle, über die zwei Softwareprogramme miteinander kommunizieren.
- Traditionelles Netz: jedes Gerät hat eigene Control Plane + Data Plane. SDN: Control Plane zentral im Controller, Geräte behalten die Data Plane.
- SDN-Schichten (Kurs: drei):
  - **Data (Forwarding) Plane**: Netzelemente, die Kundenverkehr verarbeiten (physisch oder virtuell).
  - **Control Plane**: Kern der SDN-Architektur, enthält die SDN-Controller, steuert die Geräte zentral.
  - **Application Plane**: SDN-Anwendungen, die dem Controller ihre Anforderungen mitteilen.
  - (Eine „Management Plane“ gehört in dieser Kurs-Einteilung NICHT zu den drei Schichten.)
- **Southbound API / Interface** = Controller ↔ Netzgeräte (Data Plane).
- **Northbound API / Interface** = Controller ↔ Anwendungen (Application Plane). Anwendungen „bestellen“ beim Netz, was sie brauchen (Netzvirtualisierung, dynamisches Provisioning, Firewall-Monitoring, Identity-/Access-Policies), statt dass man das Netz manuell nachjustiert.
- Für Northbound gibt es **keinen einheitlichen Standard**: Jeder Controller hat eigene APIs, die nur mit bestimmten Anwendungen funktionieren.

### Southbound-Protokolle
| Protokoll | Herkunft | Funktion |
|---|---|---|
| OpenFlow | ONF (Open Networking Foundation), Industriestandard | schreibt **Flow-Tabellen** der Switches → bestimmt Pfad der Flows; imperatives Modell |
| NETCONF | IETF-Standard | Konfiguration installieren, ändern, löschen per **RPC**, **XML**-kodiert, transaktional; Geräte kündigen ihre **Capabilities** an; nicht jedes Gerät unterstützt es |
| OpFlex | offener Standard (Cisco-initiiert) | **deklaratives** Policy-Modell; Controller (Cisco **APIC**) sendet abstrakte Policy, Gerät setzt sie mit eigener Control Plane um |

- **Imperativ (OpenFlow)**: Controller schickt detaillierte, komplexe Anweisungen („wie“) an die Geräte.
- **Deklarativ (OpFlex)**: Controller schickt das gewünschte Ergebnis („was“), vertraut den Geräten bei der Umsetzung.
- Merksatz: NETCONF = **Konfiguration** eines Geräts ändern; OpenFlow = **Forwarding-Tabelle** direkt ändern (sinnvoll, wenn eine Funktion mit der Gerätesoftware nicht konfigurierbar ist).
- Catalyst Center nutzt southbound u. a. SSH/CLI, SNMP, NETCONF, HTTPS (aus Kap. 30); SD-WAN Manager verwaltet Edges per NETCONF (Kap. 32).

## 2. REST API Response Codes and Results (S. 376)

- REST basiert auf dem HTTP-Request/Response-Modell über HTTP oder HTTPS. Request = URL (Ort der Ressource) + Methode (Aktion) + ggf. Header und Body. Response enthält in der **Status-Line** den Statuscode.
- Catalyst Center Intent API nutzt laut Kurs nur **GET, POST, PUT, DELETE**:
  - GET: Daten lesen
  - POST: neue Daten anlegen
  - PUT: bestehende Daten ersetzen/aktualisieren (Kurs: „nicht zum Anlegen“ – siehe Fehlerliste: allgemein kann PUT laut HTTP-RFC auch anlegen)
  - DELETE: Daten entfernen
- SD-WAN Manager API akzeptiert zusätzlich **PATCH** (Kurs: „PUT, DELETE, and PATCH“ neben GET/POST).

### Statuscodes
| Code | Bedeutung |
|---|---|
| 200 OK | Erfolg, Ergebnis im Body |
| 201 Created | POST/PUT hat eine neue Ressource erzeugt, Infos im Body |
| 202 Accepted | angenommen, Verarbeitung noch nicht abgeschlossen (Catalyst Center muss mit Geräten interagieren → asynchron, taskId) |
| 204 No Content | Erfolg, kein Body |
| 206 Partial Content | GET mit **Range**-Header, Server liefert nur den angeforderten Teil |
| 400 Bad Request | Server versteht Request nicht (Syntax) |
| 401 Unauthorized | Credentials fehlen oder ungültig (Token abgelaufen, falsches Passwort) |
| 403 Forbidden | Credentials erkannt, aber keine Berechtigung |
| 404 Not Found | Ressource existiert nicht |
| 409 Conflict | Ressource in Konfliktzustand (z. B. gleichzeitige Bearbeitung); späterer Retry kann klappen |
| 415 Unsupported Media Type | Body-Format nicht unterstützt (z. B. XML an JSON-only-Server; falscher Content-Type) |
| 500 Internal Server Error | Server konnte nicht erfüllen |
| 501 Not Implemented | Funktion nicht implementiert |
| 503 Service Unavailable | Server (vorübergehend) nicht verfügbar |
| 504 Gateway Timeout | Zeitlimit überschritten, keine rechtzeitige Antwort |

- Klassen: 2xx Erfolg, 4xx Fehler durch den Client-Request, 5xx Fehler auf der Serverseite. (Eigenes Wissen: 1xx informativ, 3xx Umleitung; 429 Too Many Requests = Rate-Limit, oft mit Retry-After-Header.)
- Catalyst Center verwendet nur eine Handvoll Codes; welche ein Pfad liefert, steht in der Intent API Reference.
- Fehlersuche (eigenes Wissen): 4xx → eigenen Request korrigieren (URL, Header, Body, Rechte, Token), nicht blind wiederholen (Ausnahmen: 409/429 später erneut). 5xx → Server/Dienst prüfen, Retry mit Backoff sinnvoll bei 503/504.
- Python requests (eigenes Wissen): `response.status_code`, `response.ok` (True bei Code < 400), `response.raise_for_status()` (wirft HTTPError bei 4xx/5xx), `response.json()` (Body → dict/list), `response.text` (Body als String), `json=payload` setzt Body und Content-Type automatisch, `data=json.dumps(payload)` braucht Content-Type manuell.

## 3. REST API Security (S. 377)

Zwei Aspekte: (1) Kanal vor Mitlesen schützen, (2) prüfen, dass Daten von vertrauenswürdiger Quelle kommen.
- Beispiel: Catalyst Center schiebt per REST-API TrustSec-Konfiguration an **Cisco ISE**. ISE ist der **HTTPS-Server**.
- **HTTPS (SSL/TLS)** verschlüsselt → mitgeschnittene Daten nicht einfach lesbar.
- Server (ISE) legt ein **X.509v3-Identitätszertifikat** vor; Client (Catalyst Center) prüft die Signatur, bevor der Tunnel steht. Dafür: Root-CA-Zertifikat der signierenden CA installieren, oder bei Self-Signed das Identitätszertifikat selbst installieren. → Catalyst Center weiß, dass es an das richtige Gerät pusht.
- Umgekehrt muss ISE den Client prüfen: **HTTP Basic Authentication**, Header in **jedem** Request, Authentifizierung pro Request. Dafür in ISE einen Admin-User mit Rechten auf die REST-API anlegen.
- Rechte begrenzen: Auf der **Cisco ASA** steuern User Privilege Levels die REST-API: Level ≥3 Monitoring-APIs, Level 5 GET-APIs, Level 15 PUT/POST/DELETE.
- Eigenes Wissen: Basic Auth = `Authorization: Basic base64(user:password)` – nur Kodierung, deshalb nur über TLS. `verify=False` in requests schaltet die Zertifikatsprüfung ab (Man-in-the-Middle-Risiko; nur Lab). Weitere Verfahren: Token (Catalyst Center X-Auth-Token), Session-Cookie (SD-WAN Manager JSESSIONID + X-XSRF-TOKEN), API-Key/Bearer (z. B. Meraki Dashboard), OAuth 2.0 (kurzlebige Access-Tokens). Credentials nicht im Skript hart codieren (Umgebungsvariablen/Vault).

## 4. Cisco Catalyst Center APIs (S. 378)

### Plattform
- Catalyst Center = Suite aus Anwendungen und Workflows + Plattform mit Integrationen, APIs, SDKs. Ziel: Partner-Innovation, Integration in Ökosysteme.
- Bausteine: **Intent APIs** (northbound REST), **Integration Flows / Integration API** (ITSM, IPAM, Reporting), **Events and Notification Services** (Webhooks), **Multivendor SDK** (Fremdgeräte).
- Doku: **Platform > Developer Toolkit** (Dokumentation je Call, gruppiert nach Funktionsbereichen; Methode, URL, Query-Parameter, Header, Responses, Schema, Preview/Test). Link „Swagger docs“ öffnet die Swagger-Oberfläche.
- Früher musste die Platform-App nach dem Deployment installiert und REST-APIs/Bundles aktiviert werden; in aktuellen Releases ist die Plattform standardmäßig installiert und REST-APIs/Bundles sind aktiviert.
- Intent API = policy-basierte Abstraktion des Business-Intents: man beschreibt das Ergebnis, nicht die Mechanik.

### Intent-API-Domänen
| Domäne | Inhalt |
|---|---|
| Authentication | Token holen; alle Plattform-REST-Methoden brauchen Authentifizierung; Token identifiziert die Rechte, jede Operation wird gegen die Token-Rechte autorisiert |
| Know your network | Sites (hierarchisch: Sites/Buildings), Topology (Health, physisch, L2, L3, VLAN), Devices (Network Device Detail: nach Zeitstempel, MAC, UUID, Name; Interfaces, Config, Zertifikatsstatus, Module, VLANs; add/delete/update/sync), Clients (Client Health wired/wireless, Client Detail), Users (per User-ID oder MAC), Issues (Details + Mitigation per Issue-ID oder MAC) |
| Site management | Site Design (NFV-Provisioning an Site/Area/Building/Floor), Network Settings (Credentials, globale IP-Pools, SP-Profile), SWIM (Images importieren, verteilen, aktivieren), Device Onboarding (PnP: Projekte, Workflows, Virtual Accounts, Zero-Touch), Configuration Templates (Template Programmer/Editor, Projekte, Versionierung) |
| Connectivity | Fabric wired (SDA: Edge, Border, Auth-Profile), Nonfabric Wireless (SSIDs, Wireless-/RF-Profile, APs) |
| Operational tasks | Command Runner (read-only CLI-Befehle, Keywords), Network Discovery (Discoveries + Credentials, gefundene Geräte), Path Trace (Flow-Analyse zwischen zwei Endpunkten, Statistik pro Hop), File (Dateien wie Images/Zertifikate holen), Task (Status asynchroner Aufträge), Tags |
| Policy (Application Policy) | Business-Intent in geräte-spezifische Konfiguration übersetzen; Applikationen und Application Sets verwalten |
| Event Management | Event-Subscriptions (CRUD); Benachrichtigungen bei Assurance- und Automation-(SWIM-)Events an Drittsysteme |

### Python-Workflow (Kurs-Beispiel, eigene Formulierung)
```python
import requests, json
from requests.auth import HTTPBasicAuth

def get_token(host, user, pw):
    r = requests.post(f"https://{host}/dna/system/api/v1/auth/token",
                      auth=HTTPBasicAuth(user, pw),
                      headers={"Content-Type": "application/json"},
                      verify=False)          # nur Lab
    return r.json()["Token"]                # Key mit großem T

def add_device(host, token, body):
    r = requests.post(f"https://{host}/dna/intent/api/v1/network-device",
                      data=json.dumps(body),
                      headers={"X-Auth-Token": token,
                               "Content-Type": "application/json"},
                      verify=False)
    return r.json()
```
- Body für network-device (Kurs): ipAddress (Liste), type "NETWORK_DEVICE", computeDevice False, snmpVersion, snmpROCommunity, snmpRWCommunity, snmpRetry, snmpTimeout, cliTransport, userName, password, enablePassword.
- Antwort (asynchron): `{"response": {"taskId": "...", "url": "/api/v1/task/<taskId>"}, "version": "1.0"}` → Status über Task API: `GET /dna/intent/api/v1/task/{taskId}` → Felder wie `isError`, `progress`, `failureReason`, `endTime` (eigenes Wissen). 202 heißt nur „angenommen“; erst `isError` zeigt Erfolg/Fehlschlag.
- Eigenes Wissen: Token gilt typischerweise 60 Minuten → danach 401 → neues Token. Listen-Antworten stehen unter `response` (Array), z. B. network-device mit Feldern `hostname`, `managementIpAddress`, `reachabilityStatus`, `softwareVersion`, `platformId`, `serialNumber`, `id` (UUID). `GET /dna/intent/api/v1/network-device/count` → `{"response": 42, ...}`. Große Listen per `offset`/`limit` blättern (offset beginnt bei 1).
- Command Runner (eigenes Wissen): POST `.../network-device-poller/cli/read-request` mit `commands` + `deviceUuids` → taskId → Task-`progress` ist ein JSON-**String** mit `fileId` → `GET .../file/{fileId}` liefert die Ausgabe.

### Weitere APIs und Integrationen
- **Multivendor Support**: Java-SDK zum Erstellen von **Device Packages** für Fremdhersteller. Basis-Sichtbarkeit, Monitoring, Command Runner; Geräte erscheinen korrekt statt als „unknown“; Chassis, OS-Version, Interfaces + Status; physische Topologie über Discovery-Protokolle wie **LLDP**. Device Packages nutzen NETCONF, SNMP, Telnet/SSH u. a.
- **Integration API**: REST-basierte Integration Adapter APIs, **bidirektional**; Netzdaten, Events, Notifications an externe Systeme publizieren und Informationen von dort konsumieren.
  - **ITSM** (z. B. ServiceNow, eigenes Ticketsystem): Incident-, Change-, Event-, Problem-Management, Approval-Chains, Change-/Maintenance-Window-Planung; weniger Übergaben, Deduplizierung von Issues.
  - **IPAM** (Infoblox, BlueCat out of the box): IP-Pools importieren und Nutzung synchronisieren; DDI-Einblicke (DNS, DHCP, IPAM) für Assurance.
  - Reporting-Integrationen (Kurs nennt „DaaS APIs“) für flexible Dashboards in externen Systemen.
- **Events/Webhooks**: Events (z. B. Assurance) lösen Notifications aus, z. B. als ITSM-Incident oder **Webhook** = HTTP-Callback (HTTP **POST**) an eine externe URL bei einem Event. Beispiel: nicht-konforme Geräte → App startet Software-Upgrade. Vorteil gegenüber Polling: Push in Echtzeit, keine ständigen Abfragen.

## 5. Cisco Catalyst SD-WAN REST API (S. 379)

- REST-API über den **SD-WAN Manager**: Echtzeit- und statische Infos über Overlay und Geräte, Upload von Templates und Konfiguration; eigene Portale möglich.
- Begriffe: **Resource** = Objekt mit Typ, Daten, Beziehungen und Methoden; **Collection** = homogene Gruppe von Ressourcen eines Typs, auf oberster API-Ebene.
- Collections:
  - **Monitoring**: Status/Statistik; WAN Edges sammeln alle **10 Minuten**, packen in zip, Manager holt alle 10 Minuten bzw. beim nächsten möglichen Login.
  - **Real-Time Monitoring**: Echtzeitdaten, ca. **einmal pro Sekunde**.
  - **Configuration**: Feature-/Device-Templates erstellen, Konfigurationen aus Templates lesen, Manager-Cluster.
  - **Administration**: User/Gruppen, Audit-Logs, lokaler Manager-Server (Settings, Cluster Management, Tenant Management).
  - **Device Inventory**: Seriennummern, Systemstatus (Connected Devices, Controllers, WAN Edges).
  - **Certificate Management**: Zertifikate und Schlüssel, WAN-Edge-Serial-Number-File (aus Smart Account, Edges valid/invalid markieren, an Controller senden).
  - **Troubleshooting Tools**: Geräte troubleshooten, Policy-Wirkung, Software-Update, Versionsinfos.
- Vorteile: Workflow vereinfachen, Services schnell deployen, App-Erlebnis verbessern. Konkret: Templates in großer Fabric automatisch attach/detach, Fabric-Policy dynamisch ändern, DevOps-Tools, **ChatOps**, CRM-/Ticketing-Integration, Third-Party-Monitoring, Multicloud/Hybrid-Cloud.
- API ist selbstbeschreibend/selbstdokumentierend; Doku auch unter `https://{manager}:{port}/apidocs` (Swagger).

### Authentifizierung und Aufrufe
```text
POST https://{manager}:{port}/j_security_check
Content-Type: application/x-www-form-urlencoded
Body: j_username=<user>&j_password=<pw>
→ 200 OK + Cookie JSESSIONID (begrenzte Lebensdauer)
```
- RBAC: Benutzer in Gruppen (admin, network-operators, custom) mit begrenzten Rechten.
- Eigenes Wissen (nicht im Kurs, aber prüfungsrelevant): Seit Release 19.2 braucht jeder **POST/PUT/DELETE** zusätzlich ein **XSRF/CSRF-Token**: `GET /dataservice/client/token` (mit Session-Cookie) liefert es als reinen Text; danach Header `X-XSRF-TOKEN: <token>`. Bei falschen Credentials liefert `/j_security_check` eine HTML-Loginseite (`<html>` im Body, laut DevNet-Doku vom Client zu prüfen; in der Praxis meist mit Status **200**) → Skripte prüfen auf HTML im Body bzw. auf fehlendes JSESSIONID-Cookie. `requests.Session()` speichert das Cookie automatisch.
- Alle Ressourcen liegen unter `/dataservice/...`. Antworten haben typischerweise `{"header": {...}, "data": [ ... ]}`; Keys enthalten Bindestriche (`system-ip`, `host-name`) → in Python nur per `d["host-name"]`.

### Beispiel-Endpunkte (Kurs)
| Endpunkt | Methode | Zweck |
|---|---|---|
| /dataservice/device | GET | Inventar aller Overlay-Geräte (deviceId, system-ip, host-name, reachability, status, personality, device-type, version, uuid, controlConnections …) |
| /dataservice/device/interface?deviceId=<system-ip> | GET | Interfaces eines Geräts (wie `show interface`); deviceId Pflicht, optional vpn-id, ifname, af-type |
| /dataservice/template/device/config/input | POST | Device-Input-Variablen für CLI-/Feature-Template erzeugen (templateId, deviceIds = Liste von UUIDs, isEdited, isMasterEdited) |
| /dataservice/admin/user | GET | Benutzer und Gruppen |
| /dataservice/system/device/vedges | GET | WAN-Edge-Details (serialNumber, uuid, deviceModel, deviceState, validity, vedgeCertificateState …) |
| /dataservice/certificate/view | GET | Übersicht der Zertifikats-Ansichten (Controller, vEdge List, History) |

- `isEdited`: true = bestehendes CLI-/Feature-Template wurde geändert, false = neues Template. `isMasterEdited`: true = aus Feature-Templates erstelltes Device-Template wurde geändert.
- Monitoring-GUI-Optionen (alle auch per API): Geography, Network, Alarms, Events, Audit Log, ACL Log, Interface.
- Configuration-Optionen: Devices, Certificates, Templates, Policy, CloudExpress, Cloud OnRamp. Geräte holen ihre Konfiguration beim Start vom Manager; vorher validiert der Validator das Gerät und nennt die Manager-Adresse.
- **Bulk-APIs** (große Netze): ein Aufruf für viele WAN Edges, Ergebnisse in Batches mit wählbarer Größe; Typen **State** (z. B. Anzahl/Status OMP- und BFD-Sessions) und **Statistics** (Pakete, Flows, Alarme, Events, Logs). Eigenes Wissen: Paging über `scrollId` und `hasMoreData` im `pageInfo`.

## Typische Troubleshooting-Muster
- 401 nach längerer Laufzeit (Catalyst Center) → Token abgelaufen → neu holen.
- 403 → Benutzerrolle (RBAC/ASA-Privilege-Level/ISE-Admin-Gruppe) reicht nicht.
- 415 → Content-Type/Body-Format passt nicht (z. B. XML an JSON-API, Form-Daten statt JSON).
- 400 → JSON syntaktisch kaputt (zusätzliche Klammer, einfache Anführungszeichen, Komma) oder Pflichtfeld fehlt.
- SD-WAN POST liefert 403, GET funktioniert → X-XSRF-TOKEN fehlt.
- SD-WAN-Login 200, aber Folgeaufrufe scheitern → Login eigentlich fehlgeschlagen (HTML-Body), oder Cookie nicht mitgeschickt (keine Session verwendet).
- `SSLError: certificate verify failed` → Zertifikat nicht vertraut → CA-Zertifikat hinterlegen (verify=Pfad) statt verify=False in Produktion.

## Fehler/Ungenauigkeiten im Kurs
1. **PUT** „kann keine neuen Daten anlegen“: Allgemein falsch – laut RFC 9110 Abschnitt 9.3.4 erzeugt PUT die Ressource, wenn sie nicht existiert (Antwort 201). Für einzelne APIs (wie die Intent API) mag es so dokumentiert sein.
2. Beispiel „Benutzerkonto erstellt → 200“: Für eine Neuanlage ist **201 Created** der passende Code (RFC 9110, 15.3.2); 200 ist möglich, aber das Beispiel widerspricht der eigenen Tabelle.
3. **401** sei „keine ausreichenden Rechte“: Das beschreibt **403**. 401 = fehlende/ungültige Authentifizierung (RFC 9110, 15.5.2/15.5.4); im Kurs selbst steht es in der Tabelle korrekt.
4. ASA „Privilege Level 15 or greater“: 15 ist das Maximum, „or greater“ ist sinnlos.
5. Konfigurationsoptionen „through the configuration portion of Cisco Catalyst SD-WAN Validators“: gemeint ist der **SD-WAN Manager**.
6. Template-Body (`/template/device/config/input`) enthält eine überzählige schließende Klammer → kein gültiges JSON (json.loads: „Extra data“).
7. Python-Snippets im Kurs verwenden typografische Anführungszeichen (‘ ’) → in echtem Python SyntaxError; nur Satzfehler.
8. URLs mit doppeltem Schrägstrich (`//dataservice/...`) und `{{manage_ip}}` sind Tippfehler.
9. SD-WAN-Authentifizierung: Kurs nennt nur JSESSIONID; für POST/PUT/DELETE fehlt das seit 19.2 nötige **X-XSRF-TOKEN** (Cisco DevNet SD-WAN API Docs „Authentication“).
10. Satzbruch „The common way to authenticate with the In the monitoring portion…“ – redaktioneller Fehler.

## Bilder
- `bilder/33-apis/01-sdn-planes.svg` – Application/Control/Data Plane mit Northbound- und Southbound-APIs und Merksätzen zu OpenFlow, NETCONF, OpFlex.
- `bilder/33-apis/02-imper-decl.svg` – Vergleich imperatives OpenFlow (Flow-Einträge) und deklaratives OpFlex (abstrakte Policy, Gerät setzt um).
- `bilder/33-apis/03-http-codes.svg` – Statuscodes nach Klassen 2xx/4xx/5xx mit Bedeutung und Handlungshinweis.
- `bilder/33-apis/04-api-sec.svg` – Catalyst Center ↔ ISE: TLS-Kanal, Serverzertifikat, Basic Auth pro Request, ASA-Privilege-Levels.
- `bilder/33-apis/05-cc-platform.svg` – Catalyst-Center-Plattform: Intent API, Integration API (ITSM/IPAM), Events/Webhooks, Multivendor SDK.
- `bilder/33-apis/06-cc-flow.svg` – Sequenz: Token holen, POST network-device, 202 mit taskId, Task-API pollen, Antwort interpretieren.
- `bilder/33-apis/07-sdwan-auth.svg` – Sequenz SD-WAN Manager: j_security_check, JSESSIONID, client/token, GET/POST auf /dataservice.
- `bilder/33-apis/08-sdwan-coll.svg` – SD-WAN-API-Collections mit Beispiel-Endpunkten und Bulk-APIs (State/Statistics).
