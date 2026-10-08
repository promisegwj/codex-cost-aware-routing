# Codex Workflow Reference

This is the human-readable reference for the active `codex-workflow` skill. The short skill is the operating entry point; this file explains the rationale and keeps the longer governance details.

Workflow policy defaults and the semantic role-to-model matrix live in `routing-controls.toml`. Keep prose aligned to that file instead of creating a second policy source.

## Resolve routing configuration paths first

`routing-controls.toml` is a Codex home root file, not a skill-local resource. Resolve it before reading policy or selecting roles:

- Installed skill: use `$CODEX_HOME/routing-controls.toml` when CODEX_HOME is set; otherwise use `$USERPROFILE/.codex/routing-controls.toml` on Windows.
- Repository source: when maintaining this project, use `<project-root>/codex-home/routing-controls.toml`; compare it with the deployed file only when checking or deploying runtime behavior. Do not silently substitute repository policy for missing runtime policy.
- From the skill directory, the home root is two directory levels above: `../../routing-controls.toml`. `config.toml`, `agents/` and `templates/` also belong to that home root. Only `references/` and `scripts/` are skill-relative.
- Never try `<skill-directory>/routing-controls.toml`, including `$CODEX_HOME/skills/codex-workflow/routing-controls.toml`. Check the resolved file with `Test-Path -LiteralPath` before reading it; if missing, report the exact missing path and classify it as a configuration/context failure. Do not recursively scan Codex home or infer model defaults from a different file.
- Record the resolved controls path in route evidence. `scripts/select_route.py` already resolves the home root with `Path(__file__).resolve().parents[3]`; its advice is not dispatch evidence.

## Default Intent

- Complete work reliably without letting underpowered first attempts create repeated rework.
- Conserve credits through deterministic routing, bounded context, and fewer retry loops.
- Use the root for T0/T1 implementation between required independent Astra high boundary roles.
- Treat T2 as managed and conditional rather than always hard-routed.
- Keep T3/T4 hard-routed with real independent execution evidence.
- Allow only one active writing worker per write scope.
- Validate before review.
- Escalate with a failure packet instead of blind retries.
- Treat model capacity or availability errors as runtime constraints, not code failures.
- Keep route evidence compact where independence is optional, and complete where independence is mandatory.
- Use approved ordinary Astra roles; reserve the exceptional gate for reasoning_specialist.

The root default source is `config.toml`:

```toml
model = "gpt-6.1-sol"
model_reasoning_effort = "low"
```

Sol low is the normal baseline. Luna medium requires trivial deterministic execution evidence. Initial planning and final review always use independent Astra high contexts, across all tiers. Implementation/specialist escalation remains evidence-gated.

## Two-Axis Selection And Adaptation

Read `references/two-axis-routing.md` when model/effort selection or adaptation is nontrivial. `routing-controls.toml [selection_policy]`, `[execution_profiles]` and `[adaptation_policy]` are authoritative. `scripts/select_route.py` supplies read-only deterministic advice from evidence-backed classification; advice is not agent execution.

- Choose workflow tier by consequences and governance, model by semantic capability, and effort by reasoning density. File count and a request for confidence alone do not force a model upgrade.
- Use Sol medium for integrated T2 work; Sol high for named dense reasoning or demonstrated medium reasoning insufficiency. Use Astra low for frontier defaults and medium for named dense/coupled reasoning; Astra high is mandatory for initial planning/final review; implementation or specialist high requires documented medium inadequacy.
- Diagnose failures first. Repair missing context, instructions, tools, environment and known ordinary defects; capacity follows availability fallback. None of these alone justifies increasing effort or invoking a specialist.
- Effort limit: one next-effort attempt with evidence. Capability limit: direct model promotion with evidence. Sol medium -> high -> Astra medium is an effort path; Luna -> Sol medium -> Astra medium is a capability path, not a mandatory ladder.
- Permit at most two automatic transitions and three total writer attempts per acceptance matrix, including ordinary repairs. One initial attempt per selected profile plus the separately bounded narrow rework pass; stop with a packet when the applicable budget is exhausted.
- Keep independent roles, single writer, validation-before-review and specialist gate intact. A non-default profile must use an explicit mapped default child if the registered role does not match; copy full role instructions and inspect actual isolation. Do not pretend the root model switched.
- Record actual profile, failure diagnosis, transition reason, budget, acceptance and observed usage. After five comparable accepted runs without substantive rework, consider one lower effort within the Sol low and boundary Astra high floors on a future independent task with identical checks; restore on regression. No automatic global rewrite.

