# Exploring EBGP

Quelle: ENCOR 1.4.10 Student Guide, Seiten 99–105 (Interdomain Routing with BGP, BGP Operations, Types of BGP Neighbor Relationships, BGP Path Selection, BGP Path Attributes, Discovery 11 „Configure and Verify Single-Homed EBGP“, Summary)

Topics: ENCOR-3.2.c (eBGP zwischen Nachbarn konfigurieren, Best-Path-Selection, Neighbor Relationships), Bezug zu ENCOR-3.1.a (Administrative Distance)

Ergänzungen aus eigenem Fachwissen bzw. aus dem Prüfprotokoll `research_notes/Kapitelpruefung/10-ebgp.md` (nicht im Kurs) sind mit *(Ergänzung)* markiert.

## Interdomain Routing und autonome Systeme

- **Autonomes System (AS)**: Netze bzw. Router unter **einer gemeinsamen technischen Verwaltung** mit gemeinsamer Routing-Policy. Wem die Router rechtlich gehören, spielt keine Rolle.
- **IGP** (RIP, OSPF, EIGRP, IS-IS) routet **innerhalb** eines AS, **EGP** zwischen AS. BGP (Version 4) ist das EGP des Internets.
- AS-Nummern: ursprünglich **16 Bit**; wegen Erschöpfung gibt es **32-Bit-ASNs** (4-Byte-ASN). Öffentliche ASNs vergibt die IANA (über die RIRs).

| ASN-Bereich | Verwendung |
|---|---|
| 1–64495 | öffentlich (16 Bit) |
| 23456 | *(Ergänzung)* AS_TRANS: Platzhalter gegenüber Peers ohne 4-Byte-Unterstützung (RFC 6793) |
| 64496–64511 | *(Ergänzung)* Dokumentation/Beispiele (RFC 5398) |
| **64512–65534** | **privat** (16 Bit, RFC 6996) |
| 65535 | *(Ergänzung)* reserviert (RFC 7300) |
| 65536–4199999999 | *(Ergänzung)* öffentlich 32 Bit (Teilbereiche reserviert/Doku) |
| 4200000000–4294967294 | *(Ergänzung)* privat (32 Bit, RFC 6996); 4294967295 reserviert |

- *(Ergänzung)* asdot-Schreibweise: X.Y = X·65536 + Y (z. B. 2.10 = 131082; 65546 = 1.10). Umschalten mit `bgp asnotation dot`.
- Der Kurs nennt 64512–65535 als privat und 1–64511 als öffentlich – ungenau (siehe Fehlerabschnitt).

## BGP-Eigenschaften

- Transport: **TCP Port 179** → BGP braucht keine eigene Bestätigung/Wiederholung.
- **Reliability**: Nach dem Aufbau tauschen Peers einmal die **komplette** Tabelle, danach nur **inkrementelle/triggered Updates**; keine periodischen Updates. Keepalives halten die Session.
- **Scalability**: volle Internettabelle (Kurs: über 600 000 Präfixe; heute deutlich mehr). Statt eines One-for-one-Fensters wie bei OSPF/EIGRP (nächstes Paket erst nach ACK) nutzt TCP ein **Sliding Window**: Viele Segmente dürfen unbestätigt unterwegs sein (ohne Window Scaling max. 65 535 Byte), der Empfänger bestätigt laufend.
- **Stability**: Änderungen werden **gebündelt** (batched) verschickt, damit Flaps in einem AS nicht das ganze Internet belasten; dazu Dämpfungsmechanismen (Route Dampening). Preis: **langsamere Konvergenz** als IGPs.

### Path Vector

