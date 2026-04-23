use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

fn main() {
    if let Err(err) = stage_openssl() {
        panic!("[build.rs] failed to stage OpenSSL runtime libraries: {err}");
    }
    tauri_build::build()
}

fn stage_openssl() -> Result<(), String> {
    println!("cargo:rerun-if-env-changed=OPENSSL_COPY_SKIP_EXISTING");
    println!("cargo:rerun-if-env-changed=VCPKG_ROOT");

    let manifest_dir = PathBuf::from(env::var("CARGO_MANIFEST_DIR").map_err(|e| e.to_string())?);
    let target_os = env::var("CARGO_CFG_TARGET_OS").unwrap_or_default();
    let skip_existing = env::var("OPENSSL_COPY_SKIP_EXISTING").ok().as_deref() == Some("1");

    match target_os.as_str() {
        "macos" => stage_macos(&manifest_dir, skip_existing),
        "windows" => stage_windows(&manifest_dir, skip_existing),
        _ => Ok(()),
    }
}

fn copy_if_needed(src: &Path, dest: &Path, skip_existing: bool) -> Result<(), String> {
    if skip_existing && dest.exists() {
        println!(
            "cargo:warning=OPENSSL_COPY_SKIP_EXISTING=1; keeping existing {}",
            dest.display()
        );
        return Ok(());
    }
    if let Some(parent) = dest.parent() {
        fs::create_dir_all(parent).map_err(|e| format!("mkdir {}: {e}", parent.display()))?;
    }
    fs::copy(src, dest)
        .map_err(|e| format!("copy {} -> {}: {e}", src.display(), dest.display()))?;
    println!("cargo:rerun-if-changed={}", src.display());
    Ok(())
}

fn stage_macos(manifest_dir: &Path, skip_existing: bool) -> Result<(), String> {
    let names = ["libcrypto.3.dylib", "libssl.3.dylib"];
    let frameworks = manifest_dir.join("frameworks");

    if names.iter().all(|n| frameworks.join(n).exists()) {
        if skip_existing {
            println!("cargo:warning=OPENSSL_COPY_SKIP_EXISTING=1; OpenSSL dylibs already staged");
        }
        return Ok(());
    }

    let prefix = match brew_openssl_prefix() {
        Ok(p) => p,
        Err(err) => {
            println!(
                "cargo:warning={err}; skipping OpenSSL dylib staging (required only for bundling)"
            );
            return Ok(());
        }
    };
    for name in names {
        let src = prefix.join("lib").join(name);
        if !src.exists() {
            println!(
                "cargo:warning=expected {} to exist; skipping (required only for bundling)",
                src.display()
            );
            return Ok(());
        }
        let dest = frameworks.join(name);
        copy_if_needed(&src, &dest, skip_existing)?;
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            let mut perms = fs::metadata(&dest)
                .map_err(|e| format!("stat {}: {e}", dest.display()))?
                .permissions();
            perms.set_mode(perms.mode() | 0o200);
            let _ = fs::set_permissions(&dest, perms);
        }
    }
    Ok(())
}

fn brew_openssl_prefix() -> Result<PathBuf, String> {
    if let Ok(output) = Command::new("brew")
        .args(["--prefix", "openssl@3"])
        .output()
        && output.status.success()
    {
        let path = String::from_utf8_lossy(&output.stdout).trim().to_string();
        if !path.is_empty() {
            return Ok(PathBuf::from(path));
        }
    }
    for fallback in ["/opt/homebrew/opt/openssl@3", "/usr/local/opt/openssl@3"] {
        let p = PathBuf::from(fallback);
        if p.exists() {
            return Ok(p);
        }
    }
    Err("could not resolve Homebrew openssl@3 prefix".into())
}

fn stage_windows(manifest_dir: &Path, skip_existing: bool) -> Result<(), String> {
    let dest_names = ["libcrypto-3-x64.dll", "libssl-3-x64.dll"];

    if dest_names.iter().all(|n| manifest_dir.join(n).exists()) {
        if skip_existing {
            println!("cargo:warning=OPENSSL_COPY_SKIP_EXISTING=1; OpenSSL DLLs already staged");
        }
        return Ok(());
    }

    let Ok(vcpkg_root) = env::var("VCPKG_ROOT") else {
        println!(
            "cargo:warning=VCPKG_ROOT not set; skipping OpenSSL DLL staging (required only for bundling)"
        );
        return Ok(());
    };
    let bin_dir = PathBuf::from(&vcpkg_root).join("installed/x64-windows/bin");
    if !bin_dir.exists() {
        println!(
            "cargo:warning=vcpkg dynamic OpenSSL bin dir not found at {}; skipping DLL staging (required only for bundling)",
            bin_dir.display()
        );
        return Ok(());
    }
    for (pattern_prefix, dest_name) in [
        ("libcrypto-3-", "libcrypto-3-x64.dll"),
        ("libssl-3-", "libssl-3-x64.dll"),
    ] {
        let src = fs::read_dir(&bin_dir)
            .map_err(|e| format!("read_dir {}: {e}", bin_dir.display()))?
            .filter_map(|e| e.ok())
            .map(|e| e.path())
            .find(|p| {
                p.file_name()
                    .and_then(|n| n.to_str())
                    .map(|n| n.starts_with(pattern_prefix) && n.ends_with(".dll"))
                    .unwrap_or(false)
            })
            .ok_or_else(|| {
                format!(
                    "no DLL matching '{}*.dll' in {}",
                    pattern_prefix,
                    bin_dir.display()
                )
            })?;
        let dest = manifest_dir.join(dest_name);
        copy_if_needed(&src, &dest, skip_existing)?;
    }
    Ok(())
}
