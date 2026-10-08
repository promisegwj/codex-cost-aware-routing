# Model and effort selection — 2026-10-07

Authority: routing-controls.toml, policy 2026-10-07-sol-default-astra-high-boundaries-v2.
Policy heuristics are not measured quality guarantees. Tier, model and effort remain separate.

## Resolve routing configuration paths first

`routing-controls.toml` is a Codex home root file, not a skill-local resource. Resolve it before reading policy or selecting roles:

- Installed skill: use `$CODEX_HOME/routing-controls.toml` when CODEX_HOME is set; otherwise use `$USERPROFILE/.codex/routing-controls.toml` on Windows.
- Repository source: when maintaining this project, use `<project-root>/codex-home/routing-controls.toml`; compare it with the deployed file only when checking or deploying runtime behavior. Do not silently substitute repository policy for missing runtime policy.
- From the skill directory, the home root is two directory levels above: `../../routing-controls.toml`. `config.toml`, `agents/` and `templates/` also belong to that home root. Only `references/` and `scripts/` are skill-relative.
- Never try `<skill-directory>/routing-controls.toml`, including `$CODEX_HOME/skills/codex-workflow/routing-controls.toml`. Check the resolved file with `Test-Path -LiteralPath` before reading it; if missing, report the exact missing path and classify it as a configuration/context failure. Do not recursively scan Codex home or infer model defaults from a different file.
- Record the resolved controls path in route evidence. `scripts/select_route.py` already resolves the home root with `Path(__file__).resolve().parents[3]`; its advice is not dispatch evidence.

## Decision order

1. Classify workflow tier by scope and consequence. Architecture forces T4, critical risk at least T3, shared config/engineering at least T2. Planning/final roles alone never force T4.
2. Every task, including T0/T1 and trivial execution, receives independent initial planner_frontier and final reviewer_final contexts, both Astra high minimum. No exemption, no medium-attempt prerequisite. Existing authorization permits implementation after planning; ask only for specific unauthorized actions.
3. Default root and bounded writer/discovery use Sol low; integrated or multistep work uses Sol medium, named dense derivations Sol high. Critical implementation/risk review remains Astra low/medium. Implementation/specialist Astra high still requires demonstrated medium inadequacy.
4. Luna medium only executes explicitly classified trivial deterministic low-risk steps without diagnosis, design, ambiguity or substantive reasoning. Require trivial_execution=true and nonempty execution_evidence; only worker/batch at T0/T1, bounded/routine and no risk/shared-config/engineering/architecture overlay qualify. File count and short task length are not eligibility evidence.
5. Check actual runtime mapping, exact availability, full role instructions, bounded context, ownership, acceptance and actual restrictions. Fixed registered role mismatch requires an explicitly mapped default child. Never claim the current chat model switched.

## Independent contexts and budgets

Planner, writer and final reviewer stay distinct; root may implement T0/T1. Default three-child budget covers planner + one writer + final reviewer. Optional explorer needs a recorded budget expansion. T3 retains its independent intermediate reviewer_frontier plus final review, requiring an explicit policy-required expansion to four contexts (five with explorer). T4 keeps milestone review and packets. Missing required Astra high availability or isolation returns route_blocked, never silent downgrade.

## Failures and adaptation

Context, instructions, tool, environment, capacity and diagnosed ordinary defects require cause repair or recorded safe fallback without automatic reasoning escalation. No automatic Terra fallback; retained Terra files are historical inactive profiles. Luna outage/unsuitability goes to Sol low or above. Boundary capacity retains Astra high or stops.

Effort transitions: Sol low → medium → high → Astra medium; Astra implementation low → medium → high → stop, with evidence. Luna reasoning insufficiency means its trivial lane is exceeded: reclassify to Sol medium. Capability transitions: Luna → Sol medium; Sol → Astra medium; Astra → stop or evaluate separate specialist gate. Final boundary floor is reapplied after every initial override, failure, repair, previous-profile restoration or stop path; boundary Astra high effort failure stops with handoff rather than automatic xhigh.

Allow at most two automatic transitions and three total writer attempts per acceptance matrix, including ordinary repairs. One initial attempt per profile and at most one narrow reviewer rework pass. Preserve single writer and record replacement evidence. Budget exhaustion stops new work with a failure packet. xhigh/max/ultra requires explicit request and runtime support. Specialist remains bounded, read-only and separately gated; boundary high never opens that gate.

## Read-only selector

scripts/select_route.py reads evidence-backed JSON and returns advice only; it does not dispatch, infer from arbitrary prose, switch the chat model or verify capacity.

| Input | Values / default |
|---|---|
| tier | T0..T4; T1 default |
| role | worker/reviewer/planner/final/explorer/batch; worker default; reviewer means intermediate review |
| complexity | bounded/integrated/novel; bounded default |
| reasoning | routine/multistep/dense; routine default |
| critical_risk/shared_config/engineering/architecture/high_confidence/trivial_execution | Boolean; false default |
| execution_evidence | Specific deterministic instructions and reason no judgment is needed; nonempty for Luna |
| evidence | Named reasoning/capability evidence or failure diagnosis |
| failure | none/context/instructions/tool/environment/capacity/validation_defect/effort_limit/capability_limit |
| previous_profile | Actual profile; only with failure |
| transitions_used/writer_attempts_used | Nonnegative counts across the acceptance matrix |

Unknown fields, string booleans, invalid tiers and extreme-effort requests are rejected. Stop/needs_evidence/budget_exhausted prohibit dispatch; repair_first requires repair/fallback first. Advice always includes route_executed=false, availability=unverified and specialist_gate=not_evaluated_not_authorized.

```powershell
$routePython = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$routeHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
$routeScript = Join-Path $routeHome 'skills/codex-workflow/scripts/select_route.py'
'{"tier":"T1","role":"planner"}' | & $routePython $routeScript
& $routePython $routeScript --check-policy
```

## Feedback floors

After five comparable accepted runs without substantive rework, consider a lower-effort candidate only on a future task within Sol low and boundary Astra high floors. Never downshift to Luna without its explicit eligibility evidence. Record actual model/effort, acceptance, rework, time and observed usage; missing consumption stays unavailable. API prices cannot establish Codex subscription consumption. No automatic global policy rewrite.
