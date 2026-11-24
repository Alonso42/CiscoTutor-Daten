# Exploring Virtual Private Networks and Interfaces

Quelle: ENCOR 1.4.10 Student Guide, Seiten 139–146 (138 Intro, 147 Summary Challenge, 148 Answer Key nicht ausgewertet)
Topics: ENCOR-2.2.b (Data path virtualization: GRE and IPsec tunneling)

Hinweis: Abschnitte mit "(Ergänzung)" stammen nicht aus dem Kurs, sondern aus allgemeinem Fachwissen (RFCs, Cisco-Doku) und decken prüfungsrelevante Lücken des Kurses ab (IKEv1-Modi, IKEv2-Nachrichten, NAT-T, Protokollnummern).

## 1. Site-to-Site-VPN-Technologien (S. 139)

### Logische VPN-Topologien
- Physische Verkabelung ist egal – VPN-Topologie ist eine logische Verbindung der Router.
- Drei Grundtopologien:
  - **Point-to-Point**: zwei Standorte über einen gesicherten VPN-Pfad; ein Netz kann mehrere einzelne P2P-Verbindungen enthalten.
  - **Hub-and-Spoke**: alle Spokes sprechen nur mit dem zentralen Hub. Verkehr läuft meist Spoke↔Hub; Spoke-zu-Spoke ist nur als Relais über den Hub möglich.
  - **Full Mesh**: jeder mit jedem – any-to-any, optimale direkte Pfade, maximale Flexibilität; aber n·(n−1)/2 Tunnel.
- Kombinationen:
  - **Partial Mesh**: ein Teil voll vermascht, andere Geräte per Hub-and-Spoke oder P2P angehängt. Weniger Redundanz als Full Mesh, dafür billiger; typisch für Randnetze an einem vermaschten Backbone.
  - **Tiered Hub-and-Spoke**: ein Gerät ist Hub in einer Topologie und Spoke in einer anderen; Spoke-Gruppen reden mit ihrem nächsten Hub.
  - **Joined Hub-and-Spoke**: zwei Topologien werden über eine P2P-Verbindung gekoppelt, z. B. zwei Hubs als P2P-Peers.

### Eigenschaften von Site-to-Site-VPNs
- Ersatz für klassisches geroutetes WAN (eigene Standorte oder Partner) → geringere Kosten, skalierbar.
- Authentisieren die VPN-Geräte (Peers/Sites), nicht einzelne Benutzer; kryptografischer Pfadschutz über unsichere Netze (Internet oder MPLS-WAN).
- Einfache firewallähnliche Kontrollen (Verkehr begrenzen, Spoofing verhindern).
- Meist IPsec als Kryptografie.
- Laufen oft über kontrollierte Transportnetze (MPLS) oder Internet-Backbones; wenig Filterprobleme im Transport.
- Kernverbindung des Unternehmens → Hochverfügbarkeit und QoS oft nötig.
- Lösungen: **DMVPN** (keine permanente Verbindung zwischen Sites, IPsec-Tunnel dynamisch; mGRE + NHRP), **FlexVPN** (IKEv2-basiert).
- Cisco-Router und Cisco ASA unterstützen Site-to-Site-Full-Tunnel-IPsec-VPNs.

### Abgrenzung (Ergänzung)
- **Remote-Access-VPN**: einzelner Benutzer/Client verbindet sich mit dem Unternehmen (Client-basiert z. B. Cisco Secure Client/AnyConnect mit SSL/TLS oder IKEv2/IPsec, oder clientless über Browser). Authentisierung des Benutzers.
- **MPLS-VPN (L3VPN)**: vom Provider bereitgestellt, trennt Kunden per VRF/Labels, verschlüsselt aber nicht. Wer Vertraulichkeit braucht, legt IPsec (z. B. GETVPN) darüber.

## 2. IPsec-Überblick (S. 140)
- Architektur in RFC 4301. Dienste auf IP-Ebene: Zugriffskontrolle, verbindungslose Integrität, Datenursprungs-Authentisierung, Schutz gegen Replays, Vertraulichkeit, begrenzte Verkehrsfluss-Vertraulichkeit. Schützt IP und alle höheren Protokolle.
- Bausteine:
  - **IKE / IKEv2**: Rahmen für Policy-Aushandlung und Schlüsselverwaltung.
  - **AH (Authentication Header)**: Integrität, Ursprungs-Authentisierung, Anti-Replay – **keine Verschlüsselung**; gilt als weitgehend obsolet; auf Cisco ASA nicht unterstützt.
  - **ESP (Encapsulating Security Payload)**: Integrität, Ursprungs-Authentisierung, Anti-Replay **und Vertraulichkeit** (Verschlüsselung) – bevorzugt.
  - AH und ESP können laut RFC kombiniert werden; meist reicht eines (ESP). Cisco IOS XE unterstützt die Transform-Set-Kombination AH+ESP nicht (Security for VPNs with IPsec Config Guide).
