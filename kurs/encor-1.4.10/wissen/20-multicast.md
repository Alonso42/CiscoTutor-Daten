# Introducing Multicast Protocols

Quelle: ENCOR 1.4.10 Student Guide, Seiten 211–218 (210 Intro, 219 Summary Challenge und 220 Answer Key nicht ausgewertet)

Topics: ENCOR-3.3.d (Multicast: PIM-SM, IGMPv2/v3, SSM, BiDir, MSDP)

Ergänzungen, die nicht im Kurs stehen (MAC-Mapping, IGMP Snooping, Defaults, Befehle, mroute-Flags, Anycast-RP-Konfiguration, SSM-Mapping), sind mit *(Ergänzung)* markiert und stammen aus RFCs bzw. Cisco-IOS-XE-Konfigurationsleitfäden.

---

## 1. Multicast-Grundlagen (S. 211)

### Idee
- Eine Quelle sendet **eine** Kopie an eine Gruppenadresse G. Router replizieren das Paket erst dort, wo sich die Pfade zu den Empfängern teilen (so spät wie möglich). Auf jedem Link existiert nur eine Kopie.
- Die Quelle muss die Unicast-Adressen der Empfänger nicht kennen; Quelladresse ist immer ihre eigene Unicast-Adresse, Zieladresse die Gruppe.
- Unicast: eine Kopie pro Empfänger → Last steigt 1:1 mit der Empfängerzahl. Multicast skaliert unabhängig davon.
- Router nutzen **RPF** (Reverse Path Forwarding), um Schleifen zu vermeiden.
- Empfänger melden ihr Interesse beim Last-Hop-Router (direkt angeschlossener Router) per **IGMP** (IPv4) bzw. **MLD** (IPv6).

### Vor- und Nachteile
- Vorteile: Bandbreiteneffizienz, weniger Last auf Quelle und Routern, nahezu gleichzeitige Ankunft bei allen Empfängern, neue Anwendungen (IPTV, verteilte Anwendungen).
- Nachteile (meist **UDP**-basiert): best effort (Drops, kein Retransmit sinnvoll bei Echtzeit), **keine Staukontrolle** auf Transportebene, gelegentlich **Duplikate** und **Out-of-order**-Pakete bei Topologieänderungen, Zugriffsbeschränkung/Abhörschutz schwierig.

### Anwendungsmodelle
- Häufigste Modelle: **one-to-many** (eine Quelle, viele Empfänger) und **many-to-many** (Host ist zugleich Sender und Empfänger).
- Weitere: many-to-one, few-to-many (v. a. Finanzanwendungen).
- Echtzeit: Live-Übertragungen, Finanzdaten, Whiteboard, Videokonferenz. Nicht-Echtzeit: Dateiübertragung, Replikation, VoD.

### Adressen (RFC 5771)
- IPv4-Multicast = Klasse D = **224.0.0.0/4** (224.0.0.0–239.255.255.255), die höchsten 4 Bit sind **1110**.
- **224.0.0.0/24 – Local Network Control (link-local)**: von IANA für Protokolle reserviert, wird **nie geroutet**, unabhängig vom TTL; TTL meist 1.
- *(Ergänzung)* **224.0.1.0/24 – Internetwork Control**: wird geroutet; z. B. 224.0.1.1 NTP, **224.0.1.39 Cisco-RP-Announce**, **224.0.1.40 Cisco-RP-Discovery**.
- Kurs: „Global scope“ 224.0.1.0–238.255.255.255, dynamisch im Internet vergeben. Darin liegen u. a.:
  - **232.0.0.0/8 – SSM** (Source-Specific Multicast)
  - *(Ergänzung)* 233.0.0.0/8 – GLOP (aus 16-Bit-AS-Nummer abgeleitet, RFC 3180)
- **239.0.0.0/8 – Administratively scoped** (RFC 2365): privat, nur innerhalb einer Organisation (vergleichbar mit RFC 1918).
- Bekannte Link-local-Adressen: 224.0.0.1 All Hosts, 224.0.0.2 All Routers, 224.0.0.5/224.0.0.6 OSPF, 224.0.0.9 RIPv2, 224.0.0.10 EIGRP, **224.0.0.13 All PIM Routers**, *(Ergänzung)* **224.0.0.22 IGMPv3-Reports**, 224.0.0.18 VRRP, 224.0.0.102 HSRPv2.

