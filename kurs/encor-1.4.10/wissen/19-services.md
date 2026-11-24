# Implementing Network Services (NTP, PTP, Syslog, SNMP, NetFlow, EEM)

Quelle: ENCOR 1.4.10 Student Guide, Seiten 199–207 (198 Intro, 208 Summary Challenge und 209 Answer Key nicht ausgewertet)

Topics: ENCOR-3.3.a (NTP/PTP), ENCOR-4.1 (Syslog, SNMP, Debug-Ausgaben), ENCOR-4.2 (Flexible NetFlow), ENCOR-6.6 (EEM-Applets)

---

## 1. NTP (Network Time Protocol)

### Zweck
- Synchronisiert die Uhren aller Netzgeräte. Ohne einheitliche Zeit lassen sich Log-Meldungen verschiedener Geräte nicht korrelieren; Zertifikate (PKI) und zeitbasierte Sicherheitsfunktionen brauchen korrekte Zeit.
- Transport: **UDP 123** als Quell- und Zielport.
- Zeitquelle ganz oben: autoritative Quelle (Funkuhr, GPS, Atomuhr) an einem Zeitserver.
- Poll-Intervall des Clients: **64 bis 1024 s** (2^6 bis 2^10), passt sich dynamisch an die Netzbedingungen an. Etwa eine Transaktion pro Minute reicht für die Synchronisation zweier Systeme.
- Typische Genauigkeit: ca. **1 ms im LAN**, ca. **10 ms über WAN-Strecken** (~200 km).

### Stratum
- Stratum = Anzahl NTP-Hops bis zur autoritativen Quelle. Stratum 1 = Server mit direkt angeschlossener Referenzuhr. Ein Client eines Stratum-n-Servers wird Stratum n+1.
- **Niedrigeres Stratum = bevorzugt** (näher an der Quelle). NTP wählt unter den erreichbaren, synchronisierten Quellen die mit dem niedrigsten Stratum → selbstorganisierender Baum.
- Gültige Werte für `ntp master`: 1–15. **Stratum 16 = unsynchronisiert** (z. B. in `show ntp status` als "Clock is unsynchronized, stratum 16").
- NTP synchronisiert **nie** auf ein Gerät, das selbst nicht synchron ist, und **nicht** auf ein Gerät, dessen Zeit stark von den übrigen Quellen abweicht – selbst wenn dessen Stratum niedriger ist (Falseticker).
- NTP schätzt pro Server drei Größen: **Delay** (Laufzeit), **Offset** (Korrektur, die auf die Client-Uhr angewendet wird) und **Dispersion** (maximaler Fehler der Zeitmessung zwischen den Hosts).

### NTP-Versionen
- NTPv4 (Erweiterung von v3): IPv6-Unterstützung (IPv6-Multicast statt IPv4-Broadcast), verbessertes Sicherheitsframework auf Basis Public-Key-Kryptografie/X.509 (Autokey), automatische Berechnung der Verteilhierarchie über Multicast-Gruppen.

### Betriebsmodi
| Modus | Befehl | Eigenschaften |
|---|---|---|
| Server | (keine Vorkonfiguration nötig) bzw. `ntp master [stratum]` | liefert Zeit an Clients |
| Client | `ntp server <ip|name> [key n] [prefer]` | pollt den Server (Client/Server = häufigste Variante). Ein Cisco-Client beantwortet seinerseits Zeitanfragen → kann gleichzeitig Server für andere sein |
| Peer (symmetric) | `ntp peer <ip>` | Gruppe gleichrangiger Server als gegenseitiges Backup; verliert ein Peer seine Referenz, synchronisiert er sich vom anderen (push-pull) |
| Broadcast/Multicast | Server: Interface `ntp broadcast`; Client: Interface `ntp broadcast client` | "Push"-Modus, nur im selben Subnetz (Router leiten Broadcasts nicht weiter), weniger Konfiguration, etwas geringere Genauigkeit (Informationsfluss nur in eine Richtung) |

