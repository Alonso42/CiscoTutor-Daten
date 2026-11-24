# Building Redundant Switched Topology

Quelle: ENCOR 1.4.10 Student Guide, Seiten 39–47 (STP Overview, STP Operation, STP Types and Features, Discovery 4 „Tune STP and Configure RSTP“, Introducing MST, Discovery 5 „Configure Multiple STP“, PortFast and BPDU Guard, Enhance STP with Root Guard, Summary)

Topics: ENCOR-3.1.c (Spanning Tree: RSTP, MST, Root Guard, Loop Guard, BPDU Guard, BPDU Filter)

Ergänzungen aus eigenem Fachwissen bzw. aus dem Prüfprotokoll (nicht im Kurs) sind mit *(Ergänzung)* markiert. Wichtig: Wo Kurs und aktuelles IOS-XE (Catalyst 9000) abweichen, gilt IOS-XE (siehe Abschnitt „Fehler/Ungenauigkeiten im Kurs“).

## Probleme redundanter Layer-2-Topologien

Redundante Links zwischen Switches erhöhen die Verfügbarkeit, bilden aber Layer-2-Schleifen (Bridging Loops). Ethernet-Frames haben kein TTL, deshalb kreisen sie unbegrenzt. Drei Symptome:

| Problem | Was passiert |
|---|---|
| Broadcast-Sturm | Broadcasts werden auf alle Ports außer dem Eingangsport geflutet, laufen im Kreis in beide Richtungen und vervielfachen sich, bis Links und CPUs ausgelastet sind. |
| Mehrfache Frame-Zustellung | Ein Unicast erreicht das Ziel mehrfach (über jeden Weg eine Kopie). Viele Protokolle erwarten genau eine Kopie und reagieren mit Fehlern. |
| Instabile MAC-Tabelle (MAC database instability) | Dieselbe Quell-MAC wird abwechselnd auf verschiedenen Ports gelernt („MAC flapping“), die Weiterleitung wird unzuverlässig, die CPU ist mit dem ständigen Umlernen beschäftigt. |

Lösung: Spanning Tree Protocol (STP). STP berechnet einen schleifenfreien Baum über alle Switches: Pro Segment bleibt genau ein aktiver Weg zur Root, alle übrigen redundanten Ports werden in einen Standby-Zustand (blocking/discarding) gesetzt. Blockierende Ports leiten keine Daten weiter, hören aber weiter BPDUs. Fällt ein aktiver Link aus, aktiviert STP den Ersatzweg.

## STP-Grundablauf und Port-Rollen

Drei Schritte:
1. **Root Bridge wählen** – genau eine im Netz; Bezugspunkt der Berechnung. Alle Ports der Root sind Designated Ports und forwarden.
2. **Root Port pro Nonroot-Bridge** – der Port mit den niedrigsten kumulierten Pfadkosten zur Root (genau einer je Switch).
3. **Designated Port pro Segment** – der Port des Switches, der auf diesem Segment die niedrigsten Kosten zur Root anbietet (genau einer je Segment).

Alle übrigen Ports sind **nondesignated** und blockieren.

| Rolle (802.1D) | Eigenschaften |
|---|---|
| Root Port | nur auf Nonroot-Bridges, bester Weg zur Root, forwardet, lernt MACs; max. einer pro Bridge |
| Designated Port | auf Root und Nonroot-Bridges; einer pro Segment; forwardet, lernt MACs. Auf der Root sind alle Ports designated |
| Nondesignated Port | blockiert, lernt keine MACs aus Datenframes |
| Disabled Port | administrativ abgeschaltet (shutdown) |

## BPDUs

- Bridge Protocol Data Units transportieren die STP-Information (Root-Wahl, Schleifenerkennung). Default-Intervall: **Hello 2 s**.
- Ziel-MAC: **01-80-C2-00-00-00** (IEEE-STP-Multicast); Quell-MAC: MAC des sendenden Ports.
- Felder (Configuration BPDU): Protocol ID · Version · Message Type (Configuration oder TCN) · Flags (TC, TCA) · Root Bridge ID · Root Path Cost · Sender Bridge ID · Port ID · Message Age · Max Age · Hello Time · Forward Delay.
- Zwei BPDU-Typen: Configuration BPDU und Topology Change Notification (TCN) BPDU; die Bestätigung erfolgt als TCA-Flag in einer Configuration BPDU.
- *(Ergänzung)* Versionsfeld: 0 = 802.1D, 2 = RSTP, 3 = MSTP. PVST+ sendet für VLAN 1 IEEE-BPDUs an 01-80-C2-00-00-00 (untagged im Native VLAN) und für alle VLANs SSTP-BPDUs an 0100.0ccc.cccd (für Nicht-VLAN-1 getaggt).

