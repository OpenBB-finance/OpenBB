// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

pub mod tauri_handlers;
pub mod uninstall;
pub mod utils;

use std::path::Path;
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};

use tauri::State;
use tauri::menu::{CheckMenuItemBuilder, Menu, MenuItemBuilder};
use tauri::tray::TrayIconBuilder;
use tauri::{AppHandle, Manager, RESTART_EXIT_CODE, Runtime};
use tauri_plugin_dialog::DialogExt;

#[cfg(target_os = "windows")]
extern crate winapi;

use crate::tauri_handlers::startup::{
    abort_installation, create_default_backend_services, get_installation_status, install_conda,
    install_to_directory, setup_python_environment,
};

use crate::tauri_handlers::environments::{
    create_environment, create_environment_from_requirements, execute_in_environment,
    get_environment_extensions, install_extensions, list_conda_environments, remove_environment,
    remove_extension, select_requirements_file, update_environment, update_extension,
    update_installation_error,
};

use crate::tauri_handlers::jupyter::{
    check_jupyter_server, list_jupyter_servers, open_jupyter_logs_window, start_jupyter_server,
    stop_all_jupyter_servers, stop_jupyter_server, update_jupyter_status,
};

use crate::tauri_handlers::credentials::{
    get_user_credentials, open_credentials_file, update_user_credentials,
};

use crate::tauri_handlers::backends::{
    create_backend_service, delete_backend_service, initialize_backends, list_backend_services,
    open_backend_logs_window, start_backend_service, stop_backend_service, update_backend_service,
};

use crate::utils::certs::generate_self_signed_cert;

use crate::tauri_handlers::helpers::{
    check_directory_exists, check_file_exists, get_home_directory, get_installation_directory,
    get_or_create_app_id, get_settings_directory, get_userdata_directory, get_working_directory,
    open_url_in_window, open_workspace_in_browser, save_working_directory, select_directory,
    select_file, toggle_theme, update_openbb_settings,
};

use tauri_plugin_updater::UpdaterExt;

use crate::utils::process_monitor::{
    GetProcessLogsRequest, LogEntry, LogStorage, RunningProcesses, get_log_storage,
    get_process_logs, init_process_monitoring, register_process, unregister_process,
};

use crate::uninstall::uninstall_application;

#[derive(Clone, serde::Serialize)]
struct InstallationState {
    is_installed: bool,
    installation_directory: Option<String>,
}

#[derive(Clone)]
struct ProcessLogState(LogStorage);

#[tauri::command]
fn register_process_monitoring(state: State<ProcessLogState>, process_id: String) -> bool {
    register_process(&state.0, &process_id)
}

#[tauri::command]
fn unregister_process_monitoring(state: State<ProcessLogState>, process_id: String) -> bool {
    unregister_process(&state.0, &process_id)
}

#[tauri::command]
fn get_process_logs_history(
    state: State<ProcessLogState>,
    process_id: String,
    count: Option<usize>,
) -> Vec<LogEntry> {
    let request = GetProcessLogsRequest { process_id, count };
    get_process_logs(&state.0.clone(), request)
}

