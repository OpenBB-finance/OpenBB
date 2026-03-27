import type { ModelName, RunHandoff } from "../types/quant";

const RUN_HANDOFF_KEY = "quant.runHandoff";

export function readRunHandoff(): RunHandoff | null {
  try {
    const raw = window.localStorage.getItem(RUN_HANDOFF_KEY);
    if (!raw) {
      return null;
    }
    return JSON.parse(raw) as RunHandoff;
  } catch {
    return null;
  }
}

export function writeRunHandoff(payload: {
  runId: string;
  modelName: ModelName;
  source: string;
  studyIds?: string[];
}): void {
  try {
    const next: RunHandoff = {
      runId: payload.runId,
      modelName: payload.modelName,
      source: payload.source,
      studyIds: payload.studyIds ?? [],
      createdAt: new Date().toISOString(),
    };
    window.localStorage.setItem(RUN_HANDOFF_KEY, JSON.stringify(next));
  } catch {
    // Local storage is best-effort only.
  }
}

export function clearRunHandoff(): void {
  try {
    window.localStorage.removeItem(RUN_HANDOFF_KEY);
  } catch {
    // Local storage is best-effort only.
  }
}
