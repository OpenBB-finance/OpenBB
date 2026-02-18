import { createFileRoute } from "@tanstack/react-router";
import { useCallback, useEffect, useMemo, useState } from "react";
import { resolveOpenBBBackend } from "../lib/openbbBackend";
import {
  fetchExecutionFillsHistory,
  fetchExecutionOrdersCurrent,
  fetchExecutionPnl,
  fetchExecutionPositionsCurrent,
  fetchRiskEvents,
  fetchRiskLimits,
  probeQuantMlActivation,
  previewExecutionOrders,
  riskCheckPretrade,
  submitExecutionOrders,
} from "../lib/quantApi";
import type {
  ExecutionFillsPayload,
  ExecutionOrdersPayload,
  ExecutionPnlPayload,
  ExecutionPositionsPayload,
  ExecutionPreviewPayload,
  ExecutionSubmitPayload,
  ModelName,
  RiskEventsPayload,
  RiskLimitsPayload,
  RiskPretradePayload,
} from "../types/quant";

function toErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "Request failed";
}

function JsonBlock({ data }: { data: unknown }) {
  return (
    <pre className="max-h-48 overflow-auto rounded-sm border border-theme-outline bg-theme-secondary p-2 text-[11px] text-theme-muted">
      {JSON.stringify(data, null, 2)}
    </pre>
  );
}

