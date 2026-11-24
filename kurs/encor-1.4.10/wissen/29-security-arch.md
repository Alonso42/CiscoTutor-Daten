# Exploring Enterprise Network Security Architecture

Quelle: ENCOR 1.4.10 Student Guide, Seiten 314–330 (313 Intro, 331 Summary Challenge und 332 Answer Key nicht ausgewertet)

Topics: ENCOR-5.4.a (Threat defense: Threatscape, IPS/IDS, Content Security, Logging/SIEM, Talos/Umbrella/XDR), ENCOR-5.4.b (Endpoint security: Personal Firewall, AV/Antispyware, Posture, Cisco Secure Endpoint, Netzwerkzugangskontrolle mit ISE: 802.1X, MAB, WebAuth – wie im Bestand e45-055/e45-056/r1-020/m3-029 unter 5.4.b geführt), ENCOR-5.4.c (Firewall-Konzepte, Zonen, Stateful, Cisco Secure Firewall/NGFW), ENCOR-5.4.d (TrustSec mit SGT/SXP/SGACL, MACsec/MKA), am Rande ENCOR-2.2.b (VPN-Grundbegriffe).

Ergänzungen, die nicht im Kurs stehen, sind mit *(Ergänzung)* markiert. Quellen: Cisco IOS XE 17.x Security Configuration Guides (IEEE 802.1X Port-Based Authentication, MAC Authentication Bypass, Web-Based Authentication, MACsec Encryption, Cisco TrustSec), Cisco ISE 3.x Admin Guide, Cisco Secure Firewall/Secure Endpoint Produktdokumentation, IEEE 802.1X-2010, IEEE 802.1AE, RFC 3748 (EAP), RFC 5176 (RADIUS CoA), RFC 3394 (AES Key Wrap).

### Aktuelle Produktnamen (wichtig, Kurs nutzt teils alte Namen)

| Alter Name (Kurs) | Aktueller Name |
|---|---|
| AMP for Endpoints | Cisco Secure Endpoint |
| AMP for Networks (Firepower) | Malware Defense / File Policy in Cisco Secure Firewall |
| Firepower NGFW, NGFW, Firepower Threat Defense | Cisco Secure Firewall (Software: Secure Firewall Threat Defense, FTD) |
| FireSIGHT / Firepower Management Center | Secure Firewall Management Center (FMC) |
| Email Security Appliance (ESA) | Cisco Secure Email Gateway (Cloud: Secure Email Cloud Gateway) |
| Web Security Appliance (WSA) | Cisco Secure Web Appliance |
| AnyConnect Secure Mobility Client | Cisco Secure Client (ab 5.0) |
| Threat Grid | Cisco Secure Malware Analytics |
| Stealthwatch | Cisco Secure Network Analytics |
| SecureX | End-of-Life 31.07.2024 → Nachfolger Cisco XDR |
| Collective Security Intelligence Cloud | Talos-gestützte Secure-Endpoint-Cloud |
| Umbrella | Cisco Umbrella (DNS-Layer Security/SIG; inzwischen auch Teil von Cisco Secure Access/SSE) |

*(Ergänzung)* „App-ID“ ist ein Palo-Alto-Begriff. Bei Cisco heißt die Anwendungserkennung Application Visibility and Control (AVC), auf der Secure Firewall basierend auf Snort/OpenAppID.

---

## 1. Threatscape (S. 314)

Threatscape = Gesamtheit der Bedrohungsarten und -quellen (extern und intern), ständig wachsend und nie vollständig katalogisierbar. Angreifer: Einzelpersonen, organisierte Kriminalität, Staaten (viel Geld, viel Know-how). Kein Industriezweig ist ausgenommen.

### Begriffe
- **Vulnerability (Schwachstelle):** Schwäche, die Sicherheit oder Funktion eines Systems kompromittiert (z. B. schwaches Passwort, ungepatchter Dienst).
- **Exploit:** Mechanismus/Werkzeug, das eine Schwachstelle ausnutzt. Veröffentlichte Exploit-Tools erlauben auch wenig versierten Angreifern Angriffe.
- **Threat (Bedrohung):** Umstand/Ereignis mit Schadenspotenzial (Zerstörung, Offenlegung, Veränderung von Daten, DoS), z. B. Malware gegen Workstations.
- **Risk (Risiko):** Wahrscheinlichkeit, dass eine bestimmte Bedrohung mit einem bestimmten Angriff eine bestimmte Schwachstelle ausnutzt und Schaden entsteht.

### Angriffs- und Bedrohungsarten
| Art | Kernidee | Gegenmaßnahmen *(Ergänzung)* |
|---|---|---|
| DoS / DDoS | kritische Ressource (Bandbreite, CPU, Sessions) erschöpfen; DDoS = viele Quellen (Botnetz) | Rate-Limiting, CoPP, Upstream-Scrubbing, SYN-Cookies |
| Spoofing | Traffic mit fremder Absenderidentität (IP, MAC, ARP, DHCP); kein Angriff an sich, sondern Baustein | uRPF, DHCP Snooping, DAI, IP Source Guard |
| Reflection (und Amplification) | Anfragen mit gefälschter Quell-IP = Opfer an viele Hosts (Reflektoren); deren Antworten fluten das Opfer. Amplification: Antwort größer als Anfrage (DNS, NTP, memcached) *(Ergänzung)* | Anti-Spoofing (BCP 38), offene Resolver schließen |
| Social Engineering | Menschen manipulieren (Beziehungen, Normen, Hilfsbereitschaft) | Awareness-Schulungen |
| Phishing | Social-Engineering-Mail, die sich als legitime große Organisation ausgibt; gefälschte Webseite sammelt Konto-/Zugangsdaten. Varianten *(Ergänzung)*: Spear Phishing (gezielt), Whaling (Führungskräfte), Vishing (Telefon), Smishing (SMS) | Secure Email, Umbrella, MFA |
| Password Attacks | Raten, Brute Force (alle Kombinationen), Dictionary (Wortlisten) | Länge + großer Zeichensatz, Lockout, MFA |
| Reconnaissance | Informationssammlung vor dem eigentlichen Angriff, z. B. mit `dig`, `nslookup`, `whois` (öffentliche DNS-/Registry-Daten); *(Ergänzung)* Ping-Sweeps, Port-Scans (nmap) | IPS, Minimierung öffentlicher Infos |
| Buffer Overflow | Dienst prüft Eingabelänge nicht → benachbarter Speicher wird überschrieben → Absturz (DoS) oder eingeschleuster Code (Kompromittierung) | Patchen, Eingabevalidierung, IPS-Signaturen |
| Man-in-the-Middle | Angreifer setzt sich in den Kommunikationspfad; erfordert Angriffe auf Routing oder ARP/DNS/DHCP | DAI, DHCP Snooping, TLS/IPsec, MACsec |
| Malware | Viren, Würmer, Trojaner; installiert sich auf dem Opfersystem → Kontrolle, Verschlüsselung (Ransomware), Rechteausweitung als Teil einer APT | Secure Endpoint, NGFW, Umbrella |
| Data Loss / Exfiltration | unautorisierter Datenabfluss: E-Mail-Anhänge, unverschlüsselte Geräte, Cloud-Speicher, USB-Sticks, schlechte Zugriffskontrollen | DLP (Secure Email), Verschlüsselung, Zugriffskontrolle |
| Hacking Tools | Unterschied Security-Tool vs. Angriffstool = Absicht; Beispiele: sectools.org, Kali Linux, Metasploit; Penetrationstester nutzen sie legitim | – |

