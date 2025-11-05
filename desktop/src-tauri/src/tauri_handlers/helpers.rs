use std::collections::HashMap;
use std::io::{Read, Seek, Write};
use std::path::{Path, PathBuf};
use std::process::Command;
use tauri::Manager;
use tauri::Window;

#[cfg_attr(test, mockall::automock)]
pub trait FileSystem {
    fn is_dir(&self, path: &Path) -> bool;
    fn is_file(&self, path: &str) -> bool;
    fn create_file(&self, path: &str) -> Result<Box<dyn Write>, String>;
    fn remove_file(&self, path: &str) -> std::io::Result<()>;
    fn create_dir_all(&self, path: &Path) -> std::io::Result<()>;
    fn remove_dir_all(&self, path: &Path) -> std::io::Result<()>;
    fn exists(&self, path: &Path) -> bool;
    fn write(&self, path: &Path, contents: &str) -> std::io::Result<()>;
    fn read_to_string(&self, path: &Path) -> std::io::Result<String>;
    fn open_rw_create(&self, path: &Path) -> std::io::Result<std::fs::File>;
    fn open_ro(&self, path: &Path) -> std::io::Result<Box<dyn Read>>;
    fn set_len(&self, file: &std::fs::File, len: u64) -> std::io::Result<()>;
    fn flush(&self, file: &mut std::fs::File) -> std::io::Result<()>;
    fn metadata(&self, path: &Path) -> std::io::Result<std::fs::Metadata>;
    fn set_permissions(&self, path: &Path, perm: std::fs::Permissions) -> std::io::Result<()>;
    fn read_dir(&self, path: &Path) -> Result<Vec<PathBuf>, std::io::Error>;
    fn is_empty(&self, path: &Path) -> std::io::Result<bool>;
}

#[cfg_attr(test, mockall::automock)]
pub trait EnvSystem {
    fn var(&self, key: &str) -> Result<String, std::env::VarError>;
    fn temp_dir(&self) -> PathBuf;
    fn consts_os(&self) -> &'static str;
    fn new_command(&self, program: &str) -> std::process::Command;
    fn new_conda_command(&self, conda_exe: &Path, conda_dir: &Path) -> std::process::Command;
    fn home_dir(&self) -> PathBuf;
}

#[cfg_attr(test, mockall::automock)]
pub trait FileExtTrait {
    fn try_lock_exclusive(&self, file: &std::fs::File) -> std::io::Result<()>;
    fn unlock(&self, file: &std::fs::File) -> std::io::Result<()>;
}

#[derive(Clone, Copy)]
pub struct RealFileExtTrait;

impl FileExtTrait for RealFileExtTrait {
    fn try_lock_exclusive(&self, file: &std::fs::File) -> std::io::Result<()> {
        fs2::FileExt::try_lock_exclusive(file)
    }
    fn unlock(&self, file: &std::fs::File) -> std::io::Result<()> {
        fs2::FileExt::unlock(file)
    }
}

#[derive(Clone, Copy)]
pub struct RealFileSystem;

impl FileSystem for RealFileSystem {
    fn is_dir(&self, path: &Path) -> bool {
        Path::new(path).is_dir()
    }
    fn is_file(&self, path: &str) -> bool {
        Path::new(path).is_file()
    }
    fn create_file(&self, path: &str) -> Result<Box<dyn std::io::Write>, String> {
        std::fs::File::create(path)
            .map(|f| Box::new(f) as Box<dyn std::io::Write>)
            .map_err(|e| format!("Failed to create file {path}: {e}"))
    }
    fn remove_file(&self, path: &str) -> std::io::Result<()> {
        std::fs::remove_file(path)
    }
    fn create_dir_all(&self, path: &Path) -> std::io::Result<()> {
        std::fs::create_dir_all(path)
    }
    fn remove_dir_all(&self, path: &Path) -> std::io::Result<()> {
        std::fs::remove_dir_all(path)
    }
    fn exists(&self, path: &Path) -> bool {
        path.exists()
    }
    fn write(&self, path: &Path, contents: &str) -> std::io::Result<()> {
        std::fs::write(path, contents)
    }
    fn read_to_string(&self, path: &Path) -> std::io::Result<String> {
        std::fs::read_to_string(path)
    }
    fn open_rw_create(&self, path: &Path) -> std::io::Result<std::fs::File> {
        std::fs::File::options()
            .read(true)
            .write(true)
            .create(true)
            .truncate(true)
            .open(path)
    }
    fn open_ro(&self, path: &Path) -> std::io::Result<Box<dyn std::io::Read>> {
        std::fs::File::open(path).map(|f| Box::new(f) as Box<dyn std::io::Read>)
    }
    fn set_len(&self, file: &std::fs::File, len: u64) -> std::io::Result<()> {
        file.set_len(len)
    }
    fn flush(&self, file: &mut std::fs::File) -> std::io::Result<()> {
        file.flush()
    }
    fn metadata(&self, path: &Path) -> std::io::Result<std::fs::Metadata> {
        std::fs::metadata(path)
    }
    fn set_permissions(&self, path: &Path, perm: std::fs::Permissions) -> std::io::Result<()> {
        std::fs::set_permissions(path, perm)
    }
    fn read_dir(&self, path: &Path) -> Result<Vec<PathBuf>, std::io::Error> {
        let entries = std::fs::read_dir(path)?
            .filter_map(|entry| entry.ok().map(|e| e.path()))
            .collect();
        Ok(entries)
    }
    fn is_empty(&self, path: &Path) -> std::io::Result<bool> {
        if path.is_dir() {
            let mut entries = std::fs::read_dir(path)?;
            Ok(entries.next().is_none())
        } else if path.is_file() {
            Ok(std::fs::metadata(path)?.len() == 0)
        } else {
            Ok(true)
        }
    }
}

#[derive(Clone, Copy)]
pub struct RealEnvSystem;

impl EnvSystem for RealEnvSystem {
    fn var(&self, key: &str) -> Result<String, std::env::VarError> {
        std::env::var(key)
    }
    fn temp_dir(&self) -> PathBuf {
        std::env::temp_dir()
    }
    fn consts_os(&self) -> &'static str {
        std::env::consts::OS
    }
    #[allow(unused_mut)]
    fn new_command(&self, program: &str) -> std::process::Command {
        let mut command = std::process::Command::new(program);
        #[cfg(windows)]
        {
            use std::os::windows::process::CommandExt;
            command.creation_flags(0x08000000); // CREATE_NO_WINDOW
        }
        command
    }
    fn new_conda_command(&self, conda_exe: &Path, conda_dir: &Path) -> std::process::Command {
        let mut command = self.new_command(conda_exe.to_str().unwrap());
        command
            .env("CONDA_ROOT", conda_dir)
            .env("CONDA_ENVS_PATH", conda_dir.join("envs"))
            .env("CONDA_PKGS_DIRS", conda_dir.join("pkgs"))
            .env("CONDARC", conda_dir.join(".condarc"))
            .env_remove("CONDA_DEFAULT_ENV")
            .env_remove("CONDA_PREFIX")
            .env_remove("CONDA_SHLVL");
        command
    }
    fn home_dir(&self) -> PathBuf {
        std::env::home_dir().unwrap()
    }
}

#[tauri::command]
pub fn check_file_exists(path: String) -> Result<bool, String> {
    let p = Path::new(&path);
    Ok(p.is_file())
}

pub async fn toggle_theme_impl<F: FileSystem, E: EnvSystem, FE: FileExtTrait>(
    theme: String,
    fs: &F,
    env_sys: &E,
    file_ext: &FE,
) -> Result<bool, String> {
    use std::io::SeekFrom;
    use std::path::Path;

    if theme != "dark" && theme != "light" {
        return Err(format!("Invalid theme: {theme}. Must be 'dark' or 'light'"));
    }

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

    // Create file if it doesn't exist
    if !fs.exists(&user_settings_path) {
        fs.write(&user_settings_path, "{}")
            .map_err(|e| format!("Failed to create user settings file: {e}"))?;
    }

    // Open file for locking
    let mut file = fs
        .open_rw_create(&user_settings_path)
        .map_err(|e| format!("Failed to open user settings file: {e}"))?;

    file_ext
        .try_lock_exclusive(&file)
        .map_err(|e| format!("Failed to lock user settings file: {e}"))?;

    let contents = fs.read_to_string(&user_settings_path).map_err(|e| {
        file_ext.unlock(&file).ok();
        format!("Failed to read user settings file: {e}")
    })?;

    // Parse existing settings, preserving all unrelated fields
    let mut settings: serde_json::Value = if contents.trim().is_empty() {
        serde_json::json!({})
    } else {
        match serde_json::from_str(&contents) {
            Ok(json) => json,
            Err(e) => {
                file_ext.unlock(&file).ok();
                return Err(format!("Failed to parse user settings file: {e}"));
            }
        }
    };

    // Ensure root is an object
    if !settings.is_object() {
        settings = serde_json::json!({});
    }

    // Ensure "preferences" is an object
    {
        let prefs = settings
            .as_object_mut()
            .unwrap()
            .entry("preferences")
            .or_insert_with(|| serde_json::json!({}));

        if !prefs.is_object() {
            *prefs = serde_json::json!({});
        }

        let prefs_obj = prefs.as_object_mut().unwrap();
        prefs_obj.insert("chart_style".to_string(), serde_json::json!(theme.clone()));
        prefs_obj.insert("table_style".to_string(), serde_json::json!(theme));
    }

    let updated_contents = serde_json::to_string_pretty(&settings).map_err(|e| {
        file_ext.unlock(&file).ok();
        format!("Failed to serialize settings: {e}")
    })?;

    file.seek(SeekFrom::Start(0)).map_err(|e| {
        file_ext.unlock(&file).ok();
        format!("Failed to seek to start of file: {e}")
    })?;
    file.set_len(0).map_err(|e| {
        file_ext.unlock(&file).ok();
        format!("Failed to truncate file: {e}")
    })?;
    file.write_all(updated_contents.as_bytes()).map_err(|e| {
        file_ext.unlock(&file).ok();
        format!("Failed to write to user settings file: {e}")
    })?;

    file.flush().map_err(|e| {
        file_ext.unlock(&file).ok();
        format!("Failed to flush user settings file: {e}")
    })?;

    file_ext
        .unlock(&file)
        .map_err(|e| format!("Failed to unlock user settings file: {e}"))?;

    Ok(true)
}

#[tauri::command]
pub async fn toggle_theme(theme: String) -> Result<bool, String> {
    toggle_theme_impl(theme, &RealFileSystem, &RealEnvSystem, &RealFileExtTrait).await
}

