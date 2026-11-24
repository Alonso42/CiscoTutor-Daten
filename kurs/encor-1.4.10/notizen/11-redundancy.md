# Kapitel 11 – Implementing Network Redundancy (Kursseiten 109–115)

## 109 Need for Default Gateway Redundancy
- Host schickt alles außerhalb des eigenen Subnetzes an das Default Gateway (statisch oder per DHCP).
- Hosts haben typischerweise genau EIN Gateway; es passt sich nicht an Topologieänderungen an.
- IGP zwischen den Routern konvergiert, aber Endgeräte bekommen keine Routing-Infos -> fällt das Gateway aus, ist der Host isoliert, obwohl ein zweiter Router existiert.
- Gilt gleichermaßen für Layer-3-Switches.

## 110 Define FHRP
- Mehrere Router teilen virtuelle IP + virtuelle MAC -> ein "virtueller Router".
- Host trägt virtuelle IP als Gateway ein, ARP liefert virtuelle MAC.
- Rollenwahl, Übernahme bei Ausfall: Standby sieht keine Hellos mehr -> übernimmt; da IP und MAC mitwandern, merkt der Host nichts.
- HSRP: Cisco, RFC 2281, ein Router forwardet.
- VRRP: offener Standard, RFC 5798 (VRRPv3; Kurs nennt auch RFC 3768 = v2, RFC 2338 = v1), mehr als zwei Router möglich, ein Router forwardet.
- GLBP: Cisco, mehrere aktive Forwarder (Lastverteilung) – im Kurs nur erwähnt.

## 111 Discovery 12: HSRP (Lab)
- Topologie: PC1/PC2 – ASW1/ASW2 – R1 (192.168.1.3) / R2 (192.168.1.2) – R3 – Server 192.168.4.22. VIP 192.168.1.1, Gruppe 1. Lab auf Routern (IOL-Switches können kein HSRP).
- `standby <grp> ip <vip>`; ohne Gruppennummer -> Gruppe 0. v1: Gruppen 0–255.
- Gruppennummern lokal signifikant (pro Interface); Best Practice: Gruppe = VLAN.
- Hellos v1 an 224.0.0.2, UDP 1985. Active + Standby senden Hellos; weitere Router bleiben Listen.
- ICMP Redirects bei HSRP deaktivieren (Redirect auf physische Router-IP würde Failover aushebeln).
- Virtuelle MAC v1: 0000.0c07.acXX (XX = Gruppe hex). Show ip arp auf Active zeigt VIP mit dieser MAC.
- Active: beantwortet ARP für VIP, forwardet, sendet Hellos. Standby: sendet Hellos, hört zu, übernimmt.
- Traceroute zeigt reale Interface-IP des Active (nicht VIP) -> nützlich zur Fehlersuche.
- Bei Failover sendet neuer Active (laut Kurs) drei Gratuitous ARPs, damit Switches den neuen Port der vMAC lernen.
- Priorität 0–255, Default 100, höchste gewinnt; Gleichstand -> höchste IP.
- Preempt Default AUS (`standby 1 preempt`); ohne Preempt bleibt Active Active.
- Timer: `standby [grp] timers [msec] hello [msec] hold`; Default 3 s / 10 s; Bereich 1–255 s; Hold >= 3x Hello. `no standby <grp> timers` -> Default.
- Preempt delay: `standby 1 preempt delay minimum 300`; Empfehlung ca. 150 % der Bootzeit, damit Routing konvergiert ist.
- Lab Step 6: timers msec 200 msec 750, preempt delay minimum 300.
- `show standby` / `show standby brief` (Spalten Interface Grp Pri P State Active Standby Virtual IP; P = preempt).
- States: Initial(Init) -> Listen -> Speak -> Standby -> Active. Listen: kennt VIP, hört. Speak: sendet Hellos, nimmt an Wahl teil.
- Failover-Lab: R2 Et0/1 shut -> R1 Active, Standby "unknown"; R2 Init.
- `debug standby events`.

