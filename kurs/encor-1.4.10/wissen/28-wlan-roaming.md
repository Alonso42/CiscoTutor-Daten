# Exploring Wireless Roaming and Location Services

Quelle: ENCOR 1.4.10 Student Guide, Seiten 306–310 (Intro 305, Summary Challenge 311 und Answer Key 312 nicht verwendet). Ergänzungen aus eigenem Wissen (Catalyst 9800 / IOS-XE 17.x, IEEE 802.11k/r/v, Cisco Spaces) sind als solche gekennzeichnet.

Topics: ENCOR-LEGACY-WLAN (Wireless ist im ENCOR-Blueprint v1.2 kein eigenes Thema mehr; früher ENCOR v1.0 1.4.c "Describe wireless roaming and location services").

> Abgrenzung zu anderen Kapiteln: Mobility-Ports als Grundtabelle, Guest Anchor auf 9800 (CLI `mobility anchor`), Virtual IP, Sticky Client, Ping-Pong-Roaming, PoP/PoA-Grundbegriffe, MA/MC, WDS bei autonomen APs und FlexConnect-Gruppen stehen in Kapitel 15–18 und 27. Dieses Kapitel vertieft Roaming-Auslöser und Scanning, Mobility Group vs. Domain, den Ablauf der drei Roaming-Typen, symmetrisches/asymmetrisches Tunneling, Fast Secure Roaming (PMK Caching, OKC, CCKM, 802.11r), 802.11k/v und Location Services (Genauigkeitsstufen, FastLocate, Hyperlocation, CMX → Cisco Spaces, Platzierungsregeln).

## Wireless Roaming Overview (Seite 306)

### Wer entscheidet?
- **Der Client** entscheidet, wann und wohin er roamt. Die Infrastruktur kann nur Hinweise geben (802.11k Neighbor Report, 802.11v BSS Transition, Cisco-CCX-Roaming-Parameter) oder indirekt steuern (kleinere Zellen durch Mindestdatenraten, Optimized Roaming, Load Balancing).
- Roaming-Algorithmen unterscheiden sich je Hersteller, Treiberversion und sogar Gerätetyp desselben Herstellers.
- Während der Client andere Kanäle scannt, sich reassoziiert und neu authentifiziert, kann er keine Daten senden → jedes Roaming erzeugt eine Unterbrechung.

### Typische Roaming-Auslöser
| Auslöser | Erklärung | Braucht aktiven Verkehr? |
|---|---|---|
| Max. Retries überschritten | viele Wiederholungen → erst Datenrate senken (eine Schwelle), dann roamen (zweite Schwelle); Schwellen herstellerabhängig | ja |
| Low RSSI | Empfangspegel unter Schwelle | nein |
| Low SNR | Abstand Signal–Noise Floor unter Schwelle | nein |
| Proprietäres Load Balancing | Infrastruktur entscheidet und teilt es dem Client per Herstellerprotokoll mit | – |

- Cisco WLCs (AireOS) haben pro Band einen Satz **CCX-Client-Roaming-Parameter** (Cisco Compatible Extensions), die CCX-Clients als Schwellen übernehmen; Default-Satz kann durch eigenen ersetzt werden (eigenes Wissen: Minimum RSSI, Roaming Hysteresis, Scan Threshold, Transition Time). Bedeutung:
  - **Minimum RSSI**: Mindestpegel, den ein AP haben muss, damit der Client ihn als Ziel nimmt.
  - **Hysteresis**: Um wie viel dB der neue AP besser sein muss (verhindert Ping-Pong).
  - **Scan Threshold**: Unterhalb dieses RSSI beginnt der Client aktiv nach Alternativen zu suchen.
  - **Transition Time**: Zeit, in der der Client nach Unterschreiten der Scan-Schwelle einen neuen AP finden soll.
- CCX ist Legacy; moderne Clients nutzen 802.11k/v.

