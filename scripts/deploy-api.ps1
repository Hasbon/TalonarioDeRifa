# Redeploy backend (FastAPI) to Heroku.
# Uso (desde cualquier carpeta):
#   .\scripts\deploy-api.ps1
# Opcional:
#   .\scripts\deploy-api.ps1 -AppName talonario-rifas-api -Branch main

param(
    [string]$AppName = "talonario-rifas-api",
    [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Get-Command heroku -ErrorAction SilentlyContinue)) {
    throw "Heroku CLI no está instalada o no está en el PATH."
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git no está instalado o no está en el PATH."
}

$who = heroku auth:whoami 2>$null
if (-not $who) {
    Write-Host "No hay sesión de Heroku. Ejecuta: heroku login"
    heroku login
}

$status = git status --porcelain
if ($status) {
    Write-Host "Hay cambios sin commit. Haz commit antes de desplegar la API." -ForegroundColor Yellow
    git status --short
    throw "Abortado: working tree no está limpio."
}

Write-Host "Obteniendo token de Heroku..."
$token = (heroku auth:token 2>$null | Select-Object -Last 1).ToString().Trim()
if (-not $token) {
    throw "No se pudo obtener heroku auth:token. Ejecuta heroku login."
}

Write-Host "Generando subtree de backend (rama $Branch)..."
$split = (git subtree split --prefix backend $Branch).Trim()
if (-not $split) {
    throw "git subtree split falló."
}

Write-Host "Subiendo a Heroku app '$AppName'..."
git -c credential.helper= push "https://heroku:$token@git.heroku.com/$AppName.git" "${split}:refs/heads/main"

Write-Host ""
Write-Host "API desplegada." -ForegroundColor Green
$webUrl = (heroku apps:info -a $AppName -s 2>$null | Select-String '^web_url=' | ForEach-Object { $_.ToString().Split('=')[1] })
if ($webUrl) {
    Write-Host "Health: ${webUrl}health"
    Write-Host "Docs:   ${webUrl}docs"
} else {
    Write-Host "Info:   heroku apps:info -a $AppName"
}
Write-Host "Logs:   heroku logs --tail -a $AppName"