const EXECUTION_ENDPOINTS = [
  "POST /api/v1/quant_ml/execution/orders/preview",
  "POST /api/v1/quant_ml/execution/orders/submit",
  "POST /api/v1/quant_ml/risk/check/pretrade",
  "GET /api/v1/quant_ml/execution/orders/current",
  "GET /api/v1/quant_ml/execution/fills/history",
  "GET /api/v1/quant_ml/execution/positions/current",
  "GET /api/v1/quant_ml/execution/pnl",
  "GET /api/v1/quant_ml/risk/limits",
  "GET /api/v1/quant_ml/risk/events",
];

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
  const [orders, setOrders] = useState<ExecutionOrdersPayload | null>(null);
  const [fills, setFills] = useState<ExecutionFillsPayload | null>(null);
  const [positions, setPositions] = useState<ExecutionPositionsPayload | null>(null);
  const [pnl, setPnl] = useState<ExecutionPnlPayload | null>(null);
  const [limits, setLimits] = useState<RiskLimitsPayload | null>(null);
  const [events, setEvents] = useState<RiskEventsPayload | null>(null);

  const canSubmit = useMemo(() => {
    if (!preview || !risk) {
      return false;
    }
    return Boolean(risk.passed) && !risk.kill_switch;
  }, [preview, risk]);

  const refreshState = useCallback(async () => {
    if (!baseUrl || !runId.trim()) {
      return;
    }
    const [nextOrders, nextFills, nextPositions, nextPnl, nextLimits, nextEvents] = await Promise.all([
      fetchExecutionOrdersCurrent(baseUrl, runId.trim(), modelName),
      fetchExecutionFillsHistory(baseUrl, runId.trim(), modelName, 200),
      fetchExecutionPositionsCurrent(baseUrl, runId.trim(), modelName),
      fetchExecutionPnl(baseUrl, runId.trim(), modelName),
      fetchRiskLimits(baseUrl, runId.trim(), modelName),
      fetchRiskEvents(baseUrl, runId.trim(), modelName, 200),
    ]);
    setOrders(nextOrders);
    setFills(nextFills);
    setPositions(nextPositions);
    setPnl(nextPnl);
    setLimits(nextLimits);
    setEvents(nextEvents);
  }, [baseUrl, modelName, runId]);

  const handlePreview = useCallback(async () => {
    if (!baseUrl || !runId.trim()) {
      setErrorMessage("run_id is required");
      return;
    }
    setIsBusy(true);
    setErrorMessage(null);
    try {
      const previewPayload = await previewExecutionOrders(baseUrl, {
        run_id: runId.trim(),
        model_name: modelName,
      });
      setPreview(previewPayload);
      const riskPayload = await riskCheckPretrade(baseUrl, {
        run_id: runId.trim(),
        model_name: modelName,
      });
      setRisk(riskPayload);
      await refreshState();
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    } finally {
      setIsBusy(false);
    }
  }, [baseUrl, modelName, refreshState, runId]);

  const handleSubmit = useCallback(async () => {
    if (!canSubmit || !baseUrl || !runId.trim()) {
      return;
    }
    setIsBusy(true);
    setErrorMessage(null);
    try {
      const submitPayload = await submitExecutionOrders(baseUrl, {
        run_id: runId.trim(),
        model_name: modelName,
      });
      setSubmit(submitPayload);
      await refreshState();
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    } finally {
      setIsBusy(false);
    }
  }, [baseUrl, canSubmit, modelName, refreshState, runId]);

  useEffect(() => {
    void (async () => {
      try {
        const backend = await resolveOpenBBBackend();
        setBaseUrl(backend.baseUrl);
        const activation = await probeQuantMlActivation(backend.baseUrl);
        if (!activation.available) {
          setActivationMessage(
            activation.detail || "quant_ml extension unavailable. Execution actions are disabled.",
          );
        } else {
          setActivationMessage(null);
        }
      } catch (error) {
        setErrorMessage(toErrorMessage(error));
      }
    })();
  }, []);

  return (
    <div className="h-full min-h-0 overflow-auto py-4">
      <div className="mb-3">
        <h1 className="body-lg-medium text-theme-primary">Execution / Risk</h1>
        <p className="body-sm-regular text-theme-muted">Preview - Pretrade Risk - Submit workflow.</p>
      </div>

      <div className="mb-3 grid grid-cols-1 gap-2 md:grid-cols-3">
        <input
          className="rounded-sm border border-theme-outline bg-theme-secondary px-2 py-2 body-xs-regular text-theme-primary"
          placeholder="run_id"
          value={runId}
          onChange={(event) => setRunId(event.target.value)}
        />
        <select
          className="rounded-sm border border-theme-outline bg-theme-secondary px-2 py-2 body-xs-regular text-theme-primary"
          value={modelName}
          onChange={(event) => setModelName(event.target.value as ModelName)}
        >
          <option value="lgbm_ranker">lgbm_ranker</option>
          <option value="xgb_lstm">xgb_lstm</option>
        </select>
        <div className="flex gap-2">
          <button
            type="button"
            className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
            onClick={() => void handlePreview()}
            disabled={isBusy || Boolean(activationMessage)}
          >
            Preview + Risk Check
          </button>
          <button
            type="button"
            className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
            onClick={() => void handleSubmit()}
            disabled={isBusy || !canSubmit || Boolean(activationMessage)}
          >
            Submit
          </button>
        </div>
      </div>

      {errorMessage ? <p className="mb-3 body-xs-medium text-red-400">{errorMessage}</p> : null}
      {activationMessage ? <p className="mb-3 body-xs-medium text-amber-300">{activationMessage}</p> : null}
      {risk && (!risk.passed || risk.kill_switch) ? (
        <p className="mb-3 body-xs-medium text-amber-400">Submit blocked by risk check or kill switch.</p>
      ) : null}

      <div className="mb-3 rounded-sm border border-theme-outline bg-theme-secondary p-2">
        <p className="body-xs-medium text-theme-primary">Execution endpoints in use</p>
        <p className="body-xxs-regular text-theme-muted mt-1">{EXECUTION_ENDPOINTS.join(" | ")}</p>
      </div>

      <div className="grid grid-cols-1 gap-3 xl:grid-cols-2">
        <JsonBlock data={{ preview, risk, submit }} />
        <JsonBlock data={{ limits, events }} />
        <JsonBlock data={{ orders, fills }} />
        <JsonBlock data={{ positions, pnl }} />
      </div>
    </div>
  );
}

export const Route = createFileRoute("/execution")({
  component: ExecutionPage,
});
