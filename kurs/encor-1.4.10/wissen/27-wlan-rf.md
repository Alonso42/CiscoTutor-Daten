# Explaining Wireless Principles

Quelle: ENCOR 1.4.10 Student Guide, Seiten 296–302 (Intro 295, Summary Challenge 303 und Answer Key 304 nicht verwendet)

Topics: ENCOR-LEGACY-WLAN (Wireless ist im ENCOR-Blueprint v1.2 kein eigenes Thema mehr); reine CCNA-Grundlagen zusätzlich unter CCNA2-1.5.a (Standards/Bänder/Kanäle) und CCNA2-1.5.b (RF/Signal).

> Abgrenzung: RSSI/SNR-Grundwerte, Kanalüberlappung 1/6/11, CCI/ACI, Non-Wi-Fi-Interferer, DFS, halbe Wellenlänge bei Antennenabstand und Sticky Clients stehen in Kapitel 18 (18-wlan-ts). Split MAC, CAPWAP-Details, AP-Modi, Bridge/Mesh (RAP/MAP, AWPP) in Kapitel 15/16. Roaming (Mobility Groups, Anchor/Foreign) im Folgekapitel "Exploring Wireless Roaming and Location Services". Dieses Kapitel vertieft die **Physik und Mathematik** (Wellen, dB, EIRP, Link-Budget, Antennen) und die **802.11-PHY-Standards**.

## RF Principles (Seite 296)

### Elektromagnetische Welle, Frequenz, Wellenlänge
- Funkwelle = elektromagnetisches Feld, das sich von einem Sender aus ausbreitet; Licht ist ebenfalls elektromagnetische Energie. WLAN nutzt nicht sichtbare Wellen im Mikrowellenbereich.
- Ausbreitung immer mit Lichtgeschwindigkeit c ≈ 300.000 km/s = 3 × 10^8 m/s (im Material minimal langsamer).
- **Frequenz f** = Zyklen pro Sekunde, Einheit Hertz (Hz). 1 kHz = 10^3, 1 MHz = 10^6, 1 GHz = 10^9 Zyklen/s.
- **Wellenlänge λ (lambda)** = Strecke, die die Welle während eines Zyklus zurücklegt (gemessen in Metern).
- Grundformel: **λ = c / f** bzw. **f = c / λ**. Höhere Frequenz → kürzere Wellenlänge.

| Frequenz | Wellenlänge (gerundet) |
|---|---|
| 750 kHz (AM-Radio) | 400 m |
| 900 MHz | 33 cm |
| 2,4 GHz | 12,5 cm |
| 5 GHz | 6 cm |
| 6 GHz | 5 cm |
| 60 GHz | 5 mm |

- Merkhilfe: λ[cm] ≈ 30 / f[GHz].
- Niedrigere Frequenzen reichen weiter und durchdringen Hindernisse besser (Analogie Bass/Trommeln einer lauten Musikanlage hört man zuerst). 2,4-GHz-Zellen sind deshalb bei gleicher Leistung größer als 5- oder 6-GHz-Zellen.

### Amplitude, Phase, Modulation
- **Amplitude** = Stärke/Energie des Signals (Höhe der Welle). Mehr eingespeiste Energie pro Zyklus → größere Amplitude.
- **Aktive Verstärkung (active amplification)**: Sendeleistung wird erhöht (Verstärker). **Passive Verstärkung (passive amplification)**: Antenne bündelt die Energie in eine Richtung (Antennengewinn). **Dämpfung (attenuation)**: Abnahme von Leistung/Amplitude.
- Zu schwaches Signal → beim Empfänger nicht lesbar; zu starkes Signal → teuer, kann Empfänger übersteuern; Regulierung begrenzt die erlaubte Leistung.
- **Phase**: Position im Zyklus (0–360°). Zwei gleiche Wellen in Phase addieren ihre Amplituden (doppelte Amplitude = vierfache Leistung = +6 dB), um 180° versetzt löschen sie sich aus. Unkorrelierte Signale (z. B. Rauschen + Störer) addieren dagegen ihre Leistungen in mW (zwei gleich starke = +3 dB).
- Modulation = Veränderung einer Welleneigenschaft, um Daten zu kodieren: **AM** (Amplitude), **FM** (Frequenz), **PM/PSK** (Phase). **QAM** kombiniert Amplitude und Phase. WLAN nutzt BPSK, QPSK und QAM-Stufen (siehe IEEE-Abschnitt).