### Scanning
- Client sucht APs mit **gleicher SSID** auf anderen Kanälen.
- **Active Scan**: Radio auf Zielkanal wechseln, Probe Request senden, auf Probe Responses (oder Beacons) warten; Wartezeit nicht im Standard festgelegt, ca. 10 ms typisch.
  - **Directed Probe**: enthält konkrete SSID → nur APs mit dieser SSID antworten.
  - **Broadcast Probe**: Null-SSID → alle APs antworten mit einer Probe Response je unterstützter SSID.
- **Passive Scan**: Radio auf Kanal wechseln und auf Beacons warten; Beacon-Intervall Default ca. 100 ms (100 TU = 102,4 ms) → dauert länger, daher bevorzugen die meisten Clients aktives Scannen. (Eigenes Wissen: auf DFS-Kanälen dürfen Clients erst nach empfangenem Beacon proben → dort faktisch passiv.)
- Während des Scans kein Senden/Empfangen von Daten. Strategien:
  - **Background Scanning**: vorab, in Verkehrspausen oder nur ein Kanal pro Durchgang → Wissen über Nachbar-APs, schnelleres Roaming.
  - **On-Roam Scanning**: erst wenn Roaming nötig ist; z. B. nur nicht überlappende Kanäle scannen.
- Algorithmus-Anpassungen: Informationen wie "Voice Call aktiv" oder Ergebnisse des Background-Scans verändern das Verhalten:
  - nur Teilmenge der Kanäle scannen,
  - Scan früh abbrechen (erster akzeptabler AP genügt bei Voice),
  - Scan-Timer verkürzen (kürzer auf Probe Responses warten).

## Mobility Groups and Domains (Seite 307)

- **Mobility Group**: Gruppe von Mobility Controllern (MCs), zwischen denen nahtloses Roaming laufen soll; AireOS: **bis 24 WLCs**. Sie teilen Client-Kontext/-Zustand und Lastinformationen und leiten Daten untereinander weiter (Inter-Controller-Roaming, Redundanz).
- Roaming innerhalb der Mobility Group ohne erneute Authentifizierung (Schlüssel-Cache wird geteilt); liegt der neue AP an einem anderen WLC, werden die Client-Informationen übertragen.
- **Mobility Domain**: Ein WLC kennt auch Controller anderer Mobility Groups (in seiner Mobility List). Die Mobility List fasst bis zu **72 Controller**, davon max. 24 in derselben Gruppe (Cisco-FAQ: Kombinationen 3 × 24, 12 × 6, 24 × 3, 72 × 1; der Kurs vereinfacht zu "3 Gruppen = 72"). Mobile Announce geht zuerst an die eigene Gruppe, dann an die übrigen Einträge der Liste. Roaming zwischen Gruppen innerhalb der Domain ist möglich, Fast Secure Roaming (Key Caching) aber nur innerhalb derselben Gruppe → bei Gruppenwechsel volle Re-Authentifizierung.
- Voraussetzung: Jeder WLC muss die **eingebaute MAC-Adresse und Management-IP** des anderen eingetragen haben (gegenseitig!).
- Roamt ein Client zu einem WLC, der den alten WLC nicht kennt (andere Domain) → neue Authentifizierung, neue Association, neue IP-Adresse.
- Gemeinsamkeiten innerhalb einer Mobility Group (lt. Kurs): Mobility-(Gruppen-)Name, Controller-Code-Version, CAPWAP-Modus, ACLs, WLANs (SSIDs). Eigenes Wissen ergänzt: gleiche **Virtual Interface IP** (z. B. 192.0.2.1) auf allen WLCs, IP-Erreichbarkeit der Management-Interfaces, identische WLAN-Security-Einstellungen.

### Mobility-Nachrichten und Ports
| Verkehr | AireOS (Legacy) | Catalyst 9800 |
|---|---|---|
| Mobility Control | UDP 16666 (auch Ziel des mping) | UDP 16666, immer DTLS-verschlüsselt |
| Mobility Data | EoIP = EtherIP, IP-Protokoll 97 (alt); mit Verschlüsselung bzw. CAPWAP-basierter Secure/New Mobility UDP 16667 | CAPWAP-basiert, UDP 16667 (Data-Link-Verschlüsselung optional) |
| AP ↔ WLC | CAPWAP UDP 5246 Control, 5247 Data | gleich |