*(Ergänzung)* Virus = hängt sich an ein Wirtsprogramm und braucht Ausführung; Wurm = verbreitet sich selbstständig über das Netz; Trojaner = tarnt sich als nützliche Software; Ransomware = verschlüsselt Daten und erpresst Lösegeld; Botnetz = ferngesteuerte Rechner über Command-and-Control (C2); APT = langfristiger, gezielter, verdeckter Angriff.

### Fehlannahmen
- „Niemand interessiert sich für unser Netz“ / „Wir wurden nie gehackt“ – oft falsch.
- „Sicherheit ist nur Aufgabe der IT“ – Endbenutzer spielen die Hauptrolle bei der Umsetzung, sie sind zahlenmäßig weit überlegen.
- „Eine Firewall macht sicher“ – reine Perimeter-Denke ist überholt, interne Systeme müssen ebenfalls geschützt werden, Firewalls können fehlkonfiguriert sein und tun sich schwer mit Client-seitigen Angriffen. Keine einzelne Technologie genügt (Defense in Depth).
- Threat Intelligence: Cisco Talos (talosintelligence.com).

---

## 2. Cisco IPS (S. 315)

- IPS = tiefe Analyse des Traffics (Deep Packet Inspection) nach verdächtigem/bösartigem Verhalten; kann aktiv schützen. Ergänzt die Firewall: Firewall fragt „woher/wohin?“ (Header), IPS fragt „was steckt im Paket?“. Erkennt u. a. Botnetze, Malware, Anwendungsmissbrauch.
- **Network-based IPS:** Sensor (dedizierte Appliance oder Modul in einem anderen Gerät) an definierten Punkten im Netz, schützt unabhängig vom Ziel des Angriffs.
- **Host-based IPS (HIPS):** Software auf dem Host, erkennt nur Angriffe auf diesen Host.

### Inspektionsmethoden
| Methode | Funktionsweise | Stärke / Schwäche |
|---|---|---|
| Signature-based (rule-based, pattern matching) | vergleicht Header/Payload mit Datenbank bekannter Angriffssignaturen (Byte-Folgen im Kontext) | präzise bei bekannten Angriffen; Datenbank muss ständig aktualisiert werden; blind für Zero-Days |
| Anomaly-based: statistisch (Network Behavior Analysis) | lernt ein Normalprofil (Kommunikationsmuster, Rate, Protokollmix, Volumen) und reagiert auf Abweichungen | erkennt Unbekanntes; Lernphase, eher False Positives |
| Anomaly-based: Protocol Verification | vergleicht L3/L4/L7-Protokollnutzung mit den Standards (z. B. malformed IP packet) | erkennt Protokollmissbrauch |
| Policy-based | Aktion bei Ereignissen außerhalb einer konfigurierten Traffic-Policy | nur so gut wie die Policy |

- **NGIPS** kombiniert die Methoden, nutzt Traffic-Normalisierung und Protokoll-Decoder gegen Evasion, dazu Reputation, Kontextwissen, Event-Korrelation und Cloud-Dienste. *(Ergänzung)* Bei Cisco Secure Firewall ist die IPS-Engine Snort (FTD 7.x: Snort 3), Regeln/Feeds kommen von Talos.

### IDS vs. IPS *(Ergänzung)*
| | IDS | IPS |
|---|---|---|
| Einbau | promiscuous / out-of-band (Kopie via SPAN/TAP) | inline im Datenpfad |
| Erstes bösartiges Paket | erreicht das Ziel (nur Alarm) | kann verworfen werden |
| Latenz / Ausfallwirkung | keine Auswirkung auf Traffic | fügt Latenz hinzu; Ausfall unterbricht Traffic, wenn nicht fail-open/Bypass |
| Reaktionen | Alarm, ggf. TCP-Reset, Shunning über andere Geräte | Drop, Reset, Block der Verbindung/Quelle, Alarm |

Alarmbewertung: **True Positive** = Angriff erkannt; **False Positive** = Alarm bei harmlosem Traffic (stört Betrieb, bei IPS werden legitime Pakete verworfen); **True Negative** = harmloser Traffic korrekt ignoriert; **False Negative** = echter Angriff nicht erkannt (gefährlichster Fall).

---

## 3. VPN-Grundlagen im Security-Kontext (S. 316)

- RFC 2828 (heute RFC 4949): VPN = logisches, eingeschränkt genutztes Netz über ein öffentliches physisches Netz, oft mit Verschlüsselung und Tunneling. Virtual/Private/Network.
- Klartext-Protokolle: Telnet, FTP, TFTP, POP, SMTP.
- **Link encryption:** ganzer Frame zwischen zwei direkt verbundenen Geräten verschlüsselt (Punkt-zu-Punkt; vgl. MACsec). **Packet payload encryption:** nur die Nutzlast → über L3-Netze (Internet) routbar (vgl. IPsec).
- Anforderungen kryptografischer VPNs: Confidentiality (Verschlüsselung), Origin Authentication, Data Integrity. *(Ergänzung)* IPsec bietet zusätzlich Anti-Replay.
- Deployment: Site-to-Site vs. Remote Access (Client oder SSL-fähiger Browser). Technologien: IPsec, SSL/TLS, MPLS, L2 (Frame Relay/ATM), hybrid.
- Vorteile: Security, Scalability, Kompatibilität mit Breitband, Kostenersparnis. (Bandbreitenersparnis ist KEIN Vorteil – Verschlüsselung erzeugt Overhead.)
- Details zu IPsec/IKE: siehe Kapitel 14-vpn.

---

## 4. Content Security (S. 317)

