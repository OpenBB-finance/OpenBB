use crate::tauri_handlers::backends::stop_all_backend_services;
use crate::tauri_handlers::jupyter::stop_all_jupyter_servers;
use serde_json::Value;
use std::fs;
use std::path::Path;
use std::process::Command;
use std::thread::sleep;
use std::time::Duration;
use tauri::Emitter;

#[cfg(windows)]
use std::os::windows::process::CommandExt;

#[tauri::command]
pub async fn uninstall_application(
    app_handle: tauri::AppHandle,
    window: tauri::Window,
    remove_user_data: bool,
    remove_settings: bool,
) -> Result<Option<String>, String> {
    use crate::tauri_handlers::helpers::{RealEnvSystem, RealFileExtTrait, RealFileSystem};
    log::debug!("Starting application uninstallation");

    // Helper function to emit progress events
    let emit_progress = |step: &str| {
        let _ = window.emit("uninstall_progress", step);
    };

    // STEP 1: Stop all running processes
    emit_progress("Stopping running services...");
    log::debug!("Stopping all running processes");

    if let Err(e) = stop_all_jupyter_servers(app_handle.clone()).await {
        log::warn!("Error stopping Jupyter servers: {e}");
    }
    if let Err(e) = stop_all_backend_services(
        app_handle.clone(),
        &RealFileSystem,
        &RealEnvSystem,
        &RealFileExtTrait,
    )
    .await
    {
        log::warn!("Error stopping backend services: {e}");
    }

    // STEP 2: Remove system integrations (autostart, etc.) to prevent automatic restarts
    emit_progress("Removing system integrations...");

    // Disable autostart
    #[cfg(target_os = "macos")]
    {
        if let Err(e) = crate::utils::autostart::macos_autostart::disable_autostart(&app_handle) {
            log::warn!("Failed to disable macOS autostart: {e}");
        } else {
            log::debug!("Successfully disabled macOS autostart");
        }
    }

    #[cfg(target_os = "windows")]
    {
        if let Err(e) =
            crate::utils::autostart::windows_autostart::disable_autostart(&app_handle.clone())
        {
            log::warn!("Failed to disable Windows autostart: {e}");
        } else {
            log::debug!("Successfully disabled Windows autostart");
        }
    }

    #[cfg(target_os = "linux")]
    {
        if let Err(e) =
            crate::utils::autostart::linux_autostart::disable_autostart(&app_handle.clone())
        {
            log::warn!("Failed to disable Linux autostart: {}", e);
        } else {
            log::debug!("Successfully disabled Linux autostart");
        }
    }

    remove_system_integrations()?;

    // STEP 3: First get all the necessary directory paths
    let home_dir = std::env::var("HOME")
        .or_else(|_| std::env::var("USERPROFILE"))
        .map_err(|e| format!("Could not determine home directory: {e}"))?;
    let platform_dir = Path::new(&home_dir).join(".openbb_platform");

    // Get installation directory from system_settings.json
    let install_dir = get_installation_directory_from_settings(&platform_dir)?;
    if install_dir.is_empty() {
        log::error!("Installation directory not found in settings");
        return Err("Installation directory not found in settings".into());
    }

    log::debug!("Found installation directory: {install_dir}");

    // STEP 4: FIRST PRIORITY - Remove conda environments and installation directory
    emit_progress("Removing conda environments...");

    // Remove conda environments synchronously
    if let Err(e) = remove_conda_environments(&install_dir, &window) {
        log::warn!("Error removing conda environments: {e}");
    }

    emit_progress("Removing installation directory...");
    let install_path = Path::new(&install_dir);
    if install_path.exists() {
        // Force close any potential conda processes
        if cfg!(target_os = "windows") {
            let mut taskkill_conda = Command::new("cmd");
            let mut taskkill_python = Command::new("cmd");

            #[cfg(windows)]
            {
                taskkill_conda.creation_flags(0x08000000); // CREATE_NO_WINDOW
                taskkill_python.creation_flags(0x08000000); // CREATE_NO_WINDOW
            }

            let _ = taskkill_conda
                .args(["/C", "taskkill", "/F", "/IM", "conda.exe", "/T"])
                .status();
            let _ = taskkill_python
                .args(["/C", "taskkill", "/F", "/IM", "python.exe", "/T"])
                .status();
        } else {
            let _ = Command::new("pkill").arg("-f").arg("conda").status();
            let _ = Command::new("pkill").arg("-f").arg("python").status();
        }

        // Make multiple attempts to remove the directory
        let removal_result = remove_installation_directory(install_path);

        // If removal failed, log but continue
        if let Err(e) = removal_result {
            log::warn!("Could not fully remove installation directory: {e}");
            // The system uninstaller will handle this later
        }
    } else {
        log::warn!(
            "Installation directory not found in settings - proceeding with partial cleanup"
        );
        emit_progress("Installation directory not found - proceeding with settings cleanup...");
    }
    // If the installation directory was not found, we can still proceed with uninstalling the UI.

    // STEP 5: Update system_settings.json to remove installation paths
    emit_progress("Updating system settings...");

    let system_settings_path = platform_dir.join("system_settings.json");
    if system_settings_path.exists() {
        log::debug!("Removing 'install_settings' key from system_settings.json");

        let content = match fs::read_to_string(&system_settings_path) {
            Ok(content) => content,
            Err(e) => {
                log::warn!("Failed to read system_settings.json: {e}");
                return Err(format!("Failed to read system_settings.json: {e}"));
            }
        };

        let mut json: Value = match serde_json::from_str(&content) {
            Ok(json) => json,
            Err(e) => {
                log::warn!("Failed to parse system_settings.json: {e}");
                return Err(format!("Failed to parse system_settings.json: {e}"));
            }
        };

        if json.is_object()
            && let Some(obj) = json.as_object_mut()
        {
            // Remove YAML files listed in environments
            if let Some(envs) = obj.get("environments")
                && let Some(env_map) = envs.as_object()
            {
                for (_env_name, env_val) in env_map {
                    if let Some(env_file) = env_val.get("environment_file").and_then(|v| v.as_str())
                    {
                        let env_file_path = Path::new(env_file);
                        if env_file_path.exists() {
                            log::debug!(
                                "Removing environment YAML file: {}",
                                env_file_path.display()
                            );
                            if let Err(e) = fs::remove_file(env_file_path) {
                                log::warn!(
                                    "Failed to remove environment YAML file {}: {}",
                                    env_file_path.display(),
                                    e
                                );
                            }
                        }
                    }
                }
            }
            // Remove the environments key
            obj.remove("environments");
            obj.remove("install_settings");

            let updated_content = serde_json::to_string_pretty(&json).unwrap_or_default();
            if let Err(e) = fs::write(&system_settings_path, updated_content) {
                log::warn!("Failed to write updated system_settings.json: {e}");
            }
        }
    } // STEP 6: Remove settings if requested
    if remove_settings {
        emit_progress("Removing settings directory...");
        log::debug!("Removing settings directory: {}", platform_dir.display());
        if platform_dir.exists()
            && let Err(e) = fs::remove_dir_all(&platform_dir)
        {
            log::warn!("Failed to remove settings directory: {e}");
        }
    } else {
        // Clear just the environments folder if we're keeping settings
        let environments_dir = platform_dir.join("environments");
        if environments_dir.exists() {
            log::debug!(
                "Clearing environments folder: {}",
                environments_dir.display()
            );
            if let Err(e) = fs::remove_dir_all(&environments_dir) {
                log::warn!("Failed to clear environments folder: {e}");
            }
        }
    }

    // STEP 7: Remove user data if requested
    if remove_user_data {
        emit_progress("Removing user data...");
        let user_data_dir = platform_dir.join("user_data");
        if user_data_dir.exists() {
            log::debug!("Removing user data directory: {}", user_data_dir.display());
            if let Err(e) = fs::remove_dir_all(&user_data_dir) {
                log::warn!("Failed to remove user data directory: {e}");
            }
        }
    }

    // STEP 8: Wait to ensure operations complete
    emit_progress("Finalizing uninstallation...");
    sleep(Duration::from_secs(3));

    // STEP 9: Run system uninstaller if available on Windows
    #[cfg(target_os = "windows")]
    {
        emit_progress("Running system uninstaller...");
        let current_exe = std::env::current_exe()
            .map_err(|e| format!("Failed to get current executable path: {e}"))?;
        let app_dir = current_exe
            .parent()
            .ok_or_else(|| "Failed to determine application directory".to_string())?;

        // Run the system uninstaller and wait for it to complete - THIS IS THE ONLY THING WE NEED
        if let Err(e) = run_windows_system_uninstaller(app_dir, true) {
            log::warn!("Failed to run system uninstaller: {e}");
        }

        // Wait a moment to ensure operations complete
        sleep(Duration::from_secs(2));
    }

    emit_progress("Removing application data...");

    #[cfg(not(target_os = "windows"))]
    {
        // On non-Windows platforms, manually remove the appropriate folder
        let app_data_dir = if cfg!(target_os = "macos") {
            // On macOS: ~/Library/Application Support/co.openbb.platform
            Path::new(&home_dir)
                .join("Library")
                .join("Application Support")
                .join("co.openbb.platform")
        } else {
            // On Linux: ~/.config/co.openbb.platform
            Path::new(&home_dir)
                .join(".config")
                .join("co.openbb.platform")
        };

        if app_data_dir.exists() {
            log::debug!(
                "Removing application data directory: {}",
                app_data_dir.display()
            );
            if let Err(e) = fs::remove_dir_all(&app_data_dir) {
                log::warn!("Failed to remove application data directory: {e}");
            }
        }
    }

    emit_progress("Uninstallation complete. The application will now close.");

    #[cfg(target_os = "macos")]
    {
        use tauri::Manager;

        log::debug!("Setting up cleanup script before app exit");

        match std::env::current_exe() {
            Ok(exe_path) => {
                log::debug!("Current exe path: {}", exe_path.display());

                // Find the .app bundle
                let mut app_bundle = exe_path.clone();
                let mut found_app = false;

                for _ in 0..5 {
                    if let Some(parent) = app_bundle.parent() {
                        app_bundle = parent.to_path_buf();
                        if app_bundle.extension().and_then(|s| s.to_str()) == Some("app") {
                            log::debug!("Found .app bundle: {}", app_bundle.display());
                            found_app = true;
                            break;
                        }
                    } else {
                        break;
                    }
                }

                if found_app {
                    let app_name = app_bundle
                        .file_name()
                        .and_then(|n| n.to_str())
                        .unwrap_or("OpenBB Platform");

                    // Create script that waits for THIS process to die, then deletes the app
                    let cleanup_script = format!(
                        r#"#!/bin/bash
echo "Cleanup script started, waiting for app to exit..." > /tmp/openbb_cleanup.log

# Wait for the specific process to exit
while pgrep -f "{}" > /dev/null 2>&1; do
    sleep 1
done

echo "App process has exited, removing app bundle..." >> /tmp/openbb_cleanup.log
sleep 3

# Remove the entire .app bundle
rm -rf "{}"

# Remove the application support directories
rm -rf "$HOME/Library/Logs/co.openbb.platform"
rm -rf "$HOME/Library/Caches/co.openbb.platform"
rm -rf "$HOME/Library/WebKit/co.openbb.platform"
rm -rf "$HOME/Library/WebKit/openbb-platform"
rm -rf "$HOME/Library/Application Scripts/group.co.openbb.platform"

if [ $? -eq 0 ]; then
    echo "Successfully removed app bundle" >> /tmp/openbb_cleanup.log
    osascript -e 'display notification "OpenBB Platform completely removed" with title "Uninstall Complete"' 2>/dev/null
else
    echo "Failed to remove app bundle" >> /tmp/openbb_cleanup.log
fi

# Remove this script
rm -f "$0"
"#,
                        app_name,
                        app_bundle.display()
                    );

                    let script_path = "/tmp/openbb_uninstall_cleanup.sh";
                    if std::fs::write(script_path, cleanup_script).is_ok() {
                        let _ = std::process::Command::new("chmod")
                            .arg("+x")
                            .arg(script_path)
                            .status();

                        // Launch the cleanup script - it will wait for us to exit
                        if std::process::Command::new("bash")
                            .arg(script_path)
                            .spawn()
                            .is_ok()
                        {
                            log::debug!(
                                "Cleanup script launched - it will remove the app after we exit"
                            );
                        }
                    }
                }
            }
            Err(e) => {
                log::error!("Failed to get exe path: {e}");
            }
        }

        log::debug!("Now exiting application - cleanup script will handle app removal");

        // NOW close the window and exit the app
        if let Some(window) = app_handle.get_webview_window("main") {
            let _ = window.close();
        }

        // Exit the process - the cleanup script will detect this and remove the .app bundle
        std::process::exit(0);
    }
    #[allow(unreachable_code)]
    Ok(None)
}

