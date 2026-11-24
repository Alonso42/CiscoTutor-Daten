# Prüft neue Fragen-/Lektionsdateien gegen das CiscoTutor-Format.
# Aufruf:  .\tools\pruefen.ps1 -Kapitel 02-architecture [-Mischen]
param(
  [Parameter(Mandatory)] [string] $Kapitel,
  [switch] $Mischen
)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$utf8 = New-Object Text.UTF8Encoding $false
$fp = Join-Path $root "encor-1.4.10\fragen\$Kapitel.json"
$lp = Join-Path $root "encor-1.4.10\lektionen\$Kapitel.json"
$err = New-Object System.Collections.Generic.List[string]

$alt = Get-Content -Raw -Encoding utf8 (Join-Path $root 'repo-src\daten_fragen.json') | ConvertFrom-Json
$andere = Get-ChildItem (Join-Path $root 'encor-1.4.10\fragen') -Filter *.json | Where-Object { $_.FullName -ne $fp } |
  ForEach-Object { Get-Content -Raw -Encoding utf8 $_.FullName | ConvertFrom-Json }
$bekannt = @($alt.id) + @($andere | ForEach-Object { $_.id })

$tmp = Get-Content -Raw -Encoding utf8 $fp | ConvertFrom-Json; $q = @($tmp | ForEach-Object { $_ })
if ($Mischen) {
  $rnd = New-Object System.Random
  foreach ($x in $q) {
    if ($x.typ -in 'single','luecke','multi') {
      $n = $x.optionen.Count; $perm = @(0..($n-1) | Sort-Object { $rnd.Next() })
      $opts = @($perm | ForEach-Object { $x.optionen[$_] })
      if ($x.typ -eq 'multi') { $x.richtig = @(0..($n-1) | Where-Object { @($x.richtig) -contains $perm[$_] }) }
      else { $x.richtig = [array]::IndexOf($perm, [int]$x.richtig) }
      $x.optionen = $opts
    }
  }
  [IO.File]::WriteAllText($fp, (ConvertTo-Json -InputObject $q -Depth 8), $utf8)
}

foreach ($x in $q) {
  if ($bekannt -contains $x.id) { $err.Add("ID schon vergeben: $($x.id)") }
  if (-not $x.topic -or -not $x.frage -or -not $x.erklaerung) { $err.Add("Pflichtfeld fehlt: $($x.id)") }
  if ($x.schwierigkeit -notin 1,2,3) { $err.Add("Schwierigkeit: $($x.id)") }
  switch ($x.typ) {
    { $_ -in 'single','luecke' } { if ($x.optionen.Count -ne 4) { $err.Add("single/luecke braucht 4 Optionen: $($x.id)") }; if ([int]$x.richtig -lt 0 -or [int]$x.richtig -ge $x.optionen.Count) { $err.Add("richtig außerhalb: $($x.id)") } }
    'multi' { if ($x.optionen.Count -lt 4 -or $x.optionen.Count -gt 5) { $err.Add("multi braucht 4-5 Optionen: $($x.id)") }; if (@($x.richtig).Count -lt 2) { $err.Add("multi mit <2 richtigen: $($x.id)") }; foreach ($r in $x.richtig) { if ($r -ge $x.optionen.Count) { $err.Add("richtig außerhalb: $($x.id)") } } }
    'cli' { foreach ($w in $x.loesung) { if ($x.bausteine -notcontains $w) { $err.Add("CLI-Baustein fehlt: $($x.id) '$w'") } } }
    'zuordnung' { if ($x.paare.Count -lt 2) { $err.Add("zu wenige Paare: $($x.id)") }
                  $rechts = @(foreach ($pp in $x.paare) { $pp[1] }); if (($rechts | Sort-Object -Unique).Count -ne $rechts.Count) { $err.Add("doppelte rechte Seite: $($x.id)") } }
    default { $err.Add("unbekannter Typ: $($x.id) $($x.typ)") }
  }
}
($q.id | Group-Object | Where-Object Count -gt 1) | ForEach-Object { $err.Add("doppelte ID in Datei: $($_.Name)") }

if (Test-Path $lp) {
  $raw = Get-Content -Raw -Encoding utf8 $lp
  if ($raw.TrimStart()[0] -ne '[') { $err.Add('Lektionsdatei ist kein Array') }
  $arts = 'cloud','pc','router','server','switch'
  $ltmp = $raw | ConvertFrom-Json; foreach ($l in @($ltmp | ForEach-Object { $_ })) {
    foreach ($s in $l.seiten) {
      if (-not $s.text) { $err.Add("Lektionsseite ohne Text: $($l.id)") }
      if ($s.diagramm) {
        if ($s.diagramm.typ -notin 'topologie','tabelle','ablauf') { $err.Add("Diagrammtyp: $($s.diagramm.typ)") }
        foreach ($k in $s.diagramm.knoten) { if ($k.art -notin $arts) { $err.Add("Knotenart: $($k.art)") } }
        $ids = @($s.diagramm.knoten.id)
        foreach ($e in @($s.diagramm.kanten) + @($s.diagramm.schritte)) { if ($e -and ($ids -notcontains $e.von -or $ids -notcontains $e.nach)) { $err.Add("Kante auf unbekannten Knoten: $($e.von)->$($e.nach)") } }
      }
    }
  }
}


# Warnung: richtige Option auffaellig laenger als alle Distraktoren (verraet die Loesung)
$lang = @()
foreach ($x in $q) {
  if ($x.typ -eq 'single') {
    $r = [int]$x.richtig; $lr = $x.optionen[$r].Length
    $andere = @(0..($x.optionen.Count-1) | Where-Object { $_ -ne $r } | ForEach-Object { $x.optionen[$_].Length })
    $max = ($andere | Measure-Object -Maximum).Maximum
    if ($max -gt 0 -and $lr -gt 1.3 * $max -and $lr - $max -gt 12) { $lang += $x.id }
  }
}
if ($lang.Count) { $err.Add("Laengen-Bias (richtige Option >30% laenger als jeder Distraktor): " + ($lang -join ', ')) }

# Warnung: Erklaerung verweist auf Optionsposition (stimmt nach dem Mischen nicht mehr)
$pos = @($q | Where-Object { $_.erklaerung -match '(?i)\b(erste|zweite|dritte|vierte|letzte|obere|untere)n? (Option|Antwort)|\bOption [A-D1-4]\b|\b(first|second|third|fourth|last) option\b' } | ForEach-Object { $_.id })
if ($pos.Count) { $err.Add("Erklaerung verweist auf Optionsposition: " + ($pos -join ', ')) }
"Fragen: $($q.Count)  |  " + (($q | Group-Object typ | ForEach-Object { "$($_.Name)=$($_.Count)" }) -join ' ') + "  |  Schwierigkeit " + (($q | Group-Object schwierigkeit | Sort-Object Name | ForEach-Object { "$($_.Name):$($_.Count)" }) -join ' ')
if ($err.Count) { "FEHLER:"; $err } else { "OK – keine Formatfehler" }
