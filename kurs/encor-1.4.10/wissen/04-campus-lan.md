# Implementing Campus LAN Connectivity

Quelle: ENCOR 1.4.10 Student Guide, Seiten 31–35 (Creating a VLAN, IEEE 802.1Q, Discovery 3 „Troubleshoot VLAN and Trunk Issues“, Inter-VLAN Routing, Summary)

Topics: ENCOR-3.1.a (Layer-2-Troubleshooting: Access Ports, Trunks 802.1Q, Native VLAN, DTP, Inter-VLAN-Routing, SVIs)

Ergänzungen aus eigenem Fachwissen (nicht im Kurs) sind mit *(Ergänzung)* markiert.

## VLANs anlegen

- VLAN anlegen im globalen Konfigurationsmodus mit `vlan <id>` → wechselt in den VLAN-Konfigurationsmodus `(config-vlan)#`. Löschen mit `no vlan <id>`.
- `vlan` akzeptiert eine einzelne ID, eine Liste (Kommas) oder Bereiche (Bindestrich), z. B. `vlan 10,20,30-35`. Keine führenden Nullen eingeben.
- `name <vlan-name>` (optional): ASCII, 1–32 Zeichen, innerhalb der administrativen Domäne eindeutig. Ohne Namen vergibt der Switch `VLAN` + vierstellige Nummer (VLAN 4 → `VLAN0004`).
- Nummernbereiche:
  - VLAN 1 = Factory-Default-VLAN; alle Ports sind per Default in VLAN 1.
  - Normal Range 1–1001.
  - 1002–1005 reserviert (Token Ring/FDDI): `fddi-default`, `token-ring-default`, `fddinet-default`, `trnet-default`, Status `act/unsup`.
  - VLAN 1 und 1002–1005 werden automatisch angelegt und sind nicht löschbar.
  - *(Ergänzung)* Extended Range 1006–4094; VLAN 0 und 4095 sind reserviert (12-Bit-Feld, 4096 Werte → 1–4094 nutzbar).
- Speicherung: VIDs 1–1005 in der VLAN-Datenbank **vlan.dat im Flash**, nicht in der startup-config. Jedes neue VLAN außer VLAN 1 aktualisiert vlan.dat.

```
SwitchX(config)# vlan 2
SwitchX(config-vlan)# name Sales
SwitchX(config)# vlan 20
SwitchX(config-vlan)# name Voice
```

## Ports zuweisen, Voice VLAN

- Endgerät → Port einem **einzigen Daten-VLAN** zuordnen → Access-Port. Ein Access-Port gehört immer nur zu einem (Daten-)VLAN.
- `switchport access vlan <id>`: nicht-trunkender, ungetaggter Single-VLAN-L2-Port.
- `switchport mode access`: Port statisch als Access-Port (kein Trunk).
- `switchport voice vlan <id>`: zusätzliches Voice VLAN für ein IP-Telefon am selben Port; das Telefon taggt Sprachverkehr mit dieser VLAN-ID, der PC dahinter sendet ungetaggt ins Access-VLAN. *(Ergänzung: das Telefon lernt das Voice VLAN per CDP, alternativ LLDP-MED.)*
- *(Ergänzung)* Varianten: `switchport voice vlan <id>` (Telefon taggt mit VLAN-ID + CoS), `dot1p` (Tag mit VLAN-ID 0, nur Priorität, Sprachverkehr im Access-VLAN), `untagged` (Telefon sendet ungetaggt), `none` (Default, keine Anweisung ans Telefon).

```
SwitchX(config)# interface FastEthernet0/3
SwitchX(config-if)# switchport mode access
SwitchX(config-if)# switchport access vlan 2
SwitchX(config-if)# switchport voice vlan 20
```

### Verifikation
- `show vlan` / `show vlan brief`: eine Zeile pro VLAN mit Name, Status und **Access-Ports** (Trunk-Ports erscheinen dort NICHT). Ein Port mit Voice VLAN erscheint unter beiden VLANs (Daten- und Voice-VLAN).
- `show vlan id <id>` bzw. `show vlan name <name>`: ein einzelnes VLAN, inkl. Typ (`enet`), SAID, MTU 1500.
- `show interfaces <if> switchport`: Detail pro Port.