- IPsec schützt Pfade zwischen zwei Hosts, zwei Security Gateways (Router/Firewalls) oder Gateway↔Host.
- Neue Header: Transport Mode → hinter dem IP-Header, vor TCP/UDP. Tunnel Mode → neuer IP-Header ersetzt/umschließt das Original, ganzes Originalpaket verschlüsselt. Cisco-IPsec-VPNs nutzen standardmäßig Tunnel Mode.
- Protokollnummern (Ergänzung): **ESP = IP-Protokoll 50**, **AH = IP-Protokoll 51**, IKE = **UDP 500**, NAT-T = **UDP 4500**.
- Sicherheitsziele (Ergänzung, Merkhilfe): Confidentiality (AES, 3DES, DES), Integrity (HMAC-SHA, HMAC-MD5), Authentication (PSK, RSA-Signaturen/Zertifikate, RSA-encrypted nonces), Anti-Replay (Sequenznummern im ESP/AH-Header).

### Security Associations (SA)
- SA = Beschreibung der Schutzparameter für einen Verkehrsfluss: Algorithmen, Schlüssel, Traffic-Spezifikation, weitere Parameter (Lifetime …).
- IPsec-SAs sind **unidirektional** → für bidirektionalen Verkehr mindestens zwei (eine pro Richtung). Jede SA wird über einen **SPI** identifiziert (Ergänzung).
- Die **IKE-SA** ist eine eigene, getrennte SA (bidirektional), über die IKE dann die IPsec-SAs für den IPsec-Stack aushandelt.

### IKE
- Hybridprotokoll aus **ISAKMP** (Rahmen/Paketformat), **Oakley** und **SKEME** (Schlüsselaustauschverfahren). IOS verwendet "ISAKMP" und "IKE" synonym (Befehle `crypto isakmp …`).
- Gründe für IKE (statt manueller Schlüssel): Skalierbarkeit, handhabbare Konfiguration, Aushandlung der SA-Eigenschaften, automatische Schlüsselerzeugung und automatischer Rekey.

## 3. IKE / ISAKMP-Policy (S. 141)
- Beide Peers müssen sich auf eine ISAKMP-Policy einigen. Inhalt (Merkwort **HAGLE**):
  - **H**ash/HMAC (Integrität + Absender): SHA-1, SHA-2 (SHA-256/384/512), MD5 (vermeiden)
  - **A**uthentication: pre-share, rsa-sig, rsa-encr
  - **G**roup: DH-Gruppe (Stärke des Schlüsselaustauschs; daraus werden Encryption- und Hash-Keys abgeleitet)
  - **L**ifetime: wie lange der Schlüssel benutzt wird, bevor er ersetzt wird
  - **E**ncryption: DES (vermeiden), 3DES, AES-128/192/256
- IKE kann mehrere Policies vergleichen (Priorität = Sequenznummer, kleinere Nummer = höhere Priorität).

### IKEv1-Ablauf (Ergänzung)
- **Phase 1** baut die IKE-SA (sicherer Kanal):
  - **Main Mode**: 6 Nachrichten. 1–2 Policy-Vorschläge (SA-Proposals), 3–4 DH-Austausch + Nonces (ggf. NAT-Discovery), 5–6 Authentisierung (bereits verschlüsselt, Identität geschützt).
  - **Aggressive Mode**: 3 Nachrichten, schneller, Identität wird im Klartext übertragen (weniger sicher); oft bei Remote-Access mit PSK und dynamischer IP.
- **Phase 2 – Quick Mode**: 3 Nachrichten, geschützt durch die IKE-SA, handelt die IPsec-SAs (Transform Set, Proxy-Identitäten, Lifetime) aus; optional **PFS** = neuer DH-Austausch für die IPsec-Schlüssel.
- IKEv1-Main-Mode-Zustände in `show crypto isakmp sa`: MM_NO_STATE → MM_SA_SETUP → MM_KEY_EXCH → MM_KEY_AUTH → **QM_IDLE** (= Phase 1 fertig, IKE-SA steht und ist bereit für Quick Mode). Aggressive Mode: AG_*-Zustände.
  - Hängt bei MM_NO_STATE: keine passende Policy/keine Antwort (UDP 500 blockiert, Peer unerreichbar, Policy-Mismatch).
  - Hängt bei MM_KEY_EXCH: typisch falscher Pre-Shared Key (Authentisierung schlägt fehl).