### Abbildung IP-Gruppe → Ethernet-MAC *(Ergänzung, RFC 1112)*
- MAC = **01:00:5E** (OUI) + ein **0-Bit** + **untere 23 Bit** der IP-Adresse.
- Von den 28 variablen Bit der Gruppenadresse gehen **5 Bit verloren** → **32 IP-Gruppen** teilen sich eine MAC (32:1-Überlappung).
- Rechenweg: 2. Oktett modulo 128 (höchstes Bit streichen), 3. und 4. Oktett unverändert als Hex.
  - 239.1.1.1 → 01:00:5E:01:01:01
  - 239.130.5.10 → 130−128 = 2 → 01:00:5E:02:05:0A
  - 224.200.10.20 → 200−128 = 72 = 0x48 → 01:00:5E:48:0A:14
  - 232.10.20.30 → 01:00:5E:0A:14:1E
  - 239.255.0.1 → 255−128 = 127 = 0x7F → 01:00:5E:7F:00:01
- Folge der Überlappung: Eine NIC kann Frames einer fremden Gruppe mit derselben MAC annehmen; die IP-Schicht verwirft sie. Switches mit MAC-basiertem Snooping können solche Gruppen nicht trennen.
- IPv6: 33:33 + untere 32 Bit der IPv6-Gruppenadresse.

### Service-Modell (RFC 1112)
- Sender senden an eine Gruppenadresse, Empfänger melden Interesse, Router liefern aus.
- Gruppen stehen für Empfängermengen, nicht für einzelne Hosts. Mitglieder können jederzeit beitreten/austreten.
- Quellen senden einfach los, ohne Ankündigung; der **First-Hop-Router** (FHR, direkt an der Quelle) leitet weiter.
- Empfänger melden sich beim **Last-Hop-Router** (LHR, direkt am Empfänger). LHRs teilen die Mitgliedschaft dem Netz mit (PIM-Joins).

## 2. IGMP (S. 212)

Zweck: Host teilt dem lokalen Multicast-Router mit, welche Gruppen er empfangen will. IGMP ist IP-Protokoll 2 *(Ergänzung)*, TTL immer **1** (nur lokal gültig).

### IGMPv1 (RFC 1112)
- Query-Response-Modell. Router senden periodisch **General Queries an 224.0.0.1** (Kurs: üblicherweise alle 60–120 s).
- Hosts antworten mit **Membership Report an die Gruppenadresse** – unaufgefordert beim Beitritt (unsolicited) oder als Antwort auf Queries.
- **Report Suppression**: Hört ein Host den Report eines anderen Mitglieds derselben Gruppe, unterdrückt er seinen eigenen (spart CPU/Bandbreite).
- Kein Leave → Router merkt das Verlassen erst durch Timeout.
- Keine Querier-Wahl in v1 *(Ergänzung: der PIM-DR übernimmt das Querying)*.

### IGMPv2 (RFC 2236)
- **Group-Specific Query**: an die Gruppenadresse G statt an 224.0.0.1, fragt nur nach Mitgliedern einer Gruppe.
- **Leave Group Message** *(Ergänzung: an 224.0.0.2)* → verkürzte Leave-Latenz. Danach sendet der Querier Group-Specific Queries (Last Member Query, *Ergänzung: Default 2 Queries im Abstand 1 s*). Antwortet niemand, wird die Gruppe vom Interface entfernt.
- **Querier-Wahl**: Router mit der **niedrigsten IP-Adresse** wird Querier. Alle starten als Querier und geben die Rolle ab, sobald sie eine Query von einer niedrigeren IP hören. *(Achtung: PIM-DR = höchste Priorität/höchste IP – das ist eine andere Wahl.)*
- **Max Response Time** im Query-Paket (Kurs nennt es „query-interval response time“) steuert, wie schnell Hosts antworten → verhindert Report-Bursts. *(Ergänzung: Cisco-Default 10 s.)*
- Abwärtskompatibel zu v1.
- *(Ergänzung)* Cisco-Defaults: Query Interval 60 s, Querier Timeout 120 s (2× Query Interval), Max Response Time 10 s. Default-IGMP-Version auf Cisco-Interfaces: 2.

