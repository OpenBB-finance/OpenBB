import { invoke } from "@tauri-apps/api/core";
import { isTauriRuntimeAvailable } from "./tauriRuntime";
import type { AiAskRequest, AiAskResponse, AiIndexResult, AiStatus } from "../types/ai";

const DEFAULT_AI_DIRECTORY = ".";
const BROWSER_AI_BASE = "/__ai";

function toTauriRuntimeError(error: unknown): Error {
  if (error instanceof Error) {
    if (/undefined.*invoke/i.test(error.message) || /__TAURI_INTERNALS__/i.test(error.message)) {
      return new Error("The AI tab requires the Tauri desktop runtime. Browser-only mode is not supported.");
    }
    return error;
  }
  return new Error("The AI tab requires the Tauri desktop runtime. Browser-only mode is not supported.");
}

async function invokeAiCommand<T>(command: string, payload?: Record<string, unknown>): Promise<T> {
  try {
    return await invoke<T>(command, payload);
  } catch (error) {
    throw toTauriRuntimeError(error);
  }
}

async function browserAiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BROWSER_AI_BASE}${path}`, init);
  const payload = await response.json().catch(() => ({})) as { error?: string };

  if (!response.ok) {
    throw new Error(payload.error || `AI browser fallback returned ${response.status}.`);
  }

  return payload as T;
}

export async function getAiStatus(defaultDir = DEFAULT_AI_DIRECTORY): Promise<AiStatus> {
  if (!isTauriRuntimeAvailable() && import.meta.env.DEV) {
    return browserAiFetch<AiStatus>(`/status?defaultDir=${encodeURIComponent(defaultDir)}`);
  }
  return invokeAiCommand<AiStatus>("get_ai_status", { defaultDir });
}

export async function buildAiIndex(repoRoot: string, force = false): Promise<AiIndexResult> {
  if (!isTauriRuntimeAvailable() && import.meta.env.DEV) {
    return browserAiFetch<AiIndexResult>("/index", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repoRoot, force }),
    });
  }
  return invokeAiCommand<AiIndexResult>("build_ai_index", { repoRoot, force });
}

export async function clearAiIndex(repoRoot: string): Promise<{ ok: boolean }> {
  if (!isTauriRuntimeAvailable() && import.meta.env.DEV) {
    return browserAiFetch<{ ok: boolean }>("/clear", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repoRoot }),
    });
  }
  return invokeAiCommand<{ ok: boolean }>("clear_ai_index", { repoRoot });
}

export async function askAiQuestion(request: AiAskRequest): Promise<AiAskResponse> {
  if (!isTauriRuntimeAvailable() && import.meta.env.DEV) {
    return browserAiFetch<AiAskResponse>("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ request }),
    });
  }
  return invokeAiCommand<AiAskResponse>("ask_ai_question", { request });
}

export async function warmAiChatModel(defaultDir = DEFAULT_AI_DIRECTORY): Promise<{ ok: boolean; usedModel: string | null }> {
  if (!isTauriRuntimeAvailable() && import.meta.env.DEV) {
    return browserAiFetch<{ ok: boolean; usedModel: string | null }>("/warmup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ defaultDir }),
    });
  }
  return invokeAiCommand<{ ok: boolean; usedModel: string | null }>("warm_ai_chat_model", { defaultDir });
}
