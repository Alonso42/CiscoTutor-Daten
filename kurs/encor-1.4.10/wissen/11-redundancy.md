# Implementing Network Redundancy

Quelle: ENCOR 1.4.10 Student Guide, Seiten 109–115 (115 = Summary-Video; Summary Challenge und Answer Key nicht ausgewertet)
Topics: ENCOR-3.3.c (FHRP: HSRP, VRRP), ENCOR-1.1.b (High-Availability-Techniken: SSO, NSF, Stacking)

Hinweis: Abschnitte mit "(Ergänzung)" stehen nicht im Kurs. Sie stammen aus Cisco-Doku/RFCs bzw. aus dem Prüfprotokoll und decken prüfungsrelevante Lücken ab (GLBP-Details, VRRPv3, StackWise, NSR).

## 1. Warum Gateway-Redundanz? (S. 109)
- Ein Host schickt alles, was nicht im eigenen Subnetz liegt, an sein Default Gateway. Das Gateway ist statisch eingetragen oder per DHCP gelernt; Hosts betreiben normalerweise kein Routingprotokoll.
- Ein Host kennt typischerweise **genau ein** Gateway und passt sich Topologieänderungen nicht an.
- Beispiel aus der Kursgrafik: Router A (10.1.10.1) und Router B (10.1.10.2) bedienen beide 10.1.10.0/24, die PCs haben aber GW = 10.1.10.1. Fällt A aus, konvergiert das IGP zwischen den Routern zwar schnell, die PCs schicken aber weiter an die tote Adresse → Single Point of Failure, die redundante Topologie wird nicht genutzt.
- Gilt genauso für Layer-3-Switches (SVIs als Gateway).

## 2. FHRP-Grundprinzip (S. 110)
- Mehrere Router bilden einen **virtuellen Router** mit gemeinsamer **virtueller IP (VIP)** und **virtueller MAC (vMAC)**.
- Hosts tragen die VIP als Gateway ein; ARP auf die VIP liefert die vMAC. Welcher physische Router tatsächlich weiterleitet, ist für den Host unsichtbar.
- Das Protokoll wählt den weiterleitenden Router und regelt die Übernahme:
  1. Der Standby hört keine Hellos mehr vom aktiven Router.
  2. Der Standby übernimmt die Forwarding-Rolle.
  3. Weil VIP **und** vMAC mitwandern, merken die Endgeräte nichts (kein neuer ARP-Eintrag nötig).
- Drei FHRPs auf Cisco-Geräten:
  - **HSRP** – Cisco-proprietär, RFC 2281 (informational), ein Router leitet weiter.
  - **VRRP** – offener Standard (v2 RFC 3768, v3 RFC 5798, seit 2024 ersetzt durch RFC 9568 mit dem Begriff "Active Router" statt "Master"; v1 war RFC 2338), mehr als zwei Router sinnvoll, ein Router leitet weiter.
  - **GLBP** – Cisco, mehrere aktive Forwarder pro Gruppe → Lastverteilung (im Kurs nur genannt).

## 3. HSRP-Grundlagen (Discovery 12, S. 111)

### Lab-Topologie
- PC1/PC2 – ASW1/ASW2 – R1 (Et0/1 192.168.1.3) und R2 (Et0/1 192.168.1.2) – R3 – Server 192.168.4.22. Uplinks: R1 192.168.2.1/24 ↔ R3 .2.2; R2 192.168.3.1/24 ↔ R3 .3.2; R3 Et0/2 192.168.4.1/24.
- VIP 192.168.1.1, Gruppe 1, PCs 192.168.1.100/.101 mit GW 192.168.1.1. HSRP läuft auf den Routern (die IOL-Switches können kein HSRP).

### Rollen
| Rolle | Aufgaben |
|---|---|
| Active | beantwortet ARP für die VIP mit der vMAC, leitet Pakete an die vMAC weiter, sendet Hellos, kennt die VIP |
| Standby | sendet Hellos, überwacht den Active, übernimmt bei Ausbleiben der Hellos |
| Listen (weitere Router) | kennen die VIP, hören nur zu, senden keine regelmäßigen Hellos |
- Der "virtuelle Router" verarbeitet selbst keine Frames, er ist nur das IP/MAC-Paar.