### Topology Change bei 802.1D

1. Ein Switch erkennt eine Topologieänderung (Link geht down oder ein Port wird forwarding) und schickt eine **TCN-BPDU über seinen Root Port**.
2. Der Designated Switch auf diesem Segment bestätigt mit dem **TCA-Bit** in der nächsten Configuration BPDU und schickt seinerseits eine TCN Richtung Root. Der Sender wiederholt seine TCN, bis die TCA kommt.
3. Die Root setzt in ihren Configuration BPDUs das **TC-Bit**; alle Bridges reichen es weiter.
4. *(Ergänzung)* Wer TC-BPDUs empfängt, verkürzt das MAC-Aging auf Forward Delay (15 s). Die Root setzt das TC-Bit für Max Age + Forward Delay = **35 s**.

Im Normalbetrieb schickt ein Nonroot-Switch keine Configuration BPDUs Richtung Root, er empfängt sie auf dem Root Port und reicht sie über Designated Ports weiter. Nur TCNs laufen Richtung Root.

## Root-Bridge-Wahl und Bridge ID

- **Bridge ID (BID) = Bridge Priority + MAC-Adresse.** Niedrigste BID gewinnt.
- Priority: 0–61440, nur in **4096er-Schritten**, Default **32768**.
- **Extended System ID**: Das 16-Bit-Prioritätsfeld wird geteilt in 4 Bit Priorität und 12 Bit VLAN-ID (sys-id-ext). Darum sind nur 16 Prioritätswerte möglich (0, 4096 … 61440), und die angezeigte Priorität ist „konfigurierte Priorität + VLAN“ (VLAN 1 mit Default → **32769**; VLAN 10 → 32778).
- Bei gleicher Priorität entscheidet die niedrigste MAC. Ohne Konfiguration wird also oft der älteste Switch Root (ältere Geräte haben meist niedrigere MACs) – meist suboptimal.
- Die Wahl ist fortlaufend: Jeder Switch hält sich anfangs für die Root und sendet BPDUs mit seiner eigenen BID; sobald er eine bessere BID hört, übernimmt er diese. Erscheint später ein Switch mit besserer BID, wird er neue Root (präemptiv).

```
spanning-tree vlan 1 priority 4096          ! exakter Wert, Vielfaches von 4096
spanning-tree vlan 1 root primary           ! Makro
spanning-tree vlan 1 root secondary         ! Makro
show spanning-tree root
```

`root primary`/`root secondary` (Makros):
- primary: Ist die aktuelle Root-Priorität > 24576 → eigene Priorität 24576. Sonst → 4096 unter der Root-Priorität. Ist das nicht möglich (Root hat bereits 0), schlägt der Befehl fehl.
- secondary: setzt 28672 (Schätzwert, der Switch kennt die zweitbeste Priorität nicht).
- In der running-config steht danach nur die Zahl (`spanning-tree vlan 1 priority 24576`), nicht das Schlüsselwort. Das Makro wirkt einmalig: Ändert sich später die Root, passt es sich nicht an.

## Root Port und Pfadkosten

- Root Port = Port mit den niedrigsten **Root Path Cost** (Summe der Kosten aller Eingangsports entlang des Weges; jeder Switch addiert die Kosten seines Empfangsports zur empfangenen Root Path Cost).
- Tie-Breaker (Reihenfolge): 1. niedrigste Root Path Cost · 2. niedrigste **Sender-BID** · 3. niedrigste **Sender-Port-ID** · *(Ergänzung)* 4. niedrigste eigene Port-ID (nur bei Hub/zwei Links zum selben Segment).
- Port ID = Port-Priorität (Default 128) + Portnummer, Anzeige z. B. `128.2`.

| Bandbreite | Kurz (802.1D-1998) | Lang (802.1t / 802.1D-2004) |
|---|---|---|
| 4 Mbit/s | 250 | 5.000.000 |
| 10 Mbit/s | 100 | 2.000.000 |
| 16 Mbit/s | 62 | 1.250.000 |
| 100 Mbit/s | 19 | 200.000 |
| 1 Gbit/s | 4 | 20.000 |
| 2 Gbit/s | 3 | 10.000 |
| 10 Gbit/s | 2 | 2.000 |

- Höhere Bandbreite → niedrigere Kosten. Methode wählen: `spanning-tree pathcost method {short | long}`. **Auf Catalyst 9000 (IOS-XE) ist long der Default**; MST rechnet immer mit long. Alle Switches sollten dieselbe Methode verwenden.
- Kosten manuell (selten nötig): `spanning-tree vlan <liste> cost <wert>` auf dem eigenen Port. *(Ergänzung)* Wertebereich IOS-XE 1–200.000.000 (der Kurs nennt 1–20.000.000).

