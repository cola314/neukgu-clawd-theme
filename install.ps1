#!/usr/bin/env pwsh
# Install 늑구 (Neukgu) theme for Clawd on Desk on Windows.

$ErrorActionPreference = "Stop"

$userData = Join-Path $env:APPDATA "clawd-on-desk"
if (-not (Test-Path $userData)) {
    Write-Host "ERROR: Clawd userData not found at $userData" -ForegroundColor Red
    Write-Host "Is Clawd on Desk installed? Download from https://github.com/rullerzhou-afk/clawd-on-desk"
    exit 1
}

$themeDir  = Join-Path $userData "themes\neukgu"
$cacheDir  = Join-Path $userData "theme-cache\neukgu\assets"
$scriptDir = $PSScriptRoot

Write-Host "Installing 늑구 (Neukgu) theme..." -ForegroundColor Cyan
Write-Host "  source: $scriptDir"
Write-Host "  target: $themeDir"
Write-Host ""

# 1. Theme files -> userData/themes/neukgu/
New-Item -ItemType Directory -Force -Path (Join-Path $themeDir "assets") | Out-Null
Copy-Item (Join-Path $scriptDir "theme.json") $themeDir -Force
Copy-Item (Join-Path $scriptDir "assets\*") (Join-Path $themeDir "assets") -Force
Write-Host "  [1/2] theme + assets copied" -ForegroundColor Green

# 2. Workaround: copy PNG also to theme-cache so SVG's relative href resolves
#    (Clawd's external-theme loader caches SVGs but leaves non-SVG in source dir,
#    breaking <image href="idle-eyeless.png"> in idle-follow.svg)
New-Item -ItemType Directory -Force -Path $cacheDir | Out-Null
Copy-Item (Join-Path $scriptDir "assets\idle-eyeless.png") $cacheDir -Force
# Remove cached SVG so Clawd re-sanitizes freshly on next theme load
$cacheSvg = Join-Path $cacheDir "idle-follow.svg"
if (Test-Path $cacheSvg) { Remove-Item $cacheSvg -Force }
Write-Host "  [2/2] cache workaround applied" -ForegroundColor Green

Write-Host ""
Write-Host "Installed!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Restart Clawd on Desk (quit from tray then relaunch)"
Write-Host "  2. Right-click pet -> Theme -> 늑구 (Neukgu)"