### Konfiguration
```
Central(config)# interface Loopback10
Central(config-if)# ip address 192.168.255.1 255.255.255.0
Central(config)# ntp master 2              ! autoritativ, Stratum 2
Central(config)# ntp source Loopback10     ! Absenderadresse der NTP-Pakete
Branch1(config)# ntp server 192.168.255.1  ! Client -> Stratum 3
SW1(config)# ntp server 10.1.1.1           ! z. B. auf Branch-Router -> Stratum 4
```
- `ntp master` ohne Wert → **Stratum 8** (Default, eigenes Wissen / Cisco Command Reference).
- `ntp master` nur auf einem Gerät mit autoritativer Zeit einsetzen (selbst per `ntp server` synchronisiert oder per `clock set` gestellt). Mehrere `ntp master` mit unterschiedlicher Zeit → Instabilität; ein niedriges Stratum kann gültige Quellen "übertrumpfen". Stratum muss höher sein als das des Upstream-Geräts.
- `ntp master` erzeugt intern eine Referenzuhr mit Adresse **127.127.x.1** (drittes Oktett plattformabhängig, meist 127.127.1.1) – sichtbar in `show ntp associations` als ref clock.
- Loopback als Ziel/Quelle: Fällt ein physisches Interface des Servers aus, bleibt die Loopback über einen Alternativpfad erreichbar.
- `ntp update-calendar` (eigenes Wissen): schreibt die NTP-Zeit periodisch in die Hardware-Uhr (Calendar).

### Verifikation
```
R1# show ntp status
Clock is synchronized, stratum 3, reference is 10.1.1.1
...
R1# show ntp associations
  address        ref clock      st  when poll reach delay offset disp
*~10.1.1.1       127.127.1.1     2    36   64   377  1.0  -0.2   0.9
+~10.2.2.2       10.1.1.1        3    12   64   377  1.8   0.3   1.1
 * sys.peer, # selected, + candidate, - outlyer, x falseticker, ~ configured
```
- `*` = sys.peer (aktuelle Synchronisationsquelle), `+` = Kandidat, `-` = Outlier, `x` = Falseticker (verworfen), `#` = selected, `~` = statisch konfiguriert.
- Lokales Stratum = Stratum des sys.peer + 1.
- reach 377 (oktal) = die letzten 8 Polls erfolgreich.

### Sicherheit
- Authentifizierung: **NTP authentisiert die Quelle (Server) gegenüber dem Client**, nicht den Client. Das Gerät antwortet weiter auf nicht authentisierte Anfragen → zusätzlich ACLs.
```
ntp authentication-key 1 md5 MyPassword
ntp authenticate
ntp trusted-key 1
ntp server 10.0.1.22 key 1     ! nur auf dem Client
```
- Fehlt `ntp trusted-key` oder passt der Schlüssel nicht, bleibt der Client unsynchronisiert (`show ntp status`).
- Zugriffssteuerung per `ntp access-group {peer | serve | serve-only | query-only} <acl>`:
  - **peer**: Zeit-Requests und Control-Queries erlaubt, Gerät darf sich auch selbst auf die erlaubten Systeme synchronisieren.
  - **serve**: Requests und Queries erlaubt, aber keine Synchronisation auf diese Systeme.
  - **serve-only**: nur Zeit-Requests.
  - **query-only**: nur Control-Queries.
- Typisches Design: zwei Core-Router mit `peer`-ACL gegenseitig, `serve-only`-ACL für die Clients.
- Bei `ntp master` + ACL muss die interne Quelle 127.127.x.1 erlaubt werden, sonst verliert das Gerät seine eigene Referenz.
- Risiko ohne Schutz: Flut von Anfragen aus dem Internet, Ausspähen der Zeitserver, Umleitung (z. B. nach DNS-Cache-Poisoning) auf eine falsche Zeitquelle → zeitbasierte Sicherheitsfunktionen/Zertifikate gestört.

---

## 2. PTP (Precision Time Protocol, IEEE 1588)

- Entwickelt für sehr genaue Synchronisation in paketbasierten Netzen (Industrie, Mess-/Steuersysteme, Smart Grid/Energie, Finanzhandel). Geringe Bandbreite und wenig Rechenaufwand.
- Genauigkeit deutlich besser als NTP (Sub-Mikrosekunden-Bereich), weil Zeitstempel in Hardware gesetzt und Verweilzeiten in Switches korrigiert werden (eigenes Wissen).
- Nachrichten (eigenes Wissen, teilweise im Kurs erwähnt): **Announce** (Clock-Eigenschaften für BMCA), **Sync**/Follow_Up, **Delay_Req**/Delay_Resp (E2E), Pdelay_Req/Pdelay_Resp (P2P). Transport über Ethernet (Ethertype 0x88F7) oder UDP (Ports 319 Event / 320 General).

