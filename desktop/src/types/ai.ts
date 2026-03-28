export type ProviderId = "ollama" | "codex" | "gemini";
export type AiMode = "ask" | "agent";
export type RetrievalStrategy = "lexical" | "semantic" | "hybrid";
export type SandboxMode = "read-only" | "workspace-write" | "danger-full-access";
export type ApprovalPolicy = "default" | "on-request" | "auto_edit" | "yolo";
export type AiRetrievalMode = "semantic" | "lexical" | "supplemental";
export type AiChatRole = "user" | "assistant";

export interface ProviderCapabilities {
  chat: boolean;
  streaming: boolean;
  retrieval: boolean;
  embeddings: boolean;
  resumeSession: boolean;
  approvals: boolean;
  fileEdits: boolean;
  shellExec: boolean;
}

export interface ProviderError {
  code: string;
  message: string;
  detail?: string | null;
}

export interface ProviderStatus {
  provider: ProviderId;
  installed: boolean;
  reachable: boolean;
  authenticated: boolean;
  degraded: boolean;
  version?: string | null;
  mode?: string | null;
  capabilities: ProviderCapabilities;
  models: string[];
  defaultModel?: string | null;
  error?: ProviderError | null;
}

export interface IndexStatus {
  workspacePath?: string | null;
  ready: boolean;
  lastIndexedAt?: string | null;
  chunkCount: number;
  mode: RetrievalStrategy;
  revision?: string | null;
  embeddingProvider?: ProviderId | null;
  embeddingModel?: string | null;
  stale: boolean;
}

export interface FeatureFlags {
  codexAgentEnabled: boolean;
  geminiAgentEnabled: boolean;
}

export interface AiGatewayStatus {
  gatewayVersion: string;
  workspacePath?: string | null;
  workspaceReady: boolean;
  defaultProvider: ProviderId;
  defaultMode: AiMode;
  providers: ProviderStatus[];
  index: IndexStatus;
  settingsPath?: string | null;
  featureFlags: FeatureFlags;
}

export interface RetrievalOptions {
  enabled: boolean;
  topK: number;
  strategy: RetrievalStrategy;
}

export interface ExecutionOptions {
  sandbox: SandboxMode;
  approvalPolicy: ApprovalPolicy;
}

export interface AiRunRequest {
  provider: ProviderId;
  mode: AiMode;
  sessionId?: string;
  workspacePath: string;
  prompt: string;
  model?: string;
  supplementalContext?: string;
  retrieval?: RetrievalOptions;
  execution?: ExecutionOptions;
}

export interface AiRunCreated {
  runId: string;
  sessionId?: string | null;
  streamUrl: string;
}

export interface SessionSummary {
  sessionId: string;
  provider: ProviderId;
  mode: AiMode;
  status: "queued" | "running" | "completed" | "failed" | "cancelled";
  title: string;
  latestRunId: string;
  updatedAt: string;
}

export interface PendingApprovalSummary {
  approvalId: string;
  kind: string;
  summary: string;
}

export interface SessionDetail {
  summary: SessionSummary;
  pendingApprovals: PendingApprovalSummary[];
  recentEvents: AiRunEvent[];
}

export type AiRunEvent =
  | { type: "status"; phase: string }
  | { type: "messageDelta"; text: string }
  | { type: "messageFinal"; text: string }
  | { type: "toolStarted"; name: string; input?: unknown }
  | { type: "toolOutput"; name: string; text: string }
  | { type: "approvalRequest"; approvalId: string; kind: string; payload: unknown }
  | { type: "diffPreview"; files: Array<{ path: string; diff: string }> }
  | { type: "error"; code: string; message: string; detail?: unknown }
  | { type: "done"; usage?: Record<string, unknown> | null };

export interface AiApprovalDecision {
  decision: "accept" | "acceptForSession" | "decline" | "cancel";
  scope?: "once" | "session";
}

export interface GatewayRetrievalSettings {
  strategy: RetrievalStrategy;
  topK: number;
  allowRepoSummary: boolean;
}

export interface OllamaProviderSettings {
  enabled: boolean;
  baseUrl: string;
  defaultChatModel?: string | null;
  defaultEmbeddingModel?: string | null;
  keepAlive: string;
  requestTimeoutMs: number;
}

export interface GenericCliProviderSettings {
  enabled: boolean;
  askTransport: string;
  agentTransport: string;
  sandbox: SandboxMode;
  approvalPolicy: ApprovalPolicy;
}

export interface AiGatewaySettings {
  defaultProvider: ProviderId;
  defaultMode: AiMode;
  retrieval: GatewayRetrievalSettings;
  providers: {
    ollama: OllamaProviderSettings;
    codex: GenericCliProviderSettings;
    gemini: GenericCliProviderSettings;
  };
  featureFlags: FeatureFlags;
}

// Deprecated compatibility wrappers for the legacy AI tab flow.
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
  mode: "semantic" | "lexical";
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

export interface AiCitation {
  path: string;
  startLine: number;
  endLine: number;
  score: number;
}

export interface AiAskRequest {
  repoRoot: string;
  messages: Array<{ role: AiChatRole; content: string }>;
  maxContextChunks?: number;
  supplementalContext?: string;
  supplementalOnly?: boolean;
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
