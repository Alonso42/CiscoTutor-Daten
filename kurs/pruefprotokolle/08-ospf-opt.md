# Prüfprotokoll 08-ospf-opt

Geprüft: 133 Fragen (slg-oo-001 bis -137, Lücken in der Nummerierung bei 114, 117, 120, 121 vom Writer), Lektion (7 Seiten, alle Tabellenzellen), Notizen. Abgleich mit 07-ospf.json.
Ergebnis: 0 entfernt, 133 verbleiben. `pruefen.ps1 -Kapitel 08-ospf-opt` → OK (auch 07-ospf → OK).

## Korrekturen

| ID | Problem | Änderung | Quelle |
|---|---|---|---|
| 042 | Gestützt nur auf „according to the course“; RFC 2328 nennt das Maximum, IOS-Verhalten war nicht erklärt | Frage auf „Cisco IOS default, compatible rfc1583 active“ umgestellt, Antwort bleibt 11 (Minimum). Erklärung: IOS-Default RFC 1583 = Minimum, RFC 2328 = Maximum, per `no compatible rfc1583`. Optionen in der Länge angeglichen | RFC 1583 Abschn. 3.5 („minimum cost“) https://www.rfc-editor.org/rfc/rfc1583.txt ; RFC 2328 Abschn. 3.5 („maximum cost“) https://www.rfc-editor.org/rfc/rfc2328.txt ; Cisco OSPF CR `compatible rfc1583` („restore the method used to calculate summary route costs per RFC 1583“, Default compatible) https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/iproute_ospf/command/iro-cr-book/ospf-a1.html ; https://networklessons.com/cisco/ccie-enterprise-infrastructure/how-to-configure-ospf-summarization ; https://itskillbuilding.com/networking/network/ospf/ospf-summarization/ |
| 07: slg-os-109 | Erklärung sagte „teuerstes Teilnetz“ (nur RFC 2328), widersprach dem IOS-Default aus 08-042 | Erklärung nennt jetzt beide Fälle (IOS-Default günstigstes, RFC 2328/`no compatible rfc1583` teuerstes) | wie oben |
| Lektion S. 4, Notizen | „Laut Kurs niedrigste Kosten“ ohne Einordnung | IOS-Default vs. RFC 2328 ergänzt | wie oben |
| 044 | Erklärung ok, richtige Option zu lang | Option gekürzt; Erklärung: Zahl = Summary-Metrik, im Lab 8 Teilnetze (also keine Anzahl) | Kursausgabe (Active(11) bei Teilnetzkosten 11) + https://kemot-net.com/blog/ospf-area-range-active-vs-passive-advertisment (Komponente [110/11] ↔ Active(11)) |
| 081 | Stamm verriet die Antwort („numbers them 5, 10, 15 … first entry ___“) | Stamm neu formuliert | Cisco-Doku: Sequenznummern automatisch in Fünferschritten (Suche „ip prefix-list increments of 5“) |
| 094 | Distraktor „ifIndex of the local interface“ irreführend (IOS verwendet den ifIndex als Interface-ID); Aussage „Adresse nicht im Neighbor-Eintrag“ falsch (show ipv6 ospf neighbor detail zeigt link-local) | Distraktor ersetzt (Instance-ID), richtige Option gekürzt, Erklärung korrigiert | RFC 5340 https://www.rfc-editor.org/rfc/rfc5340 |
| 100 | Behauptung „alte Interface-Befehle funktionieren zunächst weiter“ nicht belegt | Satz entfernt, Option gekürzt | Kursnotizen |
| 106 | richtige Option deutlich länger | gekürzt, Distraktoren angeglichen | RFC 5838 Instance-IDs 0–31 IPv6 UC, 64–95 IPv4 UC https://www.rfc-editor.org/rfc/rfc5838.txt |
| 107 | Erklärung „nehmen nicht an SPF teil“ ungenau | an Cisco-Doku angepasst: keine Nachbarschaft, weil AF-Bit fehlt; Hellos ohne AF-Bit werden verworfen | https://www.cisco.com/en/US/docs/ios-xml/ios/iproute_ospf/configuration/15-mt/ip6-route-ospfv3-add-fam.html ; RFC 5838 |
| 007, 010, 013, 017, 021, 023, 027, 035, 036, 038, 043, 045, 048, 049, 050, 053, 054, 056, 057, 061, 063, 064, 069, 088, 093, 101, 102 | richtige Option auffällig länger als Distraktoren | richtige Option inhaltsgleich gekürzt (Index unverändert) | – |

