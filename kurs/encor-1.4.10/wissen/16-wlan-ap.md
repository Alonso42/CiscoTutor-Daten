# Examining Wireless AP Operation

Quelle: ENCOR 1.4.10 Student Guide, Seiten 160–165 (Intro 159, Summary Challenge 166 und Answer Key 167 nicht verwendet)

Topics: ENCOR-LEGACY-WLAN (Wireless ist im ENCOR-Blueprint v1.2 kein eigenes Prüfungsthema mehr; AP-Discovery, AP-Modi und WLC-Redundanz sind zugleich CCNA-Grundlagen)

> Aktualitätshinweis: Der Kurs beschreibt das Verhalten weitgehend mit AireOS-Begriffen (Master Controller, HA-SKU, 5508, Release 7.5, Rogue Detector Mode, Cisco Spectrum Expert). Referenzplattform heute ist der **Catalyst 9800** (IOS XE). Unterschiede sind unten jeweils als *9800* bzw. *AireOS (Legacy)* markiert. Bereits in Kapitel 15 behandelt (hier nur vertieft): CAPWAP-Ports 5246/5247, Option-43-Hex-Format, DNS-Name, `capwap ap primary-base`, SSO-Grundidee, Grundzuordnung der Modi Local/FlexConnect/Monitor/Sniffer, FlexConnect Standalone-Grundverhalten.

## Universal AP Priming

- Die **Regulatory Domain** und das **Country** eines AP legen fest, welche Kanäle und Sendeleistungen erlaubt sind.
- Klassische APs haben eine feste, ab Werk eingestellte Regulatory Domain (SKU-Suffix wie -A, -E, -Z …). **Universal APs** (Aironet, Suffix -UX) sind nicht länderspezifisch; ihre Domain wird nach dem Standort gesetzt ("Priming") und kann bei Bedarf neu gesetzt werden.
- **Manuelles Priming:** Smartphone mit der App **Cisco AirProvision** verbindet sich mit der SSID des Universal AP (gleiches WLAN; Kurs: SSID muss **WPA2-PSK** nutzen – Cisco empfiehlt WPA2-PSK, weil manche Android-Plattformen 802.1X dafür nicht unterstützen; das Telefon muss Mobilfunkempfang haben). Die App bestimmt den Standort aus den **GPS-Koordinaten** des Telefons und dem **Mobile Country Code (MCC)** der Mobilfunkmasten und primt den AP.
- **Automatisches Priming:** Ein bereits geprimter AP sendet Domain/Country in einem **verschlüsselten Teil seiner Beacons**; Cisco-proprietäres **NDP (Neighbor Discovery Protocol)**. Nicht geprimte Universal APs in der RF-Nachbarschaft übernehmen die Einstellung.
- Bei Neuinstallationen muss **mindestens ein AP pro RF-Nachbarschaft manuell** geprimt werden; die übrigen können automatisch folgen.
- Ein AP, der bereits für ein **anderes Land** geprimt war, muss **manuell** neu geprimt werden (automatisches Priming überschreibt das nicht; vorher AP zurücksetzen/unprimen). Automatisches Priming funktioniert nur für Lightweight-APs, nicht im Autonomous Mode.
- Ein AP, dessen Country/Regulatory Domain der WLC nicht konfiguriert hat, wird nicht oder ohne aktive Radios betrieben – Country-Code auf dem WLC prüfen ist ein Standard-Troubleshooting-Schritt (allgemeines Wissen).
- Aktuell (allgemeines Wissen): Ciscos Wi-Fi-7-APs (CW917x) sind "Global Use"-APs mit einer SKU weltweit; der Standort wird z. B. über die Cisco-Wireless-App bzw. Ortungsfunktionen bestimmt – gleiche Idee wie Universal Priming.

## Controller Discovery Process

Ein Controller-basierter AP muss einem WLC beitreten (join), bevor er Clients bedient. Ziel der Discovery: **möglichst viele WLCs** finden, um den Primary oder den am wenigsten ausgelasteten WLC wählen zu können.

Voraussetzung: AP hat eine IP-Adresse (statisch oder DHCP). Danach sammelt er WLC-Adressen über:

