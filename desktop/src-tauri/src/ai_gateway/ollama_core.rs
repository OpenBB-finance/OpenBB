use crate::ai_gateway::settings::default_user_settings_path;
use chrono::Utc;
use once_cell::sync::Lazy;
use openssl::sha::sha1;
use regex::Regex;
use reqwest::Client;
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::cmp::{Ordering, min};
use std::collections::{HashMap, HashSet, VecDeque};
use std::fs;
use std::io::{BufRead, BufReader, Read, Write};
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::Mutex;
use std::time::{Duration, Instant};

const DEFAULT_OLLAMA_BASE_URL: &str = "http://127.0.0.1:11434/api";
const MAX_FILE_SIZE_BYTES: u64 = 256 * 1024;
const CHUNK_LINES: usize = 120;
const CHUNK_OVERLAP: usize = 20;
const MAX_INDEX_LINE_CHARS: usize = 1200;
const MAX_INDEX_CHUNK_CHARS: usize = 8000;
const MAX_EMBED_INPUT_CHARS: usize = 2000;
const DEFAULT_CONTEXT_CHUNKS: usize = 10;
const MAX_CONTEXT_CHUNKS: usize = 16;
const EMBED_BATCH_SIZE: usize = 4;
const MAX_CHAT_CANDIDATES: usize = 4;
const CHAT_KEEP_ALIVE: &str = "15m";
const OLLAMA_DISCOVERY_CACHE_TTL: Duration = Duration::from_secs(30);
const SUMMARY_CHUNK_PATH: &str = "__project_summary__.md";
const PINNED_PATHS: [&str; 3] = [
    "README.md",
    "desktop/src/routes/__root.tsx",
    "desktop/src-tauri/src/main.rs",
];
const EXCLUDED_DIRS: [&str; 7] = [
    ".git",
    "node_modules",
    "dist",
    "target",
    ".venv",
    "logs",
    "build",
];
const EXTRA_EXCLUDED_DIRS: [&str; 1] = [".playwright-cli"];
const ALLOWED_EXTENSIONS: [&str; 11] = [
    "ts", "tsx", "js", "jsx", "rs", "py", "md", "toml", "json", "yml", "yaml",
];
const EXTRA_ALLOWED_EXTENSIONS: [&str; 1] = ["ps1"];
const LOCKFILES: [&str; 8] = [
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "poetry.lock",
    "uv.lock",
    "Cargo.lock",
    "bun.lockb",
    "composer.lock",
];
const ENDPOINT_ROUTE_MARKERS: [(&str, f32); 11] = [
    ("server.middlewares.use(\"/__ai\"", 26.0),
    ("server.middlewares.use(\"/\"", 10.0),
    ("requesturl.pathname ===", 16.0),
    ("req.method === \"get\"", 6.0),
    ("req.method === \"post\"", 6.0),
    ("#[tauri::command]", 20.0),
    ("generate_handler!(", 18.0),
    ("invoke_handler(", 12.0),
    ("jsonresponse(res, 200", 4.0),
    ("jsonresponse(res, 400", 3.0),
    ("jsonresponse(res, 404", 3.0),
];

static AI_INDEX_CACHE: Lazy<Mutex<HashMap<String, CachedAiIndex>>> =
    Lazy::new(|| Mutex::new(HashMap::new()));
static OLLAMA_BASE_URL_OVERRIDE: Lazy<Mutex<String>> =
    Lazy::new(|| Mutex::new(DEFAULT_OLLAMA_BASE_URL.to_string()));
static OLLAMA_DISCOVERY_CACHE: Lazy<Mutex<Option<(Instant, OllamaDiscovery)>>> =
    Lazy::new(|| Mutex::new(None));
