# 05 – Building Redundant Switched Topology (Kursseiten 39–47)

## Probleme ohne STP (S. 39)
- Broadcast-Sturm: Broadcasts kreisen endlos (Flooding auf alle Ports außer Eingangsport).
- Mehrfache Frame-Zustellung: Ziel bekommt Kopien desselben Unicast.
- MAC-Tabelle instabil: gleiche Quell-MAC auf verschiedenen Ports gelernt.
- STP: genau ein aktiver Pfad pro Segment, redundante Ports blockiert; bei Ausfall wird Standby-Pfad aktiviert.
- Drei Schritte: 1 Root Bridge wählen (alle Ports dort forwarding/designated), 2 Root Port pro Nonroot-Bridge (niedrigste Kosten zur Root), 3 Designated Port pro Segment (Bridge mit niedrigsten Kosten zur Root). Rest = nondesignated (blocking).
- Rollen: Root Port (nur einer pro Bridge, lernt MACs), Designated (einer pro Segment, lernt MACs), Nondesignated (blockt, lernt keine MACs), Disabled (shutdown).

## Betrieb (S. 40)
- BPDU alle 2 s (Hello). Felder: Protocol ID, Version, Message Type (Config/TCN), Flags (TC/TCA), Root BID, Root Path Cost, Sender BID, Port ID, Message Age, Max Age, Hello, Forward Delay.
- Ziel-MAC 01-80-C2-00-00-00, Quell-MAC = MAC des sendenden Ports.
- 802.1D-TC: Switch sendet TCN auf Root Port; upstream Designated Switch bestätigt mit TCA-Bit in Config-BPDU und leitet TCN weiter Richtung Root; Root sendet Config-BPDUs mit TC-Bit; alle Bridges leiten weiter.
- BID = Priority (0–61440, Schritte 4096, Default 32768) + MAC. Niedrigste BID = Root. Bei gleicher Priorität: niedrigste MAC. Wahl laufend – bessere BID übernimmt Root.
- Root Port: niedrigste kumulierte Pfadkosten; Gleichstand -> Sender BID -> Sender Port ID.
- Kosten 802.1D-1998 (short) / 802.1D-2004 (long): 10M 100/2.000.000; 100M 19/200.000; 1G 4/20.000; 10G 2/2.000; 4M 250, 16M 62, 2G 3/10.000.
- Designated Port: niedrigste Root Path Cost, dann niedrigste Sender BID, dann niedrigste Sender Port ID. Root Bridge: alle Ports designated.
- Port States 802.1D: Disabled (nichts), Blocking (empfängt BPDU), Listening (senden+empfangen BPDU, kein Lernen), Learning (lernt MAC, kein Forward), Forwarding (alles).

## STP-Varianten (S. 41)
- 802.1D/CST: eine Instanz für alle VLANs; wenig CPU, langsam, suboptimale Pfade.
- PVST+ (Cisco): eine 802.1D-Instanz pro VLAN, per-VLAN Root, langsam.
- RSTP 802.1w: schnell, eine Instanz.
- Rapid PVST+: 802.1w pro VLAN, höchster CPU/Speicherbedarf.
- MSTP 802.1s (inspiriert von Cisco MISTP): mehrere VLANs pro Instanz; Cisco-MST bis 16 Instanzen; CPU zwischen RSTP und Rapid PVST+.
- Default auf Catalyst laut Kurs: PVST+.

## Discovery 4 (S. 42)
- Lab: SW1 Root (niedrigste MAC aabb.cc00.0100), alle Prio 32769 (32768 + sys-id-ext 1). Kosten Ethernet IOL = 100 (short).
- show spanning-tree: "Spanning tree enabled protocol ieee" = PVST+, "rstp" = Rapid PVST+, Tabelle Interface/Role/Sts/Cost/Prio.Nbr/Type (Desg/Root/Altn; FWD/BLK; Shr/P2p).
- Extended System ID: Priority 4 Bit + 12 Bit VLAN-ID -> nur Vielfache von 4096, 16 Werte.
- root primary: wenn Root-Prio > 24576 -> 24576, sonst 4096 unter Root; secondary -> 28672. Running-config zeigt Zahl. Wenn Root Prio 0 -> primary scheitert.
- Pfad beeinflussen: spanning-tree vlan X cost (1–20.000.000 in der Lab-Angabe) auf eigenem Port; port-priority 0–255 Default 128 (in IOS praktisch Schritte von 16 bei 0–240) auf dem UPSTREAM-Switch (Sender Port ID). Port ID = Priorität.Portnummer (128.2).
- Beispiel: SW3 Et0/1 Root weil Sender Port ID 128.2 von SW2 < 128.4. Kosten Et0/2 auf 16 -> Et0/2 wird Root Port; danach Et0/3 SW3 Desg, SW1 Et0/1 Altn.
- debug spanning-tree events: Legacy-Konvergenz ~30 s (listening -> learning -> forwarding je 15 s).
- Timer: Hello 2 (1–10), Forward Delay 15 (4–30), Max Age 20 (6–40); nur auf Root ändern (wird propagiert). Befehl spanning-tree [vlan X] {hello-time|forward-time|max-age}.
- RSTP States: discarding, learning, forwarding. Rollen: Root, Designated, Alternate, Backup (discarding), Disabled (discarding).
- spanning-tree mode rapid-pvst; Interop: Ports zu Legacy-STP fallen zurück auf PVST+.
- RSTP TC: nur wenn Nonedge-Port in forwarding wechselt; Linkverlust ist keine TC. Initiator flutet TC-Bit auf Designated + Root Port; Empfänger löscht MACs aller Ports außer dem Empfangsport. Kein TCN außer für Legacy. Edge/PortFast-Ports lösen keine TC aus, MACs dort werden nicht geflusht.
- RSTP-Debug: Konvergenz < 1 s (proposal/agreement, sync).
- Link Types: point-to-point (full duplex), shared (half duplex); edge = PortFast. Designated Ports brauchen P2P für Rapid Transition; Root Ports nutzen Link Type nicht (sync). spanning-tree link-type point-to-point.

