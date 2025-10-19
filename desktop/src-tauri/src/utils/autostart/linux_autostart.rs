use std::fs::{self, File};
use std::io::Write;
use std::path::PathBuf;
use tauri::AppHandle;

pub fn is_autostart_enabled(app_handle: &AppHandle) -> Result<bool, String> {
    let desktop_file_path = get_autostart_desktop_file_path(app_handle)?;
    Ok(desktop_file_path.exists())
}

pub fn enable_autostart(app_handle: &AppHandle) -> Result<(), String> {
    let autostart_dir = get_autostart_directory()?;

    // Create autostart directory if it doesn't exist
    if !autostart_dir.exists() {
        fs::create_dir_all(&autostart_dir)
            .map_err(|e| format!("Failed to create autostart directory: {}", e))?;
    }

    // Get path to the desktop file
    let desktop_file_path = get_autostart_desktop_file_path(app_handle)?;

    // Get the path to the executable
    let executable_path =
        std::env::current_exe().map_err(|e| format!("Failed to get executable path: {}", e))?;

    if !executable_path.exists() {
        return Err(format!("Executable not found at {:?}", executable_path));
    }

    // Create desktop entry file
    let desktop_file_content = format!(
        r#"[Desktop Entry]
Type=Application
Name={}
Exec="{}"
Terminal=false
X-GNOME-Autostart-enabled=true
"#,
        app_handle.package_info().name,
        executable_path
            .to_str()
            .ok_or("Failed to convert executable path to string")?
    );

    // Write desktop file
    let mut file = File::create(&desktop_file_path)
        .map_err(|e| format!("Failed to create desktop file: {}", e))?;

    file.write_all(desktop_file_content.as_bytes())
        .map_err(|e| format!("Failed to write desktop file content: {}", e))?;

    // Make the desktop file executable
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let mut permissions = fs::metadata(&desktop_file_path)
            .map_err(|e| format!("Failed to get file metadata: {}", e))?
            .permissions();

        permissions.set_mode(0o755);

        fs::set_permissions(&desktop_file_path, permissions)
            .map_err(|e| format!("Failed to set file permissions: {}", e))?;
    }

    Ok(())
}

pub fn disable_autostart(app_handle: &AppHandle) -> Result<(), String> {
    let desktop_file_path = get_autostart_desktop_file_path(app_handle)?;

    if desktop_file_path.exists() {
        fs::remove_file(&desktop_file_path)
            .map_err(|e| format!("Failed to remove desktop file: {}", e))?;
    }

    Ok(())
}

fn get_autostart_directory() -> Result<PathBuf, String> {
    // Get user's config directory (usually ~/.config)
    let config_dir = dirs::config_dir().ok_or("Failed to determine user config directory")?;

    // Standard XDG autostart directory
    Ok(config_dir.join("autostart"))
}

fn get_autostart_desktop_file_path(app_handle: &AppHandle) -> Result<PathBuf, String> {
    let autostart_dir = get_autostart_directory()?;
    let app_name = app_handle.package_info().name.clone();

    Ok(autostart_dir.join(format!("{}.desktop", app_name)))
}
