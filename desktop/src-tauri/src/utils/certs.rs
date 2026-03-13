use openssl::asn1::Asn1Time;
use openssl::bn::{BigNum, MsbOption};
use openssl::error::ErrorStack;
use openssl::hash::MessageDigest;
use openssl::nid::Nid;
use openssl::pkcs12::Pkcs12;
use openssl::pkey::{PKey, Private};
use openssl::rsa::Rsa;
use openssl::x509::extension::{BasicConstraints, KeyUsage, SubjectAlternativeName};
use openssl::x509::{X509, X509Name};
use serde_json::json;
use std::path::Path;
use std::process::Output;
use std::sync::Arc;

// --- Traits for Mocking ---

#[cfg_attr(test, mockall::automock)]
pub trait FileSystem: Send + Sync {
    fn create_dir_all(&self, path: &Path) -> Result<(), String>;
    fn write(&self, path: &Path, contents: &[u8]) -> Result<(), String>;
    fn exists(&self, path: &Path) -> bool;
}

pub struct RealFileSystem;
impl FileSystem for RealFileSystem {
    fn create_dir_all(&self, path: &Path) -> Result<(), String> {
        std::fs::create_dir_all(path).map_err(|e| e.to_string())
    }

    fn write(&self, path: &Path, contents: &[u8]) -> Result<(), String> {
        std::fs::write(path, contents).map_err(|e| e.to_string())
    }

    fn exists(&self, path: &Path) -> bool {
        path.exists()
    }
}

#[cfg_attr(test, mockall::automock)]
pub trait CommandExecutor: Send + Sync {
    fn execute<'a>(&self, command: &'a str, args: &'a [&'a str]) -> Result<Output, String>;
}

pub struct RealCommandExecutor;
impl CommandExecutor for RealCommandExecutor {
    fn execute<'a>(&self, command: &'a str, args: &'a [&'a str]) -> Result<Output, String> {
        std::process::Command::new(command)
            .args(args)
            .output()
            .map_err(|e| e.to_string())
    }
}

#[cfg_attr(test, mockall::automock)]
pub trait TrustStore: Send + Sync {
    fn install(
        &self,
        cert_path: &Path,
        executor: &dyn CommandExecutor,
        fs: &dyn FileSystem,
    ) -> Result<(), String>;
}

pub struct SystemTrustStore;
impl TrustStore for SystemTrustStore {
    fn install(
        &self,
        cert_path: &Path,
        executor: &dyn CommandExecutor,
        fs: &dyn FileSystem,
    ) -> Result<(), String> {
        install_cert_in_trust_store(cert_path, executor, fs)
    }
}

// --- Certificate Service ---

pub struct CertService {
    fs: Arc<dyn FileSystem>,
    trust_store: Arc<dyn TrustStore>,
    executor: Arc<dyn CommandExecutor>,
}

impl CertService {
    pub fn new(
        fs: Arc<dyn FileSystem>,
        trust_store: Arc<dyn TrustStore>,
        executor: Arc<dyn CommandExecutor>,
    ) -> Self {
        Self {
            fs,
            trust_store,
            executor,
        }
    }

    #[allow(clippy::too_many_arguments)]
    pub fn generate_and_save_cert(
        &self,
        common_name: String,
        org_name: String,
        alt_names: Vec<String>,
        output_dir: String,
        days_valid: u32,
        password: Option<String>,
        install_in_trust_store: bool,
    ) -> Result<serde_json::Value, String> {
        self.fs
            .create_dir_all(Path::new(&output_dir))
            .map_err(|e| format!("Failed to create output directory: {e}"))?;

        let rsa = Rsa::generate(2048).map_err(|e| format!("Failed to generate RSA key: {e}"))?;
        let pkey = PKey::from_rsa(rsa).map_err(|e| format!("Failed to create private key: {e}"))?;

        let cert = generate_cert(&pkey, &common_name, &org_name, &alt_names, days_valid)
            .map_err(|e| format!("Failed to generate certificate: {e}"))?;

        let key_path = Path::new(&output_dir).join("private.key");
        let key_pem = pkey
            .private_key_to_pem_pkcs8()
            .map_err(|e| format!("Failed to convert private key to PEM: {e}"))?;
        self.fs
            .write(&key_path, &key_pem)
            .map_err(|e| format!("Failed to write private key: {e}"))?;

        let cert_path = Path::new(&output_dir).join("certificate.pem");
        let cert_pem = cert
            .to_pem()
            .map_err(|e| format!("Failed to convert certificate to PEM: {e}"))?;
        self.fs
            .write(&cert_path, &cert_pem)
            .map_err(|e| format!("Failed to write certificate: {e}"))?;

        let pkcs12 = Pkcs12::builder()
            .name(&common_name)
            .pkey(&pkey)
            .cert(&cert)
            .build2(password.as_deref().unwrap_or(""))
            .map_err(|e| format!("Failed to create PKCS#12 bundle: {e}"))?;
        let pkcs12_der = pkcs12
            .to_der()
            .map_err(|e| format!("Failed to convert PKCS#12 to DER: {e}"))?;
        let p12_path = Path::new(&output_dir).join("certificate.p12");
        self.fs
            .write(&p12_path, &pkcs12_der)
            .map_err(|e| format!("Failed to write PKCS#12 file: {e}"))?;

        if install_in_trust_store {
            self.trust_store
                .install(&cert_path, &*self.executor, &*self.fs)?;
        }

        Ok(json!({
            "key_path": key_path.to_string_lossy(),
            "cert_path": cert_path.to_string_lossy(),
            "pkcs12_path": p12_path.to_string_lossy(),
            "expires": days_valid
        }))
    }
}

