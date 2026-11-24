# Implementing Infrastructure Security

Quelle: ENCOR 1.4.10 Student Guide, Seiten 244–252 (243 Intro, 253 Summary Challenge und 254 Answer Key nicht ausgewertet)

Topics: ENCOR-5.2.a (ACLs), ENCOR-5.2.b (CoPP), ENCOR-5.1.a (Zugriffsschutz der vty-Lines mit `access-class`)

Ergänzungen, die nicht im Kurs stehen, sind mit *(Ergänzung)* markiert (Wildcard-Rechnungen, Verhalten nicht existierender ACLs, Bc-Formel des Policers, Catalyst-9000-CoPP, ICMP-Unreachable-Ratenbegrenzung). Quellen: Cisco IOS XE 17.x Security Configuration Guide (IP Access Lists), Cisco IOS QoS Command Reference (`police`), Catalyst 9000 CoPP Configuration Guide.

---

## 1. ACL-Typen (S. 244)

Zwei Arten und zwei Kennzeichnungsmethoden:

| Art | prüft | wirkt auf |
|---|---|---|
| Standard-ACL | nur **Quell-IP** | gesamte Protokollfamilie (IP) |
| Extended-ACL | Quell- und Ziel-IP, Protokoll, Ports, weitere Felder (z. B. TCP-Flags, ICMP-Typ) | gezielt einzelne Protokolle/Anwendungen |

Kennzeichnung: **nummeriert** (Zahl) oder **benannt** (alphanumerischer Name).

| IPv4-ACL-Typ | Nummernbereich |
|---|---|
| Numbered Standard | 1–99 und (erweitert) 1300–1999 |
| Numbered Extended | 100–199 und (erweitert) 2000–2699 |
| Named (Standard und Extended) | Name |

- Die Nummer bestimmt, welche Syntax der Router akzeptiert (1–99/1300–1999 → nur Quelle; 100–199/2000–2699 → Extended-Syntax).
- Es können beliebig viele ACLs existieren, aber pro Interface gilt: **eine ACL pro Protokoll (Layer 3, z. B. IPv4/IPv6), pro Richtung (in/out)**. Ein zweites `ip access-group ... in` ersetzt das erste.

## 2. Nummerierte ACLs (S. 245)

### Standard
```
RouterX(config)# access-list 1 permit 172.16.0.0 0.0.255.255
RouterX# show access-lists
Standard IP access list 1
    10 permit 172.16.0.0, wildcard bits 0.0.255.255
```
- Filtert auf Quelladresse + **Wildcard-Maske** (keine Subnetzmaske!).
- Fehlt die Wildcard, gilt **0.0.0.0** (exakter Host) – nur bei Standard-ACLs.
- `no access-list 1` löscht die **gesamte** ACL. Einzelne Zeilen per `no access-list ...` klassisch nicht entfernbar (früher: ACL in Texteditor kopieren, löschen, neu einfügen). Neuere IOS-Versionen: Sequenznummern; nummerierte ACLs lassen sich auch über `ip access-list standard 1` bearbeiten.

### Extended
```
RouterX(config)# access-list 101 deny tcp 172.16.4.0 0.0.0.255 172.16.3.0 0.0.0.255 eq 21
RouterX(config)# access-list 101 permit ip any any
RouterX# show access-lists 101
Extended IP access list 101
    10 deny tcp 172.16.4.0 0.0.0.255 172.16.3.0 0.0.0.255 eq ftp
    20 permit ip any any
```
- Syntax: `access-list <nr> {permit|deny} <protokoll> <quelle> <wildcard> [operator port] <ziel> <wildcard> [operator port] [established] [log]`
- Protokoll per Name oder Nummer: häufig `ip`, `tcp`, `udp`, `icmp`; auch `ospf` (89), `eigrp` (88), `gre` (47) oder Nummer, z. B. `112` (VRRP).
- Port-Operatoren (nur bei TCP/UDP): `eq`, `neq`, `lt`, `gt`, `range a b` (inklusiv). Ports per Nummer oder Name (`www`=80, `ftp`=21, `telnet`=23, `domain`=53, `snmp`=161 …). IOS ersetzt in der Anzeige bekannte Nummern durch Namen (21 → `ftp`, 80 → `www`).
- Port-Angabe **hinter der Quelle** = Quellport, **hinter dem Ziel** = Zielport.
- Best Practice: Extended-ACL **nahe der Quelle** des zu verwerfenden Verkehrs, korrekte Richtung.