Kursbeispiel (Seite 40): SW2 ist Root. SW1 erreicht SW2 direkt (Kosten 100) oder über SW3 (100 + 100 = 200) → Root Port Eth0/0. SW3 hat zwei parallele Links zu SW2 (gleiche Kosten, gleiche Sender-BID) → entscheidend ist die Sender-Port-ID: 128.2 (SW2 Eth0/1) schlägt 128.4 (SW2 Eth0/3) → SW3-Root-Port ist der Port an SW2 Eth0/1.

## Designated Port

- Pro Segment derjenige Port, der die niedrigsten Root Path Cost anbietet; Tie-Breaker: niedrigere Sender-BID, dann niedrigere Sender-Port-ID.
- Auf der Root sind alle Ports designated.
- Kursbeispiel: Segment SW1–SW3: SW1 und SW3 haben beide Kosten 100 zur Root → SW1 hat die niedrigere BID (MAC aabb.cc00.4600 < aabb.cc00.5000) → SW1-Port designated, SW3-Port nondesignated (blocking). SW3 hat damit einen Root Port und zwei blockierte Ports.

## Port States (802.1D)

| State | BPDUs empfangen | BPDUs senden | MAC lernen | Daten forwarden | Dauer |
|---|---|---|---|---|---|
| Disabled | nein | nein | nein | nein | – |
| Blocking | ja | nein | nein | nein | bis Max Age 20 s |
| Listening | ja | ja | nein | nein | Forward Delay 15 s |
| Learning | ja | ja | ja | nein | Forward Delay 15 s |
| Forwarding | ja | ja | ja | ja | – |

- Ein Port startet disabled, nach dem Einschalten blocking; wird er Root oder Designated Port, geht er über listening (15 s) und learning (15 s) nach forwarding, sonst zurück nach blocking.
- Konvergenz bei direktem Ausfall ≈ 30 s (2 × Forward Delay), bei indirektem Ausfall bis zu 50 s (20 s Max Age + 30 s).

### Timer

| Timer | Default | Bereich | Bedeutung |
|---|---|---|---|
| Hello | 2 s | 1–10 s | BPDU-Intervall der Root |
| Forward Delay | 15 s | 4–30 s | Dauer von listening und learning |
| Max Age | 20 s | 6–40 s | wie lange eine gespeicherte BPDU gültig bleibt |

```
spanning-tree [vlan <id>] hello-time <s>
spanning-tree [vlan <id>] forward-time <s>
spanning-tree [vlan <id>] max-age <s>
```
Timer nur auf der Root ändern – die Werte stehen in deren BPDUs und werden übernommen.

## STP-Varianten

| Variante | Standard | Instanzen | Konvergenz | CPU/Speicher | Bemerkung |
|---|---|---|---|---|---|
| STP / CST | IEEE 802.1D | 1 für alle VLANs | langsam | gering | keine Lastverteilung, suboptimale Pfade |
| PVST+ | Cisco | 1 pro VLAN (802.1D) | langsam | hoch | per-VLAN-Root, Lastverteilung |
| RSTP | IEEE 802.1w | 1 | schnell | etwas über CST | Pfadproblem wie CST |
| Rapid PVST+ | Cisco | 1 pro VLAN (802.1w) | schnell | am höchsten | per-VLAN-Root + schnell |
| MSTP / MST | IEEE 802.1s (inspiriert von Cisco MISTP) | wenige, je VLAN-Gruppe | schnell (RSTP) | zwischen RSTP und Rapid PVST+ | Cisco-Implementierung „MST“ |

- Modus global: `spanning-tree mode {pvst | rapid-pvst | mst}`.
- **Default auf Catalyst 9000 mit IOS-XE: Rapid PVST+** (der Kurs nennt PVST+, siehe Kursfehler).
- `show spanning-tree` zeigt den Modus als „Spanning tree enabled protocol **ieee**“ (PVST+), „**rstp**“ (Rapid PVST+) bzw. „**mstp**“ (MST). `show spanning-tree summary` zeigt z. B. „Switch is in rapid-pvst mode“.
- PVST+ bildet eine Instanz pro VLAN (theoretisch bis 4094), jede mit eigenen BPDUs. *(Ergänzung)* Real begrenzt die Plattform die Zahl: Catalyst 9300 unterstützt 300 STP-Instanzen (ab IOS-XE 17.2.1, vorher 256).

## Discovery 4: STP tunen und RSTP

