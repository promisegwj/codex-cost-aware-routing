# Codex Workflow Reference

This is the human-readable reference for the active `codex-workflow` skill. The short skill is the operating entry point; this file explains the rationale and keeps the longer governance details.

Workflow policy defaults and the semantic role-to-model matrix live in `codex-home/routing-controls.toml`. Keep prose aligned to that file instead of creating a second policy source.

## Default Intent

- Complete work reliably without letting underpowered first attempts create repeated rework.
- Conserve credits through deterministic routing, bounded context, and fewer retry loops.
- Use the root thread directly for T0/T1 by default.
- Treat T2 as managed and conditional rather than always hard-routed.
- Keep T3/T4 hard-routed with real independent execution evidence.
- Allow only one active writing worker per write scope.
- Validate before review.
- Escalate with a failure packet instead of blind retries.
- Treat model capacity or availability errors as runtime constraints, not code failures.
- Keep route evidence compact where independence is optional, and complete where independence is mandatory.
- Use approved ordinary Astra roles; reserve the exceptional gate for reasoning_specialist.

The root default source is `codex-home/config-routing-snippet.toml`:

```toml
model = "gpt-5.6-sol"
model_reasoning_effort = "medium"
```

This is intentionally not xhigh. Ordinary roles use the approved Luna/Astra matrix. The exceptional gate applies only to reasoning_specialist.

## Semantic Role Matrix

The active role names describe responsibility instead of pinning policy to an older model generation.

| Role | Model / effort | Default use |
|---|---|---|
| `root_direct` | `gpt-5.6-sol / medium` | T0/T1 implementation, orchestration, compact T2 decisions |
| `batch_worker` | `gpt-5.6-luna / low` | Availability-gated mechanical batch work |
| `explorer` | `gpt-5.6-luna / high` | Read-only source discovery |
| `worker_standard` | `gpt-5.6-luna / xhigh` | Managed T2 implementation |
| `worker_frontier` | `gpt-6-astra / low` | Deterministic T2 escalation, T3, T4 milestone work |
| `reviewer_risk` | `gpt-6-astra / low` | Risk review for T2 escalation, T3, and T4 milestones |
| `planner_frontier` | `gpt-6-astra / medium` | T4 planning and migration specs |
| `reviewer_final` | `gpt-6-astra / medium` | Final T4 cross-milestone review |
| `reasoning_specialist` | `gpt-6-astra / medium` | Exceptional bounded read-only reasoning after a separate gate |

`worker_standard` uses user-approved Luna/xhigh with a pinned Terra/high fallback.

Luna is not assumed to exist on every surface. `batch_worker` is guarded by `availability_gate = true` and falls back to `worker_standard` when unavailable or unsafe.

## Transition-Only Legacy Roles