- BGP überträgt pro Präfix eine **Liste der AS**, die bis zum Ziel durchlaufen werden (**AS_PATH**), die Netze am Ende des Pfades (NLRI) und weitere **Pfadattribute** (NEXT_HOP, ORIGIN, …).
- **Loop-Schutz**: Ein Router verwirft (still) ein Update, in dessen AS_PATH die **eigene ASN** schon steht.
- **Hop-by-hop-Paradigma**: Ein AS gibt nur den Pfad weiter, den es **selbst benutzt** (seinen Best Path). Es kann beeinflussen, **an welches Nachbar-AS** es Traffic übergibt, aber nicht, wie dieses weiterroutet.
- Kursbeispiel: AS 65010 erreicht AS 65060 über AS 65020 oder AS 65040. AS 65020 kennt mehrere Wege (65030 65060, 65050 65060, 65050 65030 65060), meldet aber nur seinen besten: **65020 65030 65060**. Alternativen erfährt AS 65010 erst, wenn dieser Best Path wegfällt.

### Design-Ziele

- Skalierbarkeit (wachsende Internettabelle).
- Sicherer Austausch: Router anderer AS sind nicht vertrauenswürdig → **Neighbor-Authentifizierung**, **strenge Filter**. Beispiel: Ein multihomed Kunde darf Routen von ISP A nicht an ISP B weitergeben (sonst wird er Transit-AS).
- Policies für **ausgehenden und eingehenden** Traffic.

## BGP-Betrieb

### Drei Datenstrukturen

| Tabelle | Inhalt |
|---|---|
| **Neighbor Table** | explizit konfigurierte Nachbarn, Zustand der TCP-/BGP-Sessions (keine automatische Nachbarerkennung) |
| **BGP Table** (BGP topology/forwarding database, Loc-RIB) | **alle** von allen Nachbarn gelernten Pfade; pro Präfix wird ein Best Path gewählt |
| **IP Routing Table** | Der Best Path wird angeboten; installiert wird nach **Administrative Distance** |

- AD: **eBGP 20**, **iBGP 200**. *(Ergänzung)* Lokal aggregierte/originierte BGP-Routen: 200.

### Nachrichtentypen

| Typ | Inhalt / Zweck |
|---|---|
| **OPEN** | erste Nachricht nach TCP-Aufbau: Version (4), **eigene ASN** (wird vom Peer geprüft), **Hold Time** (es gilt der **kleinere** Wert beider Seiten), **BGP Identifier** (Router-ID, 32 Bit), optionale Parameter (TLV, heute v. a. Capabilities) |
| **KEEPALIVE** | nur Header (*(Ergänzung)* 19 Byte); bestätigt das OPEN und hält die Session. Hold Time 0 → keine Keepalives |
| **UPDATE** | anfangs volle Tabelle, später inkrementell. Ein UPDATE beschreibt **einen** Pfad (einen Attributsatz): Felder **Withdrawn Routes**, **Path Attributes** (je Attribut Flags + Type Code + Länge + Wert), **NLRI** (erreichbare Präfixe) |
| **NOTIFICATION** | bei Fehlern: Error Code, Subcode, Daten; die Verbindung wird danach **sofort geschlossen** |
| *(Ergänzung)* **ROUTE-REFRESH** | Typ 5 (RFC 2918): fordert die Routen eines Peers neu an (soft reset inbound) ohne Session-Abbau |

- Ablauf: TCP-Handshake → beide senden OPEN → passt es, antwortet jede Seite mit KEEPALIVE → **Established** → UPDATE/KEEPALIVE/NOTIFICATION.
- *(Ergänzung)* Cisco-Defaults: Keepalive **60 s**, Hold Time **180 s** (`timers bgp <ka> <hold>` bzw. `neighbor x timers`). Hold Time muss 0 oder ≥ 3 s sein.
- **Router-ID**: manuell (`bgp router-id`), sonst **höchste Loopback-IPv4-Adresse**, sonst höchste aktive Interface-IPv4-Adresse (wie bei OSPF).
- *(Ergänzung)* Error Codes (RFC 4271): 1 Message Header Error, 2 OPEN Message Error (z. B. Subcode 2 Bad Peer AS), 3 UPDATE Message Error, 4 Hold Timer Expired, 5 FSM Error, 6 Cease.

### Zustandsautomat *(Ergänzung, RFC 4271)*