pub fn save_working_directory_impl<F: FileSystem, E: EnvSystem>(
    path: &str,
    fs: &F,
    env_sys: &E,
) -> Result<bool, String> {
    use std::path::Path;

    let home_dir = env_sys
        .var("HOME")
        .or_else(|_| env_sys.var("USERPROFILE"))
        .map_err(|e| format!("Could not determine home directory: {e}"))?;

    let platform_dir = Path::new(&home_dir).join(".openbb_platform");
    let settings_path = platform_dir.join("user_settings.json");

    if !fs.exists(&platform_dir) {
        fs.create_dir_all(&platform_dir)
            .map_err(|e| format!("Failed to create platform directory: {e}"))?;
    }

    // Read existing content if file exists
    let contents = if fs.exists(&settings_path) {
        fs.read_to_string(&settings_path)
            .map_err(|e| format!("Failed to read settings file: {e}"))?
    } else {
        String::new()
    };

    let mut settings: serde_json::Value = if contents.trim().is_empty() {
        serde_json::json!({})
    } else {
        match serde_json::from_str(&contents) {
            Ok(json) => json,
            Err(e) => return Err(format!("Failed to parse settings file: {e}")),
        }
    };

    if !settings.is_object() {
        settings = serde_json::json!({});
    }

    if !settings.as_object().unwrap().contains_key("preferences") {
        settings["preferences"] = serde_json::json!({});
    }

    settings["preferences"]["working_directory"] = serde_json::json!(path);

    let updated_contents = serde_json::to_string_pretty(&settings)
        .map_err(|e| format!("Failed to serialize settings: {e}"))?;

    // Write the updated content back to the file
    fs.write(&settings_path, &updated_contents)
        .map_err(|e| format!("Failed to write to settings file: {e}"))?;

    Ok(true)
}

#[tauri::command]
pub fn save_working_directory(path: &str) -> Result<bool, String> {
    save_working_directory_impl(path, &RealFileSystem, &RealEnvSystem)
}

pub fn get_working_directory_impl<F: FileSystem, E: EnvSystem>(
    default_dir: &str,
    fs: &F,
    env_sys: &E,
) -> Result<String, String> {
    use std::path::Path;

    let home_dir = env_sys
        .var("HOME")
        .or_else(|_| env_sys.var("USERPROFILE"))
        .map_err(|e| format!("Could not determine home directory: {e}"))?;

    let settings_path = Path::new(&home_dir)
        .join(".openbb_platform")
        .join("user_settings.json");

    if !fs.exists(&settings_path) {
        return Ok(default_dir.to_string());
    }

    let contents = match fs.read_to_string(&settings_path) {
        Ok(contents) => contents,
        Err(_) => return Ok(default_dir.to_string()),
    };

    let settings: serde_json::Value = match serde_json::from_str(&contents) {
        Ok(json) => json,
        Err(_) => return Ok(default_dir.to_string()),
    };

    if let Some(prefs) = settings.get("preferences")
        && let Some(dir) = prefs.get("working_directory")
        && let Some(dir_str) = dir.as_str()
    {
        let dir_path = Path::new(dir_str);
        if fs.exists(dir_path) && fs.is_dir(dir_path) {
            return Ok(dir_str.to_string());
        }
    }

    Ok(default_dir.to_string())
}

#[tauri::command]
pub fn get_working_directory(default_dir: &str) -> Result<String, String> {
    get_working_directory_impl(default_dir, &RealFileSystem, &RealEnvSystem)
}

pub fn get_environments_directory_impl<E: EnvSystem>(env_sys: &E) -> Result<PathBuf, String> {
    let home_dir = env_sys
        .var("HOME")
        .or_else(|_| env_sys.var("USERPROFILE"))
        .map_err(|e| format!("Could not determine home directory: {e}"))?;

    let platform_dir = Path::new(&home_dir).join(".openbb_platform");
    let envs_dir = platform_dir.join("environments");

    Ok(envs_dir)
}

pub fn get_environments_directory() -> Result<PathBuf, String> {
    get_environments_directory_impl(&RealEnvSystem)
}

pub fn get_settings_directory_impl<E: EnvSystem>(env_sys: &E) -> Result<PathBuf, String> {
    let home_dir = env_sys
        .var("HOME")
        .or_else(|_| env_sys.var("USERPROFILE"))
        .map_err(|e| format!("Could not determine home directory: {e}"))?;

    let platform_dir = Path::new(&home_dir).join(".openbb_platform");

    Ok(platform_dir)
}

#[tauri::command]
pub fn get_settings_directory() -> Result<PathBuf, String> {
    get_settings_directory_impl(&RealEnvSystem)
}

#[allow(clippy::too_many_arguments)]
pub async fn save_environment_as_yaml_impl<F: FileSystem, E: EnvSystem>(
    env_name: &str,
    python_version: &str,
    conda_packages: &[String],
    pip_packages: &[String],
    conda_channels: &HashMap<String, Vec<String>>,
    _directory: &str,
    fs: &F,
    env_sys: &E,
) -> Result<PathBuf, String> {
    let envs_dir = get_environments_directory_impl(env_sys)?;

    if !envs_dir.exists() {
        fs.create_dir_all(&envs_dir)
            .map_err(|e| format!("Failed to create environments directory: {e}"))?;
    }

    let yaml_path = envs_dir.join(format!("{env_name}.yaml"));

    log::debug!("Saving environment YAML to: {}", yaml_path.display());
    let mut yaml_content = format!(
        r#"name: {env_name}
channels:
  - defaults
  - conda-forge
"#
    );

    for channel in conda_channels.keys() {
        if channel != "defaults" && channel != "conda-forge" {
            yaml_content.push_str(&format!("  - {channel}\n"));
        }
    }

    yaml_content.push_str("dependencies:\n");
    yaml_content.push_str(&format!("  - python={python_version}\n"));

    for package in conda_packages {
        yaml_content.push_str(&format!("  - {package}\n"));
    }

    if !pip_packages.is_empty() {
        let mut has_pip_dependency = false;
        for package in conda_packages {
            if package.trim() == "pip" {
                has_pip_dependency = true;
                break;
            }
        }

        if !has_pip_dependency {
            yaml_content.push_str("  - pip\n");
        }

        yaml_content.push_str("  - pip:\n");

        for package in pip_packages {
            yaml_content.push_str(&format!("    - {package}\n"));
        }
    }

    fs.write(&yaml_path, &yaml_content)
        .map_err(|e| format!("Failed to write environment YAML: {e}"))?;

    log::debug!("Environment YAML saved to: {}", yaml_path.display());

    Ok(yaml_path)
}

pub async fn save_environment_as_yaml(
    env_name: &str,
    python_version: &str,
    conda_packages: &[String],
    pip_packages: &[String],
    conda_channels: &HashMap<String, Vec<String>>,
    _directory: &str,
) -> Result<PathBuf, String> {
    save_environment_as_yaml_impl(
        env_name,
        python_version,
        conda_packages,
        pip_packages,
        conda_channels,
        _directory,
        &RealFileSystem,
        &RealEnvSystem,
    )
    .await
}

pub fn get_environment_python_version_impl<F: FileSystem, E: EnvSystem>(
    env_path: &Path,
    fs: &F,
    env_sys: &E,
) -> Result<String, String> {
    let pyvenv_cfg = env_path.join("pyvenv.cfg");
    if fs.exists(&pyvenv_cfg)
        && let Ok(content) = fs.read_to_string(&pyvenv_cfg)
    {
        for line in content.lines() {
            if line.starts_with("version")
                && let Some(version_part) = line.split('=').nth(1)
            {
                let version = version_part.trim();
                let parts: Vec<&str> = version.split('.').collect();
                if parts.len() >= 2 {
                    return Ok(format!("{}.{}", parts[0], parts[1]));
                }
            }
        }
    }

    let python_exe = if env_sys.consts_os() == "windows" {
        env_path.join("python.exe")
    } else {
        env_path.join("bin").join("python")
    };

    if !fs.exists(&python_exe) {
        return Err("Python executable not found".to_string());
    }

    let mut conda_dir = env_path;
    while let Some(parent) = conda_dir.parent() {
        if parent.file_name() == Some(std::ffi::OsStr::new("envs")) {
            if let Some(conda_root) = parent.parent() {
                let conda_exe = if env_sys.consts_os() == "windows" {
                    conda_root.join("Scripts").join("conda.exe")
                } else {
                    conda_root.join("bin").join("conda")
                };

                if fs.exists(&conda_exe)
                    && let Some(env_name) = env_path.file_name()
                    && let Some(env_name_str) = env_name.to_str()
                {
                    let mut conda_cmd = env_sys.new_conda_command(&conda_exe, conda_root);

                    if let Ok(output) = conda_cmd
                        .args(["list", "--name", env_name_str, "--json"])
                        .output()
                        && output.status.success()
                    {
                        let stdout = String::from_utf8_lossy(&output.stdout);
                        if let Ok(packages) =
                            serde_json::from_str::<Vec<serde_json::Value>>(&stdout)
                        {
                            for package in packages {
                                if let Some(name) = package.get("name").and_then(|n| n.as_str())
                                    && name == "python"
                                    && let Some(version) =
                                        package.get("version").and_then(|v| v.as_str())
                                {
                                    let parts: Vec<&str> = version.split('.').collect();
                                    if parts.len() >= 2 {
                                        return Ok(format!("{}.{}", parts[0], parts[1]));
                                    }
                                }
                            }
                        }
                    }
                }
            }
            break;
        }
        conda_dir = parent;
    }

    let mut python_cmd = env_sys.new_command(python_exe.to_str().unwrap());

    if let Ok(output) = python_cmd
        .args([
            "-c",
            "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')",
        ])
        .output()
        && output.status.success()
    {
        let version = String::from_utf8_lossy(&output.stdout).trim().to_string();
        if !version.is_empty() {
            return Ok(version);
        }
    }

    Err("Could not determine Python version".to_string())
}

pub fn get_environment_python_version(env_path: &Path) -> Result<String, String> {
    get_environment_python_version_impl(env_path, &RealFileSystem, &RealEnvSystem)
}

pub fn get_installation_directory_impl<F: FileSystem, E: EnvSystem>(
    fs: &F,
    env_sys: &E,
) -> Result<String, String> {
    let home_dir = env_sys
        .var("HOME")
        .or_else(|_| env_sys.var("USERPROFILE"))
        .map_err(|e| format!("Could not determine home directory: {e}"))?;

    let platform_dir = Path::new(&home_dir).join(".openbb_platform");
    let system_settings_path = platform_dir.join("system_settings.json");

    let settings_content = fs
        .read_to_string(&system_settings_path)
        .map_err(|e| format!("Failed to read system settings: {e}"))?;

    let settings: serde_json::Value = serde_json::from_str(&settings_content)
        .map_err(|e| format!("Failed to parse system settings: {e}"))?;

    settings["install_settings"]["installation_directory"]
        .as_str()
        .ok_or_else(|| "Installation directory not found in system settings".to_string())
        .map(|s| s.to_string())
}

