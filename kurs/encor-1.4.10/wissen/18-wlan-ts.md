# Troubleshooting Wireless Client Connectivity

Quelle: ENCOR 1.4.10 Student Guide, Seiten 185–195 (Intro 184, Summary Challenge 196 und Answer Key 197 nicht verwendet)

Topics: ENCOR-LEGACY-WLAN (Wireless ist im ENCOR-Blueprint v1.2 kein eigenes Thema mehr)

> Aktualitätshinweis: Der Kurs zeigt die Werkzeuge überwiegend am **AireOS**-WLC (GUI-Monitoring-Dashboard, `show client detail`, `debug client`). AireOS ist Legacy (End-of-Sale/End-of-Life); Referenzplattform ist der **Catalyst 9800** (IOS XE) mit `show wireless client ...`, **Radioactive Tracing** und Always-On-Tracing (`show logging profile wireless`) sowie **Catalyst Center Assurance (Client 360)**. Nur das Discovery-Lab nutzt bereits einen 9800. Mehrere genannte Dritthersteller-Tools sind eingestellt (AirPcap, MetaGeek Eye P.A., Cisco Spectrum Expert).
>
> Abgrenzung: Allgemeine Troubleshooting-Methodik, SPAN/RSPAN/ERSPAN und Embedded Packet Capture stehen in Kapitel 22 (22-analysis). AP-Discovery/Join, CAPWAP, AP-Modi (Sniffer, SE-Connect, Monitor) in Kapitel 15/16. WPA2/WPA3, 802.1X/EAP, 4-Way Handshake, 9800-Profile/Tags und Gastzugang in Kapitel 17. Hier nur die Vertiefung Wireless-**Client**-Troubleshooting.

## Wireless Troubleshooting Tools Overview

Der Kurs teilt WLAN-Werkzeuge in vier Kategorien ein:

| Kategorie | Schicht (laut Kurs) | Was sie sieht | Beispiele |
|---|---|---|---|
| Spectrum Analysis | Layer 1 | gesamte HF-Energie, auch Nicht-Wi-Fi-Störer | MetaGeek Chanalyzer (+ Wi-Spy), Ekahau (Sidekick), Cisco CleanAir, Cisco Spectrum Expert (EoL), Meraki RF Spectrum |
| Wi-Fi Scanning | Layer 2 | Beacons/Probe Responses: SSID, BSSID, Kanal, RSSI, Security | MetaGeek inSSIDer, Wi-Fi Analyzer (Android), Apple AirPort Utility (iOS) |
| Packet Analysis | (Kurs: "Layer 3", korrekt: 802.11-Frames = Layer 2 und aufwärts) | alle 802.11-Frames (Management, Control, Data) zwischen AP und Client | Wireshark, OmniPeek, AirMagnet (heute NetAlly), MetaGeek Eye P.A. (eingestellt) |
| WLC GUI/CLI + Konfig-Analyse | – | Zustand von APs, Clients, Logs, Konfiguration | AireOS-GUI/CLI, 9800-GUI/CLI, Wireless Config Analyzer Express |

Merksatz: Spektrumanalysator = "Kabeltester" des WLANs (sieht Energie, dekodiert keine Frames). Scanner = was die Beacons verraten. Packet Capture = was wirklich zwischen Client und AP passiert.

## Spectrum Analysis

- Zweck: HF-Störungen erkennen, identifizieren (Gerätetyp), lokalisieren und beseitigen. Typischer Auslöser: nach der Abnahme-Messung (Post-Installation Survey) kommen neue Geräte dazu (z. B. Bewegungsmelder, Funkkameras) → Abbrüche/Leistungseinbrüche in bestimmten Bereichen.
- **Non-Wi-Fi-Interferer** im 2,4-GHz-ISM-Band: Mikrowellenherde (um 2,45 GHz, trifft vor allem die oberen Kanäle; strahlt nur in jeder zweiten Netz-Halbwelle → Duty Cycle ca. 50 %), Bluetooth (FHSS, springt über das ganze 2,4-GHz-Band, 1600 Hops/s – schmalbandig, kurz), analoge/FHSS-Funktelefone und Video-/Babyfone im 2,4- oder 5,8-GHz-Band, Funkkameras, ZigBee, Bewegungsmelder, Störsender (Jammer). **DECT** (Europa 1880–1900 MHz, USA "DECT 6.0" 1920–1930 MHz) liegt **nicht** im WLAN-Band und stört Wi-Fi nicht.
- **Duty Cycle**: Anteil der Zeit, in der ein Störer sendet (in %). Hoher Duty Cycle (z. B. Videobrücke, Jammer ≈ 100 %) blockiert den Kanal praktisch dauerhaft, weil CSMA/CA den Kanal als belegt erkennt (CCA) oder Frames zerstört werden. Niedriger Duty Cycle mit hoher Leistung → sporadische Retries.
- Wichtige Darstellungen: Echtzeit-FFT/Spektrum (Leistung über Frequenz), **Waterfall/Spectrogram** (Zeitverlauf), **Duty Cycle**, Kanal-Zusammenfassung (Channel Summary: Leistung, Anzahl Störer pro Kanal), Device Finder (Störer orten durch Richtantenne/Signalstärke).
- **MetaGeek Chanalyzer**: Windows, Hardware Wi-Spy oder Cisco-AP im SE-Connect-Modus (Zusatzlizenz); 2,4 und 5 GHz; zeigt Co-Channel/Overlapping und klassifiziert Nicht-Wi-Fi-Störer.
- **Ekahau Site Survey** (heute Ekahau AI Pro, Spektrum über Sidekick): Planung, Pre-/Post-Site-Survey, passive und aktive Messungen; erkennt Coverage Holes, CCI/ACI, zu wenig Kapazität, zu viele Clients pro AP, suboptimale Kanalwahl, fehlende Security-Einstellungen, Roaming-Probleme; misst Signalstärke, SNR, Rauschen, RTT/Packet Loss, Kanalauslastung (Beispiel: VoIP-Abbrüche in einem Bereich).
- **Cisco CleanAir**: im AP integrierte Spektrumanalyse (CleanAir-fähige AP-Hardware nötig), am WLC global/pro Band aktivierbar. Klassifiziert Störer (Interference Device Record), zeigt, welche APs den Störer hören (→ Lokalisierung), bewertet Kanäle mit **Air Quality (AQ/AQI, 1–100, 100 = sauber, 1 = schlechteste)** und Severity. Einstellungen: CleanAir global ein/aus, Störer melden ja/nein, persistente Geräte verfolgen (Persistent Device Avoidance), welche Störertypen einen **SNMP-Trap** auslösen. Mit **ED-RRM** (Event-Driven RRM) wechselt der AP bei schwerem Störer sofort den Kanal.
- **Cisco Spectrum Expert** (eingestellt): Laptop mit Sensorkarte oder Remote-Sensor = AP im **SE-Connect**-Modus. Ansichten: Spectrum Views, Active Devices, Devices (Historie), Channel Summary, Device Finder, Tools.
- **Meraki RF Spectrum**: MR-APs mit dediziertem Scan-Radio; 2,4/5 GHz (neuere auch 6 GHz) im Dashboard, Hintergrund-Monitoring für Auto RF.

