# Model routing evidence: GPT-5.4 through GPT-6

Historical benchmark/context snapshot reviewed 2026-10-03; model lanes and proposed defaults below are historical, superseded by the 2026-10-07 controls. This is a routing aid, not a universal ranking. Public API token rates do not describe Codex subscription credit consumption.

## Evidence and limits

- Artificial Analysis (AA) is an independent benchmark provider. Its Intelligence Index blends multiple reasoning, knowledge, coding, and agentic evaluations; its per-task costs are computed from its own benchmark token usage and public API rates. Values below are not the cost of a Codex session.
- Vals AI independently measures end-to-end agent tasks across coding, finance, legal, and other domains. Its model pages report test cost and scores; many runs use maximum reasoning effort, so do not assume identical results at low or medium effort.
- Neither index proves performance on this user's repositories. A local small evaluation of representative tasks remains the strongest way to tune effort thresholds.

## Capability evidence

| Family / model | Independent observations | Practical lane |
|---|---|---|
| GPT-5.4 | AA estimated xhigh Index 39; strong broad reasoning baseline. | Legacy, not preferred for new role assignment. |
| GPT-5.4 mini / nano | AA xhigh comparison: Intelligence Index 24 vs 21; weighted AA task cost $0.45 vs $0.18, with nano weaker on AutomationBench (6% vs 26%) and Terminal-Bench 4.0 (1% vs 2%). | Good cheap batch subagents for simple tasks, not autonomous complex implementation; not present in this Codex model registry. |
| GPT-5.5 | AA xhigh Index 38 and about $2.63 per AA Index task; AA marks it deprecated for ongoing broad benchmarking and recommends newer models. | Avoid as default; retain only for explicit compatibility needs. |
| GPT-5.6 Luna | AA max Index 37; Luna is on the low-cost Pareto frontier. | Routine low-risk edits, extraction, discovery, and bounded implementation. |
| GPT-5.6 Terra | AA max Index 42; AA's release comparison reports Luna and Sol dominate Terra on its intelligence/cost frontier. | Do not make a default; can remain an explicitly pinned older fallback. |
| GPT-5.6 Sol | AA's launch evaluation put Sol max at Index 59 and Coding Agent Index 80; later index versions rebase scores, so do not compare across versions. | Strong complex implementation and code review; costs more than Luna. |
| GPT-6 Luna | Vals Index 58.45%, $0.42/test (#20/65 at the Sep. 22 report); Terminal-Bench 2.1 73.03%, but Terminal-Bench 4.0 9.60% and difficult agentic/science tasks were weak. AA Luna high scored 32 vs Sol high 43, with AA estimated cost/task $0.03 vs $0.37. | Excellent cost-efficiency for routine work; avoid assigning hardest long-horizon or high-consequence tasks directly. |
| GPT-6 Sol | Vals Index 62.57%, $7.56/test (Sep. 22; score #8/65 in its narrative, current page rank differs); Terminal-Bench 4.0 34.34%, Terminal-Bench 2.1 83.15%, Code Migration 57.20%. AA reports high score 43 and medium 40. | Previous middle lane; retain as historical evidence only, not an active default. |
| GPT-6.1 Sol | OpenAI describes near-Astra performance for complex coding and professional work at lower cost; officially listed at $2/$10 per 1M input/output tokens, one-fifth Astra's standard token rates. Supports low/medium/high/xhigh/max reasoning. | Preferred intermediate model for multi-module T2 implementation, T2 risk review, and T4 planning; use medium by default, preserve Astra for critical-risk and hard T3/T4 roles. |
| GPT-6 Astra | Vals Index 66.61%, $19.09/test; Terminal-Bench 4.0 57.07%, Code Migration 67.74%, leading results in multiple hardest tasks. AA low 46, medium 50. | Reserve for hard, high-impact, uncertain, or high-consequence tasks; low effort first. |

Vals score/rank snapshots evolve as more models are evaluated. Vals's GPT-6 Luna and Sol runs used max reasoning effort; the shared benchmark method makes relative capability useful, but their measured costs are not typical Codex usage. AA v4.3.2 scores also must not be mixed with older v4.1/v4.3 scores.

## Public API price proxy (USD per 1M input / output tokens)

These are public direct-API rates, not Codex credits. Cached input may be much cheaper; reasoning tokens count as output. Exact rates can change.

| Model | Input / output | Notes |
|---|---:|---|
| GPT-5.4 | $2.50 / $15 | Flagship at release |
| GPT-5.4 Pro | $30 / $180 | Much higher cost; not in the current Codex registry |
| GPT-5.4 mini | $0.75 / $4.50 | Efficient coding / agents |
| GPT-5.4 nano | $0.20 / $1.25 | Simple high-volume work |
| GPT-5.5 | $5 / $30 | AA xhigh Index 38, $2.63/AA task; costly and superseded in AA guidance |
| GPT-5.5 Pro | $30 / $180 | Premium long reasoning; not in the current Codex registry |
| GPT-5.6 Sol | $4 / $20 | Promotional price through at least 2026-11-21 |
| GPT-5.6 Terra | $2 / $12 | Balanced tier |
| GPT-5.6 Luna | $0.20 / $1.20 | Cost-sensitive tier |
| GPT-6 Luna | $0.10 / $0.50 | Lowest-cost GPT-6 tier |
| GPT-6 Sol | $2 / $10 | Previous middle-tier model; no longer assigned to active semantic roles |
| GPT-6.1 Sol | $2 / $10 | Near-Astra complex work at one-fifth Astra standard token rates; active intermediate tier |
| GPT-6 Astra | $10 / $50 | Highest capability, highest token rate |

## Adopted role mapping

- Root default: GPT-6 Luna medium for T0/T1 and initial routing; this is a low-cost baseline, not a claim that Luna can handle every task.
- Routine T2 writer: GPT-6 Luna high for bounded changes with clear acceptance and validation.
- Intermediate T2 writer/reviewer and T4 planner: GPT-6.1 Sol medium for multi-module or reasoning-heavy work and independent T2 review.
- Frontier implementation/review: GPT-6 Astra low only on the policy's deterministic high-risk triggers or T3/T4 route.
- GPT-6 Astra medium is retained for final T4 review and a separately gated bounded reasoning specialist; high/xhigh/max require the documented evidence and runtime/user constraints already in routing-controls.toml.
- Escalate on capability need, not merely file count. Do not invoke multiple roles if the work can be completed reliably in the current context.

## Sources

- OpenAI official GPT-6.1 Sol model page, model catalog, and GPT-6.1 Sol addendum: https://developers.openai.com/api/docs/models/gpt-6.1-sol ; https://developers.openai.com/api/docs/models ; https://deploymentsafety.openai.com/gpt-6-1-sol/respecting-auto-review

- Artificial Analysis GPT-5.4, GPT-5.5, GPT-5.6 comparisons: https://artificialanalysis.ai/models/releases/gpt-5-4 ; https://artificialanalysis.ai/models/comparisons/gpt-5-4-mini-vs-gpt-5-4-nano ; https://artificialanalysis.ai/models/gpt-5-5 ; https://artificialanalysis.ai/articles/gpt-5-6-has-landed ; https://artificialanalysis.ai/articles/gpt-5-6-intelligence-vs-cost-across-sol-terra-luna
- Artificial Analysis GPT-6 Sol/Astra and Luna-vs-Sol: https://artificialanalysis.ai/models/releases/gpt-6-sol ; https://artificialanalysis.ai/models/releases/gpt-6-astra ; https://artificialanalysis.ai/models/comparisons/gpt-6-luna-high-vs-gpt-6-sol-high
- Vals AI GPT-6 Luna/Sol/Astra: https://www.vals.ai/models/openai_gpt-6-luna ; https://www.vals.ai/models/openai_gpt-6-sol ; https://www.vals.ai/models/openai_gpt-6-astra
- OpenAI public API prices used only as the token-rate proxy: https://developers.openai.com/api/docs/pricing ; GPT-5.4 Pro / GPT-5.5 Pro rates: https://developers.openai.com/api/docs/models/gpt-5.4-pro ; https://developers.openai.com/api/docs/models/gpt-5.5-pro

## Two-axis policy adoption (2026-10-03)

Use `two-axis-routing.md` and routing-controls.toml for the active model/effort transition and budget policy. Sol medium is the integrated-work baseline; high requires named dense reasoning or a demonstrated effort limit. Astra low remains a frontier baseline, with medium selected for evidenced dense/coupled reasoning. Do not use historical scores above to claim Sol high beats Astra low or that equal effort labels imply equal compute. The policy's two-transition, three-writer-attempt and five-observation thresholds are local heuristics, not published benchmark results.
