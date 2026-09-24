import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..");
const transcriptsDir = path.join(rootDir, "docs", "transcripts");
const defaultPriceBookPath = path.join(rootDir, "docs", "pricing", "openai-price-book.2026-06-11.json");
const defaultReportPath = path.join(rootDir, "docs", "reports", "routing-economics-pilot.md");

const ROUTES = {
  analysis_scout: {
    label: "Read-only scout",
    phases: ["scout_mini"],
    model_mix: { "gpt-5.4-mini": 1.0 },
    confidence: "medium",
  },
  analysis_review: {
    label: "Scout + reviewer_54",
    phases: ["scout_mini", "reviewer_54"],
    model_mix: { "gpt-5.4-mini": 0.55, "gpt-5.4": 0.45 },
    confidence: "medium",
  },
  t1_worker_54: {
    label: "worker_54",
    phases: ["worker_54"],
    model_mix: { "gpt-5.4": 1.0 },
    confidence: "medium",
  },
  t2_shared_config: {
    label: "scout_mini -> worker_54_high -> reviewer_54",
    phases: ["scout_mini", "worker_54_high", "reviewer_54"],
    model_mix: { "gpt-5.4-mini": 0.2, "gpt-5.4": 0.8 },
    confidence: "medium",
  },
  t3_high_risk: {
    label: "scout_mini -> worker_55_high -> reviewer_55",
    phases: ["scout_mini", "worker_55_high", "reviewer_55"],
    model_mix: { "gpt-5.4-mini": 0.15, "gpt-5.5": 0.85 },
    confidence: "low",
  },
  t4_planner: {
    label: "planner_55 -> worker_55_high -> reviewer_55",
    phases: ["planner_55", "worker_55_high", "reviewer_55"],
    model_mix: { "gpt-5.4-mini": 0.1, "gpt-5.5": 0.9 },
    confidence: "low",
  },
};

const KEYWORDS = {
  strongEdit: [
    "修改",
    "删掉",
    "删除",
    "简化",
    "补全",
    "配置",
    "修复",
    "调整",
    "同步",
    "更改",
    "启动",
    "你来",
    "方案修改",
  ],
  advisory: [
    "看一下",
    "检查",
    "分析",
    "谈一谈",
    "是否",
    "觉得",
    "评审",
    "复核",
    "审查",
    "需要",
    "如何",
    "怎么用",
    "讲讲",
  ],
  planning: ["规划", "方案", "架构", "迁移", "milestone", "设计"],
  sharedConfig: [
    ".codex",
    "agent",
    "agents",
    "config",
    "配置",
    "环境",
    "插件",
    "tool routing",
    "语音",
    "voice",
    "全局",
    "md文档",
    "规则",
    "路由",
  ],
  highRisk: [
    "安全",
    "权限",
    "支付",
    "加密",
    "隐私",
    "数据库",
    "删除数据",
    "迁移数据",
    "兼容",
    "public api",
    "schema",
    "contract",
  ],
};

function containsAny(text, items) {
  const normalized = text.toLowerCase();
  return items.some((item) => normalized.includes(item.toLowerCase()));
}

function classifyTask(text) {
  const normalized = text.replace(/\s+/g, " ").trim();
  const hasStrongEdit = containsAny(normalized, KEYWORDS.strongEdit);
  const hasAdvisory = containsAny(normalized, KEYWORDS.advisory);
  const hasPlanning = containsAny(normalized, KEYWORDS.planning);
  const hasSharedConfig = containsAny(normalized, KEYWORDS.sharedConfig);
  const hasHighRisk = containsAny(normalized, KEYWORDS.highRisk);

  if (hasPlanning && !hasStrongEdit) {
    return {
      tier: "T4",
      routeId: "t4_planner",
      rationale: "Planning or architecture wording detected.",
    };
  }

  if (hasHighRisk) {
    return {
      tier: "T3",
      routeId: "t3_high_risk",
      rationale: "High-risk keywords detected.",
    };
  }

  if (hasAdvisory && !hasStrongEdit) {
    if (hasSharedConfig) {
      return {
        tier: "T2-readonly",
        routeId: "analysis_review",
        rationale: "Read-only inspection of shared config or routing rules.",
      };
    }

    return {
      tier: "T0-readonly",
      routeId: "analysis_scout",
      rationale: "Read-only analysis request.",
    };
  }

  if (hasStrongEdit && hasSharedConfig) {
    return {
      tier: "T2",
      routeId: "t2_shared_config",
      rationale: "Edits touch shared config, routing, agent, or voice rules.",
    };
  }

  if (hasStrongEdit) {
    return {
      tier: "T1",
      routeId: "t1_worker_54",
      rationale: "Localized edit request without strong high-risk cues.",
    };
  }

  return {
    tier: "T2",
    routeId: "analysis_review",
    rationale: "Fallback to moderate read-only analysis route.",
  };
}