## Wi-Fi Scanning

- Scanner hören Beacons und Probe Responses und zeigen: **SSID, BSSID (MAC), Kanal, Kanalbreite, RSSI (dBm), Security (Open/WPA2/WPA3), Datenraten, zuletzt gesehen**. Keine Nicht-Wi-Fi-Störer, keine Client-Daten, keine Position.
- **inSSIDer** (Windows/macOS): physische (pro AP/BSSID) und logische Sicht (pro SSID), Kanal-Interferenz/Co-Channel, Empfehlung bester Kanal, Export nach Chanalyzer.
- **Wi-Fi Analyzer** (Android): Kanalgraph mit überlappenden "Glocken", Grid-/Graph-Ansicht.
- **Apple AirPort Utility** (iOS, Scanner muss in den Einstellungen aktiviert werden): SSID, BSSID, RSSI, Kanal, zuletzt gesehen; CSV-Export.
- Einsatz: zu viele APs auf demselben Kanal (CCI), schlechte Kanalwahl, Abdeckung eines SSID in einem Bereich, fremde Netze.

### RSSI, Rauschen, SNR

- **RSSI** in dBm (negativ; −40 sehr stark, −67 gut, −80 schwach, −90 kaum nutzbar). Jede 3 dB = Faktor 2 Leistung, 10 dB = Faktor 10.
- **Noise Floor** typischerweise −90 bis −95 dBm.
- **SNR (dB) = Signal (dBm) − Noise (dBm)**. Beispiel: −67 dBm − (−92 dBm) = 25 dB.
- Cisco-Designempfehlung für Voice/Echtzeit: Zellrand ca. **−67 dBm** und **SNR ≥ 25 dB**; Daten tolerieren weniger (ca. −72 dBm / 20 dB). Niedriger SNR → niedrigere MCS/Datenrate, mehr Retries.
- RSSI ist hersteller-spezifisch skaliert; Vergleich verschiedener Clients nur grob.

### Kanäle und Interferenz

- 2,4 GHz: Kanalmittenabstand 5 MHz, Kanalbreite 20 MHz (OFDM) bzw. 22 MHz (DSSS). Nur **1, 6, 11** überlappen sich nicht (Nordamerika; Europa erlaubt 1–13). 40 MHz im 2,4-GHz-Band ist nicht sinnvoll.
- 5 GHz: 20-MHz-Kanäle überlappen nicht (36, 40, 44 …); Channel Bonding 40/80/160 MHz reduziert die Zahl unabhängiger Kanäle; DFS-Kanäle (Radar) können Kanalwechsel erzwingen.
- **Co-Channel Interference (CCI)**: APs/Zellen auf demselben Kanal hören sich → teilen sich die Airtime (CSMA/CA wartet), Durchsatz sinkt; eigentlich "Contention". Abhilfe: andere Kanäle, Sendeleistung senken, weniger APs/SSIDs, Abstand.
- **Adjacent Channel Interference (ACI)**: überlappende Nachbarkanäle (z. B. 1 und 3) oder sehr nahe APs mit hoher Leistung → Frames werden zerstört (Rauschen statt sauberer Erkennung). Abhilfe laut Kurs: Leistung reduzieren; generell nur nicht-überlappende Kanäle.
- Zu viele SSIDs: jeder SSID sendet eigene Beacons (Standard ~102,4 ms) zur niedrigsten Mandatory Rate → Airtime-Verschwendung; Faustregel max. 3–4 SSIDs.

## Packet Analysis