## Semantic Role Matrix

The active role names describe responsibility instead of pinning policy to an older model generation.

| Role | Model / effort | Default use |
|---|---|---|
| `root_direct` | `gpt-6.1-sol / low` | T0/T1 implementation, orchestration, compact T2 decisions |
| `batch_worker` | `gpt-6-luna / medium` | Evidenced trivial deterministic, availability-gated mechanical batch work |
| `explorer` | `gpt-6.1-sol / low` | Read-only source discovery |
| `worker_standard` | `gpt-6.1-sol / low` | Managed T2 implementation |
| `worker_sol` | `gpt-6.1-sol / medium` | Intermediate T2 writer for multi-module or reasoning-heavy work |
| `worker_frontier` | `gpt-6-astra / low` | Critical-risk escalation, T3, T4 milestone work |
| `reviewer_risk` | `gpt-6.1-sol / medium` | Independent review for T2 escalation |
| `reviewer_frontier` | `gpt-6-astra / low` | T3/T4 and critical-risk review |
| `planner_frontier` | `gpt-6-astra / high` | Mandatory initial planning, every T0–T4 task |
| `reviewer_final` | `gpt-6-astra / high` | Mandatory final review after validation, every T0–T4 task |
| `reasoning_specialist` | `gpt-6-astra / medium` | Exceptional bounded read-only reasoning after a separate gate |

`worker_standard` uses Sol low for bounded changes; `worker_sol` uses Sol medium for integrated or multistep work. Luna medium only executes evidenced trivial deterministic steps. Every tier has independent Astra high planning/final review; intermediate risk review remains separate.

Luna is not assumed to exist on every surface. `batch_worker` is guarded by `availability_gate = true` and falls back to `worker_standard` when unavailable or unsafe.

## Transition-Only Legacy Roles

Legacy role files remain under `agents/` so older ledgers, templates, and deployed configurations do not break during the first transition. They are not active defaults:

- `classifier_mini`
- `mini_worker`
- `scout_mini`
- `worker_54`
- `worker_54_high`
- `worker_55`
- `worker_55_high`
- `planner_55`
- `planner_55_xhigh`
- `reviewer_54`
- `reviewer_55_medium`
- `reviewer_55`
- `reviewer_55_xhigh`

New workflow text, route ledgers, and diagrams should use semantic roles. Old names may appear only in transition-only compatibility notes or historical records.

## Tier Summary

| Tier | Use when | Default route |
|---|---|---|
| T0 | typo, import, tiny single-file edit | `planner_frontier -> root_direct or eligible batch_worker -> validation -> reviewer_final` |
| T1 | localized bug or small feature with clear scope | `planner_frontier -> root_direct or eligible batch_worker -> validation -> reviewer_final` |
| T2 | medium complexity, unclear scope, high-value config/routing, small multi-file work | managed conditional: `planner_frontier -> Sol writer by scope -> validation -> optional reviewer_risk -> reviewer_final` |
| T3 | critical consequences, public contracts, unresolved implementation failure with potential high consequences | hard route: `planner_frontier -> worker_frontier -> validation -> reviewer_frontier -> reviewer_final` |
| T4 | architecture, migration, multi-milestone project | hard route: `planner_frontier -> execution within existing authorization -> staged worker_frontier -> reviewer_frontier -> reviewer_final` |

