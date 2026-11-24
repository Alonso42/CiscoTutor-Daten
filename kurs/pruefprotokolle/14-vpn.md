# Prüfprotokoll Kapitel 14-vpn

Geprüft: 122 Fragen (encor-1.4.10/fragen/14-vpn.json), Lektion (7 Seiten inkl. Tabellen), Wissensdatei wissen/14-vpn.md, 10 SVGs in bilder/14-vpn/.
Ergebnis pruefen.ps1 (ohne -Mischen): OK – 122 Fragen (single 81, multi 12, cli 12, zuordnung 10, luecke 7; Schwierigkeit 28/63/31).

## Korrekturen
| ID/Datei | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-vp-024 | Cisco-Regel: Policy passt, wenn die Lifetime des Remote-Peers ≤ der lokalen ist; ohne Angabe des Initiators formal mehrdeutig | Frage ergänzt "R1 initiates" (3600 ≤ 86400 → Match, kürzerer Wert), Erklärung präzisiert | https://docs.manage.security.cisco.com/cdfmc/c_fptd_vpn_ike.html ; https://www.cisco.com/en/US/docs/ios-xml/ios/sec_conn_ikevpn/configuration/12-2sx/sec-aggr-mde-ike.html |
| slg-vp-026 | Erklärung: "andere Defaults verwenden MD5 und/oder 3DES mit Gruppe 2" – 65510 ist AES/MD5/Gruppe 5 | Erklärung korrigiert (65510 AES/MD5/5; 65512/65514 3DES/2) | https://www.cisco.com/en/US/docs/ios-xml/ios/sec_conn_imgmt/configuration/15-0m/sec-ipsec-usability-enhance.html |
| slg-vp-016 | Rechnung korrekt (RFC 4301), aber IOS XE unterstützt AH+ESP-Kombination nicht | Hinweis in Erklärung | https://cisco.com/en/US/docs/ios-xml/ios/sec_conn_vpnips/configuration/xe-3s/sec-cfg-vpn-ipsec.html |
| wissen/14-vpn.md | AH+ESP-Kombination ohne IOS-XE-Einschränkung; Lifetime-Regel vereinfacht | beide Stellen präzisiert | wie oben |
| bilder/14-vpn/10-lab-topologie.svg | "je Ping um 5" missverständlich | "je ping-Befehl (5 Echos) um 5" | – |

## Entfernt
keine

## Belegte Punkte (Auswahl, vom Writer markiert)
- 019/119: RFC 2408 ISAKMP, 2409 IKEv1, 4301 Architektur, 7296 IKEv2 (rfc-editor.org).
- 026/027/118: Default-Policies 65507–65514, 65508 = AES/SHA/PSK/Gruppe 5 (Cisco IPsec Usability Enhancements).
- 068: `set pfs [group1|group14|group15|group16|group19|group2|group20|group24|group5]` (IOS XE Security for VPNs with IPsec).
- 072/073/078: "IPsec VTI is limited to IP unicast and multicast traffic only", "IPsec stateful failover is not supported with IPsec VTIs" (IPsec VTI Config Guide 15.0M); 108 Virtual-Access aus Virtual Template; 070 Klartext-Features auf VTI, verschlüsselte auf physischem Interface (ebd.).
- 081/082/110: MM_KEY_EXCH + "%CRYPTO-4-IKMP_BAD_MESSAGE ... failed its sanity check or is malformed" bei PSK-Mismatch (Cisco 117259 trouble-ios-ike, 5409 ipsec-debug); MM_NO_STATE = Main Mode kommt nicht über MM1/MM2 hinaus.
- 087/105: IKE-SA 86400 s, IPsec-SA 3600 s / 4 608 000 KB (Cisco 5463-cp-r).
- 097: esp-gcm 128/256, AEAD (IOS XE IPsec Config Guide).
- 036–043, 103: Main Mode 6, Aggressive 3, Quick Mode 3, IKEv2 4 Nachrichten, Exchanges (RFC 2409, RFC 7296).
- 054–061: ESP 50, AH 51, UDP 500/4500, NAT-T (RFC 3947/3948), ESP-Header authentisiert/nicht verschlüsselt (RFC 4303).

## Unsichere Punkte
- 069/109 (Line Protocol des VTI hängt von IPsec-SA ab): aus Kurs, im abgerufenen Teil des VTI-Guides nicht wörtlich gefunden; entspricht bekanntem IOS-Verhalten – belassen.
- 079 (gleiche IP wie physisches Interface → rekursives Routing): Kursaussage, plausibel (Tunnel-Destination über den Tunnel gelernt), nicht in Cisco-Doku wörtlich belegt – belassen.
- 088: "Tunnel transport MTU 1438" stammt aus der Lab-Ausgabe des Kurses.