### IGMPv3 (RFC 3376)
- **Source Filtering**: Host meldet Gruppe **und** Quellen.
  - **INCLUDE**-Modus: nur Traffic von den aufgelisteten Quellen.
  - **EXCLUDE**-Modus: Traffic von allen Quellen außer den aufgelisteten. Ein IGMPv2-Join entspricht EXCLUDE mit leerer Liste („alle Quellen“).
- *(Ergänzung)* Reports gehen an **224.0.0.22**; **keine Report Suppression** (jeder Host meldet einzeln → Router kennt alle Mitglieder, ermöglicht Explicit Tracking).
- Grundlage für **SSM**. Aktuelle Windows-, macOS- und UNIX-Systeme unterstützen IGMPv3.

### IGMP Snooping *(Ergänzung)*
- Layer-2-Switch hört IGMP-Nachrichten mit und leitet Multicast-Frames nur an Ports mit interessierten Empfängern und an Multicast-Router-Ports weiter, statt sie im VLAN zu fluten.
- Auf Catalyst-Switches standardmäßig aktiv (`ip igmp snooping`).
- Ohne Multicast-Router im VLAN braucht Snooping einen Querier: `ip igmp snooping querier`.
- `ip igmp snooping vlan 10 immediate-leave`: Port wird sofort nach Leave entfernt (nur sinnvoll, wenn pro Port nur ein Empfänger hängt).
- CGMP: alte Cisco-proprietäre Alternative (Router informiert Switch).

### Befehle IGMP *(Ergänzung)*
```
interface Gi0/1
 ip pim sparse-mode            ! aktiviert auch IGMP auf dem Interface
 ip igmp version 3
 ip igmp join-group 239.1.1.1  ! Router selbst wird Mitglied (verarbeitet Pakete, z. B. für ping-Tests)
 ip igmp static-group 239.1.1.1 ! Router leitet die Gruppe auf das Interface, ohne selbst Mitglied zu sein
show ip igmp groups
show ip igmp interface Gi0/1   ! Version, Query Interval, Querier, DR
show ip igmp snooping groups
```

## 3. Verteilungsbäume (S. 213)

### Source Tree / Shortest Path Tree (SPT)
- Wurzel an der Quelle, kürzester Weg zu den Empfängern. Notation **(S,G)**, z. B. (192.168.1.1, 224.1.1.1).
- Für **jede Quelle** einer Gruppe existiert ein eigener SPT.
- Vorteil: optimaler Pfad, minimale Latenz. Nachteil: State pro (S,G) → Speicher.

### Shared Tree / RP Tree (RPT)
- Gemeinsame Wurzel an einem gewählten Punkt: **Rendezvous Point (RP)**. Notation **(*,G)** – * = alle Quellen.
- In PIM-SM unidirektional: Quelle → RP über einen Source Tree, dann RP → Empfänger über den Shared Tree. (Ein Empfänger zwischen Quelle und RP wird direkt bedient.)
- Vorteil: minimaler State. Nachteil: evtl. suboptimaler Pfad (Umweg über RP) → RP-Platzierung wichtig.

### Gemeinsam
- Beide Bäume sind schleifenfrei; Replikation nur an Verzweigungen.
- Bäume ändern sich dynamisch: Hat ein Ast keine Empfänger mehr, wird er gepruned; meldet sich ein Empfänger, wird er wieder aufgebaut.

## 4. IP-Multicast-Routing (S. 214)