Eigenes Beispiel:
```
SW# show vlan brief
VLAN Name        Status    Ports
1    default     active    Gi1/0/1
2    Sales       active    Gi1/0/3
20   Voice       active    Gi1/0/3
1002 fddi-default act/unsup
...
SW# show interfaces Gi1/0/3 switchport
Name: Gi1/0/3
Switchport: Enabled
Administrative Mode: static access
Operational Mode: static access
Administrative Trunking Encapsulation: dot1q
Operational Trunking Encapsulation: native
Negotiation of Trunking: Off
Access Mode VLAN: 2 (Sales)
Trunking Native Mode VLAN: 1 (default)
Voice VLAN: 20 (Voice)
```
- Wichtige Felder: **Administrative Mode** (konfiguriert: static access, trunk, dynamic auto, dynamic desirable) vs. **Operational Mode** (tatsächlich: static access, trunk, down). Ein Port im Default `dynamic auto` läuft operativ als `static access`, solange der Nachbar keinen Trunk anfragt. `Negotiation of Trunking: On` = DTP aktiv. `Access Mode VLAN: 10 (Inactive)` = VLAN existiert nicht (mehr).

## IEEE 802.1Q und Trunks

- Trunking = viele VLANs über einen Port/Link. Jeder Frame trägt einen Tag mit seiner VLAN-ID; der Empfänger ordnet ihn anhand des Tags zu.
- 802.1Q fügt einen **4-Byte-Tag** in den Ethernet-Header ein (zwischen Quell-MAC und EtherType/Length). Quell- und Ziel-MAC bleiben unverändert. Weil die FCS über den ganzen Frame gebildet wird, muss sie **neu berechnet** werden.
- Tag-Felder:
  - TPID (16 Bit) = 0x8100 → kennzeichnet 802.1Q-Frame.
  - Priority/PCP (3 Bit) → Prioritätsstufe (CoS 0–7).
  - 1-Bit-Flag: Kurs = CFI (Canonical Format Indicator); heute DEI (Drop Eligible Indicator), siehe Fehlerliste.
  - VLAN ID (12 Bit) → identifiziert das VLAN.
- *(Ergänzung)* Maximale getaggte Frame-Größe 1522 Byte statt 1518 („baby giant“).
- 802.1Q ist ein IEEE-Standard → herstellerübergreifend. (ISL war Cisco-proprietär, *Ergänzung*: Catalyst 9000 kann nur noch dot1q.)

### Native VLAN
- Alle Frames außer denen des Native VLAN werden auf dem Trunk getaggt. Native VLAN = per Default **ungetaggt**; manuelles Taggen möglich *(Ergänzung: global `vlan dot1q tag native`; Empfang ungetaggter Frames danach laut Cisco-Guides release-abhängig beschrieben – 16.8 „akzeptiert“, 17.14 „verworfen“)*.
- Default Native VLAN = VLAN 1.
- Muss auf beiden Trunk-Enden **gleich** sein; ein Mismatch vermischt den Verkehr zweier VLANs („VLAN leaking“): ungetaggter Frame aus VLAN 1 von SW1 landet bei SW2 in dessen Native VLAN 2.
- Best Practice: ein sonst unbenutztes VLAN als Native VLAN.
- CDP warnt bei Mismatch: `%CDP-4-NATIVE_VLAN_MISMATCH: Native VLAN mismatch discovered on Ethernet0/1 (1), with SW2 Ethernet0/0 (2).` → lokaler Port (lokales Native VLAN), Nachbar + dessen Port (dessen Native VLAN).
- Kurs: Bei manchen IOS-Versionen werde CDP nicht gesendet, wenn VLAN 1 auf dem Trunk deaktiviert ist. *(Korrektur: Laut Cisco werden CDP-, VTP- und PAgP-Frames auf Trunks immer mit VLAN-1-Tag gesendet, auch wenn VLAN 1 aus der allowed-Liste entfernt wurde und nicht Native VLAN ist – „VLAN 1 minimization“ betrifft nur Nutzdaten.)*
- *(Ergänzung)* PVST+ erkennt Native-Mismatch zusätzlich und setzt den Port in den betroffenen VLANs auf „PVID inconsistent“ (blockiert).

