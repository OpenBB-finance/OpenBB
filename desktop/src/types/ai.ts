export type AiRetrievalMode = "semantic" | "lexical";
export type AiChatRole = "user" | "assistant";

export interface AiStatus {
  repoRoot: string | null;
  repoReady: boolean;
  ollamaReachable: boolean;
  chatModel: string | null;
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
  timingMs: number;
  retrievalMode: AiRetrievalMode;
}
