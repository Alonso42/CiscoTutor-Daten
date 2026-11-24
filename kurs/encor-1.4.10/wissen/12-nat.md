# Implementing NAT

Quelle: ENCOR 1.4.10 Student Guide, Seiten 119–124 (124 = Summary-Video; Summary Challenge und Answer Key nicht ausgewertet)
Topics: ENCOR-3.3.b (Configure and verify NAT/PAT)

Hinweis: Abschnitte mit "(Ergänzung)" stehen nicht im Kurs, sondern stammen aus Cisco-Doku/RFCs (u. a. Timeouts, Reihenfolge der Verarbeitung, Static PAT, Troubleshooting); Belege im Prüfprotokoll research_notes/Kapitelpruefung/12-nat.md.

## 1. Wozu NAT? (S. 119)
- Viele Netze nutzen private Adressen nach RFC 1918: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16. Sie sind im Internet nicht routbar → am Netzrand müssen sie in öffentliche Adressen übersetzt werden. (Ergänzung: 100.64.0.0/10 ist Shared Address Space für Carrier-Grade NAT, RFC 6598.)
- Typischer Ort: Edge-Router zum ISP. Kursgrafik: Host 10.1.1.100 sendet ins Internet, nach dem Router trägt das Paket eine öffentliche Quelladresse.
- Man kann das ganze Netz hinter **einer** Adresse verstecken; Nebeneffekt: die interne Topologie bleibt verborgen.
- Was "privat" und "öffentlich" ist, ist für NAT egal: Welche Netze übersetzt werden, legt allein die Konfiguration fest. Deshalb geht NAT auch intern, z. B. bei einer Firmenfusion mit überlappenden privaten Netzen.

### Vorteile
- Hosts müssen nicht umnummeriert werden (Zeit/Kosten).
- Adressen sparen: PAT multiplext viele Hosts über Ports auf eine öffentliche IPv4-Adresse.
- Interne Adressen und Topologie werden nicht beworben.

### Nachteile
- Ende-zu-Ende-Prinzip gebrochen: Anwendungen mit eingebetteten IP-Adressen (z. B. FTP aktiv, SIP) oder Signaturen über die Quell-IP scheitern; teils helfen statische Zuordnungen oder Application Layer Gateways.
- Rückverfolgbarkeit: Über mehrere NAT-Stufen ist die echte Quelle schwer zu finden, Troubleshooting wird schwieriger.
- Tunnel/IPsec: NAT verändert Header, die IPsec per Integritätsprüfung schützt (AH scheitert grundsätzlich; ESP braucht NAT-Traversal, UDP 4500 – Ergänzung).
- Von außen initiierte TCP-Verbindungen und zustandslose UDP-Protokolle finden ohne statische Zuordnung kein Ziel.
- Zusätzliche Verarbeitung: IP-Header (und ggf. TCP/UDP-Header, Prüfsummen) müssen umgeschrieben werden.

## 2. Adresstypen (S. 120)
- **Inside** = Netze, deren Adressen übersetzt werden; **Outside** = alles andere (meist Internet).

| Begriff | Bedeutung | typisch |
|---|---|---|
| Inside Local | Adresse des inneren Hosts, wie sie am Host konfiguriert/per DHCP vergeben ist | RFC 1918, z. B. 10.1.1.100 |
| Inside Global | Adresse, in die Inside Local übersetzt wird – so sieht das Internet den Host | öffentlich, vom ISP, z. B. 209.165.201.5 |
| Outside Global | echte Adresse des externen Hosts | öffentlich |
| Outside Local | Adresse des externen Hosts, wie das Innennetz sie sieht | meist = Outside Global; anders nur bei Outside-NAT (z. B. Fusion mit überlappenden Netzen) |
- Merkhilfe: Inside/Outside = **wo** steht der Host; Local/Global = **von wo** wird die Adresse gesehen (von innen sichtbar / von außen sichtbar).
- Ein Internet-Server sieht als Quelle die **Inside Global**-Adresse.
- Fusionsbeispiel (eigenes): Firma A und B nutzen beide 10.1.1.0/24. A1 10.1.1.10 (Inside Local) → 198.51.100.10 (Inside Global). Server B1 hat real 10.1.1.20 (Outside Global), A sieht ihn als 172.16.2.20 (Outside Local). Konfiguration Outside-Seite: `ip nat outside source static 10.1.1.20 172.16.2.20` (erst Outside Global, dann Outside Local).

