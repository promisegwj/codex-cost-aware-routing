---
name: codex-workflow
description: Use for coding, debugging, code review, log triage, architecture planning, and routing-policy work when you want cost-aware semantic roles, routine Astra low/medium roles and a separately gated specialist, single-writer execution, validation-before-review, bounded delegation, and failure-packet escalation.
---

# Codex Workflow

Use this skill when the task involves coding, debugging, review, logs, migrations, or planning and reliable completion matters. The active policy uses semantic roles whose model and effort mapping lives in `codex-home/routing-controls.toml`.

Root default comes from `codex-home/config-routing-snippet.toml`: `gpt-5.6-sol / medium`. Do not silently turn the root thread into xhigh. Luna xhigh is approved for worker_standard. Astra high needs medium inadequacy evidence; Astra xhigh/max/ultra need explicit user request.

## Core Rules

1. Prefer deterministic routing before any extra exploration.
2. T0/T1 default to root-thread implementation and do not automatically create child contexts.
3. T2 is managed and conditional: use compact evidence, optional children, and deterministic frontier capability escalation.
4. T3/T4 are explicit hard routes: required roles must run in separate execution contexts or the route stops as `route_blocked`.
5. Use at most one active writing worker per write scope unless the user explicitly asks for parallel implementation.
6. Validate first, then review when the tier calls for it.
7. Run a Reuse Gate before every child spawn; prefer sending narrow rework or reviewer closure to an existing matching child.
8. Keep Spawn Budget, Reviewer Stickiness, and Explorer Fanout Cap active.
9. Treat model capacity or availability errors as runtime constraints, not task failures.
10. Escalate with a failure packet instead of blind retries.
11. Voice/TTS broadcast failures are sidecar failures; they do not change task, route, validation, or reviewer status.
12. Routine Astra low/medium roles are approved. Only reasoning_specialist requires the exceptional gate and never replaces the writer.

## Active Semantic Roles

The authoritative role matrix is in `[model_roles]` inside `routing-controls.toml`.

| Role | Model / Effort | Use |
|---|---|---|
| `root_direct` | `gpt-5.6-sol / medium` | Default root thread for T0/T1 and orchestration |
| `batch_worker` | `gpt-5.6-luna / low` | Availability-gated mechanical batch work only |
| `explorer` | `gpt-5.6-luna / high` | Read-only discovery and validation focus |
| `worker_standard` | `gpt-5.6-luna / xhigh` | Default managed T2 writer |
| `worker_frontier` | `gpt-6-astra / low` | T2 能力升级 escalation, T3 writer, T4 milestone writer |
| `reviewer_risk` | `gpt-6-astra / low` | T2 escalation review, T3 review, T4 milestone review |
| `planner_frontier` | `gpt-6-astra / medium` | T4 planning and migration specs |
| `reviewer_final` | `gpt-6-astra / medium` | Final T4 cross-milestone review |
| `reasoning_specialist` | `gpt-6-astra / medium` | Read-only, bounded exceptional reasoning after the GPT-6 gate passes |

Legacy 5.4/5.5 files such as `scout_mini`, `worker_55_high`, `planner_55_xhigh`, and `reviewer_55` are transition-only compatibility files. Do not use them in new active defaults.

## Tier Mapping

### T0

Use for typos, imports, tiny config edits, and single-file localized fixes.

```text
root_direct -> focused validation -> return
```

### T1

Use for local bugfixes and small features with clear scope and low risk.

```text
root_direct -> focused validation -> return
```

Do not spawn a reviewer by default. If the T1 diff exposes unexpected risk, re-score the task as T2/T3 instead of bolting on heavy review informally.

### T2

Use for medium complexity, unclear scope, high-value configuration/routing work, or small multi-file changes.

```text
managed conditional:
root_direct decision -> optional explorer -> worker_standard -> validation -> optional reviewer_risk
```

T2 compact evidence must record route decision, spawned child ids if any, model/effort source, validation result, and why frontier capability escalation was or was not triggered.

Escalate T2 to `worker_frontier` (`gpt-6-astra / low`) when any deterministic trigger applies:

