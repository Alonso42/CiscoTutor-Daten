# Kapitelprüfung 11-redundancy

Geprüft: 131 Fragen, Lektion (8 Seiten, alle Tabellenzellen), Notizen. Danach 130 Fragen, `pruefen.ps1 -Kapitel 11-redundancy` → OK (single 84, multi 13, cli 14, zuordnung 11, luecke 8; Schwierigkeit 32/68/30).

## Korrekturen
| ID | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-hr-074 | CLI `standby 10 version 2` ist falsch, denn `standby version {1\|2}` ist ein Interface-Befehl ohne Gruppennummer | Lösung jetzt `standby version 2`, Frage und Erklärung angepasst, "10" bleibt als Ablenker | https://www3-realm.cisco.com/en/US/docs/ios-xml/ios/ipapp_fhrp/command/fhp-s2.html ; https://www.cisco.com/en/US/docs/ios-xml/ios/ipv6/configuration/xe-3sg/ip6-fhrp.pdf |
| slg-hr-098 | In der richtigen Option stand "msec timers must be set on the backup too", Cisco sagt dazu aber etwas anderes: Backups akzeptieren keine msec-Werte und zeigen deshalb immer 1 s an | Richtige Option: "Expected; backups always display 1 second with msec timers"; Erklärung angepasst | https://www.cisco.com/en/US/docs/ios-xml/ios/ipapp_fhrp/configuration/15-e/fhp-15-e-book_chapter_0100.html |
| slg-hr-113 | Die Failover-Zeiten (<2 min / <30 s / <1 s) sind Kurswerte. Cisco-Dokumente nennen je nach Plattform andere Werte (z. B. RPR+ ca. 30 s, SSO 0–3 s) | Zeitangaben aus den Paaren entfernt, Erklärung um "plattformabhängig" ergänzt | https://www3-realm.cisco.com/en/US/docs/ios/12_0s/feature/guide/fs22rpr.html ; https://www.cisco.com/en/US/docs/ios-xml/ios/ha/configuration/xe-3s/ha-config-stateful-switchover.html |
| slg-hr-114 | Die Erklärung behauptete "RPR+ behält Portzustände", das ist nicht belegt | Umformuliert: Module werden nicht neu geladen, L2/L3-Funktionen starten erst nach dem Wechsel | wie oben |
| Lektion S. 2 | Preempt-Delay-Faustregel "150 %" ist nicht offiziell belegt | Umformuliert: Delay > Bootzeit, 150 % ausdrücklich als Kurs-Faustregel gekennzeichnet | Cisco HA Campus DG (Delay > Bootzeit) |
| Lektion S. 7 | Konkrete Zeiten (<2 min, <30 s, <1 s, Cat 9400 <200 ms) sind nicht belegt | Ersetzt durch relative Angaben, die Spalte heißt jetzt "plattformabhängig" | wie 113 |
| Notizen | `standby <grp> version 2` | Korrigiert zu `standby version 2` | wie 074 |

## Entfernt
| ID | Grund |
|---|---|
| slg-hr-031 | Die Rechenfrage beruht auf der "Bootzeit + 50 %"-Regel aus dem Kurs. In der Cisco-Doku ist sie nicht belegt, Foren nennen widersprüchlich 50 % bzw. 150 %. |

## Gezielt belegt (ohne Änderung)
- GLBP 008–012, 071, 072, 112: bis 4 AVF pro Gruppe, 1024 Gruppen/Interface (0–1023), Default round-robin, vMAC 0007.B400.XXYY, Hello an 224.0.0.102 über UDP 3222. Quellen: https://www.cisco.com/en/US/docs/ios-xml/ios/ipapp/configuration/15-0m/Configuring_GLBP.html ; https://www.cisco.com/c/en/us/support/docs/switches/catalyst-6500-series-switches/81565-glbp-cat65k.html
- HSRP: Klartext-Auth max. 8 Zeichen (067); v2 vor IPv6 nötig, 224.0.0.102 erlaubt CGMP parallel, 6-Byte-Identifier (075–077); IPv6-vMAC 0005.73A0.0000–0FFF, FF02::66, UDP 2029 (070, 079); `standby 1 ipv6 autoconfig` (078); nicht konfigurierte Timer und VIP werden aus den Hellos gelernt (039, 081, vgl. RFC 2281); Gruppen v1 0–255, v2 0–4095; vMACs nachgerechnet (018: 0x32 = 50, 019: 300 = 0x12C, 020/095: 20 = 0x14). Quelle: Cisco FHRP Command Reference fhp-s2, RFC 2281.
- VRRP: Skew/Master Down nachgerechnet (090: 3,609 s; 091: 3,570 s; 092), Owner 255 (089), Preempt Default an (093/105), RFC 3768 ohne Auth und TTL 255 (102/103). VRRPv3: IPv4+IPv6, Zentisekunden, `fhrp version vrrp v3`, address-family, `address … primary`, FF02::12 (106–109). Quellen: RFC 3768, RFC 5798/9568, Cisco VRRPv3 Protocol Support.
- Tracking/Preempt nachgerechnet: 049 (90 < 100), 050 (105 > 100), 051 (105 bzw. 90), 052, 057, 058, 105.
- Switch-HA: Fallback auf RPR bei unterschiedlichen Images (115) ist für Cisco IOS SSO belegt (fssso20s, Forenmeldung PFREDUN VERSION_MISMATCH). Außerdem belegt: `mode sso`, `nsf ietf`/`nsf cisco`, NSF-capable/-aware, NSR (116–122).
- StackWise 125–131: 9300-Stack mit max. 8 Switches, StackWise Virtual mit genau 2 Switches über SVL, DAD/Recovery-Mode, MEC, keine Neuwahl des Active-Switches beim Hinzufügen.

