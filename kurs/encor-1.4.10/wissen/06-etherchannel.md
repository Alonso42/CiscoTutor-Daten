# Implementing Layer 2 Port Aggregation

Quelle: ENCOR 1.4.10 Student Guide, Seiten 51–58 (Need for EtherChannel, EtherChannel Mode Interactions, Layer 2 EtherChannel Configuration Guidelines, EtherChannel Load-Balancing Options, Troubleshoot EtherChannel Issues, Discovery 6 „Troubleshoot EtherChannel“, Describe Policy-Based Routing, Summary)

Topics: ENCOR-3.1.b (Layer-2-/Layer-3-EtherChannel, LACP, PAgP, statisch), ENCOR-3.2.d (Policy-Based Routing)

Ergänzungen aus eigenem Fachwissen bzw. aus dem Prüfprotokoll (nicht im Kurs) sind mit *(Ergänzung)* markiert.

## Warum EtherChannel?

- Mehr Bandbreite durch schnellere Links ist teuer und endlich. Mehr parallele Links zwischen zwei Switches helfen ohne Bündelung nicht: STP sieht eine Schleife und blockiert alle bis auf einen. Uplinks werden zum Engpass (Congestion Point), wenn viele Access-Ports auf einen Uplink treffen.
- **EtherChannel** fasst mehrere physische Ports zu einem logischen Port (**Port-channel**, `Po<n>`) zusammen. Ursprünglich von Cisco für Fast Ethernet/Gigabit Ethernet entwickelt.
- STP, Routing-Protokolle usw. sehen nur das logische Interface → nichts wird blockiert, alle Member leiten weiter.

Vorteile:
| Vorteil | Erklärung |
|---|---|
| Logische Aggregation | n Links = ein Interface; Konfiguration einmal am Port-channel, gilt konsistent für alle Member |
| Mehr Bandbreite | vorhandene Ports nutzen statt teurer Upgrades |
| Load Sharing | Verteilung per Hash (MAC, IP, L4-Ports – plattformabhängig) |
| Ein logischer STP-Port | keine Blockierung innerhalb des Bündels |
| Redundanz | Ausfall eines Members = keine Topologieänderung, keine STP-Neuberechnung, nur weniger Durchsatz; der Channel läuft, solange mindestens ein Member aktiv ist |

Grenzen/Regeln:
- Ein EtherChannel verbindet immer genau **zwei Geräte** (Switch–Switch, Switch–Server/Router/Firewall). *(Ergänzung)* Ausnahme mit Multichassis-Techniken (StackWise Virtual, VSS, vPC) – dort erscheinen zwei Chassis als ein logischer Partner.
- 2–8 aktive Ports pro Bündel; bei LACP bis zu 16 Ports konfigurierbar, davon 8 aktiv und 8 Hot-Standby.
- Keine gemischten Porttypen/Geschwindigkeiten (Fast Ethernet + Gigabit nicht in einem Bündel).
- Mehrere EtherChannels zwischen denselben zwei Switches sind möglich – dann blockiert STP ein ganzes EtherChannel (alle seine Member).

## Aushandlungsprotokolle und Modi

| Methode | Standard | Modi | Bemerkung |
|---|---|---|---|
| LACP | IEEE 802.3ad (heute 802.1AX) | `active`, `passive` | herstellerübergreifend |
| PAgP | Cisco-proprietär | `desirable`, `auto` | nur Cisco-Geräte |
| statisch | – | `on` | keine Protokollpakete, keine Prüfung |

Modi:
- **active** (LACP) / **desirable** (PAgP): sendet unbedingt Aushandlungspakete.
- **passive** (LACP) / **auto** (PAgP): antwortet nur, wenn die Gegenseite verhandelt.
- **on**: bündelt sofort ohne Aushandlung; on-Ports senden weder PAgP noch LACP.

Kombinationen, die ein Bündel bilden:
| Seite A \ Seite B | on | active | passive | desirable | auto |
|---|---|---|---|---|---|
| on | ja | – | – | – | – |
| active | – | ja | ja | – | – |
| passive | – | ja | nein | – | – |
| desirable | – | – | – | ja | ja |
| auto | – | – | – | ja | nein |

Merksatz: Mindestens eine Seite muss aktiv werben; LACP und PAgP sprechen nicht miteinander; `on` funktioniert nur mit `on`. Ein Bündel nutzt genau ein Protokoll.

