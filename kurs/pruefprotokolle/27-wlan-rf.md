# Prüfprotokoll 27-wlan-rf (Explaining Wireless Principles)

Datum: 2026-11-24 · Checker · pruefen.ps1 (ohne -Mischen): OK (130 Fragen; single 89, multi 13, cli 10, zuordnung 10, luecke 8; Schwierigkeit 32/63/35)

## Umfang
- 130 Fragen einzeln geprüft (Antwort, alle Distraktoren, Erklärung, Eindeutigkeit, Topic).
- 44 Fragen mit Rechenanteil in Python (`python -I`) nachgerechnet: 001, 002, 005, 009, 010, 011, 022, 024, 025, 031, 032, 034–041, 044, 045, 048–053, 057, 070, 079, 080, 082, 085, 087, 094, 095, 096, 099, 100, 104, 126, 127, 145, 146 (inkl. λ, dBm↔mW, dB-Faktoren, dBi/dBd, EIRP, Link-Budget/Fade Margin, SINR in mW, Fresnel-Radius, HT/VHT/HE-PHY-Raten aus Unterträgern × Bits × Coding Rate × SS / Symboldauer, Airtime). Alle Ergebnisse stimmen (z. B. HT40 MCS7 SGI 150 Mbps, VHT80 MCS9 SGI 433,3, HE80 MCS11 0,8 µs 600,5 → ×8 = 4804 Mbps, SINR 14,86 dB, Fresnel 5,09 m).
- Lektion (7 Seiten, jede Tabellenzelle), Wissensdatei inkl. Kursfehler-Liste, 9 SVGs (alle `[xml]` OK).

## Korrekturen
| ID / Datei | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-rf-009 | "two in-phase copies of the same signal" addieren sich kohärent (Amplitude ×2 → +6 dB = −64 dBm), nicht +3 dB; markierte −67 dBm war physikalisch falsch | Frage auf zwei unkorrelierte Störsignale umgestellt (Leistungsaddition in mW → −67 dBm korrekt); Erklärung ergänzt | Physik (kohärente vs. inkohärente Addition), Python-Rechnung |
| slg-rf-046 | "introduced with 802.11ax": TWT stammt ursprünglich aus 802.11ah | Frage → "key enhancements of 802.11ax compared with 802.11ac" | IEEE 802.11ah-2016 (TWT) |
| slg-rf-094 | Erklärung suggerierte zusätzlichen Effekt ("zudem") | Präzisiert: Gesamtleistung gleich, Rauschen ×2 → −3 dB SNR | – |
| slg-rf-137 | IOS-XE-17.x-Syntax enthält Slot: `ap name <ap> dot11 5ghz slot 1 txpower {level|auto}` (Range 1–8) | Tokens `slot`,`1` ergänzt, Erklärung angepasst | https://www.cisco.com/c/en/us/td/docs/wireless/controller/9800/17-14/config-guide/b_wl_17_14_cg/m_enabling_ap_console.html |
| slg-rf-138 | dito `ap name <ap> dot11 5ghz slot 1 channel {n|auto|width ...}` | Tokens `slot`,`1` ergänzt, Erklärung angepasst | wie oben |
| wissen/27-wlan-rf.md | "Zwei gleiche Wellen in Phase … +3 dB" falsch (kohärent +6 dB) | korrigiert, Unterschied kohärent/unkorreliert ergänzt; Beispiel 2 × −70 dBm als "unkorreliert" markiert | Physik |
| wissen/27-wlan-rf.md | 802.11be: "16 SS im Standard, 46 Gbps" | finaler Standard 8 SS → ≈ 23 Gbps (2,88 Gbps/SS bei 320 MHz MCS 13, nachgerechnet); 46 Gbps nur mit 16 SS (frühe Drafts) | https://mrncciew.com/2024/12/14/wi-fi-7-overview/ , https://devopedia.org/ieee-802-11be |
| lektionen/27-wlan-rf.json | Seite 1 "in Phase +3 dB", Seite 3 "zwei gleiche Signale +3 dB", Tabelle 802.11be "≈ 46 Gbps" | +6 dB (kohärent) / "unkorreliert +3 dB" / "≈ 23 Gbps (8 SS)" | wie oben |
| bilder/27-wlan-rf/06-standards.svg | "≈ 46 Gbps theor." | "≈ 23 Gbps (8 SS)"; XML erneut geprüft | wie oben |

