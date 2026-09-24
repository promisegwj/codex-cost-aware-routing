# AGENTS.md

1. 如果问题无法通过思考、查资料或现有工具可靠解决，直接说明卡点、风险和希望我提供的帮助，不要编造结果。
2. 在所有会加载这份全局 `AGENTS.md` 的 Codex 对话里，正式回复如需语音摘要，应先触发播报，再继续发送文字版回复；不需要等待播报结束后才开始输出文字。
3. 语音摘要默认采用“总分总”：先一句结论，再讲 2 到 4 个关键依据、完成项或注意点，最后一句收束下一步；内容更像口头汇报，不要主要朗读调试过程。
4. 默认使用 A3-v3：`zh-CN-XiaoxiaoNeural`，语速 `+7%`，音高 `-1Hz`。如果当前调用方不是 PowerShell 本身，优先命令是 `powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -InputFormat None -File "E:\CodexWorkSpace\voice自动读取讲解回复内容\say-neural.ps1" -Voice "zh-CN-XiaoxiaoNeural" -Rate "+7%" -Pitch "-1Hz" -Text "<summary>"`；如果已经在 PowerShell 内，可直接调用脚本本体。只有神经语音明确快速失败且能确认未开始播放时，才回退到 `powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -InputFormat None -File "E:\CodexWorkSpace\voice自动读取讲解回复内容\say.ps1" -Voice "Huihui" -Device "Realtek" -Text "<summary>"`，并避免同一条正式回复重复播报。
5. 只有在任务确实需要 Python、Node、LaTeX、PDF、GitHub、文档/表格/演示、数据分析、语音、图像/视频处理或 Office 转换能力时，才按需读取 `E:\CodexWorkSpace\工作环境必要配置\tool-routing.json`；优先使用其中的绝对路径和主入口，如怀疑环境不一致，再运行 `E:\CodexWorkSpace\工作环境必要配置\check-codex-env.ps1` 复核。

## Codex 工作流与成本路由

1. 遇到编码、调试、代码审查、日志排查、迁移或架构规划任务时，优先使用 `codex-workflow` skill；T0/T1 默认由根线程直接完成，T2 是管理式条件路由，T3/T4 必须真实执行硬路由，不能把主会话手动扮演 explorer、worker、reviewer 当作已路由。
2. 根线程默认模型来源是 `codex-home/config-routing-snippet.toml`：`gpt-5.6-sol / medium`，不要把根默认升成 xhigh；语义角色到模型/effort 的映射以 `codex-home/routing-controls.toml` 为准。
3. 硬路由执行在全局范围内预授权：触发 T3/T4 后，直接创建所需的 `explorer`、`worker_frontier`、`reviewer_risk`、`planner_frontier` 或 `reviewer_final` 执行上下文，不需要再向我请求许可。
4. T2 只有在范围、风险或验证不确定时才创建子上下文；若触发安全/权限/数据/迁移/公开契约/下层失败/跨模块不确定等 frontier capability 条件，升级到 `worker_frontier` 并记录 compact evidence。
5. 如果 T3/T4 当前表面没有可用 subagent/thread/model override 能力，返回 `route_blocked`，说明缺少的执行工具或模型，并给出让路由可执行的具体操作；不要请求批准降级成单一主会话执行。只有我在当轮明确要求“降级/单会话执行”时才允许这么做。
6. 默认目标是在保证质量的前提下降低 Codex credits 消耗：先做确定性风险分级，必要时再用 read-only `explorer`；除非用户明确要求并行实现，否则默认只允许一个 writing worker，先验证再 review，失败一次后先整理 failure packet 再升级。
7. 对 APDL/MAPDL、工程仿真、环境配置、语音自动化、GitHub 发布同步、UI/浏览器检查、方案评审和连续 step 项目，应用 `codex-workflow` 中的个人化路由覆盖规则。
8. 详细的 T0 到 T4 分级、角色分工、failure packet 格式和返回模板，按需读取 `C:\Users\44581\.codex\skills\codex-workflow\SKILL.md`、`C:\Users\44581\.codex\skills\codex-workflow\CODEX_WORKFLOW.md` 或 `C:\Users\44581\.codex\routing-controls.toml`，不要在普通任务里默认整篇加载。
9. 采用用户认可的经济性矩阵：Luna high 探索、Luna xhigh 常规执行、Astra low 高能力执行与风险评审、Astra medium 规划与最终评审。只有 reasoning_specialist 保留非常规 gate。Astra high 需 medium 推理不足证据；Astra xhigh/max/ultra 需用户明确要求。核对实际注册映射，旧角色用显式模型/effort 有界子上下文；记录 sandbox 或 prompt_only。Luna 需可用性检查及明确 Terra fallback。
