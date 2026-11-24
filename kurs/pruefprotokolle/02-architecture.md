# Kapitelprüfung 02-architecture

Datum: 2026-11-24 · Checker (Schritt 7)

## Umfang
- Fragen: 122 geprüft (slg-ar-033…122 einzeln neu, slg-ar-001…032 gegengelesen; ein älteres Protokoll für 02 gab es nicht)
- Wissensdatei `encor-1.4.10/wissen/02-architecture.md` geprüft
- Lektion `encor-1.4.10/lektionen/02-architecture.json`: Seiten 6–8 einzeln, jede Tabellenzelle; Seiten 1–5 gegengelesen
- 9 SVGs in `encor-1.4.10/bilder/02-architecture/`: Inhalt + `[xml]`-Wohlgeformtheit (alle OK)
- Full-Mesh-Rechnungen nachgerechnet: B × (N − 2) mit N = 2B → 2/4 = 4, 3/6 = 12, 4/8 = 24, 5/10 = 40, 6/12 = 60; Zuwachs 3→4 Blöcke = 12 (Frage 077). Herleitung N·(N−2)/2 = B·(N−2) stimmt (079). Fragen 016, 077, 078, 079 und Tabellen in Wissen/Lektion/SVG 05 stimmen alle.
- `pruefen.ps1 -Kapitel 02-architecture` (ohne -Mischen): OK, 122 Fragen (single 77, multi 15, zuordnung 13, cli 9, luecke 8; Schwierigkeit 27/69/26)

## Korrekturen
| ID/Datei | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-ar-068 (Erklärung) | „summary-address gilt nur für externe Routen am ASBR“ zu absolut (geht auch am ABR für externe/NSSA-Routen) | „fasst nur externe (redistribuierte) Routen zusammen, typischerweise am ASBR“ | Cisco OSPF Command Reference (area range / summary-address), https://www3-realm.cisco.com/en/US/docs/ios-xml/ios/iproute_ospf/command/ospf-a1.html ; Cisco Press OSPF Command Handbook |
| slg-ar-069 (Erklärung) | „Queries enden an der Distribution“ ungenau: Die Summary begrenzt die Query-Domäne, weil der Core das Einzelpräfix nicht kennt und sofort antwortet | Erklärung umformuliert | EIGRP-Summarization/Query-Scoping (Cisco EIGRP Config Guide) |
| slg-ar-092 (Frage) | „VLAN 40 must exist on three access switches“ ließ Option „Routed Access mit VLAN 40 je Switch als eigenes Subnetz“ halbwegs zu | „VLAN 40, a single IP subnet, must span three access switches“ | Eindeutigkeit |
| Lektion Seite 5 | „ein Core hält sie [Links] konstant“ falsch – mit Core wächst die Zahl linear (2 Links pro Distribution-Switch) | Text korrigiert | Cisco Campus LAN/WLAN Design Guide: „N * 2 redundant links … down from N * (N-1) / 2“, https://www.cisco.com/c/en/us/td/docs/solutions/CVD/Campus/cisco-campus-lan-wlan-design-guide.html |
| bilder/04-l2-vs-l3.svg | STP-Blocking inkonsistent: bei einem VLAN über beide Access-Switches waren Access1→Dist2 und Access2→Dist1 blockiert (geht für eine Root-Bridge nicht) | Root an Dist 1 beschriftet, blockiert sind jetzt beide Uplinks zu Dist 2 | STP-Grundlagen (Alternate Port zum Nicht-Root) |
| Wissen (Fast/Perpetual PoE) | Ergänzt: Fast PoE ca. 25 s nach Stromwiederkehr, nur mit Perpetual PoE wirksam; Perpetual auch bei Crash/Upgrade (außer MCU-Upgrade) | ergänzt | Cisco „Deploying 90W Cisco UPOE+ with Catalyst 9000“, https://www.cisco.com/c/en/us/products/collateral/switches/catalyst-9300-series-switches/guide-c07-744813.html |
| Wissen (Core-Formel) | Hinweis auf CVD-Zählweise N×(N−1)/2 vs. N×2 ergänzt | ergänzt | CVD Campus LAN/WLAN (s. o.) |

