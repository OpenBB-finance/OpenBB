use crate::tauri_handlers::helpers::{
    EnvSystem, FileExtTrait, FileSystem, RealEnvSystem, RealFileExtTrait, RealFileSystem,
    get_installation_directory_impl,
};
use crate::utils::command_sanitizer::validate_command_input;
use crate::utils::process_monitor::{RunningProcesses, register_process};
use chrono::Utc;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fmt;
use std::io::{BufRead, BufReader, Read, Seek, SeekFrom, Write};
use std::path::PathBuf;
use std::process::Stdio;
use tauri::{AppHandle, Emitter, Manager};
use uuid::Uuid;

#[derive(Clone, serde::Serialize)]
pub struct Payload {
    message: String,
}

#[derive(Clone, serde::Serialize)]
struct BackendUrlPayload {
    id: String,
    url: String,
}

// =============== CORE DATA STRUCTURES ===============

/// Backend service configuration and state
#[derive(Debug, Clone, Serialize, Deserialize, Default, PartialEq)]
pub struct BackendService {
    // Core identification
    pub id: String,
    pub name: String,

    // Command and environment
    pub command: String,
    pub environment: String,
    pub auto_start: bool,

    // Runtime state
    pub status: String,

    // Process tracking
    #[serde(skip_serializing_if = "Option::is_none")]
    #[serde(alias = "envFile", rename = "envFile")]
    pub env_file: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    #[serde(alias = "envVars", rename = "envVars")]
    pub env_vars: Option<HashMap<String, String>>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub working_directory: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub host: Option<String>, // Host for the backend service

    #[serde(skip_serializing_if = "Option::is_none")]
    pub port: Option<u16>, // Port for the backend service

    #[serde(skip_serializing_if = "Option::is_none")]
    pub url: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub pid: Option<u32>, // Process PID

    // Metadata
    #[serde(skip_serializing_if = "Option::is_none")]
    pub started_at: Option<String>,

    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
}

impl BackendService {
    pub fn new(
        name: String,
        command: String,
        working_directory: Option<String>,
        environment: String,
        env_file: Option<String>,
        env_vars: Option<HashMap<String, String>>,
        auto_start: bool,
    ) -> Self {
        Self {
            id: Uuid::new_v4().to_string(),
            name,
            command,
            working_directory,
            environment,
            env_file,
            env_vars,
            auto_start,
            host: None,
            port: None,
            url: None,
            status: BackendStatus::Stopped.to_string(),
            pid: None,
            started_at: None,
            error: None,
        }
    }

    /// Check if the backend should be considered running
    pub fn is_running(&self) -> bool {
        self.status == "running" && self.pid.is_some()
    }
}

/// Enum for backend status
#[derive(Debug, Clone)]
pub enum BackendStatus {
    Running,
    Stopped,
    Starting,
    Stopping,
    Error,
}

impl fmt::Display for BackendStatus {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let s = match self {
            Self::Running => "running",
            Self::Stopped => "stopped",
            Self::Starting => "starting",
            Self::Stopping => "stopping",
            Self::Error => "error",
        };
        write!(f, "{s}")
    }
}

/// Load environment variables from a .env file
fn load_env_file<F: FileSystem>(
    env_file_path: &str,
    fs: &F,
) -> Result<HashMap<String, String>, String> {
    let mut env_vars = HashMap::new();

    if env_file_path.trim().is_empty() {
        return Ok(env_vars);
    }
    let content = fs
        .read_to_string(std::path::Path::new(env_file_path))
        .map_err(|e| format!("Failed to read env file {env_file_path}: {e}"))?;

    for line in content.lines() {
        let line = line.trim();

        // Skip empty lines and comments
        if line.is_empty() || line.starts_with('#') {
            continue;
        }

        // Parse KEY=VALUE format
        if let Some(eq_pos) = line.find('=') {
            let key = line[..eq_pos].trim().to_string();
            let value = line[eq_pos + 1..].trim();

            // Remove quotes if present
            let value = if (value.starts_with('"') && value.ends_with('"'))
                || (value.starts_with('\'') && value.ends_with('\''))
            {
                &value[1..value.len() - 1]
            } else {
                value
            };

            env_vars.insert(key, value.to_string());
        }
    }

    Ok(env_vars)
}

fn clean_error_message(raw_message: &str) -> String {
    // Look for the pattern: file:line:command:error
    // We want to extract just "command: error"
    if let Some(last_colon) = raw_message.rfind(": ") {
        let after_last_colon = &raw_message[last_colon + 2..]; // Get "command not found"

        // Find the second-to-last colon to get the command part
        let before_last_colon = &raw_message[..last_colon];
        if let Some(second_last_colon) = before_last_colon.rfind(": ") {
            let command_part = &before_last_colon[second_last_colon + 2..]; // Get "openbb-api"
            return format!("{}: {}", command_part, after_last_colon);
        }
    }

    // Fallback: return the original message
    raw_message.to_string()
}

/// Get the backends directory
fn get_backends_dir<F: FileSystem, E: EnvSystem>(fs: &F, env_sys: &E) -> PathBuf {
    let app_dir =
        get_installation_directory_impl(fs, env_sys).unwrap_or_else(|_| String::from("./"));
    let backends_dir = PathBuf::from(app_dir).join("backends");

    if !fs.exists(&backends_dir) {
        let _ = fs.create_dir_all(&backends_dir);
    }

    backends_dir
}

/// Get the backends configuration file path
fn get_backends_config_path<F: FileSystem, E: EnvSystem>(fs: &F, env_sys: &E) -> PathBuf {
    get_backends_dir(fs, env_sys).join("backends.json")
}

/// Load all backends from configuration file
pub fn load_backends_config<F: FileSystem, E: EnvSystem>(
    fs: &F,
    env_sys: &E,
) -> Result<Vec<BackendService>, String> {
    let config_path = get_backends_config_path(fs, env_sys);

    if !fs.exists(&config_path) {
        return Ok(Vec::new());
    }

    let mut file = match fs.open_ro(&config_path) {
        Ok(file) => file,
        Err(e) => return Err(format!("Failed to open backends config: {e}")),
    };

    let mut contents = String::new();
    if let Err(e) = file.read_to_string(&mut contents) {
        return Err(format!("Failed to read backends config: {e}"));
    }

    if contents.trim().is_empty() {
        return Ok(Vec::new());
    }

    serde_json::from_str(&contents).map_err(|e| format!("Failed to parse backends config: {e}"))
}

/// Save backends to configuration file
pub fn save_backends_config<F: FileSystem, E: EnvSystem, FE: FileExtTrait>(
    backends: &[BackendService],
    fs: &F,
    env_sys: &E,
    file_ext: &FE,
) -> Result<(), String> {
    let config_path = get_backends_config_path(fs, env_sys);

    let json = serde_json::to_string_pretty(backends)
        .map_err(|e| format!("Failed to serialize backends: {e}"))?;

    let mut file = fs
        .open_rw_create(&config_path)
        .map_err(|e| format!("Failed to open backends config for locking: {e}"))?;

    file_ext
        .try_lock_exclusive(&file)
        .map_err(|e| format!("Failed to lock backends config: {e}"))?;

    // Truncate and write
    file.seek(SeekFrom::Start(0)).map_err(|e| {
        file_ext.unlock(&file).ok();
        format!("Failed to seek backends config: {e}")
    })?;
    file.set_len(0).map_err(|e| {
        file_ext.unlock(&file).ok();
        format!("Failed to truncate backends config: {e}")
    })?;
    file.write_all(json.as_bytes()).map_err(|e| {
        file_ext.unlock(&file).ok();
        format!("Failed to write backends config: {e}")
    })?;
    file.flush().map_err(|e| {
        file_ext.unlock(&file).ok();
        format!("Failed to flush backends config: {e}")
    })?;

    // Unlock file
    file_ext
        .unlock(&file)
        .map_err(|e| format!("Failed to unlock backends config: {e}"))?;

    Ok(())
}