### RPF
- Unicast-Routing betrachtet nur das Ziel. Multicast-Routing betrachtet die **Quelle**: Upstream = Richtung Quelle, Downstream = Richtung Empfänger.
- **RPF-Check**: Router sucht die Quelladresse in der Unicast-Routing-Tabelle. Kam das Paket auf dem Interface an, über das der Router selbst zur Quelle routen würde (**RPF-Interface**), besteht es den Check; sonst wird es verworfen.
- Auf dem Shared Tree wird gegen die **RP-Adresse** geprüft, auf dem SPT gegen die **Quelladresse**.
- *(Ergänzung)* Bei Equal-Cost-Pfaden wählt IOS standardmäßig den Nachbarn mit der höchsten IP als RPF-Nachbarn.
- *(Ergänzung)* Wenn Unicast- und Multicast-Topologie abweichen (z. B. Multicast nur über einen Tunnel): **static mroute** (`ip mroute <src> <mask> <rpf-neighbor|interface>`) oder MP-BGP (Address Family ipv4 multicast).
- *(Ergänzung)* Prüfen: `show ip rpf <source>`.

### PIM (Protocol Independent Multicast)
- Nutzt **die vorhandene Unicast-Routing-Tabelle** (EIGRP, OSPF, BGP, statisch) für den RPF-Check; tauscht **keine** eigenen Routing-Updates aus.
- *(Ergänzung)* PIMv2: IP-Protokoll **103**, Hellos an **224.0.0.13**, Hello-Intervall 30 s, Holdtime 105 s. **DR-Wahl**: höchste DR-Priorität (Default 1), dann höchste IP. Der DR auf dem Empfänger-LAN sendet Joins, der DR auf dem Quell-LAN sendet Register.
- *(Ergänzung)* **Assert**: Leiten zwei Router auf ein Multiaccess-Segment dieselbe Gruppe weiter, gewinnt der mit der niedrigeren AD, dann der besseren Metrik zur Quelle, dann der höchsten IP; der Verlierer pruned.

### PIM Dense Mode (PIM-DM)
- **Push-Modell**: Flood & Prune. Traffic wird zunächst überall hin geflutet; Router ohne Empfänger/Downstream-Nachbarn senden **Prune**. Der Vorgang wiederholt sich periodisch (Kurs: alle 3 Minuten).
- Nur **Source Trees (S,G)**, kein Shared Tree, kein RP.
- Sinnvoll nur, wenn fast jedes Subnetz Empfänger hat. Kaum noch eingesetzt.
- *(Ergänzung)* Graft-Nachricht hebt einen Prune schnell wieder auf, wenn ein neuer Empfänger erscheint.

### PIM Sparse Mode (PIM-SM, RFC 7761)
- **Explizites Pull-Modell**: Traffic nur dorthin, wo jemand per Join danach fragt. Für alle Produktionsnetze die empfohlene Wahl, unabhängig von Dichte.
- Shared Tree am RP, Umschalten auf SPT möglich.
- Ablauf:
  1. Empfänger sendet IGMP-Report → LHR (DR) sendet **(*,G)-Join** hop-by-hop zum RP → Ast des Shared Tree.
  2. Quelle sendet → FHR (DR) kapselt die Pakete in **PIM-Register** und schickt sie per **Unicast** an den RP.
  3. RP entpackt, leitet den Shared Tree hinunter und sendet einen **(S,G)-Join** Richtung Quelle.
  4. Sobald der Traffic nativ über den SPT am RP ankommt, sendet der RP **Register-Stop** (Unicast) an den FHR.
  5. **SPT-Switchover**: Überschreitet der Traffic die SPT-Threshold, sendet der LHR einen (S,G)-Join direkt Richtung Quelle. **Default-Threshold 0** → Umschalten nach dem ersten Paket. *(Ergänzung: danach (S,G,rpt)-Prune mit RP-Bit Richtung RP; `ip pim spt-threshold infinity` verhindert das Umschalten.)*
- Verschiedene RPs für verschiedene Gruppenbereiche per ACL möglich; pro Gruppe gibt es aber immer **nur eine RP-Adresse** (bei Anycast-RP teilen sich mehrere Router diese Adresse).
- Erweiterungen: **BiDir-PIM** (many-to-many), **SSM** (nur SPTs, kein RP, 232/8).

