# Using Network Analysis Tools

Quelle: ENCOR 1.4.10 Student Guide, Seiten 229–240 (228 Intro, 241 Summary Challenge, 242 Answer Key nicht ausgewertet)

Topics: ENCOR-4.1 (Diagnose mit debug, conditional debug, traceroute, ping, SNMP, syslog; Troubleshooting-Methodik, Hardware-Diagnose, show-Filter), ENCOR-4.4 (IP SLA), ENCOR-4.3 (SPAN, RSPAN, ERSPAN, Packet-Capture)

---

## Troubleshooting-Konzepte (S. 229)

- Ein Problem „existiert“ für den Betrieb erst, wenn es bemerkt und gemeldet wird. Meldezeitpunkt ≠ Zeitpunkt des auslösenden Ereignisses.
- Der Nutzer setzt das Problem mit dem **Symptom** gleich, der Troubleshooter sucht die **Root Cause** (Ursache). Diese unterschiedliche Sicht erzeugt leicht Missverständnisse.
- Ablauf grob: **Problem melden/definieren → Diagnose → Lösung vorschlagen/bewerten → implementieren → dokumentieren**.
- **Lösung vs. Workaround**: Eine Lösung beseitigt die Ursache, ein Workaround lindert nur die Symptome (Überbrückung, bis die echte Lösung möglich ist).
- Nach der Behebung: alle Änderungen dokumentieren – hilft beim nächsten ähnlichen Fall.

### Diagnoseprinzipien (die meiste Zeit fließt in die Diagnose)
| Element | Inhalt |
|---|---|
| Gather information | Symptome sammeln – direkt (beobachten) oder indirekt (Tests ausführen). Die Problemmeldung allein reicht fast nie. |
| Analyze | Gesammelte Daten mit Wissen über System, Prozesse und **Baseline** vergleichen → normal vs. abnormal trennen. |
| Eliminate | Durch Vergleich von beobachtetem und erwartetem Verhalten mögliche Ursachen ausschließen. |
| Propose hypothesis | Verbleibende Ursachen nach Wahrscheinlichkeit bewerten, wahrscheinlichste als Hypothese wählen. |
| Test | Hypothese bestätigen/widerlegen – meist durch eine darauf basierende Lösung + Verifikation; wenn das zu disruptiv ist, weitere Informationen sammeln. |

Erster Schritt des Gesamtprozesses: **Define the problem**.

## Troubleshooting-Prozeduren: Überblick (S. 230)

Kursmodell: **Define Problem → [Gather Information → Analyze Information → Eliminate Potential Causes → Propose Hypothesis → Test Hypothesis] (= Diagnose, iterativ) → Solve Problem and Document Solution**.

- In der Praxis springt man zwischen den Phasen hin und her (sammeln, analysieren, eliminieren, wieder sammeln …).
- Eine **Troubleshooting-Methode** bestimmt, *wie* man sich durch die Phasen bewegt. Strukturiertes Vorgehen → vorhersagbare Ergebnisse, Übergabe an Kollegen und Unterbrechen/Fortsetzen möglich. Unstrukturiertes Vorgehen ist ineffizient und nicht übergebbar.

### Strukturierte Methoden (Ergänzung aus Standardwissen, Cisco TSHOOT/ENCOR-Literatur)
| Methode | Vorgehen | Wann sinnvoll |
|---|---|---|
| Top-down | Bei Schicht 7 (Anwendung) beginnen und nach unten arbeiten | Problem vermutlich anwendungsnah; Nutzer meldet „Anwendung X geht nicht“ |
| Bottom-up | Bei Schicht 1 (Kabel, Link) beginnen und nach oben arbeiten | Physikalisches Problem vermutet; sehr gründlich, aber zeitaufwendig bei komplexen Problemen |
| Divide and conquer | In der Mitte (oft Schicht 3, z. B. Ping) beginnen; bei Erfolg aufwärts, sonst abwärts | Erfahrener Troubleshooter, häufigster „Profi“-Ansatz |
| Follow the traffic path | Pfad des Pakets von Quelle zu Ziel Gerät für Gerät verfolgen | Erreichbarkeitsprobleme durch mehrere Geräte hindurch |
| Compare configurations / Spot the differences | Funktionierende mit nicht funktionierender Konfiguration/Gerät vergleichen | Wenig Expertise im Detail, aber funktionierende Referenz vorhanden |
| Swap components | Verdächtige Komponente (Kabel, Modul, Gerät) gegen bekannt gute tauschen | Hardwareverdacht; isoliert, erklärt aber nicht immer die Ursache |

## Case Study (S. 231)