| Methode | Wie | Bemerkung |
|---|---|---|
| Subnet Broadcast (L2) | CAPWAP Discovery Request als Broadcast im lokalen Subnetz; alle WLCs dort antworten | Endet am Router; per `ip helper-address` + `ip forward-protocol udp 5246` als L3-Discovery weiterleitbar (dann IP/UDP statt MAC-Ziel) |
| Lokal gespeicherte Adressen | Primary/Secondary/Tertiary aus NVRAM (frühere Joins oder manuell, z. B. `capwap ap primary-base`), plus beim Join gelernte **Mobility-Group-Mitglieder** | Bleiben über Reboot erhalten |
| DHCP Vendor Option | IPv4: **Option 43**; IPv6: **DHCPv6 Option 52**; AP schickt im DHCP Discover einen modellabhängigen Vendor Class Identifier (**Option 60**) | WLC-Liste kommt im DHCP ACK; AP sendet dann **Unicast** Discovery Requests an jede Adresse |
| DNS | DHCP liefert **Option 6** (DNS-Server) und **Option 15** (Domain); AP löst `CISCO-CAPWAP-CONTROLLER.<domain>` auf | Mehrere A/AAAA-Records möglich; unterschiedliche Domains pro DHCP-Scope verteilen APs auf verschiedene WLCs |

Option 43 (Cisco, Typ 0xF1): `f1` + Länge (4 × Anzahl WLCs) + IP-Adressen in Hex. Beispiel 1 WLC 192.168.11.5 → `f104c0a80b05`. (RFC 5417 definiert zusätzlich DHCPv4 Option 138 für CAPWAP-AC-Adressen.)

```
! L3-Discovery per Broadcast-Weiterleitung (IOS/IOS XE Router bzw. SVI des AP-VLANs)
ip forward-protocol udp 5246
interface Vlan50
 ip helper-address 10.10.10.5
! DHCP-Scope mit DNS-Discovery
ip dhcp pool AP-POOL
 network 10.50.0.0 255.255.255.0
 default-router 10.50.0.1
 dns-server 10.1.1.53
 domain-name corp.local
```

Die **Discovery Response** enthält u. a. den WLC-Namen, seine AP-Kapazität und die aktuelle AP-Zahl (Auslastung) sowie ggf. das Master-Flag.

### CAPWAP-Join-Ablauf (RFC 5415, allgemeines Wissen)

1. **Discovery** (Discovery Request/Response, UDP 5246)
2. **DTLS Setup** – gegenseitige Authentisierung per Zertifikat (AP: Manufacturing Installed Certificate, MIC; WLC: Geräte- bzw. selbstsigniertes Zertifikat). Falsche Uhrzeit auf dem WLC (Zertifikat "noch nicht gültig") ist ein klassischer Join-Fehler.
3. **Join** (Join Request/Response)
4. **Image Data** – nur wenn die AP-Software nicht zur WLC-Version passt: AP lädt Image, rebootet und joint erneut.
5. **Configure** (Configuration Status Request/Response) – WLANs, Radio-Parameter.
6. **Data Check** → **Run** – Betrieb; Keepalive per **Echo Request/Response** (Heartbeat) auf dem Control-Kanal.

### AP Join Order

1. **Primary** Controller (falls konfiguriert)
2. **Secondary**
3. **Tertiary**
4. **Master Controller** – nur wenn **keine** Controller-Info im AP hinterlegt ist. *AireOS (Legacy)*: `config network master-base enable`; gedacht zum Erst-Einrichten/Stagen neuer APs, nicht für Produktion. *9800*: kein Master-Controller-Feature.
5. **Least-loaded Controller** – größte freie AP-Kapazität.

- Primary/Secondary/Tertiary werden über den **Namen** (System Name) in der Discovery Response gematcht; liegen die WLCs nicht in derselben Mobility Group, müssen **Name und IP-Adresse** angegeben werden.
- *Mit Master:* Alle APs ohne gespeicherten Controller, die per L2/L3-Broadcast suchen, joinen automatisch den Master. Admin sieht so die neuen APs und konfiguriert sie dann auf ihren Ziel-WLC um.
- *Ohne Master:* APs verteilen sich auf den am wenigsten ausgelasteten WLC. Beispiel mit zwei leeren WLCs: AP1 → erster Antwortender (z. B. WLC1), AP2 → WLC2 (0 statt 1), AP3 → Gleichstand, erster Antwortender, AP4 → der weniger belastete.
- Kurs: Last ist **relativ**: 50-AP-WLC mit 10 APs (20 %) gilt als weniger ausgelastet als 6-AP-WLC mit 3 APs (50 %). Cisco-Doku (119286) spricht von der **excess capacity** (freie AP-Plätze) aus der Discovery Response; bei Gleichstand gewinnt der zuerst antwortende WLC. In den Beispielen führen beide Maßstäbe zum selben Ergebnis (40 bzw. 3 freie Plätze).
- Kursaussage "Load Balancing erst ab drei APs pro WLC" – siehe Fehlerliste.