- Wenn andere Tools nicht reichen: Paketmitschnitt dekodiert jeden Frame.
- Zwei Wege: **kabelseitig** mit SPAN/RSPAN/ERSPAN (sieht beim Local-Mode-AP CAPWAP-gekapselten Verkehr zwischen AP und WLC; beim 9800 auch per EPC) oder **über die Luft** (over the air) mit einem AP im **Sniffer-Modus** (am WLC: Sniffer-Modus aktivieren, Band/Kanal wählen, IP des Analyse-PCs angeben) oder mit einem eigenen Sniffer-Adapter.
- Over-the-Air-Capture-Grundregeln (eigenes Wissen, über den Kurs hinaus):
  - Der Adapter muss im **Monitor-Modus (RFMON)** laufen. **Promiscuous** reicht bei WLAN nicht – dann sieht man nur Frames des eigenen BSS, ohne 802.11-Header-Details.
  - Ein Adapter hört **genau einen Kanal** (plus gewählte Breite). Kanal und Kanalbreite/Primärkanal müssen zum AP passen; Client roamt auf einen anderen Kanal → Mitschnitt reißt ab. Mehrere Adapter für mehrere Kanäle.
  - Der Adapter muss den PHY des Clients beherrschen (Spatial Streams, 802.11ac/ax/be), sonst kann er High-Rate-Datenframes nicht dekodieren.
  - Nahe am Client messen (man sieht, was der Client sieht).
  - **Radiotap-Header** (bzw. PPI/PEEKREMOTE beim Cisco-Sniffer-AP): Metadaten je Frame – Kanal, Frequenz, Datenrate/MCS, RSSI, Noise. Diese Infos stehen nicht im 802.11-Frame selbst.
  - Verschlüsselte Daten (WPA2-PSK) kann Wireshark nur mit PSK/Passphrase + SSID **und** mitgeschnittenem 4-Way Handshake entschlüsseln; WPA2-Enterprise nur mit PMK; WPA3-SAE praktisch nicht.
  - Nützliche Wireshark-Filter: `wlan.fc.type_subtype == 0x04` Probe Request, `0x05` Probe Response, `0x08` Beacon, `0x0b` Authentication, `0x00` Association Request, `0x01` Association Response, `0x0a` Disassociation, `0x0c` Deauthentication; `eapol` (4-Way Handshake/EAP), `wlan.addr == <client-mac>`; `bootp`/`dhcp`.
- **Wireshark**: Open Source; Windows, Linux, macOS, Solaris, FreeBSD, NetBSD. Kurs: für WLAN-Captures AirPcap Nx nötig – veraltet (AirPcap eingestellt); heute Monitor-Modus unter Linux/macOS (Wireless Diagnostics → Sniffer), Npcap mit geeigneten Adaptern unter Windows oder AP im Sniffer-Modus.
- **MetaGeek Eye P.A.** (Windows, eingestellt): Captures mit AirPcap Nx in beiden Bändern; zeigt Frames nach Typ (Control/Management/Data) und Airtime-Verbraucher; liest auch Wireshark-/OmniPeek-Dateien.
- **OmniPeek**, **AirMagnet**: kommerzielle Analyzer.

## Cisco AireOS GUI and CLI Tools (Legacy)

### GUI – Monitoring Dashboard (AireOS 8.x)
- Standard-Startseite nach Login: **Monitoring Dashboard** (Network Summary). Oben **numerische Statistiken**: Wireless Networks (WLANs aktiv/inaktiv), Wired Networks (RLANs/Clients), Access Points, Active Clients (2,4/5 GHz), Rogues (APs/Clients), Interferers (2,4/5 GHz). Klick führt in die Advanced-Ansicht.
- **Graphische Widgets**: Access Points (Clients, Traffic, Durchsatz → Access Point View mit Radio-Details), Operating Systems, Applications, Clients, Top WLANs.
- Linker Monitoring-Bereich: Network Summary (Access Points → Tabs Clients, RF Troubleshooting mit Nachbar-/Rogue-APs, CleanAir-Störer, Tools/Restart; Clients → Client View).
- **Client View**: Infografik 1 = Verbindungsstufe (Connection Stage), Infografik 2 = Verbindungsweg Controller → Client. Tools: **Ping Test**, **Connection** (Verbindungslogs), **Event Log** (exportierbar), **Packet Capture**.
- Weitere Menüs: Rogues, Interferers, Wireless Dashboard (AP/Client Performance), **Best Practices** (Compliance; pro Parameter "Fix it Now", "Restore Default", "Manual Configuration", "Ignore").
- Klassische Advanced-GUI: Monitor Summary (Controller Summary, Most Recent Traps, AP Summary, Client Summary); Wireless > All APs (Uptime, Associated Time – kürzlich neu gejointe APs unten in der Liste); Management (Message Logs, Trap Logs, Tech Support); Monitor > CleanAir (Störer pro Radio/AP, Severity, Duty Cycle; Worst Air Quality Report; AQI-Report).
- Monitor > Clients > Detail: Client Properties (MAC, IP, VLAN, Mobility Role, Policy Manager State, Security Policy Completed), AP Properties (AP MAC/Name, AP Type, WLAN Profile, Status, Association ID, 802.11 Authentication, Reason Code, Status Code, Short Preamble, PBCC, Channel Agility, Timeout, Data Switching), Client Statistics (RSSI, SNR, Retries), Security Information (Policy Type RSN/WPA2, Cipher CCMP, EAP-Typ), QoS-Properties.