## 3. NAT-Varianten (S. 121)
| Variante | Zuordnung | Einsatz | Tabelleneintrag |
|---|---|---|---|
| Static NAT | 1:1, fest | Server von außen erreichbar (Webserver, DMZ) | permanent, sofort sichtbar |
| Dynamic NAT | n:m aus einem Pool | Hosts bekommen beim ersten Paket eine freie Pool-Adresse | "simple entry" (nur IP) |
| PAT / Overload | n:1 über Ports | Standard bei Internetzugang (Heimrouter) | "extended entry" (IP + Port) |

### Static NAT – Ablauf (Kursgrafik, eigene Worte)
1. Host A im Internet (209.165.202.131) öffnet eine Verbindung zu Server B über dessen Inside Global 209.165.201.5.
2. Router empfängt das Paket am Outside-Interface, sucht mit der **Inside Global als Schlüssel** in der NAT-Tabelle und ersetzt das Ziel durch 10.1.1.101.
3. Server B antwortet mit Quelle 10.1.1.101.
4. Router (Inside-Interface) ersetzt die Quelle wieder durch 209.165.201.5 und leitet weiter.
- Statische Einträge funktionieren in beide Richtungen: Pakete vom Inside-Interface mit der Inside-Local-Quelle werden übersetzt, ebenso Pakete am Outside-Interface an die Inside-Global-Adresse.

### Dynamic NAT – Ablauf
- Hosts 10.1.1.100 und .101 öffnen Verbindungen zu Host B 209.165.202.131.
- Erstes Paket von .101: kein Eintrag → Router nimmt eine freie Adresse aus dem Pool (209.165.201.5) und legt einen simple entry an; für .100 die nächste (209.165.201.6).
- Antworten an .5 bzw. .6 werden über die Inside Global zurückübersetzt.
- Jeder Host belegt eine eigene Pool-Adresse; ist der Pool leer, bekommen weitere Hosts keine Übersetzung (Pool-"misses" steigen).

### PAT – Ablauf und Portregeln
- Alle Sessions teilen sich 209.165.201.5; unterschieden wird über den Quellport (16 bit → theoretisch 65 536 Ports pro Adresse).
- Kursbeispiel: 10.1.1.100:1723 → 209.165.201.5:1723; 10.1.1.101:1927 → :1927; zweite Session von 10.1.1.101 mit Quellport 1723 → Port belegt → Kurs zeigt 209.165.201.5:1724. Nach der Cisco-Regel (s. u.) wäre es der **erste freie Port ab Beginn der Gruppe**, also 1024, sofern frei. In den Bildern und in Fragen gilt die Cisco-Regel.
- Regeln (Cisco NAT FAQ 26704): PAT versucht zuerst den Originalport zu behalten. Ist er belegt, sucht es **vom Anfang** der passenden Portgruppe **0–511, 512–1023, 1024–65535** aus den ersten freien Port (nicht "Originalport + 1"). Ist kein Port frei und gibt es weitere Pool-Adressen, wechselt PAT zur nächsten Adresse und versucht dort wieder den Originalport; sonst wird das Paket verworfen. Die FAQ nennt selbst eine Ausnahme (12.2S-Codebasis mit anderer Portlogik); auf IOS XE kann die Portwahl ebenfalls abweichen – die Prüfungsregel ist die FAQ-Regel.
- Rückweg (connection tracking): Lookup mit Inside-Global-Adresse + Port **und** Outside-Adresse + Port als Schlüssel. Nur angefragte Antworten passen → von außen initiierter Verkehr hat keinen Eintrag.
- ICMP: Der Query-Identifier wird wie ein Port behandelt (RFC 3022).