| Zustand | Bedeutung |
|---|---|
| Idle | wartet auf Start; nach Fehlern auch Wartezustand. `Idle (Admin)` = `neighbor x shutdown`, `Idle (PfxCt)` = maximum-prefix überschritten |
| Connect | TCP-Aufbau läuft |
| Active | TCP-Versuch gescheitert, neuer Versuch. Dauerhaft Active = TCP klappt nicht (falsche Adresse, keine Route, Port 179 gefiltert, falsche Quelladresse/fehlendes ebgp-multihop) |
| OpenSent | eigenes OPEN gesendet, warte auf OPEN des Peers. **Falsche Peer-ASN** wird hier erkannt → NOTIFICATION (OPEN Message Error / Bad Peer AS) |
| OpenConfirm | OPEN des Peers akzeptiert, warte auf KEEPALIVE |
| Established | UPDATEs werden ausgetauscht |

- Der Kurs erklärt nur: Zustand **Active** = Router versucht, die Verbindung aufzubauen, sie steht noch nicht.

## Nachbarbeziehungen

- **BGP Speaker**: jeder Router, auf dem BGP läuft. **BGP Peer/Neighbor**: ein Speaker, der mit einem anderen explizit für den Austausch konfiguriert ist (TCP-basiert).
- **iBGP**: Peers im **selben AS**; oft nicht direkt verbunden; bei Providern für Redundanz und Lastverteilung.
- **eBGP**: Peers in **verschiedenen AS**: Kunde–ISP, ISP–ISP, CE–PE bei MPLS-VPNs (Routen zwischen Kundenstandorten durch die MPLS-Wolke).
- Voraussetzungen für eBGP (Kurs):
  1. **Unterschiedliche ASNs**.
  2. **Nachbar definiert**, TCP-Session steht, bevor Updates fließen.
  3. **Erreichbarkeit**: per Default **direkt verbunden**.
- *(Ergänzung)* eBGP sendet mit **TTL 1**; für Loopback-Peering `neighbor x ebgp-multihop <n>` (oder `disable-connected-check` bei direkter Verbindung) plus `neighbor x update-source Loopback0`. iBGP nutzt TTL 255.
- *(Ergänzung)* Unterschiede eBGP/iBGP beim Weitergeben:

| | eBGP | iBGP |
|---|---|---|
| NEXT_HOP | wird auf die eigene Adresse gesetzt | bleibt **unverändert** (sonst `next-hop-self`) |
| AS_PATH | eigene ASN wird vorangestellt | unverändert |
| Weitergabe | an alle Peers | iBGP-gelernte Routen **nicht** an andere iBGP-Peers (Split Horizon → Full Mesh oder Route Reflector) |
| `show ip bgp neighbors` | `external link` | `internal link` |

## Best-Path-Selection

- BGP wählt pro Präfix **genau einen** Best Path nach **Policy**, nicht nach Bandbreite, Delay oder Auslastung. Kein Load Balancing per Default (*(Ergänzung)* nur mit `maximum-paths`).
- Nicht-beste Pfade bleiben als Backup in der BGP-Tabelle.
- Voraussetzungen: kein AS-Loop, **Next Hop erreichbar**.
- Reihenfolge (Kurs, mit Cisco 13753 abgeglichen):

| # | Kriterium | besser |
|---|---|---|
| 1 | **Weight** (Cisco, nur lokal) | höher |
| 2 | **LOCAL_PREF** (AS-weit) | höher |
| 3 | lokal originiert (network, aggregate, redistribute; Next Hop 0.0.0.0) | bevorzugt |
| 4 | **AS_PATH**-Länge | kürzer |
| 5 | **ORIGIN** | i (IGP) < e (EGP) < ? (incomplete) |
| 6 | **MED** (nur bei gleichem Nachbar-AS) | niedriger |
| 7 | eBGP vor iBGP | eBGP |
| 8 | IGP-Metrik zum Next Hop | niedriger |
| 9 | ältester eBGP-Pfad (stabilster) | älter |
| 10 | Router-ID des Nachbarn | niedriger |
| 11 | Nachbar-IP-Adresse | niedriger |

