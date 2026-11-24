# Notizen Kapitel 06 – Implementing Layer 2 Port Aggregation (Kursseiten 51–58)

## 51 Need for EtherChannel
- Problem: schnellere Links teuer und nicht unendlich skalierbar; mehrere parallele Links -> STP blockiert alle bis auf einen.
- EtherChannel: mehrere physische Ports -> ein logischer Port (port-channel). STP sieht nur einen Link -> nichts blockiert, alle Member aktiv.
- Eigenschaften: Aggregation, mehr Bandbreite, Load Sharing, ein logischer STP-Port, Redundanz.
- Immer 1:1 – ein EtherChannel verbindet genau zwei Geräte (Switch–Switch, Switch–Server/Router). Kein Bündel zu zwei verschiedenen Switches.
- 2–8 Ports (auf neueren Modellen 16), keine Mischung von Porttypen (FE + GE nicht in einem Bündel).
- Mehrere ECs zwischen zwei Switches möglich -> STP blockiert dann ein ganzes EC (alle Member).
- Config zentral auf dem port-channel -> konsistent. Ausfall eines Members: keine Topologieänderung, kein STP-Neuberechnen, nur weniger Durchsatz; EC läuft, solange ≥1 Link aktiv.

## 52 Mode Interactions
- Drei Wege: LACP, PAgP, statisch (on).
- LACP: IEEE 802.3ad, herstellerübergreifend; prüft Konsistenz (Speed, Duplex, VLAN). Switch mit niedrigster System Priority entscheidet, welche Ports aktiv werden; Ports nach Port Priority (niedriger = besser). Üblich bis 16 Links zuweisbar, max. 8 aktiv, Rest standby (übernimmt bei Ausfall). Max. aktive Links plattformabhängig.
- LACP-Modi: active (sendet unbedingt), passive (antwortet nur).
- PAgP: Cisco-proprietär; bündelt nur Ports mit gleichen Eigenschaften (Speed, Duplex, Native VLAN, VLAN-Range, Trunking-Status/-Typ); fügt Gruppe als einen Port in STP ein.
- PAgP-Modi: desirable (sendet unbedingt), auto (antwortet nur). on-Ports senden keine PAgP-Pakete.
- PAgP-Option silent/non-silent: non-silent = Bündel erst nach bestätigter Bidirektionalität (Schutz gegen unidirektionale Fehler, v. a. Glasfaser); silent = Bündel auch ohne empfangene Pakete (stille Partner wie Fileserver, Analyzer). (Kurs nennt Defaults; Cisco-Doku: ohne Angabe gilt silent – daher keine Default-Frage.)
- on: keine Aushandlung, keine Konsistenzprüfung, kein Link-Management; sofort im Bündel, auch wenn Gegenseite nicht passt. Negotiation = Overhead/Verzögerung, on = keine Verzögerung, aber riskant.

## 53 Konfigurations-Leitfaden
- Schritte: Ports identifizieren -> channel-group <n> mode <on|auto|desirable|active|passive> -> port-channel-Interface konfigurieren -> verifizieren.
- Best Practice: Anzahl Ports als Zweierpotenz (2/4/8) für gute Lastverteilung.
- on-Modus für Gegenstellen ohne PAgP/LACP; Fehlkonfiguration -> Paketverlust/STP-Schleifen.
- Änderungen am port-channel wirken aufs ganze EC, Änderungen am physischen Port nur dort.
- Gleich sein müssen: Speed, Duplex, Mode (access/trunk), Native + Allowed VLANs (Trunk), Access-VLAN.
- Ports müssen nicht benachbart oder auf demselben Modul sein.
- Shutdown eines Members = Linkausfall, Traffic über Rest.
- Unterschiedliche STP-Port-Kosten verhindern das Bündeln nicht.

## 54 Load-Balancing
- Hash-Eingaben: dst-ip, dst-mac, src-dst-ip, src-dst-mac, src-ip, src-mac (alle); src-port, dst-port, src-dst-port (4500/6500/9K).
- Methode global (port-channel load-balance <methode>), gilt für ALLE ECs des Switches; verschiedene Methoden pro EC unmöglich. Optionen mit "port-channel load-balance ?".
- Default meist src-dst-ip (plattformabhängig).
- Ein Feld -> niedrige Bits des Hashs; zwei Felder -> XOR. 2 Links: letztes Bit; 4 Links: letzte 2 Bits; 8 Links: letzte 3 Bits.
- Eine Konversation (gleiches Adresspaar) immer über denselben Link. Ungleichgewicht bei dominanten Host-Paaren -> andere Hash-Eingaben (z. B. L4-Ports).
- Überwiegend IP -> nach IP/Ports balancieren; Nicht-IP-Frames werden bei IP-Methode nach MAC verteilt.
- Zweierpotenz-Anzahl -> gleichmäßig; 3 Links -> ungleich (ein Link bekommt mehr Buckets).
- Welcher Port ein Flow nimmt, ist nicht steuerbar – nur die Methode.