// Function to get installation directory from system_settings.json
fn get_installation_directory_from_settings(platform_dir: &Path) -> Result<String, String> {
    let system_settings_path = platform_dir.join("system_settings.json");
    if !system_settings_path.exists() {
        return Ok(String::new());
    }

    let content = fs::read_to_string(&system_settings_path)
        .map_err(|e| format!("Failed to read system_settings.json: {e}"))?;

    let json: Value = serde_json::from_str(&content)
        .map_err(|e| format!("Failed to parse system_settings.json: {e}"))?;

    // Look for the correct key "installation_directory" inside "install_settings"
    let install_dir = json
        .get("install_settings")
        .and_then(|settings| settings.get("installation_directory"))
        .and_then(|dir| dir.as_str())
        .unwrap_or("");

    if install_dir.is_empty() {
        log::warn!("Installation directory not found in settings");
        log::debug!("Settings content: {json:?}");
    } else {
        log::debug!("Found installation directory in settings: {install_dir}");
    }

    Ok(install_dir.to_string())
}

// Function to remove conda environments SYNCHRONOUSLY
fn remove_conda_environments(install_dir: &str, window: &tauri::Window) -> Result<(), String> {
    #[cfg(target_os = "windows")]
    {
        // On Windows, use the proper Miniforge3 uninstaller
        let uninstaller_path = Path::new(install_dir)
            .join("conda")
            .join("Uninstall-Miniforge3.exe");

        log::debug!(
            "Looking for Miniforge3 uninstaller at: {}",
            uninstaller_path.display()
        );

        if uninstaller_path.exists() {
            let _ = window.emit("uninstall_progress", "Running Miniforge3 uninstaller...");
            log::debug!(
                "Running Miniforge3 uninstaller: {}",
                uninstaller_path.display()
            );

            let mut uninstaller_cmd = Command::new(&uninstaller_path);
            #[cfg(windows)]
            {
                uninstaller_cmd.creation_flags(0x08000000); // CREATE_NO_WINDOW
            }

            // Run the uninstaller with silent mode
            let status = uninstaller_cmd
                .args(["/S"]) // Silent uninstall
                .status()
                .map_err(|e| format!("Failed to execute Miniforge3 uninstaller: {e}"))?;

            if status.success() {
                log::debug!("Miniforge3 uninstaller completed successfully");
                let _ = window.emit("uninstall_progress", "Miniforge3 uninstaller completed");
                return Ok(());
            } else {
                log::warn!("Miniforge3 uninstaller failed with status: {status}");
                // Continue with manual removal as fallback
            }
        } else {
            log::warn!(
                "Miniforge3 uninstaller not found at {}",
                uninstaller_path.display()
            );
            // Continue with manual removal as fallback
        }
    }

    // Fallback: Manual conda environment removal (for non-Windows or if uninstaller fails)
    let conda_path = if cfg!(target_os = "windows") {
        Path::new(install_dir)
            .join("conda")
            .join("Scripts")
            .join("conda.exe")
    } else {
        Path::new(install_dir)
            .join("conda")
            .join("bin")
            .join("conda")
    };

    log::debug!("Conda path: {}", conda_path.display());
    if !conda_path.exists() {
        log::warn!("Conda executable not found at {}", conda_path.display());
        return Ok(()); // Continue with uninstallation even if conda isn't found
    }

    log::debug!("Conda found at: {}", conda_path.display());

    // Get environments directory
    let env_dir = Path::new(install_dir).join("conda").join("envs");
    if !env_dir.exists() {
        log::debug!("No environments directory found at {}", env_dir.display());
        return Ok(());
    }

    // List directories in the environments directory directly
    let mut environments = Vec::new();
    match std::fs::read_dir(&env_dir) {
        Ok(entries) => {
            for entry in entries.flatten() {
                if let Ok(file_type) = entry.file_type()
                    && file_type.is_dir()
                    && let Some(name) = entry.file_name().to_str()
                    && name.to_lowercase() != "base"
                {
                    environments.push(name.to_string());
                }
            }
        }
        Err(e) => {
            log::warn!("Failed to read environments directory: {e}");
            return Ok(()); // Continue with uninstallation even if we can't read environments
        }
    }

    // Skip base environment and remove individual environments
    for env_name in environments {
        let _ = window.emit(
            "uninstall_progress",
            format!("Removing conda environment: {env_name}..."),
        );
        log::debug!("Removing conda environment: {env_name}");

        let mut cmd = if cfg!(target_os = "windows") {
            let mut c = Command::new("cmd");
            #[cfg(windows)]
            {
                c.creation_flags(0x08000000); // CREATE_NO_WINDOW
            }
            c.args([
                "/C",
                conda_path.to_str().unwrap(),
                "env",
                "remove",
                "--name",
                &env_name,
                "--yes",
            ]);
            c
        } else {
            let mut c = Command::new(conda_path.to_str().unwrap());
            c.args(["env", "remove", "--name", &env_name, "--yes"]);
            c
        };

        log::debug!("Executing command: {cmd:?}");

        let output = cmd
            .output()
            .map_err(|e| format!("Failed to execute conda: {e}"))?;

        if !output.status.success() {
            log::warn!(
                "Failed to remove conda environment {}: {}",
                env_name,
                String::from_utf8_lossy(&output.stderr)
            );
            log::warn!("Stdout: {}", String::from_utf8_lossy(&output.stdout));
        } else {
            log::debug!("Successfully removed conda environment: {env_name}");
        }
    }

    Ok(())
}

