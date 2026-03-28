use crate::ai_gateway::errors::{
    GatewayResult, process_crashed, provider_busy, provider_not_authenticated, provider_not_installed,
};
use crate::ai_gateway::ollama_core::PreparedAiPrompt;
use crate::ai_gateway::providers::command_runner::RealCommandRunner;
use crate::ai_gateway::providers::gemini_headless::DEFAULT_GEMINI_MODEL;
use crate::ai_gateway::sessions::SessionStore;
use crate::ai_gateway::settings::AiGatewaySettings;
use crate::ai_gateway::{AiApprovalDecision, AiRunEvent, AiRunRequest};
use serde_json::{Value, json};
use std::process::Stdio;
use std::sync::Arc;
use std::time::Instant;
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader, Lines};
use tokio::process::{ChildStdin, ChildStdout};
use tokio::sync::{mpsc::UnboundedSender, oneshot};

pub async fn detect_flag(_settings: &AiGatewaySettings) -> Option<String> {
    let output = RealCommandRunner::output("gemini", &["--help"]).await.ok()?;
    let help = format!(
        "{}\n{}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr)
    );
    if help.contains("--acp") {
        Some("--acp".to_string())
    } else if help.contains("--experimental-acp") {
        Some("--experimental-acp".to_string())
    } else {
        None
    }
}

pub async fn run_agent(
    request: &AiRunRequest,
    prepared_prompt: &PreparedAiPrompt,
    _settings: &AiGatewaySettings,
    events: UnboundedSender<AiRunEvent>,
    sessions: Arc<SessionStore>,
    run_id: String,
    session_id: Option<String>,
) -> GatewayResult<Option<Value>> {
    if RealCommandRunner::command("gemini").is_err() {
        return Err(provider_not_installed("gemini"));
    }
    let Some(session_id) = session_id else {
        return Err(process_crashed("gemini", "Agent mode requires a session ID."));
    };
    let acp_flag = detect_flag(_settings)
        .await
        .ok_or_else(|| process_crashed("gemini", "Gemini ACP is unavailable in this runtime."))?;
    let resolved_model = request
        .model
        .clone()
        .unwrap_or_else(|| DEFAULT_GEMINI_MODEL.to_string());

    let mut command = RealCommandRunner::command("gemini")?;
    command
        .arg(acp_flag)
        .arg("-m")
        .arg(&resolved_model)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let mut child = command
        .spawn()
        .map_err(|error| process_crashed("gemini", error.to_string()))?;
    let mut stdin = child
        .stdin
        .take()
        .ok_or_else(|| process_crashed("gemini", "stdin pipe unavailable"))?;
    let stdout = child
        .stdout
        .take()
        .ok_or_else(|| process_crashed("gemini", "stdout pipe unavailable"))?;
    let stderr = child
        .stderr
        .take()
        .ok_or_else(|| process_crashed("gemini", "stderr pipe unavailable"))?;
    let mut stdout_lines = BufReader::new(stdout).lines();
    let mut stderr_lines = BufReader::new(stderr).lines();
    let mut stderr_buffer = Vec::new();
    let started_at = Instant::now();

    send_rpc(
        &mut stdin,
        1,
        "initialize",
        json!({
            "protocolVersion": 1,
            "clientCapabilities": {
                "fs": {
                    "readTextFile": true,
                    "writeTextFile": true
                }
            }
        }),
    )
    .await?;
    read_response(&mut stdout_lines, &mut stderr_lines, 1, &mut stderr_buffer, "gemini").await?;

    send_rpc(
        &mut stdin,
        2,
        "session/new",
        json!({
            "cwd": request.workspace_path,
            "mcpServers": [],
        }),
    )
    .await?;
    let session = read_response(&mut stdout_lines, &mut stderr_lines, 2, &mut stderr_buffer, "gemini").await?;
    let gemini_session_id = session
        .get("sessionId")
        .and_then(|value| value.as_str())
        .ok_or_else(|| process_crashed("gemini", "session/new did not return a session ID."))?
        .to_string();

    send_rpc(
        &mut stdin,
        3,
        "session/prompt",
        json!({
            "sessionId": gemini_session_id,
            "prompt": [{
                "type": "text",
                "text": prepared_prompt.compiled_prompt
            }]
        }),
    )
    .await?;

    let mut final_message = String::new();
    let mut prompt_result: Option<Value> = None;

    loop {
        tokio::select! {
            line = stdout_lines.next_line() => {
                match line {
                    Ok(Some(line)) => {
                        if line.trim().is_empty() {
                            continue;
                        }
                        let value: Value = serde_json::from_str(&line)
                            .map_err(|error| process_crashed("gemini", format!("Invalid ACP JSON: {error}")))?;
                        if value.get("id").and_then(|v| v.as_i64()) == Some(3) {
                            if let Some(error) = value.get("error") {
                                let message = error.get("message").and_then(|v| v.as_str()).unwrap_or("Gemini ACP request failed.");
                                let lower = message.to_ascii_lowercase();
                                if lower.contains("auth")
                                    || lower.contains("api key")
                                {
                                    return Err(provider_not_authenticated("gemini", message));
                                }
                                if lower.contains("no capacity")
                                    || lower.contains("rate limit")
                                    || lower.contains("429")
                                    || lower.contains("overloaded")
                                {
                                    return Err(provider_busy("gemini", message));
                                }
                                return Err(process_crashed("gemini", message.to_string()));
                            }
                            prompt_result = Some(value.get("result").cloned().unwrap_or(Value::Null));
                            break;
                        }
                        if let Some(method) = value.get("method").and_then(|v| v.as_str()) {
                            match method {
                                "session/update" => {
                                    if let Some(update) = value.get("params").and_then(|p| p.get("update")) {
                                        match update.get("sessionUpdate").and_then(|v| v.as_str()) {
                                            Some("agent_message_chunk") => {
                                                if let Some(text) = extract_update_text(update) {
                                                    final_message.push_str(&text);
                                                    let _ = events.send(AiRunEvent::MessageDelta { text });
                                                }
                                            }
                                            Some("agent_thought_chunk") => {
                                                if let Some(text) = extract_update_text(update) {
                                                    let _ = events.send(AiRunEvent::ToolOutput {
                                                        name: "reasoning".to_string(),
                                                        text,
                                                    });
                                                }
                                            }
                                            Some("tool_call") => {
                                                let _ = events.send(AiRunEvent::ToolStarted {
                                                    name: update.get("title").and_then(|v| v.as_str()).unwrap_or("tool").to_string(),
                                                    input: Some(update.clone()),
                                                });
                                            }
                                            Some("tool_call_update") => {
                                                let _ = events.send(AiRunEvent::ToolOutput {
                                                    name: update.get("title").and_then(|v| v.as_str()).unwrap_or("tool").to_string(),
                                                    text: extract_tool_update_text(update),
                                                });
                                            }
                                            _ => {}
                                        }
                                    }
                                }
                                "session/request_permission" => {
                                    handle_permission_request(
                                        &mut stdin,
                                        &value,
                                        &events,
                                        sessions.clone(),
                                        &run_id,
                                        &session_id,
                                    )
                                    .await?;
                                }
                                _ => {}
                            }
                        }
                    }
                    Ok(None) => break,
                    Err(error) => return Err(process_crashed("gemini", error.to_string())),
                }
            }
            line = stderr_lines.next_line() => {
                match line {
                    Ok(Some(line)) => stderr_buffer.push(line),
                    Ok(None) => {}
                    Err(error) => stderr_buffer.push(error.to_string()),
                }
            }
        }
    }

    let _ = child.kill().await;
    let _ = child.wait().await;

    if final_message.is_empty() {
        if let Some(result) = prompt_result.as_ref()
            && result
                .get("stopReason")
                .and_then(|value| value.as_str())
                .map(|value| value == "cancelled")
                .unwrap_or(false)
        {
            return Err(process_crashed("gemini", "Gemini ACP run was cancelled."));
        }
        final_message = "Gemini ACP completed the run, but this CLI version did not stream a final assistant message.".to_string();
    }

    let _ = events.send(AiRunEvent::MessageFinal {
        text: final_message.clone(),
    });

    Ok(Some(json!({
        "usedModel": resolved_model,
        "citations": prepared_prompt.citations,
        "retrievalMode": prepared_prompt.retrieval_mode,
        "timingMs": started_at.elapsed().as_millis() as u64,
        "provider": "gemini",
        "providerUsage": prompt_result,
    })))
}

