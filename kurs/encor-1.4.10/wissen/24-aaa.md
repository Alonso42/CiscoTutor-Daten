# Implementing Secure Access Control

Quelle: ENCOR 1.4.10 Student Guide, Seiten 256–265 (255 Intro, 266 Summary Challenge und 267 Answer Key nicht ausgewertet)

Topics: ENCOR-5.1.a (Lines, Passwörter, lokale Benutzer, SSH, Privilege Levels), ENCOR-5.1.b (AAA mit RADIUS/TACACS+: Authentication, Authorization, Accounting)

Ergänzungen, die nicht im Kurs stehen, sind mit *(Ergänzung)* markiert. Quellen: Cisco IOS XE 17.x Security Configuration Guide (AAA, Configuring Authentication/Authorization/Accounting, Secure Shell), Cisco IOS Security Command Reference (`address ipv4 (RADIUS)`, `aaa authorization`, `login block-for`), RFC 2865/2866 (RADIUS), RFC 8907 (TACACS+).

---

## 1. Zugriff auf das Gerät absichern (S. 256)

### Zugangswege
| Weg | Art | Bewertung |
|---|---|---|
| Console-Port, AUX-Port | serielle, direkte Verbindung (Out-of-Band) | physischer Zugang nötig, trotzdem Passwort setzen |
| vty-Lines per **Telnet** (TCP 23) | In-Band über das Netz | alles im Klartext – auch Benutzername und Passwort; mitschneidbar |
| vty-Lines per **SSH** (TCP 22) | In-Band, verschlüsselt | Standard; Client kann die Identität des Servers prüfen (Schutz vor Man-in-the-Middle), Zugangsdaten und Daten verschlüsselt |
| GUI per HTTP / **HTTPS** | Web | HTTPS bevorzugen (Server-Identität, Verschlüsselung) |

Best Practice: Passwörter möglichst zentral auf einem AAA-Server; lokal gespeicherte Passwörter in der Konfiguration nur gehasht/verschlüsselt.

### Passwortarten
1. **Enable-Passwort/-Secret** – Zugang zum privilegierten EXEC-Modus (Level 15)
2. **Line-Passwort** – Login an console/aux/vty
3. **Username-Passwort** – lokale Benutzerdatenbank

### Enable Secret und Hash-Typen
```
Router(config)# enable algorithm-type ?
  md5     -> Type 5
  scrypt  -> Type 9
  sha256  -> Type 8 (PBKDF2 mit SHA-256)
Router(config)# enable algorithm-type scrypt secret MySecret
Router# show running-config | include enable
enable secret 9 $9$...
Router(config)# enable secret class
enable secret 5 $1$...          <- im Kursbeispiel klassisches MD5
```
- `enable algorithm-type` gibt es seit IOS 15.3(3).
- Die Zahl vor dem Hash verrät den Typ:

| Typ | Verfahren | Bewertung |
|---|---|---|
| 0 | Klartext | nie verwenden |
| 4 | SHA-256 ohne Salt *(Ergänzung)* | fehlerhaft implementiert, abgekündigt |
| 5 | MD5 (gesalzen) | gilt als unsicher, vermeiden |
| 6 | AES, umkehrbar *(Ergänzung; Kurs erwähnt `password encryption aes`)* | für Schlüssel/Keys, die das Gerät im Klartext braucht |
| 7 | Vigenère-Verschlüsselung (`service password-encryption`) | trivial umkehrbar – nur Schutz vor Schulterblick |
| 8 | PBKDF2-SHA-256 | gut |
| 9 | scrypt | am stärksten gegen Brute Force (Kurs-Empfehlung) |

- `enable password X` (ohne secret) wird im Klartext (Typ 0) bzw. mit `service password-encryption` als Typ 7 gespeichert. Sind `enable password` und `enable secret` beide gesetzt, gilt **enable secret** *(Ergänzung, Cisco-Standardverhalten)*.
- `enable secret level N` legt ein Secret für ein bestimmtes Privilege Level fest; ohne Level gilt es für Level 15 (Kurs, Discovery Schritt 2).