- *(Ergänzung)* Merkhilfe: Weight und Local Pref „hoch gewinnt“, alles andere „niedrig/kurz gewinnt“. Ausgelassene Detailschritte bei Cisco: AIGP, Multipath-Prüfung, Cluster-List-Länge.
- Kursbeispiel: 7 Pfade zu 10.0.0.0, alle Weight 0 → weiter zu LOCAL_PREF; 4 Pfade mit 200, die anderen 100/100/150 → nur die vier mit 200 gehen in den nächsten Schritt, die anderen bleiben in der Tabelle, sind aber ausgeschieden.
- Der gewonnene BGP-Pfad konkurriert per AD mit anderen Quellen. *(Ergänzung)* Verliert er, steht er mit `r` (RIB-failure) in `show ip bgp`.

## Pfadattribute

| Klasse | Bedeutung | Beispiele |
|---|---|---|
| **Well-known mandatory** | jeder Router muss sie kennen; in jedem UPDATE mit NLRI vorhanden | ORIGIN, AS_PATH, NEXT_HOP |
| **Well-known discretionary** | jeder kennt sie, Vorhandensein optional | LOCAL_PREF, ATOMIC_AGGREGATE |
| **Optional transitive** | muss nicht verstanden werden; unbekannt → trotzdem weitergeben und **Partial-Bit** setzen | AGGREGATOR, COMMUNITY |
| **Optional non-transitive** | unbekannt → beim Weitergeben **entfernen** | MED |

- **ORIGIN**: `i` bei `network`-Befehl oder BGP-Aggregation, `?` (incomplete) bei Redistribution, `e` (EGP) historisch/obsolet.
- **AS_PATH**: Folge der AS bis zum Ziel. Beim Originieren **leer**; beim Verlassen eines AS (eBGP) wird die ASN **vorangestellt**; das Ursprungs-AS steht **ganz rechts**. Kürzer ist besser; dient dem Loop-Schutz.
- **NEXT_HOP**: Adresse, an die Pakete für das Präfix geschickt werden. eBGP setzt die eigene Adresse; iBGP ändert ihn per Default nicht.
- **ATOMIC_AGGREGATE**: zeigt an, dass bei der Aggregation Pfadinformation (z. B. AS-Pfade) verloren ging. *(Ergänzung)* **AGGREGATOR**: ASN und Router-ID/IP des aggregierenden Routers.
- **COMMUNITY**: Markierung von Routen, an der andere Router Filter oder Policies festmachen.

### Weight (Cisco-spezifisch, kein übertragenes Attribut)

- Nur auf dem lokalen Router, wird **nie** weitergegeben. Bereich 0–65535; **lokal originiert 32768**, gelernte Pfade **0**. Höher ist besser.
- Einsatz: **ein** Router mit mehreren Ausgängen.
- Kursbeispiel: R1 (AS 65040) lernt 209.165.201.0 über R2 und R4; Weight 200 für Updates von R2, 150 von R4 → R1 nutzt R2.

### LOCAL_PREF

- Gilt im ganzen eigenen AS (über iBGP verteilt), wird an eBGP-Peers **nicht** gesendet. Default **100**, höher ist besser.
- Einsatz: **mehrere Edge-Router** mit Ausgängen; einmal am Rand setzen, alle Router im AS wählen konsistent.
- Kursbeispiel: R2 setzt für Updates von R3 LOCAL_PREF 200, R1 für Updates von R5 150; R1 und R2 tauschen sich per iBGP aus → beide verlassen das AS über R3.

### AS_PATH-Beispiel (Kurs)

- R4 (AS 65020) originiert 209.165.201.0. Weg über R3 (AS 65030) zu R2 (AS 65040): AS_PATH **65030 65020**. Weg über R5 (AS 65010) und R6 (AS 65050) zu R1: **65050 65010 65020**. AS 65040 wählt den kürzeren Pfad über R2/R3.

### MED (Multi-Exit Discriminator, „BGP metric“)

