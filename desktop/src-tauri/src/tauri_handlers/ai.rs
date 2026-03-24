use crate::tauri_handlers::helpers::{RealEnvSystem, RealFileSystem, get_working_directory_impl};
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

const OLLAMA_BASE_URL: &str = "http://localhost:11434/api";
const MAX_FILE_SIZE_BYTES: u64 = 256 * 1024;
const CHUNK_LINES: usize = 120;
const CHUNK_OVERLAP: usize = 20;
const DEFAULT_CONTEXT_CHUNKS: usize = 10;
const MAX_CONTEXT_CHUNKS: usize = 16;
const EMBED_BATCH_SIZE: usize = 12;
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

static AI_INDEX_CACHE: Lazy<Mutex<HashMap<String, CachedAiIndex>>> =
    Lazy::new(|| Mutex::new(HashMap::new()));

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum RetrievalMode {
    Semantic,
    Lexical,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AiStatus {
    pub repo_root: Option<String>,
    pub repo_ready: bool,
    pub ollama_reachable: bool,
    pub chat_model: Option<String>,
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
    pub timing_ms: u64,
    pub retrieval_mode: RetrievalMode,
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
    mode: RetrievalMode,
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

#[tauri::command]
pub async fn get_ai_status(default_dir: String) -> Result<AiStatus, String> {
    let repo_context = resolve_repo_context(&default_dir)?;
    let client = build_http_client(5)?;
    let discovery = discover_ollama(&client).await;

    let mut index_ready = false;
    let mut last_indexed_at = None;
    let mut chunk_count = 0;

    if repo_context.repo_ready
        && let Some(repo_root) = repo_context.repo_root.as_ref()
    {
        let index_context = build_index_context(repo_root, discovery.embedding_model.as_deref())?;
        if let Some(manifest) = read_manifest_if_present(&index_directory(&index_context)?)? {
            last_indexed_at = Some(manifest.last_indexed_at.clone());
            chunk_count = manifest.chunk_count;
            index_ready = manifest.revision == index_context.revision;
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
        embedding_model: discovery.embedding_model,
        available_models: discovery.available_models,
        index_ready,
        last_indexed_at,
        chunk_count,
        mode: discovery.mode,
    })
}

#[tauri::command]
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

#[tauri::command]
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

#[tauri::command]
pub async fn ask_ai_question(request: AiAskRequest) -> Result<AiAskResponse, String> {
    let started_at = Instant::now();
    let repo_root = ensure_repo_root(&request.repo_root)?;
    let client = build_http_client(90)?;
    let discovery = discover_ollama(&client).await;

    if !discovery.reachable {
        return Err(
            "Ollama is not reachable at http://localhost:11434. Start Ollama and try again."
                .to_string(),
        );
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

    let index_context = build_index_context(&repo_root, discovery.embedding_model.as_deref())?;
    let cached_index = load_cached_index(&repo_root, &index_context).or_else(|_| {
        let lexical_context = build_index_context(&repo_root, None)?;
        load_cached_index(&repo_root, &lexical_context)
    })?;

    if cached_index.chunks.is_empty() {
        return Err("AI index is empty. Rebuild the index and try again.".to_string());
    }

    let latest_user_message = request
        .messages
        .iter()
        .rev()
        .find(|message| message.role == "user")
        .or_else(|| request.messages.last())
        .ok_or_else(|| "A question is required before asking the project AI.".to_string())?;

    let requested_context = request
        .max_context_chunks
        .unwrap_or(DEFAULT_CONTEXT_CHUNKS)
        .clamp(1, MAX_CONTEXT_CHUNKS);

    let semantic_candidates =
        if cached_index.manifest.mode == RetrievalMode::Semantic && !cached_index.embeddings.is_empty() {
            if let Some(model) = cached_index.manifest.embedding_model.as_deref() {
                match embed_query(&client, model, &latest_user_message.content).await {
                    Ok(query_embedding) => {
                        Some(rank_chunks_semantic(&query_embedding, &cached_index.embeddings))
                    }
                    Err(_) => None,
                }
            } else {
                None
            }
        } else {
            None
        };

    let retrieval_mode = if semantic_candidates.is_some() {
        RetrievalMode::Semantic
    } else {
        RetrievalMode::Lexical
    };

    let mut ranked = semantic_candidates
        .unwrap_or_else(|| rank_chunks_lexical(&latest_user_message.content, &cached_index.chunks));
    ranked.sort_by(|left, right| right.score.total_cmp(&left.score));

    let selected_indexes =
        select_context_chunk_indexes(&ranked, &cached_index.chunks, requested_context);
    let citations = selected_indexes
        .iter()
        .filter_map(|index| {
            let chunk = cached_index.chunks.get(*index)?;
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

    let response = chat_with_fallback(
        &client,
        &chat_candidates,
        build_chat_messages(&cached_index, &request.messages, &selected_indexes),
    )
    .await?;

    Ok(AiAskResponse {
        answer: response.message.content.trim().to_string(),
        citations,
        used_model: response.model,
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
    index: &CachedAiIndex,
    messages: &[AiChatMessage],
    selected_indexes: &[usize],
) -> Vec<serde_json::Value> {
    let system_prompt = "You are a read-only project guide for this repository. Explain the codebase precisely, never invent files or behaviors, say when information is missing, and cite file paths with line ranges in every substantive answer.";
    let context_prompt = build_context_prompt(index, selected_indexes);

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

fn resolve_repo_context(default_dir: &str) -> Result<RepoContext, String> {
    let default_candidate = default_directory_candidate(default_dir)?;
    let stored_candidate = get_working_directory_impl(default_dir, &RealFileSystem, &RealEnvSystem)
        .ok()
        .map(PathBuf::from);
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
            "chunk_lines={CHUNK_LINES};chunk_overlap={CHUNK_OVERLAP};max_file_bytes={MAX_FILE_SIZE_BYTES};extensions={};extra_extensions={};excluded_dirs={};extra_excluded_dirs={};embedding_model={}",
            ALLOWED_EXTENSIONS.join(","),
            EXTRA_ALLOWED_EXTENSIONS.join(","),
            EXCLUDED_DIRS.join(","),
            EXTRA_EXCLUDED_DIRS.join(","),
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
        let chunk_text = lines[start_index..end_index].join("\n");
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
    let tags_response = client.get(format!("{OLLAMA_BASE_URL}/tags")).send().await;
    let Ok(response) = tags_response else {
        return OllamaDiscovery {
            reachable: false,
            available_models: Vec::new(),
            chat_model: None,
            chat_candidates: Vec::new(),
            embedding_model: None,
            mode: RetrievalMode::Lexical,
        };
    };

    if !response.status().is_success() {
        return OllamaDiscovery {
            reachable: false,
            available_models: Vec::new(),
            chat_model: None,
            chat_candidates: Vec::new(),
            embedding_model: None,
            mode: RetrievalMode::Lexical,
        };
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
    let mode = if embedding_model.is_some() {
        RetrievalMode::Semantic
    } else {
        RetrievalMode::Lexical
    };

    OllamaDiscovery {
        reachable: true,
        available_models,
        chat_model,
        chat_candidates,
        embedding_model,
        mode,
    }
}

fn build_chat_candidates(models: &[OllamaModel]) -> Vec<String> {
    let mut candidates = models.to_vec();
    candidates.sort_by(compare_chat_models);
    candidates.into_iter().map(|model| model.name).collect()
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
    if normalized.contains("coder") {
        0
    } else if normalized.contains("instruct") || normalized.contains("chat") {
        1
    } else {
        2
    }
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
        &format!("{OLLAMA_BASE_URL}/embed"),
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
    for batch in chunks.chunks(EMBED_BATCH_SIZE) {
        let inputs = batch.iter().map(|chunk| chunk.text.clone()).collect::<Vec<_>>();
        let batch_embeddings = embed_input_batch(client, model, inputs).await?;

        if batch_embeddings.len() != batch.len() {
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

async fn embed_query(client: &Client, model: &str, input: &str) -> Result<Vec<f32>, String> {
    let response = post_json::<OllamaEmbedResponse>(
        client,
        &format!("{OLLAMA_BASE_URL}/embed"),
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
            &format!("{OLLAMA_BASE_URL}/embed"),
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
            Err(error) => return Err(error),
        }
    }

    Ok(embeddings)
}

fn split_string_batch(batch: &[String]) -> (Vec<String>, Vec<String>) {
    let midpoint = (batch.len() / 2).max(1);
    (batch[..midpoint].to_vec(), batch[midpoint..].to_vec())
}

async fn chat_with_fallback(
    client: &Client,
    candidate_models: &[String],
    messages: Vec<serde_json::Value>,
) -> Result<OllamaChatResponse, String> {
    let mut last_error = None;

    for model in candidate_models {
        match post_json::<OllamaChatResponse>(
            client,
            &format!("{OLLAMA_BASE_URL}/chat"),
            json!({
                "model": model,
                "stream": false,
                "keep_alive": "5m",
                "messages": messages.clone(),
            }),
        )
        .await
        {
            Ok(response) => return Ok(response),
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
            score: lexical_score(&query_tokens, chunk),
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

fn lexical_score(query_tokens: &[String], chunk: &IndexedChunk) -> f32 {
    if query_tokens.is_empty() {
        return 0.0;
    }

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

    overlap as f32 / query_tokens.len() as f32 + path_bonus + substring_bonus
}

fn select_context_chunk_indexes(
    ranked: &[RankedChunk],
    chunks: &[IndexedChunk],
    max_chunks: usize,
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

    if let Some(index) = chunks.iter().position(|chunk| chunk.path == SUMMARY_CHUNK_PATH)
        && seen.insert(index)
    {
        selected.push(index);
    }

    selected
}

fn build_context_prompt(index: &CachedAiIndex, selected_indexes: &[usize]) -> String {
    let mut sections = Vec::new();
    sections.push(format!(
        "Repository root: {}\nIndexed at: {}\nRetrieval mode: {:?}",
        index.manifest.repo_root, index.manifest.last_indexed_at, index.manifest.mode
    ));
    sections.push(format!("Project summary:\n{}", index.manifest.summary_prompt));

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
                path: "desktop/src/routes/ops.tsx".to_string(),
                start_line: 1,
                end_line: 10,
                sha1: "b".to_string(),
                language: "tsx".to_string(),
                text: "Scheduler and registry page".to_string(),
            },
        ];

        let mut ranked = rank_chunks_lexical("AI route guide", &chunks);
        ranked.sort_by(|left, right| right.score.total_cmp(&left.score));
        assert_eq!(ranked[0].index, 0);
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
        ]);

        assert_eq!(candidates[0], "qwen2.5-coder:1.5b");
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