static ENDPOINT_QUERY_RE: Lazy<Regex> = Lazy::new(|| {
    Regex::new(
        r"(?i)(endpoint|endpoints|route|routes|command|commands|handler|handlers|api|apis|path|paths|url|urls|invoke|invokes|expose|exposes|tauri|middleware)",
    )
    .unwrap()
});
static ROUTE_LITERAL_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r#"['"`](\/[A-Za-z0-9_./:-]+)['"`]"#).unwrap());
static NOISY_PATH_RE: Lazy<Regex> =
    Lazy::new(|| Regex::new(r"(?i)(^|/)(tests?|__tests__)/record/|(^|/)record/http/").unwrap());

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum RetrievalMode {
    Semantic,
    Lexical,
    Supplemental,
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
    pub mode: RetrievalMode,
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
    pub retrieval_mode: RetrievalMode,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PreparedAiPrompt {
    pub system_prompt: String,
    pub context_prompt: String,
    pub latest_user_prompt: String,
    pub compiled_prompt: String,
    pub citations: Vec<AiCitation>,
    pub retrieval_mode: RetrievalMode,
    pub repo_root: String,
    pub available_embedding_model: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct AiIndexManifest {
    repo_root: String,
    repo_hash: String,
    head_revision: String,
    config_hash: String,
    revision: String,
    scanned_files: usize,
    indexed_files: usize,
    skipped_files: usize,
    chunk_count: usize,
    last_indexed_at: String,
    embedding_model: Option<String>,
    embedding_dim: Option<usize>,
    mode: RetrievalMode,
    summary_prompt: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct IndexedChunk {
    path: String,
    start_line: usize,
    end_line: usize,
    sha1: String,
    language: String,
    text: String,
}

#[derive(Debug, Clone)]
struct CachedAiIndex {
    manifest: AiIndexManifest,
    chunks: Vec<IndexedChunk>,
    embeddings: Vec<Vec<f32>>,
}

#[derive(Debug, Clone)]
struct RepoContext {
    repo_root: Option<PathBuf>,
    repo_ready: bool,
}

#[derive(Debug, Clone)]
struct IndexContext {
    repo_hash: String,
    head_revision: String,
    config_hash: String,
    revision: String,
}

#[derive(Debug, Clone)]
struct OllamaDiscovery {
    reachable: bool,
    available_models: Vec<String>,
    chat_model: Option<String>,
    chat_candidates: Vec<String>,
    embedding_model: Option<String>,
}

pub fn set_ollama_base_url(base_url: impl Into<String>) {
    let value = base_url.into();
    if let Ok(mut guard) = OLLAMA_BASE_URL_OVERRIDE.lock() {
        *guard = value;
    }
    if let Ok(mut discovery) = OLLAMA_DISCOVERY_CACHE.lock() {
        *discovery = None;
    }
}

pub fn current_ollama_base_url() -> String {
    OLLAMA_BASE_URL_OVERRIDE
        .lock()
        .map(|guard| guard.clone())
        .unwrap_or_else(|_| DEFAULT_OLLAMA_BASE_URL.to_string())
}

#[derive(Debug, Clone, Deserialize)]
struct OllamaTagsResponse {
    #[serde(default)]
    models: Vec<OllamaModel>,
}

#[derive(Debug, Clone, Default, Deserialize)]
struct OllamaModelDetails {
    #[serde(default)]
    parameter_size: String,
}

#[derive(Debug, Clone, Deserialize)]
struct OllamaModel {
    name: String,
    #[serde(default)]
    size: u64,
    #[serde(default)]
    details: OllamaModelDetails,
}

#[derive(Debug, Deserialize)]
struct OllamaEmbedResponse {
    #[serde(default)]
    embeddings: Vec<Vec<f32>>,
}

#[derive(Debug, Deserialize)]
struct OllamaChatResponse {
    model: String,
    message: OllamaChatMessageResponse,
    #[serde(default)]
    total_duration: Option<u64>,
    #[serde(default)]
    load_duration: Option<u64>,
    #[serde(default)]
    prompt_eval_duration: Option<u64>,
    #[serde(default)]
    eval_duration: Option<u64>,
}

#[derive(Debug, Deserialize)]
struct OllamaChatMessageResponse {
    content: String,
}

#[derive(Debug, Clone)]
struct RankedChunk {
    index: usize,
    score: f32,
}

pub async fn get_ai_status(default_dir: String) -> Result<AiStatus, String> {
    let repo_context = resolve_repo_context(&default_dir)?;
    let client = build_http_client(5)?;
    let discovery = discover_ollama(&client).await;

    let mut index_ready = false;
    let mut last_indexed_at = None;
    let mut chunk_count = 0;
    let mut status_mode = RetrievalMode::Lexical;

    if repo_context.repo_ready
        && let Some(repo_root) = repo_context.repo_root.as_ref()
    {
        let index_context = build_index_context(repo_root, discovery.embedding_model.as_deref())?;
        if let Some(manifest) = read_manifest_if_present(&index_directory(&index_context)?)? {
            last_indexed_at = Some(manifest.last_indexed_at.clone());
            chunk_count = manifest.chunk_count;
            index_ready = manifest.revision == index_context.revision;
            if index_ready && manifest.embedding_model.is_some() && manifest.embedding_dim.unwrap_or(0) > 0 {
                status_mode = RetrievalMode::Semantic;
            }
        }
    }

    Ok(AiStatus {
        repo_root: repo_context
            .repo_root
            .as_ref()
            .map(|path| path.to_string_lossy().to_string()),
        repo_ready: repo_context.repo_ready,
        ollama_reachable: discovery.reachable,
        chat_model: discovery.chat_model,
        chat_candidates: discovery.chat_candidates,
        embedding_model: discovery.embedding_model,
        available_models: discovery.available_models,
        index_ready,
        last_indexed_at,
        chunk_count,
        mode: status_mode,
    })
}

pub async fn warm_ai_chat_model(default_dir: String) -> Result<serde_json::Value, String> {
    let _ = default_dir;

    let client = build_http_client(60)?;
    let discovery = discover_ollama(&client).await;
    if !discovery.reachable || discovery.chat_candidates.is_empty() {
        return Ok(json!({
            "ok": false,
            "usedModel": serde_json::Value::Null,
        }));
    }

    let response = chat_with_fallback(
        &client,
        &discovery.chat_candidates[..1],
        vec![
            json!({
                "role": "system",
                "content": "Reply with READY only.",
            }),
            json!({
                "role": "user",
                "content": "READY",
            }),
        ],
    )
    .await?;

    Ok(json!({
        "ok": true,
        "usedModel": response.response.model,
    }))
}

pub async fn build_ai_index(repo_root: String, force: Option<bool>) -> Result<AiIndexResult, String> {
    let repo_root = ensure_repo_root(&repo_root)?;
    let client = build_http_client(300)?;
    let discovery = discover_ollama(&client).await;
    let index_context = build_index_context(&repo_root, discovery.embedding_model.as_deref())?;
    let index_dir = index_directory(&index_context)?;

    if !force.unwrap_or(false)
        && let Some(existing_manifest) = read_manifest_if_present(&index_dir)?
        && existing_manifest.revision == index_context.revision
    {
        if let Ok(cache) = load_cached_index(&repo_root, &index_context) {
            let mut store = AI_INDEX_CACHE.lock().unwrap();
            store.insert(index_context.repo_hash.clone(), cache);
        }
        return Ok(AiIndexResult {
            repo_root: repo_root.to_string_lossy().to_string(),
            scanned_files: existing_manifest.scanned_files,
            indexed_files: existing_manifest.indexed_files,
            skipped_files: existing_manifest.skipped_files,
            chunk_count: existing_manifest.chunk_count,
            last_indexed_at: existing_manifest.last_indexed_at,
            revision: existing_manifest.revision,
        });
    }

    fs::create_dir_all(&index_dir).map_err(|error| {
        format!(
            "Failed to create AI index directory {}: {error}",
            index_dir.display()
        )
    })?;

    let repo_files = collect_repo_files(&repo_root)?;
    let scanned_files = repo_files.len();
    let mut indexed_files = 0usize;
    let mut chunks = Vec::new();

    let summary_prompt = build_project_summary(&repo_root, &repo_files);
    chunks.push(IndexedChunk {
        path: SUMMARY_CHUNK_PATH.to_string(),
        start_line: 1,
        end_line: summary_prompt.lines().count().max(1),
        sha1: sha1_hex(summary_prompt.as_bytes()),
        language: "md".to_string(),
        text: summary_prompt.clone(),
    });

    for file_path in &repo_files {
        if let Some(relative_path) = normalize_relative_path(&repo_root, file_path) {
            let Some(file_contents) = read_text_file(file_path)? else {
                continue;
            };
            let language = detect_language(&relative_path);
            let file_chunks = chunk_file_contents(&relative_path, &language, &file_contents);
            if !file_chunks.is_empty() {
                indexed_files += 1;
                chunks.extend(file_chunks);
            }
        }
    }

    let skipped_files = scanned_files.saturating_sub(indexed_files);
    let mut embeddings = Vec::new();
    let mut embedding_dim = None;
    let mut embedding_model = discovery.embedding_model.clone();
    let mode = if let Some(model) = embedding_model.clone() {
        match embed_chunks(&client, &model, &chunks).await {
            Ok(embedded) => {
                embedding_dim = embedded.first().map(std::vec::Vec::len);
                embeddings = embedded;
                RetrievalMode::Semantic
            }
            Err(_) => {
                embedding_model = None;
                RetrievalMode::Lexical
            }
        }
    } else {
        RetrievalMode::Lexical
    };

    let last_indexed_at = Utc::now().to_rfc3339();
    let manifest = AiIndexManifest {
        repo_root: repo_root.to_string_lossy().to_string(),
        repo_hash: index_context.repo_hash.clone(),
        head_revision: index_context.head_revision.clone(),
        config_hash: index_context.config_hash.clone(),
        revision: index_context.revision.clone(),
        scanned_files,
        indexed_files,
        skipped_files,
        chunk_count: chunks.len(),
        last_indexed_at: last_indexed_at.clone(),
        embedding_model,
        embedding_dim,
        mode: mode.clone(),
        summary_prompt,
    };

    write_manifest(&index_dir, &manifest)?;
    write_chunks(&index_dir, &chunks)?;
    write_embeddings(&index_dir, &embeddings)?;

    let cached_index = CachedAiIndex {
        manifest: manifest.clone(),
        chunks,
        embeddings,
    };
    let mut store = AI_INDEX_CACHE.lock().unwrap();
    store.insert(index_context.repo_hash.clone(), cached_index);

    Ok(AiIndexResult {
        repo_root: repo_root.to_string_lossy().to_string(),
        scanned_files,
        indexed_files,
        skipped_files,
        chunk_count: manifest.chunk_count,
        last_indexed_at,
        revision: index_context.revision,
    })
}

pub async fn clear_ai_index(repo_root: String) -> Result<serde_json::Value, String> {
    let repo_root = ensure_repo_root(&repo_root)?;
    let index_context = build_index_context(&repo_root, None)?;
    let index_dir = index_directory(&index_context)?;
    if index_dir.exists() {
        fs::remove_dir_all(&index_dir).map_err(|error| {
            format!("Failed to clear AI index directory {}: {error}", index_dir.display())
        })?;
    }

    let mut store = AI_INDEX_CACHE.lock().unwrap();
    store.remove(&index_context.repo_hash);

    Ok(json!({ "ok": true }))
}

pub async fn prepare_ai_prompt(request: AiAskRequest) -> Result<PreparedAiPrompt, String> {
    let client = build_http_client(90)?;
    let discovery = discover_ollama(&client).await;
    let supplemental_context = request
        .supplemental_context
        .as_deref()
        .map(str::trim)
        .filter(|value| !value.is_empty());
    let supplemental_only = request.supplemental_only.unwrap_or(false) && supplemental_context.is_some();

    let latest_user_message = request
        .messages
        .iter()
        .rev()
        .find(|message| message.role == "user")
        .or_else(|| request.messages.last())
        .ok_or_else(|| "A question is required before asking the project AI.".to_string())?;

    let mut cached_index: Option<CachedAiIndex> = None;
    let mut selected_indexes: Vec<usize> = Vec::new();
    let mut citations: Vec<AiCitation> = Vec::new();
    let mut include_summary = false;
    let retrieval_mode = if supplemental_only {
        RetrievalMode::Supplemental
    } else {
        let repo_root = ensure_repo_root(&request.repo_root)?;
        let index_context = build_index_context(&repo_root, discovery.embedding_model.as_deref())?;
        let next_index = load_cached_index(&repo_root, &index_context).or_else(|_| {
            let lexical_context = build_index_context(&repo_root, None)?;
            load_cached_index(&repo_root, &lexical_context)
        })?;

        if next_index.chunks.is_empty() {
            return Err("AI index is empty. Rebuild the index and try again.".to_string());
        }

        let requested_context = request
            .max_context_chunks
            .unwrap_or(DEFAULT_CONTEXT_CHUNKS)
            .clamp(1, MAX_CONTEXT_CHUNKS);
        include_summary = should_include_repository_summary(&latest_user_message.content);

        let semantic_candidates = if next_index.manifest.mode == RetrievalMode::Semantic
            && !next_index.embeddings.is_empty()
        {
            if let Some(model) = next_index.manifest.embedding_model.as_deref() {
                match embed_query(&client, model, &latest_user_message.content).await {
                    Ok(query_embedding) => Some(rank_chunks_semantic(&query_embedding, &next_index.embeddings)),
                    Err(_) => None,
                }
            } else {
                None
            }
        } else {
            None
        };

        let mode = if semantic_candidates.is_some() {
            RetrievalMode::Semantic
        } else {
            RetrievalMode::Lexical
        };

        let mut ranked = semantic_candidates
            .unwrap_or_else(|| rank_chunks_lexical(&latest_user_message.content, &next_index.chunks));
        ranked.sort_by(|left, right| right.score.total_cmp(&left.score));

        selected_indexes =
            select_context_chunk_indexes(&ranked, &next_index.chunks, requested_context, include_summary);
        citations = selected_indexes
            .iter()
            .filter_map(|index| {
                let chunk = next_index.chunks.get(*index)?;
                if chunk.path == SUMMARY_CHUNK_PATH {
                    return None;
                }
                let score = ranked
                    .iter()
                    .find(|entry| entry.index == *index)
                    .map(|entry| entry.score)
                    .unwrap_or(0.0);
                Some(AiCitation {
                    path: chunk.path.clone(),
                    start_line: chunk.start_line,
                    end_line: chunk.end_line,
                    score,
                })
            })
            .collect::<Vec<_>>();
        cached_index = Some(next_index);
        mode
    };

    let system_prompt = build_system_prompt(cached_index.is_some(), supplemental_context);
    let context_prompt = build_context_prompt(
        cached_index.as_ref(),
        &selected_indexes,
        include_summary,
        &latest_user_message.content,
        supplemental_context,
    );
    let compiled_prompt = compile_prompt_for_cli(
        &system_prompt,
        &context_prompt,
        &request.messages,
        &latest_user_message.content,
    );

    Ok(PreparedAiPrompt {
        system_prompt,
        context_prompt,
        latest_user_prompt: latest_user_message.content.clone(),
        compiled_prompt,
        citations: compact_citations(citations),
        retrieval_mode,
        repo_root: request.repo_root,
        available_embedding_model: discovery.embedding_model,
    })
}

fn compile_prompt_for_cli(
    system_prompt: &str,
    context_prompt: &str,
    messages: &[AiChatMessage],
    latest_user_prompt: &str,
) -> String {
    let mut lines = vec![
        "You are answering inside OpenBB Desktop AI Gateway.".to_string(),
        String::new(),
        "SYSTEM PROMPT:".to_string(),
        system_prompt.to_string(),
        String::new(),
        "CONTEXT:".to_string(),
        context_prompt.to_string(),
        String::new(),
        "CONVERSATION:".to_string(),
    ];

    for message in messages {
        lines.push(format!("{}: {}", message.role.to_uppercase(), message.content));
    }
    lines.push(String::new());
    lines.push("TASK:".to_string());
    lines.push(format!(
        "Respond to the latest user prompt. Keep answers concise and concrete.\nLatest user prompt: {latest_user_prompt}"
    ));
    lines.join("\n")
}

pub async fn ask_ai_question(request: AiAskRequest) -> Result<AiAskResponse, String> {
    let started_at = Instant::now();
    let client = build_http_client(90)?;
    let discovery = discover_ollama(&client).await;
    let supplemental_context = request
        .supplemental_context
        .as_deref()
        .map(str::trim)
        .filter(|value| !value.is_empty());
    let supplemental_only = request.supplemental_only.unwrap_or(false) && supplemental_context.is_some();

    if !discovery.reachable {
        return Err(format!(
            "Ollama is not reachable at {}. Start Ollama and try again.",
            current_ollama_base_url()
        ));
    }

    let chat_candidates = if discovery.chat_candidates.is_empty() {
        discovery.chat_model.iter().cloned().collect::<Vec<_>>()
    } else {
        discovery.chat_candidates.clone()
    };

    if chat_candidates.is_empty() {
        return Err(
            "No usable Ollama chat model detected. Install one with `ollama pull qwen2.5-coder:1.5b` or another chat model."
                .to_string(),
        );
    }

    let latest_user_message = request
        .messages
        .iter()
        .rev()
        .find(|message| message.role == "user")
        .or_else(|| request.messages.last())
        .ok_or_else(|| "A question is required before asking the project AI.".to_string())?;

    let mut cached_index: Option<CachedAiIndex> = None;
    let mut selected_indexes: Vec<usize> = Vec::new();
    let mut citations: Vec<AiCitation> = Vec::new();
    let mut include_summary = false;
    let retrieval_mode = if supplemental_only {
        RetrievalMode::Supplemental
    } else {
        let repo_root = ensure_repo_root(&request.repo_root)?;
        let index_context = build_index_context(&repo_root, discovery.embedding_model.as_deref())?;
        let next_index = load_cached_index(&repo_root, &index_context).or_else(|_| {
            let lexical_context = build_index_context(&repo_root, None)?;
            load_cached_index(&repo_root, &lexical_context)
        })?;

        if next_index.chunks.is_empty() {
            return Err("AI index is empty. Rebuild the index and try again.".to_string());
        }

        let requested_context = request
            .max_context_chunks
            .unwrap_or(DEFAULT_CONTEXT_CHUNKS)
            .clamp(1, MAX_CONTEXT_CHUNKS);
        include_summary = should_include_repository_summary(&latest_user_message.content);

        let semantic_candidates = if next_index.manifest.mode == RetrievalMode::Semantic
            && !next_index.embeddings.is_empty()
        {
            if let Some(model) = next_index.manifest.embedding_model.as_deref() {
                match embed_query(&client, model, &latest_user_message.content).await {
                    Ok(query_embedding) => {
                        Some(rank_chunks_semantic(&query_embedding, &next_index.embeddings))
                    }
                    Err(_) => None,
                }
            } else {
                None
            }
        } else {
            None
        };

        let mode = if semantic_candidates.is_some() {
            RetrievalMode::Semantic
        } else {
            RetrievalMode::Lexical
        };

        let mut ranked = semantic_candidates
            .unwrap_or_else(|| rank_chunks_lexical(&latest_user_message.content, &next_index.chunks));
        ranked.sort_by(|left, right| right.score.total_cmp(&left.score));

        selected_indexes =
            select_context_chunk_indexes(&ranked, &next_index.chunks, requested_context, include_summary);
        citations = selected_indexes
            .iter()
            .filter_map(|index| {
                let chunk = next_index.chunks.get(*index)?;
                if chunk.path == SUMMARY_CHUNK_PATH {
                    return None;
                }
                let score = ranked
                    .iter()
                    .find(|entry| entry.index == *index)
                    .map(|entry| entry.score)
                    .unwrap_or(0.0);
                Some(AiCitation {
                    path: chunk.path.clone(),
                    start_line: chunk.start_line,
                    end_line: chunk.end_line,
                    score,
                })
            })
            .collect::<Vec<_>>();
        cached_index = Some(next_index);
        mode
    };

    let response = chat_with_fallback(
        &client,
        &chat_candidates,
        build_chat_messages(
            cached_index.as_ref(),
            &request.messages,
            &selected_indexes,
            include_summary,
            &latest_user_message.content,
            supplemental_context,
        ),
    )
    .await?;

    Ok(AiAskResponse {
        answer: response.response.message.content.trim().to_string(),
        citations: compact_citations(citations),
        used_model: response.response.model,
        attempted_models: Some(response.attempted_models),
        model_total_ms: ollama_duration_to_ms(response.response.total_duration),
        load_ms: ollama_duration_to_ms(response.response.load_duration),
        prompt_eval_ms: ollama_duration_to_ms(response.response.prompt_eval_duration),
        eval_ms: ollama_duration_to_ms(response.response.eval_duration),
        timing_ms: started_at.elapsed().as_millis().try_into().unwrap_or(u64::MAX),
        retrieval_mode,
    })
}

fn build_http_client(timeout_secs: u64) -> Result<Client, String> {
    Client::builder()
        .timeout(Duration::from_secs(timeout_secs))
        .build()
        .map_err(|error| format!("Failed to build HTTP client: {error}"))
}

fn build_chat_messages(
    index: Option<&CachedAiIndex>,
    messages: &[AiChatMessage],
    selected_indexes: &[usize],
    include_summary: bool,
    user_query: &str,
    supplemental_context: Option<&str>,
) -> Vec<serde_json::Value> {
    let system_prompt = build_system_prompt(index.is_some(), supplemental_context);
    let context_prompt =
        build_context_prompt(index, selected_indexes, include_summary, user_query, supplemental_context);

    let mut chat_messages = vec![
        json!({
            "role": "system",
            "content": system_prompt,
        }),
        json!({
            "role": "system",
            "content": context_prompt,
        }),
    ];

    chat_messages.extend(messages.iter().map(|message| {
        json!({
            "role": message.role,
            "content": message.content,
        })
    }));
    chat_messages
}

fn build_system_prompt(has_repository_context: bool, supplemental_context: Option<&str>) -> String {
    let has_supplemental_context = supplemental_context
        .map(|value| !value.trim().is_empty())
        .unwrap_or(false);

    if has_repository_context && has_supplemental_context {
        return "You are the OpenBB repository assistant. Answer from the provided repository context first. Keep answers concise and concrete: use at most 6 bullets or 2 short paragraphs unless the user asks for more detail. Prefer file paths, route names, commands, and implementation facts from the retrieved context. When enumerating items, match the count you state to the list you provide. If the user asks about endpoints or commands, list every matching endpoint or command found in the provided context. For endpoints or commands, only quote literal path strings or command names that appear verbatim in the context. Never rename or infer new endpoint names. If the retrieved code shows a middleware or mount prefix together with nested pathname checks in the same chunk, report the public route as prefix plus nested pathname. Avoid generic software advice unless the repository context clearly supports it. If the context is insufficient, say so plainly and state what is missing. You also have supplemental OpenBB market data. Use it as the primary source for market, financial statement, and expected price-range questions. Do not claim that you cannot access market data when supplemental context is present."
            .to_string();
    }

    if has_supplemental_context {
        return "You are the OpenBB market data assistant. Answer from the provided OpenBB market data first. Keep answers concise and concrete: use at most 6 bullets or 2 short paragraphs unless the user asks for more detail. If the user asks for an expected stock-price range, anchor on analyst target low, consensus, median, and high when available and label it as a scenario range, not a guarantee. If the provided market data is insufficient for a precise range, say what is missing. Do not say that you cannot access market data when the supplemental context is present."
            .to_string();
    }

    "You are the OpenBB repository assistant. Answer from the provided repository context first. Keep answers concise and concrete: use at most 6 bullets or 2 short paragraphs unless the user asks for more detail. Prefer file paths, route names, commands, and implementation facts from the retrieved context. When enumerating items, match the count you state to the list you provide. If the user asks about endpoints or commands, list every matching endpoint or command found in the provided context. For endpoints or commands, only quote literal path strings or command names that appear verbatim in the context. Never rename or infer new endpoint names. If the retrieved code shows a middleware or mount prefix together with nested pathname checks in the same chunk, report the public route as prefix plus nested pathname. Avoid generic software advice unless the repository context clearly supports it. If the context is insufficient, say so plainly and state what is missing."
        .to_string()
}

fn compact_citations(citations: Vec<AiCitation>) -> Vec<AiCitation> {
    let mut merged: Vec<AiCitation> = Vec::new();

    for citation in citations {
        if let Some(previous) = merged.last_mut()
            && previous.path == citation.path
            && citation.start_line <= previous.end_line + 25
        {
            previous.end_line = previous.end_line.max(citation.end_line);
            previous.score = previous.score.max(citation.score);
            continue;
        }

        merged.push(citation);
    }

    merged.truncate(4);
    merged
}

fn ollama_duration_to_ms(value: Option<u64>) -> Option<u64> {
    value.map(|duration| duration / 1_000_000)
}

fn resolve_repo_context(default_dir: &str) -> Result<RepoContext, String> {
    let default_candidate = default_directory_candidate(default_dir)?;
    let stored_candidate = read_stored_working_directory(default_dir).ok().map(PathBuf::from);
    let current_dir = std::env::current_dir()
        .map_err(|error| format!("Failed to determine current directory: {error}"))?;

    let candidates = vec![
        Some(default_candidate),
        Some(current_dir),
        stored_candidate,
    ];
    let mut seen = HashSet::new();

    for candidate in candidates.iter().flatten() {
        let absolute = best_effort_absolute(candidate);
        let key = absolute.to_string_lossy().to_string();
        if !seen.insert(key) {
            continue;
        }
        if let Some(repo_root) = find_git_root(&absolute) {
            return Ok(RepoContext {
                repo_root: Some(repo_root),
                repo_ready: true,
            });
        }
    }

    let fallback = candidates
        .into_iter()
        .flatten()
        .map(|path| best_effort_absolute(&path))
        .next();

    Ok(RepoContext {
        repo_root: fallback,
        repo_ready: false,
    })
}

fn read_stored_working_directory(default_dir: &str) -> Result<String, String> {
    let settings_path = default_user_settings_path()?;
    if !settings_path.exists() {
        return Ok(default_dir.to_string());
    }
    let contents = fs::read_to_string(&settings_path)
        .map_err(|error| format!("Failed to read settings file {}: {error}", settings_path.display()))?;
    let settings: serde_json::Value =
        serde_json::from_str(&contents).map_err(|error| format!("Failed to parse settings JSON: {error}"))?;

    if let Some(path) = settings
        .get("preferences")
        .and_then(|value| value.get("working_directory"))
        .and_then(|value| value.as_str())
    {
        return Ok(path.to_string());
    }

    Ok(default_dir.to_string())
}

fn default_directory_candidate(default_dir: &str) -> Result<PathBuf, String> {
    if default_dir.trim().is_empty() || default_dir == "." {
        return std::env::current_dir()
            .map_err(|error| format!("Failed to determine current directory: {error}"));
    }
    let path = PathBuf::from(default_dir);
    Ok(if path.is_absolute() {
        path
    } else {
        std::env::current_dir()
            .map_err(|error| format!("Failed to determine current directory: {error}"))?
            .join(path)
    })
}

fn ensure_repo_root(repo_root: &str) -> Result<PathBuf, String> {
    let repo_path = best_effort_absolute(Path::new(repo_root));
    find_git_root(&repo_path).ok_or_else(|| {
        format!(
            "The selected path is not inside a Git repository: {}",
            repo_path.display()
        )
    })
}

fn find_git_root(start_path: &Path) -> Option<PathBuf> {
    let mut current = best_effort_absolute(start_path);
    loop {
        if current.join(".git").exists() {
            return Some(current);
        }
        if !current.pop() {
            return None;
        }
    }
}

fn best_effort_absolute(path: &Path) -> PathBuf {
    if let Ok(canonical) = path.canonicalize() {
        return canonical;
    }
    if path.is_absolute() {
        return path.to_path_buf();
    }
    std::env::current_dir()
        .unwrap_or_else(|_| PathBuf::from("."))
        .join(path)
}

fn build_index_context(repo_root: &Path, embedding_model: Option<&str>) -> Result<IndexContext, String> {
    let absolute_root = best_effort_absolute(repo_root);
    let repo_root_str = absolute_root.to_string_lossy().to_string();
    let repo_hash = sha1_hex(repo_root_str.as_bytes());
    let head_revision = git_head_revision(&absolute_root).unwrap_or_else(|| "nogit".to_string());
    let config_hash = sha1_hex(
        format!(
            "chunk_lines={CHUNK_LINES};chunk_overlap={CHUNK_OVERLAP};max_file_bytes={MAX_FILE_SIZE_BYTES};max_index_line_chars={MAX_INDEX_LINE_CHARS};max_index_chunk_chars={MAX_INDEX_CHUNK_CHARS};max_embed_input_chars={MAX_EMBED_INPUT_CHARS};extensions={};extra_extensions={};excluded_dirs={};extra_excluded_dirs={};noisy_path_re={};embedding_model={}",
            ALLOWED_EXTENSIONS.join(","),
            EXTRA_ALLOWED_EXTENSIONS.join(","),
            EXCLUDED_DIRS.join(","),
            EXTRA_EXCLUDED_DIRS.join(","),
            NOISY_PATH_RE.as_str(),
            embedding_model.unwrap_or("lexical")
        )
        .as_bytes(),
    );
    let revision = sha1_hex(
        format!("{repo_root_str}\n{head_revision}\n{config_hash}").as_bytes(),
    );

    Ok(IndexContext {
        repo_hash,
        head_revision,
        config_hash,
        revision,
    })
}

fn git_head_revision(repo_root: &Path) -> Option<String> {
    let output = Command::new("git")
        .arg("-C")
        .arg(repo_root)
        .arg("rev-parse")
        .arg("HEAD")
        .output()
        .ok()?;
    if !output.status.success() {
        return None;
    }
    let revision = String::from_utf8_lossy(&output.stdout).trim().to_string();
    if revision.is_empty() {
        None
    } else {
        Some(revision)
    }
}

fn sha1_hex(input: &[u8]) -> String {
    sha1(input)
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect::<Vec<_>>()
        .join("")
}

fn index_directory(index_context: &IndexContext) -> Result<PathBuf, String> {
    let home_dir = std::env::var("HOME")
        .or_else(|_| std::env::var("USERPROFILE"))
        .map_err(|error| format!("Could not determine home directory: {error}"))?;
    Ok(Path::new(&home_dir)
        .join(".openbb_platform")
        .join("ai_gateway")
        .join("index")
        .join(&index_context.repo_hash))
}

fn legacy_index_directory(index_context: &IndexContext) -> Result<PathBuf, String> {
    let home_dir = std::env::var("HOME")
        .or_else(|_| std::env::var("USERPROFILE"))
        .map_err(|error| format!("Could not determine home directory: {error}"))?;
    Ok(Path::new(&home_dir)
        .join(".openbb_platform")
        .join("ai_index")
        .join(&index_context.repo_hash))
}

fn manifest_path(index_dir: &Path) -> PathBuf {
    index_dir.join("manifest.json")
}

fn chunks_path(index_dir: &Path) -> PathBuf {
    index_dir.join("chunks.jsonl")
}

fn embeddings_path(index_dir: &Path) -> PathBuf {
    index_dir.join("embeddings.bin")
}

fn read_manifest_if_present(index_dir: &Path) -> Result<Option<AiIndexManifest>, String> {
    let path = manifest_path(index_dir);
    if !path.exists() {
        return Ok(None);
    }
    let contents = fs::read_to_string(&path)
        .map_err(|error| format!("Failed to read AI manifest {}: {error}", path.display()))?;
    serde_json::from_str::<AiIndexManifest>(&contents)
        .map(Some)
        .map_err(|error| format!("Failed to parse AI manifest {}: {error}", path.display()))
}

fn write_manifest(index_dir: &Path, manifest: &AiIndexManifest) -> Result<(), String> {
    let path = manifest_path(index_dir);
    let serialized = serde_json::to_string_pretty(manifest)
        .map_err(|error| format!("Failed to serialize AI manifest: {error}"))?;
    fs::write(&path, serialized)
        .map_err(|error| format!("Failed to write AI manifest {}: {error}", path.display()))
}

fn write_chunks(index_dir: &Path, chunks: &[IndexedChunk]) -> Result<(), String> {
    let path = chunks_path(index_dir);
    let mut file = fs::File::create(&path)
        .map_err(|error| format!("Failed to create AI chunk file {}: {error}", path.display()))?;
    for chunk in chunks {
        let serialized = serde_json::to_string(chunk)
            .map_err(|error| format!("Failed to serialize AI chunk: {error}"))?;
        file.write_all(serialized.as_bytes())
            .and_then(|_| file.write_all(b"\n"))
            .map_err(|error| format!("Failed to write AI chunk file {}: {error}", path.display()))?;
    }
    Ok(())
}

fn write_embeddings(index_dir: &Path, embeddings: &[Vec<f32>]) -> Result<(), String> {
    let path = embeddings_path(index_dir);
    let mut file = fs::File::create(&path)
        .map_err(|error| format!("Failed to create AI embeddings file {}: {error}", path.display()))?;
    for vector in embeddings {
        for value in vector {
            file.write_all(&value.to_le_bytes()).map_err(|error| {
                format!("Failed to write AI embeddings file {}: {error}", path.display())
            })?;
        }
    }
    Ok(())
}

fn load_cached_index(repo_root: &Path, index_context: &IndexContext) -> Result<CachedAiIndex, String> {
    if let Some(cached) = AI_INDEX_CACHE
        .lock()
        .unwrap()
        .get(&index_context.repo_hash)
        .cloned()
        && cached.manifest.revision == index_context.revision
    {
        return Ok(cached);
    }

    let index_dir = index_directory(index_context)?;
    if !index_dir.exists() {
        migrate_legacy_index_if_possible(index_context)?;
    }
    let manifest = read_manifest_if_present(&index_dir)?
        .ok_or_else(|| "AI index not found. Build the index before asking a question.".to_string())?;

    let chunks = read_chunks(&index_dir)?;
    let embeddings = read_embeddings(&index_dir, manifest.chunk_count, manifest.embedding_dim)?;
    let cached = CachedAiIndex {
        manifest,
        chunks,
        embeddings,
    };

    let mut store = AI_INDEX_CACHE.lock().unwrap();
    let repo_hash = sha1_hex(repo_root.to_string_lossy().as_bytes());
    store.insert(repo_hash, cached.clone());
    Ok(cached)
}

fn migrate_legacy_index_if_possible(index_context: &IndexContext) -> Result<(), String> {
    let legacy_dir = legacy_index_directory(index_context)?;
    if !legacy_dir.exists() {
        return Ok(());
    }
    let current_dir = index_directory(index_context)?;
    if current_dir.exists() {
        return Ok(());
    }
    fs::create_dir_all(&current_dir).map_err(|error| {
        format!(
            "Failed to create AI gateway index directory {}: {error}",
            current_dir.display()
        )
    })?;
    for file_name in ["manifest.json", "chunks.jsonl", "embeddings.bin"] {
        let source = legacy_dir.join(file_name);
        if source.exists() {
            let destination = current_dir.join(file_name);
            fs::copy(&source, &destination).map_err(|error| {
                format!(
                    "Failed to migrate AI index file {} -> {}: {error}",
                    source.display(),
                    destination.display()
                )
            })?;
        }
    }
    Ok(())
}

fn read_chunks(index_dir: &Path) -> Result<Vec<IndexedChunk>, String> {
    let path = chunks_path(index_dir);
    let file = fs::File::open(&path)
        .map_err(|error| format!("Failed to open AI chunk file {}: {error}", path.display()))?;
    let reader = BufReader::new(file);
    let mut chunks = Vec::new();
    for line in reader.lines() {
        let line = line.map_err(|error| {
            format!("Failed to read AI chunk line from {}: {error}", path.display())
        })?;
        if line.trim().is_empty() {
            continue;
        }
        let chunk = serde_json::from_str::<IndexedChunk>(&line).map_err(|error| {
            format!("Failed to parse AI chunk from {}: {error}", path.display())
        })?;
        chunks.push(chunk);
    }
    Ok(chunks)
}

fn read_embeddings(
    index_dir: &Path,
    chunk_count: usize,
    embedding_dim: Option<usize>,
) -> Result<Vec<Vec<f32>>, String> {
    let Some(dim) = embedding_dim else {
        return Ok(Vec::new());
    };
    if chunk_count == 0 || dim == 0 {
        return Ok(Vec::new());
    }

    let path = embeddings_path(index_dir);
    if !path.exists() {
        return Ok(Vec::new());
    }

    let mut file = fs::File::open(&path)
        .map_err(|error| format!("Failed to open AI embeddings file {}: {error}", path.display()))?;
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer)
        .map_err(|error| format!("Failed to read AI embeddings file {}: {error}", path.display()))?;

    let expected_bytes = chunk_count
        .checked_mul(dim)
        .and_then(|count| count.checked_mul(std::mem::size_of::<f32>()))
        .ok_or_else(|| "AI embeddings file size overflowed the expected layout.".to_string())?;

    if buffer.len() != expected_bytes {
        return Err(format!(
            "AI embeddings file {} has an unexpected size: expected {expected_bytes}, got {}",
            path.display(),
            buffer.len()
        ));
    }

    let mut embeddings = Vec::with_capacity(chunk_count);
    for chunk_index in 0..chunk_count {
        let mut vector = Vec::with_capacity(dim);
        for dim_index in 0..dim {
            let offset = (chunk_index * dim + dim_index) * 4;
            let bytes = [
                buffer[offset],
                buffer[offset + 1],
                buffer[offset + 2],
                buffer[offset + 3],
            ];
            vector.push(f32::from_le_bytes(bytes));
        }
        embeddings.push(vector);
    }
    Ok(embeddings)
}

fn collect_repo_files(repo_root: &Path) -> Result<Vec<PathBuf>, String> {
    if let Some(git_files) = collect_repo_files_from_git(repo_root) {
        return Ok(git_files);
    }
    collect_repo_files_from_walk(repo_root)
}

fn collect_repo_files_from_git(repo_root: &Path) -> Option<Vec<PathBuf>> {
    let output = Command::new("git")
        .arg("-C")
        .arg(repo_root)
        .arg("ls-files")
        .output()
        .ok()?;
    if !output.status.success() {
        return None;
    }

    let files = String::from_utf8_lossy(&output.stdout)
        .lines()
        .filter_map(|line| {
            let trimmed = line.trim();
            if trimmed.is_empty() || should_skip_relative_path(trimmed) {
                return None;
            }
            let full_path = repo_root.join(trimmed);
            let metadata = fs::metadata(&full_path).ok()?;
            if metadata.len() > MAX_FILE_SIZE_BYTES || !metadata.is_file() {
                return None;
            }
            Some(full_path)
        })
        .collect::<Vec<_>>();

    Some(files)
}

fn collect_repo_files_from_walk(repo_root: &Path) -> Result<Vec<PathBuf>, String> {
    let mut files = Vec::new();
    walk_repo(repo_root, repo_root, &mut files)?;
    Ok(files)
}

fn walk_repo(current_dir: &Path, repo_root: &Path, files: &mut Vec<PathBuf>) -> Result<(), String> {
    let entries = fs::read_dir(current_dir)
        .map_err(|error| format!("Failed to read repository directory {}: {error}", current_dir.display()))?;

    for entry in entries {
        let entry = entry.map_err(|error| {
            format!(
                "Failed to inspect repository entry in {}: {error}",
                current_dir.display()
            )
        })?;
        let path = entry.path();
        let relative = normalize_relative_path(repo_root, &path).unwrap_or_default();
        if path.is_dir() {
            let dir_name = path.file_name().and_then(|name| name.to_str()).unwrap_or_default();
            if EXCLUDED_DIRS.contains(&dir_name) || EXTRA_EXCLUDED_DIRS.contains(&dir_name) {
                continue;
            }
            walk_repo(&path, repo_root, files)?;
            continue;
        }

        if relative.is_empty() || should_skip_relative_path(&relative) {
            continue;
        }
        let metadata = entry.metadata().map_err(|error| {
            format!("Failed to read metadata for {}: {error}", path.display())
        })?;
        if metadata.len() > MAX_FILE_SIZE_BYTES || !metadata.is_file() {
            continue;
        }
        files.push(path);
    }
    Ok(())
}

fn should_skip_relative_path(relative_path: &str) -> bool {
    let normalized = relative_path.replace('\\', "/");
    let segments = normalized.split('/').collect::<Vec<_>>();

    if segments
        .iter()
        .any(|segment| EXCLUDED_DIRS.contains(segment) || EXTRA_EXCLUDED_DIRS.contains(segment))
    {
        return true;
    }

    let file_name = segments.last().copied().unwrap_or_default();
    if file_name.is_empty() {
        return true;
    }
    if LOCKFILES.contains(&file_name) {
        return true;
    }
    if file_name.ends_with(".min.js")
        || file_name.ends_with(".min.jsx")
        || file_name.ends_with(".min.ts")
        || file_name.ends_with(".min.tsx")
    {
        return true;
    }
    if file_name.contains(".generated.") || file_name.contains(".gen.") {
        return true;
    }
    if NOISY_PATH_RE.is_match(&normalized) {
        return true;
    }

    let extension = Path::new(file_name)
        .extension()
        .and_then(|ext| ext.to_str())
        .unwrap_or_default()
        .to_ascii_lowercase();

    if extension.is_empty() {
        return true;
    }

    !(ALLOWED_EXTENSIONS.contains(&extension.as_str())
        || EXTRA_ALLOWED_EXTENSIONS.contains(&extension.as_str()))
}

fn normalize_relative_path(repo_root: &Path, path: &Path) -> Option<String> {
    path.strip_prefix(repo_root)
        .ok()
        .map(|relative| relative.to_string_lossy().replace('\\', "/"))
}

fn read_text_file(path: &Path) -> Result<Option<String>, String> {
    let bytes = fs::read(path)
        .map_err(|error| format!("Failed to read file {}: {error}", path.display()))?;
    if bytes.len() as u64 > MAX_FILE_SIZE_BYTES {
        return Ok(None);
    }
    if bytes.iter().take(1024).any(|byte| *byte == 0) {
        return Ok(None);
    }
    match String::from_utf8(bytes) {
        Ok(contents) => Ok(Some(contents)),
        Err(_) => Ok(None),
    }
}

fn detect_language(path: &str) -> String {
    Path::new(path)
        .extension()
        .and_then(|ext| ext.to_str())
        .unwrap_or("txt")
        .to_ascii_lowercase()
}

fn truncate_indexed_line(line: &str) -> String {
    let count = line.chars().count();
    if count <= MAX_INDEX_LINE_CHARS {
        return line.to_string();
    }

    line.chars().take(MAX_INDEX_LINE_CHARS).collect::<String>() + " …[line truncated for AI index]"
}

fn truncate_chunk_body(input: String) -> String {
    if input.chars().count() <= MAX_INDEX_CHUNK_CHARS {
        return input;
    }

    input.chars().take(MAX_INDEX_CHUNK_CHARS).collect::<String>() + "\n...[chunk truncated for AI index]"
}

fn build_embedding_input(chunk: &IndexedChunk) -> String {
    let prefix = format!("{}:{}-{}\n", chunk.path, chunk.start_line, chunk.end_line);
    let remaining = MAX_EMBED_INPUT_CHARS.saturating_sub(prefix.chars().count()).max(256);
    let body = if chunk.text.chars().count() > remaining {
        chunk.text.chars().take(remaining).collect::<String>() + "\n...[embedding input truncated]"
    } else {
        chunk.text.clone()
    };

    format!("{prefix}{body}")
}

fn chunk_file_contents(path: &str, language: &str, contents: &str) -> Vec<IndexedChunk> {
    let lines = contents.lines().collect::<Vec<_>>();
    if lines.is_empty() {
        return Vec::new();
    }

    let mut chunks = Vec::new();
    let step = CHUNK_LINES.saturating_sub(CHUNK_OVERLAP).max(1);
    let mut start_index = 0usize;

    while start_index < lines.len() {
        let end_index = min(start_index + CHUNK_LINES, lines.len());
        let chunk_text = truncate_chunk_body(
            lines[start_index..end_index]
                .iter()
                .map(|line| truncate_indexed_line(line))
                .collect::<Vec<_>>()
                .join("\n"),
        );
        chunks.push(IndexedChunk {
            path: path.to_string(),
            start_line: start_index + 1,
            end_line: end_index,
            sha1: sha1_hex(chunk_text.as_bytes()),
            language: language.to_string(),
            text: chunk_text,
        });

        if end_index == lines.len() {
            break;
        }
        start_index += step;
    }

    chunks
}

fn build_project_summary(repo_root: &Path, repo_files: &[PathBuf]) -> String {
    let top_level_dirs = fs::read_dir(repo_root)
        .ok()
        .into_iter()
        .flatten()
        .filter_map(|entry| entry.ok())
        .map(|entry| entry.path())
        .filter(|path| path.is_dir())
        .filter_map(|path| {
            path.file_name()
                .and_then(|name| name.to_str())
                .map(|name| name.to_string())
        })
        .filter(|name| !EXCLUDED_DIRS.contains(&name.as_str()) && !EXTRA_EXCLUDED_DIRS.contains(&name.as_str()))
        .collect::<Vec<_>>();

    let route_files = repo_files
        .iter()
        .filter_map(|path| normalize_relative_path(repo_root, path))
        .filter(|path| path.starts_with("desktop/src/routes/"))
        .collect::<Vec<_>>();

    let tauri_commands = discover_tauri_commands(repo_root);
    let readme_summary = summarize_readme(repo_root);
    let backend_resolution_summary = describe_backend_resolution(repo_root);

    format!(
        "# Project Summary\n\n## Top-Level Directories\n{}\n\n## Desktop Routes\n{}\n\n## Tauri Commands\n{}\n\n## Backend Resolution Flow\n{}\n\n## README Highlights\n{}\n",
        if top_level_dirs.is_empty() {
            "- None detected".to_string()
        } else {
            top_level_dirs
                .iter()
                .map(|dir| format!("- {dir}"))
                .collect::<Vec<_>>()
                .join("\n")
        },
        if route_files.is_empty() {
            "- None detected".to_string()
        } else {
            route_files
                .iter()
                .map(|route| format!("- {route}"))
                .collect::<Vec<_>>()
                .join("\n")
        },
        if tauri_commands.is_empty() {
            "- None detected".to_string()
        } else {
            tauri_commands
                .iter()
                .map(|command| format!("- {command}"))
                .collect::<Vec<_>>()
                .join("\n")
        },
        backend_resolution_summary,
        readme_summary
    )
}

fn discover_tauri_commands(repo_root: &Path) -> Vec<String> {
    let command_regex = Regex::new(r"#\s*\[tauri::command\]\s*pub\s+(?:async\s+)?fn\s+([a-zA-Z0-9_]+)")
        .expect("tauri command regex should compile");
    let handlers_dir = repo_root.join("desktop/src-tauri/src/tauri_handlers");
    let Ok(entries) = fs::read_dir(handlers_dir) else {
        return Vec::new();
    };

    let mut commands = Vec::new();
    for entry in entries.flatten() {
        let path = entry.path();
        if path.extension().and_then(|ext| ext.to_str()) != Some("rs") {
            continue;
        }
        if let Ok(contents) = fs::read_to_string(&path) {
            for captures in command_regex.captures_iter(&contents) {
                if let Some(command) = captures.get(1) {
                    commands.push(command.as_str().to_string());
                }
            }
        }
    }
    commands.sort();
    commands.dedup();
    commands
}

fn summarize_readme(repo_root: &Path) -> String {
    let readme_path = repo_root.join("README.md");
    let Ok(contents) = fs::read_to_string(readme_path) else {
        return "- README.md not found".to_string();
    };

    let lines = contents
        .lines()
        .map(str::trim)
        .filter(|line| !line.is_empty())
        .filter(|line| !line.starts_with("!["))
        .take(12)
        .map(|line| format!("- {line}"))
        .collect::<Vec<_>>();

    if lines.is_empty() {
        "- README.md was empty".to_string()
    } else {
        lines.join("\n")
    }
}

fn describe_backend_resolution(repo_root: &Path) -> String {
    let backend_path = repo_root.join("desktop/src/lib/openbbBackend.ts");
    if !backend_path.exists() {
        return "- openbbBackend.ts not found".to_string();
    }

    [
        "- resolveOpenBBBackend prefers a stored backend URL when it still passes health checks.",
        "- If Tauri backend service introspection is available, it tries the running OpenBB API service URL first.",
        "- If there is no running service URL, it parses the configured backend command for host and port flags.",
        "- If service discovery fails, it falls back to local defaults and retries loopback health endpoints before returning a disconnected state.",
    ]
    .join("\n")
}

async fn discover_ollama(client: &Client) -> OllamaDiscovery {
    if let Some((cached_at, cached)) = OLLAMA_DISCOVERY_CACHE.lock().unwrap().as_ref()
        && cached_at.elapsed() < OLLAMA_DISCOVERY_CACHE_TTL
    {
        return cached.clone();
    }

    let tags_response = client
        .get(format!("{}/tags", current_ollama_base_url()))
        .send()
        .await;
    let Ok(response) = tags_response else {
        let discovery = OllamaDiscovery {
            reachable: false,
            available_models: Vec::new(),
            chat_model: None,
            chat_candidates: Vec::new(),
            embedding_model: None,
        };
        *OLLAMA_DISCOVERY_CACHE.lock().unwrap() = Some((Instant::now(), discovery.clone()));
        return discovery;
    };

    if !response.status().is_success() {
        let discovery = OllamaDiscovery {
            reachable: false,
            available_models: Vec::new(),
            chat_model: None,
            chat_candidates: Vec::new(),
            embedding_model: None,
        };
        *OLLAMA_DISCOVERY_CACHE.lock().unwrap() = Some((Instant::now(), discovery.clone()));
        return discovery;
    }

    let models = response
        .json::<OllamaTagsResponse>()
        .await
        .map(|payload| payload.models)
        .unwrap_or_default();
    let available_models = models.iter().map(|model| model.name.clone()).collect::<Vec<_>>();
    let chat_candidates = build_chat_candidates(&models);
    let chat_model = chat_candidates.first().cloned();
    let embedding_model = pick_embedding_model(client, &available_models).await;
    let discovery = OllamaDiscovery {
        reachable: true,
        available_models,
        chat_model,
        chat_candidates,
        embedding_model,
    };
    *OLLAMA_DISCOVERY_CACHE.lock().unwrap() = Some((Instant::now(), discovery.clone()));
    discovery
}

fn build_chat_candidates(models: &[OllamaModel]) -> Vec<String> {
    let mut candidates = models.to_vec();
    candidates.sort_by(compare_chat_models);
    candidates
        .into_iter()
        .filter(|model| !is_embedding_only_model_name(&model.name))
        .take(MAX_CHAT_CANDIDATES)
        .map(|model| model.name)
        .collect()
}

fn compare_chat_models(left: &OllamaModel, right: &OllamaModel) -> Ordering {
    chat_model_priority(left)
        .cmp(&chat_model_priority(right))
        .then_with(|| compare_optional_f32(model_parameter_size(left), model_parameter_size(right)))
        .then_with(|| left.size.cmp(&right.size))
        .then_with(|| left.name.cmp(&right.name))
}

fn chat_model_priority(model: &OllamaModel) -> u8 {
    let normalized = model.name.to_ascii_lowercase();
    if is_embedding_only_model_name(&normalized) {
        99
    } else if normalized.contains("coder") {
        0
    } else if normalized.contains("instruct") || normalized.contains("chat") {
        1
    } else if normalized.contains("qwen")
        || normalized.contains("llama")
        || normalized.contains("mistral")
        || normalized.contains("gemma")
        || normalized.contains("phi")
    {
        2
    } else {
        3
    }
}

fn is_embedding_only_model_name(model_name: &str) -> bool {
    let normalized = model_name.to_ascii_lowercase();
    normalized.contains("embed")
        || normalized.contains("embedding")
        || normalized.contains("minilm")
        || normalized.contains("nomic")
        || normalized.contains("bge")
        || normalized.contains("e5")
}

fn compare_optional_f32(left: Option<f32>, right: Option<f32>) -> Ordering {
    match (left, right) {
        (Some(left), Some(right)) => left.partial_cmp(&right).unwrap_or(Ordering::Equal),
        (Some(_), None) => Ordering::Less,
        (None, Some(_)) => Ordering::Greater,
        (None, None) => Ordering::Equal,
    }
}

fn model_parameter_size(model: &OllamaModel) -> Option<f32> {
    parse_parameter_size(&model.details.parameter_size)
}

fn parse_parameter_size(input: &str) -> Option<f32> {
    if input.trim().is_empty() {
        return None;
    }

    let upper = input.trim().to_ascii_uppercase();
    let (number, scale) = if let Some(value) = upper.strip_suffix('B') {
        (value, 1.0)
    } else if let Some(value) = upper.strip_suffix('M') {
        (value, 0.001)
    } else if let Some(value) = upper.strip_suffix('K') {
        (value, 0.000_001)
    } else {
        (upper.as_str(), 1.0)
    };

    number.trim().parse::<f32>().ok().map(|value| value * scale)
}

fn model_base_name(model: &str) -> &str {
    model.split(':').next().unwrap_or(model)
}

async fn pick_embedding_model(client: &Client, available_models: &[String]) -> Option<String> {
    let exact_preferences = ["qwen3-embedding", "embeddinggemma", "all-minilm"];
    let mut candidates = Vec::new();

    for preferred in exact_preferences {
        if let Some(model) = available_models
            .iter()
            .find(|model| model_base_name(model).eq_ignore_ascii_case(preferred))
        {
            candidates.push(model.clone());
        }
    }

    for model in available_models {
        let normalized = model.to_ascii_lowercase();
        if normalized.contains("embed")
            || normalized.contains("embedding")
            || normalized.contains("minilm")
            || normalized.contains("nomic")
        {
            candidates.push(model.clone());
        }
    }

    for model in available_models.iter().take(3) {
        candidates.push(model.clone());
    }

    let mut seen = HashSet::new();
    for candidate in candidates {
        if !seen.insert(candidate.clone()) {
            continue;
        }
        if probe_embedding_model(client, &candidate).await {
            return Some(candidate);
        }
    }

    None
}

async fn probe_embedding_model(client: &Client, model: &str) -> bool {
    post_json::<OllamaEmbedResponse>(
        client,
        &format!("{}/embed", current_ollama_base_url()),
        json!({
            "model": model,
            "input": "ping",
            "truncate": true,
        }),
    )
    .await
    .map(|response| !response.embeddings.is_empty() && !response.embeddings[0].is_empty())
    .unwrap_or(false)
}

async fn embed_chunks(
    client: &Client,
    model: &str,
    chunks: &[IndexedChunk],
) -> Result<Vec<Vec<f32>>, String> {
    let mut embeddings = Vec::new();
    let embedding_dim = probe_embedding_dimension(client, model).await.ok().flatten();
    for batch in chunks.chunks(EMBED_BATCH_SIZE) {
        let inputs = batch.iter().map(build_embedding_input).collect::<Vec<_>>();
        let batch_embeddings = embed_input_batch(client, model, inputs).await?;

        if batch_embeddings.len() != batch.len() {
            if let Some(dim) = embedding_dim {
                let mut padded = batch_embeddings;
                while padded.len() < batch.len() {
                    padded.push(vec![0.0; dim]);
                }
                embeddings.extend(padded);
                continue;
            }
            return Err(format!(
                "Ollama returned {} embeddings for a batch of {} chunks.",
                batch_embeddings.len(),
                batch.len()
            ));
        }
        embeddings.extend(batch_embeddings);
    }
    Ok(embeddings)
}

async fn probe_embedding_dimension(client: &Client, model: &str) -> Result<Option<usize>, String> {
    let response = post_json::<OllamaEmbedResponse>(
        client,
        &format!("{}/embed", current_ollama_base_url()),
        json!({
            "model": model,
            "input": "ping",
            "truncate": true,
            "keep_alive": "5m",
        }),
    )
    .await?;

    Ok(response
        .embeddings
        .into_iter()
        .next()
        .map(|vector| vector.len())
        .filter(|dim| *dim > 0))
}

async fn embed_query(client: &Client, model: &str, input: &str) -> Result<Vec<f32>, String> {
    let response = post_json::<OllamaEmbedResponse>(
        client,
        &format!("{}/embed", current_ollama_base_url()),
        json!({
            "model": model,
            "input": input,
            "truncate": true,
            "keep_alive": "5m",
        }),
    )
    .await?;

    response
        .embeddings
        .into_iter()
        .next()
        .ok_or_else(|| "Ollama did not return a query embedding.".to_string())
}

async fn post_json<T>(client: &Client, url: &str, payload: serde_json::Value) -> Result<T, String>
where
    T: for<'de> Deserialize<'de>,
{
    let response = client
        .post(url)
        .json(&payload)
        .send()
        .await
        .map_err(|error| format!("Failed to contact Ollama at {url}: {error}"))?;

    if !response.status().is_success() {
        let status = response.status();
        let body = response.text().await.unwrap_or_default();
        return Err(format!("Ollama request to {url} failed with status {status}: {body}"));
    }

    response
        .json::<T>()
        .await
        .map_err(|error| format!("Failed to parse Ollama response from {url}: {error}"))
}

async fn embed_input_batch(
    client: &Client,
    model: &str,
    inputs: Vec<String>,
) -> Result<Vec<Vec<f32>>, String> {
    let mut pending = VecDeque::from([inputs]);
    let mut embeddings = Vec::new();

    while let Some(batch) = pending.pop_front() {
        let batch_len = batch.len();
        let batch_for_split = batch.clone();
        let response = post_json::<OllamaEmbedResponse>(
            client,
            &format!("{}/embed", current_ollama_base_url()),
            json!({
                "model": model,
                "input": batch,
                "truncate": true,
                "keep_alive": "5m",
            }),
        )
        .await;

        match response {
            Ok(response) if response.embeddings.len() == batch_len => {
                embeddings.extend(response.embeddings);
            }
            Ok(_) if batch_len > 1 => {
                let (left, right) = split_string_batch(&batch_for_split);
                pending.push_front(right);
                pending.push_front(left);
            }
            Ok(response) => {
                return Err(format!(
                    "Ollama returned {} embeddings for a batch of {} chunks.",
                    response.embeddings.len(),
                    batch_len
                ));
            }
            Err(_) if batch_len > 1 => {
                let (left, right) = split_string_batch(&batch_for_split);
                pending.push_front(right);
                pending.push_front(left);
            }
            Err(error) => {
                if let Some(dim) = probe_embedding_dimension(client, model).await.ok().flatten() {
                    embeddings.push(vec![0.0; dim]);
                } else {
                    return Err(error);
                }
            }
        }
    }

    Ok(embeddings)
}

fn split_string_batch(batch: &[String]) -> (Vec<String>, Vec<String>) {
    let midpoint = (batch.len() / 2).max(1);
    (batch[..midpoint].to_vec(), batch[midpoint..].to_vec())
}

struct ChatAttemptResult {
    response: OllamaChatResponse,
    attempted_models: Vec<String>,
}

async fn chat_with_fallback(
    client: &Client,
    candidate_models: &[String],
    messages: Vec<serde_json::Value>,
) -> Result<ChatAttemptResult, String> {
    let mut last_error = None;
    let mut attempted_models = Vec::new();

    for model in candidate_models {
        attempted_models.push(model.clone());
        match post_json::<OllamaChatResponse>(
            client,
            &format!("{}/chat", current_ollama_base_url()),
            json!({
                "model": model,
                "stream": false,
                "keep_alive": CHAT_KEEP_ALIVE,
                "messages": messages.clone(),
            }),
        )
        .await
        {
            Ok(response) => {
                return Ok(ChatAttemptResult {
                    response,
                    attempted_models,
                })
            }
            Err(error) => last_error = Some(format!("{model}: {error}")),
        }
    }

    Err(last_error.unwrap_or_else(|| "No Ollama chat model could answer the request.".to_string()))
}

fn rank_chunks_semantic(query_embedding: &[f32], embeddings: &[Vec<f32>]) -> Vec<RankedChunk> {
    embeddings
        .iter()
        .enumerate()
        .map(|(index, embedding)| RankedChunk {
            index,
            score: cosine_similarity(query_embedding, embedding),
        })
        .collect()
}

fn cosine_similarity(left: &[f32], right: &[f32]) -> f32 {
    if left.is_empty() || right.is_empty() || left.len() != right.len() {
        return 0.0;
    }
    let mut dot_product = 0.0f32;
    let mut left_norm = 0.0f32;
    let mut right_norm = 0.0f32;

    for (left_value, right_value) in left.iter().zip(right.iter()) {
        dot_product += left_value * right_value;
        left_norm += left_value * left_value;
        right_norm += right_value * right_value;
    }

    if left_norm == 0.0 || right_norm == 0.0 {
        return 0.0;
    }

    dot_product / (left_norm.sqrt() * right_norm.sqrt())
}

fn rank_chunks_lexical(query: &str, chunks: &[IndexedChunk]) -> Vec<RankedChunk> {
    let query_tokens = tokenize_query(query);
    chunks
        .iter()
        .enumerate()
        .map(|(index, chunk)| RankedChunk {
            index,
            score: lexical_score(query, &query_tokens, chunk),
        })
        .collect()
}

fn tokenize(input: &str) -> Vec<String> {
    let mut tokens = Vec::new();
    let mut current = String::new();
    let characters = input.chars().collect::<Vec<_>>();

    for (index, character) in characters.iter().enumerate() {
        let previous = index.checked_sub(1).and_then(|value| characters.get(value));
        let next = characters.get(index + 1);

        if !character.is_alphanumeric() && *character != '_' {
            if !current.is_empty() {
                tokens.push(current.to_ascii_lowercase());
                current.clear();
            }
            continue;
        }

        let should_split = character.is_uppercase()
            && !current.is_empty()
            && previous.is_some_and(|value| {
                value.is_lowercase()
                    || value.is_ascii_digit()
                    || (value.is_uppercase() && next.is_some_and(|next_value| next_value.is_lowercase()))
            });

        if should_split {
            tokens.push(current.to_ascii_lowercase());
            current.clear();
        }

        current.push(*character);
    }

    if !current.is_empty() {
        tokens.push(current.to_ascii_lowercase());
    }

    tokens
}

fn tokenize_query(input: &str) -> Vec<String> {
    let filtered = tokenize(input)
        .into_iter()
        .filter(|token| !is_query_stopword(token))
        .collect::<Vec<_>>();

    if filtered.is_empty() {
        tokenize(input)
    } else {
        filtered
    }
}

fn is_query_stopword(token: &str) -> bool {
    matches!(
        token,
        "a"
            | "an"
            | "and"
            | "codebase"
            | "describe"
            | "does"
            | "explain"
            | "for"
            | "how"
            | "in"
            | "is"
            | "me"
            | "project"
            | "repository"
            | "tell"
            | "the"
            | "this"
            | "to"
            | "what"
    )
}

fn has_endpoint_intent(query: &str, query_tokens: &[String]) -> bool {
    ENDPOINT_QUERY_RE.is_match(query)
        || query_tokens
            .iter()
            .any(|token| token.contains('/') || token.contains("__"))
}

fn count_substring_occurrences(haystack: &str, needle: &str) -> usize {
    if needle.is_empty() {
        return 0;
    }

    let mut count = 0;
    let mut offset = 0;
    while let Some(next) = haystack[offset..].find(needle) {
        count += 1;
        offset += next + needle.len();
    }

    count
}

fn lexical_score(query: &str, query_tokens: &[String], chunk: &IndexedChunk) -> f32 {
    if query_tokens.is_empty() {
        return 0.0;
    }

    let query_lower = query.to_ascii_lowercase();
    let haystack = format!("{} {}", chunk.path, chunk.text);
    let haystack_lower = haystack.to_ascii_lowercase();
    let chunk_tokens = tokenize(&haystack).into_iter().collect::<HashSet<_>>();
    let path_tokens = tokenize(&chunk.path).into_iter().collect::<HashSet<_>>();
    let overlap = query_tokens
        .iter()
        .filter(|token| chunk_tokens.contains(token.as_str()))
        .count();
    let path_bonus = query_tokens
        .iter()
        .filter(|token| path_tokens.contains(token.as_str()))
        .count() as f32
        * 0.35;
    let substring_bonus = query_tokens
        .iter()
        .filter(|token| haystack_lower.contains(token.as_str()))
        .count() as f32
        * 0.05;
    let mut score = overlap as f32 / query_tokens.len() as f32 + path_bonus + substring_bonus;

    if has_endpoint_intent(query, query_tokens) {
        let route_marker_score = ENDPOINT_ROUTE_MARKERS
            .iter()
            .map(|(marker, weight)| count_substring_occurrences(&haystack_lower, marker).min(2) as f32 * weight)
            .sum::<f32>();
        let literal_route_count = ROUTE_LITERAL_RE.find_iter(chunk.text.as_str()).count().min(8) as f32;
        let literal_query_hits = query_tokens
            .iter()
            .filter(|token| {
                (token.contains('/') || token.contains("__") || token.contains('.'))
                    && haystack_lower.contains(token.as_str())
            })
            .count() as f32;
        let chunk_path_lower = chunk.path.to_ascii_lowercase();
        let strong_path_match = query_tokens
            .iter()
            .filter(|token| chunk_path_lower.contains(token.as_str()))
            .count() as f32;

        score += route_marker_score;
        score += literal_route_count * 3.5;
        score += literal_query_hits * 10.0;

        if route_marker_score > 0.0 && strong_path_match >= 2.0 {
            score += 18.0 + strong_path_match * 3.0;
        }
        if query_lower.contains("browser")
            && query_lower.contains("fallback")
            && chunk_path_lower
                .replace(|character: char| !character.is_ascii_alphanumeric(), "")
                .contains("aibrowserfallback")
        {
            score += 18.0;
        }
        if query_lower.contains("tauri")
            && (chunk_path_lower.ends_with("main.rs")
                || chunk_path_lower.contains("/tauri_handlers/ai.rs"))
        {
            score += 12.0;
        }
        if chunk_path_lower.ends_with(".md") {
            score -= 10.0;
        }
    }

    score
}

fn select_context_chunk_indexes(
    ranked: &[RankedChunk],
    chunks: &[IndexedChunk],
    max_chunks: usize,
    include_summary: bool,
) -> Vec<usize> {
    let mut selected = Vec::new();
    let mut seen = HashSet::new();

    for ranked_chunk in ranked.iter().take(max_chunks) {
        if seen.insert(ranked_chunk.index) {
            selected.push(ranked_chunk.index);
        }
    }

    for pinned_path in PINNED_PATHS {
        if let Some(index) = chunks.iter().position(|chunk| chunk.path == pinned_path)
            && seen.insert(index)
        {
            selected.push(index);
        }
    }

    if include_summary
        && let Some(index) = chunks.iter().position(|chunk| chunk.path == SUMMARY_CHUNK_PATH)
        && seen.insert(index)
    {
        selected.push(index);
    }

    selected
}

fn should_include_repository_summary(query: &str) -> bool {
    !has_endpoint_intent(query, &tokenize_query(query))
        && !Regex::new(r"(?i)(function|class|file|filepath|\.tsx|\.ts|\.rs|main\.rs|aibrowserfallback)")
            .unwrap()
            .is_match(query)
}

fn build_context_prompt(
    index: Option<&CachedAiIndex>,
    selected_indexes: &[usize],
    include_summary: bool,
    user_query: &str,
    supplemental_context: Option<&str>,
) -> String {
    let mut sections = Vec::new();
    if let Some(supplemental) = supplemental_context
        .map(str::trim)
        .filter(|value| !value.is_empty())
    {
        sections.push(format!("OpenBB supplemental market data:\n{}", supplemental));
    }

    let Some(index) = index else {
        return sections.join("\n\n");
    };

    if has_endpoint_intent(user_query, &tokenize_query(user_query)) {
        sections.push(
            "Task hint: this is an endpoint or command lookup. Use only literal route strings or command names from the retrieved code chunks.".to_string(),
        );
    }
    sections.push(format!(
        "Repository root: {}\nIndexed at: {}\nRetrieval mode: {:?}",
        index.manifest.repo_root, index.manifest.last_indexed_at, index.manifest.mode
    ));
    if include_summary {
        sections.push(format!("Project summary:\n{}", index.manifest.summary_prompt));
    }

    for index_value in selected_indexes {
        if let Some(chunk) = index.chunks.get(*index_value) {
            sections.push(format!(
                "Context chunk: {}:{}-{}\n```{}\n{}\n```",
                chunk.path,
                chunk.start_line,
                chunk.end_line,
                chunk.language,
                truncate_for_prompt(&chunk.text, 4_500)
            ));
        }
    }

    sections.join("\n\n")
}

fn truncate_for_prompt(input: &str, max_chars: usize) -> String {
    if input.chars().count() <= max_chars {
        return input.to_string();
    }
    input.chars().take(max_chars).collect::<String>() + "\n...[truncated]"
}

#[cfg(test)]
mod tests {
    use super::*;

    fn temp_path(name: &str) -> PathBuf {
        let unique = format!(
            "{}-{}",
            name,
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        );
        std::env::temp_dir().join(unique)
    }

    #[test]
    fn should_skip_known_generated_and_binary_like_paths() {
        assert!(should_skip_relative_path("node_modules/react/index.js"));
        assert!(should_skip_relative_path("desktop/dist/app.js"));
        assert!(should_skip_relative_path("desktop/src/routeTree.gen.ts"));
        assert!(should_skip_relative_path("package-lock.json"));
        assert!(should_skip_relative_path("desktop/src/vendor/chart.min.js"));
        assert!(should_skip_relative_path(
            "openbb_platform/providers/fred/tests/record/http/test_fred_fetchers/example.yaml"
        ));
        assert!(!should_skip_relative_path("desktop/src/routes/ai.tsx"));
        assert!(!should_skip_relative_path("README.md"));
        assert!(!should_skip_relative_path("scripts/setup.ps1"));
    }

    #[test]
    fn chunking_respects_overlap_and_line_ranges() {
        let content = (1..=250)
            .map(|line| format!("line-{line}"))
            .collect::<Vec<_>>()
            .join("\n");
        let chunks = chunk_file_contents("desktop/src/routes/ai.tsx", "tsx", &content);

        assert_eq!(chunks.len(), 3);
        assert_eq!(chunks[0].start_line, 1);
        assert_eq!(chunks[0].end_line, 120);
        assert_eq!(chunks[1].start_line, 101);
        assert_eq!(chunks[1].end_line, 220);
        assert_eq!(chunks[2].start_line, 201);
        assert_eq!(chunks[2].end_line, 250);
    }

    #[test]
    fn chunking_truncates_oversized_lines_and_chunks() {
        let giant_line = "x".repeat(20_000);
        let content = format!("{giant_line}\n{giant_line}");
        let chunks = chunk_file_contents("desktop/src/components/GamestonkIcon.tsx", "tsx", &content);

        assert_eq!(chunks.len(), 1);
        assert!(chunks[0].text.contains("truncated for AI index"));
        assert!(chunks[0].text.chars().count() <= MAX_INDEX_CHUNK_CHARS + 64);
    }

    #[test]
    fn cosine_similarity_prefers_closer_vectors() {
        let query = vec![1.0, 0.0, 0.0];
        let embeddings = vec![vec![0.95, 0.01, 0.0], vec![0.0, 1.0, 0.0], vec![0.5, 0.5, 0.0]];
        let mut ranked = rank_chunks_semantic(&query, &embeddings);
        ranked.sort_by(|left, right| right.score.total_cmp(&left.score));

        assert_eq!(ranked[0].index, 0);
        assert_eq!(ranked[1].index, 2);
        assert_eq!(ranked[2].index, 1);
    }

    #[test]
    fn lexical_ranking_prefers_overlap_and_path_match() {
        let chunks = vec![
            IndexedChunk {
                path: "README.md".to_string(),
                start_line: 1,
                end_line: 10,
                sha1: "a".to_string(),
                language: "md".to_string(),
                text: "OpenBB desktop AI route guide".to_string(),
            },
            IndexedChunk {
                path: "desktop/src/routes/ai.tsx".to_string(),
                start_line: 1,
                end_line: 10,
                sha1: "b".to_string(),
                language: "tsx".to_string(),
                text: "createFileRoute('/ai') gateway provider status route".to_string(),
            },
        ];

        let mut ranked = rank_chunks_lexical("AI route guide", &chunks);
        ranked.sort_by(|left, right| right.score.total_cmp(&left.score));
        assert_eq!(ranked[0].index, 1);
    }

    #[test]
    fn lexical_ranking_prefers_openbb_backend_resolution_file() {
        let chunks = vec![
            IndexedChunk {
                path: "desktop/src/tests/routes/backends.test.tsx".to_string(),
                start_line: 1,
                end_line: 10,
                sha1: "a".to_string(),
                language: "tsx".to_string(),
                text: "backend route tests".to_string(),
            },
            IndexedChunk {
                path: "desktop/src/lib/openbbBackend.ts".to_string(),
                start_line: 1,
                end_line: 20,
                sha1: "b".to_string(),
                language: "ts".to_string(),
                text: "export async function resolveOpenBBBackend() { return null; }".to_string(),
            },
        ];

        let mut ranked = rank_chunks_lexical("How does this project resolve the OpenBB backend?", &chunks);
        ranked.sort_by(|left, right| right.score.total_cmp(&left.score));
        assert_eq!(ranked[0].index, 1);
    }

    #[test]
    fn endpoint_queries_prefer_route_definition_chunks() {
        let chunks = vec![
            IndexedChunk {
                path: "desktop/dev/aiBrowserFallback.ts".to_string(),
                start_line: 100,
                end_line: 140,
                sha1: "a".to_string(),
                language: "ts".to_string(),
                text: "function createAiBrowserFallbackPlugin() { return true; }".to_string(),
            },
            IndexedChunk {
                path: "desktop/dev/aiBrowserFallback.ts".to_string(),
                start_line: 1300,
                end_line: 1380,
                sha1: "b".to_string(),
                language: "ts".to_string(),
                text: "server.middlewares.use(\"/__ai\", async (req, res) => {\nif (req.method === \"GET\" && requestUrl.pathname === \"/status\") {}\nif (req.method === \"POST\" && requestUrl.pathname === \"/ask\") {}\n}".to_string(),
            },
            IndexedChunk {
                path: "README.md".to_string(),
                start_line: 1,
                end_line: 20,
                sha1: "c".to_string(),
                language: "md".to_string(),
                text: "AI browser fallback overview".to_string(),
            },
        ];

        let mut ranked = rank_chunks_lexical(
            "Which file implements the browser AI fallback, and what endpoints does it expose?",
            &chunks,
        );
        ranked.sort_by(|left, right| right.score.total_cmp(&left.score));

        assert_eq!(ranked[0].index, 1);
    }

    #[test]
    fn chat_candidates_prefer_smaller_coder_models() {
        let candidates = build_chat_candidates(&[
            OllamaModel {
                name: "qwen3-coder:latest".to_string(),
                size: 18_556_700_761,
                details: OllamaModelDetails {
                    parameter_size: "30.5B".to_string(),
                },
            },
            OllamaModel {
                name: "qwen2.5-coder:1.5b".to_string(),
                size: 986_062_089,
                details: OllamaModelDetails {
                    parameter_size: "1.5B".to_string(),
                },
            },
            OllamaModel {
                name: "llama3.2-chat".to_string(),
                size: 2_000_000_000,
                details: OllamaModelDetails {
                    parameter_size: "3.0B".to_string(),
                },
            },
            OllamaModel {
                name: "qwen3-embedding:latest".to_string(),
                size: 600_000_000,
                details: OllamaModelDetails {
                    parameter_size: "0.6B".to_string(),
                },
            },
        ]);

        assert_eq!(candidates[0], "qwen2.5-coder:1.5b");
        assert!(!candidates.iter().any(|candidate| candidate.contains("embedding")));
    }

    #[test]
    fn compact_citations_merges_adjacent_ranges() {
        let citations = compact_citations(vec![
            AiCitation {
                path: "desktop/src/routes/ai.tsx".to_string(),
                start_line: 10,
                end_line: 40,
                score: 0.9,
            },
            AiCitation {
                path: "desktop/src/routes/ai.tsx".to_string(),
                start_line: 48,
                end_line: 72,
                score: 0.8,
            },
            AiCitation {
                path: "desktop/src/lib/aiApi.ts".to_string(),
                start_line: 1,
                end_line: 24,
                score: 0.7,
            },
        ]);

        assert_eq!(citations.len(), 2);
        assert_eq!(citations[0].start_line, 10);
        assert_eq!(citations[0].end_line, 72);
    }

    #[test]
    fn repository_summary_is_disabled_for_endpoint_queries() {
        assert!(!should_include_repository_summary(
            "Which endpoints does the browser AI fallback expose?"
        ));
        assert!(should_include_repository_summary(
            "How does the AI tab work overall?"
        ));
    }

    #[test]
    fn supplemental_market_context_can_build_without_repo_chunks() {
        let context = build_context_prompt(
            None,
            &[],
            false,
            "Analyze IBM financial statements and estimate a price range.",
            Some("OpenBB market data for IBM:\n- Current price: $194.50"),
        );
        let messages = build_chat_messages(
            None,
            &[AiChatMessage {
                role: "user".to_string(),
                content: "Analyze IBM financial statements.".to_string(),
            }],
            &[],
            false,
            "Analyze IBM financial statements.",
            Some("OpenBB market data for IBM:\n- Current price: $194.50"),
        );

        assert!(context.contains("OpenBB supplemental market data"));
        assert!(messages
            .first()
            .and_then(|message| message.get("content"))
            .and_then(|value| value.as_str())
            .unwrap_or_default()
            .contains("market data assistant"));
    }

    #[test]
    fn json_parsing_matches_ollama_responses() {
        let tags = serde_json::from_str::<OllamaTagsResponse>(
            r#"{"models":[{"name":"qwen3-coder","size":12,"details":{"parameter_size":"30.5B"}},{"name":"embeddinggemma","size":3,"details":{"parameter_size":"334M"}}]}"#,
        )
        .unwrap();
        assert_eq!(tags.models.len(), 2);
        assert_eq!(tags.models[0].name, "qwen3-coder");
        assert_eq!(tags.models[1].details.parameter_size, "334M");

        let embed = serde_json::from_str::<OllamaEmbedResponse>(
            r#"{"embeddings":[[0.1,0.2,0.3],[0.4,0.5,0.6]]}"#,
        )
        .unwrap();
        assert_eq!(embed.embeddings.len(), 2);
        assert_eq!(embed.embeddings[0].len(), 3);

        let chat = serde_json::from_str::<OllamaChatResponse>(
            r#"{"model":"qwen3-coder","message":{"content":"Answer"}}"#,
        )
        .unwrap();
        assert_eq!(chat.model, "qwen3-coder");
        assert_eq!(chat.message.content, "Answer");
    }

    #[test]
    fn walk_fallback_collects_only_supported_text_files() {
        let repo_root = temp_path("openbb-ai-index");
        fs::create_dir_all(repo_root.join("desktop/src/routes")).unwrap();
        fs::create_dir_all(repo_root.join("node_modules/react")).unwrap();
        fs::write(repo_root.join("README.md"), "# Hello").unwrap();
        fs::write(repo_root.join("desktop/src/routes/ai.tsx"), "export const x = 1;").unwrap();
        fs::write(repo_root.join("desktop/src/routes/routeTree.gen.ts"), "generated").unwrap();
        fs::write(repo_root.join("node_modules/react/index.js"), "ignored").unwrap();

        let files = collect_repo_files_from_walk(&repo_root).unwrap();
        let normalized = files
            .iter()
            .filter_map(|path| normalize_relative_path(&repo_root, path))
            .collect::<Vec<_>>();

        assert!(normalized.contains(&"README.md".to_string()));
        assert!(normalized.contains(&"desktop/src/routes/ai.tsx".to_string()));
        assert!(!normalized.contains(&"desktop/src/routes/routeTree.gen.ts".to_string()));
        assert!(!normalized.iter().any(|path| path.contains("node_modules")));

        let _ = fs::remove_dir_all(repo_root);
    }

    #[tokio::test]
    #[ignore = "requires local Ollama chat and embedding models"]
    async fn live_ai_round_trip_indexes_and_answers() {
        let client = build_http_client(30).unwrap();
        let discovery = discover_ollama(&client).await;
        assert!(discovery.reachable, "Ollama must be reachable for the live AI smoke test.");
        assert!(
            discovery.chat_model.is_some(),
            "At least one chat model must be installed for the live AI smoke test."
        );

        let repo_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .parent()
            .unwrap()
            .parent()
            .unwrap()
            .to_path_buf();
        let repo_root_str = repo_root.to_string_lossy().to_string();

        let index_result = build_ai_index(repo_root_str.clone(), Some(false)).await.unwrap();
        assert!(index_result.chunk_count > 0, "Index should contain at least one chunk.");

        let answer = ask_ai_question(AiAskRequest {
            repo_root: repo_root_str.clone(),
            messages: vec![AiChatMessage {
                role: "user".to_string(),
                content: "How does this project resolve the OpenBB backend?".to_string(),
            }],
            max_context_chunks: Some(8),
            supplemental_context: None,
            supplemental_only: None,
        })
        .await
        .unwrap();

        assert!(
            !answer.answer.trim().is_empty(),
            "AI answer should not be empty after indexing."
        );
        assert!(
            answer
                .citations
                .iter()
                .any(|citation| citation.path.contains("openbbBackend.ts")),
            "Expected at least one citation from openbbBackend.ts, got {:?}",
            answer
                .citations
                .iter()
                .map(|citation| citation.path.clone())
                .collect::<Vec<_>>()
        );
    }
}