### AireOS CLI
```
config paging disable                 ! vor dem Mitloggen (keine --More--)
show client summary                   ! MAC, AP, WLAN-ID, Radio
show client detail <mac>              ! Username, AP, SSID, IP, VLAN, Datenraten, Mobility State, Security, Policy Manager State, RSSI, SNR
show client ap 802.11{a|b} <ap>|all   ! Clients pro Radio
show traplog                          ! letzte Traps
show logging                          ! Message Log + Log-Level
show 802.11{a|b}                      ! Radio-Netzwerkeinstellungen (Status, Raten, Power, Kanal)
show wlan <id>                        ! WLAN-Einstellungen (Name, Security, Status)
show ap config 802.11{a|b} [summary] <ap>
show ap config general <ap>
show ap join stats summary all
show ap summary
show ap wlan 802.11{a|b} <ap>         ! WLAN-IDs, Interfaces, BSSID
debug client <mac>                    ! Makro: aktiviert mehrere Client-Debugs (laut Kurs acht) + MAC-Filter
debug disable-all
```
- `debug client <mac>` kombiniert die wichtigsten Debugs zu Association/Authentication/DHCP (u. a. dot11, dot1x, pem, dhcp) und filtert auf eine MAC → weniger Ausgabe, schont den Controller.
- `show client detail`: **Policy Manager State RUN** = fertig; **Security Policy Completed Yes** = 802.1X/4-Way erfolgreich; Mobility State Local/Anchor/Foreign; RSSI/SNR für die HF-Qualität. Beispiel (gekürzt):
```
Client MAC Address............ 00:40:96:aa:6f:71
Client State.................. Associated
Wireless LAN Id............... 1
BSSID......................... f0:25:72:3c:40:1f
Channel....................... 36
IP Address.................... 10.9.4.101
Reason Code................... 1
Status Code................... 0
Mobility State................ Local
Security Policy Completed..... Yes
Policy Manager State.......... RUN
Policy Type................... WPA2
Radio Signal Strength Indicator.... -75 dBm
Signal to Noise Ratio.............. 21 dB
```

## Catalyst 9800 (aktuelle Plattform, eigenes Wissen)

```
show wireless client summary                         ! MAC, AP, WLAN, State (Run, IP Learn, Authenticating, Webauth Pending ...)
show wireless client mac-address <mac> detail        ! Policy Manager State, VLAN, IP, AP, RSSI/SNR, Security, Session Timeout
show wireless exclusionlist                          ! ausgeschlossene Clients
show wlan summary / show wlan name <wlan>            ! WLAN-Status, Security, Broadcast
show ap summary / show ap tag summary                ! Tags pro AP (Policy/Site/RF)
show wireless tag policy detailed <tag>              ! WLAN-zu-Policy-Profile-Zuordnung
show wireless profile policy detailed <profile>      ! VLAN, Central Switching usw.
show aaa servers                                     ! RADIUS-Server State UP/DEAD, Zähler
show wireless mobility summary                       ! Mobility-Peers, Control/Data Link Status
debug wireless mac <mac> [internal] [monitor-time <s>]   ! Radioactive Trace starten (Default 1800 s)
no debug wireless mac <mac>                          ! stoppen → ra_trace-Datei in bootflash:
show logging profile wireless start last 30 minutes filter mac <mac> to-file bootflash:client.txt   ! Always-On-Tracing nachträglich auswerten
```
- **Client-Zustände (Policy Manager)** auf dem 9800: Associating → L2 Authentication (Authenticating) → Mobility → **IP Learn** → (Webauth Pending) → **Run**. Hängt ein Client in IP Learn, bekommt er keine DHCP-Adresse (VLAN falsch, kein DHCP-Relay, Scope leer, Trunk fehlt). Hängt er in Authenticating, scheitert 802.1X/PSK. Webauth Pending = Portal-Login fehlt.
- **Radioactive Tracing (RA Trace)**: bedingtes Debugging pro MAC über alle Prozesse (wncd, wncmgrd, sman, dot1x, aaa …) hinweg, ohne globale Debugs – auch in Produktion vertretbar. GUI: Troubleshooting > Radioactive Trace (MAC hinzufügen, Start, Generate für die letzten x Minuten). Ergebnis als Datei (`ra_trace_MAC_...`), auswertbar mit dem Cisco Wireless Debug Analyzer.
- **Always-On Tracing**: Der 9800 schreibt ständig Traces auf Notice-Level; `show logging profile wireless ... filter mac` holt nachträglich Ereignisse eines Clients, auch wenn vorher kein Debug lief. Ohne `start last <n> {minutes|hours|days}` geht der Befehl standardmäßig nur **10 Minuten** zurück (Cisco 213949).
- **Syslog-Beispiele** (Lab): `%DOT1X-5-FAIL: ... wncd: Authentication failed for client (2cfd.a161.b0ce) with reason (AAA Server Down)`.
- GUI: Monitoring > Wireless > Clients (Zustand), Monitoring > Wireless > AP Statistics (Tags), Troubleshooting > Syslog, Ping and Traceroute, Radioactive Trace, Packet Capture.
- **AAA-Kette 9800**: WLAN → Authentication Method List (z. B. dot1x-method) → Server Group (ISE-Group) → RADIUS Server (IP + Shared Secret). Fehlt die Method List am WLAN, weiß der WLC nicht, wohin er EAP schicken soll.

### Catalyst Center Assurance – Client 360
- Pro Client: Health Score (1–10), Onboarding-Zeitstrahl (Association, Authentication, DHCP mit Dauer und Fehlergrund), Connectivity (RSSI, SNR, Datenrate), Event Viewer, Path Trace, Application Experience, **Intelligent Capture** (OTA-Captures/Spektrum vom AP, je nach AP/Lizenz), Time Travel (Zustand zu einem früheren Zeitpunkt).
- Vorteil: Ursache auch für vergangene Probleme sichtbar, ohne vorher Debugs gesetzt zu haben.

## Cisco Wireless Config Analyzer Express (WCAE)

