# Redeploy API (Heroku) + frontend (Firebase).
# Uso:
#   .\scripts\deploy-all.ps1

param(
    [string]$AppName = "talonario-rifas-api",
    [string]$Branch = "main",
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

& (Join-Path $Root "scripts\deploy-api.ps1") -AppName $AppName -Branch $Branch
& (Join-Path $Root "scripts\deploy-front.ps1") -SkipInstall:$SkipInstall