## T2 Managed Conditional Route

T2 balances cost and independence. It is not allowed to silently pretend that separate child contexts ran, but it also does not need a full hard-route fanout when the root thread can make a bounded decision and the work remains below T3.

Required compact evidence:

- route decision and tier
- spawned child ids if any
- model/effort source, usually `routing-controls model_roles mapping`
- validation result
- frontier capability escalation decision

Default T2 route:

```text
planner_frontier -> Sol writer by scope -> validation -> optional reviewer_risk -> reviewer_final
```

Use `worker_sol` (`gpt-6.1-sol / medium`) when scope requires integrated or multistep Sol reasoning but has no critical-risk trigger. Escalate to `worker_frontier` (`gpt-6-astra / low`) for critical risk or evidenced assigned-model limits under the adaptation policy:

- security, auth, permissions, payments, privacy, or encryption
- data loss, data consistency, or migration risk
- public API, schema, contract, or backward compatibility risk
- an unresolved implementation failure has potential high consequences
- user explicitly requests a frontier model
- reviewer or validator finds a high-severity issue
- demonstrated assigned-model limitations under the two-axis adaptation policy

If T2 expands into T3/T4, stop and re-route through the hard routing gate.

## Exceptional GPT-6 Reasoning Gate

`reasoning_specialist` is deliberately orthogonal to T0-T4. It is not an automatic next rung above T4, and it never becomes the implementation writer.

The gate passes only through one of two evidence paths:

1. A named subproblem contains explicit ultra-hard coupling or genuinely novel reasoning, and the record explains why the current assigned route cannot reliably resolve it.
2. A failure packet from an actual assigned-route attempt demonstrates a reasoning limitation. Tool failures, unavailable executables, permissions, missing context, environment problems, timeouts, and model capacity do not qualify.

The following are negative cases and must keep the specialist gate closed when they appear alone:

- T3 or T4 classification
- security or other high risk
- a large file count or broad repository
- a request for high confidence
- model capacity or temporary unavailability

When the gate passes, isolate one bounded read-only reasoning or planning question. The existing assigned writer remains responsible for changes and validation. Invoke the registered `reasoning_specialist` role at `gpt-6-astra / medium`. If the role is not registered on the current surface, a `default` child may be used only after the same gate passes, with explicit `model=gpt-6-astra`, `reasoning_effort=medium`, and a bounded prompt or limited fork. Inspect the actual execution restriction and record `read_only_enforcement=sandbox` or `prompt_only`. The prompt must say read-only, no file changes, no implementation, and return a specialist handoff, but prompt-only enforcement is not a hard isolation guarantee. If enforced read-only isolation is required and unavailable, return `route_blocked`. Role-registration fallback does not relax the model or effort availability gate.

Medium is the default. High requires recorded evidence that medium reasoning was inadequate for the same bounded question. Xhigh, max, and ultra require an explicit user request plus support on the current runtime. Do not infer a GPT-6.1 Sol, Luna, or Terra substitute from a family label or an economics table.

## T3/T4 Hard Routing Enforcement

For required boundary roles at every tier and T3/T4 roles, the route is not executed until required roles have real execution evidence.

1. Perform Execution Context Discovery. Record whether the current surface exposes subagent, thread, or model-override execution; visible roles; expected route; and route-blocked decision. If tools are not visible, use `tool_search` before returning `route_blocked`.
2. Start or update a route ledger from `templates/route-ledger.md`.
3. Run Reuse Gate before any child spawn: check `parent_route_id + role + scope_key + acceptance_matrix_id + batch_id`.
4. Run `explorer`, `worker_frontier`, `planner_frontier`, `reviewer_frontier`, and `reviewer_final` in separate contexts when the tier requires them.
5. Route evidence must name child id, parent id when visible, thread source, evidence source, agent role, model/effort source, status, and adoption reason.
6. Goal mode, continuation prompts, and handoff packages are not hard-routing evidence.
7. If no separate execution context can be created after discovery and `tool_search`, return `route_blocked` and name the missing tool or unavailable model. Do not request approval to degrade into one main-agent pass.

