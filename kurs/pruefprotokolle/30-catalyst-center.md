# Kapitelprüfung 30-catalyst-center

Datum: 2026-11-24 · Checker-Lauf 1 (UNVOLLSTÄNDIG – Websuche nicht verfügbar)

## Wichtiger Hinweis
WebSearch und WebFetch lieferten bei jedem Aufruf "You've hit your 5-hour limit · resets 5:10pm (Europe/Berlin)". Die laut Anleitung verpflichtende Websuche konnte deshalb NICHT durchgeführt werden. Die Prüfung erfolgte offline (Fachwissen + Konsistenz mit Wissensdatei/Kurs). Ein zweiter Checker-Lauf mit Websuche ist nötig, v. a. für die Writer-markierten Fragen 024–027, 034, 042–046, 090, 093–095, 114, 115 sowie 012, 038, 061, 086.

## Umfang
- Fragen geprüft: 135 (alle einzeln, offline), verbleibend 135
- Lektion: 8 Seiten geprüft (inkl. Tabellenzellen)
- Wissensdatei: geprüft
- SVGs: 10 geprüft, alle wohlgeformt ([xml] OK), Inhalt konsistent mit Wissensdatei
- pruefen.ps1 -Kapitel 30-catalyst-center (ohne -Mischen): OK (single 95, zuordnung 10, multi 11, luecke 10, cli 9; Schwierigkeit 30/72/33)

## Korrekturen
| ID/Datei | Problem | Änderung |
|---|---|---|
| slg-cc-012 | Distraktor "Up to three ISE deployments" – Anzahl unterstützter ISE-Cluster ist release-abhängig (neuere Releases evtl. mehrere), Distraktor nicht sicher falsch; Erklärung "genau eine ISE" ebenso | Distraktor ersetzt durch "AAA servers can be defined only at the Global level of the hierarchy" (eindeutig falsch, Override pro Site); Erklärung angepasst |
| slg-cc-033 | CLI-Bausteine trennten Befehl, `<IQ>yes/no` und `<R>no` in separate Zeilen – im Template stehen IQ/R in derselben Zeile wie der Befehl (vgl. 034 und Cisco-Beispiel) | Befehl+IQ+R zu einem Baustein zusammengefasst, Ablenker mit `<R>yes` als ganze Zeile, Frage/Erklärung präzisiert (Änderung per Raw-Text-Replace, da Edit-Tool <-Escapes nicht matchte; Struktur unverändert, Parse geprüft) |
| slg-cc-045 | Erklärung behauptete ungeprüft, #set-Variablen erschienen nie im Form Editor | Satz entschärft |
| slg-cc-086 | Zwei-Hop-Grenze ist Kurs-/Standardwert; neuere Releases evtl. größere Discovery-Tiefe | Frage: "Using the default discovery scope of two hops"; Erklärung "standardmäßig" |
| lektionen/30 Seite 3 | "genau eine ISE-Deployment" | ersetzt durch "Cisco ISE dient als AAA- und Policy-Server" |
| wissen/30 | ISE-Anzahl, LAN-Automation-Reichweite, Template-Beispiel (Leerzeichen vor `<IQ>`) | als Kursstand markiert bzw. korrigiert |
| bilder/07-templates.svg | IQ/R-Teil auf eigener Zeile dargestellt (irreführend) | in eine Zeile gesetzt, Hinweis "(<IQ>/<R> in derselben Zeile)" |

## Entfernt
Keine.

## Offline als plausibel/korrekt bewertet (Web-Beleg ausstehend)
- 024/025: Option 43 `5A1N;B2;K4;I<ip>;J<port>`, K4=HTTP, K5=HTTPS (Cisco PnP Solution Guide)
- 026: `domain-name` im DHCP-Pool; 022: Fallback `pnpserver.<domain>`
- 027: `pnpa service discovery stop` (privileged EXEC)
- 034: verschachtelt #MODE_ENABLE / #INTERACTIVE (Cisco Template-Doku-Beispiel)
- 042–046: Velocity `$var`, `#set`, `#if(... == ...)`, `#foreach($x in [1..n])` – Range inklusiv (Velocity User Guide)
- 090: Northbound Intent API, Westbound Integration (ITSM/IPAM), Eastbound Events & Notifications, Southbound Multivendor SDK (DNA Center Platform Overview, developer.cisco.com)
- 093–095: `/dna/intent/api/v1/network-device`, Token via `POST /dna/system/api/v1/auth/token`, Gültigkeit 60 min, 401 nach Ablauf, 429 bei Rate-Limit, 202 + taskId → `GET /dna/intent/api/v1/task/{taskId}`
- 114/115: Health 1–3 Poor/rot, 4–7 Fair/orange, 8–10 Good/grün; Geräte-Score = niedrigster Subscore
- Topic-Zuordnung: 4.5 (Workflows), 6.4 (APIs/Adapter), 1.3.a (SD-Access-Policies, LAN Automation) – passend

