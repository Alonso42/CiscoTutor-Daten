# Implementing Wireless Client Authentication

Quelle: ENCOR 1.4.10 Student Guide, Seiten 169–181 (Intro 168, Summary Challenge 182 und Answer Key 183 nicht verwendet)

Topics: ENCOR-LEGACY-WLAN (Wireless ist im ENCOR-Blueprint v1.2 kein eigenes Thema mehr); reine CCNA-Grundlagen zu WPA2/WPA3 zusätzlich CCNA2-1.5.c

> Aktualitätshinweis: Der Kurs nennt WPA2 als "aktuellen Standard" und erwähnt WPA3 nur mit SAE. Stand heute ist **WPA3** (SAE, PMF Pflicht, 192-bit-Modus, OWE/Enhanced Open) Pflicht für Wi-Fi 6E/6 GHz und Wi-Fi-7-Zertifizierung. **WEP** und **WPA (TKIP)** sind gebrochen bzw. veraltet und dürfen nicht mehr eingesetzt werden; TKIP/WEP erlauben außerdem keine 802.11n/ac/ax-Datenraten. Referenzplattform ist der **Catalyst 9800** (IOS XE); AireOS ist Legacy.
>
> Abgrenzung: 802.1X-Grundrollen, EAPOL-Gruppenadresse, Host-Modes, MAB, dACL, CoA, Central WebAuth auf Switches und ISE-Personas stehen in Kapitel 29 (29-security-arch), RADIUS/TACACS+ in Kapitel 24 (24-aaa). Hier nur die Wireless-spezifische Vertiefung.

## Authentication Methods (Überblick)

- WEP (Original-802.11) erwies sich als schwach → IEEE 802.11i und Wi-Fi Alliance entwickelten **WPA** (Zwischenlösung, TKIP auf RC4-Basis, lief auf alter WEP-Hardware) und **WPA2** (volle 802.11i-Umsetzung, **AES-CCMP**).
- **WPA2/WPA3 Personal**: ein gemeinsamer Schlüssel (PSK bzw. SAE-Passwort) für alle Clients des SSID; kein RADIUS. Für Heim/SOHO. Wer das Passwort kennt, gehört dazu – keine individuelle Zuordnung, Widerruf nur durch Passwortwechsel für alle.
- **WPA2/WPA3 Enterprise**: 802.1X + EAP; jeder Benutzer/jedes Gerät wird einzeln gegen einen **RADIUS-Server** authentifiziert; individuelle, dynamische Sitzungsschlüssel pro Client.
- **WPA3** (Wi-Fi Alliance, 2018):
  - **WPA3-Personal** ersetzt PSK durch **SAE** (Simultaneous Authentication of Equals, "Dragonfly", eingeführt mit IEEE 802.11s-2011, seit 802.11-2012 im Basisstandard). Schutz gegen **Offline-Wörterbuchangriffe** (Mitschnitt des Handshakes reicht nicht zum Knacken) und **Forward Secrecy** (späteres Bekanntwerden des Passworts entschlüsselt alten Verkehr nicht).
  - **PMF (802.11w) ist bei WPA3 Pflicht** (Protected Management Frames).
  - **WPA3-Enterprise**: 802.1X wie WPA2-Enterprise, PMF Pflicht. Optional **192-bit-Modus** (CNSA/Suite B): GCMP-256, HMAC-SHA-384, ECDH/ECDSA mit 384-bit-Kurven, nur **EAP-TLS** mit entsprechend starken Zertifikaten.
  - **Transition Mode**: WPA2-PSK und WPA3-SAE auf demselben SSID (PMF "optional/capable"), damit Alt-Clients weiter funktionieren – Sicherheit nur so gut wie das schwächere Verfahren.
  - **6 GHz (Wi-Fi 6E/7)**: nur WPA3 (SAE/Enterprise) oder OWE, PMF Pflicht; WPA2 und reines Open sind dort nicht erlaubt.
- **Open** (keine Authentifizierung, keine Verschlüsselung) – typischer Gast-SSID mit WebAuth. **Enhanced Open / OWE** (Opportunistic Wireless Encryption, RFC 8110): Diffie-Hellman-Austausch bei der Association → individuelle Verschlüsselung ohne Passwort, aber **keine Authentifizierung** (schützt vor passivem Mitlesen, nicht vor Evil Twin). OWE-Transition-Mode: offenes SSID plus verstecktes OWE-SSID.
- **WebAuth** (Web-Portal): für Gäste, für Geräte ohne 802.1X-Supplicant, als Fallback für Mitarbeitergeräte, deren 802.1X scheitert.
- **MAB** (MAC Authentication Bypass): für Geräte ohne Benutzerinteraktion (Drucker, Kameras); MAC-Adresse als Identität (leicht fälschbar).
- **WPS** (Wi-Fi Protected Setup, früher Wi-Fi Simple Config; Push-Button/PIN) ist nicht Teil von WPA2, hat bekannte Schwächen (PIN-Brute-Force) und soll deaktiviert werden.