// =============== PROCESS MANAGEMENT ===============

/// Check if a process is running
fn is_process_running<E: EnvSystem>(pid: u32, env_sys: &E) -> bool {
    #[cfg(target_family = "unix")]
    {
        env_sys
            .new_command("kill")
            .args(["-0", &pid.to_string()])
            .status()
            .map(|status| status.success())
            .unwrap_or(false)
    }
    #[cfg(target_os = "windows")]
    {
        let mut cmd = env_sys.new_command("tasklist");
        cmd.args(["/FI", &format!("PID eq {pid}"), "/NH"])
            .output()
            .map(|output| String::from_utf8_lossy(&output.stdout).contains(&pid.to_string()))
            .unwrap_or(false)
    }
}

// =============== TAURI COMMANDS ===============

/// Stop a backend service
pub async fn stop_backend_service_impl<F: FileSystem, E: EnvSystem, FE: FileExtTrait>(
    app_handle: tauri::AppHandle,
    id: String,
    fs: &F,
    env_sys: &E,
    file_ext: &FE,
) -> Result<(), String> {
    log::debug!("Stopping backend service: {id}");

    let backends = load_backends_config(fs, env_sys)?;
    let backend = backends
        .iter()
        .find(|b| b.id == id)
        .ok_or_else(|| "Backend not found".to_string())?;

    let port = backend.port;

    if let Some(port) = port {
        log::debug!("KILLING PROCESSES ON PORT {port}");

        let port_kill_message = format!("🎯 Killing all processes on port {port}");
        let port_kill_timestamp = chrono::Utc::now().timestamp_millis();
        let process_id = format!("backend-{id}");
        let log_storage = crate::get_log_storage();
        let port_kill_entry = crate::utils::process_monitor::LogEntry {
            timestamp: port_kill_timestamp,
            content: port_kill_message.clone(),
            process_id: process_id.clone(),
        };
        if let Ok(mut storage) = log_storage.lock()
            && let Some(buffer) = storage.get_mut(&process_id)
        {
            buffer.add(port_kill_entry);
        }

        let port_kill_payload = serde_json::json!({
            "processId": process_id,
            "output": "",
            "timestamp": port_kill_timestamp,
            "type": "system"
        });
        let _ = app_handle.emit("process-output", port_kill_payload);

        // Kill processes using the port
        #[cfg(target_os = "macos")]
        {
            // Find PIDs using the port
            let output = env_sys
                .new_command("lsof")
                .args(["-ti", &format!("tcp:{port}")])
                .output();

            if let Ok(output) = output {
                let pids_str = String::from_utf8_lossy(&output.stdout);
                for pid_str in pids_str.lines() {
                    if let Ok(pid) = pid_str.trim().parse::<u32>() {
                        log::debug!("Killing process {pid} using port {port}");
                        let kill_result = env_sys
                            .new_command("kill")
                            .args(["-9", &pid.to_string()])
                            .output();
                        log::debug!("Port kill result for PID {pid}: {kill_result:?}");
                    }
                }
            }
        }

        #[cfg(target_os = "linux")]
        {
            // Use fuser to kill processes on port
            let output = env_sys
                .new_command("fuser")
                .args(["-k", &format!("{}/tcp", port)])
                .output();
            log::debug!("Port kill result (Linux): {:?}", output);

            // Also try lsof approach as backup
            let output = env_sys
                .new_command("lsof")
                .args(["-ti", &format!("tcp:{}", port)])
                .output();

            if let Ok(output) = output {
                let pids_str = String::from_utf8_lossy(&output.stdout);
                for pid_str in pids_str.lines() {
                    if let Ok(pid) = pid_str.trim().parse::<u32>() {
                        log::debug!("Killing process {} using port {}", pid, port);
                        let _ = env_sys
                            .new_command("kill")
                            .args(["-9", &pid.to_string()])
                            .output();
                    }
                }
            }
        }

        #[cfg(target_os = "windows")]
        {
            // Find PIDs using the port with netstat
            let mut cmd = env_sys.new_command("netstat");
            let output = cmd.args(["-ano"]).output();

            if let Ok(output) = output {
                let netstat_output = String::from_utf8_lossy(&output.stdout);
                for line in netstat_output.lines() {
                    if line.contains(&format!(":{port}"))
                        && line.contains("LISTENING")
                        && let Some(pid_str) = line.split_whitespace().last()
                        && let Ok(pid) = pid_str.parse::<u32>()
                    {
                        log::debug!("Killing process {pid} using port {port}");
                        let mut kill_cmd = env_sys.new_command("taskkill");
                        let kill_result = kill_cmd.args(["/F", "/PID", &pid.to_string()]).output();
                        log::debug!("Port kill result for PID {pid}: {kill_result:?}");
                    }
                }
            }
        }

        // Wait for port kills to take effect
        std::thread::sleep(std::time::Duration::from_millis(2000));
    }

    // Emit shutdown start message to logs
    let process_id = format!("backend-{id}");
    let timestamp = chrono::Utc::now().timestamp_millis();
    let shutdown_message = format!("🛑 Stopping backend service '{0}'", backend.name);

    // Store in log buffer
    let log_storage = crate::get_log_storage();
    let entry = crate::utils::process_monitor::LogEntry {
        timestamp,
        content: shutdown_message.clone(),
        process_id: process_id.clone(),
    };
    if let Ok(mut storage) = log_storage.lock()
        && let Some(buffer) = storage.get_mut(&process_id)
    {
        buffer.add(entry);
    }

    // Also emit as event
    let shutdown_start_payload = serde_json::json!({
        "processId": process_id,
        "output": shutdown_message,
        "timestamp": timestamp,
        "type": "system"
    });
    let _ = app_handle.emit("process-output", shutdown_start_payload);

    // Remove from process tracking and kill process
    if let Some(processes) = app_handle.try_state::<RunningProcesses>() {
        match processes.kill_process(&id) {
            Ok(true) => log::debug!("Successfully killed backend process: {id}"),
            Ok(false) => log::warn!("Backend {id} not found in process tracking"),
            Err(e) => log::error!("Error killing backend process {id}: {e}"),
        }
    } else {
        log::warn!("RunningProcesses state not available for killing process: {id}");
    }

    // Kill by PID if available (fallback)
    if let Some(pid) = backend.pid {
        log::debug!("Killing process (PID: {pid})");

        let kill_message = format!("💀 Terminating process PID {pid}");
        let kill_timestamp = chrono::Utc::now().timestamp_millis();

        // Store in log buffer
        let kill_entry = crate::utils::process_monitor::LogEntry {
            timestamp: kill_timestamp,
            content: kill_message.clone(),
            process_id: process_id.clone(),
        };
        if let Ok(mut storage) = log_storage.lock()
            && let Some(buffer) = storage.get_mut(&process_id)
        {
            buffer.add(kill_entry);
        }

        let kill_payload = serde_json::json!({
            "processId": process_id,
            "output": kill_message,
            "timestamp": kill_timestamp,
            "type": "system"
        });
        let _ = app_handle.emit("process-output", kill_payload);

        #[cfg(target_os = "windows")]
        {
            let mut cmd = env_sys.new_command("taskkill");
            let output = cmd.args(["/F", "/PID", &pid.to_string()]).output();
            log::debug!("PID kill result: {output:?}");
        }
        #[cfg(not(target_os = "windows"))]
        {
            let output = env_sys
                .new_command("kill")
                .args(["-9", &pid.to_string()])
                .output();
            log::debug!("PID kill result: {output:?}");
        }
    }

    // Wait a moment for process to die
    std::thread::sleep(std::time::Duration::from_millis(1000));

    // Update status in config
    let mut backends = load_backends_config(fs, env_sys)?;
    if let Some(backend_config) = backends.iter_mut().find(|b| b.id == id) {
        backend_config.status = BackendStatus::Stopped.to_string();
        backend_config.pid = None;
        backend_config.url = None;
        backend_config.started_at = None;
        backend_config.host = None;
        backend_config.port = None;
    }
    save_backends_config(&backends, fs, env_sys, file_ext)?;

    // Emit final shutdown completion message
    let shutdown_complete_message =
        format!("🟢 Backend service '{}' stopped successfully", backend.name);
    let shutdown_complete_timestamp = chrono::Utc::now().timestamp_millis();

    let shutdown_complete_entry = crate::utils::process_monitor::LogEntry {
        timestamp: shutdown_complete_timestamp,
        content: shutdown_complete_message.clone(),
        process_id: process_id.clone(),
    };
    if let Ok(mut storage) = log_storage.lock()
        && let Some(buffer) = storage.get_mut(&process_id)
    {
        buffer.add(shutdown_complete_entry);
    }

    let shutdown_complete_payload = serde_json::json!({
        "processId": process_id,
        "output": shutdown_complete_message,
        "timestamp": shutdown_complete_timestamp,
        "type": "system"
    });
    let _ = app_handle.emit("process-output", shutdown_complete_payload);

    log::debug!("Backend service '{id}' stopped");
    Ok(())
}

