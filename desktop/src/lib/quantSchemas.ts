import { z } from "zod";
import type {
  DashboardSnapshotV2Payload,
  RunAuditPayload,
  RunLatestConstraintsPayload,
  RunLatestMetaPayload,
  RunRiskPayload,
  RunExposuresPayload,
} from "../types/quant";

const modelNameSchema = z.enum(["xgb_lstm", "lgbm_ranker"]);
const statusSchema = z.enum(["ok", "insufficient_data", "not_found"]);
const portfolioPositionSchema = z.object({
  symbol: z.string(),
  weight: z.number(),
});
const portfolioRiskContributionSchema = z.object({
  symbol: z.string(),
  contribution: z.number(),
});

const constraintBindingItemSchema = z.object({
  constraint_type: z.string(),
  binding_count: z.number(),
  binding_ratio: z.number(),
});

const runLatestMetaSchema = z.object({
  run_id: z.string().nullable().optional(),
  run_uid: z.string().nullable().optional(),
  model_name: modelNameSchema,
  as_of_date: z.string().nullable().optional(),
  status: statusSchema,
  artifact_contract_version: z.string().nullable().optional(),
  required_artifacts_ready: z.boolean(),
  universe_stage_counts: z.record(z.number()),
  artifact_completeness: z.array(
    z.object({
      artifact: z.string(),
      ready: z.boolean(),
      path: z.string().nullable().optional(),
    }),
  ),
  message: z.string().nullable().optional(),
});

const runLatestConstraintsSchema = z.object({
  run_id: z.string(),
  model_name: modelNameSchema,
  status: statusSchema,
  message: z.string().nullable().optional(),
  items: z.array(constraintBindingItemSchema),
  liquidity_clip_ratio: z.number(),
  risk_contribution_max: z.number(),
  top_risk_contribution: z.array(portfolioRiskContributionSchema),
  liquidity_adv_top: z.array(
    z.object({
      symbol: z.string(),
      adv_weight_cap: z.number(),
    }),
  ),
});

const dashboardSnapshotSchema = z.object({
  run_id: z.string(),
  run_uid: z.string().nullable().optional(),
  model_name: modelNameSchema,
  as_of_utc: z.string(),
  total_return: z.number(),
  cagr: z.number(),
  sharpe: z.number(),
  sortino: z.number(),
  max_drawdown: z.number(),
  volatility: z.number(),
  turnover: z.number(),
  win_rate: z.number(),
  exposure: z.record(z.number()),
  risk_contrib_top10: z.array(portfolioRiskContributionSchema),
  constraint_bindings: z.array(constraintBindingItemSchema),
  ic_rolling: z.array(z.record(z.union([z.string(), z.number()]))),
  currency: z.string(),
});

const runAuditSchema = z.object({
  run_id: z.string(),
  status: statusSchema,
  message: z.string().nullable().optional(),
  events: z.array(
    z.object({
      id: z.number().nullable().optional(),
      run_id: z.string(),
      event_type: z.string(),
      severity: z.enum(["info", "warning", "critical"]),
      payload: z.record(z.unknown()),
      created_at_utc: z.string(),
    }),
  ),
});

const runRiskSchema = z.object({
  run_id: z.string(),
  model_name: modelNameSchema,
  status: statusSchema,
  message: z.string().nullable().optional(),
  vol_ex_ante: z.number(),
  cvar_95: z.number(),
  position_risk_contrib_top5: z.array(portfolioRiskContributionSchema),
  position_risk_contrib_top10: z.array(portfolioRiskContributionSchema),
  position_return_contrib_top5: z.array(portfolioRiskContributionSchema),
  worst5_positions: z.array(portfolioRiskContributionSchema),
});

const runExposuresSchema = z.object({
  run_id: z.string(),
  model_name: modelNameSchema,
  status: statusSchema,
  message: z.string().nullable().optional(),
  sector_exposure: z.array(
    z.object({
      category: z.string(),
      weight: z.number(),
    }),
  ),
  factor_exposure: z.record(z.number()),
  beta_spy: z.number(),
  beta_qqq: z.number(),
  duration_estimate: z.number(),
  top10_long: z.array(portfolioPositionSchema),
  top10_short: z.array(portfolioPositionSchema),
});

function parseWithSchema<T>(schema: z.ZodType<T>, payload: unknown, label: string): T {
  const parsed = schema.safeParse(payload);
  if (parsed.success) {
    return parsed.data;
  }
  throw new Error(`${label} response validation failed`);
}

export function parseRunLatestMeta(payload: unknown): RunLatestMetaPayload {
  return parseWithSchema(runLatestMetaSchema, payload, "run_latest_meta");
}

export function parseRunLatestConstraints(payload: unknown): RunLatestConstraintsPayload {
  return parseWithSchema(runLatestConstraintsSchema, payload, "run_latest_constraints");
}

export function parseRunSnapshot(payload: unknown): DashboardSnapshotV2Payload {
  return parseWithSchema(dashboardSnapshotSchema, payload, "run_snapshot");
}

export function parseRunAudit(payload: unknown): RunAuditPayload {
  return parseWithSchema(runAuditSchema, payload, "run_audit");
}

export function parseRunRisk(payload: unknown): RunRiskPayload {
  return parseWithSchema(runRiskSchema, payload, "run_risk");
}

export function parseRunExposures(payload: unknown): RunExposuresPayload {
  return parseWithSchema(runExposuresSchema, payload, "run_exposures");
}