### Wildcard-Masken *(Ergänzung, Rechenregeln)*
- Bit 0 = muss übereinstimmen, Bit 1 = egal.
- Für zusammenhängende Präfixe: Wildcard = 255.255.255.255 − Subnetzmaske (/24 → 0.0.0.255, /20 → 0.0.15.255, /27 → 0.0.0.31, /30 → 0.0.0.3).
- `host 10.1.1.1` = `10.1.1.1 0.0.0.0`; `any` = `0.0.0.0 255.255.255.255`.
- Bereiche zusammenfassen: 10.10.8.0–10.10.11.255 = `10.10.8.0 0.0.3.255` (Blockgröße 4 im 3. Oktett, Start muss durch 4 teilbar sein).
- Nicht zusammenhängende Wildcards möglich: `192.168.1.1 0.0.0.254` = alle ungeraden Hosts in 192.168.1.0/24.
- Typischer Fehler: Subnetzmaske statt Wildcard (`permit 10.1.1.0 255.255.255.0` matcht jede Adresse, deren letztes Oktett 0 ist).

## 3. ACLs zur Verkehrsfilterung (S. 246)

Szenario: PC2 soll kein Internet bekommen. Möglich: Standard-ACL **inbound** auf dem LAN-Interface oder **outbound** auf dem Internet-Interface. Andere Hosts (PC1) explizit erlauben – sonst greift das implizite deny.

Abarbeitung:
- ACEs werden **von oben nach unten** geprüft, **erster Treffer entscheidet**, danach keine weitere Prüfung.
- Am Ende steht ein **implizites `deny any`** (nicht in `show access-lists` sichtbar, keine Zähler). Eine ACL mit nur deny-Zeilen blockiert alles.
- Verworfene Pakete: Router sendet ICMP Destination Unreachable (administratively prohibited) an den Absender (Ping zeigt `U`).

**Outbound-ACL** (Flussdiagramm): Paket kommt an → Routing-Lookup (kein Eintrag → verwerfen) → Ausgangsinterface gewählt → ACL vorhanden? nein → senden; ja → ACEs prüfen → permit → senden, deny/kein Treffer → verwerfen + Absender benachrichtigen.

**Inbound-ACL**: Prüfung **vor** dem Routing-Lookup → spart Lookup bei verworfenen Paketen, daher effizienter.

## 4. ACLs auf Interfaces anwenden (S. 247)

```
Branch(config)# access-list 1 deny host 10.1.1.101
Branch(config)# access-list 1 permit 10.1.1.0 0.0.0.255
Branch(config)# interface GigabitEthernet0/1        ! Richtung Internet
Branch(config-if)# ip access-group 1 out
```
oder Extended, nahe der Quelle:
```
Branch(config)# access-list 101 deny ip host 10.1.1.101 any
Branch(config)# access-list 101 permit ip 10.1.1.0 0.0.0.255 any
Branch(config)# interface GigabitEthernet0/0        ! LAN
Branch(config-if)# ip access-group 101 in
```
- Ablauf: ACL anlegen → Interface wählen → `ip access-group <nr|name> {in|out}`.
- Entfernen: `no ip access-group ...` am Interface, danach ggf. `no access-list <nr>` global.
- Standard-ACL inbound auf dem LAN-Interface würde zusätzlich **jede** Kommunikation PC2 ↔ Router unterbinden (auch Gateway-Ping, Telnet/SSH zum Router usw.).
- Platzierung: Standard **nahe Ziel** (filtert sonst zu viel, da nur Quelle bekannt), Extended **nahe Quelle** (verwirft unerwünschten Verkehr früh, spart Bandbreite).
- *(Ergänzung)* Wird mit `ip access-group` eine **nicht existierende** ACL referenziert, filtert IOS nicht (alles erlaubt). Outbound-ACLs filtern **keinen vom Router selbst erzeugten** Verkehr.