Zuordnung typischer Endgeräte: Gast → WebAuth; Mitarbeiter-Laptop/IP-Phone → 802.1X; Kamera/Drucker → MAB (oder iPSK).

### Verschlüsselungs-Übersicht

| Verfahren | Cipher | Status |
|---|---|---|
| WEP | RC4, 40/104-bit Key + 24-bit IV | gebrochen, verboten |
| WPA | TKIP (RC4) | veraltet, nicht mit 802.11n+ Raten |
| WPA2 | AES-CCMP-128 | Standard, aber PSK offline angreifbar |
| WPA3 | CCMP-128 (Personal/Enterprise), GCMP-256 (192-bit) | aktuell |

## PSK Authentication

- PSK = **symmetrisches** Verfahren: derselbe Schlüssel auf Client und AP.
- Gespeicherter PSK authentifiziert das **Gerät**, nicht den **Benutzer** (wer das Notebook hat, ist drin).
- Authentifizierung kann am AP/WLC (Layer 2) oder tiefer im Netz (Layer 3, z. B. WebAuth) stattfinden.
- **Open System Authentication** (802.11-Default): keine Schlüssel, keine Verschlüsselung – nur "ich bin ein 802.11-Gerät". Danach Association.
- **Shared Key Authentication (SKA)** = WEP-Verfahren: AP schickt Klartext-Challenge, Client verschlüsselt sie mit WEP-Key, AP prüft. Ein Angreifer sieht Challenge und Antwort → Keystream/Key ableitbar. SKA gilt als unsicher und ist veraltet.
- **WPA/WPA2-PSK funktioniert anders**: Open Authentication + Association, dann **4-Way Handshake**; der PSK wird **nie** übertragen, auch nicht verschlüsselt. Aus dem PSK wird die **PMK** abgeleitet: PMK = PBKDF2(Passphrase, SSID, 4096 Iterationen, 256 bit). Passphrase 8–63 ASCII-Zeichen oder 64 Hex-Zeichen.
- Grenzen von WPA2-PSK: keine individuelle Authentifizierung, alle gleiche Rechte, schwache Passphrasen per **Offline-Wörterbuchangriff** auf einen mitgeschnittenen 4-Way-Handshake knackbar; wer den PSK kennt und den Handshake eines anderen Clients mitschneidet, kann dessen Verkehr entschlüsseln (keine Forward Secrecy).
- **iPSK (Identity PSK, Cisco)**: ein SSID, aber pro Gerät/Gerätegruppe eigener PSK. WLAN mit PSK + **MAC Filtering**; der WLC schickt die MAC an ISE, ISE liefert per Cisco-AV-Pair den passenden PSK (und optional VLAN/ACL). Vorteil: einzelne Geräte widerrufbar, ohne alle umzustellen; typisch für IoT ohne 802.1X.

## 802.1X User Authentication Overview (Wireless-Sicht)

- Rollen: Supplicant (Client), **Authenticator** (im WLAN: **AP bzw. WLC** – beim zentralen Lightweight-Design ist der **WLC** der RADIUS-Client/NAS; bei FlexConnect mit lokaler Authentifizierung der AP), Authentication Server (RADIUS, z. B. ISE). In Kleinstnetzen kann der Authentication Server lokal auf WLC/AP laufen (Local EAP).
- Ablauf im WLAN: Open System Authentication → Association (Association ID) → logischer Port blockiert (nur EAPOL erlaubt) → EAP-Austausch (Supplicant ↔ WLC per EAPOL, WLC ↔ RADIUS per RADIUS) → Access-Accept + EAP-Success → **4-Way Handshake** → Datenverkehr.
- Weil zuerst Open Authentication stattfindet, zeigen WLAN-Scanner 802.1X-Netze manchmal als "open" an – entscheidend ist das RSN-IE (AKM 802.1X) im Beacon.
- Gegenseitige Authentifizierung: Client prüft das **Server-Zertifikat** (Schutz vor Rogue AP/Evil Twin).
- Ergebnis der EAP-Methode: **MSK** (Master Session Key) auf Client und Server; daraus **PMK**. Der RADIUS-Server sendet die PMK im **Access-Accept** (MS-MPPE-Recv/Send-Key, mit dem Shared Secret geschützt) an den Authenticator; der Client berechnet seine PMK selbst. Damit hat jeder Client einen eigenen, sitzungsbezogenen Schlüssel.
- Trennung Authentifizierung/Verschlüsselung: rechenintensive asymmetrische Verfahren nur für die Authentifizierung, schnelle symmetrische Verschlüsselung (AES) für die Daten.

## PKI and Certificate-Based Authentication