## Unsichere Punkte (für Lauf 2 mit Websuche)
- 038 Datentypen Form Editor (String/Integer/IP/MAC; kein Boolean/Date?) – release-abhängig
- 061 Resync max. 40 Geräte, 062 Polling-Default 25 min (Kursangaben)
- 071 KGV-Update alle 7 Tage, 078 max. 3 Image Distribution Server
- 106 On-prem-only AI-Analytics nur "excessive onboarding time"
- 116/117 NAT/Latenz 100/200 ms
- 122 DN3-Skalierungswerte (Data Sheet)
- 012 Anzahl ISE-Cluster (Wissensdatei-Hinweis)

## Web-Nachprüfung (Checker-Lauf 2, 2026-11-24)
WebSearch/WebFetch funktionierten. Geprüft: alle Pflicht-IDs plus Stichprobe (>30 weitere). pruefen.ps1 -Kapitel 30-catalyst-center (ohne -Mischen): OK, 133 Fragen (single 93, zuordnung 10, multi 11, luecke 10, cli 9; Schwierigkeit 30/71/32).

### Belegt (ohne Änderung)
| IDs | Beleg | Quelle |
|---|---|---|
| 022, 023, 024, 025, 082 | Option 43 `5A1N;B2;K4;I…;J…`, B1/B2/B3, K4=HTTP/K5=HTTPS, I=IP/FQDN, J=Port; DNS-Fallback `pnpserver.<domain>` aus per DHCP gelernter Domain; Reihenfolge DHCP → DNS → PnP Connect (devicehelper.cisco.com); Trustpool-Import vor HTTPS | https://www.cisco.com/c/en/us/td/docs/Sanity/arudupa/PnP_Guide.html ; https://www.cisco.com/c/en/us/support/docs/cloud-systems-management/catalyst-center/225887-understand-switch-onboarding-through.html |
| 026 | `domain-name` ist der DHCP-Pool-Befehl (IOS); Agent bildet pnpserver.<domain> | PnP_Guide (s. o.) |
| 027 | `pnpa service discovery stop` im privilegierten EXEC | https://www.cisco.com/c/en/us/support/docs/routers/xe-sd-wan-routers/218137-configure-basic-parameters-to-form-contr.html ; https://www.cisco.com/c/en/us/td/docs/routers/sdwan/configuration/sdwan-xe-gs-book/hardware-and-software-installation.html |
| 032, 034, 035, 036, 039, 040, 041, 131, 030 | `#MODE_ENABLE`/`#MODE_END_ENABLE`, `#INTERACTIVE`/`#ENDS_INTERACTIVE`, `Befehl<IQ>Frage<R>Antwort` in einer Zeile (Großschreibung), `<MLTCMD>`, Default global config, nur committete Templates, Composite = committete Templates mit Reihenfolge, Blocklist-Warnung, Templates dürfen Network-Intent nicht überschreiben, Day-0 in „Onboarding Configuration“ ohne Sonderkeywords | https://www.cisco.com/c/en/us/td/docs/cloud-systems-management/network-automation-and-management/catalyst-center/2-3-7/user_guide/b_cisco_catalyst_center_user_guide_237/b_cisco_dna_center_ug_2_3_7_chapter_01000.html ; https://blogs.cisco.com/developer/velocity-templates-in-dna-center-3 |
| 038 | Variablentypen String, Integer, IP Address, MAC Address (kein Boolean/Date) | User Guide 2.3.7 Templates (s. o.); https://netascode.cisco.com/docs/data_models/catalyst_center/templates/template/ |
| 042–046 | Velocity `$var`/`${var}`, `#set( $a = … )`, `#if( $foo == "bar" )`, `#foreach( $i in [1..3] )`; Range inklusiv (`[1..5]` → 1 2 3 4 5); Jinja2 als zweite Sprache | https://velocity.apache.org/engine/2.3/vtl-reference.html ; https://velocity.apache.org/engine/2.3/user-guide.html ; https://www.cisco.com/c/en/us/support/docs/cloud-systems-management/catalyst-center/225714-understand-templates-on-catalyst-center.html |
| 090, 091, 092 | Northbound Intent API, Westbound Integration (ITSM/IT4IT), Eastbound Events & Notifications (Webhooks), Southbound Multivendor SDK | https://developer.cisco.com/docs/dna-center/ (Platform Overview) ; https://developer.cisco.com/docs/dna-center/2-3-7-9/ |
| 093, 096 | `GET /dna/intent/api/v1/network-device`, REST/JSON über HTTPS | https://developer.cisco.com/docs/catalyst-center/ |
| 094 | Token via `POST /dna/system/api/v1/auth/token`, Lebensdauer 60 min, danach 401, Header X-Auth-Token; 429 bei Rate-Limit (Community-Belege) | https://developer.cisco.com/docs/catalyst-center/authentication/ ; https://community.cisco.com/t5/controllers/rate-limit-exceeded-dna-center-api/m-p/5021519 |
| 095 | 202 Accepted mit taskId + url `dna/intent/api/v1/task/{taskId}`, Ende über endTime/isError | https://developer.cisco.com/docs/catalyst-center/asynchronous-api/ |
| 114, 115 | Poor 1–3, Fair 4–7, Good 8–10; Geräte-Health = niedrigster KPI-Subscore (Switch: CPU, Memory, Link Errors …) | https://www.cisco.com/c/en/us/td/docs/cloud-systems-management/network-automation-and-management/catalyst-center-assurance/2-3-7/b_cisco_catalyst_assurance_2_3_7_ug/b_cisco_catalyst_assurance_2_3_6_ug_chapter_0110.html |
| 048, 049, 050 | Täglicher Job 23:00 Uhr für Geräte ohne Compliance-Check in 7 Tagen; Compliance-Typen inkl. Startup vs Running, Image, PSIRT, Network Profile, EoX | https://www.cisco.com/c/en/us/td/docs/cloud-systems-management/network-automation-and-management/catalyst-center/2-3-7/user_guide/b_cisco_catalyst_center_user_guide_237/m-compliance-audit-for-network-devices.html |
| 052–058, 014, 118, 119, 120, 124 | CDP/LLDP-Level Default 16 (1–16); IP-Range bis 4096 Geräte; Mgmt-IP: höchste Loopback, sonst höchste Ethernet-IP ohne Subinterfaces, dann Serial; mind. 1 CLI + 1 SNMP-Credential; Level 15 oder Enable-Passwort; SNMPv2c-Read genügt; NFVIS braucht HTTP(S); Credential-Sets werden durchprobiert; WLC über Management-IP, nicht Service Port | https://www.cisco.com/c/en/us/td/docs/cloud-systems-management/network-automation-and-management/catalyst-center/2-3-7/user_guide/b_cisco_catalyst_center_user_guide_237/b_cisco_dna_center_ug_2_3_7_chapter_010.html |
| 064, 065, 135, 071, 078, 108, 111, 107 | Device Controllability Default an, Site-Wechsel ersetzt SNMP/Syslog/NetFlow, Entfernen aus Site lässt Settings stehen, Löschen optional mit Clean-up, Global: keine Änderung; KGV-Auto-Download alle 7 Tage; bis zu drei externe Image Distribution Server; Advantage-Lizenz für AI Network Analytics; MRE-Knowledge-Base täglich automatisch (Cloud nötig); ausgehend TCP 443 zu *.kairos.ciscolabs.com | https://www.cisco.com/c/en/us/td/docs/cloud-systems-management/network-automation-and-management/catalyst-center/2-3-7/admin_guide/b_cisco_catalyst_center_admin_guide_237/b_cisco_dna_center_admin_guide_2_3_7_chapter_010.html |
| 069, 072, 073, 074, 076, 080 | Golden Image je Familie/Rolle; Prechecks u. a. Flash-Check; Post-Checks; Distribution kopiert, Activation mit Reboot; Golden SMU nur mit Golden Base Image; Offline-Import → Gerätefamilie manuell zuordnen | https://www.cisco.com/c/en/us/td/docs/cloud-systems-management/network-automation-and-management/catalyst-center/2-3-7/user_guide/b_cisco_catalyst_center_user_guide_237/b_cisco_dna_center_ug_2_3_7_chapter_0100.html |
| 117 | 100 ms empfohlen, > 200 ms RTT nicht unterstützt | https://community.cisco.com/t5/cisco-catalyst-center/network-requirements-for-dna-center/m-p/4275444 ; https://www.ciscolive.com/c/dam/r/ciscolive/global-event/docs/2025/pdf/BRKOPS-2698.pdf |
| 121 | Hardware-Appliance, virtuell auf ESXi und AWS | https://www.cisco.com/c/en/us/products/collateral/cloud-systems-management/dna-center/nb-06-dna-center-data-sheet-cte-en.html |