### Konfiguration und Grundfakten
```
interface Ethernet0/1
 ip address 192.168.1.2 255.255.255.0
 standby 1 ip 192.168.1.1
 standby 1 priority 110
 standby 1 preempt
```
- Ohne Gruppennummer → Gruppe 0. Gruppennummern sind nur pro Interface bedeutsam; Best Practice: Gruppe = VLAN-Nummer (mit v2 bis 4095 möglich).
- HSRPv1-Hellos: Multicast 224.0.0.2, UDP 1985. Active und Standby senden Hellos.
- vMAC v1: `0000.0c07.acXX`, XX = Gruppe in Hex (Gruppe 1 → `0000.0c07.ac01`, Gruppe 50 → `...ac32`).
- `show ip arp` auf dem Active zeigt die VIP mit der vMAC.
- **Traceroute** zeigt die echte Interface-IP des Active, nicht die VIP → praktisch, um den gerade aktiven Router zu finden.
- Bei einem Wechsel sendet der neue Active Gratuitous ARPs (Kurs: drei), damit die Switches den neuen Port der vMAC lernen.
- ICMP-Redirects sollten auf HSRP-Interfaces aus sein (ein Redirect auf die physische Router-IP würde den Failover aushebeln).

### Priorität und Preemption
- Priorität 8 Bit (0–255, RFC 2281; IOS-Konfigurationsguides nennen als konfigurierbaren Bereich 1–255), Default 100; die höchste gewinnt, bei Gleichstand die höchste Interface-IP (im Lab mit Default-Prioritäten daher zunächst R1 = .3 Active).
- **Preempt ist bei HSRP standardmäßig aus**: Ein laufender Active bleibt Active, auch wenn ein Router mit höherer Priorität dazukommt. Neuwahl nur, wenn der Active ausfällt (fällt der Standby aus, wird nur ein neuer Standby gewählt).
- `standby 1 preempt` auf dem besseren Router erlaubt die Übernahme → `%HSRP-5-STATECHANGE: Ethernet0/1 Grp 1 state Standby -> Active`.
- `standby 1 preempt delay minimum 300`: Preemption erst nach 300 s, damit Routing/Uplinks nach einem Reboot stehen. Die Verzögerung muss länger als die Boot-/Konvergenzzeit sein; der Kurs nennt als Faustregel ca. 150 % der Bootzeit (nicht offiziell belegt).

### Timer
```
standby [gruppe] timers [msec] <hello> [msec] <hold>
standby 1 timers msec 200 msec 750      ! Lab-Beispiel
no standby 1 timers                     ! zurück auf Default
```
- Default Hello 3 s, Hold 10 s; Bereich in Sekunden: Hello 1–254, Hold bis 255 (größer als Hello); mit `msec` Millisekunden. Hold sollte mindestens das Dreifache des Hellos sein.
- Nicht konfigurierte Router lernen Timer (und VIP) aus den Hellos des Active. Zu kurze Timer bringen wenig, wenn das IGP langsamer konvergiert; außerdem CPU-Last.

### Zustände (S. 111)
| Zustand | Bedeutung |
|---|---|
| Initial | Start: HSRP läuft noch nicht (nach Konfigurationsänderung oder wenn das Interface hochkommt) |
| Listen | kennt die VIP, hört Hellos von Active/Standby |
| Speak | sendet Hellos, nimmt aktiv an der Wahl teil |
| Standby | Kandidat für Active, sendet Hellos |
| Active | leitet weiter, beantwortet ARP, sendet Hellos |
- Ablaufbeispiel: Router A startet allein → Listen → Speak → hört keinen Höheren → Standby → hört keinen Active → Active. Router B startet später, hört in Listen, dass es Active und Standby-Kandidaten gibt → wird Standby (ohne Preempt kein Wechsel trotz gleicher/höherer Priorität).

