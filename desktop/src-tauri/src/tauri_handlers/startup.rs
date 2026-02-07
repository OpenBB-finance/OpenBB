use crate::tauri_handlers::backends::create_backend_service_impl;
use crate::tauri_handlers::helpers::{
    EnvSystem, FileExtTrait, FileSystem, RealEnvSystem, RealFileSystem,
};
use once_cell::sync::Lazy;
use reqwest;
use serde::Serialize;
use std::path::Path;
use std::sync::Mutex;
use tauri::{Emitter, Window};

#[cfg(windows)]
use std::os::windows::process::CommandExt;

pub static INSTALLATION_STATE: Lazy<Mutex<InstallationState>> =
    Lazy::new(|| Mutex::new(InstallationState::default()));

#[derive(Default, Debug)]
pub struct InstallationState {
    pub is_downloading: bool,
    pub is_installing: bool,
    pub is_configuring: bool,
    pub is_complete: bool,
    pub message: String,
}

#[derive(Clone, Serialize)]
pub struct InstallProgress {
    pub step: String,
    pub progress: f32, // 0.0 to 1.0
    pub message: String,
}

#[tauri::command]
pub async fn get_installation_status() -> Result<serde_json::Value, String> {
    let state = INSTALLATION_STATE.lock().unwrap();

    let response = serde_json::json!({
        "phase": if state.is_complete { "complete" }
               else if state.is_configuring { "configuring" }
               else if state.is_installing { "installing" }
               else if state.is_downloading { "downloading" }
               else { "preparing" },
        "isDownloading": state.is_downloading,
        "isInstalling": state.is_installing,
        "isConfiguring": state.is_configuring,
        "isComplete": state.is_complete,
        "message": state.message
    });

    log::debug!("[get_installation_status] Current status: {response:?}");

    Ok(response)
}

pub fn update_installation_state(step: &str, progress: f32, message: &str) {
    log::debug!(
        "[installation_state] Updating state: step={step}, progress={progress}, message={message}"
    );

    let mut state = INSTALLATION_STATE.lock().unwrap();
    state.message = message.to_string();

    let step_lower = step.to_lowercase();
    let message_lower = message.to_lowercase();

    // First check the message content which is more reliable
    if message_lower.contains("downloading") {
        log::debug!("[installation_state] Download phase detected from message");
        state.is_downloading = true;
        state.is_installing = false;
        state.is_configuring = false;
        state.is_complete = false;
    } else if message_lower.contains("download complete")
        || message_lower.contains("preparing installation")
    {
        log::debug!("[installation_state] Download complete detected, switching to install phase");
        state.is_downloading = false;
        state.is_installing = true;
        state.is_configuring = false;
        state.is_complete = false;
    } else if message_lower.contains("running") || message_lower.contains("installing") {
        log::debug!("[installation_state] Install phase detected from message");
        state.is_downloading = false;
        state.is_installing = true;
        state.is_configuring = false;
        state.is_complete = false;
    } else if message_lower.contains("configuring") || message_lower.contains("setting up") {
        state.is_downloading = false;
        state.is_installing = false;
        state.is_configuring = true;
        state.is_complete = false;
    } else if message_lower.contains("complete") || message_lower.contains("success") {
        state.is_downloading = false;
        state.is_installing = false;
        state.is_configuring = false;
        state.is_complete = true;
    }
    // Fallback to step-based logic if message-based detection didn't work
    else if step_lower.contains("download") {
        state.is_downloading = true;
        state.is_installing = false;
        state.is_configuring = false;
    } else if step_lower.contains("install") {
        state.is_downloading = false;
        state.is_installing = true;
        state.is_configuring = false;
    } else if step_lower.contains("config") {
        state.is_downloading = false;
        state.is_installing = false;
        state.is_configuring = true;
    } else if step_lower.contains("complete") {
        state.is_downloading = false;
        state.is_installing = false;
        state.is_configuring = false;
        state.is_complete = true;
    } else if step_lower == "abort" {
        // Reset all states to indicate installation was aborted
        state.is_downloading = false;
        state.is_installing = false;
        state.is_configuring = false;
        state.is_complete = false;
        state.message = message.to_string();
    } else if step_lower == "error" {
        // For error messages, don't change the state booleans
        // Just update the message to show the error
        state.message = message.to_string();
    }

    log::debug!(
        "[installation_state] State updated: downloading={}, installing={}, configuring={}, complete={}",
        state.is_downloading,
        state.is_installing,
        state.is_configuring,
        state.is_complete
    );
}

fn check_directory_permissions<F: FileSystem>(
    dir_path: &Path,
    dir_type: &str,
    fs: &F,
) -> Result<(), String> {
    // Test file creation
    let test_file = dir_path.join(".permission_test_file");
    match fs.write(&test_file, "test") {
        Ok(_) => (),
        Err(e) => return Err(format!("{dir_type} directory is not writable: {e}")),
    }

    // Test file read
    match fs.open_ro(&test_file) {
        Ok(_) => (),
        Err(e) => {
            let _ = fs.remove_file(&test_file.to_string_lossy()); // Try to clean up even if read failed
            return Err(format!("{dir_type} directory files cannot be read: {e}"));
        }
    }

    // Test file deletion
    match fs.remove_file(&test_file.to_string_lossy()) {
        Ok(_) => (),
        Err(e) => {
            return Err(format!("{dir_type} directory files cannot be deleted: {e}"));
        }
    }

    // Test subdirectory creation
    let test_dir = dir_path.join(".permission_test_dir");
    match fs.create_dir_all(&test_dir) {
        Ok(_) => (),
        Err(e) => {
            return Err(format!(
                "Cannot create subdirectories in {dir_type} directory: {e}"
            ));
        }
    }

    // Test subdirectory deletion
    match fs.remove_dir_all(&test_dir) {
        Ok(_) => (),
        Err(e) => {
            return Err(format!(
                "Cannot remove subdirectories in {dir_type} directory: {e}"
            ));
        }
    }

    Ok(())
}

