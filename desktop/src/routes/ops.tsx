import { createFileRoute } from "@tanstack/react-router";
import { useCallback, useEffect, useState } from "react";
import { resolveOpenBBBackend } from "../lib/openbbBackend";
import { fetchOpsStatus, probeQuantMlActivation } from "../lib/quantApi";
import type { OpsStatusPayload } from "../types/quant";

function toErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "Request failed";
}

const OPS_ENDPOINTS = ["GET /api/v1/quant_ml/ops/status"];

function OpsPage() {
  const [baseUrl, setBaseUrl] = useState("");
  const [payload, setPayload] = useState<OpsStatusPayload | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activationMessage, setActivationMessage] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const refresh = useCallback(async () => {
    if (!baseUrl) {
      return;
    }
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const next = await fetchOpsStatus(baseUrl);
      setPayload(next);
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  }, [baseUrl]);

  useEffect(() => {
    void (async () => {
      try {
        const backend = await resolveOpenBBBackend();
        setBaseUrl(backend.baseUrl);
        const activation = await probeQuantMlActivation(backend.baseUrl);
        if (!activation.available) {
          setActivationMessage(
            activation.detail || "quant_ml extension unavailable. Ops status endpoint is inactive.",
          );
        } else {
          setActivationMessage(null);
        }
      } catch (error) {
        setErrorMessage(toErrorMessage(error));
      }
    })();
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return (
    <div className="h-full min-h-0 overflow-auto py-4">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <h1 className="body-lg-medium text-theme-primary">Ops</h1>
          <p className="body-sm-regular text-theme-muted">Jobs / cache versions / latest runs / macro health.</p>
        </div>
        <button type="button" className="button-secondary rounded-sm px-3 py-2 body-xs-medium" onClick={() => void refresh()} disabled={isLoading}>
          Refresh
        </button>
      </div>

      {errorMessage ? <p className="mb-2 body-xs-medium text-red-400">{errorMessage}</p> : null}
      {activationMessage ? <p className="mb-2 body-xs-medium text-amber-300">{activationMessage}</p> : null}
      {actionMessage ? <p className="mb-2 body-xs-medium text-sky-300">{actionMessage}</p> : null}

      <div className="mb-3 rounded-sm border border-theme-outline bg-theme-secondary p-2">
        <p className="body-xs-medium text-theme-primary">Ops endpoints in use</p>
        <p className="body-xxs-regular text-theme-muted mt-1">{OPS_ENDPOINTS.join(" | ")}</p>
      </div>

      <div className="mb-3 flex gap-2">
        <button
          type="button"
          className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
          onClick={() => setActionMessage("Restart action is not exposed by current backend API.")}
        >
          Restart Jobs
        </button>
        <button
          type="button"
          className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
          onClick={() => setActionMessage("Cleanup action is not exposed by current backend API.")}
        >
          Cleanup Cache
        </button>
      </div>

      <pre className="max-h-[70vh] overflow-auto rounded-sm border border-theme-outline bg-theme-secondary p-3 text-[11px] text-theme-muted">
        {JSON.stringify(payload, null, 2)}
      </pre>
    </div>
  );
}

export const Route = createFileRoute("/ops")({
  component: OpsPage,
});