Topologie: SW1, SW2, SW3 im Dreieck; SW1 Eth0/0 – SW2 Eth0/2, SW1 Eth0/1 – SW3 Eth0/3, zwei parallele Links SW3 Eth0/1 – SW2 Eth0/1 und SW3 Eth0/2 – SW2 Eth0/3. Zwei Schleifen: SW1-SW2-SW3 und SW2-SW3. Alle Ports in IOL sind Ethernet (Kosten 100 short, Typ „Shr“).

1. Ausgangslage: alle Prioritäten 32769, SW1 Root wegen niedrigster MAC.
2. `spanning-tree vlan 1 root primary` auf SW2 → SW2 Root (Priorität 24577 = 24576 + 1); alle SW2-Ports Desg FWD.

```
SW2# show spanning-tree
VLAN0001
  Spanning tree enabled protocol ieee
  Root ID    Priority    24577
             Address     aabb.cc00.0200
             This bridge is the root
  Bridge ID  Priority    24577  (priority 24576 sys-id-ext 1)
Interface    Role Sts Cost  Prio.Nbr Type
Et0/1        Desg FWD 100   128.2    Shr
Et0/2        Desg FWD 100   128.3    Shr
Et0/3        Desg FWD 100   128.4    Shr
```
(Eigenes, korrigiertes Beispiel – im Kurs steht in der Bridge-ID-Zeile fälschlich 28673.)

3. Pfad manipulieren: SW3 Et0/1 ist Root Port (Sender-Port-ID 128.2 schlägt 128.4). Ziel: Et0/2 soll Root Port werden.
   - Variante A, lokal auf SW3: `interface Ethernet0/2` → `spanning-tree vlan 1 cost 16` (niedriger als 100) → Et0/2 wird Root Port, Et0/1 blockiert.
   - Variante B, auf dem Upstream-Switch SW2: Port-Priorität von SW2 Et0/3 senken (`spanning-tree vlan 1 port-priority 64`), dann gewinnt dessen Sender-Port-ID. Port-Priorität wirkt also **beim Nachbarn**, nicht lokal.
   - Port-Priorität: Default 128, *(Ergänzung)* IOS-XE 0–240 in 16er-Schritten (Kurs: 0–255). Niedriger = bevorzugt.
4. `debug spanning-tree events` + Shutdown des Root Ports: neuer Root Port → listening → (15 s) learning → (15 s) forwarding, insgesamt ~30 s, dazu TCN-Meldungen („sent Topology Change Notice on Et0/1“).
5. Migration auf RSTP: `spanning-tree mode rapid-pvst` auf allen Switches. Erneutes Shutdown: Konvergenz unter 1 s (Debug zeigt proposal/agreement und sync).

## RSTP (802.1w) im Detail

### Port States und Rollen

| 802.1D-State | RSTP-State |
|---|---|
| Disabled, Blocking, Listening | Discarding |
| Learning | Learning |
| Forwarding | Forwarding |

| RSTP-Rolle | Bedeutung | State |
|---|---|---|
| Root | bester Weg zur Root | forwarding |
| Designated | bester Port des Segments | forwarding |
| Alternate | Ersatz-Root-Port (alternativer Weg zur Root über einen anderen Switch) | discarding |
| Backup | Ersatz für einen Designated Port am selben Segment (zweiter Port desselben Switches, z. B. Hub) | discarding |
| Disabled | abgeschaltet | discarding |

### Schnelle Konvergenz
- Jede Bridge sendet im Hello-Takt eigene BPDUs (nicht nur Weiterleitung der Root-BPDU). Nach **3 verpassten Hellos (6 s)** gilt die Information als verloren.
- Proposal/Agreement (Handshake) auf Point-to-Point-Links: Ein neuer Designated Port sendet Proposal → Nachbar setzt alle Nonedge-Designated-Ports auf discarding (**Sync**) → Nachbar antwortet auf seinem Root Port mit Agreement → der Designated Port geht sofort in forwarding. Die Welle läuft Richtung Netzrand weiter.
- Alternate Ports übernehmen bei Ausfall des Root Ports sofort.
- Interoperabilität: Empfängt ein Port 802.1D-BPDUs, fällt er (pro Port) auf das alte Verfahren zurück.