### BMCA (Best Master Clock Algorithm)
- Läuft lokal auf jedem Port in jedem Announce-Intervall; Clocks müssen nicht miteinander verhandeln; verhindert zwei oder keine Primary Clock.
- Vergleichsreihenfolge (IEEE 1588-2008): **Priority1 → Clock Class → Accuracy → Variance (Offset Scaled Log Variance) → Priority2 → Clock Identity (64-bit EUI)**. Jeweils gewinnt der **niedrigere** Wert (eigenes Wissen, IEEE 1588).
- Priority1 und Priority2: 0–255, Default **128**; vom Admin setzbar. Class/Accuracy/Variance beschreiben die Uhrqualität (GPS = höchste Qualität).

### Clock-Typen
| Typ | Merkmal |
|---|---|
| Grandmaster Clock | primäre Zeitquelle der Domäne, meist mit GPS-/Atomuhr |
| Ordinary Clock | ein PTP-Port; Endgerät; häufigster Typ; kann per BMCA Primary oder Secondary werden |
| Boundary Clock | mehrere PTP-Ports; terminiert PTP; Secondary-Port synchronisiert sich auf Upstream-Primary, Primary-Ports versorgen Downstream; ersetzt normalen Switch/Router |
| Transparent Clock | leitet PTP weiter, trägt Verweilzeit im Correction Field der Event-Messages ein |

- **E2E Transparent Clock**: misst Durchlaufzeit von SYNC und DELAY_REQUEST, korrigiert aber nicht die Leitungslaufzeit.
- **P2P Transparent Clock**: misst zusätzlich die Link-Laufzeit zum Upstream-Nachbarn (Peer Delay); Correction Field enthält dann Summe aller Verweil- und Link-Delays.

### PTP-Domäne
- Menge von Clocks, die sich untereinander synchronisieren; mehrere Domänen können ein Medium teilen.
- Default-Domäne **0**; Cisco-IE-Switches arbeiten mit einer Domäne; Boundary Clock verwirft Pakete mit falscher Domäne.

### Konfiguration (Cisco IOS XE, IE-Switches)
```
ptp mode {boundary {delay-req | pdelay-req} | e2etransparent | p2ptransparent}
ptp domain 8
interface Gi1/0/1
 ptp vlan 5                 ! PTP-VLAN auf Trunk (Default: Native VLAN); VLAN muss existieren und erlaubt sein
interface Vlan5
 ptp transport ipv4 udp     ! L3-PTP: nur IPv4
ptp source loopback        ! bzw. ptp source <address> / ptp source vlan
interface Gi1/0/2
 no ptp enable              ! PTP gezielt pro Interface abschalten
```
- boundary: Switch nimmt an der GM-Wahl teil; ohne bessere Clock wird er selbst Grandmaster.
- e2etransparent: Default-Modus (laut Kurs für IE-Switches; laut Catalyst-9300-Config-Guide 17.10 auch dort), weniger Jitter/Fehlerakkumulation als Boundary.
- Catalyst 9300 (Config Guide 17.10): Default-Profil global per Default deaktiviert; nach globaler Aktivierung auf allen Interfaces aktiv; L3-PTP nur IPv4 (IPv6 und VRF nicht unterstützt); Priority1 = 255 → Clock kann nicht Grandmaster werden; `show ptp parent` zeigt im Transparent-Modus nichts.
- p2ptransparent: Switch synchronisiert seine eigene Uhr nicht und nimmt nicht an der Primary-Wahl teil.
- Im Boundary-Modus werden nur PTP-Pakete im PTP-VLAN verarbeitet.

### Verifikation
- `show ptp brief` (Port-States aller Interfaces), `show ptp port <if>`, `show ptp clock` (Clock Identity, Priority1/2), `show ptp parent` (Grandmaster, auf den synchronisiert wird).

---

## 3. Logging / Syslog

### Grundlagen
- Lokales Logging skaliert nicht und geht beim Reload verloren → externe Ziele. Externe Mechanismen: **Syslog**, **SNMP-Traps**, **NetFlow-Export**.
- Syslog = Protokoll, um Event-Meldungen über IP an Collector zu senden; **UDP 514**, unzuverlässig (keine Bestätigung, keine Wiederholung).