## Reuse Gate And Spawn Budget

Reuse Gate is a required pre-spawn check. The pool key is:

```text
parent_route_id + role + scope_key + acceptance_matrix_id + batch_id
```

When an existing child matches that key and is still suitable, send narrow follow-up into that child. A new child is allowed only when the existing child is failed, blocked, timed out, closed, unavailable, polluted, working on an expanded scope, or the route needs an independent lens that cannot be satisfied by the existing context.

Spawn Budget rules:

- User-requested child counts are caps, not targets.
- T2/T3 default child budget is three: planner, one writer and final reviewer. Optional explorers require an explicit expansion packet. T3 intermediate reviewer is a fourth required context; record the policy-required expansion before spawning it.
- The same role may appear at most once for the same scope unless the scope or acceptance matrix expands.
- Budget expansion requires a packet naming the requested expansion, current children, why reuse is unsafe, expected extra value, and stop condition.
- Placeholder, mistaken, or wrong-scope children are recorded as `ignored` / `pollution`.

## Single-Writer Discipline

Only one writer may be active on the same write scope unless the user explicitly asks for parallel implementation. The main agent may prepare non-conflicting validation or acceptance criteria while waiting, but should not race a healthy child writer.

Replacing a writer is allowed only when it failed, blocked, timed out, was abandoned or closed, produced unavailable or unusable output, or the user explicitly requested degraded main-thread execution. Before replacement, record the old writer status and a replacement packet.

Main-session substitution is narrower than replacement. It is allowed only after `blocked`, `timeout`, `closed_with_unusable_output`, or explicit user-degraded execution, and it must record original worker id, blocking reason, reusable output, main-session write scope, validation commands, and reviewer closure plan.

## Reviewer Stickiness

The reviewer that raised a material issue should close it when possible. For the same `acceptance_matrix_id`, use the same reviewer for closure unless it is blocked, unavailable, timed out, polluted, or the acceptance matrix changed.

One intermediate risk reviewer plus the mandatory final reviewer is allowed with recorded distinct purposes; the child budget still requires expansion where needed. Additional reviewers require a recorded reason or expansion packet. If the original reviewer cannot rerun, the final note must name the substitute validation or review evidence.

## Explorer Fanout Cap

Explorer fanout is read-only discovery, not a way to race implementation. Default maximum is four explorers, and a user-requested number is a cap.

Before fanout, record:

- coverage matrix
- lens per explorer
- stop condition

Do not spawn multiple explorers with the same lens and same scope unless the coverage matrix explicitly justifies it.

## Model Capacity And Availability Fallback

The error:

```text
Selected model is at capacity. Please try a different model.
```

means the selected pool was unavailable at that moment. It is not a task failure.

Rules:

- Do not count a capacity error as a worker implementation failure.
- Record the route note as `model_capacity`.
- Use the closest safe available model/profile by cost and capability.
- Do not assume Luna exists. `batch_worker` requires availability evidence and falls back to `worker_standard`.
- For high-risk work, do not blindly downgrade implementation quality. Use a safe higher-capability route, planning-only fallback, or pause.
- Capacity does not open the specialist gate or authorize automatic expensive effort increases.

## Risk Scoring

The following cues guide discovery and validation planning; they are not a numeric model-upgrade threshold. File count and ordinary environment failures alone do not promote the model.

Add risk cues for:

- `+3`: auth, security, permissions, payments, encryption
- `+3`: migrations, data deletion, data consistency
- `+2`: public API, schema, contract
- `+2`: root cause unknown
- `+2`: lower-tier worker already failed
- `+1`: more than five files likely change
- `+1`: no clear validation path
- `+1`: vague request
- `+1`: frontend/backend coupling
- `+1`: cache, concurrency, async jobs
- `+1`: cross-module refactor