### LACP im Detail
- Tauscht LACPDUs aus, vergleicht die Port-Fähigkeiten und prüft Konsistenz (Speed, Duplex, VLAN-Konfiguration). Erleichtert gemischte Herstellerumgebungen.
- Der Switch mit der **niedrigsten System Priority** (bzw. System-ID = Priority + MAC) ist der entscheidende Partner und bestimmt, welche Ports aktiv werden – nach **Port Priority** (niedriger Wert = höhere Priorität, Gleichstand → niedrigere Portnummer).
- Üblich: bis 16 Links zuweisbar, max. 8 aktiv; überzählige Ports sind **Hot-Standby** (Flag `H`) und springen bei Ausfall ein. Maximale Zahl aktiver Links ist plattformabhängig.
- *(Ergänzung)* System- und Port-Priority: Default 32768, Bereich 1–65535. Befehle: `lacp system-priority <n>` (global), `lacp port-priority <n>` (Interface), `lacp max-bundle <1–8>` (Port-channel), `port-channel min-links <2–8>` (Port-channel; zu wenige Member → Po down, Flag `M`), `lacp rate fast` (LACPDU jede Sekunde statt alle 30 s; Timeout 3 Intervalle). LACP-Ziel-MAC 0180.c200.0002.
- *(Ergänzung)* `channel-protocol {lacp | pagp}` (Interface) schränkt die erlaubten Modi ein. LACP- und PAgP-Modi lassen sich nicht im selben Channel mischen (IOS lehnt das mit „Invalid etherchnl mode“ ab).

### PAgP im Detail
- Cisco-proprietär; bündelt nur Ports mit gleichen Eigenschaften (Speed, Duplex, Native VLAN, VLAN-Range, Trunking-Status und -Typ) und meldet das Bündel als einen Port an STP.
- Zusätzliche Option für `auto`/`desirable`:
  - **non-silent**: Bündel erst, wenn bidirektionaler Verkehr bestätigt ist (der Port muss empfangen und senden) → Schutz vor unidirektionalen Fehlern, typisch bei Glasfaser, die sonst Bridging Loops verursachen können.
  - **silent**: Bündel auch ohne empfangene Pakete; für stille Partner (z. B. Fileserver oder Packet Analyzer, der keinen Verkehr erzeugt). Ohne silent würde ein PAgP-Port am stillen Partner nie operativ.
  - *(Ergänzung)* Wird `non-silent` nicht angegeben, gilt **silent** (Cat9300 Config Guide).

```
interface range Gi1/0/1 - 2
 channel-group 3 mode desirable non-silent
```

### Statisch (on)
- Kein Overhead, keine Verzögerung durch Aushandlung, aber auch **keine Konsistenzprüfung und kein Link-Management**: Der Port ist sofort im Bündel, selbst wenn die Gegenseite nicht passt. Nur für Gegenstellen ohne PAgP/LACP verwenden. Fehlkonfiguration → Paketverlust oder STP-Schleifen.

## Konfiguration (Layer 2)

Ablauf:
1. Ports auswählen (beide Switches), am besten **2, 4 oder 8** (Zweierpotenz → gleichmäßige Lastverteilung).
2. Auf den Interfaces `channel-group <n> mode <on | auto | desirable | active | passive>` – legt bei L2 den Port-channel automatisch an.
3. Port-channel-Interface konfigurieren (Trunk, VLANs …).
4. Verifizieren.

```
SW1(config)# interface range Ethernet0/0 - 1
SW1(config-if-range)# switchport trunk encapsulation dot1q
SW1(config-if-range)# switchport mode trunk
SW1(config-if-range)# channel-group 1 mode active
SW1(config)# interface Port-channel1
SW1(config-if)# switchport trunk allowed vlan 10,11,20
SW1# show etherchannel summary
```

