use crate::ai_gateway::errors::GatewayError;
use crate::ai_gateway::providers;
use crate::ai_gateway::retrieval;
use crate::ai_gateway::sessions::{SessionStore, create_run_record};
use crate::ai_gateway::settings::{AiGatewaySettings, load_settings_from_file, save_settings_to_file};
use crate::ai_gateway::sse::encode_event;
use crate::ai_gateway::{
    AiApprovalDecision, AiGatewayStatus, AiRunCreated, AiRunEvent, AiRunRequest, IndexStatus,
    ProviderStatus, SessionDetail, SessionSummary,
};
use axum::extract::{Path as AxumPath, Query, State};
use axum::response::sse::{KeepAlive, Sse};
use axum::response::{IntoResponse, Response};
use axum::routing::{get, post};
use axum::{Json, Router};
use futures_util::stream::{self, StreamExt};
use serde::Deserialize;
use std::convert::Infallible;
use std::path::PathBuf;
use std::sync::Arc;
use std::time::{Duration, Instant};
use tokio::sync::RwLock;
use tokio_stream::wrappers::BroadcastStream;
use uuid::Uuid;

#[derive(Clone)]
pub struct GatewayState {
    pub settings_path: PathBuf,
    pub sessions: Arc<SessionStore>,
    pub provider_status_cache: Arc<RwLock<Option<(Instant, Vec<ProviderStatus>)>>>,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
struct StatusQuery {
    workspace_path: Option<String>,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
struct BuildIndexBody {
    workspace_path: String,
    force: Option<bool>,
    embedding_provider: Option<String>,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
struct ClearIndexBody {
    workspace_path: String,
}

pub fn build_router(settings_path: PathBuf) -> Router {
    let state = GatewayState {
        settings_path,
        sessions: Arc::new(SessionStore::default()),
        provider_status_cache: Arc::new(RwLock::new(None)),
    };

    Router::new()
        .route("/v1/status", get(get_status))
        .route("/v1/providers/status", get(get_provider_statuses))
        .route("/v1/index/status", get(get_index_status))
        .route("/v1/index/build", post(post_build_index))
        .route("/v1/index/clear", post(post_clear_index))
        .route("/v1/runs", post(post_run))
        .route("/v1/runs/{run_id}/stream", get(get_run_stream))
        .route("/v1/runs/{run_id}/cancel", post(post_cancel_run))
        .route("/v1/sessions", get(get_sessions))
        .route("/v1/sessions/{session_id}", get(get_session_detail))
        .route("/v1/approvals/{approval_id}/respond", post(post_approval_response))
        .route("/v1/settings", get(get_settings).put(put_settings))
        .with_state(state)
}

async fn get_status(
    State(state): State<GatewayState>,
    Query(query): Query<StatusQuery>,
) -> Result<Json<AiGatewayStatus>, GatewayError> {
    let settings = load_settings_from_file(&state.settings_path)
        .map_err(|error| GatewayError::new("E_INVALID_CONFIG", error))?;
    let workspace_path = query.workspace_path.unwrap_or_else(|| ".".to_string());
    let providers = cached_provider_statuses(&state, &settings).await;
    let index = retrieval::index_status(workspace_path.clone(), &settings)
        .await
        .unwrap_or_else(|_| IndexStatus::default());
    Ok(Json(AiGatewayStatus {
        gateway_version: env!("CARGO_PKG_VERSION").to_string(),
        workspace_path: Some(workspace_path.clone()),
        workspace_ready: std::path::Path::new(&workspace_path).exists(),
        default_provider: settings.default_provider.clone(),
        default_mode: settings.default_mode.clone(),
        providers,
        index,
        settings_path: Some(state.settings_path.to_string_lossy().to_string()),
        feature_flags: settings.feature_flags.clone(),
    }))
}

async fn get_provider_statuses(
    State(state): State<GatewayState>,
) -> Result<Json<Vec<ProviderStatus>>, GatewayError> {
    let settings = load_settings_from_file(&state.settings_path)
        .map_err(|error| GatewayError::new("E_INVALID_CONFIG", error))?;
    Ok(Json(cached_provider_statuses(&state, &settings).await))
}

async fn get_index_status(
    State(state): State<GatewayState>,
    Query(query): Query<StatusQuery>,
) -> Result<Json<IndexStatus>, GatewayError> {
    let settings = load_settings_from_file(&state.settings_path)
        .map_err(|error| GatewayError::new("E_INVALID_CONFIG", error))?;
    let workspace_path = query.workspace_path.unwrap_or_else(|| ".".to_string());
    let status = retrieval::index_status(workspace_path, &settings)
        .await
        .map_err(|error| GatewayError::new("E_INDEX_STALE", error))?;
    Ok(Json(status))
}

async fn post_build_index(
    State(state): State<GatewayState>,
    Json(body): Json<BuildIndexBody>,
) -> Result<Json<serde_json::Value>, GatewayError> {
    let settings = load_settings_from_file(&state.settings_path)
        .map_err(|error| GatewayError::new("E_INVALID_CONFIG", error))?;
    let _ = body.embedding_provider;
    let payload = retrieval::build_index(body.workspace_path, body.force.unwrap_or(false), &settings)
        .await
        .map_err(|error| GatewayError::new("E_INDEX_STALE", error))?;
    Ok(Json(payload))
}

async fn post_clear_index(
    State(state): State<GatewayState>,
    Json(body): Json<ClearIndexBody>,
) -> Result<Json<serde_json::Value>, GatewayError> {
    let settings = load_settings_from_file(&state.settings_path)
        .map_err(|error| GatewayError::new("E_INVALID_CONFIG", error))?;
    let payload = retrieval::clear_index(body.workspace_path, &settings)
        .await
        .map_err(|error| GatewayError::new("E_INDEX_STALE", error))?;
    Ok(Json(payload))
}

async fn post_run(
    State(state): State<GatewayState>,
    Json(request): Json<AiRunRequest>,
) -> Result<Json<AiRunCreated>, GatewayError> {
    let settings = load_settings_from_file(&state.settings_path)
        .map_err(|error| GatewayError::new("E_INVALID_CONFIG", error))?;
    providers::ensure_agent_supported(&request, &settings)?;

    let run_id = Uuid::new_v4().to_string();
    let session_id = request
        .session_id
        .clone()
        .or_else(|| Some(Uuid::new_v4().to_string()));
    let title = request
        .prompt
        .lines()
        .next()
        .map(|line| line.trim())
        .filter(|line| !line.is_empty())
        .map(|line| line.chars().take(120).collect::<String>())
        .unwrap_or_else(|| "AI session".to_string());
    let record = create_run_record(
        run_id.clone(),
        session_id.clone(),
        request.provider.clone(),
        request.mode.clone(),
        title,
    );
    let _ = record.input_tx.send(AiRunEvent::Status {
        phase: "queued".to_string(),
    });
    state.sessions.insert(record.clone()).await;

    let request_clone = request.clone();
    let settings_clone = settings.clone();
    let worker_record = record.clone();
    let sessions = state.sessions.clone();
    let run_id_for_worker = run_id.clone();
    let session_id_for_worker = session_id.clone();
    let worker = tokio::spawn(async move {
        let _ = worker_record.input_tx.send(AiRunEvent::Status {
            phase: "running".to_string(),
        });
        let prepared_prompt = match retrieval::prepare_prompt(&request_clone, &settings_clone).await {
            Ok(prompt) => prompt,
            Err(error) => {
                let _ = worker_record.input_tx.send(AiRunEvent::Error {
                    code: "E_INDEX_STALE".to_string(),
                    message: error,
                    detail: None,
                });
                let _ = worker_record.input_tx.send(AiRunEvent::Done { usage: None });
                return;
            }
        };
        let result = if request_clone.mode == crate::ai_gateway::AiMode::Agent {
            providers::run_agent(
                &request_clone,
                &prepared_prompt,
                &settings_clone,
                worker_record.input_tx.clone(),
                sessions,
                run_id_for_worker,
                session_id_for_worker,
            )
            .await
        } else {
            providers::run_ask(
                &request_clone,
                &prepared_prompt,
                &settings_clone,
                worker_record.input_tx.clone(),
            )
            .await
        };
        match result {
            Ok(usage) => {
                let _ = worker_record.input_tx.send(AiRunEvent::Done { usage });
            }
            Err(error) => {
                let _ = worker_record.input_tx.send(AiRunEvent::Error {
                    code: error.code,
                    message: error.message,
                    detail: error.detail.map(serde_json::Value::String),
                });
                let _ = worker_record.input_tx.send(AiRunEvent::Done { usage: None });
            }
        }
    });
    if let Ok(mut guard) = record.worker.lock() {
        *guard = Some(worker);
    }

    Ok(Json(AiRunCreated {
        run_id: run_id.clone(),
        session_id,
        stream_url: format!("/v1/runs/{run_id}/stream"),
    }))
}

async fn get_run_stream(
    State(state): State<GatewayState>,
    AxumPath(run_id): AxumPath<String>,
) -> Result<Sse<impl futures_util::Stream<Item = Result<axum::response::sse::Event, Infallible>>>, GatewayError>
{
    let record = state
        .sessions
        .get(&run_id)
        .await
        .ok_or_else(|| GatewayError::new("E_PROCESS_CRASHED", format!("Unknown run `{run_id}`.")))?;
    let history = record.history_snapshot();
    let live = BroadcastStream::new(record.subscribe()).filter_map(|event| async move {
        match event {
            Ok(event) => Some(Ok::<_, Infallible>(encode_event(&event))),
            Err(_) => None,
        }
    });
    let history_stream = stream::iter(
        history
            .into_iter()
            .map(|event| Ok::<_, Infallible>(encode_event(&event))),
    );
    Ok(Sse::new(history_stream.chain(live)).keep_alive(KeepAlive::new().interval(Duration::from_secs(15))))
}

async fn post_cancel_run(
    State(state): State<GatewayState>,
    AxumPath(run_id): AxumPath<String>,
) -> Result<Json<serde_json::Value>, GatewayError> {
    Ok(Json(serde_json::json!({
        "ok": state.sessions.cancel(&run_id).await,
    })))
}

async fn get_sessions(
    State(state): State<GatewayState>,
) -> Result<Json<Vec<SessionSummary>>, GatewayError> {
    Ok(Json(state.sessions.list_sessions().await))
}

async fn get_session_detail(
    State(state): State<GatewayState>,
    AxumPath(session_id): AxumPath<String>,
) -> Result<Json<SessionDetail>, GatewayError> {
    state
        .sessions
        .session_detail(&session_id)
        .await
        .map(Json)
        .ok_or_else(|| GatewayError::new("E_PROCESS_CRASHED", format!("Unknown session `{session_id}`.")))
}

async fn post_approval_response(
    State(state): State<GatewayState>,
    AxumPath(approval_id): AxumPath<String>,
    Json(decision): Json<AiApprovalDecision>,
) -> Result<Json<serde_json::Value>, GatewayError> {
    Ok(Json(serde_json::json!({
        "ok": state.sessions.resolve_approval(&approval_id, decision).await,
    })))
}

async fn get_settings(
    State(state): State<GatewayState>,
) -> Result<Json<AiGatewaySettings>, GatewayError> {
    let settings = load_settings_from_file(&state.settings_path)
        .map_err(|error| GatewayError::new("E_INVALID_CONFIG", error))?;
    Ok(Json(settings))
}

async fn put_settings(
    State(state): State<GatewayState>,
    Json(settings): Json<AiGatewaySettings>,
) -> Result<Json<AiGatewaySettings>, GatewayError> {
    save_settings_to_file(&state.settings_path, &settings)
        .map_err(|error| GatewayError::new("E_INVALID_CONFIG", error))?;
    *state.provider_status_cache.write().await = None;
    Ok(Json(settings))
}

async fn cached_provider_statuses(state: &GatewayState, settings: &AiGatewaySettings) -> Vec<ProviderStatus> {
    if let Some((instant, statuses)) = state.provider_status_cache.read().await.as_ref()
        && instant.elapsed() < Duration::from_secs(30)
    {
        return statuses.clone();
    }
    let statuses = providers::detect_all(settings).await;
    *state.provider_status_cache.write().await = Some((Instant::now(), statuses.clone()));
    statuses
}

impl IntoResponse for GatewayError {
    fn into_response(self) -> Response {
        let status = match self.code.as_str() {
            "E_PROVIDER_NOT_INSTALLED" => axum::http::StatusCode::BAD_REQUEST,
            "E_PROVIDER_NOT_AUTHENTICATED" => axum::http::StatusCode::UNAUTHORIZED,
            "E_PROVIDER_BUSY" => axum::http::StatusCode::SERVICE_UNAVAILABLE,
            "E_UNSUPPORTED_TRANSPORT" => axum::http::StatusCode::BAD_REQUEST,
            _ => axum::http::StatusCode::INTERNAL_SERVER_ERROR,
        };
        let body = Json(serde_json::json!({
            "error": self.message,
            "code": self.code,
            "detail": self.detail,
        }));
        (status, body).into_response()
    }
}