- **PKI**: Rahmenwerk aus CA(s), Zertifikaten, Registrierung, Widerruf.
- **Asymmetrisch**: Schlüsselpaar public/private; was mit einem verschlüsselt wird, kann nur der andere entschlüsseln. Vertraulichkeit: mit dem **Public Key des Empfängers** verschlüsseln. Signatur: mit dem **eigenen Private Key** signieren (technisch: Hash der Nachricht signieren), Empfänger prüft mit dem Public Key des Absenders → Authentizität/Integrität.
- **Zertifikat (X.509)**: Public Key + Identität (Subject, SAN) + Gültigkeit (notBefore/notAfter) + Seriennummer + Issuer + Verwendungszweck (Extended Key Usage, z. B. Server Authentication / Client Authentication), signiert vom **Private Key der CA**.
- **Vertrauenskette**: Root-CA (selbstsigniert, im Trust Store des Betriebssystems/Supplicants) → Intermediate/Issuing CA → End-Entity-Zertifikat. Prüfung: Signatur jedes Glieds mit dem Public Key des Ausstellers bis zu einem vertrauenswürdigen Root.
- **Selbstsigniertes Zertifikat**: Issuer = Subject; z. B. WLC-WebUI nach dem ersten Boot oder ISE-Default → Browser-Warnung; im Lab akzeptiert, produktiv durch CA-Zertifikat ersetzen.
- **Widerruf**: **CRL** (Certificate Revocation List, von der CA signierte Liste widerrufener Seriennummern, periodisch abgerufen) oder **OCSP** (Online Certificate Status Protocol, Echtzeitabfrage pro Zertifikat). ISE kann Client-Zertifikate bei EAP-TLS per CRL/OCSP prüfen.
- **Enrollment**: CA-Zertifikat holen und (out-of-band) verifizieren → Schlüsselpaar erzeugen → **CSR** (PKCS#10, enthält Public Key + Identität, mit eigenem Private Key signiert) → CA prüft, signiert → Zertifikat installieren. Automatisiert per **SCEP** (oder EST, MDM, Gruppenrichtlinie).
- Authentifizierung mit Zertifikaten: Parteien tauschen Zertifikate aus; die CA ist dabei **nicht** beteiligt (Offline-Prüfung über die Signatur), außer für Widerrufsprüfungen.
- Zeit ist kritisch: falsche Uhr auf Client/ISE/WLC → Zertifikat "noch nicht gültig" oder "abgelaufen" → EAP-TLS/PEAP scheitert (NTP!).
- WLCs bringen vorinstallierte Gerätezertifikate mit oder fordern eines bei einer CA an; auch als lokaler EAP-Server nutzbar.

## Introduction to EAP

- EAP (RFC 3748) ist ein **Rahmen**: definiert Nachrichten und Ablauf, nicht die Methode. Vier Codes: **Request, Response, Success, Failure**. Requests/Responses haben einen Type (z. B. Identity, NAK, TLS) und einen Identifier zum Zuordnen.
- **NAK**: Client lehnt die angebotene Methode ab und schlägt eine andere vor → EAP-Methode auf Client und Server muss zusammenpassen.
- Transport: **EAPOL** (EAP over LAN, 802.1X) zwischen Supplicant und Authenticator; **RADIUS** (EAP-Message-Attribut) zwischen Authenticator und Server. AP/WLC reichen EAP-Inhalte nur durch.
- Authentication Server: **Local EAP** auf dem WLC (lokale DB oder LDAP; auch als Backup, wenn RADIUS nicht erreichbar) oder extern (ISE, Microsoft NPS, beliebiger RADIUS).
- WPA2/WPA3-Enterprise-Zertifizierung prüft u. a. EAP-TLS, PEAP (MSCHAPv2/GTC), EAP-TTLS, EAP-SIM, EAP-AKA; EAP-FAST ist Cisco-Methode (RFC 4851).

### EAP-Methoden im Vergleich

| Methode | Client-Zertifikat | Server-Zertifikat | Innere Methode | Bemerkung |
|---|---|---|---|---|
| EAP-TLS (RFC 5216) | ja | ja | keine (Zertifikat ist Credential) | sicherste, braucht PKI auf Clients; einzig erlaubte bei WPA3-192 |
| PEAP | nein | ja | EAP-MSCHAPv2 (AD) oder EAP-GTC (Token/LDAP) | von Cisco, Microsoft, RSA; weit verbreitet |
| EAP-FAST (RFC 4851) | nein | optional | MSCHAPv2/GTC im Tunnel | Cisco; Tunnel über **PAC** statt Zertifikat |
| EAP-TTLS (RFC 5281) | nein | ja | auch Nicht-EAP (PAP, CHAP, MSCHAPv2) | ursprünglich Funk Software |
| LEAP | nein | nein | – | Cisco, MS-CHAPv1-basiert, offline knackbar → nicht einsetzen |
| TEAP (RFC 7170) | optional | ja | EAP-Chaining Maschine+User | Nachfolger von EAP-FAST (siehe Kapitel 29) |

## EAP-TLS

- Beide Seiten brauchen Zertifikat + Private Key. Ablauf: EAPOL-Start → Identity Request/Response → Server sendet Zertifikat → Client prüft es und sendet sein Zertifikat → beide prüfen Signaturen über CA → TLS-Handshake abgeschlossen → Schlüsselmaterial (MSK → PMK).
- Asymmetrische Kryptografie wird nicht für die Funkverschlüsselung genutzt (zu CPU-intensiv, und der TLS-Tunnel endet am Server, nicht am AP). Stattdessen PMK an den Authenticator → 4-Way Handshake → AES zwischen Client und AP.
- Identität ist bei EAP-TLS unkritisch (Zertifikat zählt); ISE kann Attribute aus dem Zertifikat (CN, SAN) für Autorisierung nutzen.
- Nachteil: PKI-Aufwand (Zertifikate für jeden Client, Verteilung per MDM/GPO/SCEP, Widerruf).

## PEAP

- Phase 1: TLS-Tunnel mit **nur Server-Zertifikat** (Client prüft Server-Zertifikat gegen vertrauenswürdige CA). Phase 2: innere EAP-Methode im Tunnel – **EAP-MSCHAPv2** (Benutzername/Passwort gegen AD) oder **EAP-GTC** (Token, OTP, LDAP).
- **Äußere Identität** (Outer Identity) darf anonym sein (z. B. anonymous@firma.de), die echte Identität geht erst im Tunnel – Schutz vor Mitlesen. Die äußere Identität kann für das Realm-Routing genutzt werden.
- Wichtigster Sicherheitsfehler: Clients, die das **Server-Zertifikat nicht prüfen**, verbinden sich mit einem Evil Twin; dort wird der MSCHAPv2-Austausch mitgeschnitten und offline angegriffen → Server-Validierung (CA + Servername) per Profil erzwingen.
- Ergebnis wie EAP-TLS: PMK → Access-Accept → 4-Way Handshake.

## EAP-FAST

- Cisco-Methode ohne Pflicht zu Zertifikaten; Tunnel basiert auf **PAC (Protected Access Credential)**.
- Phasen: **Phase 0** – PAC-Provisionierung (automatisch "in-band" oder manuell); anonymes Provisioning (anonymous Diffie-Hellman) ist anfällig für MITM, authentifiziertes Provisioning nutzt ein Server-Zertifikat. **Phase 1** – TLS-Tunnel mit PAC (PAC-Key als Shared Secret). **Phase 2** – Benutzer-Authentifizierung im Tunnel (MSCHAPv2, GTC).
- PAC-Bestandteile: **PAC-Key** (32 Byte, zufällig vom Server erzeugt, Basis für den Tunnel), **PAC-Opaque** (nur der Server kann es lesen; enthält PAC-Key + Identität, verschlüsselt mit dem Master Key des Servers – Server muss keine PAC-Datenbank halten), **PAC-Info** (mindestens A-ID = Authority-ID des Servers, optional Lebensdauer).
- Ablauf PAC-Nutzung: Server sendet A-ID → Client wählt passende PAC → schickt PAC-Opaque → Server entschlüsselt mit Master Key, erhält PAC-Key → Tunnel.
- Identität im NAI-Format (user@realm).
- Heute weitgehend durch **TEAP** abgelöst.

## Guest Access with WebAuth

Drei Designentscheidungen: **Pfadisolierung** (lokaler WLC oder Anchor-WLC), **Portalseiten** (auf dem WLC oder extern), **Benutzerkonten** (lokal auf dem WLC oder zentral auf RADIUS/ISE).

- **Local Web Authentication (LWA)**: WLC stellt Portal + lokale Gastkonten (Benutzername, Passwort, zulässiges WLAN, Lebensdauer); SSID typischerweise **Open** + Layer-3-Web-Policy, eigenes Gast-VLAN. Anpassbare Login-Seite, AUP. **Lobby Ambassador**: Management-Konto, das nur Gastkonten anlegen/verlängern/löschen darf.
- **LWA mit externer Authentifizierung**: Portal am WLC, Prüfung der Credentials per RADIUS (ISE).
- **Central Web Authentication (CWA)**: ISE stellt Portal und Gastkonten. WLAN: Layer 2 none/Open + **MAC Filtering** (MAB zu ISE); ISE antwortet mit **url-redirect** und **url-redirect-acl**; Policy Profile mit **AAA Override** und **NAC State (RADIUS NAC)**; nach dem Portal-Login sendet ISE **CoA**, der WLC authentifiziert neu und vergibt die endgültige Policy. Vorteil: zentrale Konten, Sponsor-/Self-Registration-Portale, Audit in ISE.
- Pre-Auth: DHCP und DNS müssen vor der Anmeldung erlaubt sein; nur HTTP/HTTPS wird umgeleitet. HTTPS-Umleitung erzeugt Zertifikatswarnungen (darum öffnete der Kurs-Lab den virtuellen Portal-IP direkt).
- **Virtual IP** des WLC (9800: im globalen Parameter-Map `virtual-ip ipv4 192.0.2.1`; AireOS: Virtual Interface) – nicht routbare Adresse, unter der das WebAuth-Portal erscheint; muss auf allen WLCs einer Mobility-Gruppe gleich sein.
- **9800 WebAuth Parameter-Map-Typen**: `webauth` (Benutzername/Passwort), `consent` (nur AUP akzeptieren, "web-passthrough"), `webconsent` (AUP + Credentials), `authbypass` (MAC gegen Server, ohne Interaktion).

### Guest Anchor (Auto-Anchor)

- Gast-SSID auf den Campus-APs, aber Gastverkehr soll in der **DMZ** austreten, ohne Gast-VLAN durch den Campus zu ziehen.
- **Foreign WLC** (an dem die APs hängen) tunnelt den Client-Verkehr zum **Anchor WLC** in der DMZ (Mobility-Tunnel). Der Anchor vergibt die IP (Gast-VLAN liegt nur dort), stellt meist auch das LWA-Portal bereit und leitet ins Internet.
- 9800: Mobility-Tunnel ist **CAPWAP** (Control UDP **16666**, Data UDP **16667**); AireOS-Legacy nutzte **EoIP** (IP-Protokoll 97) + UDP 16666 für Control. Diese Ports in der DMZ-Firewall freigeben.
- 9800-Konfiguration: im Policy Profile des Foreign `mobility anchor <anchor-ip> priority 1`; auf dem Anchor im Policy Profile `mobility anchor` (ohne IP = Export-Anchor). WLAN-Profil (Name, SSID, Security) **und Policy-Profil (gleicher Name, gleiche Einstellungen; nur das VLAN darf abweichen)** müssen laut Cisco auf beiden WLCs übereinstimmen. Mobility-Peering muss "up" sein.
- Mehrere Anchors für Redundanz (Prioritäten).

## Describe EAPOL / 4-Way Handshake

- EAPOL transportiert EAP zwischen Supplicant und Authenticator und zusätzlich die **EAPOL-Key**-Frames des 4-Way-Handshakes.
- Schlüsselhierarchie (WPA2):
  - **PMK** (Pairwise Master Key, 256 bit): bei Enterprise aus der MSK (vom RADIUS-Server an den Authenticator), bei Personal aus dem PSK (PBKDF2). Wird nie über Funk übertragen.
  - **PTK** (Pairwise Transient Key) = PRF(PMK, ANonce, SNonce, MAC-Adresse AP, MAC-Adresse Client). Bestandteile: **KCK** (MIC über EAPOL-Key-Frames), **KEK** (verschlüsselt die GTK im Handshake), **TK** (verschlüsselt Unicast-Daten).
  - **GTK** (Group Temporal Key): vom AP erzeugt, für Broadcast/Multicast an alle Clients des BSS; bei WPA3/PMF zusätzlich **IGTK** für Broadcast-Management-Frames.
- Ablauf:
  1. AP → Client: **ANonce** (kein MIC).
  2. Client erzeugt SNonce, berechnet PTK; Client → AP: **SNonce + MIC** (+ RSN-IE). AP berechnet PTK und prüft MIC → beweist, dass der Client dieselbe PMK hat.
  3. AP → Client: ANonce, **MIC**, **GTK (mit KEK verschlüsselt)**, RSN-IE, Install-Flag. Client prüft MIC, installiert PTK + GTK.
  4. Client → AP: Bestätigung mit MIC; AP installiert PTK. Port offen für Daten.
- **Group Key Handshake** (2 Nachrichten) verteilt später eine neue GTK (z. B. periodisch oder wenn ein Client den BSS verlässt).
- Fehlerbilder: falscher PSK → MIC in Nachricht 2 ungültig, AP bricht nach Nachricht 1 / 2 ab ("4-way handshake timeout"/ MIC failure); kein Hinweis auf "falsches Passwort" im Frame selbst. KRACK (2017) nutzte Neuinstallation der Schlüssel bei wiederholter Nachricht 3 – durch Patches behoben.
- Roaming: voller 802.1X-Neuaufbau ist langsam; **PMK Caching / OKC** und **802.11r (Fast Transition)** verkürzen das, indem beim Roaming nur noch der Schlüsselhandshake (bzw. FT-Austausch) läuft.

## Initialize Centralized Cisco WLC

- Catalyst 9800-Modelle: 9800-80, 9800-40, 9800-L (Hardware), 9800-CL (virtuell/Cloud), Embedded auf Catalyst 9300 (SD-Access), EWC auf Catalyst-APs. Deployment-Modelle: Centralized, FlexConnect, SD-Access (Fabric).
- WLC kommt **ohne Konfiguration**. Initialisierung per Console-CLI, Day-0 CLI-Wizard (`setup`) oder Day-0 GUI-Wizard.
- Console: RJ-45 und USB (mini-B bzw. micro-B je Modell; USB hat Vorrang, wenn beide stecken), **9600 Baud, 8 Datenbits, 1 Stoppbit, keine Parität, keine Flusskontrolle**. 9800-CL: VGA-/serielle VM-Konsole.
- Day-0 CLI-Wizard: nur ohne Startup-Config (neu oder nach `write erase` + Reload). Abfragen u. a.: Management-Interface und -IP, statische Route, Management-Credentials, **Wireless Management Interface**, Deployment-Modus (standalone/active/standby), Hostname, AP-Credentials, **Country Code**, NTP/Zeit; optional Zeitzone, Client-Dichte, AAA-Server, SSID, **Virtual IP**, RF Group Name, HA. Abschluss: `[2] Save this configuration to nvram and exit`. Erneut startbar mit `setup` im privileged EXEC; Wizard überspringen mit "no".
- Day-0 GUI (9800-Hardware): PC an Service Port/Front-Port, `https://<ip>`; Default-Login **webui**, Passwort = **Seriennummer** des Geräts (laut Kurs). Danach Admin-Konto, General Settings (Deployment-Modus, Country, Zeit, NTP, AAA), Wireless Management Settings (Port, VLAN, IP, Gateway), Wireless Networks (Employee/Guest-SSID), Advanced (RF Client Density, AP Certificate) → Finish.
- EWC: SSID **CiscoAirProvision**, `https://mywifi.cisco.com`, Default webui/cisco; alternativ Cisco Catalyst/Wireless App. Voraussetzungen: kein anderer WLC im Netz, externer DHCP.
- Default: SSH an, Telnet aus; CLI-Session-Timeout Default 5 min (laut Kurs; der IOS-XE-Default für `exec-timeout` auf Line-Ebene ist 10 min – im Zweifel am Gerät prüfen).

### WLC-Interfaces

| Catalyst 9800 | AireOS (Legacy) | Zweck |
|---|---|---|
| Wireless Management Interface (meist SVI, z. B. Vlan10) | Management Interface (+ früher AP-Manager) | CAPWAP-Terminierung, RADIUS-Quelle, Management |
| Service Port **Gi0** (VRF Mgmt-intf, Out-of-Band) | Service-Port | OOB-Management; eigenes Subnetz, kein Client-Verkehr |
| Virtual IP im WebAuth-Parameter-Map (`virtual-ip ipv4 192.0.2.1`) | Virtual Interface (früher 1.1.1.1, heute 192.0.2.1 empfohlen) | WebAuth-Portal-Adresse, DHCP-Proxy; nicht routbar, auf allen WLCs der Mobility-Gruppe gleich |
| Client-VLANs auf dem Trunk (SVI nicht nötig) | Dynamic Interfaces | VLANs, in die Client-Verkehr ausgegeben wird |
| RP-Port / Redundancy Management Interface | Redundancy Port/RMI | SSO-Synchronisation |

## Getting Familiar with Cisco WLC GUI (9800)

- Zugriff per Browser auf `http(s)://<WLC-IP>`; HTTP Port 80, HTTPS Port 443 (beide per Default aktiv); HTTP für die GUI deaktivieren empfohlen (WebAuth- und GUI-Zugriff getrennt konfigurierbar). IOS-XE-Befehle: `ip http server`, `ip http secure-server`.
- Dashboard: Anzahl WLANs, APs, Clients (aktiv/excluded), Rogues, Interferer; Widgets (CPU/Memory, Top WLANs, Top APs, Client-Gerätetypen, Systeminfo). Landing Page anpassbar.
- Hauptmenü: **Monitoring**, **Configuration**, **Administration** (Benutzer, Software, CLI, Best Practices), **Licensing**, **Troubleshooting** (Packet Capture, Ping/Traceroute, Logs, Radioactive Trace/Debug).

## Catalyst 9800 Konfigurationsmodell (Profile und Tags)

- **WLAN Profile**: SSID, WLAN-ID, Status, Broadcast, Funkband, **Layer-2-Security** (WPA2/WPA3, AKM PSK/802.1X/SAE/FT, PMF), **Layer-3-Security** (Web Policy, Parameter Map), AAA-Authentifizierungsliste.
- **Policy Profile**: VLAN/VLAN-Gruppe, ACL, QoS, Central/Local Switching und Authentication (FlexConnect), AAA Override, NAC State, Session Timeout, Accounting, **Mobility Anchor**.
- **Policy Tag**: verbindet WLAN Profile ↔ Policy Profile (welche SSIDs mit welcher Policy ein AP ausstrahlt).
- **Site Tag**: AP Join Profile (CAPWAP, Credentials, Backup-WLC …), Flex Profile, Local Site ja/nein (Local- vs. FlexConnect-Modus).
- **RF Tag**: RF Profile 2.4/5/6 GHz.
- Jedes AP hat genau einen Policy-, Site- und RF-Tag; ohne Zuweisung die Default-Tags (`default-policy-tag`, `default-site-tag`, `default-rf-tag`). Der `default-policy-tag` bindet laut Cisco-Dokumentation nur WLANs mit ID 1–16 automatisch an das `default-policy-profile`.
- Zuweisung: statisch pro AP (`ap <MAC>` → `policy-tag`, `site-tag`, `rf-tag`), per Filter (Regex auf AP-Namen), per Location (Basic Wireless Setup) oder Catalyst Center. Änderung des Tags kann ein CAPWAP-Neuaufbau des AP auslösen (Kurs: AP startet Join neu, Location zeigt kurz 0 Joined APs).
- Basic/Advanced Wireless Setup Wizard: erzeugt Profile und Tags im Hintergrund (intent-based).

### CLI-Beispiele (IOS XE 17.x)

WPA2-PSK:
```
wlan ENCOR-SALES 30 ENCOR-SALES
 no security wpa akm dot1x
 security wpa akm psk
 security wpa psk set-key ascii 0 <Passphrase>
 no shutdown
```
(Ein neues 9800-WLAN hat per Default WPA2 + AES-CCMP + AKM 802.1X.)

WPA2/WPA3-Enterprise mit ISE:
```
aaa new-model
radius server ISE
 address ipv4 10.10.10.60 auth-port 1812 acct-port 1813
 key <Secret>
aaa group server radius ISE-Group
 server name ISE
aaa authentication dot1x dot1x-method group ISE-Group
wlan CORP 20 CORP
 security dot1x authentication-list dot1x-method
 no shutdown
```

WPA3-SAE:
```
wlan HOME3 5 HOME3
 no security wpa wpa2
 security wpa wpa3
 no security wpa akm dot1x
 security wpa akm sae
 security wpa psk set-key ascii 0 <Passwort>
 security pmf mandatory
 no shutdown
```

Gast mit LWA (Consent):
```
parameter-map type webauth global
 type consent
 virtual-ip ipv4 192.0.2.1
wlan ENCOR-Guest 40 ENCOR-Guest
 no security wpa
 security web-auth
 security web-auth parameter-map global
 no shutdown
```

Policy Profile, Policy Tag, AP:
```
wireless profile policy PP-EMP
 vlan 30
 no shutdown
wireless tag policy PT-CAMPUS
 wlan ENCOR-SALES policy PP-EMP
ap 00aa.bbcc.ddee
 policy-tag PT-CAMPUS
```

Verifikation:
```
show wlan summary
show wlan name ENCOR-SALES
show wireless client summary
show wireless client mac-address <MAC> detail
show wireless tag policy summary
show ap tag summary
```
Typischer Ausschnitt `show wireless client mac-address … detail` (gekürzt, Beispiel):
```
Client MAC Address : 3c22.fb11.2233
Wireless LAN Name  : ENCOR-SALES
Policy Profile     : PP-EMP
VLAN               : 30
Policy Manager State: Run
Authentication     : 802.1X
  EAP Type         : PEAP
Encryption Cipher  : CCMP (AES)
Auth Key Management: 802.1x
```
Client-Zustände (Policy Manager): Associated → Authenticating (L2) → (Mobility) → IP Learn → (Webauth Pending) → **Run**. Ein Gast im Zustand *Webauth Pending* hat zwar IP, darf aber nur Pre-Auth-Verkehr (DHCP/DNS) senden.

## Discovery 18 (Lab): Configure Wireless Client Authentication

- Topologie: Admin-PC 10.10.10.10, Campus-WLC 9800-CL 10.10.10.30 (WMI), Gateway 10.10.10.1/10.10.30.1/10.10.40.1, ISE 10.10.10.60, Employee-VLAN 30, Guest-VLAN 40, zwei APs per DHCP im Management-Netz.
- Task 1: Basic Wireless Setup → Location "Campus" (Location Type Local = AP-Modus Local; Client Density Typical).
- Task 2: WLAN ENCOR-SALES, WLAN-ID 30 (Empfehlung: ID = VLAN-Nummer), Layer 2 WPA + WPA2, WPA2-Policy, AES (CCMP128), AKM PSK statt 802.1X, PSK ASCII. VLAN 30 zuordnen, APs per AP Provisioning der Location zuweisen → APs joinen neu (CAPWAP-Neuaufbau). Test: Client erhält 10.10.30.x, Ping Gateway.
- Task 3: ISE – Benutzer anlegen, WLC als **Network Device (NAD)** mit IP 10.10.10.30/32 und RADIUS Shared Secret. WLC – AAA Wizard: RADIUS-Server (Name, IP, Key), Server Group, Method List Typ **dot1x** (nur Authentication). WLAN umstellen: AKM 802.1X, AAA → Authentication List `dot1x-method`. WLAN zeigt [WPA2][Auth(802.1X)]. Client: PEAP mit GTC, Benutzername/Passwort.
- Task 4: WebAuth-Parameter-Map global → Typ **consent**; WLAN ENCOR-Guest (ID 40): Layer 2 **None**, Layer 3 **Web Policy** + Parameter-Map global, VLAN 40. Client bekommt IP 10.10.40.x, Ping zum Gateway scheitert, Status **Webauth Pending** bis zur Zustimmung über `192.0.2.1`; danach Gateway erreichbar, Employee-Netz weiterhin nicht (Segmentierung). Zeitlimit im Lab: Anmeldung innerhalb 120 s.
- Für einen neuen WLAN sind mindestens Profilname, SSID und WLAN-ID nötig; für einen AAA-Server Name, IP-Adresse und Shared Secret.

## Fehler/Ungenauigkeiten im Kurs

- S. 170: "PSK authentication process also known as shared key authentication (SKA)" – vermischt zwei Verfahren. SKA ist das WEP-Challenge-Verfahren; WPA/WPA2-PSK nutzt Open Authentication + 4-Way Handshake (der Kurs sagt das weiter unten selbst). Quelle: IEEE 802.11-2020, Kap. 12 (RSNA); Wi-Fi Alliance WPA2/WPA3 Spec.
- S. 170: In SKA "entschlüsselt" der AP die Antwort nicht im eigentlichen Sinn, sondern vergleicht das Ergebnis mit seiner eigenen WEP-Verschlüsselung der Challenge – inhaltlich gleichwertig, aber ungenau.
- S. 169: WPA2 als "current standard" ist veraltet – WPA3 ist seit 2018 verfügbar, seit 2020 Pflicht für Wi-Fi-CERTIFIED-Geräte und im 6-GHz-Band zwingend.
- S. 172: Digitale Signatur als "Verschlüsseln der Credentials mit dem Private Key" ist vereinfacht; signiert wird ein Hash. Ebenso wird ein CSR nicht "mit dem Public Key der CA verschlüsselt", sondern mit dem Private Key des Antragstellers signiert (SCEP umhüllt die Anfrage zusätzlich). Quelle: RFC 2986 (PKCS#10), RFC 8894 (SCEP).
- S. 173 Tabelle: EAP-TTLS als "proprietary standard" – EAP-TTLSv0 ist in RFC 5281 (informational) offen beschrieben und z. B. in Windows, Android, iOS eingebaut. "Provider Microsoft" für EAP-TLS ist irreführend (IETF-Standard RFC 5216). LEAP als "Medium" ist zu wohlwollend – LEAP ist mit asleap offline knackbar und darf nicht mehr eingesetzt werden.
- S. 173: "EAP-TLS gaining popularity because it can be supported by ISE" – der eigentliche Grund ist die höhere Sicherheit (keine Passwörter) und Zero-Trust/WPA3-192.
- S. 174/175: "primary key" als Ausschreibung von PMK – korrekt heißt PMK **Pairwise Master Key** (Cisco ersetzt "master" sprachlich durch "primary"); auch "primary session key" meint die MSK (Master Session Key, RFC 3748/5247).
- S. 175: "PMK can be used to directly generate a WEP key" – veraltet; heute leitet der 4-Way Handshake daraus PTK/GTK für CCMP/GCMP ab.
- S. 175: PEAP "tut nur so", als ob TLS liefe – tatsächlich ist Phase 1 ein echter TLS-Handshake mit Server-Zertifikat (nur ohne Client-Zertifikat).
- S. 179: USB-Konsole einmal "micro-B", einmal "5-pin mini-USB Type-B" – modellabhängig; der Text widerspricht sich.
- S. 179: Centralized wird einmal für "small campus", dann als "ideal for large enterprise" beschrieben.
- S. 181 (Lab): Schritt 23 spricht von "ISE login page", obwohl der Lab eine lokale Consent-Seite des WLC nutzt; Schritt 17 nennt die Windows-Taskleiste, die Client-PCs sind aber Linux mit Network Manager.

## Bilder

- `bilder/17-wlan-auth/01-modi.svg` – Übersicht WLAN-Sicherheitsmodi: Open, OWE, WPA2/WPA3-Personal, WPA2/WPA3-Enterprise, Status (veraltet/aktuell) und Cipher.
- `bilder/17-wlan-auth/02-4way.svg` – 4-Way Handshake mit ANonce/SNonce/MIC/GTK und Schlüsselhierarchie PMK → PTK (KCK/KEK/TK) + GTK.
- `bilder/17-wlan-auth/03-dot1x-wlan.svg` – 802.1X im zentralen WLAN: Open Auth, Association, EAPOL zum WLC, RADIUS zu ISE, PMK im Access-Accept, danach 4-Way Handshake.
- `bilder/17-wlan-auth/04-eap-vergl.svg` – Vergleich EAP-TLS / PEAP / EAP-FAST: Zertifikate, Tunnel, innere Methode, Phasen.
- `bilder/17-wlan-auth/05-pki-kette.svg` – PKI: Root-CA → Issuing CA → Server-/Client-Zertifikat, Prüfung über Signaturen, CRL/OCSP.
- `bilder/17-wlan-auth/06-guest-anc.svg` – Guest Anchor: Foreign-WLC tunnelt Gastverkehr zum Anchor in der DMZ; LWA vs. CWA.
- `bilder/17-wlan-auth/07-9800-tags.svg` – Catalyst-9800-Modell: WLAN Profile + Policy Profile → Policy Tag; Site Tag; RF Tag; AP.
- `bilder/17-wlan-auth/08-wlc-if.svg` – WLC-Interfaces 9800 vs. AireOS und Day-0-Wege (CLI-Wizard, GUI-Wizard, EWC).
