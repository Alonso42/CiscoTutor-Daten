# Kapitelprüfung 33-apis

Datum: 2026-11-24 · Checker
Geprüft: 108 Fragen (encor-1.4.10/fragen/33-apis.json), Lektion (8 Seiten, alle Tabellenzellen), Wissensdatei, 8 SVGs.
Ergebnis pruefen.ps1 (ohne -Mischen): OK – 108 Fragen (single 71, multi 10, zuordnung 9, luecke 8, cli 10; Schwierigkeit 27/55/26).

## Vorgehen
- Jede Frage einzeln geprüft (markierte Antwort, Distraktoren, Erklärung, Eindeutigkeit, Topic).
- Python-Snippets lokal ausgeführt (Python 3.15, Mock-Daten): 023 → ['edge-2'], 025 → Offsets 1/501/1001, 026 → TypeError (string indices must be integers), 102 → json.loads(...)['fileId'] = '9f2c', 027 → KeyError, 028 → ['BR2-Edge'], 093 → len(d['data'])=3 / len(d)=2, 106 → Liste der host-name-Werte, 039 → json.loads „Extra data“ (→ 400), 047 → base64("admin:C1sco12345") = YWRtaW46QzFzY28xMjM0NQ==, 090 → 3 Requests / 5 Datensätze. Alle stimmen mit den markierten Antworten überein.
- Das Paket `requests` ist lokal NICHT installiert (kein Download ohne Freigabe) → requests-Verhalten (031, 032, 046, 078, 103, 104, 107, 108) gegen die offizielle API-Doku belegt statt ausgeführt.

## Belege (vom Writer markierte Punkte)
- 019/048/098/097/095 X-Auth-Token, POST /dna/system/api/v1/auth/token mit Basic Auth: https://developer.cisco.com/docs/catalyst-center/authentication-api ; https://developer.cisco.com/docs/dna-center/authentication-and-authorization
- 025 offset 1-basiert, limit max. 500: https://developer.cisco.com/docs/catalyst-center/get-device-list/ ; https://developer.cisco.com/docs/dna-center/2-3-5/get-device-list
- 026/037/102/020 Task-Felder isError, failureReason, progress, endTime (endTime ⇒ abgeschlossen): https://developer.cisco.com/docs/catalyst-center/asynchronous-api/ ; Ansible task_info https://cisco-en-programmability.github.io/catalystcenter-ansible/v2.2.1/plugins/task_info_module.html
- 031/107 data=dict → Form-Encoding, json= → JSON-Body; 032 raise_for_status → HTTPError; 108 ok = status_code < 400; 046 verify=Pfad zum CA-Bundle, verify=False → MitM-Risiko; 078 Session = Cookie-Persistenz: https://requests.readthedocs.io/en/latest/api/
- 074/075/103 j_security_check x-www-form-urlencoded, j_username/j_password; 076 falsches Login → HTML-Loginseite im Body; 104 /dataservice/client/token liefert XSRF-Token; 077 POST ohne passendes X-XSRF-TOKEN → 403, Pflicht seit 19.2: https://developer.cisco.com/docs/sdwan/authentication/ ; https://www.cisco.com/c/en/us/support/docs/software-resources/220229-configure-postman-to-execute-apis-on-vma.html ; Community-Thread „vManage API GET works POST fails“ (403 „Token provided via HTTP Header does not match“)
- 048 Meraki v1: Authorization: Bearer <API-Key>: https://developer.cisco.com/meraki/api-v1/authorization/
- 044/045 ASA REST Privilege 3/5/15: https://www.cisco.com/c/en/us/td/docs/security/asa/api/asa_rest_api.html
- 014–017, 033, 036 Statuscodes 401/403/406/408/409/415/501/503/504 (RFC 9110 Abschn. 15): https://www.rfc-editor.org/rfc/rfc9110.html
- 030/038/086/090: Logik/Interpretation geprüft (200 + leere Liste = kein Treffer; 4xx-Body-Fehlermeldung → Request korrigieren; Schleife bis hasMoreData false).

## Korrekturen
| ID / Datei | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-ap-037 | „Felder einer Task-Antwort“: taskId steht in der 202-Antwort, nicht im Task-Objekt (dort heißt es id) | Fragetext: „Feld eines asynchronen Catalyst-Center-Auftrags (202-Antwort bzw. Task-API)“ | developer.cisco.com/docs/catalyst-center/asynchronous-api/ |
| slg-ap-086 | Wert "deviceState": "READY" nicht sauber belegbar, für die Antwort unnötig | deviceState aus dem Fragetext entfernt, nur validity invalid | – |
| wissen/33-apis.md | „/j_security_check liefert bei falschem Login 200“ – DevNet-Doku nennt nur HTML-Body, keinen Code | umformuliert: HTML-Loginseite (<html> prüfen), in der Praxis meist 200 | developer.cisco.com/docs/sdwan/authentication/ |

## Entfernt
keine

## Bilder
8 SVGs: alle wohlgeformt ([xml] OK), UTF-8 ohne BOM, <title> erstes Kind. Inhaltlich korrekt, keine Korrektur nötig.

## Unsichere Punkte
- 076 / SVG 07 / Lektion S. 9: Statuscode 200 bei falschem SD-WAN-Login ist praxisüblich (Community-Codebeispiele prüfen erst 200, dann <html>), aber nicht explizit in Cisco-Doku.
- 033: 409 als „später ohne Änderung wiederholbar“ folgt der Kursaussage; RFC 9110 sagt, der Client könne den Konflikt ggf. auflösen und erneut senden.
- 030: 200 mit leerer response-Liste bei nicht passendem hostname-Filter ist das übliche Verhalten der Intent API, nicht als eigener Satz in der Doku gefunden.
- requests-Verhalten nicht ausgeführt (Paket fehlt), nur per Doku belegt.
