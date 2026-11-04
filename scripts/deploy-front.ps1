# Redeploy frontend (React/Vite) to Firebase Hosting.
# Uso:
#   .\scripts\deploy-front.ps1
# Opcional (saltar npm install):
#   .\scripts\deploy-front.ps1 -SkipInstall

param(
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Get-Command firebase -ErrorAction SilentlyContinue)) {
    throw "firebase-tools no está instalado. Ejecuta: npm install -g firebase-tools"
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "npm no está instalado o no está en el PATH."
}

$envFile = Join-Path $Root "frontend\.env.production"
if (-not (Test-Path $envFile)) {
    Write-Host "Falta frontend\.env.production" -ForegroundColor Yellow
    Write-Host "Copia frontend\.env.production.example y pon las URLs reales."
    throw "Abortado: sin .env.production"
}

Write-Host "Proyecto Firebase:"
firebase use

Set-Location (Join-Path $Root "frontend")
if (-not $SkipInstall) {
    Write-Host "npm install..."
    npm install
}
Write-Host "npm run build..."
npm run build

Set-Location $Root
Write-Host "firebase deploy --only hosting..."
firebase deploy --only hosting

Write-Host ""
Write-Host "Frontend desplegado." -ForegroundColor Green
Write-Host "URL típica: https://talonario-rifas-hasbon.web.app"