Troubleshooting Join (Cisco 119286 u. a.): UDP 5246/5247 durch Firewalls, Uhrzeit/NTP auf dem WLC (WLC-Zeit muss im Gültigkeitszeitraum des AP-Zertifikats liegen), Country Code (Log "Regulatory Domain Mismatch … not allowed to join"), AP-Lizenz/Kapazität, AP-Autorisierung per MAC ("AP Authorization failure"), Software-Kompatibilität. *9800*: `show ap summary`, `show wireless stats ap join summary`, `show ap name <AP> config general`. Auf dem AP: `show capwap client rcb`.

## AP Failover

- Bei WLC-Ausfall wandern die APs zu anderen WLCs mit freier Kapazität; mit **AP Fallback** (Standard: aktiv) kehren sie zum Primary zurück, sobald er wieder da ist.
- **Heartbeat** (CAPWAP Echo): Standard alle **30 s**. Fehlt ein ACK, wiederholt der AP den Heartbeat bis zu **5-mal** in kurzen Abständen (Kurs: 1 s; Cisco-Konfigurationsguides nennen als Default-Retransmit-Interval 3 s). Nach dem 5. erfolglosen Versuch gilt der WLC als unerreichbar → neuer Controller.
- Retransmit-Count und -Interval (sowie der Heartbeat) sind einstellbar: kleinere Werte = schnellere Erkennung, aber mehr Control-Traffic. *AireOS*: Fast Heartbeat 1–10 s für Local/FlexConnect.
- **Primary Discovery Request**: APs prüfen periodisch die Erreichbarkeit der Backup-Controller ihrer Liste; Timer 30–3600 s, Default **120 s** (Primary Discovery Timeout).
- Zwei Arten der Backup-Konfiguration:
  - **pro AP**: Primary, Secondary, Tertiary (*9800*: `ap name <AP> controller primary <name> <ip>` usw.)
  - **global am WLC**: Primary Backup und Secondary Backup Controller (*9800*: im AP Join Profile, `capwap backup primary <name> <ip>` / `capwap backup secondary <name> <ip>`)
- Reihenfolge nach Ausfall des Primary: AP-Primary → AP-Secondary → AP-Tertiary → WLC-Primary-Backup → WLC-Secondary-Backup → dynamische CAPWAP-Auswahl (least loaded).

### Failover Priority

- Jeder WLC hat eine begrenzte AP-Kapazität. Mit aktivierter Failover-Priorität kann ein voller Backup-WLC einen **niedriger priorisierten AP trennen**, um einem höher priorisierten Platz zu machen.
- Stufen: **1 Low** (Default für alle APs), **2 Medium**, **3 High**, **4 Critical** (höchste).
- Funktion muss global aktiviert **und** pro AP gesetzt werden. *AireOS (Legacy)*: `config network ap-priority enable`, `config ap priority 4 <AP>`. *9800*: `ap name <AP> priority 4`.

### AP Fallback

- Standard aktiv. Beim Zurückwechseln entsteht eine Unterbrechung (Kurs: ca. 12–30 s, abhängig von Timern), weil die APs neu joinen.
- Bei instabiler Verbindung zum Primary droht **Flapping** zwischen Primary und Backup. Manche deaktivieren Fallback und migrieren im Wartungsfenster. Empfehlung des Kurses: Fallback eingeschaltet lassen und nur während der Fehlerbehebung abschalten.

## High Availability

| Variante | Prinzip | Zustand | Bemerkungen |
|---|---|---|---|
| AP-spezifisch (Primary/Secondary/Tertiary pro AP) | jeder AP kennt bis zu drei WLCs | stateless | vorhersagbar, schneller Failover, Fallback, flexibel (1:1, N:1, N:N:1); mehr Planung |
| N+1 | ein Backup-WLC für mehrere Primary-WLCs | stateless | WLCs unabhängig (eigene Konfig/IP, evtl. andere HW/SW, auch über WAN in anderem RZ); AP-Priorität bei Überbuchung; APs rejoinen, Clients reassoziieren |
| AP SSO / Client SSO | 1:1 Active/Standby-Hot | stateful | gleiche Konfiguration und gleiche Management-IP; Sync über Redundancy Port |