## 55 Troubleshooting
- Inkonsistenzen der Member (Speed, Duplex, Trunking, Layer) -> Kanal geht nicht oder Member "s" (suspended).
- Port-channel = ein logisches Interface für STP/Routing; Hash wählt physischen Link.
- Prüfen: show interfaces (Speed/Duplex), show interfaces switchport / show run interface (Mode, VLAN, Native, Allowed, Encapsulation).
- L3-EC: alle Member "no switchport" (gleicher Layer).
- Duplex-Mismatch: Link kann up/up sein, aber viele Fehler.
- show etherchannel summary / show etherchannel <n> detail. P = bundled in port-channel (Kurs schreibt fälschlich "passive"), s = suspended. Mismatch -> Port suspendiert bis Konsistenz wieder da.
- show etherchannel load-balance (Methode), show etherchannel traffic (Statistik).
- Inkonsistenzen zwischen beiden Seiten: Modus-Mismatch -> Kanal down, Ports I (stand-alone), D, err-disabled. Spalte Protocol: "-" = on/manuell, sonst LACP/PAgP. Nur ein Protokoll pro EC.
- Bildende Kombinationen: active-active, active-passive, desirable-desirable, desirable-auto, on-on.
- Po mit "D" = nicht gebildet. Member "I" = individual (Protokoll-Mismatch), "D" = down/disabled.
- on gegen nicht-konfigurierte Gegenseite: Gegenseite sieht Einzelports -> Schleife -> STP/Guard err-disabled.
- Ungleiche Verteilung: hängt von Methode und Linkanzahl ab; z. B. dst-mac und 90 % Traffic an Gateway-MAC -> ein Link.
- EtherChannel Guard: erkennt Fehlkonfig (Log "%PM-SP-4-ERR_DISABLE: channel-misconfig error detected on Po3, putting Te1/3 in err-disable state"). Erwartet gleiche BPDUs auf allen Membern; BPDUs mit verschiedenen MACs -> Nachbar behandelt Links einzeln -> err-disable. Befehl spanning-tree etherchannel guard misconfig, default aktiv, Verifikation show spanning-tree summary ("EtherChannel misconfig guard is enabled").

## 56 Discovery 6 (Lab)
- SW1/SW2, 4 Links: E0/0–E0/1 = Po1, E0/2–E0/3 = Po2, dot1q-Trunks, PC1/PC2 in VLAN 11. Nur Standardprotokolle, SW1 initiiert, SW2 antwortet -> SW1 active, SW2 passive (LACP).
- Problem 1: SW2 Po2(SD) LACP, Et0/2(s) Et0/3(s). SW1 Po2(SU) Protocol "-" Et0/2(P) Et0/3(P) -> SW1 "channel-group 2 mode on". Fix: no channel-group 2 mode on, channel-group 2 mode active. Log: %EC-5-L3DONTBNDL2: Et0/3 suspended: LACP currently not enabled on the remote port.
- Danach weiter SD; Ursache laut Lab: SW2 Po2 "switchport trunk allowed vlan 1-10,12-4094" (VLAN 11 fehlt) vs. SW1 alle VLANs; Fix: no switchport trunk allowed vlan ... auf SW2 Po2.
- Problem 2: SW1 Po1 nur Et0/1(P); SW2 Po1 Et0/0(s) Et0/1(P). SW1 E0/0: "no switchport", kein channel-group. Fix: switchport, switchport trunk encapsulation dot1q, switchport mode trunk, channel-group 1 mode active. Danach Po1(SU) Et0/0(P) Et0/1(P).
- Flags: D down, P bundled, I stand-alone, s suspended, H hot-standby (LACP), R Layer3, S Layer2, U in use, f failed to allocate aggregator, M not in use/min links not met, u unsuitable, w waiting, d default port.
- IOL-Hinweis: shutdown wird in IOL beim Nachbarn als up/up gesehen.

## 57 PBR
- Klassisches Routing: zielbasiert. PBR überschreibt das für bestimmte Pakete (Policy: rechtlich, vertraglich, politisch).
- Angewendet auf eingehende oder lokal erzeugte Pakete; benötigt route-map (match -> Pakete auswählen, set -> Weiterleitung ändern).
- Z. B. Routing nach Quell-IP: 192.168.1.0/24 -> ISP1, 192.168.2.0/24 -> ISP2.
- Nutzen: source-based transit-provider selection, Load Sharing nach Traffic-Eigenschaften.

## Eigenes Wissen (nicht im Kurs, für Fragen genutzt – vom Checker zu prüfen)
- LACP: system-priority/port-priority Default 32768, Bereich 1–65535; System-ID = Priority + MAC; Gleichstand -> niedrigere MAC bzw. Portnummer. lacp max-bundle, lacp rate fast (1 s statt 30 s), show lacp sys-id, show lacp neighbor, port-channel min-links, LACP-Ziel-MAC 01-80-C2-00-00-02, channel-protocol.
- errdisable recovery cause channel-misconfig; Hash-Polarisation; ein Flow nie schneller als ein Member; show interfaces port-channel BW = Summe der gebündelten Member.
- PBR: set ip next-hop vs. set ip default next-hop, set interface Null0, verify-availability/track, mehrere Next-Hops, ACL-deny in Route-Map, Eintrag ohne match, ip policy nur eingehend, ip local policy, debug ip policy, match length.