Szenario: Nutzerin meldet „Internet geht nicht“ (cisco.com nicht erreichbar).
1. **Define**: genaue Beschreibung einholen und Problem reproduzieren (gestern ging es noch).
2. **Gather** (bottom-up am Laptop): WLAN an, Ping Gateway ok, Ping interner Server ok, Ping öffentliche IP ok, Zugriff per Name schlägt fehl; `nslookup` → Timeout gegen einen DNS-Server.
3. **Analyze**: DNS-Server-Adresse am Laptop weicht von der Dokumentation ab; laut Doku kommt DNS per DHCP.
4. **Eliminate + Hypothesis**: Manuelle Fehlkonfiguration ausgeschlossen (Laptop steht auf DHCP) → Hypothese: DHCP-Pool der Buchhaltung verteilt falschen DNS-Server.
5. **Test**: DNS am Laptop testweise manuell auf den dokumentierten Server setzen → funktioniert. Das ist nur ein Test/Workaround; danach wieder auf DHCP zurückstellen.
6. **Solve + Document**: DNS-Server im DHCP-Pool korrigieren, testen, Konfiguration speichern, Änderung dokumentieren.

Merksätze: Ping auf IP geht, Name nicht → DNS-Problem. Gute Dokumentation (Baseline) ist zentral; fehlende/veraltete Doku ist in der Praxis häufig. Erfolg beim Aufstellen von Hypothesen hängt von Wissen, Erfahrung und Systemkenntnis ab.

## Basic Hardware Diagnostics (S. 232)

### CPU – `show processes cpu`
```
R1# show processes cpu sorted 1min
CPU utilization for five seconds: 30%/26%; one minute: 12%; five minutes: 9%
 PID Runtime(ms) Invoked uSecs  5Sec   1Min   5Min TTY Process
 109    26750192 94989172  281  2.39%  1.36%  1.32%  0 IP Input
```
- `X%/Y%`: X = **gesamte** CPU-Last der letzten 5 s, Y = **Interrupt**-Anteil (Pakete, die die CPU per Interrupt verarbeiten muss, z. B. punted Traffic). X − Y = Summe der Prozesse (im Beispiel 30 − 26 = 4 %).
- Danach Mittelwerte 1 min und 5 min; je Prozess PID, Laufzeit, Aufrufe und Anteile. `sorted` sortiert absteigend (`sorted 5sec | 1min | 5min`).
- `show processes cpu history` zeigt ASCII-Grafik der letzten 60 s / 60 min / 72 h.
- Bewertung laut Kurs: dauerhaft > 70–80 % → Troubleshooting nötig; kurze Spitzen meist harmlos. Interrupt-Anteil 0–5 % normal, 5–10 % akzeptabel, > 10 % untersuchen.
- Die CPU hat zwei Aufgaben: IOS-Prozesse ausführen und Pakete von/zur Switching-Hardware senden/empfangen. Überlast, wenn ein Prozess zu viel Zeit braucht oder zu viele Pakete gepuntet werden.
- Gründe für Punting zur CPU: Fragmentierung, IP Options, TTL = 1 (TTL-Expiry), ACL mit `log`, Forwarding-Probleme, Multicast-RPF-Drops, Multicast-Pfadaufbau, an den Router selbst adressierter Verkehr.

### Router-Kategorien
| Typ | Control/Data Plane | Forwarding |
|---|---|---|
| Software-based | gemeinsam, eine CPU für alles | CPU |
| Hardware-based | getrennt | ASIC; was das ASIC nicht kann, wird zur CPU gepuntet |
| Hardware-assisted | getrennt | Network Processor (NP); was der NP nicht kann, wird gepuntet |

### Speicher – `show memory`
- Zeigt **Processor**- und **I/O**-Memory (Total, Used, Free, Lowest, Largest). I/O-Memory dient der temporären Paketpufferung.
- Wenig freier Speicher → Performance bricht ein, im Extremfall Reload. Speicherzuweisungsfehler erzeugen **%SYS-2-MALLOCFAIL**.
- „Lowest“ = niedrigster je gemessener freier Wert, „Largest“ = größter zusammenhängender freier Block (Fragmentierung erkennbar).

### Interfaces – `show interfaces`
```
GigabitEthernet0/0 is up, line protocol is up
  Full Duplex, 1Gbps, media type is RJ45
  Input queue: 1/75/1596/0 (size/max/drops/flushes); Total output drops: 0
  Output queue: 0/40 (size/max)
     0 runts, 0 giants, 0 throttles
     3 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
     0 output errors, 0 collisions, 1 interface resets
```
| Zähler | Bedeutung / typische Ursache |
|---|---|
| Input queue drops | Router erhält mehr Verkehr, als die CPU verarbeiten kann (gilt für prozessvermittelte Pakete) |
| Output drops | Ausgangsqueue voll → Stau/Überlast des Links |
| Input errors | Summe von Fehlern wie runts, giants, CRC, frame, overrun, ignored; Ursachen: Interface/Kabel, Duplex, CRC |
| Output errors | meist Duplex-Probleme (laut Kurs) |
| CRC | FCS stimmt nicht → Kabel/EMI/defekter Port, oder Gegenstelle im Duplex-Mismatch |
| Runts | Frames < 64 Byte (oft Kollisionsreste, Duplex-Mismatch) |
| Giants | Frames > maximaler Größe (MTU-Mismatch, Jumbo-Frames ohne Konfiguration) |
| Collisions | nur in Half-Duplex normal; bei Full-Duplex dürfen keine auftreten |
| Late collisions | Kollision nach den ersten 64 Byte → typisch **Duplex-Mismatch** (Half-Duplex-Seite) oder zu lange Kabel |
| Ignored / overrun / no buffer | Hardware-/Pufferengpass, Bursts |

