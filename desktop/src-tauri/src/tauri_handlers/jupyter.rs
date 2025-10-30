use super::helpers::{EnvSystem, RealEnvSystem};
use once_cell::sync::Lazy;
use std::collections::HashMap;
use std::sync::Mutex;
use tauri::Emitter;
use tauri::Manager;

// Storage for active Jupyter processes and their URLs
static ACTIVE_JUPYTER_SERVERS: Lazy<Mutex<HashMap<String, (String, u32)>>> =
    Lazy::new(|| Mutex::new(HashMap::new()));

// Function to extract Jupyter URL with token from stdout
fn extract_jupyter_url(output: &str) -> Option<String> {
    // More comprehensive URL detection patterns
    let patterns = [
        regex::Regex::new(r"(https?://[^\s]+token=[^\s]+)").unwrap(),
        regex::Regex::new(r"(https?://(?:localhost|127\.0\.0\.1):[0-9]+[^\s]*)").unwrap(),
        regex::Regex::new(r"(http://[^:\s]+:[0-9]+[^\s]*)").unwrap(),
    ];

    for pattern in &patterns {
        if let Some(cap) = pattern.captures(output)
            && let Some(url_match) = cap.get(1)
        {
            let url = url_match.as_str().to_string();
            // Clean up the URL by removing any trailing characters
            let clean_url = url
                .trim_end_matches(&['.', ',', ')', ']', '}'][..])
                .to_string();
            return Some(clean_url);
        }
    }
    None
}