### Cisco Secure Email Gateway (Kurs: ESA)
- Firewall- und Threat-Monitoring-Appliance für SMTP: schnelles Blocken neuer E-Mail-basierter Blended Attacks, Kontrolle/Verschlüsselung sensibler ausgehender Mails (DLP), hohe Spam-Erkennungsrate mit wenigen False Positives, „Zero-Hour“-Antivirus (Outbreak Filters).
- Kursbild: eingehende Mail → (1) Perimeter → (2) ESA prüft → Malware wird verworfen; saubere Mail → (3) an den Empfänger.
- *(Ergänzung)* Das Gateway ist ein Mail Transfer Agent (MTA): Der MX-Record zeigt auf das Gateway (oder die Firewall leitet SMTP per NAT/Regel dorthin). Reputationsfilter nutzen Talos-Daten (früher SenderBase).

### Cisco Secure Web Appliance (Kurs: WSA)
- Sicherer Webzugang, Content Security, Threat Mitigation: Advanced Malware Protection, Application Visibility and Control, Reporting, Secure Mobility.
- Ablauf blockiert: Request (z. B. Glücksspiel-Site) → WSA → Block-Seite mit Policy-Hinweis an den Benutzer.
- Ablauf erlaubt: Request → WSA → WSA proxyt zur Website → Antwort an WSA → Malware-Prüfung → Inhalt an Benutzer.
- *(Ergänzung)* Einbindung explizit (Browser/PAC/WPAD zeigt auf Proxy) oder transparent (WCCP-Umleitung durch Router/Switch/Firewall).

### Cisco Umbrella *(Ergänzung)*
- DNS-Layer Security in der Cloud: Blockiert Anfragen zu bösartigen Domains (Malware, Phishing, C2-Callbacks) bereits bei der DNS-Auflösung, also bevor eine IP-/TCP-Verbindung entsteht, unabhängig von Port/Protokoll. Erweiterbar zum Secure Internet Gateway (SIG, Cloud-Proxy/Firewall).

---

## 5. Logging, Syslog und SIEM (S. 318)

- Logging nötig für Troubleshooting, Policy-Compliance-Auditing, Erkennung beginnender/laufender Angriffe und als Audit Trail für Forensik.
- Alle Cisco Security-Geräte loggen: Firewall (erlaubte/blockierte Verbindungen mit Grund), VPN (erfolgreiche/fehlgeschlagene Logins), IPS (Alarme), Content Security (erlaubte/abgelehnte Requests mit Grund).
- Ziele für Logmeldungen: Console, Monitor (vty), Memory Buffer, Syslog-Server, SNMP Trap, Flash.
- Syslog: Meldungen an einen zentralen Syslog-Daemon → Aggregation, geschützte Langzeitspeicherung.
- Beispiel ASA: `%ASA-6-302016: Teardown UDP connection ... duration 0:02:01 bytes 313` → Plattform ASA, Severity 6 (informational), Message-ID 302016 (UDP-Verbindung beendet).
- **SIEM** (Security Information and Event Management): sammelt, normalisiert und korreliert Logs vieler Quellen, Echtzeit-Analyse von Security-Alerts. *(Ergänzung)* Voraussetzung für Korrelation: synchrone Uhren (NTP) und Zeitstempel in den Logs. SOAR automatisiert die Reaktion; Cisco XDR korreliert Telemetrie mehrerer Security-Produkte (Nachfolger von SecureX).

---

## 6. Endpoint Security (S. 319–321)

- Endpoint Security = Schutz von Desktop, Laptop, Tablet, Smartphone (auch Drucker) + Verifikation von Benutzer, Gerät und Gerätezustand.
- Klassische Einzelprodukte (Personal Firewall, Antivirus, Antispyware) reichen gegen gezielte, persistente Angriffe nicht mehr; nötig ist Advanced Malware Protection als kontinuierlicher Prozess: erkennen, bestätigen, verfolgen, analysieren, beheben – vor, während und nach einem Angriff.
- Studien zur AV-Effektivität: 5 % bis 90 % je nach Studienbedingungen → man muss davon ausgehen, dass Malware ins Netz gelangt.

### Personal Firewall (S. 320)
- Schützt einen einzelnen Host (traditionelle Firewall: Traffic zwischen Netzen an Policy Enforcement Points). Heute in die Betriebssysteme integriert.
- **Distributed Firewall:** flächendeckende Personal Firewalls, deren Policies zentral verwaltet werden → ähnlicher Schutz wie eine traditionelle Firewall.
- Wichtig für mobile Geräte (Hotel, Flughafen, Café, Homeoffice) und bei **Split Tunneling** im Remote-Access-VPN: Internet-Traffic außerhalb des Tunnels → ein Angreifer könnte eine Backdoor auf dem Client nutzen und über dessen Tunnel ins interne Netz gelangen.
- Funktionen: Port-/Protokoll-Regeln, anwendungsbasierte Allow-/Block-Listen (Rückfrage beim Benutzer bei neuen Anwendungen), Netzwerkprofile (work/home/public).

### Antivirus und Antispyware (S. 321)
- Erkennen auch Keylogger, Backdoors, Rootkits, Browser Hijacker, Trojaner, Ransomware. Malware nimmt zu, Effektivität von AV sinkt.
- **Signature-based:** Datenbank mit Merkmalen bekannter Malware; versagt bei Zero-Day-Angriffen.
- **Heuristics:** unscharfe Treffer, erkennt Varianten/Familien mutierender Malware.
- **Behavioral-based:** überwacht Prozessverhalten (z. B. Veränderung anderer Executables, Keylogging) → gewisser Zero-Day-Schutz.
- Datenbanken aktuell halten (Auto-Update). **Real-time protection:** prüft Daten beim Laden in den Arbeitsspeicher (USB-Autostart, E-Mail öffnen, Web-Transaktion), nicht nur geplante Scans.
- Spyware sammelt unbemerkt Informationen (oft Tracking-Cookies); Keylogger gelten als Malware. Adware ist legitim, solange der Benutzer zustimmt und weiß, was er eintauscht; verdeckt → Spyware; Tracking-Daten für Phishing → Malware. AV und Antispyware überschneiden sich.

---

## 7. Centralized Endpoint Policy Enforcement – Posture (S. 322)