### IKEv2 (Ergänzung)
- RFC 7296, nicht rückwärtskompatibel zu IKEv1.
- Basisaustausch nur **4 Nachrichten**: **IKE_SA_INIT** (2 Nachrichten: Algorithmen, DH, Nonces) + **IKE_AUTH** (2 Nachrichten: Identität, Authentisierung, gleichzeitig erste Child-SA = IPsec-SA). Weitere Child-SAs/Rekey per **CREATE_CHILD_SA**; Löschen/DPD per **INFORMATIONAL**.
- Eingebaut: NAT-Traversal, Dead Peer Detection (Liveness), Anti-DoS-Cookies, **EAP** für Benutzer-Authentisierung (Remote Access), **asymmetrische** Authentisierung (z. B. eine Seite PSK, andere Zertifikat).
- Basis von **FlexVPN**. IOS-Bausteine: `crypto ikev2 proposal`, `crypto ikev2 policy`, `crypto ikev2 keyring`, `crypto ikev2 profile`.

### NAT-Traversal (Ergänzung)
- ESP hat keine Ports → PAT kann ESP nicht übersetzen; AH bricht bei NAT immer, weil AH den (unveränderlichen Teil des) äußeren IP-Header(s) mit authentisiert.
- NAT-T erkennt NAT (NAT-D-Payloads) und kapselt ESP in **UDP 4500**; IKE wechselt ebenfalls auf UDP 4500.
- Firewall zwischen Peers muss erlauben: UDP 500, UDP 4500, ESP (IP 50) (AH: IP 51, falls verwendet).

## 4. IPsec-Modi (S. 142)
- **Transport Mode**: nur der Payload wird verschlüsselt, Original-IP-Header bleibt (ESP-Header wird dahinter eingefügt). Für Hosts und Gateways; schützt Upper-Layer-Protokolle und ausgewählte IP-Header-Felder. Typisch: End-to-End oder GRE over IPsec/DMVPN (GRE liefert schon den äußeren Header → spart 20 Byte).
- **Tunnel Mode**: ganzes Originalpaket inkl. Original-IP-Header verschlüsselt, neuer äußerer IP-Header (Adressen der Gateways). Nötig, wenn das Ziel des Pakets nicht der Endpunkt der Verschlüsselung ist (VPN-Gateways verschlüsseln fremden Verkehr). Versteckt auch private/nicht registrierte Adressen.
- ESP-Paketaufbau:
  - Transport: `[IP HDR][ESP HDR][Daten][ESP Trailer][ESP Auth]`
  - Tunnel: `[New IP HDR][ESP HDR][IP HDR][Daten][ESP Trailer][ESP Auth]`
  - **Verschlüsselt**: alles zwischen ESP-Header und ESP-Trailer (inkl. Trailer) – im Tunnel Mode also inkl. Original-IP-Header.
  - **Authentisiert** (ESP-ICV): ESP-Header bis ESP-Trailer. Der äußere (neue) IP-Header ist bei ESP **nicht** authentisiert → NAT-tauglich (mit NAT-T).
  - AH dagegen authentisiert das ganze Paket inklusive der unveränderlichen Felder des äußeren IP-Headers → NAT-inkompatibel.
- ESP-Header (Ergänzung): SPI (32 Bit) + Sequenznummer (32 Bit, Anti-Replay); Trailer: Padding, Pad Length, Next Header; ESP Auth = ICV.
- Overhead (Ergänzung): Tunnel Mode zusätzlich 20 Byte neuer IPv4-Header; ESP-Overhead variabel (IV, Padding, ICV).