- security, auth, permissions, payments, privacy, or encryption
- data loss, data consistency, or migration risk
- public API, schema, contract, or backward compatibility risk
- a lower-tier attempt failed or blocked with unclear root cause
- cross-module refactor with unclear validation
- user explicitly requests frontier or high-confidence completion
- reviewer or validator finds a high-severity issue

### T3

Use for high-risk implementation.

```text
explorer -> worker_frontier -> focused validation -> reviewer_risk
```

T3 is a hard route. If separate execution contexts or required model overrides are unavailable after tool discovery, return `route_blocked`.

### T4

Use for architecture, migrations, and multi-milestone work.

```text
planner_frontier -> spec approval -> per-milestone packet -> staged worker_frontier execution -> reviewer_risk -> reviewer_final
```

Each milestone should use `codex-home/templates/t4-milestone-packet.md`. Final closure uses `reviewer_final`.

## Exceptional GPT-6 Reasoning Gate

This gate applies only to reasoning_specialist. Approved routine Astra low/medium roles need no exceptional gate; tier, risk, confidence, or capacity alone do not trigger the specialist.

Use `reasoning_specialist` only for one bounded read-only reasoning or planning subproblem and only when one of these paths is evidenced:

1. The subproblem has explicit ultra-hard coupling or genuinely novel reasoning, and the route record explains why the current assigned route is insufficient.
2. A completed failure packet demonstrates that the assigned route attempt failed because of a reasoning limit, rather than a tool, environment, permission, context, or model-capacity problem.

Keep the assigned writer. The specialist returns a handoff; the existing writer implements and validates it. Default to `gpt-6-astra / medium`. Use high only after documented medium-effort inadequacy. Use xhigh, max, or ultra only when the user explicitly requests that effort and the current runtime supports it.

Prefer the registered `reasoning_specialist` role. If that role is not registered on the current surface, and only after the gate passes, a `default` child may use explicit `model=gpt-6-astra`, `reasoning_effort=medium`, and a bounded prompt or limited fork containing only the relevant subproblem. Inspect and record the execution context's actual write restriction. The fallback prompt must explicitly say read-only, make no file changes, do not implement, and return a specialist handoff to the existing writer, but prompt-only enforcement is not a hard sandbox guarantee. Record `read_only_enforcement=sandbox` or `prompt_only` in the ledger. If the subproblem requires enforced read-only isolation and no read-only sandbox is available, return `route_blocked`. Missing role registration is not permission to broaden context. Check model and effort availability explicitly; unavailability does not bypass the gate, justify a different GPT-6 route, or count as assigned-route reasoning failure.

## Hard Routing Gate

For T3/T4, the route is not considered executed until the required roles have real execution evidence.

1. Perform Execution Context Discovery. Record whether the current surface exposes subagent, thread, or model-override execution; which route roles are available; the expected route; and whether the route can proceed. If tools are not visible, use `tool_search` before deciding the route is blocked.
2. Start or update the route ledger from `codex-home/templates/route-ledger.md`.
3. Before any spawn, apply the Reuse Gate against `parent_route_id + role + scope_key + acceptance_matrix_id + batch_id`.
4. Run required explorer, worker, planner, and reviewer roles in separate execution contexts.
5. Route evidence must identify child id, parent id when visible, thread source, evidence source, agent role, status, and adoption reason. If model or effort comes from role configuration, mark it `routing-controls model_roles mapping`.
6. Do not treat Goal mode, continuation prompts, or handoff packages as hard routing evidence.
7. Do not replace a writer unless it failed, blocked, timed out, was abandoned, or produced unavailable or unusable output. Record a replacement packet first.
8. The main agent may write implementation directly only after a valid main-session substitution reason or explicit user-degraded execution request.

## T2 Managed Route

T2 does not require a full hard-route ledger by default, but it does require compact evidence. If T2 creates child contexts, record each child id, role, model/effort source, status, output summary, and adoption reason. If T2 escalates to frontier capability, state which deterministic trigger fired.

If the task becomes T3/T4-shaped during implementation, stop and re-route through the hard routing gate.

