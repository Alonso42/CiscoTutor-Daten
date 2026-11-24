# Kapitelprüfung 28-wlan-roaming

Datum: 2026-11-24 · Checker · Websuche (WebSearch/WebFetch), kein Browser.

## Umfang
- Fragen geprüft: 105 (alle einzeln). Danach 105 (keine entfernt): single 64, multi 11, luecke 8, zuordnung 10, cli 12; Schwierigkeit 27/56/22.
- Lektion (7 Seiten, alle Tabellenzellen), Wissensdatei, 9 SVGs (alle wohlgeformt per [xml]).
- `pruefen.ps1 -Kapitel 28-wlan-roaming` (ohne -Mischen): OK.

## Verwendete Quellen
- Q1: Cisco, Building Mobility Tunnels on Catalyst 9800 (UDP 16666/16667, Control-DTLS immer an, Data-DTLS optional, Default-Gruppenname "default", CLI wireless mobility group name/member, show wireless mobility summary, AireOS 8.10 MR1+, `encrypt enable`, `member hash`): https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/213913-building-mobility-tunnels-on-catalyst-98.html
- Q2: Cisco WLC Mobility Groups FAQ (24 WLCs pro Gruppe; Mobility List bis 72, max. 24 pro Gruppe, Kombinationen 3×24/12×6/24×3/72×1; UDP 16666 Control und Mobility-Ping; IP 97 Data; UDP 16667 für verschlüsselte Daten; Mobility Ping Control vs. EoIP; Mobile Announce zuerst in der eigenen Gruppe; CCKM/PKC nur innerhalb der Gruppe, bei Gruppenwechsel volle Authentifizierung, IP bleibt): https://www.cisco.com/c/en/us/support/docs/wireless/4400-series-wireless-lan-controllers/107188-mobility-groups-faq.html
- Q3: Cisco Catalyst 9800 Roaming Primer (Adaptive 11r: RSN-IE ohne FT-AKM, MDID im Beacon, iOS/Samsung; Over-the-Air Default; OKC Default, PMK an Mobility Group verteilt; Roam-Zeiten volle Auth 120 ms–Sekunden, OKC 8–100 ms, CCKM/11r 4–50 ms): https://www.cisco.com/c/en/us/products/collateral/wireless/catalyst-9800-series-wireless-controllers/cat9800-ser-primer-enterprise-wlan-guide.html
- Q4: Cisco Catalyst 9800 Configuration Best Practices (Adaptive FT Default, Empfehlung Mixed Mode, Over-the-DS deaktiviert lassen, 11v Default an, Optimized Roaming nicht empfohlen, Anchor: Export Anchor, Tunnel CAPWAP + DTLS): https://www.cisco.com/c/en/us/products/collateral/wireless/catalyst-9800-series-wireless-controllers/guide-c07-743627.html
- Q5: Cisco 9800 802.11r/k/v Fast Roams (bss-transition disassociation-imminent): https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/221671-understand-802-11r-11k-11v-fast-roams-on.html
- Q6: Cisco 802.11r Deployment Guide (AireOS `config wlan security ft {enable|disable} <id>`, `config wlan security ft over-the-ds`): https://www.cisco.com/c/ja_jp/td/docs/wireless/controller/technotes/80211r-ft/b-80211r-dg.html
- Q7: Cisco IOS-XE 3.3 Deployment Guide 802.11r/k/w (gleiche IOS-XE-WLAN-CLI-Linie: `security ft [over-the-ds]`, `assisted-roaming neighbor-list`) – per Suchsnippet.
- Q8: Cisco 9800 ↔ CMX (NMSP TCP 16113, `show nmsp status`): https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/214729-configuring-and-troubleshooting-cmx-conn.html
- Q9: EoS/EoL AP 4800 (EoS 31.10.2022, LDoS 31.10.2027): https://www.cisco.com/c/en/us/products/collateral/wireless/aironet-4800-access-point/aironet-4800-series-access-points-eol.html ; Hyperlocation-Modul (EoS 30.04.2019, LDoS 30.04.2024): https://www.cisco.com/c/en/us/products/collateral/interfaces-modules/aironet-hyperlocation-module-advanced-security/eos-eol-notice-c51-741567.html
- Q10: Cisco Spaces FAQ (Lizenzstufen Extend, ACT, Smart Spaces; früher See/Extend/Act), Spaces-Datenblatt (Connector, FastLocate/Hyperlocation über Connector): https://spaces.cisco.com/setupguide/faq/ , https://cisco.com/c/en/us/products/collateral/wireless/dna-spaces/datasheet-c78-741786.html