### Line-Passwort
```
line con 0
 password cisco
 login                 <- fragt das Line-Passwort ab
 exec-timeout 5 0      <- Minuten Sekunden; nach 5 min Inaktivität abmelden
Router(config)# service password-encryption
 -> line con 0 / password 7 1511021F0725
```
- `login` = Authentifizierung nur mit dem Line-Passwort (kein Benutzername, keine Nachvollziehbarkeit).
- `service password-encryption` verschlüsselt alle bisherigen und künftigen Klartext-Passwörter (Line-, enable password-, username password-) als Typ 7. Secrets bleiben unberührt. *(Ergänzung: Ein späteres `no service password-encryption` entschlüsselt bereits verschlüsselte Passwörter nicht wieder.)*
- *(Ergänzung)* Default exec-timeout = 10 Minuten; `exec-timeout 0 0` schaltet den Timeout ab (nicht empfohlen).
- *(Ergänzung)* vty mit `login`, aber ohne `password`: Telnet-/SSH-Verbindung wird mit „Password required, but none set“ abgewiesen.

### Username-Passwort (lokale Benutzerdatenbank)
```
username badexample password badpassword                 -> Typ 0 bzw. 7
username admin privilege 15 secret Cisco123                -> Typ 5 im Kursbeispiel
username tier1 algorithm-type scrypt secret tier1secret    -> Typ 9
username tier2 algorithm-type sha256 secret tier2secret    -> Typ 8
line vty 0 4
 login local             <- lokale Benutzerdatenbank statt Line-Passwort
```
- `privilege 15` = höchste Stufe, alle Befehle.
- `login local` ersetzt die Abfrage des Line-Passworts (das Line-Passwort wird dann nicht mehr benutzt).
- Für HTTP/HTTPS-Zugriff mit der lokalen Datenbank: `ip http authentication local`.

### Privilege Levels *(teilweise Ergänzung)*
| Level | Bedeutung |
|---|---|
| 0 | nur wenige Befehle (disable, enable, exit, help, logout) |
| 1 | User EXEC (`>`), Standard nach dem Login |
| 2–14 | frei definierbar, z. B. `privilege exec level 5 show running-config`, Zugang mit `enable 5` |
| 15 | privileged EXEC (`#`), alle Befehle |

Prüfen mit `show privilege`. `disable` kehrt zu Level 1 zurück.

### Weitere Härtungsbefehle
| Befehl | Modus | Wirkung |
|---|---|---|
| `security passwords min-length N` | global | Mindestlänge für Benutzer-, enable- und Line-Passwörter (Kurs-Tabelle schreibt fälschlich `security password`) |
| `transport input ssh` | line vty | nur SSH, Telnet wird abgewiesen |
| `login block-for S attempts N within T` | global | nach N Fehlversuchen in T Sekunden S Sekunden „Quiet Period“ (keine Logins) |
| `login quiet-mode access-class ACL` | global | Hosts aus der ACL dürfen auch während der Quiet Period verbinden |
| `login delay S` | global | Wartezeit zwischen Login-Versuchen; nur `login block-for` → automatisch 1 s Delay |

- Login Block wirkt auf virtuelle Verbindungen (Telnet, SSH), bremst Wörterbuch-/DoS-Angriffe.
- `login block-for` muss vor `login delay` konfiguriert sein.
- *(Ergänzung)* `show login` zeigt Zustand und Quiet Mode; `login on-failure log` / `login on-success log` erzeugen Syslog-Meldungen.

## 2. AAA-Framework (S. 257)
| Funktion | Frage | Inhalt |
|---|---|---|
| **Authentication** | Wer bist du? | Identität prüfen (Credentials gegen Datenbank), optional Challenge/Response |
| **Authorization** | Was darfst du? | Rechte: welche EXEC-Befehle, Zugang zur Shell, Privilege Level, PPP/SLIP; als Attribut-Wert-Paare (AV pairs) lokal oder auf dem Server |
| **Accounting** | Was hast du getan? | Logins, Befehle, Sitzungsdauer, Bytes → AV-Paare an den Accounting-Server; Billing, Audit, Reporting |