#[tauri::command]
pub async fn stop_backend_service(app_handle: tauri::AppHandle, id: String) -> Result<(), String> {
    stop_backend_service_impl(
        app_handle,
        id,
        &RealFileSystem,
        &RealEnvSystem,
        &RealFileExtTrait,
    )
    .await
}

// Helper function to remove ANSI escape sequences from a string
fn remove_ansi_escape_sequences(input: &str) -> String {
    let ansi_regex = regex::Regex::new(r"\x1B\[[0-9;]*[a-zA-Z]").unwrap();
    ansi_regex.replace_all(input, "").to_string()
}

/// Selects the best URL from a list based on predefined priorities.
fn select_best_url(urls: &[String], original_log_line: &str) -> Option<String> {
    if urls.is_empty() {
        return None;
    }

    let mut selected_url: Option<String> = None;

    // Priority 1: URLs ending with /mcp or /sse
    if let Some(url) = urls
        .iter()
        .find(|u| u.ends_with("/mcp") || u.ends_with("/sse"))
    {
        selected_url = Some(url.clone());
    }

    // Priority 2: URLs containing /mcp or /sse
    if selected_url.is_none()
        && let Some(url) = urls
            .iter()
            .find(|u| u.contains("/mcp") || u.contains("/sse"))
    {
        selected_url = Some(url.clone());
    }

    // Priority 3: URLs for docs/openapi
    if selected_url.is_none()
        && let Some(url) = urls
            .iter()
            .find(|u| u.contains("docs") || u.contains("openapi") || u.contains("redoc"))
    {
        selected_url = Some(url.clone());
    }

    // Fallback: use the last URL found
    if selected_url.is_none() {
        selected_url = urls.last().cloned();
    }

    // Final adjustment for MCP servers
    if let Some(mut url) = selected_url {
        if original_log_line.contains("MCP server")
            && !url.contains("/mcp")
            && !url.contains("/sse")
        {
            url = url.trim_end_matches('/').to_string();
            if original_log_line.contains("streamable-http") {
                url.push_str("/mcp");
            } else if original_log_line.contains("sse") {
                url.push_str("/sse");
            } else {
                url.push_str("/mcp"); // Default
            }
        }
        return Some(url);
    }

    None
}

#[tauri::command]
pub async fn start_backend_service(
    app_handle: tauri::AppHandle,
    id: String,
) -> Result<BackendService, String> {
    start_backend_service_impl(
        app_handle,
        id,
        RealFileSystem,
        RealEnvSystem,
        RealFileExtTrait,
    )
    .await
}

/// Start a backend service
pub async fn start_backend_service_impl<
    F: FileSystem + Send + Sync + 'static + Clone + Copy,
    E: EnvSystem + Send + Sync + 'static + Clone + Copy,
    FE: FileExtTrait + Send + Sync + 'static + Clone + Copy,