### Grundkonfiguration *(Ergänzung)*
```
ip multicast-routing          ! auf manchen Plattformen: ip multicast-routing distributed
interface Gi0/0
 ip pim sparse-mode
ip pim rp-address 10.0.0.1
```

### show ip mroute – Flags *(Ergänzung, belegt in Cisco Command Reference)*
| Flag | Bedeutung |
|---|---|
| D | Dense |
| S | Sparse |
| B | Bidir Group |
| s | SSM Group |
| C | Connected (direkt angeschlossenes Mitglied) |
| L | Local (Router selbst ist Mitglied) |
| P | Pruned (OIL leer) |
| R | RP-bit set ((S,G)-Eintrag zeigt Richtung RP, nach SPT-Prune) |
| F | Register flag (Router registriert eine direkt angeschlossene Quelle → FHR) |
| T | SPT-bit set (Pakete wurden über den SPT empfangen) |
| J | Join SPT (Rate über Threshold → nächstes Paket löst SPT-Join aus) |
| M | MSDP created entry |
| A | Candidate for MSDP Advertisement |
| I | Received Source Specific Host Report |

Beispiel (LHR nach SPT-Switchover, gekürzt):
```
(*, 239.1.1.1), 00:05:10/00:02:55, RP 10.0.0.1, flags: SJC
  Incoming interface: Gi0/1, RPF nbr 10.1.12.1
  Outgoing interface list:
    Gi0/3, Forward/Sparse, 00:05:10/00:02:55
(10.1.1.10, 239.1.1.1), 00:01:02/00:02:57, flags: JT
  Incoming interface: Gi0/2, RPF nbr 10.1.23.2
  Outgoing interface list:
    Gi0/3, Forward/Sparse, 00:01:02/00:02:57
```
- (*,G): Incoming Interface zeigt zum RP; (S,G): Incoming Interface zeigt zur Quelle. Incoming Interface „Null“ mit RPF-Nachbar 0.0.0.0 deutet auf fehlende Route/RPF-Fehler hin.

## 5. Rendezvous Point (S. 215)

- RP = gemeinsame Wurzel des Shared Tree. Alle Router einer PIM-Domäne müssen eine Gruppe auf **denselben** RP abbilden.

### Static RP
- RP-Adresse auf **jedem** Router konfigurieren: `ip pim rp-address 10.0.0.1 [ACL]`.
- Einfach, für kleine/stabile Netze. Aber: Änderung = jeden Router anfassen; **kein Failover**, kein Load-Balancing.
- Redundanz/Lastteilung mit **Anycast-RP**.
- Koexistiert mit Auto-RP; **dynamisch gelernter RP hat Vorrang** vor dem statischen. *(Ergänzung: Schlüsselwort `override` dreht das um.)*

### BSR (Bootstrap Router, RFC 5059)
- Standardisiert (PIMv2), herstellerübergreifend, auch für IPv6.
- Candidate-BSRs → ein BSR wird gewählt *(Ergänzung: höchste Priorität, dann höchste IP)*. Candidate-RPs melden sich *(Ergänzung: per Unicast)* beim BSR.
- BSR verteilt das **RP-Set** (alle C-RPs) an alle Router *(Ergänzung: Bootstrap-Nachrichten hop-by-hop an 224.0.0.13 – Kurs sagt „broadcast“)*; jeder Router wählt mit demselben Hash-Algorithmus denselben RP.
- Konfiguration nur auf C-BSRs und C-RPs; Backup-RPs möglich.
```
ip pim bsr-candidate Loopback0
ip pim rp-candidate Loopback0 group-list 10
```