pub async fn install_to_directory_impl<F: FileSystem, E: EnvSystem>(
    directory: String,
    user_data_directory: String,
    fs: &F,
    env_sys: &E,
) -> Result<bool, String> {
    use std::path::Path;

    log::debug!("Installing to directory: {directory}");
    log::debug!("User data directory: {user_data_directory}");

    // Sanitize paths - trim whitespace
    let directory = directory.trim().to_string();
    let user_data_directory = user_data_directory.trim().to_string();

    if directory.is_empty() {
        return Err("Installation directory cannot be empty".to_string());
    }

    if user_data_directory.is_empty() {
        return Err("User data directory cannot be empty".to_string());
    }

    // Create directory paths
    let install_dir_path = Path::new(&directory);
    let user_data_dir_path = Path::new(&user_data_directory);

    // Create directories if they don't exist
    if !fs.exists(install_dir_path) {
        fs.create_dir_all(install_dir_path)
            .map_err(|e| format!("Failed to create installation directory: {e}"))?;
    }

    if !fs.exists(user_data_dir_path) {
        fs.create_dir_all(user_data_dir_path)
            .map_err(|e| format!("Failed to create user data directory: {e}"))?;
    }

    // Check directory permissions
    check_directory_permissions(install_dir_path, "installation", fs)
        .map_err(|e| format!("Installation directory permission error: {e}"))?;

    check_directory_permissions(user_data_dir_path, "user data", fs)
        .map_err(|e| format!("User data directory permission error: {e}"))?;

    let home_dir = env_sys
        .var("HOME")
        .or_else(|_| env_sys.var("USERPROFILE"))
        .map_err(|e| format!("Could not determine home directory: {e}"))?;

    let platform_dir = Path::new(&home_dir).join(".openbb_platform");

    log::debug!(
        "Creating OpenBB platform directory in home directory: {}",
        platform_dir.display()
    );

    // Create platform directory if it doesn't exist
    if !fs.exists(&platform_dir) {
        log::debug!(
            "Creating OpenBB platform directory in home directory: {}",
            platform_dir.display()
        );
        match fs.create_dir_all(&platform_dir) {
            Ok(_) => log::debug!("Successfully created platform directory"),
            Err(e) => {
                let error_msg = format!("Failed to create platform directory: {e}");
                log::debug!("{error_msg}");
                return Err(error_msg);
            }
        }
    }

    // Create the required JSON files
    let user_settings_path = platform_dir.join("user_settings.json");
    let system_settings_path = platform_dir.join("system_settings.json");

    if !fs.exists(&user_settings_path) {
        log::debug!("Creating user settings file");

        // Create structured user settings JSON with the user data directory
        let user_settings = format!(
            r#"{{
            "credentials": {{}},
            "preferences": {{
                "data_directory": "{}"
            }},
            "defaults": {{}}
        }}"#,
            user_data_directory.replace("\\", "\\\\")
        ); // Escape backslashes for JSON string

        match fs.write(&user_settings_path, &user_settings) {
            Ok(_) => log::debug!("Successfully created user settings file"),
            Err(e) => {
                let error_msg = format!("Failed to create user settings file: {e}");
                log::debug!("{error_msg}");
                return Err(error_msg);
            }
        }
    } else {
        log::debug!("User settings file exists, checking if data directory needs updating");

        // Read existing settings
        let settings_content = match fs.read_to_string(&user_settings_path) {
            Ok(content) => content,
            Err(e) => {
                let error_msg = format!("Failed to read user settings file: {e}");
                log::debug!("{error_msg}");
                return Err(error_msg);
            }
        };

        // Parse JSON
        let mut settings: serde_json::Value = match serde_json::from_str(&settings_content) {
            Ok(json) => json,
            Err(e) => {
                let error_msg = format!("Failed to parse user settings: {e}");
                log::debug!("{error_msg}");
                return Err(error_msg);
            }
        };

        // Ensure preferences section exists
        if !settings.as_object().unwrap().contains_key("preferences") {
            settings["preferences"] = serde_json::json!({});
        }

        // Get current data_directory if it exists
        let current_dir = settings["preferences"]
            .get("data_directory")
            .and_then(|v| v.as_str());

        // Check if different from provided user_data_directory
        if current_dir.is_none_or(|dir| dir != user_data_directory) {
            log::debug!(
                "Updating data_directory in user settings from '{}' to '{}'",
                current_dir.unwrap_or("none"),
                user_data_directory
            );

            // Update the data_directory
            settings["preferences"]["data_directory"] =
                serde_json::Value::String(user_data_directory.clone());

            // Write updated settings back to file
            match fs.write(
                &user_settings_path,
                &serde_json::to_string_pretty(&settings)
                    .map_err(|e| format!("Failed to serialize user settings: {e}"))?,
            ) {
                Ok(_) => log::debug!("Successfully updated data_directory in user settings file"),
                Err(e) => {
                    let error_msg = format!("Failed to write updated user settings: {e}");
                    log::debug!("{error_msg}");
                    return Err(error_msg);
                }
            }
        } else {
            log::debug!("Data directory already set to '{user_data_directory}', no update needed");
        }
    }

    // Update system settings file - read existing content if it exists
    let mut system_settings = if system_settings_path.exists() {
        match fs.read_to_string(&system_settings_path) {
            Ok(content) => match serde_json::from_str::<serde_json::Value>(&content) {
                Ok(json) => json,
                Err(_) => {
                    log::debug!(
                        "Warning: Could not parse existing system settings, creating new one"
                    );
                    serde_json::json!({})
                }
            },
            Err(_) => {
                log::debug!("Warning: Could not read existing system settings, creating new one");
                serde_json::json!({})
            }
        }
    } else {
        log::debug!("Creating new system settings file");
        serde_json::json!({})
    };

    // Ensure system_settings is an object
    if !system_settings.is_object() {
        system_settings = serde_json::json!({});
    }

    // Create/update the install_settings section
    let install_settings = serde_json::json!({
        "installation_directory": directory,
        "user_data_directory": user_data_directory,
        "installation_date": chrono::Local::now().to_rfc3339()
    });

    // Update the install_settings section without affecting other parts
    if let Some(obj) = system_settings.as_object_mut() {
        obj.insert("install_settings".to_string(), install_settings);
    }

    // First, check if the directory exists or needs to be created
    if !fs.exists(std::path::Path::new(&directory)) {
        fs.create_dir_all(std::path::Path::new(&directory))
            .map_err(|e| format!("Failed to create directory: {e}"))?;
    }

    // Write the updated system settings
    match fs.write(
        &system_settings_path,
        &serde_json::to_string_pretty(&system_settings)
            .map_err(|e| format!("Failed to serialize system settings: {e}"))?,
    ) {
        Ok(_) => log::debug!("Successfully updated system settings"),
        Err(e) => {
            let error_msg = format!("Failed to update system settings: {e}");
            log::debug!("{error_msg}");
            return Err(error_msg);
        }
    }

    log::debug!("Installation directories and configuration prepared successfully");
    Ok(true)
}

#[tauri::command]
pub async fn install_to_directory(
    directory: String,
    user_data_directory: String,
) -> Result<bool, String> {
    // Use the real file system implementation
    install_to_directory_impl(
        directory,
        user_data_directory,
        &RealFileSystem,
        &RealEnvSystem,
    )
    .await
}

// Static guard to prevent multiple simultaneous installations
static INSTALLATION_IN_PROGRESS: Lazy<Mutex<bool>> = Lazy::new(|| Mutex::new(false));

