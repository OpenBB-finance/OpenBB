pub mod errors;
pub mod http;
pub mod ollama_core;
pub mod providers;
pub mod retrieval;
pub mod sessions;
pub mod settings;
pub mod sse;

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
#[serde(rename_all = "lowercase")]
pub enum ProviderId {
    Ollama,
    Codex,
    Gemini,
}

impl ProviderId {
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Ollama => "ollama",
            Self::Codex => "codex",
            Self::Gemini => "gemini",
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum AiMode {
    Ask,
    Agent,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "kebab-case")]
pub enum RetrievalStrategy {
    Lexical,
    Semantic,
    Hybrid,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "kebab-case")]
pub enum SandboxMode {
    ReadOnly,
    WorkspaceWrite,
    DangerFullAccess,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "kebab-case")]
pub enum ApprovalPolicy {
    Default,
    OnRequest,
    AutoEdit,
    Yolo,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
#[serde(rename_all = "camelCase")]
pub struct ProviderCapabilities {
    pub chat: bool,
    pub streaming: bool,
    pub retrieval: bool,
    pub embeddings: bool,
    pub resume_session: bool,
    pub approvals: bool,
    pub file_edits: bool,
    pub shell_exec: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ProviderError {
    pub code: String,
    pub message: String,
    pub detail: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ProviderStatus {
    pub provider: ProviderId,
    pub installed: bool,
    pub reachable: bool,
    pub authenticated: bool,
    pub degraded: bool,
    pub version: Option<String>,
    pub mode: Option<String>,
    pub capabilities: ProviderCapabilities,
    pub models: Vec<String>,
    pub default_model: Option<String>,
    pub error: Option<ProviderError>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct IndexStatus {
    pub workspace_path: Option<String>,
    pub ready: bool,
    pub last_indexed_at: Option<String>,
    pub chunk_count: usize,
    pub mode: RetrievalStrategy,
    pub revision: Option<String>,
    pub embedding_provider: Option<ProviderId>,
    pub embedding_model: Option<String>,
    pub stale: bool,
}

impl Default for IndexStatus {
    fn default() -> Self {
        Self {
            workspace_path: None,
            ready: false,
            last_indexed_at: None,
            chunk_count: 0,
            mode: RetrievalStrategy::Lexical,
            revision: None,
            embedding_provider: None,
            embedding_model: None,
            stale: false,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
#[serde(rename_all = "camelCase")]
pub struct FeatureFlags {
    pub codex_agent_enabled: bool,
    pub gemini_agent_enabled: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AiGatewayStatus {
    pub gateway_version: String,
    pub workspace_path: Option<String>,
    pub workspace_ready: bool,
    pub default_provider: ProviderId,
    pub default_mode: AiMode,
    pub providers: Vec<ProviderStatus>,
    pub index: IndexStatus,
    pub settings_path: Option<String>,
    pub feature_flags: FeatureFlags,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct RetrievalOptions {
    pub enabled: bool,
    pub top_k: usize,
    pub strategy: RetrievalStrategy,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ExecutionOptions {
    pub sandbox: SandboxMode,
    pub approval_policy: ApprovalPolicy,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AiRunRequest {
    pub provider: ProviderId,
    pub mode: AiMode,
    pub session_id: Option<String>,
    pub workspace_path: String,
    pub prompt: String,
    pub model: Option<String>,
    pub supplemental_context: Option<String>,
    pub retrieval: Option<RetrievalOptions>,
    pub execution: Option<ExecutionOptions>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AiRunCreated {
    pub run_id: String,
    pub session_id: Option<String>,
    pub stream_url: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SessionSummary {
    pub session_id: String,
    pub provider: ProviderId,
    pub mode: AiMode,
    pub status: String,
    pub title: String,
    pub latest_run_id: String,
    pub updated_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PendingApprovalSummary {
    pub approval_id: String,
    pub kind: String,
    pub summary: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SessionDetail {
    pub summary: SessionSummary,
    pub pending_approvals: Vec<PendingApprovalSummary>,
    pub recent_events: Vec<AiRunEvent>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "camelCase")]
pub enum AiRunEvent {
    Status {
        phase: String,
    },
    MessageDelta {
        text: String,
    },
    MessageFinal {
        text: String,
    },
    ToolStarted {
        name: String,
        input: Option<serde_json::Value>,
    },
    ToolOutput {
        name: String,
        text: String,
    },
    ApprovalRequest {
        approval_id: String,
        kind: String,
        payload: serde_json::Value,
    },
    DiffPreview {
        files: Vec<DiffPreviewFile>,
    },
    Error {
        code: String,
        message: String,
        detail: Option<serde_json::Value>,
    },
    Done {
        usage: Option<serde_json::Value>,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct DiffPreviewFile {
    pub path: String,
    pub diff: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AiApprovalDecision {
    pub decision: String,
    pub scope: Option<String>,
}
