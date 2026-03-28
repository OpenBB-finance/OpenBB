use crate::ai_gateway::providers::command_runner::RealCommandRunner;
use crate::ai_gateway::errors::{
    GatewayResult, process_crashed, provider_busy, provider_not_authenticated, provider_not_installed,
};
use crate::ai_gateway::ollama_core::PreparedAiPrompt;
use crate::ai_gateway::settings::AiGatewaySettings;
use crate::ai_gateway::{AiRunEvent, AiRunRequest, ProviderCapabilities, ProviderError, ProviderId, ProviderStatus};
use serde_json::Value;
use std::process::Stdio;
use std::time::Instant;
use tokio::io::{AsyncBufReadExt, BufReader};
use tokio::sync::mpsc::UnboundedSender;

pub const DEFAULT_GEMINI_MODEL: &str = "gemini-2.5-flash";

pub async fn detect(settings: &AiGatewaySettings) -> ProviderStatus {
    if RealCommandRunner::command("gemini").is_err() {
        return ProviderStatus {
            provider: ProviderId::Gemini,
            installed: false,
            reachable: false,
            authenticated: false,
            degraded: false,
            version: None,
            mode: Some(settings.providers.gemini.ask_transport.clone()),
            capabilities: ProviderCapabilities::default(),
            models: Vec::new(),
            default_model: None,
            error: Some(ProviderError {
                code: "E_PROVIDER_NOT_INSTALLED".to_string(),
                message: "Gemini CLI is not installed.".to_string(),
                detail: None,
            }),
        };
    }

    let version = read_version().await.ok();
    let help_text = read_help().await.unwrap_or_default();
    let supports_acp = help_text.contains("--acp") || help_text.contains("--experimental-acp");
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
    if settings.feature_flags.gemini_agent_enabled && supports_acp {
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
                message: "Gemini CLI is installed but not authenticated.".to_string(),
                detail: Some(detail),
            }),
        ),
    };

    ProviderStatus {
        provider: ProviderId::Gemini,
        installed: true,
        reachable: true,
        authenticated,
        degraded: !authenticated,
        version,
        mode: Some(settings.providers.gemini.ask_transport.clone()),
        capabilities,
        models: Vec::new(),
        default_model: Some(DEFAULT_GEMINI_MODEL.to_string()),
        error,
    }
}