>(
    app_handle: tauri::AppHandle,
    id: String,
    fs: F,
    env_sys: E,
    file_ext: FE,
) -> Result<BackendService, String> {
    // Load configs
    let backends = load_backends_config(&fs, &env_sys)?;
    let backend = backends
        .iter()
        .find(|b| b.id == id)
        .ok_or_else(|| "Backend not found".to_string())?
        .clone();

    if let Err(validation_error) = validate_command_input(&backend.command, &fs, &env_sys) {
        log::error!(
            "Command validation failed for backend '{}': {}",
            backend.name,
            validation_error
        );

        // Update backend status to error in config
        let mut backends = load_backends_config(&fs, &env_sys)?;
        if let Some(backend_config) = backends.iter_mut().find(|b| b.id == id) {
            backend_config.status = BackendStatus::Error.to_string();
            backend_config.error =
                Some(format!("Dangerous command detected: {}", validation_error));
        }
        save_backends_config(&backends, &fs, &env_sys, &file_ext)?;

        return Err(format!("Cannot start backend: {}", validation_error));
    }

    // Check if already running
    if backend.status == "running"
        && let Some(pid) = backend.pid
        && is_process_running(pid, &env_sys)
    {
        return Ok(backend);
    }

    // Get conda directory
    let install_dir = get_installation_directory_impl(&fs, &env_sys)?;
    let conda_dir = std::path::Path::new(&install_dir).join("conda");

    // Get conda executable
    let conda_exe = if env_sys.consts_os() == "windows" {
        conda_dir.join("Scripts").join("conda.exe")
    } else {
        conda_dir.join("bin").join("conda")
    };

    if !fs.exists(&conda_exe) {
        return Err(format!(
            "Conda executable not found at: {}",
            conda_exe.display()
        ));
    }

    // Load environment variables from env file if specified
    let mut env_exports = String::new();
    if let Some(env_file) = &backend.env_file
        && !env_file.trim().is_empty()
    {
        match load_env_file(env_file, &fs) {
            Ok(env_vars) => {
                for (key, value) in env_vars {
                    if env_sys.consts_os() == "windows" {
                        // For batch files, need to handle special characters
                        env_exports.push_str(&format!("set \"{key}={value}\"\n"));
                    } else {
                        // For bash, use export and quote the value
                        env_exports.push_str(&format!(
                            "export {}='{}'\n",
                            key,
                            value.replace('\'', "'\\''")
                        ));
                    }
                }
                log::debug!("Loaded environment variables from: {env_file}");
            }
            Err(e) => {
                log::warn!("Failed to load env file {env_file}: {e}");
                // Continue without env file - don't fail the start
            }
        }
    }

    // Add environment variables from env_vars
    if let Some(env_vars) = &backend.env_vars {
        for (key, value) in env_vars {
            if env_sys.consts_os() == "windows" {
                env_exports.push_str(&format!("set \"{key}={value}\"\n"));
            } else {
                env_exports.push_str(&format!(
                    "export {}='{}'\n",
                    key,
                    value.replace('\'', "'\\''")
                ));
            }
        }
        log::debug!("Loaded environment variables from direct configuration");
    }

    // Create activation script for the environment
    let script_ext = if env_sys.consts_os() == "windows" {
        "bat"
    } else {
        "sh"
    };
    let script_path = env_sys
        .temp_dir()
        .join(format!("backend_start_{}.{}", backend.id, script_ext));

    // Modify command if it's "openbb-api" and an env_file is present
    let mut command_to_run = backend.command.clone();
    if command_to_run.contains("openbb-api") {
        if let Some(env_file) = &backend.env_file
            && !env_file.trim().is_empty()
        {
            command_to_run.push_str(&format!(" --env_file \"{env_file}\""));

            // Handle UVICORN_ variables
            if let Ok(env_vars) = load_env_file(env_file, &fs) {
                for (key, value) in env_vars {
                    if key.starts_with("UVICORN_") {
                        let arg_key = key.replace("UVICORN_", "").to_lowercase();
                        let arg = format!("--{arg_key}");
                        if !command_to_run.contains(&arg) {
                            command_to_run.push_str(&format!(" {arg} \"{value}\""));
                        }
                    }
                }
            }
        }
        // Also handle UVICORN_ variables from the main env_vars configuration
        if let Some(env_vars) = &backend.env_vars {
            for (key, value) in env_vars {
                if key.starts_with("UVICORN_") {
                    let arg_key = key.replace("UVICORN_", "").to_lowercase();
                    let arg = format!("--{arg_key}");
                    if !command_to_run.contains(&arg) {
                        command_to_run.push_str(&format!(" {arg} \"{value}\""));
                    }
                }
            }
        }
    }

    let script_content = if env_sys.consts_os() == "windows" {
        format!(
            r#"@echo off
setlocal enabledelayedexpansion
set "CONDA_ROOT={}"
set "CONDA_ENVS_PATH={}"
set "CONDA_PKGS_DIRS={}"
set "CONDARC={}"
set CONDA_DEFAULT_ENV=
set CONDA_PREFIX=
set CONDA_SHLVL=
set "PATH={};{};%PATH%"

REM Initialize conda for batch
call "{}\condabin\conda.bat" --version >nul 2>&1
if errorlevel 1 (
    echo Conda not properly initialized
    exit /b 1
)

REM Activate the environment
call "{}\condabin\conda.bat" activate {} 2>nul
if errorlevel 1 (
    echo Failed to activate environment: {}
    exit /b 1
)

echo Environment {} activated successfully

REM Set environment variables from .env file
{}

{}
"#,
            conda_dir.to_string_lossy(),
            conda_dir.join("envs").to_string_lossy(),
            conda_dir.join("pkgs").to_string_lossy(),
            conda_dir.join(".condarc").to_string_lossy(),
            conda_dir.join("Scripts").to_string_lossy(),
            conda_dir.join("condabin").to_string_lossy(),
            conda_dir.to_string_lossy(),
            conda_dir.to_string_lossy(),
            backend.environment,
            backend.environment,
            backend.environment,
            env_exports,
            command_to_run
        )
    } else {
        format!(
            r#"#!/bin/bash
export CONDA_ROOT="{}"
export CONDA_ENVS_PATH="{}"
export CONDA_PKGS_DIRS="{}"
export CONDARC="{}"
unset CONDA_DEFAULT_ENV
unset CONDA_PREFIX
unset CONDA_SHLVL
export PATH="{}:{}:$PATH"

# Initialize conda for bash
source "{}/etc/profile.d/conda.sh"
if [ $? -ne 0 ]; then
    echo "Failed to initialize conda"
    exit 1
fi

# Activate the environment
conda activate {}
if [ $? -ne 0 ]; then
    echo "Failed to activate environment: {}"
    exit 1
fi

echo "Environment {} activated successfully"

# Set environment variables from .env file
{}

{}
"#,
            conda_dir.to_string_lossy(),
            conda_dir.join("envs").to_string_lossy(),
            conda_dir.join("pkgs").to_string_lossy(),
            conda_dir.join(".condarc").to_string_lossy(),
            conda_dir.join("bin").to_string_lossy(),
            conda_dir.join("condabin").to_string_lossy(),
            conda_dir.to_string_lossy(),
            backend.environment,
            backend.environment,
            backend.environment,
            env_exports,
            command_to_run
        )
    };

    // Write script
    fs.write(&script_path, &script_content)
        .map_err(|e| format!("Failed to create activation script: {e}"))?;

    // Make executable on Unix
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let mut perms = fs
            .metadata(&script_path)
            .map_err(|e| format!("Failed to get script permissions: {e}"))?
            .permissions();
        perms.set_mode(0o755);
        fs.set_permissions(&script_path, perms)
            .map_err(|e| format!("Failed to set script permissions: {e}"))?;
    }

    // Create command to run the script
    let mut cmd = if cfg!(target_os = "windows") {
        let mut c = env_sys.new_command("cmd");
        c.args(["/c", &script_path.to_string_lossy()]);
        c
    } else {
        let mut c = env_sys.new_command("bash");
        c.arg(&script_path);
        c
    };

    // Setup I/O
    cmd.stdout(Stdio::piped()).stderr(Stdio::piped());

    // Set working directory if specified
    if let Some(working_dir) = &backend.working_directory {
        cmd.current_dir(working_dir);
    } else {
        cmd.current_dir(get_backends_dir(&fs, &env_sys));
    }

    // Spawn the process
    let mut child = match cmd.spawn() {
        Ok(child) => child,
        Err(e) => {
            let _ = fs.remove_file(&script_path.to_string_lossy());
            let error = format!("Failed to start backend: {e}");
            return Err(error);
        }
    };

    // Clean up script after a delay
    let script_path_clone = script_path.clone();
    std::thread::spawn(move || {
        std::thread::sleep(std::time::Duration::from_secs(5));
        let _ = fs.remove_file(&script_path_clone.to_string_lossy());
    });

    // Get process PID
    let process_pid = child.id();
    let process_id = format!("backend-{id}");

    // Register process for monitoring
    let log_storage = crate::get_log_storage();
    register_process(&log_storage, &process_id);
    log::debug!("Registered backend process for monitoring with ID: {process_id}");

    // --- Shared state for URL detection ---
    let detected_urls = std::sync::Arc::new(std::sync::Mutex::new(Vec::<String>::new()));
    let last_line_with_url = std::sync::Arc::new(std::sync::Mutex::new(String::new()));
    let debounce_thread =
        std::sync::Arc::new(std::sync::Mutex::new(None::<std::thread::JoinHandle<()>>));

    // --- Stderr/Stdout Log Processing ---
    let script_path_str = script_path.to_string_lossy().to_string();
    let log_processor = move |line: String,
                              stream_type: &str,
                              app_handle: &AppHandle,
                              backend_id: &str,
                              process_id: &str| {
        let line = line.replace(&format!("{}: ", script_path_str), "");

        // --- Generic Log Forwarding ---
        let timestamp = chrono::Utc::now().timestamp_millis();
        let log_storage = crate::get_log_storage();
        let entry = crate::utils::process_monitor::LogEntry {
            timestamp,
            content: line.clone(),
            process_id: process_id.to_string(),
        };
        if let Ok(mut storage) = log_storage.lock()
            && let Some(buffer) = storage.get_mut(process_id)
        {
            buffer.add(entry);
        }
        let payload = serde_json::json!({
            "processId": process_id,
            "output": line,
            "timestamp": timestamp,
            "type": stream_type
        });
        if let Err(e) = app_handle.emit("process-output", payload) {
            log::error!("Failed to emit process-output event: {e}");
        }

        // --- Command Not Found Error Handling ---
        if line.trim_end().ends_with(": command not found") {
            let clean_error = clean_error_message(&line);
            log::error!("Backend {} failed to start: {}", backend_id, clean_error);

            if let Ok(mut backends) = load_backends_config(&fs, &env_sys) {
                if let Some(b) = backends.iter_mut().find(|b| b.id == backend_id) {
                    b.status = BackendStatus::Error.to_string();
                    b.error = Some(clean_error);
                    b.pid = None;
                }
                if let Err(e) = save_backends_config(&backends, &fs, &env_sys, &file_ext) {
                    log::error!("Failed to save backend error state: {e}");
                }
            }
            if let Some(p) = app_handle.try_state::<RunningProcesses>() {
                let _ = p.kill_process(backend_id);
            }
            return; // Stop processing
        }

        // --- PID and URL Extraction ---
        let clean_line = remove_ansi_escape_sequences(&line);
        let pid_regex = regex::Regex::new(r"Started server process \[(\d+)\]").unwrap();
        let url_pattern = r"(https?:\/\/(?:localhost|\d{1,3}(?:\.\d{1,3}){3})(?::\d+)?(?:[^\s]*)?)";
        let url_regex = regex::Regex::new(url_pattern).unwrap();

        // PID Extraction
        if let Some(caps) = pid_regex.captures(&clean_line)
            && let Some(pid_match) = caps.get(1)
            && let Ok(real_pid) = pid_match.as_str().parse::<u32>()
        {
            log::info!("Found server PID: {real_pid} for backend {backend_id}");
            if let Ok(mut backends) = load_backends_config(&fs, &env_sys)
                && let Some(b) = backends.iter_mut().find(|b| b.id == backend_id)
            {
                b.pid = Some(real_pid);
                if let Err(e) = save_backends_config(&backends, &fs, &env_sys, &file_ext) {
                    log::error!("Failed to save PID to config: {e}");
                }
            }
        }

        // URL Extraction and Debounced Update
        let found_urls: Vec<String> = url_regex
            .find_iter(&clean_line)
            .map(|m| m.as_str().to_string())
            .collect();

        if !found_urls.is_empty() {
            log::debug!("Found URLs in log line: {:?}", found_urls);
            if let Ok(mut urls) = detected_urls.lock() {
                urls.extend(found_urls);
            }
            if let Ok(mut last_line) = last_line_with_url.lock() {
                *last_line = clean_line.clone();
            }

            // --- Debounce Logic ---
            let mut debounce_guard = debounce_thread.lock().unwrap();
            if let Some(handle) = debounce_guard.take() {
                handle.thread().unpark(); // In case it was sleeping
            }

            let backend_id_clone = backend_id.to_string();
            let detected_urls_clone = detected_urls.clone();
            let last_line_clone = last_line_with_url.clone();
            let fs_clone = fs;
            let env_sys_clone = env_sys;
            let file_ext_clone = file_ext;
            let app_handle_clone = app_handle.clone();

            *debounce_guard = Some(std::thread::spawn(move || {
                std::thread::sleep(std::time::Duration::from_millis(1500));

                let final_urls = detected_urls_clone.lock().unwrap().clone();
                let final_line = last_line_clone.lock().unwrap().clone();

                if let Some(best_url) = select_best_url(&final_urls, &final_line) {
                    log::info!("Selected best URL for backend {backend_id_clone}: {best_url}");
                    if let Ok(mut backends) = load_backends_config(&fs_clone, &env_sys_clone)
                        && let Some(b) = backends.iter_mut().find(|b| b.id == backend_id_clone)
                    {
                        b.url = Some(best_url.clone());
                        if let Ok(parsed) = url::Url::parse(&best_url) {
                            b.host = parsed.host_str().map(String::from);
                            b.port = parsed.port();
                        }
                        if save_backends_config(
                            &backends,
                            &fs_clone,
                            &env_sys_clone,
                            &file_ext_clone,
                        )
                        .is_ok()
                        {
                            if let Err(e) = app_handle_clone.emit(
                                "backend-url-discovered",
                                BackendUrlPayload {
                                    id: backend_id_clone,
                                    url: best_url,
                                },
                            ) {
                                log::error!("Failed to emit backend-url-discovered event: {e}");
                            }
                        } else {
                            log::error!("Failed to save final URL to config");
                        }
                    }
                }
            }));
        }
    };

    // --- Spawn Threads for Stdout/Stderr ---
    let _stdout_thread = if let Some(stdout) = child.stdout.take() {
        let app_handle_clone = app_handle.clone();
        let backend_id_clone = backend.id.clone();
        let process_id_clone = process_id.clone();
        let processor = log_processor.clone();
        Some(std::thread::spawn(move || {
            let reader = BufReader::new(stdout);
            for line in reader.lines().map_while(Result::ok) {
                processor(
                    line,
                    "stdout",
                    &app_handle_clone,
                    &backend_id_clone,
                    &process_id_clone,
                );
            }
        }))
    } else {
        None
    };

    let _stderr_thread = if let Some(stderr) = child.stderr.take() {
        let app_handle_clone = app_handle.clone();
        let backend_id_clone = backend.id.clone();
        let process_id_clone = process_id.clone();
        Some(std::thread::spawn(move || {
            let reader = BufReader::new(stderr);
            for line in reader.lines().map_while(Result::ok) {
                log_processor(
                    line,
                    "stderr",
                    &app_handle_clone,
                    &backend_id_clone,
                    &process_id_clone,
                );
            }
        }))
    } else {
        None
    };

    // Store the running backend in the process monitoring system
    if let Some(processes) = app_handle.try_state::<RunningProcesses>() {
        if let Err(e) = processes.add_process(backend.id.clone(), child) {
            log::error!("Failed to add backend to process tracking: {e}");
            return Err(format!("Failed to track backend process: {e}"));
        }
        log::debug!("Backend {} added to process tracking", backend.id);
    } else {
        log::warn!(
            "RunningProcesses state not available, backend will not be tracked for auto-cleanup"
        );
    }

    // CRITICAL: Reload config from disk before updating runtime state.
    // This prevents a race condition where a separate settings update
    // could be overwritten by this startup process.
    let mut backends = load_backends_config(&fs, &env_sys)?;
    let final_backend_state;

    if let Some(backend_config) = backends.iter_mut().find(|b| b.id == id) {
        // Update runtime state on the fresh config object
        backend_config.status = BackendStatus::Running.to_string();
        backend_config.pid = Some(process_pid);
        backend_config.started_at = Some(Utc::now().to_rfc3339());
        backend_config.error = None;

        // The host/port/url are discovered asynchronously by the log reader threads.
        // We do not touch them here.

        final_backend_state = backend_config.clone();
    } else {
        return Err(format!(
            "Backend with id {id} not found in config after start"
        ));
    }

    // Save the updated state
    save_backends_config(&backends, &fs, &env_sys, &file_ext)?;

    if let Err(e) = app_handle.emit(
        "boolean-message",
        Payload {
            message: "true".to_string(),
        },
    ) {
        log::error!("Failed to emit boolean-message event: {e}");
    }

    Ok(final_backend_state)
}