## 4. Konfiguration (S. 121/123)
```
! Rollen festlegen
interface Ethernet0/0
 ip nat inside
interface Ethernet0/3
 ip nat outside

! Static NAT (lokal zuerst, dann global)
ip nat inside source static 10.10.2.20 198.51.100.20

! Dynamic NAT: Pool + ACL (Wildcard!) + Regel
ip nat pool NatPool 198.51.100.100 198.51.100.149 netmask 255.255.255.0
access-list 10 permit 10.10.1.0 0.0.0.255
ip nat inside source list 10 pool NatPool

! PAT auf die Interface-Adresse bzw. auf einen Pool
access-list 20 permit 10.10.3.0 0.0.0.255
ip nat inside source list 20 interface Ethernet0/3 overload
ip nat inside source list 20 pool NatPool overload
```
- Pool 198.51.100.100–149 = 50 Adressen. Statt `netmask` geht `prefix-length 24`. Start und Ende sollten im selben Subnetz liegen.
- Ergänzung Static PAT (Port-Forwarding): `ip nat inside source static tcp 192.168.20.10 80 198.51.100.10 8080`; mit `interface Gi0/0/1` statt fester IP, wenn die WAN-Adresse per DHCP kommt.
- Ergänzung statische Netz-Zuordnung: `ip nat inside source static network 10.1.1.0 198.51.100.0 /24`.
- ACL nicht zu weit fassen (`permit any` kostet Ressourcen und kann Router-eigenen Verkehr erfassen).

### Timeouts (Ergänzung, Command Reference `ip nat translation`)
| Eintrag | Default |
|---|---|
| simple/dynamischer Eintrag (`timeout`) | 86 400 s (24 h) Inaktivität |
| UDP | 300 s |
| TCP | 86 400 s |
| DNS, ICMP, TCP-FIN/RST, SYN | je 60 s |
- Im Lab: ICMP-Einträge verschwinden schnell, der Pool-Eintrag (simple entry) bleibt 24 h.

## 5. NAT Virtual Interface – NVI (S. 122)
- Ab IOS 12.3(14)T. Keine inside/outside-Rollen: auf allen beteiligten Interfaces `ip nat enable`; globaler Befehl ohne `inside`:
```
access-list 10 permit 192.168.10.0 0.0.0.255
ip nat source list 10 interface Ethernet0/1 overload
interface Ethernet0/0
 ip nat enable
interface Ethernet0/1
 ip nat enable
```
- Reihenfolge: klassisches NAT ist **asymmetrisch** (inside→outside: erst Routing, dann NAT; outside→inside: erst NAT, dann Routing). NVI ist **symmetrisch**: Routing → NAT → Routing. Durch den zweiten Routing-Schritt funktionieren auch Flüsse "inside → inside" (z. B. interner Client spricht internen Server über dessen öffentliche Adresse an = Hairpinning), was mit klassischem NAT scheitert.
- **NVI wird auf Cisco IOS XE nicht unterstützt** (Kurs und IOS-XE NAT Config Guide) → auf IOS-XE-Plattformen klassische Konfiguration.
- Beim ersten `ip nat inside` meldet klassisches IOS im Lab "Interface NVI0, changed state to up" – IOS legt intern ein Hilfsinterface an; das ist kein NVI-Betrieb.
- Kontrolle bei NVI: `show ip nat nvi translations`, `show ip nat nvi statistics`.

## 6. Reihenfolge der Verarbeitung (Ergänzung, Cisco Doc 6209)
| Richtung | Ablauf | Folge |
|---|---|---|
| Inside → Outside | Input-ACL → Routing → NAT (Quelle wird Inside Global) → Crypto → Output-ACL | Input-ACL am Inside-Interface sieht Inside Local; ohne Route wird verworfen, bevor ein Eintrag entsteht; Output-ACL am Outside sieht Inside Global |
| Outside → Inside | Input-ACL → NAT (Ziel wird Inside Local) → Routing | Input-ACL am Outside-Interface muss die Inside-Global-Adresse erlauben |