## Unsichere Punkte
- 101: Das genaue Logformat `%VRRP-4-BADAUTHTYPE … type 0, expected 254` stammt aus dem Kurslab und wurde nicht online verifiziert. Die Antwortlogik (R2 ohne Auth, beide werden Master) ist plausibel.
- 115: Für Catalyst 9400 gibt es keine wörtliche Aussage im 9400-HA-Guide, belegt ist das Verhalten aber allgemein für IOS SSO.

## Wissen & Bilder (Checker 2026-11-24)
Geprüft: wissen/11-redundancy.md (alle Abschnitte), bilder/11-redundancy/01–10 (Inhalt jeder Beschriftung, [xml] wohlgeformt, kein BOM, Skript-Check Text/Text, Text/Linie, viewBox: alle OK). Rechnungen mit `python -I` nachgerechnet: Skew/MDI (254→3,008; 200→3,219; 110→3,570; 100→3,609; 1→3,996 s; Balkenlängen im Bild passen), VRRPv3 156×100/256 = 60,9 cs, Tracking 110−20=90, 110−10=100, 120−15/−30, vMACs v1/v2/VRRP (ac01, ac14, ac32, acff, f001, f014, f12c, ffff, 0101, 010a).
Korrekturen:
- Wissen: RFC 9568 (ersetzt 5798, "Active Router") ergänzt; VRRPv3-Skew präzisiert (60,9 cs, ganzzahlig 60), Defaults aus RFC 9568 (100 cs, Preempt True, vMAC IPv4/IPv6). Quelle: https://www.rfc-editor.org/rfc/rfc9568.html
- Wissen: HSRP-Timerbereich "1–255" → Hello 1–254, Hold bis 255. Quelle: Cisco-Konfigurationsguides (3825, 6500; CLI `<1-254>`/`<2-255>`), vgl. https://networklessons.com/ip-services/hsrp-timers
- Wissen: HSRP-Priorität präzisiert (8-Bit-Feld 0–255; IOS-Guides nennen konfigurierbar 1–255).
- Wissen: SVL-DAD präzisiert (Recovery Mode schaltet alle Ports außer SVL/DAD ab, Reload nach SVL-Wiederherstellung). Quelle: Cat9500 SVL Config Guide (zitiert in https://community.cisco.com/t5/switching/9500-stackwise-virtual-recovery-mode/td-p/4409124)
- Bild 02-fhrp-idee: Interface-Endungen getauscht (R1 .3, R2 .2), passend zur Lab-Adressierung R1 = .3, R2 = .2.
- Bild 08-fhrp-vergl: VRRP-Standard um RFC 9568 ergänzt.
Belegt ohne Änderung: HSRP Default 100, track decrement 10, preempt aus, v1 0000.0C07.ACxy/224.0.0.2, v2 0000.0C9F.F000–FFF/224.0.0.102, Gruppen 0–255/0–4095 (https://www.cisco.com/en/US/docs/ios-xml/ios/ipapp_fhrp/configuration/15-0s/fhp-hsrp.html); VRRP 1–254/255/0, Preempt Default (RFC 9568).
Offen: Die HSRP-Prioritätsuntergrenze (0 oder 1) ist uneinheitlich dokumentiert (IOS-Guides 1–255, NX-OS/Literatur 0–255); Lektion und Bilder 03/08 nennen weiter "0–255" – prüfungsrelevant ist nur Default 100/höher gewinnt. Command Reference fhp-s2 war per WebFetch nicht abrufbar (504).