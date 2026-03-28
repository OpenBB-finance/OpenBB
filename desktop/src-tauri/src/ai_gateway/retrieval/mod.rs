use crate::ai_gateway::ollama_core::{self, AiAskRequest, PreparedAiPrompt, RetrievalMode};
use crate::ai_gateway::settings::AiGatewaySettings;
use crate::ai_gateway::{AiRunRequest, IndexStatus, ProviderId, RetrievalStrategy};

pub async fn index_status(
    workspace_path: String,
    settings: &AiGatewaySettings,
) -> Result<IndexStatus, String> {
    ollama_core::set_ollama_base_url(settings.providers.ollama.base_url.clone());
    let status = ollama_core::get_ai_status(workspace_path).await?;
    Ok(IndexStatus {
        workspace_path: status.repo_root,
        ready: status.index_ready,
        last_indexed_at: status.last_indexed_at,
        chunk_count: status.chunk_count,
        mode: match status.mode {
            RetrievalMode::Semantic => RetrievalStrategy::Semantic,
            RetrievalMode::Lexical => RetrievalStrategy::Lexical,
            RetrievalMode::Supplemental => RetrievalStrategy::Lexical,
        },
        revision: None,
        embedding_provider: status.embedding_model.as_ref().map(|_| ProviderId::Ollama),
        embedding_model: status.embedding_model,
        stale: false,
    })
}

pub async fn build_index(
    workspace_path: String,
    force: bool,
    settings: &AiGatewaySettings,
) -> Result<serde_json::Value, String> {
    ollama_core::set_ollama_base_url(settings.providers.ollama.base_url.clone());
    let result = ollama_core::build_ai_index(workspace_path, Some(force)).await?;
    serde_json::to_value(result).map_err(|error| format!("Failed to serialize index build result: {error}"))
}

pub async fn clear_index(
    workspace_path: String,
    settings: &AiGatewaySettings,
) -> Result<serde_json::Value, String> {
    ollama_core::set_ollama_base_url(settings.providers.ollama.base_url.clone());
    ollama_core::clear_ai_index(workspace_path).await
}

pub async fn prepare_prompt(
    request: &AiRunRequest,
    settings: &AiGatewaySettings,
) -> Result<PreparedAiPrompt, String> {
    ollama_core::set_ollama_base_url(settings.providers.ollama.base_url.clone());
    ollama_core::prepare_ai_prompt(AiAskRequest {
        repo_root: request.workspace_path.clone(),
        messages: vec![ollama_core::AiChatMessage {
            role: "user".to_string(),
            content: request.prompt.clone(),
        }],
        max_context_chunks: request.retrieval.as_ref().map(|value| value.top_k),
        supplemental_context: request.supplemental_context.clone(),
        supplemental_only: Some(
            request
                .retrieval
                .as_ref()
                .map(|value| !value.enabled)
                .unwrap_or(false),
        ),
    })
    .await
}