async fn check_and_apply_update(app: AppHandle, always_prompt: bool) {
    let show_error = |app: &AppHandle, title: &str, message: String| {
        app.dialog()
            .message(message)
            .title(title)
            .kind(tauri_plugin_dialog::MessageDialogKind::Error)
            .show(|_| {});
    };
    let update_url = "https://github.com/OpenBB-finance/OpenBB/releases/download/ODP/latest.json";

    let ap_id = get_or_create_app_id();

    let headers = {
        let mut headers = reqwest::header::HeaderMap::new();

        match reqwest::header::HeaderValue::from_str("ODP-Updater") {
            Ok(user_agent) => {
                headers.insert(reqwest::header::USER_AGENT, user_agent);
            }
            Err(e) => {
                log::error!("Failed to create User-Agent header: {}", e);
                if always_prompt {
                    show_error(
                        &app,
                        "Update Check Failed",
                        format!("Failed to create User-Agent header: {}", e),
                    );
                }
                return;
            }
        }

        match reqwest::header::HeaderValue::from_str(&ap_id) {
            Ok(app_id) => {
                headers.insert(reqwest::header::HeaderName::from_static("x-app-id"), app_id);
            }
            Err(e) => {
                log::error!("Failed to create X-App-ID header: {}", e);
                if always_prompt {
                    show_error(
                        &app,
                        "Update Check Failed",
                        format!("Failed to create X-App-ID header: {}", e),
                    );
                }
                return;
            }
        }

        headers
    };

    let url = match update_url.parse() {
        Ok(url) => url,
        Err(e) => {
            let err_msg = format!("Failed to parse update URL: {}", e);
            log::error!("{}", err_msg);
            if always_prompt {
                show_error(&app, "Update Check Failed", err_msg);
            }
            return;
        }
    };

    let updater_res = app
        .updater_builder()
        .headers(headers)
        .endpoints(vec![url])
        .and_then(|builder| builder.build());

    match updater_res {
        Ok(updater) => {
            match updater.check().await {
                Ok(Some(update)) => {
                    let app_clone = app.clone();
                    app.dialog()
                    .message(format!(
                        "A new version ({}) is available. Would you like to install it now? The update will close the application and restart.",
                        update.version
                    ))
                    .title("Update Available")
                    .kind(tauri_plugin_dialog::MessageDialogKind::Info)
                    .buttons(tauri_plugin_dialog::MessageDialogButtons::YesNo)
                    .show(move |install| {
                        if install {
                            let app_clone_inner = app_clone.clone();
                            tauri::async_runtime::spawn(async move {
                                if let Some(window) = app_clone_inner.get_webview_window("main") {
                                    let _ = window.show();
                                    let _ = window.set_focus();
                                }

                                if let Err(e) = update.download_and_install(|_, _| {}, || {}).await
                                {
                                    log::error!("Failed to install update: {}", e);
                                    show_error(
                                        &app_clone_inner,
                                        "Update Failed",
                                        format!("Failed to install update: {}", e),
                                    );
                                } else {
                                    log::info!("Update installed successfully, restarting...");

                                    // SET THE FLAG TO SHOW WINDOW AFTER RESTART
                                    if let Ok(home_dir) = std::env::var("HOME").or_else(|_| std::env::var("USERPROFILE")) {
                                        let flag_path = std::path::Path::new(&home_dir).join(".openbb_platform").join(".show_on_restart");
                                        let _ = std::fs::write(flag_path, "1");
                                        log::info!("Set flag to show window on restart");
                                    }

                                    if let Some(window) = app_clone_inner.get_webview_window("main") {
                                        let _ = window.show();
                                    }

                                    app_clone_inner.request_restart();

                                    /* #[cfg(not(target_os = "macos"))]
                                    {
                                        use std::process::Command;

                                        if let Ok(exe_path) = std::env::current_exe() {
                                            log::debug!("Relaunching from: {}", exe_path.display());
                                            let _ = Command::new(exe_path).spawn();
                                            std::process::exit(0);
                                        } else {
                                            log::error!("Could not determine executable path for restart");
                                            app_clone_inner.restart();
                                        }
                                    }
                                    */
                                }
                            });
                        }
                    });
                }
                Ok(None) => {
                    log::debug!("No updates available");
                    if always_prompt {
                        app.dialog()
                            .message("You are already running the latest version.")
                            .title("No Updates Available")
                            .kind(tauri_plugin_dialog::MessageDialogKind::Info)
                            .show(|_| {});
                    }
                }
                Err(e) => {
                    let err_msg = format!("Failed to check for updates: {}", e);
                    log::error!("{}", err_msg);
                    if always_prompt {
                        show_error(&app, "Update Check Failed", err_msg);
                    }
                }
            }
        }
        Err(e) => {
            let err_msg = format!("Failed to build updater: {}", e);
            log::error!("{}", err_msg);
            if always_prompt {
                show_error(&app, "Update Check Failed", err_msg);
            }
        }
    }
}