### Topology Change bei RSTP
- TC nur dann, wenn ein **Nonedge-Port in forwarding wechselt**. Ein Linkverlust allein ist keine Topologieänderung (er schafft keinen neuen Weg; hat der Downstream-Switch einen Alternate Port, schaltet er diesen frei – das ist dann die TC).
- Der Auslöser selbst flutet BPDUs mit gesetztem TC-Bit über alle Nonedge-Designated-Ports und seinen Root Port (nicht erst die Root). Für eine Dauer von 2 × Hello.
- Empfänger einer TC-BPDU löschen die gelernten MACs auf allen Ports **außer dem Empfangsport** und fluten die TC ihrerseits weiter.
- Keine TCN-BPDU mehr, außer zur Kommunikation mit Legacy-Bridges.
- Edge-Ports (PortFast) lösen keine TC aus, ihre MAC-Einträge werden nicht geflusht.

### Link Types
| Link Type | Erkennung | Bedeutung |
|---|---|---|
| point-to-point | Full Duplex | direkt mit genau einem Switch verbunden → Rapid Transition möglich |
| shared | Half Duplex | geteiltes Medium (Hub) → klassische Timer |
| edge | PortFast konfiguriert | Endgerät, sofort forwarding |

- Link Type wird automatisch aus dem Duplex ermittelt, manuell: `spanning-tree link-type point-to-point`.
- Designated Ports brauchen P2P für die schnelle Transition. Root Ports nutzen den Link Type nicht (sie werden über Sync schnell); Alternate/Backup meist auch nicht.
- Anzeige in `show spanning-tree`, Spalte Type: `P2p`, `Shr`, `P2p Edge`.

## MST (802.1s)

### Motivation
- PVST+ erzeugt eine Instanz pro VLAN (theoretisch bis 4094) mit eigenen BPDUs, Root-Wahlen und Pfadberechnungen. Meist gibt es aber nur wenige sinnvolle logische Topologien (z. B. zwei Uplinks).
- MST bildet Gruppen von VLANs auf wenige Instanzen ab: Anzahl Instanzen = Anzahl gewünschter logischer Pfade. Beispiel: VLAN 1–500 über Pfad A, 501–1000 über Pfad B → 2 MST-Instanzen statt 1000 PVST+-Instanzen.
- Rechnet mit RSTP-Mechanismen (schnell), ist rückwärtskompatibel zu 802.1D und PVST+.
- Ausfälle in einer Instanz betreffen andere Instanzen nicht direkt.
- *(Ergänzung)* Anzahl Instanzen – die Cisco-Quellen widersprechen sich: Der Kurs und das TAC-Dokument „Troubleshoot MST on Catalyst 9000“ nennen 16 (IST + 15 MSTIs, MSTI 1–15). Der Cat9300 17.9 Configuration Guide nennt dagegen „up to 65 MST instances“ (IST + 64 MSTIs, wie IEEE 802.1s es maximal erlaubt). Die Zahl ist also plattform- bzw. releaseabhängig und sollte nicht als feste Prüfungszahl gelernt werden. Entscheidend für die Prüfung ist: wenige Instanzen, MST0 = IST immer vorhanden.

### Region
Switches gehören zur selben MST-Region, wenn drei Attribute übereinstimmen:
| Attribut | Größe |
|---|---|
| Konfigurationsname | 32 Byte (case-sensitive) |
| Revisionsnummer | 2 Byte (0–65535) |
| VLAN-zu-Instanz-Tabelle | 4096 Einträge |

- In der BPDU steht nur ein **Digest** (Hash) der Tabelle plus Name und Revision. Unterschiedlicher Digest → **Regionsgrenze**. Ebenfalls Grenze: Empfang von 802.1D-BPDUs (Legacy-Bridge) oder ein Designated Bridge in anderer Region.
- Die Revision wird nicht automatisch erhöht; bei Änderungen manuell hochzählen (und überall gleich setzen).
- Nach außen wirkt eine Region wie eine einzige virtuelle Bridge.
- *(Ergänzung)* `show spanning-tree mst configuration digest` zeigt auch den „Pre-std Digest“ (Cisco prestandard).

### IST und BPDUs
- **Instanz 0 = IST (Internal Spanning Tree)**: läuft auf allen Ports der Region, egal ob Access oder Trunk und egal welche VLANs der Port führt. Alle nicht zugeordneten VLANs landen in MST0.
- Es gibt **nur eine BPDU** (die IST-BPDU); Informationen der übrigen Instanzen (MSTIs) stecken als M-Records darin. Einzelinstanzen senden keine eigenen BPDUs.