### Korrigiert
| ID | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-cc-012 | „Client/Endpoint nur RADIUS“ nicht belegbar (Datenmodell erlaubt RADIUS/TACACS für beide Klassen) | Optionen 3/4 ersetzt: Distraktor „AAA settings reach devices only through Day-0 templates“, richtig „Separate AAA servers can be set for network devices and for clients“; Erklärung neu | https://netascode.cisco.com/docs/data_models/catalyst_center/network_settings/aaa_servers/ ; https://community.cisco.com/t5/cisco-catalyst-center/can-t-see-where-the-client-endpoint-aaa-servers-are-configured/m-p/4918949 |
| slg-cc-033 | Distraktor `#END_INTERACTIVE` wird in Cisco-Blog/Webcast-Beispielen tatsächlich verwendet → nicht eindeutig falsch | ersetzt durch `#INTERACTIVE_END` (offizielle Schreibweise `#ENDS_INTERACTIVE` bleibt Lösung) | User Guide 2.3.7 Templates; blogs.cisco.com/developer/velocity-templates-in-dna-center-3 |
| slg-cc-034 | Distraktor `#END_MODE_ENABLE` erscheint im Cisco-Blogbeispiel → nicht eindeutig falsch | ersetzt durch `#ENABLE_MODE_END` | wie oben |
| slg-cc-037 | „Not a Variable“ heißt in 2.3.7 Variable-Schalter | Erklärung ergänzt | User Guide 2.3.7 Templates |
| slg-cc-039 | Distraktor nannte „25-minute inventory resync“ (veralteter Default) | „next periodic inventory resync“ | User Guide 2.3.7 Inventory |
| slg-cc-061 | Resync-Limit „max. 40 Geräte“ nicht belegbar | umformuliert: manueller Resync startet sofort, unabhängig vom periodischen Intervall | https://www.cisco.com/c/en/us/td/docs/cloud-systems-management/network-automation-and-management/catalyst-center/2-3-7/user_guide/b_cisco_catalyst_center_user_guide_237/b_cisco_dna_center_ug_2_3_7_chapter_011.html |
| slg-cc-062 | Default 25 min veraltet; User Guide 2.3.7: „default interval is every 24 hours“ | Frage auf Release 2.3.7 bezogen, richtige Option „24 hours“ (Index 2), 25-min-Option entfernt | wie oben; https://developer.cisco.com/docs/dna-center/update-global-resync-interval |
| slg-cc-068 | Status heißt in 2.3.7 „Outdated“ | Frage/Erklärung: „flagged as outdated ('Needs Update' in older releases)“ | User Guide 2.3.7 SWIM |
| slg-cc-075 | „zwei Reloads“ bei ROMMON nicht belegbar | umformuliert: Voraussetzung ist cisco.com-Konfiguration (ROMMON-Datei wird automatisch geladen); richtig Index 3 | User Guide 2.3.7 SWIM |
| slg-cc-086 | Default-Tiefe „zwei Hops“ nicht belegbar; Discovery Level einstellbar (1–5, ältere Releases bis 3) | Frage nennt nun „discovery depth (level) of 2“; Erklärung neu | https://developer.cisco.com/docs/dna-center/lan-automation-start-v2 ; https://netascode.cisco.com/docs/data_models/catalyst_center/lan_automation/lan_automation/ |
| slg-cc-122 | Mit 3000 Netzwerkgeräten + 4500 APs passt laut Data Sheet 2.3.7 keine APL-L-Konfiguration (non-fabric 2000/6000, fabric 4000/4000) | Szenario: ohne Fabric, 1800 Netzwerkgeräte + 5500 APs → APL-L; Erklärung mit Data-Sheet-Werten | https://www.cisco.com/c/en/us/products/collateral/cloud-systems-management/dna-center/nb-06-dna-center-data-sheet-cte-en.html |
| wissen/30 | 25 min, zwei Hops, zwei Reboots, NAT, on-prem-only, Client nur RADIUS | als Kursangabe/nicht web-belegt markiert bzw. mit 2.3.7-Wert ergänzt | s. o. |
| lektionen/30 | Seiten mit „nur RADIUS“, „25 Minuten/40 Geräte“, „nicht über NAT“, „zwei Hops“, „zwei Reboots“ | durch belegte Aussagen ersetzt (JSON-Parse geprüft) | s. o. |

### Entfernt
| ID | Grund |
|---|---|
| slg-cc-106 | „On-prem only erkennt nur excessive onboarding time“ – keine Web-Quelle gefunden |
| slg-cc-116 | „Assurance unterstützt keine Verwaltung über NAT“ – keine offizielle Quelle gefunden (NAT nur als Troubleshooting-Ursache erwähnt) |

### Weiterhin unsicher (behalten)
- 059/060 Last-Sync-Status-Werte (Wrong Credentials, Partial Collection Failure): ältere Releases; 2.3.7 zeigt Manageability/Reachability-Status.
- 109 Liste der ohne Cloud betroffenen Features: plausibel (Heatmap/Comparative Analytics sind Cloud-AI-Funktionen laut Cisco Live), keine explizite Liste gefunden.
- 079 Label „Suggested“: im 2.3.7-SWIM-Kapitel nicht definiert.
- 078: API-Doku nennt „up to two remote servers“ (lokal zusätzlich), User/Admin Guide „up to three external“ – Frage folgt dem Guide.