## 112 HSRP Advanced
- Ohne Tracking verliert Active seine Rolle nur bei Ausfall des HSRP-Interface oder des Routers.
- Uplink-Ausfall bei R2: ohne Tracking suboptimaler Pfad (R2 -> R1 -> Core).
- Object Tracking: `track 1 interface e0/0 line-protocol`, `standby 10 track 1 decrement 20`; Default decrement 10; Preempt auf allen nötig.
- Mehrere Track-Statements möglich (z. B. erst bei Ausfall von zwei Uplinks abgeben).
- `show track <n>`, `show standby` zeigt Tracking.
- MHSRP: Lastverteilung über mehrere Gruppen (pro VLAN, oder mehrere Gruppen/VIPs im selben VLAN). STP-Root und HSRP-Active auf denselben Switch legen. Beispiel: SW1 Grp10 Pri110 / Grp20 Pri90; SW2 umgekehrt.
- Authentifizierung: plaintext (`standby 1 authentication <string>`, max. 8 Zeichen) oder MD5 (`standby 1 authentication md5 key-string [0|7] <string>` oder `... md5 key-chain <name>`). Gleiche Einstellungen auf allen Peers. Schutz vor Rogue-Router (DoS/MITM).
- Versionen: v1 IPv4, Gruppen 0–255, 0000.0C07.ACxx, 224.0.0.2, Default. v2 IPv4/IPv6, Gruppen 0–4095, 0000.0C9F.Fxxx, 224.0.0.102. `standby version 2` (Interface-Befehl, ohne Gruppennummer). Nicht interoperabel. IPv6-HSRP braucht v2. v2 hat 6-Byte-Identifier (Interface-MAC des Senders).

## 113 Discovery 13: VRRP
- Master/Backup; ein Master, ein oder mehrere Backups. Priorität 0–255, Default 100; 0 = Master tritt zurück (schnelle Übernahme). Owner (VIP = eigene Interface-IP) = 255, immer Master wenn verfügbar.
- Nur der Master sendet Advertisements an 224.0.0.18, IP-Protokoll 112; Intervall 1 s.
- Master Down Interval = 3x Advertisement + Skew Time ((256-Prio)/256): Prio 100 -> 3,609 s, Prio 110 -> 3,570 s (Lab-Output).
- Millisekunden-Timer: Cisco-Erweiterung, auf Master und Backup konfigurieren; show vrrp auf Backup zeigt Master Adv. trotzdem 1 s.
- Preempt Default AN.
- VRRP-Gruppe 1–255, kein Default-Gruppe (muss angegeben werden).
- vMAC 0000.5e00.01XX.
- `vrrp 1 ip`, `vrrp 1 priority 110`, `show vrrp`, `show vrrp brief` (Spalten Grp Pri Time Own Pre State Master addr Group addr).
- Authentifizierung: RFC 2338 (v1) hatte text/MD5; RFC 3768 und 5798 entfernten sie. IOS kann noch: `vrrp 1 authentication text <key>`, `vrrp 1 authentication md5 key-string <key>` oder key-chain. TTL=255-Check schützt gegen entfernte Injektion.
- Auth-Mismatch -> %VRRP-4-BADAUTHTYPE, beide sehen sich als Master.
- Hinweis: Neuere IOS-XE nutzen VRRPv3 (`fhrp version vrrp v3`, `vrrp 1 address-family ipv4`) – eigenes Wissen.

## 114 Switch HA
- RPR: Standby nur teilweise gebootet; bei Failover alle Module neu laden, < 2 min.
- RPR+: Standby gebootet, keine L2/L3-Funktionen; kein Reload der Module, < 30 s.
- SSO: Standby voll initialisiert, Startup+Running synchron, L2-Info + Interface-Status synchron (keine Link-Flaps), < 1 s.
- NSF (mit SSO): schneller Neuaufbau der RIB nach Switchover; FIB/CEF forwardet weiter.
- Catalyst 9400 NSF/SSO: Switchover <= 150 ms, < 200 ms Unterbrechung.

## Mögliche Kursfehler / Ungereimtheiten
- 111 Step 3: show ip arp auf R1 zeigt 192.168.1.2 als lokale Adresse (Age "-"), obwohl R1 = 192.168.1.3.
- 111 Step 7: Nach Konfig von timers msec 200 msec 750 zeigt show standby "Hello time 3 sec, hold time 10 sec".
- 111 Step 13: R2 zeigt Pri 100 ohne P, obwohl 110 + preempt konfiguriert.
- 111: "Timer müssen auf allen Geräten identisch sein" – tatsächlich lernen nicht konfigurierte Router die Timer vom Active.
- 113: "default holdtime is 3 seconds" – korrekt ist Master Down Interval 3x Adv + Skew (~3,6 s).
- 113: "default VRRP authentication is plaintext" – Default ist keine Auth; text ist nur der Default-Typ, wenn ohne Schlüsselwort konfiguriert.