pub async fn run_ask(
    request: &AiRunRequest,
    prepared_prompt: &PreparedAiPrompt,
    _settings: &AiGatewaySettings,
    events: UnboundedSender<AiRunEvent>,
) -> GatewayResult<Option<Value>> {
    if RealCommandRunner::command("gemini").is_err() {
        return Err(provider_not_installed("gemini"));
    }
    let started_at = Instant::now();
    let resolved_model = request
        .model
        .clone()
        .unwrap_or_else(|| DEFAULT_GEMINI_MODEL.to_string());

    let mut command = RealCommandRunner::command("gemini")?;
    command
        .arg("-p")
        .arg(&prepared_prompt.compiled_prompt)
        .arg("--output-format")
        .arg("stream-json")
        .arg("--model")
        .arg(&resolved_model)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    let mut child = command.spawn().map_err(|error| process_crashed("gemini", error.to_string()))?;
    let stdout = child
        .stdout
        .take()
        .ok_or_else(|| process_crashed("gemini", "stdout pipe unavailable"))?;
    let stderr = child
        .stderr
        .take()
        .ok_or_else(|| process_crashed("gemini", "stderr pipe unavailable"))?;

    let mut stdout_reader = BufReader::new(stdout).lines();
    let mut stderr_reader = BufReader::new(stderr).lines();
    let mut final_message: Option<String> = None;
    let mut assistant_message = String::new();
    let mut stderr_output = Vec::new();
    let mut usage: Option<Value> = None;

    loop {
        tokio::select! {
            line = stdout_reader.next_line() => {
                match line {
                    Ok(Some(line)) => {
                        if line.trim().is_empty() {
                            continue;
                        }
                        if let Ok(json) = serde_json::from_str::<Value>(&line) {
                            let event_type = json
                                .get("type")
                                .and_then(|value| value.as_str())
                                .or_else(|| json.get("event").and_then(|value| value.as_str()));
                            match event_type {
                                Some("message") => {
                                    let role = json
                                        .get("role")
                                        .and_then(|value| value.as_str())
                                        .unwrap_or_default();
                                    if let Some(text) = extract_text(&json) {
                                        if role.eq_ignore_ascii_case("assistant") {
                                            assistant_message.push_str(&text);
                                            let _ = events.send(AiRunEvent::MessageDelta { text });
                                        }
                                    }
                                }
                                Some("tool_use") => {
                                    let _ = events.send(AiRunEvent::ToolStarted {
                                        name: json.get("name").and_then(|value| value.as_str()).unwrap_or("tool").to_string(),
                                        input: json.get("input").cloned(),
                                    });
                                }
                                Some("tool_result") => {
                                    let text = extract_text(&json).unwrap_or_else(|| json.to_string());
                                    let _ = events.send(AiRunEvent::ToolOutput {
                                        name: json.get("name").and_then(|value| value.as_str()).unwrap_or("tool").to_string(),
                                        text,
                                    });
                                }
                                Some("result") => {
                                    final_message = extract_text(&json)
                                        .or_else(|| {
                                            let trimmed = assistant_message.trim();
                                            if trimmed.is_empty() {
                                                None
                                            } else {
                                                Some(trimmed.to_string())
                                            }
                                        });
                                    if let Some(text) = final_message.clone() {
                                        let _ = events.send(AiRunEvent::MessageFinal { text });
                                    }
                                    usage = Some(json.clone());
                                }
                                Some("error") => {
                                    let detail = extract_text(&json).unwrap_or_else(|| json.to_string());
                                    return Err(process_crashed("gemini", detail));
                                }
                                Some("init") => {
                                    let _ = events.send(AiRunEvent::Status {
                                        phase: "running".to_string(),
                                    });
                                }
                                _ => {}
                            }
                        }
                    }
                    Ok(None) => break,
                    Err(error) => return Err(process_crashed("gemini", error.to_string())),
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

    let status = child.wait().await.map_err(|error| process_crashed("gemini", error.to_string()))?;
    if !status.success() {
        let detail = stderr_output.join("\n");
        let detail_lower = detail.to_ascii_lowercase();
        if detail.to_lowercase().contains("auth") || detail.to_lowercase().contains("api_key") {
            return Err(provider_not_authenticated("gemini", detail));
        }
        if detail_lower.contains("no capacity")
            || detail_lower.contains("rate limit")
            || detail_lower.contains("429")
            || detail_lower.contains("overloaded")
        {
            return Err(provider_busy("gemini", detail));
        }
        return Err(process_crashed("gemini", detail));
    }

    if final_message.is_none() {
        return Err(process_crashed("gemini", "Gemini did not emit a final result event."));
    }

    Ok(Some(serde_json::json!({
        "usedModel": resolved_model,
        "citations": prepared_prompt.citations,
        "retrievalMode": prepared_prompt.retrieval_mode,
        "timingMs": started_at.elapsed().as_millis() as u64,
        "provider": "gemini",
        "providerUsage": usage
    })))
}

fn extract_text(value: &Value) -> Option<String> {
    value
        .get("content")
        .and_then(|v| v.as_str())
        .map(ToString::to_string)
        .or_else(|| {
            value
                .get("message")
                .and_then(|message| message.get("content"))
                .and_then(|v| v.as_str())
                .map(ToString::to_string)
        })
        .or_else(|| {
            value
                .get("result")
                .and_then(|result| result.get("content"))
                .and_then(|v| v.as_str())
                .map(ToString::to_string)
        })
        .or_else(|| {
            value
                .get("content")
                .and_then(|content| content.get("text"))
                .and_then(|v| v.as_str())
                .map(ToString::to_string)
        })
        .or_else(|| value.get("text").and_then(|v| v.as_str()).map(ToString::to_string))
        .or_else(|| {
            value
                .get("message")
                .and_then(|message| message.get("text"))
                .and_then(|v| v.as_str())
                .map(ToString::to_string)
        })
        .or_else(|| {
            value
                .get("result")
                .and_then(|result| result.get("text"))
                .and_then(|v| v.as_str())
                .map(ToString::to_string)
        })
}

async fn read_version() -> Result<String, String> {
    let output = RealCommandRunner::output("gemini", &["--version"])
        .await
        .map_err(|error| error.to_string())?;
    if !output.status.success() {
        return Err(String::from_utf8_lossy(&output.stderr).trim().to_string());
    }
    Ok(String::from_utf8_lossy(&output.stdout).trim().to_string())
}

async fn read_help() -> Result<String, String> {
    let output = RealCommandRunner::output("gemini", &["--help"])
        .await
        .map_err(|error| error.to_string())?;
    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).to_string();
    Ok(format!("{stdout}\n{stderr}"))
}

async fn probe_auth() -> Result<(), String> {
    let output = RealCommandRunner::output(
        "gemini",
        &["-p", "Reply with exactly OK", "--output-format", "json"],
    )
    .await
    .map_err(|error| error.to_string())?;
    if output.status.success() {
        Ok(())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).trim().to_string())
    }
}