### Auto-RP (Cisco-proprietär)
- **Candidate-RPs** senden **RP-Announce** an **224.0.1.39** (CISCO-RP-ANNOUNCE).
- **Mapping Agents** hören 224.0.1.39, wählen pro Gruppenbereich den RP *(Ergänzung: höchste IP gewinnt)* und senden **RP-Discovery** an **224.0.1.40** (CISCO-RP-DISCOVERY). Alle PIM-Router hören 224.0.1.40.
- Konfiguration nur auf C-RPs und Mapping Agents; Backup-RPs möglich. **Nicht für IPv6.**
- *(Ergänzung)* 224.0.1.39/40 werden im Dense Mode geflutet – in reinen Sparse-Mode-Netzen ist dafür `ip pim autorp listener` (oder sparse-dense-mode) nötig, sonst Henne-Ei-Problem (ohne RP kein Sparse-Forwarding der Auto-RP-Gruppen).
```
ip pim send-rp-announce Loopback0 scope 16 group-list 10
ip pim send-rp-discovery Loopback0 scope 16
ip pim autorp listener
show ip pim rp mapping
```
- **Auto-RP und BSR nicht gemeinsam** im selben Netz.

### Anycast-RP *(Ergänzung zum Kurs-Hinweis)*
- Mehrere RPs mit **derselben /32-Adresse** (z. B. Loopback1); alle Router nutzen diese Adresse als (statischen) RP. Das IGP leitet jeden zum nächsten RP; fällt einer aus, konvergiert das IGP zum anderen.
- Da Quellen sich nur bei „ihrem“ RP registrieren, tauschen die RPs aktive Quellen per **MSDP** aus (Peering über eindeutige Adressen, `ip msdp originator-id` mit eindeutiger Adresse).

## 6. Source-Specific Multicast (S. 216)

- Variante von PIM-SM, nur **(S,G)-SPTs**, **kein Shared Tree, kein RP**, kein MSDP nötig (RFC 3569 Überblick, *Ergänzung: Spezifikation RFC 4607*).
- Reservierter Bereich **232.0.0.0/8**; Router dürfen dafür keinen Shared Tree bauen. *(Ergänzung: `ip pim ssm default` aktiviert 232/8, `ip pim ssm range <ACL>` eigene Bereiche.)*
- Ablauf: Host meldet per **IGMPv3** Quelle + Gruppe → LHR erzeugt (S,G)-State und sendet sofort einen **(S,G)-Join** Richtung Quelle. Kein (*,G)-Join, keine Register.
- Wie erfährt der Host die Quelle? Out-of-band: Verzeichnisdienst, Session-Ankündigung, Webseite.
- Ideal für **one-to-many** mit **bekannten Quellen** (Broadcast-artige Anwendungen, IPTV).
- Adressvergabe vereinfacht: Gruppenadresse muss nicht global eindeutig sein – (S1,G) und (S2,G) sind getrennte Kanäle.
- Koexistiert mit normalen PIM-SM-Gruppen.
- Voraussetzung: IGMPv3 auf Hosts und LHR. *(Ergänzung: Ausnahme **SSM-Mapping** – der LHR übersetzt IGMPv1/v2-Reports für SSM-Gruppen per statischer Zuordnung oder DNS in (S,G)-Joins: `ip igmp ssm-map enable`, `ip igmp ssm-map static <ACL> <source>`; auch URD als ältere Alternative.)*
- Altgeräte, die 232/8 nicht kennen, könnten Shared Trees bauen → Filter:
  - RP: Register für 232/8 sofort mit Register-Stop beantworten.
  - LHR: keine (*,G)-Joins für 232/8.
  - Zwischenrouter: keine (S,G)-RP-bit-Prunes.
  - MSDP: keine SA-Nachrichten für 232/8 erzeugen/weiterleiten (auf RP/Border-Router).

## 7. Bidirectional PIM (S. 217)