## 5. IPsec-VPN-Typen auf Cisco IOS (S. 143)
- **VTI (Virtual Tunnel Interface)**: IPsec-Site-to-Site über ein Tunnelinterface; Verkehr kommt nur an Tunnelendpunkten in den Tunnel; neue Header kapseln den Verkehr.
- **DMVPN**: skalierbare IPsec-VPNs, zentral gesteuert; direkte Branch-zu-Branch-Verbindungen (z. B. VoIP) ohne permanente Tunnel; Zero-Touch-Bereitstellung; weniger Latenz/Jitter, entlastet die Zentrale. Bausteine: mGRE, NHRP, IPsec, Routing-Protokoll.
- **FlexVPN**: einheitliche Lösung auf Basis von **IKEv2** für alle VPN-Arten (Remote Access, Teleworker, Site-to-Site, Mobility, Managed Security). Vorteile:
  - Transport: Internet oder privates MPLS-VPN
  - Ein Headend nimmt Site-to-Site- und Remote-Access-Verbindungen gleichzeitig an
  - Redundanz: dynamisches Routing über Tunnel; IKEv2-basierte Routenverteilung + Server-Clustering; IPsec/IKEv2-Active/Standby-Stateful-Failover zwischen zwei Chassis
  - Interoperabel mit IKEv2-Fremdherstellern inkl. nativer Clients von iOS/Android
  - Multicast: Hub repliziert pro Spoke oder lässt das Transportnetz nach der Verschlüsselung replizieren
  - Hierarchisches QoS pro Tunnel/SA
  - Zentrale Policies (Split-Tunnel, VRF-Auswahl, DNS …) via AAA/RADIUS pro Peer
  - VRF-aware: Inside-VRF und Front-Door-VRF
- **GET VPN** (nur erwähnt; Ergänzung): tunnelloses Gruppen-IPsec mit GDOI und Key Server, behält Original-IP-Header bei, ideal für any-to-any über private MPLS-WANs.

## 6. Cisco IOS VTI (S. 144)
- Einfacher als GRE/L2TP + Crypto Map; keine statische Bindung der IPsec-Session an ein physisches Interface; Tunnelendpunkt ist ein virtuelles, routbares Interface → normale Interface-Features nutzbar.
- Ersetzt Crypto-Map-Konfiguration; Crypto Maps werden intern pro Tunnel automatisch erzeugt (in `show crypto ipsec sa` sichtbar als `Crypto map tag: Tunnel0-head-0`).
- Features für Klartext (z. B. QoS, ACL auf Benutzerverkehr) auf dem VTI; Features für verschlüsselten Verkehr auf dem physischen Außeninterface.
- Eigenschaften: verhält sich wie ein normaler Tunnel (einer pro Remote-Site); Kapselung ESP oder AH; **Line Protocol hängt vom Zustand der IPsec-SAs ab**.
- Vorteile: einfachere Konfiguration, flexible Feature-Platzierung, **Multicast-Unterstützung**, bessere Skalierbarkeit (weniger SAs – eine SA-Paar für alles statt pro ACL-Eintrag), routbares Interface → alle IP-Routing-Protokolle.
- Grenzen: nur IP-Unicast und -Multicast (GRE ist multiprotokollfähig); IPsec-Stateful-Failover wird nicht unterstützt (stattdessen Routing-Protokolle).
- Kurs-Hinweis: nicht dieselbe IP wie das physische Interface verwenden (Rekursion/Flapping mit dynamischem Routing) – der Kurs nutzt aber selbst `ip unnumbered` auf das physische Interface (siehe Fehlerliste).
- Deployment:
  - Static VTI für P2P; **Dynamic VTI** (Virtual-Template) am Hub großer Hub-and-Spoke-Netze.
  - Dynamisches Routing in großen Netzen bzw. für Pfad-/Peer-Redundanz; sonst statisch.
  - VTI = Standard für einzelne P2P-Links und Hub-and-Spoke; DMVPN oder GET VPN für große Partial/Full-Mesh-Umgebungen.

Beispiel (eigene Adressen):
```
interface Tunnel0
 description VPN zu Filiale 12
 ip unnumbered GigabitEthernet0/0
 tunnel source GigabitEthernet0/0
 tunnel destination 198.51.100.2
 tunnel mode ipsec ipv4
 tunnel protection ipsec profile VPN-PROF
```
- Für IPv6: `tunnel mode ipsec ipv6` (Ergänzung).

### IKE-Peering mit PSK planen
- Schritte: IKE-SA aufbauen, PSK für gegenseitige Authentisierung, Encryption+Hash für den IKE-Kanal, DH-Gruppe passender Stärke, passende Lifetime, PSK an Name/IP des Peers binden.
- Authentisierungsmethoden in IOS: PSK, RSA-encrypted nonces, RSA-Signaturen.
- DH-Länge über die Gruppe: 1 = 768 Bit, 2 = 1024, 5 = 1536, 14 = 2048, 15 = 3072, 16 = 4096; 19/20/21 = ECP 256/384/521 (Ergänzung für 1, 15, 16, 19–21). Höhere Gruppe = stärker, aber mehr Rechenaufwand beim Tunnelaufbau.
- Default-IKE-Policies (seit IOS 12.4(20)T): 8 Stück, Prioritäten 65507 (höchste) … 65514 (niedrigste). PSK-basierte:

| Priorität | Auth | Encryption | Hash | DH |
|---|---|---|---|---|
| 65508 | PSK | AES | SHA | 5 |
| 65510 | PSK | AES | MD5 | 5 |
| 65512 | PSK | 3DES | SHA | 2 |
| 65514 | PSK | 3DES | MD5 | 2 |

- Empfehlungen: MD5 und DH 2 meiden; SHA-2 bevorzugen; DH 14+ für langfristigen Schutz. Default-Policies abschaltbar mit `no crypto isakmp default policy`; erscheinen in `show crypto isakmp policy`, solange keine eigene Policy existiert.
- Lifetime muss nicht übereinstimmen – es gilt der kürzere Wert (Cisco-Doku formal: Match, wenn die Lifetime des Remote-Peers ≤ der lokalen ist; in der Praxis senkt IOS auf den kürzeren Wert). IOS-Default IKE-Lifetime 86400 s (Ergänzung). IPsec-SA-Default 3600 s / 4 608 000 KB (im Lab-Output sichtbar).

Konfiguration (eigene Werte):
```
crypto isakmp policy 10
 authentication pre-share
 hash sha
 encryption aes 128      ! Kurzform: encr aes 128
 group 14
 lifetime 3600
crypto isakmp key MeinLangerSchluessel address 203.0.113.2
```
- Reihenfolge: erst Policy, dann Credentials. Gegenstelle spiegelbildlich.

### Verifikation / Troubleshooting
- Ablauf: Verkehr geht nicht durch den VTI → (1) IKE-SA prüfen (`show crypto isakmp policy`, `show crypto isakmp sa`) – sonst IKE-SA troubleshooten; (2) IPsec-SA prüfen (`show crypto ipsec sa`) – sonst IPsec-Policies (Transform Set) angleichen; (3) Routing in den Tunnel prüfen – sonst statische Routen/IGP über den Tunnel.
- `show crypto isakmp sa`: Spalten dst, src, state, conn-id, status; gesund = `QM_IDLE` + `ACTIVE`.
- IKE-Session wird erst aufgebaut, wenn IPsec sie anfordert (interessanter Verkehr bzw. VTI-Bringup).
- Weitere (Ergänzung): `show crypto session` (UP-ACTIVE), `debug crypto isakmp`, `clear crypto sa counters` (setzt Zähler zurück), `clear crypto session`.

## 7. Discovery 17 – Static VTI Point-to-Point (S. 145)
Topologie: PC1 (10.10.1.11) – E0/1 **R2** E0/0 (172.17.1.2) – (172.17.1.1) E0/0 **R1** E0/1 (172.18.4.1) – (172.18.4.2) E0/0 **R3** E0/1 (10.10.2.1) – PC2 (10.10.2.12). R1 = Internet/Transit, R3 vorkonfiguriert.

Schritte auf R2:
1. `crypto isakmp policy 10` mit pre-share, sha, aes 128, group 14, lifetime 3600
2. `crypto isakmp key cisco address 172.18.4.2`
3. `crypto ipsec transform-set MYSET esp-aes 128 esp-sha-hmac` (muss zum Peer passen)
4. `crypto ipsec profile MYPROFILE` → `set transform-set MYSET`
5. `interface Tunnel0` → `ip unnumbered Ethernet0/0`, `tunnel source Ethernet0/0`, `tunnel destination 172.18.4.2`
6. `tunnel mode ipsec ipv4`, `tunnel protection ipsec profile MYPROFILE`
7. `ip route 10.10.2.0 255.255.255.0 Tunnel0`

