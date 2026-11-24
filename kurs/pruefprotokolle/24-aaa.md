# Kapitelprüfung 24-aaa (Implementing Secure Access Control)

Datum: 2026-11-24 · Checker
Geprüft: 134 Fragen (fragen/24-aaa.json; die ID slg-aa-082 fehlt schon beim Writer), Lektion (8 Seiten, alle Tabellenzellen), Wissensdatei, 8 SVGs (alle mit [xml] wohlgeformt).
pruefen.ps1 -Kapitel 24-aaa (ohne -Mischen): OK. Verteilung: single 83, multi 15, cli 14, zuordnung 12, luecke 10; Schwierigkeit 1:33 / 2:67 / 3:34.

## Korrekturen
| ID/Datei | Problem | Änderung | Quelle |
|---|---|---|---|
| slg-aa-077 | Distraktor „Accounting can be performed without any authentication“ ist laut Cisco richtig („You can use accounting alone…“), die Frage war also mehrdeutig | Distraktor geändert in „Authorization can be performed without any authentication“; Erklärung angepasst | https://www.cisco.com/en/US/docs/security/asa/asa91/configuration/general/aaa_overview.html |
| slg-aa-129 | Erklärung sagte „360 ist das Minimum von crypto key generate rsa“; das ist nicht belegt, und auf aktuellem IOS XE gilt es nicht mehr | Satz entfernt; ergänzt: Minimum 768 Bit laut SSH-Guide, ab IOS XE 17.11.1 werden <2048 Bit abgelehnt | SSH Guide: https://www.cisco.com/en/US/docs/ios-xml/ios/sec_usr_ssh/configuration/15-e/sec-secure-shell-v2.html ; FN72511: https://www.cisco.com/c/en/us/support/docs/field-notices/725/fn72511.html |
| slg-aa-022 | Hinweis auf den aktuellen Stand fehlte | Erklärung um FN72511 (17.11.1: 2048 Bit) ergänzt | wie oben |
| slg-aa-025 | „Bestehende Sitzungen laufen weiter“ ist nicht belegt | Satz entfernt; Erklärung stützt sich jetzt auf das Cisco-Zitat „When you delete the RSA key pair, you automatically disable the SSH server“ | SSH Guide (s. o.) |
| slg-aa-045 | In der Liste der Header-Felder fehlten die Flags | Erklärung ergänzt: 12-Byte-Header mit Flags, RFC 8907 | RFC 8907 §4.1 |
| Wissen §2 | „Authorization und Accounting setzen eine Authentifizierung voraus“ | korrigiert: nur Authorization setzt sie voraus, Accounting geht auch allein | ASA-AAA-Overview (s. o.) |
| Wissen §10 | 2048-Bit-Regel ab 17.11.1 und Zeroize-Wirkung fehlten | ergänzt | FN72511, SSH Guide |
| Lektion S. 4, S. 3, S. 9 | gleicher Accounting-Fehler; 17.11.1-Hinweis; „alle Befehle“ → „alle Level-15-Befehle“ (bei commands 15) | Texte korrigiert | wie oben |
| Bild 02-aaa-drei-a.svg | Merksatz „Authorization und Accounting setzen … voraus“ | geändert in „Authorization setzt sie immer voraus; Accounting geht auch allein.“ | wie oben |
| Bild 08-ssh-setup.svg | nur „mind. 768 Bit“ | „SSHv2: mind. 768 Bit (ab XE 17.11.1: 2048)“ | FN72511 |

## Entfernt
Keine.