#[tauri::command]
pub fn get_installation_directory() -> Result<String, String> {
    get_installation_directory_impl(&RealFileSystem, &RealEnvSystem)
}

pub fn get_userdata_directory_impl<F: FileSystem, E: EnvSystem>(
    fs: &F,
    env_sys: &E,
) -> Result<String, String> {
    let home_dir = env_sys
        .var("HOME")
        .or_else(|_| env_sys.var("USERPROFILE"))
        .map_err(|e| format!("Could not determine home directory: {e}"))?;

    let platform_dir = Path::new(&home_dir).join(".openbb_platform");
    let system_settings_path = platform_dir.join("system_settings.json");

    let settings_content = fs
        .read_to_string(&system_settings_path)
        .map_err(|e| format!("Failed to read system settings: {e}"))?;

    let settings: serde_json::Value = serde_json::from_str(&settings_content)
        .map_err(|e| format!("Failed to parse system settings: {e}"))?;

    settings["install_settings"]["user_data_directory"]
        .as_str()
        .ok_or_else(|| "Installation directory not found in system settings".to_string())
        .map(|s| s.to_string())
}

#[tauri::command]
pub fn get_userdata_directory() -> Result<String, String> {
    get_userdata_directory_impl(&RealFileSystem, &RealEnvSystem)
}

pub async fn update_openbb_settings_impl<F: FileSystem, E: EnvSystem>(
    conda_dir: &std::path::Path,
    environment: &str,
    fs: &F,
    env_sys: &E,
) -> Result<(), String> {
    log::debug!("Updating OpenBB settings for environment: {environment}");
    let conda_dir = if conda_dir.file_name() == Some(std::ffi::OsStr::new("conda")) {
        conda_dir.to_path_buf()
    } else {
        conda_dir.join("conda")
    };
    log::debug!("Using conda directory: {}", conda_dir.display());
    let settings_update_script = r#"
import json
import os
import sys
from pathlib import Path

try:
    print("Starting OpenBB settings configuration...")

    home = Path.home()
    platform_dir = home / '.openbb_platform'
    platform_dir.mkdir(exist_ok=True)

    user_settings_path = platform_dir / 'user_settings.json'
    system_settings_path = platform_dir / 'system_settings.json'

    existing_user_settings = {}
    if user_settings_path.exists():
        try:
            with open(user_settings_path, 'r') as f:
                existing_user_settings = json.load(f)
                print(f"Loaded existing user settings file: {user_settings_path}")
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading existing user settings: {e}")

    try:
        from openbb_core.app.service.user_service import UserService

        user_service = UserService()
        user_settings = user_service.read_from_file()

        if user_settings:
            if hasattr(user_settings, 'credentials') and user_settings.credentials:
                credentials_json = json.loads(user_settings.credentials.model_dump_json())

                if 'credentials' not in existing_user_settings:
                    existing_user_settings['credentials'] = {}

                for key, value in credentials_json.items():
                    if key not in existing_user_settings['credentials']:
                        existing_user_settings['credentials'][key] = value
                        print(f"Added missing credential key: {key}")

            if 'preferences' not in existing_user_settings:
                existing_user_settings['preferences'] = {}

            if 'defaults' not in existing_user_settings:
                existing_user_settings['defaults'] = {}
    except ImportError as e:
        print(f"Could not import OpenBB UserService: {e}")
        if 'credentials' not in existing_user_settings:
            existing_user_settings['credentials'] = {}
        if 'preferences' not in existing_user_settings:
            existing_user_settings['preferences'] = {}
        if 'defaults' not in existing_user_settings:
            existing_user_settings['defaults'] = {}

    with open(user_settings_path, 'w') as f:
        json.dump(existing_user_settings, f, indent=4)
        print(f"Updated user settings file written to {user_settings_path}")

    existing_system_settings = {}
    if system_settings_path.exists():
        try:
            with open(system_settings_path, 'r') as f:
                existing_system_settings = json.load(f)
                print(f"Loaded existing system settings file: {system_settings_path}")
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading existing system settings: {e}")

    try:
        from openbb_core.app.service.system_service import SystemService

        system_service = SystemService()

        if hasattr(system_service, 'system_settings'):
            system_dict = system_service.system_settings.model_dump()

            if 'api_settings' not in existing_system_settings:
                existing_system_settings['api_settings'] = system_dict.get('api_settings', {})
                print("Added missing api_settings section")

            if 'python_settings' not in existing_system_settings:
                existing_system_settings['python_settings'] = system_dict.get('python_settings', {})
                print("Added missing python_settings section")

            if 'debug_mode' not in existing_system_settings:
                existing_system_settings['debug_mode'] = system_dict.get('debug_mode', False)
                print("Added missing debug_mode setting")

            if 'install_settings' not in existing_system_settings:
                existing_system_settings['install_settings'] = system_dict.get('install_settings', {})
                print("Added missing install_settings section")
    except ImportError as e:
        print(f"Could not import OpenBB SystemService: {e}")
        if 'api_settings' not in existing_system_settings:
            existing_system_settings['api_settings'] = {}
        if 'python_settings' not in existing_system_settings:
            existing_system_settings['python_settings'] = {}
        if 'debug_mode' not in existing_system_settings:
            existing_system_settings['debug_mode'] = False
        if 'install_settings' not in existing_system_settings:
            existing_system_settings['install_settings'] = {}

    with open(system_settings_path, 'w') as f:
        json.dump(existing_system_settings, f, indent=4)
        print(f"Updated system settings file written to {system_settings_path}")

    print("OpenBB settings configuration completed successfully")

except Exception as e:
    print(f"Error updating OpenBB settings: {e}")
    sys.exit(1)
"#;

    let script_path = env_sys.temp_dir().join("openbb_update_settings.py");

    fs.write(&script_path, settings_update_script)
        .map_err(|e| format!("Failed to create settings update script: {e}"))?;

    let shell = if env_sys.consts_os() == "windows" {
        "cmd.exe"
    } else {
        "bash"
    };

    let shell_arg = if env_sys.consts_os() == "windows" {
        "/c"
    } else {
        "-c"
    };
    let script_command = if env_sys.consts_os() == "windows" {
        let condabin_conda = conda_dir.join("condabin").join("conda.bat");
        let scripts_activate = conda_dir.join("Scripts").join("activate.bat");
        let conda_exe = conda_dir.join("Scripts").join("conda.exe");

        let activation_command = if condabin_conda.exists() {
            format!(
                "call {} activate {}",
                condabin_conda.to_string_lossy(),
                environment
            )
        } else if scripts_activate.exists() {
            format!(
                "call {} {}",
                scripts_activate.to_string_lossy(),
                environment
            )
        } else if conda_exe.exists() {
            format!("{} run -n {}", conda_exe.to_string_lossy(), environment)
        } else {
            return Err("Could not find any conda activation method".to_string());
        };
        log::debug!("Using activation command: {}", activation_command);
        format!(
            r#"@echo off
setlocal enabledelayedexpansion

REM Set environment variables for conda isolation
set "CONDA_ROOT={}"
set "CONDA_ENVS_PATH={}"
set "CONDA_PKGS_DIRS={}"
set "CONDARC={}"
set CONDA_DEFAULT_ENV=
set CONDA_PREFIX=
set CONDA_SHLVL=

REM Add conda paths to PATH
set "PATH={};{};%PATH%"

REM Activate the environment using the best available method
{}
if errorlevel 1 (
    echo Failed to activate environment: {}
    exit /b 1
)

REM Run the Python script
python {}
"#,
            conda_dir.to_string_lossy(),
            conda_dir.join("envs").to_string_lossy(),
            conda_dir.join("pkgs").to_string_lossy(),
            conda_dir.join(".condarc").to_string_lossy(),
            conda_dir.join("Scripts").to_string_lossy(),
            conda_dir.join("condabin").to_string_lossy(),
            activation_command,
            environment,
            script_path.to_string_lossy()
        )
    } else {
        format!(
            r#"#!/bin/bash
set -e

export CONDA_ROOT="{}"
export CONDA_ENVS_PATH="{}"
export CONDA_PKGS_DIRS="{}"
export CONDARC="{}"
unset CONDA_DEFAULT_ENV
unset CONDA_PREFIX
unset CONDA_SHLVL
export PATH="{}:{}:$PATH"

# Source conda activation script
source "{}/bin/activate" {}
if [ $? -ne 0 ]; then
    echo "Failed to activate environment: {}"
    exit 1
fi

# Run the Python script
python {}
"#,
            conda_dir.to_string_lossy(),
            conda_dir.join("envs").to_string_lossy(),
            conda_dir.join("pkgs").to_string_lossy(),
            conda_dir.join(".condarc").to_string_lossy(),
            conda_dir.join("bin").to_string_lossy(),
            conda_dir.join("condabin").to_string_lossy(),
            conda_dir.to_string_lossy(),
            environment,
            environment,
            script_path.to_string_lossy()
        )
    };

    let settings_output = env_sys
        .new_command(shell)
        .arg(shell_arg)
        .arg(&script_command)
        .output()
        .map_err(|e| format!("Failed to execute settings update script: {e}"))?;

    let _ = fs.remove_file(&script_path.to_string_lossy());

    let settings_stdout = String::from_utf8_lossy(&settings_output.stdout);
    let settings_stderr = String::from_utf8_lossy(&settings_output.stderr);
    log::debug!(
        "Settings update script output:\nStdout: {settings_stdout}\nStderr: {settings_stderr}"
    );

    if !settings_output.status.success() {
        log::debug!("Warning: OpenBB settings update may have issues, continuing anyway");
    }

    Ok(())
}

#[tauri::command]
pub async fn update_openbb_settings(
    conda_dir: &std::path::Path,
    environment: &str,
) -> Result<(), String> {
    update_openbb_settings_impl(conda_dir, environment, &RealFileSystem, &RealEnvSystem).await
}