### N+1

- Backup-WLC idealerweise geografisch getrennt (NOC/RZ). Globale HA-Timer für schnellere Erkennung, AP-Priorität bei zu wenig Lizenzen/Kapazität.
- *AireOS (Legacy)*: **HA-SKU** – Secondary mit minimaler Lizenz, bietet trotzdem die volle Hardware-Kapazität (Kursbeispiel 5508: 50-AP-Lizenz als HA-SKU → 500 APs). *9800*: Smart Licensing, keine HA-SKU; N+1 weiterhin möglich (inkl. N+1 Hitless Upgrade).

### AP SSO / Client SSO

- Nach Aktivierung rebooten beide WLCs; Primary wird **Active**, Secondary **Standby-Hot**. Nach einem Switchover tauschen die Rollen; Auslöser: manuell, Controller- oder Netzausfall.
- Standby überwacht den Active über einen dedizierten **Redundancy Port (RP)**; zusätzlich **Redundancy Management Interface (RMI)**. Über den RP laufen Konfigurations-/Zustands-Sync und Rollenaushandlung.
- **Kein Preemption**: Kommt der frühere Active zurück, wird er Standby.
- *AireOS*: Rolle bei Erstinbetriebnahme durch HA-SKU (Gerät mit HA-SKU wird beim ersten Pairing immer Standby), sonst manuell. *9800*: Chassis-Priorität bzw. Konfiguration; `show chassis`, `show redundancy`; RMI-Konfiguration `redun-management interface Vlan<x> chassis 1 address <ip> chassis 2 address <ip>`.
- **Nur AP SSO** (AireOS < 7.5): AP-Sessions bleiben, aber Clients werden deauthentifiziert und reassoziieren.
- **Client SSO** (AireOS ab 7.5, beim 9800 Standard): Clients im **RUN-State** (Authentifizierung und DHCP abgeschlossen, Verkehr läuft) werden synchronisiert → keine Reassoziation, keine SSID-Unterbrechung. Clients mitten in Authentifizierung/DHCP müssen neu beginnen.
- AP SSO kombinierbar mit Secondary/Tertiary: Das HA-Paar ist für die APs der **Primary** (eine Management-IP); erst wenn **beide** WLCs des Paares ausfallen, gehen die APs zu Secondary/Tertiary.

## AP Modes

Nicht jedes AP-Modell unterstützt jeden Modus.

| Modus | Bedient Clients? | Kern |
|---|---|---|
| **Local** | ja | Default nach Join; Management und Daten per CAPWAP zum WLC (central switching); Off-Channel-Scanning für RRM und Rogue Detection |
| **FlexConnect** | ja | Filialen; pro WLAN lokal oder zentral geswitcht, Authentifizierung lokal oder zentral; Connected vs. Standalone Mode |
| **Bridge / Mesh** | ja (je nach Modell/Radio) | RAP/MAP, Backhaul über Funk, AWPP |
| **Flex+Bridge** (allgemeines Wissen) | ja | Mesh mit FlexConnect-Local-Switching |
| **OEAP** (Office Extend) | ja | Spezielles FlexConnect für Telearbeit: sicherer Tunnel ins Firmennetz + lokal geroutete private SSID |
| **Monitor** | nein | dedizierter Sensor: Location (Context-Aware), Rogue Detection, IDS/wIPS; Submodi für RFID-Tracking und wIPS (AireOS) |
| **Rogue Detector** | nein (Radio aus) | *AireOS*: lauscht auf dem Kabel (Trunk-Port) nach ARP, vergleicht mit Rogue-MACs; ob/wie der 9800 ihn noch anbietet, ist in der Cisco-Doku nicht eindeutig belegt |
| **Sniffer** | nein | Promiscuous Capture eines Kanals inkl. Timing/Signalstärke, Weiterleitung an PC mit Analyzer (OmniPeek, Wireshark, AirMagnet) – AiroPeek-Header; *9800* leitet per UDP Quellport 5555 → Zielport 5000 an den Analyzer weiter; Wireshark: Decode As → PEEKREMOTE |
| **SE-Connect** (SOMM) | nein | CleanAir-AP als Spektrumsensor; Rohdaten an Chanalyzer/Spectrum Expert |

