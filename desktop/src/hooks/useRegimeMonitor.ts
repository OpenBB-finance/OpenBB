import { useEffect, useMemo, useState } from "react";
import { createRegimeStreamUrl } from "../lib/macroApi";
import { openOpenBBSseStream } from "../lib/openbbSse";
import type { MacroRegimePoint, RegimeStreamEvent, RegimeTransitionItem } from "../types/macro";

interface UseRegimeMonitorResult {
  latestScores: MacroRegimePoint | null;
  currentLabel: string | null;
  transition: RegimeTransitionItem | null;
  isConnected: boolean;
  lastUpdated: string | null;
}

function isRegimePoint(value: unknown): value is MacroRegimePoint {
  if (!value || typeof value !== "object") {
    return false;
  }
  const row = value as Record<string, unknown>;
  return (
    typeof row.date === "string" &&
    typeof row.risk_on_score === "number" &&
    typeof row.inflation_score === "number" &&
    typeof row.growth_score === "number" &&
    typeof row.liquidity_score === "number" &&
    typeof row.credit_stress_score === "number"
  );
}

export function useRegimeMonitor(baseUrl: string | null, intervalSec = 60): UseRegimeMonitorResult {
  const [latestScores, setLatestScores] = useState<MacroRegimePoint | null>(null);
  const [currentLabel, setCurrentLabel] = useState<string | null>(null);
  const [transition, setTransition] = useState<RegimeTransitionItem | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  const streamUrl = useMemo(() => {
    if (!baseUrl) {
      return null;
    }
    return createRegimeStreamUrl(baseUrl, intervalSec);
  }, [baseUrl, intervalSec]);

  useEffect(() => {
    if (!streamUrl) {
      setIsConnected(false);
      return;
    }

    const stream = openOpenBBSseStream(streamUrl, {
      eventTypes: ["scores_update", "transition"],
      onOpen: () => setIsConnected(true),
      onEvent: (event) => {
        if (event.type === "scores_update") {
          try {
            const payload = JSON.parse(event.data) as RegimeStreamEvent;
            if (isRegimePoint(payload.data)) {
              setLatestScores(payload.data);
            }
            setCurrentLabel(payload.label ?? null);
            setLastUpdated(payload.timestamp ?? new Date().toISOString());
          } catch {
            // Ignore malformed SSE events.
          }
          return;
        }

        if (event.type === "transition") {
          try {
            const payload = JSON.parse(event.data) as RegimeStreamEvent;
            setTransition({
              date: payload.timestamp ?? new Date().toISOString(),
              axis: "label",
              from_score: 0,
              to_score: 0,
              delta: 0,
              direction: "rising",
              severity: "minor",
            });
            setCurrentLabel(payload.to_label ?? payload.label ?? null);
            setLastUpdated(payload.timestamp ?? new Date().toISOString());
          } catch {
            // Ignore malformed SSE events.
          }
        }
      },
      onConnectionError: () => setIsConnected(false),
    });

    return () => {
      stream.close();
      setIsConnected(false);
    };
  }, [streamUrl]);

  return {
    latestScores,
    currentLabel,
    transition,
    isConnected,
    lastUpdated,
  };
}