## Gezielt belegte Punkte (Writer-Markierungen)
- 002: enable secret hat Vorrang vor enable password, Cisco-Standardverhalten. OK.
- 008/126: exec-timeout 0 0 schaltet den Timeout ab; der Default ist 10 Minuten. OK.
- 010/011: Die Login-Enhancements-Doku sagt, dass mit `login block-for` allein automatisch 1 s Delay gilt und dass `login block-for` vor `login delay` konfiguriert sein muss. OK. (https://supportforums.cisco.com/legacyfs/online/legacy/9/5/4/12459-CISCO%20IOS%20Login%20Enhancements%20(Login%20Block).pdf, CIS-Benchmark)
- 013: security passwords min-length gilt für Benutzer-, enable- und Line-Passwörter; kürzere Passwörter werden abgelehnt. OK.
- 015/052/111: Ohne AAA übernimmt login local das Level aus dem username-Eintrag. Mit aaa new-model ohne `aaa authorization exec` landet der Benutzer auf Level 1. Bekanntes Verhalten, im Discovery-Lab gezeigt. OK.
- 017: enable secret level 7 / enable 7. OK.
- 022/129: Laut SSH Config Guide gilt „For SSH Version 2, the modulus size must be at least 768 bits“. OK (siehe Korrektur).
- 025/133: Laut SSH Config Guide wird der SSH-Server automatisch deaktiviert, wenn die Schlüssel gelöscht werden. OK.
- 045/131: Der TACACS+-Header (RFC 8907) besteht aus version 1 + type 1 + seq_no 1 + flags 1 + session_id 4 + length 4 = 12 Byte. Verschleiert wird nur der Body. OK.
- 046: 802.1X/EAP läuft über RADIUS. OK.
- 048/104: Die Cisco IOS Security Command Reference sagt: „If auth-port and acct-port are not specified, the default value of auth-port is 1645 and … acct-port is 1646“. In aktuellen IOS-XE-Beispielen werden Ports meist explizit gesetzt. Community-Threads („port 1812 config but port 1645 used“) bestätigen die IOS-Defaults 1645/1646. Behalten, aber als leicht unsicher markiert (siehe unten).
- 050/091: Das Shared Secret wird nie übertragen (RFC 2865 §3, §5.2). OK.
- 033/040/087/095 (Fallback-Regel): Die nächste Methode bzw. der nächste Server wird nur bei ERROR versucht, FAIL/Reject beendet die Prüfung (Cisco Configuring Authentication). OK.
- 038/090/039 (aaa new-model): Cisco Tech Note: „The aaa new-model command immediately applies local authentication to all lines and interfaces (except console line con 0)“. OK. (https://www.cisco.com/c/en/us/support/docs/security-vpn/terminal-access-controller-access-control-system-tacacs-/200606-aaa-authentication-login-default-local.html)
- 054/057/130: Ohne `aaa authorization console` wird die Konsole nicht autorisiert. Ohne Rückfallmethode führt ein Serverausfall bei commands 15 dazu, dass die Befehle auf vty abgelehnt werden. OK.
- 067: Die Authentifizierung fällt auf local zurück, die exec-Autorisierung ohne Fallback scheitert („Authorization failed“). OK.
- 068: reload in 10 / reload cancel. OK.
- 070: cisco-av-pair shell:priv-lvl=15 im Access-Accept, zusätzlich muss aaa authorization exec … group radius konfiguriert sein. OK.
- 084: no service password-encryption entschlüsselt nichts. OK.
- 097/124: Level 0 umfasst disable, enable, exit, help, logout; Level 1 und 15 sind Standard, 2–14 frei belegbar. OK.
- 135/035: local-case prüft den Benutzernamen case-sensitiv. OK.

## Unsichere Punkte
- 048/104/Wissen §7: Der Default 1645/1646 für `radius server`/`address ipv4` ohne Portangabe ist nur aus der IOS Command Reference (radius-server host) und aus Community-Berichten belegt. Eine aktuelle IOS-XE-17-Seite mit ausdrücklichem Default habe ich nicht gefunden. Nach allgemeinem Kenntnisstand gilt der Default weiterhin, daher habe ich die Fragen behalten.
- 059: Die Bezeichnung „GET_PASSWORD (8)“ stammt aus der IOS-Debug-Ausgabe (Kurs-Lab); RFC 8907 nennt den Status GETPASS (0x05). Die Frage bezieht sich auf die Debug-Ausgabe und ist korrekt.
- 129: Die Distraktoren 360/512/4096 sind eindeutig falsch. Auf IOS XE ab 17.11.1 gilt praktisch 2048, das steht in der Erklärung.