fn remove_installation_directory(install_path: &Path) -> Result<(), String> {
    log::debug!(
        "Removing installation directory: {}",
        install_path.display()
    );

    let result = fs::remove_dir_all(install_path);
    if result.is_ok() {
        log::debug!("Successfully removed installation directory");
        return Ok(());
    }

    log::warn!("Initial removal attempt failed: {result:?}");
    sleep(Duration::from_secs(1));

    #[cfg(target_os = "windows")]
    {
        log::debug!("Attempting Windows-specific removal");
        let mut cmd = Command::new("cmd");
        #[cfg(windows)]
        {
            cmd.creation_flags(0x08000000); // CREATE_NO_WINDOW
        }
        let output = cmd
            .args(["/C", "rd", "/s", "/q", install_path.to_str().unwrap()])
            .output();

        if let Ok(o) = output
            && o.status.success()
        {
            log::debug!("Successfully removed with Windows rd command");
            return Ok(());
        }
    }

    #[cfg(not(target_os = "windows"))]
    {
        log::debug!("Attempting Unix-specific removal");
        let output = Command::new("rm")
            .args(["-rf", install_path.to_str().unwrap()])
            .output();

        if let Ok(o) = output
            && o.status.success()
        {
            log::debug!("Successfully removed with rm command");
            return Ok(());
        }
    }

    if install_path.exists() {
        Err("Could not fully remove installation directory".into())
    } else {
        Ok(())
    }
}

