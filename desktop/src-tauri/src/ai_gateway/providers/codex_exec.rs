use crate::ai_gateway::providers::command_runner::RealCommandRunner;
use crate::ai_gateway::errors::{
    GatewayResult, process_crashed, provider_not_authenticated, provider_not_installed,
};
use crate::ai_gateway::ollama_core::PreparedAiPrompt;
use crate::ai_gateway::settings::AiGatewaySettings;
use crate::ai_gateway::{AiRunEvent, AiRunRequest, ProviderCapabilities, ProviderError, ProviderId, ProviderStatus};
use serde_json::Value;
use std::process::Stdio;
use tokio::io::{AsyncBufReadExt, BufReader};
use tokio::sync::mpsc::UnboundedSender;

pub async fn detect(settings: &AiGatewaySettings) -> ProviderStatus {
    if RealCommandRunner::command("codex").is_err() {
        return ProviderStatus {
            provider: ProviderId::Codex,
            installed: false,
            reachable: false,
            authenticated: false,
            degraded: false,
            version: None,
            mode: Some(settings.providers.codex.ask_transport.clone()),
            capabilities: ProviderCapabilities::default(),
            models: Vec::new(),
            default_model: None,
            error: Some(ProviderError {
                code: "E_PROVIDER_NOT_INSTALLED".to_string(),
                message: "Codex CLI is not installed.".to_string(),
                detail: None,
            }),
        };
    }

    let version = read_version().await.ok();
    let app_server_available = help_contains("codex", &["app-server"]).await;
    let auth_probe = probe_auth().await;

    let mut capabilities = ProviderCapabilities {
        chat: true,
        streaming: true,
        retrieval: true,
        embeddings: false,
        resume_session: false,
        approvals: false,
        file_edits: false,
        shell_exec: false,
    };
    if settings.feature_flags.codex_agent_enabled && app_server_available {
        capabilities.resume_session = true;
        capabilities.approvals = true;
        capabilities.file_edits = true;
        capabilities.shell_exec = true;
    }

    let (authenticated, error) = match auth_probe {
        Ok(()) => (true, None),
        Err(detail) => (
            false,
            Some(ProviderError {
                code: "E_PROVIDER_NOT_AUTHENTICATED".to_string(),
                message: "Codex CLI is installed but not authenticated.".to_string(),
                detail: Some(detail),
            }),
        ),
    };

    ProviderStatus {
        provider: ProviderId::Codex,
        installed: true,
        reachable: true,
        authenticated,
        degraded: !authenticated,
        version,
        mode: Some(settings.providers.codex.ask_transport.clone()),
        capabilities,
        models: Vec::new(),
        default_model: None,
        error,
    }
}

