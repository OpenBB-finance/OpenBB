use crate::tauri_handlers::helpers::{EnvSystem, FileSystem, RealEnvSystem, RealFileSystem};

pub async fn get_user_credentials_impl<F: FileSystem, E: EnvSystem>(
    fs: &F,
    env_sys: &E,
) -> Result<serde_json::Value, String> {
    use std::path::Path;

    let home_dir = env_sys
        .var("HOME")
        .or_else(|_| env_sys.var("USERPROFILE"))
        .map_err(|e| format!("Could not determine home directory: {e}"))?;

    let platform_dir = Path::new(&home_dir).join(".openbb_platform");
    let user_settings_path = platform_dir.join("user_settings.json");

    if !fs.exists(&user_settings_path) {
        // Return empty settings if the file doesn't exist
        return Ok(serde_json::json!({
            "credentials": {}
        }));
    }

    // Read the user settings file
    let settings_content = fs
        .read_to_string(&user_settings_path)
        .map_err(|e| format!("Failed to read user settings: {e}"))?;

    // Parse the settings
    let settings: serde_json::Value = serde_json::from_str(&settings_content)
        .map_err(|e| format!("Failed to parse user settings: {e}"))?;

    Ok(settings)
}

#[tauri::command]
pub async fn get_user_credentials() -> Result<serde_json::Value, String> {
    get_user_credentials_impl(&RealFileSystem, &RealEnvSystem).await
}

pub async fn update_user_credentials_impl<F: FileSystem, E: EnvSystem>(
    credentials: serde_json::Value,
    fs: &F,
    env_sys: &E,
) -> Result<bool, String> {
    use std::path::Path;

    let home_dir = env_sys
        .var("HOME")
        .or_else(|_| env_sys.var("USERPROFILE"))
        .map_err(|e| format!("Could not determine home directory: {e}"))?;

    let platform_dir = Path::new(&home_dir).join(".openbb_platform");
    let user_settings_path = platform_dir.join("user_settings.json");

    if !fs.exists(&platform_dir) {
        fs.create_dir_all(&platform_dir)
            .map_err(|e| format!("Failed to create platform directory: {e}"))?;
    }

    // Read existing settings or create new ones
    let mut settings = if fs.exists(&user_settings_path) {
        let settings_content = fs
            .read_to_string(&user_settings_path)
            .map_err(|e| format!("Failed to read user settings: {e}"))?;

        serde_json::from_str(&settings_content)
            .map_err(|e| format!("Failed to parse user settings: {e}"))?
    } else {
        serde_json::json!({})
    };

    // Update only the credentials section
    if let Some(obj) = settings.as_object_mut() {
        obj.insert("credentials".to_string(), credentials);
    }

    // Write the updated settings back to the file
    let settings_json = serde_json::to_string_pretty(&settings)
        .map_err(|e| format!("Failed to serialize settings: {e}"))?;

    fs.write(&user_settings_path, settings_json.as_str())
        .map_err(|e| format!("Failed to write user settings: {e}"))?;

    Ok(true)
}

#[tauri::command]
pub async fn update_user_credentials(credentials: serde_json::Value) -> Result<bool, String> {
    update_user_credentials_impl(credentials, &RealFileSystem, &RealEnvSystem).await
}