- Cloudbasierter Nachfolger des **WLCCA** (Wireless LAN Controller Config Analyzer, früher Windows-Programm). Unterstützt **AireOS** und **Catalyst 9800**. URL: cway.cisco.com/tools/WirelessAnalyzer/ (Analyse läuft lokal im Browser).
- Eingabe: AireOS `show run-config` (bzw. `show tech`, `show log`), 9800 `show tech wireless`.
- Führt laut Kurs mehr als 184 Konfigurationsprüfungen durch (Security, WLANs, Mobility, Mesh, Flex, AP, RF), abgeleitet aus TAC-Erfahrung.
- Zusätzlich: **AP Data Summarization** (AP-Hardware und Modi), **RF Stats** (RF-Statistik pro WLC, AP-Gruppe/Flex-Gruppe), **RF Health** (vereinfachter Gesundheitsbericht: Co-Channel/Side-Channel, Noise, Low SNR Clients, Radio Utilization, CleanAir-Störer je Low/Medium/High), **Log File Summarization** (Meldungen mit Anzahl, erster/letzter Zeitpunkt).
- Keine Analyse von Debug-Ausgaben (dafür: Cisco **Wireless Debug Analyzer**, ebenfalls auf cway.cisco.com) und keine Site-Survey-Auswertung.

## Common Wireless Client Connectivity Issues (Kategorien)

1. **Client to AP Connectivity**: Antennen und HF-Interferenz, AP-Stromversorgung (PoE), Client-Association mit dem AP.
2. **WLAN Configuration**: netzseitige und clientseitige Fehler.
3. **Infrastructure Configuration**: VLAN/Trunk, AP-Join am WLC, Zeitsynchronisation, RF-/Mobility-Gruppen, WLC-Security-Einstellungen (Client disabled/excluded).

Faustregel: **Viele Nutzer betroffen → Netzseite** (WLC-Konfiguration, RADIUS, DHCP). **Ein oder zwei Nutzer → Client** (Profil, Passwort, Treiber, falsches SSID).

## Client to AP Connectivity

### Antennen
- Maximal unterstützte Anzahl Antennen nutzen, gleiche Antennentypen, gleiche Ausrichtung; APs mit internen Antennen horizontal (Decke) montieren.
- Abstand externer Antennen ca. ½ bis 1 Wellenlänge (Multipath): 2,4 GHz λ ≈ 12,5 cm → ½ λ ≈ 6,25 cm (Kurs: ~6,35 cm); 5,2 GHz λ ≈ 5,8 cm → ½ λ ≈ 2,9 cm (Kurs ~2,8 cm).
- High-Gain-Antennen nur zertifiziert (FCC/ETSI) für das jeweilige Gerät.

### HF-Ausbreitung / Interferenz
- Quellen: fremde 802.11-Netze, Mikrowelle, Funktelefone, Bluetooth, TDD-Telefone, Funkkameras.
- CCI → Kanal auf nicht-überlappenden Kanal ändern oder AP versetzen; ACI → Leistung senken. Nicht-802.11-Störer mit CleanAir/Spektrumanalyse finden und entfernen.
- inSSIDer zeigt, ob zu viele APs auf einem Kanal sind und wie ausgelastet der Kanal ist.
- Schwaches Signal (Wände, Metall absorbieren/reflektieren) → intermittierende Verbindung; Leistung erhöhen oder Antennen ändern – aber siehe Power-Mismatch.

### Typische Fehlerbilder Client ↔ AP (eigenes Wissen)
- **Sticky Client**: Der Client entscheidet über das Roaming und bleibt an einem weit entfernten AP mit schwachem RSSI, obwohl ein besserer AP da ist. Abhilfe: niedrige Datenraten deaktivieren (höhere niedrigste Mandatory Rate → kleinere Zellen), **802.11k** (Neighbor Report) und **802.11v** (BSS Transition Management), Cisco **Optimized Roaming**, Zellgrößen per TPC/RRM; nicht: AP-Leistung erhöhen.
- **Power-Mismatch** (asymmetrischer Link): AP sendet mit hoher Leistung (z. B. 20 dBm), Client nur mit ca. 10–15 dBm. Client sieht volle Balken, aber der AP hört den Client schlecht → Retries, Abbrüche, Upstream schlecht. Abhilfe: AP-Leistung an Client-Leistung angleichen, mehr APs mit weniger Leistung.
- **Data-Rate-Konfiguration**: Ein Client muss **alle Mandatory (Basic) Rates** unterstützen, sonst wird die Association abgelehnt (802.11-Status 18). Beacons und Broadcasts gehen mit der niedrigsten Mandatory Rate. 802.11b-Raten (1/2/5,5/11) deaktivieren → reine 802.11b-Clients können nicht mehr assoziieren; Gewinn: weniger Airtime-Verbrauch, kleinere Zellen.
- **Band-Probleme**: WLAN/Radio Policy nur 5 GHz → 2,4-GHz-only-Clients sehen den SSID nicht. 6 GHz verlangt WPA3/OWE und Wi-Fi-6E-fähige Clients. **Band Select** verzögert Probe Responses im 2,4-GHz-Band, um Dual-Band-Clients nach 5 GHz zu schieben (kann Voice-Clients beim Roaming stören).
- **Roaming-Probleme**: Mobility-Gruppenname falsch, Mobility-Tunnel down (9800: Control/Data Link nicht Up, Ports UDP 16666/16667 blockiert), unterschiedliche WLAN-Konfiguration auf den WLCs, volle 802.1X-Reauthentifizierung bei jedem Roam (Abhilfe: 802.11r FT, OKC/CCKM, PMK-Caching).
- **AP-Strom (PoE)**: 802.3af liefert 15,4 W am Switch, 12,95 W garantiert am Gerät; 802.3at (PoE+) 30 W / 25,5 W; 802.3bt Typ 3 60 W / 51 W, Typ 4 90 W / 71 W (Cisco UPOE/UPOE+). Zu wenig Leistung → AP startet nicht oder läuft eingeschränkt (Radios/Spatial Streams/USB aus). Prüfen: `show power inline`. AC-Netzteil und PoE nicht gleichzeitig. Bei Pre-Standard-Switches oder Power Injector am WLC einstellen (AP > Advanced).