## Entfernt
keine

## Belege für markierte Fragen (Auswahl)
- 044 UPOE+ 90 W PSE (PD ca. 71 W): UPOE+-Deployment-Guide (URL oben).
- 045/046 `power inline port perpetual-poe-ha` (Strom bleibt beim Reload), `power inline port poe-ha` = Fast PoE (Strom vor IOS-Boot nach Ausfall, setzt Perpetual voraus): UPOE+-Guide; Cisco PoE Config Guide „Perpetual PoE and Fast PoE“.
- 047/048 `power-deny` = unzureichendes Budget (%ILPOWER-5-ILPOWER_POWER_DENY), `show power inline`: UPOE+-Guide; Cisco TechNote 215636 Troubleshooting PoE.
- 060/061/072 ECMP nur bei gleichen Kosten, CEF-Lastverteilung; 071 routed P2P-Links ohne STP: CVD Campus („use both uplinks“ ohne STP-Blocking).
- 063 `ip ospf network point-to-point` (keine DR/BDR-Wahl): OSPF Command Reference.
- 064 `eigrp stub` Default = connected summary: EIGRP Command Reference / Config Guide (https://cisco.com/en/US/docs/ios-xml/ios/iproute_eigrp/configuration/xe-3sg/ire-cfg-eigrp.html).
- 068/069 `area range`, `ip summary-address eigrp`: Command References.
- 081 „three or more distributions → core“, 083/084/086 „< 25 APs“, „groups of 50 or fewer APs“, „dozens / hundreds“: CVD Campus LAN/WLAN (wörtlich bestätigt).
- 082 „> 15.000 Nutzer/Geräte“: nur in älterer CVD-Fassung (2016, SlideShare-Kopie) gefunden; aktuelle CVD nennt keine Zahl → kursbasiert, belassen.
- 089/090/021/022/020 Looped/Loop-free, GLBP nur non-looped, FHRP-Timer-Tuning = CPU: CVD (wörtlich).
- 093/094/095/097/098/099 Simplified Distribution, MEC, kein FHRP, `stackwise-virtual link 1` / `stackwise-virtual dual-active-detection`: CVD; Cisco TechNote 216537 Troubleshoot SVL (https://www.cisco.com/c/en/us/support/docs/switches/catalyst-9500-series-switches/216537-troubleshoot-svl-on-catalyst-9000-switch.html).
- 106 AWS Direct Connect, Azure ExpressRoute, Google Cloud Interconnect: Anbieter-/Vergleichsdokumentation.
- 113/114 Multicloud AWS: zwei SD-WAN-Edges (C8000V) in Transit-VPC + TGW, IPsec automatisch: Cisco SD-WAN Cloud OnRamp for IaaS White Paper (https://www.cisco.com/c/en/us/solutions/collateral/enterprise-networks/sd-wan/white-paper-c11-742817.html).
- 032/031 vQoE aus Verlust und Latenz, 0–10: Cisco TechNote 221041 Cloud OnRamp for SaaS.
- 121 Access-Layer-Funktionen (PoE, 802.1X/Port Security, VLAN): CVD.

## Unsichere Punkte
- 082 (15.000) nur kursbasiert/ältere CVD belegt.
- 089: STP-Kosten „4“ entsprechen der Short-Pathcost-Methode; bei `pathcost method long` wären es 20000 – für die Frage irrelevant.
- 113/114/Lektion 8: Ablauf nach Kursstand (Transit-VPC-Modell); neuere Releases bieten auch TGW-Connect/GRE und Cloud-WAN-Varianten.
- Cloud-OnRamp-„Secure SD-WAN“ als Use Case ist Kurs-Systematik (in Wissen unter Fehler/Ungenauigkeiten vermerkt); Fragen 115/116 bleiben kursnah.