Duplex-Mismatch-Muster: Half-Duplex-Seite zählt **late collisions**, Full-Duplex-Seite zählt **CRC/FCS-Fehler und runts**. Folge: Link up, aber langsam/fehlerhaft.

- Weitere Felder: MTU, BW, DLY, reliability, txload/rxload, Duplex/Speed, Queueing strategy, „Last clearing of counters“ (Zähler mit `clear counters` nullen, dann neu beobachten).
- MTU sauber planen – verschiedene MTUs (Ethernet, PPP, IP, MPLS).

### `show controllers` und `show platform`
- `show controllers`: hardwarenahe Detailstatistik je Interface-Controller (Rx/Tx Good/Bad Bytes und Frames, Größenverteilung). Bei seriellen Interfaces: Kabel angeschlossen? DTE oder DCE?
- `show platform`: Plattform-/Hardwaredaten (z. B. Backplane-EEPROM, Interrupt-Throttling). Hilfreich bei Reload-Analysen; vor einem TAC-Case sammeln.

## Filtered Show Commands (S. 233)

Syntax: `show … | {include | exclude | begin | section} <regex>`

| Filter | Wirkung | Beispiel |
|---|---|---|
| `include` | nur Zeilen, die passen | `show ip route \| include 10.10` |
| `exclude` | Zeilen, die passen, weglassen | `show ip interface brief \| exclude down` |
| `begin` | Ausgabe ab erster passender Zeile | `show running-config \| begin line vty` |
| `section` | passende Konfigurationsabschnitte inkl. eingerückter Unterzeilen | `show running-config \| section router ospf` |

Regex-Zeichen (Cisco IOS):
| Zeichen | Bedeutung | Beispiel |
|---|---|---|
| `^` | Zeilenanfang | `^Giga` → Zeilen, die mit „Giga“ beginnen |
| `$` | Zeilenende | `123$` passt auf „0123“, nicht auf „1234“ |
| `\|` | ODER | `include ^Giga\|errors\|packets` |
| `*` | 0..n Wiederholungen des **vorangehenden Zeichens** | `2345*` passt auf 234, 2345, 23455 … |
| `.` | beliebiges einzelnes Zeichen | `10.1.1.` (Punkt ist Wildcard!) |
| `_` | Leerzeichen, Komma, Klammer, Anfang/Ende (v. a. BGP) | `_65001_` |

- Matching ist **case-sensitive** und leerzeichenempfindlich (Interfacenamen beginnen groß: „GigabitEthernet“).
- Beispiel: `show interfaces Gi0/0 | include ^Giga|errors|packets` → Statuszeile, Paket- und Fehlerzähler.

## Discovery 23: ping, traceroute, debug (S. 234)

Topologie: PC1 – R1 – R2 – R3 – R4 – SW – PC2 (zusätzlich R5 zwischen R2 und R3), OSPF. Fehler: R1 annonciert 10.10.10.0/24 (PC1-LAN) nicht in OSPF.

### ping
- ICMP Echo Request/Reply: prüft Erreichbarkeit, RTT, Paketverlust. Erfolgreich, wenn Request ankommt und Reply innerhalb des Timeouts (Default **2 s**) zurückkommt. Default: **5 Echos à 100 Byte**.
- Router beantworten Pings mit niedriger Priorität → Verarbeitungsverzögerung möglich (RTT-Ausreißer beim ersten Paket, auch ARP).
- Erster Ping oft `.!!!!` (80 %): erstes Paket geht wegen ARP-Auflösung verloren.

| Zeichen | Bedeutung |
|---|---|
| `!` | Reply empfangen |
| `.` | Timeout beim Warten auf Reply |
| `U` | Destination Unreachable empfangen |
| `Q` | Source Quench (Ziel zu beschäftigt) |
| `M` | Could not fragment (DF gesetzt, MTU zu klein) |
| `?` | unbekannter Pakettyp |
| `&` | Packet lifetime exceeded (TTL abgelaufen) |