### Best Practices und Fallstricke
- Trunks zwischen Switches, alle VLANs erlaubt, **kein manuelles VLAN-Pruning** – bei PVST+ würde Pruning auch die STP-Instanz des VLANs vom Link entfernen, bei MST läuft jede Instanz auf jedem Link weiter.
- Fall 1: Zwei Trunks, auf einem nur VLAN 10, auf dem anderen nur VLAN 20, beide VLANs in MST1 → MST1 blockiert einen der Links, und wenn es gerade der einzige Link mit VLAN 10 ist, ist VLAN 10 zwischen den Switches unterbrochen.
- Fall 2: Zwei Access-Links (VLAN 10 und VLAN 20) zwischen zwei Switches – gleiches Problem.
- Fall 3: Access-Links VLAN 10 (MST0) und VLAN 20 (MST1): Die IST läuft auf beiden Links, sieht eine Schleife und blockiert einen davon – trifft es den VLAN-10-Link, kommt VLAN 10 nicht mehr durch, obwohl keine echte Schleife existiert.
- Deshalb: keine Access-Links zwischen Switches, keine Nutz-VLANs auf die IST mappen.

### Konfiguration

```
SW(config)# spanning-tree mst configuration
SW(config-mst)# name CCNP
SW(config-mst)# revision 1
SW(config-mst)# instance 1 vlan 2,3
SW(config-mst)# instance 2 vlan 4,5
SW(config-mst)# show pending        ! geplante Konfiguration
SW(config-mst)# show current        ! aktive Konfiguration
SW(config-mst)# exit                ! übernimmt (auch: end); abort verwirft
SW(config)# spanning-tree mode mst  ! erst nach dem Mapping
SW(config)# spanning-tree mst 1 root primary
SW(config)# spanning-tree mst 2 root secondary
SW(config)# spanning-tree mst 1 priority 4096
SW(config-if)# spanning-tree mst 1 port-priority 64   ! 0–240, 16er-Schritte, Default 128
SW(config-if)# spanning-tree mst 1 cost 1000000       ! 1–200.000.000
```

Verifikation:
```
show spanning-tree summary              ! "Switch is in mst mode (IEEE Standard)", MST0/MST1/MST2
show spanning-tree mst configuration    ! Name, Revision, Instances configured, VLAN-Mapping
show spanning-tree mst configuration digest
show spanning-tree mst 1                ! Rollen/Kosten je Instanz
```

### Discovery 5
- Ausgangslage PVST+: VLAN 2–5; SW1 Root für VLAN 2/3, SW2 Root für VLAN 4/5 → SW3 nutzt für VLAN 2/3 den Uplink zu SW1, für 4/5 den zu SW2.
- Migration: Region „CCNP“, Revision 1, VLAN 2/3 → MST1, VLAN 4/5 → MST2. SW1: `mst 1 root primary`, `mst 2 root secondary`; SW2 umgekehrt. Ergebnis: gleiche Lastverteilung mit nur 3 Instanzen (MST0, 1, 2).
- MST-Kosten im IOL: Ethernet = 2.000.000 (long, 10 Mbit/s).
- Port-Priorität 64 für MST1 auf SW3 Et0/2 → Anzeige `64.3`; ändert die Rollen auf SW3 selbst nicht (wirkt nur beim Nachbarn).
- Kosten 1.000.000 auf SW3 Et0/2 (Richtung SW2) für MST1: Weg über SW2 kostet 1.000.000 + 2.000.000 (SW2→SW1) = 3.000.000 > 2.000.000 direkt → Et0/2 bleibt **Alternate**. Merke: Es zählt immer die Gesamtsumme bis zur Root.

## PortFast und BPDU Guard

### Problem
Ohne PortFast braucht ein Host-Port nach Link-up 30 s (listening + learning, plus ggf. bis 20 s blocking). Folge: DHCP-Timeouts, langsame Anmeldung. An Host-Ports kann aber keine Schleife entstehen.

### PortFast
- Port geht **sofort in forwarding**, überspringt listening/learning. Nur auf Access-Ports zu Endgeräten (PCs, Server, Drucker).
- An einem PortFast-Port sollten nie BPDUs ankommen; tun sie es doch, hängt ein Switch daran (z. B. Nutzer steckt einen Mini-Switch an zwei Dosen → Schleife).
- PortFast-Ports erzeugen keine Topology Changes.
- `switchport host` = Makro: Access-Modus + PortFast + kein EtherChannel.

### BPDU Guard
- Empfängt ein Port mit BPDU Guard eine BPDU, wird er **err-disabled** (abgeschaltet). Sichert die STP-Domänengrenze.
- Logmeldung im Kurs (alte CatOS-Form): `%SPANTREE-2-RX_PORTFAST: Received BPDU on PortFast enable port. Disabling 2/1`. *(Ergänzung)* IOS-XE: `%SPANTREE-2-BLOCK_BPDUGUARD: Received BPDU on port GigabitEthernet1/0/5 with BPDU Guard enabled. Disabling port.` und `%PM-4-ERR_DISABLE: bpduguard error detected on Gi1/0/5, putting Gi1/0/5 in err-disable state` (auf Catalyst 6500 mit `-SP-` im Facility-Namen, z. B. `%PM-SP-4-ERR_DISABLE`).
- Erholung: `shutdown`/`no shutdown` oder *(Ergänzung)* `errdisable recovery cause bpduguard` (Recovery ist per Default aus; nach Aktivierung Default-Intervall 300 s, änderbar mit `errdisable recovery interval <s>`).