/// List all backend services
pub fn list_backend_services_impl<F: FileSystem, E: EnvSystem>(
    fs: &F,
    env_sys: &E,
) -> Result<Vec<BackendService>, String> {
    let backends = load_backends_config(fs, env_sys).unwrap_or_default();

    Ok(backends)
}

#[tauri::command]
pub fn list_backend_services() -> Result<Vec<BackendService>, String> {
    list_backend_services_impl(&RealFileSystem, &RealEnvSystem)
}

/// Create a new backend service
pub fn create_backend_service_impl<F: FileSystem, E: EnvSystem, FE: FileExtTrait>(
    backend: BackendService,
    fs: &F,
    env_sys: &E,
    file_ext: &FE,
) -> Result<BackendService, String> {
    let mut backends = load_backends_config(fs, env_sys)?;

    // Validate required fields
    if backend.name.is_empty() {
        return Err("Backend name is required".to_string());
    }
    if backend.command.is_empty() {
        return Err("Command is required".to_string());
    }
    if backend.environment.is_empty() {
        return Err("Environment is required".to_string());
    }
    // Check for duplicate name
    if backends.iter().any(|b| b.name == backend.name) {
        return Err("A backend with this name already exists".to_string());
    }

    if let Err(validation_error) = validate_command_input(&backend.command, fs, env_sys) {
        return Err(format!("Invalid command: {}", validation_error));
    }

    // Create new backend with defaults
    let mut new_backend = backend;
    new_backend.id = Uuid::new_v4().to_string();
    new_backend.status = BackendStatus::Stopped.to_string();
    new_backend.pid = None;
    new_backend.url = None;
    new_backend.started_at = None;

    // Add to config and save
    backends.push(new_backend.clone());
    save_backends_config(&backends, fs, env_sys, file_ext)?;

    Ok(new_backend)
}

#[tauri::command]
pub fn create_backend_service(backend: BackendService) -> Result<BackendService, String> {
    create_backend_service_impl(backend, &RealFileSystem, &RealEnvSystem, &RealFileExtTrait)
}

