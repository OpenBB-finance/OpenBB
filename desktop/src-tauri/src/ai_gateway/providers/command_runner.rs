use crate::ai_gateway::errors::{GatewayResult, process_crashed, provider_not_installed};
use std::fs;
use std::path::{Path, PathBuf};
use tokio::process::Command;

pub struct RealCommandRunner;

impl RealCommandRunner {
    pub fn command(program: &str) -> GatewayResult<Command> {
        let resolved = resolve_program(program)?;
        Ok(build_command(program, resolved))
    }

    pub async fn output(program: &str, args: &[&str]) -> GatewayResult<std::process::Output> {
        let mut command = Self::command(program)?;
        command.args(args);
        command
            .output()
            .await
            .map_err(|error| process_crashed(program, error.to_string()))
    }
}

fn build_command(program: &str, resolved: PathBuf) -> Command {
    #[cfg(windows)]
    {
        if resolved
            .extension()
            .and_then(|value| value.to_str())
            .map(|value| matches!(value.to_ascii_lowercase().as_str(), "cmd" | "bat"))
            .unwrap_or(false)
        {
            if let Some((node_program, script_path)) = resolve_node_wrapper_script(&resolved) {
                let mut command = Command::new(node_program);
                command.arg(script_path);
                return command;
            }
            let mut command = Command::new("cmd.exe");
            command.arg("/d").arg("/s").arg("/c").arg(resolved);
            return command;
        }
    }

    let _ = program;
    Command::new(resolved)
}

#[cfg(windows)]
fn resolve_node_wrapper_script(wrapper: &Path) -> Option<(PathBuf, PathBuf)> {
    let contents = fs::read_to_string(wrapper).ok()?;
    let marker = "\"%dp0%\\";
    let line = contents
        .lines()
        .find(|line| line.contains(marker) && line.contains(".js"))?;
    let start = line.find(marker)? + marker.len();
    let suffix = &line[start..];
    let end = suffix.find(".js\"")?;
    let relative_script = &suffix[..end + 3];
    let base_dir = wrapper.parent()?;
    let script_path = base_dir.join(relative_script.replace('\\', std::path::MAIN_SEPARATOR_STR));
    if !script_path.exists() {
        return None;
    }
    let node_program = {
        let bundled = base_dir.join("node.exe");
        if bundled.exists() {
            bundled
        } else {
            PathBuf::from("node")
        }
    };
    Some((node_program, script_path))
}

fn resolve_program(program: &str) -> GatewayResult<PathBuf> {
    #[cfg(windows)]
    {
        if let Ok(candidate) = which::which(format!("{program}.cmd")) {
            return Ok(candidate);
        }
    }

    let resolved = which::which(program).map_err(|_| provider_not_installed(program))?;
    #[cfg(windows)]
    {
        if resolved
            .extension()
            .and_then(|value| value.to_str())
            .map(|value| value.eq_ignore_ascii_case("ps1"))
            .unwrap_or(false)
        {
            let cmd_candidate = resolved.with_extension("cmd");
            if cmd_candidate.exists() {
                return Ok(cmd_candidate);
            }
            let bare_candidate = resolved.with_extension("");
            if bare_candidate.exists() && is_executable_like(&bare_candidate) {
                return Ok(bare_candidate);
            }
        }
    }
    Ok(resolved)
}

#[cfg(windows)]
fn is_executable_like(path: &Path) -> bool {
    matches!(
        path.extension().and_then(|value| value.to_str()).map(|value| value.to_ascii_lowercase()),
        Some(ext) if ext == "exe" || ext == "cmd" || ext == "bat"
    ) || path.extension().is_none()
}
