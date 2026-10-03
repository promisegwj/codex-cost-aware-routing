# AGENTS.md

1. This folder is the source project for the Codex cost-aware model-routing workflow. Treat files here as the maintainable source of truth, not as throwaway notes from a single conversation.
2. For coding, debugging, review, log triage, migration, or architecture-planning work in this project, use the local `codex-home/skills/codex-workflow/SKILL.md` logic first: deterministic risk scoring, semantic economic roles, root-thread T0/T1, managed/conditional T2, hard-routed T3/T4, one writing worker by default, validate before review, and failure-packet escalation after a failed attempt.
3. Keep generated or deployable Codex assets under `codex-home/`: agents, skill files, profile configs, and config snippets. Keep human context under `WORK_MEMORY.md` and `docs/`.
4. Do not store secrets, tokens, account credentials, private keys, or machine-local auth material in this project. Config templates may include paths, model names, roles, and workflow rules only.
5. When changing routing behavior, update both the runnable skill/template files and the work memory that explains why the rule exists. This prevents global Codex behavior from drifting away from the project record.
6. Voice reply behavior is owned by `E:\CodexWorkSpace\voice自动读取讲解回复内容`. This project may reference that history, but it should not become the place where TTS helper scripts or voice profiles are maintained.
7. Follow routing-controls.toml: GPT-6 Luna low discovery, medium root and high bounded T2; GPT-6.1 Sol medium integrated work/review/planning and evidenced high effort; Astra low/medium frontier routes, high only after medium inadequacy. Keep tier, model and effort separate; classify failures and enforce transition/attempt budgets. Only reasoning_specialist has the exceptional gate.