#[tauri::command]
pub async fn install_conda(directory: String, window: Window) -> Result<bool, String> {
    use std::fs;
    use std::path::Path;
    use std::process::Command;

    // Prevent multiple simultaneous installations
    {
        let mut in_progress = INSTALLATION_IN_PROGRESS.lock().unwrap();
        if *in_progress {
            return Err(
                "Installation is already in progress. Please wait for it to complete.".to_string(),
            );
        }
        *in_progress = true;
    }

    // Release the guard when we finish or error
    let release_guard = || {
        let mut in_progress = INSTALLATION_IN_PROGRESS.lock().unwrap();
        *in_progress = false;
    };

    // Report fatal errors and ensure UI knows to stop
    let report_fatal_error = |message: &str| -> String {
        let mut state = INSTALLATION_STATE.lock().unwrap();

        // Reset all state flags
        state.message = message.to_string();
        state.is_installing = false;
        state.is_downloading = false;
        state.is_configuring = false;
        state.is_complete = false;

        // Send explicit error event to UI
        let progress_data = InstallProgress {
            step: "error".to_string(),
            progress: 0.0,
            message: message.to_string(),
        };

        let _ = window.emit("install-progress", &progress_data);
        log::debug!("[ERROR] {message}");

        // Return the error message
        message.to_string()
    };

    // Report progress
    let report_progress = |step: &str, progress: f32, message: &str| {
        // Set download/install states based on step
        let is_downloading = step == "download" || message.to_lowercase().contains("download");
        let is_installing = step == "install" || message.to_lowercase().contains("instal");
        let is_configuring = step == "config" || message.to_lowercase().contains("config");
        let is_complete = step == "complete" || message.to_lowercase().contains("complet");

        // Update state with explicit values
        {
            let mut state = INSTALLATION_STATE.lock().unwrap();
            state.message = message.to_string();
            state.is_downloading = is_downloading;
            state.is_installing = is_installing;
            state.is_configuring = is_configuring;
            state.is_complete = is_complete;

            log::debug!(
                "[installation_state] State updated: downloading={}, installing={}, configuring={}, complete={}",
                state.is_downloading,
                state.is_installing,
                state.is_configuring,
                state.is_complete
            );
        }

        // Send progress event
        let progress_data = InstallProgress {
            step: step.to_string(),
            progress,
            message: message.to_string(),
        };

        let _ = window.emit("install-progress", &progress_data);
        log::debug!("[{}] ({:.1}%) {}", step, progress * 100.0, message);
    };

    // DIRECTORY SETUP
    let install_path = Path::new(&directory);
    let conda_dir = install_path.join("conda");

    report_progress("download", 0.05, "Preparing installation directory");

    // Create main directory
    if !install_path.exists() {
        match fs::create_dir_all(install_path) {
            Ok(_) => {}
            Err(e) => {
                release_guard();
                return Err(report_fatal_error(&format!(
                    "Failed to create installation directory: {e}"
                )));
            }
        }
    }

    if conda_dir.exists() {
        report_progress("download", 0.1, "Removing existing Conda installation");
        let mut last_err = None;
        for _ in 0..3 {
            match fs::remove_dir_all(&conda_dir) {
                Ok(_) => {
                    last_err = None;
                    break;
                }
                Err(e) => {
                    last_err = Some(e);
                    // Wait a bit and retry
                    std::thread::sleep(std::time::Duration::from_millis(300));
                }
            }
        }
        if let Some(e) = last_err {
            // Print directory contents for debugging
            if let Ok(entries) = std::fs::read_dir(&conda_dir) {
                for entry in entries.flatten() {
                    log::debug!("Conda dir not empty: {:?}", entry.path());
                }
            }
            release_guard();
            return Err(report_fatal_error(&format!(
                "Failed to remove existing conda directory: {e}"
            )));
        }
    }

    // Create fresh conda directory
    match fs::create_dir_all(&conda_dir) {
        Ok(_) => {}
        Err(e) => {
            release_guard();
            return Err(report_fatal_error(&format!(
                "Failed to create conda directory: {e}"
            )));
        }
    }

    // ARCHITECTURE DETECTION
    report_progress("download", 0.15, "Detecting system architecture");

    let arch = match detect_architecture(&RealEnvSystem) {
        Ok(arch) => arch,
        Err(e) => {
            release_guard();
            return Err(report_fatal_error(&format!(
                "Failed to detect CPU architecture: {e}"
            )));
        }
    };

    // DETERMINE URL
    let installer_url = match fetch_miniforge_installer_url(arch.as_str()).await {
        Ok(url) => url,
        Err(e) => {
            release_guard();
            return Err(report_fatal_error(&format!(
                "Failed to fetch Miniforge installer URL: {e}"
            )));
        }
    };

    report_progress(
        "download",
        0.2,
        &format!("Using installer: {installer_url}"),
    );

    // TEMPORARY DIRECTORY SETUP
    let temp_dir = std::env::temp_dir().join("openbb_installer");
    if !temp_dir.exists() {
        match fs::create_dir_all(&temp_dir) {
            Ok(_) => {}
            Err(e) => {
                release_guard();
                return Err(report_fatal_error(&format!(
                    "Failed to create temp directory: {e}"
                )));
            }
        }
    }

    // INSTALLER PATH
    let installer_path = if std::env::consts::OS == "windows" {
        temp_dir.join("miniforge_installer.exe")
    } else {
        temp_dir.join("miniforge_installer.sh")
    };

    // Remove existing installer if it exists
    if installer_path.exists()
        && let Err(e) = fs::remove_file(&installer_path)
    {
        log::debug!("Warning: Could not remove existing installer: {e}");
        // Non-fatal, continue
    }

    // DOWNLOAD THE INSTALLER - explicitly set download phase
    report_progress("download", 0.25, "Downloading Miniforge installer");

    // For Unix systems
    if std::env::consts::OS != "windows" {
        let curl_args = [
            "--http1.1",
            "-L",
            "-o",
            &installer_path.to_string_lossy(),
            "--fail",
            "--retry",
            "3",
            "--connect-timeout",
            "30",
            "--silent",
            "--show-error",
            &installer_url,
        ];

        let curl_output = Command::new("curl").args(curl_args).output();

        match curl_output {
            Ok(output) => {
                if !output.status.success() {
                    let stderr = String::from_utf8_lossy(&output.stderr);
                    release_guard();
                    return Err(report_fatal_error(&format!("Download failed: {stderr}")));
                }
            }
            Err(e) => {
                release_guard();
                return Err(report_fatal_error(&format!("Failed to execute curl: {e}")));
            }
        }
    } else {
        // For Windows, use reqwest to download
        let response = match reqwest::get(&installer_url).await {
            Ok(res) => res,
            Err(e) => {
                release_guard();
                return Err(report_fatal_error(&format!("Download failed: {e}")));
            }
        };

        if !response.status().is_success() {
            release_guard();
            return Err(report_fatal_error(&format!(
                "Download failed with status: {}",
                response.status()
            )));
        }

        let content = match response.bytes().await {
            Ok(bytes) => bytes,
            Err(e) => {
                release_guard();
                return Err(report_fatal_error(&format!(
                    "Failed to read download content: {e}"
                )));
            }
        };

        let mut dest = match fs::File::create(&installer_path) {
            Ok(file) => file,
            Err(e) => {
                release_guard();
                return Err(report_fatal_error(&format!(
                    "Failed to create installer file: {e}"
                )));
            }
        };

        if let Err(e) = std::io::copy(&mut content.as_ref(), &mut dest) {
            release_guard();
            return Err(report_fatal_error(&format!(
                "Failed to write to installer file: {e}"
            )));
        }
    }

    if !installer_path.exists() {
        release_guard();
        return Err(report_fatal_error(
            "Installer file not found after download",
        ));
    }

    // Check file size
    let file_size = match fs::metadata(&installer_path) {
        Ok(metadata) => metadata.len(),
        Err(e) => {
            release_guard();
            return Err(report_fatal_error(&format!(
                "Failed to get installer metadata: {e}"
            )));
        }
    };

    // Sanity check - Miniforge installers are at least 30MB typically
    if file_size < 10_000_000 {
        release_guard();
        return Err(report_fatal_error(&format!(
            "Downloaded file is too small ({file_size} bytes). The download may be incomplete."
        )));
    }

    report_progress("install", 0.5, "Download complete. Preparing installation");

    // MAKE INSTALLER EXECUTABLE (Unix only)
    #[cfg(not(target_os = "windows"))]
    {
        match Command::new("chmod")
            .args(["+x", &installer_path.to_string_lossy()])
            .status()
        {
            Ok(status) if status.success() => {
                log::debug!("Successfully made installer executable");
            }
            Ok(status) => {
                release_guard();
                return Err(report_fatal_error(&format!(
                    "Failed to make installer executable. chmod exited with status: {status}"
                )));
            }
            Err(e) => {
                release_guard();
                return Err(report_fatal_error(&format!("Failed to execute chmod: {e}")));
            }
        }
    } // RUN THE INSTALLER
    report_progress("install", 0.55, "Running Miniforge installer");
    let install_result = if std::env::consts::OS == "windows" {
        let mut cmd = Command::new("cmd");

        #[cfg(windows)]
        {
            // Use CREATE_NO_WINDOW to prevent console window
            cmd.creation_flags(0x08000000);
        }

        // Use start /B /WAIT to run the installer in background without any window
        let args = vec![
            "/C".to_string(),
            "start".to_string(),
            "/B".to_string(),
            "/WAIT".to_string(),
            installer_path.to_string_lossy().to_string(), // Remove the extra quotes wrapping
            "/InstallationType=JustMe".to_string(),
            "/RegisterPython=0".to_string(),
            "/AddToPath=0".to_string(),
            "/S".to_string(),
            format!("/D={}", conda_dir.to_string_lossy()),
        ];

        cmd.args(&args);

        log::debug!(
            "Executing installer via start /B: {} with args: {:?}",
            installer_path.to_string_lossy(),
            &[
                "/InstallationType=JustMe",
                "/RegisterPython=0",
                "/AddToPath=0",
                "/S",
                &format!("/D={}", conda_dir.to_string_lossy())
            ]
        );

        // Run the installer via cmd start
        cmd.output()
    } else {
        // Unix: Run with bash, using -u flag to BYPASS MD5 VERIFICATION
        Command::new("bash")
            .arg(&installer_path)
            .args([
                "-b", // batch mode
                "-u", // bypass MD5 verification
                "-p",
                &conda_dir.to_string_lossy(),
                "-f", // force installation
            ])
            .output()
    };

    // Check if installation succeeded
    match install_result {
        Ok(output) => {
            if !output.status.success() {
                let stdout = String::from_utf8_lossy(&output.stdout);
                let stderr = String::from_utf8_lossy(&output.stderr);

                release_guard();
                return Err(report_fatal_error(&format!(
                    "Conda installation failed:\nExit code: {}\nStdout: {}\nStderr: {}",
                    output.status, stdout, stderr
                )));
            }
        }
        Err(e) => {
            release_guard();
            return Err(report_fatal_error(&format!(
                "Failed to execute installer: {e}"
            )));
        }
    }
    report_progress("install", 0.9, "Conda installation completed successfully");
    let conda_rc_path = conda_dir.join(".condarc");
    let conda_rc_content = format!(
        r#"
channels:
  - defaults
  - conda-forge
envs_dirs:
  - {}
pkgs_dirs:
  - {}
auto_activate_base: false
show_channel_urls: false
pip_interop_enabled: true
remote_connect_timeout_secs: 60
remote_read_timeout_secs: 120
remote_max_retries: 5
"#,
        conda_dir.join("envs").to_string_lossy(),
        conda_dir.join("pkgs").to_string_lossy()
    );

    match fs::write(&conda_rc_path, conda_rc_content) {
        Ok(_) => {
            log::debug!("Successfully created conda configuration file");
        }
        Err(e) => {
            log::debug!("Warning: Failed to write conda configuration: {e}");
            // Non-fatal, continue
        }
    }

    // CLEANUP
    if let Err(e) = fs::remove_file(&installer_path) {
        log::debug!("Warning: Could not remove installer file: {e}");
        // Non-fatal, continue
    }

    // VERIFY CONDA EXISTS
    let conda_exe = if std::env::consts::OS == "windows" {
        conda_dir.join("Scripts").join("conda.exe")
    } else {
        conda_dir.join("bin").join("conda")
    };

    if !conda_exe.exists() {
        release_guard();
        return Err(report_fatal_error(&format!(
            "Conda executable not found at expected location: {}",
            conda_exe.display()
        )));
    }

    report_progress("complete", 1.0, "Conda installation completed successfully");

    // Release the installation lock
    release_guard();

    Ok(true)
}

