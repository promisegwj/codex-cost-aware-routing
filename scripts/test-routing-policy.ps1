[CmdletBinding()]
param(
    [string]$PythonPath = (Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe')
)
$ErrorActionPreference = 'Stop'
$routingRoot = Split-Path -Parent $PSScriptRoot
$selector = Join-Path $routingRoot 'codex-home/skills/codex-workflow/scripts/select_route.py'
$scenarios = Join-Path $routingRoot 'codex-home/skills/codex-workflow/scripts/test_select_route.py'
& $PythonPath $selector --check-policy
if ($LASTEXITCODE -ne 0) { throw 'Routing policy consistency failed' }
& $PythonPath $scenarios
if ($LASTEXITCODE -ne 0) { throw 'Routing regression scenarios failed' }
Write-Host 'Routing policy and scenario validation passed.'