// --- Tauri Command ---

#[tauri::command]
pub async fn generate_self_signed_cert(
    common_name: String,
    org_name: String,
    alt_names: Vec<String>,
    output_dir: String,
    days_valid: u32,
    password: Option<String>,
    install_in_trust_store: bool,
) -> Result<serde_json::Value, String> {
    let cert_service = CertService::new(
        Arc::new(RealFileSystem),
        Arc::new(SystemTrustStore),
        Arc::new(RealCommandExecutor),
    );
    cert_service.generate_and_save_cert(
        common_name,
        org_name,
        alt_names,
        output_dir,
        days_valid,
        password,
        install_in_trust_store,
    )
}

// --- Helper Functions ---

fn generate_cert(
    pkey: &PKey<Private>,
    common_name: &str,
    org_name: &str,
    alt_names: &[String],
    days_valid: u32,
) -> Result<X509, ErrorStack> {
    let mut x509_name = X509Name::builder()?;
    x509_name.append_entry_by_nid(Nid::COMMONNAME, common_name)?;
    x509_name.append_entry_by_nid(Nid::ORGANIZATIONNAME, org_name)?;
    let x509_name = x509_name.build();

    let mut cert_builder = X509::builder()?;
    cert_builder.set_version(2)?;

    let serial_number = {
        let mut serial = BigNum::new()?;
        serial.rand(159, MsbOption::MAYBE_ZERO, false)?;
        serial.to_asn1_integer()?
    };
    cert_builder.set_serial_number(&serial_number)?;

    cert_builder.set_issuer_name(&x509_name)?;
    cert_builder.set_subject_name(&x509_name)?;

    let not_before = Asn1Time::days_from_now(0)?;
    let not_after = Asn1Time::days_from_now(days_valid)?;
    cert_builder.set_not_before(&not_before)?;
    cert_builder.set_not_after(&not_after)?;

    cert_builder.set_pubkey(pkey)?;

    let basic_constraints = BasicConstraints::new().critical().ca().build()?;
    cert_builder.append_extension(basic_constraints)?;

    let key_usage = KeyUsage::new()
        .digital_signature()
        .key_encipherment()
        .build()?;
    cert_builder.append_extension(key_usage)?;

    if !alt_names.is_empty() {
        let mut san_builder = SubjectAlternativeName::new();
        for name in alt_names {
            if name.parse::<std::net::IpAddr>().is_ok() {
                san_builder.ip(name);
            } else {
                san_builder.dns(name);
            }
        }
        let san = san_builder.build(&cert_builder.x509v3_context(None, None))?;
        cert_builder.append_extension(san)?;
    }

    cert_builder.sign(pkey, MessageDigest::sha256())?;
    Ok(cert_builder.build())
}

#[cfg(target_os = "windows")]
fn install_cert_in_trust_store(
    cert_path: &Path,
    executor: &dyn CommandExecutor,
    _fs: &dyn FileSystem,
) -> Result<(), String> {
    let cert_path_str = cert_path.to_str().ok_or("Invalid certificate path")?;

    // Install to the Current User's Root certificate store. This does not require elevation.
    let output = executor.execute("certutil", &["-user", "-addstore", "Root", cert_path_str])?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!(
            "Failed to add certificate to user's trust store. Stderr: {stderr}",
        ));
    }

    Ok(())
}