async fn trigger_update_dialog(app: AppHandle) {
    check_and_apply_update(app, true).await;
}

async fn background_update_check(app: AppHandle) {
    check_and_apply_update(app, false).await;
}

fn check_installation_on_startup() -> InstallationState {
    log::debug!("STARTUP: Checking installation status");

    let home_dir = match std::env::var("HOME").or_else(|_| std::env::var("USERPROFILE")) {
        Ok(dir) => dir,
        Err(e) => {
            log::debug!("STARTUP: Failed to get home directory: {e}");
            return InstallationState {
                is_installed: false,
                installation_directory: None,
            };
        }
    };

    let platform_dir = Path::new(&home_dir).join(".openbb_platform");
    let system_settings_path = platform_dir.join("system_settings.json");

    log::debug!(
        "STARTUP: Looking for system settings at: {}",
        system_settings_path.display()
    );

    if !system_settings_path.exists() {
        log::debug!("STARTUP: System settings file not found");
        return InstallationState {
            is_installed: false,
            installation_directory: None,
        };
    }

    log::debug!("STARTUP: System settings file found");

    let settings_content = match std::fs::read_to_string(&system_settings_path) {
        Ok(content) => content,
        Err(e) => {
            log::debug!("STARTUP: Failed to read settings file: {e}");
            return InstallationState {
                is_installed: false,
                installation_directory: None,
            };
        }
    };

    let settings: serde_json::Value = match serde_json::from_str(&settings_content) {
        Ok(json) => json,
        Err(e) => {
            log::debug!("STARTUP: Failed to parse settings JSON: {e}");
            return InstallationState {
                is_installed: false,
                installation_directory: None,
            };
        }
    };

    let mut install_dir = None;

    if let Some(install_settings) = settings.get("install_settings")
        && let Some(dir) = install_settings.get("installation_directory")
        && let Some(dir_str) = dir.as_str()
    {
        log::debug!("STARTUP: Found installation directory in install_settings: {dir_str}");
        let conda_dir = Path::new(dir_str).join("conda");

        let conda_exe = if cfg!(target_os = "windows") {
            conda_dir.join("Scripts").join("conda.exe")
        } else {
            conda_dir.join("bin").join("conda")
        };

        if conda_exe.exists() {
            log::debug!("STARTUP: Conda executable found at {}", conda_exe.display());
            install_dir = Some(dir_str.to_string());
        } else {
            log::debug!(
                "STARTUP: Conda executable not found at {}",
                conda_exe.display()
            );
        }
    }

    if install_dir.is_none()
        && let Some(dir) = settings.get("installation_directory")
        && let Some(dir_str) = dir.as_str()
    {
        log::debug!("STARTUP: Found installation directory at root level: {dir_str}");
        let conda_dir = Path::new(dir_str).join("conda");

        let conda_exe = if cfg!(target_os = "windows") {
            conda_dir.join("Scripts").join("conda.exe")
        } else {
            conda_dir.join("bin").join("conda")
        };

        if conda_exe.exists() {
            log::debug!("STARTUP: Conda executable found at {}", conda_exe.display());
            install_dir = Some(dir_str.to_string());
        } else {
            log::debug!(
                "STARTUP: Conda executable not found at {}",
                conda_exe.display()
            );
        }
    }

    let is_installed = install_dir.is_some();
    log::debug!(
        "STARTUP: Installation status: {}",
        if is_installed { "VALID" } else { "INVALID" }
    );

    InstallationState {
        is_installed,
        installation_directory: install_dir,
    }
}

#[tauri::command]
fn get_installation_state(state: tauri::State<InstallationState>) -> InstallationState {
    state.inner().clone()
}

#[tauri::command]
fn navigate_to_page<R: Runtime>(app_handle: AppHandle<R>, page: &str) {
    if let Some(window) = app_handle.get_webview_window("main") {
        let _ = window.show();
        let _ = window.set_focus();

        let js = format!(
            r#"
            if (localStorage.getItem('environments-first-load-done') === 'true') {{
                window.location.href = '{page}';
            }} else {{
                console.log('Navigation prevented: environments-first-load-done not set');
            }}
            "#
        );
        let _ = window.eval(&js);
    }
}