### Client Association (AireOS-Codes)
- Erster Anlaufpunkt bei Client-Problemen: WLC-Startseite (Monitoring Dashboard), dann Monitor > Clients.
- Nach dem ersten Associations-Versuch steht der Client in der Client-Datenbank; `show client detail` zeigt IP, Authentifizierungsmethode, VLAN, Mobility State, Reason/Status Code, ob **Security Policy Completed**.
- **Reason Codes** laut Kurs (Kurs-Bezeichnungen, teils von IEEE 802.11 abweichend, siehe Fehlerliste):

| Code | Name | Bedeutung (Kurs) |
|---|---|---|
| 0 | noReasonCode | normaler Betrieb |
| 1 | unspecifiedReason | assoziiert, aber nicht mehr autorisiert |
| 2 | previousAuthNotValid | assoziiert, aber nicht autorisiert |
| 3 | deauthenticationLeaving | AP offline, Client deauthentifiziert |
| 4 | disassociationDueToInactivity | Kurs: Session Timeout überschritten (IEEE: Inaktivität) |
| 5 | disassociationAPBusy | AP ausgelastet (z. B. Load Balancing) |
| 6 | class2FrameFromNonAuthStation | Daten vor Authentifizierung |
| 7 | class2FrameFromNonAssStation | Daten vor Association (IEEE: Class-3-Frame) |
| 8 | disassociationStaHasLeft | Client von OS auf anderen AP verschoben |
| 9 | staReqAssociationWithoutAuth | noch nicht autorisiert, versucht zu assoziieren |
| 99 | missingReasonCode | kurzzeitig unbekannter Zustand |

- **Status Codes** (Cisco-Client-Status): 0 idle, 1 aaaPending, 2 authenticated, 3 associated, 4 powersave, 5 disassociated, 6 tobedeleted, 7 probing, 8 disabled (vom WLC für eine definierte Zeit ausgeschlossen).
- Attribute: **Short Preamble** (für manche Telefone, z. B. SpectraLink, deaktivieren), PBCC, Channel Agility, **Timeout** (Session Timeout → erzwungene Reauthentifizierung), **Data Switching** (local/central, nur FlexConnect).

## Verbindungsphasen eines WLAN-Clients (Gesamtablauf, eigenes Wissen)

| Phase | Frames | Typischer Fehler | Sichtbar als |
|---|---|---|---|
| 1 Discovery | Beacon (passiv) oder Probe Request/Response (aktiv) | SSID deaktiviert, nicht im Policy Tag, falsches Band, Broadcast aus, Schreibweise | Client sieht SSID nicht; WLC kennt Client nicht |
| 2 802.11 Authentication | Open System Auth (2 Frames) | selten; WPA3-SAE-Commit/Confirm-Fehler | – |
| 3 Association | Association Request/Response (AID) | Mandatory Rate nicht unterstützt, AP voll, Client excluded | Status ≠ 0 in Assoc Response |
| 4 802.1X/EAP (Enterprise) | EAPOL ↔ WLC ↔ RADIUS | RADIUS nicht erreichbar, Shared Secret, Method List fehlt, Zertifikat, Passwort | 9800: Authenticating, Syslog DOT1X-5-FAIL |
| 5 4-Way Handshake | EAPOL-Key M1–M4 | falscher PSK (MIC-Fehler M2) | Client bricht ab, Exclusion |
| 6 Mobility / L3 | (WLC-intern), DHCP | falsches VLAN/Interface, kein DHCP-Relay, Scope leer, Trunk fehlt | 9800: IP Learn; Client 169.254.x.x |
| 7 (WebAuth) | HTTP-Redirect | Portal/DNS/ACL | Webauth Pending |
| 8 RUN | Daten | – | Run/RUN |

## WLAN Configuration

### Netzseitig (viele Nutzer betroffen → zuerst WLC prüfen)
- **SSID falsch geschrieben** (Groß-/Kleinschreibung zählt) → vorkonfiguriertes Profil verbindet nicht.
- **SSID nicht aktiviert** → Clients sehen/erreichen ihn nicht.
- **Radio Policy falsches Band** → Single-Band-Clients sehen den SSID nicht.
- **Interface/Interface Group falsch** (9800: VLAN im Policy Profile) → IP im falschen Subnetz bzw. keine IP.
- **Security passt nicht** (Authentifizierung/Verschlüsselung) → Client kann nicht verbinden; prüfen, ob Clients das Verfahren unterstützen.
- **RADIUS nicht erreichbar/falsch konfiguriert** → 802.1X scheitert; ISE braucht den WLC als Network Device (IP + Shared Secret), der WLC den RADIUS-Server mit korrekter IP und Secret.
- **Datenraten nicht unterstützt** → Client muss alle Mandatory Rates können.

### Clientseitig (ein, zwei Nutzer)
- Richtiges SSID? (Mitarbeiter am Contractor-SSID → Benutzer nicht in dessen Datenbank)
- Richtiges Band/Kanal? (Kurs; real wählt der Client den Kanal per Scan)
- Richtige Security (802.1X statt Open/PSK im Profil)?
- Bekommt er eine IP (DHCP-Scope erschöpft, Leases nicht freigegeben)?
- Tippfehler/altes Passwort.

## Infrastructure Configuration