function deltaUsage(previous, current) {
  if (!current) {
    return {
      input_tokens: 0,
      cached_input_tokens: 0,
      output_tokens: 0,
      reasoning_output_tokens: 0,
      total_tokens: 0,
    };
  }

  const base = previous || {
    input_tokens: 0,
    cached_input_tokens: 0,
    output_tokens: 0,
    reasoning_output_tokens: 0,
    total_tokens: 0,
  };

  return {
    input_tokens: current.input_tokens - base.input_tokens,
    cached_input_tokens: current.cached_input_tokens - base.cached_input_tokens,
    output_tokens: current.output_tokens - base.output_tokens,
    reasoning_output_tokens: current.reasoning_output_tokens - base.reasoning_output_tokens,
    total_tokens: current.total_tokens - base.total_tokens,
  };
}

function minutesBetween(start, end) {
  if (!start || !end) {
    return null;
  }

  return (new Date(end).getTime() - new Date(start).getTime()) / 60000;
}

function usageBreakdown(usage) {
  const cachedInput = Math.max(0, usage.cached_input_tokens);
  const totalInput = Math.max(0, usage.input_tokens);
  const uncachedInput = Math.max(0, totalInput - cachedInput);

  return {
    input_tokens: totalInput,
    uncached_input_tokens: uncachedInput,
    cached_input_tokens: cachedInput,
    output_tokens: Math.max(0, usage.output_tokens),
    reasoning_output_tokens: Math.max(0, usage.reasoning_output_tokens),
    total_tokens: Math.max(0, usage.total_tokens),
  };
}

function costFromUsage(usage, rates, creditsPerUsd) {
  const breakdown = usageBreakdown(usage);
  const usd =
    (breakdown.uncached_input_tokens / 1_000_000) * rates.input +
    (breakdown.cached_input_tokens / 1_000_000) * rates.cached_input +
    (breakdown.output_tokens / 1_000_000) * rates.output;

  return {
    usd,
    credits: usd * creditsPerUsd,
  };
}

function weightedUsageCost(usage, modelMix, modelRates, creditsPerUsd) {
  let usd = 0;
  let credits = 0;

  for (const [modelName, share] of Object.entries(modelMix)) {
    const rates = modelRates[modelName];
    if (!rates) {
      throw new Error(`Missing rates for model ${modelName}`);
    }

    const scaledUsage = {
      input_tokens: usage.input_tokens * share,
      cached_input_tokens: usage.cached_input_tokens * share,
      output_tokens: usage.output_tokens * share,
      reasoning_output_tokens: usage.reasoning_output_tokens * share,
      total_tokens: usage.total_tokens * share,
    };
    const part = costFromUsage(scaledUsage, rates, creditsPerUsd);
    usd += part.usd;
    credits += part.credits;
  }

  return { usd, credits };
}

function formatNumber(value, digits = 2) {
  return Number(value).toFixed(digits);
}

function formatInt(value) {
  return Math.round(value).toLocaleString();
}

function sumMetric(items, selector) {
  return items.reduce((sum, item) => sum + selector(item), 0);
}

function parseArgs(argv) {
  const options = {
    priceBookPath: defaultPriceBookPath,
    priceBookId: "standard_short_context",
    baselineModel: "gpt-5.5",
    writeReport: false,
    reportPath: defaultReportPath,
    json: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === "--price-book-id" && argv[index + 1]) {
      options.priceBookId = argv[index + 1];
      index += 1;
      continue;
    }

    if (arg === "--price-book-path" && argv[index + 1]) {
      options.priceBookPath = path.resolve(argv[index + 1]);
      index += 1;
      continue;
    }

    if (arg === "--baseline-model" && argv[index + 1]) {
      options.baselineModel = argv[index + 1];
      index += 1;
      continue;
    }

    if (arg === "--write-report") {
      options.writeReport = true;
      continue;
    }

    if (arg === "--report-path" && argv[index + 1]) {
      options.reportPath = path.resolve(argv[index + 1]);
      index += 1;
      continue;
    }

    if (arg === "--json") {
      options.json = true;
    }
  }

  return options;
}