Richtlinien:
- Änderungen am **Port-channel** wirken auf alle Member; Änderungen an einem **physischen Interface** nur auf dieses (→ Gefahr der Inkonsistenz).
- Alle Member brauchen gleiche Werte bei: **Speed und Duplex**, **Mode (access/trunk)**, **Access-VLAN** bzw. bei Trunks **Native VLAN, Allowed VLANs und Encapsulation**, sowie denselben **Layer** (alle L2 oder alle L3).
- Ports müssen nicht benachbart sein und nicht auf demselben Modul liegen (auch über Module hinweg möglich).
- Ein Member auf `shutdown` gilt als Link-Ausfall; der Verkehr läuft über die übrigen Member.
- Unterschiedliche STP-Port-Kosten verhindern die Bündelung nicht (solange alles andere passt).
- *(Ergänzung)* Layer-3-EtherChannel: Member und Port-channel mit `no switchport`, IP-Adresse auf dem Port-channel (`interface Port-channel1` → `no switchport` → `ip address …`); `show etherchannel summary` zeigt dann `RU`.

## Lastverteilung (Load Balancing)

- Pro Frame berechnet der Switch einen **Hash** aus gewählten Header-Feldern; die niederwertigen Bits des Hashs bestimmen den Member-Link. Verteilung ist deshalb **nicht automatisch gleichmäßig**.
- Methode global: `port-channel load-balance <methode>`, gilt für **alle** EtherChannels des Switches; unterschiedliche Methoden pro Channel sind nicht möglich. Mögliche Werte zeigt `port-channel load-balance ?`, aktive Methode `show etherchannel load-balance`.
- **Default ist plattformabhängig. Catalyst 9300 (IOS-XE 17.x): `src-mac`.** (Kurs: „meist src-dst-ip“.)

| Hash-Eingabe | Feld | Plattform (laut Kurs) |
|---|---|---|
| dst-ip | Ziel-IP | alle |
| dst-mac | Ziel-MAC | alle |
| src-dst-ip | Quell- und Ziel-IP | alle |
| src-dst-mac | Quell- und Ziel-MAC | alle |
| src-ip | Quell-IP | alle |
| src-mac | Quell-MAC | alle |
| src-port | Quell-L4-Port | 4500, 6500, 9000 |
| dst-port | Ziel-L4-Port | 4500, 6500, 9000 |
| src-dst-port | Quell- und Ziel-L4-Port | 4500, 6500, 9000 |

Wirkung der Methoden:
- dst-ip / dst-mac: gleiches Ziel → immer derselbe Link, egal welche Quelle.
- src-ip / src-mac: gleiche Quelle → derselbe Link; verschiedene Quellen verteilt.
- src-dst-…: Paar aus Quelle und Ziel bestimmt den Link (A→B kann einen anderen Link nehmen als A→C).

Bit-Rechnung:
- **Ein Feld** gehasht → die niedrigsten Bits werden direkt als Index genutzt.
- **Zwei Felder** → **XOR** der beiden, dann die niedrigsten Bits.
- 2 Links → letztes Bit, 4 Links → letzte 2 Bits, 8 Links → letzte 3 Bits (vereinfachtes Kursmodell).
- *(Ergänzung)* Real rechnen Catalyst-Switches mit einem 3-Bit-Hash, also **8 Hash-Werte (0–7)**, die auf die Member verteilt werden – unabhängig von der Linkanzahl. Bei 2, 4 oder 8 Links bekommt jeder Link gleich viele Werte (4/2/1), sonst nicht (siehe Konsequenzen). Quelle: Cisco Tech Note 12023 „Understanding EtherChannel Load Balancing and Redundancy on Catalyst Switches“.

Beispiel (2 Links, src-dst-ip, letztes Bit von Quelle XOR Ziel):
| Quelle → Ziel | Bits | XOR | Link |
|---|---|---|---|
| …0 (gerade) → …0 | 0 ⊕ 0 | 0 | 0 |
| …0 → …1 (ungerade) | 0 ⊕ 1 | 1 | 1 |
| …1 → …0 | 1 ⊕ 0 | 1 | 1 |
| …1 → …1 | 1 ⊕ 1 | 0 | 0 |
(z. B. 10.1.1.101 → 10.1.1.103: beide ungerade → Link 0.)

