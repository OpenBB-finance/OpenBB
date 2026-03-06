import { useEffect, useState } from "react";
import { resolveUniverse } from "../lib/quantApi";
import { toApiUniverseId } from "../lib/quantConfig";
import type { UniverseResolveState, UniverseSetId } from "../lib/quantConfig";

type BackendConnection = { connected: boolean; baseUrl: string } | null;

interface UseQuantUniverseResolveOptions {
  backend: BackendConnection;
  isUniverseSetMode: boolean;
  selectedUniverseSet: UniverseSetId;
  minimumRequired: number;
}

const INITIAL_UNIVERSE_RESOLVE_STATE: UniverseResolveState = {
  status: "idle",
  message: null,
  count: null,
  minimumRequired: 0,
  meetsMinimum: true,
};

export function useQuantUniverseResolve({
  backend,
  isUniverseSetMode,
  selectedUniverseSet,
  minimumRequired,
}: UseQuantUniverseResolveOptions) {
  const [universeResolveState, setUniverseResolveState] = useState<UniverseResolveState>(
    INITIAL_UNIVERSE_RESOLVE_STATE,
  );

  useEffect(() => {
    if (!isUniverseSetMode) {
      setUniverseResolveState(INITIAL_UNIVERSE_RESOLVE_STATE);
      return;
    }
    if (!backend?.connected) {
      setUniverseResolveState({
        status: "error",
        message: "OpenBB API is not connected.",
        count: null,
        minimumRequired,
        meetsMinimum: false,
      });
      return;
    }

    let cancelled = false;
    setUniverseResolveState((prev) => ({
      ...prev,
      status: "loading",
      message: null,
      count: null,
      minimumRequired,
      meetsMinimum: false,
    }));

    void (async () => {
      try {
        const resolved = await resolveUniverse(
          backend.baseUrl,
          toApiUniverseId(selectedUniverseSet),
          "train",
          false,
        );
        if (cancelled) {
          return;
        }
        const currentMinimumRequired = Number(resolved.minimum_required ?? minimumRequired);
        const meetsMinimum =
          typeof resolved.meets_minimum === "boolean"
            ? resolved.meets_minimum
            : currentMinimumRequired <= 0 || Number(resolved.count) >= currentMinimumRequired;
        setUniverseResolveState({
          status: "ok",
          message: null,
          count: Number(resolved.count),
          minimumRequired: currentMinimumRequired,
          meetsMinimum,
        });
      } catch (error) {
        if (cancelled) {
          return;
        }
        setUniverseResolveState({
          status: "error",
          message: error instanceof Error ? error.message : "Failed to resolve selected universe set.",
          count: null,
          minimumRequired,
          meetsMinimum: false,
        });
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [backend, isUniverseSetMode, minimumRequired, selectedUniverseSet]);

  const isTrainBlockedByUniverse =
    isUniverseSetMode &&
    (universeResolveState.status === "loading" ||
      universeResolveState.status === "error" ||
      universeResolveState.meetsMinimum === false);

  return {
    universeResolveState,
    isTrainBlockedByUniverse,
  };
}