async function loadPriceBook(priceBookPath, priceBookId) {
  const raw = await fs.readFile(priceBookPath, "utf8");
  const payload = JSON.parse(raw);
  const selectedBookId = priceBookId || payload.default_price_book;
  const selectedBook = payload.price_books[selectedBookId];

  if (!selectedBook) {
    throw new Error(`Unknown price book: ${selectedBookId}`);
  }

  return {
    meta: payload,
    id: selectedBookId,
    models: selectedBook.models,
    creditsPerUsd: payload.credit_policy.credits_per_usd,
  };
}

async function parseTranscript(filePath, pricing) {
  const content = await fs.readFile(filePath, "utf8");
  const lines = content.split(/\r?\n/).filter(Boolean);
  const userMessages = [];
  const turns = [];
  let latestUsage = null;
  let previousTurnUsage = null;
  let sessionMeta = null;
  let lastTaskTimestamp = null;

  for (const line of lines) {
    let row;
    try {
      row = JSON.parse(line);
    } catch {
      continue;
    }

    if (row.type === "session_meta") {
      sessionMeta = row.payload || null;
      continue;
    }

    if (row?.payload?.type === "user_message") {
      userMessages.push((row.payload.message || "").trim());
      continue;
    }

    if (row?.payload?.type === "token_count") {
      latestUsage = row.payload.info?.total_token_usage || latestUsage;
      continue;
    }

    if (row?.payload?.type === "task_complete") {
      const taskIndex = turns.length;
      const userMessage = userMessages[taskIndex] || "(missing user message)";
      const compactMessage = userMessage.trim();
      const classification =
        /^\d+$/.test(compactMessage) && turns.length > 0
          ? {
              tier: turns[turns.length - 1].tier,
              routeId: turns[turns.length - 1].route_id,
              rationale: "Numeric follow-up inherits the previous route.",
            }
          : classifyTask(userMessage);

      const route = ROUTES[classification.routeId];
      const usage = deltaUsage(previousTurnUsage, latestUsage);
      const baseline = costFromUsage(
        usage,
        pricing.models[pricing.meta.default_baseline_model],
        pricing.creditsPerUsd
      );
      const routed = weightedUsageCost(usage, route.model_mix, pricing.models, pricing.creditsPerUsd);

      turns.push({
        turn_index: taskIndex + 1,
        timestamp: row.timestamp,
        elapsed_minutes_since_prior_task: minutesBetween(lastTaskTimestamp, row.timestamp),
        user_message: userMessage,
        tier: classification.tier,
        route_id: classification.routeId,
        route_label: route.label,
        rationale: classification.rationale,
        route_confidence: route.confidence,
        phases: route.phases,
        model_mix: route.model_mix,
        usage,
        baseline,
        routed,
      });

      previousTurnUsage = latestUsage;
      lastTaskTimestamp = row.timestamp;
    }
  }

  const totals = turns.reduce(
    (sum, turn) => {
      const breakdown = usageBreakdown(turn.usage);
      sum.input_tokens += breakdown.input_tokens;
      sum.uncached_input_tokens += breakdown.uncached_input_tokens;
      sum.cached_input_tokens += breakdown.cached_input_tokens;
      sum.output_tokens += breakdown.output_tokens;
      sum.reasoning_output_tokens += breakdown.reasoning_output_tokens;
      sum.total_tokens += breakdown.total_tokens;
      sum.baseline_usd += turn.baseline.usd;
      sum.baseline_credits += turn.baseline.credits;
      sum.routed_usd += turn.routed.usd;
      sum.routed_credits += turn.routed.credits;
      sum.route_phase_count += turn.phases.length;
      return sum;
    },
    {
      input_tokens: 0,
      uncached_input_tokens: 0,
      cached_input_tokens: 0,
      output_tokens: 0,
      reasoning_output_tokens: 0,
      total_tokens: 0,
      baseline_usd: 0,
      baseline_credits: 0,
      routed_usd: 0,
      routed_credits: 0,
      route_phase_count: 0,
    }
  );

  const estimatedSavingsUsd = totals.baseline_usd - totals.routed_usd;
  const estimatedSavingsCredits = totals.baseline_credits - totals.routed_credits;

  return {
    file: path.basename(filePath),
    session_id: sessionMeta?.id || null,
    source_cwd: sessionMeta?.cwd || null,
    tasks: turns,
    totals: {
      ...totals,
      estimated_savings_usd: estimatedSavingsUsd,
      estimated_savings_credits: estimatedSavingsCredits,
      estimated_savings_ratio: totals.baseline_usd === 0 ? 0 : estimatedSavingsUsd / totals.baseline_usd,
      average_route_phases: turns.length === 0 ? 0 : totals.route_phase_count / turns.length,
      baseline_phase_count: 1,
    },
  };
}