## 5. Named ACLs (S. 248)

```
Branch(config)# ip access-list standard Subnet_ONLY
Branch(config-std-nacl)# permit 10.1.1.0 0.0.0.255
Branch(config)# interface Gi0/0
Branch(config-if)# ip access-group Subnet_ONLY in
```
- Modus `config-std-nacl` bzw. `config-ext-nacl`; Name eindeutig, Großschreibung empfohlen (nicht Pflicht).
- Sequenznummern automatisch ab **10 in 10er-Schritten**; eigene Nummern möglich → Einfügen an beliebiger Stelle:
```
Branch(config)# ip access-list standard Subnet_ONLY
Branch(config-std-nacl)# 5 deny host 10.1.1.25
Branch# show access-lists
Standard IP access list Subnet_ONLY
    5 deny   10.1.1.25
    10 permit 10.1.1.0, wildcard bits 0.0.0.255
```
- `no 10` löscht genau Zeile 10.
- Neu nummerieren ohne Reload: `ip access-list resequence <name> <start> <schritt>` (Kurs schreibt verkürzt „access-list resequence“). Laut Kurs nummeriert ein Reload die Einträge ebenfalls neu (10, 20 …).
- Auch nummerierte ACLs können im ACL-Konfigurationsmodus bearbeitet werden (Nummer statt Name).

Extended Named:
```
Branch(config)# ip access-list extended WWW-ACCESS
Branch(config-ext-nacl)# 30 permit tcp 10.1.1.0 0.0.0.255 any eq 80
Branch(config-ext-nacl)# 40 permit tcp 10.1.1.0 0.0.0.255 any eq 443
Branch(config-if)# ip access-group WWW-ACCESS in
Extended IP access list WWW-ACCESS
    30 permit tcp 10.1.1.0 0.0.0.255 any eq www
    40 permit tcp 10.1.1.0 0.0.0.255 any eq 443
```

## 6. Discovery 25 – Standard- und Extended-ACLs

Topologie: PC1 10.10.1.10/24 – R1 E0/0 (10.10.1.1) · SRV1 10.10.2.20/24 – R1 E0/1 (10.10.2.1) · R1 E0/3 198.51.100.2/30 – R2 E0/3 198.51.100.1 · R2 E0/0 203.0.113.1/24 mit PC2 (.40) und SRV2 (.30, DNS + HTTP/HTTPS). Statisches Routing. Erst Konnektivität testen (Telnet auf Port 80/443 als einfacher Port-Test), dann ACLs.