## 7. Discovery 14 – Lab (S. 123)
- Topologie: R1 mit Et0/0 (SW1: PC1 10.10.1.10, PC2 10.10.1.20, Netz 10.10.1.0/24), Et0/1 (SW2: SRV1 10.10.2.20), Et0/2 (SW4: PC3 10.10.3.10, PC4 10.10.3.20), Et0/3 outside 198.51.100.2/24 zu R2 (ISP). Hinter R2: SRV2 203.0.113.30. Gateways jeweils .1.
- Vor NAT: R1 selbst erreicht SRV2 (öffentliche Quelle 198.51.100.2), SRV1 nicht – private Quelle wird beim ISP verworfen bzw. die Antwort findet nicht zurück.
- Task 1 Static: SRV1 ↔ 198.51.100.20. Tabelle zeigt sofort `--- 198.51.100.20 10.10.2.20 --- ---`. Telnet von SRV2 auf 198.51.100.20 erzeugt zusätzlich `tcp 198.51.100.20:23 10.10.2.20:23 203.0.113.30:<port> 203.0.113.30:<port>`.
- Task 2 Dynamic: Pool 198.51.100.100–149, ACL 10 für 10.10.1.0/24. Ping von PC1 → `icmp 198.51.100.100:<id> ...` plus simple entry `--- 198.51.100.100 10.10.1.10 --- ---`; PC2 bekommt .101.
- Task 3 PAT: ACL 20 für 10.10.3.0/24, `overload` auf Et0/3 → `tcp 198.51.100.2:21299 10.10.3.10:21299 203.0.113.30:23 ...` und `tcp 198.51.100.2:34023 10.10.3.20:34023 ...` – Unterscheidung nur über den Inside-Global-Port. Rückpaket an Port 21299 → PC3, an 34023 → PC4.
- `clear ip nat translation *` löscht alle dynamischen Einträge; statische bleiben.

### show ip nat statistics (eigenes, gekürztes Beispiel)
```
Total active translations: 3 (1 static, 2 dynamic; 2 extended)
Outside interfaces: Ethernet0/3
Inside interfaces: Ethernet0/0, Ethernet0/1, Ethernet0/2
Hits: 389  Misses: 0
CEF Translated packets: 389, CEF Punted packets: 0
Expired translations: 4
Dynamic mappings:
-- Inside Source
[Id: 1] access-list 10 pool NatPool refcount 0
 pool NatPool: netmask 255.255.255.0
   start 198.51.100.100 end 198.51.100.149
   type generic, total addresses 50, allocated 0 (0%), misses 0
[Id: 2] access-list 20 interface Ethernet0/3 refcount 2
```
- Hits/Misses (Kopfzeile): Lookups mit bzw. ohne vorhandenen Eintrag – ein Miss heißt "neuer Eintrag nötig", ist also normal.
- Pool-`misses`: fehlgeschlagene Zuweisungen → Pool erschöpft (overload ergänzen oder Pool vergrößern).
- `refcount`: Anzahl der Übersetzungen, die die Regel gerade nutzen.
- `allocated x (y%)`: belegte Pool-Adressen, z. B. 2 von 50 = 4 %, 3 von 50 = 6 %.
- `show ip nat translations verbose` zeigt zusätzlich Erstellzeit und letzte Nutzung je Eintrag.

## 8. Troubleshooting (Ergänzung, systematisch)
1. `show ip nat statistics`: Inside/Outside-Interfaces richtig? Gibt es eine Regel unter "Dynamic mappings"? Pool voll (misses)?
2. `show ip nat translations`: entstehen Einträge?
3. ACL prüfen: Wildcard statt Subnetzmaske? Neues Subnetz enthalten? Nicht erfasster Verkehr wird nicht verworfen, sondern **unübersetzt** geroutet und scheitert erst beim ISP.
4. Routing in beide Richtungen: Default-Route nach außen; der ISP braucht eine Route zum Pool, wenn dieser nicht im Transfernetz liegt.
5. Nach Änderungen alte Einträge mit `clear ip nat translation *` entfernen. Meldung "%Dynamic Mapping in Use, Cannot remove" beim Löschen einer Regel → erst Einträge löschen.
6. `debug ip nat` zeigt Übersetzungen live (in Produktion vorsichtig).
- Vom Router selbst erzeugter Verkehr (Quelle = WAN-Adresse) wird von `ip nat inside source` nicht übersetzt.