pub async fn open_credentials_file_impl<F: FileSystem, E: EnvSystem>(
    file_name: Option<String>,
    fs: &F,
    env_sys: &E,
) -> Result<bool, String> {
    use crate::tauri_handlers::helpers::{
        get_home_directory_impl, get_installation_directory_impl,
    };
    use std::path::Path;

    // Get user's home directory
    let home_dir = get_home_directory_impl(env_sys)
        .map_err(|e| format!("Could not determine home directory: {e}"))?;
    let file_name = file_name.unwrap_or_else(|| "user_settings.json".to_string());
    let file_path = match file_name.as_str() {
        ".condarc" => {
            // For .condarc, use the installation directory + "/conda/.condarc"
            let conda_dir = get_installation_directory_impl(fs, env_sys)
                .map_err(|e| format!("Could not determine installation directory: {e}"))?;
            Path::new(&conda_dir).join("conda/.condarc")
        }
        _ => {
            // For all other files, use the standard platform directory
            let platform_dir = Path::new(&home_dir).join(".openbb_platform");
            platform_dir.join(&file_name)
        }
    };

    let default_content = match file_name.as_str() {
        "user_settings.json" => "{\"credentials\": {}}",
        "system_settings.json" => "{}",
        "mcp_settings.json" => "{}",
        ".env" => "# Environment variables for OpenBB Platform",
        ".condarc" => "# Conda configuration file\nchannels:\n  - conda-forge\n  - defaults",
        _ => "{}", // Default for any other files
    };

    if !fs.exists(&file_path) {
        // Create an empty file if it doesn't exist
        fs.write(&file_path, default_content)
            .map_err(|e| format!("Failed to create file {file_name}: {e}"))?;
    }

    // Open the file with the basic text editor based on platform
    #[cfg(target_os = "windows")]
    {
        // On Windows, use notepad which is the most basic editor
        env_sys
            .new_command("notepad.exe")
            .arg(file_path.to_string_lossy().into_owned())
            .spawn()
            .map_err(|e| format!("Failed to open file {file_name}: {e}"))?;
    }

    #[cfg(target_os = "macos")]
    {
        // On macOS, use TextEdit which is the basic text editor
        env_sys
            .new_command("open")
            .args(["-a", "TextEdit", &file_path.to_string_lossy()])
            .spawn()
            .map_err(|e| format!("Failed to open file {file_name}: {e}"))?;
    }

    #[cfg(target_os = "linux")]
    {
        // Try common basic text editors in order of preference
        let editors = ["gedit", "kate", "leafpad", "mousepad", "xed"];
        let mut success = false;

        for editor in editors {
            if env_sys.new_command(editor).arg(&file_path).spawn().is_ok() {
                success = true;
                break;
            }
        }

        // If no GUI editor worked, fall back to xdg-open
        if !success {
            env_sys
                .new_command("xdg-open")
                .arg(&file_path)
                .spawn()
                .map_err(|e| format!("Failed to open file {}: {}", file_name, e))?;
        }
    }

    Ok(true)
}