- Authentication funktioniert allein; Authorization setzt immer eine Authentifizierung voraus. Accounting kann laut Cisco allein oder zusammen mit den anderen beiden eingesetzt werden (z. B. `aaa accounting system` für Geräteereignisse).
- Bei jeder einzelnen Funktion (z. B. ein Befehl) kann das Gerät den Server um Erlaubnis fragen (Command Authorization).

## 3. Vorteile von AAA (S. 258)
- **Flexibilität/Granularität**: Autorisierung pro Befehl oder pro Interface – mit lokalen Passwörtern nicht möglich.
- **Skalierbarkeit**: zentrale Benutzerverwaltung statt Benutzer auf jedem Gerät; jeder Admin mit eigenem Konto → Aktionen nachvollziehbar (keine geteilten Konten).
- **Standard und proprietär**: RADIUS ist offener Standard (Hersteller mischbar), TACACS+ von Cisco.
- **Redundanz**: mehrere Server in einer Server-Gruppe; fällt einer aus, wird der nächste gefragt.
- (Routing-Protokoll-Authentifizierung ist kein AAA-Vorteil.)

## 4. Authentifizierungsoptionen und Method Lists (S. 259)
Faktoren: etwas, das man **weiß** (Passwort), **hat** (Zertifikat), **ist** (Biometrie).

```
aaa authentication <service> {default | LISTNAME} method1 [method2 ...]
  service: login (CLI: Console, Telnet, SSH), enable, ppp, dot1x ...
  methods: group radius | group tacacs+ | group GRUPPENNAME | local | local-case | enable | line | none
```
- **default**-Liste: gilt automatisch für alle Lines/Interfaces ohne eigene benannte Liste.
- **Benannte** Liste: wirkt erst, wenn sie zugewiesen wird (`login authentication NAME` unter der Line) und hat dann Vorrang vor default.
- **Fallback-Regel**: Die nächste Methode wird nur bei **ERROR** probiert (Server nicht erreichbar/keine Antwort), **nicht bei FAIL** (Server lehnt Benutzer/Passwort ab). Ein falsches Passwort auf dem Server führt also nicht zur lokalen Datenbank.
- `local` = lokale Benutzer (Benutzername case-insensitiv), `local-case` = Benutzername case-sensitiv, `enable` = enable-Passwort, `line` = Line-Passwort, `none` = Zugang ohne Authentifizierung, wenn alle vorherigen Methoden ERROR liefern – in Produktion vermeiden.
- Server einer Gruppe werden der Reihe nach gefragt; der nächste Server nur, wenn der vorherige nicht antwortet.

## 5. RADIUS und TACACS+ (S. 260)
Client-Server-Modell: Benutzer → **NAS** (Network Access Server, z. B. Router, Switch, Firewall, AP) → AAA-Server (z. B. Cisco ISE, früher Cisco Secure ACS). Das Gerät ist RADIUS-/TACACS+-**Client**.

| | RADIUS | TACACS+ |
|---|---|---|
| Herkunft | Livingston Enterprises, offener Standard (RFC 2865 Authc/Authz, RFC 2866 Accounting) | Cisco (heute als RFC 8907 dokumentiert, *Ergänzung*) |
| Transport | UDP 1812 (Authc+Authz), 1813 (Accounting); Altports 1645/1646 | TCP 49 |
| AAA-Trennung | Authentication + Authorization kombiniert, Accounting getrennt | alle drei Funktionen getrennt |
| Challenge/Response | einseitig, eine Challenge | zweiseitig, mehrere Challenges |
| Verschlüsselung | nur das Passwort (User-Password-Attribut) | gesamter Paket-Body (Header bleibt lesbar, *Ergänzung*) |
| Einsatz | Network Access (802.1X, VPN, WLAN) | Device Administration (CLI-Zugang, Command Authorization) |

