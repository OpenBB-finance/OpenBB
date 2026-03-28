import { invoke } from "@tauri-apps/api/core";
import { isTauriRuntimeAvailable } from "./tauriRuntime";
import type {
  AiAskRequest,
  AiAskResponse,
  AiGatewaySettings,
  AiGatewayStatus,
  AiIndexResult,
  AiApprovalDecision,
  AiRunCreated,
  AiRunEvent,
  AiRunRequest,
  AiStatus,
  SessionDetail,
  SessionSummary,
} from "../types/ai";

const DEFAULT_AI_DIRECTORY = ".";
const DEV_AI_BASE = "/__ai/v1";

interface AiGatewayInfo {
  baseUrl: string;
  ready: boolean;
  degraded: boolean;
  settingsPath: string;
}

let cachedGatewayInfo: AiGatewayInfo | null = null;

function toTauriRuntimeError(error: unknown): Error {
  if (error instanceof Error) {
    if (/undefined.*invoke/i.test(error.message) || /__TAURI_INTERNALS__/i.test(error.message)) {
      return new Error("The AI tab requires the Tauri desktop runtime or the dev AI gateway.");
    }
    return error;
  }
  return new Error("The AI tab requires the Tauri desktop runtime or the dev AI gateway.");
}

async function invokeAiCommand<T>(command: string, payload?: Record<string, unknown>): Promise<T> {
  try {
    return await invoke<T>(command, payload);
  } catch (error) {
    throw toTauriRuntimeError(error);
  }
}

async function resolveGatewayBaseUrl(): Promise<string> {
  if (!isTauriRuntimeAvailable() && import.meta.env.DEV) {
    return DEV_AI_BASE;
  }
  if (cachedGatewayInfo?.ready && cachedGatewayInfo.baseUrl) {
    return `${cachedGatewayInfo.baseUrl}/v1`;
  }
  cachedGatewayInfo = await invokeAiCommand<AiGatewayInfo>("get_ai_gateway_info");
  return `${cachedGatewayInfo.baseUrl}/v1`;
}

async function gatewayFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const baseUrl = await resolveGatewayBaseUrl();
  const response = await fetch(`${baseUrl}${path}`, init);
  const text = await response.text();
  if (!response.ok) {
    throw new Error(text || `AI gateway returned ${response.status}.`);
  }
  if (!text) {
    return {} as T;
  }
  return JSON.parse(text) as T;
}

export async function getAiGatewayStatus(defaultDir = DEFAULT_AI_DIRECTORY): Promise<AiGatewayStatus> {
  return gatewayFetch<AiGatewayStatus>(`/status?workspacePath=${encodeURIComponent(defaultDir)}`);
}

export async function getAiSettings(): Promise<AiGatewaySettings> {
  return gatewayFetch<AiGatewaySettings>("/settings");
}

export async function updateAiSettings(settings: AiGatewaySettings): Promise<AiGatewaySettings> {
  return gatewayFetch<AiGatewaySettings>("/settings", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(settings),
  });
}

export async function buildAiIndex(workspacePath: string, force = false): Promise<AiIndexResult> {
  return gatewayFetch<AiIndexResult>("/index/build", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ workspacePath, force }),
  });
}

export async function clearAiIndex(workspacePath: string): Promise<{ ok: boolean }> {
  return gatewayFetch<{ ok: boolean }>("/index/clear", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ workspacePath }),
  });
}

export async function createAiRun(request: AiRunRequest): Promise<AiRunCreated> {
  return gatewayFetch<AiRunCreated>("/runs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
}

export async function listAiSessions(): Promise<SessionSummary[]> {
  return gatewayFetch<SessionSummary[]>("/sessions");
}

export async function getAiSession(sessionId: string): Promise<SessionDetail> {
  return gatewayFetch<SessionDetail>(`/sessions/${encodeURIComponent(sessionId)}`);
}

export async function respondToAiApproval(
  approvalId: string,
  decision: AiApprovalDecision,
): Promise<{ ok: boolean }> {
  return gatewayFetch<{ ok: boolean }>(`/approvals/${encodeURIComponent(approvalId)}/respond`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(decision),
  });
}

export async function cancelAiRun(runId: string): Promise<{ ok: boolean }> {
  return gatewayFetch<{ ok: boolean }>(`/runs/${encodeURIComponent(runId)}/cancel`, {
    method: "POST",
  });
}