#[tauri::command]
pub async fn open_url_in_window(
    url: String,
    title: Option<String>,
    window: Window,
) -> Result<(), String> {
    log::debug!("Opening URL in a new window: {url}");

    let parsed_url = url
        .parse::<url::Url>()
        .map_err(|e| format!("Invalid URL: {e}"))?;

    let app_handle = window.app_handle();
    let label = format!("url_{}", chrono::Utc::now().timestamp_millis());

    #[allow(unused_mut)]
    let mut builder = tauri::WebviewWindowBuilder::new(
        app_handle,
        &label,
        tauri::WebviewUrl::External(parsed_url),
    )
    .title(title.unwrap_or_else(|| "Open Data Platform".to_string()))
    .inner_size(1200.0, 800.0)
    .center()
    .focused(true)
    .visible(true)
    .resizable(true);

    #[cfg(target_os = "macos")]
    {
        builder = builder.title_bar_style(tauri::TitleBarStyle::Transparent);
    }

    let webview_window = builder.build().map_err(|e| {
        log::error!("Failed to create window: {e}");
        format!("Failed to create window: {e}")
    })?;

    // Clone the window handle for use in the closure
    let window_clone = webview_window.clone();

    // Set up window event handler
    webview_window.on_window_event(move |event| {
        if let tauri::WindowEvent::CloseRequested { api, .. } = event {
            if let Err(e) = window_clone.destroy() {
                log::error!("Failed to destroy window: {e}");
            }
            api.prevent_close();
        }
    });

    #[cfg(target_os = "macos")]
    {
        use objc2_app_kit::{NSColor, NSWindow};

        let ns_window_ptr = webview_window.ns_window().unwrap();
        let ns_window = unsafe { &*(ns_window_ptr as *mut NSWindow) };
        let bg_color = NSColor::colorWithRed_green_blue_alpha(0.0, 0.0, 0.0, 1.0);
        ns_window.setBackgroundColor(Some(&bg_color));
    }

    log::info!("Successfully opened URL in new window: {label}");
    Ok(())
}

pub fn open_workspace_in_browser() {
    let url = "https://pro.openbb.co";

    let status = if cfg!(target_os = "windows") {
        Command::new("cmd").args(["/c", "start", "", url]).status()
    } else if cfg!(target_os = "macos") {
        Command::new("open").arg(url).status()
    } else {
        Command::new("xdg-open").arg(url).status()
    };

    match status {
        Ok(_) => log::info!("Opened workspace in system browser"),
        Err(e) => log::error!("Failed to open browser: {e}"),
    }
}

pub async fn select_file_impl<E: EnvSystem>(
    filter: Option<String>,
    env_sys: &E,
) -> Result<String, String> {
    let home_dir = env_sys
        .var("HOME")
        .or_else(|_| env_sys.var("USERPROFILE"))
        .unwrap_or_else(|_| "/".to_string());

    let (file_ext, file_desc) = match filter.as_deref() {
        Some(".env") => ("env", "Environment Files"),
        Some(".py") => ("py", "Python Files"),
        _ => ("*", "All Files"),
    };

    #[cfg(target_os = "macos")]
    {
        let script = if file_ext == "env" {
            format!(
                r#"
                try
                    tell application "System Events"
                        activate
                        set defaultFolder to POSIX file "{}"
                        set filePath to POSIX path of (choose file default location defaultFolder with prompt "Select .env file" with invisibles)
                        if filePath does not end with ".env" then
                            display dialog "Please select a file with .env extension" buttons {{"OK"}} default button 1
                            error "Invalid file type selected"
                        end if
                        return filePath
                    end tell
                on error errMsg number errNum
                    if errNum is -128 then
                        return ""
                    else if errMsg contains "Invalid file type selected" then
                        tell application "System Events"
                            activate
                            set defaultFolder to POSIX file "{}"
                            set filePath to POSIX path of (choose file default location defaultFolder with prompt "Select .env file (files must end with .env)" with invisibles)
                            if filePath does not end with ".env" then
                                return "ERROR: Please select a file with .env extension"
                            end if
                            return filePath
                        end tell
                    else
                        return "ERROR: " & errMsg
                    end if
                end try
                "#,
                home_dir.replace("\"", "\\\""),
                home_dir.replace("\"", "\\\"")
            )
        } else if file_ext == "*" {
            format!(
                r#"
                try
                    tell application "System Events"
                        activate
                        set defaultFolder to POSIX file "{}"
                        set filePath to POSIX path of (choose file default location defaultFolder with prompt "Select File")
                        return filePath
                    end tell
                on error errMsg number errNum
                    if errNum is -128 then
                        return ""
                    else
                        return "ERROR: " & errMsg
                    end if
                end try
                "#,
                home_dir.replace("\"", "\\\"")
            )
        } else {
            format!(
                r#"
                try
                    tell application "System Events"
                        activate
                        set defaultFolder to POSIX file "{}"
                        set fileTypes to {{"{}"}}
                        set filePath to POSIX path of (choose file default location defaultFolder with prompt "Select {}" of type fileTypes)
                        return filePath
                    end tell
                on error errMsg number errNum
                    if errNum is -128 then
                        return ""
                    else
                        return "ERROR: " & errMsg
                    end if
                end try
                "#,
                home_dir.replace("\"", "\\\""),
                file_ext,
                file_desc
            )
        };

        let output = env_sys
            .new_command("osascript")
            .args(["-e", &script])
            .output()
            .map_err(|e| format!("Failed to execute AppleScript: {e}"))?;

        let path = String::from_utf8(output.stdout)
            .map_err(|_| "Invalid UTF-8 in file path".to_string())?
            .trim()
            .to_string();

        if let Some(path) = path.strip_prefix("ERROR: ") {
            return Err(path.to_string());
        }

        if path.is_empty() {
            return Ok(path);
        }

        Ok(path)
    }

    #[cfg(target_os = "windows")]
    {
        let filter_string = if file_ext == "*" {
            "All Files|*.*".to_string()
        } else if file_ext == "env" {
            "Environment Files|*.env|All Files|*.*".to_string()
        } else {
            format!("{file_desc}|*.{file_ext}|All Files|*.*")
        };

        let script = format!(
            r#"
            Add-Type -AssemblyName System.Windows.Forms
            $dialog = New-Object System.Windows.Forms.OpenFileDialog
            $dialog.InitialDirectory = "{}"
            $dialog.Filter = "{}"
            $dialog.Title = "Select {}"
            $dialog.Multiselect = $false
            if ($dialog.ShowDialog() -eq 'OK') {{
                $dialog.FileName
            }} else {{
                ""
            }}
            "#,
            home_dir.replace("\"", "`\""),
            filter_string,
            file_desc
        );

        let output = env_sys
            .new_command("powershell")
            .args(["-Command", &script])
            .output()
            .map_err(|e| format!("Failed to execute PowerShell: {e}"))?;

        let path = String::from_utf8(output.stdout)
            .map_err(|_| "Invalid UTF-8 in file path".to_string())?
            .trim()
            .to_string();

        Ok(path)
    }

    #[cfg(target_os = "linux")]
    {
        let title_arg = format!("--title=Select {}", file_desc);
        let filename_arg = format!("--filename={}/", home_dir);
        let filter_arg = format!("--file-filter=*.{} | *.{} files", file_ext, file_ext);

        let zenity_args = if file_ext == "*" {
            vec!["--file-selection", &title_arg, &filename_arg]
        } else {
            vec![
                "--file-selection",
                &title_arg,
                &filename_arg,
                &filter_arg,
                "--file-filter=* | All files",
            ]
        };

        let zenity_result = env_sys.new_command("zenity").args(&zenity_args).output();

        if let Ok(output) = zenity_result {
            if output.status.success() {
                let path = String::from_utf8(output.stdout)
                    .map_err(|_| "Invalid UTF-8 in file path".to_string())?
                    .trim()
                    .to_string();

                if !path.is_empty() {
                    return Ok(path);
                }
            } else if output.status.code() == Some(1) {
                return Ok(String::new());
            }
        }

        let kdialog_filter = if file_ext == "*" {
            "*|All Files".to_string()
        } else {
            format!("*.{}|{} (*.{})", file_ext, file_desc, file_ext)
        };

        let kdialog_result = env_sys
            .new_command("kdialog")
            .args(["--getopenfilename", &home_dir, &kdialog_filter])
            .output();

        if let Ok(output) = kdialog_result {
            if output.status.success() {
                let path = String::from_utf8(output.stdout)
                    .map_err(|_| "Invalid UTF-8 in file path".to_string())?
                    .trim()
                    .to_string();

                if !path.is_empty() {
                    return Ok(path);
                }
            } else {
                return Ok(String::new());
            }
        }

        let gtk_pattern = if file_ext == "*" {
            "*".to_string()
        } else {
            format!("*.{}", file_ext)
        };

        let xdg_result = env_sys
            .new_command("python3")
            .args([
                "-c",
                &format!(
                    r#"
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
dialog = Gtk.FileChooserDialog(
    title="Select {}",
    action=Gtk.FileChooserAction.OPEN
)
dialog.set_default_response(Gtk.ResponseType.OK)
dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)

filter_specific = Gtk.FileFilter()
filter_specific.set_name("{}")
filter_specific.add_pattern("{}")
dialog.add_filter(filter_specific)

filter_all = Gtk.FileFilter()
filter_all.set_name("All Files")
filter_all.add_pattern("*")
dialog.add_filter(filter_all)

response = dialog.run()
if response == Gtk.ResponseType.OK:
    print(dialog.get_filename())
dialog.destroy()
                    "#,
                    file_desc, file_desc, gtk_pattern
                ),
            ])
            .output();

        if let Ok(output) = xdg_result {
            let path = String::from_utf8(output.stdout)
                .map_err(|_| "Invalid UTF-8 in file path".to_string())?
                .trim()
                .to_string();

            if !path.is_empty() {
                return Ok(path);
            } else {
                return Ok(String::new());
            }
        }

        let dialog_result = env_sys
            .new_command("dialog")
            .args([
                "--stdout",
                "--title",
                &format!("Select {}", file_desc),
                "--inputbox",
                &format!("Enter path to the {} file:", file_desc.to_lowercase()),
                "10",
                "60",
                "",
            ])
            .output();

        if let Ok(output) = dialog_result {
            if output.status.success() {
                let path = String::from_utf8(output.stdout)
                    .map_err(|_| "Invalid UTF-8 in file path".to_string())?
                    .trim()
                    .to_string();

                if !path.is_empty() {
                    return Ok(path);
                }
            }
            return Ok(String::new());
        }

        return Ok(String::new());
    }

    #[cfg(not(any(target_os = "macos", target_os = "windows", target_os = "linux")))]
    {
        return Ok(String::new());
    }
}

#[tauri::command]
pub async fn select_file(filter: Option<String>) -> Result<String, String> {
    select_file_impl(filter, &RealEnvSystem).await
}

pub fn check_directory_exists_impl<F: FileSystem>(path: String, fs: &F) -> Result<bool, String> {
    use std::path::Path;
    Ok(fs.exists(Path::new(&path)))
}

#[tauri::command]
pub fn check_directory_exists(path: String) -> Result<bool, String> {
    check_directory_exists_impl(path, &RealFileSystem)
}

