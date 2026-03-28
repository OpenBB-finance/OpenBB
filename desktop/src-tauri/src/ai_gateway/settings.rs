use crate::ai_gateway::{AiMode, ApprovalPolicy, FeatureFlags, ProviderId, RetrievalStrategy, SandboxMode};
use serde::{Deserialize, Serialize};
use serde_json::{Map, Value, json};
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct GatewayRetrievalSettings {
    pub strategy: RetrievalStrategy,
    pub top_k: usize,
    pub allow_repo_summary: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OllamaSettings {
    pub enabled: bool,
    pub base_url: String,
    pub default_chat_model: Option<String>,
    pub default_embedding_model: Option<String>,
    pub keep_alive: String,
    pub request_timeout_ms: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CodexSettings {
    pub enabled: bool,
    pub ask_transport: String,
    pub agent_transport: String,
    pub sandbox: SandboxMode,
    pub approval_policy: ApprovalPolicy,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct GeminiSettings {
    pub enabled: bool,
    pub ask_transport: String,
    pub agent_transport: String,
    pub sandbox: SandboxMode,
    pub approval_policy: ApprovalPolicy,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ProviderSettings {
    pub ollama: OllamaSettings,
    pub codex: CodexSettings,
    pub gemini: GeminiSettings,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AiGatewaySettings {
    pub default_provider: ProviderId,
    pub default_mode: AiMode,
    pub retrieval: GatewayRetrievalSettings,
    pub providers: ProviderSettings,
    pub feature_flags: FeatureFlags,
}

impl Default for AiGatewaySettings {
    fn default() -> Self {
        Self {
            default_provider: ProviderId::Ollama,
            default_mode: AiMode::Ask,
            retrieval: GatewayRetrievalSettings {
                strategy: RetrievalStrategy::Hybrid,
                top_k: 8,
                allow_repo_summary: true,
            },
            providers: ProviderSettings {
                ollama: OllamaSettings {
                    enabled: true,
                    base_url: "http://127.0.0.1:11434/api".to_string(),
                    default_chat_model: Some("qwen2.5-coder:1.5b".to_string()),
                    default_embedding_model: Some("qwen3-embedding".to_string()),
                    keep_alive: "15m".to_string(),
                    request_timeout_ms: 45_000,
                },
                codex: CodexSettings {
                    enabled: true,
                    ask_transport: "exec".to_string(),
                    agent_transport: "app-server".to_string(),
                    sandbox: SandboxMode::ReadOnly,
                    approval_policy: ApprovalPolicy::OnRequest,
                },
                gemini: GeminiSettings {
                    enabled: true,
                    ask_transport: "headless".to_string(),
                    agent_transport: "acp".to_string(),
                    sandbox: SandboxMode::ReadOnly,
                    approval_policy: ApprovalPolicy::Default,
                },
            },
            feature_flags: FeatureFlags {
                codex_agent_enabled: false,
                gemini_agent_enabled: false,
            },
        }
    }
}

pub fn default_user_settings_path() -> Result<PathBuf, String> {
    let home_dir = std::env::var("HOME")
        .or_else(|_| std::env::var("USERPROFILE"))
        .map_err(|error| format!("Could not determine home directory: {error}"))?;
    Ok(Path::new(&home_dir)
        .join(".openbb_platform")
        .join("user_settings.json"))
}

fn ensure_preferences_object(root: &mut Value) -> &mut Map<String, Value> {
    if !root.is_object() {
        *root = json!({});
    }
    let root_object = root.as_object_mut().expect("root object");
    let prefs = root_object
        .entry("preferences")
        .or_insert_with(|| json!({}));
    if !prefs.is_object() {
        *prefs = json!({});
    }
    prefs.as_object_mut().expect("preferences object")
}

pub fn load_settings_from_file(path: &Path) -> Result<AiGatewaySettings, String> {
    if !path.exists() {
        return Ok(AiGatewaySettings::default());
    }

    let contents = fs::read_to_string(path)
        .map_err(|error| format!("Failed to read settings file {}: {error}", path.display()))?;
    if contents.trim().is_empty() {
        return Ok(AiGatewaySettings::default());
    }

    let json: Value = serde_json::from_str(&contents)
        .map_err(|error| format!("Failed to parse settings file {}: {error}", path.display()))?;
    let preferences = json
        .get("preferences")
        .and_then(|value| value.get("ai_gateway"))
        .cloned()
        .unwrap_or_else(|| serde_json::to_value(AiGatewaySettings::default()).unwrap_or_else(|_| json!({})));

    serde_json::from_value(preferences).map_err(|error| {
        format!(
            "Failed to parse preferences.ai_gateway from {}: {error}",
            path.display()
        )
    })
}

pub fn save_settings_to_file(path: &Path, settings: &AiGatewaySettings) -> Result<(), String> {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)
            .map_err(|error| format!("Failed to create settings directory {}: {error}", parent.display()))?;
    }

    let contents = if path.exists() {
        fs::read_to_string(path)
            .map_err(|error| format!("Failed to read settings file {}: {error}", path.display()))?
    } else {
        "{}".to_string()
    };
    let mut json = if contents.trim().is_empty() {
        json!({})
    } else {
        serde_json::from_str::<Value>(&contents).unwrap_or_else(|_| json!({}))
    };
    let preferences = ensure_preferences_object(&mut json);
    preferences.insert(
        "ai_gateway".to_string(),
        serde_json::to_value(settings).map_err(|error| format!("Failed to serialize AI gateway settings: {error}"))?,
    );

    fs::write(
        path,
        serde_json::to_string_pretty(&json)
            .map_err(|error| format!("Failed to serialize user settings JSON: {error}"))?,
    )
    .map_err(|error| format!("Failed to write settings file {}: {error}", path.display()))
}