async fn send_rpc(
    stdin: &mut ChildStdin,
    id: i64,
    method: &str,
    params: Value,
) -> GatewayResult<()> {
    let payload = json!({
        "jsonrpc": "2.0",
        "id": id,
        "method": method,
        "params": params,
    });
    stdin
        .write_all(format!("{}\n", payload).as_bytes())
        .await
        .map_err(|error| process_crashed("gemini", error.to_string()))
}

async fn send_response(stdin: &mut ChildStdin, id: i64, result: Value) -> GatewayResult<()> {
    let payload = json!({
        "jsonrpc": "2.0",
        "id": id,
        "result": result,
    });
    stdin
        .write_all(format!("{}\n", payload).as_bytes())
        .await
        .map_err(|error| process_crashed("gemini", error.to_string()))
}

async fn read_response(
    stdout_lines: &mut Lines<BufReader<ChildStdout>>,
    stderr_lines: &mut Lines<BufReader<tokio::process::ChildStderr>>,
    expected_id: i64,
    stderr_buffer: &mut Vec<String>,
    provider: &str,
) -> GatewayResult<Value> {
    loop {
        tokio::select! {
            line = stdout_lines.next_line() => {
                match line {
                    Ok(Some(line)) => {
                        if line.trim().is_empty() {
                            continue;
                        }
                        let value: Value = serde_json::from_str(&line)
                            .map_err(|error| process_crashed(provider, format!("Invalid JSON-RPC response: {error}")))?;
                        if value.get("id").and_then(|v| v.as_i64()) == Some(expected_id) {
                            if let Some(error) = value.get("error") {
                                let message = error.get("message").and_then(|v| v.as_str()).unwrap_or("Provider returned an error.");
                                if message.to_ascii_lowercase().contains("auth")
                                    || message.to_ascii_lowercase().contains("api key")
                                {
                                    return Err(provider_not_authenticated(provider, message));
                                }
                                return Err(process_crashed(provider, message.to_string()));
                            }
                            return Ok(value.get("result").cloned().unwrap_or(Value::Null));
                        }
                    }
                    Ok(None) => return Err(process_crashed(provider, "Process exited before returning a response.")),
                    Err(error) => return Err(process_crashed(provider, error.to_string())),
                }
            }
            line = stderr_lines.next_line() => {
                match line {
                    Ok(Some(line)) => stderr_buffer.push(line),
                    Ok(None) => {}
                    Err(error) => stderr_buffer.push(error.to_string()),
                }
            }
        }
    }
}