- Optional non-transitive. Ein AS teilt einem **Nachbar-AS** mit, über welchen von **mehreren Eingängen** es Traffic empfangen möchte → beeinflusst **eingehenden** Traffic. Niedriger ist besser.
- Der Empfänger darf den MED im eigenen AS (iBGP) weitergeben, aber **nicht** an ein weiteres AS.
- IOS vergleicht MED per Default nur zwischen Pfaden **aus demselben Nachbar-AS** (*(Ergänzung)* sonst `bgp always-compare-med`). Fehlender MED zählt als 0 (*(Ergänzung)* mit `bgp bestpath med missing-as-worst` als schlechtester Wert).
- Der Nachbar kann den MED ignorieren oder überschreiben – keine Garantie.
- Kursbeispiel: AS 65010 meldet 172.20.0.0 über R2 mit MED 200 und über R3 mit MED 150 an R1 → R1 nutzt R3.

### Reichweite im Überblick

| Wert | bleibt … |
|---|---|
| Weight | auf dem einen Router |
| LOCAL_PREF | im eigenen AS |
| MED | geht ins Nachbar-AS, dort im AS verteilt, nicht weiter |
| AS_PATH, ORIGIN, COMMUNITY | über alle AS (COMMUNITY sofern nicht entfernt) |

## Discovery 11: Single-Homed eBGP

Topologie:

| Gerät | AS | Interface | Adresse |
|---|---|---|---|
| SP1 (Provider) | 1 | Ethernet0/1 → R1 | 192.168.1.10/24 |
| | | Ethernet0/2 → R2 | 192.168.2.10/24 |
| | | Loopback0 (LAN) | 10.0.3.1/24 |
| R1 (Kunde) | 100 | Ethernet0/1 | 192.168.1.11/24 |
| | | Loopback0 | 10.0.1.1/24 |
| R2 (Kunde) | 200 | Ethernet0/2 | 192.168.2.11/24 |
| | | Loopback0 | 10.0.2.1/24 |

Benötigte Angaben: eigene und alle Nachbar-ASNs, Nachbaradressen, zu annoncierende Netze. Drei Schritte: Prozess starten, Nachbarn definieren, Netze annoncieren.

```
R1# show running-config | section bgp
router bgp 100
 bgp log-neighbor-changes
 network 10.0.1.0 mask 255.255.255.0
 neighbor 192.168.1.10 remote-as 1

SP1(config)# router bgp 1
SP1(config-router)# neighbor 192.168.1.11 remote-as 100
SP1(config-router)# neighbor 192.168.2.11 remote-as 200
SP1(config-router)# network 10.0.3.0 mask 255.255.255.0
```

- Pro Router **höchstens ein BGP-Prozess** → ein Router gehört genau zu einem AS.
- Nachbaradresse bei eBGP per Default ohne IGP erreichbar, also direkt verbunden; nicht direkt verbundene Peers brauchen Zusatzkonfiguration.
- Log beim Aufbau: `%BGP-5-ADJCHANGE: neighbor 192.168.1.11 Up`.
- **network-Befehl** in BGP: schaltet BGP auf **keinem** Interface ein (das tun die `neighbor`-Befehle), sondern **originiert** ein Präfix in die BGP-Tabelle – nur, wenn es **exakt mit dieser Maske** in der Routing-Tabelle steht. Ohne `mask` gilt die **klassenbezogene** Maske (`network 172.16.0.0` = /16). Für ein Subnetz: `network 172.16.1.0 mask 255.255.255.0`. Vorher mit `show ip route` prüfen.

### Verifikation (gekürzte Beispielausgaben)

```
SP1# show ip bgp summary
BGP router identifier 10.0.3.1, local AS number 1
BGP table version is 4, main routing table version 4
Neighbor      V    AS MsgRcvd MsgSent TblVer InQ OutQ Up/Down  State/PfxRcd
192.168.1.11  4   100       5       6      4   0    0 00:00:10        1
192.168.2.11  4   200       5       6      4   0    0 00:00:10        1
```
- Router-ID kommt von Loopback0. **Table version** steigt bei jeder Änderung der BGP-Tabelle.
- Spalten: Nachbar-IP, BGP-Version, Remote-AS, empfangene/gesendete Nachrichten, zuletzt an den Nachbarn gesendete Tabellenversion, Eingangs-/Ausgangswarteschlange, Dauer im aktuellen Zustand, **State/PfxRcd**: Steht eine **Zahl**, ist die Session **Established** und die Zahl = empfangene Präfixe; sonst steht der Zustandsname (z. B. Active, Idle).

