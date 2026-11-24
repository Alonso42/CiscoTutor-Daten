# Kapitelprüfung 04-campus-lan (Runde 2)

Datum: 2026-11-24 · Checker · Datei: encor-1.4.10\fragen\04-campus-lan.json

## Umfang
- Fragen: 111 geprüft (slg-vl-033…111 neu, jede einzeln; 001…032 gegengelesen)
- Wissensdatei wissen\04-campus-lan.md geprüft
- Lektion lektionen\04-campus-lan.json, alle 9 Seiten (neu 7–9) inkl. Tabellenzellen geprüft
- 8 SVGs in bilder\04-campus-lan\ inhaltlich und per [xml] geprüft – alle wohlgeformt, inhaltlich korrekt
- pruefen.ps1 -Kapitel 04-campus-lan (ohne -Mischen): OK (cli 12, single 73, multi 10, luecke 7, zuordnung 9; Schwierigkeit 26/60/25)

## Korrekturen
| ID/Datei | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-vl-098 | Antwort „untagged frames are dropped“ ist nicht eindeutig: Cisco-Guides widersprechen sich (16.8: „accepts untagged packets“, 17.14: „drops untagged packets“) | Frage umgestellt auf das unstrittige Sendeverhalten (Native-VLAN-Frames werden mit Native-VLAN-ID getaggt); Erklärung nennt den Release-Unterschied | https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-14/configuration_guide/lyr2/b_1714_lyr2_9300_cg/configuring_ieee_802_1q_tunneling.html ; https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/16-8/configuration_guide/lyr2_lyr3/b_168_lyr2_9300_cg/b_168_lyr2_lyr3_9300_cg_chapter_0110.html |
| wissen (Native VLAN) | Kursaussage „CDP wird nicht gesendet, wenn VLAN 1 vom Trunk entfernt ist“ ohne Korrektur übernommen | Als Kursaussage markiert und korrigiert: CDP/VTP/PAgP laufen immer mit VLAN-1-Tag, auch wenn VLAN 1 entfernt wurde | Cisco-Doku zitiert in https://community.cisco.com/t5/switching/clear-vlan-1-from-trunks/m-p/961864 |
| wissen (vlan dot1q tag native) | Empfangsverhalten fehlte | Hinweis auf release-abhängige Beschreibung ergänzt | s. o. (16.8 / 17.14) |

## Entfernt
keine

## Belege zu den markierten Fragen
- 038 n-802.1q = per DTP ausgehandelte Encapsulation: https://community.cisco.com/t5/switching/what-does-n-802-1q-mean-under-trunking/td-p/1365148
- 051 IP erst nach encapsulation dot1Q („Configuring IP routing on a LAN subinterface is only allowed if…“): https://www.cisco.com/en/US/docs/ios-xml/ios/lanswitch/configuration/15-2s/lsw-vlan-cfg-rtg.html
- 052 Parent shutdown → Subinterfaces administratively down: https://community.cisco.com/t5/switching/subinterfaces-will-not-come-up-on-1921/m-p/3841367
- 054 encapsulation dot1Q <vlan> native: Cisco IOS Routing Between VLANs (s. 051)
- 057–060, 096 SVI-Autostate (VLAN existiert/aktiv, SVI nicht shutdown, ≥1 L2-Port up + STP forwarding; switchport autostate exclude): https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-12/configuration_guide/int_hw/b_1712_int_and_hw_9300_cg/configuring_interface_characteristics.html ; down/down bei fehlendem VLAN vs. up/down: https://community.cisco.com/t5/switching/vlan-svi-line-protocol-is-down-why/m-p/5019902
- 067/068 show interfaces status (disabled / routed / trunk): Catalyst-Ausgaben (manualslib Cat 2950/4500) – Standardverhalten
- 069–071 802.1Q: VID 12 Bit, 0 und 4095 reserviert; 1522 Byte; DEI (IEEE 802.1Q-2011) – Standardwissen, im Wissen dokumentiert
- 076 „% Access VLAN does not exist. Creating vlan“: https://community.cisco.com/t5/other-network-architecture/unable-to-add-a-vlan-to-the-vlan-database-although-it-says-it/m-p/4016331
- 078 nonegotiate auf dynamic-Port abgelehnt („Conflict between 'nonegotiate' and 'dynamic' status“): https://community.cisco.com/t5/switching/disabling-dtp-for-3550-switcport-access/m-p/415390
- 079–082 DTP/Switch Spoofing/Double Tagging: https://en.wikipedia.org/wiki/Dynamic_Trunking_Protocol und Cisco-Community (s. o.)
- 084/085 „An interface whose trunk encapsulation is "Auto" can not be configured to "trunk" mode“: https://community.cisco.com/t5/switching/trunking-on-older-switches/m-p/2781675
- 087 switchport voice vlan {vlan-id | dot1p | none | untagged}; dot1p = VLAN 0/Priorität, Verkehr im Access-VLAN; none = Telefon nutzt eigene Konfiguration (Default): https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/16-9/command_reference/b_169_9300_cr/layer_2_3_commands.html ; https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-16/configuration_guide/vlan/b_1716_vlan_9300_cg/configuring_voice_vlans.pdf
- 100 doppelte dot1Q-ID auf zwei Subinterfaces abgelehnt („Configuration of multiple subinterfaces of the same main interface with the same VID … is not permitted“): https://community.cisco.com/t5/routing/subinterfaces-in-same-vlan-with-vrf-or-maby-bvi/m-p/2507009

## Unsichere Punkte
- 038, 052, 076, 078, 100: Belege sind Cisco-Community-Threads mit zitierten IOS-Meldungen, keine offizielle Config-Guide-Seite; Verhalten ist aber seit Jahren konsistent.
- 076: Auto-Anlage gilt im VTP-Server/Transparent-Modus; im VTP-Client-Modus nicht möglich (Frage nennt keinen VTP-Modus, Default ist Server).
- 079: Ergebnis „bleibt Access“ ist Folgerung aus DTP-Logik (Fremdhersteller antwortet nicht auf DTP), Standard-Lehrmeinung.
