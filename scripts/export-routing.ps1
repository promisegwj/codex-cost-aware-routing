param(
    [string]$CodexRoot = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' })
)
$ErrorActionPreference = 'Stop'
$taskRepository = Split-Path $PSScriptRoot -Parent
$taskDeployableRoot = Join-Path $taskRepository 'codex-home'
$taskSourceRoot = (Resolve-Path -LiteralPath $CodexRoot).Path
$taskManifest = Get-Content -LiteralPath (Join-Path $taskRepository 'routing-files.txt')

# Export only the curated routing manifest. Never copy the whole Codex home.
foreach ($taskRelative in $taskManifest) {
    if ([string]::IsNullOrWhiteSpace($taskRelative)) { continue }
    if ([IO.Path]::IsPathRooted($taskRelative) -or $taskRelative.Split('/') -contains '..') {
        throw "Invalid routing manifest entry: $taskRelative"
    }
    $taskSource = Join-Path $taskSourceRoot $taskRelative
    $taskDestination = Join-Path $taskDeployableRoot $taskRelative
    if (-not (Test-Path -LiteralPath $taskSource -PathType Leaf)) {
        throw "Missing routing file: $taskSource"
    }
    if ([IO.Path]::GetFullPath($taskSource) -eq [IO.Path]::GetFullPath($taskDestination)) {
        throw 'Run this exporter from the repository, not from the deployed Codex directory.'
    }
    New-Item -ItemType Directory -Force -Path (Split-Path $taskDestination) | Out-Null
    if ($taskRelative -eq 'AGENTS.md') {
        # Export only the routing section, never unrelated machine-global instructions.
        $taskAgentsText = [IO.File]::ReadAllText($taskSource)
        $taskManagedMatch = [regex]::Match($taskAgentsText, '(?ms)^## Codex model routing \(managed\)\r?\n.*?(?=^## |\z)')
        if (-not $taskManagedMatch.Success) { throw 'Managed routing AGENTS section is missing' }
        [IO.File]::WriteAllText($taskDestination, $taskManagedMatch.Value.TrimEnd() + "`n", [Text.UTF8Encoding]::new($false))
    } else {
        Copy-Item -LiteralPath $taskSource -Destination $taskDestination
    }
}

# Extract only root model defaults; no credentials, servers or notification paths.
$taskConfigLines = Get-Content -LiteralPath (Join-Path $taskSourceRoot 'config.toml')
$taskRootDefaults = @{}
foreach ($taskLine in $taskConfigLines) {
    if ($taskLine -match '^\s*\[') { break }
    if ($taskLine -match '^\s*(model|model_reasoning_effort)\s*=\s*"([^"\r\n]+)"\s*$') {
        $taskRootDefaults[$Matches[1]] = $Matches[2]
    }
}
foreach ($taskKey in @('model', 'model_reasoning_effort')) {
    if (-not $taskRootDefaults.ContainsKey($taskKey)) { throw "Missing root default: $taskKey" }
}
$taskSnippet = @(
    '# Routing root defaults only. Merge these keys; do not replace a full config.toml.'
    '# In an existing [agents] table, use max_concurrent_threads_per_session = 6.'
    '# max_threads is its legacy alias; never configure both names together.'
    ('model = "{0}"' -f $taskRootDefaults['model'])
    ('model_reasoning_effort = "{0}"' -f $taskRootDefaults['model_reasoning_effort'])
)
[IO.File]::WriteAllLines((Join-Path $taskDeployableRoot 'config-routing-snippet.toml'), $taskSnippet, [Text.UTF8Encoding]::new($false))
Write-Output "Exported $($taskManifest.Count) routing files and root defaults to $taskRepository"
