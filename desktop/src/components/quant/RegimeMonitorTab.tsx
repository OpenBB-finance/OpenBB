import { useCallback, useEffect, useMemo, useState } from "react";
import {
  fetchHmmRegime,
  fetchMacroAlerts,
  fetchMacroRegime,
  fetchRegimeSchedulerStatus,
  fetchRegimeTransitions,
  triggerRegimeRefresh,
} from "../../lib/macroApi";
import type {
  HmmRegimePayload,
  MacroAlertsResponse,
  MacroRegimeResponse,
  RegimeSchedulerStatus,
  RegimeTransitionResponse,
} from "../../types/macro";
import { useRegimeMonitor } from "../../hooks/useRegimeMonitor";
import { RegimeLiveIndicator } from "./RegimeLiveIndicator";
import { RegimeStatusCard } from "./RegimeStatusCard";
import { RegimeRadarChart } from "./RegimeRadarChart";
import { RegimeTimelineChart } from "./RegimeTimelineChart";
import { RegimeTransitionTable } from "./RegimeTransitionTable";
import { MacroAlertsPanel } from "./MacroAlertsPanel";

interface RegimeMonitorTabProps {
  baseUrl: string | null;
}

export function RegimeMonitorTab({ baseUrl }: RegimeMonitorTabProps) {
  const [regimeData, setRegimeData] = useState<MacroRegimeResponse | null>(null);
  const [hmmData, setHmmData] = useState<HmmRegimePayload | null>(null);
  const [transitions, setTransitions] = useState<RegimeTransitionResponse | null>(null);
  const [alerts, setAlerts] = useState<MacroAlertsResponse | null>(null);
  const [schedulerStatus, setSchedulerStatus] = useState<RegimeSchedulerStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { latestScores, currentLabel, transition, isConnected, lastUpdated } = useRegimeMonitor(baseUrl);

  const load = useCallback(async () => {
    if (!baseUrl) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const [regime, hmm, transitionPayload, alertPayload, scheduler] = await Promise.all([
        fetchMacroRegime(baseUrl, { freq: "W", fill: "ffill" }),
        fetchHmmRegime(baseUrl),
        fetchRegimeTransitions(baseUrl),
        fetchMacroAlerts(baseUrl),
        fetchRegimeSchedulerStatus(baseUrl),
      ]);
      setRegimeData(regime);
      setHmmData(hmm);
      setTransitions(transitionPayload);
      setAlerts(alertPayload);
      setSchedulerStatus(scheduler);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load regime monitor data.");
    } finally {
      setLoading(false);
    }
  }, [baseUrl]);

  useEffect(() => {
    void load();
  }, [load]);

  const mergedTransitions = useMemo(() => {
    const rows = [...(transitions?.transitions ?? [])];
    if (transition) {
      rows.unshift(transition);
    }
    return rows;
  }, [transition, transitions?.transitions]);

  const handleRefresh = useCallback(async () => {
    if (!baseUrl) {
      return;
    }
    try {
      await triggerRegimeRefresh(baseUrl);
    } finally {
      await load();
    }
  }, [baseUrl, load]);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <RegimeLiveIndicator connected={isConnected} lastUpdated={lastUpdated} />
        <div className="flex items-center gap-2">
          <button
            type="button"
            className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
            onClick={() => void handleRefresh()}
            disabled={!baseUrl || loading}
          >
            {loading ? "Refreshing..." : "Refresh Now"}
          </button>
          <span className="body-xxs-regular text-theme-muted">
            Scheduler: {schedulerStatus?.running ? "running" : "stopped"}
          </span>
        </div>
      </div>

      {error ? (
        <div className="rounded-sm border border-red-500/50 bg-red-500/10 p-2">
          <p className="body-xs-medium text-red-300">{error}</p>
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <RegimeStatusCard label={currentLabel} scores={latestScores ?? regimeData?.latest ?? null} />
        <RegimeRadarChart scores={latestScores ?? regimeData?.latest ?? null} />
      </div>

      <RegimeTimelineChart hmmData={hmmData} regimeData={regimeData} />

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <RegimeTransitionTable transitions={mergedTransitions} />
        <MacroAlertsPanel alerts={alerts} />
      </div>
    </div>
  );
}