### Free Space Path Loss (FSPL)
- Abnahme der Signalstärke allein durch die Entfernung, ohne Hindernis ("free"). Ursache ist nicht die Distanz an sich, sondern: (1) die Energie verteilt sich auf eine immer größere Kugeloberfläche, (2) die Empfangsantenne hat eine begrenzte Fläche und fängt nur einen Bruchteil auf.
- Faustregeln: **doppelte Entfernung ≈ +6 dB Verlust** (Leistung auf ein Viertel), **zehnfache Entfernung = +20 dB**. Doppelte Frequenz ≈ +6 dB (bei isotropen Antennen, weil die effektive Antennenfläche mit λ² schrumpft).
- Formel (eigene Ergänzung): FSPL[dB] = 20·log10(d[km]) + 20·log10(f[MHz]) + 32,44. Beispiele: 1 m bei 2,437 GHz ≈ 40 dB, 100 m ≈ 80 dB; 1 m bei 5,18 GHz ≈ 47 dB → 5 GHz hat bei gleicher Distanz ca. 6,5 dB mehr FSPL als 2,4 GHz.
- "Path loss" (ohne "free") schließt zusätzlich Hindernisse, Absorption usw. ein.

### RF-Phänomene (eigene Ergänzung, Prüfungsstoff CCNA/CWNA)
| Phänomen | Was passiert | Typische Ursache/Folge |
|---|---|---|
| Reflexion (reflection) | Welle prallt an glatter, großer Oberfläche ab | Metall, Glas mit Metallbeschichtung, Wasserflächen → Multipath |
| Refraktion (refraction) | Welle wird beim Übergang zwischen Medien unterschiedlicher Dichte gebrochen (Richtungsänderung) | Glas, Luftschichten mit Temperatur-/Feuchteunterschieden (Außenlinks) |
| Absorption | Material nimmt Energie auf und wandelt sie in Wärme → Dämpfung | Wasser, Menschen, Pflanzen, Beton; steigt mit der Frequenz |
| Streuung (scattering) | Welle wird an rauen/unebenen Oberflächen oder vielen kleinen Partikeln in viele Richtungen verteilt | Staub, Maschendrahtzaun, Laub, Kies |
| Beugung (diffraction) | Welle biegt sich um die Kante eines Hindernisses | hinter dem Hindernis entsteht ein "RF-Schatten" |
| Multipath | mehrere Kopien (direkt + reflektiert) kommen zeitversetzt an | bei SISO: Upfade, Downfade, Nulling, Datenkorruption (ISI); MIMO nutzt Multipath für Spatial Multiplexing |

- **Fresnel-Zone** (eigene Ergänzung): ellipsenförmiger Raum um die Sichtlinie einer Richtfunkstrecke. Ist die erste Fresnel-Zone zu mehr als ca. 40 % blockiert (d. h. weniger als 60 % frei), wird der Link unzuverlässig, auch wenn optische Sichtverbindung besteht. Radius in der Mitte: r ≈ 8,66 · √(D[km] / f[GHz]) Meter (z. B. 1 km, 2,4 GHz → ca. 5,6 m; 60 % → ca. 3,4 m). Größere Distanz → größere Zone; höhere Frequenz → kleinere Zone. Bäume, Gebäude oder Erdkrümmung bei langen Links beachten.

### RSSI, Noise, SNR, SINR
- **RSSI**: empfangene Signalstärke, meist in dBm (negativ, näher an 0 = stärker). Herstellerabhängige Rohwerte (0–255, oft max. 100 oder 60) werden in dBm umgerechnet – RSSI verschiedener Karten ist daher nicht direkt vergleichbar. **RCPI** (802.11k, Received Channel Power Indicator) ist der standardisierte Messwert.
- **Noise floor**: Hintergrundrauschen in dBm, typisch ca. −90 bis −95 dBm (Kurs: "typisch −95"). Niedriger (negativer) ist besser.
- **SNR = RSSI − Noise** (dBm − dBm = dB). Beispiel −55 − (−95) = 40 dB. Faustregel Kurs: > 20 dB gut; Cisco-Voice-Empfehlung am Zellrand −67 dBm und ≥ 25 dB (siehe Kap. 18).
- **SINR** = Signal / (Interferenz + Rauschen). Leistungen müssen in mW addiert werden, nicht in dB! Beispiel: Signal −65 dBm, Rauschen −95 dBm, Interferenz −80 dBm → Summe ≈ −79,9 dBm → SINR ≈ 15 dB. Kurs: SINR ≥ 25 dB für Voice.
- Höhere Datenraten (höhere QAM-Stufe) brauchen mehr SNR; sinkt das SNR, wechselt der Client auf eine niedrigere MCS (Rate Shifting/Dynamic Rate Switching).

## Watts and Decibels (Seite 297)
- **Watt (W)**: absolute Leistung, 1 W = 1 Joule pro Sekunde. WLAN-Sender arbeiten im mW-Bereich (typischer AP ca. 100 mW = 20 dBm; abhängig von Land/Indoor/Outdoor).
- **Dezibel (dB)**: logarithmisches, **relatives** Verhältnis zweier Leistungen: dB = 10·log10(P1/P2).
- **Regel der 3 und 10**: +3 dB ≈ ×2, −3 dB ≈ ÷2, +10 dB = ×10, −10 dB = ÷10, 0 dB = gleich. Daraus: +6 dB = ×4, +9 dB = ×8, +20 dB = ×100, +13 dB = ×20, +7 dB = ×5 (10 − 3).
- **dBm**: Leistung relativ zu **1 mW** → absolute Größe. Formeln: P[mW] = 10^(P[dBm]/10); P[dBm] = 10·log10(P[mW]).

