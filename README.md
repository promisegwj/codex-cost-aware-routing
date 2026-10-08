# Codex Cost-Aware Routing

按任务复杂度、后果和推理投入选择 Codex 模型与代理。当前策略：`2026-10-07-sol-default-astra-high-boundaries-v2`。

这是 Codex 读取执行的工作流规则与配置集合。选择器提供只读建议；真正派发由主代理执行，需检查实际模型绑定、可用性和隔离能力。

## 当前模型与流程

默认 GPT-6.1 Sol/low；常规工作使用 Sol low 及以上，集成或多步推理使用 medium，有证据的密集推导使用 high。Luna 只保留 medium，用于有明确证据的特别简单、规则完全确定、无需实质思考的执行。

每个 T0–T4 任务都由独立 Astra/high 起的初始规划与最终审核把关，包括纯执行任务。规划、实施和最终审核保持独立；这些边界角色不强制升为 T4。最终审核在适当验证之后执行。T3/T4 保留中间风险或阶段审查。

三子代理预算覆盖规划、单一实施者、最终审核。可选发现代理需记录预算扩展；T3 必需的第四个中间风险审查上下文也须记录扩展。已有用户授权足以按计划实施，无需重复批准。

实施/专家 Astra high 仍需 medium 不足证据；独立专家门槛不变。缺少必需 Astra/high 或隔离能力则 route_blocked。七个自动模型/档位组合为 Luna medium、Sol low/medium/high、Astra low/medium/high；历史 Terra 文件不再自动回退。

失败先分类和修复原因，每个验收范围最多两次自动转换、三次写入尝试。后续调低档位不可低于 Sol/low 和边界 Astra/high，也不可绕过 Luna 执行资格。xhigh/max/ultra 需要明确要求和运行时支持。这些规则是本地策略，质量收益仍需真实任务观察，公开 API 价格不代表订阅消耗。

## 文档与文件

- [直白说明与完整例子](模型档位与路由方法说明.md)
- [实施记录](路由方案实施记录.md)
- [权威策略](codex-home/routing-controls.toml)
- [技能入口](codex-home/skills/codex-workflow/SKILL.md)
- [模型与档位选择说明](codex-home/skills/codex-workflow/references/two-axis-routing.md)
- `codex-home/agents/`：角色默认配置；旧角色仅供历史兼容。
- `codex-home/profiles/`：原生配置片段和明确的回退。
- `codex-home/templates/`：路由和阶段交接模板。
- `scripts/`：导出、同步、验证及历史经济性分析工具。

旧流程图和日期固定的经济性材料保留为历史参考；它们的模型标签不能替代当前策略。

## Git 管理与本机同步

仓库保留 `promisegwj/codex-cost-aware-routing` 原有提交历史，部署文件继续位于 `codex-home/`。

本机运行文件在 Codex 用户目录，使用 `$CODEX_HOME`（未设置时为 `$USERPROFILE/.codex`）。本机变更后，导出受管理文件并检查差异：

```powershell
.\scripts\export-routing.ps1
git diff
```

导出按 `routing-files.txt` 的 27 项清单复制，并提取根模型默认值。它不导出完整全局配置、认证信息、会话和缓存。Git 提交不会自动部署。

部署前备份目标同名文件；先预览：

```powershell
.\scripts\sync-to-codex-home.ps1 -CodexHome "$env:USERPROFILE\.codex" -WhatIf
```

实际同步：

```powershell
.\scripts\sync-to-codex-home.ps1 -CodexHome "$env:USERPROFILE\.codex"
```

同步会覆盖管理范围内的路由文件，合并全局 AGENTS 中的 managed 路由段，保留其他指令；profile 复制到目标 `profiles/`。它不会自动备份或合并 `config.toml`。只把 `codex-home/config-routing-snippet.toml` 的两个键按需合并到已有全局配置，并按实际需要保留代理启用与线程上限设置。详细路由自定义键不能放进 `config.toml`。

## 验证

需要 Python 3.11+，不再依赖原作者 E 盘的工具路径。当前电脑默认使用应用提供的 Python：

```powershell
.\scripts\test-routing-policy.ps1
```

其他环境指定解释器：

```powershell
.\scripts\test-routing-policy.ps1 -PythonPath '<python-executable>'
```

检查角色、七个自动配置、边界下限及原生 profile 的一致性，并运行路由场景检查。检查器不调用模型，不确认账户的模型容量或权限。

## 历史与公开范围

保留原仓库的历史角色、经济性资料和分析工具，不将它们作为当前默认模型路线。`WORK_MEMORY.md`、对话、认证、日志及缓存不提交。历史费用估算不能代表当前 Codex 账单。