### Verifikation (eigene, gekürzte Beispiele)
```
R2# show standby brief
                     P indicates configured to preempt.
Interface   Grp  Pri P State   Active          Standby         Virtual IP
Et0/1       1    110 P Active  local           192.168.1.3     192.168.1.1
```
- Spalte `P` = preempt konfiguriert. `show standby` zeigt zusätzlich vMAC, Timer, Active/Standby-Adresse, Priorität, Tracking.
- Failover-Test im Lab: R2 Et0/1 shut → R2 geht nach Init, R1 wird Active, Standby "unknown". `debug standby events` zeigt die Zustandswechsel.

## 4. HSRP – erweiterte Funktionen (S. 112)

### Interface-/Object-Tracking
- Ohne Tracking verliert der Active seine Rolle nur, wenn sein HSRP-Interface oder der ganze Router ausfällt. Fällt nur sein **Uplink** aus, bleibt er Active → Verkehr läuft PC → R2 → LAN → R1 → Core (suboptimal).
- Lösung: Objekt definieren und an die Gruppe binden; geht das Objekt down, sinkt die Priorität um den Decrement-Wert (Default **10**). Damit der andere übernimmt, braucht **er** `preempt` (und für die Rückkehr auch der ursprüngliche Active).
```
track 1 interface Ethernet0/0 line-protocol
interface Ethernet0/1
 standby 10 ip 192.168.10.1
 standby 10 priority 110
 standby 10 preempt
 standby 10 track 1 decrement 20
```
- Rechnung Kursbeispiel: R2 110 − 20 = 90 < 100 (R1) → R1 übernimmt per Preempt.
- Rechenfalle: Decrement muss die Prioritätsdifferenz **überschreiten** (110 − 10 = 100 = Gleichstand → dann entscheidet die höhere IP, nicht der Decrement).
- Mehrere `track`-Zeilen pro Gruppe möglich, die Abzüge addieren sich (z. B. 120 mit 2 × 15: ein Uplink weg → 105, beide weg → 90).
- Objekte können auch Routen (`track 2 ip route 0.0.0.0 0.0.0.0 reachability`) oder IP-SLA-Proben sein. Ältere native Syntax (`standby 1 track Ethernet0/0 20`) gilt auf neuen Plattformen als überholt.
- Kontrolle: `show track 1`, `show standby` (Tracking-Zeilen mit Zustand).

### MHSRP – Lastverteilung mit mehreren Gruppen
- HSRP leitet pro Gruppe nur über einen Router. Bei Default-Prioritäten wird oft ein Switch Active für alle VLANs → nur ein Uplink genutzt.
- Lösung: pro VLAN eine Gruppe, abwechselnd Active, **STP-Root und HSRP-Active auf demselben Switch** (sonst Umweg über den Inter-Switch-Link):
```
Switch1: spanning-tree vlan 10 root primary / vlan 20 root secondary
 interface vlan 10: standby 10 ip 10.1.10.1, priority 110, preempt
 interface vlan 20: standby 20 ip 10.1.20.1, priority 90,  preempt
Switch2: spiegelbildlich (vlan 20 root primary, Gruppe 20 Prio 110, Gruppe 10 Prio 90)
```
- Auch in **einem** VLAN möglich: zwei Gruppen mit zwei VIPs auf demselben Interface, Hosts werden auf die beiden Gateways verteilt (z. B. per DHCP-Scopes).

### Authentifizierung
- Schutz gegen fremde Router, die per hoher Priorität Active werden (DoS bzw. Man-in-the-Middle).
- Klartext: `standby 1 authentication <string>` (max. 8 Zeichen, mitlesbar).
- MD5 (bevorzugt): `standby 1 authentication md5 key-string [0|7] <string>` – Hash über die Nachricht, Schlüssel wird nie übertragen; in der Running-Config als Typ 7 gespeichert (schwache Verschlüsselung).
- Oder Key Chain (mehrere Schlüssel, Gültigkeitszeiten):
```
key chain HSRP-KEYS
 key 1
  key-string MeinSchluessel
interface Ethernet0/1
 standby 1 authentication md5 key-chain HSRP-KEYS
```
- Alle Peers brauchen identische Einstellungen, sonst sieht jeder sich als Active.

