use crate::ai_gateway::errors::{GatewayResult, provider_busy, process_crashed};
use crate::ai_gateway::ollama_core;
use crate::ai_gateway::settings::AiGatewaySettings;
use crate::ai_gateway::{AiRunEvent, AiRunRequest, ProviderCapabilities, ProviderId, ProviderStatus};
use tokio::sync::mpsc::UnboundedSender;

pub async fn detect(settings: &AiGatewaySettings) -> ProviderStatus {
    ollama_core::set_ollama_base_url(settings.providers.ollama.base_url.clone());
    match ollama_core::get_ai_status(".".to_string()).await {
        Ok(status) => ProviderStatus {
            provider: ProviderId::Ollama,
            installed: true,
            reachable: status.ollama_reachable,
            authenticated: status.ollama_reachable,
            degraded: !status.ollama_reachable,
            version: None,
            mode: Some("http".to_string()),
            capabilities: ProviderCapabilities {
                chat: true,
                streaming: false,
                retrieval: true,
                embeddings: status.embedding_model.is_some(),
                resume_session: false,
                approvals: false,
                file_edits: false,
                shell_exec: false,
            },
            models: status.available_models,
            default_model: status.chat_model,
            error: if status.ollama_reachable {
                None
            } else {
                Some(crate::ai_gateway::ProviderError {
                    code: "E_PROVIDER_NOT_AUTHENTICATED".to_string(),
                    message: format!(
                        "Ollama is not reachable at {}.",
                        settings.providers.ollama.base_url
                    ),
                    detail: None,
                })
            },
        },
        Err(error) => ProviderStatus {
            provider: ProviderId::Ollama,
            installed: true,
            reachable: false,
            authenticated: false,
            degraded: true,
            version: None,
            mode: Some("http".to_string()),
            capabilities: ProviderCapabilities::default(),
            models: Vec::new(),
            default_model: settings.providers.ollama.default_chat_model.clone(),
            error: Some(crate::ai_gateway::ProviderError {
                code: "E_PROVIDER_NOT_AUTHENTICATED".to_string(),
                message: "Ollama is unavailable.".to_string(),
                detail: Some(error),
            }),
        },
    }
}

pub async fn run_ask(
    request: &AiRunRequest,
    _prepared_prompt: &ollama_core::PreparedAiPrompt,
    settings: &AiGatewaySettings,
    events: UnboundedSender<AiRunEvent>,
) -> GatewayResult<Option<serde_json::Value>> {
    ollama_core::set_ollama_base_url(settings.providers.ollama.base_url.clone());
    let response = ollama_core::ask_ai_question(ollama_core::AiAskRequest {
        repo_root: request.workspace_path.clone(),
        messages: vec![ollama_core::AiChatMessage {
            role: "user".to_string(),
            content: request.prompt.clone(),
        }],
        max_context_chunks: request.retrieval.as_ref().map(|value| value.top_k),
        supplemental_context: request.supplemental_context.clone(),
        supplemental_only: Some(false),
    })
    .await
    .map_err(|error| {
        if error.contains("503") {
            provider_busy("ollama", error)
        } else {
            process_crashed("ollama", error)
        }
    })?;

    let _ = events.send(AiRunEvent::MessageFinal {
        text: response.answer.clone(),
    });
    Ok(Some(serde_json::json!({
        "usedModel": response.used_model,
        "attemptedModels": response.attempted_models,
        "citations": response.citations,
        "retrievalMode": response.retrieval_mode,
        "timingMs": response.timing_ms,
        "modelTotalMs": response.model_total_ms,
        "loadMs": response.load_ms,
        "promptEvalMs": response.prompt_eval_ms,
        "evalMs": response.eval_ms
    })))
}