## Model Capacity Fallback

If Codex reports `Selected model is at capacity. Please try a different model.` or an equivalent selected-model availability error:

1. Do not count it as a code failure.
2. Record it as `model_capacity`.
3. Switch to the closest safe available model/profile by both cost and capability.
4. Do not assume `batch_worker` is available; Luna requires an availability gate and a configured fallback, normally `worker_standard`.
5. For high-risk work, do not silently downgrade implementation quality. Use a safe higher-capability route, planning-only fallback, or pause for user choice when needed.
6. Capacity does not trigger the specialist or automatic Astra effort increases; ordinary approved Astra low/medium roles remain governed by the role matrix.

## Risk Cues

Add risk for:

- auth, security, permissions, payments, encryption: `+3`
- migrations, data deletion, data consistency: `+3`
- public API, schema, contract: `+2`
- root cause unknown: `+2`
- a lower-tier worker already failed: `+2`
- more than 5 files likely change: `+1`
- no clear validation path: `+1`
- vague request: `+1`
- frontend + backend coupling: `+1`
- cache, concurrency, async jobs: `+1`
- cross-module refactor: `+1`

Force at least T3 for security, permissions, payments, privacy, irreversible data changes, public compatibility, or failed lower-tier attempts with unclear root cause.

## User-Specific Routing Overlay

1. APDL, MAPDL, engineering simulation, build-only logs, validation matrices, rail/track/damping/floating-slab work: default to at least T2 and escalate when validation or generated outputs are uncertain.
2. Environment, Codex config, plugins, tool routing, executable paths, global settings: default to T2 when editing shared config. Verify with path existence, CLI/profile loading, dry-run sync, or a small smoke command.
3. Voice automation and TTS reply behavior: treat as script/config work in the Voice project. Do not move voice helper ownership into this routing project.
4. Git, GitHub, release, sync, commit, push: start read-only with branch/status/diff/remote awareness. Commit or push only when explicitly asked.
5. UI, browser, Chrome, localhost, frontend layout, 3D preview: require browser or screenshot verification for meaningful UI changes.
6. Review words such as `评审`, `复核`, `审查`, `检查`, `方案`, and `规划` normally mean read-only reviewer/planner mode until the user asks for implementation.
7. Consecutive step projects such as `step1`, `step2`, `继续推进`, and `下一轮` should end with a continuation packet.
8. Formal documents, papers, Word, PDF, LaTeX, Zotero, slides, or spreadsheets should route to the relevant document/data skill and include render/compile/visual QA when layout matters.

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

## Failure Packet

Use this exact shape after a failed worker attempt:

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

## Effective Mapping And Economic Assumptions

User-approved empirical matching: Terra medium -> Luna high (score 47, consumption 17 -> 5); Terra high -> Luna xhigh (50, 40 -> 10); Sol high -> Astra low (57, 80 -> 60); Sol xhigh -> Astra medium (59, 130 -> 110). These unverified user estimates are not official prices or guaranteed task equivalence. Policy assumption: image Sol/Terra/Luna map to existing gpt-5.6 identifiers; Astra maps to gpt-6-astra. Root remains Sol medium and batch remains Luna low.

Compare registered effective model/effort against controls before invocation. Stale or missing registrations require a default child with explicit mapped model/effort, bounded fork/context, full role instructions, ownership and acceptance criteria. Verify exact model/effort availability. Record actual read-only enforcement as sandbox or prompt_only; prompt-only is not hard isolation. Return route_blocked if required isolation is unavailable. Preserve independent roles, single writer and validation before review.

Luna explorer/worker_standard require availability and suitability checks. Pinned fallback profiles are explorer-terra-fallback (Terra medium read-only) and worker-terra-fallback (Terra high workspace-write). Batch considers worker_standard then its pinned fallback. Record reason and selected fallback before invocation; no hidden rerouting. Capacity cannot automatically raise Astra effort. Astra high requires documented medium reasoning inadequacy; Astra xhigh/max/ultra require explicit user request and runtime support. Only reasoning_specialist requires the exceptional gate; ordinary approved Astra low/medium roles do not.