1. **Numbered Standard nahe Ziel** – PC1 darf nicht ins 10.10.2.0/24:
```
access-list 1 deny host 10.10.1.10
access-list 1 permit any
interface Ethernet0/1
 ip access-group 1 out
```
PC1-Ping auf SRV1 → `U.U.U` (Unreachables vom Router), PC2 klappt. DNS von PC1 funktioniert weiter (anderes Ziel).
```
R1# show access-list
Standard IP access list 1
    10 deny   10.10.1.10 (8 matches)
    20 permit any (5 matches)
```
2. **Named Standard auf vty-Lines**:
```
ip access-list standard VTY-ACCESS
 permit host 10.10.1.10
 deny any log
line vty 0 4
 access-class VTY-ACCESS in
```
- Explizites `deny any log` nur, um Logging/Zähler zu bekommen. Log-Meldung z. B. `%SEC-6-IPACCESSLOGNP: list VTY-ACCESS denied 0 203.0.113.40 -> 0.0.0.0, 1 packet`. PC2 erhält `% Connection refused by remote host`.
- `log` ist CPU-intensiv (Process-Switching der passenden Pakete + Erzeugen der Meldungen) → in Produktion vorsichtig.
- `access-class` gilt für Verbindungen **zu** den Lines, unabhängig vom Eingangs-Interface.
3. **Named Extended inbound am Internet-Interface E0/3** (TRAFFIC-FILTER):
```
ip access-list extended TRAFFIC-FILTER
 permit tcp any host 10.10.2.20 eq www
 permit tcp any host 10.10.2.20 eq 443
 permit icmp any 10.10.1.0 0.0.0.255 echo-reply
 permit udp host 203.0.113.30 eq domain 10.10.1.0 0.0.0.255
 permit tcp any eq www 10.10.1.0 0.0.0.255 established
 permit tcp any eq 443 10.10.1.0 0.0.0.255 established
 deny ip any any
interface Ethernet0/3
 ip access-group TRAFFIC-FILTER in
```
- `established` matcht TCP-Segmente mit gesetztem **ACK oder RST** → nur Antworten auf intern aufgebaute Verbindungen; neue Verbindungen von außen (nur SYN) werden nicht erfasst.
- Rückverkehr wird über den **Quellport** geprüft (DNS-Antwort: Quellport 53; HTTP-Antwort: Quellport 80).
- Ping von PC2 auf PC1 scheitert (Echo-Request nicht erlaubt).
4. **Einfügen** einer Zeile: `65 permit tcp host 203.0.113.40 host 10.10.2.20 eq 22` landet zwischen 60 und 70 (vor dem expliziten deny). Löschen z. B. mit `no 40`.

Beispiel-Zähler:
```
Extended IP access list TRAFFIC-FILTER
    10 permit tcp any host 10.10.2.20 eq www (13 matches)
    ...
    65 permit tcp host 203.0.113.40 host 10.10.2.20 eq 22 (32 matches)
    70 deny ip any any (5 matches)
```

## 7. Control Plane – Überblick (S. 250)

Control Plane = Hardware/Software für Routing und Management; braucht CPU des Route Processors (RP).

Vier logische **Traffic Planes**:
| Plane | Beispiele | Ziel aus Sicht des Geräts |
|---|---|---|
| Data | Benutzerverkehr Endgerät→Endgerät | transit |
| Control | ARP, BGP, OSPF | receive (CPU) |
| Management | Telnet, SSH, TFTP, SNMP, FTP, NTP | receive (CPU) |
| Services | GRE, QoS, MPLS-VPN, SSL/IPsec-Verschlüsselung („high-touch“) | transit oder receive (z. B. VPN-Endpunkt) |

Drei Pakettypen aus lokaler Sicht:
- **Transit**: normale zielbasierte Weiterleitung per CEF → „fast path“.
- **Receive**: an das Gerät selbst adressiert (Control/Management) → müssen zur CPU → „**punt**“ = Verschieben aus dem Fast Path in den langsamen Pfad des RP.
- **Exception-IP und Non-IP**: IPv4 mit IP-Optionen, TTL abgelaufen, unerreichbares Ziel; Non-IP: Layer-2-Keepalives, IS-IS, CDP, PPP LCP → ebenfalls RP.

Der Punt-Pfad/RP schafft viel weniger Pakete/s als der Fast Path. Überlast (bösartig: Floods, gecraftete Pakete; nicht bösartig: Fehlkonfiguration, Bugs, Rekonvergenz) gefährdet Routing und Management → RP schützen.

## 8. Control Plane Policing (S. 251)

