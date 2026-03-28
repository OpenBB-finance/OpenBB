use crate::ai_gateway::settings::{AiGatewaySettings, default_user_settings_path, load_settings_from_file};
use crate::ai_gateway::{
    AiGatewayStatus, AiMode, AiRunCreated, AiRunEvent, AiRunRequest, ApprovalPolicy,
    ProviderId, RetrievalStrategy, SandboxMode,
};
use once_cell::sync::Lazy;
use reqwest::Client;
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::path::{Path, PathBuf};
use std::process::Stdio;
use std::sync::Mutex;
use std::time::Duration;
use tauri::{AppHandle, Manager};
use tokio::io::{AsyncBufReadExt, BufReader};
use tokio::process::{Child, Command};

static GATEWAY_RUNTIME: Lazy<Mutex<GatewayRuntime>> = Lazy::new(|| Mutex::new(GatewayRuntime::default()));

#[derive(Default)]
struct GatewayRuntime {
    base_url: Option<String>,
    child: Option<Child>,
    restart_attempts: usize,
    degraded: bool,
    settings_path: Option<PathBuf>,
    resource_dir: Option<PathBuf>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AiGatewayInfo {
    pub base_url: String,
    pub ready: bool,
    pub degraded: bool,
    pub settings_path: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AiStatus {
    pub repo_root: Option<String>,
    pub repo_ready: bool,
    pub ollama_reachable: bool,
    pub chat_model: Option<String>,
    pub chat_candidates: Vec<String>,
    pub embedding_model: Option<String>,
    pub available_models: Vec<String>,
    pub index_ready: bool,
    pub last_indexed_at: Option<String>,
    pub chunk_count: usize,
    pub mode: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AiIndexResult {
    pub repo_root: String,
    pub scanned_files: usize,
    pub indexed_files: usize,
    pub skipped_files: usize,
    pub chunk_count: usize,
    pub last_indexed_at: String,
    pub revision: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AiChatMessage {
    pub role: String,
    pub content: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AiAskRequest {
    pub repo_root: String,
    pub messages: Vec<AiChatMessage>,
    pub max_context_chunks: Option<usize>,
    pub supplemental_context: Option<String>,
    pub supplemental_only: Option<bool>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AiCitation {
    pub path: String,
    pub start_line: usize,
    pub end_line: usize,
    pub score: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AiAskResponse {
    pub answer: String,
    pub citations: Vec<AiCitation>,
    pub used_model: String,
    pub attempted_models: Option<Vec<String>>,
    pub model_total_ms: Option<u64>,
    pub load_ms: Option<u64>,
    pub prompt_eval_ms: Option<u64>,
    pub eval_ms: Option<u64>,
    pub timing_ms: u64,
    pub retrieval_mode: String,
}

pub async fn initialize_ai_gateway(app_handle: AppHandle) {
    if let Ok(resource_dir) = app_handle.path().resource_dir() {
        let mut runtime = GATEWAY_RUNTIME.lock().unwrap();
        runtime.resource_dir = Some(resource_dir);
    }
    let _ = ensure_gateway_available().await;
}

#[tauri::command]
pub async fn get_ai_gateway_info() -> Result<AiGatewayInfo, String> {
    ensure_gateway_available().await
}

#[tauri::command]
pub async fn ensure_ai_gateway_running() -> Result<AiGatewayInfo, String> {
    ensure_gateway_available().await
}

#[tauri::command]
pub async fn stop_ai_gateway() -> Result<bool, String> {
    let mut child = {
        let mut runtime = GATEWAY_RUNTIME.lock().unwrap();
        runtime.base_url = None;
        runtime.child.take()
    };
    if let Some(process) = child.as_mut() {
        let _ = process.kill().await;
    }
    Ok(true)
}

#[tauri::command]
pub async fn get_ai_status(default_dir: String) -> Result<AiStatus, String> {
    let gateway = ensure_gateway_available().await?;
    let status: AiGatewayStatus = gateway_get(&gateway.base_url, &format!("/v1/status?workspacePath={}", urlencoding::encode(&default_dir))).await?;
    let ollama = status
        .providers
        .iter()
        .find(|provider| provider.provider == ProviderId::Ollama);
    Ok(AiStatus {
        repo_root: status.workspace_path,
        repo_ready: status.workspace_ready,
        ollama_reachable: ollama.map(|provider| provider.reachable).unwrap_or(false),
        chat_model: ollama.and_then(|provider| provider.default_model.clone()),
        chat_candidates: ollama.map(|provider| provider.models.clone()).unwrap_or_default(),
        embedding_model: status.index.embedding_model.clone(),
        available_models: ollama.map(|provider| provider.models.clone()).unwrap_or_default(),
        index_ready: status.index.ready,
        last_indexed_at: status.index.last_indexed_at,
        chunk_count: status.index.chunk_count,
        mode: match status.index.mode {
            RetrievalStrategy::Hybrid => "semantic".to_string(),
            RetrievalStrategy::Semantic => "semantic".to_string(),
            RetrievalStrategy::Lexical => "lexical".to_string(),
        },
    })
}

#[tauri::command]
pub async fn warm_ai_chat_model(_default_dir: String) -> Result<serde_json::Value, String> {
    let settings = load_ai_settings()?;
    Ok(json!({
        "ok": true,
        "usedModel": settings.providers.ollama.default_chat_model,
    }))
}

#[tauri::command]
pub async fn build_ai_index(repo_root: String, force: Option<bool>) -> Result<AiIndexResult, String> {
    let gateway = ensure_gateway_available().await?;
    let value: serde_json::Value = gateway_post(
        &gateway.base_url,
        "/v1/index/build",
        json!({
            "workspacePath": repo_root,
            "force": force.unwrap_or(false),
        }),
    )
    .await?;
    serde_json::from_value(value).map_err(|error| format!("Failed to decode index build result: {error}"))
}

#[tauri::command]
pub async fn clear_ai_index(repo_root: String) -> Result<serde_json::Value, String> {
    let gateway = ensure_gateway_available().await?;
    gateway_post(
        &gateway.base_url,
        "/v1/index/clear",
        json!({
            "workspacePath": repo_root,
        }),
    )
    .await
}

#[tauri::command]
pub async fn ask_ai_question(request: AiAskRequest) -> Result<AiAskResponse, String> {
    let gateway = ensure_gateway_available().await?;
    let settings = load_ai_settings()?;
    let latest_prompt = request
        .messages
        .iter()
        .rev()
        .find(|message| message.role == "user")
        .or_else(|| request.messages.last())
        .ok_or_else(|| "A question is required before asking AI.".to_string())?
        .content
        .clone();
    let created: AiRunCreated = gateway_post(
        &gateway.base_url,
        "/v1/runs",
        json!(AiRunRequest {
            provider: settings.default_provider,
            mode: AiMode::Ask,
            session_id: None,
            workspace_path: request.repo_root.clone(),
            prompt: latest_prompt,
            model: None,
            supplemental_context: request.supplemental_context.clone(),
            retrieval: Some(crate::ai_gateway::RetrievalOptions {
                enabled: true,
                top_k: request.max_context_chunks.unwrap_or(settings.retrieval.top_k),
                strategy: settings.retrieval.strategy,
            }),
            execution: Some(crate::ai_gateway::ExecutionOptions {
                sandbox: SandboxMode::ReadOnly,
                approval_policy: ApprovalPolicy::Default,
            }),
        }),
    )
    .await?;

    collect_run_response(&gateway.base_url, &created.run_id).await
}

#[tauri::command]
pub async fn get_ai_settings() -> Result<AiGatewaySettings, String> {
    load_ai_settings()
}

#[tauri::command]
pub async fn update_ai_settings(settings: AiGatewaySettings) -> Result<AiGatewaySettings, String> {
    let gateway = ensure_gateway_available().await?;
    gateway_put(&gateway.base_url, "/v1/settings", serde_json::to_value(&settings).map_err(|error| error.to_string())?).await
}

async fn ensure_gateway_available() -> Result<AiGatewayInfo, String> {
    let settings_path = default_user_settings_path()?;
    if let Some(info) = existing_gateway_info(&settings_path).await? {
        return Ok(info);
    }
    spawn_gateway(settings_path).await
}

async fn existing_gateway_info(settings_path: &Path) -> Result<Option<AiGatewayInfo>, String> {
    let mut runtime = GATEWAY_RUNTIME.lock().unwrap();
    if let Some(child) = runtime.child.as_mut() {
        match child.try_wait() {
            Ok(Some(_)) => {
                runtime.child = None;
                runtime.base_url = None;
                runtime.restart_attempts = runtime.restart_attempts.saturating_add(1);
                if runtime.restart_attempts >= 3 {
                    runtime.degraded = true;
                }
                return Ok(None);
            }
            Ok(None) => {}
            Err(error) => return Err(format!("Failed to inspect AI gateway process: {error}")),
        }
    }
    if let Some(base_url) = runtime.base_url.clone() {
        return Ok(Some(AiGatewayInfo {
            base_url,
            ready: true,
            degraded: runtime.degraded,
            settings_path: settings_path.to_string_lossy().to_string(),
        }));
    }
    Ok(None)
}

async fn spawn_gateway(settings_path: PathBuf) -> Result<AiGatewayInfo, String> {
    let resource_dir = GATEWAY_RUNTIME
        .lock()
        .unwrap()
        .resource_dir
        .clone();
    let (program, args) = resolve_gateway_command(&settings_path, resource_dir.as_deref())?;
    let mut command = Command::new(program);
    command
        .args(args)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    let mut child = command
        .spawn()
        .map_err(|error| format!("Failed to start AI gateway process: {error}"))?;
    let stdout = child
        .stdout
        .take()
        .ok_or_else(|| "AI gateway stdout pipe is unavailable.".to_string())?;
    let stderr = child
        .stderr
        .take()
        .ok_or_else(|| "AI gateway stderr pipe is unavailable.".to_string())?;

    let mut stdout_lines = BufReader::new(stdout).lines();
    let ready_line = tokio::time::timeout(Duration::from_secs(30), stdout_lines.next_line())
        .await
        .map_err(|_| "Timed out waiting for AI gateway readiness.".to_string())?
        .map_err(|error| format!("Failed to read AI gateway readiness: {error}"))?
        .ok_or_else(|| "AI gateway exited before signaling readiness.".to_string())?;

    let ready_json: serde_json::Value =
        serde_json::from_str(&ready_line).map_err(|error| format!("Failed to parse AI gateway readiness: {error}"))?;
    let port = ready_json
        .get("port")
        .and_then(|value| value.as_u64())
        .ok_or_else(|| "AI gateway readiness did not include a port.".to_string())?;
    let host = ready_json
        .get("host")
        .and_then(|value| value.as_str())
        .unwrap_or("127.0.0.1");
    let base_url = format!("http://{host}:{port}");

    tokio::spawn(async move {
        let mut reader = stdout_lines;
        while let Ok(Some(line)) = reader.next_line().await {
            log::debug!("ai-gateway stdout: {line}");
        }
    });
    tokio::spawn(async move {
        let mut reader = BufReader::new(stderr).lines();
        while let Ok(Some(line)) = reader.next_line().await {
            log::warn!("ai-gateway stderr: {line}");
        }
    });

    let mut runtime = GATEWAY_RUNTIME.lock().unwrap();
    runtime.base_url = Some(base_url.clone());
    runtime.child = Some(child);
    runtime.degraded = false;
    runtime.restart_attempts = 0;
    runtime.settings_path = Some(settings_path.clone());

    Ok(AiGatewayInfo {
        base_url,
        ready: true,
        degraded: false,
        settings_path: settings_path.to_string_lossy().to_string(),
    })
}

fn resolve_gateway_command(settings_path: &Path, resource_dir: Option<&Path>) -> Result<(String, Vec<String>), String> {
    let exe_name = if cfg!(windows) {
        "openbb-ai-gateway.exe"
    } else {
        "openbb-ai-gateway"
    };
    let current_exe = std::env::current_exe()
        .map_err(|error| format!("Failed to resolve current executable: {error}"))?;
    let mut candidates = Vec::new();
    if let Some(resource_dir) = resource_dir {
        candidates.push(resource_dir.join("ai").join(exe_name));
    }
    candidates.push(current_exe.with_file_name(exe_name));
    candidates.push(
        current_exe
            .parent()
            .map(|parent| parent.join("binaries").join(exe_name))
            .unwrap_or_else(|| PathBuf::from(exe_name)),
    );
    for candidate in candidates {
        if candidate.exists() {
            return Ok((
                candidate.to_string_lossy().to_string(),
                vec![
                    "--host".to_string(),
                    "127.0.0.1".to_string(),
                    "--port".to_string(),
                    "0".to_string(),
                    "--settings".to_string(),
                    settings_path.to_string_lossy().to_string(),
                ],
            ));
        }
    }

    #[cfg(debug_assertions)]
    {
        return Ok((
            "cargo".to_string(),
            vec![
                "run".to_string(),
                "--manifest-path".to_string(),
                Path::new(env!("CARGO_MANIFEST_DIR"))
                    .join("Cargo.toml")
                    .to_string_lossy()
                    .to_string(),
                "--bin".to_string(),
                "openbb-ai-gateway".to_string(),
                "--".to_string(),
                "--host".to_string(),
                "127.0.0.1".to_string(),
                "--port".to_string(),
                "0".to_string(),
                "--settings".to_string(),
                settings_path.to_string_lossy().to_string(),
            ],
        ));
    }

    #[cfg(not(debug_assertions))]
    {
        Err("Could not locate openbb-ai-gateway binary.".to_string())
    }
}

async fn gateway_get<T>(base_url: &str, path: &str) -> Result<T, String>
where
    T: serde::de::DeserializeOwned,
{
    let client = Client::builder()
        .timeout(Duration::from_secs(120))
        .build()
        .map_err(|error| format!("Failed to build AI gateway client: {error}"))?;
    let response = client
        .get(format!("{base_url}{path}"))
        .send()
        .await
        .map_err(|error| format!("AI gateway request failed: {error}"))?;
    let status = response.status();
    let value = response.text().await.unwrap_or_default();
    if !status.is_success() {
        return Err(value);
    }
    serde_json::from_str(&value).map_err(|error| format!("Failed to decode AI gateway response: {error}"))
}

async fn gateway_post<T>(base_url: &str, path: &str, body: serde_json::Value) -> Result<T, String>
where
    T: serde::de::DeserializeOwned,
{
    let client = Client::builder()
        .timeout(Duration::from_secs(120))
        .build()
        .map_err(|error| format!("Failed to build AI gateway client: {error}"))?;
    let response = client
        .post(format!("{base_url}{path}"))
        .json(&body)
        .send()
        .await
        .map_err(|error| format!("AI gateway POST failed: {error}"))?;
    let status = response.status();
    let value = response.text().await.unwrap_or_default();
    if !status.is_success() {
        return Err(value);
    }
    serde_json::from_str(&value).map_err(|error| format!("Failed to decode AI gateway POST response: {error}"))
}

async fn gateway_put<T>(base_url: &str, path: &str, body: serde_json::Value) -> Result<T, String>
where
    T: serde::de::DeserializeOwned,
{
    let client = Client::builder()
        .timeout(Duration::from_secs(120))
        .build()
        .map_err(|error| format!("Failed to build AI gateway client: {error}"))?;
    let response = client
        .put(format!("{base_url}{path}"))
        .json(&body)
        .send()
        .await
        .map_err(|error| format!("AI gateway PUT failed: {error}"))?;
    let status = response.status();
    let value = response.text().await.unwrap_or_default();
    if !status.is_success() {
        return Err(value);
    }
    serde_json::from_str(&value).map_err(|error| format!("Failed to decode AI gateway PUT response: {error}"))
}

async fn collect_run_response(base_url: &str, run_id: &str) -> Result<AiAskResponse, String> {
    let client = Client::builder()
        .timeout(Duration::from_secs(240))
        .build()
        .map_err(|error| format!("Failed to build AI gateway client: {error}"))?;
    let mut response = client
        .get(format!("{base_url}/v1/runs/{run_id}/stream"))
        .send()
        .await
        .map_err(|error| format!("Failed to open AI gateway run stream: {error}"))?;
    let mut buffer = String::new();
    let mut answer = String::new();
    let mut citations = Vec::new();
    let mut used_model = "unknown".to_string();
    let mut attempted_models = None;
    let mut model_total_ms = None;
    let mut load_ms = None;
    let mut prompt_eval_ms = None;
    let mut eval_ms = None;
    let mut timing_ms = 0;
    let mut retrieval_mode = "lexical".to_string();

    loop {
        let Some(chunk) = response
            .chunk()
            .await
            .map_err(|error| format!("Failed to read AI gateway stream: {error}"))?
        else {
            break;
        };
        buffer.push_str(&String::from_utf8_lossy(&chunk));
        while let Some(index) = buffer.find("\n\n") {
            let raw = buffer[..index].to_string();
            buffer = buffer[index + 2..].to_string();
            if let Some(data_line) = raw.lines().find(|line| line.starts_with("data:")) {
                let json_line = data_line.trim_start_matches("data:").trim();
                let event: AiRunEvent = serde_json::from_str(json_line)
                    .map_err(|error| format!("Failed to decode AI gateway SSE event: {error}"))?;
                match event {
                    AiRunEvent::MessageFinal { text } => answer = text,
                    AiRunEvent::Done { usage } => {
                        if let Some(usage) = usage {
                            if let Some(value) = usage.get("citations").cloned() {
                                citations = serde_json::from_value(value).unwrap_or_default();
                            }
                            if let Some(value) = usage.get("usedModel").and_then(|value| value.as_str()) {
                                used_model = value.to_string();
                            }
                            attempted_models = usage
                                .get("attemptedModels")
                                .cloned()
                                .and_then(|value| serde_json::from_value(value).ok());
                            model_total_ms = usage.get("modelTotalMs").and_then(|value| value.as_u64());
                            load_ms = usage.get("loadMs").and_then(|value| value.as_u64());
                            prompt_eval_ms = usage.get("promptEvalMs").and_then(|value| value.as_u64());
                            eval_ms = usage.get("evalMs").and_then(|value| value.as_u64());
                            timing_ms = usage.get("timingMs").and_then(|value| value.as_u64()).unwrap_or(0);
                            if let Some(mode) = usage.get("retrievalMode").and_then(|value| value.as_str()) {
                                retrieval_mode = mode.to_string();
                            }
                        }
                        return Ok(AiAskResponse {
                            answer,
                            citations,
                            used_model,
                            attempted_models,
                            model_total_ms,
                            load_ms,
                            prompt_eval_ms,
                            eval_ms,
                            timing_ms,
                            retrieval_mode,
                        });
                    }
                    AiRunEvent::Error { message, .. } => return Err(message),
                    _ => {}
                }
            }
        }
    }

    Err("AI gateway stream ended before a final response was received.".to_string())
}

fn load_ai_settings() -> Result<AiGatewaySettings, String> {
    let settings_path = default_user_settings_path()?;
    load_settings_from_file(&settings_path)
}
