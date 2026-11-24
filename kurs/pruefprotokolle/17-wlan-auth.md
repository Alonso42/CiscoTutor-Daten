# Kapitelprüfung 17-wlan-auth

Datum: 2026-11-24 · Checker (Schritt 7, nur WebSearch/WebFetch)

## Umfang
- Fragen geprüft: 118 (alle einzeln; markierte Writer-IDs zuerst gezielt belegt)
- Lektion: 7 Seiten, jede Tabellenzelle geprüft
- Wissensdatei: wissen/17-wlan-auth.md vollständig geprüft
- Bilder: 8 SVGs inhaltlich geprüft, alle als [xml] wohlgeformt
- pruefen.ps1 -Kapitel 17-wlan-auth (ohne -Mischen): OK (single 75, luecke 9, multi 13, zuordnung 9, cli 12; Schwierigkeit 29/61/28)

## Belege (Auswahl)
| Thema | Fragen | Quelle |
|---|---|---|
| default-policy-tag bindet nur WLAN-ID 1–16 | 085 | https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/213911-understand-catalyst-9800-wireless-contro.html |
| Policy-Tag-Syntax `wlan <WLAN> policy <PP>`, Tag-Wechsel → AP-Rejoin ca. 1 min | 087, 108 | ebd. |
| WPA2-PSK-CLI (`security wpa psk set-key ascii 0`, `no security wpa akm dot1x`, `security wpa akm psk`); dot1x-WLAN nur mit `security dot1x authentication-list` → Default WPA2/AES/802.1X; LWA-WLAN mit `security web-auth parameter-map global`; `virtual-ip ipv4 192.0.2.1`; Policy Profiles stets mit `no shutdown` | 088, 089, 090, 091, 079, 080, 086 | https://cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/217368-cooking-recipe-minimum-bootstrap-cli-co.html |
| `set-key ascii 8` = verschlüsselte Form (Type 8) | 090 | https://community.cisco.com/t5/wireless/9800-encrypt-psk-in-config-file/m-p/4516830 |
| `security wpa akm sae`, PMF Pflicht bei WPA3, Transition PSK+SAE mit PMF optional, 6 GHz nur WPA3/OWE + PMF, GCMP-256 im 192-bit-Modus | 009–011, 016, 092–094 | https://www.cisco.com/c/en/us/products/collateral/wireless/catalyst-9100ax-access-points/wpa3-dep-guide-og.html |
| 192-bit-Modus: nur EAP-TLS, GCMP-256, RSA ≥ 3072 / P-384 | 015, 016 | https://securew2.com/blog/eap-method-requirements-for-wpa3-enterprise ; Zebra WPA3 Integrator Guide |
| iPSK: PSK + MAC Filtering, AV-Pairs `psk-mode=ascii`, `psk=<key>` | 019–021 | https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/216130-configure-catalyst-9800-wlc-ipsk-with-ci.html |
| Mobility Anchor: Foreign `mobility anchor <IP> priority <n>`, Anchor `mobility anchor`; WLAN- und Policy-Profil-Namen müssen identisch sein | 068–070 | https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/213912-configure-mobility-anchor-on-catalyst-98.html |
| Mobility-Ports UDP 16666 (Control) / 16667 (Data) | 066 | https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/213913-building-mobility-tunnels-on-catalyst-98.html |
| AireOS-Legacy: EoIP IP-Protokoll 97 + UDP 16666 | 067 | https://www.cisco.com/c/en/us/support/docs/wireless/4400-series-wireless-lan-controllers/107458-wga-faq.html |
| AireOS Virtual Interface (WebAuth, DHCP Relay), in Mobility-Gruppe gleiche IP | 075, 076, 102, 116 | Cisco WLC Config Guide (Mirror), https://community.cisco.com/t5/wireless/wlc-virtual-interfaces/td-p/785825 |
| Client-Zustände IP Learn / Webauth Pending / Run | 074, 095, 096 | https://www.cisco.com/c/en/us/support/docs/wireless/catalyst-9800-series-wireless-controllers/221912-troubleshoot-common-issues-with-lwa-on-9.html ; 226071 (Foreign/Anchor-Traffic-Flow) |
| PBKDF2(Passphrase, SSID, 4096, 256), 8–63 ASCII / 64 Hex, 4-Way-Handshake, KCK/KEK/TK, Group Key Handshake | 003–006, 026–031 | IEEE 802.11-2020 Kap. 12 (RSNA) – Fachwissen, konsistent mit Cisco-Doku |
| EAP-TLS RFC 5216, TTLS RFC 5281 (Nicht-EAP-Innenmethoden), EAP-FAST RFC 4851 (PAC-Key/Opaque/Info, A-ID), RFC 3748 (4 Codes, NAK) | 033, 034, 052–062 | RFCs |