- Interface-ACLs: wirken auf **alle** Pakete eines Interfaces (alle Planes) und müssen auf **jedem** Interface konfiguriert werden → mühsam.
- **CoPP** behandelt die Control Plane als eigene Einheit mit virtuellem Ein-/Ausgang; erlaubt permit/deny und **Ratenbegrenzung** von Verkehr zur CPU. Einmal konfiguriert, gilt für alle Interfaces.
- Konfiguration über **MQC** (wie QoS), nur der Anwendungsort unterscheidet sich. Bei CoPP ist **Policing** die relevante Aktion.

Drei Schritte (Reihenfolge: ACL → class-map → policy-map → service-policy):
```
access-list 100 permit udp any any eq snmp
access-list 100 permit tcp any any eq www
access-list 100 permit tcp any any eq 443
access-list 100 permit tcp any any eq 22
class-map COPP_class
 match access-group 100
policy-map COPP_policy
 class COPP_class
  police 300000 conform-action transmit exceed-action drop
 class class-default
  police rate 50 pps conform-action transmit exceed-action drop
control-plane
 service-policy input COPP_policy
```
- `police <bps>` oder `police rate <n> pps`.
- `class-default`: immer automatisch am Ende, implizites `match any`, keine eigenen Match-Kriterien.
- class-map ohne Schlüsselwort = `match-all`.

Verifikation:
| Befehl | zeigt |
|---|---|
| `show access-lists 100` | welche ACEs Treffer haben |
| `show class-map` | Klassen und Match-Kriterien |
| `show policy-map` | konfigurierte Aktionen (z. B. `police cir 300000 bc 9375`) |
| `show policy-map control-plane` | **dynamische** Zähler: conformed/exceeded Pakete/Bytes, Raten, Drops |

*(Ergänzung)* Default-Bc beim Single-Rate-Policer = CIR/32 in Byte (= 250 ms Verkehr), mindestens 1500 Byte: 300000 → 9375, 100000 → 3125, 50000 → 1562, 8000 und 12000 → 1500 (deckt sich mit den Kursausgaben). Die 250-ms-Regel ist im Cisco IOS XE QoS MQC Configuration Guide („QoS Packet Policing“) dokumentiert; das 1500-Byte-Minimum ist aus den Kursausgaben abgeleitet und kann je Plattform abweichen.

## 9. Discovery 26 – CoPP

Topologie: PC1 10.1.1.50, R1 10.1.1.1, R2 10.1.1.2 im selben Segment; OSPFv2 und VRRP (R2 Master, VIP 10.1.1.254).

```
ip access-list extended COPP-ICMP
 permit icmp any any
ip access-list extended COPP-TELNET
 permit tcp any any eq telnet
ip access-list extended COPP-OSPF
 permit ospf any any
ip access-list extended COPP-VRRP
 permit 112 any host 224.0.0.18
class-map COPP-MAP-ICMP
 match access-group name COPP-ICMP
 ...
policy-map ROUTER-COPP-POLICY
 class COPP-MAP-ICMP
  police 8000 conform-action transmit exceed-action drop
 class COPP-MAP-TELNET
  police 100000 conform-action transmit exceed-action drop
 class COPP-MAP-OSPF
  police 300000 conform-action transmit exceed-action drop
 class COPP-MAP-VRRP
  police 50000 conform-action transmit exceed-action drop
 class class-default
  police 12000 conform-action transmit exceed-action transmit
control-plane
 service-policy input ROUTER-COPP-POLICY
%CP-5-FEATURE: Control-plane Policing feature enabled on Control plane aggregate path
```
- VRRP = IP-Protokoll **112**, Multicast **224.0.0.18** (OSPF 89, EIGRP 88).
- ACL-`permit` = gehört zur Klasse. Laut Kurs: `deny` → Paket geht ungepolict zur CPU (siehe Fehlerliste).
- class-default enthält Layer-2-Keepalives, Non-IP (z. B. IS-IS) → **nie** mit conform **und** exceed = drop policen; Best Practice: class-default nicht ratenbegrenzen (im Lab nur als Beispiel, exceed = transmit).
- Nach Aktivierung: OSPF- und VRRP-Hellos erzeugen sofort ACL-Treffer.
- Test: `ping 10.1.1.1 repeat 1000` von PC1 → einzelne `.` im Ping, weil ICMP über 8 kbps verworfen wird. Ausgabe (gekürzt):
```
Class-map: COPP-MAP-ICMP (match-all)
  547 packets, 62358 bytes
  police:
    cir 8000 bps, bc 1500 bytes
    conformed 508 packets, 57912 bytes; actions: transmit
    exceeded 39 packets, 4446 bytes; actions: drop
```
- Telnet (100 kbps) bleibt ohne Drops.
- Viele Treffer in class-default → **Catch-All-Klasse** (ACL COPP-CATCH-ALL mit permit tcp/udp/icmp/ip any any, z. B. 50 kbps, exceed drop) vor class-default einfügen, mit `clear access-list counters` + `show access-lists` analysieren: (1) übersehener legitimer Receive-Verkehr, (2) Angriff → verwerfen, (3) legitimer Rest.
- *(Ergänzung)* Catalyst 9000: CoPP ist ab Werk mit der System-Policy `system-cpp-policy` aktiv; Raten der Systemklassen sind anpassbar.