### Ziele
| Ziel | Befehl | Hinweis |
|---|---|---|
| Console | `logging console [level]` | Default an, Level debugging; Console verarbeitet Log-Output immer – langsame Console + viele Debugs → CPU-Last |
| VTY/AUX (Telnet/SSH) | `logging monitor [level]` + pro Sitzung `terminal monitor` | ohne `terminal monitor` keine Meldungen in der SSH-Sitzung |
| Buffer (RAM) | `logging buffered [size] [level]` | zirkulär, älteste Meldungen werden überschrieben; `show logging` zeigt älteste zuerst |
| Syslog-Server | `logging host <ip>` (oder kurz `logging <ip>`), `logging trap <level>` | mehrfach eingeben → Liste von Servern; Default-Trap-Level informational (6) |
| Flash | `logging persistent` | übersteht Reload, gut für sporadische Probleme |
- `logging source-interface Loopback0` (eigenes Wissen): feste Absenderadresse.

### Format
`seq no: timestamp: %FACILITY-SEVERITY-MNEMONIC: description`
- seq no nur mit `service sequence-numbers`.
- Zeitstempel mit `service timestamps log datetime [msec] [localtime] [show-timezone]` (oder `uptime`). (Kurs schreibt fälschlich "service time stamps log".)
- Beispiel: `*Apr 22 11:05:55.423: %LINEPROTO-5-UPDOWN: Line protocol on Interface FastEthernet0/22, changed state to up` → Facility LINEPROTO, Severity 5, Mnemonic UPDOWN.
- Ein `*` vor dem Zeitstempel (eigenes Wissen) zeigt, dass die Uhr nicht autoritativ/synchron ist.

### Severity-Level
| Nr | Name (Keyword) | Bedeutung |
|---|---|---|
| 0 | emergencies | System unbenutzbar |
| 1 | alerts | sofortiges Handeln nötig |
| 2 | critical | kritischer Zustand |
| 3 | errors | Fehlerzustand |
| 4 | warnings | Warnung |
| 5 | notifications | normal, aber signifikant |
| 6 | informational | Information |
| 7 | debugging | Debug-Meldungen |
- **Filterlogik**: Ein konfiguriertes Level x schickt alle Meldungen mit Level 0 bis x (gleich oder schwerwiegender). Kleinere Zahl = schwerer.
- Debug-Ausgaben haben Level 7 → erscheinen nur auf Zielen mit Level debugging.

### Lab (Discovery 20)
```
R1(config)# logging 10.1.1.10
R1(config)# logging trap informational
%SYS-5-CONFIG_I: Configured from console by console
%SYS-6-LOGGINGHOST_STARTSTOP: Logging to host 10.1.1.10 port 514 started - CLI initiated
R1# show logging
Console logging: level debugging, 32 messages logged
Monitor logging: level debugging, 0 messages logged
Buffer logging:  level debugging, 32 messages logged
Trap logging: level informational, 35 message lines logged
    Logging to 10.1.1.10 (udp port 514, audit disabled, link up), 2 message lines logged
Log Buffer (4096 bytes): ...
```
- `no shutdown` / `shutdown` auf Et0/3 erzeugt: `%LINK-3-UPDOWN`, `%LINEPROTO-5-UPDOWN`, `%LINK-5-CHANGED` (administratively down), `%LINEPROTO-5-UPDOWN`, `%SYS-5-CONFIG_I` – fünf Meldungen.

---

## 4. SNMP

### Komponenten
- **Manager (NMS)**: sammelt Daten per Polling oder empfängt Traps; Historie, Trends, Alarme.
- **Agent**: auf dem Gerät; hält Werte gemäß **MIB** (Sammlung von Objektdefinitionen, Objekte über **OIDs** adressiert).
- Polling hat Verzögerung bis zum nächsten Poll; **Traps** = unaufgeforderte, ereignisbasierte Meldungen vom Agent (nahezu Echtzeit).
- Ports (eigenes Wissen/Standard): Agent **UDP 161** (Get/Set), Manager empfängt Traps/Informs auf **UDP 162**.