- Anforderungen an Endpoint-Schutz gehören in die Security Policy; idealerweise beim Netzzugang durchgesetzt.
- Kurs: AnyConnect Secure Mobility Client 4.0 (heute **Cisco Secure Client**) mit Modulen: VPN (SSL/IPsec IKEv2), Network Access Manager (802.1X-Supplicant), ISE Posture, Web Security u. a.; Plattformen Windows, macOS, Linux, iOS, Android.
- **ISE Posture Module:** für interne Endpunkte (wired/wireless). **Client-side evaluation**: Client erhält Posture-Anforderungen von ISE, sammelt Daten, vergleicht selbst und meldet das Ergebnis an ISE.
- **ASA Posture Module** (HostScan, heute Secure Firewall Posture): für Remote-Access-VPN. **Server-side evaluation**: ASA fragt nur Attribute ab, bewertet selbst (DAP) und entscheidet über den VPN-Zugang.
- Beide prüfen OS-Version, Antivirus, Antispyware; laut Kurs prüft nur das ASA-Modul zusätzlich die Personal Firewall (siehe Fehlerabschnitt: aktuelle ISE-Versionen kennen Firewall-Conditions).
- Remediation ASA: nur mit bereits installierter Software (deaktivierte Software aktivieren, AV/AS-Updates erzwingen, Firewall-Policy pushen); erfordert Advanced Endpoint Assessment License.
- Remediation ISE: **Quarantäne** – stark eingeschränkter Zugang (nur zu Remediation-Servern), nach Installation erneuter Posture-Check, bei Compliance normaler Zugang (per CoA).
- *(Ergänzung)* ISE-Posture-Status: Unknown, Compliant, NonCompliant. Typischer Ablauf: Auth → Autorisierung „Posture unknown“ mit Redirect-ACL + dACL → Posture-Check → CoA → Vollzugang.

---

## 8. Cisco Secure Endpoint (Kurs: AMP for Endpoints, S. 323)

- Annahme: Malware gelangt irgendwann ins Netz (Kurs: selbst die besten Produkte erkennen realistisch ~40 %). Schutz entlang des Attack Continuum: before, during, after.
- Telemetriemodell mit Big Data, kontinuierlicher Analyse, Advanced Analytics; Endpunkte: PCs, Macs, Mobilgeräte, virtuelle Systeme.
- Cloud-basierte Erkennung (Kurs: Collective Security Intelligence Cloud): schnelle Erkennung bekannter Malware (Hash-Lookup), Cloud-Ressourcen für Dateien mit unbekannter Disposition, Machine Learning.
- **File Trajectory:** auf welchen Hosts eine Datei gesehen wurde. **Device Trajectory:** welche Aktionen Dateien auf einem bestimmten Host ausgeführt haben (Root-Cause-Analyse).
- Blockieren bösartiger Netzwerkverbindungen: Security Intelligence Feeds (IP-Reputation), Custom IP Block Lists.
- **Retrospective alerting / Cloud recall:** Disposition einer Datei wechselt nachträglich von unknown zu malicious → Cloud alarmiert alle Systeme, auf denen die Datei gesehen wurde, und stellt sie unter Quarantäne.
- Simple Custom Detections (Hash-Listen) und Advanced Custom Detections (eigene Signaturen); Gruppen mit unterschiedlichen Policies; Reporting.
- Engines: **Spero** = Machine-Learning-Engine in der Cloud, nutzt einen Fingerprint mit vielen Dateiattributen (gesendet zusammen mit dem SHA-256-Hash). **Ethos** = „fuzzy“ Erkennung (Fuzzy Fingerprinting) für Varianten, wird bei unbekannter/neutraler Disposition genutzt.
- Komponenten: Cloud, Connector (auf dem Endpunkt; sendet Datei-Infos, erhält Disposition), Mobile-App (Kurs: nur Android), Mac Connector, AMP for Networks (Firepower fragt Disposition für Dateien im Netzverkehr ab).
- Connector-Vergleich laut Kurs: Windows: SHA-256-Check, Spero, Ethos, Advanced Analytics, Quarantäne; File/Device Trajectory, File Analytics; Simple + Advanced Custom Detection, Application Blocking, IP Block Lists. Mac: SHA-256, AV-Signaturen, Analytics, Quarantäne; Trajectory; Simple Custom Detection, App Blocking, IP Block Lists. Mobile: SHA-1-Check, Post-Installation Detection; Simple Custom Detection.
- Rolle der Cloud: Detection Publishing (Signaturen in der Cloud → kleiner Connector, Custom Signatures werden gepusht), Big-Data-Verarbeitung, Entscheidungen in Echtzeit (geringe Latenz), Reporting.
- *(Ergänzung)* Sandboxing unbekannter Dateien: Cisco Secure Malware Analytics (ehemals Threat Grid).

---

## 9. Firewall-Konzepte und Cisco Secure Firewall (S. 324)

- Firewall = System, das eine Access-Control-Policy zwischen zwei oder mehr Security Zones durchsetzt (Klassifizieren → Weiterleiten oder Verwerfen).
- Grundanforderungen: (1) selbst angriffsresistent, (2) einziger Transitpunkt zwischen Zonen (keine Backdoor-Pfade), (3) Traffic-Filterung; die Policy folgt der zentralen Security Policy, nicht der Laune des Admins.
- Typische Orte: Internet Edge (stark exponiert), Data Center (auch interne Bedrohungen). Weitere Dienste: NAT, mehrere Zonen, VPN-Terminierung.
- Implementierungsformen: Paketfilter auf Routern/Switches, dedizierte Appliances, komplexe Systeme mit IPS, Application Awareness und Content Security.
- **Drei-Zonen-Modell:** Inside (privat, vertrauenswürdig), Outside (Internet, nicht vertrauenswürdig), DMZ (öffentlich erreichbare Server). Typische Policy: Outside→Inside verboten; Inside→Outside meist erlaubt (ggf. Protokolle eingeschränkt); Outside→DMZ nur definierte Ports auf definierten Servern; DMZ→andere Zonen sehr restriktiv (kein Sprungbrett).
- Schutzwirkungen: weniger Exposition sensibler Hosts; Schutz vor Protokollmissbrauch (Fragmentierung, TCP-State, Application-Layer-Konformität, malformed Packets).
- Grenzen: Fehlkonfiguration/Hardwareausfall katastrophal (→ HA), Performance-Engpass (richtig dimensionieren), keine Kontrolle über umgehende Pfade (offenes WLAN, Mobilfunk, USB), Benutzer umgehen als „oppressiv“ empfundene Policies, Angriffe innerhalb einer Zone (Ausnahmen: VLAN ACLs, zentral verwaltete Host-Firewalls).

### Stateless vs. Stateful *(Ergänzung, Kurs streift nur „connection state flows at the TCP layer“)*
| | Stateless (Paketfilter, ACL) | Stateful |
|---|---|---|
| Entscheidung | jedes Paket einzeln (IP, Protokoll, Ports, Flags) | anhand einer Verbindungstabelle (State Table) |
| Rückverkehr | eigene Regel nötig (z. B. Ephemeral Ports oder `established`) | automatisch erlaubt, wenn zur bekannten Verbindung gehörig |
| Schwächen | spoofbare Flags, große Regelwerke | Ressourcenverbrauch der State Table |