- 9800 unterstützt **kein EoIP**; Inter-Release Controller Mobility (IRCM) mit AireOS nur über den CAPWAP-basierten Secure-Mobility-Tunnel (AireOS 8.10 MR1 oder neuer bzw. spezielle IRCM-8.5-Images; AireOS-seitig `config mobility group member add <MAC> <IP> <Gruppe> encrypt enable`, bei 9800-CL zusätzlich `config mobility group member hash`). 9800-Default-Gruppenname: `default`.
- Wichtige Mobility-Nachrichten (eigenes Wissen): **Mobile Announce** (neuer WLC fragt die Peers, wer den Client kennt), **Handoff Request/Reply** (Kontextübergabe), Keepalives für Control- und Data-Pfad.

### CLI
```
! AireOS (Legacy)
config mobility group domain CAMPUS
config mobility group member add 00:1a:2b:3c:4d:5e 10.10.20.2 CAMPUS
show mobility summary
mping 10.10.20.2        ! testet Mobility Control (UDP 16666)
eping 10.10.20.2        ! testet den Mobility-Datenpfad

! Catalyst 9800 (IOS-XE)
wireless mobility group name CAMPUS
wireless mobility mac-address 001e.bd01.0001
wireless mobility group member mac-address 001e.bd02.0002 ip 10.10.20.2 group CAMPUS
show wireless mobility summary
show wireless mobility peer ip 10.10.20.2
```
Beispiel (gekürzt) `show wireless mobility summary` auf 9800:
```
Mobility Group Name: CAMPUS
...
IP Address    Public Ip     MAC Address     Group Name  Multicast IP  Status   PMTU
10.10.10.2    N/A           001e.bd01.0001  CAMPUS      0.0.0.0       N/A      N/A   (lokal)
10.10.20.2    10.10.20.2    001e.bd02.0002  CAMPUS      0.0.0.0       Up       1385
```
- Status "Control and Data Path Down" / "Data Path Down" → Firewall/ACL für UDP 16666/16667 oder falsche MAC/IP prüfen.

## Wireless Roaming Types (Seite 308)

### Client-Datenbank
Bei Association legt der WLC einen Eintrag an: MAC- und IP-Adresse, Security-Kontext und Associations (Schlüssel), QoS-Kontext, WLAN, zugeordneter AP. Damit leitet er Frames weiter.

### Layer 2 Roaming (gleiches VLAN/Subnetz)
1. **Intra-Controller**: Neuer AP hängt am selben WLC → WLC aktualisiert nur den Datenbankeintrag (neuer AP), ggf. neuer Security-Kontext. PoP und PoA bleiben gleich.
2. **Inter-Controller L2**: Neuer AP an anderem WLC; WLCs tauschen Mobility-Nachrichten aus, der Client-Eintrag wird **verschoben** (Kurs schreibt an einer Stelle "kopiert"), PoP und PoA wandern komplett zum neuen WLC, Verkehr läuft über den neuen Pfad. Voraussetzung: WLCs L2-adjazent bzw. gleiches VLAN/Subnetz für die SSID, gleiche Mobility Group, kompatible Software. Im zentralen Deployment ist der WLC zugleich MC und MA.
- Transparent für den Client, solange er kein DHCP Discover sendet und kein Session Timeout abläuft.

### Layer 3 Roaming (Inter-Subnet)
- Gleiche SSID, aber am neuen WLC einem anderen VLAN/Subnetz zugeordnet (z. B. Distribution getrennt durch gerouteten Core).
- Ablauf: Mobility-Nachrichten; alter WLC markiert den Client als **Anchor**, Eintrag wird zum neuen WLC **kopiert** und dort als **Foreign** markiert. PoA → Foreign, PoP bleibt am Anchor. Client **behält seine IP-Adresse**, Policy bleibt konsistent.
- **Symmetric Mobility Tunneling**: Verkehr in beide Richtungen läuft Foreign ↔ Anchor durch den Mobility-Tunnel; Anchor bringt ihn ins Netz. In aktuellen AireOS-Releases Default und nicht mehr abschaltbar (Umstellung um Release 5.2, laut älteren Cisco-Guides; online nicht mehr direkt belegbar), auf 9800 einzige Variante.
- **Asymmetric Tunneling** (Legacy): nur Downstream über den Anchor, Upstream verlässt der Verkehr den Foreign direkt mit einer Quell-IP aus dem Anchor-Subnetz → scheitert an uRPF/Anti-Spoofing und stateful/source-basierten Firewalls. Deshalb fordert der Kurs gleiche Zugriffsrechte und keine source-basierten Routing-/Firewall-Regeln.
- Rollen im Client-Detail: Local, Anchor, Foreign (bzw. Export Anchor / Export Foreign beim Auto-Anchor).