```
SP1# show ip bgp neighbors 192.168.1.11
BGP neighbor is 192.168.1.11,  remote AS 100, external link
  BGP version 4, remote router ID 10.0.1.1
  BGP state = Established, up for 00:01:16
  ... hold time is 180, keepalive interval is 60 seconds
  Neighbor capabilities:
    Route refresh: advertised and received(new)
    Four-octets ASN Capability: advertised and received
    Address family IPv4 Unicast: advertised and received
```
- `external link` = eBGP-Peer in anderem AS.

```
R1# show ip bgp
     Network          Next Hop        Metric LocPrf Weight Path
 *>  10.0.1.0/24      0.0.0.0              0         32768 i
 *>  10.0.2.0/24      192.168.1.10                       0 1 200 i
 *>  10.0.3.0/24      192.168.1.10         0             0 1 i
```
- `*` gültig, `>` Best Path; *(Ergänzung)* weitere Statuscodes `i` intern (iBGP), `r` RIB-failure, `s` suppressed, `d` damped, `h` history, `m` multipath.
- Origin-Code am Ende des Pfads: `i` / `e` / `?`.
- Lokal originiert: Next Hop **0.0.0.0**, Weight **32768**, leerer AS_PATH (nur `i`).
- 10.0.2.0/24: von R2 über SP1 → AS_PATH **1 200**, Next Hop = SP1 (192.168.1.10); die **Metric-Spalte ist leer**, weil SP1 den MED von R2 nicht an ein weiteres AS weitergibt. 10.0.3.0/24 hat MED 0, weil SP1 es selbst originiert.

```
SP1# show ip route bgp
B   10.0.1.0/24 [20/0] via 192.168.1.11, 00:20:31
B   10.0.2.0/24 [20/0] via 192.168.2.11, 00:20:14
```
- `[20/0]` = AD 20 (eBGP) / Metrik = MED 0. Abschließend Ping auf 10.0.1.1 und 10.0.2.1.

### Troubleshooting-Hinweise

- Nachbar bleibt Idle/Active: Adresse/remote-as, Erreichbarkeit, TCP 179, bei Loopbacks update-source und ebgp-multihop prüfen.
- Falsche remote-as: NOTIFICATION „Bad Peer AS“, Session kommt nicht über OpenSent hinaus.
- Präfix wird nicht annonciert: network-Befehl ohne exakten RIB-Eintrag (Maske prüfen).
- Route in BGP, aber nicht in der RIB: Next Hop nicht erreichbar (kein `>`) oder bessere AD (`r`).

## Fehler/Ungenauigkeiten im Kurs