/// Update a backend service
pub async fn update_backend_service_impl<
    F: FileSystem + Send + Sync + 'static + Clone + Copy,
    E: EnvSystem + Send + Sync + 'static + Clone + Copy,
    FE: FileExtTrait + Send + Sync + 'static + Clone + Copy,
>(
    backend: BackendService,
    fs: F,
    env_sys: E,
    file_ext: FE,
) -> Result<BackendService, String> {
    let mut backends = load_backends_config(&fs, &env_sys)?;

    // Find existing backend
    let index = backends
        .iter()
        .position(|b| b.id == backend.id)
        .ok_or_else(|| "Backend not found".to_string())?;

    let old_backend = &mut backends[index];

    // Validate command if it's being updated
    if !backend.command.is_empty()
        && let Err(validation_error) = validate_command_input(&backend.command, &fs, &env_sys)
    {
        return Err(format!("Invalid command: {}", validation_error));
    }

    // Apply changes from the incoming backend object to the existing configuration.
    // This preserves any fields that weren't sent in the update request.
    old_backend.name = backend.name;
    old_backend.command = backend.command;
    old_backend.environment = backend.environment;
    old_backend.auto_start = backend.auto_start;
    old_backend.error = backend.error;

    // Only update optional fields if they are provided in the request.
    // This prevents erasing existing values with `None` if the frontend
    // sends a partial update (e.g., just updating the name shouldn't clear envVars).
    if backend.working_directory.is_some() {
        old_backend.working_directory = backend.working_directory;
    }
    if backend.env_file.is_some() {
        old_backend.env_file = backend.env_file;
    }
    if backend.env_vars.is_some() {
        old_backend.env_vars = backend.env_vars;
    }
    if backend.host.is_some() {
        old_backend.host = backend.host;
    }
    if backend.port.is_some() {
        old_backend.port = backend.port;
    }
    if backend.url.is_some() {
        old_backend.url = backend.url;
    }

    let result_backend = old_backend.clone();

    // Save the updated configuration
    save_backends_config(&backends, &fs, &env_sys, &file_ext)?;

    // Return the updated backend configuration.
    // The server is NOT restarted. The new settings will apply on next manual start.
    Ok(result_backend)
}

#[tauri::command]
pub async fn update_backend_service(backend: BackendService) -> Result<BackendService, String> {
    update_backend_service_impl(backend, RealFileSystem, RealEnvSystem, RealFileExtTrait).await
}

/// Delete a backend service
pub async fn delete_backend_service_impl<F: FileSystem, E: EnvSystem, FE: FileExtTrait>(
    app_handle: tauri::AppHandle,
    id: String,
    fs: &F,
    env_sys: &E,
    file_ext: &FE,
) -> Result<(), String> {
    let mut backends = load_backends_config(fs, env_sys)?;

    // Find the backend
    let index = backends
        .iter()
        .position(|b| b.id == id)
        .ok_or_else(|| "Backend not found".to_string())?;

    let backend = backends[index].clone();

    // Stop if running
    if backend.status == "running" {
        stop_backend_service(app_handle, id.clone()).await?;
    }

    // Remove from config
    backends.remove(index);
    save_backends_config(&backends, fs, env_sys, file_ext)?;

    Ok(())
}

#[tauri::command]
pub async fn delete_backend_service(
    app_handle: tauri::AppHandle,
    id: String,
) -> Result<(), String> {
    delete_backend_service_impl(
        app_handle,
        id,
        &RealFileSystem,
        &RealEnvSystem,
        &RealFileExtTrait,
    )
    .await
}

/// Stop all running backend services
pub async fn stop_all_backend_services<F: FileSystem, E: EnvSystem, FE: FileExtTrait>(
    app_handle: tauri::AppHandle,
    fs: &F,
    env_sys: &E,
    file_ext: &FE,
) -> Result<(), String> {
    let backends = load_backends_config(fs, env_sys)?;

    log::debug!(
        "Stopping all backend services ({} configured backends)",
        backends.len()
    );

    let mut stop_errors = Vec::new();

    for backend in backends {
        if backend.status == "running" || backend.status == "starting" {
            log::debug!("Stopping backend: {}", backend.name);

            match stop_backend_service_impl(app_handle.clone(), backend.id, fs, env_sys, file_ext)
                .await
            {
                Ok(_) => log::debug!("Successfully stopped backend: {}", backend.name),
                Err(e) => {
                    let error_msg = format!("Failed to stop backend {}: {}", backend.name, e);
                    log::debug!("{error_msg}");
                    stop_errors.push(error_msg);
                }
            }
        }
    }

    if !stop_errors.is_empty() {
        return Err(format!(
            "Failed to stop some backends: {}",
            stop_errors.join("; ")
        ));
    }

    log::debug!("Successfully stopped all backend services");
    Ok(())
}

pub async fn initialize_backends<
    F: FileSystem + Send + Sync + 'static + Clone + Copy,
    E: EnvSystem + Send + Sync + 'static + Clone + Copy,
    FE: FileExtTrait + Send + Sync + 'static + Clone + Copy,
>(
    app_handle: &AppHandle,
    fs: F,
    env_sys: E,
    file_ext: FE,
) -> Result<(), String> {
    log::debug!("Initializing backend services on application startup");
    // Load backends
    let mut backends = load_backends_config(&fs, &env_sys)?;
    let mut modified = false;

    // Reset running state for all backends on startup
    for backend in &mut backends {
        if backend.status == "running" {
            let pid_running = match backend.pid {
                Some(pid) => is_process_running(pid, &env_sys),
                None => false,
            };

            if !pid_running {
                log::debug!(
                    "Backend {} was marked as running but process is not active, updating status",
                    backend.name
                );
                backend.status = BackendStatus::Stopped.to_string();
                backend.pid = None;
                backend.url = None;
                backend.host = None;
                backend.port = None;
                modified = true;
            }
        }
    }

    // Save updated status
    if modified {
        save_backends_config(&backends, &fs, &env_sys, &file_ext)?;
    }

    // Auto-start configured backends
    for backend in backends.iter() {
        if backend.auto_start && backend.status == BackendStatus::Stopped.to_string() {
            log::debug!("Auto-starting backend: {}", backend.name);

            if let Err(validation_error) = validate_command_input(&backend.command, &fs, &env_sys) {
                log::error!(
                    "Skipping auto-start of backend '{}' due to dangerous command: {}",
                    backend.name,
                    validation_error
                );

                // Update backend status to error
                let mut backends_to_update = load_backends_config(&fs, &env_sys)?;
                if let Some(backend_config) =
                    backends_to_update.iter_mut().find(|b| b.id == backend.id)
                {
                    backend_config.status = BackendStatus::Error.to_string();
                    backend_config.error = Some(format!(
                        "Backend could not be started -> {}",
                        validation_error
                    ));
                }
                if let Err(e) = save_backends_config(&backends_to_update, &fs, &env_sys, &file_ext)
                {
                    log::error!("Failed to save backend error status: {}", e);
                }
                continue; // Skip this backend
            }

            // Start the backend - the start_backend_service function will save the real PID, URL and port
            match start_backend_service_impl(
                app_handle.clone(),
                backend.id.clone(),
                fs,
                env_sys,
                file_ext,
            )
            .await
            {
                Ok(_) => log::debug!("Successfully auto-started backend: {}", backend.name),
                Err(e) => log::error!("Failed to auto-start backend '{}': {}", backend.name, e),
            }

            // Add a small delay between starting backends
            std::thread::sleep(std::time::Duration::from_millis(500));
        }
    }

    log::debug!("Backend services initialized");
    Ok(())
}

