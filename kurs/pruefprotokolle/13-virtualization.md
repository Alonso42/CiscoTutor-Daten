# Prüfprotokoll 13-virtualization

Geprüft: 120 Fragen (slg-vr-001 bis 120) und die Lektion (7 Seiten, jede Tabellenzelle). Ergebnis von pruefen.ps1 ohne -Mischen: OK (single 77, luecke 10, multi 11, zuordnung 11, cli 11; Schwierigkeit 1:20, 2:69, 3:31).

## Korrekturen
| ID | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-vr-097 | Die markierte Antwort "one hop: 172.16.14.1" war so nicht haltbar. IOS-traceroute nutzt UDP-Probes, und das Port-Unreachable des Ziels trägt die Adresse des Eingangs-Interfaces. Angezeigt würde also 172.16.99.2 (Tunnel-IP von R4), nicht die Loopback. | Frage nach der Hop-Anzahl umformuliert, Optionen sind jetzt Hop-Anzahlen (richtig: ein Hop, R4). Die Erklärung nennt die Tunnel-IP. | https://community.cisco.com/t5/networking-documents/traceroute-behavior-on-cisco-routers-ios-ios-xe/ta-p/3163669 , https://www.cisco.com/c/en/us/support/docs/ip/ip-routed-protocols/22826-traceroute.html |
| slg-vr-102 | Laut Erklärung enthält der RFC-2784-Header die "C/K/S-Bits". In RFC 2784 gibt es aber nur das C-Bit, K und S kommen erst mit RFC 2890 hinzu. | Erklärung präzisiert. Die Antwort war richtig. | https://www.rfc-editor.org/rfc/rfc2784 |

Entfernt: keine.

## Belegte Punkte (Auswahl)
- GRE-Keepalives: Standardmäßig aus, Default-Periode 10 s, Retries 3. Sie funktionieren auch, wenn die Gegenstelle keine Keepalives kennt (072, 074, 093, Lektion). Für 073 ergibt die Zählerlogik bei keepalive 5 4 rund 20 s. https://www.cisco.com/c/en/us/support/docs/ip/generic-routing-encapsulation-gre/63760-gre-keepalives-63760.html
- MTU/MSS: Selbst nachgerechnet. 1500−24=1476, MSS 1436. Mit Key 1500−28=1472. Der Wert 1400/1360 für GRE over IPsec ist eine gängige Empfehlung (061–064, 094, 115). Beleg für die MTU- bzw. PMTUD-Ursache bei 065: https://www.cisco.com/c/en/us/support/docs/ip/generic-routing-encapsulation-gre/13725-56.html
- GRE-Header: 4 Byte Basis. Die optionalen Felder (Checksum, Key, Sequence Number) haben je 4 Byte (RFC 2784/2890).
- Rekursives Routing und %TUN-5-RECURDOWN, Abhilfe per spezifischer statischer Route oder getrenntem Routing (075, 076, 108). https://www.cisco.com/c/en/us/support/docs/ip/enhanced-interior-gateway-routing-protocol-eigrp/22327-gre-flap.html
- tunnel vrf und vrf forwarding: Underlay- gegenüber Overlay-Auflösung (090, 106). https://www.cisco.com/c/en/us/support/docs/multiprotocol-label-switching-mpls/mpls/46252-grewithvrf.html
- Route Leaking per `ip route vrf X ... next-hop global` (052): Die Route landet in der VRF-Tabelle, der Next Hop wird in der globalen Tabelle aufgelöst. https://www.cisco.com/c/en/us/support/docs/ip/ip-routing/200158-Configure-Route-Leaking-between-Global-a.html
- Default-Bandbreite eines Tunnels 100 kbit/s (ältere IOS-Versionen 9 kbit/s). OSPF-Kosten 100000/100=1000, plus 10 für Ethernet (10 Mbit/s IOL) ergibt 1010 (079, 080). Belegt über Cisco Community. Die Lab-Ausgabe "BW 100 Kbit/sec" steht in den Notizen.
- OSPF auf GRE-Tunnel: Netzwerktyp point-to-point, also FULL/- und keine DR-Wahl (081). Belegt über Community und networklessons.
- NFVIS: Linux/KVM-basiert, läuft auf ENCS, UCS und C8300-uCPE und hostet Cisco-VNFs (015). https://developer.cisco.com/docs/nfv/cisco-nfv-solutions
- Topic-IDs gegen ENCOR v1.2 geprüft: 2.1.a Hypervisor Typ 1/2, 2.1.b VM (Container/NFV ebenfalls hier), 2.1.c Virtual Switching, 2.2.a VRF, 2.2.b GRE/IPsec. Alle plausibel.

## Unsichere Punkte
- 073: Die "~20 s" sind aus der Zählerlogik abgeleitet. Ein exakter Sekundenwert steht nicht im Doc, die Antwortoptionen (5/9/20/40) bleiben aber eindeutig.
- 079/081: Die Tunnel-Default-Bandbreite (100 kbit/s) und den Default-Netzwerktyp p2p belegen nur Community- und Trainingsquellen, kein offizieller Config Guide. Sie decken sich aber mit der Lab-Ausgabe aus dem Kurs.
- 033 (Virtual Firewall, "Layers 2 to 4 plus services") stammt aus der Kurssicht und wurde unverändert gelassen.

## Wissen & Bilder (Checker 2026-11-24)
Geprüft: wissen/13-virtualization.md, bilder/13-virtualization/01–10 (Inhalt, [xml], kein BOM, Skript-Check: alle OK). Rechnungen: GRE-MTU/MSS 1476/1436, 1472/1432, 1464/1424, 1400/1360; OSPF 100000/100 = 1000, +10 = 1010, +1 = 1001; 9 kbit/s → 11111; Konsolidierung 20+40+10 = 70 %; vCPU 20+2+2 = 24.
- Wissen: Tunnel-Default-Bandbreite ergänzt: 100 kbit/s auf aktuellem IOS/IOS XE, alte IOS-Versionen 9 kbit/s (Änderung ca. 2007, CSCse69736, nur Community-Beleg). Der Wert dient nur als Metrik, er bremst nicht. Quellen: https://community.cisco.com/t5/routing/default-bw-value-on-vpn-tunnel-is-100-kbit/td-p/2278321 , https://community.cisco.com/t5/routing/default-delay-value-on-tunnel-interfaces-differing-values-on/td-p/1604557
- Ohne Änderung belegt: GRE-Header RFC 2784 (C-Bit, Reserved0, Ver, Protocol Type) und RFC 2890 (K-/S-Bit), Overhead 24 Byte, Keepalive-Defaults, RECURDOWN, tunnel vrf vs. vrf forwarding (Quellen siehe oben). Die Bilder 07–10 stimmen mit Wissen, Lektion und Fragen überein (Traceroute-Hop 172.16.99.2, FULL/-).
Offen: Für die 100-kbit/s- bzw. 9-kbit/s-Defaults gibt es keinen offiziellen Config-Guide-Beleg, nur Community-Quellen und die Lab-Ausgabe.