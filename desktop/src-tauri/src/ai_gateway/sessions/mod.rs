use crate::ai_gateway::{
    AiMode, AiApprovalDecision, AiRunEvent, PendingApprovalSummary, ProviderId, SessionDetail,
    SessionSummary,
};
use chrono::Utc;
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use tokio::sync::{RwLock, broadcast, mpsc, oneshot};
use tokio::task::JoinHandle;

pub struct RunRecord {
    pub run_id: String,
    pub session_id: Option<String>,
    pub provider: ProviderId,
    pub mode: AiMode,
    pub title: String,
    pub history: Arc<Mutex<Vec<AiRunEvent>>>,
    pub tx: broadcast::Sender<AiRunEvent>,
    pub input_tx: mpsc::UnboundedSender<AiRunEvent>,
    pub worker: Arc<Mutex<Option<JoinHandle<()>>>>,
}

impl RunRecord {
    pub fn subscribe(&self) -> broadcast::Receiver<AiRunEvent> {
        self.tx.subscribe()
    }

    pub fn history_snapshot(&self) -> Vec<AiRunEvent> {
        self.history.lock().map(|guard| guard.clone()).unwrap_or_default()
    }

    pub fn abort(&self) {
        if let Ok(mut worker) = self.worker.lock()
            && let Some(handle) = worker.take()
        {
            handle.abort();
        }
    }
}

struct SessionMetadata {
    pub session_id: String,
    pub provider: ProviderId,
    pub mode: AiMode,
    pub title: String,
    pub latest_run_id: String,
    pub updated_at: String,
}

struct PendingApproval {
    pub approval_id: String,
    pub session_id: String,
    pub run_id: String,
    pub kind: String,
    pub summary: String,
    pub responder: Mutex<Option<oneshot::Sender<AiApprovalDecision>>>,
}

#[derive(Default)]
pub struct SessionStore {
    runs: RwLock<HashMap<String, Arc<RunRecord>>>,
    sessions: RwLock<HashMap<String, SessionMetadata>>,
    approvals: RwLock<HashMap<String, Arc<PendingApproval>>>,
}

impl SessionStore {
    pub async fn insert(&self, record: Arc<RunRecord>) {
        self.runs
            .write()
            .await
            .insert(record.run_id.clone(), record.clone());
        if let Some(session_id) = record.session_id.as_ref() {
            self.sessions.write().await.insert(
                session_id.clone(),
                SessionMetadata {
                    session_id: session_id.clone(),
                    provider: record.provider.clone(),
                    mode: record.mode.clone(),
                    title: record.title.clone(),
                    latest_run_id: record.run_id.clone(),
                    updated_at: now_iso(),
                },
            );
        }
    }

    pub async fn get(&self, run_id: &str) -> Option<Arc<RunRecord>> {
        self.runs.read().await.get(run_id).cloned()
    }

    pub async fn list_sessions(&self) -> Vec<SessionSummary> {
        let sessions = self.sessions.read().await;
        let runs = self.runs.read().await;
        let mut items = sessions
            .values()
            .filter_map(|metadata| {
                runs.get(&metadata.latest_run_id)
                    .map(|record| self.build_summary(metadata, record))
            })
            .collect::<Vec<_>>();
        items.sort_by(|left, right| right.updated_at.cmp(&left.updated_at));
        items
    }

    pub async fn session_detail(&self, session_id: &str) -> Option<SessionDetail> {
        let sessions = self.sessions.read().await;
        let metadata = sessions.get(session_id)?;
        let runs = self.runs.read().await;
        let record = runs.get(&metadata.latest_run_id)?;
        let pending = self
            .approvals_for_session(session_id)
            .await
            .into_iter()
            .map(|approval| PendingApprovalSummary {
                approval_id: approval.approval_id.clone(),
                kind: approval.kind.clone(),
                summary: approval.summary.clone(),
            })
            .collect::<Vec<_>>();
        Some(SessionDetail {
            summary: self.build_summary(metadata, record),
            pending_approvals: pending,
            recent_events: record.history_snapshot(),
        })
    }

    pub async fn register_approval(
        &self,
        run_id: &str,
        session_id: &str,
        kind: String,
        summary: String,
        responder: oneshot::Sender<AiApprovalDecision>,
    ) -> String {
        let approval_id = uuid::Uuid::new_v4().to_string();
        self.approvals.write().await.insert(
            approval_id.clone(),
            Arc::new(PendingApproval {
                approval_id: approval_id.clone(),
                session_id: session_id.to_string(),
                run_id: run_id.to_string(),
                kind,
                summary,
                responder: Mutex::new(Some(responder)),
            }),
        );
        if let Some(metadata) = self.sessions.write().await.get_mut(session_id) {
            metadata.updated_at = now_iso();
        }
        approval_id
    }

