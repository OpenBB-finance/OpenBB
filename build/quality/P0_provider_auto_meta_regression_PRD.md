# P0 PRD: Auto 选源策略引擎 + 统一 Meta + 每日回归

## 1. 背景与问题
当前 OpenBB 在多源调用场景存在三个痛点：
- `provider=auto` 主要依赖提示词约定，服务端缺乏统一策略执行。
- 响应元信息不统一，外部 Agent 难以解释“为什么用了这个源、是否发生回退、可信度多少”。
- 缺少可重复的真实业务回归基准，准确性无法持续证明。

## 2. 与上游对照结论
对照 `origin/develop`：
- 上游不存在本地新增的 `provider` raw router 改造与策略模块。
- 上游也未包含本地 MCP 工具增强和 provider 自动回退链。
- 结论：当前方向（服务端策略 + 可观测 meta + 回归基准）优于“仅回到上游原样”。应在当前分支继续演进，不回退。

## 3. P0 目标
1. Provider 省略时默认 `auto`，并可显式传 `provider=auto`。
2. 服务端自动选择数据源并按策略回退。
3. 所有 API 结果统一输出 `extra.meta` 核心字段。
4. 建立每日回归并输出可审计报告。

## 4. 功能需求
### 4.1 服务端策略引擎
- 输入：`route`、`requested_provider`、命令覆盖字典、凭证状态。
- 输出：有序候选 provider 列表。
- 规则：
  - 显式 provider：只尝试该源。
  - `auto`：按质量优先级排序，并结合凭证可用性。
  - 执行失败后按候选顺序回退。

### 4.2 统一 Meta 结构
每次调用返回 `extra.meta`（或 raw provider 的 `meta`）至少包含：
- `route`
- `provider_requested`
- `provider_used`
- `provider_candidates`
- `fallback_trace`
- `confidence`

### 4.3 每日回归基准
- 用真实业务问题覆盖 equity / futures / macro / rates / regulators。
- 每日自动跑并产出 Markdown 报告。
- 失败即红灯，可用于发布门禁。

## 5. 已落地实现（本次）
- 新增策略模块：`/Users/lichengyin/Desktop/Projects/OpenBB/openbb_platform/core/openbb_core/api/provider_strategy.py`
- API wrapper 自动策略与 meta 注入：
  - `/Users/lichengyin/Desktop/Projects/OpenBB/openbb_platform/core/openbb_core/api/router/commands.py`
- Raw provider router 自动回退与 meta：
  - `/Users/lichengyin/Desktop/Projects/OpenBB/openbb_platform/core/openbb_core/api/router/provider.py`
- 新增/更新测试：
  - `/Users/lichengyin/Desktop/Projects/OpenBB/openbb_platform/core/tests/api/test_router/test_provider_strategy.py`
  - `/Users/lichengyin/Desktop/Projects/OpenBB/openbb_platform/core/tests/api/test_router/test_router_provider.py`
  - `/Users/lichengyin/Desktop/Projects/OpenBB/openbb_platform/core/tests/api/test_router/test_commands_auto_provider.py`
- 新增每日回归：
  - `/Users/lichengyin/Desktop/Projects/OpenBB/build/quality/daily_regression_cases.json`
  - `/Users/lichengyin/Desktop/Projects/OpenBB/build/quality/run_daily_regression.py`
  - `/Users/lichengyin/Desktop/Projects/OpenBB/build/quality/README.md`

## 6. 验收指标（P0）
- 功能：
  - provider 省略时不再 422，而是自动执行并返回数据或可解释错误。
  - `provider=auto` 显式传入可执行。
- 可观测性：
  - `meta` 关键字段覆盖率 100%。
  - `fallback_trace` 首次失败与后续成功均可追踪。
- 稳定性：
  - 每日回归通过率 >= 95%。
  - 连续 7 天无“无 meta 返回”回归。

## 7. 非目标（P0 不做）
- 不在 P0 内实现跨源字段级融合（只做选源与回退）。
- 不在 P0 内做复杂统计置信度模型（先用策略分+失败惩罚）。
- 不在 P0 内覆盖全部 200+ MCP tools 的端到端回归（先覆盖高价值业务题库）。

## 8. 风险与后续建议
- 风险：部分 provider 的“可用但无数据”会影响自动选择体验。
- 建议：
  1. P1 增加 provider 健康分（成功率、时延、近 24h 错误率）。
  2. P1 增加路由级白名单策略（如宏观优先 IMF/OECD/FRED）。
  3. P1 增加 `meta` 中 `selection_reason`，便于 Agent 做解释。