| dBm | mW | dBm | mW |
|---|---|---|---|
| −30 | 0,001 (1 µW) | 13 | 20 |
| −20 | 0,01 | 14 | 25 |
| −10 | 0,1 | 16 | 40 |
| −3 | 0,5 | 17 | 50 |
| 0 | 1 | 20 | 100 |
| 3 | 2 | 23 | 200 |
| 6 | 4 | 24 | 250 |
| 7 | 5 | 27 | 500 |
| 10 | 10 | 30 | 1000 (1 W) |
| | | 36 | ≈ 4000 (4 W) |

- Rechenweg dBm → mW: Wert als Summe von 10ern und 3ern zerlegen, bei 1 mW beginnen. 36 dBm = 10+10+10+3+3 → 1·10·10·10·2·2 = 4000 mW. 27 dBm = 30 − 3 → 500 mW.
- Rechenweg mW → dBm: Wert als Produkt von 2ern und 10ern zerlegen. 40 mW = 10·2·2 → 10+3+3 = 16 dBm. 50 mW = 100/2 → 20 − 3 = 17 dBm.
- Merke: dB + dB = dB, dBm + dB = dBm (Gewinn/Verlust auf absolute Leistung), dBm − dBm = dB (z. B. SNR). dBm + dBm ist **keine** sinnvolle Rechnung in dB – Leistungen addiert man in mW (zwei gleich starke, unkorrelierte Signale ergeben +3 dB, z. B. 2 × −70 dBm = −67 dBm).
- **dBi**: Antennengewinn relativ zum (theoretischen) **isotropen Strahler** (punktförmig, strahlt kugelförmig gleichmäßig; existiert nicht real). **dBd**: relativ zu einem **Dipol** (Halbwellendipol hat 2,14 dBi). **dBi = dBd + 2,14**. Nur gleiche Einheiten vergleichen.
- Antenne ist **passiv**: sie erzeugt keine Energie, sondern bündelt sie (Ballon-Analogie: gleiche Luftmenge, nur anders geformt).
- **EIRP** (Effective Isotropic Radiated Power) = Leistung, die ein isotroper Strahler abstrahlen müsste, um in der Hauptstrahlrichtung dieselbe Leistungsdichte zu erzeugen:
  **EIRP [dBm] = Sendeleistung [dBm] − Kabel-/Steckerverlust [dB] + Antennengewinn [dBi]**.
  Kursbeispiel: 17 dBm − 3 dB + 28 dBi = 42 dBm; bei einem FCC-EIRP-Limit von 36 dBm muss Leistung reduziert oder eine andere Antenne gewählt werden.
- Regulierung: Behörden (FCC, ETSI usw.) begrenzen Sendeleistung **und** EIRP; Installateur muss Antenne + Leistung passend wählen. (Beispielwert: 2,4 GHz Europa 20 dBm = 100 mW EIRP; FCC 2,4 GHz Punkt-zu-Mehrpunkt 36 dBm EIRP.)
- **Link-Budget** (eigene Ergänzung): Empfangspegel = EIRP − Pfadverlust (FSPL + Hindernisse) + Empfangsantennengewinn − Empfangskabelverlust. Muss über der Empfängerempfindlichkeit (receiver sensitivity) der gewünschten Datenrate liegen; die Differenz ist die **Fade Margin** (typisch 10–20 dB Reserve für Außenlinks).

## Antenna Characteristics (Seite 298)
- Zwei Familien: **omnidirektional** (360° in der Horizontalen) und **direktional** (bündeln in eine Richtung). Beide strahlen dieselbe Gesamtenergie ab; die direktionale hat in Hauptrichtung mehr Gewinn (höherer dBi).
- **Beamwidth**: Öffnungswinkel der Hauptkeule, gemessen zwischen den Punkten, an denen die Leistung um 3 dB (Halbwert) gefallen ist. Schmaler Strahl → höherer Gewinn → größere Reichweite in diese Richtung (Taschenlampen-Analogie).
- **Strahlungsdiagramme**: **H-Plane / Azimut** = Draufsicht (vorne/hinten/links/rechts); **E-Plane / Elevation** = Seitenansicht (vorne/hinten/oben/unten). Zusammen erlauben sie die 3D-Vorstellung.
- **Omni**: in der Azimut-Ebene rund, in der Elevation "Donut". Mehr Gewinn = flacherer, dünnerer Donut (weniger Abdeckung direkt unter/über der Antenne, mehr Reichweite seitlich).
  - Dipol (dual-band, "Rubber Duck"): 2,14 dBi bzw. ca. 2 dBi (2,4 GHz) / 4 dBi (5 GHz) im Kursbeispiel; Indoor, "One-floor coverage".
  - Integrierte Antennen typischer Office-APs: ca. 4 dBi (Kurs).
  - High-Gain-Omni für Decke: 5,2 dBi (≈ doppelt so stark wie Dipol, da +3 dB); Montage nach Herstellervorgabe (nach unten zeigend wegen Polarisation und Pattern-Form).
  - Mast-Omni 12 dBi: dünner Donut, große Reichweite, ≈ 4,8 × (Kurs "mehr als viermal") so stark wie 5,2 dBi.