- ASA *(Ergänzung)*: Security Levels 0–100 (inside 100, outside 0); Traffic von höher nach niedriger standardmäßig erlaubt, Rückverkehr per Stateful Inspection; gleiche Levels standardmäßig blockiert (`same-security-traffic permit inter-interface`).
- IOS Zone-Based Policy Firewall (ZBFW) *(Ergänzung)*: Interfaces werden Zonen zugeordnet; Traffic zwischen Zonen nur per zone-pair mit Inspect-Policy; innerhalb derselben Zone frei; zwischen Zonen-Interface und Nicht-Zonen-Interface verworfen; Self-Zone = Router selbst (standardmäßig alles erlaubt).

```
zone security INSIDE
zone security OUTSIDE
class-map type inspect match-any WEB
 match protocol http
 match protocol https
policy-map type inspect IN-OUT
 class type inspect WEB
  inspect
 class class-default
  drop
zone-pair security IN-OUT source INSIDE destination OUTSIDE
 service-policy type inspect IN-OUT
interface Gi0/0
 zone-member security INSIDE
```

### Cisco Secure Firewall (früher „Cisco NGFW“/Firepower)
Zusätzlich zu First-Generation-Funktionen: integrierter Threat- und Malware-Schutz, Policies auf Basis von Anwendungen statt Ports, URL-Filtering, Indications of Compromise (IoC), umfassende Sichtbarkeit, weniger Komplexität, Integration mit anderen Security-Lösungen.
- **URL Filtering:** Proxy-Funktion in der Firewall, URL-Kategorien und Reputation-Scores.
- **Application Visibility and Control (AVC):** erkennt Anwendungen am Datenstrom statt an Portnummern (porthoppende Apps wie Skype; Teilfunktionen wie Spiele in Facebook).
- **Context Awareness:** wer, worauf, von wo, mit welchem Gerät, wann (z. B. Marketing darf Facebook, aber keine Facebook-Spiele; Firmenlaptop vs. Privathandy).
- **IPS** integriert, verstärkt durch Kontext. **Advanced Malware Protection** (heute Malware Defense): Erkennung, Blockierung, Tracking, Analyse, Remediation.
- *(Ergänzung)* Software: Secure Firewall Threat Defense (FTD) mit Snort 3, Management über FMC (on-prem), cdFMC (Cloud) oder FDM (lokal). Security Intelligence = Blocklisten für IP/URL/DNS auf Basis von Talos-Feeds. TLS-Decryption-Policy für Inspektion verschlüsselter Verbindungen. Benutzeridentität z. B. über ISE/pxGrid.
- *(Ergänzung)* Encrypted Traffic Analytics (ETA): Catalyst-Switches exportieren erweiterte NetFlow-Daten (Initial Data Packet, Sequence of Packet Lengths and Times), Secure Network Analytics erkennt damit Malware in verschlüsseltem Traffic ohne Entschlüsselung (Topic 5.4.a).

---

## 10. Cisco TrustSec (S. 325)

- Problem klassischer Security: Policies hängen an L3-Adressen/VLANs/Topologie. TrustSec nutzt stattdessen die **Identität/Rolle** (Kontext: Benutzer, Gerätetyp, Posture, Ort) → konsistente Policies über wired, wireless, VPN, auch wenn Ressourcen umziehen.
- TrustSec umfasst SGTs und MACsec. Funktionen in Switches, Routern, WLCs und Firewalls; Support stark plattform-/versionsabhängig → früh im Design prüfen.

### Drei Funktionsbereiche
1. **Classification** (Zuweisung SGT ↔ IP): **dynamisch** am Access Layer über 802.1X, MAB oder WebAuth (ISE schickt SGT im Authorization-Ergebnis, als Permission zusätzlich zu oder statt einem Authorization Profile); **statisch** meist im Data Center (IP/Subnetz→SGT, VLAN→SGT, Port→SGT; lokal auf dem NAD oder zentral in ISE, NAD lädt die Mappings herunter).
2. **Transport/Propagation:** **Inline Tagging** – SGT im Ethernet-Header (Cisco Meta Data, CMD, EtherType 0x8909, 16-Bit-SGT-Feld; Kurs: ca. 20 Byte Overhead) zwischen fähigen Geräten; Sender setzt das Tag beim Egress, Empfänger liest es beim Ingress. **SXP** (SGT Exchange Protocol) – überträgt IP-to-SGT-Bindings über Geräte ohne Inline-Tagging-Hardware *(Ergänzung: TCP 64999, Rollen Speaker/Listener)*.
3. **Enforcement:** permit/deny auf Basis von Source- und Destination-SGT: **SGACL** auf Switches, **SGFW** (Security Group Firewall) auf Routern (IOS ZBFW ab 15.2, `match security-group` in class-maps) und Firewalls (ASA ab 9.0, ACEs mit SGT/Security-Group-Namen; benötigt Security-Group-Tabelle und IP-SGT-Mapping). SGFW-Policy wird lokal auf dem Gerät gepflegt, SGACL-Policy zentral in ISE.

- **SGT:** eindeutiges 16-Bit-Tag = Rolle/Privileg der Quelle. Das Paket trägt nur das **Source-SGT**; das Destination-SGT (DGT) wird am Enforcement-Punkt aus der Zieladresse ermittelt (deshalb Enforcement typischerweise am Egress).
- SGACL-Switches können sogar zwischen Hosts im gleichen VLAN filtern.
- **Policy Matrix:** Source-SGT × Destination-SGT; jede Zelle enthält eine geordnete Liste von SGACLs. Die SGACL selbst enthält keine Gruppen und keine IP-Adressen (z. B. `deny tcp dst eq 21`); dieselbe SGACL kann in vielen Zellen stehen. Neue Gruppe → Matrix wächst um eine Zeile und eine Spalte; Policy zentral in ISE, dynamisch an alle Enforcement-Punkte verteilt.
- Vorteile: weniger ACEs (Anzahl hängt von der Zahl der Berechtigungen ab, nicht von IP-Bereichen), nur eine Kopie je SGACL im TCAM, topologieunabhängig, einfache Wartung.
- MACsec + Inline-SGT: Tag liegt im verschlüsselten/authentisierten Teil; Overhead 802.1AE + CMD ca. 40 Byte (MTU beachten).

```
! (Ergänzung) Beispiele IOS XE
cts role-based enforcement                       ! SGACL-Enforcement global aktivieren
cts role-based sgt-map 10.1.50.10 sgt 100        ! statisches IP-SGT-Mapping
interface Gi1/0/48
 cts manual
  policy static sgt 2 trusted                    ! Inline-Tagging auf Uplink
cts sxp enable
show cts role-based sgt-map all
show cts role-based permissions
```

---

## 11. MACsec (S. 326)