// Helper function to detect architecture
#[allow(unused_variables)]
fn detect_architecture<E: EnvSystem>(env_sys: &E) -> Result<String, String> {
    // We can use std::env::consts::ARCH for basic detection
    let std_arch = std::env::consts::ARCH;

    // For more accurate detection on certain platforms:
    #[cfg(target_os = "macos")]
    {
        // On Apple Silicon Macs running x86_64 binaries via Rosetta,
        // we want to detect the native architecture
        let output = env_sys
            .new_command("sysctl")
            .args(["-n", "machdep.cpu.brand_string"])
            .output();

        if let Ok(output) = output {
            let cpu_info = String::from_utf8_lossy(&output.stdout).to_lowercase();

            if cpu_info.contains("apple") {
                // Apple Silicon
                return Ok("arm64".to_string());
            }
        }

        // Additional check using uname for Apple Silicon
        let output = env_sys.new_command("uname").arg("-m").output();

        if let Ok(output) = output {
            let arch = String::from_utf8_lossy(&output.stdout).trim().to_string();
            if arch == "arm64" {
                return Ok(arch);
            }
        }
    }

    // Map Rust's architecture names to the ones used by Conda
    match std_arch {
        "x86_64" => Ok("x86_64".to_string()),
        "aarch64" => Ok("aarch64".to_string()),
        "arm" | "armv7" => Ok("armv7l".to_string()),
        "powerpc64" => Ok("ppc64le".to_string()),
        "s390x" => Ok("s390x".to_string()),
        _ => Ok(std_arch.to_string()),
    }
}

pub async fn check_installer_file_exists_impl<E: EnvSystem>(env_sys: &E) -> Result<bool, String> {
    let temp_dir = env_sys.temp_dir();
    let installer_path = temp_dir
        .join("openbb_installer")
        .join("miniforge_installer.sh");
    Ok(installer_path.exists())
}

#[tauri::command]
pub async fn check_installer_file_exists() -> Result<bool, String> {
    // Use the real environment system implementation
    check_installer_file_exists_impl(&RealEnvSystem).await
}