Force at least T3 for security, permissions, payments, privacy, irreversible data changes, public compatibility, or unresolved implementation failures with potential high consequences. Context/tool/environment/capacity failures do not force T3.

## User-Specific Overlay

- APDL/MAPDL, engineering simulation, build-only logs, validation matrices, rail/track/damping/floating-slab work default to at least T2.
- Environment, Codex config, plugins, tool routing, executable paths, and global settings default to T2 when editing shared config; verify with path/profile/CLI behavior or dry-run sync.
- Voice automation is script/config work in the Voice project; routing policy may reference it but must not own voice helper scripts.
- Git/GitHub/release/sync tasks start read-only with branch/status/diff/remote awareness; commit or push only when explicitly asked.
- UI/browser/Chrome/localhost/frontend/3D preview tasks need browser or screenshot verification for meaningful UI changes.
- `评审`、`复核`、`审查`、`检查`、`方案`、`规划` normally mean read-only reviewer/planner mode until the user asks for implementation.
- Consecutive step projects should return a continuation packet: current stop, validation state, blockers, next step, and what not to repeat.
- Formal documents, papers, Word, PDF, LaTeX, Zotero, slides, and spreadsheets should route to the relevant document/data skill with render/compile/visual QA when layout matters.

## T4 Milestone Packets

Rules:

- The planner defines milestones before implementation.
- Each milestone uses `templates/t4-milestone-packet.md`.
- Default milestone implementation uses `worker_frontier`.
- Only a separately scored T0/T1 trivial deterministic subtask under a T4 parent may use Luna medium with explicit eligibility evidence and availability; never use Luna for an entire T4 milestone. The parent retains its frontier writer, milestone review and Astra high final review; every subtask also retains mandatory Astra high boundary roles.
- Each milestone gets focused validation and `reviewer_frontier`.
- The final merged state gets a cross-milestone pass from `reviewer_final`.

## Failure Packet

Use after a failed worker attempt instead of looping:

```text
# Failure Packet

## Original goal
## Constraints / acceptance criteria
## Attempted approach
## Current diff summary
## Validation result
- command:
- result:
- failure summary:

## Relevant files
## Reviewer findings
## Suspected root cause of failure
## What not to repeat
## Recommended escalation
- target worker:
- reasoning effort:
- specific instructions:
```

## Output Format

Return concise results:

```text
完成情况:
- ...

修改文件:
- file: change

验证:
- command: passed / failed / not run

风险或后续:
- ...

路由证据:
- tier, role, model/effort source, child ids if any, route_blocked or escalation note
```

## Effective Mapping And Economic Assumptions

See `references/model-selection-evidence-2026-09.md` for historical benchmark evidence and official GPT-6.1 Sol guidance; do not transfer older-model scores to 6.1 Sol. Public API price figures are only comparison proxies and do not establish Codex subscription credit consumption.

Compare registered effective model/effort against controls before invocation. Stale or missing registrations require a default child with explicit mapped model/effort, bounded fork/context, full role instructions, ownership and acceptance criteria. Verify exact model/effort availability. Record actual read-only enforcement as sandbox or prompt_only; prompt-only is not hard isolation. Return route_blocked if required isolation is unavailable. Preserve independent roles, single writer and validation before review.

Luna medium requires trivial deterministic execution evidence and availability. If unsuitable or unavailable, use Sol low or above with recorded reason. Historical Terra fallback files are inactive; no automatic Terra route. Planning/final review preserve Astra high and return route_blocked if unavailable. Implementation/specialist Astra high requires documented medium inadequacy; xhigh/max/ultra requires explicit request plus runtime support. Only reasoning_specialist requires its exceptional gate.
