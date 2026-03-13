// This module provides functionality to manage autostart settings on macOS using only system services.
use std::path::PathBuf;
use std::process::Command;
use tauri::{AppHandle, Runtime};

// Get application path for macOS - prioritize .app bundle over direct executable
fn get_app_path<R: Runtime>(_app_handle: &AppHandle<R>) -> Result<PathBuf, String> {
    // First try to find the .app bundle to preserve the icon
    let exe_path = std::env::current_exe()
        .map_err(|e| format!("Failed to get current executable path: {e}"))?;

    // Check if we're inside an .app bundle structure
    let mut path = exe_path.clone();
    let mut found_app_bundle = false;

    // Navigate up to look for .app bundle
    for _ in 0..5 {
        // Limit the search depth
        if let Some(parent) = path.parent() {
            path = parent.to_path_buf();

            if path.extension().is_some_and(|ext| ext == "app") {
                log::debug!("Found .app bundle at: {}", path.display());
                found_app_bundle = true;
                break;
            }
        } else {
            break;
        }
    }

    if found_app_bundle {
        // Use the .app bundle to preserve icon
        return Ok(path);
    }

    // If no .app bundle was found, use the executable directly
    log::debug!(
        "No .app bundle found, using executable: {}",
        exe_path.display()
    );
    Ok(exe_path)
}

/// Enable autostart using pure AppleScript on macOS
pub fn enable_autostart<R: Runtime>(app_handle: &AppHandle<R>) -> Result<(), String> {
    // Get the path to the application
    let app_path = get_app_path(app_handle)?;
    let app_path_str = app_path
        .to_str()
        .ok_or_else(|| "Invalid app path".to_string())?;

    log::debug!("Enabling autostart for: {app_path_str}");

    // First check if it's already in login items
    let check_script = format!(
        r#"tell application "System Events"
            set loginItems to login items
            repeat with loginItem in loginItems
                try
                    set itemPath to path of loginItem as string
                    if itemPath contains "{}" then
                        return true
                    end if
                end try
            end repeat
            return false
        end tell"#,
        app_path_str.replace(r#"""#, r#"\""#)
    );

    let output = Command::new("osascript")
        .arg("-e")
        .arg(&check_script)
        .output()
        .map_err(|e| format!("Failed to execute AppleScript: {e}"))?;

    let stdout = String::from_utf8_lossy(&output.stdout).trim().to_string();
    log::debug!("Check if already in login items: {stdout}");

    if stdout == "true" {
        log::debug!("App is already in login items");
        return Ok(());
    }

    // Add to login items with AppleScript - set the display name to "OpenBB Platform" and add --autostart argument
    let script = format!(
        r#"tell application "System Events"
            make new login item at end with properties {{path:"{}", hidden:false, name:"OpenBB Platform"}}
        end tell"#,
        app_path_str.replace(r#"""#, r#"\""#)
    );

    let output = Command::new("osascript")
        .arg("-e")
        .arg(&script)
        .output()
        .map_err(|e| format!("Failed to execute AppleScript: {e}"))?;

    if !output.status.success() {
        let error = String::from_utf8_lossy(&output.stderr);
        log::error!("AppleScript error: {error}");
        return Err(format!("Failed to add to login items: {error}"));
    }

    log::debug!("Successfully added to login items");
    Ok(())
}

/// Disable autostart using pure AppleScript on macOS
pub fn disable_autostart<R: Runtime>(app_handle: &AppHandle<R>) -> Result<(), String> {
    log::debug!("Disabling autostart");

    // Get the app path to identify it in login items
    let app_path = get_app_path(app_handle)?;
    let app_path_str = app_path
        .to_str()
        .ok_or_else(|| "Invalid app path".to_string())?;

    log::debug!("Disabling autostart for: {app_path_str}");

    // Remove login items that match the app path or have known app names or binary names
    let script = format!(
        r#"tell application "System Events"
        set loginItems to login items
        set itemsToRemove to {{}}

        repeat with loginItem in loginItems
            try
                set itemPath to path of loginItem as string
                set itemName to name of loginItem as string

                -- Check if path matches or name matches known app names or binary names
                if itemPath contains "{}" or itemName = "OpenBB Platform" or itemName = "Open Data Platform" or itemName = "app" or itemName = "openbb-platform" then
                    set end of itemsToRemove to loginItem
                end if
            end try
        end repeat

        -- Remove found items (iterate in reverse to avoid index issues)
        repeat with i from (count of itemsToRemove) to 1 by -1
            try
                delete item i of itemsToRemove
            end try
        end repeat

        return count of itemsToRemove
        end tell"#,
        app_path_str.replace(r#"""#, r#"\""#)
    );

    let output = Command::new("osascript")
        .arg("-e")
        .arg(&script)
        .output()
        .map_err(|e| format!("Failed to execute AppleScript: {e}"))?;

    if !output.status.success() {
        let error = String::from_utf8_lossy(&output.stderr);
        log::error!("AppleScript error: {error}");
        return Err(format!("Failed to remove from login items: {error}"));
    }

    let stdout = String::from_utf8_lossy(&output.stdout).trim().to_string();
    let removed_count = stdout.parse::<i32>().unwrap_or(0);
    log::debug!("Successfully removed {} login items", removed_count);

    Ok(())
}

/// Check if autostart is enabled using pure AppleScript on macOS
pub fn is_autostart_enabled<R: Runtime>(app_handle: &AppHandle<R>) -> Result<bool, String> {
    // Get the app path to identify it in login items
    let app_path = get_app_path(app_handle)?;
    let app_path_str = app_path
        .to_str()
        .ok_or_else(|| "Invalid app path".to_string())?;

    log::debug!("Checking login items for: {app_path_str}");

    // Create AppleScript to check if app is in login items
    let script = format!(
        r#"tell application "System Events"
            set loginItems to login items
            repeat with loginItem in loginItems
                try
                    set itemPath to path of loginItem as string
                    if itemPath contains "{}" then
                        return true
                    end if
                end try
            end repeat
            return false
        end tell"#,
        app_path_str.replace(r#"""#, r#"\""#)
    );

    let output = Command::new("osascript")
        .arg("-e")
        .arg(&script)
        .output()
        .map_err(|e| format!("Failed to execute AppleScript: {e}"))?;

    if !output.status.success() {
        let error = String::from_utf8_lossy(&output.stderr);
        log::error!("AppleScript error: {error}");
        return Err(format!("Failed to check login items: {error}"));
    }

    let stdout = String::from_utf8_lossy(&output.stdout).trim().to_string();
    let is_enabled = stdout == "true";
    log::debug!("App is in login items: {is_enabled}");

    Ok(is_enabled)
}