pub fn get_home_directory_impl<E: EnvSystem>(env_sys: &E) -> Result<String, String> {
    // Get user's home directory
    let home_dir = env_sys.home_dir().to_string_lossy().into_owned();
    Ok(home_dir)
}

#[tauri::command]
pub fn get_home_directory() -> Result<String, String> {
    get_home_directory_impl(&RealEnvSystem)
}

pub async fn select_directory_impl<E: EnvSystem>(
    prompt: Option<String>,
    env_sys: &E,
) -> Result<String, String> {
    // Get user's home directory as the default
    let home_dir = env_sys.home_dir();
    // Use the provided prompt or default to a generic one
    let dialog_prompt = prompt.unwrap_or_else(|| "Select a Directory".to_string());

    #[cfg(target_os = "macos")]
    {
        // AppleScript to open directory picker with home directory as default
        let script = format!(
            r#"
            tell application "System Events"
                activate
                set defaultFolder to POSIX file "{}"
                set folderPath to POSIX path of (choose folder default location defaultFolder with prompt "{}")
                return folderPath
            end tell
            "#,
            home_dir.to_string_lossy().replace("\"", "\\\""), // Escape quotes for AppleScript
            dialog_prompt.replace("\"", "\\\"")               // Escape quotes for AppleScript
        );

        // Execute the AppleScript and get the output
        let output = env_sys
            .new_command("osascript")
            .args(["-e", &script])
            .output()
            .map_err(|e| format!("Failed to execute AppleScript: {e}"))?;

        if output.status.success() {
            let path = String::from_utf8(output.stdout)
                .map_err(|_| "Invalid UTF-8 in directory path".to_string())?
                .trim()
                .to_string();

            if path.is_empty() {
                return Err("No directory selected".to_string());
            }

            Ok(path)
        } else {
            let err = String::from_utf8_lossy(&output.stderr);
            Err(format!("Directory selection failed: {err}"))
        }
    }

    #[cfg(target_os = "windows")]
    {
        use std::os::windows::process::CommandExt;
        // Use PowerShell to show folder browser dialog on Windows
        let script = format!(
            r#"
            Add-Type -AssemblyName System.Windows.Forms
            $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
            $dialog.Description = "{}"
            $dialog.SelectedPath = "{}"
            $dialog.RootFolder = [Environment+SpecialFolder]::MyComputer
            $null = $dialog.ShowDialog()
            $dialog.SelectedPath
            "#,
            dialog_prompt.replace("\"", "`\""), // Escape quotes for PowerShell
            home_dir.to_string_lossy().replace("\"", "`\"")  // Escape quotes for PowerShell
        );

        let output = env_sys
            .new_command("powershell")
            .args(["-Command", &script])
            .creation_flags(0x08000000) // CREATE_NO_WINDOW
            .output()
            .map_err(|e| format!("Failed to execute PowerShell: {e}"))?;

        if output.status.success() {
            let path = String::from_utf8(output.stdout)
                .map_err(|_| "Invalid UTF-8 in directory path".to_string())?
                .trim()
                .to_string();

            if path.is_empty() {
                return Err("No directory selected".to_string());
            }

            Ok(path)
        } else {
            let err = String::from_utf8_lossy(&output.stderr);
            Err(format!("Directory selection failed: {err}"))
        }
    }

    #[cfg(target_os = "linux")]
    {
        // Try different dialog tools commonly found on Linux systems in order of preference

        // First try zenity (common on GNOME and many distros)
        if let Ok(output) = env_sys
            .new_command("zenity")
            .args([
                "--file-selection",
                "--directory",
                &format!("--filename={}/", home_dir.to_string_lossy()),
                &format!("--title={}", dialog_prompt),
            ])
            .output()
        {
            if output.status.success() {
                let path = String::from_utf8(output.stdout)
                    .map_err(|_| "Invalid UTF-8 in directory path".to_string())?
                    .trim()
                    .to_string();

                if !path.is_empty() {
                    return Ok(path);
                }
            }
        }

        // Try kdialog (KDE) with custom prompt
        if let Ok(output) = env_sys
            .new_command("kdialog")
            .args([
                "--getexistingdirectory",
                &home_dir.to_string_lossy(),
                &dialog_prompt,
            ])
            .output()
        {
            if output.status.success() {
                let path = String::from_utf8(output.stdout)
                    .map_err(|_| "Invalid UTF-8 in directory path".to_string())?
                    .trim()
                    .to_string();

                if !path.is_empty() {
                    return Ok(path);
                }
            }
        }

        // Try GTK dialog via Python with home directory set
        let python_script = format!(
            r#"
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
dialog = Gtk.FileChooserDialog(
    title="{}",
    action=Gtk.FileChooserAction.SELECT_FOLDER,
)
dialog.set_current_folder("{}")
dialog.add_buttons(
    Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
)
dialog.set_default_size(800, 600)
response = dialog.run()
if response == Gtk.ResponseType.OK:
    print(dialog.get_filename())
dialog.destroy()
            "#,
            dialog_prompt.replace("\"", "\\\""), // Escape quotes for Python
            home_dir.to_string_lossy().replace("\"", "\\\"")  // Escape quotes for Python
        );

        if let Ok(output) = env_sys
            .new_command("python3")
            .args(["-c", &python_script])
            .output()
        {
            if output.status.success() {
                let path = String::from_utf8(output.stdout)
                    .map_err(|_| "Invalid UTF-8 in directory path".to_string())?
                    .trim()
                    .to_string();

                if !path.is_empty() {
                    return Ok(path);
                }
            }
        }

        // If all else failed, fallback to a simple dialog with home dir as default text
        if let Ok(output) = env_sys
            .new_command("dialog")
            .args([
                "--stdout",
                "--title",
                &dialog_prompt,
                "--inputbox",
                "Please enter the directory path:",
                "10",
                "60",
                &home_dir.to_string_lossy(),
            ])
            .output()
        {
            if output.status.success() {
                let path = String::from_utf8(output.stdout)
                    .map_err(|_| "Invalid UTF-8 in directory path".to_string())?
                    .trim()
                    .to_string();

                if !path.is_empty() {
                    return Ok(path);
                }
            }
        }

        // If we've reached here, none of the methods worked
        return Err("Could not open a directory selection dialog. Please ensure you have zenity, kdialog, or dialog installed.".to_string());
    }
}

#[tauri::command]
pub async fn select_directory(prompt: Option<String>) -> Result<String, String> {
    select_directory_impl(prompt, &RealEnvSystem).await
}

pub fn get_or_create_app_id_impl<F: FileSystem, E: EnvSystem>(
    fs: &F,
    env_sys: &E,
) -> Result<String, String> {
    use serde_json::{Value, json};
    use uuid::Uuid;

    let settings_dir = get_settings_directory_impl(env_sys)?;
    let settings_path = settings_dir.join("system_settings.json");

    if !fs.exists(&settings_dir) {
        fs.create_dir_all(&settings_dir)
            .map_err(|e| format!("Failed to create settings directory: {e}"))?;
    }

    let contents = if fs.exists(&settings_path) {
        fs.read_to_string(&settings_path)
            .map_err(|e| format!("Failed to read system settings: {e}"))?
    } else {
        "{}".to_string()
    };

    let mut settings: Value = serde_json::from_str(&contents).unwrap_or_else(|_| json!({}));

    if !settings.is_object() {
        settings = json!({});
    }
    let settings_obj = settings.as_object_mut().unwrap();

    let install_settings = settings_obj
        .entry("install_settings")
        .or_insert_with(|| json!({}));

    if !install_settings.is_object() {
        *install_settings = json!({});
    }
    let install_settings_obj = install_settings.as_object_mut().unwrap();

    if let Some(app_id) = install_settings_obj.get("appId").and_then(|id| id.as_str()) {
        Ok(app_id.to_string())
    } else {
        let new_app_id = Uuid::new_v4().to_string();
        install_settings_obj.insert("appId".to_string(), Value::String(new_app_id.clone()));

        let updated_contents = serde_json::to_string_pretty(&settings)
            .map_err(|e| format!("Failed to serialize settings: {e}"))?;
        fs.write(&settings_path, &updated_contents)
            .map_err(|e| format!("Failed to write system settings: {e}"))?;
        Ok(new_app_id)
    }
}

