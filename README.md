# Codex Cost-Aware Routing

按任务复杂度、后果和推理投入选择 Codex 模型与代理。当前策略：`2026-10-03-two-axis-v1`。

这是 Codex 读取执行的工作流规则与配置集合。选择器提供只读建议；真正派发由主代理执行，需检查实际模型绑定、可用性和隔离能力。

## 当前模型与档位

| 模型 | 正常路由覆盖的推理档位 | 主要职责 |
|---|---|---|
| GPT-6 Luna | low / medium / high | 发现、简单根线程任务、边界清楚的 T2 |
| GPT-6.1 Sol | medium / high | 复杂 T2 实施、独立 T2 审查、T4 规划；有证据时提高推理投入 |
| GPT-6 Astra | low / medium / high | 高后果工作、T3/T4 实施审查、能力升级、最终审查；high 要求 medium 不足证据 |
| GPT-5.6 Terra | medium / high（备用） | Luna 不可用且适合任务时的发现或实施回退 |

xhigh/max/ultra 不属于自动选择配置，要求用户明确提出和实际运行时支持。公开 API 价格不能推断 Codex 订阅消耗。

## 路由与调整

- T0/T1 主线程直接完成；T2 按范围和验证需要条件委派；T3/T4 保留独立角色、单一写入者、验证后审查。
- 普通复杂工作以 Sol/medium 起步。任务已理解而推导投入不足时，可走 Sol medium → high → Astra medium。
- 持续理解或能力不足时，按证据直接换模型，不必逐档尝试。
- 资料、指令、工具、环境、容量和已定位普通缺陷先处理原因，不自动增加推理投入。
- 每个验收范围最多两次自动配置转换、三次写入尝试。观察五次可比成功后，可在后续任务试低一档，验收退化则恢复。

这些阈值是本地策略，不是已完成的模型成本或性能实测。

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

本机运行文件在 Codex 用户目录，当前电脑为 `C:/Users/ZengS/.codex`。本机变更后，导出受管理文件并检查差异：

```powershell
.\scripts\export-routing.ps1
git diff
```

导出按 `routing-files.txt` 的 21 项清单复制，并提取根模型默认值。它不导出完整全局配置、认证信息、会话和缓存。Git 提交不会自动部署。

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
.\scripts\test-routing-policy.ps1 -PythonPath 'C:\absolute\python.exe'
```

检查角色、八个自动配置、回退及原生 profile 的一致性，并运行路由场景检查。检查器不调用模型，不确认账户的模型容量或权限。

## 历史与公开范围

保留原仓库的历史角色、经济性资料和分析工具，不将它们作为当前默认模型路线。`WORK_MEMORY.md`、对话、认证、日志及缓存不提交。历史费用估算不能代表当前 Codex 账单。
