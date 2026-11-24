# Kopiert Wissensbasis, Bilder, Fragen, Lektionen, Werkzeuge und Prüfprotokolle
# in den Klon von CiscoTutor-Daten (Ordner kurs/) und committet lokal. Pusht NICHT.
# Aufruf:  .\tools\git-sync.ps1 -Repo <pfad-zum-klon> -Nachricht "Text"
param(
  [Parameter(Mandatory)] [string] $Repo,
  [Parameter(Mandatory)] [string] $Nachricht
)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$ziel = Join-Path $Repo 'kurs'
New-Item -ItemType Directory -Force $ziel | Out-Null

# encor-1.4.10 (ohne Arbeitsreste) spiegeln
$quelle = Join-Path $root 'encor-1.4.10'
$zielKurs = Join-Path $ziel 'encor-1.4.10'
robocopy $quelle $zielKurs /MIR /NFL /NDL /NJH /NJS /NP | Out-Null
# Werkzeuge
robocopy (Join-Path $root 'tools') (Join-Path $ziel 'tools') pruefen.ps1 ANLEITUNG-KAPITEL.md git-sync.ps1 /NFL /NDL /NJH /NJS /NP | Out-Null
# Prüfprotokolle und Faktencheck-Bericht
robocopy (Join-Path $root 'research_notes\Kapitelpruefung') (Join-Path $ziel 'pruefprotokolle') /MIR /NFL /NDL /NJH /NJS /NP | Out-Null
$bericht = Join-Path $root 'reports\CiscoTutor Fragen Faktencheck.md'
if (Test-Path $bericht) { Copy-Item $bericht (Join-Path $ziel 'pruefprotokolle\Faktencheck-Bestand-1132-Fragen.md') -Force }

git -C $Repo add kurs
$st = git -C $Repo status --porcelain
if (-not $st) { 'Keine Änderungen.'; return }
git -C $Repo commit -q -m $Nachricht
git -C $Repo log --oneline -1
git -C $Repo show --stat --oneline HEAD | Select-Object -Last 3