pub async fn start_jupyter_server_impl<R: tauri::Runtime, E: EnvSystem>(
    app_handle: tauri::AppHandle<R>,
    environment: String,
    directory: String,
    working: String,
    env_sys: &E,
) -> Result<serde_json::Value, String> {
    use std::path::Path;
    use std::process::Stdio;

    log::debug!("Starting Jupyter server for environment: {environment}"); // Check if server is already running
    let already_running_url = {
        let servers = ACTIVE_JUPYTER_SERVERS.lock().unwrap();
        servers.get(&environment).map(|(url, _)| url.clone())
    };

    // Return early if already running
    if let Some(url) = already_running_url {
        log::debug!("Jupyter server already running with URL: {url}");
        return Ok(serde_json::json!({
            "url": url,
            "already_running": true,
            "status": "running"
        }));
    }
    let conda_dir = Path::new(&directory).join("conda");
    let parent_dir = conda_dir
        .parent()
        .ok_or("Could not get parent directory of conda_dir")?;
    let jupyter_parent = parent_dir.join("Jupyter");

    let conda_exe = if env_sys.consts_os() == "windows" {
        conda_dir.join("Scripts").join("conda.exe")
    } else {
        conda_dir.join("bin").join("conda")
    };

    let mut process_builder = env_sys.new_conda_command(&conda_exe, &conda_dir);

    process_builder.args([
        "run",
        "-n",
        &environment,
        "--no-capture-output",
        "jupyter",
        "lab",
        "--no-browser",
        "--notebook-dir",
        &working,
    ]);

    process_builder
        .env("JUPYTER_CONFIG_DIR", jupyter_parent.join("jupyter_config"))
        .env("JUPYTER_DATA_DIR", jupyter_parent.join("jupyter_data"))
        .env(
            "JUPYTER_RUNTIME_DIR",
            jupyter_parent.join("jupyter_runtime"),
        );
    // Launch the Jupyter process
    let mut process = match process_builder
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
    {
        Ok(p) => p,
        Err(e) => {
            return Err(format!("Failed to start Jupyter process: {e}"));
        }
    }; // Create a unique identifier for the process logs
    let process_log_id = format!("jupyter-{environment}");

    // Register the process for monitoring with the process monitor system
    crate::utils::process_monitor::register_process(&crate::get_log_storage(), &process_log_id);

    // Get the process ID before we lose access to the process
    let process_id = process.id();

    log::debug!("Started Jupyter process with PID: {process_id} - giving to process monitor");

    // Give the process to the process monitor to handle I/O
    let (tx_sender, mut tx_receiver) = tokio::sync::mpsc::channel::<String>(100);

    // Capture stdout and stderr manually since process monitor might not do what we need
    if let Some(stdout) = process.stdout.take() {
        let reader = std::io::BufReader::new(stdout);
        let process_id_clone = process_log_id.clone();
        let log_storage = crate::get_log_storage();
        let tx_sender_clone = tx_sender.clone();
        let app_handle_clone = app_handle.clone();

        std::thread::spawn(move || {
            use std::io::BufRead;
            for line in reader.lines().map_while(Result::ok) {
                log::debug!("JUPYTER STDOUT: {line}");

                // Send to channel for URL detection
                let _ = tx_sender_clone.blocking_send(line.clone());

                // Store in process monitor
                let timestamp = chrono::Utc::now().timestamp_millis();
                let entry = crate::utils::process_monitor::LogEntry {
                    timestamp,
                    content: line.clone(),
                    process_id: process_id_clone.clone(),
                };

                if let Ok(mut storage) = log_storage.lock()
                    && let Some(buffer) = storage.get_mut(&process_id_clone)
                {
                    buffer.add(entry);
                }

                // Emit event
                let payload = serde_json::json!({
                    "processId": process_id_clone,
                    "output": line,
                    "timestamp": timestamp
                });
                let _ = app_handle_clone.emit("process-output", payload);
            }
        });
    }

    if let Some(stderr) = process.stderr.take() {
        let reader = std::io::BufReader::new(stderr);
        let process_id_clone = process_log_id.clone();
        let log_storage = crate::get_log_storage();
        let tx_sender_clone = tx_sender.clone();
        let app_handle_clone = app_handle.clone();

        std::thread::spawn(move || {
            use std::io::BufRead;
            for line in reader.lines().map_while(Result::ok) {
                log::debug!("JUPYTER STDERR: {line}");
                // Send to channel for URL detection
                let _ = tx_sender_clone.blocking_send(line.clone());

                // Store in process monitor
                let timestamp = chrono::Utc::now().timestamp_millis();
                let entry = crate::utils::process_monitor::LogEntry {
                    timestamp,
                    content: line.clone(),
                    process_id: process_id_clone.clone(),
                };

                if let Ok(mut storage) = log_storage.lock()
                    && let Some(buffer) = storage.get_mut(&process_id_clone)
                {
                    buffer.add(entry);
                }

                // Emit event
                let payload = serde_json::json!({
                    "processId": process_id_clone,
                    "output": line,
                    "timestamp": timestamp
                });
                let _ = app_handle_clone.emit("process-output", payload);
            }
        });
    } // Wait for Jupyter to start and extract the URL from our channel
    let mut jupyter_url = String::new();
    let timeout = std::time::Duration::from_secs(30);
    let start_time = std::time::Instant::now();

    log::debug!("Waiting for Jupyter server URL...");

    while start_time.elapsed() < timeout {
        match tx_receiver.recv().await {
            Some(line) => {
                log::debug!("Jupyter output: {}", line.trim());
                if let Some(url) = extract_jupyter_url(&line) {
                    jupyter_url = url;
                    log::debug!("Found Jupyter URL: {jupyter_url}");
                    break;
                }

                // Also check for simple http URLs
                if let Some(url_start) = line.find("http://") {
                    let url: String = line[url_start..]
                        .split_whitespace()
                        .next()
                        .unwrap_or_default()
                        .to_string();

                    if url.contains("localhost") && (url.contains("lab") || url.contains("8888")) {
                        jupyter_url = url;
                        log::debug!("Found Jupyter URL: {jupyter_url}");
                        break;
                    }
                }
            }
            None => break,
        }
    }
    if !jupyter_url.is_empty() {
        // Store the URL and process ID for this environment
        {
            let mut servers = ACTIVE_JUPYTER_SERVERS.lock().unwrap();
            servers.insert(environment.clone(), (jupyter_url.clone(), process_id));
        }

        log::debug!("Jupyter server started successfully with URL: {jupyter_url}");

        Ok(serde_json::json!({
            "url": jupyter_url,
            "already_running": false,
            "status": "running",
            "process_id": process_id
        }))
    } else {
        // Kill the process if we didn't find a URL
        let _ = process.kill();
        Err("Failed to get Jupyter server URL within timeout period - check logs".to_string())
    }
}

#[tauri::command]
pub async fn start_jupyter_server<R: tauri::Runtime>(
    app_handle: tauri::AppHandle<R>,
    environment: String,
    directory: String,
    working: String,
) -> Result<serde_json::Value, String> {
    start_jupyter_server_impl(app_handle, environment, directory, working, &RealEnvSystem).await
}