### HSRP-Versionen
| | HSRPv1 | HSRPv2 |
|---|---|---|
| Default | ja | nein (`standby version 2`, Interface-Befehl ohne Gruppe) |
| Adressfamilie | IPv4 | IPv4 und IPv6 |
| Gruppen | 0–255 | 0–4095 |
| Hello an | 224.0.0.2, UDP 1985 | 224.0.0.102, UDP 1985 (IPv6: FF02::66, UDP 2029) |
| vMAC | `0000.0c07.acXX` (2 Hex-Stellen) | `0000.0c9f.fXXX` (3 Hex-Stellen); IPv6 `0005.73a0.0XXX` |
| Paket | – | zusätzliches 6-Byte-Identifier-Feld (Interface-MAC des Senders) |
- v1 und v2 sind **nicht** kompatibel; ein Interface fährt nur eine Version. IPv6-HSRP setzt v2 voraus (`standby 1 ipv6 autoconfig`).
- Grund für 224.0.0.102: 224.0.0.2 kollidiert mit CGMP-Verarbeitung; mit v2 können beide parallel laufen.
- vMAC-Rechnung: Gruppe 20 → v1 `0000.0c07.ac14`, v2 `0000.0c9f.f014`; Gruppe 300 → nur v2: `0000.0c9f.f12c`; Gruppe 4095 → `0000.0c9f.ffff`.

## 5. VRRP (Discovery 13, S. 113)

### Grundlagen
- Master ≈ HSRP-Active, Backup ≈ HSRP-Standby. Eine Gruppe hat einen Master und einen oder mehrere Backups.
- Priorität: konfigurierbar 1–254, Default 100, höchste gewinnt (Gleichstand → höchste IP).
  - **255** = Owner: Die VIP ist die echte Interface-Adresse dieses Routers; er ist immer Master, solange er läuft (Prioritäten der anderen sind dann egal).
  - **0** = Master tritt zurück (z. B. beim Herunterfahren) → Backups übernehmen sofort, ohne das Master Down Interval abzuwarten.
- Nur der **Master** sendet Advertisements: 224.0.0.18, **IP-Protokoll 112** (kein UDP), Intervall Default 1 s. TTL muss 255 sein → Pakete von außerhalb des Segments werden verworfen.
- **Preempt ist bei VRRP standardmäßig an.**
- Gruppe 1–255, Gruppennummer muss immer angegeben werden (kein Default wie HSRP-Gruppe 0).
- vMAC `0000.5e00.01XX` (XX = Gruppe hex, Gruppe 1 → `0000.5e00.0101`, Gruppe 10 → `...010a`).
- Lastverteilung wie MHSRP: mehrere VRRP-Gruppen mit unterschiedlichen Mastern und Gateways für verschiedene Clients.

### Master Down Interval (Rechnen!)
- Backup erklärt den Master für tot nach **Master_Down_Interval = 3 × Advertisement_Interval + Skew_Time**, Skew_Time = (256 − Priorität) / 256 s (VRRPv2, Intervall 1 s).
- Höhere Priorität → kleinerer Skew → dieser Backup übernimmt zuerst (keine Wahlkollision).

| Priorität | Skew | Master Down Interval |
|---|---|---|
| 254 | 0,0078 s | 3,008 s |
| 200 | 0,2188 s | 3,219 s |
| 110 | 0,5703 s | 3,570 s |
| 100 | 0,6094 s | 3,609 s |
| 1 | 0,9961 s | 3,996 s |
- Lab-Ausgabe: Backup R1 (Prio 100) zeigt "Master Down interval is 3.609 sec", Master R2 (Prio 110) zeigt 3.570 sec bzw. in `show vrrp brief` Spalte Time 3570 (ms).
- VRRPv3 (Ergänzung): Werte in Zentisekunden, Skew = ((256 − Prio) × Intervall) / 256, z. B. Prio 100 bei 100 cs → Skew = 156 × 100 / 256 ≈ 60,9 cs (ganzzahlig 60 cs), MDI ≈ 360 cs. RFC 9568 (ersetzt 5798) nennt dieselben Formeln als Skew_Time/Active_Down_Interval; Default-Intervall 100 cs, Preempt_Mode Default True, vMAC IPv4 `0000.5e00.01XX`, IPv6 `0000.5e00.02XX`.

