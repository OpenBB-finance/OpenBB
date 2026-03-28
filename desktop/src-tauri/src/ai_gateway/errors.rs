use serde::Serialize;

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct GatewayError {
    pub code: String,
    pub message: String,
    pub detail: Option<String>,
}

impl GatewayError {
    pub fn new(code: impl Into<String>, message: impl Into<String>) -> Self {
        Self {
            code: code.into(),
            message: message.into(),
            detail: None,
        }
    }

    pub fn with_detail(mut self, detail: impl Into<String>) -> Self {
        self.detail = Some(detail.into());
        self
    }
}

impl std::fmt::Display for GatewayError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}: {}", self.code, self.message)
    }
}

impl std::error::Error for GatewayError {}

pub type GatewayResult<T> = Result<T, GatewayError>;

pub fn provider_not_installed(provider: &str) -> GatewayError {
    GatewayError::new(
        "E_PROVIDER_NOT_INSTALLED",
        format!("{provider} CLI is not installed or not on PATH."),
    )
}

pub fn provider_not_authenticated(provider: &str, detail: impl Into<String>) -> GatewayError {
    GatewayError::new(
        "E_PROVIDER_NOT_AUTHENTICATED",
        format!("{provider} is installed but not authenticated."),
    )
    .with_detail(detail)
}

pub fn provider_busy(provider: &str, detail: impl Into<String>) -> GatewayError {
    GatewayError::new("E_PROVIDER_BUSY", format!("{provider} is busy."))
        .with_detail(detail)
}

pub fn process_crashed(provider: &str, detail: impl Into<String>) -> GatewayError {
    GatewayError::new(
        "E_PROCESS_CRASHED",
        format!("{provider} process exited unexpectedly."),
    )
    .with_detail(detail)
}

pub fn unsupported_transport(provider: &str, transport: &str) -> GatewayError {
    GatewayError::new(
        "E_UNSUPPORTED_TRANSPORT",
        format!("{provider} transport `{transport}` is unavailable."),
    )
}