- **Direktional**:
  - **Patch** (flach, Wandmontage): einige dBi (Kursbild 4 dBi bei 2,4 GHz / 3 dBi bei 5 GHz; marktüblich ca. 6–9 dBi); strahlt etwas nach hinten; gut für lange Räume, über Türen.
  - **Yagi (Yagi-Uda)**: Kammstruktur im Zylinder, ca. 13–13,5 dBi; schmale Keule, Neben- (side lobes) und Rückkeulen ("butterfly effect" laut Kurs); Korridore, Lagerhallen; Polarisation per Markierung beachten.
  - **Parabolantenne (dish)**: sehr hoher Gewinn (Kurs 21 dBi), sehr schmaler Strahl; Punkt-zu-Punkt-Außenlinks.
  - **Sektorantenne** (eigene Ergänzung): direktional mit z. B. 60–120° Öffnung, Outdoor/Stadien.
- **Polarisation** (eigene Ergänzung): Ausrichtung des elektrischen Feldes (vertikal/horizontal). Sender- und Empfangsantenne müssen gleich polarisiert sein; 90° Fehlausrichtung (Cross-Polarization) kostet theoretisch sehr viel Signal (in der Praxis oft 20 dB und mehr; indoor durch Reflexionen weniger). Indoor üblich vertikal.
- **Antenna Diversity** (SISO): ein Radio, zwei Antennen, es wird die jeweils bessere gewählt (nicht gleichzeitig).
- Rekord-Fernverbindung WLAN laut Kurs: 382 km mit Parabolantennen.

## IEEE Wireless Standards (Seite 299)
IEEE 802.11 definiert Layer 1 und Layer 2 (PHY und MAC) des WLAN. Der Kurs spricht vom "ISM-Band"; genauer ist 2,4 GHz ISM, 5 GHz größtenteils U-NII, 6 GHz U-NII-5 bis -8.

| Standard | Wi-Fi-Name | Jahr | Band | Verfahren | Kanalbreite max. | max. Modulation | Spatial Streams | max. PHY-Rate |
|---|---|---|---|---|---|---|---|---|
| 802.11 (Original) | – | 1997 | 2,4 GHz | FHSS/DSSS, IR | 22 MHz | DBPSK/DQPSK | 1 | 2 Mbps |
| 802.11b | – | 1999 | 2,4 GHz | DSSS (HR-DSSS, CCK) | 22 MHz | CCK | 1 | 11 Mbps |
| 802.11a | – | 1999 | 5 GHz | OFDM | 20 MHz | 64-QAM | 1 | 54 Mbps |
| 802.11g | – | 2003 | 2,4 GHz | OFDM (ERP), abwärtskompatibel zu b | 20 MHz | 64-QAM | 1 | 54 Mbps |
| 802.11n (HT) | Wi-Fi 4 | 2009 | 2,4 + 5 GHz | OFDM, MIMO | 40 MHz | 64-QAM | 4 | 600 Mbps |
| 802.11ac (VHT) | Wi-Fi 5 | 2013 | nur 5 GHz | OFDM, DL MU-MIMO (Wave 2) | 80 (W1) / 160 MHz (W2) | 256-QAM | 8 (W1 Produkte 3) | 1,3 Gbps (W1) / 6,93 Gbps |
| 802.11ax (HE) | Wi-Fi 6 / 6E (6 GHz) | 2021 | 2,4 + 5 (+6) GHz | OFDMA, DL+UL MU-MIMO | 160 MHz | 1024-QAM | 8 | 9,6 Gbps (8 SS, 160 MHz); Kurs: ~4,8 Gbps bei 80 MHz |
| 802.11be (EHT) | Wi-Fi 7 | 2024 (Wi-Fi CERTIFIED 7) | 2,4 + 5 + 6 GHz | OFDMA, MLO, Multi-RU | 320 MHz (nur 6 GHz) | 4096-QAM | 8 (16 nur in frühen Drafts) | ca. 23 Gbps (8 SS × 2,88 Gbps); oft genannte 46 Gbps setzen 16 SS voraus |

