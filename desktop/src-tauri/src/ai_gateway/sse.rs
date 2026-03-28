use crate::ai_gateway::AiRunEvent;
use axum::response::sse::Event;

pub fn encode_event(event: &AiRunEvent) -> Event {
    Event::default().data(
        serde_json::to_string(event)
            .unwrap_or_else(|_| "{\"type\":\"error\",\"code\":\"E_PROCESS_CRASHED\",\"message\":\"Failed to encode event.\"}".to_string()),
    )
}