#[cfg(target_os = "macos")]
fn install_cert_in_trust_store(
    cert_path: &Path,
    executor: &dyn CommandExecutor,
    _fs: &dyn FileSystem,
) -> Result<(), String> {
    let cert_path_str = cert_path.to_str().ok_or("Invalid certificate path")?;

    // Install to Login Keychain
    if let Some(home_dir) = dirs::home_dir() {
        let login_keychain_path = home_dir
            .join("Library/Keychains/login.keychain-db")
            .to_string_lossy()
            .to_string();
        let output_login = executor.execute(
            "security",
            &[
                "add-trusted-cert",
                "-d",
                "-r",
                "trustRoot",
                "-k",
                &login_keychain_path,
                cert_path_str,
            ],
        )?;
        if !output_login.status.success() {
            let stderr = String::from_utf8_lossy(&output_login.stderr);
            return Err(format!(
                "Failed to add certificate to login keychain. Stderr: {stderr}"
            ));
        }
    } else {
        return Err("Could not find user home directory to locate login keychain.".to_string());
    }

    Ok(())
}

#[cfg(target_os = "linux")]
fn install_cert_in_trust_store(
    cert_path: &Path,
    executor: &dyn CommandExecutor,
    fs: &dyn FileSystem,
) -> Result<(), String> {
    // Install certificate to the user's NSS database for browser support (Firefox, Chrome).
    // This is the most common method for user-level trust on Linux.
    if let Ok(certutil_path) = which::which("certutil") {
        if let Some(home_dir) = dirs::home_dir() {
            let nss_db_path = home_dir.join(".pki/nssdb");
            if !fs.exists(&nss_db_path) {
                // Create the NSS DB if it doesn't exist.
                log::info!("NSS database not found, creating a new one.");
                let db_dir = nss_db_path.to_str().unwrap();
                let output = executor.execute(
                    certutil_path.to_str().unwrap(),
                    &["-N", "-d", &format!("sql:{}", db_dir), "--empty-password"],
                )?;
                if !output.status.success() {
                    let stderr = String::from_utf8_lossy(&output.stderr);
                    log::warn!("Failed to create NSS database. Stderr: {}", stderr);
                    // Continue anyway, as adding the cert might still work if the dir is there.
                }
            }

            let cert_path_str = cert_path.to_str().ok_or("Invalid certificate path")?;
            let cert_name = cert_path
                .file_name()
                .and_then(|s| s.to_str())
                .unwrap_or("openbb-cert");
            let cert_nickname = format!("OpenBB Platform - {}", cert_name);
            let db_path_str = format!("sql:{}", nss_db_path.to_str().unwrap());

            let add_cert_output = executor.execute(
                certutil_path.to_str().unwrap(),
                &[
                    "-A",
                    "-n",
                    &cert_nickname,
                    "-t",
                    "TC,,", // C for SSL, T for email, P for code signing. TC,, means trusted for SSL.
                    "-i",
                    cert_path_str,
                    "-d",
                    &db_path_str,
                ],
            )?;

            if !add_cert_output.status.success() {
                let stderr = String::from_utf8_lossy(&add_cert_output.stderr);
                return Err(format!(
                    "Failed to add certificate to user's browser trust store (NSS DB). Stderr: {}",
                    stderr
                ));
            }
        } else {
            return Err("Could not find user home directory.".to_string());
        }
    } else {
        return Err(
            "`certutil` command not found. Please install the `libnss3-tools` package (or equivalent) to install the certificate for browser support.".to_string()
        );
    }

    Ok(())
}

#[cfg(not(any(target_os = "windows", target_os = "macos", target_os = "linux")))]
fn install_cert_in_trust_store(
    _cert_path: &Path,
    _executor: &dyn CommandExecutor,
    _fs: &dyn FileSystem,
) -> Result<(), String> {
    Err("Unsupported OS for installing certificates in trust store.".to_string())
}

#[cfg(test)]
mod tests {
    use super::*;
    use mockall::predicate::*;