- **802.11b**: Raten 1, 2, 5,5, 11 Mbps; DSSS mit Barker-Code (1/2 Mbps) bzw. CCK (5,5/11 Mbps).
- **802.11a/g**: OFDM-Raten 6, 9, 12, 18, 24, 36, 48, 54 Mbps (48 Datenträger, 64-QAM 3/4 bei 54 Mbps). 802.11g in Mischumgebung mit 11b braucht Schutzmechanismen (RTS/CTS oder CTS-to-self) → Durchsatz sinkt (eigene Ergänzung).
- **OFDM**: Multicarrier – viele schmale, orthogonale (sich überlappende, aber nicht störende) Unterträger mit 312,5 kHz Abstand (a/g/n/ac); robust gegen Multipath, spektral effizient. **DSSS**: Single-Carrier, spreizt jedes Bit über einen breiten Kanal (22 MHz).
- **802.11n**: Channel Bonding bis 40 MHz, Frame Aggregation (A-MPDU/A-MSDU), Block ACK, MIMO bis 4×4:4, Short Guard Interval (400 ns). 1 SS bei 20 MHz max. 72,2 Mbps, bei 40 MHz 150 Mbps → 4 SS = 600 Mbps. Abwärtskompatibel zu a und b/g.
- **802.11ac**: nur 5 GHz (Dual-Band-APs nutzen auf 2,4 GHz 802.11n). Wave 1: bis 80 MHz, 256-QAM, 1–3 SS, 1,3 Gbps (3 SS × 433,3). Wave 2: 160 MHz (bzw. 80+80), bis 8 SS (Standard), **DL MU-MIMO** bis 4 Clients gleichzeitig, 6,93 Gbps (8 × 866,7). Pro Spatial Stream (MCS 9, SGI): 20 MHz 86,7 (MCS 8), 40 MHz 200, 80 MHz 433,3, 160 MHz 866,7 Mbps. Unterstützt alle Pflichtmodi von a und n → keine Probleme mit Bestands-Clients.
- **802.11ax (Wi-Fi 6)**: ratifiziert Februar 2021; Dual-Band 2,4 + 5 GHz (Wi-Fi 6E erweitert auf 6 GHz). OFDMA mit **Resource Units (RU)** – Kanal wird zwischen mehreren Clients aufgeteilt (kleinste RU 26 Töne; 20 MHz bis zu 9 Clients); DL **und UL MU-MIMO** (bis 8 Nutzer); **1024-QAM** (10 bit/Symbol, +25 % gegenüber 256-QAM); 4× längere OFDM-Symbole (12,8 µs + GI, Unterträgerabstand 78,125 kHz); **BSS Coloring** (Spatial Reuse gegen CCI); **Target Wake Time (TWT)** für IoT-Akkus. Pro SS (MCS 11, 0,8 µs GI): 20 MHz 143,4, 80 MHz 600,5, 160 MHz 1201 Mbps → 8 SS × 80 MHz ≈ 4,8 Gbps, 8 SS × 160 MHz ≈ 9,6 Gbps.
- **802.11be (Wi-Fi 7)** (nicht im Kurs): 320-MHz-Kanäle (nur 6 GHz), **4096-QAM** (12 bit/Symbol, +20 % gegenüber 1024-QAM), **Multi-Link Operation (MLO)** – ein Client nutzt mehrere Bänder/Links gleichzeitig bzw. wechselt nahtlos; Multi-RU pro Client; Preamble Puncturing (gestörten 20-MHz-Teil eines breiten Kanals aussparen). Pro SS 320 MHz MCS 13 ≈ 2,88 Gbps.
- **6 GHz** (Wi-Fi 6E/7): USA 5925–7125 MHz (1200 MHz → 59 × 20 MHz, 14 × 80 MHz, 7 × 160 MHz), EU 5945–6425 MHz (480 MHz → 24 × 20 MHz). Nur WPA3/OWE erlaubt, keine Legacy-Clients.
- Kanalnummern: 2,4 GHz Mittenfrequenz = 2407 + 5·n MHz (Kanal 1 = 2412, 6 = 2437, 11 = 2462; Kanal 14 = 2484 nur Japan/11b). 5 GHz = 5000 + 5·n MHz (Kanal 36 = 5180, 149 = 5745).

### Modulation, Kodierung, MCS
- Bits pro Symbol: BPSK 1, QPSK 2, 16-QAM 4, 64-QAM 6, 256-QAM 8, 1024-QAM 10, 4096-QAM 12. Je höher die QAM-Stufe, desto dichter liegen die Konstellationspunkte → mehr SNR nötig, nur nahe am AP erreichbar.
- **Coding Rate** (FEC): Anteil Nutzbits, z. B. 1/2, 3/4, 5/6 (5/6 = wenig Redundanz, schneller, empfindlicher).
- **MCS-Index** = Kombination aus Modulation + Coding Rate (bei 802.11n zusätzlich Anzahl SS: MCS 0–31). Beispiele: 802.11n/ac MCS 7 = 64-QAM 5/6, 802.11ac MCS 9 = 256-QAM 5/6, 802.11ax MCS 11 = 1024-QAM 5/6, 802.11be MCS 13 = 4096-QAM 5/6.
- **Guard Interval (GI)**: Pause zwischen Symbolen gegen Inter-Symbol-Interference durch Multipath. Legacy 800 ns, Short GI 400 ns (n/ac, +ca. 11 %); 802.11ax 0,8/1,6/3,2 µs.
- PHY-Rate ≈ Datenunterträger × Bits/Symbol × Coding Rate × Spatial Streams / Symboldauer. Realer Durchsatz typischerweise nur ca. 50–70 % der PHY-Rate (Overhead, Contention, ACKs).
- Kanalbreite: Verdopplung (20→40→80→160→320 MHz) verdoppelt grob die Rate (etwas mehr, da relativ weniger Randträger), halbiert aber die Zahl der nicht überlappenden Kanäle und senkt das SNR um ca. 3 dB (Rauschen über breiteren Kanal).