#[tauri::command]
pub async fn stop_all_jupyter_servers<R: tauri::Runtime>(
    app_handle: tauri::AppHandle<R>,
) -> Result<bool, String> {
    log::debug!("Stopping all active Jupyter servers");

    let environments: Vec<String>;

    // Scope to limit the lock duration
    {
        let active_servers = match ACTIVE_JUPYTER_SERVERS.lock() {
            Ok(s) => s,
            Err(_) => return Err("Failed to acquire server lock".to_string()),
        };
        environments = active_servers.keys().cloned().collect();
    }

    for env in environments {
        log::debug!("Stopping Jupyter server for environment: {env}");
        match stop_jupyter_server_impl(app_handle.clone(), env.clone(), &RealEnvSystem).await {
            Ok(_) => log::debug!("Successfully stopped Jupyter server for environment: {env}"),
            Err(e) => log::error!("Error stopping Jupyter server for environment {env}: {e}"),
        }
    }

    Ok(true)
}

pub async fn stop_jupyter_server_impl<R: tauri::Runtime, E: EnvSystem>(
    app_handle: tauri::AppHandle<R>,
    environment: String,
    env_sys: &E,
) -> Result<bool, String> {
    log::debug!("Stopping Jupyter server for environment: {environment}");

    // Get the URL and PID from tracking and remove it
    let (jupyter_url, process_id) = {
        let mut servers = match ACTIVE_JUPYTER_SERVERS.lock() {
            Ok(s) => s,
            Err(_) => return Err("Failed to acquire server lock".to_string()),
        };

        match servers.remove(&environment) {
            Some((url, pid)) => (url, pid),
            None => {
                return Err(format!(
                    "No active Jupyter server found for environment: {environment}"
                ));
            }
        }
    };
    log::debug!("Found Jupyter server with PID {process_id} and URL: {jupyter_url}");
    let port = match extract_port_from_url(&jupyter_url) {
        Some(p) => p,
        None => {
            return Err(format!(
                "Could not extract port from Jupyter URL: {jupyter_url}. Cannot stop server without port."
            ));
        }
    };

    let kill_success = if env_sys.consts_os() == "windows" {
        log::debug!("🎯 Targeting Jupyter on port {port} (Windows)");
        // Use netstat to find the exact PID using this port
        let netstat_result = env_sys
            .new_command("cmd")
            .args([
                "/c",
                &format!("netstat -ano | findstr :{port} | findstr LISTENING"),
            ])
            .output();

        match netstat_result {
            Ok(output) => {
                let netstat_output = String::from_utf8_lossy(&output.stdout);

                let mut killed_any = false;
                for line in netstat_output.lines() {
                    let parts: Vec<&str> = line.split_whitespace().collect();
                    if let Some(pid_str) = parts.last()
                        && let Ok(pid) = pid_str.parse::<u32>()
                    {
                        log::debug!("🎯 Found PID {pid} using port {port}, terminating...");
                        // Kill this specific PID
                        let kill_result = env_sys
                            .new_command("taskkill")
                            .args(["/F", "/PID", &pid.to_string()])
                            .output();

                        match kill_result {
                            Ok(kill_output) => {
                                if kill_output.status.success() {
                                    log::debug!("✅ Successfully terminated Jupyter PID {pid}");
                                    killed_any = true;
                                } else {
                                    let stderr = String::from_utf8_lossy(&kill_output.stderr);
                                    log::warn!("Failed to kill PID {pid}: {stderr}");
                                }
                            }
                            Err(e) => {
                                log::error!("Failed to execute taskkill for PID {pid}: {e}")
                            }
                        }
                    }
                }
                killed_any
            }
            Err(e) => {
                log::error!("Failed to execute netstat: {e}");
                false
            }
        }
    } else {
        log::debug!("🎯 Targeting Jupyter on port {port} (Unix)");

        // Use lsof to find processes using this port, specifically listening TCP
        let lsof_result = env_sys
            .new_command("lsof")
            .args(["-ti", &format!("tcp:{port}"), "-sTCP:LISTEN"])
            .output();

        match lsof_result {
            Ok(output) => {
                let lsof_output = String::from_utf8_lossy(&output.stdout);

                let mut killed_any = false;
                for line in lsof_output.lines() {
                    let pid_str = line.trim();
                    if let Ok(pid) = pid_str.parse::<u32>() {
                        log::debug!("🎯 Found PID {pid} using port {port}, terminating...");

                        // Kill this specific PID
                        let kill_result = env_sys
                            .new_command("kill")
                            .args(["-9", &pid.to_string()])
                            .output();

                        match kill_result {
                            Ok(_) => {
                                log::debug!("✅ Successfully terminated Jupyter PID {pid}");
                                killed_any = true;
                            }
                            Err(e) => log::error!("Failed to kill PID {pid}: {e}"),
                        }
                    }
                }
                killed_any
            }
            Err(e) => {
                log::warn!("lsof failed, trying fuser: {e}");

                // Fallback: try fuser
                let fuser_result = env_sys
                    .new_command("fuser")
                    .args(["-k", &format!("{port}/tcp")])
                    .output();

                match fuser_result {
                    Ok(fuser_output) => {
                        if fuser_output.status.success() {
                            log::debug!("✅ fuser successfully killed processes on port {port}");
                            true
                        } else {
                            log::warn!("fuser failed for port {port}");
                            false
                        }
                    }
                    Err(e) => {
                        log::error!("fuser also failed: {e}");
                        false
                    }
                }
            }
        }
    };

    log::debug!("Jupyter server for environment '{environment}' stopped (success: {kill_success})");

    // Send completion message to logs
    let completion_message = format!("✅ Jupyter server '{environment}' stopped successfully");
    let completion_timestamp = chrono::Utc::now().timestamp_millis();

    let completion_entry = crate::utils::process_monitor::LogEntry {
        timestamp: completion_timestamp,
        content: completion_message.clone(),
        process_id: format!("jupyter-{environment}"),
    };

    let log_storage = crate::get_log_storage();
    if let Ok(mut storage) = log_storage.lock()
        && let Some(buffer) = storage.get_mut(&format!("jupyter-{environment}"))
    {
        buffer.add(completion_entry);
    }

    // Emit completion message as event
    let completion_payload = serde_json::json!({
        "processId": format!("jupyter-{}", environment),
        "output": completion_message,
        "timestamp": completion_timestamp,
        "type": "system"
    });
    let _ = app_handle.emit("process-output", completion_payload);

    Ok(kill_success)
}

