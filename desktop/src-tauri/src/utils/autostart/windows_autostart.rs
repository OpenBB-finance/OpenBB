use std::fs;
use std::path::{Path, PathBuf};
use tauri::AppHandle;

pub fn is_autostart_enabled(app_handle: &AppHandle) -> Result<bool, String> {
    let startup_dir = get_windows_startup_dir()
        .map_err(|e| format!("Failed to get Windows startup directory: {e}"))?;

    let shortcut_path = get_shortcut_path(app_handle, &startup_dir)
        .map_err(|e| format!("Failed to determine shortcut path: {e}"))?;

    Ok(shortcut_path.exists())
}

pub fn enable_autostart(app_handle: &AppHandle) -> Result<(), String> {
    let startup_dir = get_windows_startup_dir()
        .map_err(|e| format!("Failed to get Windows startup directory: {e}"))?;

    if !startup_dir.exists() {
        fs::create_dir_all(&startup_dir)
            .map_err(|e| format!("Failed to create Startup directory: {e}"))?;
    }

    let shortcut_path = get_shortcut_path(app_handle, &startup_dir)
        .map_err(|e| format!("Failed to determine shortcut path: {e}"))?;

    // Get the path to the executable
    let executable_path =
        std::env::current_exe().map_err(|e| format!("Failed to get executable path: {e}"))?;

    if !executable_path.exists() {
        return Err(format!("Executable not found at {executable_path:?}"));
    }

    use std::ptr;
    use winapi::Interface;
    use winapi::shared::guiddef::GUID;
    use winapi::shared::winerror::SUCCEEDED;
    use winapi::shared::wtypesbase::CLSCTX_INPROC_SERVER;
    use winapi::um::combaseapi::{CoCreateInstance, CoInitializeEx, CoUninitialize};
    use winapi::um::objbase::COINIT_APARTMENTTHREADED;
    use winapi::um::objidl::IPersistFile;
    use winapi::um::shobjidl_core::IShellLinkW;
    use winapi::um::winuser::SW_SHOW;

    // Define CLSID_ShellLink manually if not available in winapi
    const CLSID_SHELL_LINK: GUID = GUID {
        Data1: 0x00021401,
        Data2: 0x0000,
        Data3: 0x0000,
        Data4: [0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x46],
    };

    // Precompute wide strings outside unsafe to avoid early returns inside COM section
    let wide_exe_path: Vec<u16> = executable_path
        .to_str()
        .ok_or("Failed to convert path to string")?
        .encode_utf16()
        .chain(std::iter::once(0))
        .collect();

    let wide_shortcut_path: Vec<u16> = shortcut_path
        .to_str()
        .ok_or("Failed to convert shortcut path to string")?
        .encode_utf16()
        .chain(std::iter::once(0))
        .collect();

    unsafe {
        // Initialize COM
        let hr_init = CoInitializeEx(ptr::null_mut(), COINIT_APARTMENTTHREADED);
        if !SUCCEEDED(hr_init) {
            return Err(format!("Failed to initialize COM: {hr_init:#x}"));
        }

        // Create shell link object
        let mut shell_link: *mut IShellLinkW = ptr::null_mut();
        let hr = CoCreateInstance(
            &CLSID_SHELL_LINK,
            ptr::null_mut(),
            CLSCTX_INPROC_SERVER,
            &IShellLinkW::uuidof(),
            &mut shell_link as *mut _ as *mut _,
        );

        if !SUCCEEDED(hr) || shell_link.is_null() {
            CoUninitialize();
            return Err(format!("Failed to create shell link: {hr:#x}"));
        }

        let hr_set_path = (*shell_link).SetPath(wide_exe_path.as_ptr());
        if !SUCCEEDED(hr_set_path) {
            (*shell_link).Release();
            CoUninitialize();
            return Err(format!("Failed to set shortcut path: {hr_set_path:#x}"));
        }

        let hr_set_show = (*shell_link).SetShowCmd(SW_SHOW);
        if !SUCCEEDED(hr_set_show) {
            (*shell_link).Release();
            CoUninitialize();
            return Err(format!("Failed to set show command: {hr_set_show:#x}"));
        }

        let mut persist_file: *mut IPersistFile = ptr::null_mut();
        let hr_query = (*shell_link).QueryInterface(
            &IPersistFile::uuidof(),
            &mut persist_file as *mut _ as *mut _,
        );

        if !SUCCEEDED(hr_query) || persist_file.is_null() {
            (*shell_link).Release();
            CoUninitialize();
            return Err(format!(
                "Failed to get IPersistFile interface: {hr_query:#x}"
            ));
        }

        let hr_save = (*persist_file).Save(wide_shortcut_path.as_ptr(), 1);
        if !SUCCEEDED(hr_save) {
            (*persist_file).Release();
            (*shell_link).Release();
            CoUninitialize();
            return Err(format!("Failed to save shortcut: {hr_save:#x}"));
        }

        (*persist_file).Release();
        (*shell_link).Release();
        CoUninitialize();
    }

    Ok(())
}

pub fn disable_autostart(app_handle: &AppHandle) -> Result<(), String> {
    let startup_dir = get_windows_startup_dir()
        .map_err(|e| format!("Failed to get Windows startup directory: {e}"))?;

    let shortcut_path = get_shortcut_path(app_handle, &startup_dir)
        .map_err(|e| format!("Failed to determine shortcut path: {e}"))?;

    if shortcut_path.exists() {
        fs::remove_file(&shortcut_path)
            .map_err(|e| format!("Failed to remove shortcut file: {e}"))?;
    }

    Ok(())
}

fn get_windows_startup_dir() -> Result<PathBuf, String> {
    let appdata = std::env::var("APPDATA")
        .map_err(|_| "Failed to get APPDATA environment variable".to_string())?;

    Ok(Path::new(&appdata)
        .join("Microsoft")
        .join("Windows")
        .join("Start Menu")
        .join("Programs")
        .join("Startup"))
}

fn get_shortcut_path(app_handle: &AppHandle, startup_dir: &Path) -> Result<PathBuf, String> {
    let app_name = app_handle.package_info().name.clone();
    Ok(startup_dir.join(format!("{app_name}.lnk")))
}