## MST (S. 43/44)
- Ziel: Instanzen = Anzahl logischer Pfade; weniger CPU. PVST+ bis 4094 Instanzen.
- Region: gleicher Name (32 Byte), Revision (2 Byte), VLAN-Instanz-Tabelle (4096 Einträge). BPDU trägt nur Digest der Tabelle (+ Name, Revision). Digest unterschiedlich -> Regionsgrenze. Auch Grenze: Empfang von 802.1D-BPDUs.
- Revision steigt nicht automatisch.
- Eine BPDU (IST-BPDU, MSTI-Infos als M-Records) für alle Instanzen. IST (Instanz 0) läuft auf allen Ports der Region, egal welche VLANs.
- Best Practice: Trunks, kein manuelles Pruning, keine Access-Links zwischen Switches; keine VLANs auf IST mappen (Problemfall: Access-Links VLAN10 (MST0) und VLAN20 (MST1) -> IST blockt einen -> VLAN10 tot).
- Config: spanning-tree mst configuration / name / revision / instance 1 vlan 2,3 / show pending / show current / exit|end übernimmt, abort verwirft. spanning-tree mode mst erst nach Mapping. spanning-tree mst 1 root primary|secondary, spanning-tree mst X priority. Nicht gemappte VLANs -> MST0.
- show spanning-tree summary: "Switch is in mst mode (IEEE Standard)", MST0/MST1/MST2.
- show spanning-tree mst configuration [digest]: Name [CCNP], Revision, Instances configured, Digest, Pre-std Digest (Cisco prestandard).
- spanning-tree mst 1 port-priority 64 (0–240, Schritte 16, Default 128), spanning-tree mst 1 cost X (1–200.000.000). Lab: Et0/2 cost 1.000.000 bleibt Altn, weil Pfad über SW2 zusätzlich SW2->SW1-Kosten enthält.
- MST-Kosten: long (Ethernet 10M = 2.000.000).

## PortFast / BPDU Guard (S. 45)
- Ohne PortFast: blocking (bis 20 s Max Age), listening 15 s, learning 15 s -> 30–50 s; DHCP-Timeouts.
- PortFast: sofort forwarding, nur Access-Ports zu Hosts.
- BPDU Guard: BPDU empfangen -> err-disabled, Log %SPANTREE-2-RX_PORTFAST.
- Interface: spanning-tree portfast; spanning-tree bpduguard enable. Global: spanning-tree portfast default (alle Nicht-Trunk-Ports); spanning-tree portfast bpduguard default (BPDU Guard für alle PortFast-Ports).
- Verifizieren: show running-config interface; show spanning-tree summary ("Portfast Default is enabled", "PortFast BPDU Guard Default is enabled"); show spanning-tree interface X portfast (zeigt global+interface). Globales PortFast steht nicht in der Interface-Config.
- switchport host = access + portfast + kein Channeling.
- BPDU Filter verfügbar, aber nicht empfohlen.

## Root Guard (S. 46)
- Angreifer sendet BPDUs mit niedrigerer BID -> wird Root -> MitM.
- Root Guard: superiore BPDU auf Port -> root-inconsistent (wie listening, kein Forwarding); Erholung automatisch, wenn superiore BPDUs aufhören. spanning-tree guard root; auf Ports Richtung Switches, die nie Root werden sollen.

## Ergänzend (eigenes Wissen, nicht im Kurs, für Fragen genutzt)
- Loop Guard: spanning-tree guard loop / spanning-tree loopguard default; Nicht-designated Port, der keine BPDUs mehr bekommt -> loop-inconsistent statt forwarding; Erholung bei BPDU-Empfang.
- BPDU Filter global (portfast bpdufilter default): auf PortFast-Ports keine BPDUs senden; bei BPDU-Empfang verliert Port PortFast-Status und Filter -> normales STP. Interface (spanning-tree bpdufilter enable): sendet/empfängt keine BPDUs -> Schleifengefahr.
- errdisable recovery cause bpduguard, show interfaces status err-disabled, show spanning-tree inconsistentports.