- Hosttests: 127.0.0.1 (IP-Stack), eigene IP (NIC/Stack), Default Gateway (lokales Netz), entferntes Ziel.
- **Quelle**: Standardmäßig ist die Quell-IP die des **ausgehenden Interfaces**. Ping vom Router ohne Quelle kann klappen, vom Client-LAN aus aber nicht → Rückroute zum Client-Subnetz fehlt. Test: `ping 10.10.50.2 source ethernet 0/0` (bzw. Quell-IP).
- Extended ping (nur privileged EXEC, `ping` ohne Argumente): Protocol [ip], Target, Repeat count [5], Datagram size [100], Timeout [2], Extended commands [n], Source address or interface (vollständiger Name, z. B. „Ethernet0“, nicht „e0“), Type of service [0], Set DF bit [no], Validate reply data [no], Data pattern [0xABCD], Loose/Strict/Record/Timestamp/Verbose [none], Sweep range of sizes [n] (Sweep min [36], max [18024], interval [1]).
  - **Record**: bis zu 9 Hops, Hin- **und** Rückweg (traceroute zeigt nur Hinweg).
  - **Loose**/**Strict** Source Routing; **Timestamp**; Verbose wird mit jeder Option mitgewählt.
  - Data pattern z. B. für Framing-/Clocking-Probleme auf seriellen Leitungen.
- Erfolgsquote < 80 % gilt meist als problematisch.
- One-Liner-Optionen: `ping <ziel> source <if|ip> size <n> df-bit repeat <n> timeout <s>`.

### MTU mit DF-Bit ermitteln
```
R1# ping 10.10.50.2 size 1476 df-bit   → !!!!!
R1# ping 10.10.50.2 size 1477 df-bit   → M.M.M
```
→ Pfad-MTU = 1476 Byte (`size` ist die gesamte IP-Paketgröße). Typische Ursache: GRE-Tunnel (24 Byte Overhead: 1500 − 24 = 1476).
- Sweep: Repeat 1, DF yes, Sweep 1400–1500 → 101 Pakete; 77 erfolgreich (1400…1476), Rest „M“ bzw. „.“.
- Fragmentierung vermeiden: CPU-Last, Header-Overhead pro Fragment, Verlust eines Fragments = ganzes Paket neu.

### traceroute (Cisco IOS)
- Sendet **UDP**-Probes, **3 pro TTL**, Ziel-Ports ab **33434** (pro Probe +1). TTL beginnt bei 1; jeder Router, der TTL auf 0 dekrementiert, sendet **ICMP Time Exceeded**. Das Ziel antwortet mit **ICMP Port Unreachable** → Ende. (Windows `tracert` nutzt ICMP Echo.)
- Defaults (IOS): Timeout 3 s, Probe count 3, max TTL 30.
- Abbruch: Ctrl+Shift+6, dann X.

| Zeichen | Bedeutung |
|---|---|
| nn msec | RTT je Probe |
| `*` | Probe Timeout |
| `A` (!A) | administratively prohibited (z. B. ACL) |
| `Q` | Source Quench |
| `I` | Test vom Benutzer unterbrochen |
| `U` | Port unreachable |
| `H` (!H) | Host unreachable |
| `N` (!N) | Network unreachable |
| `P` | Protocol unreachable |
| `T` | Timeout |
| `?` | unbekannter Pakettyp |

- Lab: traceroute von PC2 zu PC1 zeigt nur `* * *` ab Hop 1; der Kurs folgert daraus, dass schon R4 keine Route ins Ziel-Subnetz hat (als allgemeine Regel unsicher, siehe Fehlerliste Punkt 7) (`show ip route 10.10.10.1` → „% Subnet not in table“). Lösung: `network 10.10.10.0 0.0.0.255 area 0` auf R1.

### debug
- Debugs liefern Diagnoseinfos zu Protokoll- und Netzwerkereignissen – mit Vorsicht, nur gezielt. Unter Last kann der Router hängen; vorher `show processes cpu` prüfen.
- Ausgabeziele: **Console** (Default aktiv; die Console verarbeitet Debug-Ausgabe immer, auch wenn man per VTY arbeitet → `no logging console` erwägen), **VTY/AUX** (`terminal monitor` nötig), **Buffer/Syslog** (`logging buffered`, `logging host`).
- `logging synchronous` (line con/vty): Eingabe wird nicht von Meldungen zerrissen.
- Ausschalten: `no debug …`, `undebug all`, `no debug all`; aktive Debugs: `show debug(ging)`.
- `debug ip packet [acl] [detail]`: zeigt nur **prozessvermittelte** Pakete (an den Router/vom Router selbst). CEF-/fast-switched Transitverkehr erscheint nicht. Um Transit zu sehen: `no ip route-cache` am Interface (CPU-Risiko! nie bei MPLS). Mit ACL einschränken: `access-list 10 permit 10.10.30.1` + `debug ip packet 10`.
- Beispielausgabe: `IP: s=10.10.30.1 (Ethernet0/0), d=224.0.0.5, len 80, rcvd 0` (OSPF-Hello an 224.0.0.5).
- **Conditional debug**: `debug condition interface e0/0` → „Condition 1 set“; `show debug condition`; Optionen u. a. interface, ip, mac-address, vlan, username, vcid, session-id. Mehrere Bedingungen: Ausgabe, wenn **mindestens eine** passt. Entfernen: `undebug condition <id>|all` bzw. `no debug condition all`.

## Cisco IOS IP SLAs (S. 235)

- SLA = Vertrag über Dienstgüte (Verfügbarkeit, RTT, Latenz, Jitter, Paketverlust). **IP SLA** = von Cisco-Geräten erzeugte aktive Tests (synthetischer Verkehr), die prüfen, ob die SLA eingehalten wird.
- Operationen (plattformabhängig): `dhcp`, `dns`, `ftp`, `http`, `icmp-echo`, `path-echo`, `path-jitter`, `tcp-connect`, `udp-echo`, `udp-jitter` (u. a. auch SIP/VoIP-Ops).
- Metriken: Latenz/Antwortzeit, Paketverlust, Jitter und Sprachqualität (MOS/ICPIF), Ende-zu-Ende-Konnektivität.
- Einsatz: Verfügbarkeitsmonitoring, Performance-Monitoring, VoIP/Video/VPN-Monitoring, SLA-Prüfung des Providers, MPLS-Monitoring, Troubleshooting, Budget-Planung; reduziert **MTTR**.
- **Source**: Gerät, auf dem die Operation konfiguriert ist (CLI oder SNMP); speichert Ergebnisse in einer MIB (per SNMP auslesbar). Ziel kann ein beliebiges IP-Gerät sein.
- **Responder** (`ip sla responder`): Cisco-Gerät, das Testpakete beantwortet und **Zeitstempel** setzt, sodass die Verarbeitungszeit auf dem Responder herausgerechnet wird. Nötig z. B. für udp-jitter; icmp-echo braucht keinen Responder.
- Ablauf: **Control Phase** – Source schickt Control-Nachricht an **UDP 1967** („öffne Port X“), Responder bestätigt und lauscht; **Probing Phase** – Testverkehr auf Port X; danach hört der Responder wieder auf.
- Für One-Way-Messwerte (Latenz pro Richtung) müssen Source und Responder per **NTP** synchronisiert sein.
- Mehrere IP-SLA-Operationen können gleichzeitig laufen.

## Discovery 24: IP SLA konfigurieren (S. 236)

Topologie: HQ (192.168.1.1) – WAN – Branch (172.16.1.1, Lo0 172.16.22.254).

```
HQ(config)# ip sla 1
HQ(config-ip-sla)# icmp-echo 172.16.22.254 [source-interface Gi0/0]
HQ(config-ip-sla-echo)# frequency 30         ! optional
HQ(config-ip-sla-echo)# exit
HQ(config)# ip sla schedule 1 life forever start-time now

HQ(config)# ip sla 2
HQ(config-ip-sla)# udp-jitter 172.16.22.254 65051 num-packets 20
HQ(config-ip-sla-jitter)# request-data-size 160
HQ(config-ip-sla-jitter)# frequency 30
HQ(config)# ip sla schedule 2 start-time now
Branch(config)# ip sla responder
```
- Operationsnummer ist frei wählbar (identifiziert den Test lokal). Bei icmp-echo ist nur die Ziel-IP Pflicht. Ziel am besten Loopback (bei mehreren Pfaden).
- `ip sla schedule <nr> [life {forever|<sek>}] [start-time {hh:mm[:ss] [month day]|pending|now|after hh:mm:ss}] [ageout <sek>] [recurring]`
  - Default life = **3600 s** (1 h); ohne `start-time` bleibt die Operation **pending**.
  - `ageout`: wie lange die Daten nach Ende behalten werden; `recurring`: täglich zur gleichen Zeit.
  - Eine geplante Operation kann nicht mehr geändert werden → `no ip sla schedule <nr>` bzw. Operation löschen und neu anlegen.
- Defaults (`show ip sla configuration`): Operation timeout **5000 ms**, frequency **60 s**, threshold 5000 ms, ICMP request-data-size 28, ToS 0, Entry ageout never.
- udp-jitter: `udp-jitter <ziel-ip> <ziel-port> [source-ip …] [source-port …] [control {enable|disable}] [num-packets n] [interval ms]` – Defaults: **10 Pakete (num-packets), 20 ms Abstand (interval), 32 Byte Payload (request-data-size)**; `show ip sla configuration` zeigt z. B. „Packet Interval (milliseconds)/Number of packets: 20/10“. Achtung: Der Fließtext einiger Cisco-Config-Guides (15-S/XE-3S) beschreibt ein Beispiel mit 10 Byte und 10 ms – die Default-Tabelle desselben Guides und die Command Reference nennen 10 Pakete / 32 Byte / 20 ms. Im Beispiel: 20 Pakete × 160 Byte, 20 ms Abstand, alle 30 s.
- Jitter = Varianz der Paketabstände (Inter-Packet Delay Variation). Positiver Jitter: Pakete kommen weiter auseinander an als gesendet; negativ: enger. Ideal 0.

### Verifikation
```
HQ# show ip sla statistics 1
IPSLA operation id: 1
        Latest RTT: 1 milliseconds
Latest operation return code: OK
Number of successes: 32
Number of failures: 0
Operation time to live: Forever
```
- udp-jitter-Statistik zusätzlich: RTT Min/Avg/Max, One-Way-Latenz SD/DS, Jitter SD/DS, Packet Loss SD/DS, Out of Sequence, Tail Drop, Late Arrival, MOS, ICPIF.
- `show ip sla statistics [aggregated|details]`, `show ip sla configuration`, `show ip sla summary`, `show ip sla application` (unterstützte Operationen, Anzahl konfiguriert/aktiv), `show ip sla responder`.
- Return codes u. a.: OK, Timeout, Over threshold, No connection.

### IP SLA + Object Tracking (Standardwissen, ENCOR 4.4)
```
track 1 ip sla 1 reachability       ! up bei OK oder Over threshold
! track 1 ip sla 1 state           ! up nur bei OK
 delay up 30 down 10                ! optional: Flattern dämpfen (Syntax: delay {up s [down s] | [up s] down s})
ip route 0.0.0.0 0.0.0.0 203.0.113.1 track 1     ! primäre Route, verschwindet bei Track down
ip route 0.0.0.0 0.0.0.0 198.51.100.1 10         ! Floating Static als Backup (AD 10)
interface Gi0/1
 standby 1 track 1 decrement 20     ! HSRP-Priorität senken (preempt beim Partner nötig)
show track 1
```

## SPAN Overview (S. 237)

- Problem: Switches leiten Unicasts nach MAC-Tabelle nur an den Zielport → Sniffer an einem anderen Port sieht nichts (bei Hubs sah er alles).
- **SPAN** (Switched Port Analyzer) kopiert Verkehr von **Source**-Ports (L2 oder L3) bzw. Source-**VLANs** an einen **Destination**-(Monitor-)Port. Richtung: `rx`, `tx` oder `both` (**Default both**).
- **Session** = Zuordnung Quellen ↔ Ziel, identifiziert durch Session-Nummer. Eine Session hat **entweder** Ports **oder** VLANs als Quelle, nicht beides.
- Local SPAN: alles auf einem Switch; keine getrennten Source-/Destination-Sessions.

```
SW1(config)# monitor session 1 source interface Gi0/1 [rx|tx|both]
SW1(config)# monitor session 1 source vlan 10 rx
SW1(config)# monitor session 1 destination interface Gi0/2 [encapsulation replicate] [ingress …]
SW1# show monitor [session 1]
```
- Regeln: Zielport kann nicht gleichzeitig Quellport sein (und umgekehrt); Anzahl Zielports plattformabhängig; der Zielport ist **kein normaler Switchport** mehr (nur gespiegelter Verkehr, kein normales Forwarding, keine STP-Teilnahme).
- `show monitor`: Type „Local Session“, Source Ports (Both: Gi0/1), Destination Ports, Encapsulation Native, Ingress Disabled.
- Bandbreite: Wird ein 1-Gbit-Port in beide Richtungen gespiegelt, können bis zu 2 Gbit/s auf einen 1-Gbit-Zielport treffen → Drops der Kopien (nicht des Originalverkehrs).
- Ohne `encapsulation replicate` werden Tags/L2-Protokolle i. d. R. nicht originalgetreu übernommen (Native).

## Remote SPAN (S. 238)

- RSPAN: Quell- und Zielports auf **verschiedenen Switches**; Transport über ein dediziertes **RSPAN-VLAN** (Layer 2, über Trunks).
- Bausteine: **RSPAN source session**, **RSPAN VLAN**, **RSPAN destination session**.
- Das RSPAN-VLAN wird wie ein normales VLAN angelegt + `remote-span`, und zwar auf **allen Switches im Pfad** (und es muss auf den Trunks erlaubt sein). Kopierter Verkehr wird in diesem VLAN geflutet (kein MAC-Learning).
- Session-Nummern sind lokal pro Switch und müssen nicht übereinstimmen.
- Manche (ältere) Plattformen brauchen einen **Reflector Port** (physischer Port als Loopback, sendet nichts nach außen; nur eine Session pro Reflector).

```
! Quell-Switch
SW1(config)# vlan 100
SW1(config-vlan)# name SPAN-VLAN
SW1(config-vlan)# remote-span
SW1(config)# monitor session 2 source interface Gi0/1
SW1(config)# monitor session 2 destination remote vlan 100
! Ziel-Switch
SW2(config)# vlan 100
SW2(config-vlan)# remote-span
SW2(config)# monitor session 3 source remote vlan 100
SW2(config)# monitor session 3 destination interface Gi0/2
SW# show monitor        ! "Remote Source Session" / "Remote Destination Session"
SW# show vlan remote-span
```

## ERSPAN (S. 239)

- **Encapsulated RSPAN**: gespiegelter Verkehr wird in **GRE** gekapselt → über ein **Layer-3**-Netz routbar.
- Bausteine: ERSPAN source session, GRE-gekapselter Verkehr, ERSPAN destination session. Gerät nur mit Source-Session = ERSPAN source device; nur mit Destination-Session = ERSPAN termination device.
- Source-Session: Quellports/-VLANs + **Ziel-IP**, **ERSPAN-ID**, optional VRF, `origin ip address` (Quell-IP der GRE-Pakete). Destination-Session: Zielports + dieselbe IP (lokal auf dem Ziel-Switch konfiguriert) + dieselbe ERSPAN-ID.
- Einschränkungen: kopiert keinen lokal erzeugten RSPAN-VLAN-Verkehr von Trunk-Quellports und keinen lokal erzeugten ERSPAN-GRE-Verkehr; Ports **oder** VLANs als Quelle.

```
Switch-1(config)# monitor session 1 type erspan-source
Switch-1(config-mon-erspan-src)# source interface Gi0/0/1 [rx|tx|both]
Switch-1(config-mon-erspan-src)# no shutdown
Switch-1(config-mon-erspan-src)# destination
Switch-1(config-mon-erspan-src-dst)# erspan-id 1
Switch-1(config-mon-erspan-src-dst)# ip address 2.2.2.2
Switch-1(config-mon-erspan-src-dst)# origin ip address 1.1.1.1

Switch-2(config)# monitor session 1 type erspan-destination
Switch-2(config-mon-erspan-dst)# destination interface Gi0/0/1
Switch-2(config-mon-erspan-dst)# no shutdown
Switch-2(config-mon-erspan-dst)# source
Switch-2(config-mon-erspan-dst-src)# erspan-id 1
Switch-2(config-mon-erspan-dst-src)# ip address 2.2.2.2

Switch-1# show monitor session 1
 Type : ERSPAN Source Session   Status : Admin Enabled
 Source Ports : RX Only : Gi0/0/1
 Destination IP Address : 2.2.2.2   MTU : 1464   ! Wert plattformabhängig (Cat9k-Beispiele: 1500/9000)
 Destination ERSPAN ID : 1          Origin IP Address : 1.1.1.1
```
- Statistik (ASR/ISR IOS XE): `show platform hardware qfp active feature erspan state`.

### Vergleich
| | Local SPAN | RSPAN | ERSPAN |
|---|---|---|---|
| Quelle/Ziel | gleicher Switch | verschiedene Switches | verschiedene Geräte |
| Transport | intern | RSPAN-VLAN (L2-Trunks) | GRE über L3 |
| Kennung | Session-Nr. | RSPAN-VLAN | ERSPAN-ID + IP |

## Cisco Packet Capture Tools (S. 240)

- Geräte können Pakete durch/zu/von sich selbst mitschneiden. Speicherung im **DRAM-Puffer** → nach Reload weg. Anzeige per CLI (Summary/Detail), Export als **PCAP** für Wireshark & Co.
- Tools:
  - **Embedded Packet Capture (EPC)**: Router, Capture an verschiedenen Punkten im **CEF**-Pfad; Support modellabhängig; PCAP-Export.
  - **Embedded Wireshark**: Catalyst 4500 (Sup7E ab 3.3SG) und 3850 (heute Catalyst 9000 / IOS XE); nur IP Base/IP Services; ausgehend mitgeschnittene Pakete zeigen evtl. noch nicht die Rewrites des Switches (TTL, VLAN-Tag, CoS, Checksumme, MAC, DSCP …).
  - **Mini Protocol Analyzer (MPA)**: Cat6500/7600/ME6500; nutzt eine **SPAN-Session**, Puffer lokal; Filter nach VLAN/ACL/MAC; libpcap-Export.
- Gemeinsam: **EXEC-Befehle** zum Starten/Stoppen, Puffergröße und -typ (linear/circular), Paketgröße; Export; nützlich, wenn kein externer Sniffer anschließbar ist oder remote; Begrenzung über Filter/Rate-Limits.

```
! IOS XE (Catalyst 9000 / ISR / ASR) – alles im privileged EXEC
monitor capture CAP interface GigabitEthernet1/0/1 both
monitor capture CAP match ipv4 any any          ! oder: access-list CAP-ACL
monitor capture CAP buffer size 10 [circular]   ! MB
monitor capture CAP limit duration 60
monitor capture CAP start
monitor capture CAP stop
show monitor capture CAP buffer brief | detailed
monitor capture CAP export flash:cap.pcap
no monitor capture CAP
```
- Capture-Punkt auch `control-plane` (Verkehr zur/von der CPU).

## Fehler/Ungenauigkeiten im Kurs

1. **Regex `*` (S. 233)**: Kurs: „2345* matches 2345, 2345 2345, 2345 2345 2345“. Korrekt: `*` wiederholt nur das **vorangehende Zeichen** (5) 0..n-mal → passt auf 234, 2345, 23455 …; für die Wiederholung des ganzen Musters braucht man Klammern `(2345 )*`. Quelle: Cisco „Regular Expressions“ (Terminal Services Config Guide, Appendix „Understanding Regular Expressions“).
2. **SPAN „Ingress: Disabled“ (S. 237)**: Kurs: dadurch würde nur der den Switch verlassende Verkehr zum Zielport kopiert. Korrekt: „Ingress Disabled“ bedeutet, dass der Zielport **keinen eingehenden Verkehr vom Sniffer** annimmt/weiterleitet; gespiegelt werden weiterhin die konfigurierten Richtungen (hier Both). Quelle: Catalyst 9300 SPAN Config Guide (`ingress`-Option des destination-Befehls).
3. **RSPAN (S. 238)**: Kurs: „These two sessions need to be defined on both the local and remote switches.“ Korrekt: Source-Session auf dem Quell-Switch, Destination-Session auf dem Ziel-Switch; nur das RSPAN-VLAN muss auf allen Switches existieren. Quelle: Catalyst SPAN/RSPAN Config Guide.
4. **ERSPAN-Konfiguration (S. 239)**: Beispiele ohne `no shutdown` – ERSPAN-Sessions sind standardmäßig administrativ down und müssen aktiviert werden (Kurs-Ausgabe zeigt aber „Admin Enabled“). Außerdem Tippfehler „used by the destination and destination sessions“ (gemeint: source und destination). Quelle: IOS XE ERSPAN Config Guide.
5. **udp-jitter-Payload (S. 236)**: Kurs nennt 10 Byte Default-Payload (übernommen aus dem Fließtext-Beispiel der Cisco-Guides, das auch 10 ms Abstand annimmt); die Default-Tabelle im Cisco UDP-Jitter-Config-Guide und die Command Reference nennen 10 Pakete, 32 Byte request-data-size, 20 ms interval. Quelle: https://www.cisco.com/en/US/docs/ios-xml/ios/ipsla/configuration/15-2s/sla_udp_jitter.html (Table 1). Payload-Default nicht abgefragt. Außerdem passt die Jitter-Erklärung („more than 10 milliseconds apart“) nicht zum Default-Abstand 20 ms – das Beispiel nimmt 10 ms Sendeabstand an.
6. **NTP (S. 235)**: Kurs formuliert pauschal, Uhren müssten per NTP synchronisiert sein – nötig ist das für **One-Way**-Messungen (Latenz/Jitter je Richtung); RTT-Messungen funktionieren auch ohne.
7. **traceroute „* * *“ ab Hop 1 (S. 234)**: Der Kurs folgert, schon R4 habe keine Route ins Ziel-Subnetz. Eine Probe mit TTL 1 läuft aber auf R4 ab, und R4 könnte Time Exceeded (bzw. ohne Route ICMP Unreachable, rate-limitiert) an PC2 schicken. Die Ausgabe ist im Lab-Kontext plausibel, als allgemeine Regel aber unsicher – nicht als Frage verwendet.
8. **Packet Capture (S. 240)**: „ACL zur Angabe der maximalen Capture-Rate“ ist missverständlich – ACLs filtern, *welche* Pakete mitgeschnitten werden; Rate/Länge werden über eigene Limits gesteuert.

## Bilder

- `bilder/22-analysis/01-ts-prozess.svg` – Troubleshooting-Prozess: Define → iterative Diagnose (Gather, Analyze, Eliminate, Hypothesis, Test) → Solve & Document.
- `bilder/22-analysis/02-ts-methoden.svg` – Methoden top-down, bottom-up, divide-and-conquer am OSI-Stapel plus follow-the-path, compare, swap.
- `bilder/22-analysis/03-cpu-auslastung.svg` – Lesen von „CPU utilization 30%/26%“: Gesamt, Interrupt, Prozesse; Punting-Gründe und Schwellwerte.
- `bilder/22-analysis/04-if-zaehler.svg` – Interface-Zähler und typische Ursachen, Duplex-Mismatch-Muster.
- `bilder/22-analysis/05-ping-mtu.svg` – Ping-Zeichen und MTU-Ermittlung mit DF-Bit/Sweep (GRE 1476).
- `bilder/22-analysis/06-traceroute.svg` – traceroute-Mechanik: UDP-Probes mit steigender TTL, Time Exceeded, Port Unreachable.
- `bilder/22-analysis/07-ip-sla.svg` – IP SLA Source/Responder (Control Phase UDP 1967, Probing) und Tracking → statische Route/HSRP.
- `bilder/22-analysis/08-span-typen.svg` – Local SPAN, RSPAN (RSPAN-VLAN) und ERSPAN (GRE über L3) im Vergleich.
- `bilder/22-analysis/09-epc.svg` – Embedded Packet Capture: definieren → start → stop → anzeigen → PCAP-Export → Wireshark.
