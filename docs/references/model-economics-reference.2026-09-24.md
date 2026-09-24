# User-Provided Model Economics Reference (2026-09-24)

## Status and evidence boundary

This is a transcription of the model-capability image attached by the user on 2026-09-24. The image itself says the Astra data is based on user-feedback experience and that weekly consumption is an experience estimate rather than an official fixed value.

Treat every intelligence and weekly-consumption value below as an **unverified estimate**. These numbers are not official OpenAI prices, bills, quotas, or Codex credits. The user subsequently authorized using equal-score, lower-consumption pairs to update routine role mappings. This does not establish official prices or modify the maintained price book.

The family labels `Astra`, `Sol`, `Terra`, and `Luna` in the image do not specify a model generation. The approved policy explicitly assumes Sol/Terra/Luna correspond to the existing GPT-5.6 identifiers and Astra to gpt-6-astra; this is an operational assumption, not a fact established by the image. In particular, do not infer GPT-6 Sol/Luna/Terra routes from this table.

Official model documentation: <https://developers.openai.com/api/docs/models/gpt-6-astra>. This link confirms the `gpt-6-astra` model identity; actual effort options must still be checked on the current runtime surface.

## Transcribed image values

| Rank | Image label | Approx. intelligence | Estimated weekly consumption | Image evaluation |
|---:|---|---:|---:|---|
| 1 | Astra Ultra | 62 | 320 | 能力上限档 |
| 2 | Astra 极高 | 61 | 230 | 非常烧额度 |
| 3 | Astra 高 | 60 | 170 | 高难任务再开 |
| 4 | Astra 中 | 59 | 110 | Astra 甜点位 |
| 5 | Sol 极高 | 59 | 130 | 追求上限 |
| 6 | Astra 轻度 | 57 | 60 | 新一代日常强者 |
| 7 | Sol 高 | 57 | 80 | 重要任务才开 |
| 8 | Sol 中 | 56 | 45 | 高质量甜点位 |
| 9 | 5.5 极高 | 56 | 260 | 性价比最低 |
| 10 | 5.5 高 | 54 | 160 | 不推荐 |
| 11 | Terra 极高 | 53 | 60 | 开始不划算 |
| 12 | Sol 轻度 | 51 | 25 | 很值得 |
| 13 | 5.5 中 | 51 | 75 | 不推荐 |
| 14 | Luna 极高 | 50 | 10 | 额度性价比之王 |
| 15 | Terra 高 | 50 | 40 | 一般 |
| 16 | Luna 高 | 47 | 5 | 超级甜点位 |
| 17 | Terra 中 | 47 | 17 | 很好 |
| 18 | 5.5 轻度 | 44 | 25 | Sol 更合适 |
| 19 | Terra 轻度 | 41 | 10 | 一般 |
| 20 | Luna 中 | 39 | 1.7 | 极省 |
| 21 | Luna 轻度 | 34 | 1 | 极省，但能力有限 |

## Approved routing use

- Keep `gpt-5.6-sol / medium` as root default and Luna low for mechanical batch work.
- Use Luna high for explorer instead of Terra medium; Luna xhigh for worker_standard instead of Terra high.
- Use Astra low for worker_frontier/reviewer_risk instead of Sol high; Astra medium for planner_frontier/reviewer_final instead of Sol xhigh.
- These routine Astra low/medium roles do not require the exceptional gate. Only reasoning_specialist remains gated, bounded, and read-only.
- Check exact model/effort availability and task suitability. Luna roles have explicitly recorded pinned Terra medium/high fallback profiles; do not silently reroute.
- Verify registered effective mappings before use; stale registrations need explicit model/effort overrides with bounded context and the full role instructions.
- Treat equal table scores as empirical selection guidance, not guaranteed task equivalence. Validate actual outputs.
- Do not edit `docs/pricing/openai-price-book.2026-06-11.json` from these estimates.