### RADIUS-Ablauf
1. NAS → Server: **Access-Request** (Benutzername, verschleiertes Passwort, NAS-IP, NAS-Port).
2. Server prüft (Shared Secret muss passen) und Benutzer/Passwort.
3. **Access-Accept** mit AV-Paaren (z. B. IP-Adresse, ACL, VLAN, Privilege) oder **Access-Reject**. Optional **Access-Challenge** (z. B. Token-PIN).
4. Accounting getrennt: **Accounting-Request** (Start/Stop) / **Accounting-Response**.
→ Authentication und Authorization stecken in einem Request/Accept – deshalb keine echte Befehlsautorisierung.

### TACACS+-Ablauf
1. TCP-Verbindung zu Port 49.
2. NAS holt sich vom Server den Username-Prompt, sendet den Namen, Server fordert Passwort an (GETPASS), NAS sendet Passwort.
3. Server antwortet PASS (Accept) oder FAIL (Reject).
4. Danach getrennt: Authorization-Request/-Response (z. B. Shell + priv-lvl, einzelne Befehle) und Accounting-Request/-Response.

## 6. AAA aktivieren, lokaler Fallback (S. 261)
```
Switch(config)# username admin secret adminpass       <- zuerst! (Aussperr-Schutz)
Switch(config)# aaa new-model
aaa authentication login default local                 <- nur lokal
aaa authentication login default group radius local    <- RADIUS, Fallback lokal
```
- Erst nach `aaa new-model` sind die übrigen `aaa`-Befehle sichtbar.
- `aaa new-model` aktiviert sofort lokale Authentifizierung auf allen Lines außer `line con 0` (so Kurs und Cisco-Doku: ohne default-Liste nutzen vty-Lines die lokale Datenbank, die Konsole bleibt ohne Authentifizierung). Wer vorher keinen lokalen Benutzer angelegt hat, kann sich per SSH/Telnet nicht mehr anmelden.
- Lokalen Benutzer als Backup immer anlegen; `secret` statt `password`; Algorithmus scrypt oder sha256 statt MD5.
- `local` ans Ende der Methodenliste = lokale Datenbank nur, wenn alle Server nicht erreichbar sind.
- Ist eine default-Liste konfiguriert, gilt sie auch für die Konsole.

## 7. RADIUS für Console und vty (S. 262)
```
radius server RADSRV
 address ipv4 10.255.255.101 auth-port 1812 acct-port 1813
 key SecretRAD
aaa group server radius RADSRVGROUP
 server name RADSRV
aaa authentication login SRVAUTH group RADSRVGROUP local
line con 0
 login authentication SRVAUTH
line vty 0 4
 login authentication SRVAUTH
```
- Modi: `(config-radius-server)#`, `(config-sg-radius)#`.
- Key = Shared Secret, muss auf NAS und Server identisch sein.
- Ports optional; *(Ergänzung)* ohne Angabe nutzt IOS die Cisco-Defaults **1645/1646**, ISE und RFC verwenden 1812/1813 → bei Abweichung Ports explizit setzen.
- Benannte Liste SRVAUTH wirkt nur, wo sie zugewiesen ist.

## 8. TACACS+ für Console und vty (S. 263)
```
tacacs server TACSRV
 address ipv4 10.255.255.102
 key SecretTAC
 ! port 49 ist default, "port N" nur für abweichenden Port
aaa group server tacacs+ TACSRVGROUP
 server name TACSRV
aaa authentication login default group TACSRVGROUP local
```
- Modi: `(config-server-tacacs)#`, `(config-sg-tacacs+)#`.
- Die default-Liste gilt automatisch auf allen Lines, außer auf Lines mit explizit zugewiesener benannter Liste.
- Beispiel aus der Kursfrage: vty mit `login authentication default` (group radius local line) → Reihenfolge RADIUS → lokaler Benutzer → Line-Passwort; Console mit Liste `none` → kein Login.