```
interface Gi1/0/5
 spanning-tree portfast
 spanning-tree bpduguard enable
!
spanning-tree portfast default            ! PortFast auf allen Nicht-Trunk-Ports
spanning-tree portfast bpduguard default  ! BPDU Guard auf allen operativen PortFast-Ports
```

Verifikation:
- `show running-config interface Gi1/0/5` – nur Interface-Befehle; globale Defaults stehen dort nicht.
- `show spanning-tree summary` – „Portfast Default is enabled“, „PortFast BPDU Guard Default is enabled“.
- `show spanning-tree interface Gi1/0/5 portfast` – PortFast-Status des Ports.
- *(Ergänzung)* `show interfaces status err-disabled`, `show errdisable recovery`.
- Hinweis: PortFast an Switch-Ports kann Schleifen erzeugen; BPDU Filter existiert, wird aber nicht empfohlen.

### *(Ergänzung)* BPDU Filter
- Global `spanning-tree portfast bpdufilter default`: PortFast-Ports senden keine BPDUs; empfängt ein solcher Port doch eine BPDU, verliert er PortFast und Filter und nimmt normal an STP teil.
- Interface `spanning-tree bpdufilter enable`: Port sendet und verarbeitet keine BPDUs → STP ist dort praktisch aus, Schleifengefahr.

## Root Guard

- Angriff: Ein Angreifer (oder falsch konfigurierter Switch) sendet BPDUs mit besserer BID (z. B. Priorität 0 und kleinere MAC), wird Root, und der Verkehr zwischen den Switches läuft über ihn → Man-in-the-Middle, Schleifen, suboptimale Pfade (betrifft Vertraulichkeit, Integrität, Verfügbarkeit).
- **Root Guard** (`spanning-tree guard root`, Interface): Empfängt der Port eine **superiore BPDU**, wird er **root-inconsistent** (entspricht listening, kein Datenverkehr). Die BPDU wird ignoriert, die bestehende Root bleibt.
- Erholung automatisch, sobald keine superioren BPDUs mehr eintreffen.
- Einsatz: auf Designated Ports Richtung Switches, die nie Root werden dürfen (Distribution → Access), nie auf Root Ports.
- *(Ergänzung)* `show spanning-tree inconsistentports` listet root- und loop-inconsistente Ports. Root Guard und Loop Guard nicht gleichzeitig auf demselben Port.

## *(Ergänzung)* Loop Guard

- `spanning-tree guard loop` (Interface) bzw. `spanning-tree loopguard default` (global).
- Schützt Root- und Alternate-Ports: Bleiben die BPDUs aus (z. B. unidirektionaler Link), würde der Port nach Max Age designated und forwarding → Schleife. Loop Guard setzt ihn stattdessen in **loop-inconsistent** (blockiert).
- Erholung automatisch, sobald wieder BPDUs ankommen.

## Troubleshooting-Checkliste

- Root falsch? `show spanning-tree root` / `show spanning-tree vlan X` – Root ID vs. Bridge ID, Priorität (+ sys-id-ext), MAC.
- Unerwarteter Root Port? Kosten summieren (pathcost-Methode prüfen, Mischung short/long vermeiden), dann Sender-BID, dann Sender-Port-ID des Nachbarn.
- Langsame Konvergenz? Modus (ieee vs. rstp), Link Type (Shr statt P2p bei Half Duplex), fehlendes PortFast an Hosts.
- Port err-disabled? BPDU Guard → `show interfaces status err-disabled`, Ursache beseitigen, shut/no shut.
- MST-Probleme: Name/Revision/Mapping auf allen Switches vergleichen (`show spanning-tree mst configuration digest`), Pruning/Access-Links zwischen Switches vermeiden.
- Häufiges MAC-Flushing/TC: `show spanning-tree detail` (Anzahl TCs, „last change occurred … from“), Host-Ports ohne PortFast finden.

## Fehler/Ungenauigkeiten im Kurs

