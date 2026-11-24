# Kapitelprüfung 18-wlan-ts (Checker)

Datum: 2026-11-24
Geprüft: 122 Fragen (fragen/18-wlan-ts.json, flaches JSON-Array bestätigt), Lektion (7 Seiten inkl. aller Tabellenzellen), Wissensdatei, 10 SVGs (alle wohlgeformt, `<title>` erstes Kind, UTF-8 ohne BOM).
pruefen.ps1 -Kapitel 18-wlan-ts (ohne -Mischen): OK. Verbleibend: 122 Fragen (single 75, multi 14, cli 12, zuordnung 12, luecke 9; Schwierigkeit 31/63/28).

## Korrekturen

| ID / Datei | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-wt-035 | `show logging profile wireless filter mac … to-file` reicht ohne `start last` nur 10 Minuten zurück; Szenario „vor einer Stunde“ wäre damit nicht abgedeckt | Frage nennt „letzte 2 Stunden“, Lösung `show logging profile wireless start last 2 hours filter mac 3c22.fb11.2233 to-file bootflash:client.log` (Bausteine ergänzt), Erklärung ergänzt | https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/213949-wireless-debugging-and-log-collection-on.html |
| slg-wt-103 | Erklärung ohne Hinweis auf das 10-Minuten-Standardfenster | Hinweis auf `start last` ergänzt | wie oben |
| slg-wt-054 | „WLC default 60 s“ mehrdeutig: AireOS ab 8.5 Default 180 s | Frage auf Catalyst-9800-Policy-Profile präzisiert; Erklärung nennt AireOS 8.5+ 180 s | https://www.cisco.com/c/en/us/support/docs/lan-switching/8021x/214466-802-1x-client-exclusion-on-an-aireos-wlc.html ; 9800 Best Practices („exclusion set to 60 seconds“): https://www.cisco.com/c/en/us/products/collateral/wireless/catalyst-9800-series-wireless-controllers/guide-c07-743627.html |
| slg-wt-047 | Erklärung „6 = Daten vor der Authentifizierung“ falsch (Class-2-Frame = (Re)Assoc/Disassoc, Daten = Class 3) | Erklärung korrigiert | IEEE 802.11 Reason Codes, z. B. https://networkingdocs.hpe.com/documentation/us/en/software/mist/mist-wireless/topics/ref/mist-wifi-error-codes.html |
| slg-wt-021 | AQ-Skala „0 bis 100“; Cisco: 1 (schlechteste) bis 100 | Erklärung auf 1–100 | https://cisco.com/c/en/us/support/docs/wireless/mobility-express/212544-configure-cisco-clean-air-on-mobility-ex.html |
| Lektion Seite 3 | AQ 0–100 | 1–100 | wie oben |
| Lektion Seite 6 | Always-On-Befehl ohne Zeitfenster | `start last 1 hours` + 10-Minuten-Hinweis | 213949 |
| Wissen | AQ 0–100; Exclusion-Default ohne Versionsangabe; Always-On 10-Min-Default fehlte; Reason 6 nicht in Fehlerliste | korrigiert/ergänzt (AQ 1–100; AireOS <8.5 60 s, ab 8.5 180 s, 9800 60 s; 10-Min-Hinweis; Fehlerliste 4a) | s. o. |
| 01-tool-layer.svg, 03-interferer.svg | AQ 0–100 | AQ 1–100 | s. o. |

## Entfernt
Keine.

## Gezielt belegt (Writer-Markierungen, ohne Änderung)
- 003–006, 062, 064: Monitor-Modus, ein Kanal, Radiotap-Metadaten; Wireshark braucht alle vier Handshake-Pakete + wpa-pwd Passphrase:SSID (https://wiki.wireshark.org/HowToDecrypt802.11).
- 007/008: Management-Subtypen 0 AssocReq, 4 ProbeReq, 8 Beacon, 0x0a Disassoc, 0x0b Auth, 0x0c Deauth (IEEE 802.11).
- 009/010/119/120: SNR −71−(−94)=23 dB; −60 dBm mit 8 dB SNR → Noise −68 dBm; 20→17 dBm = −3 dB ≈ halbe Leistung (100→50 mW) – nachgerechnet.
- 011: −67 dBm / 25 dB SNR (Cisco VoWLAN Design Guide: https://www.cisco.com/en/US/docs/solutions/Enterprise/Mobility/emob30dg/Voice.html).
- 017: DECT EU 1880–1900, DECT 6.0 1920–1930 MHz (https://en.wikipedia.org/wiki/DECT). 018: Bluetooth FHSS 1-MHz-Kanäle.
- 024: ED-RRM sofortige Kanalbewertung/-wechsel (212544).
- 033/034/055/070: `show wireless client mac-address … detail`, `debug wireless mac <mac>`, ra_trace in bootflash:, monitor-time Default 1800 s (213949).
- 036/037/039/040/042/048: 9800-Befehle Syntax plausibel/standard (show wireless exclusionlist, show aaa servers, `vlan` im Policy Profile, `address ipv4 … auth-port 1812 acct-port 1813`, show ap tag summary).
- 051/071: PoE 802.3af 15,4/12,95 W, at 30/25,5 W, bt T3 60/51 W, T4 90/71,3 W (https://ethernetalliance.org/wp-content/uploads/2019/12/WP_EA_Overview8023bt_V2p1_FINAL.pdf).
- 066/084: Mobility UDP 16666 Control, 16667 Data (https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/213913-building-mobility-tunnels-on-catalyst-98.html).
- 069/104: Client 360 mit Onboarding, RSSI/SNR, Time Travel (Cisco DNAC Assurance-Material, 226132).
- 077/101/097/098: Status 17 (AP kann keine weiteren STAs), 18 (BSSBasicRateSet), Reason 4 Inaktivität, 5 AP überlastet, 15 4-Way-Handshake-Timeout.
- 081: Band Select für Voice-WLAN deaktivieren (https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/214863-voice-deployment-on-catalyst-9800-wirele.html).
- 105: Wireless Debug Analyzer parst 9800 RA-Traces und Always-On-Traces (https://cisco.com/c/en/us/support/docs/wireless/standalone-controllers/220344-troubleshoot-with-wireless-debug-analyze.html).
- 109: λ = 3·10^8 / 2,4·10^9 = 12,5 cm → ½ λ ≈ 6,25 cm – nachgerechnet.
- 063/078/079/082/083/095/096/111–113: Standardwissen, konsistent mit 9800 Best Practices (802.11k/v empfohlen) und AireOS-Zuständen (DHCP_REQD).

## Unsichere Punkte
- 9800-Default Exclusion-Timeout 60 s nur indirekt belegt (Best-Practices-Text „normally … 60 seconds“, Community-Ausgaben); kein Config-Guide-Zitat gefunden. Distraktoren (10/300/3600) enthalten 180 nicht, Frage bleibt eindeutig.
- 066 „Mobility-Gruppenname identisch“: Für nahtloses Roaming mit PMK-Cache nötig; Inter-Gruppen-Roaming ist grundsätzlich möglich. Als Prüfpunkt vertretbar, belassen.
- Kursbezogene Fragen (029, 030, 052, 056, 121) beruhen auf dem Kursinhalt (AireOS-GUI, WCAE, RF-Gruppe max. 20 WLCs, Short Preamble SpectraLink).
