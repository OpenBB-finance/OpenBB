export type AiRetrievalMode = "semantic" | "lexical" | "supplemental";
export type AiChatRole = "user" | "assistant";

export interface AiStatus {
  repoRoot: string | null;
  repoReady: boolean;
  ollamaReachable: boolean;
  chatModel: string | null;
  chatCandidates: string[];
  embeddingModel: string | null;
  availableModels: string[];
  indexReady: boolean;
  lastIndexedAt: string | null;
  chunkCount: number;
  mode: AiRetrievalMode;
}

export interface AiIndexResult {
  repoRoot: string;
  scannedFiles: number;
  indexedFiles: number;
  skippedFiles: number;
  chunkCount: number;
  lastIndexedAt: string;
  revision: string;
}

export interface AiAskRequest {
  repoRoot: string;
  messages: Array<{ role: AiChatRole; content: string }>;
  maxContextChunks?: number;
  supplementalContext?: string;
  supplementalOnly?: boolean;
}

export interface AiCitation {
  path: string;
  startLine: number;
  endLine: number;
  score: number;
}

export interface AiAskResponse {
  answer: string;
  citations: AiCitation[];
  usedModel: string;
  attemptedModels?: string[];
  modelTotalMs?: number | null;
  loadMs?: number | null;
  promptEvalMs?: number | null;
  evalMs?: number | null;
  timingMs: number;
  retrievalMode: AiRetrievalMode;
}