#[tauri::command]
async fn quit_application(app_handle: AppHandle) {
    log::debug!("Quit application command received, running cleanup...");
    cleanup_all_processes(app_handle.clone()).await;
    app_handle.exit(0);
}

async fn cleanup_all_processes(app_handle: AppHandle) {
    use crate::tauri_handlers::helpers::{RealEnvSystem, RealFileExtTrait, RealFileSystem};
    log::debug!("Running complete application cleanup");

    let cleanup_timeout = std::time::Duration::from_secs(10);

    let cleanup_result = tokio::time::timeout(cleanup_timeout, async {
        match tokio::time::timeout(
            std::time::Duration::from_secs(3),
            tauri_handlers::jupyter::stop_all_jupyter_servers(app_handle.clone()),
        )
        .await
        {
            Ok(Ok(_)) => log::debug!("Successfully stopped all Jupyter servers"),
            Ok(Err(e)) => log::error!("Error stopping Jupyter servers: {e}"),
            Err(_) => log::warn!("Jupyter servers shutdown timed out"),
        }

        match tokio::time::timeout(
            std::time::Duration::from_secs(3),
            tauri_handlers::backends::stop_all_backend_services(
                app_handle,
                &RealFileSystem,
                &RealEnvSystem,
                &RealFileExtTrait,
            ),
        )
        .await
        {
            Ok(Ok(_)) => log::debug!("Successfully stopped all backend services"),
            Ok(Err(e)) => log::error!("Error stopping backend services: {e}"),
            Err(_) => log::warn!("Backend services shutdown timed out"),
        }
    })
    .await;

    match cleanup_result {
        Ok(_) => log::debug!("All cleanup completed successfully"),
        Err(_) => log::warn!("Cleanup process timed out after 10 seconds"),
    }

    #[cfg(target_os = "windows")]
    {
        log::debug!("Waiting for Windows to clean up UI resources...");
        tokio::time::sleep(std::time::Duration::from_millis(500)).await;
    }

    log::debug!("Cleanup complete");
}