#[tauri::command]
pub async fn stop_jupyter_server<R: tauri::Runtime>(
    app_handle: tauri::AppHandle<R>,
    environment: String,
) -> Result<bool, String> {
    stop_jupyter_server_impl(app_handle, environment, &RealEnvSystem).await
}

// Helper function to extract port from Jupyter URL
fn extract_port_from_url(url: &str) -> Option<String> {
    // Try different URL patterns to extract port
    let port_patterns = [
        r"://localhost:(\d+)",
        r"://127\.0\.0\.1:(\d+)",
        r"://[^:]+:(\d+)",
    ];

    for pattern in &port_patterns {
        if let Ok(regex) = regex::Regex::new(pattern)
            && let Some(cap) = regex.captures(url)
            && let Some(port_match) = cap.get(1)
        {
            return Some(port_match.as_str().to_string());
        }
    }

    // Fallback: look for any number after a colon, handling query params and fragments
    if let Some(colon_pos) = url.rfind(':') {
        let after_colon = &url[colon_pos + 1..];

        // Handle cases like :8888/lab?token=abc or :8888#something
        let port_end_chars = ['/', '?', '#'];
        let port_str = if let Some(end_pos) = after_colon.find(|c| port_end_chars.contains(&c)) {
            &after_colon[..end_pos]
        } else {
            after_colon
        };

        if port_str.chars().all(|c| c.is_ascii_digit()) && !port_str.is_empty() {
            return Some(port_str.to_string());
        }
    }

    None
}

#[tauri::command]
pub async fn check_jupyter_server(environment: String) -> Result<serde_json::Value, String> {
    let servers = match ACTIVE_JUPYTER_SERVERS.lock() {
        Ok(s) => s,
        Err(_) => return Err("Failed to acquire server lock".to_string()),
    };

    if let Some((url, process_id)) = servers.get(&environment) {
        Ok(serde_json::json!({
            "running": true,
            "url": url.clone(),
            "status": "running",
            "environment": environment,
            "process_id": process_id
        }))
    } else {
        Ok(serde_json::json!({
            "running": false,
            "url": null,
            "status": "not_found",
            "environment": environment
        }))
    }
}