/// Open backend logs window
#[tauri::command]
pub async fn open_backend_logs_window(
    app_handle: tauri::AppHandle,
    id: String,
) -> Result<(), String> {
    // Create a window label with the backend id for uniqueness
    let window_label = format!("backend-logs-{id}");
    // Check if the window already exists, and focus it if it does
    if let Some(existing_window) = app_handle.get_webview_window(&window_label) {
        existing_window.show().map_err(|e| e.to_string())?;
        existing_window.set_focus().map_err(|e| e.to_string())?;
        return Ok(());
    }
    let backends = load_backends_config(&RealFileSystem, &RealEnvSystem)?;
    let backend_name = backends
        .iter()
        .find(|b| b.id == id)
        .map(|b| b.name.clone())
        .unwrap_or_else(|| id.clone());
    // Create a new window with the backend id in the URL parameters
    #[allow(unused_mut)]
    let mut builder = tauri::WebviewWindowBuilder::new(
        &app_handle,
        &window_label,
        tauri::WebviewUrl::App(format!("/backend-logs?id={id}").into()),
    )
    .title(format!("Open Data Platform: {backend_name} Logs"))
    .inner_size(1000.0, 600.0)
    .resizable(true)
    .center()
    .min_inner_size(600.0, 200.0)
    .visible(true);

    #[cfg(target_os = "macos")]
    {
        builder = builder.title_bar_style(tauri::TitleBarStyle::Transparent);
    }

    let log_viewer_window = builder
        .build()
        .map_err(|e| format!("Failed to create log viewer window: {e}"))?;

    // Show and focus the newly created window
    log_viewer_window
        .show()
        .map_err(|e| format!("Failed to show log viewer window: {e}"))?;
    log_viewer_window
        .set_focus()
        .map_err(|e| format!("Failed to focus log viewer window: {e}"))?;

    if let Some(window) = app_handle.get_webview_window(&window_label) {
        let window_clone = window.clone();
        window.on_window_event(move |event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                window_clone.hide().unwrap();
                api.prevent_close();
            }
        });
        // This sets the titlebar color as black in macOS
        #[cfg(target_os = "macos")]
        {
            use objc2_app_kit::{NSColor, NSWindow};
            let ns_window_ptr = window.ns_window().unwrap();
            let ns_window = unsafe { &*(ns_window_ptr as *mut NSWindow) };
            let bg_color = { NSColor::colorWithRed_green_blue_alpha(0.0, 0.0, 0.0, 1.0) };
            ns_window.setBackgroundColor(Some(&bg_color));
        };
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::tauri_handlers::helpers::{MockEnvSystem, MockFileExtTrait};
    use std::collections::HashMap;
    use std::env::VarError;
    use std::io::{Cursor, Read, Write};
    use std::path::{Path, PathBuf};
    use std::sync::{Arc, Mutex};

    // In-memory file system for robust, path-agnostic mocking
    #[derive(Clone)]
    struct InMemoryFS {
        files: Arc<Mutex<HashMap<PathBuf, String>>>,
        temp_file_path: PathBuf,
    }

    impl InMemoryFS {
        fn new() -> Self {
            let temp_dir = std::env::temp_dir();
            let temp_file_path = temp_dir.join(format!(
                "test_backend_{}.json",
                std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap()
                    .as_nanos()
            ));
            Self {
                files: Arc::new(Mutex::new(HashMap::new())),
                temp_file_path,
            }
        }
    }

    impl crate::tauri_handlers::helpers::FileSystem for InMemoryFS {
        fn is_dir(&self, _path: &Path) -> bool {
            false
        }
        fn is_file(&self, path: &str) -> bool {
            let files = self.files.lock().unwrap();
            files.contains_key(&PathBuf::from(path))
        }
        fn create_file(&self, path: &str) -> Result<Box<dyn Write>, String> {
            let files = self.files.clone();
            let path = PathBuf::from(path);
            Ok(Box::new(InMemoryWriter { files, path }))
        }
        fn remove_file(&self, path: &str) -> std::io::Result<()> {
            self.files.lock().unwrap().remove(&PathBuf::from(path));
            Ok(())
        }
        fn create_dir_all(&self, _path: &Path) -> std::io::Result<()> {
            Ok(())
        }
        fn remove_dir_all(&self, _path: &Path) -> std::io::Result<()> {
            Ok(())
        }
        fn exists(&self, path: &Path) -> bool {
            if path.ends_with("backends.json") {
                return self.temp_file_path.exists()
                    || self.files.lock().unwrap().contains_key(path);
            }
            self.files.lock().unwrap().contains_key(path)
        }
        fn write(&self, path: &Path, contents: &str) -> std::io::Result<()> {
            self.files
                .lock()
                .unwrap()
                .insert(path.to_path_buf(), contents.to_string());
            Ok(())
        }
        fn read_to_string(&self, path: &Path) -> std::io::Result<String> {
            if path.ends_with("backends.json") && self.temp_file_path.exists() {
                return std::fs::read_to_string(&self.temp_file_path);
            }
            self.files
                .lock()
                .unwrap()
                .get(path)
                .cloned()
                .ok_or_else(|| std::io::Error::new(std::io::ErrorKind::NotFound, "not found"))
        }
        fn open_rw_create(&self, path: &Path) -> std::io::Result<std::fs::File> {
            if path.ends_with("backends.json") {
                std::fs::File::create(&self.temp_file_path)
            } else {
                unimplemented!("open_rw_create is only mocked for backends.json")
            }
        }
        fn open_ro(&self, path: &Path) -> std::io::Result<Box<dyn Read>> {
            if path.ends_with("backends.json") && self.temp_file_path.exists() {
                return std::fs::File::open(&self.temp_file_path)
                    .map(|f| Box::new(f) as Box<dyn Read>);
            }
            let files = self.files.lock().unwrap();
            let data = files.get(path).cloned().unwrap_or_default().into_bytes();
            Ok(Box::new(Cursor::new(data)))
        }
        fn set_len(&self, _file: &std::fs::File, _len: u64) -> std::io::Result<()> {
            Ok(())
        }
        fn flush(&self, _file: &mut std::fs::File) -> std::io::Result<()> {
            Ok(())
        }
        fn metadata(&self, _path: &Path) -> std::io::Result<std::fs::Metadata> {
            // This is a mock implementation. We need to return a valid Metadata object.
            // We can create a temporary file, get its metadata, and then delete it.
            // This is a bit of a hack, but it's a simple way to get a valid Metadata object.
            let temp_dir = std::env::temp_dir();
            let temp_file_path = temp_dir.join("mock_metadata");
            std::fs::File::create(&temp_file_path)?;
            let metadata = std::fs::metadata(&temp_file_path)?;
            std::fs::remove_file(&temp_file_path)?;
            Ok(metadata)
        }
        fn set_permissions(
            &self,
            _path: &Path,
            _perm: std::fs::Permissions,
        ) -> std::io::Result<()> {
            Ok(())
        }
        fn read_dir(&self, _path: &Path) -> Result<Vec<PathBuf>, std::io::Error> {
            Ok(vec![])
        }
        fn is_empty(&self, path: &Path) -> Result<bool, std::io::Error> {
            self.files
                .lock()
                .unwrap()
                .get(path)
                .map_or(Ok(true), |content| Ok(content.is_empty()))
        }
    }

    struct InMemoryWriter {
        files: Arc<Mutex<HashMap<PathBuf, String>>>,
        path: PathBuf,
    }

    impl Write for InMemoryWriter {
        fn write(&mut self, buf: &[u8]) -> std::io::Result<usize> {
            let mut files = self.files.lock().unwrap();
            let entry = files.entry(self.path.clone()).or_default();
            entry.push_str(&String::from_utf8_lossy(buf));
            Ok(buf.len())
        }
        fn flush(&mut self) -> std::io::Result<()> {
            Ok(())
        }
    }

    fn mock_env() -> MockEnvSystem {
        let mut mock_env = MockEnvSystem::new();
        mock_env
            .expect_var()
            .withf(|var| var == "HOME" || var == "APPDATA")
            .returning(|_| {
                Ok(if cfg!(windows) {
                    r"C:\mock\home".to_string()
                } else {
                    "/mock/home".to_string()
                })
            });
        mock_env
            .expect_var()
            .withf(|var| var == "OPENBB_PLATFORM_INSTALL_DIR")
            .returning(|_| Err(VarError::NotPresent));
        mock_env
            .expect_consts_os()
            .returning(|| if cfg!(windows) { "windows" } else { "unix" });
        mock_env.expect_temp_dir().returning(|| {
            if cfg!(windows) {
                PathBuf::from(r"C:\mock\tmp")
            } else {
                PathBuf::from("/mock/tmp")
            }
        });
        mock_env
    }

    #[test]
    fn test_create_backend_service_impl() {
        let fs = InMemoryFS::new();
        let mock_env = mock_env();
        let mut mock_file_ext = MockFileExtTrait::new();
        mock_file_ext
            .expect_try_lock_exclusive()
            .returning(|_| Ok(()));
        mock_file_ext.expect_unlock().returning(|_| Ok(()));

        let backend = BackendService {
            name: "TestBackend".to_string(),
            command: "python test.py".to_string(),
            environment: "base".to_string(),
            ..Default::default()
        };

        let created = create_backend_service_impl(backend, &fs, &mock_env, &mock_file_ext).unwrap();
        assert_eq!(created.name, "TestBackend");
        assert_eq!(created.status, "stopped");
        assert!(!created.id.is_empty());
    }

    #[test]
    fn test_create_backend_service_duplicate_name() {
        let fs = InMemoryFS::new();
        let mock_env = mock_env();
        let mut mock_file_ext = MockFileExtTrait::new();
        mock_file_ext
            .expect_try_lock_exclusive()
            .returning(|_| Ok(()));
        mock_file_ext.expect_unlock().returning(|_| Ok(()));

        let backend = BackendService {
            name: "TestBackend".to_string(),
            command: "python test.py".to_string(),
            environment: "base".to_string(),
            ..Default::default()
        };

        // First creation should succeed
        let created = create_backend_service_impl(backend.clone(), &fs, &mock_env, &mock_file_ext);
        assert!(created.is_ok());

        // Second creation with the same name should fail
        let result = create_backend_service_impl(backend, &fs, &mock_env, &mock_file_ext);
        assert!(
            result.is_err(),
            "Expected error for duplicate backend name, got {result:?}"
        );
        assert_eq!(
            result.unwrap_err(),
            "A backend with this name already exists"
        );
    }

    #[test]
    fn test_load_env_file_parsing() {
        struct DummyFS;
        impl crate::tauri_handlers::helpers::FileSystem for DummyFS {
            fn read_to_string(&self, _path: &Path) -> std::io::Result<String> {
                Ok("FOO=bar\nBAR=\"baz\"\n# Comment\nQUOTED='quux'\n".to_string())
            }
            fn open_ro(&self, _path: &Path) -> std::io::Result<Box<dyn Read>> {
                Ok(Box::new(Cursor::new(
                    "FOO=bar\nBAR=\"baz\"\n# Comment\nQUOTED='quux'\n"
                        .as_bytes()
                        .to_vec(),
                )))
            }
            // All other methods can be left unimplemented for this test
            fn is_dir(&self, _path: &Path) -> bool {
                false
            }
            fn is_file(&self, _path: &str) -> bool {
                false
            }
            fn create_file(&self, _path: &str) -> Result<Box<dyn Write>, String> {
                unimplemented!()
            }
            fn remove_file(&self, _path: &str) -> std::io::Result<()> {
                Ok(())
            }
            fn create_dir_all(&self, _path: &Path) -> std::io::Result<()> {
                Ok(())
            }
            fn remove_dir_all(&self, _path: &Path) -> std::io::Result<()> {
                Ok(())
            }
            fn exists(&self, _path: &Path) -> bool {
                false
            }
            fn write(&self, _path: &Path, _contents: &str) -> std::io::Result<()> {
                Ok(())
            }
            fn open_rw_create(&self, _path: &Path) -> std::io::Result<std::fs::File> {
                unimplemented!("Not needed for this test")
            }
            fn set_len(&self, _file: &std::fs::File, _len: u64) -> std::io::Result<()> {
                Ok(())
            }
            fn flush(&self, _file: &mut std::fs::File) -> std::io::Result<()> {
                Ok(())
            }
            fn metadata(&self, _path: &Path) -> std::io::Result<std::fs::Metadata> {
                unimplemented!("Not needed for this test")
            }
            fn set_permissions(
                &self,
                _path: &Path,
                _perm: std::fs::Permissions,
            ) -> std::io::Result<()> {
                Ok(())
            }
            fn read_dir(&self, _path: &Path) -> Result<Vec<PathBuf>, std::io::Error> {
                Ok(vec![])
            }
            fn is_empty(&self, _path: &std::path::Path) -> std::io::Result<bool> {
                Ok(true)
            }
        }
        let fs = DummyFS;
        let vars = load_env_file::<DummyFS>("dummy.env", &fs).unwrap();
        assert_eq!(vars.get("FOO"), Some(&"bar".to_string()));
        assert_eq!(vars.get("BAR"), Some(&"baz".to_string()));
        assert_eq!(vars.get("QUOTED"), Some(&"quux".to_string()));
    }

    #[test]
    fn test_backend_status_enum() {
        assert_eq!(BackendStatus::Running.to_string(), "running");
        assert_eq!(BackendStatus::Stopped.to_string(), "stopped");
        assert_eq!(BackendStatus::Starting.to_string(), "starting");
        assert_eq!(BackendStatus::Stopping.to_string(), "stopping");
        assert_eq!(BackendStatus::Error.to_string(), "error");
    }

    #[test]
    fn test_save_backends_config_serialization() {
        let fs = InMemoryFS::new();
        let mock_env = mock_env();
        let mut mock_file_ext = MockFileExtTrait::new();
        mock_file_ext
            .expect_try_lock_exclusive()
            .returning(|_| Ok(()));
        mock_file_ext.expect_unlock().returning(|_| Ok(()));

        let backends = vec![BackendService {
            name: "TestBackend".to_string(),
            command: "python test.py".to_string(),
            environment: "base".to_string(),
            ..Default::default()
        }];

        let result = save_backends_config(&backends, &fs, &mock_env, &mock_file_ext);
        assert!(result.is_ok());
    }

    #[test]
    fn test_is_process_running_unix_and_windows() {
        let mut mock_env = MockEnvSystem::new();

        #[cfg(unix)]
        {
            use std::process::Command;
            mock_env
                .expect_new_command()
                .with(mockall::predicate::eq("kill"))
                .returning(|_| {
                    // always fails
                    Command::new("false")
                });
            assert!(!is_process_running(12345, &mock_env));
        }
        #[cfg(windows)]
        {
            use std::process::Command;
            // Mock tasklist to return a command that will fail to execute.
            mock_env
                .expect_new_command()
                .with(mockall::predicate::eq("tasklist"))
                .returning(|_| Command::new("this_command_should_not_exist"));
            assert!(!is_process_running(12345, &mock_env));
        }
    }

    #[test]
    fn test_list_backend_services_impl() {
        let fs = InMemoryFS::new();
        let mock_env = mock_env();
        let mut mock_file_ext = MockFileExtTrait::new();
        mock_file_ext
            .expect_try_lock_exclusive()
            .returning(|_| Ok(()));
        mock_file_ext.expect_unlock().returning(|_| Ok(()));

        // Prepare a backend and save it
        let backend = BackendService {
            name: "TestBackend".to_string(),
            command: "python test.py".to_string(),
            environment: "base".to_string(),
            ..Default::default()
        };
        // Save the backend to the config
        let _ = create_backend_service_impl(backend.clone(), &fs, &mock_env, &mock_file_ext);

        // Now list backends
        let backends = list_backend_services_impl(&fs, &mock_env).unwrap();
        assert_eq!(backends.len(), 1);
        assert_eq!(backends[0].name, "TestBackend");
        assert_eq!(backends[0].command, "python test.py");
        assert_eq!(backends[0].environment, "base");
    }
}