### Auto-Anchor Mobility (Guest Tunneling)
- Gesamter Verkehr eines WLANs (meist Gast) wird zu einem vordefinierten Anchor-WLC (oder mehreren) getunnelt, unabhängig vom AP-Standort.
- Zweck: Gast-Verkehr durch Firewall/DMZ führen, geografische Zugriffsregel (Verkehr immer in einem bestimmten Subnetz), Ersatz für L3-Roaming, wenn eine Firewall dieses stört.
- Ablauf: Client assoziiert an WLC1 (PoA), WLC1 tunnelt (symmetrisch, EoIP oder CAPWAP) zum Anchor; IP-Adresse (DHCP) und WebAuth kommen vom Anchor; Anchor ist der PoP und bleibt fest. Roamt der Gast zu WLC2, wechselt nur der PoA; IP und PoP bleiben.
- Eigenes Wissen: Anchor braucht keine APs; Foreign = "Export Foreign", Anchor = "Export Anchor"; mehrere Anchors mit Priorität möglich. Der Anchor muss nicht in derselben Mobility Group sein, nur in der Mobility List (Peering), oft eigene Gruppe in der DMZ. AireOS: `config wlan mobility anchor add <wlan-id> <anchor-ip>`.

## Fast Secure Roaming und 802.11k/v (eigenes Wissen, im Kurs nur angedeutet)

### Zeitbudget
- Voice: Gesamt-Roaming-Unterbrechung **< 150 ms** (orientiert am Budget für Einweg-Verzögerung), ideal < 50 ms. Typische Roam-Zeiten laut Cisco (9800 Roaming Primer): volle Authentifizierung 120 ms bis einige Sekunden, OKC 8–100 ms, CCKM/802.11r/Adaptive 11r 4–50 ms.
- WPA2/WPA3-Personal: beim Roaming nur 4-Way Handshake (PMK aus Passphrase bekannt) → schnell, aber kein Enterprise-Schutz.

### Verfahren
| Verfahren | Prinzip | Hinweis |
|---|---|---|
| PMK Caching (SKC, "sticky") | Client und AP/WLC cachen den PMK; Rückkehr zu einem **schon besuchten** AP mit PMKID in der Reassociation → nur 4-Way Handshake | hilft nicht beim ersten Besuch eines AP |
| OKC (Opportunistic Key Caching) | PMK wird an alle APs des WLC/der Mobility Group verteilt; Client berechnet PMKID für den **neuen** AP selbst | nicht IEEE-standardisiert, aber weit verbreitet |
| CCKM | Cisco-proprietär (CCX), WLC als Key Manager | Legacy, nur CCX-Clients (alte Cisco-Phones) |
| 802.11r FT | IEEE-Standard; Schlüsselhierarchie PMK-R0 (R0KH, WLC) → PMK-R1 (R1KH) → PTK; 4-Way Handshake in Authentication/Reassociation integriert | Over-the-Air oder Over-the-DS |