### MIMO-Techniken
- **SISO**: Legacy (a/b/g), ein Radio, schaltet zwischen Antennen um (Diversity); anfällig für Multipath.
- **MIMO**: mehrere Radios/Antennen + Signalverarbeitung. Notation **T×R:S** (z. B. 4×4:4 = 4 Sende-, 4 Empfangsketten, 4 Spatial Streams). Die nutzbaren Streams einer Verbindung sind durch das schwächere Gerät begrenzt (AP 4×4:4 + Client 2×2:2 → max. 2 SS). Laut Kurs bringt ein MIMO-AP auch Legacy-Clients bis zu 30 % mehr Leistung (Cisco ClientLink).
- Drei Techniken:
  - **MRC (Maximal Ratio Combining)**: Empfängerseite (meist AP); kombiniert die Signale aller Empfangsantennen phasenrichtig → besseres SNR; funktioniert mit jedem Sender (auch Legacy); Empfänger braucht mehrere Antennen.
  - **Tx Beamforming**: Senderseite; Phase pro Sendeantenne so anpassen, dass die Signale beim Empfänger in Phase ankommen → höherer Pegel am Client. Gut für stationäre Clients indoor. **Explizit**: Client liefert per **Sounding** (NDP Announcement + NDP, Feedback) Kanalinformationen – beide Seiten müssen es unterstützen (802.11ac/ax standardisiert ein Verfahren). **Implizit**: AP schätzt aus empfangenen Frames, funktioniert auch mit älteren Clients (Cisco ClientLink, auf AP-Chipsatz, keine Konfiguration nötig; ClientLink 3.0 verbessert Up- und Downlink).
  - **Spatial Multiplexing**: Datenstrom wird in mehrere Spatial Streams aufgeteilt, jeder über eigene Sendekette auf derselben Frequenz; Multipath sorgt für unterscheidbare Pfade. Sender und Empfänger müssen MIMO (n/ac/ax) können. Mehr SS = mehr Durchsatz (linear).
- **SU-MIMO** (802.11n): mehrere Streams, aber immer nur zu einem Client. **MU-MIMO** (802.11ac Wave 2: nur Downlink, bis 4 Clients; 802.11ax: Downlink und Uplink, bis 8 Nutzer): AP formt pro Client einen Strahl und setzt Nullstellen ("null steering") in Richtung der anderen Clients. Besonders nützlich für Single-Stream-Clients (Smartphones). Gewinn je nach Kanal 1× bis 2–3×; fällt er unter 1×, nutzt der AP wieder SU-MIMO.
- MU-MIMO vs. OFDMA: MU-MIMO trennt Clients **räumlich** (gleiche Frequenz, verschiedene Strahlen, gut für große Datenmengen nahe beieinander stehender, gut getrennter Clients); OFDMA trennt **in der Frequenz** (RUs, ideal für viele kleine Pakete/hohe Dichte, IoT, Voice).