Wichtige Ausgaben (gekürzt, sinngemäß):
- `show crypto ipsec sa`: `interface: Tunnel0`, `Crypto map tag: Tunnel0-head-0`, local/remote ident `0.0.0.0/0.0.0.0/0/0` (VTI schützt "alles", was in den Tunnel geroutet wird), `current_peer 172.18.4.2 port 500` (kein NAT-T), Zähler `#pkts encaps/encrypt/digest` und `#pkts decaps/decrypt/verify`, `plaintext mtu 1438`, `PFS (Y/N): N`, inbound/outbound ESP-SAs mit SPI, `transform: esp-aes esp-sha-hmac`, `in use settings ={Tunnel, }`, `sa timing: remaining key lifetime (k/sec): (4608000/3537)`, `IV size: 16 bytes`, `replay detection support: Y`, `Status: ACTIVE`. Keine AH-SAs.
- Vor dem Ping: Zähler 0; nach 5 Pings: encaps 5/decaps 5; nach weiteren 5 PC-Pings: 10/10.
- `show interface tunnel 0`: up/up, `Interface is unnumbered. Using address of Ethernet0/0`, `Tunnel protocol/transport IPSEC/IP`, `Tunnel transport MTU 1438 bytes`, `Tunnel protection via IPSec (profile "MYPROFILE")`, Keepalive not set.
- `show ip route`: `S 10.10.2.0/24 is directly connected, Tunnel0`.
- Troubleshooting-Gedanken: encaps steigt, decaps bleibt 0 → Rückweg/Peer-Seite (Route, Transform-Set/ACL beim Peer, ESP gefiltert); beide 0 → kein Verkehr in den Tunnel geroutet bzw. SA nicht aufgebaut.

## Fehler/Ungenauigkeiten im Kurs
1. S. 140: "IKE … defined by RFC 2408" – falsch. RFC 2408 ist ISAKMP; IKE(v1) ist RFC 2409; IKEv2 ist RFC 7296. (Quelle: rfc-editor.org, RFC 2409 "The Internet Key Exchange (IKE)")
2. S. 144/145: Der Kurs warnt, der Tunnel solle nicht dieselbe IP wie das physische Interface nutzen, konfiguriert aber im Beispiel und im Lab `ip unnumbered GigabitEthernet0/0`/`Ethernet0/0` – also genau das. Mit statischen Routen funktioniert es, mit dynamischem Routing besser eine eigene Tunnel-IP oder ein Loopback verwenden.
3. S. 145, Lab Schritt 4: Ping auf 10.10.2.1 mit Quelle Ethernet0/1, die Ausgabe zeigt aber "Sending … to 10.10.10.1" und "source address of 172.16.2.3" – inkonsistente Beispielausgabe (richtig wäre Ziel 10.10.2.1, Quelle 10.10.1.1).
4. S. 145, Command List: `ip unnumbered` wird als "Assigns an IP subnet and address to the interface" beschrieben – ungenau; der Befehl leiht sich die Adresse eines anderen Interfaces, ohne eigenes Subnetz.
5. S. 140/142: Tunnel Mode "verschlüsselt Payload und Header" – gemeint ist der Original-IP-Header; der neue äußere Header ist natürlich unverschlüsselt.
6. S. 141: "security appliance" in der IOS-Policy-Beschreibung (Text aus ASA-Doku übernommen) – gilt gleichermaßen für Router.

## Bilder
- `bilder/14-vpn/01-vpn-topologien.svg` – Point-to-Point, Hub-and-Spoke und Full Mesh im Vergleich mit Tunnelanzahl.
- `bilder/14-vpn/02-site-to-site-vpn.svg` – Remote-Sites per IPsec-Tunnel an ein Gateway; intern unverschlüsselt zu den Ressourcen.
- `bilder/14-vpn/03-ike-sa-ipsec-sa.svg` – eine bidirektionale IKE-SA und zwei unidirektionale IPsec-SAs mit SPI zwischen zwei Peers.
- `bilder/14-vpn/04-isakmp-policy-hagle.svg` – Bestandteile der ISAKMP-Policy (HAGLE) mit Beispielwerten.
- `bilder/14-vpn/05-esp-transport-tunnel.svg` – ESP-Paketaufbau Transport vs. Tunnel Mode mit verschlüsseltem und authentisiertem Bereich.
- `bilder/14-vpn/06-ike-ablauf.svg` – IKEv1 Main Mode (6) + Quick Mode (3) vs. IKEv2 IKE_SA_INIT/IKE_AUTH (4).
- `bilder/14-vpn/07-vpn-typen.svg` – VTI, DMVPN und FlexVPN nebeneinander.
- `bilder/14-vpn/08-vti-konfiguration.svg` – Bausteinkette Policy → Key → Transform Set → IPsec Profile → Tunnel-Interface → Route.
- `bilder/14-vpn/09-vti-troubleshooting.svg` – Prüfreihenfolge IKE-SA → IPsec-SA → Routing.
- `bilder/14-vpn/10-lab-topologie.svg` – Lab-Topologie R2–R1–R3 mit Adressen und VTI.