## Korrekturen
| ID / Datei | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-wr-014 (Erklärung) | "Mobility Domain aus bis zu drei Gruppen = 72" zu eng | 72 = Obergrenze der Mobility List, z. B. 3 × 24 | Q2 |
| slg-wr-015 | Frage setzte "bis zu drei Gruppen" voraus; laut Cisco auch 72 Gruppen à 1 möglich | Frage umformuliert: Mobility List bis ___ Controller, max. 24 je Gruppe; Erklärung mit Kombinationen | Q2 |
| slg-wr-037 | "AireOS since 5.2" online nicht belegbar | "recent AireOS releases"; Cisco-Doku bestätigt symmetrisch = Default und nicht konfigurierbar in neueren Releases | Cisco IP-Phone Deployment Guides (Suchsnippets) |
| slg-wr-050 (Erklärung) | Herkunft des 150-ms-Werts unscharf | als Richtwert (angelehnt an 150-ms-Einwegbudget) mit Cisco-Roam-Zeiten ergänzt | Q3 |
| slg-wr-060 | Adaptive 11r nicht nur Apple | Option "supported devices (e.g., iOS)"; Erklärung: RSN-IE ohne FT-AKM, iOS/Samsung, 9800-Default, Cisco empfiehlt Mixed Mode | Q3, Q4 |
| Lektion Seite 2 (Text + Tabellenzelle) | "bis 3 Gruppen = 72" | Mobility List bis 72, max. 24 je Gruppe (z. B. 3 × 24) | Q2 |
| Wissen | 72er-Grenze, 16667 als "verschlüsselter Control-Port" (falsch, laut FAQ verschlüsselte Daten), 5.2-Angabe, Adaptive 11r, Spaces-Lizenzstufen, EoL-Aussage FastLocate | korrigiert/ergänzt (IRCM-Voraussetzungen, Default-Gruppenname, Roam-Zeiten, EoS-Daten, Over-the-DS-Empfehlung) | Q1–Q4, Q9, Q10 |
| 02-mob-gruppe.svg | Kopfzeile "bis 3 Gruppen = bis 72 WLCs" | "bis 72 WLCs, max. 24 je Gruppe (z. B. 3 × 24)" | Q2 |
| 06-fast-roam.svg | Zeile "OKC / CCKM" mit 4-Way-Balken; CCKM nutzt keinen separaten 4-Way Handshake | Zeile auf "OKC" reduziert | Q3 (CCKM eigene, schnellere Roam-Zeit) |

## Entfernt
Keine.

## Geprüft ohne Änderung (Auswahl markierter IDs)
- 010 (DFS → faktisch passives Scannen), 012 (CCX-Parameter), 021 (IRCM nur über Secure Mobility, Q1), 022/076 (Ports, DTLS, Q1/Q2), 023/030 (mping Control UDP 16666 / eping Data, Q2), 024 (Mobile Announce, Q2), 025–029 (CLI, Q1; AireOS `config mobility group domain`/`member add` Standard-Syntax), 036 (asymmetrisch → uRPF), 042/043 (Anchor nur Peer, keine APs nötig, Q4), 044 (AireOS `config wlan mobility anchor add`), 051–059, 061–074 (Fast Roaming, 11k/v/r, CLI `security ft`, `security wpa akm ft dot1x`, `assisted-roaming neighbor-list`, AireOS `config wlan security ft enable`), 077 (Ortungstechniken), 088/089, 095–099 (Spaces, Connector, NMSP TCP 16113, `show nmsp status`, MAC-Randomisierung), 104 (Rogue-/Interferer-Ortung).

## Unsichere Punkte
- 9800-CLI `security wpa akm ft dot1x` und `assisted-roaming neighbor-list` nur über IOS-XE-Deployment-Guide-Snippets und Konsistenz der IOS-XE-WLAN-CLI belegt, Command Reference 17.x war per WebFetch nicht erreichbar (404/504).
- Optimized Roaming (072): Trennung unter Schwelle und Ablehnung/Rejections nur über Cisco-Community (Cisco-Mitarbeiter) belegt; Antwort vertretbar.
- Release 5.2 für symmetrisches Tunneling: nur noch indirekt belegbar, daher aus Frage 037 entfernt, in der Wissensdatei als unsicher markiert.
- Location-Faustregeln (−75 dBm, 2500 sq ft, 20 % Überlappung) stammen aus dem Kurs; nicht separat online verifiziert.