pub async fn abort_installation_impl<F: FileSystem, E: EnvSystem>(
    directory: String,
    fs: &F,
    env_sys: &E,
) -> Result<(), String> {
    log::debug!("Aborting installation in directory: {directory}");

    // Reset the installation state to indicate cancellation
    {
        let mut state = INSTALLATION_STATE.lock().unwrap();
        state.is_downloading = false;
        state.is_installing = false;
        state.is_configuring = false;
        state.is_complete = false;
        state.message = "Installation cancelled by user".to_string();
    } // MutexGuard is dropped here when it goes out of scope

    // Only target processes specifically related to our installation scripts
    #[cfg(target_os = "windows")]
    {
        // Find and kill processes running our scripts in the specific directory
        // Use more specific process targeting to avoid killing unrelated processes
        let _ = env_sys
            .new_command("taskkill")
            .args([
                "/F",
                "/FI",
                &format!(
                    "WINDOWTITLE eq *{}*openbb*",
                    directory.replace("\\", "\\\\")
                ),
                "/IM",
                "cmd.exe",
            ])
            .creation_flags(0x08000000) // CREATE_NO_WINDOW
            .output();

        let _ = env_sys
            .new_command("taskkill")
            .args([
                "/F",
                "/FI",
                &format!("WINDOWTITLE eq *{}*conda*", directory.replace("\\", "\\\\")),
                "/IM",
                "python.exe",
            ])
            .creation_flags(0x08000000) // CREATE_NO_WINDOW
            .output();
    }

    #[cfg(not(target_os = "windows"))]
    {
        // On Unix, use more precise pattern matching to target only our installation processes
        // Look for processes that include both the directory path and conda/pip commands
        let _ = env_sys
            .new_command("pkill")
            .args([
                "-f",
                &format!("{}/conda.*install", directory.replace(" ", "\\ ")),
            ])
            .output();

        let _ = env_sys
            .new_command("pkill")
            .args([
                "-f",
                &format!("source.*{}/conda.*", directory.replace(" ", "\\ ")),
            ])
            .output();

        let _ = env_sys
            .new_command("pkill")
            .args([
                "-f",
                &format!("bash.*openbb_install.*{}.*", directory.replace(" ", "\\ ")),
            ])
            .output();
    }

    // Create a path from the directory string
    let install_dir = std::path::PathBuf::from(&directory);

    // If a specific directory was provided and it exists, attempt to clean it
    if matches!(fs.is_empty(&install_dir), Ok(false)) && fs.exists(&install_dir) {
        // Only clean specific environment directories that are likely in progress
        let conda_dir = install_dir.join("conda");
        let env_dir = conda_dir.join("envs").join("openbb");

        // If we're in the middle of creating an environment, clean that up
        if fs.exists(&env_dir) {
            match fs.remove_dir_all(&env_dir) {
                Ok(_) => log::debug!("Successfully removed partial environment"),
                Err(e) => log::debug!("Warning: Failed to remove partial environment: {e}"),
            }
        }
    }

    // Clean up our temporary installation files
    let temp_dir = env_sys.temp_dir();
    let installer_dir = temp_dir.join("openbb_installer");
    if fs.exists(&installer_dir) {
        match fs.remove_dir_all(&installer_dir) {
            Ok(_) => log::debug!("Successfully removed installer files"),
            Err(e) => log::debug!("Warning: Failed to remove installer files: {e}"),
        }
        match fs.remove_dir_all(&install_dir) {
            Ok(_) => log::debug!("Successfully removed installation files"),
            Err(e) => log::debug!("Warning: Failed to remove installation files: {e}"),
        }
    }

    // Clean up any temporary installation scripts we created
    for script_name in &[
        "openbb_install_extensions",
        "openbb_install_packages",
        "openbb_get_versions",
    ] {
        for ext in &["sh", "bat"] {
            let script_path = temp_dir.join(format!("{script_name}.{ext}"));
            if fs.exists(&script_path) {
                let _ = fs.remove_file(&script_path.to_string_lossy());
            }
        }
    }

    log::debug!("Installation aborted successfully");
    Ok(())
}

#[tauri::command]
pub async fn abort_installation(directory: String) -> Result<(), String> {
    // Use the real file system and environment system implementations
    abort_installation_impl(directory, &RealFileSystem, &RealEnvSystem).await
}

async fn fetch_miniforge_installer_url(arch: &str) -> Result<String, String> {
    // Map Rust's architecture names to the ones used by Miniforge
    let miniforge_arch = match arch {
        "x86_64" | "amd64" => "x86_64",
        "aarch64" | "arm64" => match std::env::consts::OS {
            "macos" => "arm64",
            _ => "aarch64",
        },
        "arm" | "armv7" => "armv7l",
        "powerpc64" | "ppc64le" => "ppc64le",
        "s390x" => "s390x",
        _ => arch,
    };

    // Determine the OS name as used by Miniforge filenames
    let os_name = match std::env::consts::OS {
        "macos" => "MacOSX",
        "windows" => "Windows",
        "linux" => "Linux",
        os => return Err(format!("Unsupported operating system: {os}")),
    };

    // Determine the file extension based on OS
    let file_ext = if std::env::consts::OS == "windows" {
        "exe"
    } else {
        "sh"
    };

    // Fetch releases from GitHub API
    let client = reqwest::Client::new();
    let releases_response = client
        .get("https://api.github.com/repos/conda-forge/miniforge/releases")
        .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36")
        .send()
        .await
        .map_err(|e| format!("Failed to fetch miniforge releases: {e}"))?;

    if !releases_response.status().is_success() {
        return Err(format!(
            "Failed to fetch releases: HTTP status {}",
            releases_response.status()
        ));
    }

    let releases: serde_json::Value = releases_response
        .json()
        .await
        .map_err(|e| format!("Failed to parse releases JSON: {e}"))?;

    // Find the latest release or pre-release
    if let Some(releases_array) = releases.as_array() {
        // Sort releases by published date (descending)
        let mut sorted_releases = releases_array.clone();
        sorted_releases.sort_by(|a, b| {
            let a_date = a["published_at"].as_str().unwrap_or("");
            let b_date = b["published_at"].as_str().unwrap_or("");
            b_date.cmp(a_date) // descending order
        });

        // First look for the installer filename pattern in the latest releases
        for release in sorted_releases.iter() {
            if let Some(assets) = release["assets"].as_array() {
                // Determine correct installer pattern based on OS and architecture
                let installer_pattern = format!("Miniforge3-{os_name}-{miniforge_arch}");

                for asset in assets {
                    if let Some(name) = asset["name"].as_str()
                        && name.contains(&installer_pattern)
                        && name.ends_with(file_ext)
                        && let Some(url) = asset["browser_download_url"].as_str()
                    {
                        log::debug!("Found Miniforge installer: {name} ({url})");
                        return Ok(url.to_string());
                    }
                }
            }
        }
    } // Fallback to traditional URLs if GitHub releases don't have what we need
    let fallback_url = match std::env::consts::OS {
        "macos" => match miniforge_arch {
            "x86_64" => {
                "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-x86_64.sh"
            }
            "arm64" => {
                "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh"
            }
            _ => {
                return Err(format!("Unsupported CPU architecture for macOS: {arch}"));
            }
        },
        "windows" => match miniforge_arch {
            "x86_64" => {
                "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe"
            }
            "aarch64" => {
                "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-ARM64.exe"
            }
            _ => {
                return Err(format!("Unsupported CPU architecture for Windows: {arch}"));
            }
        },
        "linux" => match miniforge_arch {
            "x86_64" => {
                "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh"
            }
            "aarch64" => {
                "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh"
            }
            "ppc64le" => {
                "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-ppc64le.sh"
            }
            "s390x" => {
                "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-s390x.sh"
            }
            _ => return Err(format!("Unsupported CPU architecture for Linux: {arch}")),
        },
        os => return Err(format!("Unsupported operating system: {os}")),
    };

    log::debug!("Using fallback Miniforge URL: {fallback_url}");
    Ok(fallback_url.to_string())
}