### Millisekunden-Timer
- Nicht Teil von RFC 3768, Cisco-Erweiterung: `vrrp 1 timers advertise msec 200`. Nur zwischen Cisco-Geräten sinnvoll und nur mit Bedacht einsetzen.
- Kurs: auf Master und Backup konfigurieren. Cisco-Doku (siehe Prüfprotokoll): Backups übernehmen msec-Werte nicht in die Anzeige – `show vrrp` auf dem Backup zeigt "Master Advertisement interval" immer 1 s, obwohl der Master schneller sendet. Alternative: `vrrp 1 timers learn` auf dem Backup.

### Konfiguration und Verifikation (Legacy-Syntax wie im Lab)
```
interface Ethernet0/1
 vrrp 1 ip 192.168.1.1
 vrrp 1 priority 110
R2# show vrrp brief
Interface  Grp Pri Time  Own Pre State   Master addr     Group addr
Et0/1      1   110 3570       Y  Master  192.168.1.2     192.168.1.1
```
- Spalten: `Own` = Owner (VIP = eigene Adresse), `Pre` = Preempt. Konsolenmeldung beim Wechsel: `%VRRP-6-STATECHANGE: Et0/1 Grp 1 state Backup -> Master`.

### VRRP-Authentifizierung
- RFC 2338 (v1) kannte Klartext und MD5; RFC 3768 und RFC 5798 haben Authentifizierung wieder gestrichen (schützt nicht gegen mehrere Master durch Fehlkonfiguration, Angreifer kann ohnehin ARP stören). Schutz bleibt der TTL-255-Check.
- Cisco IOS kann es weiterhin: `vrrp 1 authentication text <key>`, `vrrp 1 authentication md5 key-string <key>` oder `... md5 key-chain <name>`.
- Default ist **keine** Authentifizierung. Bei Mismatch: Log `%VRRP-4-BADAUTHTYPE`, beide Router werden Master.

### VRRPv3 auf IOS XE (Ergänzung)
```
fhrp version vrrp v3
interface GigabitEthernet1/0/1
 vrrp 1 address-family ipv4
  address 192.168.1.1 primary
  priority 110
```
- IPv4 und IPv6 (FF02::12), Zentisekunden-Timer, keine Authentifizierung.

## 6. Vergleich der FHRPs (Kurs + Ergänzung GLBP)
| | HSRP | VRRP | GLBP (Ergänzung) |
|---|---|---|---|
| Standard | Cisco (RFC 2281) | IETF (RFC 3768/5798, aktuell 9568) | Cisco |
| Rollen | Active/Standby/Listen | Master/Backup | AVG + bis 4 AVF |
| Forwarder pro Gruppe | 1 | 1 | bis 4 |
| Default-Prio | 100 | 100 (Owner 255) | 100 |
| Preempt-Default | aus | an | AVG aus, AVF an |
| Timer-Default | Hello 3 s / Hold 10 s | Adv 1 s | Hello 3 s / Hold 10 s |
| Nachrichten | 224.0.0.2 bzw. .102, UDP 1985 | 224.0.0.18, IP-Prot. 112 | 224.0.0.102, UDP 3222 |
| vMAC | 0000.0c07.acXX / 0000.0c9f.fXXX | 0000.5e00.01XX | 0007.b400.XXYY |
- GLBP: Der Active Virtual Gateway (AVG) beantwortet alle ARP-Anfragen für die eine VIP und verteilt reihum (Default round-robin) die vMACs der bis zu vier Active Virtual Forwarder; Gruppen 0–1023. Fällt ein AVF aus, übernimmt ein anderer dessen vMAC.

## 7. Hochverfügbarkeit im Switch (S. 114)
- Redundante Supervisoren in modularen Catalyst-Switches; der Modus bestimmt, wie weit der Standby vorbereitet ist. Je bereiter, desto kürzer der Failover.