    pub async fn resolve_approval(&self, approval_id: &str, decision: AiApprovalDecision) -> bool {
        let approval = self.approvals.write().await.remove(approval_id);
        let Some(approval) = approval else {
            return false;
        };
        if let Ok(mut responder) = approval.responder.lock()
            && let Some(tx) = responder.take()
        {
            let _ = tx.send(decision);
        }
        if let Some(metadata) = self.sessions.write().await.get_mut(&approval.session_id) {
            metadata.updated_at = now_iso();
        }
        true
    }

    pub async fn cancel(&self, run_id: &str) -> bool {
        if let Some(record) = self.get(run_id).await {
            record.abort();
            let _ = record.input_tx.send(AiRunEvent::Error {
                code: "E_PROCESS_CRASHED".to_string(),
                message: "Run cancelled by user.".to_string(),
                detail: None,
            });
            let _ = record.input_tx.send(AiRunEvent::Done { usage: None });
            if let Some(session_id) = record.session_id.as_ref()
                && let Some(metadata) = self.sessions.write().await.get_mut(session_id)
            {
                metadata.updated_at = now_iso();
            }
            true
        } else {
            false
        }
    }

    fn build_summary(&self, metadata: &SessionMetadata, record: &Arc<RunRecord>) -> SessionSummary {
        SessionSummary {
            session_id: metadata.session_id.clone(),
            provider: metadata.provider.clone(),
            mode: metadata.mode.clone(),
            status: latest_status(record),
            title: metadata.title.clone(),
            latest_run_id: metadata.latest_run_id.clone(),
            updated_at: metadata.updated_at.clone(),
        }
    }

    async fn approvals_for_session(&self, session_id: &str) -> Vec<Arc<PendingApproval>> {
        self.approvals
            .read()
            .await
            .values()
            .filter(|approval| approval.session_id == session_id)
            .cloned()
            .collect()
    }
}

fn latest_status(record: &Arc<RunRecord>) -> String {
    let history = record.history_snapshot();
    let mut saw_done = false;
    let mut latest_phase: Option<String> = None;
    for event in &history {
        match event {
            AiRunEvent::Error { message, .. } if message.eq_ignore_ascii_case("Run cancelled by user.") => {
                return "cancelled".to_string();
            }
            AiRunEvent::Error { .. } => return "failed".to_string(),
            AiRunEvent::Done { .. } => saw_done = true,
            AiRunEvent::Status { phase } if matches!(phase.as_str(), "queued" | "running") => {
                latest_phase = Some(phase.clone());
            }
            _ => {}
        }
    }
    if saw_done {
        "completed".to_string()
    } else if let Some(phase) = latest_phase {
        phase
    } else {
        "queued".to_string()
    }
}

fn now_iso() -> String {
    Utc::now().to_rfc3339()
}

pub fn create_run_record(
    run_id: String,
    session_id: Option<String>,
    provider: ProviderId,
    mode: AiMode,
    title: String,
) -> Arc<RunRecord> {
    let (tx, _rx) = broadcast::channel(128);
    let (input_tx, mut input_rx) = mpsc::unbounded_channel::<AiRunEvent>();
    let history = Arc::new(Mutex::new(Vec::new()));
    let history_clone = history.clone();
    let tx_clone = tx.clone();
    tokio::spawn(async move {
        while let Some(event) = input_rx.recv().await {
            if let Ok(mut guard) = history_clone.lock() {
                guard.push(event.clone());
            }
            let _ = tx_clone.send(event);
        }
    });

    Arc::new(RunRecord {
        run_id,
        session_id,
        provider,
        mode,
        title,
        history,
        tx,
        input_tx,
        worker: Arc::new(Mutex::new(None)),
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn latest_status_prefers_cancelled_over_done() {
        let record = create_run_record(
            "run-1".to_string(),
            Some("session-1".to_string()),
            ProviderId::Gemini,
            AiMode::Agent,
            "cancel smoke".to_string(),
        );
        if let Ok(mut guard) = record.history.lock() {
            guard.push(AiRunEvent::Status {
                phase: "running".to_string(),
            });
            guard.push(AiRunEvent::Error {
                code: "E_PROCESS_CRASHED".to_string(),
                message: "Run cancelled by user.".to_string(),
                detail: None,
            });
            guard.push(AiRunEvent::Done { usage: None });
        }
        assert_eq!(latest_status(&record), "cancelled");
    }
}
