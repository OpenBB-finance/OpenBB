import { createFileRoute } from "@tanstack/react-router";
import { useCallback, useEffect, useMemo, useState } from "react";
import { resolveOpenBBBackend } from "../lib/openbbBackend";
import {
  fetchExecutionMode,
  fetchExecutionFillsHistory,
  fetchExecutionOrdersCurrent,
  fetchExecutionPnl,
  fetchExecutionPositionsCurrent,
  fetchRiskEvents,
  fetchRunAudit,
  fetchRunConstraints,
  fetchRunExposures,
  fetchRunRisk,
  fetchRiskLimits,
  fetchUniverseExclusions,
  fetchUniverseSnapshot,
  probeQuantMlActivation,
  previewExecutionOrders,
  riskCheckPretrade,
  submitExecutionOrders,
  updateExecutionMode,
} from "../lib/quantApi";
import type {
  ExecutionMode,
  ExecutionModePayload,
  ExecutionFillsPayload,
  ExecutionOrdersPayload,
  ExecutionPnlPayload,
  ExecutionPositionsPayload,
  ExecutionPreviewPayload,
  ExecutionSubmitPayload,
  ModelName,
  RunAuditPayload,
  RunConstraintsPayload,
  RunExposuresPayload,
  RunRiskPayload,
  RiskEventsPayload,
  RiskLimitsPayload,
  RiskPretradePayload,
  UniverseExclusionsPayload,
  UniverseSnapshotPayload,
} from "../types/quant";

function toErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "Request failed";
}

function formatNum(v: number | null | undefined, digits = 4): string {
  if (v === null || v === undefined || Number.isNaN(v)) return "-";
  return v.toFixed(digits);
}

function formatPct(v: number | null | undefined, digits = 2): string {
  if (v === null || v === undefined || Number.isNaN(v)) return "-";
  return `${(v * 100).toFixed(digits)}%`;
}

function StatusBadge({ passed }: { passed: boolean }) {
  return (
    <span
      className={`rounded-sm border px-2 py-0.5 body-xxs-medium ${
        passed
          ? "border-emerald-500/50 bg-emerald-500/15 text-emerald-300"
          : "border-red-500/50 bg-red-500/15 text-red-300"
      }`}
    >
      {passed ? "PASS" : "FAIL"}
    </span>
  );
}