| Modus | Zustand des Standby | Bei Ausfall des Active | Kurs-Failoverzeit (plattformabhängig) |
|---|---|---|---|
| RPR | nur teilweise gebootet | alle Module neu laden, Supervisor-Funktionen initialisieren | < 2 min |
| RPR+ | gebootet, Supervisor und Route Engine initialisiert, keine L2/L3-Funktionen gestartet | Initialisierung abschließen, Module werden nicht neu geladen | < 30 s |
| SSO | voll gebootet; Startup- und Running-Config synchron, L2-Informationen und Interface-Zustände synchron | übernimmt sofort, Hardware-Switching läuft weiter, Links flappen nicht | < 1 s |
- Die Zeitangaben sind Kurswerte; Cisco nennt je nach Plattform andere Werte (Prüfprotokoll). SSO setzt kompatible Images voraus, sonst Fallback auf RPR.
```
redundancy
 mode sso
show redundancy
```
- **NSF** (mit SSO): Nach dem Switchover leitet die Hardware mit der alten FIB/CEF-Tabelle weiter, während die Routingprotokolle per Graceful Restart die RIB neu aufbauen; Nachbarn müssen NSF-aware sein (`router ospf 1` → `nsf` bzw. `nsf ietf`/`nsf cisco`).
- Catalyst 9400 mit NSF/SSO (Kurswerte): Switchover ≤ 150 ms, < 200 ms Verkehrsunterbrechung; Links und Uplinks bleiben oben; SSO ist dort Default-Redundanzmodus; Bootzeit ca. 9 min.
- **NSR** (Ergänzung): Der Standby hält die Protokollzustände selbst, Nachbarn müssen nichts beitragen.

## 8. Stacking und StackWise Virtual (Ergänzung, nicht im Kurs)
- StackWise-480 (Catalyst 9300): bis 8 Switches per Stack-Kabel → ein logischer Switch. Active-Switch mit Control Plane, Standby per SSO synchron, übrige Member leiten Daten weiter. Ein neuer Switch mit höherer Priorität verdrängt den laufenden Active nicht.
- StackWise Virtual (z. B. Catalyst 9500/9600): genau 2 Switches über Ethernet-Links (SVL, StackWise Virtual Link); eine Control Plane, ein SVI pro VLAN → kein FHRP nötig. Access-Switches nutzen Multichassis EtherChannel (MEC) zu beiden Chassis, STP blockiert nichts. Dual-Active Detection (DAD) erkennt Split-Brain nach SVL-Ausfall; der bisherige Active schaltet dann in Recovery Mode alle Ports außer SVL- und DAD-Ports ab und wartet, bis die SVL wieder steht (danach Reload als Standby).

## 9. Troubleshooting-Checkliste
- Beide Router Active (Split-Brain): Hellos kommen nicht an (VLAN/Trunk, ACL), Authentifizierungs- oder Versions-Mismatch (v1/v2), unterschiedliche Gruppennummern.
- Besserer Router wird nicht Active: `preempt` fehlt (HSRP-Default aus).
- Uplink-Ausfall ohne Rollenwechsel: Tracking fehlt, Decrement zu klein oder Peer ohne preempt.
- Ständige Wechsel (Flapping): zu aggressive Timer, Preempt ohne Delay nach Reboot.
- Asymmetrischer Verkehr/Umwege: STP-Root und HSRP-Active liegen auf verschiedenen Switches.
- Nützlich: `show standby brief`, `show vrrp brief`, `show track`, `debug standby events`, Traceroute (zeigt reale IP des Active).

