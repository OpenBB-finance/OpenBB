use crate::ai_gateway::errors::{
    GatewayResult, process_crashed, provider_not_authenticated, provider_not_installed,
};
use crate::ai_gateway::ollama_core::PreparedAiPrompt;
use crate::ai_gateway::providers::command_runner::RealCommandRunner;
use crate::ai_gateway::sessions::SessionStore;
use crate::ai_gateway::settings::AiGatewaySettings;
use crate::ai_gateway::{AiApprovalDecision, AiRunEvent, AiRunRequest, DiffPreviewFile, SandboxMode};
use serde_json::{Value, json};
use std::process::Stdio;
use std::sync::Arc;
use std::time::Instant;
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader, Lines};
use tokio::process::ChildStdout;
use tokio::sync::{mpsc::UnboundedSender, oneshot};

pub async fn transport_available(_settings: &AiGatewaySettings) -> bool {
    RealCommandRunner::output("codex", &["app-server", "--help"])
        .await
        .map(|output| output.status.success())
        .unwrap_or(false)
}

pub async fn run_agent(
    request: &AiRunRequest,
    prepared_prompt: &PreparedAiPrompt,
    settings: &AiGatewaySettings,
    events: UnboundedSender<AiRunEvent>,
    sessions: Arc<SessionStore>,
    run_id: String,
    session_id: Option<String>,
) -> GatewayResult<Option<Value>> {
    if RealCommandRunner::command("codex").is_err() {
        return Err(provider_not_installed("codex"));
    }
    let Some(session_id) = session_id else {
        return Err(process_crashed("codex", "Agent mode requires a session ID."));
    };

    let mut command = RealCommandRunner::command("codex")?;
    command
        .arg("app-server")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let mut child = command
        .spawn()
        .map_err(|error| process_crashed("codex", error.to_string()))?;
    let mut stdin = child
        .stdin
        .take()
        .ok_or_else(|| process_crashed("codex", "stdin pipe unavailable"))?;
    let stdout = child
        .stdout
        .take()
        .ok_or_else(|| process_crashed("codex", "stdout pipe unavailable"))?;
    let stderr = child
        .stderr
        .take()
        .ok_or_else(|| process_crashed("codex", "stderr pipe unavailable"))?;
    let mut stdout_lines = BufReader::new(stdout).lines();
    let mut stderr_lines = BufReader::new(stderr).lines();
    let mut stderr_buffer = Vec::new();
    let started_at = Instant::now();

    send_rpc(
        &mut stdin,
        1,
        "initialize",
        json!({
            "protocolVersion": "2",
            "clientInfo": { "name": "openbb-desktop", "version": env!("CARGO_PKG_VERSION") },
            "capabilities": {},
        }),
    )
    .await?;
    read_response(&mut stdout_lines, &mut stderr_lines, 1, &mut stderr_buffer, "codex").await?;

    send_rpc(&mut stdin, 2, "account/read", json!({})).await?;
    let account = read_response(&mut stdout_lines, &mut stderr_lines, 2, &mut stderr_buffer, "codex").await?;
    if account
        .get("account")
        .and_then(|value| value.as_object())
        .is_none()
    {
        return Err(provider_not_authenticated(
            "codex",
            "Codex app-server account/read did not return an authenticated account.",
        ));
    }

    send_rpc(
        &mut stdin,
        3,
        "thread/start",
        json!({
            "model": request.model,
            "modelProvider": Value::Null,
            "cwd": request.workspace_path,
            "approvalPolicy": approval_policy(request, settings),
            "sandbox": sandbox_mode(request, settings),
            "config": Value::Null,
            "baseInstructions": Value::Null,
            "developerInstructions": Value::Null,
            "experimentalRawEvents": false,
        }),
    )
    .await?;
    let thread_started = read_response(&mut stdout_lines, &mut stderr_lines, 3, &mut stderr_buffer, "codex").await?;
    let thread_id = thread_started
        .get("thread")
        .and_then(|value| value.get("id"))
        .and_then(|value| value.as_str())
        .ok_or_else(|| process_crashed("codex", "thread/start did not return a thread ID."))?
        .to_string();
    let used_model = thread_started
        .get("model")
        .and_then(|value| value.as_str())
        .map(ToString::to_string)
        .or_else(|| request.model.clone());

    send_rpc(
        &mut stdin,
        4,
        "turn/start",
        json!({
            "threadId": thread_id,
            "input": [{ "type": "text", "text": prepared_prompt.compiled_prompt }],
            "cwd": request.workspace_path,
            "approvalPolicy": approval_policy(request, settings),
            "sandboxPolicy": sandbox_policy(request, settings),
            "model": request.model,
            "effort": Value::Null,
            "summary": Value::Null,
            "outputSchema": Value::Null,
        }),
    )
    .await?;
    read_response(&mut stdout_lines, &mut stderr_lines, 4, &mut stderr_buffer, "codex").await?;

    let mut final_message = String::new();
    let mut sent_final_message = false;
    let mut usage: Option<Value> = None;
    let mut completed = false;

    while !completed {
        tokio::select! {
            line = stdout_lines.next_line() => {
                match line {
                    Ok(Some(line)) => {
                        if line.trim().is_empty() {
                            continue;
                        }
                        let value: Value = serde_json::from_str(&line)
                            .map_err(|error| process_crashed("codex", format!("Invalid app-server JSON: {error}")))?;
                        if let Some(id) = value.get("id").and_then(|v| v.as_i64()) {
                            if id == 0 || value.get("result").is_some() || value.get("error").is_some() {
                                continue;
                            }
                        }
                        if let Some(method) = value.get("method").and_then(|v| v.as_str()) {
                            match method {
                                "turn/started" => {
                                    let _ = events.send(AiRunEvent::Status {
                                        phase: "running".to_string(),
                                    });
                                }
                                "item/agentMessage/delta" => {
                                    if let Some(text) = value.get("params").and_then(|p| p.get("delta")).and_then(|v| v.as_str()) {
                                        final_message.push_str(text);
                                        let _ = events.send(AiRunEvent::MessageDelta { text: text.to_string() });
                                    }
                                }
                                "item/reasoning/summaryTextDelta" => {
                                    if let Some(text) = value.get("params").and_then(|p| p.get("delta")).and_then(|v| v.as_str()) {
                                        let _ = events.send(AiRunEvent::ToolOutput {
                                            name: "reasoning".to_string(),
                                            text: text.to_string(),
                                        });
                                    }
                                }
                                "item/started" => {
                                    if let Some(item) = value.get("params").and_then(|p| p.get("item")) {
                                        if let Some(item_type) = item.get("type").and_then(|v| v.as_str()) {
                                            if item_type == "commandExecution" {
                                                let _ = events.send(AiRunEvent::ToolStarted {
                                                    name: item.get("command").and_then(|v| v.as_str()).unwrap_or("command").to_string(),
                                                    input: Some(item.clone()),
                                                });
                                            }
                                        }
                                    }
                                }
                                "item/commandExecution/outputDelta" => {
                                    let params = value.get("params").cloned().unwrap_or(Value::Null);
                                    let _ = events.send(AiRunEvent::ToolOutput {
                                        name: "command".to_string(),
                                        text: params.get("delta").and_then(|v| v.as_str()).unwrap_or_default().to_string(),
                                    });
                                }
                                "item/completed" => {
                                    if let Some(item) = value.get("params").and_then(|p| p.get("item")) {
                                        match item.get("type").and_then(|v| v.as_str()) {
                                            Some("agentMessage") => {
                                                let text = item.get("text").and_then(|v| v.as_str()).unwrap_or_default().to_string();
                                                if !text.is_empty() {
                                                    final_message = text.clone();
                                                    if !sent_final_message {
                                                        let _ = events.send(AiRunEvent::MessageFinal { text });
                                                        sent_final_message = true;
                                                    }
                                                }
                                            }
                                            Some("reasoning") => {
                                                let text = item
                                                    .get("summary")
                                                    .and_then(|v| v.as_array())
                                                    .map(|items| items.iter().filter_map(|entry| entry.as_str()).collect::<Vec<_>>().join("\n"))
                                                    .filter(|text| !text.is_empty())
                                                    .or_else(|| item.get("content").and_then(|v| v.as_array()).map(|items| items.iter().filter_map(|entry| entry.as_str()).collect::<Vec<_>>().join("\n")))
                                                    .unwrap_or_default();
                                                if !text.is_empty() {
                                                    let _ = events.send(AiRunEvent::ToolOutput {
                                                        name: "reasoning".to_string(),
                                                        text,
                                                    });
                                                }
                                            }
                                            Some("commandExecution") => {
                                                let text = item.get("aggregatedOutput").and_then(|v| v.as_str()).unwrap_or_default().to_string();
                                                if !text.is_empty() {
                                                    let _ = events.send(AiRunEvent::ToolOutput {
                                                        name: item.get("command").and_then(|v| v.as_str()).unwrap_or("command").to_string(),
                                                        text,
                                                    });
                                                }
                                            }
                                            Some("fileChange") => {
                                                if let Some(changes) = item.get("changes").and_then(|v| v.as_array()) {
                                                    let files = changes
                                                        .iter()
                                                        .map(|change| DiffPreviewFile {
                                                            path: change.get("path").and_then(|v| v.as_str()).unwrap_or("file").to_string(),
                                                            diff: change.get("diff").and_then(|v| v.as_str()).unwrap_or_default().to_string(),
                                                        })
                                                        .collect::<Vec<_>>();
                                                    if !files.is_empty() {
                                                        let _ = events.send(AiRunEvent::DiffPreview { files });
                                                    }
                                                }
                                            }
                                            _ => {}
                                        }
                                    }
                                }
                                "codex/event/exec_command_end" => {
                                    if let Some(msg) = value.get("params").and_then(|p| p.get("msg")) {
                                        let text = msg
                                            .get("formatted_output")
                                            .and_then(|v| v.as_str())
                                            .or_else(|| msg.get("aggregated_output").and_then(|v| v.as_str()))
                                            .or_else(|| msg.get("stdout").and_then(|v| v.as_str()))
                                            .unwrap_or_default()
                                            .to_string();
                                        if !text.is_empty() {
                                            let name = msg
                                                .get("command")
                                                .and_then(|v| v.as_array())
                                                .map(|parts| {
                                                    parts
                                                        .iter()
                                                        .filter_map(|part| part.as_str())
                                                        .collect::<Vec<_>>()
                                                        .join(" ")
                                                })
                                                .filter(|name| !name.is_empty())
                                                .unwrap_or_else(|| "command".to_string());
                                            let _ = events.send(AiRunEvent::ToolOutput { name, text });
                                        }
                                    }
                                }
                                "turn/diff_updated" => {
                                    if let Some(diff) = value.get("params").and_then(|p| p.get("diff")).and_then(|v| v.as_str()) {
                                        let _ = events.send(AiRunEvent::DiffPreview {
                                            files: vec![DiffPreviewFile {
                                                path: "turn.diff".to_string(),
                                                diff: diff.to_string(),
                                            }],
                                        });
                                    }
                                }
                                "item/commandExecution/requestApproval" => {
                                    handle_approval_request(
                                        &mut stdin,
                                        &value,
                                        "command",
                                        &events,
                                        sessions.clone(),
                                        &run_id,
                                        &session_id,
                                    )
                                    .await?;
                                }
                                "item/fileChange/requestApproval" => {
                                    handle_approval_request(
                                        &mut stdin,
                                        &value,
                                        "file",
                                        &events,
                                        sessions.clone(),
                                        &run_id,
                                        &session_id,
                                    )
                                    .await?;
                                }
                                "thread/tokenUsage/updated" => {
                                    usage = value.get("params").and_then(|p| p.get("tokenUsage")).cloned().or_else(|| value.get("params").cloned());
                                }
                                "turn/completed" => {
                                    completed = true;
                                    if final_message.is_empty() {
                                        if let Some(turn_status) = value.get("params").and_then(|p| p.get("turn")).and_then(|turn| turn.get("status")).and_then(|v| v.as_str())
                                            && turn_status == "failed"
                                        {
                                            return Err(process_crashed("codex", "Codex app-server turn failed."));
                                        }
                                    }
                                }
                                "error" => {
                                    return Err(process_crashed(
                                        "codex",
                                        value
                                            .get("params")
                                            .and_then(|p| p.get("message"))
                                            .and_then(|v| v.as_str())
                                            .unwrap_or("Codex app-server reported an error.")
                                            .to_string(),
                                    ));
                                }
                                _ => {}
                            }
                        }
                    }
                    Ok(None) => break,
                    Err(error) => return Err(process_crashed("codex", error.to_string())),
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
        return Err(process_crashed("codex", "Codex app-server did not emit a final agent message."));
    }
    if !final_message.is_empty() && !sent_final_message {
        let _ = events.send(AiRunEvent::MessageFinal {
            text: final_message.clone(),
        });
    }

    Ok(Some(json!({
        "usedModel": used_model,
        "citations": prepared_prompt.citations,
        "retrievalMode": prepared_prompt.retrieval_mode,
        "timingMs": started_at.elapsed().as_millis() as u64,
        "provider": "codex",
        "providerUsage": usage,
    })))
}

async fn send_rpc(
    stdin: &mut tokio::process::ChildStdin,
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
        .map_err(|error| process_crashed("codex", error.to_string()))
}

async fn send_response(
    stdin: &mut tokio::process::ChildStdin,
    id: i64,
    result: Value,
) -> GatewayResult<()> {
    let payload = json!({
        "jsonrpc": "2.0",
        "id": id,
        "result": result,
    });
    stdin
        .write_all(format!("{}\n", payload).as_bytes())
        .await
        .map_err(|error| process_crashed("codex", error.to_string()))
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
                                if message.to_ascii_lowercase().contains("auth") || message.to_ascii_lowercase().contains("login") {
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

async fn handle_approval_request(
    stdin: &mut tokio::process::ChildStdin,
    value: &Value,
    kind: &str,
    events: &UnboundedSender<AiRunEvent>,
    sessions: Arc<SessionStore>,
    run_id: &str,
    session_id: &str,
) -> GatewayResult<()> {
    let request_id = value
        .get("id")
        .and_then(|v| v.as_i64())
        .ok_or_else(|| process_crashed("codex", "Approval request did not include an RPC id."))?;
    let params = value.get("params").cloned().unwrap_or(Value::Null);
    let summary = params
        .get("reason")
        .and_then(|v| v.as_str())
        .map(ToString::to_string)
        .unwrap_or_else(|| format!("{kind} approval requested"));
    let (tx, rx) = oneshot::channel::<AiApprovalDecision>();
    let approval_id = sessions
        .register_approval(run_id, session_id, kind.to_string(), summary.clone(), tx)
        .await;
    let _ = events.send(AiRunEvent::ApprovalRequest {
        approval_id: approval_id.clone(),
        kind: kind.to_string(),
        payload: params.clone(),
    });
    let decision = rx.await.unwrap_or(AiApprovalDecision {
        decision: "cancel".to_string(),
        scope: None,
    });
    let result = json!({
        "decision": map_approval_decision(&decision),
    });
    send_response(stdin, request_id, result).await
}

fn map_approval_decision(decision: &AiApprovalDecision) -> Value {
    match decision.decision.as_str() {
        "accept" => Value::String("accept".to_string()),
        "acceptForSession" => Value::String("acceptForSession".to_string()),
        "decline" => Value::String("decline".to_string()),
        _ => Value::String("cancel".to_string()),
    }
}

fn sandbox_mode(request: &AiRunRequest, settings: &AiGatewaySettings) -> &'static str {
    match request
        .execution
        .as_ref()
        .map(|value| &value.sandbox)
        .unwrap_or(&settings.providers.codex.sandbox)
    {
        SandboxMode::ReadOnly => "read-only",
        SandboxMode::WorkspaceWrite => "workspace-write",
        SandboxMode::DangerFullAccess => "danger-full-access",
    }
}

fn sandbox_policy(request: &AiRunRequest, settings: &AiGatewaySettings) -> Value {
    match request
        .execution
        .as_ref()
        .map(|value| &value.sandbox)
        .unwrap_or(&settings.providers.codex.sandbox)
    {
        SandboxMode::ReadOnly => json!({ "type": "readOnly" }),
        SandboxMode::WorkspaceWrite => json!({ "type": "workspaceWrite" }),
        SandboxMode::DangerFullAccess => json!({ "type": "dangerFullAccess" }),
    }
}

fn approval_policy(request: &AiRunRequest, settings: &AiGatewaySettings) -> &'static str {
    match request
        .execution
        .as_ref()
        .map(|value| &value.approval_policy)
        .unwrap_or(&settings.providers.codex.approval_policy)
    {
        crate::ai_gateway::ApprovalPolicy::Default => "on-request",
        crate::ai_gateway::ApprovalPolicy::OnRequest => "on-request",
        crate::ai_gateway::ApprovalPolicy::AutoEdit => "never",
        crate::ai_gateway::ApprovalPolicy::Yolo => "never",
    }
}