function renderMarkdownReport(result) {
  const { pricing, sessions, portfolio } = result;
  const lines = [];

  lines.push("# Routing Economics Pilot");
  lines.push("");
  lines.push("## Price Mode");
  lines.push("");
  lines.push(`- Price book: \`${pricing.price_book_id}\``);
  lines.push(`- Baseline model: \`${pricing.default_baseline_model}\``);
  lines.push(`- Credit policy: \`${pricing.credit_policy.name}\` = ${pricing.credit_policy.credits_per_usd} credits / USD`);
  lines.push(`- Source file: \`${pricing.source_file}\``);
  lines.push("");
  lines.push("## Assumptions");
  lines.push("");
  lines.push("- Baseline assumes all observed task tokens are charged as `gpt-5.5` under the selected price book.");
  lines.push("- Routed estimate keeps token volume fixed and only changes the model mix by route tier.");
  lines.push("- Cached input tokens are treated as a subset of input tokens and billed at the cached-input rate.");
  lines.push("- Reasoning output tokens are reported for observability but not double-billed; they are assumed to sit inside output tokens.");
  lines.push("- Credits are converted from USD using the project credit policy that matches the user's workflow diagram.");
  lines.push("");
  lines.push("## Portfolio Summary");
  lines.push("");
  lines.push(`- Sessions analyzed: ${sessions.length}`);
  lines.push(`- Input tokens: ${formatInt(portfolio.input_tokens)}`);
  lines.push(`- Cached input tokens: ${formatInt(portfolio.cached_input_tokens)}`);
  lines.push(`- Uncached input tokens: ${formatInt(portfolio.uncached_input_tokens)}`);
  lines.push(`- Output tokens: ${formatInt(portfolio.output_tokens)}`);
  lines.push(`- Total tokens: ${formatInt(portfolio.total_tokens)}`);
  lines.push(`- Baseline cost: ${formatNumber(portfolio.baseline_credits)} credits / $${formatNumber(portfolio.baseline_usd)}`);
  lines.push(`- Routed cost: ${formatNumber(portfolio.routed_credits)} credits / $${formatNumber(portfolio.routed_usd)}`);
  lines.push(
    `- Estimated savings: ${formatNumber(portfolio.estimated_savings_credits)} credits / $${formatNumber(
      portfolio.estimated_savings_usd
    )} (${formatNumber(portfolio.estimated_savings_ratio * 100)}%)`
  );
  lines.push(`- Average routed phase count per task: ${formatNumber(portfolio.average_route_phases)}`);
  lines.push("");

  for (const session of sessions) {
    lines.push(`## ${session.file}`);
    lines.push("");
    lines.push(`- Tokens: ${formatInt(session.totals.total_tokens)}`);
    lines.push(`- Baseline: ${formatNumber(session.totals.baseline_credits)} credits / $${formatNumber(session.totals.baseline_usd)}`);
    lines.push(`- Routed: ${formatNumber(session.totals.routed_credits)} credits / $${formatNumber(session.totals.routed_usd)}`);
    lines.push(
      `- Savings: ${formatNumber(session.totals.estimated_savings_credits)} credits / $${formatNumber(
        session.totals.estimated_savings_usd
      )} (${formatNumber(session.totals.estimated_savings_ratio * 100)}%)`
    );
    lines.push(`- Average route phases: ${formatNumber(session.totals.average_route_phases)}`);
    lines.push("");
    lines.push("| Turn | Tier | Route | Total Tokens | Routed Credits | Routed USD | Note |");
    lines.push("|---|---|---|---:|---:|---:|---|");

    for (const turn of session.tasks) {
      const note = turn.user_message.replace(/\|/g, "\\|").slice(0, 60);
      lines.push(
        `| ${turn.turn_index} | ${turn.tier} | ${turn.route_label} | ${formatInt(turn.usage.total_tokens)} | ${formatNumber(
          turn.routed.credits
        )} | $${formatNumber(turn.routed.usd)} | ${note} |`
      );
    }

    lines.push("");
  }

  lines.push("## Interpretation Guide");
  lines.push("");
  lines.push("- Read-heavy or shared-config tasks usually save more because more token volume can stay on `gpt-5.4-mini` or `gpt-5.4`.");
  lines.push("- T4 planning work naturally saves less because much of the work still belongs on `gpt-5.5`.");
  lines.push("- Higher phase count is a latency proxy, not a full productivity metric. It suggests more coordination overhead, not necessarily lower end-to-end success.");
  lines.push("- For a stronger production-grade dashboard, feed this script post-rollout task transcripts rather than only the original routing-design sessions.");

  return lines.join("\n");
}