## 9. Authorization und Accounting (S. 264)
```
aaa authorization exec MYTACAUTH group TACSRVGROUP local if-authenticated
aaa authorization commands 15 MYTACAUTH group TACSRVGROUP local
aaa authorization config-commands
line vty 0 4
 authorization exec MYTACAUTH
 authorization commands 15 MYTACAUTH

aaa accounting exec MYTACACC start-stop group TACSRVGROUP
aaa accounting commands 15 MYTACACC start-stop group TACSRVGROUP
line vty 0 4
 accounting exec MYTACACC
 accounting commands 15 MYTACACC
```
Syntax:
```
aaa authorization {commands LEVEL | config-commands | configuration | exec | network | reverse-access} {default | NAME} methods
aaa accounting {system | exec | commands LEVEL | connection | network} {default | NAME} {start-stop | stop-only | none} methods
line: authorization {commands LEVEL | exec | reverse-access} {default | NAME}
line: accounting {commands LEVEL | connection | exec} {default | NAME}
```
- `exec`: Darf der Benutzer überhaupt eine EXEC-Shell starten? Der Server kann ein Privilege Level mitgeben (TACACS+-AV `priv-lvl=15`) → Benutzer landet direkt im `#`-Modus.
- `commands LEVEL`: jeder Befehl des Levels wird vom Server genehmigt (nur TACACS+ kann einzelne Befehle autorisieren; RADIUS nur „alles oder nichts“ beim Login).
- `config-commands`: Befehle im Konfigurationsmodus werden ebenfalls autorisiert.
- `if-authenticated`: Autorisierung gilt als erteilt, wenn der Benutzer authentifiziert ist (letzte Rückfallmethode).
- Authorization wirkt **nicht auf der Konsole**, solange `aaa authorization console` fehlt (default) – Schutz, damit man fehlerhafte Autorisierung über die Konsole reparieren kann.
- Accounting: `system` (Reload u. ä.), `exec` (Sitzung mit Benutzer, Adresse, Dauer), `commands LEVEL` (jeder Befehl mit Benutzer). Record-Typen: `start-stop` (Start- und Stop-Record), `stop-only` (nur Stop), `none`.
- Accounting braucht einen zentralen Server (kein lokaler Speicher dafür).
- Ohne Line-Befehl gilt jeweils die default-Liste.

## 10. Discovery 27: Lokales und serverbasiertes AAA (S. 265)
Topologie: Rtr-1 (Gi0 10.10.10.5/24, Lo0), Ubuntu-PC 10.10.10.15, TACACS+-Server 10.10.10.41 im selben Segment.

### Task 1 – SSH
```
enable algorithm-type scrypt secret cisco
ip domain-name cisco.com                  <- Hostname + Domain = Schlüsselname
crypto key generate rsa                   <- interaktiv 1024 oder: ... modulus 1024 (besser 2048)
ip ssh version 2
username admin algorithm-type scrypt secret Cisco123
line vty 0 4
 transport input ssh
 login local
```
- Nach dem Erzeugen des RSA-Schlüssels ist SSH automatisch aktiv. „SSH 1.99“ = Version 2, die auch v1 annimmt. SSHv1 vermeiden (schwache Integrität).
- *(Ergänzung)* SSHv2 braucht einen Schlüssel mit mindestens 768 Bit (Cisco Secure Shell Config Guide); ab IOS XE 17.11.1 werden RSA-Schlüssel unter 2048 Bit für SSH standardmäßig abgelehnt (Field Notice FN72511). `crypto key zeroize rsa` löscht die Schlüssel und deaktiviert damit den SSH-Server; Hostname darf nicht der Default `Router` sein, sonst lehnt `crypto key generate rsa` ab.
- `show crypto key mypubkey rsa`: Schlüsselpaar `Rtr-1.cisco.com` (General Purpose) plus temporärer Schlüssel `Rtr-1.cisco.com.server`.
- `show ip ssh`:
```
SSH Enabled - version 2.0
Authentication methods:publickey,keyboard-interactive,password
Authentication timeout: 120 secs; Authentication retries: 3
```
- Beim ersten Verbinden zeigt der Client (PuTTY) den Fingerprint des Server-Schlüssels; nach Akzeptieren steht er im Known-Hosts-Speicher.
- `show ssh`: eine Connection mit IN- und OUT-Session, Version 2.0, aes256-ctr, hmac-sha2-256, Username admin.