### Trunk konfigurieren
```
SwitchX(config)# interface FastEthernet0/11
SwitchX(config-if)# switchport mode trunk
SwitchX(config-if)# switchport trunk native vlan 99
```
- Gegenseite (SwitchY) muss ebenfalls trunken und Native VLAN 99 nutzen.
- *(Ergänzung)* Auf Switches mit ISL-Unterstützung muss vorher `switchport trunk encapsulation dot1q` gesetzt werden, sonst wird `switchport mode trunk` abgelehnt (Encapsulation „auto“).

### DTP
- Dynamic Trunking Protocol: Cisco-proprietär, verhandelt Trunks automatisch; andere Hersteller unterstützen es nicht.
- Wird automatisch auf Ports mit bestimmten Trunk-Modi aktiv; verhandelt nur, wenn die Gegenseite ebenfalls DTP-fähig ist.
- Catalyst-Ports laufen per Default mit DTP (Kursausgabe: Default-Port = `dynamic auto`).
- Ergebnis-Matrix: auto+auto = Access; auto+desirable = Trunk; desirable+desirable = Trunk; trunk(on)+auto/desirable = Trunk; trunk+trunk = Trunk; access + trunk = Fehlkonfiguration.
- Im Lab: SW1 Et0/1 `on` (mode trunk), SW2 Et0/0 `desirable` → Trunk läuft.
- Empfehlung: Trunks **statisch** konfigurieren. *(Ergänzung)* `switchport nonegotiate` schaltet DTP-Frames ab (nur bei `mode trunk` oder `mode access` erlaubt, nicht bei dynamic-Modi); Nutzerports fest auf `switchport mode access`, um **Switch Spoofing** (Angreifer handelt per DTP einen Trunk aus) zu verhindern.
- *(Ergänzung)* **Double Tagging**: Angreifer im Native VLAN des Trunks sendet doppelt getaggten Frame; der erste Switch entfernt den äußeren (native) Tag, der nächste Switch sieht den inneren Tag → Frame landet im Ziel-VLAN. Nur Einweg. Gegenmaßnahmen: Native VLAN unbenutzt (kein Nutzerport darin), `vlan dot1q tag native`.

### Verifikation von Trunks
```
SwitchX# show interfaces FastEthernet0/11 switchport
Administrative Mode: trunk
Operational Mode: trunk
Administrative Trunking Encapsulation: dot1q
Negotiation of Trunking: On
Trunking Native Mode VLAN: 99

SW1# show interfaces trunk
Port   Mode  Encapsulation  Status    Native vlan
Et0/0  on    802.1q         trunking  1
Et0/1  on    802.1q         trunking  1
Port   Vlans allowed on trunk
Et0/0  1-4094
Et0/1  1-61,63-1000
Port   Vlans allowed and active in management domain
Et0/0  1,62
Et0/1  1
Port   Vlans in spanning tree forwarding state and not pruned
Et0/0  1,62
Et0/1  1
```
- Spalte **Mode**: on (= `switchport mode trunk`), desirable, auto. *(Ergänzung: Encapsulation `n-802.1q` = per DTP ausgehandelt.)*
- **Status**: trunking / not-trunking.
- Drei VLAN-Abschnitte (aufeinander aufbauend):
  1. *allowed on trunk* = konfigurierte allowed-Liste (Default 1–4094).
  2. *allowed and active in management domain* = erlaubt UND lokal existierend/aktiv.
  3. *in spanning tree forwarding state and not pruned* = davon die, die STP forwardet und VTP nicht geprunt hat.

### Allowed-VLAN-Liste *(Befehlsvarianten teilweise Ergänzung)*
- `switchport trunk allowed vlan 10,20` → **ersetzt** die Liste komplett.
- `... allowed vlan add 62` → hinzufügen (Lab-Fix).
- `... allowed vlan remove 62` → entfernen.
- `... allowed vlan except 62` → alle außer 62.
- `... allowed vlan all` → Default; `... allowed vlan none` → keins.
- Running-Config zeigt immer die resultierende Liste (z. B. `switchport trunk allowed vlan 1-61,63-1000`).
- Allowed-Listen müssen zu den Anforderungen auf **beiden** Seiten passen; fehlt ein VLAN auf einer Seite, fällt das VLAN über diesen Link aus.

## Troubleshooting VLANs (Discovery 3, Task 1)