function buildPortfolioSummary(sessions) {
  const totals = {
    input_tokens: sumMetric(sessions, (session) => session.totals.input_tokens),
    uncached_input_tokens: sumMetric(sessions, (session) => session.totals.uncached_input_tokens),
    cached_input_tokens: sumMetric(sessions, (session) => session.totals.cached_input_tokens),
    output_tokens: sumMetric(sessions, (session) => session.totals.output_tokens),
    reasoning_output_tokens: sumMetric(sessions, (session) => session.totals.reasoning_output_tokens),
    total_tokens: sumMetric(sessions, (session) => session.totals.total_tokens),
    baseline_usd: sumMetric(sessions, (session) => session.totals.baseline_usd),
    baseline_credits: sumMetric(sessions, (session) => session.totals.baseline_credits),
    routed_usd: sumMetric(sessions, (session) => session.totals.routed_usd),
    routed_credits: sumMetric(sessions, (session) => session.totals.routed_credits),
    average_route_phases:
      sessions.length === 0 ? 0 : sumMetric(sessions, (session) => session.totals.average_route_phases) / sessions.length,
  };

  return {
    ...totals,
    estimated_savings_usd: totals.baseline_usd - totals.routed_usd,
    estimated_savings_credits: totals.baseline_credits - totals.routed_credits,
    estimated_savings_ratio: totals.baseline_usd === 0 ? 0 : (totals.baseline_usd - totals.routed_usd) / totals.baseline_usd,
  };
}

export async function analyzeRoutingEconomics(options = {}) {
  const mergedOptions = {
    priceBookPath: options.priceBookPath || defaultPriceBookPath,
    priceBookId: options.priceBookId || "standard_short_context",
    baselineModel: options.baselineModel || "gpt-5.5",
  };
  const pricingBook = await loadPriceBook(mergedOptions.priceBookPath, mergedOptions.priceBookId);
  pricingBook.meta.default_baseline_model = mergedOptions.baselineModel;

  const files = (await fs.readdir(transcriptsDir))
    .filter((name) => name.endsWith(".jsonl"))
    .sort();
  const sessions = [];

  for (const file of files) {
    sessions.push(await parseTranscript(path.join(transcriptsDir, file), pricingBook));
  }

  const pricing = {
    source_file: mergedOptions.priceBookPath,
    price_book_id: pricingBook.id,
    default_baseline_model: mergedOptions.baselineModel,
    credit_policy: pricingBook.meta.credit_policy,
    source_notes: pricingBook.meta.sources,
    reference_models: pricingBook.models,
  };

  const result = {
    generated_at: new Date().toISOString(),
    pricing,
    sessions,
    portfolio: buildPortfolioSummary(sessions),
  };

  result.markdown_report = renderMarkdownReport(result);
  return result;
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const result = await analyzeRoutingEconomics(options);

  if (options.writeReport) {
    await fs.mkdir(path.dirname(options.reportPath), { recursive: true });
    await fs.writeFile(options.reportPath, result.markdown_report, "utf8");
  }

  if (options.json) {
    process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
    return;
  }

  process.stdout.write(`${result.markdown_report}\n`);
}

if (import.meta.url === `file://${__filename}`) {
  main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
}