| Symptom | Ursache | Lösung |
|---|---|---|
| nur die ersten Hosts kommen raus | Pool ohne overload voll | overload oder größerer Pool |
| ein neues VLAN geht nicht | ACL ohne das Subnetz / Interface ohne `ip nat inside` | ACL bzw. Interface ergänzen |
| keine Einträge, Rollen vertauscht | inside/outside falsch gesetzt | Rollen korrigieren |
| Tabelle leer, keine Route nach außen | Routing vor NAT scheitert | Default-Route |
| Einträge da, keine Antworten | ISP routet den Pool nicht | Route beim ISP |

## Fehler/Ungenauigkeiten im Kurs
- S. 123 Task 1 Step 6: Telnet-Session wird als "von SRV1 zu SRV2" beschrieben, tatsächlich baut SRV2 sie zu SRV1 (198.51.100.20) auf.
- S. 123 Task 2 Step 10: Adressen als "198.151.100.100/101" geschrieben – Tippfehler, korrekt 198.51.100.100/101.
- S. 123 Task 3 Step 9: "Peak translations: 2" bei "Total active translations: 3" – in sich widersprüchlich (Peak kann nicht kleiner als der aktuelle Stand sein).
- S. 123 Task 2 Step 11: "allocated 3 (6%)", obwohl die Tabelle nur zwei zugewiesene Pool-Adressen zeigt (2/50 = 4 %).
- S. 119: "Das erste Paket wird process-switched" – pauschal veraltet (NAT FAQ: IOS-NAT unterstützt CEF-, Fast- und Process-Switching, Fast Switching ab 12.4T entfallen; zum ersten Paket sagt die FAQ nichts). Im selben Lab zeigt `show ip nat statistics` "CEF Translated packets: 389, CEF Punted packets: 0", und IOS-XE-Plattformen übersetzen in Hardware. **(neu gefunden)**
- S. 119: NAT "schützt das Netzwerk" – NAT verbirgt Adressen, ist aber kein Sicherheitsmechanismus (keine Filterung, kein Ersatz für Firewall/ACL); Schutz entsteht nur als Nebeneffekt, weil unangefragter Verkehr keinen Eintrag findet. **(neu gefunden, Ungenauigkeit)**
- S. 121: Das Kursbeispiel (belegter Port 1723 → 1724) widerspricht der im Kurs selbst genannten und in der Cisco NAT FAQ 26704 belegten Regel: Gesucht wird ab **Beginn** der Portgruppe der erste freie Port, hier also 1024 (wenn frei). Gilt in Wissen, Bildern, Lektion und Fragen; reales Verhalten kann je nach Codebasis abweichen (FAQ: Ausnahme 12.2S). **(geklärt)**
- S. 121: Dynamic NAT als typische Lösung "bei Firmenfusion mit gleichem Adressraum" – für überlappende Netze braucht man vor allem Outside-NAT (Outside Local ≠ Outside Global); reines Dynamic Inside NAT löst nur die halbe Richtung. **(neu gefunden, Ungenauigkeit)**

## Bilder
- `bilder/12-nat/01-nat-idee.svg` – Privates Netz hinter einem NAT-Router, Quelladresse wird an der Grenze ersetzt.
- `bilder/12-nat/02-adresstypen.svg` – Vier Adresstypen als 2×2-Matrix (Inside/Outside × Local/Global) mit Beispiel.
- `bilder/12-nat/03-varianten.svg` – Static (1:1), Dynamic (n:m) und PAT (n:1) nebeneinander.
- `bilder/12-nat/04-static-flow.svg` – Ablauf Static NAT mit Lookup über die Inside Global.
- `bilder/12-nat/05-pat-tabelle.svg` – PAT-Tabelle mit Portwechsel 1723 → 1024 (erster freier Port der Gruppe) und Portgruppen.
- `bilder/12-nat/06-reihenfolge.svg` – Reihenfolge Routing/NAT/ACL je Richtung, klassisch vs. NVI.
- `bilder/12-nat/07-lab-topo.svg` – Discovery-14-Topologie mit den drei Subnetzen und ihrer NAT-Variante.
- `bilder/12-nat/08-statistics.svg` – Gelesene Zeilen von `show ip nat statistics` mit Bedeutung.
- `bilder/12-nat/09-fehlersuche.svg` – Fehlersuche als Ablauf in fünf Schritten.
