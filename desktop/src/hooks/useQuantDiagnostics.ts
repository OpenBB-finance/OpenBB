import { useEffect } from "react";
import {
  fetchAlertsCurrent,
  fetchModelIc,
  fetchModelPerformance,
  fetchModelRegime,
  fetchModelShap,
  fetchPortfolioExposure,
  fetchPortfolioRisk,
  fetchRegimeCurrent,
} from "../lib/quantApi";
import type { Dispatch, SetStateAction } from "react";
import type {
  AlertsPayload,
  ModelICPayload,
  ModelName,
  ModelPerformancePayload,
  ModelRegimePayload,
  ModelShapPayload,
  PortfolioExposurePayload,
  PortfolioRiskPayload,
  RegimeCurrentPayload,
  RunStatusPayload,
} from "../types/quant";

type BackendConnection = { connected: boolean; baseUrl: string } | null;

interface UseQuantDiagnosticsOptions {
  backend: BackendConnection;
  runId: string | null;
  runStatus: RunStatusPayload | null;
  selectedModel: ModelName;
  setModelIcPayload: Dispatch<SetStateAction<ModelICPayload | null>>;
  setModelRegimePayload: Dispatch<SetStateAction<ModelRegimePayload | null>>;
  setModelShapPayload: Dispatch<SetStateAction<ModelShapPayload | null>>;
  setModelPerformancePayload: Dispatch<
    SetStateAction<ModelPerformancePayload | null>
  >;
  setPortfolioExposurePayload: Dispatch<
    SetStateAction<PortfolioExposurePayload | null>
  >;
  setPortfolioRiskPayload: Dispatch<SetStateAction<PortfolioRiskPayload | null>>;
  setRegimeCurrentPayload: Dispatch<SetStateAction<RegimeCurrentPayload | null>>;
  setCurrentAlertsPayload: Dispatch<SetStateAction<AlertsPayload | null>>;
  setDiagnosticsError: Dispatch<SetStateAction<string | null>>;
}

export function useQuantDiagnostics({
  backend,
  runId,
  runStatus,
  selectedModel,
  setModelIcPayload,
  setModelRegimePayload,
  setModelShapPayload,
  setModelPerformancePayload,
  setPortfolioExposurePayload,
  setPortfolioRiskPayload,
  setRegimeCurrentPayload,
  setCurrentAlertsPayload,
  setDiagnosticsError,
}: UseQuantDiagnosticsOptions) {
  useEffect(() => {
    if (!backend?.connected || !runId || runStatus?.status !== "completed") {
      setModelIcPayload(null);
      setModelRegimePayload(null);
      setModelShapPayload(null);
      setModelPerformancePayload(null);
      setPortfolioExposurePayload(null);
      setPortfolioRiskPayload(null);
      setRegimeCurrentPayload(null);
      setCurrentAlertsPayload(null);
      setDiagnosticsError(null);
      return;
    }

    let disposed = false;
    void (async () => {
      const [
        icRes,
        regimeRes,
        shapRes,
        performanceRes,
        exposureRes,
        riskRes,
        regimeCurrentRes,
        alertsRes,
      ] = await Promise.allSettled([
        fetchModelIc(backend.baseUrl, runId, selectedModel),
        fetchModelRegime(backend.baseUrl, runId, selectedModel),
        fetchModelShap(backend.baseUrl, runId, selectedModel),
        fetchModelPerformance(backend.baseUrl, runId),
        fetchPortfolioExposure(backend.baseUrl, runId, selectedModel),
        fetchPortfolioRisk(backend.baseUrl, runId, selectedModel),
        fetchRegimeCurrent(backend.baseUrl, runId, selectedModel),
        fetchAlertsCurrent(backend.baseUrl, runId, selectedModel),
      ]);

      if (disposed) {
        return;
      }

      const errors: string[] = [];
      if (icRes.status === "fulfilled") {
        setModelIcPayload(icRes.value);
      } else {
        setModelIcPayload(null);
        errors.push(
          icRes.reason instanceof Error ? icRes.reason.message : "model/ic failed",
        );
      }
      if (regimeRes.status === "fulfilled") {
        setModelRegimePayload(regimeRes.value);
      } else {
        setModelRegimePayload(null);
        errors.push(
          regimeRes.reason instanceof Error
            ? regimeRes.reason.message
            : "model/regime failed",
        );
      }
      if (shapRes.status === "fulfilled") {
        setModelShapPayload(shapRes.value);
      } else {
        setModelShapPayload(null);
        errors.push(
          shapRes.reason instanceof Error
            ? shapRes.reason.message
            : "model/shap failed",
        );
      }
      if (performanceRes.status === "fulfilled") {
        setModelPerformancePayload(performanceRes.value);
      } else {
        setModelPerformancePayload(null);
        errors.push(
          performanceRes.reason instanceof Error
            ? performanceRes.reason.message
            : "model/performance failed",
        );
      }
      if (exposureRes.status === "fulfilled") {
        setPortfolioExposurePayload(exposureRes.value);
      } else {
        setPortfolioExposurePayload(null);
        errors.push(
          exposureRes.reason instanceof Error
            ? exposureRes.reason.message
            : "portfolio/exposure failed",
        );
      }
      if (riskRes.status === "fulfilled") {
        setPortfolioRiskPayload(riskRes.value);
      } else {
        setPortfolioRiskPayload(null);
        errors.push(
          riskRes.reason instanceof Error
            ? riskRes.reason.message
            : "portfolio/risk failed",
        );
      }
      if (regimeCurrentRes.status === "fulfilled") {
        setRegimeCurrentPayload(regimeCurrentRes.value);
      } else {
        setRegimeCurrentPayload(null);
        errors.push(
          regimeCurrentRes.reason instanceof Error
            ? regimeCurrentRes.reason.message
            : "regime/current failed",
        );
      }
      if (alertsRes.status === "fulfilled") {
        setCurrentAlertsPayload(alertsRes.value);
      } else {
        setCurrentAlertsPayload(null);
        errors.push(
          alertsRes.reason instanceof Error
            ? alertsRes.reason.message
            : "alerts/current failed",
        );
      }
      setDiagnosticsError(errors.length > 0 ? errors.join(" | ") : null);
    })();

    return () => {
      disposed = true;
    };
  }, [
    backend,
    runId,
    runStatus?.status,
    selectedModel,
    setCurrentAlertsPayload,
    setDiagnosticsError,
    setModelIcPayload,
    setModelPerformancePayload,
    setModelRegimePayload,
    setModelShapPayload,
    setPortfolioExposurePayload,
    setPortfolioRiskPayload,
    setRegimeCurrentPayload,
  ]);
}
