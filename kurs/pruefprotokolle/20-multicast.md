# Kapitelprüfung 20-multicast

Datum: 2026-11-24 · Checker

## Umfang
- Fragen: 139 geprüft (single 92, multi 11, luecke 10, zuordnung 12, cli 14; Schwierigkeit 27/78/34), alle Optionen, Distraktoren und Erklärungen
- Lektion: lektionen/20-multicast.json, 8 Seiten inkl. aller Tabellenzellen
- Wissensdatei: wissen/20-multicast.md
- Bilder: 11 SVGs in bilder/20-multicast/, alle als XML wohlgeformt ([xml]-Test OK), inhaltlich geprüft
- pruefen.ps1 -Kapitel 20-multicast (ohne -Mischen): OK

## MAC-Mapping selbst nachgerechnet (001–008, 138)
- 239.130.5.10: 130 = 0x82, oberstes Bit weg = 0x02, Ergebnis 01:00:5E:02:05:0A ✔
- 224.200.10.20: 200 = 0xC8, weg = 0x48, Ergebnis 01:00:5E:48:0A:14 ✔
- 003: 239.129.1.1, 238.1.1.1 und 225.1.1.1 ergeben alle 01:00:5E:01:01:01; 239.1.2.1 ergibt 01:02:01 ✔
- 005: 232.10.20.30 ergibt 0A:14:1E; 232.138/233.138/224.10 treffen, 232.10.148.30 (0x94) und .31 nicht ✔
- 138: 239.128.1.2 ergibt 00:01:02; 224.255.0.1 ergibt 7F:00:01; 232.20.30.40 ergibt 14:1E:28 ✔
- 004/006/007: 28 variable Bit, 23 kopiert, 2^5 = 32 ✔ (RFC 1112 Abschnitt 6.4)

## Korrekturen
| ID/Datei | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-mc-068 | „Only one RP is active per group“ stimmt bei Anycast-RP nicht (mehrere RPs sind gleichzeitig aktiv) | Option jetzt „Each group maps to one RP address“, Erklärung um den Hinweis auf Anycast-RP ergänzt | RFC 4610 / RFC 3446 (Anycast-RP) |
| slg-mc-119 | In der Erklärung stand „UDP-Kapselung ist nur eine Option“. RFC 3618 nennt nur TCP; die optionale Kapselung betrifft Daten in SAs, nicht den Transport | Klammer durch „(RFC 3618)“ ersetzt | https://www.rfc-editor.org/rfc/rfc3618.html (Abschnitte 11, 14) |
| wissen, Abschnitt 1 | „Empfänger melden ihr Interesse beim First-Hop-/Last-Hop-Router“: falsch, Empfänger melden sich beim LHR | Korrigiert zu Last-Hop-Router | RFC 1112/2236 |
| wissen, PIM-SM | „pro Gruppe nur ein RP aktiv“ (wie bei 068) | Geändert zu „nur eine RP-Adresse“ mit Anycast-Hinweis | RFC 4610 |
| wissen, MSDP | „UDP-Kapselung als Option“ (wie bei 119) | Entfernt; ergänzt, dass RFC 3618 SA-Caching vorschreibt | RFC 3618 |

## Entfernt
Keine.

## Belege (Auswahl)
- IGMP-Defaults auf IOS XE: Query Interval 60 s, Querier Timeout 2 × Query Interval (also 120 s), Default-Version IGMPv2: Cisco IGMP Config Guide XE 16, https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/ipmulti_igmp/configuration/xe-16/imc-igmp-xe-16-book/imc-customizing-igmp.html (betrifft 025, 030–032, 035)
- RPF bei ECMP: standardmäßig der PIM-Nachbar mit der höchsten IP; Lastteilung erst mit `ip multicast multipath`: https://www.cisco.com/en/US/docs/ios-xml/ios/ipmulti_optim/configuration/xe-3sg/imc_load_splt_ecmp.html (048)
- Auto-RP: Der Mapping Agent wählt den C-RP mit der höchsten IP: https://www.cisco.com/c/en/us/support/docs/ip/ip-multicast/41680-rp-announce.html (085)
- BSR: höchste Priorität, dann höchste IP. C-RP-Adv gehen per Unicast an den BSR, Bootstrap-Nachrichten hop-by-hop an 224.0.0.13: https://www.rfc-editor.org/rfc/rfc5059.html (086–088, 090, 095, 139)
- MSDP: TCP 639, SA-Periode 60 s, SAs müssen gecacht werden: RFC 3618 (119, 120, 125). Auf Cisco ist SA-Caching seit 12.1(7) Default und nicht abschaltbar: Cisco IOS 12.2 MSDP Command Reference (`ip msdp cache-sa-state`) und imc_msdp Config Guide
- Static RP und Auto-RP: Dynamisch gelernte Mappings haben Vorrang, außer mit `override`: https://www.cisco.com/c/en/us/support/docs/ip/multicast/118405-config-rp-00.html (081, 082)
- mroute-Flags (S, s, B, C, F, T, I, P, J, R, A): Cisco MFIB-Verifikationsguide und `show ip mroute` Command Reference, https://www.cisco.com/en/US/docs/ios-xml/ios/ipmulti_mfib/configuration/15-1s/Verifying_IPv4_Multicast_Forwarding_Using_the_MFIB.html (069–076)
- SSM-Filter für 232/8 bei Legacy-Routern: Der RP nimmt keine Register an (Register-Stop), dazu keine (*,G)-Joins und keine SAs für 232/8: RFC 4608 (108)
- IGMPv3: Reports an 224.0.0.22, keine Report Suppression, ein IGMPv2-Join entspricht EXCLUDE{}: RFC 3376 (024, 026–029, 109). IGMPv2: Leave an 224.0.0.2, Group-Specific Query an G, Querier ist die niedrigste IP: RFC 2236 (017–021, 029)
- PIM: IP-Protokoll 103, Hellos und Join/Prune/Assert an 224.0.0.13, Register und Register-Stop per Unicast; Assert-Reihenfolge ist Metric Preference (AD), dann Metrik, dann höchste IP; DR ist die höchste Priorität, dann die höchste IP: RFC 7761 (051–054, 060–066). PIM-DM mit Graft: RFC 3973 (055–057). BiDir mit DF pro Link und RP nach bester Metrik zum RP: RFC 5015 (110–118). SSM: RFC 4607

## Unsichere Punkte (belassen)
- 025/030/Lektion: Die Max Response Time von 10 s als Cisco-Default ist allgemein bekannt, steht aber auf der abgerufenen XE-16-Seite nicht ausdrücklich. Der Wert ist konsistent mit der Show-Ausgabe.
- 074: `RP 0.0.0.0` zusammen mit Flags SC ist realistisch, je nach Release erscheinen dabei aber z. B. auch SJC oder ein Dense-Fallback (D). Die Aussage „kein RP-Mapping“ bleibt eindeutig.
- 108: RFC 4608 formuliert, dass der RP keine Register für 232/8 annimmt. Register-Stop ist die praktische Umsetzung (Kurs/Cisco). Die Antwort ist unter den Optionen eindeutig.
- Lektion und alle 11 SVGs: keine Sachfehler gefunden (IGMP-Vergleich, Adressbereiche, MAC-Rechenweg, PIM-SM-Schritte, RP-Ermittlung, SSM, BiDir-DF, MSDP/Anycast-RP).