Konsequenzen:
- Eine Konversation (gleiches Adresspaar) läuft **immer über denselben Link** → kein Reordering, aber ein einzelner Flow wird nie schneller als ein Member-Link.
- Dominiert ein Host-Paar den Verkehr, ist ein Link überlastet → Methode mit mehr Varianz wählen (z. B. L4-Ports).
- Überwiegend IP-Verkehr → nach IP-Adressen oder Ports verteilen. *(Ergänzung)* Nicht-IP-Frames werden bei IP-basierter Methode anhand der MAC-Adressen verteilt.
- **Zweierpotenz** an Links: Die 8 Hash-Werte verteilen sich bei 2, 4 oder 8 Links gleichmäßig (4 Links: je 2 Werte, 1:1:1:1). Bei anderen Linkzahlen nicht: **3 Links → 3:3:2**, 5 Links → 2:2:2:1:1, 6 Links → 2:2:1:1:1:1, 7 Links → 2:1:1:1:1:1:1 (Cisco Tech Note 12023). Das gilt bei vielen verschiedenen Flows mit zufälligen Adressen.
- Welchen Port ein bestimmter Flow nimmt, ist nicht direkt steuerbar – nur die Methode.
- *(Ergänzung)* Hash-Polarisation: Verwenden mehrere Stufen hintereinander dieselbe Hash-Eingabe, landen Flows immer auf denselben Links.
- *(Ergänzung)* Beispiel für Ungleichgewicht: `dst-mac` an einem Access-Switch, fast aller Verkehr geht an die MAC des Default-Gateways → praktisch ein Link.

## Troubleshooting

### Typische Fehlerbilder
| Ursache | Symptom |
|---|---|
| Inkonsistente Member (Speed, Duplex, Trunk-Mode, Native/Allowed VLAN, Layer 2 vs. 3) | Channel bildet sich nicht oder einzelne Member werden suspendiert (`s`) |
| Unterschiedliche Modi/Protokolle auf beiden Seiten (z. B. LACP gegen PAgP, passive/passive, on gegen active) | Channel down (`SD`), Member stand-alone (`I`), suspendiert (`s`), down (`D`) oder err-disabled |
| Hash-Methode passt nicht zum Verkehr / Anzahl Links ungünstig | ungleiche Auslastung der Member |

### Vorgehen
1. **Speed/Duplex**: `show interfaces <if>` – Korrektur mit `speed {10|100|1000|auto|nonegotiate}` / `duplex {auto|full|half}`. Ein Duplex-Mismatch (nur eine Seite autonegotiate) kann up/up zeigen, aber viele Fehler produzieren.
2. **Trunk/VLAN**: `show interfaces <if> switchport` oder `show running-config interface <if>` – Mode, Access-VLAN, Native VLAN, Allowed VLANs, Encapsulation müssen übereinstimmen.
3. **Layer**: Bei L3-EtherChannel auf allen Membern `no switchport`.
4. **Status**: `show etherchannel summary`, `show etherchannel <n> detail`. Spalte *Protocol*: `LACP`, `PAgP` oder `-` (= `on`, manuell).
5. **Verteilung**: `show etherchannel load-balance`, `show etherchannel traffic` (Auslastung je Member).
6. *(Ergänzung)* LACP-Details: `show lacp neighbor`, `show lacp sys-id`, `show lacp internal`; PAgP: `show pagp neighbor`.

Tipp: Konfiguration über `interface range` bzw. am Port-channel vornehmen, damit alle Member identisch bleiben.

### Flags in `show etherchannel summary`
| Flag | Bedeutung |
|---|---|
| D | down |
| P | bundled in port-channel |
| I | stand-alone (individuell, nicht gebündelt) |
| s | suspended |
| H | Hot-standby (nur LACP) |
| R | Layer 3 |
| S | Layer 2 |
| U | in use |
| f | failed to allocate aggregator |
| M | not in use, minimum links not met |
| u | unsuitable for bundling |
| w | waiting to be aggregated |
| d | default port |

Gesund: Port-channel `SU` (L2) bzw. `RU` (L3), alle Member `P`. `SD` heißt: Bündel nicht gebildet.

Beispiel (eigenes):
```
Group  Port-channel  Protocol    Ports
------+-------------+-----------+------------------------
1      Po1(SU)         LACP      Gi1/0/1(P)  Gi1/0/2(P)
2      Po2(SD)         LACP      Gi1/0/3(s)  Gi1/0/4(s)
3      Po3(SU)          -        Gi1/0/5(P)  Gi1/0/6(P)
```
Po2: LACP-Ports suspendiert – z. B. weil die Gegenseite `on` nutzt und keine LACPDUs schickt. Po3: statisch (`-`).

