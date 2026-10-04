# Model and effort selection — 2026-10-03

The authoritative defaults, transition rules and budgets are in routing-controls.toml.
These are policy heuristics, not measured model performance claims. Never rank all
model/effort pairs on a single guaranteed intelligence scale.

## Resolve routing configuration paths first

`routing-controls.toml` is a Codex home root file, not a skill-local resource. Resolve it before reading policy or selecting roles:

- Installed skill: use `$CODEX_HOME/routing-controls.toml` when CODEX_HOME is set; otherwise use `$USERPROFILE/.codex/routing-controls.toml` on Windows.
- Repository source: when maintaining this project, use `<project-root>/codex-home/routing-controls.toml`; compare it with the deployed file only when checking or deploying runtime behavior. Do not silently substitute repository policy for missing runtime policy.
- From the skill directory, the home root is two directory levels above: `../../routing-controls.toml`. `config.toml`, `agents/` and `templates/` also belong to that home root. Only `references/` and `scripts/` are skill-relative.
- Never try `<skill-directory>/routing-controls.toml`, including `$CODEX_HOME/skills/codex-workflow/routing-controls.toml`. Check the resolved file with `Test-Path -LiteralPath` before reading it; if missing, report the exact missing path and classify it as a configuration/context failure. Do not recursively scan Codex home or infer model defaults from a different file.
- Record the resolved controls path in route evidence. `scripts/select_route.py` already resolves the home root with `Path(__file__).resolve().parents[3]`; its advice is not dispatch evidence.

## Decision order

1. Classify workflow tier and consequences. T3/T4 independence, validation and
   single-writer requirements continue even if the selected effort changes.
2. Confirm task context, executable/tool results and acceptance criteria. Discover
   narrowly before treating ambiguity as a capability failure.
3. Select model by semantic scope: Luna for bounded work, 6.1 Sol for integrated
   implementation and domain reasoning, Astra for critical risk or evidenced
   capability limits. More files alone is not a capability reason. A request for
   confidence calls for better acceptance, validation and review.
4. Select effort separately. Sol medium is the complex-work baseline. Use Sol high
   initially only for named dense constraints or derivations. Astra low remains
   the frontier baseline; use medium for named dense/coupled reasoning. Astra high
   requires an actual medium attempt and evidence of inadequate reasoning.
5. Check actual runtime mapping and model/effort availability before dispatch.
   Registered roles are fixed defaults, not dynamic overrides. A different profile
   requires a default child with explicit model/effort and complete role instructions
   from agents/<semantic_role>.toml, bounded context, ownership and acceptance.
   Inspect actual read-only enforcement; a prompt does not create a sandbox.
   The current root model may have been manually selected; never claim it switched.

## Failure and bounded adaptation

| Diagnosis | Action |
|---|---|
| Missing context, wrong instructions, tool/environment failure | Repair the identified cause on the current profile |
| Capacity | Record unavailability; choose an available, suitable configured fallback; no effort escalation |
| A known ordinary implementation defect | Narrow repair and validation; no automatic reasoning promotion |
| Task was understood but a specific derivation/constraint was missed | Increase one effort step with evidence |
| Persistent misunderstanding, wrong abstraction, domain/tool-planning limits | Upgrade model directly with evidence |
| Newly discovered critical consequence | Re-score at least T3; preserve Astra and independent review |

Automatic effort transitions: Luna low -> medium -> high -> Sol medium;
Sol medium -> high -> Astra medium; Astra low -> medium -> high -> stop.
Capability transitions: Luna -> Sol medium; Sol -> Astra medium; Astra -> stop
or evaluate the separate bounded specialist gate. Never force traversal of every
effort setting before a model upgrade.

An adaptation changes at most one selected profile per attempt. Allow no more than
two automatic transitions and three total writer attempts per acceptance matrix,
including ordinary repairs and model changes. max_worker_attempts=1 caps initial attempts per profile; a narrow repair is separately bounded and still counts toward the total;
max_rework_passes=1 caps reviewer-requested narrow repair. Reuse a suitable child
when its profile still matches. A changed profile may require replacing a stopped
writer; record the replacement and do not race it. Budgets take precedence over
available next profiles. Return a failure/continuation packet when exhausted.
Environment repairs do not count as writer attempts until implementation/repair
work resumes. xhigh/max/ultra require explicit user request and exact runtime support.

The specialist remains exceptional, read-only, and separate from ordinary model
promotion. Model promotion to Astra does not itself authorize a specialist.

## Route selector

scripts/select_route.py is a deterministic, read-only advisor. It reads the controls
and an evidence-backed JSON classification. It neither infers risk from arbitrary
text nor spawns agents, calls models, or rewrites user-selected settings.
Use it when classification or adaptation is nontrivial; the explicit policy table
suffices for obvious T0/T1 work. Always record actual execution separately.

PowerShell (bundled runtime, no reliance on the broken local py launcher):

```powershell
$routePython = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$routeHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
$routeScript = Join-Path $routeHome 'skills/codex-workflow/scripts/select_route.py'
'{"tier":"T2","complexity":"integrated"}' | & $routePython $routeScript
& $routePython $routeScript --task (Join-Path (Get-Location) 'task.json')
& $routePython $routeScript --check-policy
```

Input fields (unknown fields, invalid values and string booleans are rejected):

| Field | Values / default |
|---|---|
| tier | T0..T4; default T1; high risk and overlays can raise it |
| role | worker/reviewer/planner/final/explorer/batch; default worker |
| complexity | bounded/integrated/novel; default bounded |
| reasoning | routine/multistep/dense; default routine |
| critical_risk/shared_config/engineering/architecture/high_confidence | Boolean; default false |
| failure | none/context/instructions/tool/environment/capacity/validation_defect/effort_limit/capability_limit |
| evidence | Named reasoning/capability evidence or failure diagnosis; text |
| previous_profile | Actual previously used execution_profiles key; required for reasoning adaptation |
| transitions_used/writer_attempts_used | Nonnegative counts carried across the entire acceptance matrix |

Failure example:

```json
{"tier":"T2","complexity":"integrated","failure":"effort_limit",
 "previous_profile":"sol_medium","evidence":"Context and tools verified; derivation omitted the specified boundary condition",
 "transitions_used":0,"writer_attempts_used":1}
```

This selects sol_high. Omitting evidence yields needs_evidence, not authorization.
Explicit extreme effort is handled by the orchestrator outside the automatic advisor.
Advice carries route_executed=false and availability=unverified. Stop statuses
(needs_evidence, budget_exhausted, stop) prohibit dispatch; repair_first requires
repair/fallback before resuming. Do not treat JSON output as tool execution evidence.

## Feedback and future downshifts

Record accepted result, actual model/effort, substantive rework, elapsed time and
observed usage in the route ledger. Unknown usage remains unavailable; API token
rates do not determine Codex subscription usage. Optimize total work to acceptance,
including retries and handoffs. Do not run exploratory model calls on every task.

After five comparable accepted runs without substantive rework, a future independent
task may try one lower effort step with identical acceptance checks. Restore the
previous profile on regression. The threshold is an initial heuristic; it is not
proof of equivalent capability. Never downgrade an unfinished critical-risk task
or auto-rewrite global policy from a single successful run.

## Basis

Official model guidance supplies the workload distinctions; the transition/budget
thresholds above are local design decisions, pending representative task evidence.
- https://developers.openai.com/api/docs/guides/model-selection
- https://developers.openai.com/api/docs/models/gpt-6.1-sol
- https://developers.openai.com/api/docs/guides/reasoning