### Local Mode – Off-Channel-Scanning

- Der AP bedient Clients auf seinem Kanal und geht periodisch **kurz off-channel** (Kurs/Forum ~50 ms; Cisco 7.2-Guide: max. 60 ms; TAC-Doc 214393: ca. 80 ms alle 3–20 s), um andere Kanäle zu messen (Rauschen, Interferenz, Nachbar-APs, Rogues). RRM-Monitor-Intervall (Channel Scan) Default 180 s; Kursbeispiel: im 2,4-GHz-Band ca. 13 s auf dem eigenen Kanal zwischen zwei Scans, im 5-GHz-Band wegen der vielen Kanäle ca. 10 s (Zahlen nicht offiziell belegt).
- Kanalliste und Intervall sind auf dem WLC konfigurierbar (Kurs nennt das missverständlich "total RTT").
- Allgemeines Wissen: Off-Channel Scanning Defer verschiebt Scans, solange z. B. Voice-Verkehr (hohe UP-Werte) läuft.

### FlexConnect (Vertiefung zu Kapitel 15)

- Switching pro WLAN: **local** (Daten über 802.1Q-Trunk ins lokale VLAN, auch mehrere WLANs auf dasselbe VLAN) oder **central** (CAPWAP zum WLC, dort VLAN/Dynamic Interface; Verkehr zu lokalen Ressourcen läuft zweimal über das WAN).
- Authentifizierung unabhängig davon **lokal** (am AP: Open, PSK, 802.1X mit lokal definiertem RADIUS/Local EAP) oder **zentral** (über WLC; braucht Connected Mode).
- **Connected Mode**: CAPWAP-Control (DTLS über WAN) steht; AP proxyt Associations/Authentisierungen zum WLC.
- **Standalone Mode**: CAPWAP-Control weg.

| Zustand | Modus | Verhalten |
|---|---|---|
| Central Auth – Central Switching | nur connected | 802.1X/Web zentral, Daten zum WLC |
| Central Auth – Local Switching | nur connected | zentrale Auth, Daten lokal |
| Local Auth – Local Switching | connected und standalone | Open/PSK/802.1X mit lokalem RADIUS; neue Clients weiterhin möglich |
| Authentication Down – Central Switching Down | standalone | zentral geswitchte WLANs: keine Beacons/Probe Responses, Clients getrennt |
| Authentication Down – Local Switching | standalone | zentrale Auth → neue Clients abgelehnt; bestehende bleiben bis Session Timeout; Beacons, solange noch Clients da sind |

- Web Authentication im Standalone: bestehende Clients bleiben, neue werden disassoziiert; fällt die Clientzahl auf 0, stellt der AP die Beacons dieses WLANs ein.
- Bestehende 802.1X-Clients auf lokal geswitchten WLANs bleiben bis Roaming/Session Timeout, sofern der AP sie nicht selbst reauthentifizieren kann.
- *9800*: FlexConnect über Site Tag ohne `local-site` + Flex Profile; OEAP über `office-extend` im Flex Profile (allgemeines Wissen).

### Bridge Mode / Mesh

- Wireless Bridge verbindet LANs (z. B. Gebäude in einigen km Abstand); arbeitet auf **Layer 2**, kein Routing – wirkt wie ein Funk-Trunk zwischen Switches.
- Topologien: **Point-to-Point** und **Point-to-Multipoint** (Spokes kommunizieren nur über den zentralen Punkt; fällt dieser aus, sind die Spokes isoliert).
- Manche Bridges bedienen zusätzlich Clients (hybrid), andere nur Bridging. Outdoor: Feuchtigkeit, Blitzschutz.
- **Mesh**: Knoten als Repeater; **RAP** (Root AP, kabelgebunden) und **MAP** (Mesh AP, nur Funk). Dual-Radio: ein Radio für Backhaul (typisch 5 GHz), eins für Clients.
- **AWPP** (Adaptive Wireless Path Protocol) wählt den Pfad mit der höchsten **Ease** (Gegenteil von Kosten), berechnet aus **SNR** und **Hop-Zahl** der Nachbarn; Pfade passen sich an Last, Funkbedingungen und Priorisierung an; Ausfall eines Knotens → Nachbarn finden neuen Weg; mehr Knoten = mehr Kapazität.
- Allgemeines Wissen: Bridge Group Name (BGN) gruppiert Mesh-APs; MAPs müssen am WLC autorisiert sein (MAC-Filter/AAA).

