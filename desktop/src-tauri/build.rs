use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

fn main() {
    if let Err(err) = stage_openssl() {
        panic!("[build.rs] failed to stage OpenSSL runtime libraries: {err}");
    }
    if let Err(err) = stage_sbom_placeholders() {
        panic!("[build.rs] failed to stage SBOM placeholders: {err}");
    }
    tauri_build::build()
}

fn stage_sbom_placeholders() -> Result<(), String> {
    let manifest_dir = PathBuf::from(env::var("CARGO_MANIFEST_DIR").map_err(|e| e.to_string())?);
    for name in [
        "open-data-platform-SBOM-cargo.cdx.xml",
        "open-data-platform-SBOM-npm.cdx.xml",
    ] {
        let path = manifest_dir.join(name);
        if path.exists() {
            continue;
        }
        let stub = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<bom xmlns=\"http://cyclonedx.org/schema/bom/1.6\" version=\"1\"><components/></bom>\n";
        fs::write(&path, stub).map_err(|e| format!("write {}: {e}", path.display()))?;
        println!(
            "cargo:warning=wrote SBOM placeholder at {}; CI regenerates real SBOMs before bundling",
            path.display()
        );
    }
    Ok(())
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

    rewrite_macos_install_names(&frameworks, &names, &prefix)?;
    Ok(())
}

fn rewrite_macos_install_names(
    frameworks: &Path,
    names: &[&str],
    brew_prefix: &Path,
) -> Result<(), String> {
    for name in names {
        let dest = frameworks.join(name);
        let new_id = format!("@executable_path/../Frameworks/{name}");
        run_install_name_tool(&["-id", &new_id, dest.to_str().unwrap()])?;

        let output = Command::new("otool")
            .args(["-L", dest.to_str().unwrap()])
            .output()
            .map_err(|e| format!("otool -L {}: {e}", dest.display()))?;
        if !output.status.success() {
            return Err(format!(
                "otool -L {} failed: {}",
                dest.display(),
                String::from_utf8_lossy(&output.stderr)
            ));
        }
        let listing = String::from_utf8_lossy(&output.stdout).into_owned();
        for dep in names {
            if dep == name {
                continue;
            }
            for line in listing.lines() {
                let trimmed = line.trim();
                let path = trimmed.split_whitespace().next().unwrap_or("");
                if path.is_empty() || path == dest.to_str().unwrap() {
                    continue;
                }
                if path.ends_with(&format!("/{dep}"))
                    && (path.starts_with(brew_prefix.to_str().unwrap_or(""))
                        || path.starts_with("/usr/local/")
                        || path.starts_with("/opt/homebrew/")
                        || path.starts_with("@loader_path")
                        || path.starts_with("@rpath"))
                {
                    let new_dep = format!("@executable_path/../Frameworks/{dep}");
                    run_install_name_tool(&["-change", path, &new_dep, dest.to_str().unwrap()])?;
                }
            }
        }

        let _ = Command::new("codesign")
            .args(["--force", "--sign", "-", dest.to_str().unwrap()])
            .status();
    }
    Ok(())
}

fn run_install_name_tool(args: &[&str]) -> Result<(), String> {
    let output = Command::new("install_name_tool")
        .args(args)
        .output()
        .map_err(|e| format!("install_name_tool {:?}: {e}", args))?;
    if !output.status.success() {
        return Err(format!(
            "install_name_tool {:?} failed: {}",
            args,
            String::from_utf8_lossy(&output.stderr)
        ));
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
        return Err(
            "VCPKG_ROOT is not set; install OpenSSL via vcpkg (openssl:x64-windows or openssl:arm64-windows) before building"
                .into(),
        );
    };

    let target_arch = env::var("CARGO_CFG_TARGET_ARCH").unwrap_or_default();
    let triplets: &[&str] = match target_arch.as_str() {
        "aarch64" => &["arm64-windows", "x64-windows"],
        _ => &["x64-windows", "arm64-windows"],
    };

    let bin_dir = triplets
        .iter()
        .map(|t| PathBuf::from(&vcpkg_root).join(format!("installed/{t}/bin")))
        .find(|p| p.exists())
        .ok_or_else(|| {
            format!(
                "no vcpkg dynamic OpenSSL install found under {}/installed/{{x64,arm64}}-windows/bin; run `vcpkg install openssl:x64-windows` (or openssl:arm64-windows)",
                vcpkg_root
            )
        })?;

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