pub async fn run_ask(
    request: &AiRunRequest,
    prepared_prompt: &PreparedAiPrompt,
    settings: &AiGatewaySettings,
    events: UnboundedSender<AiRunEvent>,
) -> GatewayResult<Option<Value>> {
    if RealCommandRunner::command("codex").is_err() {
        return Err(provider_not_installed("codex"));
    }

    let mut command = RealCommandRunner::command("codex")?;
    command
        .arg("exec")
        .arg("--json")
        .arg("--skip-git-repo-check")
        .arg("--sandbox")
        .arg(match request
            .execution
            .as_ref()
            .map(|value| &value.sandbox)
            .unwrap_or(&settings.providers.codex.sandbox)
        {
            crate::ai_gateway::SandboxMode::ReadOnly => "read-only",
            crate::ai_gateway::SandboxMode::WorkspaceWrite => "workspace-write",
            crate::ai_gateway::SandboxMode::DangerFullAccess => "danger-full-access",
        })
        .arg("-C")
        .arg(&request.workspace_path)
        .arg(&prepared_prompt.compiled_prompt)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    if let Some(model) = request.model.as_ref() {
        command.arg("-m").arg(model);
    }

    let mut child = command.spawn().map_err(|error| process_crashed("codex", error.to_string()))?;
    let stdout = child
        .stdout
        .take()
        .ok_or_else(|| process_crashed("codex", "stdout pipe unavailable"))?;
    let stderr = child
        .stderr
        .take()
        .ok_or_else(|| process_crashed("codex", "stderr pipe unavailable"))?;

    let mut stdout_reader = BufReader::new(stdout).lines();
    let mut stderr_reader = BufReader::new(stderr).lines();
    let mut final_message: Option<String> = None;
    let mut usage: Option<Value> = None;
    let mut stderr_output = Vec::new();

    loop {
        tokio::select! {
            line = stdout_reader.next_line() => {
                match line {
                    Ok(Some(line)) => {
                        if line.trim().is_empty() {
                            continue;
                        }
                        if let Ok(json) = serde_json::from_str::<Value>(&line) {
                            match json.get("type").and_then(|value| value.as_str()) {
                                Some("item.completed") => {
                                    let item = json.get("item").cloned().unwrap_or(Value::Null);
                                    match item.get("type").and_then(|value| value.as_str()) {
                                        Some("agent_message") => {
                                            let text = item.get("text").and_then(|value| value.as_str()).unwrap_or("").to_string();
                                            final_message = Some(text.clone());
                                            let _ = events.send(AiRunEvent::MessageFinal { text });
                                        }
                                        Some("reasoning") => {
                                            let text = item.get("text").and_then(|value| value.as_str()).unwrap_or("").to_string();
                                            let _ = events.send(AiRunEvent::ToolOutput {
                                                name: "reasoning".to_string(),
                                                text,
                                            });
                                        }
                                        _ => {}
                                    }
                                }
                                Some("turn.completed") => {
                                    usage = json.get("usage").cloned();
                                }
                                Some("turn.started") | Some("thread.started") => {
                                    let _ = events.send(AiRunEvent::Status {
                                        phase: "running".to_string(),
                                    });
                                }
                                _ => {}
                            }
                        }
                    }
                    Ok(None) => break,
                    Err(error) => return Err(process_crashed("codex", error.to_string())),
                }
            }
            line = stderr_reader.next_line() => {
                match line {
                    Ok(Some(line)) => stderr_output.push(line),
                    Ok(None) => {}
                    Err(error) => stderr_output.push(error.to_string()),
                }
            }
        }
    }

    let status = child.wait().await.map_err(|error| process_crashed("codex", error.to_string()))?;
    if !status.success() {
        let detail = stderr_output.join("\n");
        if detail.to_lowercase().contains("login") || detail.to_lowercase().contains("auth") {
            return Err(provider_not_authenticated("codex", detail));
        }
        return Err(process_crashed("codex", detail));
    }

    if final_message.is_none() {
        return Err(process_crashed("codex", "Codex did not return a final agent message."));
    }

    Ok(Some(serde_json::json!({
        "usedModel": request.model,
        "citations": prepared_prompt.citations,
        "retrievalMode": prepared_prompt.retrieval_mode,
        "provider": "codex",
        "usage": usage
    })))
}

async fn read_version() -> Result<String, String> {
    let output = RealCommandRunner::output("codex", &["--version"])
        .await
        .map_err(|error| error.to_string())?;
    if !output.status.success() {
        return Err(String::from_utf8_lossy(&output.stderr).trim().to_string());
    }
    Ok(String::from_utf8_lossy(&output.stdout).trim().to_string())
}

async fn help_contains(program: &str, args: &[&str]) -> bool {
    let Ok(mut command) = RealCommandRunner::command(program) else {
        return false;
    };
    for arg in args {
        command.arg(arg);
    }
    command.arg("--help");
    match command.output().await {
        Ok(output) => output.status.success(),
        Err(_) => false,
    }
}

async fn probe_auth() -> Result<(), String> {
    let output = RealCommandRunner::output(
        "codex",
        &[
            "exec",
            "--json",
            "--skip-git-repo-check",
            "--sandbox",
            "read-only",
            "Reply with exactly OK",
        ],
    )
    .await
    .map_err(|error| error.to_string())?;
    if output.status.success() {
        Ok(())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).trim().to_string())
    }
}
