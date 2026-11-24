# Introducing QoS

Quelle: ENCOR 1.4.10 Student Guide, Seiten 222–225 (221 Intro, 226 Summary Challenge und 227 Answer Key nicht ausgewertet)

Topics: ENCOR-1.4 (Interpret QoS configurations: classification, marking, policing, shaping, queuing, congestion avoidance)

Ergänzungen, die nicht im Kurs stehen (QoS-Modelle Best Effort/IntServ/DiffServ, ToS-Byte-Aufbau und Umrechnungen, AF-Formel, Token Bucket, WRED-Schwellen, MQC-Detailsyntax, `show policy-map interface`-Ausgaben, Catalyst-Trust-Verhalten), sind mit *(Ergänzung)* markiert und stammen aus RFC 791/2474/2475/2597/3246/3168/2697/2698/4594, ITU-T G.114 und Cisco-IOS-XE-QoS-Konfigurationsleitfäden.

---

## 1. Einfluss von Anwendungen auf das Netz (S. 222)

### Anwendungsklassen
| Klasse | Beispiel | Bandbreite | Verzögerung |
|---|---|---|---|
| Batch | FTP, TFTP (Dateitransfer) | wichtig, aber nicht kritisch – Transfer wird irgendwann fertig | unkritisch |
| Interaktiv | Inventarabfrage, Datenbank-Frontend, Terminal Services | weniger kritisch | Antwortzeit wichtig, aber nicht kritisch |
| Echtzeit | VoIP, Videokonferenz | kritisch | kritisch; verlorene Daten werden **nicht** neu übertragen |

Echtzeitanwendungen brauchen ausreichende Bandbreite **und** QoS, weil Verzögerung und Verlust die Qualität direkt zerstören (kein Retransmit über RTP/UDP).

### IPv4-Header
- Quell- und Zieladresse je 32 Bit.
- Weitere Felder: Version, IHL (Header-Länge), **Type of Service / Service Type** (QoS-Information), Total Length, Identification, Flags, Fragment Offset, TTL, Protocol, Header Checksum, Options, Padding (Header endet auf 32-Bit-Grenze).
- Für QoS relevant ist das **ToS-Byte** (8 Bit). In IPv6 heißt dasselbe Feld **Traffic Class**.

### Verkehrseigenschaften
| | Daten | Voice | Video (interaktiv) |
|---|---|---|---|
| Charakter | bursty, „greedy", unvorhersehbar | glatt, vorhersehbar, konstante Rate, kleine Pakete | bursty, „greedy", variable Paketgrößen und Rate |
| Verlust | unempfindlich (TCP-Retransmit) | empfindlich (UDP) | empfindlich (UDP) |
| Verzögerung | unempfindlich (je nach Anwendung) | empfindlich | empfindlich |
| One-Way-Anforderung | – | Latenz ≤ 150 ms, Jitter ≤ 30 ms, Verlust ≤ 1 %, 30–128 kbps | Latenz ≤ 150 ms, Jitter ≤ 30 ms, Verlust ≤ 0,1–1 %, 384 kbps bis > 20 Mbps |