- *(Ergänzung)* **I oder s bei fehlendem LACP-Partner:** Das steuert der Port-channel-Befehl `port-channel standalone-disable`. Ist er aktiv, werden Member ohne empfangene LACPDUs **suspendiert (`s`)**. Ohne ihn fallen sie in den **Individual-/Stand-alone-Zustand (`I`)** und leiten als Einzelports weiter (ein Schleifenrisiko). Der Cat9300 17.9 Configuration Guide beschreibt als Verhalten: „When no response is received from an LACP peer, ports in the port channel are moved to suspended state“. Der Default des Befehls ist je nach Plattform und Release unterschiedlich. Deshalb gilt für Prüfungsszenarien: `s` = Inkonsistenz oder Partner ohne LACP, `I` = keine Aushandlung, der Port arbeitet einzeln. Prüfen lässt sich das mit `show running-config interface Po<n>` und `show etherchannel <n> detail`.

### EtherChannel Guard
- Erkennt Fehlkonfiguration zwischen Switch und Nachbar, typischerweise: eine Seite bündelt (z. B. `on`), die andere nicht. Der bündelnde Switch erwartet auf allen Membern dieselben BPDUs (eine Quell-MAC). Kommen BPDUs mit unterschiedlichen MACs, behandelt der Nachbar die Links einzeln → Schleifengefahr → Member werden **err-disabled**.
- Log (Kursbeispiel, Cat6500-Form): `%PM-SP-4-ERR_DISABLE: channel-misconfig error detected on Po3, putting Te1/3 in err-disable state`. *(Ergänzung)* Davor meldet STP meist `%SPANTREE-2-CHNL_MISCFG: Detected loop due to etherchannel misconfiguration of <if>` (Cisco Tech Note 69980).
- Befehl: `spanning-tree etherchannel guard misconfig` (global), **standardmäßig aktiv**. Prüfen: `show spanning-tree summary` → „EtherChannel misconfig guard is enabled“.
- *(Ergänzung)* Automatische Erholung: `errdisable recovery cause channel-misconfig` (Default-Intervall 300 s).

## Discovery 6: Troubleshoot EtherChannel

Topologie: SW1 und SW2 über vier Links verbunden: Et0/0–0/1 = Po1, Et0/2–0/3 = Po2, alle Dot1Q-Trunks. PC1 (10.10.11.11) an SW1 Et1/0, PC2 (10.10.11.12) an SW2 Et1/0, beide in VLAN 11. Vorgabe: nur Standardprotokolle; SW1 initiiert (LACP active), SW2 antwortet (LACP passive).

Fehler 1 – Po2 down:
- SW2: `Po2(SD) LACP`, Et0/2(s), Et0/3(s). SW1: `Po2(SU)` mit Protocol `-`, Et0/2(P), Et0/3(P) → SW1 nutzt `channel-group 2 mode on`.
- Fix auf SW1: `no channel-group 2 mode on`, `channel-group 2 mode active`. Log: `%EC-5-L3DONTBNDL2: Et0/3 suspended: LACP currently not enabled on the remote port.` (vorübergehend, bis beide Seiten LACP sprechen).
- Danach laut Lab weiterhin `SD`; als Ursache wird eine Allowed-VLAN-Abweichung am Port-channel angegeben (SW2 `switchport trunk allowed vlan 1-10,12-4094`, SW1 alle VLANs) → Fix auf SW2: `no switchport trunk allowed vlan 1-10,12-4094`. Ergebnis: Po2(SU), Member (P), PC1 erreicht PC2 (VLAN 11 wieder durchgelassen). Siehe Hinweis in „Fehler/Ungenauigkeiten“.

Fehler 2 – Po1 nur mit einem Member:
- SW1 Po1 nur Et0/1(P); SW2 Po1 Et0/0(s), Et0/1(P).
- Ursache: SW1 Et0/0 ist `no switchport` (L3) und ohne `channel-group`.
- Fix: `switchport`, `switchport trunk encapsulation dot1q`, `switchport mode trunk`, `channel-group 1 mode active` → Po1(SU), Et0/0(P), Et0/1(P).

IOL-Hinweis: Ein per `shutdown` abgeschaltetes Interface erscheint beim Nachbarn in IOL als up/up (auf echter Hardware down/down).

## Policy-Based Routing (PBR)