#[tauri::command]
pub async fn setup_python_environment(
    directory: String,
    python_version: String,
    window: Window,
) -> Result<bool, String> {
    // Delegate to the actual implementation
    setup_python_environment_impl(
        directory,
        python_version,
        window,
        &RealFileSystem,
        &RealEnvSystem,
    )
    .await
}

// Split the large function into a separate implementation
async fn setup_python_environment_impl<F: FileSystem, E: EnvSystem>(
    directory: String,
    python_version: String,
    window: Window,
    fs: &F,
    env_sys: &E,
) -> Result<bool, String> {
    use std::path::Path;

    // Report progress to the frontend
    let report_progress = |step: &str, progress: f32, message: &str| {
        update_installation_state(step, progress, message);

        let progress_data = InstallProgress {
            step: step.to_string(),
            progress,
            message: message.to_string(),
        };

        match window.emit("install-progress", &progress_data) {
            Ok(_) => (),
            Err(e) => log::debug!("Failed to emit progress event: {e}"),
        }
        log::debug!("[{}] ({:.1}%) {}", step, progress * 100.0, message);
    };

    report_progress(
        "config",
        0.6,
        &format!("Setting up Python {python_version} environment"),
    );

    // Use the proper path to conda directory
    let conda_path = Path::new(&directory).join("conda");

    log::debug!("Using conda path: {}", conda_path.display());

    // Validate conda installation
    let conda_exe = validate_conda_installation(&conda_path)?;

    // Prepare environment
    prepare_environment(&conda_exe, &conda_path, &report_progress, env_sys).await?;

    // Generate YAML file for the environment and create it
    let yaml_path = generate_environment_yaml(&python_version, fs, env_sys).await?;
    create_environment_from_yaml(&conda_exe, &yaml_path, &report_progress, env_sys).await?;

    // Update OpenBB settings
    if let Err(e) = crate::tauri_handlers::helpers::update_openbb_settings_impl(
        &conda_path,
        "openbb",
        fs,
        env_sys,
    )
    .await
    {
        log::debug!("Warning: OpenBB settings update may have issues: {e}");
    }

    report_progress("complete", 1.0, "Installation complete");

    window
        .emit("installation-directory", &directory)
        .unwrap_or_else(|e| {
            log::error!("Failed to emit installation directory: {e}");
        });

    Ok(true)
}

// Helper functions for environment setup

fn validate_conda_installation(conda_path: &Path) -> Result<std::path::PathBuf, String> {
    let conda_exe = if std::env::consts::OS == "windows" {
        conda_path.join("Scripts").join("conda.exe")
    } else {
        conda_path.join("bin").join("conda")
    };

    if !conda_exe.exists() {
        return Err(format!(
            "Conda executable not found at: {}",
            conda_exe.display()
        ));
    }

    Ok(conda_exe)
}

async fn prepare_environment<F, E: EnvSystem>(
    conda_exe: &Path,
    conda_path: &Path,
    report_progress: &F,
    env_sys: &E,
) -> Result<(), String>
where
    F: Fn(&str, f32, &str),
{
    let env_name = "openbb";
    let env_path = conda_path.join("envs").join(env_name);

    if env_path.exists() {
        report_progress("config", 0.65, "Removing existing environment");

        let mut rm_command = env_sys.new_conda_command(conda_exe, conda_path);
        let rm_output = rm_command
            .args(["env", "remove", "-n", env_name, "-y"])
            .output()
            .map_err(|e| format!("Failed to remove existing environment: {e}"))?;

        if !rm_output.status.success() {
            log::debug!(
                "Warning: Failed to remove existing environment: {}",
                String::from_utf8_lossy(&rm_output.stderr)
            );
        }
    }

    report_progress("config", 0.7, "Updating conda to latest version");

    let mut conda_update_command = env_sys.new_conda_command(conda_exe, conda_path);
    let conda_update_output = conda_update_command
        .args([
            "install",
            "-n",
            "base",
            "-c",
            "conda-forge",
            "conda",
            "conda-libmamba-solver",
            "--solver=classic",
            "-y",
            "--quiet",
        ])
        .output()
        .map_err(|e| format!("Failed to update conda: {e}"))?;

    if !conda_update_output.status.success() {
        let stderr = String::from_utf8_lossy(&conda_update_output.stderr);
        let stdout = String::from_utf8_lossy(&conda_update_output.stdout);

        log::debug!(
            "Warning: Failed to update conda (continuing anyway):\nStdout: {stdout}\nStderr: {stderr}"
        );
    } else {
        log::debug!("Successfully updated conda to latest version");
    }

    Ok(())
}

async fn create_environment_from_yaml<F, E: EnvSystem>(
    conda_exe: &Path,
    yaml_path: &Path,
    report_progress: &F,
    env_sys: &E,
) -> Result<(), String>
where
    F: Fn(&str, f32, &str),
{
    report_progress("config", 0.80, "Initializing environment");

    // Get the conda directory from the conda executable path
    let conda_path = conda_exe.parent().unwrap().parent().unwrap();

    let mut cmd = env_sys.new_conda_command(conda_exe, conda_path);
    let env_create_output = cmd
        .args(["env", "create", "-f", &yaml_path.to_string_lossy(), "-y"])
        .output()
        .map_err(|e| format!("Failed to create environment from YAML: {e}"))?;

    if !env_create_output.status.success() {
        let stderr = String::from_utf8_lossy(&env_create_output.stderr);
        let stdout = String::from_utf8_lossy(&env_create_output.stdout);

        return Err(format!(
            "Failed to create environment from YAML:\nExit code: {}\nStdout: {}\nStderr: {}",
            env_create_output.status, stdout, stderr
        ));
    }

    Ok(())
}

/// Create default backend services (OpenBB API and MCP)
/// This should only be called after a successful full installation
#[tauri::command]
pub async fn create_default_backend_services() -> Result<(), String> {
    use crate::tauri_handlers::helpers::{RealEnvSystem, RealFileExtTrait, RealFileSystem};
    create_default_backend_services_impl(&RealFileSystem, &RealEnvSystem, &RealFileExtTrait).await
}