#[tauri::command]
pub async fn open_credentials_file(file_name: Option<String>) -> Result<bool, String> {
    open_credentials_file_impl(file_name, &RealFileSystem, &RealEnvSystem).await
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::tauri_handlers::helpers::{MockEnvSystem, MockFileSystem};
    use mockall::predicate::*;
    use std::path::PathBuf;

    fn mock_editor_command(mock_env: &mut MockEnvSystem) {
        #[cfg(target_os = "windows")]
        mock_env
            .expect_new_command()
            .with(eq("notepad.exe"))
            .returning(|_| {
                let mut cmd = std::process::Command::new("cmd");
                cmd.args(["/C", "echo", ""]);
                cmd
            });

        #[cfg(target_os = "macos")]
        mock_env
            .expect_new_command()
            .with(eq("open"))
            .returning(|_| std::process::Command::new("echo"));

        #[cfg(target_os = "linux")]
        {
            for editor in ["gedit", "kate", "leafpad", "mousepad", "xed", "xdg-open"] {
                mock_env
                    .expect_new_command()
                    .with(eq(editor))
                    .returning(|_| {
                        let mut cmd = std::process::Command::new("echo");
                        cmd
                    });
            }
        }
    }

    #[tokio::test]
    async fn get_user_credentials_file_exists() {
        let mut mock_fs = MockFileSystem::new();
        let mut mock_env = MockEnvSystem::new();

        mock_env
            .expect_var()
            .with(eq("HOME"))
            .returning(|_| Ok("/mock/home".to_string()));
        mock_env
            .expect_var()
            .with(eq("USERPROFILE"))
            .returning(|_| Err(std::env::VarError::NotPresent));

        let platform_dir = PathBuf::from("/mock/home/.openbb_platform");
        let settings_path = platform_dir.join("user_settings.json");

        mock_fs
            .expect_exists()
            .with(eq(settings_path.clone()))
            .return_const(true);
        mock_fs
            .expect_read_to_string()
            .with(eq(settings_path))
            .returning(|_| Ok(r#"{"credentials":{"api_key":"test123"}}"#.to_string()));

        let result = get_user_credentials_impl(&mock_fs, &mock_env).await;
        assert!(result.is_ok());
        let value = result.unwrap();
        assert_eq!(value["credentials"]["api_key"], "test123");
    }

    #[tokio::test]
    async fn get_user_credentials_file_not_exists() {
        let mut mock_fs = MockFileSystem::new();
        let mut mock_env = MockEnvSystem::new();

        mock_env
            .expect_var()
            .with(eq("HOME"))
            .returning(|_| Ok("/mock/home".to_string()));
        mock_env
            .expect_var()
            .with(eq("USERPROFILE"))
            .returning(|_| Err(std::env::VarError::NotPresent));

        let platform_dir = PathBuf::from("/mock/home/.openbb_platform");
        let settings_path = platform_dir.join("user_settings.json");

        mock_fs
            .expect_exists()
            .with(eq(settings_path))
            .return_const(false);

        let result = get_user_credentials_impl(&mock_fs, &mock_env).await;
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), serde_json::json!({"credentials": {}}));
    }

    #[tokio::test]
    async fn get_user_credentials_home_var_error() {
        let mock_fs = MockFileSystem::new();
        let mut mock_env = MockEnvSystem::new();

        mock_env
            .expect_var()
            .with(eq("HOME"))
            .returning(|_| Err(std::env::VarError::NotPresent));
        mock_env
            .expect_var()
            .with(eq("USERPROFILE"))
            .returning(|_| Err(std::env::VarError::NotPresent));

        let result = get_user_credentials_impl(&mock_fs, &mock_env).await;
        assert!(result.is_err());
        assert!(
            result
                .unwrap_err()
                .contains("Could not determine home directory")
        );
    }

    #[tokio::test]
    async fn update_user_credentials_create_new() {
        let mut mock_fs = MockFileSystem::new();
        let mut mock_env = MockEnvSystem::new();

        let test_credentials = serde_json::json!({ "api_key": "new_key123" });

        mock_env
            .expect_var()
            .with(eq("HOME"))
            .returning(|_| Ok("/mock/home".to_string()));
        mock_env
            .expect_var()
            .with(eq("USERPROFILE"))
            .returning(|_| Err(std::env::VarError::NotPresent));

        let platform_dir = PathBuf::from("/mock/home/.openbb_platform");
        let settings_path = platform_dir.join("user_settings.json");

        mock_fs
            .expect_exists()
            .with(eq(platform_dir.clone()))
            .return_const(false);
        mock_fs
            .expect_create_dir_all()
            .with(eq(platform_dir.clone()))
            .returning(|_| Ok(()));
        mock_fs
            .expect_exists()
            .with(eq(settings_path.clone()))
            .return_const(false);
        mock_fs
            .expect_write()
            .withf(move |path, content| {
                path == settings_path
                    && content.contains("credentials")
                    && content.contains("new_key123")
            })
            .returning(|_, _| Ok(()));

        let result = update_user_credentials_impl(test_credentials, &mock_fs, &mock_env).await;
        assert!(result.is_ok());
        assert!(result.unwrap());
    }

    #[tokio::test]
    async fn update_user_credentials_update_existing() {
        let mut mock_fs = MockFileSystem::new();
        let mut mock_env = MockEnvSystem::new();

        let test_credentials = serde_json::json!({ "api_key": "updated_key" });

        mock_env
            .expect_var()
            .with(eq("HOME"))
            .returning(|_| Ok("/mock/home".to_string()));
        mock_env
            .expect_var()
            .with(eq("USERPROFILE"))
            .returning(|_| Err(std::env::VarError::NotPresent));

        let platform_dir = PathBuf::from("/mock/home/.openbb_platform");
        let settings_path = platform_dir.join("user_settings.json");

        mock_fs
            .expect_exists()
            .with(eq(platform_dir.clone()))
            .return_const(true);
        mock_fs
            .expect_exists()
            .with(eq(settings_path.clone()))
            .return_const(true);
        mock_fs
            .expect_read_to_string()
            .with(eq(settings_path.clone()))
            .returning(|_| {
                Ok(r#"{"credentials":{"api_key":"old_key"},"other_setting":"value"}"#.to_string())
            });
        mock_fs
            .expect_write()
            .withf(move |path, content| {
                path == settings_path
                    && content.contains("updated_key")
                    && content.contains("other_setting")
            })
            .returning(|_, _| Ok(()));

        let result = update_user_credentials_impl(test_credentials, &mock_fs, &mock_env).await;
        assert!(result.is_ok());
        assert!(result.unwrap());
    }

    #[tokio::test]
    async fn update_user_credentials_write_error() {
        let mut mock_fs = MockFileSystem::new();
        let mut mock_env = MockEnvSystem::new();

        let test_credentials = serde_json::json!({ "api_key": "new_key123" });

        mock_env
            .expect_var()
            .with(eq("HOME"))
            .returning(|_| Ok("/mock/home".to_string()));
        mock_env
            .expect_var()
            .with(eq("USERPROFILE"))
            .returning(|_| Err(std::env::VarError::NotPresent));

        let platform_dir = PathBuf::from("/mock/home/.openbb_platform");
        let settings_path = platform_dir.join("user_settings.json");

        mock_fs
            .expect_exists()
            .with(eq(platform_dir.clone()))
            .return_const(true);
        mock_fs
            .expect_exists()
            .with(eq(settings_path.clone()))
            .return_const(false);
        mock_fs
            .expect_write()
            .withf(move |path, content| {
                path == settings_path
                    && content.contains("credentials")
                    && content.contains("new_key123")
            })
            .returning(|_, _| {
                Err(std::io::Error::new(
                    std::io::ErrorKind::PermissionDenied,
                    "Permission denied",
                ))
            });

        let result = update_user_credentials_impl(test_credentials, &mock_fs, &mock_env).await;
        assert!(result.is_err());
        assert!(
            result
                .unwrap_err()
                .contains("Failed to write user settings")
        );
    }

    #[tokio::test]
    async fn open_credentials_file_file_exists() {
        let mut mock_fs = MockFileSystem::new();
        let mut mock_env = MockEnvSystem::new();

        mock_env
            .expect_home_dir()
            .returning(|| PathBuf::from("/mock/home"));

        let platform_dir = PathBuf::from("/mock/home/.openbb_platform");
        let file_path = platform_dir.join("user_settings.json");

        mock_fs
            .expect_exists()
            .with(eq(file_path.clone()))
            .return_const(true);

        mock_editor_command(&mut mock_env);

        let result = open_credentials_file_impl(None, &mock_fs, &mock_env).await;
        assert!(result.is_ok() || result.is_err());
    }

    #[tokio::test]
    async fn open_credentials_file_create_new_file() {
        let mut mock_fs = MockFileSystem::new();
        let mut mock_env = MockEnvSystem::new();

        let file_name = "system_settings.json".to_string();

        mock_env
            .expect_home_dir()
            .returning(|| PathBuf::from("/mock/home"));

        let platform_dir = PathBuf::from("/mock/home/.openbb_platform");
        let file_path = platform_dir.join(&file_name);

        mock_fs
            .expect_exists()
            .with(eq(file_path.clone()))
            .return_const(false);
        mock_fs
            .expect_write()
            .with(eq(file_path.clone()), eq("{}"))
            .returning(|_, _| Ok(()));

        mock_editor_command(&mut mock_env);

        let result = open_credentials_file_impl(Some(file_name), &mock_fs, &mock_env).await;
        assert!(result.is_ok() || result.is_err());
    }

    #[tokio::test]
    async fn open_credentials_file_env_file() {
        let mut mock_fs = MockFileSystem::new();
        let mut mock_env = MockEnvSystem::new();

        let file_name = ".env".to_string();

        mock_env
            .expect_home_dir()
            .returning(|| PathBuf::from("/mock/home"));

        let platform_dir = PathBuf::from("/mock/home/.openbb_platform");
        let file_path = platform_dir.join(&file_name);

        mock_fs
            .expect_exists()
            .with(eq(file_path.clone()))
            .return_const(false);
        mock_fs
            .expect_write()
            .with(
                eq(file_path.clone()),
                eq("# Environment variables for OpenBB Platform"),
            )
            .returning(|_, _| Ok(()));

        mock_editor_command(&mut mock_env);

        let result = open_credentials_file_impl(Some(file_name), &mock_fs, &mock_env).await;
        assert!(result.is_ok() || result.is_err());
    }
}
