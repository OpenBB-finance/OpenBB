# OpenBB P0 Quality Gate

本目录用于落地 P0 质量目标：
- 服务端 `auto` 选源可验证
- `meta` 字段统一且可机读
- 每日用真实业务问题做回归

## 文件说明
- `daily_regression_cases.json`：真实业务问题题库（中英双语描述）。
- `run_daily_regression.py`：回归执行器，自动校验 HTTP、结果非空、`meta` 完整性与 `confidence` 区间。
- `reports/`：每日执行后输出 Markdown 报告。

## 本地执行
```bash
python3 build/quality/run_daily_regression.py \
  --base-url http://127.0.0.1:6900
```

## 验收规则（脚本内置）
每个用例必须同时满足：
- HTTP 200
- `results` 非空
- `extra.meta` 存在
- `extra.meta` 包含以下键：
  - `route`
  - `provider_requested`
  - `provider_used`
  - `provider_candidates`
  - `fallback_trace`
  - `confidence`
  - `selection_reason`
- `fallback_trace` 为非空列表
- `fallback_trace` 最后一跳必须是 `success` 且 provider 与 `provider_used` 一致
- `provider_used` 必须出现在 `provider_candidates` 中
- `confidence` 在 `[0, 1]`
- 若用例声明 `expected_provider_requested=auto`，则必须匹配
- 若用例声明 `expected_selection_mode`，需与 `meta.selection_reason.mode` 一致

## 每日任务建议
可用 cron 在每日北京时间 08:30 运行（按你的系统时区调整）：
```bash
30 8 * * * cd /Users/lichengyin/Desktop/Projects/OpenBB && \
python3 build/quality/run_daily_regression.py --base-url http://127.0.0.1:6900
```

## 失败处理建议
1. 先看 `reports/*.md` 中失败用例的 `Check Matrix`。
2. 若是 `http_200` 失败，优先排查服务连通性和 provider 凭证。
3. 若是 `meta_keys_complete` 失败，优先检查 API wrapper 是否部署到最新版本。
4. 若是 `non_empty_results` 失败，确认日期窗口与符号是否有效，再看 provider 回退链。