async fn handle_permission_request(
    stdin: &mut ChildStdin,
    value: &Value,
    events: &UnboundedSender<AiRunEvent>,
    sessions: Arc<SessionStore>,
    run_id: &str,
    session_id: &str,
) -> GatewayResult<()> {
    let request_id = value
        .get("id")
        .and_then(|v| v.as_i64())
        .ok_or_else(|| process_crashed("gemini", "Permission request did not include an RPC id."))?;
    let params = value.get("params").cloned().unwrap_or(Value::Null);
    let summary = params
        .get("toolCall")
        .and_then(|tool| tool.get("title"))
        .and_then(|value| value.as_str())
        .map(ToString::to_string)
        .unwrap_or_else(|| "Gemini tool permission requested".to_string());
    let (tx, rx) = oneshot::channel::<AiApprovalDecision>();
    let approval_id = sessions
        .register_approval(run_id, session_id, "tool".to_string(), summary.clone(), tx)
        .await;
    let _ = events.send(AiRunEvent::ApprovalRequest {
        approval_id: approval_id.clone(),
        kind: "tool".to_string(),
        payload: params.clone(),
    });
    let decision = rx.await.unwrap_or(AiApprovalDecision {
        decision: "cancel".to_string(),
        scope: None,
    });
    let result = if decision.decision == "cancel" {
        json!({
            "outcome": {
                "outcome": "cancelled"
            }
        })
    } else {
        json!({
            "outcome": {
                "outcome": "selected",
                "optionId": select_permission_option(&params, &decision),
            }
        })
    };
    send_response(stdin, request_id, result).await
}

fn extract_update_text(update: &Value) -> Option<String> {
    update
        .get("content")
        .and_then(|content| content.get("text"))
        .and_then(|value| value.as_str())
        .map(ToString::to_string)
}

fn extract_tool_update_text(update: &Value) -> String {
    if let Some(content) = update.get("content").and_then(|value| value.as_array()) {
        let parts = content
            .iter()
            .filter_map(|entry| {
                entry.get("text")
                    .and_then(|value| value.as_str())
                    .map(ToString::to_string)
                    .or_else(|| entry.get("type").and_then(|value| value.as_str()).map(ToString::to_string))
            })
            .collect::<Vec<_>>();
        if !parts.is_empty() {
            return parts.join("\n");
        }
    }
    update.to_string()
}

fn select_permission_option(params: &Value, decision: &AiApprovalDecision) -> String {
    let options = params
        .get("options")
        .and_then(|value| value.as_array())
        .cloned()
        .unwrap_or_default();
    let find_option = |needle: &[&str]| -> Option<String> {
        options.iter().find_map(|option| {
            let haystack = format!(
                "{} {} {}",
                option.get("optionId").and_then(|value| value.as_str()).unwrap_or_default(),
                option.get("kind").and_then(|value| value.as_str()).unwrap_or_default(),
                option.get("name").and_then(|value| value.as_str()).unwrap_or_default(),
            )
            .to_ascii_lowercase();
            if needle.iter().any(|fragment| haystack.contains(fragment)) {
                option
                    .get("optionId")
                    .and_then(|value| value.as_str())
                    .map(ToString::to_string)
            } else {
                None
            }
        })
    };

    match decision.decision.as_str() {
        "acceptForSession" => find_option(&["always", "session", "proceedalways"])
            .or_else(|| options.last().and_then(|option| option.get("optionId").and_then(|value| value.as_str()).map(ToString::to_string))),
        "decline" => find_option(&["decline", "deny", "reject", "cancel"])
            .or_else(|| options.last().and_then(|option| option.get("optionId").and_then(|value| value.as_str()).map(ToString::to_string))),
        _ => find_option(&["once", "allow", "proceedonce", "accept"])
            .or_else(|| options.first().and_then(|option| option.get("optionId").and_then(|value| value.as_str()).map(ToString::to_string))),
    }
    .unwrap_or_else(|| "cancel".to_string())
}