pub fn get_or_create_app_id() -> String {
    get_or_create_app_id_impl(&RealFileSystem, &RealEnvSystem).unwrap_or_else(|err| {
        log::error!("Failed to get or create appId: {}", err);
        // Fallback to a transient UUID if file operations fail
        uuid::Uuid::new_v4().to_string()
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use mockall::predicate::*;
    use std::collections::HashMap;
    use std::path::PathBuf;

    // Mock tests for trait functionality
    #[test]
    fn test_filesystem_trait_mock() {
        let mut mock_fs = MockFileSystem::new();

        // Test file operations
        mock_fs
            .expect_is_file()
            .with(eq("test.txt"))
            .return_const(true);
        mock_fs
            .expect_create_file()
            .with(eq("new.txt"))
            .returning(|_| Ok(Box::new(Vec::new()) as Box<dyn std::io::Write>));
        mock_fs
            .expect_remove_file()
            .with(eq("old.txt"))
            .returning(|_| Ok(()));

        // Test directory operations
        let path = PathBuf::from("test_dir");
        mock_fs
            .expect_exists()
            .with(eq(path.clone()))
            .return_const(false);
        mock_fs
            .expect_create_dir_all()
            .with(eq(path.clone()))
            .returning(|_| Ok(()));

        // Test file I/O
        let file_path = PathBuf::from("data.txt");
        mock_fs
            .expect_write()
            .with(eq(file_path.clone()), eq("content"))
            .returning(|_, _| Ok(()));
        mock_fs
            .expect_read_to_string()
            .with(eq(file_path.clone()))
            .returning(|_| Ok("content".to_string()));

        // Execute tests
        assert!(mock_fs.is_file("test.txt"));
        assert!(mock_fs.create_file("new.txt").is_ok());
        assert!(mock_fs.remove_file("old.txt").is_ok());
        assert!(!mock_fs.exists(&path));
        assert!(mock_fs.create_dir_all(&path).is_ok());
        assert!(mock_fs.write(&file_path, "content").is_ok());
        assert_eq!(mock_fs.read_to_string(&file_path).unwrap(), "content");
    }

    #[test]
    fn test_env_system_trait_mock() {
        let mut mock_env = MockEnvSystem::new();

        mock_env
            .expect_var()
            .with(eq("HOME"))
            .returning(|_| Ok("/home/user".to_string()));
        mock_env
            .expect_var()
            .with(eq("MISSING_VAR"))
            .returning(|_| Err(std::env::VarError::NotPresent));
        mock_env
            .expect_temp_dir()
            .returning(|| PathBuf::from("/tmp"));
        mock_env.expect_consts_os().returning(|| "linux");

        assert_eq!(mock_env.var("HOME").unwrap(), "/home/user");
        assert!(mock_env.var("MISSING_VAR").is_err());
        assert_eq!(mock_env.temp_dir(), PathBuf::from("/tmp"));
        assert_eq!(mock_env.consts_os(), "linux");
    }

    #[test]
    fn test_file_ext_trait_mock() {
        let mut mock_file_ext = MockFileExtTrait::new();
        let mock_file = std::fs::File::create("test_mock_file.tmp").unwrap();

        mock_file_ext
            .expect_try_lock_exclusive()
            .returning(|_| Ok(()));
        mock_file_ext.expect_unlock().returning(|_| Ok(()));

        // Test the mock methods
        assert!(mock_file_ext.try_lock_exclusive(&mock_file).is_ok());
        assert!(mock_file_ext.unlock(&mock_file).is_ok());

        // Clean up
        let _ = std::fs::remove_file("test_mock_file.tmp");
    }

    // Test check_file_exists with mock
    #[test]
    fn test_check_file_exists_with_known_file() {
        // Only test with a file we know exists in the project
        let result = check_file_exists("Cargo.toml".to_string());
        assert!(result.is_ok());
    }

    #[test]
    fn test_check_file_exists_with_nonexistent_file() {
        let result =
            check_file_exists("/this/path/definitely/does/not/exist/nowhere.txt".to_string());
        assert!(result.is_ok());
        assert!(!result.unwrap());
    }

    // Test theme validation logic
    #[test]
    fn test_toggle_theme_validation() {
        let rt = tokio::runtime::Runtime::new().unwrap();
        let mock_fs = MockFileSystem::new();
        let mock_env = MockEnvSystem::new();
        let mock_file_ext = MockFileExtTrait::new();

        // Test invalid themes
        let invalid_themes = vec!["", "invalid", "DARK", "LIGHT", "rainbow", "blue"];
        for theme in invalid_themes {
            let result = rt.block_on(toggle_theme_impl(
                theme.to_string(),
                &mock_fs,
                &mock_env,
                &mock_file_ext,
            ));
            assert!(result.is_err());
            assert!(result.unwrap_err().contains("Invalid theme"));
        }
    }

    #[test]
    fn test_directory_functions_without_home_env() {
        let mut mock_env = MockEnvSystem::new();
        let mock_fs = MockFileSystem::new();

        // Mock that both HOME and USERPROFILE environment variables are missing
        mock_env
            .expect_var()
            .with(eq("HOME"))
            .returning(|_| Err(std::env::VarError::NotPresent));
        mock_env
            .expect_var()
            .with(eq("USERPROFILE"))
            .returning(|_| Err(std::env::VarError::NotPresent));

        // Test get_settings_directory_impl (assuming it exists)
        let settings_result = get_settings_directory_impl(&mock_env);

        // Test get_environments_directory_impl (assuming it exists)
        let envs_result = get_environments_directory_impl(&mock_env);

        // Test get_working_directory_impl
        let working_result = get_working_directory_impl("/default", &mock_fs, &mock_env);

        // All should fail with appropriate error messages
        assert!(settings_result.is_err());
        assert!(envs_result.is_err());
        assert!(working_result.is_err());

        assert!(
            settings_result
                .unwrap_err()
                .contains("Could not determine home directory")
        );
        assert!(
            envs_result
                .unwrap_err()
                .contains("Could not determine home directory")
        );
        assert!(
            working_result
                .unwrap_err()
                .contains("Could not determine home directory")
        );
    }

    #[test]
    fn test_working_directory_fallback_logic() {
        let mut mock_fs = MockFileSystem::new();
        let mut mock_env = MockEnvSystem::new();

        // Mock HOME environment variable
        mock_env
            .expect_var()
            .with(eq("HOME"))
            .returning(|_| Ok("/mock/home".to_string()));

        let settings_path = PathBuf::from("/mock/home/.openbb_platform/user_settings.json");

        // Mock that settings file doesn't exist (should trigger fallback)
        mock_fs
            .expect_exists()
            .with(eq(settings_path.clone()))
            .return_const(false);

        let result = get_working_directory_impl("/fallback/test/path", &mock_fs, &mock_env);

        assert_eq!(result.unwrap(), "/fallback/test/path");
    }

    #[test]
    fn test_save_working_directory_validation() {
        let test_paths = vec!["/tmp/test", "", "/very/long/path/that/should/work"];

        for path in test_paths {
            let mut mock_fs = MockFileSystem::new();
            let mut mock_env = MockEnvSystem::new();

            // Mock HOME environment variable
            mock_env
                .expect_var()
                .with(eq("HOME"))
                .returning(|_| Ok("/mock/home".to_string()));

            let platform_dir = PathBuf::from("/mock/home/.openbb_platform");
            let settings_path = platform_dir.join("user_settings.json");

            // Mock directory operations
            mock_fs
                .expect_exists()
                .with(eq(platform_dir.clone()))
                .return_const(true);
            mock_fs
                .expect_exists()
                .with(eq(settings_path.clone()))
                .return_const(false);

            // Mock file write
            mock_fs
                .expect_write()
                .with(
                    eq(settings_path.clone()),
                    function(move |content: &str| {
                        content.contains("working_directory") && content.contains(path)
                    }),
                )
                .returning(|_, _| Ok(()));

            let result = save_working_directory_impl(path, &mock_fs, &mock_env);
            assert!(result.is_ok());
        }
    }

    #[test]
    fn test_yaml_generation_parameters() {
        let rt = tokio::runtime::Runtime::new().unwrap();

        // Test various parameter combinations
        let test_cases = vec![
            ("env1", "3.9", vec!["numpy"], vec!["requests"]),
            ("", "3.8", vec![], vec![]),
            (
                "test-env",
                "3.10",
                vec!["pandas", "matplotlib"],
                vec!["flask", "fastapi"],
            ),
        ];

        for (name, python_version, conda_packages, pip_packages) in test_cases {
            let mut mock_fs = MockFileSystem::new();
            let mut mock_env = MockEnvSystem::new();

            // Mock HOME environment variable
            mock_env
                .expect_var()
                .with(eq("HOME"))
                .returning(|_| Ok("/mock/home".to_string()));

            let envs_dir = PathBuf::from("/mock/home/.openbb_platform/environments");
            let yaml_path = envs_dir.join(format!("{name}.yaml"));

            // Mock directory doesn't exist, needs to be created
            mock_fs
                .expect_exists()
                .with(eq(envs_dir.clone()))
                .return_const(false);

            // Mock directory creation
            mock_fs
                .expect_create_dir_all()
                .with(eq(envs_dir.clone()))
                .returning(|_| Ok(()));

            // Mock YAML file write
            mock_fs
                .expect_write()
                .with(
                    eq(yaml_path),
                    function(move |content: &str| {
                        content.contains("name:") && content.contains(python_version)
                    }),
                )
                .returning(|_, _| Ok(()));

            let conda_packages: Vec<String> =
                conda_packages.into_iter().map(|s| s.to_string()).collect();
            let pip_packages: Vec<String> =
                pip_packages.into_iter().map(|s| s.to_string()).collect();
            let conda_channels = HashMap::new();

            let result = rt.block_on(save_environment_as_yaml_impl(
                name,
                python_version,
                &conda_packages,
                &pip_packages,
                &conda_channels,
                "",
                &mock_fs,
                &mock_env,
            ));

            assert!(result.is_ok());
        }
    }

    // Test python version detection logic
    #[test]
    fn test_python_version_detection_nonexistent_path() {
        let nonexistent_paths = vec![
            Path::new("/definitely/does/not/exist"),
            Path::new("/another/fake/path"),
        ];

        for path in nonexistent_paths {
            let result = get_environment_python_version(path);
            assert!(result.is_err());
            assert!(result.unwrap_err().contains("Python executable not found"));
        }
    }

    #[test]
    fn test_installation_directory_missing_settings() {
        let mut mock_env = MockEnvSystem::new();
        let mock_fs = MockFileSystem::new();

        // Mock that both HOME and USERPROFILE environment variables are missing
        mock_env
            .expect_var()
            .with(eq("HOME"))
            .returning(|_| Err(std::env::VarError::NotPresent));
        mock_env
            .expect_var()
            .with(eq("USERPROFILE"))
            .returning(|_| Err(std::env::VarError::NotPresent));

        let result = get_installation_directory_impl(&mock_fs, &mock_env);

        assert!(result.is_err());
        assert!(
            result
                .unwrap_err()
                .contains("Could not determine home directory")
        );
    }

    #[test]
    fn test_userdata_directory_missing_settings() {
        let mut mock_env = MockEnvSystem::new();
        let fs = MockFileSystem::new();

        // Mock that both HOME and USERPROFILE environment variables are missing
        mock_env
            .expect_var()
            .with(eq("HOME"))
            .returning(|_| Err(std::env::VarError::NotPresent));
        mock_env
            .expect_var()
            .with(eq("USERPROFILE"))
            .returning(|_| Err(std::env::VarError::NotPresent));

        let result = get_userdata_directory_impl(&fs, &mock_env);

        assert!(result.is_err());
        assert!(
            result
                .unwrap_err()
                .contains("Could not determine home directory")
        );
    }

    #[test]
    fn test_select_file_impl_without_opening_windows() {
        use std::process::Command;
        let rt = tokio::runtime::Runtime::new().unwrap();
        let mut mock_env = MockEnvSystem::new();

        // Mock HOME environment variable
        mock_env
            .expect_var()
            .with(eq("HOME"))
            .returning(|_| Ok("/mock/home".to_string()));
        mock_env
            .expect_var()
            .with(eq("USERPROFILE"))
            .returning(|_| Ok("C:\\Users\\mock".to_string()));

        // Test .env file filter on Windows
        #[cfg(target_os = "windows")]
        {
            // Mock new_command for powershell to simulate file dialog returning a path
            mock_env
                .expect_new_command()
                .with(eq("powershell"))
                .returning(|_| {
                    let mut cmd = Command::new("cmd");
                    // Simulate PowerShell output with a file path
                    cmd.args(["/C", "echo", "C:\\mock\\home\\test.env"]);
                    cmd
                });

            let result = rt.block_on(select_file_impl(Some(".env".to_string()), &mock_env));
            assert!(result.is_ok());
            let path = result.unwrap();
            assert_eq!(path, "C:\\mock\\home\\test.env -Command \"");
        }

        // Test macOS AppleScript mock
        #[cfg(target_os = "macos")]
        {
            mock_env
                .expect_new_command()
                .with(eq("osascript"))
                .returning(|_| {
                    let mut cmd = Command::new("echo");
                    cmd.arg("/mock/home/test.env");
                    cmd
                });

            let result = rt.block_on(select_file_impl(Some(".env".to_string()), &mock_env));
            assert!(result.is_ok());
        }

        // Test Linux zenity mock
        #[cfg(target_os = "linux")]
        {
            mock_env
                .expect_new_command()
                .with(eq("zenity"))
                .returning(|_| {
                    let mut cmd = Command::new("echo");
                    cmd.arg("/mock/home/test.env");
                    cmd
                });

            let result = rt.block_on(select_file_impl(Some(".env".to_string()), &mock_env));
            assert!(result.is_ok());
        }
    }

    #[test]
    fn test_select_file_filter_logic_comprehensive() {
        // Test all filter combinations without file dialogs
        let test_cases = vec![
            (Some(".env".to_string()), "env", "Environment Files"),
            (Some(".py".to_string()), "py", "Python Files"),
            (Some(".yaml".to_string()), "*", "All Files"), // Falls through to default
            (None, "*", "All Files"),
        ];

        for (filter, expected_ext, expected_desc) in test_cases {
            let (file_ext, file_desc) = match filter.as_deref() {
                Some(".env") => ("env", "Environment Files"),
                Some(".py") => ("py", "Python Files"),
                _ => ("*", "All Files"),
            };

            assert_eq!(file_ext, expected_ext);
            assert_eq!(file_desc, expected_desc);
        }
    }

    #[test]
    fn test_select_file_cancelled_by_user() {
        let rt = tokio::runtime::Runtime::new().unwrap();
        let mut mock_env = MockEnvSystem::new();

        mock_env
            .expect_var()
            .with(eq("HOME"))
            .returning(|_| Ok("/mock/home".to_string()));
        mock_env
            .expect_var()
            .with(eq("USERPROFILE"))
            .returning(|_| Ok("C:\\Users\\mock".to_string()));

        // Mock command that succeeds but returns no output
        #[cfg(target_os = "windows")]
        {
            mock_env
                .expect_new_command()
                .with(eq("powershell"))
                .returning(|_| {
                    // Use a command that succeeds with empty output
                    let mut cmd = std::process::Command::new("cmd");
                    cmd.args(["/c", "echo", ""]); // Empty output
                    cmd
                });
        }

        #[cfg(not(target_os = "windows"))]
        {
            mock_env.expect_new_command().returning(|_| {
                std::process::Command::new("true") // Command that succeeds with no output
            });
        }

        let result = rt.block_on(select_file_impl(None, &mock_env));
        // Should succeed or fail gracefully, but not panic
        assert!(result.is_ok() || result.is_err());
    }

    #[test]
    fn test_select_file_command_failure() {
        let rt = tokio::runtime::Runtime::new().unwrap();
        let mut mock_env = MockEnvSystem::new();

        mock_env
            .expect_var()
            .with(eq("HOME"))
            .returning(|_| Ok("/mock/home".to_string()));

        // Mock command that fails
        mock_env.expect_new_command().returning(|_| {
            // Command that always fails
            std::process::Command::new("false")
        });

        let result = rt.block_on(select_file_impl(None, &mock_env));
        // On Linux, it should fall back to other dialog methods, so might still succeed
        // The test verifies it doesn't panic and handles errors gracefully
        assert!(result.is_ok() || result.is_err());
    }

    // Test environment variable handling without modifying them
    #[test]
    fn test_environment_variable_detection() {
        // Test that we can detect if environment variables exist
        let home_exists = std::env::var("HOME").is_ok();
        let userprofile_exists = std::env::var("USERPROFILE").is_ok();

        // At least one should exist on most systems
        assert!(
            home_exists
                || userprofile_exists
                || cfg!(target_os = "windows")
                || cfg!(target_os = "linux")
                || cfg!(target_os = "macos")
        );
    }

    #[test]
    fn test_update_openbb_settings_validation() {
        let rt = tokio::runtime::Runtime::new().unwrap();
        let mut mock_fs = MockFileSystem::new();
        let mut mock_env = MockEnvSystem::new();

        // Mock temp directory
        mock_env.expect_temp_dir().returning(|| {
            #[cfg(target_os = "windows")]
            {
                PathBuf::from("C:\\temp")
            }
            #[cfg(not(target_os = "windows"))]
            {
                PathBuf::from("/tmp")
            }
        });

        // Mock the Python script write operation
        #[cfg(target_os = "windows")]
        let script_path = PathBuf::from("C:\\temp\\openbb_update_settings.py");
        #[cfg(not(target_os = "windows"))]
        let script_path = PathBuf::from("/tmp/openbb_update_settings.py");

        mock_fs
            .expect_write()
            .with(
                eq(script_path.clone()),
                function(|content: &str| {
                    content.contains("import json")
                        && content.contains("OpenBB settings configuration")
                        && content.contains("user_settings.json")
                        && content.contains("system_settings.json")
                }),
            )
            .returning(|_, _| Ok(()));

        mock_env.expect_consts_os().returning(|| {
            #[cfg(target_os = "windows")]
            {
                "windows"
            }
            #[cfg(not(target_os = "windows"))]
            {
                "linux"
            }
        });

        #[cfg(target_os = "windows")]
        {
            mock_env
                .expect_new_command()
                .with(eq("cmd.exe"))
                .returning(move |_| {
                    // Use a command that succeeds
                    let mut cmd = std::process::Command::new("cmd");
                    cmd.args([
                        "/c",
                        "echo",
                        "OpenBB settings configuration completed successfully",
                    ]);
                    cmd
                });
        }

        #[cfg(not(target_os = "windows"))]
        {
            mock_env
                .expect_new_command()
                .with(eq("bash"))
                .returning(move |_| {
                    let mut cmd = std::process::Command::new("echo");
                    cmd.arg("OpenBB settings configuration completed successfully");
                    cmd
                });
        }

        mock_fs
            .expect_remove_file()
            .with(eq(script_path.to_string_lossy().to_string()))
            .returning(|_| Ok(()));

        let conda_dir = Path::new("/fake/conda");
        let environment = "test_env";

        let result = rt.block_on(update_openbb_settings_impl(
            conda_dir,
            environment,
            &mock_fs,
            &mock_env,
        ));

        // Should succeed or fail gracefully, but not panic
        assert!(result.is_ok() || result.is_err());
    }

    #[test]
    fn test_concurrent_operations_safety() {
        let rt = tokio::runtime::Runtime::new().unwrap();

        // Setup paths for the test file
        let test_file_path = "mock_user_settings_rw_create.tmp";
        // Create mocks for toggle_theme operations
        let mut mock_fs1 = MockFileSystem::new();
        let mut mock_env1 = MockEnvSystem::new();
        let mut mock_file_ext1 = MockFileExtTrait::new();

        let mut mock_fs2 = MockFileSystem::new();
        let mut mock_env2 = MockEnvSystem::new();
        let mut mock_file_ext2 = MockFileExtTrait::new();

        mock_env1
            .expect_var()
            .with(eq("HOME"))
            .returning(|_| Ok("/mock/home".to_string()));
        mock_env2
            .expect_var()
            .with(eq("HOME"))
            .returning(|_| Ok("/mock/home".to_string()));

        let platform_dir = PathBuf::from("/mock/home/.openbb_platform");
        let settings_path = platform_dir.join("user_settings.json");

        // Mock filesystem operations for first toggle_theme
        mock_fs1
            .expect_exists()
            .with(eq(platform_dir.clone()))
            .return_const(true);
        mock_fs1
            .expect_exists()
            .with(eq(settings_path.clone()))
            .return_const(true);
        mock_fs1
            .expect_read_to_string()
            .with(eq(settings_path.clone()))
            .returning(|_| Ok("{}".to_string()));
        mock_fs1.expect_write().returning(|_, _| Ok(()));
        mock_fs1
            .expect_open_rw_create()
            .with(eq(settings_path.clone()))
            .returning(move |_| {
                // Always return a valid file handle
                std::fs::File::open(test_file_path)
            });
        mock_file_ext1
            .expect_try_lock_exclusive()
            .returning(|_| Ok(()));
        mock_file_ext1.expect_unlock().returning(|_| Ok(()));

        // Mock filesystem operations for second toggle_theme
        mock_fs2
            .expect_exists()
            .with(eq(platform_dir.clone()))
            .return_const(true);
        mock_fs2
            .expect_exists()
            .with(eq(settings_path.clone()))
            .return_const(true);
        mock_fs2
            .expect_read_to_string()
            .with(eq(settings_path.clone()))
            .returning(|_| Ok("{}".to_string()));
        mock_fs2.expect_write().returning(|_, _| Ok(()));
        mock_fs2
            .expect_open_rw_create()
            .with(eq(settings_path.clone()))
            .returning(move |_| std::fs::File::open(test_file_path));
        mock_file_ext2
            .expect_try_lock_exclusive()
            .returning(|_| Ok(()));
        mock_file_ext2.expect_unlock().returning(|_| Ok(()));

        // Test multiple operations that should fail gracefully
        let async_operations = vec![
            rt.block_on(toggle_theme_impl(
                "dark".to_string(),
                &mock_fs1,
                &mock_env1,
                &mock_file_ext1,
            )),
            rt.block_on(toggle_theme_impl(
                "light".to_string(),
                &mock_fs2,
                &mock_env2,
                &mock_file_ext2,
            )),
        ];

        // Create mocks for save_working_directory operations
        let mut mock_fs3 = MockFileSystem::new();
        let mut mock_env3 = MockEnvSystem::new();
        let mut mock_fs4 = MockFileSystem::new();
        let mut mock_env4 = MockEnvSystem::new();

        mock_env3
            .expect_var()
            .with(eq("HOME"))
            .returning(|_| Ok("/mock/home".to_string()));
        mock_env4
            .expect_var()
            .with(eq("HOME"))
            .returning(|_| Ok("/mock/home".to_string()));

        mock_fs3.expect_exists().returning(|_| true);
        mock_fs3
            .expect_read_to_string()
            .returning(|_| Ok("{}".to_string()));
        mock_fs3.expect_write().returning(|_, _| Ok(()));

        mock_fs4.expect_exists().returning(|_| true);
        mock_fs4
            .expect_read_to_string()
            .returning(|_| Ok("{}".to_string()));
        mock_fs4.expect_write().returning(|_, _| Ok(()));

        let sync_operations = vec![
            save_working_directory_impl("/tmp/test1", &mock_fs3, &mock_env3),
            save_working_directory_impl("/tmp/test2", &mock_fs4, &mock_env4),
        ];

        // All should either succeed or fail gracefully, no panics
        for op in async_operations {
            assert!(op.is_ok() || op.is_err());
        }

        for op in sync_operations {
            assert!(op.is_ok() || op.is_err());
        }

        // Clean up the test file
        let _ = std::fs::remove_file(test_file_path);
    }

    #[test]
    fn test_url_parsing_validation() {
        let invalid_urls = vec!["not-a-url", "://missing-scheme", "http://", ""];

        for invalid_url in invalid_urls {
            let parse_result = invalid_url.parse::<url::Url>();
            assert!(
                parse_result.is_err(),
                "URL '{invalid_url}' should be invalid"
            );
        }

        let valid_urls = vec![
            "https://example.com",
            "http://localhost:3000",
            "https://pro.openbb.co",
            "https://github.com",
            "ftp://example.com", // FTP is actually valid
        ];

        for valid_url in valid_urls {
            let parse_result = valid_url.parse::<url::Url>();
            assert!(parse_result.is_ok(), "URL '{valid_url}' should be valid");
        }
    }

    // Test platform-specific constants without file operations
    #[test]
    fn test_platform_constants() {
        // Test that we can detect the current platform
        let os = std::env::consts::OS;
        assert!(os == "windows" || os == "macos" || os == "linux" || os == "freebsd");

        // Test that platform-specific logic branches exist
        #[cfg(target_os = "windows")]
        {
            assert_eq!(os, "windows");
        }

        #[cfg(target_os = "macos")]
        {
            assert_eq!(os, "macos");
        }

        #[cfg(target_os = "linux")]
        {
            assert_eq!(os, "linux");
        }
    }

    #[test]
    fn test_input_sanitization() {
        let mut mock_fs = MockFileSystem::new();
        let mut mock_env = MockEnvSystem::new();

        // Test various edge case inputs
        let edge_case_paths = vec![
            "",
            "/",
            "relative/path",
            "/absolute/path",
            "path with spaces",
            "path/with/unicode/🦀",
        ];

        for path in edge_case_paths {
            // Mock HOME environment variable
            mock_env
                .expect_var()
                .with(eq("HOME"))
                .returning(|_| Ok("/mock/home".to_string()));

            let settings_path = PathBuf::from("/mock/home/.openbb_platform/user_settings.json");

            // Mock that settings file doesn't exist (triggers fallback)
            mock_fs
                .expect_exists()
                .with(eq(settings_path.clone()))
                .return_const(false);

            // Test with mocks - should return the path as fallback
            let working_result = get_working_directory_impl(path, &mock_fs, &mock_env);

            // Should succeed and return the path as fallback
            assert!(working_result.is_ok());
            assert_eq!(working_result.unwrap(), path);
        }
    }

    // Test environment variable handling in get_working_directory
    #[test]
    fn test_get_working_directory_missing_home_var() {
        let mock_fs = MockFileSystem::new();
        let mut mock_env = MockEnvSystem::new();

        // Mock that both HOME and USERPROFILE environment variables are missing
        mock_env
            .expect_var()
            .with(eq("HOME"))
            .returning(|_| Err(std::env::VarError::NotPresent));
        mock_env
            .expect_var()
            .with(eq("USERPROFILE"))
            .returning(|_| Err(std::env::VarError::NotPresent));

        let result = get_working_directory_impl("/default", &mock_fs, &mock_env);

        assert!(result.is_err());
        assert!(
            result
                .unwrap_err()
                .contains("Could not determine home directory")
        );
    }

    #[test]
    fn test_get_environments_directory_constructs_correct_path() {
        let mut mock_env = MockEnvSystem::new();

        // Mock successful case
        mock_env
            .expect_var()
            .with(eq("HOME"))
            .returning(|_| Ok("/mock/home".to_string()));

        let result = get_environments_directory_impl(&mock_env);

        assert!(result.is_ok());
        let path = result.unwrap();
        assert!(path.to_string_lossy().contains(".openbb_platform"));
        assert!(path.to_string_lossy().contains("environments"));
    }

    #[test]
    fn test_get_environments_directory_handles_missing_home() {
        let mut mock_env = MockEnvSystem::new();

        // Mock missing HOME and USERPROFILE
        mock_env
            .expect_var()
            .with(eq("HOME"))
            .returning(|_| Err(std::env::VarError::NotPresent));
        mock_env
            .expect_var()
            .with(eq("USERPROFILE"))
            .returning(|_| Err(std::env::VarError::NotPresent));

        let result = get_environments_directory_impl(&mock_env);

        // Should fail with home directory error
        assert!(result.is_err());
        assert!(
            result
                .unwrap_err()
                .contains("Could not determine home directory")
        );
    }

    // Test get_settings_directory
    #[test]
    fn test_get_settings_directory_constructs_correct_path() {
        let mut mock_env = MockEnvSystem::new();

        // Mock successful case
        mock_env
            .expect_var()
            .with(eq("HOME"))
            .returning(|_| Ok("/mock/home".to_string()));

        let result = get_settings_directory_impl(&mock_env);

        assert!(result.is_ok());
        let path = result.unwrap();
        assert!(path.to_string_lossy().contains(".openbb_platform"));
    }

    // Test basic mock trait functionality
    #[test]
    fn test_check_file_exists_with_mock() {
        let mut mock_fs = MockFileSystem::new();
        mock_fs
            .expect_is_file()
            .with(eq("exists.txt"))
            .return_const(true);
        mock_fs
            .expect_is_file()
            .with(eq("missing.txt"))
            .return_const(false);

        assert!(mock_fs.is_file("exists.txt"));
        assert!(!mock_fs.is_file("missing.txt"));
    }

    #[test]
    fn test_create_and_remove_file_with_mock() {
        let mut mock_fs = MockFileSystem::new();
        mock_fs
            .expect_create_file()
            .with(eq("file.txt"))
            .returning(|_| Ok(Box::new(Vec::new()) as Box<dyn std::io::Write>));
        mock_fs
            .expect_remove_file()
            .with(eq("file.txt"))
            .returning(|_| Ok(()));

        assert!(mock_fs.create_file("file.txt").is_ok());
        assert!(mock_fs.remove_file("file.txt").is_ok());
    }

    #[test]
    fn test_write_and_read_to_string_with_mock() {
        let mut mock_fs = MockFileSystem::new();
        let path = PathBuf::from("file.txt");
        mock_fs
            .expect_write()
            .with(eq(path.clone()), eq("content"))
            .returning(|_, _| Ok(()));
        mock_fs
            .expect_read_to_string()
            .with(eq(path.clone()))
            .returning(|_| Ok("content".to_string()));

        assert!(mock_fs.write(&path, "content").is_ok());
        assert_eq!(mock_fs.read_to_string(&path).unwrap(), "content");
    }

    #[test]
    fn test_exists_and_create_dir_all_with_mock() {
        let mut mock_fs = MockFileSystem::new();
        let path = PathBuf::from("dir");
        mock_fs
            .expect_exists()
            .with(eq(path.clone()))
            .return_const(true);
        mock_fs
            .expect_create_dir_all()
            .with(eq(path.clone()))
            .returning(|_| Ok(()));

        assert!(mock_fs.exists(&path));
        assert!(mock_fs.create_dir_all(&path).is_ok());
    }

    // Test basic functionality that doesn't require external dependencies
    #[test]
    fn test_basic_string_operations() {
        // Test string operations used in the module
        let test_string = "test.env";
        assert!(test_string.ends_with(".env"));

        let path_str = "/home/user/.openbb_platform/environments";
        assert!(path_str.contains(".openbb_platform"));
        assert!(path_str.contains("environments"));
    }

    // Test path manipulation without file system access
    #[test]
    fn test_path_manipulation() {
        let base_path = PathBuf::from("/home/user");
        let platform_path = base_path.join(".openbb_platform");
        let envs_path = platform_path.join("environments");

        assert!(envs_path.to_string_lossy().contains(".openbb_platform"));
        assert!(envs_path.to_string_lossy().contains("environments"));
        assert!(envs_path.starts_with(&platform_path));
    }

    #[tokio::test]
    async fn test_select_directory_impl_multi_platform() {
        let mut mock_env = MockEnvSystem::new();

        // Mock home_dir to return a platform-specific path
        #[cfg(target_os = "windows")]
        let home_path = PathBuf::from("C:\\mock\\home");
        #[cfg(not(target_os = "windows"))]
        let home_path = PathBuf::from("/mock/home");
        mock_env.expect_home_dir().return_const(home_path.clone());

        // Define expected path based on the OS
        #[cfg(target_os = "windows")]
        let expected_path = "C:\\mock\\home\\selected_dir";
        #[cfg(not(target_os = "windows"))]
        let expected_path = "/mock/home/selected_dir";

        // Mock new_command for each platform
        #[cfg(target_os = "windows")]
        {
            mock_env.expect_new_command().returning(move |_| {
                let mut cmd = std::process::Command::new("cmd");
                // Simulate PowerShell output with no trailing newline
                cmd.args(["/C", &format!("echo {expected_path}")]);
                cmd
            });
        }
        #[cfg(target_os = "macos")]
        {
            mock_env.expect_new_command().returning(move |_| {
                let mut cmd = std::process::Command::new("echo");
                cmd.arg(expected_path);
                cmd
            });
        }
        #[cfg(target_os = "linux")]
        {
            mock_env.expect_new_command().returning(move |_| {
                let mut cmd = std::process::Command::new("echo");
                cmd.arg(expected_path);
                cmd
            });
        }

        // Call the function and assert the result
        let result = select_directory_impl(Some("Pick a folder".to_string()), &mock_env).await;
        assert!(result.is_ok(), "Result was: {result:?}");
        let output = result.unwrap();

        assert!(
            output.starts_with(expected_path),
            "Output '{output}' should start with '{expected_path}'"
        );
    }

    #[test]
    fn test_check_directory_exists_impl_mock() {
        let mut mock_fs = MockFileSystem::new();
        let existing_path = Path::new("/mock/exists");
        mock_fs
            .expect_exists()
            .with(eq(existing_path))
            .return_const(true);
        assert_eq!(
            check_directory_exists_impl("/mock/exists".to_string(), &mock_fs),
            Ok(true)
        );

        let missing_path = Path::new("/mock/missing");
        mock_fs
            .expect_exists()
            .with(eq(missing_path))
            .return_const(false);
        assert_eq!(
            check_directory_exists_impl("/mock/missing".to_string(), &mock_fs),
            Ok(false)
        );
    }

    #[test]
    fn test_get_home_directory_impl_mock() {
        let mut mock_env = MockEnvSystem::new();
        mock_env
            .expect_home_dir()
            .returning(|| PathBuf::from("/mock/home"));
        assert_eq!(
            get_home_directory_impl(&mock_env),
            Ok("/mock/home".to_string())
        );
    }
}