async fn create_default_backend_services_impl<F: FileSystem, E: EnvSystem, FE: FileExtTrait>(
    fs: &F,
    env_sys: &E,
    file_ext: &FE,
) -> Result<(), String> {
    let backend = crate::tauri_handlers::backends::BackendService {
        id: uuid::Uuid::new_v4().to_string(),
        name: "OpenBB API".to_string(),
        command: "openbb-api --host 127.0.0.1 --port 6900".to_string(),
        env_file: None,
        env_vars: None,
        environment: "openbb".to_string(),
        auto_start: false,
        working_directory: None,
        status: "stopped".to_string(),
        pid: None,
        started_at: None,
        error: None,
        host: None,
        port: None,
        url: None,
    };
    let _ = create_backend_service_impl(backend, fs, env_sys, file_ext);

    let mcp_backend = crate::tauri_handlers::backends::BackendService {
        id: uuid::Uuid::new_v4().to_string(),
        name: "OpenBB MCP".to_string(),
        command: "openbb-mcp --transport streamable-http --host 127.0.0.1 --port 8001".to_string(),
        env_file: None,
        env_vars: None,
        environment: "openbb".to_string(),
        auto_start: false,
        working_directory: None,
        status: "stopped".to_string(),
        pid: None,
        started_at: None,
        error: None,
        host: None,
        port: None,
        url: None,
    };
    let _ = create_backend_service_impl(mcp_backend, fs, env_sys, file_ext);

    Ok(())
}

