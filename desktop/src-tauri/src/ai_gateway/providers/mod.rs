pub mod command_runner;
pub mod codex_app_server;
pub mod codex_exec;
pub mod gemini_acp;
pub mod gemini_headless;
pub mod ollama;

use crate::ai_gateway::errors::{GatewayError, GatewayResult, unsupported_transport};
use crate::ai_gateway::ollama_core::{AiAskRequest, PreparedAiPrompt};
use crate::ai_gateway::sessions::SessionStore;
use crate::ai_gateway::settings::AiGatewaySettings;
use crate::ai_gateway::{AiMode, AiRunEvent, AiRunRequest, ProviderId, ProviderStatus};
use std::sync::Arc;
use tokio::sync::mpsc::UnboundedSender;

pub async fn detect_all(settings: &AiGatewaySettings) -> Vec<ProviderStatus> {
    vec![
        ollama::detect(settings).await,
        codex_exec::detect(settings).await,
        gemini_headless::detect(settings).await,
    ]
}

pub async fn run_ask(
    request: &AiRunRequest,
    prepared_prompt: &PreparedAiPrompt,
    settings: &AiGatewaySettings,
    events: UnboundedSender<AiRunEvent>,
) -> GatewayResult<Option<serde_json::Value>> {
    match request.provider {
        ProviderId::Ollama => {
            ollama::run_ask(request, prepared_prompt, settings, events).await
        }
        ProviderId::Codex => {
            codex_exec::run_ask(request, prepared_prompt, settings, events).await
        }
        ProviderId::Gemini => {
            gemini_headless::run_ask(request, prepared_prompt, settings, events).await
        }
    }
}

pub fn ensure_agent_supported(request: &AiRunRequest, settings: &AiGatewaySettings) -> GatewayResult<()> {
    if request.mode != AiMode::Agent {
        return Ok(());
    }

    match request.provider {
        ProviderId::Ollama => Err(unsupported_transport("ollama", "agent")),
        ProviderId::Codex => {
            if settings.feature_flags.codex_agent_enabled {
                Ok(())
            } else {
                Err(unsupported_transport("codex", "app-server"))
            }
        }
        ProviderId::Gemini => {
            if settings.feature_flags.gemini_agent_enabled {
                Ok(())
            } else {
                Err(unsupported_transport("gemini", "acp"))
            }
        }
    }
}

pub async fn run_agent(
    request: &AiRunRequest,
    prepared_prompt: &PreparedAiPrompt,
    settings: &AiGatewaySettings,
    events: UnboundedSender<AiRunEvent>,
    sessions: Arc<SessionStore>,
    run_id: String,
    session_id: Option<String>,
) -> GatewayResult<Option<serde_json::Value>> {
    match request.provider {
        ProviderId::Ollama => Err(unsupported_transport("ollama", "agent")),
        ProviderId::Codex => {
            codex_app_server::run_agent(
                request,
                prepared_prompt,
                settings,
                events,
                sessions,
                run_id,
                session_id,
            )
            .await
        }
        ProviderId::Gemini => {
            gemini_acp::run_agent(
                request,
                prepared_prompt,
                settings,
                events,
                sessions,
                run_id,
                session_id,
            )
            .await
        }
    }
}

pub fn build_legacy_request(request: &AiRunRequest) -> AiAskRequest {
    AiAskRequest {
        repo_root: request.workspace_path.clone(),
        messages: vec![crate::ai_gateway::ollama_core::AiChatMessage {
            role: "user".to_string(),
            content: request.prompt.clone(),
        }],
        max_context_chunks: request.retrieval.as_ref().map(|value| value.top_k),
        supplemental_context: request.supplemental_context.clone(),
        supplemental_only: Some(false),
    }
}

pub fn send_error(events: &UnboundedSender<AiRunEvent>, error: &GatewayError) {
    let _ = events.send(AiRunEvent::Error {
        code: error.code.clone(),
        message: error.message.clone(),
        detail: error
            .detail
            .as_ref()
            .map(|detail| serde_json::Value::String(detail.clone())),
    });
}
