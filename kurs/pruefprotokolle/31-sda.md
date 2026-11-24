# Prüfprotokoll 31-sda (Checker)

Datum: 2026-11-24
Geprüft: 122 Fragen (fragen/31-sda.json), Lektion (7 Seiten inkl. aller Tabellenzellen), Wissensdatei wissen/31-sda.md, 9 SVGs (alle wohlgeformt per [xml]).
Ergebnis: 121 Fragen, pruefen.ps1 (ohne -Mischen) OK.

## Quellen
- Cisco SD-Access Solution Design Guide (CVD): https://www.cisco.com/c/en/us/td/docs/solutions/CVD/Campus/cisco-sda-design-guide.html
  (50 Byte VXLAN-Overhead, min. 1550 MTU, MTU 9100 per LAN Automation; 20 ms RTT AP↔WLC; Fabric APs local mode, direkt an Edge oder Extended Node; L2-Handoff: Border wird Default-Gateway, SVI gleicher IP im Legacy-Netz deaktivieren; IP-Transit: VRF-Lite pro VN + eBGP, Peer-Gerät manuell; SD-Access Transit trägt VRF und SGT; Extended Node per 802.1Q-Trunk/EtherChannel, INFRA_VN; ISE 2 Knoten alle Personas; Edges/Borders registrieren bei allen CP Nodes; IS-IS-Vorteile; L2 Flooding = Multicast-Gruppe, nicht default; FiaB: Einzelswitch/Stack/StackWise Virtual, Dual-FiaB unterstützt)
- Cisco Tech-Dokument 220427 (SD-Access Wireless, Cat 9800): https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/220427-implement-software-defined-access-for-wi.html
  (AP-Join: WLC fragt CP nach AP-RLOC, CP informiert Edge, Edge baut VXLAN-Tunnel; Client-Onboarding: WLC programmiert AP mit L2VNID/SGT/RLOC, registriert L2 beim CP, Edge registriert IP nach DHCP Snooping; Roaming: CP informiert Roam-to- und Roam-from-Edge; show access-tunnel summary)
- Cisco Live BRKENS-2810 / Cisco TAC 220361 (LISP/VXLAN-Troubleshooting, show lisp session mit Peer x.x.x.x:4342 Up, VXLAN UDP 4789)
- RFC 9300/9301 (LISP Data 4341 / Control 4342), RFC 7348 (VXLAN, UDP-Quellport-Hash, 4789), draft-smith-vxlan-group-policy (16-Bit Group Policy ID)
- Cisco Community (DNAC Netzwerkanforderungen): 100 ms RTT empfohlen / 200 ms Maximum Catalyst Center ↔ Geräte: https://community.cisco.com/t5/cisco-catalyst-center/network-requirements-for-dna-center/m-p/4275059
- ENCOR v1.2 Blueprint: https://learningcontent.cisco.com/documents/marketing/exam-topics/350-401-ENCORE-v1.2.pdf (1.3 SD-Access: 1.3.a CP/DP-Elemente, 1.3.b traditioneller Campus; 2.3.a LISP, 2.3.b VXLAN; 5.4.d TrustSec/MACsec – konsistent mit Bestand in daten_fragen.json)

## MTU-Rechnung (006, 115, SVG 06)
1500 (inneres IP) + 14 (innerer Ethernet) + 8 (VXLAN) + 8 (UDP) + 20 (äußeres IP) = 1550 Byte IP-MTU. Korrekt; deckt sich mit CVD ("minimum starting MTU of at least 1550 bytes").