| Stelle | Kursaussage | Richtig | Quelle |
|---|---|---|---|
| S. 99, S. 104 | öffentlich 1–64511, privat **64512–65535** | privat 64512–**65534**; 65535 reserviert; 64496–64511 Dokumentation; privat 32 Bit 4200000000–4294967294 | RFC 6996, RFC 7300, RFC 5398 |
| S. 99 | TCP-Fenster „65,576 bytes“ | Tippfehler; ohne Window Scaling max. **65 535** Byte | RFC 793/7323 |
| S. 99, S. 100 | „periodic TCP keepalives“, „BGP/TCP keepalive message“ | BGP-KEEPALIVE ist eine eigene BGP-Nachricht (Typ 4), kein TCP-Keepalive | RFC 4271 |
| S. 100 | Versionsfeld: die höchste gemeinsame Version wird verwendet | Im OPEN selbst wird nichts ausgehandelt, es steht nur die eigene Version. Unterstützt der Empfänger sie nicht, sendet er eine NOTIFICATION (OPEN Message Error / Unsupported Version Number). Deren Datenfeld nennt die höchste lokal unterstützte Version unterhalb der angebotenen, und der Sender kann es damit erneut versuchen. Im Ergebnis landet man so bei der höchsten gemeinsamen Version, aber erst über einen neuen Verbindungsaufbau. Heute ist das unkritisch, weil praktisch nur BGP-4 existiert | RFC 4271 Kap. 6.2 |
| S. 100 | Beispiel für einen optionalen OPEN-Parameter: Session-Authentifizierung | Der Auth-Parameter ist veraltet; heute ist der relevante optionale Parameter **Capabilities**. Authentifizierung läuft über TCP-MD5/TCP-AO | RFC 4271 (Anhang: Auth-Parameter entfernt); RFC 5492 |
| S. 100 | falsche ASN im OPEN → Session beendet | stimmt; erkannt wird es im Zustand **OpenSent** (NOTIFICATION OPEN Message Error / Bad Peer AS) | RFC 4271; Prüfprotokoll |
| S. 103 | „Each router modifies the next-hop attribute“ | gilt für eBGP; **iBGP ändert den Next Hop nicht** (außer next-hop-self) | RFC 4271 Kap. 5.1.3 |
| S. 103, Abschnitt Nontransitive | „If an update containing an **optional transitive** attribute is received …“ | gemeint ist **optional non-transitive**: unbekannte non-transitive Attribute werden entfernt | RFC 4271 Kap. 5 |
| S. 103 | MED wird beim Weitergeben an ein weiteres AS „auf 0 zurückgesetzt“ | Der MED wird **nicht** weitergegeben (Attribut fehlt, `show ip bgp` zeigt leere Metric-Spalte); erst der Empfänger behandelt einen fehlenden MED per Default wie 0 | RFC 4271 Kap. 5.1.4; Cisco 13753; Lab-Ausgabe S. 104 |
| S. 103 | well-known mandatory „für jede Route in jedem Update“ | in jedem UPDATE, das NLRI enthält (reine Withdraw-Updates brauchen keine Attribute) | RFC 4271 |
| S. 104 | „Network 10.0.1.2.0/24 is the simulated LAN in AS 200“ | Tippfehler: **10.0.2.0/24** | Topologie |
| S. 104 | erste `show ip route`-Ausgabe: „10.0.0.0/8 … 2 subnets“ bei vier Einträgen; `show ip bgp summary` mit „2 network entries“, obwohl drei Präfixe existieren | Ausgaben stammen aus unterschiedlichen Zeitpunkten; richtig wären 4 Subnetze bzw. 3 Einträge | Lab-Ausgaben |
| S. 104 | Spaltenbeschreibung: AS-Nummer „this address is derived …“ | Copy-Paste-Fehler; gemeint ist die konfigurierte remote-as | – |

## Bilder

Ordner `bilder/10-ebgp/`:

- `01-igp-egp.svg` – IGP innerhalb, BGP zwischen autonomen Systemen; TCP 179; ASN-Bereiche (privat 64512–65534, 32 Bit).
- `02-path-vector.svg` – Hop-by-hop-Paradigma: AS 65020 meldet AS 65010 nur seinen Best Path zu AS 65060, Loop-Schutz über die eigene ASN im AS_PATH.
- `03-tabellen.svg` – Neighbor Table, BGP Table und Routing Table mit AD 20/200 und Übergabe des Best Path.
- `04-nachrichten.svg` – Sessionaufbau mit OPEN/KEEPALIVE/UPDATE/NOTIFICATION und Inhalt der OPEN-Nachricht.
- `05-fsm.svg` – BGP-Zustandsautomat Idle → Connect/Active → OpenSent → OpenConfirm → Established mit typischen Fehlerursachen.
- `06-ebgp-ibgp.svg` – eBGP vs. iBGP: Peers, TTL, Next Hop, AS_PATH, AD, Split Horizon.
- `07-best-path.svg` – Best-Path-Reihenfolge als Treppe mit „höher/niedriger ist besser“.
- `08-attribute.svg` – Vier Attributklassen mit Beispielen und Reichweite von Weight, LOCAL_PREF und MED.
- `09-lab-topo.svg` – Discovery-11-Topologie (SP1 AS 1, R1 AS 100, R2 AS 200) mit Konfiguration und erwarteter `show ip bgp`-Sicht auf R1.
