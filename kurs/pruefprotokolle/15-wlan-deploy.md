# Prüfprotokoll 15-wlan-deploy

Geprüft: 118 Fragen (slg-wd-001 … 118), Lektion (8 Seiten inkl. aller Tabellenzellen), Wissensdatei, 9 SVGs.
Ergebnis: 117 Fragen, `pruefen.ps1 -Kapitel 15-wlan-deploy` → OK (single 76, multi 11, luecke 9, cli 11, zuordnung 10; Schwierigkeit 27/65/25).

## Belegte Kernfakten
- CAPWAP UDP 5246 Control / 5247 Data, Control per DTLS (Discovery vorher im Klartext), Data-DTLS optional (MAY); Split MAC / Local MAC – RFC 5415 https://www.rfc-editor.org/rfc/rfc5415.txt
- LWAPP UDP 12222 Data / 12223 Control – https://www.cisco.com/c/en/us/support/docs/wireless-mobility/wireless-lan-wlan/99947-lwapp-traffic-study.html
- Mobility-Tunnel 9800: UDP 16666 Control, 16667 Data – https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/213913-building-mobility-tunnels-on-catalyst-98.html
- FlexConnect: RTT 300 ms Daten, 100 ms Daten+Voice, MTU ≥ 500 Byte, 12,8 kbps/AP empfohlen – https://www.cisco.com/c/en/us/products/collateral/wireless/catalyst-9800-series-wireless-controllers/cat-9800-flexconnect-branch-deployment-guide-og.html
- 9800-CLI `wireless tag site … / flex-profile / no local-site`, `wireless profile policy … / no central switching`, `ap <mac> / site-tag` – https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/213945-understand-flexconnect-on-9800-wireless.html
- AP-CLI `capwap ap primary-base <name> <ip>` (enable mode) – https://www.cisco.com/en/US/products/ps6366/products_tech_note09186a00809a3f5d.shtml
- Option 43 TLV f1: Rechnung 10.10.10.5/.6 → f108 0a0a0a05 0a0a0a06 korrekt; 192.168.10.5 → f104c0a80a05 korrekt.
- WDS: WDS und Infrastruktur-APs im selben Subnetz/LAN-Segment – https://cisco.com/c/en/us/support/docs/wireless-mobility/wireless-lan-wlan/65346-wds-faq.html
- Meraki L3-Roaming verteilt oder über Concentrator – https://documentation.meraki.com/Architectures_and_Best_Practices/Cisco_Meraki_Best_Practice_Design/Best_Practice_Design_-_MR_Wireless/Wireless_Layer_3_Roaming_Best_Practices
- Meraki Out-of-Band, Verhalten bei Cloud-Verlust – https://documentation.meraki.com/General_Administration/Cross-Platform_Content/Behavior_during_Connection_Loss_to_Cisco_Meraki_Cloud
- CW917x Unified (eine SKU, Meraki oder 9800) – https://www.cisco.com/c/en/us/td/docs/wireless/access_point/technical-reference/cw9172-dg.html
- AireOS 8.10 letzter Release, 3504/5520/8540 EoS/EoL, Migration auf 9800 – https://www.cisco.com/c/en/us/products/collateral/wireless/8500-series-wireless-controllers/wireless-software-8-10-pb.html
- EWC auf 9300: 200 APs/4000 Clients, SD-Access; Non-Fabric-Modus nur bis 17.3.x (EoS) – https://cisco.com/c/en/us/products/collateral/wireless/catalyst-9800-series-wireless-controllers/guide-c07-744299.html
- 9800-CL Templates 1000/3000/6000 APs, 10k/32k/64k Clients, 2,1 Gbps Low Profile, Public Cloud VPC+VPN, FlexConnect Local Switching – https://cisco.com/c/en/us/products/collateral/wireless/catalyst-9800-cl-wireless-controller-cloud/nb-06-cat9800-cl-cloud-wirel-data-sheet-ctp-en.html
- Mobility Express: 100 APs/2000 Clients, Flex-Architektur (Central Auth, Local Switching), keine Lizenz, Failover, Wave-1-APs als Subordinates – https://cisco.com/c/en/us/solutions/collateral/enterprise-networks/mobility-express/q-and-a-c67-734485.html

## Korrekturen
| ID | Problem | Änderung |
|---|---|---|
| slg-wd-065 | CLI-Syntax falsch: 9800 nutzt `no central switching` (Leerzeichen), nicht `central-switching` | Bausteine/Lösung auf `no` `central` `switching` (Ablenker authentication, dhcp, local-site, shutdown), Erklärung angepasst (Quelle 213945) |
| slg-wd-064 | Ablenker `central-switching` lehrte falsche Schreibweise | ersetzt durch `flex-mode` |
| slg-wd-017 | Erklärung „immer DTLS“ ignoriert Discovery im Klartext | Erklärung präzisiert (RFC 5415) |
| slg-wd-054 | „höchstens vier Fragmente“ nicht belegbar | Zusatz entfernt, Quelle 9800 Flex Guide genannt |
| slg-wd-072 | „Authentication of wireless users“ läuft bei Cloud-Verlust nicht pauschal weiter (Meraki-Cloud-Auth/Splash für neue Clients eingeschränkt) | Option → „Wireless access for already connected clients“, Erklärung ergänzt |
| slg-wd-092 | Public-Cloud-Wert veraltet | Erklärung um aktuellen Datenblattwert (6000 APs) ergänzt |
| slg-wd-097 | Frage nannte Kurswert 1,5 Gbps als Fakt; Datenblatt 2,1 Gbps | Frage neutral „roughly 2 Gbps“ |
| Wissensdatei | `no central-switching`, „vier Fragmente“, ME-VLAN-Regel als harte Regel, veraltete 9800-CL-Werte | korrigiert/ergänzt, Fehlerliste erweitert (EWC Non-SDA EoS, 9800-CL-Werte) |
| Lektion | `no central-switching`; ME-VLAN-Regel | Syntax korrigiert, „laut Kurs“ ergänzt |
| 08-mobexp.svg | „ein VLAN für alle APs“ als harte Regel | „APs im selben VLAN (Kurs-Empfehlung)“ |

## Entfernt
- slg-wd-101: „Alle ME-APs müssen im selben VLAN sein“ als einzige Ursache – nicht offiziell belegbar; Community-Berichte zeigen Join über Subnetze per Option 43, damit wäre der Distraktor „needs DHCP option 43 pointing to the primary AP“ ebenfalls vertretbar.

## SVGs
Alle 9 wohlgeformt ([xml]), <title> erstes Kindelement, keine doppelten Text-Koordinaten; Inhalte geprüft (nur 08 geändert).

## Unsichere Punkte (belassen)
- 0,35 kbps Control-Traffic pro FlexConnect-AP (Kurswert, als „laut Kurs“ gekennzeichnet; Cisco empfiehlt min. 12,8 kbps/AP Bandbreite).
- EWC-Limit „max. zwei pro Standort“ und 200 APs: Kurswert, durch Cisco Community/Deployment Guide gestützt.
- 9800-L 500 APs mit Performance-Lizenz (Wissensdatei): nicht direkt im Suchergebnis bestätigt, aber durch EWC-Guide („9800-L … up to 500 APs“) gestützt.
- Mobility-Ports: Einige Community-Posts deuten 16666/16667 bei AireOS als non-secure/secure; Cisco-9800-Doku: 16666 Control, 16667 Data (so in Fragen verwendet).
