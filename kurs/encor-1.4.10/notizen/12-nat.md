# Notizen Kapitel "Implementing NAT" (Kursseiten 119–124)

## 119 Define NAT
- Private Adressen (RFC 1918) sind im Internet nicht routbar → am Netzrand Übersetzung privat ↔ öffentlich nötig.
- NAT meist am Edge-Router zum ISP; kann das ganze Netz hinter einer Adresse verstecken (Nebeneffekt: Topologie verborgen).
- Was übersetzt wird, ist Konfigurationssache (nicht "privat/öffentlich") → NAT auch intern einsetzbar, z. B. bei Firmenfusion mit überlappenden privaten Netzen.
- Vorteile: kein Readressieren aller Hosts nötig; Adressen sparen durch PAT (Port-Multiplexing); interne Adressen/Topologie werden nicht beworben.
- Nachteile: Ende-zu-Ende-Prinzip gebrochen (Apps mit eingebetteten IPs, digitale Signaturen über Quell-IP); Rückverfolgbarkeit/Troubleshooting schwerer; Tunnel wie IPsec gestört (Integritätsprüfung der Header); von außen initiierte TCP-Verbindungen und manche UDP-Protokolle problematisch (statische Mappings als Abhilfe); mehr Switching-Verzögerung (Header + ggf. TCP/UDP-Header umschreiben; laut Kurs erstes Paket process-switched).

## 120 Adresstypen
- Inside = Netze, deren Adressen übersetzt werden; Outside = alles andere.
- Inside local: am Host konfigurierte/DHCP-Adresse (meist RFC 1918).
- Inside global: Adresse, in die inside local übersetzt wird (meist öffentlich).
- Outside global: echte Adresse des externen Hosts.
- Outside local: Adresse des externen Hosts, wie das Innennetz sie sieht – relevant bei überlappenden Netzen (Fusion).
- Merkhilfe: local = von innen sichtbar, global = von außen sichtbar.

## 121 Implementierungen
- Static NAT 1:1 – Server von außen erreichbar. Eintrag permanent.
- Dynamic NAT: Pool öffentlicher Adressen, many-to-many; erster Paketfluss erzeugt "simple entry".
- PAT/overload: many-to-one über Ports; "extended entry"; Ports 16 bit → theoretisch ~65.536 pro Adresse.
- PAT versucht Originalport zu behalten; sonst erster freier Port in der Portgruppe 0–511, 512–1023, 1024–65535; danach nächste Pool-Adresse.
- Rückweg PAT: Lookup über inside global + Port und outside global + Port (connection tracking).
- Statisches NAT Rückweg: Lookup mit inside global als Schlüssel.

## 122 NVI
- Ab IOS 12.3(14)T; `ip nat enable` auf den Interfaces, keine inside/outside-Rolle; globaler Befehl `ip nat source list 10 interface e0/1 overload` (ohne "inside").
- Klassisch: inside→outside erst Routing, dann NAT; outside→inside umgekehrt. NVI: Routing – NAT – Routing (symmetrisch) → inside-zu-inside-Flüsse (Hairpin) möglich.
- Laut Kurs: NVI auf IOS XE nicht unterstützt.

## 123 Discovery 14 (Lab)
- R1 e0/0–e0/2 inside (10.10.1/2/3.0/24), e0/3 outside 198.51.100.2/24, R2 ISP, SRV2 203.0.113.30.
- Vor NAT: R1 erreicht SRV2 (öffentliche Quelle), SRV1 nicht (private Quelle, wird verworfen).
- Erstes `ip nat inside` → Meldung Interface NVI0 up (internes NVI).
- Static: `ip nat inside source static 10.10.2.20 198.51.100.20`; Tabelle zeigt sofort "---"-Eintrag. Bei Telnet von außen zusätzlicher tcp-Extended-Eintrag.
- Dynamic: `ip nat pool NatPool 198.51.100.100 198.51.100.149 netmask 255.255.255.0` (50 Adressen), `access-list 10 permit 10.10.1.0 0.0.0.255`, `ip nat inside source list 10 pool NatPool`. Simple dynamic entry 24 h Inaktivitäts-Timeout, ICMP-Einträge kurzlebig.
- `show ip nat statistics`: aktive Übersetzungen (static/dynamic/extended), Peak, Inside/Outside-Interfaces, Hits/Misses, Expired, Pool: total/allocated/misses, refcount.
- `clear ip nat translation *` löscht dynamische, statische bleiben.
- PAT: `access-list 20 permit 10.10.3.0 0.0.0.255`, `ip nat inside source list 20 interface e0/3 overload`; Einträge unterscheiden sich am inside-global-Port.

## Kursfehler/Auffälligkeiten
- Lab Task 1 Step 6: Telnet-Session wird als "von SRV1 zu SRV2" bezeichnet, tatsächlich SRV2 → SRV1.
- Lab Task 2 Step 10: Adressen als "198.151.100.100/101" geschrieben (Tippfehler, korrekt 198.51.100.x).
- Lab Task 3 Step 9: "Peak translations: 2" bei "Total active translations: 3" – inkonsistent.
- Lab Task 2 Step 11: "allocated 3 (6%)" bei nur zwei zugewiesenen Pool-Adressen in der Tabelle.