## Fehler/Ungenauigkeiten im Kurs

1. **Least-loaded-Join "erst ab drei APs"**: Der Kurs behauptet, Load Balancing greife erst, wenn mindestens drei APs an einem WLC hängen, beschreibt aber gleichzeitig das Beispiel AP1→WLC1, AP2→WLC2 (Verteilung ab dem zweiten AP). Der Satz ist widersprüchlich und in aktueller Cisco-Doku nicht belegt; die Auswahl erfolgt nach freier Kapazität aus der Discovery Response. (Quelle: Cisco "Understand the Lightweight AP Join Process / WLC Discovery and Join", Cisco.com.)
2. **Local Mode "monitort alle Kanäle gleichzeitig"**: Ein Radio kann nicht gleichzeitig auf allen Kanälen hören; der Kurs beschreibt selbst im nächsten Absatz das sequenzielle Off-Channel-Scanning. Korrekt: periodisches, sequentielles Scannen.
3. **"Configuration of the total RTT"** beim Off-Channel-Scan: gemeint ist das Monitor-/Scan-Intervall bzw. die Kanalliste (RRM Monitor Intervals), keine Round Trip Time.
4. **Heartbeat-Retransmit-Intervall 1 s**: Cisco-Konfigurationsguides (AireOS `config advanced timers ap-retransmit-interval`, 9800 AP Join Profile) nennen als Default 3 s bei 5 Wiederholungen; der Kurs/die Grafik zeigt 1 s. Für Prüfungsfragen nur "5 Wiederholungen" und "30 s Heartbeat" verwenden.
5. **AP SSO: "alle Clients werden deauthentifiziert"** gilt nur ohne Client SSO (AireOS vor 7.5). Der Kurs erwähnt Client SSO im übernächsten Absatz; beim Catalyst 9800 ist SSO immer AP- **und** Client-SSO.
6. **Primary-Discovery-Timer** wird im Kurs vermischt (Intervall der Primary Discovery Requests vs. Antwortzeit). Gemeint ist der Primary Discovery Timeout (30–3600 s, Default 120 s), nach dem der AP seine Backup-Liste neu prüft.
7. Veraltet: Master Controller (9800: laut Cisco Community kein Äquivalent – Option 43/DNS/Priming nutzen), HA-SKU, 5508, Release 7.5, Rogue Detector Mode (AireOS-Begriff; 9800-Unterstützung nicht belegt), Cisco Spectrum Expert (abgekündigt), Aironet (Nachfolger Catalyst 9100/CW91xx), AirProvision-Priming (für die Wi-Fi-7-Generation durch Global-Use-Konzept ersetzt).

## Bilder

- `bilder/16-wlan-ap/01-priming.svg` – Universal AP Priming: manuell per Smartphone (GPS + MCC, WPA2-PSK-SSID) und automatisch per NDP-Beacon an Nachbar-APs.
- `bilder/16-wlan-ap/02-discovery.svg` – Die vier Discovery-Quellen (Broadcast, gespeichert, DHCP Option 43/52, DNS) mit typischen Details.
- `bilder/16-wlan-ap/03-joinorder.svg` – Join-Reihenfolge Primary → Secondary → Tertiary → Master → Least Loaded.
- `bilder/16-wlan-ap/04-capwap-fsm.svg` – CAPWAP-Zustände vom Discovery bis Run inkl. Image-Download-Schleife.
- `bilder/16-wlan-ap/05-leastload.svg` – Verteilung von vier APs auf zwei WLCs ohne Master und relative Lastberechnung.
- `bilder/16-wlan-ap/06-heartbeat.svg` – Heartbeat (30 s), 5 Wiederholungen, Wechsel zum Backup-WLC und Backup-Reihenfolge.
- `bilder/16-wlan-ap/07-ha-modelle.svg` – Vergleich AP-spezifisch (N:N:1), N+1 und SSO-Paar mit Redundancy Port.
- `bilder/16-wlan-ap/08-apmodi.svg` – Übersicht der AP-Modi: bedienen Clients oder nur Sensor/Spezialfunktion.
- `bilder/16-wlan-ap/09-mesh.svg` – Bridge-Topologien (P2P, P2MP) und Mesh mit RAP/MAP und AWPP-Ease.