fn main() {
    let _ = fix_path_env::fix();
    init_process_monitoring();

    tauri::Builder::default()
        .plugin(tauri_plugin_updater::Builder::new().build())
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_single_instance::init(|app, _, _| {
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.show();
                let _ = window.set_focus();
            }
        }))
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_persisted_scope::init())
        .plugin(tauri_plugin_log::Builder::new().clear_targets().target(tauri_plugin_log::Target::new(
            tauri_plugin_log::TargetKind::Stdout,
        )).target(tauri_plugin_log::Target::new(tauri_plugin_log::TargetKind::Stderr)).build())
        .plugin(tauri_plugin_dialog::init())
        .manage(ProcessLogState(get_log_storage()))
        .manage(RunningProcesses::new())
        .manage(check_installation_on_startup())
        .invoke_handler(tauri::generate_handler![
            toggle_theme,
            navigate_to_page,
            save_working_directory,
            get_working_directory,
            get_home_directory,
            select_directory,
            get_installation_directory,
            get_userdata_directory,
            get_settings_directory,
            select_file,
            install_to_directory,
            check_directory_exists,
            check_file_exists,
            install_conda,
            abort_installation,
            get_installation_status,
            get_installation_state,
            setup_python_environment,
            create_environment,
            list_conda_environments,
            get_environment_extensions,
            install_extensions,
            update_extension,
            update_environment,
            update_installation_error,
            remove_extension,
            remove_environment,
            create_environment_from_requirements,
            select_requirements_file,
            execute_in_environment,
            start_jupyter_server,
            stop_jupyter_server,
            stop_all_jupyter_servers,
            check_jupyter_server,
            list_jupyter_servers,
            get_user_credentials,
            open_credentials_file,
            update_user_credentials,
            open_url_in_window,
            register_process_monitoring,
            unregister_process_monitoring,
            get_process_logs_history,
            open_jupyter_logs_window,
            update_jupyter_status,
            open_backend_logs_window,
            start_backend_service,
            stop_backend_service,
            update_backend_service,
            create_backend_service,
            delete_backend_service,
            list_backend_services,
            uninstall_application,
            quit_application,
            generate_self_signed_cert,
            update_openbb_settings,
            create_default_backend_services
        ])
        .setup(|app_handle| {
            let install_state = check_installation_on_startup();

            let show_after_update = {
                if let Ok(home_dir) = std::env::var("HOME").or_else(|_| std::env::var("USERPROFILE")) {
                    let flag_path = std::path::Path::new(&home_dir).join(".openbb_platform").join(".show_on_restart");
                    if flag_path.exists() {
                        log::info!("Found update restart flag - will show window");
                        let _ = std::fs::remove_file(&flag_path);
                        true
                    } else {
                        false
                    }
                } else {
                    false
                }
            };

            if install_state.is_installed {
                let backend_handle = app_handle.handle().clone();
                tauri::async_runtime::spawn(async move {
                    use crate::tauri_handlers::helpers::{RealFileExtTrait, RealFileSystem, RealEnvSystem};
                    tokio::time::sleep(std::time::Duration::from_millis(100)).await;
                    log::debug!("Initializing backends after state setup delay");
                    if let Err(e) = initialize_backends(&backend_handle, RealFileSystem, RealEnvSystem, RealFileExtTrait).await {
                        log::error!("Failed to initialize backends: {e}");
                    }
                });
            }

            if let Some(window) = app_handle.get_webview_window("main") {
                window.set_menu(Menu::new(app_handle.handle())?)?;
            }

            let autostart_enabled = {
                #[cfg(target_os = "macos")]
                {
                    utils::autostart::macos_autostart::is_autostart_enabled(app_handle.handle()).unwrap_or(true)
                }
                #[cfg(target_os = "windows")]
                {
                    utils::autostart::windows_autostart::is_autostart_enabled(app_handle.handle()).unwrap_or(true)
                }
                #[cfg(target_os = "linux")]
                {
                    utils::autostart::linux_autostart::is_autostart_enabled(&app_handle.handle()).unwrap_or(true)
                }
            };
            log::debug!("Autostart is currently: {}", if autostart_enabled { "enabled" } else { "disabled" });

            let handle = app_handle.handle().clone();
            let open_item = MenuItemBuilder::new("Open Window").id("open").build(&handle)?;
            let open_workspace = MenuItemBuilder::new("Go to Workspace").id("open_workspace").build(&handle)?;
            let separator1 = tauri::menu::PredefinedMenuItem::separator(&handle)?;
            let open_environments_item = MenuItemBuilder::new("Environments").id("open_environments").build(&handle)?;
            let open_api_keys_item = MenuItemBuilder::new("API Keys").id("open_api_keys").build(&handle)?;
            let open_backends_item = MenuItemBuilder::new("Backends").id("open_backends").build(&handle)?;
            let separator2 = tauri::menu::PredefinedMenuItem::separator(&handle)?;
            let start_at_login_item = CheckMenuItemBuilder::new("Start at Login in Background")
                .id("start_at_login")
                .checked(autostart_enabled)
                .build(&handle)?;
            let separator3 = tauri::menu::PredefinedMenuItem::separator(&handle)?;
            let check_updates_item = MenuItemBuilder::new("Check for Updates").id("check_updates").build(&handle)?;
            let uninstall_item = MenuItemBuilder::new("Uninstall").id("uninstall").build(&handle)?;
            let quit_item = MenuItemBuilder::new("Quit").id("quit").build(&handle)?;

            let menu = Menu::with_items(&handle, &[
                &open_item,
                &open_workspace,
                &separator1,
                &open_backends_item,
                &open_environments_item,
                &open_api_keys_item,
                &separator2,
                &start_at_login_item,
                &separator3,
                &check_updates_item,
                &uninstall_item,
                &quit_item
            ])?;

            let icon = handle.default_window_icon().unwrap().clone();
            let tray_handle = handle.clone();
            let tray = TrayIconBuilder::new()
                .icon(icon)
                .tooltip("Open Data Platform - By OpenBB")
                .menu(&menu)
                .on_menu_event(move |_tray, event| {
                    let id_string = event.id().0.as_str();
                      match id_string {
                        "quit" => {
                            log::debug!("Received termination signal, running cleanup...");
                            let rt = tokio::runtime::Runtime::new().unwrap();
                            let cleanup_handle = tray_handle.clone();
                            rt.block_on(async {
                                cleanup_all_processes(cleanup_handle).await;
                            });
                            log::debug!("Exiting application");
                            tray_handle.exit(0);
                        }
                        "open" => {
                            if let Some(window) = tray_handle.get_webview_window("main") {
                                window.show().unwrap();
                                window.set_focus().unwrap();
                            }
                        }
                        "open_workspace" => open_workspace_in_browser(),
                        "open_environments" => navigate_to_page(tray_handle.clone(), "/environments"),
                        "open_api_keys" => navigate_to_page(tray_handle.clone(), "/api-keys"),
                        "open_backends" => navigate_to_page(tray_handle.clone(), "/backends"),
                        "check_updates" => {
                            let update_handle = tray_handle.clone();
                            tauri::async_runtime::spawn(async move {
                                trigger_update_dialog(update_handle).await;
                            });
                        }
                        "uninstall" => {
                            if let Some(window) = tray_handle.get_webview_window("main") {
                                window.show().unwrap();
                                window.set_focus().unwrap();
                                let install_state = check_installation_on_startup();
                                if !install_state.is_installed {
                                    tray_handle.dialog().message("The installation appears to be incomplete. To uninstall, quit the application and remove the application from the operating system.").kind(tauri_plugin_dialog::MessageDialogKind::Error).show(|_| {});
                                } else {
                                    window.eval("window.location.href = '/uninstall';").unwrap();
                                }
                            }
                        },
                        "start_at_login" => {
                            let app_handle = tray_handle.clone();
                            let is_enabled = {
                                #[cfg(target_os = "macos")]
                                {
                                    utils::autostart::macos_autostart::is_autostart_enabled(&app_handle).unwrap_or(false)
                                }
                                #[cfg(target_os = "windows")]
                                {
                                    utils::autostart::windows_autostart::is_autostart_enabled(&app_handle).unwrap_or(false)
                                }
                                #[cfg(target_os = "linux")]
                                {
                                    utils::autostart::linux_autostart::is_autostart_enabled(&app_handle).unwrap_or(false)
                                }
                            };
                            log::debug!("Current autostart status: {}", if is_enabled { "enabled" } else { "disabled" });
                            let target_state = !is_enabled;
                            log::debug!("Attempting to {} autostart", if target_state { "enable" } else { "disable" });
                            let result = {
                                #[cfg(target_os = "macos")]
                                {
                                    if target_state {
                                        utils::autostart::macos_autostart::enable_autostart(&app_handle)
                                    } else {
                                        utils::autostart::macos_autostart::disable_autostart(&app_handle)
                                    }
                                }
                                #[cfg(target_os = "windows")]
                                {
                                    if target_state {
                                        utils::autostart::windows_autostart::enable_autostart(&app_handle)
                                    } else {
                                        utils::autostart::windows_autostart::disable_autostart(&app_handle)
                                    }
                                }
                                #[cfg(target_os = "linux")]
                                {
                                    if target_state {
                                        utils::autostart::linux_autostart::enable_autostart(&app_handle)
                                    } else {
                                        utils::autostart::linux_autostart::disable_autostart(&app_handle)
                                    }
                                }
                            };
                            if let Err(e) = result {
                                log::error!("Failed to {} autostart: {}", if target_state { "enable" } else { "disable" }, e);
                                return;
                            }
                            if let Err(e) = start_at_login_item.set_checked(target_state) {
                                log::error!("Failed to update menu item state: {e}");
                            } else {
                                log::debug!("Menu item state updated to: {target_state}");
                            }
                            log::debug!("Successfully {} autostart", if target_state { "enabled" } else { "disabled" });
                        }
                        _ => {}
                    }
                })
                .build(&handle)
                .unwrap();

            app_handle.manage(tray);

            if let Some(window) = app_handle.get_webview_window("main") {
                let window_clone = window.clone();
                window.on_window_event(move |event| {
                    if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                        window_clone.hide().unwrap();
                        api.prevent_close();
                    }
                });
                #[cfg(target_os = "macos")]
                {
                    use objc2_app_kit::{NSColor, NSWindow};
                    let ns_window_ptr = window.ns_window().unwrap();
                    let ns_window = unsafe { &*(ns_window_ptr as *mut NSWindow) };
                    let bg_color = NSColor::colorWithRed_green_blue_alpha(0.0, 0.0, 0.0, 1.0);
                    ns_window.setBackgroundColor(Some(&bg_color));
                };
            }

            let exit_handle = app_handle.handle().clone();
            ctrlc::set_handler(move || {
                println!("Received termination signal, running cleanup...");
                let rt = tokio::runtime::Runtime::new().unwrap();
                let cleanup_handle = exit_handle.clone();
                rt.block_on(async {
                    cleanup_all_processes(cleanup_handle).await;
                });
                exit_handle.exit(0);
            }).unwrap_or_else(|e| log::error!("Error setting Ctrl-C handler: {e}"));

            #[cfg(target_os = "macos")]
            {
                let termination_handle = app_handle.handle().clone();
                utils::app_termination::setup_termination_handler(termination_handle);
            }

            if !install_state.is_installed {
                log::info!("Installation is INVALID - showing window and navigating to setup");
                if let Some(window) = handle.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                    let _ = window.eval("localStorage.clear(); console.log('localStorage cleared due to INVALID installation');");
                    let _ = window.eval("window.location.href = '/setup'");
                }
            } else {
                // VALID INSTALLATION
                log::info!("Installation is VALID");

                let update_handle = handle.clone();
                tauri::async_runtime::spawn(async move {
                    log::debug!("Starting background update check...");
                    tokio::time::sleep(std::time::Duration::from_secs(3)).await;
                    background_update_check(update_handle).await;
                });

                if let Some(window) = handle.get_webview_window("main") {
                    let _ = window.eval("localStorage.setItem('environments-first-load-done', 'true');");

                    if show_after_update {
                        log::info!("SHOWING WINDOW AFTER UPDATE RESTART");
                        let _ = window.show();
                    }

                    let _ = window.set_focus();
                }
            }
            Ok(())
        })
        .build(tauri::generate_context!())
        .unwrap_or_else(|e| {
            log::error!("Error while building Tauri application: {e}");
            std::process::exit(1);
        })
        .run(|app_handle, event| {
            let is_restart_requested = Arc::new(AtomicBool::new(false));
            let is_restart_requested_clone = is_restart_requested.clone();

            if let tauri::RunEvent::ExitRequested { code, ..} = event
                && code.unwrap() == RESTART_EXIT_CODE {
                    is_restart_requested.store(true, Ordering::SeqCst);
                }

            if let tauri::RunEvent::ExitRequested { ref api, .. } = event {
                log::debug!("Caught applicationWillTerminate event, running cleanup...");
                api.prevent_exit();
                let rt = tokio::runtime::Runtime::new().unwrap();
                let cleanup_handle = app_handle.clone();
                rt.block_on(async {
                    cleanup_all_processes(cleanup_handle).await;
                });
                if is_restart_requested_clone.load(Ordering::SeqCst) {
                    log::debug!("Restart requested, exiting with restart code");
                    tauri::process::restart(&app_handle.env());
                } else {
                    log::debug!("Exiting application normally");
                    std::process::exit(0);
                }
            }

            #[cfg(target_os = "macos")]
            {
            if let tauri::RunEvent::Reopen { .. } = event
                && let Some(window) = app_handle.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }

            if let tauri::RunEvent::Exit = event
                && is_restart_requested_clone.load(Ordering::SeqCst) {
                    app_handle.cleanup_before_exit();
                    let env = app_handle.env();
                    tauri::process::restart(&env);
                }
        });
}