### Konzept
- Normales IP-Routing entscheidet **nur nach der Zieladresse**. PBR überschreibt diese Entscheidung für ausgewählte Pakete anhand anderer Kriterien (Quelladresse, Protokoll, Paketlänge …).
- Einsatzgründe: rechtliche, vertragliche oder politische Vorgaben, die bestimmte Pfade erzwingen.
- PBR wirkt auf **eingehende** Pakete (am Eingangs-Interface) oder auf **lokal erzeugte** Pakete des Routers.
- Umsetzung immer mit einer **Route-Map**: `match` wählt Pakete aus, `set` legt die Weiterleitung fest (Next Hop, Ausgangs-Interface …). Pakete, die passen, umgehen die Routing-Tabelle.
- Nutzen:
  - **Source-based transit-provider selection**: Verkehr aus verschiedenen Quellnetzen über verschiedene ISPs leiten (z. B. 192.168.1.0/24 → ISP1, 192.168.2.0/24 → ISP2).
  - **Load Sharing** nach Verkehrseigenschaften, zusätzlich zum zielbasierten Load Sharing des Routings.

### *(Ergänzung)* Konfiguration und Verhalten

```
access-list 10 permit 192.168.2.0 0.0.0.255
!
route-map PBR-ISP permit 10
 match ip address 10
 set ip next-hop 203.165.201.1
!
interface Gi0/1                 ! LAN-Seite, Eingang
 ip policy route-map PBR-ISP
!
ip local policy route-map LOCAL-PBR   ! für vom Router selbst erzeugte Pakete
```

| Aktion | Verhalten |
|---|---|
| `set ip next-hop <ip> [<ip2>]` | überschreibt die Routing-Tabelle; Next Hop muss adjazent sein; mehrere werden der Reihe nach versucht; ist keiner erreichbar → normales Routing |
| `set ip default next-hop <ip>` | greift nur, wenn es **keine explizite Route** zum Ziel gibt (Default-Route zählt nicht) |
| `set interface <if>` | Ausgangs-Interface erzwingen (z. B. `Null0` zum Verwerfen) |
| `set ip next-hop verify-availability <ip> <seq> track <n>` | Next Hop nur, solange das Track-Objekt up ist |
| `set ip next-hop recursive <ip>` | nicht direkt verbundener Next Hop |

- `match ip address <acl>` und `match length <min> <max>` sind typische Kriterien. Route-Map-Eintrag ohne `match` → passt auf alle Pakete.
- Pakete, die auf keinen Eintrag passen oder auf `deny` treffen (Route-Map-deny oder ACL-deny im permit-Eintrag), werden **normal (zielbasiert) geroutet**, nicht verworfen.
- `ip policy route-map` wirkt nur eingehend; ausgehend gibt es keine Interface-PBR.
- Prüfen: `show route-map` (Treffer-Zähler), `show ip policy`, `debug ip policy`.

## Fehler/Ungenauigkeiten im Kurs

