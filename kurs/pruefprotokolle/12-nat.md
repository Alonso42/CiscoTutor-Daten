# Kapitelprüfung 12-nat

Geprüft: 118 Fragen (slg-nt-001 bis -118) und die Lektion nat-encor (8 Seiten, jede Tabellenzelle).
Ergebnis: 0 korrigiert, 1 entfernt, 117 verbleibend. pruefen.ps1 (ohne -Mischen) meldet OK.

## Entfernt
| ID | Problem | Quelle |
|---|---|---|
| slg-nt-025 | Die Frage beruht darauf, dass IOS einen Pool ablehnt, wenn Start- und Endadresse in verschiedenen Subnetzen liegen (Meldung "%Start and end addresses on different subnets"). Das stimmt sehr wahrscheinlich, ließ sich aber in keiner Cisco-Doku nachweisen (weder Command Reference noch NAT FAQ). Laut Auftrag deshalb entfernt. | https://cisco.com/c/en/us/support/docs/ip/network-address-translation-nat/26704-nat-faq-00.html (nennt nur die Syntax) |

## Gezielt belegte Punkte (alle korrekt, ohne Änderung)
- 010/011/115 `ip nat outside source static <outside-global> <outside-local>`: Doc 13773, Tabelle mit outside local 172.31.16.5 / outside global 172.16.89.32 bei `ip nat outside source static 172.16.89.32 172.31.16.5`. https://www.cisco.com/c/en/us/support/docs/ip/network-address-translation-nat/13773-2.html
- 029/030/031/073/078 Timeouts (Command Reference `ip nat translation (timeout)`): timeout 86400 s, udp-timeout 300 s, tcp-timeout 86400 s, dns/icmp/finrst/syn je 60 s, pptp 86400 s. https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/ipaddr/command/ipaddr-cr-book/ipaddr-i4.html
- 054–061 und Lektion S. 8, Reihenfolge der Verarbeitung (Doc 6209): inside→outside = Input-ACL, Routing, NAT, Crypto, Output-ACL. outside→inside = Input-ACL, NAT, Routing. https://www.cisco.com/c/en/us/support/docs/ip/network-address-translation-nat/6209-5.html
- 066/069/Lektion S. 9, NVI auf IOS XE: Der IOS XE NAT Config Guide (3S) sagt wörtlich "NAT Virtual Interfaces (NVIs) are not supported in the Cisco IOS XE software." https://www.cisco.com/en/US/docs/ios-xml/ios/ipaddr_nat/configuration/xe-3s/iadnat-addr-consv.html
- 022 `ip nat inside source static network local-ip global-ip`: Syntax steht im selben Guide.
- 075 `show ip nat translations verbose` zeigt, wann ein Eintrag angelegt und zuletzt benutzt wurde: Quelle dieselbe.
- 049 permit any: Doc 13772 sagt, permit any in NAT-ACLs verbraucht zu viele Router-Ressourcen. Der 15.2MT-Guide warnt vor zu offenen ACLs. https://bxin.cisco.com/c/en/us/support/docs/ip/network-address-translation-nat/13772-12.pdf
- 036–039 PAT-Portgruppen 0–511 / 512–1023 / 1024–65535, Originalport wird nach Möglichkeit behalten, sonst nächste Pool-Adresse: NAT FAQ 26704.
- 085 der ISP braucht eine Route zum Pool: NAT FAQ 26704 (Pool-Routing).
- 116 "%Dynamic Mapping in Use, Cannot remove", Lösung clear ip nat translation: Doc 13779. https://www.cisco.com/c/en/us/support/docs/ip/network-address-translation-nat/13779-clear-nat-comments.html
- 079 ICMP-Query-Identifier wird wie ein Port behandelt: RFC 3022 (NAPT übersetzt TCP/UDP-Ports und ICMP-Query-IDs). https://www.rfc-editor.org/rfc/rfc3022
- 096 100.64.0.0/10 ist Shared Address Space: RFC 6598. https://www.rfc-editor.org/rfc/rfc6598
- 027/113 Pool-misses = fehlgeschlagene Zuweisungen: Erklärung in der Cisco Community (https://community.cisco.com/t5/other-security-subjects/clarification-of-nat-statistics/m-p/217605). 028 Hits/Misses: nach Feldbeschreibung der Command Reference.
- Adresstypen 001–012, 004, 094, 105 und Lektion S. 2: einzeln nachvollzogen, alle korrekt.

## Unsichere Punkte (behalten)
- 077 refcount = Zahl der Übersetzungen, die die Zuordnung gerade nutzen: Stimmt mit der Kurs-Lab-Ausgabe und mit Community-Ausgaben überein. Eine offizielle Feldbeschreibung habe ich nicht gefunden.
- 068 `show ip nat nvi translations`: Die Command Reference belegt `show ip nat nvi statistics` (12.3(14)T). Die translations-Variante steht nur in Cisco-Schulungsmaterial. Ich halte sie für sicher.
- 083 vom Router selbst erzeugter Verkehr (Quelle = WAN-Adresse) wird nicht per inside source übersetzt: Folgt aus der Regel inside→outside. Ein expliziter Doku-Satz fehlt.
- 067 Meldung NVI0 up beim ersten ip nat inside: aus dem Kurs, nicht separat belegt.

## Wissen & Bilder (Checker 2026-11-24)
Geprüft: wissen/12-nat.md, bilder/12-nat/01–09 (Inhalt, [xml], kein BOM, Skript-Check: alle OK). Rechnungen: Pool 149−100+1 = 50, 2/50 = 4 %, 3/50 = 6 %, 2^16 = 65 536 Ports.
PAT-Portwahl geklärt: Die Cisco NAT FAQ sagt, IOS behält nach Möglichkeit den Originalport, sonst sucht es **vom Anfang** der Portgruppe (0–511, 512–1023, 1024–65535) den ersten freien Port. Danach kommt die nächste Pool-Adresse mit dem Originalport, sonst Drop; die FAQ nennt eine Ausnahme für 12.2S. Das Kursbeispiel 1723 → 1724 widerspricht dieser Regel. Quelle: https://www.cisco.com/c/en/us/support/docs/ip/network-address-translation-nat/26704-nat-faq-00.html
- Lektion (Seite PAT): Sie sagt bereits "ersten freien Port in derselben Gruppe" und ist damit korrekt, keine Änderung. Die Fragen 037–039 sind konsistent.
- Wissen: Regel präzisiert ("vom Anfang der Gruppe", "nicht Originalport + 1", Drop, 12.2S/IOS-XE-Hinweis), Kursbeispiel als Abweichung markiert, Fehlerliste auf "geklärt" gesetzt.
- Bild 05-pat-tabelle: 209.165.201.5:1724 → :1024, Hinweis "belegt → erster freier ab 1024", Regel 2 präzisiert. Bild 03-varianten: 1724 → 1024.
- Erstes Paket CEF vs. process-switched: Laut FAQ unterstützt IOS-NAT CEF-, Fast- und Process-Switching, Fast Switching gibt es ab 12.4T nicht mehr. Zum ersten Paket sagt die FAQ nichts. Die Wissens-Aussage "pauschal veraltet" bleibt, belegt durch die Lab-Ausgabe "CEF Punted packets: 0"; FAQ-Satz ergänzt.
- NVI auf IOS XE nicht unterstützt: bestätigt (IOS XE NAT Config Guide 3S, siehe oben im Protokoll).
- Hinweis: Laut FAQ übersetzt NAT ab 12.4(20)T auch lokal erzeugte HSRP-/Routing-Pakete, die zum Outside-Interface hinausgehen. Die Wissens-Aussage "Router-eigener Verkehr (Quelle = WAN-Adresse) wird nicht übersetzt" gilt weiterhin, weil es dabei um die ACL-Quelle geht. Nicht geändert.