## Fehler/Ungenauigkeiten im Kurs
- S. 112: `standby 10 version 2` – falsch, `standby version 2` ist ein Interface-Befehl ohne Gruppennummer (Cisco FHRP Command Reference, siehe Prüfprotokoll).
- S. 112: "preceding the string with the seven keywords" – gemeint ist die Ziffer 7 vor dem verschlüsselten Key-String (`key-string 7 <hash>`).
- S. 111 Step 3: `show ip arp` auf R1 zeigt 192.168.1.2 als eigene Adresse, obwohl R1 192.168.1.3 hat (Kopierfehler).
- S. 111 Step 7: Nach `standby 1 timers msec 200 msec 750` zeigt die Beispielausgabe weiter "Hello time 3 sec, hold time 10 sec".
- S. 111 Step 13: Ausgabe zeigt R2 mit Pri 100 ohne P, obwohl 110 + preempt konfiguriert sind.
- S. 111: "Timer müssen auf allen Geräten identisch sein" – nicht konfigurierte Router lernen die Timer aus den Hellos des Active (RFC 2281); identisch konfigurieren ist nur Empfehlung.
- S. 111: Preempt-Delay-Faustregel "150 % der Bootzeit" ist nicht in der Cisco-Doku belegt (Prüfprotokoll); belegt ist nur: Delay länger als Boot-/Konvergenzzeit.
- S. 113 (Grafik): Router A, B und C sind alle als "Virtual Router Master" beschriftet – nur A ist Master, B und C sind Backups. **(neu gefunden)**
- S. 113 (Grafik): Router A hat Priorität 255, obwohl die VIP 10.0.0.254 nicht seine Interface-Adresse (10.0.0.1) ist. 255 ist dem Owner vorbehalten; konfigurierbar sind 1–254 (RFC 3768 Abschnitt 5.3.4). **(neu gefunden)**
- S. 113: "Priorität 0–255" – konfigurierbar sind 1–254; 0 (Rücktritt) und 255 (Owner) setzt das Protokoll selbst (RFC 3768). **(neu gefunden)**
- S. 113: "default holdtime is 3 seconds" – VRRP hat keine Hold Time; das Master Down Interval beträgt 3 × Intervall + Skew, also ca. 3,6 s bei Prio 100 (RFC 3768 Abschnitt 6.1).
- S. 113: "Default VRRP authentication is plaintext" – Default ist keine Authentifizierung; `text` ist nur der Typ, der ohne Schlüsselwort konfiguriert wird.
- S. 113: msec-Timer "auf Master und Backup konfigurieren" – laut Cisco übernehmen Backups msec-Werte nicht in die Anzeige und zeigen immer 1 s (Prüfprotokoll, Cisco FHRP Config Guide 15-E).
- S. 113: Satz "since R1 is already active and the master R2 stays in the backup state" vermischt HSRP- und VRRP-Begriffe (gemeint: R1 ist Master, R2 bleibt Backup). **(neu gefunden, sprachlich)**
- S. 114: Failover-Zeiten < 2 min / < 30 s / < 1 s sind Kurswerte, real plattformabhängig (Prüfprotokoll: z. B. RPR+ ca. 30 s, SSO 0–3 s laut Cisco-Doku).
- S. 114: "RPR+ … switch ports can retain their state" – nicht belegt; belegt ist nur, dass die Module nicht neu geladen werden (Prüfprotokoll).
- S. 114: NSF wird als "interactive method" bezeichnet – NSF ist ein Weiterleitungsmechanismus mit Graceful Restart, nichts Interaktives (vermutlich Wortfehler). **(neu gefunden, sprachlich)**

## Bilder
- `bilder/11-redundancy/01-gw-problem.svg` – Ein Gateway pro Host als Single Point of Failure trotz zweitem Router.
- `bilder/11-redundancy/02-fhrp-idee.svg` – Virtueller Router mit VIP/vMAC, Normalbetrieb und Übernahme in drei Schritten.
- `bilder/11-redundancy/03-hsrp-states.svg` – HSRP-Zustandsautomat Initial → Listen → Speak → Standby → Active mit Bedeutung.
- `bilder/11-redundancy/04-tracking.svg` – Object Tracking: Uplink-Ausfall, Prioritätsrechnung 110 − 20 = 90 und Pfadwechsel.
- `bilder/11-redundancy/05-mhsrp.svg` – MHSRP: zwei Gruppen, abwechselnd Active, passend zum STP-Root.
- `bilder/11-redundancy/06-hsrp-v1-v2.svg` – HSRPv1 vs. v2 mit vMAC-Aufbau und Hex-Rechenbeispielen.
- `bilder/11-redundancy/07-vrrp-skew.svg` – VRRP-Rollen und Master-Down-Interval-Rechnung für mehrere Prioritäten.
- `bilder/11-redundancy/08-fhrp-vergl.svg` – Tabelle HSRP/VRRP/GLBP.
- `bilder/11-redundancy/09-sup-modi.svg` – RPR, RPR+, SSO und NSF als Bereitschaftsstufen des Standby-Supervisors.
- `bilder/11-redundancy/10-stackwise.svg` – StackWise Virtual mit SVL, MEC und DAD.