1. **S. 54, Default-Lastverteilung:** Kurs: „meist src-dst-ip“. Auf dem **Catalyst 9300 (IOS-XE 17.x) ist der Default `src-mac`**; der Default ist plattformabhängig. Quelle: Cat9300 17.9 Layer 2 Configuration Guide „Configuring EtherChannels“ und Command Reference 17.9 (`port-channel load-balance`: „The default value is src-mac“).
2. **S. 55, Flag P:** Kurs erklärt `P` als „passive“. Richtig: **P = bundled in port-channel** (siehe Flag-Legende in jeder `show etherchannel summary`-Ausgabe, auch im Lab S. 56).
3. **S. 54, „gerade Anzahl“:** Kurs empfiehlt eine gerade Anzahl Links. Entscheidend ist eine **Zweierpotenz** (2, 4, 8) – 6 Links sind gerade, verteilen aber ungleich (wie auf S. 53 selbst richtig formuliert).
4. **S. 54, Satz zu IP-Verteilung:** „Bei Verteilung nach IP-Adressen verteilt der Switch nach MAC-Adressen“ ist verkürzt/irreführend. Gemeint ist: Nicht-IP-Frames werden bei einer IP-basierten Methode nach MAC-Adressen verteilt.
5. **S. 57, PBR „manipuliert Einträge der Routing-Tabelle“:** PBR ändert die Routing-Tabelle nicht, sondern **umgeht** sie für passende Pakete (Policy wird vor dem Routing-Lookup angewendet). Quelle: Cisco IOS-XE „Policy-Based Routing“ Configuration Guide.
6. **S. 52, PAgP silent/non-silent:** Der Kurs sagt, desirable laufe per Default non-silent und auto silent. Laut aktueller Cisco-Doku gilt ohne Angabe von `non-silent` für beide Modi **silent**. Daher keine Default-Fragen dazu. Quelle: Cat9300 17.9 Config Guide „Configuring EtherChannels“ (PAgP-Abschnitt).
7. **S. 56, Lab-Ursache Allowed VLANs (geklärt, so weit belegbar):** Das Lab begründet das weiterhin bestehende `SD` mit einer Allowed-VLAN-Abweichung zwischen den beiden Switches. Cisco formuliert die Konsistenzregel aber nur lokal: „An EtherChannel supports the same allowed range of VLANs on all the ports in a trunking Layer 2 EtherChannel“ (Cat9300 17.9 Config Guide, EtherChannel Configuration Guidelines). Gemeint sind die Member **eines** Switches. LACPDUs enthalten keine VLAN-Listen; anders als PAgP vergleicht LACP also keine VLAN-Konfiguration mit der Gegenseite. Eine abweichende Allowed-VLAN-Liste auf dem Partner verhindert das LACP-Bündel deshalb nicht. Sie blockiert nur den Verkehr des fehlenden VLANs, hier VLAN 11 (PC1↔PC2). Das spätere `SU` erklärt sich am ehesten so: Die LACP-Neuverhandlung nach dem Moduswechsel war noch nicht abgeschlossen, oder die Member auf SW2 waren untereinander bzw. zum Po inkonsistent. Was im Lab tatsächlich passierte, lässt sich nicht belegen. Für die Prüfung gilt: Allowed-VLAN-Unterschiede **zwischen Membern eines Switches** führen zu suspendierten Ports (`s`). Unterschiede zwischen den beiden Switches führen zu Verkehrsverlust im betroffenen VLAN.
8. **S. 55, Logmeldung EtherChannel Guard:** Das Beispiel nutzt die Catalyst-6500-Form (`%PM-SP-4-ERR_DISABLE`, Te1/3). Auf Catalyst 9000 lautet sie `%PM-4-ERR_DISABLE: channel-misconfig error detected …`.
9. **S. 53/54, Verteilung bei 3 Links:** Das Kursmodell (3 Links → weiterhin 2 Bits → 2:1:1) ist zu stark vereinfacht. Catalyst-Switches verteilen 8 Hash-Werte. Daraus ergibt sich bei 3 Links **3:3:2**, bei 6 Links 2:2:1:1:1:1. Gleichmäßig ist die Verteilung nur bei 2, 4 und 8 Links. Quelle: https://www.cisco.com/c/en/us/support/docs/lan-switching/etherchannel/12023-4.html

## Bilder

- `bilder/06-etherchannel/01-ec-konzept.svg` – Parallele Links ohne Bündel (STP blockiert) vs. EtherChannel (ein logischer Port, alle Links aktiv) mit den Vorteilen.
- `bilder/06-etherchannel/02-modi-matrix.svg` – Matrix der Modi on/active/passive/desirable/auto: welche Kombination ein Bündel bildet.
- `bilder/06-etherchannel/03-lacp-wahl.svg` – LACP: System Priority bestimmt den entscheidenden Switch, Port Priority die aktiven Ports, Rest Hot-Standby.
- `bilder/06-etherchannel/04-konsistenz.svg` – Was alle Member gleich haben müssen, Port-channel- vs. Member-Konfiguration, Konfigurationsablauf.
- `bilder/06-etherchannel/05-hash-xor.svg` – Hash-Berechnung mit XOR der letzten Bits und Linkwahl bei 2 bzw. 4 Links.
- `bilder/06-etherchannel/06-buckets.svg` – 8 Hash-Werte auf 4 Links (1:1:1:1) gegenüber 3 Links (3:3:2) und dominanter Flow.
- `bilder/06-etherchannel/07-ts-summary.svg` – Lesehilfe für `show etherchannel summary` (Po-Status, Member-Flags, Protocol-Spalte) mit typischen Diagnosen.
- `bilder/06-etherchannel/08-lab-topo.svg` – Discovery-6-Topologie (Po1/Po2, VLAN 11) mit den beiden Fehlern und deren Behebung.
- `bilder/06-etherchannel/09-pbr.svg` – PBR: Route-Map mit match/set vor der Routing-Tabelle, quellbasierte ISP-Wahl.