- **FT Over-the-Air**: Client spricht den Ziel-AP direkt mit FT-Authentication-Frames an, dann Reassociation.
- **FT Over-the-DS**: Client sendet FT Action Request an den **aktuellen** AP, der ihn über das Distribution System zum Ziel-AP weiterreicht; erst danach Reassociation beim Ziel-AP. Cisco empfiehlt meist Over-the-Air.
- FT-AKMs: FT-802.1X, FT-PSK, FT-SAE. Ältere Clients erkennen FT-AKM evtl. nicht → Mixed Mode (FT- und Nicht-FT-AKM auf einem WLAN, von Cisco empfohlen) oder Adaptive 802.11r (9800-Default: RSN-IE ohne FT-AKM, nur Mobility Domain wird angekündigt; unterstützte Partnergeräte wie aktuelle iOS-/Samsung-Geräte nutzen trotzdem FT). FT-only sperrt Nicht-FT-Clients aus. Over-the-Air ist Default, Over-the-DS laut Best Practices deaktiviert lassen. OKC ist auf dem 9800 Default.
- 802.11r-Beacons enthalten das Mobility Domain Information Element (MDID) – nicht zu verwechseln mit der Cisco-Mobility-Domain.
- Key-Caches werden innerhalb der Mobility Group geteilt; über Gruppengrenzen → volle Authentifizierung. FlexConnect: Key-Sharing per FlexConnect-Gruppe/Site-Tag.

### 802.11k und 802.11v
- **802.11k** (Radio Resource Measurement): **Neighbor Report** – Client fragt den AP nach Nachbar-APs/Kanälen → muss nur wenige Kanäle scannen.
- **802.11v** (Wireless Network Management): **BSS Transition Management (BTM)** – AP empfiehlt einem Client Ziel-APs; mit "Disassociation Imminent" kündigt er die Trennung an. Client darf ablehnen (Entscheidung bleibt beim Client). Weitere Funktionen: DMS, WNM-Sleep, BSS Max Idle Period.
- 9800-CLI (WLAN-Konfiguration):
```
wlan CORP 1 CORP
 security wpa akm ft dot1x
 security ft
 security ft over-the-ds          ! optional
 assisted-roaming neighbor-list   ! 802.11k
 bss-transition                   ! 802.11v
```
- AireOS: `config wlan security ft enable <id>`, `config wlan security ft over-the-ds enable <id>`, `config wlan assisted-roaming neighbor-list enable <id>`, `config wlan bss-transition enable <id>`.
- **Optimized Roaming** (Cisco): WLC trennt Clients unter einer RSSI-/Datenratenschwelle aktiv und beantwortet ihre Probes/Associations nicht → gegen Sticky Clients.

## Location Services (Seite 309)

### Analytics
- Wi-Fi-Ortung auf Basis der normalen 802.11-Infrastruktur (keine separate RFID-Empfänger-Infrastruktur nötig).
- Analytics = Daten sammeln, korrelieren, darstellen → handlungsrelevante Erkenntnisse. Nutzer: IT (Bandbreite, Login per Social Media), Marketing (Verweildauer, Wege, Interessen, Service-Differenzierung), Logistik, Einkauf usw.

### Cisco CMX (Legacy) → Cisco Spaces
- **CMX (Connected Mobile Experiences)**: drei Funktionen **Detect, Connect, Engage**.
  - **Detect**: Presence (1–2 APs, Besucher zählen, **Dwell Time**, Besucher vs. Passanten, Vergleiche über Tage/Wochen/Monate) oder Location (10 m bis 1 m; 1 m mit Hyperlocation-Modul + Antennenarray; BLE-Ortung mit BLE-Beacons/-Modulen).
  - **Connect**: Gast-Captive-Portal (Splash, AUP, Passwort per E-Mail/SMS, Social Login → zusätzliche Analysedaten; Portal pro Zone möglich).
  - **Engage**: Inhalte/Angebote an Besucher (Coupon für Wiederkehrer, Loyalty-Stufen, besserer Wi-Fi-Service für Top-Kunden).