## Wireless Component Roles (Seite 300)
- **Station (STA)**: jedes WLAN-fähige Gerät (Client, auch der AP ist formal eine STA). Client-Fähigkeiten müssen zu den AP-Fähigkeiten passen.
- **AP**: ähnlich einem **Hub** – auf einem Kanal kann zu einem Zeitpunkt nur ein Gerät senden (Half-Duplex, geteiltes Medium); arbeitet als **Translational Bridge** zwischen 802.11 und 802.3.
- **BSS / BSSID**: Basic Service Set = AP + seine Clients; BSSID = 48-bit-Kennung (MAC des AP-Radios/je SSID). SSID = Netzname.
- **Verbindungszustände**: (1) nicht authentifiziert/nicht assoziiert, (2) authentifiziert/nicht assoziiert, (3) authentifiziert und assoziiert – erst dann wird gebridged.
- Ablauf: Probe Request (Broadcast, BSSID ff:ff:ff:ff:ff:ff, enthält unterstützte Raten/Fähigkeiten) → Probe Response (nur wenn mind. eine gemeinsame Rate; enthält SSID, Raten, Security) → 802.11 Open Authentication (Sequenz 0x0001 Client, 0x0002 AP; heute fast immer erfolgreich, WEP-Shared-Key veraltet) → Association Request (gewählte Security, Fähigkeiten) → Association Response mit **Association ID (AID)** → Datenverkehr. WPA2/WPA3/802.1X kommen **erst danach**.
- AP-Reaktion auf Frames im falschen Zustand: Frame von nicht authentifizierter STA (außer Auth/Probe) → **Deauthentication** (zurück in Zustand 1); Frame von authentifizierter, nicht assoziierter STA → **Disassociation** (Zustand 2).
- Ein Client kann bei mehreren APs authentifiziert sein (beschleunigt Roaming), aber nur mit **einem** AP assoziiert sein.
- **Split MAC**: AP = Echtzeitfunktionen (Beacons, Probe Responses, ACK/Frame-Handshake, Power-Save-Buffering, Verschlüsselung/Entschlüsselung der 802.11-Frames, Channel-Monitoring, Signalqualität pro Frame an WLC). **WLC** = Authentifizierung (PSK/EAP), RRM (RF-Management), Client-IP-Adressierung, Layer-2/3-Roaming, QoS, AP-Konfiguration und Image-Management. Details in Kap. 15.
- WLC-Formen: Hardware (AireOS, Legacy; Catalyst 9800 IOS XE), virtuell, Cloud, Module (WiSM, Legacy), eingebettet in Switches (EWC auf Catalyst 9300) bzw. APs.
- **CAPWAP**: offenes Protokoll (RFC 5415), Control Plane per DTLS verschlüsselt, Data Plane standardmäßig unverschlüsselt (optional DTLS); CAPWAP-Header der Daten enthält RSSI/SNR des Clients; APs werden authentifiziert, bevor sie Konfiguration laden.
- **MA (Mobility Agent)**: terminiert CAPWAP-Tunnel, pflegt Client-Datenbank, setzt Security- und QoS-Policy durch. **MC (Mobility Controller)**: systemweite Aufgaben – Roaming-Koordination, RRM, wIPS, Gastzugang; MA meldet Client-Zustände an MC. In zentraler Architektur beide auf demselben WLC.
- **PoP (Point of Presence)**: wo der Client aus Sicht des Kabelnetzes "sitzt" (WLC mit dem Client-VLAN/IP, ARP zeigt dorthin); verankert die IP-Adresse, bleibt beim Roaming fest. **PoA (Point of Attachment)**: WLC, auf dem der CAPWAP-Tunnel des aktuellen AP endet; wandert beim Roaming mit.
- Weitere Rollen (eigene Ergänzung): **Bridge** (Punkt-zu-Punkt/Punkt-zu-Mehrpunkt zwischen LANs, oft Richtantennen), **Workgroup Bridge (WGB)** (verbindet kabelgebundene Geräte hinter sich als Client mit einem AP), **Repeater/Range Extender** (empfängt und sendet auf demselben Kanal erneut → halbiert ca. den Durchsatz; braucht ca. 50 % Zellüberlappung), **Mesh** (RAP mit Kabel, MAPs über Funk-Backhaul; Kap. 16).

## Client Density (Seite 301)
- Client-Dichte = Anzahl Clients pro AP bzw. Fläche. Einflussfaktoren laut Kurs: physische Umgebung, AP-Platzierung, Gerätetypen (Fähigkeiten), Netzlast, Kanalzuteilung (CCI bei gleichen/überlappenden Kanälen).
- Trends: Laptops ohne Ethernet-Port (nur per Adapter), aktuelle Geräte mit 802.11ax; eigene Verbindungsmanager der Hersteller; herstellerspezifische Roaming-Schwellen → **Sticky Clients** (roamen zu spät) bzw. **Ping-Pong** (roamen zu oft). Hersteller-Designguides beachten, Kompromisse nötig. Chipsätze z. B. von Intel; Cisco kooperiert mit Apple und Samsung.
- Anforderungen: mehr Geräte pro Nutzer (3–4+ inkl. Wearables/IoT, nicht alle gleichzeitig aktiv – aber alle senden RF/Probes), steigende Erwartungen (Video ca. 82 % des mobilen Datenverkehrs 2022 laut Kurs), mehr Nutzer pro Netz; **High Density** ist heute Normalfall (Hörsäle, Konferenzen, Stadien).
- Planung (eigene Ergänzung, Best Practice): **Design for capacity, not just coverage**.
  - Aggregatbedarf = Geräte × gleichzeitige Aktivität × Bandbreite pro Gerät; durch realistischen Durchsatz pro Radio teilen → Anzahl Radios/APs.
  - **Airtime** ist die knappe Ressource: Ein langsamer Client (z. B. 6 Mbps) belegt für dieselbe Datenmenge ein Vielfaches der Airtime eines schnellen (z. B. 300 Mbps → 50×) und bremst alle in der Zelle ("performance anomaly").
  - **Niedrige Datenraten deaktivieren** (z. B. 1, 2, 5,5, 11 Mbps; niedrigste Mandatory Rate 12 oder 24 Mbps): Beacons/Broadcasts/Management-Frames werden schneller gesendet, Zellen werden effektiv kleiner, weit entfernte Clients roamen früher. Nachteil: reine 802.11b-Geräte fallen weg.
  - **Kleinere Zellen**: mehr APs mit **reduzierter Sendeleistung**, damit Kanäle wiederverwendet werden können (CCI sinkt); 5/6 GHz bevorzugen (mehr Kanäle), **Band Steering/Band Select**.
  - **Schmalere Kanäle** (20 MHz, ggf. 40 MHz) in High-Density → mehr unabhängige Kanäle, weniger CCI.
  - **Wenige SSIDs** (jede SSID sendet eigene Beacons, Kap. 18), Richtantennen (Patch/Sektor) in Hallen/Stadien, Wi-Fi 6/7-Features (OFDMA, BSS Coloring, MU-MIMO), Airtime Fairness, Client-Limits pro AP.

