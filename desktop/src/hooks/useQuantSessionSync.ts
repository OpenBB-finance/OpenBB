import { useEffect } from "react";
import type { Dispatch, SetStateAction } from "react";
import { VALID_MODEL_NAMES } from "../lib/quantConfig";
import type { ModelName } from "../types/quant";

type SessionPatch = {
  run_id?: string;
  model_name?: ModelName;
};

interface UseQuantSessionSyncOptions {
  sessionRunId: string;
  sessionModelName: ModelName;
  runId: string | null;
  selectedModel: ModelName;
  setSelectedModel: Dispatch<SetStateAction<ModelName>>;
  setRunIdInput: Dispatch<SetStateAction<string>>;
  setRunId: (runId: string) => void;
  setModelName: (modelName: ModelName) => void;
  patchSession: (patch: SessionPatch) => void;
}

export function useQuantSessionSync({
  sessionRunId,
  sessionModelName,
  runId,
  selectedModel,
  setSelectedModel,
  setRunIdInput,
  setRunId,
  setModelName,
  patchSession,
}: UseQuantSessionSyncOptions): void {
  useEffect(() => {
    setSelectedModel(sessionModelName);
  }, [sessionModelName, setSelectedModel]);

  useEffect(() => {
    setRunIdInput(sessionRunId);
  }, [sessionRunId, setRunIdInput]);

  useEffect(() => {
    const search = new URLSearchParams(window.location.search);
    const queryRunId = search.get("run_id")?.trim();
    const queryModel = search.get("model") || search.get("model_name");
    if (queryRunId) {
      setRunId(queryRunId);
      setRunIdInput(queryRunId);
    }
    if (queryModel && VALID_MODEL_NAMES.includes(queryModel as ModelName)) {
      const modelName = queryModel as ModelName;
      setSelectedModel(modelName);
      setModelName(modelName);
    }
  }, [setModelName, setRunId, setRunIdInput, setSelectedModel]);

  useEffect(() => {
    if (!runId) {
      return;
    }
    setRunId(runId);
    patchSession({
      run_id: runId,
      model_name: selectedModel,
    });
    setRunIdInput(runId);
  }, [patchSession, runId, selectedModel, setRunId, setRunIdInput]);
}