### Versionen und Operationen
| Version | Neuerungen / Sicherheit |
|---|---|
| SNMPv1 | Get, GetNext, Set, Response, Trap; Community (Klartext); heute selten |
| SNMPv2 (party-based) | komplexes Sicherheitsmodell, nie akzeptiert |
| SNMPv2c | de-facto-Standard v2; GetBulk, Inform (bestätigter Trap), 64-bit-Counter; Community im Klartext |
| SNMPv3 | Sicherheit: Authentifizierung, Integrität, Verschlüsselung; Policy pro Gruppe, Benutzer mit Algorithmen und Passwörtern |
- SNMPv3-Security-Level: **noAuthNoPriv** (nur Benutzername), **authNoPriv** (HMAC-MD5/SHA, keine Verschlüsselung), **authPriv** (zusätzlich Verschlüsselung; Kurs nennt CBC-DES, IOS XE unterstützt auch 3DES/AES).
- 64-bit-Counter (ifHC*): 32-bit-Bytezähler läuft bei 10 Gbit/s nach ca. 3,4 s über (2^32 Byte · 8 / 10^10 bit/s).

### Best Practices (Kurs)
- Nur Read-only vergeben; Schreibzugriff mit separater Community/Benutzer.
- **Views** auf benötigte MIB-Teilbäume begrenzen; ist eine View definiert, ist alles andere implizit verboten.
- ACLs auf bekannte Manager.
- SNMPv3 wo möglich; Communities nicht trivial und regelmäßig ändern.

### Konfiguration (eigenes Wissen, im Kurs nicht gezeigt)
```
access-list 10 permit host 10.1.1.50
snmp-server community NMSro ro 10
snmp-server view LIMITED ifMIB included
snmp-server group NETADMIN v3 priv read LIMITED access 10
snmp-server user ADMIN NETADMIN v3 auth sha AuthPass123 priv aes 128 PrivPass123
snmp-server host 10.1.1.50 version 3 priv ADMIN
snmp-server enable traps
```

---

## 5. NetFlow / Flexible NetFlow

### Komponenten
- **Flow Exporter** (im Kurs: das Gerät, das Flows sammelt und exportiert; in FNF-Konfiguration: das Objekt mit dem Ziel), **Flow Collector** (Server, empfängt Exporte), **Flow Analyzer** (Anwendung zur Auswertung, z. B. Secure Network Analytics/Stealthwatch).
- Anwendungen: Auswirkungen neuer Anwendungen, WAN-Spitzen reduzieren, Bandbreitenfresser finden, unerlaubten Verkehr erkennen, Anomalie-/Wurmerkennung, QoS-Validierung.
- NetFlow **pusht** periodisch (im Gegensatz zum SNMP-Polling).

### Flow
- Flow = Pakete derselben Konversation mit identischen Schlüsselmerkmalen. Traditionell 7 Key Fields: **Quell-IP, Ziel-IP, Quellport, Zielport, L3-Protokoll, ToS, Input-Interface**.
- Zusatzinfos (non-key): Zeitstempel (Dauer, pps/bps), Next Hop, BGP-AS, Masken, TCP-Flags, Byte-/Paketzähler.
- Erstes Paket mit neuer Merkmalkombination erzeugt einen neuen Cache-Eintrag; folgende Pakete werden gezählt.
- Zugriff: CLI (`show`-Befehle, Echtzeit) oder Collector (Reports, historisch).

### Export / Aging
- Flow wird exportiert, wenn: **inaktiv** länger als Inactive Timer (Default **15 s**), **aktiv** länger als Active Timer (Default **30 min**; lange Flows werden in mehrere Records zerlegt, Collector setzt sie zusammen), TCP **FIN/RST**, bzw. Cache voll (Emergency/Watermark aging).

### Exportformate
- **v5**: fest, verbreitet, nur IPv4 (eigenes Wissen: keine IPv6/MPLS).
- **v9**: **template-basiert**; Template mit ID beschreibt Feldtypen/-längen; erweiterbar (IPv6, Multicast, MPLS, BGP Next Hop).
- **IPFIX** (Version 10): IETF-Standard auf Basis von v9 (RFC 5101 → RFC 7011, RFC 5102 → RFC 7012).
- Platzierung: meist am zentralen Aggregationspunkt/WAN-Edge; Export kostet Bandbreite und Ressourcen.