- Daten: nicht echtzeitfähig. Manche Daten sind kaum interaktiv (E-Mail), andere interaktiv und verzögerungsempfindlich (Datenbank). Zusätzlich gibt es eine **geschäftliche Wichtigkeit** (z. B. Live-E-Learning ist für einen E-Learning-Anbieter mission-critical, für einen Fertigungsbetrieb nur wichtig).
- Interaktives Video hat dieselben Delay-/Jitter-/Verlust-Anforderungen wie Voice, aber andere (höhere, variablere) Bandbreite. Faustregel für Overhead: **20 % mehr Bandbreite** einplanen als die Nutzdaten brauchen.
- **Streaming-Video** (z. B. On-Demand-Schulungsvideo): Verlust ≤ 5 %, Verzögerung ≤ 4–5 s – der Player puffert („Buffering 50 %"), um Laufzeitschwankungen auszugleichen.
- Nicht vergessen: netzeigener Verkehr – Routing-Protokolle (Größe/Frequenz abhängig von Protokoll und Stabilität) und Management (SNMP).
- *(Ergänzung)* ITU-T G.114 empfiehlt für Sprache ≤ 150 ms Einweg-Verzögerung (Mund-zu-Ohr); bis 400 ms gilt als eingeschränkt akzeptabel.

### *(Ergänzung)* Verzögerungsarten und Jitter
- **Serialization Delay**: Zeit, ein Paket auf das Medium zu legen = Paketgröße in Bit / Linkrate (1500 Byte auf 1 Mbps = 12 ms; auf 1 Gbps = 12 µs).
- **Propagation Delay**: Signallaufzeit, abhängig von der Entfernung (≈ 5 µs/km in Glasfaser), nicht durch QoS beeinflussbar.
- **Queuing Delay**: Wartezeit in Ausgangspuffern – das ist die Komponente, die QoS steuert.
- **Processing/Forwarding Delay**: Zeit für die Weiterleitungsentscheidung.
- **Jitter** = Schwankung der Verzögerung zwischen aufeinanderfolgenden Paketen; Endgeräte gleichen ihn mit einem **De-Jitter-Puffer** aus (erhöht aber die Gesamtverzögerung).
- Mehr Bandbreite reduziert Serialization- und Queuing-Delay, ändert aber nichts an der Propagation.

## 2. Warum QoS? (S. 223)
- Zweck: **Engpässe (Congestion) managen**, um das Benutzererlebnis zu maximieren. Nicht alle Pakete sind gleich wichtig.
- Bei Stau werden weniger wichtige Pakete **verzögert oder verworfen** zugunsten verzögerungsempfindlicher, geschäftswichtiger Pakete. Pakete verzögerungsempfindlicher Sessions „überholen" Warteschlangen anderer Sessions.
- Wenn Puffer überlaufen, trifft der Drop Sessions, die sich erholen können (TCP) oder deren Verlust geschäftlich wenig schadet.
- QoS greift nur, wenn es einen Engpass gibt; ohne Stau werden Pakete sofort gesendet.
- **QoS vs. QoE**: QoS = messbare technische Werte (Jitter, Latenz, Bandbreite, Verlust). QoE = subjektive Wahrnehmung des Nutzers. QoS dient dazu, QoE zu maximieren.
- QoS nur auf einem Teilstück ist fast wertlos: Die QoE entspricht dem **schlechtesten Segment** des Pfads → QoS muss **Ende-zu-Ende** umgesetzt werden.

### QoS-Werkzeugkategorien
1. **Classification and Marking**: Traffic einer Klasse zuordnen und das Ergebnis im Header festhalten. Klassifizierung so selten wie möglich (kostet Ressourcen) → einmal am Ingress-Rand markieren; an Übergabepunkten in andere Netze wird oft neu klassifiziert/re-markiert.
2. **Policing, Shaping, Re-Marking**: Klassen bekommen Anteile an Ressourcen; Überschreitung wird verworfen (Policing), verzögert (Shaping) oder herabmarkiert (Markdown).
3. **Congestion Management / Scheduling**: Bei Überlast wird gepuffert (Queues) und entschieden, welche Queue als nächste sendet. Verzögerungsempfindlicher Traffic, für den es keine garantierte verzögerungsfreie Bandbreite gibt, ist verworfen oft besser dran als verspätet.
4. **Link-spezifische Tools**: z. B. Fragmentierung (und Interleaving) auf langsamen WAN-Links. *(Ergänzung: LFI/MLPPP, cRTP-Header-Kompression.)*

### *(Ergänzung)* QoS-Modelle
| Modell | Prinzip | Vor-/Nachteile |
|---|---|---|
| **Best Effort** | keine Unterscheidung, FIFO | einfach, skaliert, aber keine Garantien |
| **IntServ** (RFC 1633) | Anwendung reserviert Ressourcen **pro Flow** Ende-zu-Ende per **RSVP** (Signalisierung), jeder Router hält Zustand pro Flow | harte Garantien, aber schlecht skalierbar (State pro Flow auf jedem Hop) |
| **DiffServ** (RFC 2474/2475) | Pakete werden in Klassen markiert (DSCP); jeder Hop behandelt die Klasse nach einem **Per-Hop Behavior (PHB)**, ohne Signalisierung | skaliert sehr gut, Standard in Enterprise und Provider; Garantie nur relativ (durch Provisionierung) |

## 3. Trust Boundary (S. 223)
- **Untrusted Domain**: Geräte, die der Admin nicht verwaltet bzw. auf die Nutzer zugreifen (PCs, Drucker). Markierungen von dort werden ignoriert/überschrieben, damit Nutzer sich nicht selbst Priorität geben.
- **Trusted Domain**: nur vom Admin verwaltete Geräte (Switches, Router).
- **Trust Boundary**: Rand der Trusted Domain – hier wird klassifiziert und markiert (oder vorhandene Markierung akzeptiert). Beispiele: IP-Phone, Access-Switch-Port, Übergang Enterprise ↔ Service Provider, Übergänge zwischen Behörden/Abteilungen/Schulen.
- Im Campus liegt die Trust Boundary fast immer am **Edge-/Access-Switch** (bzw. im IP-Phone, wenn der Switch dem Phone vertraut).
- Best Practice: so nah an der Quelle wie möglich klassifizieren und markieren.
- *(Ergänzung)* Catalyst 9000 (IOS XE) vertraut eingehenden DSCP/CoS-Markierungen standardmäßig; ältere Catalyst-Switches mit `mls qos` haben Ports standardmäßig untrusted (Markierung → 0). **Conditional Trust**: `trust device cisco-phone` – der Port vertraut nur, wenn per CDP ein Cisco-Phone erkannt wird; das Phone markiert Voice (EF/CoS 5) und setzt den PC-Verkehr am PC-Port zurück.

## 4. Classification and Marking (S. 224)
- **Classifier**: untersucht Felder im Paket, ordnet es einer Klasse zu und leitet es an Policy-Mechanismen (Marking, Queuing, Policing, Shaping) weiter.
- **Marker**: schreibt einen Wert in Header von Frame/Paket/Zelle/Label, um die Klassifizierungsentscheidung zu konservieren – nachfolgende Geräte müssen nicht erneut aufwendig klassifizieren.
- Layer-3-Markierung (IPP/DSCP) ist am weitesten verbreitet, weil sie **Ende-zu-Ende** gilt (L2-Markierung geht am Router verloren); L3 lässt sich leicht auf L2 abbilden.

### Markierungsfelder
| Feld | Ort | Bits |
|---|---|---|
| **CoS** (802.1p, PCP) | 802.1Q-Tag (Ethernet) | 3 → 0–7 |
| **IP Precedence** | ToS-Byte, oberste 3 Bit | 3 → 0–7 |
| **DSCP** | ToS-Byte/Traffic Class, oberste 6 Bit | 6 → 0–63 |
| **Class Selector (CS)** | DSCP-Werte, deren untere 3 Bit 0 sind = IPP-kompatibel | 3 |
| **TID** | QoS Control Field des 802.11-Frames | 3 (ähnlich, aber nicht exakt wie CoS) |
| *(Ergänzung)* MPLS EXP / TC | MPLS-Label | 3 |

- DSCP ist rückwärtskompatibel zu IP Precedence (CS-Werte). Wechsel von IPP zu DSCP, weil 8 Werte zu wenig sind.
- Weitere Markierungsmöglichkeiten: GRE, MPLS, IPsec (*Ergänzung: der ToS-Wert wird standardmäßig in den äußeren Tunnel-Header kopiert*).
- *(Ergänzung)* CoS existiert nur in getaggten Frames (802.1Q oder Priority-Tag VLAN 0) – auf einem Access-Port ohne Tag gibt es keine CoS.

### *(Ergänzung)* Aufbau des ToS-Bytes
```
Bit:   7   6   5   4   3   2   1   0
      [ IP Precedence ][ ToS (alt) ][ 0 ]   RFC 791/1349
      [        DSCP (6 Bit)        ][ECN]   RFC 2474 / 3168
```
- ToS-Byte-Wert (bei ECN = 0) = DSCP × 4. IPP = DSCP ÷ 8 (abgerundet, = obere 3 Bit).
- Beispiele: EF 46 = 101110 → ToS 0xB8 (184), IPP 5. AF41 34 = 100010 → 0x88 (136), IPP 4. CS6 48 = 110000 → 0xC0 (192). AF31 26 → 0x68 (104). CS3 24 → 0x60 (96). AF21 18 → 0x48 (72). AF11 10 → 0x28 (40). CS1 8 → 0x20 (32).
- ECN (2 Bit): 00 Not-ECT, 01/10 ECT, 11 CE (Congestion Experienced).

### *(Ergänzung)* DiffServ-PHBs
- **Default / DF** (DSCP 0): Best Effort.
- **EF** – Expedited Forwarding (RFC 3246), DSCP **46** (101110): niedrige Latenz, Jitter und Verlust → Voice, gehört in die Priority Queue.
- **AF** – Assured Forwarding (RFC 2597): 4 Klassen × 3 Drop-Precedences. **AFxy: DSCP = 8x + 2y**, Binär `xxx yy0`. x = Klasse 1–4 (höher = wichtigere Klasse in Cisco-Designs), **y = Drop-Precedence 1–3: höheres y = höhere Verwerfwahrscheinlichkeit** innerhalb derselben Klasse (AF13 wird vor AF12 vor AF11 verworfen).

| | Drop low (y=1) | medium (y=2) | high (y=3) |
|---|---|---|---|
| AF1 | AF11 = 10 | AF12 = 12 | AF13 = 14 |
| AF2 | AF21 = 18 | AF22 = 20 | AF23 = 22 |
| AF3 | AF31 = 26 | AF32 = 28 | AF33 = 30 |
| AF4 | AF41 = 34 | AF42 = 36 | AF43 = 38 |

- **CSx** = 8x: CS1 8, CS2 16, CS3 24, CS4 32, CS5 40, CS6 48, CS7 56.

### Markierungsempfehlungen (Kurstabelle, entspricht Cisco QoS Baseline / RFC 4594 grob)
| Anwendung | IPP | PHB | DSCP | CoS |
|---|---|---|---|---|
| Routing | 6 | CS6 | 48 | 6 |
| Voice | 5 | EF | 46 | 5 |
| Video Conferencing | 4 | AF41 | 34 | 4 |
| Streaming Video | 4 | CS4 | 32 | 4 |
| Mission-Critical Data | 3 | AF31 | 26 | 3 |
| Call Signaling | 3 | CS3 | 24 | 3 |
| Transactional Data | 2 | AF21 | 18 | 2 |
| Network Management | 2 | CS2 | 16 | 2 |
| Bulk Data | 1 | AF11 | 10 | 1 |
| Scavenger | 1 | CS1 | 8 | 1 |
| Best Effort | 0 | 0 (DF) | 0 | 0 |

- Scavenger (CS1) = „weniger als Best Effort" (z. B. P2P, private Videos).

### Klassifizierungswege
1. **Markings**: vorhandene L2/L3-Markierung (CoS, IPP, DSCP).
2. **Addressing**: Ein-/Ausgangsinterface, L2-Zieladresse, L3-Quell-/Zieladresse, L4-Ports. IP-Adresse → Gerätegruppe; Port → Verkehrstyp.
3. **Application Signatures**: Inhalt der Payload = **Deep Packet Inspection** (NBAR).
- **MQC** (Modular QoS CLI): plattformunabhängige Konfigurationsschnittstelle; abstrahiert das Verhalten von der Plattform-Implementierung.

### NBAR
- Network Based Application Recognition: Klassifizierung auf **Layer 4–7** per DPI; CPU-intensiver als Klassifizierung nach Markierung/Adressen/ACLs.
- Nötig, wenn Ports nicht reichen (z. B. P2P-Anwendungen mit dynamisch ausgehandelten Ports).
- Erkennung gegen **PDLM** (Packet Description Language Module) = Signaturdatenbank (*Ergänzung: in NBAR2 als Protocol Packs*).
- Modi: **Passive** (Statistiken pro Protokoll/Interface, bidirektional: Bitrate, Pakete, Bytes – *Ergänzung: `ip nbar protocol-discovery`*), **Active** (klassifiziert für QoS-Policies – *Ergänzung: `match protocol <name>` in einer class-map*).
- **NBAR2** (Next Generation NBAR): sehr viele Protokolle, auch Nicht-TCP/UDP, statische und dynamische Ports.

## 5. Policing, Shaping, Re-Marking (S. 224)
| | Policer | Shaper |
|---|---|---|
| Reaktion auf Überschreitung | **drop** oder **re-mark** (meist auf Klasse mit höherer Drop-Wahrscheinlichkeit) | **puffern** und später senden (glätten) |
| Verzögerung/Jitter | keine | ja (Queuing-Delay) |
| TCP-Retransmits | viele (Drops) | weniger |
| Typischer Ort | **Ingress** (früh verwerfen spart Ressourcen), auch Egress möglich | **Egress**, Enterprise → Provider-Link (auf CIR des Vertrags, damit der Provider-Policer nicht verwirft) |
| Puffer nötig | nein | ja |

- *(Ergänzung)* Shaping ist nur **outbound** möglich; Policing ein- und ausgehend.
- Echtzeit-Verkehr (Voice/Video) mit Policing/Shaping zu regulieren ist meist kontraproduktiv → besser **Call Admission Control (CAC)**: hält überschüssige Anrufe vom Netz fern, schützt Voice vor Voice. Policing/Shaping eignen sich vor allem für TCP-Daten.

### *(Ergänzung)* Token Bucket
- **CIR** (Committed Information Rate, bps), **Bc** (Committed Burst, Bits pro Intervall), **Tc** (Zeitintervall): **CIR = Bc / Tc** bzw. Tc = Bc / CIR.
  - Beispiel: CIR 8 Mbps, Tc 10 ms → Bc = 80 000 Bit = 10 000 Byte. CIR 64 kbps, Bc 8000 Bit → Tc 125 ms.
- **Be** (Excess Burst): zusätzliche Tokens, die nach Leerlaufphasen angespart werden dürfen.
- Shaper: Linkrate kann höher sein als CIR; der Shaper sendet pro Tc maximal Bc (+Be) Bits mit Linkrate und pausiert dann → Ø-Rate = CIR.
- Policer-Varianten:
  - Single-rate two-color: conform / exceed.
  - Single-rate three-color (RFC 2697): CIR, Bc, Be → conform / exceed / violate.
  - Two-rate three-color (RFC 2698): CIR und **PIR** → conform (≤ CIR) / exceed (zwischen CIR und PIR) / violate (> PIR). Kursabbildung: Marker setzt AF11 (conform), AF12 (exceed), AF13 (violate).
```
policy-map POLICE-IN
 class BULK
  police cir 2000000 conform-action transmit exceed-action set-dscp-transmit af12 violate-action drop
!
policy-map SHAPE-WAN
 class class-default
  shape average 50000000
  service-policy QUEUING       ! hierarchische Policy: Shaper (Parent) + Queuing (Child)
```

## 6. Congestion Management (S. 224)
- Stau entsteht, wenn Pakete schneller eintreffen, als sie den Ausgang verlassen können (Speed-Mismatch, Aggregation).
- **Queuing** (Puffern) ordnet Pakete in Ausgangspuffer und ist nur **bei Stau** aktiv. **Scheduling** entscheidet, welches Paket als nächstes gesendet wird – passiert immer.
- Scheduler-Grundtypen:
  - **Strict Priority**: niedrigere Queues nur, wenn höhere leer → Gefahr der **Starvation**.
  - **Round-Robin**: feste Reihenfolge, keine Starvation, aber Echtzeitverkehr leidet unter Verzögerung.
  - **Weighted Fair**: gewichtete Queues, keine Starvation; aber keine Bandbreitengarantie (Anteil pro Flow schwankt mit Zahl und Gewicht der Flows).
- Queuing-Ebenen: Layer 3 (komplex, MQC), Layer 2 (bei manchen Interfacetypen), Layer 1 **Tx-Ring** (Hardware-FIFO). Erst wenn der Tx-Ring voll ist, kommen die Software-Queues zum Zug → dann wird QoS (Queuing) aktiv.

### Queuing-Verfahren
| Verfahren | Funktion | Bewertung |
|---|---|---|
| **FIFO** | eine Queue, Reihenfolge der Ankunft | keine Differenzierung |
| **PQ** (Priority Queuing) | 4 Queues (*high/medium/normal/low*), strikt | Starvation niedriger Queues |
| **CQ** (Custom Queuing) | 16 Queues, Round-Robin (*byte count*) | Bandbreitenanteile, aber keine Strict Priority |
| **WFQ** | teilt Bandbreite durch Zahl der Flows (*Gewicht nach IP Precedence*) | fair, keine Garantie pro Flow |
| **CBWFQ** | Klassen (MQC) mit garantierter Mindestbandbreite + Fairness | keine Latenzgarantie → nur Daten |
| **LLQ** | CBWFQ + **Strict-Priority-Queue** | Latenz- und Bandbreitengarantie → Daten + Echtzeit (Empfehlung) |

- *(Ergänzung)* Die LLQ-Priority-Queue ist bei Stau **implizit gepolicet** auf die konfigurierte Rate (`priority 1000` / `priority percent 30`) – überschüssiger Priority-Traffic wird verworfen, damit die anderen Klassen nicht verhungern. Ohne Stau darf die Klasse mehr senden. Empfehlung (Cisco Design Guides): Priority-Queue ≤ ca. 33 % der Linkbandbreite.
- *(Ergänzung)* `bandwidth` (kbps), `bandwidth percent` (Anteil der Interfacebandbreite) und `bandwidth remaining percent` (Anteil der nach der Priority-Queue verbleibenden Bandbreite) garantieren Mindestanteile bei Stau; ungenutzte Bandbreite dürfen andere Klassen verwenden.
- *(Ergänzung)* `fair-queue` in class-default = flow-basiertes WFQ innerhalb der Default-Klasse.

## 7. Congestion Avoidance (S. 224)
- Queues sind endlich. **Tail Drop**: bei voller Queue werden ankommende Pakete verworfen (Default-Verhalten).
- Queuing verwaltet den **Anfang** der Queue, Congestion Avoidance das **Ende**.
- Problem bei TCP: Tail Drop trifft viele Flows gleichzeitig → alle reduzieren gleichzeitig (Slow Start/Congestion Window) und steigern wieder gleichzeitig → **TCP Global Synchronization**, Wellenmuster, schlecht genutzte Bandbreite.
- **RED** (Random Early Detection): überwacht die Queue-Tiefe und verwirft zufällig einzelne Pakete, sobald eine Mindestschwelle überschritten ist → einzelne Flows bremsen zeitversetzt.
- **WRED**: RED mit Gewichtung nach IPP/DSCP – wichtigere Pakete werden seltener verworfen. Cisco IOS implementiert RED als WRED.
- *(Ergänzung)* WRED-Profil pro Wert: **Minimum Threshold** (darunter kein Drop), **Maximum Threshold** (darüber Tail Drop aller Pakete dieses Werts), **Mark Probability Denominator** (Drop-Wahrscheinlichkeit an der Max-Schwelle = 1/MPD; Default 10 → 10 %). Dazwischen steigt die Wahrscheinlichkeit linear. Für AF-Klassen: AFx3 hat die niedrigste Min-Schwelle (wird zuerst verworfen).
- *(Ergänzung)* WRED wirkt nur auf Flows, die auf Verlust reagieren (TCP). Für Voice (UDP, Priority Queue) ist WRED sinnlos. Befehle: `random-detect` (IPP-basiert), `random-detect dscp-based`, `random-detect ecn` (markiert CE statt zu verwerfen, wenn ECN-fähig).

## 8. QoS-Policy definieren und interpretieren (S. 225)
### Drei Schritte (MQC)
1. **class-map** – „Welcher Traffic?" (Klassifizierung).
2. **policy-map** – „Was passiert mit dem Traffic?" (Aktionen pro Klasse).
3. **service-policy** – „Wo wird es angewendet?" (Interface + Richtung).

### Implementierungsmethoden
| Methode | Merkmale |
|---|---|
| Legacy CLI | jedes Interface einzeln, zeitaufwendig, fehleranfällig |
| MQC | modular, Policy auf viele Interfaces anwendbar, beste Methode für Feintuning |
| Cisco AutoQoS | schnellste Methode, erzeugt automatisch eine empfohlene Konfiguration (*Ergänzung: z. B. `auto qos voip trust`, auf Catalyst `auto qos trust dscp`*) |
| Cisco SDM QoS Wizard | GUI für einfache Konfigurationen (*veraltet, End-of-Life*) |

### Traffic Class
- Elemente: Name, eine oder mehrere `match`-Anweisungen, und bei mehreren Matches die Auswertungslogik: *(Ergänzung)* `match-all` (Default, UND) oder `match-any` (ODER).
- Pakete, die keine Klasse treffen, landen in **class-default** (existiert immer).
- *(Ergänzung)* Klassen werden in der Reihenfolge der policy-map geprüft; das Paket kommt in die **erste** passende Klasse.

### Kurs-Beispiel (Office-Router, langsamer WAN-Link zur Zentrale)
```
class-map VoIP
 match access-group 100
class-map Application
 match access-group 101
!
policy-map QoS-Policy
 class VoIP
  priority 100            ! LLQ 100 kbps
 class Application
  bandwidth 25            ! CBWFQ, min. 25 kbps
 class class-default
  fair-queue
!
interface Serial0/0
 service-policy output QoS-Policy
!
access-list 100 permit ip any any precedence 5
access-list 100 permit ip any any dscp ef
access-list 101 permit tcp any host 10.1.10.20
access-list 101 permit tcp any host 10.1.10.40
```
- Voice: Priorität, niedrige Verzögerung, konstante Bandbreite → `priority`. Interaktiver Verkehr: Bandbreite und niedrige Verzögerung → `bandwidth`.
- *(Ergänzung)* Da `class-map VoIP` ohne Schlüsselwort `match-all` ist, aber nur ein `match` enthält, spielt die Logik hier keine Rolle; die ODER-Verknüpfung entsteht durch die zwei ACEs in ACL 100.

### *(Ergänzung)* Wichtige MQC-Befehle
```
class-map match-any VOICE
 match dscp ef
 match cos 5
class-map match-all WEB-APP
 match protocol http          ! NBAR
 match access-group name APP-SERVERS
!
policy-map MARK-IN
 class VOICE
  set dscp ef
 class class-default
  set dscp default
!
policy-map WAN-OUT
 class VOICE
  priority percent 20
 class VIDEO
  bandwidth remaining percent 40
 class BULK
  bandwidth remaining percent 20
  random-detect dscp-based
 class class-default
  fair-queue
  random-detect dscp-based
!
interface GigabitEthernet0/0/1
 service-policy input MARK-IN
 service-policy output WAN-OUT
```
- Pro Interface und Richtung **eine** service-policy.
- Queuing-Aktionen (`priority`, `bandwidth`, `shape`, `queue-limit`, `random-detect`) gehören in Output-Policies; Marking (`set`) und `police` gehen in beide Richtungen.

### *(Ergänzung)* `show policy-map interface` lesen
```
R1# show policy-map interface GigabitEthernet0/0/1 output
! Beispiel: Policy liegt als Child unter einem 10-Mbps-Shaper (daher 20 % = 2000 kbps)
 GigabitEthernet0/0/1
  Service-policy output: WAN-OUT
    Class-map: VOICE (match-any)
      52310 packets, 10462000 bytes
      30 second offered rate 2180000 bps, drop rate 180000 bps
      Match: dscp ef (46)
      Priority: 20% (2000 kbps), burst bytes 50000, b/w exceed drops: 812
    Class-map: BULK (match-all)
      ...
      Match: dscp af11 (10)
      Queueing
      queue limit 64 packets
      (queue depth/total drops/no-buffer drops) 12/430/0
      bandwidth remaining 20%
    Class-map: class-default (match-any)
      ...
```
- `b/w exceed drops` in der Priority-Klasse → Voice überschreitet die Priority-Rate während Stau → mehr Priority-Bandbreite oder CAC.
- `total drops` in einer Queue → Tail Drop/WRED in dieser Klasse; `queue depth` > 0 → aktueller Stau.
- Offered rate 0 und Match-Zähler 0 → Klasse trifft nichts (falsche Markierung/ACL, Policy in falscher Richtung, Markierung erst nach dem Punkt der Policy).
- Policer-Ausgabe: `conformed … packets, … bytes; actions: transmit`, `exceeded …; actions: drop`, plus `conformed … bps, exceeded … bps`.

## Fehler/Ungenauigkeiten im Kurs
1. **„Service map"** in der MQC-Übersicht (S. 225): Den dritten Baustein gibt es nicht als „service map"; der Befehl heißt `service-policy input|output <name>` (Cisco IOS XE QoS Modular QoS CLI Configuration Guide). Im Fließtext ist es korrekt.
2. **Trust-Boundary-Definition** (S. 223): Der Kurs nennt die Trust Boundary einen Punkt, an dem Markierungen „nicht unbedingt vertraut" werden. Präziser: Die Trust Boundary ist der Rand der Trusted Domain; Markierungen, die *von außen* an ihr ankommen, werden nicht vertraut und dort neu gesetzt bzw. nur bedingt akzeptiert – innerhalb der Domain werden sie vertraut (Cisco Enterprise QoS SRND).
3. **„Policing … such as priority, queuing, and bandwidth"** (S. 225): `priority`/`bandwidth` sind Queuing-/Scheduling-Aktionen, kein Policing (einzige Ausnahme: der implizite Policer der LLQ-Priority-Queue).
4. **„Weighted fair … gives priority to real-time traffic"** (S. 224): WFQ bevorzugt Flows mit kleinem Volumen/höherem Gewicht, bietet aber **keine** Strict Priority für Echtzeitverkehr – genau deshalb gibt es LLQ.
5. **Cisco SDM QoS Wizard** wird als aktuelle Methode genannt; SDM ist seit Langem End-of-Life (ersetzt durch Cisco Configuration Professional, ebenfalls EoL) – für IOS XE irrelevant.
6. **CQ „provides traffic guarantees"**: gemeint sind Bandbreitenanteile (Byte-Count pro Runde), keine Latenz- oder Verlustgarantien.

## Bilder
- `bilder/21-qos/01-anforderungen.svg` – Daten/Voice/Video: Verkehrscharakter und One-Way-Anforderungen (Latenz, Jitter, Verlust, Bandbreite).
- `bilder/21-qos/02-qos-modelle.svg` – Best Effort, IntServ (RSVP, State pro Flow) und DiffServ (PHB pro Hop) im Vergleich.
- `bilder/21-qos/03-tos-byte.svg` – ToS-Byte mit IPP/DSCP/ECN, 802.1Q-PCP-Feld und Umrechnung DSCP ↔ ToS ↔ IPP.
- `bilder/21-qos/04-dscp-werte.svg` – AF-Matrix (8x+2y), EF, CS-Werte und Drop-Precedence.
- `bilder/21-qos/05-trust-boundary.svg` – Untrusted/Trusted Domain, Trust Boundary am Access-Switch/IP-Phone und am Provider-Übergang.
- `bilder/21-qos/06-police-shape.svg` – Policing (abschneiden/re-marken) vs. Shaping (puffern/glätten) mit Token-Bucket-Formel.
- `bilder/21-qos/07-llq.svg` – LLQ: Klassifizierung in Priority-Queue und CBWFQ-Queues, Scheduler, Tx-Ring.
- `bilder/21-qos/08-wred.svg` – Tail Drop und TCP Global Synchronization vs. WRED-Drop-Kurve mit Min/Max-Threshold.
- `bilder/21-qos/09-mqc.svg` – MQC-Kette class-map → policy-map → service-policy am Kursbeispiel.