Ablauf bei „keine Verbindung zwischen PCs im selben VLAN“:
1. Port im richtigen VLAN? → `show vlan`, `show mac address-table` (zeigt, welche MACs an welchem Port in welchem VLAN gelernt wurden). Falsch → `switchport access vlan`.
2. VLAN in der VLAN-Datenbank vorhanden? → `show vlan`, `show interfaces`, `show interfaces switchport`. Gelöschtes VLAN → Ports werden **inaktiv** (alle Ports dieses VLANs ohne Verbindung) bis VLAN neu angelegt oder Port umgehängt wird.
3. VLAN nicht per `shutdown` (im VLAN-Konfigmodus) deaktiviert? → `show vlan`.

```
SW1# show mac address-table interface FastEthernet0/1
Vlan  Mac Address     Type     Ports
10    000c.296a.a21c  DYNAMIC  Fa0/1
10    000f.34f9.9181  DYNAMIC  Fa0/1
```

### Lab-Szenario „Host isolieren“ (Topologie: PC1, PC2 an SW2; PC3, PC4 an SW1; SW1–SW2 Trunk; R1 an SW1 per Trunk)
- Ausgangslage: Nur die IP 10.10.10.182 ist bekannt (IPS-Alarm). VLANs sind unlogisch nummeriert (VLAN 62 „SixtyTwo“ für 10.10.10.0/24) → Lehre: Schema wie VLAN-ID = drittes Oktett hilft.
- R1 `show ip interface brief`: Ethernet0/0 unassigned up/up (Trunk-Elternteil), Ethernet0/0.21 = 10.10.1.1, Ethernet0/0.134 = 10.10.10.1, Loopback0 10.10.99.1.
- `show run interface Ethernet0/0.134` → `encapsulation dot1Q 62`, `ip address 10.10.10.1 255.255.255.0` → Subinterface-Nummer ≠ VLAN; maßgeblich ist `encapsulation dot1Q`.
- `ping 10.10.10.182` von R1, dann `show ip arp 10.10.10.182` → MAC aabb.cc00.5300 (im Lab variiert; Interface Ethernet0/0.134).
- SW1 `show mac address-table` → MAC am Port Et0/2, VLAN 62. Router-MAC aabb.cc00.0100 erscheint an Et0/0 in VLAN 1 **und** VLAN 62 (Subinterfaces teilen die physische MAC).
- Filter: `show mac address-table | include 0400`.
- Zeigt der Port zu einem anderen Switch (Trunk), dort weitersuchen, bis die MAC an einem Endgeräteport auftaucht (CDP zur Zuordnung).
- `show interfaces status`: Spalten Port, Name (description), Status, Vlan (`trunk` bei Trunks, sonst VLAN-Nummer), Duplex, Speed, Type. *(Ergänzung: admin-shutdown → Status `disabled`; `routed` bei `no switchport`.)*
- Isolieren: `interface Ethernet0/2` → `shutdown` → Logs `%LINK-5-CHANGED: ... administratively down`, `%LINEPROTO-5-UPDOWN: ... down`. Ping vom PC3 danach 0 %.
- Ping-Ausgabe `.!!!!` = erster Echo verloren (typisch wegen ARP-Auflösung), 4/5 = 80 %.

## Troubleshooting Trunks (Discovery 3, Task 2)

Ablauf (jeweils mit `show interfaces trunk`):
1. Native VLAN lokal = Nachbar? Nein → angleichen (sonst VLAN leaking).
2. Trunk-Modi passen / Trunk aufgebaut? Nein → beide Seiten statisch auf trunk (DTP auto+auto = not-trunking).
3. Allowed VLANs auf beiden Seiten passend? Nein → gewünschte VLANs auf beiden Seiten erlauben.

Kursbeispiel: `show interfaces Ethernet 0/3 trunk` → Mode auto, Status **not-trunking**, Native 2.