function ExecutionPage() {
  const [baseUrl, setBaseUrl] = useState("");
  const [runId, setRunId] = useState("");
  const [modelName, setModelName] = useState<ModelName>("lgbm_ranker");
  const [isBusy, setIsBusy] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activationMessage, setActivationMessage] = useState<string | null>(null);

  const [preview, setPreview] = useState<ExecutionPreviewPayload | null>(null);
  const [risk, setRisk] = useState<RiskPretradePayload | null>(null);
  const [submit, setSubmit] = useState<ExecutionSubmitPayload | null>(null);
  const [, setOrders] = useState<ExecutionOrdersPayload | null>(null);
  const [fills, setFills] = useState<ExecutionFillsPayload | null>(null);
  const [positions, setPositions] = useState<ExecutionPositionsPayload | null>(null);
  const [pnl, setPnl] = useState<ExecutionPnlPayload | null>(null);
  const [limits, setLimits] = useState<RiskLimitsPayload | null>(null);
  const [events, setEvents] = useState<RiskEventsPayload | null>(null);
  const [executionMode, setExecutionMode] = useState<ExecutionModePayload | null>(null);
  const [modeDraft, setModeDraft] = useState<ExecutionMode>("paper");
  const [runRisk, setRunRisk] = useState<RunRiskPayload | null>(null);
  const [runExposures, setRunExposures] = useState<RunExposuresPayload | null>(null);
  const [runConstraints, setRunConstraints] = useState<RunConstraintsPayload | null>(null);
  const [runAudit, setRunAudit] = useState<RunAuditPayload | null>(null);
  const [universeSnapshot, setUniverseSnapshot] = useState<UniverseSnapshotPayload | null>(null);
  const [universeExclusions, setUniverseExclusions] = useState<UniverseExclusionsPayload | null>(null);

  const canSubmit = useMemo(() => {
    if (!preview || !risk) return false;
    return Boolean(risk.passed) && !risk.kill_switch;
  }, [preview, risk]);

  const refreshState = useCallback(async () => {
    if (!baseUrl || !runId.trim()) return;
    const [
      nextOrders,
      nextFills,
      nextPositions,
      nextPnl,
      nextLimits,
      nextEvents,
      nextExecutionMode,
      nextRunRisk,
      nextRunExposures,
      nextRunConstraints,
      nextRunAudit,
      nextUniverseSnapshot,
      nextUniverseExclusions,
    ] = await Promise.all([
      fetchExecutionOrdersCurrent(baseUrl, runId.trim(), modelName),
      fetchExecutionFillsHistory(baseUrl, runId.trim(), modelName, 200),
      fetchExecutionPositionsCurrent(baseUrl, runId.trim(), modelName),
      fetchExecutionPnl(baseUrl, runId.trim(), modelName),
      fetchRiskLimits(baseUrl, runId.trim(), modelName),
      fetchRiskEvents(baseUrl, runId.trim(), modelName, 200),
      fetchExecutionMode(baseUrl, runId.trim(), modelName),
      fetchRunRisk(baseUrl, runId.trim(), modelName).catch(() => null),
      fetchRunExposures(baseUrl, runId.trim(), modelName).catch(() => null),
      fetchRunConstraints(baseUrl, runId.trim(), modelName).catch(() => null),
      fetchRunAudit(baseUrl, runId.trim(), 200).catch(() => null),
      fetchUniverseSnapshot(baseUrl, runId.trim()).catch(() => null),
      fetchUniverseExclusions(baseUrl, runId.trim()).catch(() => null),
    ]);
    setOrders(nextOrders);
    setFills(nextFills);
    setPositions(nextPositions);
    setPnl(nextPnl);
    setLimits(nextLimits);
    setEvents(nextEvents);
    setExecutionMode(nextExecutionMode);
    setModeDraft(nextExecutionMode.mode);
    setRunRisk(nextRunRisk);
    setRunExposures(nextRunExposures);
    setRunConstraints(nextRunConstraints);
    setRunAudit(nextRunAudit);
    setUniverseSnapshot(nextUniverseSnapshot);
    setUniverseExclusions(nextUniverseExclusions);
  }, [baseUrl, modelName, runId]);

  const handlePreview = useCallback(async () => {
    if (!baseUrl || !runId.trim()) {
      setErrorMessage("run_id를 입력하세요.");
      return;
    }
    setIsBusy(true);
    setErrorMessage(null);
    try {
      const previewPayload = await previewExecutionOrders(baseUrl, { run_id: runId.trim(), model_name: modelName });
      setPreview(previewPayload);
      const riskPayload = await riskCheckPretrade(baseUrl, { run_id: runId.trim(), model_name: modelName });
      setRisk(riskPayload);
      await refreshState();
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    } finally {
      setIsBusy(false);
    }
  }, [baseUrl, modelName, refreshState, runId]);

  const handleSubmit = useCallback(async () => {
    if (!canSubmit || !baseUrl || !runId.trim()) return;
    setIsBusy(true);
    setErrorMessage(null);
    try {
      const submitPayload = await submitExecutionOrders(baseUrl, { run_id: runId.trim(), model_name: modelName });
      setSubmit(submitPayload);
      await refreshState();
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    } finally {
      setIsBusy(false);
    }
  }, [baseUrl, canSubmit, modelName, refreshState, runId]);

  const handleSaveExecutionMode = useCallback(async () => {
    if (!baseUrl || !runId.trim()) return;
    setIsBusy(true);
    setErrorMessage(null);
    try {
      const nextMode = await updateExecutionMode(baseUrl, {
        run_id: runId.trim(),
        model_name: modelName,
        mode: modeDraft,
      });
      setExecutionMode(nextMode);
      await refreshState();
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    } finally {
      setIsBusy(false);
    }
  }, [baseUrl, modeDraft, modelName, refreshState, runId]);

  useEffect(() => {
    void (async () => {
      try {
        const backend = await resolveOpenBBBackend();
        setBaseUrl(backend.baseUrl);
        const activation = await probeQuantMlActivation(backend.baseUrl);
        if (!activation.available) {
          setActivationMessage(activation.detail || "quant_ml 확장 사용 불가. 실행 기능이 비활성화됩니다.");
        }
      } catch (error) {
        setErrorMessage(toErrorMessage(error));
      }
    })();
  }, []);

  const previewAny = preview as unknown as Record<string, unknown> | null;
  const positionsAny = positions as unknown as Record<string, unknown> | null;
  const fillsAny = fills as unknown as Record<string, unknown> | null;
  const riskAny = risk as unknown as Record<string, unknown> | null;
  const eventsAny = events as unknown as Record<string, unknown> | null;
  const pnlAny = pnl as unknown as Record<string, unknown> | null;

  const orderRows = Array.isArray(previewAny?.orders)
    ? (previewAny.orders as Array<Record<string, unknown>>)
    : [];
  const positionRows = Array.isArray(positionsAny?.positions)
    ? (positionsAny.positions as Array<Record<string, unknown>>)
    : [];
  const fillRows = Array.isArray(fillsAny?.fills)
    ? (fillsAny.fills as Array<Record<string, unknown>>)
    : [];
  const riskChecks = Array.isArray(riskAny?.checks)
    ? (riskAny.checks as Array<Record<string, unknown>>)
    : [];
  const eventRows = Array.isArray(eventsAny?.events)
    ? (eventsAny.events as Array<Record<string, unknown>>)
    : [];

  return (
    <div className="h-full min-h-0 overflow-auto py-4">
      <div className="mb-3">
        <h1 className="body-lg-medium text-theme-primary">Execution / Risk</h1>
        <p className="body-sm-regular text-theme-muted">Preview → Pretrade Risk Check → Submit 워크플로우.</p>
      </div>

      <div className="mb-3 rounded-sm border border-theme-outline bg-theme-primary p-3">
        <div className="grid grid-cols-1 gap-2 md:grid-cols-[minmax(0,1fr)_160px_auto]">
          <label className="body-xs-medium text-theme-muted">
            Run ID
            <input
              className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary px-2 py-2 body-xs-regular text-theme-primary"
              placeholder="학습 완료된 run_id 입력"
              value={runId}
              onChange={(event) => setRunId(event.target.value)}
            />
          </label>
          <label className="body-xs-medium text-theme-muted">
            Model
            <select
              className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary px-2 py-2 body-xs-regular text-theme-primary"
              value={modelName}
              onChange={(event) => setModelName(event.target.value as ModelName)}
            >
              <option value="lgbm_ranker">LGBM Ranker</option>
              <option value="xgb_lstm">XGB + LSTM</option>
            </select>
          </label>
          <div className="flex gap-2 items-end">
            <button
              type="button"
              className="button-neutral rounded-sm px-4 py-2 body-xs-medium"
              onClick={() => void handlePreview()}
              disabled={isBusy || Boolean(activationMessage)}
            >
              {isBusy ? "Processing..." : "Preview + Risk Check"}
            </button>
            <button
              type="button"
              className={`rounded-sm px-4 py-2 body-xs-medium ${canSubmit ? "button-neutral" : "button-secondary opacity-50"}`}
              onClick={() => void handleSubmit()}
              disabled={isBusy || !canSubmit || Boolean(activationMessage)}
            >
              Submit Orders
            </button>
          </div>
        </div>
        <div className="mt-3 grid grid-cols-1 gap-2 md:grid-cols-[180px_auto_1fr]">
          <label className="body-xs-medium text-theme-muted">
            Execution Mode
            <select
              className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary px-2 py-2 body-xs-regular text-theme-primary"
              value={modeDraft}
              onChange={(event) => setModeDraft(event.target.value as ExecutionMode)}
            >
              <option value="paper">paper</option>
              <option value="shadow_live">shadow_live</option>
              <option value="live_adapter">live_adapter</option>
            </select>
          </label>
          <div className="flex items-end">
            <button
              type="button"
              className="button-secondary rounded-sm px-4 py-2 body-xs-medium"
              onClick={() => void handleSaveExecutionMode()}
              disabled={isBusy || !runId.trim()}
            >
              Save Mode
            </button>
          </div>
          <div className="rounded-sm bg-theme-secondary p-2">
            <p className="body-xxs-regular text-theme-muted">Execution Adapter Status</p>
            <p className="body-xs-medium text-theme-primary">
              {executionMode?.mode ?? "paper"} | broker_ready={String(executionMode?.broker_ready ?? false)}
            </p>
            <p className="body-xxs-regular text-theme-muted">
              live_adapter={String(executionMode?.live_adapter_enabled ?? false)} | kill_switch={String(executionMode?.kill_switch ?? false)}
            </p>
          </div>
        </div>
      </div>

      {errorMessage ? (
        <div className="mb-3 rounded-sm border border-red-500/60 bg-red-500/10 p-2">
          <p className="body-xs-medium text-red-400">{errorMessage}</p>
        </div>
      ) : null}
      {activationMessage ? (
        <div className="mb-3 rounded-sm border border-amber-500/60 bg-amber-500/10 p-2">
          <p className="body-xs-medium text-amber-300">{activationMessage}</p>
        </div>
      ) : null}
      {risk && (!risk.passed || risk.kill_switch) ? (
        <div className="mb-3 rounded-sm border border-red-500/60 bg-red-500/10 p-2">
          <p className="body-xs-medium text-red-400">
            {risk.kill_switch ? "Kill switch가 활성화되어 주문이 차단되었습니다." : "리스크 체크 실패로 제출이 차단되었습니다."}
          </p>
        </div>
      ) : null}
      {submit ? (
        <div className="mb-3 rounded-sm border border-emerald-500/60 bg-emerald-500/10 p-2">
          <p className="body-xs-medium text-emerald-300">주문이 성공적으로 제출되었습니다.</p>
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-3 xl:grid-cols-2">
        <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
          <h3 className="body-sm-medium text-theme-primary mb-2">Risk Check Results</h3>
          {riskChecks.length === 0 ? (
            <p className="body-xs-regular text-theme-muted">Preview를 실행하면 리스크 체크 결과가 표시됩니다.</p>
          ) : (
            <div className="space-y-1.5">
              {riskChecks.map((check, idx) => (
                <div key={`rc-${idx}`} className="flex items-center justify-between rounded-sm bg-theme-secondary p-2">
                  <span className="body-xs-regular text-theme-primary">{String(check.name ?? check.rule ?? `Check ${idx + 1}`)}</span>
                  <StatusBadge passed={Boolean(check.passed)} />
                </div>
              ))}
            </div>
          )}
          {risk && (
            <div className="mt-2 grid grid-cols-2 gap-1.5">
              <div className="rounded-sm bg-theme-secondary p-2">
                <p className="body-xxs-regular text-theme-muted">Overall</p>
                <StatusBadge passed={Boolean(risk.passed)} />
              </div>
              <div className="rounded-sm bg-theme-secondary p-2">
                <p className="body-xxs-regular text-theme-muted">Kill Switch</p>
                <p className={`body-xs-medium ${risk.kill_switch ? "text-red-400" : "text-emerald-400"}`}>
                  {risk.kill_switch ? "ACTIVE" : "OFF"}
                </p>
              </div>
            </div>
          )}
        </div>

        <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
          <h3 className="body-sm-medium text-theme-primary mb-2">Run Diagnostics</h3>
          <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Audit Events</p>
              <p className="body-xs-medium text-theme-primary">{runAudit?.events.length ?? 0}</p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Universe Exclusions</p>
              <p className="body-xs-medium text-theme-primary">{universeExclusions?.items.length ?? 0}</p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Constraint Keys</p>
              <p className="body-xs-medium text-theme-primary">{Object.keys(runConstraints ?? {}).length}</p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Universe Stages</p>
              <p className="body-xs-medium text-theme-primary">{Object.keys(universeSnapshot?.stage_counts ?? {}).length}</p>
            </div>
          </div>
          <div className="mt-2 grid grid-cols-1 gap-2 md:grid-cols-2">
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xs-medium text-theme-primary">Run Risk</p>
              <pre className="mt-1 max-h-32 overflow-auto text-[11px] text-theme-muted">{JSON.stringify(runRisk, null, 2)}</pre>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xs-medium text-theme-primary">Run Exposures</p>
              <pre className="mt-1 max-h-32 overflow-auto text-[11px] text-theme-muted">{JSON.stringify(runExposures, null, 2)}</pre>
            </div>
          </div>
        </div>

        <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
          <h3 className="body-sm-medium text-theme-primary mb-2">Order Preview ({orderRows.length})</h3>
          {orderRows.length === 0 ? (
            <p className="body-xs-regular text-theme-muted">주문 프리뷰가 없습니다.</p>
          ) : (
            <div className="overflow-auto max-h-64">
              <table className="min-w-full text-left">
                <thead>
                  <tr className="border-b border-theme-outline">
                    <th className="px-2 py-1.5 body-xxs-medium text-theme-muted">Symbol</th>
                    <th className="px-2 py-1.5 body-xxs-medium text-theme-muted">Side</th>
                    <th className="px-2 py-1.5 body-xxs-medium text-theme-muted">Qty</th>
                    <th className="px-2 py-1.5 body-xxs-medium text-theme-muted">Weight</th>
                  </tr>
                </thead>
                <tbody>
                  {orderRows.slice(0, 30).map((row, idx) => (
                    <tr key={`ord-${idx}`} className="border-b border-theme-outline/30">
                      <td className="px-2 py-1.5 body-xxs-regular text-theme-primary">{String(row.symbol ?? "-")}</td>
                      <td className={`px-2 py-1.5 body-xxs-regular ${String(row.side) === "buy" ? "text-emerald-400" : "text-red-400"}`}>
                        {String(row.side ?? "-")}
                      </td>
                      <td className="px-2 py-1.5 body-xxs-regular text-theme-primary">{formatNum(Number(row.qty ?? row.quantity ?? 0), 0)}</td>
                      <td className="px-2 py-1.5 body-xxs-regular text-theme-primary">{formatPct(Number(row.weight ?? 0))}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
          <h3 className="body-sm-medium text-theme-primary mb-2">Positions ({positionRows.length})</h3>
          {positionRows.length === 0 ? (
            <p className="body-xs-regular text-theme-muted">포지션 데이터 없음.</p>
          ) : (
            <div className="overflow-auto max-h-48">
              <table className="min-w-full text-left">
                <thead>
                  <tr className="border-b border-theme-outline">
                    <th className="px-2 py-1.5 body-xxs-medium text-theme-muted">Symbol</th>
                    <th className="px-2 py-1.5 body-xxs-medium text-theme-muted">Qty</th>
                    <th className="px-2 py-1.5 body-xxs-medium text-theme-muted">MktVal</th>
                    <th className="px-2 py-1.5 body-xxs-medium text-theme-muted">P&L</th>
                  </tr>
                </thead>
                <tbody>
                  {positionRows.slice(0, 20).map((row, idx) => (
                    <tr key={`pos-${idx}`} className="border-b border-theme-outline/30">
                      <td className="px-2 py-1.5 body-xxs-regular text-theme-primary">{String(row.symbol ?? "-")}</td>
                      <td className="px-2 py-1.5 body-xxs-regular text-theme-primary">{formatNum(Number(row.qty ?? row.quantity ?? 0), 0)}</td>
                      <td className="px-2 py-1.5 body-xxs-regular text-theme-primary">{formatNum(Number(row.market_value ?? 0), 0)}</td>
                      <td className={`px-2 py-1.5 body-xxs-regular ${Number(row.pnl ?? 0) >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                        {formatNum(Number(row.pnl ?? 0), 2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
          <h3 className="body-sm-medium text-theme-primary mb-2">P&L / Fills / Risk Events</h3>
          {pnlAny ? (
            <div className="grid grid-cols-3 gap-1.5 mb-2">
              <div className="rounded-sm bg-theme-secondary p-2">
                <p className="body-xxs-regular text-theme-muted">Total P&L</p>
                <p className={`body-xs-medium ${Number(pnlAny.total_pnl ?? 0) >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                  {formatNum(Number(pnlAny.total_pnl ?? 0), 2)}
                </p>
              </div>
              <div className="rounded-sm bg-theme-secondary p-2">
                <p className="body-xxs-regular text-theme-muted">Realized</p>
                <p className="body-xs-medium text-theme-primary">{formatNum(Number(pnlAny.realized ?? 0), 2)}</p>
              </div>
              <div className="rounded-sm bg-theme-secondary p-2">
                <p className="body-xxs-regular text-theme-muted">Unrealized</p>
                <p className="body-xs-medium text-theme-primary">{formatNum(Number(pnlAny.unrealized ?? 0), 2)}</p>
              </div>
            </div>
          ) : null}
          <p className="body-xxs-regular text-theme-muted">Fills: {fillRows.length} | Risk Events: {eventRows.length}</p>
          {eventRows.length > 0 && (
            <div className="mt-2 max-h-32 overflow-auto space-y-1">
              {eventRows.slice(0, 10).map((ev, idx) => (
                <div key={`ev-${idx}`} className="rounded-sm bg-theme-secondary p-1.5">
                  <p className="body-xxs-regular text-theme-primary">
                    {String(ev.event_type ?? ev.type ?? "-")} | {String(ev.timestamp ?? ev.at ?? "-")}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {limits ? (
        <div className="mt-3 rounded-sm border border-theme-outline bg-theme-primary p-3">
          <h3 className="body-sm-medium text-theme-primary mb-2">Risk Limits</h3>
          <pre className="max-h-32 overflow-auto rounded-sm bg-theme-secondary p-2 text-[11px] text-theme-muted">
            {JSON.stringify(limits, null, 2)}
          </pre>
        </div>
      ) : null}
    </div>
  );
}

export const Route = createFileRoute("/execution")({
  component: ExecutionPage,
});
