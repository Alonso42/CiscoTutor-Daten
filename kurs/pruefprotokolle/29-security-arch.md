# Prüfprotokoll 29-security-arch

Geprüft: 140 Fragen (slg-sa-001 … slg-sa-140), Lektion (7 Seiten, alle Tabellenzellen/Schritte), Wissensdatei, 9 SVGs.
Ergebnis pruefen.ps1 (ohne -Mischen): OK – 140 Fragen (single 86, zuordnung 16, multi 13, luecke 10, cli 15; Schwierigkeit 33/74/33).

## Korrekturen

| ID/Datei | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-sa-006 | Distraktor „STP, through a changed bridge priority“ ist selbst eine bekannte MITM-Technik (Root-Bridge-Angriff) → nicht eindeutig falsch | ersetzt durch „LLDP, through changed system description strings“ | allgemeines L2-Security-Wissen (STP-Root-Angriff) |
| wissen/29-security-arch.md | Key-String-Länge im MKA-PSK-Beispiel unklar („64 Hex bzw. 32 für 128 Bit“) | präzisiert: 32 Hex bei aes-128-cmac, 64 bei aes-256-cmac | https://community.cisco.com/t5/networking-knowledge-base/configuring-macsec-switch-to-switch-with-pre-shared-key/ta-p/4280159 |
| wissen/29-security-arch.md | Ergänzung | Hinweis auf „dot1x Failed over / mab Authc Success“ in show authentication sessions | Catalyst 4500 Command Reference (show authentication), https://cisco.com/c/en/us/support/docs/lan-switching/8021x/220919-troubleshoot-dot1x-on-catalyst-9000-seri.html |

Entfernt: keine.

## Belege für die als „nur eigenes Wissen“ markierten Fragen
- 122 „Failed over“: Cisco Command Reference show authentication – „method ran and failed over to the next method“; Beispiel dot1x Failed over + mab Authc Success. Bestätigt.
- 106/072 EAPOL 01:80:C2:00:00:03, EtherType 0x888E; 0x88E5 MACsec; 0x8909 CMD: IEEE 802.1 Präsentation (ieee802.org/1/files/public/docs2015/ae-seaman-ede-interop-0815-v02.pdf), Wikipedia IEEE 802.1X. Bestätigt.
- 127/128/131 MAB-Timer (max-reauth-req+1)×tx-period = 90 s, Service-Type Call-Check(10): Cisco MAB Deployment Guide (www3-realm.cisco.com/en/US/docs/solutions/Enterprise/Security/TrustSec_1.99/MAB/MAB_Dep_Guide.pdf). Bestätigt.
- 129 order/priority (MAB zuerst, dot1x darf preempten): Cisco Flexible Authentication / MAB Dep Guide. Bestätigt.
- 073/074 SXP TCP 64999, Speaker/Listener: https://www.cisco.com/en/US/docs/switches/lan/trustsec/configuration/guide/sxp_config.html. Bestätigt.
- 079/080/081 cts role-based enforcement / sgt-map / show cts role-based sgt-map all: TrustSec Config Guide. Bestätigt.
- 086/087 MKA Hello 2 s, Life 6 s: Catalyst 9300 MACsec Config Guide (17.x). Bestätigt.
- 092 linksec policy should-secure: https://www.cisco.com/c/en/us/support/docs/security/identity-services-engine/220721-configure-and-troubleshoot-mka-using-sec.html, eEdge Integration with MACsec. Bestätigt.
- 093/094/095 macsec network-link, mka pre-shared-key key-chain, show mka sessions: Cat9k MACsec Guide / Community-Doku. Bestätigt.
- 096 key-server priority: Default 0, niedrigster Wert gewinnt, Gleichstand niedrigste SCI (IEEE 802.1X-2010; Cisco Community-Doku). Bestätigt.
- 033 SecureX EoL 31.07.2024 → Cisco XDR: https://www.cisco.com/c/en/us/products/collateral/security/securex/securex-eol.html. Bestätigt.
- 034 ETA: IDP + SPLT: https://www.cisco.com/c/en/us/solutions/collateral/enterprise-networks/enterprise-network-security/at-a-glance-c45-740079.html. Bestätigt.
- 050 Spero (ML) / Ethos (loose/fuzzy fingerprinting): Secure Endpoint Data Sheet, Cisco Community. Bestätigt.
- 058–061 ZBFW (Self-Zone default permit, same zone permit, zone/non-zone drop, zone-pair/zone-member/service-policy type inspect): https://www.cisco.com/c/en/us/support/docs/security/ios-firewall/98628-zone-design-guide.html. Bestätigt.
- 057 ASA Security Levels (high→low erlaubt): ASA Config Guide. Bestätigt.
- 136/137 CWA Redirect-ACL permit=redirect/deny=kein Redirect, ip http server nötig: https://www.cisco.com/c/en/us/support/docs/security/identity-services-engine/113362-config-web-auth-ise-00.html. Bestätigt.
- 105 EAPOL ohne 802.1X verworfen, Supplicant sendet nach 3 Versuchen normal: Cisco 802.1X Config Guide. Bestätigt.
- 109 Tunnel-Private-Group-ID (RFC 3580), 108 TEAP (RFC 7170), 088/107 EAP-MD5 ohne Schlüssel (RFC 3748), 089 MKA in 802.1X-2010: Standards. Bestätigt.
- 121 802.1X nicht auf Trunk/DTP/VQP/EtherChannel: Cisco 802.1X Config Guides (Trunk-Restriktion plattformabhängig, NEAT-Ausnahme – Kursaussage beibehalten).
- Übrige (007, 009, 012, 014–018, 028, 029, 032, 035, 036, 056, 064–066, 099–101, 116–120, 123, 124, 130, 135): Standard-Definitionen/Befehle, gegen Cisco-Doku plausibel und konsistent; keine Fehler.

## Bilder
Alle 9 SVGs wohlgeformt ([xml] OK), Inhalte (IDS/IPS, Zonen, Content Security, TrustSec, SGACL-Matrix, MACsec-Frame/MKA, 802.1X-Fluss, Fallback 90 s, CWA-Ablauf) fachlich korrekt. Keine Änderungen.

## Unsichere Punkte
- 098 „dACL overrides static port ACL“ (Low-Impact): Cisco-Formulierung je nach Plattform „dACL hat Vorrang/ersetzt“; Kernaussage korrekt.
- 082 „~40 Byte Overhead“ ist Kursangabe (in Erklärung als solche gekennzeichnet).