#[tauri::command]
pub async fn list_jupyter_servers() -> Result<serde_json::Value, String> {
    let servers = match ACTIVE_JUPYTER_SERVERS.lock() {
        Ok(s) => s,
        Err(_) => return Err("Failed to acquire server lock".to_string()),
    };

    let mut server_list = Vec::new();

    for (env, (url, process_id)) in servers.iter() {
        server_list.push(serde_json::json!({
            "environment": env,
            "url": url,
            "running": true,
            "status": "running",
            "process_id": process_id
        }));
    }

    Ok(serde_json::json!({
        "servers": server_list
    }))
}

#[tauri::command]
pub async fn open_jupyter_logs_window(
    app_handle: tauri::AppHandle,
    environment: String,
) -> Result<(), String> {
    let window_label = format!("jupyter-logs-{environment}");

    if let Some(existing_window) = app_handle.get_webview_window(&window_label) {
        existing_window.show().map_err(|e| e.to_string())?;
        existing_window.set_focus().map_err(|e| e.to_string())?;
        return Ok(());
    }

    #[allow(unused_mut)]
    let mut builder = tauri::WebviewWindowBuilder::new(
        &app_handle,
        &window_label,
        tauri::WebviewUrl::App(format!("/jupyter-logs?env={environment}").into()),
    )
    .title(format!("Open Data Platform: Jupyter Logs - {environment}"))
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

// Command to update Jupyter server status from other windows
#[tauri::command]
pub fn update_jupyter_status(
    app_handle: tauri::AppHandle,
    environment_name: String,
    status: String,
) -> Result<(), String> {
    // Broadcast the status update to all windows via an event
    let payload = serde_json::json!({
        "environmentName": environment_name,
        "status": status
    });

    app_handle
        .emit("jupyter-status-update", payload)
        .map_err(|e| format!("Failed to emit jupyter-status-update event: {e}"))?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    // Helper to reset ACTIVE_JUPYTER_SERVERS between tests
    fn clear_active_servers() {
        let mut servers = ACTIVE_JUPYTER_SERVERS.lock().unwrap();
        servers.clear();
    }

    #[test]
    fn test_extract_jupyter_url_patterns() {
        let samples = [
            "http://localhost:8888/lab?token=abc123",
            "https://127.0.0.1:9999/?token=def456",
            "http://myhost:8888/lab",
            "Some log output http://localhost:8888/lab?token=abc123 more text",
        ];
        for sample in &samples {
            let url = extract_jupyter_url(sample);
            assert!(url.is_some(), "Should extract URL from: {sample}");
            assert!(
                url.unwrap().contains("http"),
                "Extracted URL should contain http"
            );
        }
    }

    #[test]
    fn test_extract_port_from_url() {
        let urls = [
            ("http://localhost:8888/lab?token=abc", "8888"),
            ("https://127.0.0.1:9999/?token=def", "9999"),
            ("http://myhost:12345/lab", "12345"),
            ("http://localhost:8888", "8888"),
        ];
        for (url, expected_port) in &urls {
            let port = extract_port_from_url(url);
            assert_eq!(port.as_deref(), Some(*expected_port));
        }
    }

    #[test]
    fn test_check_jupyter_server_and_list() {
        clear_active_servers();
        let env = "test-env".to_string();
        let url = "http://localhost:8888/lab?token=abc".to_string();
        let pid = 12345u32;

        // Insert a fake server
        {
            let mut servers = ACTIVE_JUPYTER_SERVERS.lock().unwrap();
            servers.insert(env.clone(), (url.clone(), pid));
        }

        // Check single server
        let result = futures::executor::block_on(check_jupyter_server(env.clone())).unwrap();
        assert_eq!(result["running"], true);
        assert_eq!(result["url"], url);
        assert_eq!(result["process_id"], pid);

        // List all servers
        let list_result = futures::executor::block_on(list_jupyter_servers()).unwrap();
        let servers = list_result["servers"].as_array().unwrap();
        assert_eq!(servers.len(), 1);
        assert_eq!(servers[0]["environment"], env);
        assert_eq!(servers[0]["url"], url);
        assert_eq!(servers[0]["process_id"], pid);
    }

    #[test]
    fn test_platform_agnostic_url_and_port() {
        // This test just ensures the regexes work on both unix and windows-like URLs
        let unix_url = "http://localhost:8888/lab?token=abc";
        let windows_url = "http://127.0.0.1:9999/?token=def";
        assert!(extract_jupyter_url(unix_url).is_some());
        assert!(extract_jupyter_url(windows_url).is_some());
        assert_eq!(extract_port_from_url(unix_url).unwrap(), "8888");
        assert_eq!(extract_port_from_url(windows_url).unwrap(), "9999");
    }
}