export async function streamAiRun(
  runId: string,
  onEvent: (event: AiRunEvent) => void,
): Promise<void> {
  const baseUrl = await resolveGatewayBaseUrl();
  const response = await fetch(`${baseUrl}/runs/${encodeURIComponent(runId)}/stream`);
  if (!response.ok || !response.body) {
    throw new Error(`Failed to open AI run stream (${response.status}).`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    let separatorIndex = buffer.indexOf("\n\n");
    while (separatorIndex >= 0) {
      const rawEvent = buffer.slice(0, separatorIndex);
      buffer = buffer.slice(separatorIndex + 2);
      const dataLine = rawEvent
        .split("\n")
        .find((line) => line.startsWith("data:"));
      if (dataLine) {
        onEvent(JSON.parse(dataLine.slice(5).trim()) as AiRunEvent);
      }
      separatorIndex = buffer.indexOf("\n\n");
    }
  }
}

export async function askAiQuestionGateway(request: AiRunRequest): Promise<AiAskResponse> {
  const created = await createAiRun(request);
  let answer = "";
  let citations: AiAskResponse["citations"] = [];
  let usedModel = "unknown";
  let attemptedModels: string[] | undefined;
  let modelTotalMs: number | null | undefined;
  let loadMs: number | null | undefined;
  let promptEvalMs: number | null | undefined;
  let evalMs: number | null | undefined;
  let timingMs = 0;
  let retrievalMode: AiAskResponse["retrievalMode"] = "lexical";

  await streamAiRun(created.runId, (event) => {
    switch (event.type) {
      case "messageFinal":
        answer = event.text;
        break;
      case "error":
        throw new Error(event.message);
      case "done": {
        const usage = event.usage ?? {};
        citations = (usage.citations as AiAskResponse["citations"] | undefined) ?? [];
        usedModel = (usage.usedModel as string | undefined) ?? usedModel;
        attemptedModels = usage.attemptedModels as string[] | undefined;
        modelTotalMs = (usage.modelTotalMs as number | null | undefined) ?? modelTotalMs;
        loadMs = (usage.loadMs as number | null | undefined) ?? loadMs;
        promptEvalMs = (usage.promptEvalMs as number | null | undefined) ?? promptEvalMs;
        evalMs = (usage.evalMs as number | null | undefined) ?? evalMs;
        timingMs = (usage.timingMs as number | undefined) ?? timingMs;
        retrievalMode = (usage.retrievalMode as AiAskResponse["retrievalMode"] | undefined) ?? retrievalMode;
        break;
      }
      default:
        break;
    }
  });

  return {
    answer,
    citations,
    usedModel,
    attemptedModels,
    modelTotalMs,
    loadMs,
    promptEvalMs,
    evalMs,
    timingMs,
    retrievalMode,
  };
}

// Deprecated compatibility wrappers.
export async function getAiStatus(defaultDir = DEFAULT_AI_DIRECTORY): Promise<AiStatus> {
  const status = await getAiGatewayStatus(defaultDir);
  const ollama = status.providers.find((provider) => provider.provider === "ollama");
  return {
    repoRoot: status.workspacePath ?? null,
    repoReady: status.workspaceReady,
    ollamaReachable: Boolean(ollama?.reachable),
    chatModel: ollama?.defaultModel ?? null,
    chatCandidates: ollama?.models ?? [],
    embeddingModel: status.index.embeddingModel ?? null,
    availableModels: ollama?.models ?? [],
    indexReady: status.index.ready,
    lastIndexedAt: status.index.lastIndexedAt ?? null,
    chunkCount: status.index.chunkCount,
    mode: status.index.mode === "lexical" ? "lexical" : "semantic",
  };
}

export async function askAiQuestion(request: AiAskRequest): Promise<AiAskResponse> {
  const settings = await getAiSettings();
  const latestUserPrompt = [...request.messages]
    .reverse()
    .find((message) => message.role === "user")?.content
    ?? request.messages[request.messages.length - 1]?.content
    ?? "";

  return askAiQuestionGateway({
    provider: settings.defaultProvider,
    mode: settings.defaultMode,
    workspacePath: request.repoRoot,
    prompt: latestUserPrompt,
    supplementalContext: request.supplementalContext,
    retrieval: {
      enabled: !request.supplementalOnly,
      topK: request.maxContextChunks ?? settings.retrieval.topK,
      strategy: settings.retrieval.strategy,
    },
    execution: {
      sandbox: "read-only",
      approvalPolicy: "default",
    },
  });
}

export async function warmAiChatModel(_defaultDir = DEFAULT_AI_DIRECTORY): Promise<{ ok: boolean; usedModel: string | null }> {
  const settings = await getAiSettings();
  return {
    ok: true,
    usedModel: settings.providers.ollama.defaultChatModel ?? null,
  };
}