    #[test]
    fn test_generate_and_save_cert() {
        let mut fs = MockFileSystem::new();
        let mut trust_store = MockTrustStore::new();

        fs.expect_create_dir_all()
            .with(eq(Path::new("/tmp")))
            .times(1)
            .returning(|_| Ok(()));
        fs.expect_write().times(3).returning(|_, _| Ok(()));

        trust_store
            .expect_install()
            .with(eq(Path::new("/tmp/certificate.pem")), always(), always())
            .times(1)
            .returning(|_, _, _| Ok(()));

        let cert_service = CertService::new(
            Arc::new(fs),
            Arc::new(trust_store),
            Arc::new(MockCommandExecutor::new()),
        );

        let result = cert_service.generate_and_save_cert(
            "test.com".to_string(),
            "Test Org".to_string(),
            vec!["localhost".to_string()],
            "/tmp".to_string(),
            365,
            None,
            true,
        );

        assert!(result.is_ok());
    }

    #[test]
    #[cfg(target_os = "windows")]
    fn test_install_cert_in_trust_store_windows() {
        use std::os::windows::process::ExitStatusExt;
        let mut executor = MockCommandExecutor::new();
        let args: &[&str] = &["-user", "-addstore", "Root", "C:\\test.pem"];
        executor
            .expect_execute()
            .withf(move |cmd, cmd_args| cmd == "certutil" && cmd_args == args)
            .times(1)
            .returning(|_, _| {
                Ok(Output {
                    status: std::process::ExitStatus::from_raw(0),
                    stdout: Vec::new(),
                    stderr: Vec::new(),
                })
            });

        let result = install_cert_in_trust_store(
            Path::new("C:\\test.pem"),
            &executor,
            &MockFileSystem::new(),
        );
        assert!(result.is_ok());
    }

    #[test]
    #[cfg(target_os = "macos")]
    fn test_install_cert_in_trust_store_macos() {
        use std::os::unix::process::ExitStatusExt;
        let home_dir = dirs::home_dir().unwrap();
        let login_keychain_path = home_dir
            .join("Library/Keychains/login.keychain-db")
            .to_string_lossy()
            .into_owned();

        let mut executor = MockCommandExecutor::new();
        executor
            .expect_execute()
            .withf(move |cmd, args| {
                cmd == "security"
                    && args
                        == [
                            "add-trusted-cert",
                            "-d",
                            "-r",
                            "trustRoot",
                            "-k",
                            &login_keychain_path,
                            "/tmp/test.pem",
                        ]
            })
            .times(1)
            .returning(|_, _| {
                Ok(Output {
                    status: std::process::ExitStatus::from_raw(0),
                    stdout: Vec::new(),
                    stderr: Vec::new(),
                })
            });

        let result = install_cert_in_trust_store(
            Path::new("/tmp/test.pem"),
            &executor,
            &MockFileSystem::new(),
        );
        assert!(result.is_ok());
    }

    #[test]
    #[cfg(target_os = "linux")]
    fn test_install_cert_in_trust_store_linux() {
        use std::os::unix::process::ExitStatusExt;
        if which::which("certutil").is_err() {
            println!("Skipping test: certutil not found in PATH");
            return;
        }
        if dirs::home_dir().is_none() {
            println!("Skipping test: home directory not found");
            return;
        }

        let home_dir = dirs::home_dir().unwrap();
        let nss_db_path = home_dir.join(".pki/nssdb");
        let db_path_str = format!("sql:{}", nss_db_path.to_str().unwrap());
        let cert_nickname = "OpenBB Platform - certificate.pem".to_string();

        let mut executor = MockCommandExecutor::new();
        let mut fs = MockFileSystem::new();

        fs.expect_exists().with(eq(nss_db_path)).return_const(false);

        executor
            .expect_execute()
            .withf(move |cmd, args| cmd.contains("certutil") && args[0] == "-N")
            .times(1)
            .returning(|_, _| {
                Ok(Output {
                    status: std::process::ExitStatus::from_raw(0),
                    stdout: Vec::new(),
                    stderr: Vec::new(),
                })
            });

        executor
            .expect_execute()
            .withf(move |cmd, args| {
                cmd.contains("certutil")
                    && args
                        == &[
                            "-A",
                            "-n",
                            &cert_nickname,
                            "-t",
                            "TC,,",
                            "-i",
                            "/tmp/certificate.pem",
                            "-d",
                            &db_path_str,
                        ]
            })
            .times(1)
            .returning(|_, _| {
                Ok(Output {
                    status: std::process::ExitStatus::from_raw(0),
                    stdout: Vec::new(),
                    stderr: Vec::new(),
                })
            });

        let result = install_cert_in_trust_store(Path::new("/tmp/certificate.pem"), &executor, &fs);
        assert!(result.is_ok());
    }
}