## Gezielt belegte Punkte (keine Änderung nötig)
- 003/132/Lektion S. 1: Kosten = Ref/BW ganzzahlig abgeschnitten (T1 = 64 statt 64,77 → kein Runden), Minimum 1; 40G bei Ref 100000 → 2; 25G → 4. Cisco OSPF FAQ (Formel, ip ospf cost überschreibt): https://www.cisco.com/c/en/us/support/docs/ip/open-shortest-path-first-ospf/9237-9.html
- 004/006: Link-Kosten 16 Bit, max. 65535 (Cisco FAQ oben); Kappung zu langsamer Links auf 65535 laut Kurs (Cisco-Doku nennt das Verhalten nicht explizit – unsicherer Punkt, aber kursgestützt).
- 043: `area range … cost` 0–16777215 (Cisco CR area range).
- auto-cost: 1–4294967 Mbit/s, Default 100 (Cisco CR).
- 010, 011, 048, 064: Logik/Rechnung geprüft, korrekt.
- 063: distribute-list in am ABR filtert nur die lokale RIB, Type-3 wird laut Kurs-Lab weiter erzeugt; Drittquellen bestätigen (z. B. https://lpmazariegos.com/2016/04/01/ospf-filtering-part-iii/, https://itskillbuilding.com/networking/network/ospf/ospf-abr-type-3-lsa-filtering/). Frage ist ausdrücklich auf das Lab bezogen.
- 050/051/055/059: area filter-list in/out laut Cisco CR („in: prefixes advertised to the specified area from other areas“, „out: … out of the specified area to other areas“).
- 074–080, 128: ge/le-Regel len < ge ≤ le ≤ 32, IOS-Fehlermeldung „Invalid prefix range … make sure: len < ge-value <= le-value“ (Cisco Community https://community.cisco.com/t5/switching/ip-prefix-list-ge-16-vs-le-32/m-p/4096096); ohne le bis 32, ohne ge ab Präfixlänge. Alle Treffer nachgerechnet.
- 089: IPv4-AF braucht IPv6 auf dem Link + IPv4-Adresse (Cisco OSPFv3 AF Guide).
- 098/137: Ref-lstype 0x2001 Router-LSA, 0x2002 Network-LSA, 0x2009 Intra-Area-Prefix, 0x0008 Link-LSA (RFC 5340 A.4.2/Anhang).
- 099: B-Bit = ABR, E = ASBR, V = Virtual-Link-Endpunkt (RFC 5340 A.4.3).
- 129: OSPFv3 direkt über IPv6 (Next Header 89), Link-Local-Quelle, Aktivierung pro Interface, Router-ID 32 Bit.

## Dubletten/Widersprüche zu 07-ospf
- 07-109 (Summary bei Flapping) vs. 08-041/125 (alle Teilnetze weg / Aussagen zur Range): unterschiedliche Aspekte, kein Duplikat; Widerspruch zur Summary-Metrik behoben (s. o.).
- 07-110 (distribute-list in, Wirkung) vs. 08-062/063/064: 08 prüft Show-Ausgabe, ABR-Fall und Black Hole – andere Szenarien, belassen.
- 07-094 (passive-interface default, CLI) vs. 08-024 (no passive-interface, CLI) und 08-023 (Troubleshooting): ergänzend, belassen.
- 07-083 (CLI Referenzbandbreite) vs. 08-001/002 (Rechnung): belassen.

## Unsichere Punkte
- 004: Kappung berechneter Kosten > 65535 auf 65535 nur durch Kurs belegt.
- 044: Bedeutung der Zahl in Active(x) nicht in Cisco-Doku beschrieben, aber durch zwei Ausgaben konsistent (Komponentenkosten = Wert in Klammern).
- 021: per-packet bei vom Router erzeugtem Verkehr (process switching) – Kursaussage, plattformabhängig.

## Wissen & Bilder (Checker, 2026-11-24)

Geprüft: wissen/08-ospf-opt.md (alle Faktenaussagen und Rechenbeispiele), bilder/08-ospf-opt/01–09. Alle 9 SVGs wohlgeformt, UTF-8 ohne BOM.

Rechnungen nachgerechnet (alle korrekt): Kostentabelle (Ref. 10^8/10^10/10^11: 64k → 1562/65535/65535, T1 → 64/6476/64766, Ethernet 10/1000/10000 …); SPF-Beispiel 14/22/30 und Alternativen 44/32/40; Discovery 8: 21 → 2001, mit cost 500: 1501/501/1001/1500/2000/2001, fwd 1500 (Default), fwd 2000 bzw. 2500 (BR-Netze); Discovery 9: /21 aus 192.168.16–23, /22 aus 10.33.4–7, [110/21] bei Active(11); Discovery 10: /60 aus 2001:DB8:0:220–22F, 75 → 211.

Korrekturen wissen/08-ospf-opt.md:
| Stelle | Problem | Änderung |
|---|---|---|
| Distribute-List, ACL-Satz | „ein Interface-ACL ändert keine Routing-Updates“ zu pauschal (eine eingehende ACL kann OSPF-Pakete verwerfen) | präzisiert: ausgehende ACLs filtern keinen selbst erzeugten Verkehr; eingehende ACL könnte nur ganze OSPF-Pakete verwerfen, keine einzelnen Routen |

Korrekturen Bilder:
- 02-spf-baum.svg: Fußzeile zu lang (ragte über Kasten/viewBox) → gekürzt.
- 03-tuning-lab.svg: GW-Beschriftung überlappte „Area 0 · 172.16.123.0/25“ und ragte aus dem Area-Kasten → zweizeilig unter die Area-Überschrift.
- 05-summary.svg: „1 × Typ 5: 10.33.4.0/22“ überlappte „bis 10.33.7.0/24“ → unter die Linie verschoben.
- 06-filter.svg: Fußzeile zu lang (über viewBox) → gekürzt.
- 09-v3-lab.svg: Beschriftungen Ser2/0 / Kosten und Eth0/1 wurden von den Linien durchkreuzt → verschoben.

Belegt: match ip route-source bei OSPF = Router-ID des LSA-Erzeugers (Advertising Router), nicht Next Hop (Cisco IOS Route-Map-Feature-Guide 12.0S https://www3-realm.cisco.com/en/US/docs/ios/12_0s/feature/guide/routmap.html; networklessons „Route-map matching OSPF router ID“). Summary-Kosten: RFC 1583 3.5 Minimum (IOS-Default compatible rfc1583), RFC 2328 Maximum.
Offen/unsicher (unverändert): Kappung berechneter Kosten > 65535 auf 65535 nur durch Kurs und Fremdhersteller-Doku (HPE) belegt, Cisco-Doku nennt nur 16-Bit-Feld/ip ospf cost 1–65535; Bedeutung der Zahl in „Active(11)“.
Fragen: keine auffällig falsch.