### Task 2 – lokales AAA
```
username admin privilege 15 algorithm-type scrypt secret Cisco123
aaa new-model
aaa authentication login default local
aaa authorization exec default local     <- liefert priv-lvl 15 aus der lokalen DB
debug aaa authentication / debug aaa authorization
```
- Ergebnis: admin landet nach dem SSH-Login direkt im `#`-Prompt (`show privilege` → 15). Ohne `aaa authorization exec` würde das Privilege des lokalen Benutzers unter AAA nicht beim Login zugewiesen *(Ergänzung)*.
- Debug:
```
AAA/AUTHEN/LOGIN (...): Pick method list 'default'
%SEC_LOGIN-5-LOGIN_SUCCESS: Login Success [user: admin] [Source: 10.10.10.15] [localport: 22]
AAA/AUTHOR (...): Pick method list 'default'
AAA/AUTHOR/EXEC(...): processing AV priv-lvl 15
AAA/AUTHOR/EXEC(...): Authorization successful
```
- `show users` zeigt vty 0 mit User admin und Quelladresse.
- Lokales AAA ohne Accounting (kein Speicher), Accounting erst mit Server.

### Task 3 – serverbasiertes AAA (TACACS+)
```
tacacs server Ubuntu-Server
 address ipv4 10.10.10.41
 key Cisco123!
test aaa group tacacs+ admin Cisco123 new-code   -> "User successfully authenticated"
aaa authentication login default group tacacs+ local
aaa authorization exec default group tacacs+ local
aaa authorization commands 15 default group tacacs+ local
aaa authorization config-commands
aaa accounting exec default start-stop group tacacs+
aaa accounting commands 15 default stop-only group tacacs+
debug tacacs
```
- IOS XE warnt bei Klartext-Keys; starke Verschlüsselung (Typ 6, AES) mit `key config-key password-encrypt MASTERKEY` und `password encryption aes`. Der Master-Key steht nicht in der Konfiguration.
- `debug tacacs`-Ausgabe (gekürzt): `Using server 10.10.10.41` → `authen response status GET_PASSWORD` → `PASS` → Authorization mit `AV service shell`, `cmd*` → `Processed AV priv-lvl 15` → `PASS`; Befehlsautorisierung je Befehl `AUTHOR/START` → `PASS_ADD`; Accounting-Records mit `AV cmd show running-config <cr>`. Verbindungen zu `10.10.10.41/49` (TCP 49).
- Server-Log: `/var/log/tac_plus.acct` mit Router-IP, Client-IP, Benutzer, Befehl, Zeitstempel.

### Typische Troubleshooting-Punkte
- Ausgesperrt nach `aaa new-model` → vorher lokalen Benutzer anlegen, Konsole offen halten, Konfiguration erst nach Test speichern.
- Benutzer wird bei Serverfehler (Reject) nicht lokal angemeldet → korrektes Verhalten (FAIL ≠ ERROR).
- Benannte Liste ohne Wirkung → nicht unter der Line zugewiesen.
- Server immer „DEAD“/Timeouts → Erreichbarkeit, Ports (1645 vs. 1812), Quellinterface, Key.
- Command Authorization mit RADIUS funktioniert nicht → TACACS+ verwenden.
- Benutzer nach Login nur `>` → `aaa authorization exec` fehlt bzw. Server liefert kein priv-lvl.
- Nützliche Befehle: `show aaa servers`, `show aaa method-lists all` *(Ergänzung)*, `test aaa group ...`, `debug aaa authentication|authorization|accounting`, `debug tacacs`, `debug radius`.