1. **S. 41, Default-Modus:** Der Kurs nennt PVST+ als Default auf Catalyst-Switches. Auf Catalyst 9000 mit IOS-XE ist **Rapid PVST+** der Default. Quelle: Cat9300 17.9 Layer 2 Config Guide, „Configuring Spanning Tree Protocol“ (Default-Einstellungen).
2. **S. 40/42, Pfadkosten:** Der Kurs stellt die kurze Methode (802.1D-1998) in den Vordergrund (Lab: Kosten 100). Auf Catalyst 9000 ist **long (802.1t/802.1D-2004) der Default** (`spanning-tree pathcost method long`). Quelle: wie 1.
3. **S. 42, Wertebereiche:** Kurs: Port-Priorität 0–255, Kosten 1–20.000.000. IOS-XE: Port-Priorität **0–240 in 16er-Schritten**, Kosten **1–200.000.000**. Quelle: wie 1 und Cat9300 MSTP-Kapitel.
4. **S. 42, show-Ausgabe nach `root primary`:** Root ID zeigt 24577, die Bridge-ID-Zeile desselben (Root-)Switches aber 28673 (priority 28672). Auf der Root müssen beide Werte gleich sein (24577 / priority 24576 sys-id-ext 1).
5. **S. 45, Logmeldung BPDU Guard:** Die gezeigte Meldung (`%SPANTREE-2-RX_PORTFAST … Disabling 2/1` mit Port-Schreibweise 2/1) stammt aus CatOS. IOS-XE meldet `%SPANTREE-2-BLOCK_BPDUGUARD` und `%PM-4-ERR_DISABLE: bpduguard error detected`. Quelle: Cisco Tech Note 69980 „Errdisable Port State Error Recovery“.
6. **S. 41, MST-Instanzen:** „bis zu 16 Instanzen“ ist nur ein Stand. Das TAC-Dokument 218351 („Troubleshoot MST on Catalyst 9000“) nennt ebenfalls 16 (IST + 15 MSTIs). Der Cat9300 17.9 Configuration Guide („Configuring MSTP“) nennt aber 65 MST-Instanzen. Die Zahl ist plattform- und releaseabhängig, deshalb nicht als feste Zahl lernen. Quellen: https://www.cisco.com/c/en/us/support/docs/lan-switching/stp/218351-troubleshoot-mst-on-catalyst-9000-switch.html und https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-9/configuration_guide/lyr2/b_179_lyr2_9300_cg/configuring_multiple_spanning_tree_protocol.html
7. **S. 44 (Discovery 5):** Die gezeigte `show spanning-tree mst 1`-Ausgabe enthält Ports Et1/0 und Et1/1, die in der Topologie nicht vorkommen (Platzhalter/Vorlage). Außerdem wird `port-priority 64` auf SW3 konfiguriert, um den Weg zu beeinflussen – lokal hat das auf SW3 keine Wirkung, die Port-Priorität wirkt nur beim Nachbarn.

## Bilder

- `bilder/05-stp/01-loops.svg` – Bridging Loop zwischen zwei Switches mit den drei Folgen (Broadcast-Sturm, Mehrfachzustellung, MAC-Flapping) und der STP-Lösung (ein Port blockiert).
- `bilder/05-stp/02-bpdu-bid.svg` – BPDU-Felder als Leiste plus Aufbau der Bridge ID (4 Bit Priorität + 12 Bit sys-id-ext + MAC) mit Rechenbeispiel.
- `bilder/05-stp/03-rollen.svg` – Kurs-Dreieck SW1/SW2/SW3 mit Kosten, Port-IDs und den daraus gewählten Rollen (Root, Desg, Nondesg).
- `bilder/05-stp/04-states.svg` – Zustandsfolge 802.1D (Blocking → Listening → Learning → Forwarding) mit Timern und RSTP-Zuordnung.
- `bilder/05-stp/05-tc-ablauf.svg` – Topology Change bei 802.1D (TCN → TCA → TC von der Root) im Vergleich zu RSTP (Initiator flutet TC selbst).
- `bilder/05-stp/06-rstp-sync.svg` – Proposal/Agreement mit Sync auf Point-to-Point-Links und die Link Types (P2p, Shared, Edge).
- `bilder/05-stp/07-pfad-tuning.svg` – Discovery 4: Root Port über Kosten (lokal) oder Port-Priorität (beim Nachbarn) beeinflussen.
- `bilder/05-stp/08-mst-region.svg` – MST-Region (Name, Revision, Digest), IST/MST1/MST2 mit Lastverteilung wie in Discovery 5.
- `bilder/05-stp/09-mst-falle.svg` – MST-Fallstrick: Access-Links bzw. gepruente Trunks zwischen Switches, IST blockiert den einzigen Weg für ein VLAN.
- `bilder/05-stp/10-guards.svg` – Wo PortFast/BPDU Guard, Root Guard und Loop Guard im Campus sitzen und wie sie reagieren.