- IEEE **802.1AE**, Layer-2-**hop-by-hop**-Verschlüsselung: Vertraulichkeit und Integrität (*Ergänzung:* plus Replay-Schutz über Packet Number) auf kabelgebundenen Links; jedes Gerät auf dem Pfad entschlüsselt und verschlüsselt neu (Inspektion im Gerät möglich).
- Frame: DMAC | SMAC | **SecTAG** (802.1AE-Header: EtherType 0x88E5, TCI/AN, SL, Packet Number, optional SCI) | [802.1Q | CMD | EtherType | Payload verschlüsselt] | **ICV** | CRC. Authentisiert wird der Bereich von DMAC bis vor ICV, verschlüsselt ab nach dem SecTAG. MAC-Adressen bleiben im Klartext.
- Schlüssel kommen out-of-band über **MKA** (MACsec Key Agreement, definiert in IEEE 802.1X-2010; Kurs: „802.1x-REV“). MKA-Nachrichten = **MKPDUs** in EAPOL-Frames.
- Host-facing Links (Switch ↔ PC/Telefon) nur mit MKA. *(Ergänzung)* Switch-zu-Switch: MKA mit PSK oder 802.1X, oder Cisco-proprietär SAP (Security Association Protocol, `cts manual`/`sap`).
- Ablauf (Downlink): 802.1X-EAP-Authentisierung erzeugt die **MSK** → daraus **CAK** (Connectivity Association Key) und CKN (Name, aus der EAP-Session-ID) → Switch (Authenticator) ist **Key Server**, wählt Cipher Suite und erzeugt eine zufällige 128-Bit-**SAK** (Secure Association Key) → sendet sie mit AES Key Wrap (RFC 3394) verschlüsselt mit CAK-abgeleiteten Schlüsseln an den Client. Der Client ist nie Key Server und spricht nur mit einer MKA-Instanz.
- Default Cipher Suite: **GCM-AES-128** (*Ergänzung:* GCM-AES-256 und XPN-Varianten konfigurierbar).
- Policy am Port: Switch akzeptiert je nach Policy nur MACsec oder auch unverschlüsselte Frames (*Ergänzung:* `authentication linksec policy must-secure | should-secure | must-not-secure`).
- ICV-Prüfung: Switch berechnet ICV mit SAK; stimmt sie nicht → Frame wird verworfen. (Kurs formuliert ungenau „ICV encrypts“ – ICV sichert Integrität, verschlüsselt nicht.)
- MKA-Timer: MKPDUs alle **2 s** (Hello); nach **6 s** ohne MKPDU gilt die Session als beendet (relevant z. B. bei PC hinter IP-Telefon, wenn der Link am Switch nicht down geht).
- *(Ergänzung)* EAP-Methode muss Schlüsselmaterial (MSK) liefern, z. B. EAP-TLS, PEAP, EAP-FAST; EAP-MD5 liefert keine Schlüssel → kein MACsec. Key-Server-Auswahl bei MKA-PSK: niedrigster `key-server priority`-Wert gewinnt (Default 0), bei Gleichstand niedrigste SCI.

```
! (Ergänzung) Switch-zu-Switch MACsec mit MKA-PSK
key chain KC macsec
 key 01
  cryptographic-algorithm aes-128-cmac
  key-string <32 Hex-Zeichen bei aes-128-cmac, 64 bei aes-256-cmac>
mka policy MKA-POL
 macsec-cipher-suite gcm-aes-128
interface Te1/0/1
 macsec network-link
 mka policy MKA-POL
 mka pre-shared-key key-chain KC
show mka sessions          ! Status "Secured"
show macsec summary
```

---

## 12. Identity Management mit Cisco ISE / IBNS (S. 327)

- **Cisco IBNS** (Identity-Based Networking Services): Architektur aus Catalyst-Switches, WLCs und ISE – starke Authentisierung (802.1X, MAB, WebAuth), Policy-basierte Autorisierung (dACL, VLAN), breite Supplicant-Unterstützung (native OS-Supplicants, Cisco-Supplicant, Open Source unter Linux).
- Grundlage: IEEE 802.1X, portbasiert (Switchport oder WLAN am WLC). Geräte ohne Supplicant → MAB oder WebAuth (Gäste, Drucker, IP-Kameras). WLAN-Benutzer erwarten Authentisierung → gute Kandidaten für den Start.
- **Phasenweise Einführung (Deployment Modes):**

| Mode | vor Auth / bei Fehlschlag | nach erfolgreicher Auth |
|---|---|---|
| Monitor (Open) | voller Zugang, alles wird geloggt (Audit) | Autorisierung (VLAN/dACL) wird angewendet |
| Low-Impact | selektiver Zugang per statischer Port-ACL (z. B. DHCP, DNS) | dACL ersetzt/überschreibt die Port-ACL |
| High-Security (Closed) | kein Traffic (außer EAPOL) | Zugang gemäß Autorisierung |

- WLAN mit 802.1X ist binär: ohne Auth kein Zugang.
- *(Ergänzung)* Monitor/Low-Impact nutzen `authentication open` am Port. ISE-Personas: PAN (Administration), MnT (Monitoring & Troubleshooting), PSN (Policy Service – beantwortet RADIUS, hostet Portale), pxGrid (Kontextaustausch). ISE-Profiling ermittelt den Gerätetyp über Probes (RADIUS, DHCP, HTTP, SNMP, NetFlow, NMAP u. a.).

---

## 13. 802.1X für wired und wireless (S. 328)

### Rollen
- **Supplicant:** 802.1X-Software auf dem Endpunkt, fordert Zugang an.
- **Authenticator (NAD):** Switch/WLC, kontrolliert den Port, Proxy zwischen Supplicant (EAPOL) und Server (RADIUS), ist RADIUS-Client.
- **Authentication Server:** prüft die Identität (Cisco ISE; ggf. mit AD/LDAP/CA als Identity Store), teilt dem NAD das Ergebnis mit; für den Client transparent.
- Der Switch entfernt den Ethernet-Header des EAPOL-Frames und kapselt EAP unverändert in RADIUS (EAP-Message-Attribut); umgekehrt RADIUS → EAPOL. Der Server muss EAP nativ verstehen.
- *(Ergänzung)* EAPOL: EtherType 0x888E, Zieladresse 01:80:C2:00:00:03 (PAE group address); Typen EAP-Packet, EAPOL-Start, EAPOL-Logoff, EAPOL-Key (und MKA bei 802.1X-2010).

### Ablauf
1. Beginning: Authenticator sendet EAP-Request/Identity bei Link-up und periodisch, solange der Port unauthentisiert ist; Supplicant kann selbst mit **EAPOL-Start** beginnen.
2. Middle: EAP-Response/Identity → RADIUS Access-Request; Challenges (EAP-Request ↔ Access-Challenge) je nach EAP-Methode.
3. End: RADIUS Access-Accept → EAP-Success → **Port authorized**; EAPOL-Logoff → Port unauthorized.
- Ist 802.1X am NAD nicht aktiv, werden EAPOL-Frames verworfen; erhält der Supplicant nach drei Versuchen keine Antwort, sendet er so, als sei der Port autorisiert.