## Fehler/Ungenauigkeiten im Kurs
- **Amplitude**: Kurs definiert sie als Abstand zwischen höchstem und tiefstem Punkt (das ist der Spitze-Spitze-Wert; Amplitude im engeren Sinn = Abstand Nulllinie–Spitze) und nennt "gamma (γ)" als übliches Symbol – üblich ist A. (Quelle: allgemeine Physik, z. B. CWNA Study Guide, Kapitel RF Fundamentals.)
- **Noise floor "in dB von 0 bis −120"** und **SNR "0 bis 120"**: Rauschen ist eine absolute Leistung und wird in **dBm** angegeben; der SNR hat keinen festen Wertebereich bis 120. Gleiches gilt für "typischer Noise Floor −95 dB" → korrekt −95 dBm.
- **"+3 dBm = 2 mW (2 times the power)"**-Tabelle mischt dBm (absolut) und dB (relativ): +3 dB ist die Änderung, 3 dBm der absolute Wert 2 mW.
- **"Zweite Antenne ist 3 dBi stärker"** (6 vs. 9 dBi): Differenz ist 3 **dB** (Verhältnis), nicht dBi.
- **802.11ac-Durchsatz**: Kurs nennt für 80 MHz 300 Mbps (1 SS) bis 2400 Mbps (8 SS), für 160 MHz aber 867/6900 Mbps. Korrekt (MCS 9, SGI): 80 MHz 433,3 Mbps pro SS (8 SS = 3,47 Gbps); 160 MHz 866,7 Mbps (8 SS = 6,93 Gbps). (IEEE 802.11ac-2013, MCS-Tabellen; Cisco 802.11ac White Paper.)
- **802.11ax max. Rate**: Kurs "bis ~4800 Mbps" gilt nur für 80 MHz; mit 160 MHz sind 8 SS × 1201 ≈ 9,6 Gbps möglich.
- **Parabolantenne 21 dBi "fast 100-mal so stark wie ein Dipol"**: 21 − 2,14 = 18,86 dB ≈ Faktor 77 gegenüber dem Dipol (gegenüber isotrop Faktor 126).
- **Direktionalantenne "3–4 dBi statt 2,14 dBi"**: missverständlich; typische Patch-Antennen haben 6–9 dBi, Yagis 10–16 dBi.
- **Yagi**: Text 13,5 dBi, Abbildung 13 dBi.
- **"ISM-Band" für 802.11 allgemein**: 5 GHz und 6 GHz sind überwiegend U-NII-Bänder, nicht ISM.
- **Veraltet**: Tabelle endet bei 802.11ax; **802.11be (Wi-Fi 7, 2024)** mit 320 MHz, 4096-QAM und MLO fehlt; ebenso 6 GHz/Wi-Fi 6E. AireOS und WiSM sind Legacy (End-of-Life); aktuelle Plattform ist Catalyst 9800 (IOS XE).
- **MRC "nicht mit Multipath verbunden"**: MRC mildert sehr wohl Multipath-Fading (räumliche Diversität) – der Kurs relativiert das selbst im Folgeabsatz.

## Bilder
- `bilder/27-wlan-rf/01-welle.svg` – Welle mit Wellenlänge, Amplitude, Phase; Vergleich 2,4/5/6 GHz-Wellenlängen.
- `bilder/27-wlan-rf/02-db-regeln.svg` – Regel der 3 und 10 als Leiter von 1 mW bis 1 W mit dBm-Werten.
- `bilder/27-wlan-rf/03-eirp.svg` – Sender → Kabel → Antenne mit EIRP-Rechnung und Link-Budget bis zum Empfänger.
- `bilder/27-wlan-rf/04-phaenomene.svg` – Reflexion, Refraktion, Absorption, Streuung, Beugung, Multipath.
- `bilder/27-wlan-rf/05-antennen.svg` – Azimut/Elevation von Omni (Donut) und Richtantenne, Beamwidth an den −3-dB-Punkten.
- `bilder/27-wlan-rf/06-standards.svg` – Zeitstrahl 802.11b bis be mit Wi-Fi-Generation, Band, Modulation, max. Rate.
- `bilder/27-wlan-rf/07-mimo.svg` – MRC, Beamforming, Spatial Multiplexing, MU-MIMO vs. OFDMA.
- `bilder/27-wlan-rf/08-assoc.svg` – Zustände und Frames der Client-Association inkl. Deauth/Disassoc-Reaktionen.
- `bilder/27-wlan-rf/09-dichte.svg` – Airtime-Vergleich schneller/langsamer Client und High-Density-Maßnahmen.