## Fehler/Ungenauigkeiten im Kurs
1. **S. 260, RADIUS**: „Der Server vergleicht den im Request gesendeten Shared Secret“ – falsch. Das Shared Secret wird nie übertragen; es dient zum Verschleiern des Passworts (MD5-Verfahren) und zur Berechnung der Authenticator-Felder (RFC 2865, Abschn. 3 und 5.2). Ein falscher Key zeigt sich je nach Server als verworfenes Paket oder Access-Reject.
2. **S. 260**: „nur der Passwort-Teil des RADIUS-Packet-**Header**s wird verschlüsselt“ – das Passwort steht im Attribut User-Password, nicht im Header (RFC 2865, 5.2).
3. **S. 260**: TACACS+ „gesamtes Paket verschlüsselt“ – genauer: der Body; der 12-Byte-Header bleibt im Klartext (RFC 8907, Abschn. 4.5). TACACS+ ist inzwischen als RFC 8907 veröffentlicht, nicht mehr rein proprietär.
4. **S. 264**: `if-authenticated` „lässt den Benutzer sofort in den enable-Modus“ – falsch. `if-authenticated` genehmigt die Autorisierung nur, wenn der Benutzer authentifiziert ist; ein Privilege Level vergibt es nicht (Cisco Security Command Reference, `aaa authorization`).
5. **S. 264**: Im Accounting-Absatz steht „The MYTACAUTH method is applied …“ – gemeint ist die Accounting-Liste MYTACACC.
6. **S. 256**: Tabelle nennt `security password min-length`, der Befehl heißt `security passwords min-length` (wie im Fließtext).
7. **S. 265**: Hinweis zu den RSA-Schlüsseln nennt `Rtr-1.example.com`, die Ausgabe zeigt `Rtr-1.cisco.com`; der Schlüssel `.server` ist ein temporärer Schlüssel (SSHv1-Server-Key), SSHv2 nutzt das General-Purpose-Paar. Debug in Task 2 zeigt Quelle 10.10.10.50 statt der PC-Adresse 10.10.10.15; Topologie zeigt Lo0 10.10.11.1/24, Job Aid 10.10.1.1/24.
8. **S. 265, Task 2**: „Wenn eine Methode fehlschlägt, kann die nächste benutzt werden“ – ungenau; die nächste Methode greift nur bei ERROR (keine Antwort), nicht bei FAIL (S. 259 sagt es richtig).
9. **S. 258**: Im Studentenmaterial steht noch eine interne Redaktionsnotiz („Q2DEV … Response: RM“) zu einer negativ formulierten Frage.

## Bilder
- `bilder/24-aaa/01-passworttypen.svg` – Passwort-/Hash-Typen 0, 5, 7, 8, 9 mit Befehl und Sicherheitsbewertung.
- `bilder/24-aaa/02-aaa-drei-a.svg` – Die drei A (Wer bist du? / Was darfst du? / Was hast du getan?) und ihre Abhängigkeit.
- `bilder/24-aaa/03-nas-ablauf.svg` – Benutzer → NAS → AAA-Server → Zugriff auf geschützte Ressource (Schritte 1–5).
- `bilder/24-aaa/04-radius-tacacs.svg` – Vergleich RADIUS vs. TACACS+ (Ports, Trennung, Verschlüsselung, Einsatz).
- `bilder/24-aaa/05-paketfluss.svg` – Nachrichtenfolgen: RADIUS Access-Request/Accept vs. TACACS+ START/GETPASS/CONTINUE/PASS + Authorization.
- `bilder/24-aaa/06-method-list.svg` – Method List: ERROR → nächste Methode, FAIL → Abbruch.
- `bilder/24-aaa/07-aaa-bausteine.svg` – Konfigurationskette Server → Server-Gruppe → Method List → Line.
- `bilder/24-aaa/08-ssh-setup.svg` – SSH-Voraussetzungen Schritt für Schritt und Prüfbefehle.