### EAP-Methoden *(Ergänzung)*
| Methode | Server-Zertifikat | Client-Credential | Hinweis |
|---|---|---|---|
| EAP-TLS | ja | Client-Zertifikat | stärkste, gegenseitige Zertifikatsauthentisierung |
| PEAP (EAP-MSCHAPv2) | ja | Benutzername/Passwort im TLS-Tunnel | sehr verbreitet |
| EAP-FAST | optional (PAC) | Passwort oder Zertifikat im Tunnel | Cisco-Entwicklung |
| EAP-TTLS | ja | diverse innere Methoden | |
| TEAP | ja | EAP-Chaining (Maschine + Benutzer) | RFC 7170 |
| EAP-MD5 | nein | Passwort-Hash | keine gegenseitige Auth, keine Schlüssel → nicht für WLAN/MACsec |

### Autorisierungsergebnisse
- **VLAN Assignment:** dynamisches VLAN im Access-Accept (*Ergänzung:* Tunnel-Type=VLAN(13), Tunnel-Medium-Type=802(6), Tunnel-Private-Group-ID=VLAN). Kann auch bei Fehlschlag ein Gast-VLAN zuweisen – dann zentral geloggt; sonst Access-Reject und lokales Guest-/Restricted-VLAN ohne zentralen Audit Trail. Default VLAN = am Port/SSID konfiguriert, falls nichts zugewiesen wird.
- **ACL Assignment:** **dACL** (in ISE definiert, per RADIUS heruntergeladen, VSA `ip:inacl#<n>=...`, nicht in der Running-Config, wird bei Session-Ende/Auth-Fehler/Link-down entfernt) bzw. **Named ACL** (lokal auf dem WLC/Switch definiert, ISE nennt nur den Namen – muss exakt übereinstimmen; *Ergänzung:* Switch per Filter-Id, WLC per Airespace-ACL-Name).
- Time-based Access, Security Group Access (SGT).

### Host Modes
| Mode | Verhalten |
|---|---|
| single-host | genau ein MAC am Port; weiterer MAC → Security Violation |
| multi-host | erster Client authentisiert, alle weiteren hängen sich daran (keine eigene Auth) |
| multi-domain (MDA) | je ein Gerät in der Voice-Domain (IP-Telefon) und der Data-Domain (PC), unabhängig per 802.1X/MAB (Host auch WebAuth) |
| multi-auth | ein Gerät in Voice, beliebig viele einzeln authentisierte Geräte in Data |

*(Ergänzung)* Telefon wird über das AV-Pair `device-traffic-class=voice` der Voice-Domain zugeordnet.

### Change of Authorization (CoA)
- RADIUS CoA (RFC 5176) ändert eine bestehende Session dynamisch (neu authentisieren, Port bouncen, Session beenden). Beispiel Posture: zunächst eingeschränkte Autorisierung mit Redirect + dACL → Compliance festgestellt → CoA → erweiterte dACL.
- *(Ergänzung)* Switch-Seite: `aaa server radius dynamic-author` mit `client <ISE-IP> server-key <key>`.

### Implementierungsregeln
- Unterstützt auf statischen Layer-2-Access-Ports (inkl. Voice-VLAN), laut Kurs auch auf Routed Ports. **Nicht** auf Trunk-Ports, dynamischen Ports (DTP), Dynamic-Access-Ports (VQP), EtherChannel-Mitgliedern.

```
! (Ergänzung) Basiskonfiguration IOS XE (klassischer Stil)
aaa new-model
aaa authentication dot1x default group radius
aaa authorization network default group radius
aaa accounting dot1x default start-stop group radius
dot1x system-auth-control
interface Gi1/0/10
 switchport mode access
 switchport access vlan 10
 switchport voice vlan 20
 authentication host-mode multi-domain
 authentication order dot1x mab
 authentication priority dot1x mab
 authentication port-control auto
 mab
 dot1x pae authenticator
 dot1x timeout tx-period 10
show authentication sessions interface Gi1/0/10 details
```

Beispiel-Ausgabe (gekürzt, eigenes Beispiel):
```
Interface:  GigabitEthernet1/0/10
MAC Address:  0050.5688.1a2b
Status:  Authorized
Domain:  DATA
Method status list:
   Method    State
   dot1x     Authc Success
```
*(Ergänzung)* Bei MAB-Fallback zeigt die Method status list `dot1x Failed over` und `mab Authc Success` („Failed over“ = Methode lief, scheiterte und übergab an die nächste Methode).

---

## 14. MAC Authentication Bypass – MAB (S. 329)

- Alternative für Geräte ohne 802.1X (Drucker, Kameras, IoT). MAC-Adresse dient als Benutzername **und** Passwort. Keine echte Authentisierung/Verschlüsselung, leicht spoofbar, schwächer – aber erster Schritt zur Geräteidentifikation.
- Vorteile: Visibility (IP, MAC, Switch, Port verknüpft), identitätsbasierte Dienste (VLAN, dACL wie bei 802.1X), Zugangskontrolle an der Edge (L2), Fallback oder Standalone, Geräteauthentisierung ohne Benutzer.
- Grenzen: braucht eine gepflegte MAC-Datenbank (größte Herausforderung), Verzögerung als 802.1X-Fallback (wartet auf 802.1X-Timeout, solange kein Zugang), keine Benutzerauthentisierung, schwache Authentisierung (MAC-Spoofing).
- Verhalten: Vor MAB ist alles blockiert; der Switch lernt die Quell-MAC aus einem einzigen Frame, authentisiert sie; danach Traffic erlaubt, mit Source-MAC-Filterung (nur diese MAC darf senden).
- *(Ergänzung)* Access-Request mit Service-Type = Call-Check (daran erkennt ISE MAB). Default-Timer: `dot1x timeout tx-period` 30 s, `dot1x max-reauth-req` 2 → MAB startet nach (2+1)×30 = 90 s. Abhilfe: tx-period verkleinern oder `authentication order mab dot1x` + `authentication priority dot1x mab`. ISE-Option „If user not found: Continue“ erlaubt unbekannten MACs z. B. einen Gast-Redirect.

---

## 15. Web Authentication (S. 330)

- Für Gäste, Contractors oder Mitarbeiter ohne (funktionierenden) Supplicant oder ohne Konto im Identity Store; „Methode der letzten Wahl“ nach 802.1X/MAB. Wired und wireless.
- Zwei Autorisierungsstufen: (1) initial eingeschränkt – nur WebAuth-Traffic erlaubt, HTTP(S) wird zum Portal umgeleitet (dACL/VLAN auf Switch, Named ACL auf WLC); (2) nach erfolgreichem Login passendes Autorisierungsprofil.
- Benutzer muss eine per DNS auflösbare HTTP(S)-Seite aufrufen; der NAD fängt den Request ab und leitet um.