### Flexible NetFlow (Discovery 21)
```
flow exporter EXPORTER1
 description Stealthwatch
 source Loopback0
 destination 10.1.1.10          ! genau EIN Ziel pro Exporter
 transport udp 2055
 ! export-protocol netflow-v9 | ipfix  (eigenes Wissen)
flow record LANCOPE1
 match ipv4 tos
 match ipv4 protocol
 match ipv4 source address
 match ipv4 destination address
 match transport source-port
 match transport destination-port
 match interface input
 collect routing next-hop address ipv4
 collect ipv4 dscp
 collect interface output
 collect counter bytes
 collect counter packets
 collect timestamp sys-uptime first
 collect timestamp sys-uptime last
flow monitor MONITOR1
 description Main Cache
 record LANCOPE1               ! genau ein Record pro Monitor
 exporter EXPORTER1            ! mehrere Exporter möglich
 cache timeout active 60
 cache timeout inactive 60
interface Ethernet0/0
 ip flow monitor MONITOR1 input
interface Ethernet0/2
 ip flow monitor MONITOR1 input
```
- **match = Key Fields** (bestimmen die Eindeutigkeit eines Flows); **collect = Non-Key Fields** (Zusatzinfo). Ein eigener Record braucht mindestens ein match.
- Monitor = speicherresidenter Cache; mehrere Monitore möglich, kosten aber Speicher.
- Input-Monitoring auf **allen** L3-Interfaces erfasst beide Richtungen jeder Konversation.
- Mehrere Collector → mehrere Exporter, alle im Monitor referenzieren.
- IPv6: eigener Record (match ipv6 ...) und `ipv6 flow monitor ... input`.

### Verifikation
```
R1# show flow monitor
Flow Monitor MONITOR1:
  Flow Record: LANCOPE1   Flow Exporter: EXPORTER1
  Cache: Type normal, Status allocated, Size 4096 entries
  Inactive Timeout 60 secs, Active Timeout 60 secs, Update Timeout 1800 secs
R1# show flow monitor MONITOR1 cache
  Current entries 5, Flows added 62, Flows aged 57 (Active timeout 57)
  IPV4 SOURCE ADDRESS 10.10.10.10  IPV4 DESTINATION ADDRESS 10.20.20.10
  TRNS SOURCE PORT 0  TRNS DESTINATION PORT 2048  IP PROTOCOL 1   -> ICMP Echo Request
  ...  TRNS SOURCE PORT 45288  TRNS DESTINATION PORT 23  IP TOS 0xC0  ip dscp 0x30 -> Telnet
```
- ICMP im Cache: Zielport = Typ·256 + Code → Echo Request (8/0) = 2048, Echo Reply (0/0) = 0.
- ToS 0xC0 = Precedence 6 = DSCP 0x30 = 48 (CS6). Zwei Rückflows mit ToS 0xC0 und 0x00 erscheinen als **getrennte** Flows, weil ToS Key Field ist.
- Weitere Befehle: `show flow exporter [name] [statistics]`, `show flow record`, `show flow interface`.

---

## 6. Cisco IOS EEM (Embedded Event Manager)

### Architektur
- Subsystem in IOS/IOS XE (auch XR, NX-OS): **Event Detectors** → **EEM Server** → **Policies** (Applets oder Tcl-Skripte) → **Actions**.
- **Applet**: in der CLI konfiguriert (`event manager applet NAME`), eine event-Zeile + nummerierte actions.
- **Tcl-Policy**: Skript in Tool Command Language, mächtiger (eigenes Wissen: Registrierung mit `event manager directory user policy flash:/eem` und `event manager policy name.tcl`).

### Event Detectors (Auswahl)
Application, CLI (Regex auf eingegebene Befehle), Counter, GOLD, Identity (802.1X/MAB), Interface (Zähler), IP SLA, Neighbor Discovery (CDP/LLDP), NetFlow, **None** (manuell per `event manager run`), Object Tracking (EOT), OIR, RPC (SOAP über SSHv2), Resource (Embedded Resource Manager; ersetzt Memory Threshold), RF (Redundanz), Routing, SNMP (MIB-Wert/Schwelle), SNMP Notification (Trap/Inform empfangen oder erzeugt), SNMP Object (GET/SET empfangen), **Syslog** (Regex auf Syslog-Meldungen), **Timer** (countdown, watchdog, cron, absolute), IOS Watchdog, WDSysMon.

### Actions (Auswahl)
CLI-Befehle ausführen, Syslog-Meldung erzeugen, SNMP-Trap senden, E-Mail senden, Reload, Wechsel auf Standby-Prozessor, Systeminfo sammeln, Tcl ausführen.