fn remove_system_integrations() -> Result<(), String> {
    #[cfg(target_os = "windows")]
    {
        log::debug!("Removing Windows-specific system integrations");

        // Remove from all possible startup locations
        let startup_keys = [
            "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
            "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
        ];

        let entry_names = [
            "OpenBBPlatform",
            "OpenBB Platform",
            "OpenBB",
            "opebb-platform.exe",
            "co.openbb.platform",
        ];

        for key in startup_keys.iter() {
            for name in entry_names.iter() {
                let mut reg_cmd = Command::new("reg");
                #[cfg(windows)]
                {
                    reg_cmd.creation_flags(0x08000000); // CREATE_NO_WINDOW
                }
                let _ = reg_cmd.args(["delete", key, "/v", name, "/f"]).output();
            }
        }

        // Also attempt to remove any startup item with "openbb" in its path
        if let Ok(local_app_data) = std::env::var("LOCALAPPDATA") {
            let startup_dir = Path::new(&local_app_data)
                .join("Microsoft\\Windows\\Start Menu\\Programs\\Startup");
            if startup_dir.exists()
                && let Ok(entries) = fs::read_dir(&startup_dir)
            {
                for entry in entries.flatten() {
                    let path = entry.path();
                    if let Some(path_str) = path.to_str()
                        && path_str.to_lowercase().contains("openbb")
                    {
                        log::debug!("Removing startup shortcut: {path_str}");
                        let _ = fs::remove_file(&path);
                    }
                }
            }
        }
    }

    #[cfg(target_os = "macos")]
    {
        log::debug!("Removing macOS-specific system integrations");
        let home_dir = std::env::var("HOME").unwrap_or_else(|_| "".to_string());
        let plist_path =
            Path::new(&home_dir).join("Library/LaunchAgents/com.openbb.platform.plist");
        if plist_path.exists() {
            let _ = Command::new("launchctl")
                .args(["unload", plist_path.to_str().unwrap()])
                .output();
            let _ = fs::remove_file(&plist_path);
        }
    }

    #[cfg(target_os = "linux")]
    {
        log::debug!("Removing Linux-specific system integrations");
        let home_dir = std::env::var("HOME").unwrap_or_else(|_| "".to_string());
        let service_path =
            Path::new(&home_dir).join(".config/systemd/user/openbb-platform.service");
        if service_path.exists() {
            let _ = Command::new("systemctl")
                .args(["--user", "stop", "openbb-platform.service"])
                .output();
            let _ = Command::new("systemctl")
                .args(["--user", "disable", "openbb-platform.service"])
                .output();
            let _ = fs::remove_file(&service_path);
            let _ = Command::new("systemctl")
                .args(["--user", "daemon-reload"])
                .output();
        }
    }

    Ok(())
}