## Korrekturen
| ID | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-sd-005 | "RTT ≤ 100 ms zwischen Fabric-Geräten im Underlay" nicht belegbar (CVD nennt keinen solchen Wert) | umformuliert: empfohlene RTT Catalyst Center ↔ Geräte = 100 ms (200 ms max. in Erklärung), Distraktoren 10/500/100/20 | Community/DNAC-Datenblatt, CVD |
| slg-sd-042 | Erklärung: Fabric AP nur "direkt an Edge" | ergänzt "(oder einem Extended Node)" | CVD |
| slg-sd-049 | "CP benachrichtigt Roam-to-Edge, Roam-from-Edge und Border" – Border nicht belegt | auf "Choose two" (Roam-to/Roam-from) umgestellt, Border-Option durch ISE-PSN-Distraktor ersetzt | Tech-Dok 220427 |
| slg-sd-052 | Distraktor "second FiaB switch" angreifbar (Dual FiaB laut CVD unterstützt); "supervisor modules" nicht belegt | Distraktor durch "fabric WLC taking over CP role" ersetzt, richtige Option "redundant members of the switch stack", Erklärung (Einzelswitch/Stack/StackWise Virtual) | CVD |
| slg-sd-055 | "Any WLC and AP hardware and software" nicht belegbar | "Existing nonfabric WLCs and APs can be kept" + Erklärung | CVD (OTT = nonfabric WLC/APs) |
| slg-sd-057 | "using one AP subnet" nicht belegt | Option/Erklärung ohne diese Angabe | – |
| slg-sd-081 | "via REST" – Übertragungsweg CC→ISE nicht eindeutig (REST/pxGrid) | "It is written to ISE, …", Erklärung neutral | Community, CVD |
| Lektion S.1 | "RTT ≤ 100 ms" | entfernt | s. 005 |
| Lektion S.6 | Roaming: "… und Border", "Roaming unter 50 ms" | nur neue/alte Edge; 50 ms entfernt; "20 ms (RTT)" | 220427, CVD |
| Lektion S.7 | "mit jeder WLC/AP-Hardware" | "mit der bestehenden Non-Fabric-WLC/AP-Hardware" | CVD |
| Wissen | 100 ms, <50 ms, Roaming-Border, OTT "beliebige HW", FiaB-Resilienz, Fabric AP an Extended Node | präzisiert bzw. als Kursangabe gekennzeichnet, Fehlerliste Punkt 9 ergänzt | s. o. |
| SVG 08-wireless | "beliebige HW/SW" beim OTT-WLC | "Non-Fabric, bestehend" | CVD |

## Entfernt
| ID | Grund |
|---|---|
| slg-sd-066 | "Roaming < 50 ms" nicht in Cisco-Dokumentation belegbar (nur Kursangabe) |

## Gezielt belegt (Writer-Markierungen), ohne Änderung
- 059–064, 104: VRF-Lite pro VN (SVI/Subinterface) + eBGP, Peer manuell; Route Leaking Fusion; L2-Handoff (Legacy-SVI deaktivieren); SD-Access Transit erhält VRF+SGT; IP-Transit entkapselt am Border → SXP/Inline-Tagging (CVD).
- 072: UDP 4342 Control (RFC 9301), 4341 Data, 4789 VXLAN.
- 082–085, 122: Ausgabeformate show lisp instance-id … map-cache/database, show lisp session (Peer:4342 Up), show lisp site plausibel und konsistent mit IOS-XE (gekürzte Beispiele).
- 053: Extended Node per 802.1Q-Trunk (EtherChannel) an Edge, INFRA_VN (CVD).
- 076: NDP = Network Data Platform (DNA-Center-Architektur NCP/NDP).
- 006: s. MTU-Rechnung. 051: 20 ms RTT (CVD).
- CLI 110–121: Syntax gültig (show lisp session/site, show lisp instance-id 4099 ipv4 map-cache|database, show access-tunnel summary, system mtu 9100, net …, ip router isis, vrf forwarding, address-family ipv4 vrf, neighbor … remote-as, show ip route vrf).
- Topic-IDs: plausibel gegen v1.2 und Bestand (5.4.d = TrustSec/MACsec im Bestand).

## Unsichere Punkte (belassen)
- 093 (CDP-Macro nur ohne Port-Authentifizierung) und 058 (OTT: Border annonciert WLC-/Client-Subnetze) beruhen auf Kursaussagen; fachlich plausibel, keine widersprechende Quelle gefunden.
- 036/037 (pxGrid + REST, PAN) Standardwissen zur CC-ISE-Integration, nicht im Volltext nachgelesen.