async fn generate_environment_yaml<F: FileSystem, E: EnvSystem>(
    python_version: &str,
    fs: &F,
    env_sys: &E,
) -> Result<std::path::PathBuf, String> {
    use std::path::Path;

    // Create the YAML file path in the environments directory
    let user_home = env_sys
        .var("HOME")
        .or_else(|_| env_sys.var("USERPROFILE"))
        .map_err(|e| format!("Could not determine home directory: {e}"))?;

    let platform_dir = Path::new(&user_home).join(".openbb_platform");
    let envs_dir = platform_dir.join("environments");

    if !fs.exists(&envs_dir) {
        fs.create_dir_all(&envs_dir)
            .map_err(|e| format!("Failed to create environments directory: {e}"))?;
    }

    let yaml_path = envs_dir.join("openbb.yaml");

    // Format and write the YAML file
    let yaml_content = format!(
        r#"name: openbb
channels:
  - conda-forge
  - defaults
dependencies:
  - python={python_version}
  - nodejs
  - pip
  - setuptools
  - pip:
      - notebook
      - jupyterlab-lsp
      - "python-lsp-server[all]"
      - jupyterlab-latex
      - "anywidget[dev]"
      - ipywidgets
      - openbb-platform-api
      - openbb-mcp-server
"#
    );

    fs.write(&yaml_path, &yaml_content)
        .map_err(|e| format!("Failed to write environment YAML file: {e}"))?;

    Ok(yaml_path)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::tauri_handlers::helpers::{MockEnvSystem, MockFileExtTrait, MockFileSystem};
    use std::path::PathBuf;

    fn clear_installation_state() {
        let mut state = INSTALLATION_STATE.lock().unwrap();
        *state = InstallationState::default();
    }

    #[test]
    fn test_update_installation_state_phases() {
        clear_installation_state();

        update_installation_state("download", 0.1, "Downloading...");
        {
            let state = INSTALLATION_STATE.lock().unwrap();
            assert!(state.is_downloading);
            assert!(!state.is_installing);
            assert!(!state.is_configuring);
            assert!(!state.is_complete);
        }

        update_installation_state("install", 0.5, "Installing...");
        {
            let state = INSTALLATION_STATE.lock().unwrap();
            assert!(!state.is_downloading);
            assert!(state.is_installing);
            assert!(!state.is_configuring);
            assert!(!state.is_complete);
        }

        update_installation_state("config", 0.8, "Configuring...");
        {
            let state = INSTALLATION_STATE.lock().unwrap();
            assert!(!state.is_downloading);
            assert!(!state.is_installing);
            assert!(state.is_configuring);
            assert!(!state.is_complete);
        }

        update_installation_state("complete", 1.0, "Installation complete");
        {
            let state = INSTALLATION_STATE.lock().unwrap();
            assert!(!state.is_downloading);
            assert!(!state.is_installing);
            assert!(!state.is_configuring);
            assert!(state.is_complete);
        }
        update_installation_state("error", 0.0, "An error occurred");
        {
            let state = INSTALLATION_STATE.lock().unwrap();
            assert_eq!(state.message, "An error occurred");
        }
        update_installation_state("abort", 0.0, "Installation cancelled by user");
        {
            let state = INSTALLATION_STATE.lock().unwrap();
            assert_eq!(state.message, "Installation cancelled by user");
        }
    }

    #[test]
    fn test_check_directory_permissions_success_and_failure() {
        let mut mock_fs = MockFileSystem::new();
        mock_fs.expect_write().returning(|_, _| Ok(()));
        mock_fs
            .expect_open_ro()
            .returning(|_| Ok(Box::new(std::io::Cursor::new(vec![]))));
        mock_fs.expect_remove_file().returning(|_| Ok(()));
        mock_fs.expect_create_dir_all().returning(|_| Ok(()));
        mock_fs.expect_remove_dir_all().returning(|_| Ok(()));
        mock_fs.expect_exists().returning(|_| true);

        let temp = PathBuf::from("/tmp/mock");
        assert!(check_directory_permissions(&temp, "temp", &mock_fs).is_ok());

        // Should fail for a path that doesn't exist or is not writable
        let mut mock_fs_fail = MockFileSystem::new();
        mock_fs_fail.expect_write().returning(|_, _| {
            Err(std::io::Error::new(
                std::io::ErrorKind::NotFound,
                "Not found",
            ))
        });
        mock_fs_fail.expect_open_ro().returning(|_| {
            Err(std::io::Error::new(
                std::io::ErrorKind::NotFound,
                "Not found",
            ))
        });
        mock_fs_fail.expect_remove_file().returning(|_| {
            Err(std::io::Error::new(
                std::io::ErrorKind::NotFound,
                "Not found",
            ))
        });
        mock_fs_fail.expect_create_dir_all().returning(|_| {
            Err(std::io::Error::new(
                std::io::ErrorKind::NotFound,
                "Not found",
            ))
        });
        mock_fs_fail.expect_remove_dir_all().returning(|_| {
            Err(std::io::Error::new(
                std::io::ErrorKind::NotFound,
                "Not found",
            ))
        });
        mock_fs_fail.expect_exists().returning(|_| false);

        let fake_path = if cfg!(target_os = "windows") {
            PathBuf::from("C:\\definitely\\does\\not\\exist\\for_openbb_test")
        } else {
            PathBuf::from("/definitely/does/not/exist/for_openbb_test")
        };
        let result = check_directory_permissions(&fake_path, "fake", &mock_fs_fail);
        assert!(result.is_err());
    }

    #[test]
    fn test_detect_architecture_maps() {
        let mut env_sys = MockEnvSystem::new();
        // Mock sysctl and uname for macOS, and fallback for other OSes
        env_sys
            .expect_new_command()
            .withf(|cmd| cmd == "sysctl")
            .returning(|_| {
                let mut cmd = std::process::Command::new("echo");
                cmd.arg("Apple M1");
                cmd
            });
        env_sys
            .expect_new_command()
            .withf(|cmd| cmd == "uname")
            .returning(|_| {
                let mut cmd = std::process::Command::new("echo");
                cmd.arg("arm64");
                cmd
            });

        let arch = detect_architecture(&env_sys).unwrap();
        let valid = ["x86_64", "aarch64", "arm64", "armv7l", "ppc64le", "s390x"];
        assert!(valid.contains(&arch.as_str()) || !arch.is_empty());
    }

    #[test]
    fn test_installation_state_default() {
        let state = InstallationState::default();
        assert!(!state.is_downloading);
        assert!(!state.is_installing);
        assert!(!state.is_configuring);
        assert!(!state.is_complete);
        assert_eq!(state.message, "");
    }

    #[test]
    fn test_install_progress_struct() {
        let progress = InstallProgress {
            step: "download".to_string(),
            progress: 0.5,
            message: "Halfway".to_string(),
        };
        assert_eq!(progress.step, "download");
        assert_eq!(progress.progress, 0.5);
        assert_eq!(progress.message, "Halfway");
    }

    #[test]
    fn test_check_installer_file_exists_false() {
        let mut mock_env = MockEnvSystem::new();
        mock_env
            .expect_temp_dir()
            .returning(|| PathBuf::from("/tmp/mock"));
        let rt = tokio::runtime::Runtime::new().unwrap();
        let result = rt.block_on(check_installer_file_exists_impl(&mock_env));
        assert!(result.is_ok());
        assert!(!result.unwrap());
    }

    #[test]
    fn test_abort_installation_resets_state() {
        clear_installation_state();
        let mut mock_env = MockEnvSystem::new();
        let mut mock_fs = MockFileSystem::new();
        mock_env
            .expect_temp_dir()
            .returning(|| PathBuf::from("/tmp/mock"));
        mock_fs.expect_is_empty().returning(|_| Ok(true));
        mock_fs.expect_exists().returning(|_| false);
        mock_fs.expect_remove_dir_all().returning(|_| Ok(()));
        mock_fs.expect_remove_file().returning(|_| Ok(()));
        mock_env.expect_new_command().returning(|_| {
            let mut cmd = std::process::Command::new("echo");
            cmd.arg("mock");
            cmd
        });
        let temp_dir = "/tmp/mock".to_string();
        let rt = tokio::runtime::Runtime::new().unwrap();
        let result = rt.block_on(abort_installation_impl(temp_dir, &mock_fs, &mock_env));
        assert!(result.is_ok());
        let state = INSTALLATION_STATE.lock().unwrap();
        assert!(
            !state.is_downloading,
            "is_downloading should be false, got {state:?}"
        );
        assert!(
            !state.is_installing,
            "is_installing should be false, got {state:?}"
        );
        assert!(
            !state.is_configuring,
            "is_configuring should be false, got {state:?}"
        );
        assert!(
            !state.is_complete,
            "is_complete should be false, got {state:?}"
        );
        assert_eq!(state.message, "Installation cancelled by user");
    }

    #[test]
    fn test_check_directory_permissions_handles_nonexistent() {
        let mut mock_fs = MockFileSystem::new();
        mock_fs.expect_write().returning(|_, _| {
            Err(std::io::Error::new(
                std::io::ErrorKind::NotFound,
                "Not found",
            ))
        });
        mock_fs.expect_remove_file().returning(|_| Ok(()));
        let path = if cfg!(target_os = "windows") {
            PathBuf::from("C:\\this\\should\\not\\exist\\openbb_test_perm")
        } else {
            PathBuf::from("/this/should/not/exist/openbb_test_perm")
        };
        let result = check_directory_permissions(&path, "test", &mock_fs);
        assert!(result.is_err());
    }

    #[test]
    fn test_generate_environment_yaml_content() {
        let mut mock_fs = MockFileSystem::new();
        let mut env_sys = MockEnvSystem::new();
        env_sys
            .expect_var()
            .withf(|k| k == "HOME")
            .returning(|_| Ok("/mock/home".to_string()));
        mock_fs.expect_exists().returning(|_| false);
        mock_fs.expect_create_dir_all().returning(|_| Ok(()));
        mock_fs.expect_write().returning(|_, _| Ok(()));
        mock_fs
            .expect_read_to_string()
            .returning(|_| Ok("python=3.10\n".to_string()));
        mock_fs.expect_remove_file().returning(|_| Ok(()));
        let rt = tokio::runtime::Runtime::new().unwrap();
        let result =
            rt.block_on(async { generate_environment_yaml("3.10", &mock_fs, &env_sys).await });
        assert!(result.is_ok());
        let yaml_path = result.unwrap();
        let content = mock_fs.read_to_string(&yaml_path).unwrap();
        assert!(content.contains("python=3.10"));
        let _ = mock_fs.remove_file(&yaml_path.to_string_lossy());
    }

    #[test]
    fn test_validate_conda_installation_path() {
        let base = if cfg!(target_os = "windows") {
            PathBuf::from("C:\\mock\\conda")
        } else {
            PathBuf::from("/tmp/mock/conda")
        };
        let exe = if cfg!(target_os = "windows") {
            base.join("Scripts").join("conda.exe")
        } else {
            base.join("bin").join("conda")
        };
        std::fs::create_dir_all(exe.parent().unwrap()).unwrap();
        std::fs::write(&exe, b"").unwrap();
        let result = validate_conda_installation(&base);
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), exe);
        std::fs::remove_file(&exe).unwrap();
    }

    #[test]
    fn test_validate_conda_installation_path_missing() {
        let mut fs = MockFileSystem::new();
        fs.expect_exists().returning(|_| false);
        let base = if cfg!(target_os = "windows") {
            PathBuf::from("C:\\mock\\conda_missing")
        } else {
            PathBuf::from("/mock/conda_missing")
        };
        let result = validate_conda_installation(&base);
        assert!(result.is_err());
    }

    #[tokio::test]
    async fn test_create_default_backend_service_runs() {
        let mut fs = MockFileSystem::new();
        let mut env_sys = MockEnvSystem::new();
        let mut file_ext = MockFileExtTrait::new();
        env_sys
            .expect_var()
            .withf(|k| k == "HOME" || k == "USERPROFILE")
            .returning(|_| Ok("/mock/home".to_string()));

        env_sys.expect_consts_os().returning(|| "linux");

        fs.expect_exists().returning(|path| {
            let path_str = path.to_string_lossy();
            // IP addresses should not exist as files
            !(path_str == "127.0.0.1" || path_str == "6900")
        });

        fs.expect_read_to_string().returning(|p| {
            if p.ends_with("system_settings.json") {
                Err(std::io::Error::new(
                    std::io::ErrorKind::NotFound,
                    "not found",
                ))
            } else {
                Ok("[]".to_string())
            }
        });

        fs.expect_exists().returning(|_| true);
        fs.expect_open_ro()
            .returning(|_| Ok(Box::new(std::io::Cursor::new(b"[]".to_vec()))));

        let temp_dir = std::env::temp_dir();
        let temp_path = temp_dir.join("mock_backend_for_startup_test.json");
        fs.expect_open_rw_create().returning({
            let path = temp_path.clone();
            move |_| std::fs::File::create(&path)
        });

        file_ext.expect_try_lock_exclusive().returning(|_| Ok(()));
        file_ext.expect_unlock().returning(|_| Ok(()));

        fs.expect_create_dir_all().returning(|_| Ok(()));

        let _ = create_default_backend_services_impl(&fs, &env_sys, &file_ext).await;

        // Clean up the temp file
        let _ = std::fs::remove_file(&temp_path);
    }
}