## Fehler/Ungenauigkeiten im Kurs

1. **S. 248, Kontrollfrage zu SSH**: Alle Antwortoptionen beginnen mit `ip access-list 101 deny ...` – das ist ungültige Syntax. Nummerierte Einträge werden mit `access-list 101 deny tcp ... eq 22` angelegt; `ip access-list` erwartet `standard|extended|resequence|...`. (Cisco IOS XE Security Command Reference, `access-list (IP extended)`.)
2. **S. 248**: „access-list resequence“ – korrekter Befehl ist `ip access-list resequence <acl> <start> <increment>` (globaler Modus).
3. **S. 249, Step 8**: Testliste nennt „PC2 … Telnet zu SRV2 Port 443“, die gezeigte Ausgabe stammt aber von PC1 (Antwortverkehr Port 443 an 10.10.1.0/24 wird durch die established-Zeile erlaubt; gemeint ist PC1).
4. **S. 252**: „Ein deny in der CoPP-ACL leitet Pakete ungepolict an die Control Plane weiter“ ist ungenau: Ein deny bedeutet nur, dass das Paket **nicht zu dieser Klasse** gehört; es wird gegen die folgenden Klassen und zuletzt gegen class-default geprüft und dort ggf. gepolict. (Cisco „Deploying Control Plane Policing“ White Paper / CoPP Config Guide.)
5. **S. 245, Hinweis**: In der Kontrollfrage „Which two commands correctly create standard access lists?“ sind `access-list 1 permit 172.16.0.0` (Wildcard 0.0.0.0 → nur Host 172.16.0.0) und `access-list 1 permit 172.16.0.0 255.255.0.0` (Maske als Wildcard → falscher Match) syntaktisch gültig; „korrekt“ ist dort im Sinne von „matcht das Netz 172.16.0.0/16“ zu verstehen.

## Bilder

- `01-acl-typen.svg` – Standard vs. Extended: geprüfte Header-Felder und Nummernbereiche.
- `02-wildcard.svg` – Wildcard-Bits (0 = prüfen, 1 = egal) mit Rechenbeispielen und host/any.
- `03-acl-ablauf.svg` – Top-down-Abarbeitung, first match, implizites deny.
- `04-in-out.svg` – Inbound- vs. Outbound-ACL relativ zum Routing-Lookup.
- `05-platzierung.svg` – Platzierung Standard nahe Ziel, Extended nahe Quelle (Discovery-25-Topologie).
- `06-traffic-planes.svg` – Data/Control/Management/Services-Plane, Fast Path vs. Punt zum RP.
- `07-copp.svg` – Interface-ACL vs. CoPP auf der virtuellen Control-Plane-Schnittstelle, MQC-Kette.