### Syntax (Beispiele)
```
event manager applet interface_Shutdown
 event syslog pattern "Interface Ethernet0/0, changed state to administratively down"
 action 1.0 cli command "enable"
 action 1.5 cli command "config t"
 action 2.0 cli command "interface e0/0"
 action 2.5 cli command "no shutdown"
 action 3.0 cli command "end"
 action 3.5 cli command "who"
 action 4.0 mail server "192.168.1.1" to "engineer@example.com" from "EEM@example.com" subject "..." body "Current users $_cli_result"

event manager applet Stop_Debug
 event cli pattern "debug" sync no skip yes
 action 1.0 cli command "enable"
 action 2.0 cli command "sh users | append unix:Debug"
 action 3.0 cli command "sh clock | append unix:Debug_clock"
```
Weitere (eigenes Wissen):
```
event timer watchdog time 300               ! alle 300 s
event timer countdown time 60               ! einmalig nach 60 s
event timer cron cron-entry "0 8 * * 1-5"   ! Mo–Fr 08:00
event track 1 state down
event none                                   ! manuell: event manager run NAME
action 1.0 syslog priority critical msg "Uplink down"
action 2.0 snmp-trap strdata "..."
action 3.0 reload
```
- Applet-CLI startet im **User EXEC** (Prompt `R1>`) → zuerst `action ... cli command "enable"`.
- Actions laufen in **alphanumerischer Reihenfolge der Labels** (String-Sortierung: "10" vor "2") – daher Labels wie 1.0, 1.5, 2.0 oder 010, 020 (eigenes Wissen, Cisco EEM Config Guide).
- `$_cli_result` = Ausgabe des letzten cli-Befehls; `$_syslog_msg` = auslösende Syslog-Meldung.
- `event cli ... sync no skip yes`: Befehl wird **nicht** ausgeführt, Policy läuft asynchron. `sync yes`: CLI wartet auf die Policy, deren Exit-Status entscheidet, ob der Befehl ausgeführt wird.
- Default **maxrun 20 s** (in `show event manager policy registered` sichtbar); längere Applets per `maxrun` im event-Befehl.
- EEM führt CLI-Aktionen über eine **VTY-Sitzung** aus (`%SYS-5-CONFIG_I: Configured from console by on vty0 (EEM:interface_Shutdown)`). Mit AAA-Command-Authorization braucht EEM `event manager session cli username <user>` (eigenes Wissen).
- Syslog-Pattern ist ein **regulärer Ausdruck** und wird als Teilstring gesucht: "Ethernet0/0, changed state to down" passt z. B. auch auf "GigabitEthernet0/0, ..." und sowohl auf die LINK- als auch die LINEPROTO-Meldung.

### Verifikation / Troubleshooting
- `show event manager policy registered` (Klasse, Typ, Event-Typ, Zeit, Name, maxrun, Actions).
- `debug event manager action cli` → `%HA_EM-6-LOG: <applet> : DEBUG(cli_lib) : : IN/OUT ...`.
- Fehler in einer Action (z. B. `%HA_EM-3-FMPD_SMTP` – SMTP-Server nicht erreichbar, `%HA_EM-3-FMPD_ERROR ... statement 4.0`) beendet das Applet an dieser Stelle; vorherige Actions sind bereits ausgeführt.
- Lab-Effekt: Das interface_Shutdown-Applet macht jedes administrative Abschalten von Et0/0 sofort rückgängig.

### Einsatzzwecke
- Troubleshooting sporadischer Probleme (automatisches Sammeln von show/debug-Ausgaben im richtigen Moment).
- Workarounds bis zur Root-Cause-Analyse (z. B. Interface automatisch zurücksetzen).
- Beispiele aus dem Kurs: Befehle sperren (z. B. reload), Konfig-Änderungen melden, Konfiguration sichern, Routing-Tabellen-Änderungen melden, Erreichbarkeit periodisch prüfen.

---

