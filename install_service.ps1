# ============================================================
# Installation du backend comme service Windows avec NSSM
# Exécuter en tant qu'Administrateur :
#   Right-click -> "Run with PowerShell as Administrator"
#   ou : Start-Process powershell -Verb RunAs -ArgumentList "-File install_service.ps1"
# ============================================================

$ServiceName  = "EtatJournalierBackend"
$ProjectRoot  = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir   = Join-Path $ProjectRoot "back_end"
$PythonExe    = (Get-Command python).Source   # ou mettre le chemin complet si plusieurs Python

# Ajuster si votre nssm.exe n'est pas dans le PATH
$Nssm = "nssm"

Write-Host "=== Installation du service '$ServiceName' ===" -ForegroundColor Cyan

# Supprimer l'ancien service si existe
$existing = sc.exe query $ServiceName 2>$null
if ($existing -match "STATE") {
    Write-Host "Service existant détecté, suppression..." -ForegroundColor Yellow
    & $Nssm stop $ServiceName
    & $Nssm remove $ServiceName confirm
}

# Installer
& $Nssm install $ServiceName $PythonExe "main_https.py"

# Répertoire de travail
& $Nssm set $ServiceName AppDirectory $BackendDir

# Redémarrage automatique en cas de crash
& $Nssm set $ServiceName AppRestartDelay 5000

# Logs (créer le dossier logs/ si inexistant)
$LogDir = Join-Path $ProjectRoot "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
& $Nssm set $ServiceName AppStdout (Join-Path $LogDir "backend-out.log")
& $Nssm set $ServiceName AppStderr (Join-Path $LogDir "backend-err.log")
& $Nssm set $ServiceName AppRotateFiles 1
& $Nssm set $ServiceName AppRotateBytes 5000000   # rotation à 5 MB

# Description
& $Nssm set $ServiceName Description "Etat Journalier - Backend FastAPI HTTPS"

# Démarrage automatique au boot
& $Nssm set $ServiceName Start SERVICE_AUTO_START

# Démarrer maintenant
Write-Host "Démarrage du service..." -ForegroundColor Cyan
& $Nssm start $ServiceName

Start-Sleep -Seconds 2
$status = sc.exe query $ServiceName | Select-String "STATE"
Write-Host "Statut : $status" -ForegroundColor Green
Write-Host ""
Write-Host "Commandes utiles :" -ForegroundColor Yellow
Write-Host "  nssm status $ServiceName"
Write-Host "  nssm restart $ServiceName"
Write-Host "  nssm stop $ServiceName"
Write-Host "  nssm edit $ServiceName     (interface graphique)"