- Deployment: on-prem auf **MSE**-Appliance oder als VM (z. B. UCS), oder CMX Cloud (zwei SaaS-Lizenzstufen).
- Analytics-Tools: **Presence Analytics** (Zählung pro Etage/Gebäude, neu vs. wiederkehrend, Besucher vs. Passant, Conversion Rate, Dwell Time, Spitzenzeiten → Personalplanung), **Location Analytics** (Heatmaps live und Playback, Correlation = Wegeverfolgung, z. B. Food Court).
- **Aktuell**: CMX und MSE sind End-of-Life; Nachfolger ist **Cisco Spaces** (vorher Cisco DNA Spaces), cloudbasiert, Anbindung des 9800 direkt oder über den **Spaces Connector**; Meraki nativ. Lizenzstufen historisch SEE, EXTEND, ACT; aktuell laut Spaces-FAQ Extend, ACT und Smart Spaces. Controller ↔ Location-Engine historisch per **NMSP** (Network Mobility Services Protocol, TCP 16113); `show nmsp status`.

### Genauigkeitsstufen (Kurstabelle)
| Stufe | Genauigkeit | Ergebnis | Use Case | AP-Anforderung |
|---|---|---|---|---|
| Presence | ~20 m | In-Zone-Erkennung | Venue-Ebene, Besucher, Dwell Time | ≥ 1 AP |
| Basic Location | ~7 m | x/y-Koordinaten | Zonen-Korrelation | ≥ 3 APs, Kartenintegration |
| Enhanced (FastLocate) | ~5 m | höhere Refresh-Rate | Subzonen-Navigation | dichtere APs, FastLocate aktiv |
| Hyperlocation | ~1 m | sehr genau | Produktplatzierung, Asset-Management | modulare APs mit Hyperlocation-Modul |

### Verfahren (teils eigenes Wissen)
- **RSSI-Trilateration**: Aus RSSI wird über ein Pfadverlustmodell die Entfernung zu jedem AP geschätzt; ≥ 3 APs nötig, die den Client hören (Probes oder Daten).
- **RF Fingerprinting**: gemessene RSSI-Vektoren werden mit einem RF-Modell der Etage verglichen; **Kalibrierung** (Begehung mit Client an bekannten Punkten) erfasst Wände/Dämpfung real → genauer als reine Distanzformel.
- **Probe-RSSI-Problem**: Clients proben selten/unregelmäßig (Stromsparen) und auf vielen Kanälen; Nachbar-APs auf anderen Kanälen hören Daten des Clients nicht.
- **FastLocate**: Nutzt RSSI aus **Datenpaketen**; dafür scannen Monitor-Radios (WSM-Modul in bestimmten APs) gleichzeitig alle Kanäle → häufigere, netzinitiierte Updates, ohne die Client-Radios (2,4/5 GHz) zu belasten.
- **Hyperlocation**: **Angle of Arrival (AoA)** mit Antennenarray (Hyperlocation-Modul) + BLE-Beacon → ~1 m.
- **TDoA** (Time Difference of Arrival): für Wi-Fi-RFID-Tags in großen offenen Bereichen (synchronisierte Empfänger).
- MAC-Randomisierung moderner Smartphones verfälscht Presence-Zählungen (neue MAC = neuer Besucher).
- Genauigkeitsangaben sind statistisch (z. B. Anteil der Messungen innerhalb von x m).

### Platzierungsregeln für Location
- Mindestens **3 APs** pro Etage hören den Client mit **≥ −75 dBm**.
- Faustregel 1 AP pro **2500 sq ft** (~230 m²); Dichte per Site Survey bestimmen; Abstand der APs ca. 12–20 m.
- APs entlang der **Außenwände/Ecken** (Perimeter) und versetzt (staggered); bei hoher Dichte zusätzlich APs in der Mitte; mind. **4 APs mit Sichtverbindung** zum Client anstreben.
- **20 % Zellüberlappung** für Roaming und Ortung.
- **Convex Hull**: Linie um die äußersten APs muss die gesamte Fläche umschließen; Clients außerhalb werden ungenau verortet.
- Langer schmaler Raum: nicht in einer Linie in der Mitte, sondern versetzt an beiden Außenwänden.
- Fehlende Sichtverbindung → mehr APs, sonst hören evtl. nur 2 APs den Client.

## Summary (Seite 310)
Nur Video-Verweis.