## Fehler/Ungenauigkeiten im Kurs
1. **"It is not possible to adjust the NTP poll interval on a router."** – Falsch für IOS/IOS XE: `ntp server <ip> minpoll <4-17> maxpoll <4-17>` existiert. (Cisco IOS Basic System Management Command Reference, `ntp server`.)
2. **"Cisco devices support only MD5 authentication for NTP."** – Veraltet: neuere IOS-XE-Releases unterstützen zusätzlich z. B. `hmac-sha1`/`hmac-sha2-256` bzw. `cmac-aes-128` bei `ntp authentication-key` (IOS XE 17.x Command Reference).
3. ACL-Beispiel **`access-list 1 permit 10.1.0.0.0.0.255.255`** – Tippfehler, korrekt `access-list 1 permit 10.1.0.0 0.0.255.255`. Außerdem "Corel" statt "Core1".
4. Syslog-Tabelle: **"service time stamps log[datetime | log]"** – korrekt `service timestamps log [datetime | uptime]`.
5. **"The highest severity level is level 7"** – missverständlich: 7 (debugging) ist die höchste *Nummer*, aber die *geringste* Schwere; die schwerste Stufe ist 0 (emergencies).
6. **"By default ... the default severity level is debugging"** – gilt für Console/Monitor/Buffer; für `logging trap` (Syslog-Server) ist der Default informational (Cisco Command Reference `logging trap`).
7. PTP: **"range is from 4 to 127. The default value is 0"** für `ptp domain` – widersprüchlich (Default liegt außerhalb des genannten Bereichs); Plattformdoku prüfen (Catalyst/IE: 0–127 bzw. profilabhängig). Hinweis: Der Catalyst-9300-Config-Guide 17.10 enthält denselben Widerspruch (Befehlsbeschreibung 4–127, Default 0; AES67-Tabelle 0–255).
8. NetFlow: **"About 15 percent of the switched traffic is used for export"** – Cisco nennt ca. **1,5 %** Exportvolumen (Cisco NetFlow Performance Analysis White Paper). 15 % ist vermutlich ein Kommafehler.
9. NetFlow-Schritte: Bündeln von 30–50 Flows in UDP wird "NetFlow Monitor" genannt und der Cache "NetFlow record" – Begriffe vermischt: In FNF ist der Record die Feld-Definition, der Monitor der Cache, der Exporter das Exportziel.
10. "IPFIX v10 does not have anything to do with NetFlow" – irreführend: IPFIX basiert direkt auf NetFlow v9 (RFC 3954 → RFC 7011).
11. SNMP-authPriv: nur "CBC-DES" genannt – IOS XE unterstützt auch 3DES und AES-128/192/256 (`snmp-server user ... priv aes 128`).
12. EEM-Lab-Text: "show users | append flash:Debug" im Fließtext, Befehle nutzen `unix:` – nur Inkonsistenz (Lab-Plattform).

## Bilder
- `bilder/19-services/01-ntp-stratum.svg` – NTP-Hierarchie von Referenzuhr (Stratum 0/1) über Stratum 2/3 bis zu den Clients, Stratum = Hops + 1, Stratum 16 = unsynchronisiert.
- `bilder/19-services/02-ntp-modi.svg` – Die vier NTP-Modi (Client/Server, Peer, Broadcast) mit Befehlen und Richtung des Zeitflusses.
- `bilder/19-services/03-ntp-sicherheit.svg` – NTP-Authentifizierung (Server wird gegenüber Client authentisiert) und die vier `ntp access-group`-Stufen.
- `bilder/19-services/04-ptp-clocks.svg` – PTP-Hierarchie mit Grandmaster, Boundary Clock, Transparent Clock und Ordinary Clocks, Primary-/Secondary-Ports.
- `bilder/19-services/05-ptp-bmca.svg` – BMCA-Vergleichsreihenfolge Priority1 → Class → Accuracy → Variance → Priority2 → Identity (niedriger gewinnt).
- `bilder/19-services/06-syslog-level.svg` – Aufbau einer Syslog-Meldung und Severity-Skala 0–7 mit Filterlogik "Level x = 0 bis x".
- `bilder/19-services/07-snmp.svg` – SNMP-Manager/Agent/MIB mit Get/Set (UDP 161), Trap/Inform (UDP 162) und SNMPv3-Security-Levels.
- `bilder/19-services/08-netflow-ablauf.svg` – Flow-Erkennung über Key Fields, Cache, Aging-Trigger und Export an Collector/Analyzer.
- `bilder/19-services/09-fnr-bausteine.svg` – Flexible-NetFlow-Objekte Record (match/collect), Exporter, Monitor und Interface-Zuordnung.
- `bilder/19-services/10-eem-ablauf.svg` – EEM-Architektur: Event Detector → EEM Server → Applet/Tcl-Policy → Actions, mit Applet-Beispiel.