- Problem PIM-SM bei many-to-many: Register-Kapselung und (S,G)-State für jede Quelle → viel Speicher/CPU.
- BiDir: derselbe Baum für Quelle → RP und RP → Empfänger. **Nur (*,G)**, keine Register, **keine (S,G)-Einträge, kein SPT-Switchover**.
- **Designated Forwarder (DF)**: pro Link **und pro RP** ein DF = Router mit dem **besten Unicast-Pfad zum RP**. Gewählt auf Multiaccess- und Point-to-Point-Links, einmalig bei RP-Discovery; DF-Ausfall wird über PIM-Hellos erkannt → Neuwahl.
- Aufgaben des DF: einziger Router, der Pakete **downstream** auf den Link weiterleitet, und einziger, der Pakete vom Link **upstream** Richtung RP mitnimmt. Er sendet (*,G)-Joins Richtung RP; Downstream-Router adressieren ihre Joins an den DF (Upstream-Router-Feld). Nicht-DFs ignorieren Joins.
- Weiterleitungsregel: Paket wird weitergeleitet, wenn es auf dem IIF (Richtung RP) ankommt (downstream) **oder** der Router DF des Empfangs-Links ist (upstream). Es geht an alle OIL-Interfaces und das IIF, außer dem Empfangsinterface.
- Traffic kann auf einem Ast direkt zu Empfängern fließen, ohne erst den RP zu erreichen.
- Gruppen als bidirektional kennzeichnen: statisch oder per Auto-RP/BSR (Bidir-Bit im Encoded-Group-Feld). Koexistiert mit normalen PIM-SM-Gruppen.
- *(Ergänzung)* `ip pim rp-address 10.0.0.1 bidir`; `show ip mroute` zeigt Flag **B** und „Bidir-Upstream“. Der RP kann eine „Phantom-RP“-Adresse sein, da keine Register terminiert werden.
- Beispiel: Börsenhandel mit Tausenden Teilnehmern.

## 8. MSDP (S. 218)

- **Interdomain**: verbindet die RPs verschiedener PIM-SM-Domänen. Keine Interdomain-Shared-Trees, nur Interdomain-Source-Trees.
- Funktioniert **nur mit PIM-SM** (RP kennt alle Quellen über Register und alle Empfänger über (*,G)-Joins).
- RP, bei dem sich eine Quelle registriert, erzeugt **Source-Active (SA)**-Nachrichten (S, G, Originator-RP) – periodisch alle **60 s**, solange die Quelle aktiv ist – an alle MSDP-Peers.
- MSDP-Peers kommunizieren über **TCP** *(Ergänzung: Port 639, RFC 3618; SAs werden laut RFC gecacht)*.
- **Peer-RPF-Check**: SA wird nur akzeptiert/geflutet, wenn sie vom RPF-Peer Richtung Originator-RP kommt (BGP-AS-Pfad). Verhindert Schleifen. Stub-Domänen mit nur einem Peer (Default-Peer) akzeptieren alles.
- Empfangender RP mit (*,G)-State und **nicht-leerer OIL** sendet einen (S,G)-Join Richtung Quelle (über den BGP/MBGP-Pfad, nicht über die MSDP-Session). Ohne Empfänger kein Join.
- Der LHR kann danach per SPT-Switchover direkt auf die Quelle umschalten.
- **SA-Cache**: Kurs sagt „typischerweise nicht gespeichert“; Caching reduziert Join-Latenz (RP muss nicht auf die nächste periodische SA warten). Nicht cachende Speaker können cachende abfragen.
- Kein Full Mesh nötig; eine MSDP-Verbindung zu den übrigen reicht.
- ISP-Anforderungen: explizites Join-Protokoll → PIM-SM; bestehendes Betriebsmodell → MP-BGP; eigener RP ohne Teilen mit Konkurrenz und freie RP-Platzierung → MSDP.
```
ip msdp peer 192.0.2.2 connect-source Loopback0 remote-as 65002
ip msdp originator-id Loopback0
show ip msdp peer
show ip msdp sa-cache
show ip msdp summary
```

## Troubleshooting-Checkliste *(Ergänzung)*
1. `show ip igmp groups` am LHR: Ist der Empfänger angemeldet? Richtige IGMP-Version (SSM braucht v3)?
2. `show ip pim neighbor` / `show ip pim interface`: PIM auf allen Interfaces des Pfads aktiv? (Fehlt PIM auf einem Interface → RPF-Interface ohne PIM-Nachbar.)
3. `show ip pim rp mapping`: Kennt jeder Router denselben RP?
4. `show ip rpf <Quelle/RP>`: Stimmt das RPF-Interface? Sonst Unicast-Routing oder static mroute korrigieren.
5. `show ip mroute <G>`: Einträge, Flags, Incoming Interface, OIL; `show ip mroute count` für Paketzähler/RPF-Fails.
6. TTL der Quelle zu klein? (Pakete sterben unterwegs.)