| Szenario | Pro | Contra |
|---|---|---|
| Central WebAuth (CWA) | wired + wireless; Portal auf ISE (PSN); Auth auf ISE; CoA nach Login | stabile Verbindung NAD↔ISE nötig |
| Local WebAuth (LWA, WLC oder Switch) | NAD stellt Web-Dienst; Auth näher am Client | kein CoA, kein zentraler Audit Trail, Portal-Konfiguration auf jedem Switch |
| Device Registration WebAuth | wired + wireless; Onboarding; kein Benutzerlogin nötig (AUP) | ISE muss immer erreichbar sein |

- Kursvarianten: NAD mit CWA (Redirect zu ISE, CoA); WLC mit LWA (WLC → ISE-Guest-Portal mit Login + AUP → Browser zurück zum WLC → WLC authentisiert per RADIUS → Weiterleitung zur Ursprungsseite); Wired NAD mit LWA (Portal postet HTTPS-URL mit Credentials an den Switch, der per RADIUS gegen ISE prüft); Device Registration (MAB → unbekannte MAC → ISE antwortet mit URL-Redirect-Profil → AUP-Seite).
- *(Ergänzung)* CWA-Ablauf im Detail: MAB schlägt „fehl“ bzw. unbekannter Endpunkt → ISE schickt Access-Accept mit `url-redirect` und `url-redirect-acl` → Benutzer loggt sich auf dem ISE-Portal ein → ISE sendet CoA (Reauthenticate) → erneute MAB-Anfrage wird jetzt als Guest-Flow erkannt → Vollzugang. Auf Catalyst-Switches bedeutet in der Redirect-ACL `permit` = „umleiten“ und `deny` = „nicht umleiten“; für das Abfangen muss der HTTP(S)-Server des Switches laufen (`ip http server`/`ip http secure-server`). Gastportal-Typen in ISE: Hotspot (nur AUP), Self-Registered, Sponsored.

### Gesamt-Reihenfolge
Standard: **802.1X → MAB → WebAuth** (stärkste Methode zuerst; WebAuth als letzte Rückfallebene). Mit `authentication order` die Reihenfolge der Versuche, mit `authentication priority` die Rangfolge, welche Methode eine laufende niedrigere unterbrechen darf.

---

## Fehler/Ungenauigkeiten im Kurs

1. **Veraltete Produktnamen** (AMP for Endpoints, Firepower, FireSIGHT, ESA, WSA, AnyConnect 4.0, Collective Security Intelligence Cloud). Korrekt: Cisco Secure Endpoint, Secure Firewall (FTD/FMC), Secure Email Gateway, Secure Web Appliance, Secure Client. Quelle: cisco.com Produktseiten (Rebranding 2020–2023). SecureX wurde zum 31.07.2024 abgekündigt, Nachfolger Cisco XDR.
2. **S. 317 Content Security:** „ASA intercepts the email and forwards it to the ESA“ ist vereinfacht. Das Gateway ist selbst MTA; der MX-Record zeigt auf das Gateway, die Firewall lässt SMTP nur durch bzw. NATet dorthin. Quelle: Cisco Secure Email Gateway User Guide (Deployment).
3. **S. 323 Secure Endpoint:** Plattformangaben (Mobile nur Android ab 2.1, Mac ab OS X 10.7) sind historisch; „40 % Erkennungsrate“ ist eine Kursbehauptung ohne Quelle. Ethos wird von Cisco als „Fuzzy Fingerprinting“-Engine beschrieben, nicht als „fuzzy logic“.
4. **S. 322 Posture:** Aussage, nur das ASA-Modul prüfe Personal Firewalls, ist veraltet – ISE (ab 2.x) kennt Firewall-Conditions im Posture. AnyConnect 4.0 ist durch Secure Client 5.x ersetzt; „Advanced Endpoint Assessment License“ ist ein ASA-Altlizenzbegriff.
5. **S. 326 MACsec:** „An ICV encrypts and protects MACsec frames“ – die ICV verschlüsselt nicht, sie sichert Integrität/Authentizität. MKA ist in IEEE 802.1X-2010 definiert (Kurs: „802.1x-REV“). „Host-facing links can only be secured using MKA“ stimmt, Switch-zu-Switch-Links können zusätzlich SAP (Cisco) nutzen.
6. **S. 325 TrustSec:** „about 20 bytes of overhead“ für CMD ist eine Kursangabe; Cisco beziffert das CMD mit SGT-Option kleiner (die genaue Größe hängt von Optionen ab). Für Prüfungsfragen nicht verwenden.
7. **S. 328 802.1X:** „Single host mode: if the client leaves, the switch changes the port link state to down“ ist missverständlich – die Session wird beendet und der Port kehrt in den unautorisierten Zustand zurück, der physische Link geht nicht zwingend down.
8. **S. 316 VPN:** RFC 2828 ist durch RFC 4949 ersetzt.

## Bilder

- `bilder/29-security-arch/01-ids-ips.svg` – IDS (promiscuous über SPAN-Kopie) vs. IPS (inline) mit Folgen für das erste bösartige Paket und Latenz.
- `bilder/29-security-arch/02-fw-zonen.svg` – Drei-Zonen-Modell Inside/Outside/DMZ mit typischen erlaubten und verbotenen Richtungen.
- `bilder/29-security-arch/03-content-sec.svg` – Secure Email Gateway (eingehende Mail) und Secure Web Appliance (Proxy-Ablauf erlaubt/blockiert).
- `bilder/29-security-arch/04-trustsec-3.svg` – TrustSec: Classification am Ingress, Transport (Inline/SXP), Enforcement am Egress mit SGACL.
- `bilder/29-security-arch/05-sgacl-mat.svg` – SGACL-Policy-Matrix (Source × Destination SGT) mit wiederverwendeter SGACL.
- `bilder/29-security-arch/06-macsec-frm.svg` – MACsec-Frame mit SecTAG, verschlüsseltem Bereich, ICV sowie MKA-Schlüsselkette MSK→CAK→SAK.
- `bilder/29-security-arch/07-dot1x-flow.svg` – 802.1X-Rollen und Nachrichtenfluss EAPOL ↔ RADIUS bis Port Authorized.
- `bilder/29-security-arch/08-fallback.svg` – Reihenfolge 802.1X → MAB → WebAuth mit Default-Timern (90 s) und Einsatzfällen.
- `bilder/29-security-arch/09-cwa-ablauf.svg` – Central WebAuth: MAB, Redirect, Portal-Login, CoA, Vollzugang.
