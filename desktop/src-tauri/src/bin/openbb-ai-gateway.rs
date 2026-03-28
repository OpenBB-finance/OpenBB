#[path = "../ai_gateway/mod.rs"]
mod ai_gateway;

use ai_gateway::http::build_router;
use ai_gateway::settings::default_user_settings_path;
use std::path::PathBuf;
use tokio::net::TcpListener;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut host = "127.0.0.1".to_string();
    let mut port = 0u16;
    let mut settings_path: Option<PathBuf> = None;
    let mut args = std::env::args().skip(1);

    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--host" => {
                if let Some(value) = args.next() {
                    host = value;
                }
            }
            "--port" => {
                if let Some(value) = args.next() {
                    port = value.parse::<u16>().unwrap_or(0);
                }
            }
            "--settings" => {
                if let Some(value) = args.next() {
                    settings_path = Some(PathBuf::from(value));
                }
            }
            _ => {}
        }
    }

    let settings_path = settings_path.unwrap_or(default_user_settings_path()?);
    let router = build_router(settings_path.clone());
    let listener = TcpListener::bind((host.as_str(), port)).await?;
    let local_addr = listener.local_addr()?;

    println!(
        "{}",
        serde_json::json!({
            "type": "ready",
            "port": local_addr.port(),
            "host": local_addr.ip().to_string(),
            "version": env!("CARGO_PKG_VERSION"),
            "settingsPath": settings_path.to_string_lossy(),
        })
    );

    axum::serve(listener, router).await?;
    Ok(())
}