## Fehler/Ungenauigkeiten im Kurs
1. **S. 212**: Das IGMPv2-Feld heißt **Max Response Time** (RFC 2236, Abschnitt 2.2), nicht „query-interval response time“. Das Query Interval ist ein separater Timer.
2. **S. 215**: Der BSR „broadcastet“ das RP-Set nicht, sondern flutet Bootstrap-Nachrichten hop-by-hop an 224.0.0.13 (RFC 5059).
3. **S. 216**: SSM wird mit RFC 3569 zitiert; das ist nur die Architekturübersicht. Die eigentliche SSM-Spezifikation ist **RFC 4607**.
4. **S. 216 / Bestand**: „SSM benötigt IGMPv3“ ist als absolute Aussage ungenau: Mit **SSM-Mapping** (oder URD) können IGMPv1/v2-Hosts SSM-Dienste nutzen (Cisco IP Multicast Configuration Guide, „SSM Mapping“).
5. **S. 218**: Das MSDP-Beispiel widerspricht sich: Die Quelle wird erst in Domäne B, später der First-Hop-Router „s“ in Domäne A verortet; der RP in Domäne B sendet SAs „an seine Peers in B und C“.
6. **S. 218**: „SA-Nachrichten werden typischerweise nicht gespeichert“ – auf Cisco IOS/IOS XE ist SA-Caching standardmäßig aktiv (seit IOS 12.1(7) nicht abschaltbar; Cisco „Configuring MSDP“).
7. **S. 211**: Der „Global scope“ 224.0.1.0–238.255.255.255 schließt SSM (232/8) und GLOP (233/8) ein – keine Fehlaussage, aber die Sonderbereiche fehlen dort.
8. **S. 214**: Die Formulierung, der Router repliziere auf Downstream-Pfade nach „best unicast route metric“, ist irreführend: Die OIL entsteht durch PIM-Joins/IGMP-Mitgliedschaft; die Unicast-Metrik bestimmt nur das RPF-(Upstream-)Interface.

## Bilder
- `bilder/20-multicast/01-uni-multi.svg` – Unicast (eine Kopie pro Empfänger) vs. Multicast (eine Kopie pro Link, Replikation an der Verzweigung).
- `bilder/20-multicast/02-adressbereiche.svg` – Aufteilung von 224.0.0.0/4 (link-local, Internetwork Control, SSM, GLOP, admin-scoped) und bekannte Adressen.
- `bilder/20-multicast/03-mac-mapping.svg` – Bit-Abbildung IP-Gruppe → 01:00:5E-MAC mit Rechenbeispiel und 32:1-Überlappung.
- `bilder/20-multicast/04-igmp-versionen.svg` – Vergleichstabelle IGMPv1/v2/v3 und IGMPv2-Leave-Ablauf.
- `bilder/20-multicast/05-baumtypen.svg` – Source Tree (S,G) und Shared Tree (*,G) mit RP-Umweg.
- `bilder/20-multicast/06-rpf-check.svg` – RPF-Check: Paket auf RPF-Interface wird weitergeleitet, Kopie auf anderem Interface verworfen.
- `bilder/20-multicast/07-pim-sm-ablauf.svg` – PIM-SM in sechs Schritten: (*,G)-Join, Register, (S,G)-Join, Register-Stop, SPT-Switchover, RP-Bit-Prune.
- `bilder/20-multicast/08-rp-ermittlung.svg` – Static RP, Auto-RP (224.0.1.39/40) und BSR im Vergleich.
- `bilder/20-multicast/09-ssm.svg` – SSM-Ablauf mit IGMPv3-INCLUDE-Report und direktem (S,G)-Join, SSM-Mapping als Ausnahme.
- `bilder/20-multicast/10-bidir-df.svg` – BiDir-PIM mit DF-Wahl nach bester Unicast-Metrik zum RP.
- `bilder/20-multicast/11-msdp-anycast-rp.svg` – MSDP-SA-Austausch zwischen Domänen und Anycast-RP mit MSDP innerhalb einer Domäne.