## Entfernt
keine

## Belegte Fakten (Auswahl, markierte Writer-Punkte)
- 9800 `ap dot11 5ghz rrm channel dca chan-width {20|40|80|160|best}` (139): AireOS→9800 Mapping Guide https://www.cisco.com/c/en/us/td/docs/wireless/controller/9800/cli-mapping/cli_mapping/cisco-aireos-controller-to-cisco-catalyst-9800-series-wireless-controller-command-reference-mapping-guide.html
- AireOS `config 802.11{a|b} chan_width <ap> {20|40|80|160|best}` (144): https://www.cisco.com/c/en/us/td/docs/wireless/controller/8-10/cmd-ref/b-cr810/config_commands_802_11.html
- `ap dot11 24ghz rate RATE_1M disable` / `{disable|mandatory|supported}`, Band vorher shutdown (134–136): https://www.cisco.com/c/en/us/td/docs/wireless/technology/5760_deploy/CT5760_Controller_Deployment_Guide/Radio_Resource_Management_Configuration.pdf , https://www.cisco.com/c/en/us/td/docs/wireless/controller/9800/command-reference/b_wireless_cr/configuration-commands-a-to-f.html
- AireOS `config 802.11b rate disabled 1`, `config 802.11a txPower ap <ap> {global|level}` (141, 143): 8.10 Command Reference (s. o.)
- Tx-Power-Level 1 = max, je Stufe ≈ 3 dB, 1–8 (137, 143, 145): https://www.cisco.com/c/en/us/td/docs/wireless/controller/technotes/8-3/b_RRM_White_Paper/tpc.html
- `show ap dot11 5ghz summary` Spalten Width/Txpwr/Channel (140, 145): https://community.cisco.com/t5/wireless/flapping-on-5ghz-channel/m-p/4947143 , https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/217738-monitor-catalyst-9800-kpis-key-performa.html
- 6 GHz USA: 1200 MHz, 59/29/14/7 Kanäle (100): https://blogs.cisco.com/networking/wifi-6e-6ghz-wifi-spectrum-unleashed , https://www.electronics-notes.com/articles/connectivity/wifi-ieee-802-11/6-ghz-band-wifi-channels-frequencies-bandwidths.php
- 9 × 26-Ton-RU in 20 MHz (091): https://en.wikipedia.org/wiki/Resource_Unit
- 802.11be 8 SS / 23 Gbps, 320 MHz nur 6 GHz, 4096-QAM, MLO (054, 083–085): s. o.

## Unsichere Punkte
- 137/138: Ob die slot-lose Altform (16.x) in 17.x noch akzeptiert wird, ist nicht belegt; daher auf die dokumentierte 17.x-Form mit `slot 1` umgestellt.
- 107 (ac Wave 2 MU-MIMO max. 4 Clients) und 091/107 (ax MU-MIMO max. 8 Nutzer): Standardwissen (VHT MU-PPDU max. 4 User; HE max. 8), per Websuche nur sekundär bestätigt.
- 116 (Class-3-Frame von authentifizierter, nicht assoziierter STA → Disassociation): IEEE 802.11 Frame-Klassen-Regel, Kurs bestätigt; nicht online nachgeschlagen.
- 802.11be-Erscheinungsjahr: Wi-Fi CERTIFIED 7 Jan. 2024; IEEE-Veröffentlichung 2024/25 – in der Wissensdatei entsprechend formuliert.
