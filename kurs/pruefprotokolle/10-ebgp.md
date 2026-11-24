# Prüfprotokoll 10-ebgp

Geprüft: 136 Fragen (encor-1.4.10/fragen/10-ebgp.json) und die Lektion (7 Seiten, alle Tabellenzellen). Entfernt: 0. Verbleibend: 136.
pruefen.ps1 -Kapitel 10-ebgp (ohne -Mischen): OK.

## Quellen
- Cisco BGP Best Path Selection Algorithm: https://www.cisco.com/c/en/us/support/docs/ip/border-gateway-protocol-bgp/13753-25.html (Reihenfolge Weight > LP > lokal originiert (+AIGP) > AS_PATH > Origin > MED > eBGP vor iBGP > IGP-Metrik > Multipath > ältester eBGP-Pfad > Router-ID > Cluster-List > Nachbaradresse; ein fehlender MED zählt als 0, mit missing-as-worst als 4294967294; MED wird nur bei gleichem Nachbar-AS verglichen; Bedingungen für den Schritt „ältester Pfad“)
- RFC 4271: https://www.rfc-editor.org/rfc/rfc4271.txt (Hold Time 0 oder >= 3 s, Kollision: die Verbindung des Speakers mit dem höheren BGP Identifier bleibt, Partial-Bit, unbekannte non-transitive Attribute werden verworfen, Error Codes 1–6, Bad Peer AS, Malformed AS_PATH, KEEPALIVE = 19 Byte, MED wird nicht an weitere AS gegeben, AGGREGATOR = AS + IP, ATOMIC_AGGREGATE: Empfänger darf das NLRI nicht spezifischer machen)
- RFC 6996: https://www.rfc-editor.org/rfc/rfc6996.txt (privat 64512–65534 und 4200000000–4294967294)
- RFC 7300: https://www.rfc-editor.org/rfc/rfc7300.txt (65535 und 4294967295 reserviert)
- RFC 6793: https://www.rfc-editor.org/rfc/rfc6793.txt (AS_TRANS 23456, AS4_PATH optional transitive)
- Cisco 4-Byte ASN / bgp asnotation dot: https://cisco.com/en/US/docs/ios-xml/ios/iproute_bgp/configuration/xe-3sg/irg-4byte-asn.html
- RIB-failure: https://www.cisco.com/c/en/us/support/docs/ip/border-gateway-protocol-bgp/213286-understand-bgp-rib-failure-and-the-bgp-s.html
- maximum-prefix / Idle (PfxCt): https://www.cisco.com/c/en/us/support/docs/ip/border-gateway-protocol-bgp/25160-bgp-maximum-prefix.html
- Weight 0–65535, 32768 lokal, Router-ID: höchste Loopback: https://cisco.com/warp/public/459/25.shtml
- eBGP TTL 1 / ebgp-multihop / disable-connected-check: Cisco BGP Command Reference (neighbor ebgp-multihop) sowie Cisco-Community-Threads; zu iBGP TTL 255 gibt es Cisco Press (CCNP ROUTE) und Sekundärquellen, eine offizielle Cisco-Seite habe ich dazu nicht gefunden.
- FSM-Zustände: RFC 4271 Kap. 8 und networklessons „BGP Neighbor Adjacency States“
- OutQ/InQ: Hersteller-Dokus mit identischer Spaltenlogik (IP Infusion, Dell); eine Cisco-Definition habe ich nicht gefunden.

## Korrekturen
| ID | Problem | Änderung |
|---|---|---|
| slg-bg-090 | Distraktor „The aggregate must not be split by downstream routers“ ist nach RFC 4271 5.1.6 eigentlich richtig (das NLRI darf nicht spezifischer gemacht werden), damit hatte die Frage zwei richtige Antworten | Distraktor ersetzt durch „The aggregate contains exactly one component route“, Erklärung ergänzt |
| slg-bg-001, 003, 004, 006, 007, 015, 016, 017, 021, 028, 029, 033, 039, 040, 043, 044, 056, 057, 061, 066, 072, 074, 076, 078, 081, 089, 091, 092, 094, 098, 101, 104, 105, 106, 112, 124, 130, 132 | Die richtige Option war auffällig länger als die Distraktoren (oft das 1,4- bis 2,5-fache) | Optionen auf ähnliche Länge umformuliert. Inhalt und richtig-Index bleiben gleich, bei 098 wurde zusätzlich ein mehrdeutiger Distraktor ersetzt („does not create an AS_PATH“ → „strips the local AS“) |
| slg-bg-104 | Erklärung an die gekürzte Option angepasst | – |
| Lektion S. 1 | Der Bereich 1–64495 schloss AS_TRANS 23456 ein, obwohl 23456 eigens als AS_TRANS geführt wird | „außer 23456“ ergänzt |
| Lektion S. 3 | Eine falsche Peer-ASN wurde dem Zustand OpenConfirm zugeordnet. Geprüft wird das empfangene OPEN aber in OpenSent | Text korrigiert (OpenSent: auf OPEN warten, bei falscher ASN OPEN Message Error/Bad Peer AS; OpenConfirm: OPEN akzeptiert, auf KEEPALIVE warten) |

