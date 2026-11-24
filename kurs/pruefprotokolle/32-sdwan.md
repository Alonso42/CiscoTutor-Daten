# Prüfprotokoll 32-sdwan (Checker)

Datum: 2026-11-24
Geprüft: 118 Fragen (fragen\32-sdwan.json), Lektion (8 Seiten, alle Tabellenzellen), Wissensdatei wissen\32-sdwan.md, 9 SVGs (bilder\32-sdwan\, alle als [xml] wohlgeformt, inhaltlich geprüft).
Ergebnis pruefen.ps1 (ohne -Mischen): OK, 118 Fragen (single 73, multi 13, zuordnung 11, luecke 9, cli 12; Schwierigkeit 28/62/28).

## Korrekturen

| ID / Datei | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-wn-050 (Erklärung) | Service-VPN-Bereich "1–511, 513–65530, 65531–65535 reserviert" nicht belegbar | Auf "1–65525 ohne 512, darüber intern (z. B. 65528–65530)" korrigiert; Antwort (VPN 513) bleibt richtig | https://www.cisco.com/c/en/us/td/docs/routers/sdwan/configuration/segmentation/ios-xe-17/segmentation-book-xe/segmentation.html ("Range: 1 to 65525, excluding 512"); https://community.cisco.com/t5/sd-wan-and-cloud-networking/are-vpns-65528-65529-65530-reserved-only-for-loopback-inerfaces/td-p/4801626 |
| slg-wn-086 (Erklärung) | gleicher Bereichsfehler | Erklärung angepasst; Paar "VPN 65535 – intern reserviert" bleibt korrekt | wie oben |
| slg-wn-046 | Absolutaussage "no tunnels" gilt nur per Default (allow-same-site-tunnels) | Frage um "With default settings" ergänzt, Erklärung nennt allow-same-site-tunnels | https://community.cisco.com/t5/sd-wan-and-cloud-networking/can-two-sd-wan-routers-with-same-global-ip-establish-tunnel/td-p/5011342 |
| slg-wn-059 (Erklärung) | klargestellt, dass die Einschränkung für jede Color gilt (TLOC-Eindeutigkeit) | Erklärung präzisiert | https://www.networkacademy.io/ccie-enterprise/sdwan/controlling-the-topology-restricted-tloc-color |
| wissen\32-sdwan.md | VPN-Bereich (2 Stellen); Site-ID-Aussage ohne "standardmäßig" | korrigiert | s. o. |
| lektionen\32-sdwan.json Seite 5 | VPN-Bereich | "1–65525 ohne 512" | s. o. |
| bilder\32-sdwan\07-vpns.svg | VPN-Bereich im Text | korrigiert, [xml] OK | s. o. |

## Entfernt
Keine.

## Gezielt belegte Writer-Punkte (Auswahl)
- 009/010/093/108/094: Validator immer DTLS, kein Port-Hopping; Edge baut DTLS zum Validator nach Erhalt der Liste ab; DTLS Default zu Manager/Controller, TLS optional; Port-Hopping 12346, 12366, 12386, 12406, 12426; Manager-Cluster mind. 3 (014) – https://www.cisco.com/c/en/us/td/docs/routers/sdwan/configuration/sdwan-xe-gs-book/cisco-sd-wan-overlay-network-bringup.html
- 065: BFD per Color hello 1000 ms, multiplier 7; app-route multiplier 6, poll 600000 ms – https://netascode.cisco.com/docs/data_models/sdwan/edge_feature_templates/bfd/ ; https://cisco.com/c/en/us/support/docs/routers/sd-wan/221604-understand-bfd-protocol-relationship-wit.html
- 095/101: OMP graceful restart Default 12 h (43200 s), max 7 d – https://www.ciscolive.com/c/dam/r/ciscolive/emea/docs/2023/pdf/BRKTRS-3793.pdf ; https://netascode.cisco.com/docs/data_models/sdwan/edge_feature_templates/omp/
- 073, 075–083: config-transaction/commit, system-ip/site-id/organization-name/vbond, interface Tunnel + tunnel mode sdwan, sdwan → interface → tunnel-interface → encapsulation ipsec/color; show sdwan control connections/local-properties – https://www.cisco.com/c/en/us/support/docs/routers/xe-sd-wan-routers/218137-configure-basic-parameters-to-form-contr.html ; https://www.cisco.com/c/en/us/support/docs/routers/sd-wan/222302-troubleshoot-common-sd-wan-control-and-d.html
- 057/058/074/084: restrict nur gleiche Color – networkacademy.io (s. o.)
- 067: ohne strict Weiterleitung trotz SLA-Verletzung, strict = drop, fallback-to-best-path – https://www.cisco.com/c/en/us/td/docs/solutions/CVD/SDWAN/cisco-sdwan-application-aware-routing-deploy-guide.html
- 069/070/071/072: Moduswechsel (NVRAM/Startup gelöscht, Running-Config im bootflash, YANG-Konfig bleibt), Default autonomous, 17.2.1r – https://www.cisco.com/c/en/us/td/docs/routers/sdwan/configuration/sdwan-xe-gs-book/install-upgrade-17-2-later.html ; https://www.cisco.com/c/en/us/td/docs/routers/c8400/c8400-software-config-guide/Autonomous-Controller.html
- 029: GET /dataservice/device, Token /dataservice/client/token, j_security_check – https://developer.cisco.com/docs/sdwan/authentication/
- 099: symmetrisch/symmetrisch kein direkter Tunnel – https://www.networkacademy.io/index.php/ccie-enterprise/sdwan/tlocs-and-nat ; https://www.cisco.com/c/en/us/support/docs/routers/xe-sd-wan-routers/222973-configure-static-nat-for-tloc-extension.html
- 115: 20.12/17.12 Empfehlung Configuration Groups – https://www.cisco.com/c/en/us/support/docs/routers/sd-wan/222297-quick-start-guide-simplified-configura.html
- 015, 017, 020, 021, 096, 092, 104, 113, 116: Architektur-/Rechenaussagen, konsistent mit CVD/Policies-Guide und Kursinhalt; kein Fehler gefunden.

## Unsichere Punkte
- Port-Hopping und "Validator immer DTLS" sind im Getting-Started-Guide belegt; der genaue BFD-Default (1000 ms/7) stammt aus dem Cisco-Netascode-Datenmodell, nicht aus einem Config Guide (gilt in der Praxis aber als Standard).
- slg-wn-059: Die Regel "eine Color pro Edge-Tunnel-Interface" ist nur sekundär belegt (networkacademy, Kurs); Frage bleibt, weil die Antwort mit Kurs und TLOC-Eindeutigkeit übereinstimmt.
- slg-wn-060/061 (Controller-Color steuert public/private) beruhen auf dem Kurs, sind aber mit der Color-Logik konsistent.