### Lab-Ablauf „PC1 erreicht PC2 (10.10.10.20), aber nicht PC4 (10.10.10.40)“
1. Ping bestätigt: PC1→PC2 ok, PC1→PC4 0 %.
2. SW2: `show cdp neighbors` → PC1 an Eth0/1, PC2 an Eth0/2, SW1 an Eth0/0 (Port-ID Eth0/1). `show vlan` → Et0/1, Et0/2 in VLAN 62. (Mit echten PCs gibt es kein CDP → stattdessen IP→ARP→MAC-Tabelle.)
3. SW1: CDP → PC4 an Eth0/3, SW2 an Eth0/1, R1 an Eth0/0 (Port-ID Eth0/0.21). `show vlan` → Et0/2, Et0/3 in VLAN 62; VLAN 1 ohne Ports (beide anderen Ports sind Trunks).
4. CDP-Meldung auf SW1: Native VLAN mismatch Ethernet0/1 (1) vs. SW2 Ethernet0/0 (2). `show interfaces trunk`: SW1 Native 1, SW2 Et0/0 desirable/Native 2.
5. Fix auf SW2: `switchport trunk native vlan 1` → CDP-Meldungen hören auf.
6. Ping PC1→PC4 weiterhin 0 % → zweiter Fehler.
7. `show interfaces trunk`: SW1 Et0/1 allowed `1-61,63-1000` → active `1` → VLAN 62 fehlt. SW2 Et0/0 allowed `1-1000`, active `1,62`.
8. `show run interface Ethernet0/1` auf SW1 bestätigt `switchport trunk allowed vlan 1-61,63-1000`.
9. Fix: `switchport trunk allowed vlan add 62`.
10. Ping `.!!!!` 80 % – kann etwas dauern (STP/ARP).
- Lehre: mehrere Fehler gleichzeitig möglich; nach jedem Fix erneut testen.

## Inter-VLAN-Routing

- Jedes VLAN = eigene Broadcast-Domäne, eigenes Switching-Segment, eigenes IP-Subnetz; zwischen VLANs wird nicht geswitcht → Layer-3-Gerät nötig.
- Option 1 – **Router mit je einem Interface pro VLAN**: mehrere physische Interfaces an Router und Switch (Switchports als Access-Ports); skaliert nicht (Interfaces gehen aus).
- Option 2 – **Router on a Stick**: ein physisches Router-Interface als Trunk an einen Switch-Trunkport; pro VLAN ein **Subinterface** (virtuelles Interface) mit eigener IP und VLAN-Zuordnung (`encapsulation dot1Q <vlan>`). Der Router routet zwischen den direkt verbundenen Subnetzen und schickt den Frame mit dem Tag des Ziel-VLANs über dasselbe physische Interface zurück. Engpass: der Trunk (Verkehr läuft hin und zurück).
- Option 3 – **Layer-3-Switch**: switcht innerhalb eines VLANs, routet zwischen VLANs (in Hardware). Braucht pro VLAN ein **VLAN-Interface (SVI)** mit IP aus dem VLAN-Subnetz und `ip routing`. Skaliert besser als Router on a Stick.
- Ein L3-Switch ist primär ein L2-Gerät mit Routing-Funktionen; ein Router ein L3-Gerät mit einigen Switching-Funktionen. Catalyst 2960 unterstützt statisches Routing auf SVIs, aber keine Routing-Protokolle. *(Ergänzung: dafür `sdm prefer lanbase-routing` + Reload.)*

```
! Router on a Stick (eigenes Beispiel)
interface GigabitEthernet0/0
 no shutdown
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 10.1.10.1 255.255.255.0
interface GigabitEthernet0/0.20
 encapsulation dot1Q 20
 ip address 10.1.20.1 255.255.255.0

! Layer-3-Switch (Kursbeispiel sinngemäß)
ip routing
interface Vlan10
 ip address 10.1.10.1 255.255.255.0
 no shutdown
interface Vlan20
 ip address 10.1.20.1 255.255.255.0
 no shutdown
```
- Hosts in VLAN 10 → Gateway 10.1.10.1, VLAN 20 → 10.1.20.1.
- *(Ergänzung)* Router-Subinterfaces: IP-Adresse wird erst akzeptiert, wenn `encapsulation dot1Q` gesetzt ist. Native VLAN am Router: `encapsulation dot1Q <vlan> native` (oder IP auf dem physischen Interface). Ist das physische Interface `shutdown`, sind alle Subinterfaces down.
- *(Ergänzung)* SVI-Status (Autostate): SVI ist up/up, wenn das VLAN existiert und aktiv ist, das SVI nicht shutdown ist und mindestens ein L2-Port in diesem VLAN up ist und im STP-Forwarding-Zustand (Access-Port im VLAN oder Trunk, der das VLAN führt). Sonst „up/down“ (bzw. down/down, wenn das VLAN fehlt). `switchport autostate exclude` auf einem Port nimmt ihn aus dieser Berechnung aus (z. B. Monitoring-Port).
- *(Ergänzung)* Ohne `ip routing` erreichen Hosts ihr eigenes SVI, aber nicht das andere VLAN.