- **VLAN/Trunk**: typisch mindestens vier VLANs (Management, Mitarbeiter, Contractor, Gast). Fehler:
  - Trunk Switch ↔ WLC erlaubt nicht alle Client-VLANs → Clientverkehr kommt nicht an, ggf. auch AP ↔ WLC gestört.
  - AP-Switchport im falschen VLAN → AP/Clients falsches Netz, Authentifizierung scheitert.
  - Native VLAN Switchport ≠ AP-Erwartung → AP kann nicht joinen.
  - Dynamic Interfaces (AireOS) jeweils eigenes VLAN/Subnetz.
- **AP-Discovery**: DHCP-Adresse im richtigen Subnetz, Option 43, DNS `CISCO-CAPWAP-CONTROLLER`, Management-Interface (AireOS) bzw. Wireless Management Interface (9800, Kurs: "WCM") erreichbar.
- **AP-Join**: Uhrzeit außerhalb Zertifikatsgültigkeit (NTP!), Regulatory Domain passt nicht, Firewall blockiert CAPWAP (UDP 5246/5247), maximale AP-Anzahl erreicht.
- **Zeit**: NTP auf WLC, Switches, ISE; Zeitzone/Sommerzeit. Betrifft Redundanz, Logging, AP-Join (Zertifikate), Mobility, EAP-TLS.
- **RF Group** (RRM): max. 20 WLCs; Name muss exakt passen (Groß-/Kleinschreibung, Leerzeichen); Netzwerkpfad für RF-Hellos.
- **Mobility Group** (Roaming): Name exakt gleich; IPs (public/private) erreichbar; AireOS: Management-MACs korrekt; Control und Data Link "Up".
- **WLC Security Settings**:
  - **Client disabled** (manuell, AireOS: Security > AAA > Disabled Clients) → kann nicht assoziieren, bis entfernt.
  - **Client excluded** (automatisch, Client Exclusion Policies unter Security > Wireless Protection Policies): zu viele 802.11-Association-Fehler, 802.11-Authentication-Fehler, 802.1X-Fehler, WebAuth-Fehler (zusätzlich IP-Theft/IP-Reuse). Exclusion und Timeout pro WLAN (AireOS Advanced-Tab; Default 60 s vor AireOS 8.5, ab 8.5 180 s) bzw. pro Policy Profile (9800, `exclusionlist timeout`, Default 60 s). Monitor zeigt "Excluded"; warten oder Eintrag entfernen.

## Discovery 19 (Lab): Troubleshoot Wireless Client Connectivity

Topologie: Client PC, Campus AP, Campus 9800 WLC (10.10.10.30; Interfaces auch 10.10.30.30 und 10.10.40.30), Campus Switch, Cisco ISE (10.10.10.60), Gateway Router (10.10.10.1/10.10.30.1/10.10.40.1). Location "Campus" mit WLANs ENCOR-Sales (PSK, VLAN 30) und ENCOR-Accounting (802.1X über ISE, VLAN 40).

**Fall 1 – Sales-SSID nicht sichtbar, dann keine IP**
1. Client sieht ENCOR-Sales nicht. Dashboard: 1 AP, beide Radios up. WLAN ist aktiviert, Broadcast SSID enabled.
2. Monitoring > Wireless > AP Statistics: AP hat **default-policy-tag/default-site-tag/default-rf-tag** und Default AP Profile – die Campus-Tags mit den WLANs fehlen → SSID wird nicht ausgestrahlt.
3. Fix: Configuration > Wireless Setup > Basic > Location Campus > AP Provisioning: AP hinzufügen, Apply. AP baut CAPWAP neu auf (ca. 60 s "0 Joined APs").
4. Danach Verbindung mit PSK Cisco123 – Client hängt in **IP Learn** (keine DHCP-Adresse).
5. Ursache: WLAN in der Location an **VLAN 11** statt VLAN 30 gebunden (kein DHCP in VLAN 11). Fix: VLAN 30 wählen, Apply → Client erhält 10.10.30.x, Ping auf 10.10.30.1.
- Mögliche Ursachen für IP Learn allgemein: DHCP-Server falsch, kein DHCP-Relay (ip helper-address), ACL blockiert DHCP, WLAN-VLAN/Trunk falsch.

**Fall 2 – Accounting-802.1X scheitert**
1. Client (PEAP, accounting_user) kann nicht verbinden; Monitoring > Clients zeigt nichts.
2. Troubleshooting > Syslog: `%DOT1X-5-FAIL ... reason (AAA Server Down)`.
3. Ping vom WLC zu ISE 10.10.10.60 erfolgreich. Configuration > Security > AAA: RADIUS-Server "ISE-Server" hat falsche IP **10.10.10.66** → korrigiert auf 10.10.10.60.
4. Immer noch dieselbe Meldung: Im WLAN (Security > AAA) ist **keine Authentication List** zugewiesen. Kette: WLAN → Method List `dot1x-method` → Gruppe `ISE-Group` → Server `ISE-Server`. Fix: dot1x-method zuweisen → Client erhält 10.10.40.x.
- Lehre: Ping (ICMP) beweist nicht, dass RADIUS (UDP 1812/1813) funktioniert oder das Shared Secret stimmt; mehrere Fehler können sich überlagern – nach jeder Korrektur erneut testen.

## Fehler/Ungenauigkeiten im Kurs