## Gezielt geprüft (alles korrekt)
- 010–014 und 118: ASN-Bereiche, asdot-Umrechnung (2.10 = 131082, 65546 = 1.10) und AS_TRANS stimmen.
- 030, 031, 121 (FSM), 033 (PfxCt), 108 (Kollision), 109, 122 (Hold Time) und 127 (Error Codes) stimmen.
- 035 (disable-connected-check), 036 und 041 (TTL), 038–040 (Next Hop, Split Horizon), 124 (allowas-in/as-override) und 016 (RIB-failure) stimmen.
- 065, 068–082 und 094 (Best-Path-Reihenfolge) stimmen. Bei 072 gewinnt der ältere eBGP-Pfad, weil MED nicht verglichen wird und die IGP-Metrik gleich ist.
- 084–088 (Attributklassen) stimmen, ebenso 095 (fehlender MED = 0).
- 100–105, 114, 123, 126, 128, 133 und die CLI-Fragen 027, 045–054 stimmen.

## Unsichere Punkte
- slg-bg-126: Die OutQ-Definition ist nur über Dokus anderer Hersteller mit identischer Spaltenlogik belegt. Ich halte sie für unkritisch.
- slg-bg-036 und 041 (iBGP TTL 255): Belegt durch Cisco Press und Sekundärquellen, eine Cisco-Doku-Seite habe ich nicht gefunden.
- slg-bg-003 und 004 (Fenster bei OSPF/EIGRP, gebündelte Updates): vereinfachte Kursaussagen, als Konzeptfragen vertretbar.
- Lektion S. 6: Der Ablauf lässt die Schritte Multipath, AIGP und Cluster-List aus. Für ENCOR ist diese Vereinfachung vertretbar, die Reihenfolge der genannten Schritte stimmt mit Cisco 13753 überein.

## Wissen & Bilder

Geprüft: `encor-1.4.10/wissen/10-ebgp.md` (jede Faktenaussage) und die 9 SVGs in `bilder/10-ebgp/`.

### Korrekturen Wissensdatei
| Stelle | Problem | Änderung | Quelle |
|---|---|---|---|
| Fehlertabelle Versionsfeld | Die Aussage „BGP-4 handelt die Version nicht aus“ war zu absolut | Präzisiert: Das OPEN enthält nur die eigene Version. Bei nicht unterstützter Version kommt eine NOTIFICATION Unsupported Version Number, deren Datenfeld die höchste lokal unterstützte Version unterhalb der angebotenen nennt. Danach ist ein neuer Versuch möglich | RFC 4271 Kap. 6.2 https://www.rfc-editor.org/rfc/rfc4271.txt |
| Fehlertabelle OPEN-Parameter | Quelle ergänzt | RFC 4271 (Auth-Parameter entfernt, OPEN-Subcode 5 „Deprecated“) und RFC 5492 (Capabilities) | RFC 4271, RFC 5492 |

Bestätigt: KEEPALIVE ist BGP-Nachrichtentyp 4 (1 OPEN, 2 UPDATE, 3 NOTIFICATION, 4 KEEPALIVE) und hat nur den 19-Byte-Header. MED „MAY be propagated over IBGP“ und „MUST NOT be propagated to other neighboring ASes“ (RFC 4271 5.1.4), dazu passen die leere Metric-Spalte für 10.0.2.0/24 und Metric 0 für das von SP1 originierte Netz. Ebenfalls bestätigt sind die ASN-Bereiche nach RFC 6793/6996/7300/5398, die Best-Path-Reihenfolge nach Cisco 13753 (siehe Quellen oben), Hold Time 0 oder ≥ 3 s, die Error Codes 1–6, AD 20/200, Weight 32768 lokal und LOCAL_PREF 100.

### Bilder
- Alle 9 SVGs sind wohlgeformt und als UTF-8 ohne BOM gespeichert. Das Skript fand keinen Text außerhalb der viewBox und keine Text-Text-Überlappung. Die Text-Linien-Treffer in 01, 02 und 06 sind Fehlalarme: Es sind die Knotenbeschriftungen, und die Linien liegen unter den gefüllten Kreisen bzw. Ellipsen.
- `08-attribute.svg`: Die Fußzeile „MED: eigenes AS wünscht sich beim Nachbarn den Eingang“ widersprach der Grafik, die den MED vom Nachbar-AS ins eigene AS zeigt. Neu: „MED: Nachbar-AS nennt uns seinen bevorzugten Eingang (niedriger besser)“.
- 01–07 und 09 sind inhaltlich korrekt. Geprüft wurden z. B. PfxRcd 2 auf R1, [20/0] auf SP1, die Path-Vector-Pfade und der FSM-Ablauf mit Bad Peer AS in OpenSent.

### Fragen
Kein Widerspruch zu den geprüften Fragen (u. a. slg-bg-019, 059, 066, 072, 095, 116 und 127 geprüft). Keine Frage behandelt die Versionsverhandlung.