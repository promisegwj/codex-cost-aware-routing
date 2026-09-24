param(
    [string]$CodexHome = "$env:USERPROFILE\.codex",
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$SourceRoot = Join-Path $ProjectRoot "codex-home"

if (-not (Test-Path -LiteralPath $SourceRoot)) {
    throw "Missing source folder: $SourceRoot"
}

function Copy-ManagedFile {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    $parent = Split-Path -Parent $Destination
    if ($WhatIf) {
        Write-Host "[what-if] Copy $Source -> $Destination"
        return
    }

    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    Copy-Item -LiteralPath $Source -Destination $Destination -Force
}

function Copy-ManagedTree {
    param(
        [Parameter(Mandatory = $true)][string]$SourceDir,
        [Parameter(Mandatory = $true)][string]$DestinationDir
    )

    if (-not (Test-Path -LiteralPath $SourceDir)) {
        return
    }

    $sourceFull = [System.IO.Path]::GetFullPath($SourceDir).TrimEnd('\', '/')
    Get-ChildItem -LiteralPath $SourceDir -File -Recurse | ForEach-Object {
        $fileFull = [System.IO.Path]::GetFullPath($_.FullName)
        $relative = $fileFull.Substring($sourceFull.Length).TrimStart('\', '/')
        $target = Join-Path $DestinationDir $relative
        Copy-ManagedFile -Source $_.FullName -Destination $target
    }
}

Copy-ManagedTree -SourceDir (Join-Path $SourceRoot "agents") -DestinationDir (Join-Path $CodexHome "agents")
Copy-ManagedTree -SourceDir (Join-Path $SourceRoot "skills") -DestinationDir (Join-Path $CodexHome "skills")
Copy-ManagedTree -SourceDir (Join-Path $SourceRoot "templates") -DestinationDir (Join-Path $CodexHome "templates")

$GlobalAgents = Join-Path $SourceRoot "AGENTS.md"
if (Test-Path -LiteralPath $GlobalAgents) {
    Copy-ManagedFile -Source $GlobalAgents -Destination (Join-Path $CodexHome "AGENTS.md")
}

$RoutingControls = Join-Path $SourceRoot "routing-controls.toml"
if (Test-Path -LiteralPath $RoutingControls) {
    Copy-ManagedFile -Source $RoutingControls -Destination (Join-Path $CodexHome "routing-controls.toml")
}

$ProfilesDir = Join-Path $SourceRoot "profiles"
if (Test-Path -LiteralPath $ProfilesDir) {
    Get-ChildItem -LiteralPath $ProfilesDir -Filter "*.config.toml" -File | ForEach-Object {
        Copy-ManagedFile -Source $_.FullName -Destination (Join-Path $CodexHome $_.Name)
    }
}

$Snippet = Join-Path $SourceRoot "config-routing-snippet.toml"
Write-Host ""
Write-Host "Managed files copied from:"
Write-Host "  $SourceRoot"
Write-Host ""
Write-Host "Config snippet was not merged automatically:"
Write-Host "  $Snippet"
Write-Host ""
Write-Host "Review and merge it into:"
Write-Host "  $(Join-Path $CodexHome 'config.toml')"