1. **Packet Analysis als "Layer 3"**: 802.11-Analyzer arbeiten auf Layer 2 (802.11-MAC-Header, Management/Control/Data-Frames) und dekodieren darüber alle Schichten. (IEEE 802.11-2020, Clause 9)
2. **"Promiscuous mode" für WLAN-Captures**: Für Over-the-Air-Mitschnitte ist der **Monitor-Modus (RFMON)** nötig; Promiscuous liefert nur Frames des eigenen BSS ohne Radio-Metadaten. (Wireshark Wiki "CaptureSetup/WLAN")
3. **AirPcap Nx "required" für Wireshark-WLAN-Captures**: AirPcap ist seit Jahren eingestellt; heute Monitor-Modus unter Linux/macOS, Npcap mit geeigneten Adaptern oder ein Cisco-AP im Sniffer-Modus. Ebenso eingestellt: MetaGeek Eye P.A., Cisco Spectrum Expert. (Wireshark Wiki, MetaGeek)
4a. **Reason Code 6 "Daten vor Authentifizierung"**: IEEE: "Class 2 frame received from nonauthenticated STA" – Class-2-Frames sind (Re)Association-/Disassociation-Frames, keine Datenframes (Daten = Class 3). (IEEE 802.11-2020, Table 9-49)
4. **Reason Code 7 "class2FrameFromNonAssStation"**: IEEE 802.11 definiert Reason 7 als "Class 3 frame received from nonassociated STA". (IEEE 802.11-2020, Table 9-49)
5. **Reason Code 4 = "Session Timeout überschritten"**: Reason 4 bedeutet Disassociation wegen **Inaktivität** (Idle Timeout), nicht Session Timeout. (IEEE 802.11-2020, Table 9-49)
6. **Reason Code 3 = "AP ging offline"**: IEEE: Deauthentifiziert, weil die sendende Station die ESS verlässt – kann AP oder Client sein. Reason 8 bedeutet allgemein "Disassociated because sending STA is leaving BSS", nicht nur Load Balancing.
7. **Status "disabled … by the operating system"**: Ausgeschlossen bzw. deaktiviert wird der Client vom **WLC** (Client Exclusion), nicht vom Betriebssystem. Außerdem widersprüchlich: aaaPending einmal "AAA transaction completed", in der Tabelle "Completing an AAA transaction" (Letzteres ist richtig).
8. **Lab-Fall 2 Schluss "erfolgreich per WebAuth authentifiziert"**: Das Accounting-WLAN nutzt 802.1X (PEAP) über ISE, kein WebAuth.
9. **Ping zum ISE "zeigt Konnektivität zum RADIUS-Server"**: ICMP prüft nicht UDP 1812/1813 und nicht das Shared Secret (`show aaa servers`, `test aaa group ...` bzw. ISE Live Logs nutzen).
10. **Clientseitig "manuell anderen Kanal am Adapter konfiguriert"**: Im Infrastruktur-Modus wählt der Client den Kanal per Scan; den Kanal bestimmt der AP. Kanäle 1/6/11 sind die US-Empfehlung, kein Muss für Clients.
11. **802.3af "12,95 W nach Kabelverlust bei langen Kabeln"**: 12,95 W ist die vom Standard garantierte Leistung am Endgerät bei 100 m; 802.3at liefert 25,5 W am Endgerät (30 W am Switch). 802.3bt (60/90 W) fehlt im Kurs, wird aber von aktuellen Wi-Fi-6E/7-APs oft benötigt.
12. **Antennenabstand 2,4 GHz ~6,35 cm**: ½ λ bei 2,4 GHz ≈ 6,25 cm (λ = c/f ≈ 12,5 cm) – geringfügige Abweichung.
13. **Plattform**: Der Kurs erklärt die Werkzeuge an AireOS (Legacy). Auf dem Catalyst 9800 heißen die Gegenstücke `show wireless client mac-address … detail`, Radioactive Tracing (`debug wireless mac`), `show logging profile wireless`; in Catalyst Center Client 360.

## Bilder

- `bilder/18-wlan-ts/01-tool-layer.svg` – Werkzeugkategorien (Spektrum, Scanner, Packet Capture, WLC-Tools) mit dem, was sie sehen und nicht sehen.
- `bilder/18-wlan-ts/02-kanal-24.svg` – 2,4-GHz-Kanäle 1–13 mit Überlappung, nicht-überlappende Kanäle 1/6/11, CCI vs. ACI.
- `bilder/18-wlan-ts/03-interferer.svg` – Nicht-Wi-Fi-Störer im Spektrum (Mikrowelle, Bluetooth, Videobrücke) mit Duty Cycle; DECT außerhalb des WLAN-Bands.
- `bilder/18-wlan-ts/04-rssi-snr.svg` – RSSI-Skala, Noise Floor und SNR-Rechnung mit Zielwerten.
- `bilder/18-wlan-ts/05-phasen.svg` – Verbindungsphasen Probe → Auth → Assoc → 802.1X → 4-Way → DHCP → RUN mit typischem Fehler je Phase.
- `bilder/18-wlan-ts/06-ota-capture.svg` – Over-the-Air-Capture: Monitor-Modus, ein Kanal, Radiotap-Header, Entschlüsselungsvoraussetzungen.
- `bilder/18-wlan-ts/07-fehlerorte.svg` – Fehlerorte in der Topologie: Client↔AP, WLAN-Konfiguration, Infrastruktur.
- `bilder/18-wlan-ts/08-9800-tools.svg` – Werkzeugkette Catalyst 9800/Catalyst Center gegenüber AireOS.
- `bilder/18-wlan-ts/09-lab-faelle.svg` – Discovery 19: beide Fälle mit Symptom, Ursache, Fix; AAA-Kette WLAN → Method List → Group → Server.
- `bilder/18-wlan-ts/10-sticky.svg` – Sticky Client und Power-Mismatch mit Gegenmaßnahmen.