## Fehler/Ungenauigkeiten im Kurs
1. Seite 307: "User data ... via EoIP (IP protocol 97) or CAPWAP (UDP port 5246)". UDP 5246 ist CAPWAP-**Control** zwischen AP und WLC. CAPWAP-basierte Mobility-Daten laufen über **UDP 16667** (Control UDP 16666). Quelle: Cisco Catalyst 9800 Configuration Guide, Kapitel "Mobility"; Cisco WLC Mobility Groups FAQ.
2. Seite 307: "UDP 16666 for unencrypted traffic" – für den 9800 veraltet: dort ist der Control-Kanal immer DTLS-verschlüsselt (UDP 16666), 16667 ist Data. Auch bei altem AireOS diente 16667 laut Cisco Mobility Groups FAQ für verschlüsselte Mobility-**Daten** (statt EoIP), nicht für Control.
3. Seite 307: Gemeinsame Eigenschaft "Mobility domain name" – gemeint ist der **Mobility-Group-Name**; "Version of controller code" ist zu streng, Inter-Release Controller Mobility (IRCM) zwischen unterschiedlichen Releases wird unterstützt. Wichtig fehlt: gleiche **Virtual-Interface-IP**.
4. Seite 308: Inter-Controller L2 – einmal "copied", später "moved". Korrekt: Bei L2 wird der Eintrag **verschoben** (neuer WLC wird Local), bei L3 **kopiert** (Anchor + Foreign).
5. Seite 308: Auto-Anchor als "subset of a mobility group" – der Anchor muss nur Mobility-Peer sein, häufig in eigener Gruppe (DMZ).
6. Seite 308/309: Durchgängig AireOS/CMX-Terminologie; aktuell 9800 und Cisco Spaces (CMX, MSE, DNA Spaces abgelöst). "Mocular APs" in der Tabelle = Tippfehler für "Modular APs".
7. Seite 309: Die beschriebene Hardware ist abgekündigt: Hyperlocation-Modul/-Antenne End-of-Sale 30.04.2019 (Support-Ende 30.04.2024), AP 4800 (Hyperlocation integriert) End-of-Sale 31.10.2022, Support-Ende 31.10.2027; WSM-Modul der 3600/3700 ebenfalls Legacy. FastLocate und Hyperlocation werden im Spaces-Datenblatt noch als Funktionen über den Spaces Connector geführt; heutige Catalyst-9100-APs bringen zusätzlich BLE/IoT-Radio für Spaces mit.

## Bilder
- `bilder/28-wlan-roaming/01-roam-ausl.svg` – Roaming-Auslöser (Retries, RSSI, SNR, Load Balancing) und Active vs. Passive Scan.
- `bilder/28-wlan-roaming/02-mob-gruppe.svg` – Mobility Group (bis 24 WLCs) vs. Mobility Domain/Mobility List (bis 72 WLCs, max. 24 je Gruppe), Fast Roaming nur in der Gruppe.
- `bilder/28-wlan-roaming/03-l2-roam.svg` – Intra-Controller und Inter-Controller L2: Eintrag wird aktualisiert bzw. verschoben, PoP+PoA wandern.
- `bilder/28-wlan-roaming/04-l3-roam.svg` – L3-Roaming: Anchor (PoP) / Foreign (PoA), symmetrischer Tunnel, Client behält IP.
- `bilder/28-wlan-roaming/05-auto-anchor.svg` – Guest Auto-Anchor: Foreign-WLCs tunneln das Gast-WLAN zum Anchor in der DMZ.
- `bilder/28-wlan-roaming/06-fast-roam.svg` – Zeitvergleich volle EAP-Authentifizierung vs. PMK-Cache vs. OKC vs. 802.11r (Voice-Budget 150 ms).
- `bilder/28-wlan-roaming/07-ft-ota-ds.svg` – 802.11r Over-the-Air vs. Over-the-DS.
- `bilder/28-wlan-roaming/08-loc-stufen.svg` – Location-Genauigkeitsstufen Presence/Basic/FastLocate/Hyperlocation.
- `bilder/28-wlan-roaming/09-ap-platz.svg` – AP-Platzierung für Location: Perimeter + Mitte, Convex Hull, empfohlen vs. nicht empfohlen.