#[cfg(target_os = "windows")]
fn run_windows_system_uninstaller(app_dir: &Path, remove_user_data: bool) -> Result<(), String> {
    // Create a delayed script that will run AFTER our process exits!
    // This is critical because uninstall.exe will kill the current process

    if let Ok(temp_dir) = std::env::var("TEMP") {
        // Put the script in the root of TEMP directory rather than inside LocalAppData
        let script_path = Path::new(&temp_dir).join("openbb_uninstall.bat");
        let mut uninstall_paths = Vec::new();

        // Check in app_dir
        let app_uninstaller = app_dir.join("uninstall.exe");
        if app_uninstaller.exists() {
            log::debug!(
                "Found uninstaller in app directory: {}",
                app_uninstaller.display()
            );
            uninstall_paths.push(app_uninstaller);
        }

        // Also check in LocalAppData
        if let Ok(local_app_data) = std::env::var("LOCALAPPDATA") {
            let localappdata_uninstaller = Path::new(&local_app_data)
                .join("OpenBB Platform")
                .join("uninstall.exe");
            if localappdata_uninstaller.exists() {
                log::debug!(
                    "Found uninstaller in LocalAppData: {}",
                    localappdata_uninstaller.display()
                );
                uninstall_paths.push(localappdata_uninstaller);
            }
        }

        if uninstall_paths.is_empty() {
            log::warn!("No uninstall.exe found in any location!");
            return Err("Could not find uninstall.exe".to_string());
        }

        // Use the first found uninstaller (typically the app_dir one)
        let primary_uninstaller = uninstall_paths[0].to_str().unwrap();

        // Create a batch file to run the uninstaller AFTER our process exits
        let remove_flag = if remove_user_data {
            "/removeUserData=true"
        } else {
            ""
        };

        let batch_content = format!(
            "@echo off\r\n\
            echo Waiting for OpenBB processes to exit...\r\n\
            timeout /t 5 > nul\r\n\
            taskkill /F /IM openbb-platform.exe /T > nul 2>&1\r\n\
            timeout /t 2 > nul\r\n\
            \r\n\
            echo Running uninstaller...\r\n\
            start /wait \"\" \"{primary_uninstaller}\" /S {remove_flag}\r\n\
            \r\n\
            CD /D \"%TEMP%\"\r\n\
            \r\n\
            echo Cleaning up remaining folders...\r\n\
            if exist \"%LOCALAPPDATA%\\OpenBB Platform\" (\r\n\
                rmdir /s /q \"%LOCALAPPDATA%\\OpenBB Platform\"\r\n\
            )\r\n\
            \r\n\
            if exist \"%LOCALAPPDATA%\\co.openbb.platform\" (\r\n\
                rmdir /s /q \"%LOCALAPPDATA%\\co.openbb.platform\"\r\n\
            )\r\n\
            \r\n\
            echo All done. Press any key to exit.\r\n\
            pause > nul\r\n\
            exit\r\n"
        );

        log::debug!(
            "Creating delayed uninstaller script: {}",
            script_path.display()
        );
        if let Err(e) = fs::write(&script_path, batch_content) {
            log::error!("Failed to write uninstaller script: {e}");
            return Err(format!("Failed to write uninstaller script: {e}"));
        }

        log::debug!("Launching delayed uninstaller script");
        let mut cmd = Command::new("cmd");
        // Do NOT hide this window
        if let Err(e) = cmd
            .args([
                "/C",
                "start",
                "OpenBB Platform Final Cleanup",
                script_path.to_str().unwrap(),
            ])
            .spawn()
        {
            log::error!("Failed to launch uninstaller script: {e}");
            return Err(format!("Failed to launch uninstaller script: {e}"));
        }

        log::debug!("Uninstaller will run after application exits");
        return Ok(());
    }

    Err("Failed to get TEMP directory".to_string())
}