## Korrekturen
| ID / Datei | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-wu-068 (Erklärung) | Unvollständig: Cisco verlangt auch identischen Policy-Profil-Namen | Ergänzt (nur VLAN darf abweichen); Antwort unverändert korrekt | 213912 |
| slg-wu-086 (Erklärung) | Behauptung „neues Policy Profile ist zunächst shutdown“ nicht direkt belegbar | Umformuliert: Status DISABLED = shutdown, Cisco-Beispiele enden mit `no shutdown`; Antwort unverändert | 217368, 213911 |
| Lektion, Seite 6 (Text) | „WLAN-Konfiguration auf beiden gleich“ unvollständig | WLAN- und Policy-Profil (Namen + Einstellungen außer VLAN) | 213912 |
| Lektion, Seite 7 (Tabelle) | Zeile „Site Tag / RF Tag“ zeigte als CLI-Beispiel die AP-Tag-Zuweisung | Zeile korrigiert (`wireless tag site ST-1 / ap-profile default-ap-profile`) und eigene Zeile „Tag-Zuweisung am AP“ ergänzt | 213911 |
| Wissen: Guest Anchor | wie 068 | Policy-Profil-Name ergänzt | 213912 |
| Wissen: SAE | „IEEE 802.11-2016“ als Ursprung ungenau | „eingeführt mit 802.11s-2011, seit 802.11-2012 im Basisstandard“ | IEEE 802.11s-2011 |
| Wissen: CLI-Timeout | Kurswert 5 min ohne Hinweis | Hinweis ergänzt: IOS-XE `exec-timeout`-Default 10 min | IOS-XE Line-Defaults |
| Bild 04-eap-vergl.svg | „+ Offline-Angriff auf MSCHAPv2“ las sich als Vorteil | „→ Offline-Angriff …“ (Folge des fehlenden Zertifikatschecks) | – |
| Bild 06-guest-anc.svg | wie 068 | „WLAN- und Policy-Profil (Namen, Security) auf beiden WLCs identisch“ | 213912 |

## Entfernt
keine

## Unsichere Punkte (belassen, als „laut Kurs“ gekennzeichnet bzw. nicht kritisch)
- slg-wu-100: Pflichtfelder des Day-0-CLI-Wizards (Country Code, Credentials, WMI) stammen aus dem Kurs; offizielle Liste online nicht gefunden. Distraktoren (RF Network Name, Guest-SSID) sind laut Kurs optional.
- slg-wu-101/105: EWC-Default webui/cisco und GUI-Wizard-Passwort = Seriennummer „laut Kurs“.
- slg-wu-076: Zertifikatsfehler nach Roaming bei abweichender Virtual IP ist plausibel; Cisco verlangt gleiche Virtual IP in der Mobility-Gruppe (belegt), die genaue Symptomatik ist nicht dokumentiert.
- Default-Status eines neu angelegten Policy Profiles (shutdown) online nicht explizit gefunden; Frage 086 hängt nicht davon ab (Status DISABLED steht im Stamm).