Legacy role files remain under `codex-home/agents/` so older ledgers, templates, and deployed configurations do not break during the first transition. They are not active defaults:

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
| T0 | typo, import, tiny single-file edit | `root_direct -> validation -> return` |
| T1 | localized bug or small feature with clear scope | `root_direct -> validation -> return` |
| T2 | medium complexity, unclear scope, high-value config/routing, small multi-file work | managed conditional: `optional explorer -> worker_standard -> validation -> optional reviewer_risk` |
| T3 | security, auth, data, public contract, failed lower tier | hard route: `explorer -> worker_frontier -> validation -> reviewer_risk` |
| T4 | architecture, migration, multi-milestone project | hard route: `planner_frontier -> spec approval -> staged worker_frontier -> reviewer_risk -> reviewer_final` |

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
root_direct decision -> optional explorer -> worker_standard -> validation -> optional reviewer_risk
```

Escalate T2 to `worker_frontier` (`gpt-6-astra / low`) when any trigger applies:

- security, auth, permissions, payments, privacy, or encryption
- data loss, data consistency, or migration risk
- public API, schema, contract, or backward compatibility risk
- lower-tier attempt failed or blocked with unclear root cause
- cross-module refactor with unclear validation
- user explicitly requests frontier or high-confidence completion
- reviewer or validator finds a high-severity issue

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

Medium is the default. High requires recorded evidence that medium reasoning was inadequate for the same bounded question. Xhigh, max, and ultra require an explicit user request plus support on the current runtime. Do not infer a GPT-6 Sol, Luna, or Terra substitute from a family label or an economics table.

## T3/T4 Hard Routing Enforcement

For T3/T4, the route is not executed until required roles have real execution evidence.

1. Perform Execution Context Discovery. Record whether the current surface exposes subagent, thread, or model-override execution; visible roles; expected route; and route-blocked decision. If tools are not visible, use `tool_search` before returning `route_blocked`.
2. Start or update a route ledger from `codex-home/templates/route-ledger.md`.
3. Run Reuse Gate before any child spawn: check `parent_route_id + role + scope_key + acceptance_matrix_id + batch_id`.
4. Run `explorer`, `worker_frontier`, `planner_frontier`, `reviewer_risk`, and `reviewer_final` in separate contexts when the tier requires them.
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
- T2/T3 default child budget is three when children are actually needed.
- The same role may appear at most once for the same scope unless the scope or acceptance matrix expands.
- Budget expansion requires a packet naming the requested expansion, current children, why reuse is unsafe, expected extra value, and stop condition.
- Placeholder, mistaken, or wrong-scope children are recorded as `ignored` / `pollution`.

## Single-Writer Discipline

Only one writer may be active on the same write scope unless the user explicitly asks for parallel implementation. The main agent may prepare non-conflicting validation or acceptance criteria while waiting, but should not race a healthy child writer.

Replacing a writer is allowed only when it failed, blocked, timed out, was abandoned or closed, produced unavailable or unusable output, or the user explicitly requested degraded main-thread execution. Before replacement, record the old writer status and a replacement packet.

Main-session substitution is narrower than replacement. It is allowed only after `blocked`, `timeout`, `closed_with_unusable_output`, or explicit user-degraded execution, and it must record original worker id, blocking reason, reusable output, main-session write scope, validation commands, and reviewer closure plan.

## Reviewer Stickiness

The reviewer that raised a material issue should close it when possible. For the same `acceptance_matrix_id`, use the same reviewer for closure unless it is blocked, unavailable, timed out, polluted, or the acceptance matrix changed.

More than one reviewer for the same acceptance matrix needs a recorded reason or budget-expansion packet. If the original reviewer cannot rerun, the final note must name the substitute validation or review evidence.

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

Add risk for:

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

Force at least T3 for security, permissions, payments, privacy, irreversible data changes, public compatibility, or failed low-tier attempts with unclear root cause.

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
- Each milestone uses `codex-home/templates/t4-milestone-packet.md`.
- Default milestone implementation uses `worker_frontier`.
- Low-risk mechanical batch subtasks may use `batch_worker` only after Luna availability is confirmed and the fallback is recorded.
- Each milestone gets focused validation and `reviewer_risk`.
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

User-approved empirical matching: Terra medium -> Luna high (score 47, consumption 17 -> 5); Terra high -> Luna xhigh (50, 40 -> 10); Sol high -> Astra low (57, 80 -> 60); Sol xhigh -> Astra medium (59, 130 -> 110). These unverified user estimates are not official prices or guaranteed task equivalence. Policy assumption: image Sol/Terra/Luna map to existing gpt-5.6 identifiers; Astra maps to gpt-6-astra. Root remains Sol medium and batch remains Luna low.

Compare registered effective model/effort against controls before invocation. Stale or missing registrations require a default child with explicit mapped model/effort, bounded fork/context, full role instructions, ownership and acceptance criteria. Verify exact model/effort availability. Record actual read-only enforcement as sandbox or prompt_only; prompt-only is not hard isolation. Return route_blocked if required isolation is unavailable. Preserve independent roles, single writer and validation before review.

Luna explorer/worker_standard require availability and suitability checks. Pinned fallback profiles are explorer-terra-fallback (Terra medium read-only) and worker-terra-fallback (Terra high workspace-write). Batch considers worker_standard then its pinned fallback. Record reason and selected fallback before invocation; no hidden rerouting. Capacity cannot automatically raise Astra effort. Astra high requires documented medium reasoning inadequacy; Astra xhigh/max/ultra require explicit user request and runtime support. Only reasoning_specialist requires the exceptional gate; ordinary approved Astra low/medium roles do not.