## Fehler/Ungenauigkeiten im Kurs

1. **S. 31, show interfaces Fa0/3 switchport**: Obwohl im Beispiel `switchport mode access` konfiguriert wurde, zeigt die Ausgabe `Administrative Mode: dynamic auto` und `Negotiation of Trunking: On`. Korrekt wäre nach `switchport mode access`: `Administrative Mode: static access`, `Negotiation of Trunking: Off` (so auch korrekt in der Ausgabe auf S. 33). Quelle: Cisco Catalyst Interface/VLAN Configuration Guide, `show interfaces switchport`.
2. **S. 32, 802.1Q-Tag**: Das 1-Bit-Feld wird als CFI (MAC canonical/noncanonical) beschrieben. Seit IEEE 802.1Q-2011 heißt es **DEI (Drop Eligible Indicator)** und markiert Frames, die bei Überlast bevorzugt verworfen werden dürfen. Quelle: IEEE 802.1Q-2011/2018.
3. **S. 33, Ping-Ausgaben**: Bei `.!!!!` (R1→10.10.10.182 und PC1→10.10.10.20) steht „Success rate is 100 percent (5/5)“. Korrekt ist 80 percent (4/5) – wie in Step 7 und Step 10 richtig gezeigt.
4. **S. 33, show mac address-table auf SW1**: Es werden 4 Einträge gezeigt, aber „Total Mac Addresses for this criterion: 5“ (eine Zeile fehlt in der Darstellung).
5. **S. 32/33, „Native VLAN mismatch merges traffic between VLANs“**: Vereinfacht. Mit PVST+/Rapid PVST+ erkennt STP den Mismatch und blockiert den Port in den betroffenen VLANs (PVID_Inc), sodass das Leaking in der Praxis meist zu Verbindungsverlust führt. Quelle: Cisco STP Troubleshooting („%SPANTREE-2-RECV_PVID_ERR“).
6. **S. 33, Kursbeispiel Trunk-Troubleshooting**: Die Beispielausgabe kombiniert `not-trunking` (DTP auto) mit einer Native-VLAN-Mismatch-Meldung; ein Native-VLAN-Mismatch ist nur auf einem laufenden Trunk relevant – zwei getrennte Fehlerbilder in einem Beispiel.

## Bilder

- `bilder/04-campus-lan/01-access-voice.svg` – Access-Port mit Daten-VLAN (PC, ungetaggt) und Voice VLAN (IP-Telefon, getaggt) an einem Switchport.
- `bilder/04-campus-lan/02-dot1q-tag.svg` – Ethernet-Frame mit eingefügtem 802.1Q-Tag (TPID, PCP, DEI, VID) und neu berechneter FCS.
- `bilder/04-campus-lan/03-native-vlan.svg` – Native-VLAN-Mismatch: ungetaggter Frame wechselt das VLAN, CDP-Meldung.
- `bilder/04-campus-lan/04-trunk-show.svg` – Die drei VLAN-Listen von `show interfaces trunk` als Filterkette (allowed → active → forwarding) am Lab-Beispiel.
- `bilder/04-campus-lan/05-lab-topo.svg` – Discovery-3-Topologie (PC1–PC4, SW1, SW2, R1) mit Ports, VLAN 62 und den beiden Trunk-Fehlern.
- `bilder/04-campus-lan/06-host-finden.svg` – Host-Suche: IP → ARP am Gateway → MAC-Tabelle → Port → ggf. CDP zum nächsten Switch.
- `bilder/04-campus-lan/07-ts-flows.svg` – Entscheidungsabläufe VLAN- und Trunk-Troubleshooting.
- `bilder/04-campus-lan/08-intervlan.svg` – Drei Inter-VLAN-Routing-Optionen im Vergleich (Interface pro VLAN, Router on a Stick, L3-Switch mit SVIs).
