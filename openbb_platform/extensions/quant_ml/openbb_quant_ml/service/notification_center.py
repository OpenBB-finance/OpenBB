"""Notification outbox, dedupe, and multi-channel dispatch."""

from __future__ import annotations

import hashlib
import json
import os
import smtplib
from datetime import UTC, datetime, timedelta
from email.message import EmailMessage
from typing import Any
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from openbb_quant_ml.models import (
    NotificationItemResponse,
    NotificationsHistoryResponse,
)
from openbb_quant_ml.service.ops_policy import get_ops_policy
from openbb_quant_ml.service.registry.run_registry_db import (
    enqueue_notification,
    find_recent_notification,
    list_notifications,
    update_notification_status,
)

_TIMEOUT_SEC = 10


def _now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def _now_iso() -> str:
    return _now().isoformat()


def _policy_notifications() -> dict[str, Any]:
    policy = get_ops_policy()
    notifications = policy.get("notifications", {}) if isinstance(policy, dict) else {}
    return notifications if isinstance(notifications, dict) else {}


def _enabled_channels(explicit: list[str] | None = None) -> list[str]:
    if explicit:
        return [str(item).strip().lower() for item in explicit if str(item).strip()]
    cfg = _policy_notifications().get("channels", {})
    channels: list[str] = []
    if isinstance(cfg, dict):
        for name, payload in cfg.items():
            if isinstance(payload, dict) and bool(payload.get("enabled", False)):
                channels.append(str(name).strip().lower())
    return channels


def _fingerprint(
    *,
    run_id: str | None,
    event_type: str,
    title: str,
    body: str,
) -> str:
    payload = f"{run_id or ''}|{event_type}|{title}|{body}".encode()
    return hashlib.sha1(payload).hexdigest()


def _is_duplicate(fingerprint: str, channel: str) -> bool:
    notifications = _policy_notifications()
    window_minutes = int(notifications.get("dedupe_window_minutes", 240) or 240)
    cutoff = _now() - timedelta(minutes=max(window_minutes, 1))
    for row in find_recent_notification(fingerprint=fingerprint, channel=channel, limit=5):
        created_at = str(row.get("created_at_utc") or "")
        try:
            created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except ValueError:
            continue
        status = str(row.get("status", "")).strip().lower()
        if status in {"sent", "queued", "duplicate"} and created_dt >= cutoff:
            return True
    return False


def _send_slack(payload: dict[str, Any]) -> None:
    url = str(os.environ.get("SLACK_WEBHOOK_URL", "")).strip()
    if not url:
        raise RuntimeError("SLACK_WEBHOOK_URL is not configured")
    body = json.dumps(
        {
            "text": f"*{payload['title']}*\n{payload['body']}",
            "username": "Quant ML Bot",
        }
    ).encode("utf-8")
    req = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=_TIMEOUT_SEC):
        return None


def _send_discord(payload: dict[str, Any]) -> None:
    url = str(os.environ.get("DISCORD_WEBHOOK_URL", "")).strip()
    if not url:
        raise RuntimeError("DISCORD_WEBHOOK_URL is not configured")
    body = json.dumps(
        {
            "embeds": [
                {
                    "title": payload["title"],
                    "description": payload["body"][:2000],
                    "timestamp": _now_iso(),
                }
            ]
        }
    ).encode("utf-8")
    req = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=_TIMEOUT_SEC):
        return None


def _send_webhook(payload: dict[str, Any]) -> None:
    url = str(os.environ.get("NOTIFY_WEBHOOK_URL", "")).strip()
    if not url:
        raise RuntimeError("NOTIFY_WEBHOOK_URL is not configured")
    body = json.dumps(payload).encode("utf-8")
    req = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=_TIMEOUT_SEC):
        return None


def _send_telegram(payload: dict[str, Any]) -> None:
    token = str(os.environ.get("TELEGRAM_BOT_TOKEN", "")).strip()
    chat_id = str(os.environ.get("TELEGRAM_CHAT_ID", "")).strip()
    if not token or not chat_id:
        raise RuntimeError("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not configured")
    body = urlencode(
        {
            "chat_id": chat_id,
            "text": f"{payload['title']}\n{payload['body']}",
        }
    ).encode("utf-8")
    req = Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urlopen(req, timeout=_TIMEOUT_SEC):
        return None


def _send_email(payload: dict[str, Any]) -> None:
    host = str(os.environ.get("SMTP_HOST", "")).strip()
    port = int(str(os.environ.get("SMTP_PORT", "587")).strip() or "587")
    username = str(os.environ.get("SMTP_USERNAME", "")).strip()
    password = str(os.environ.get("SMTP_PASSWORD", "")).strip()
    to_addr = str(os.environ.get("EMAIL_TO", "")).strip()
    from_addr = str(os.environ.get("EMAIL_FROM", username or "")).strip()
    use_tls = str(os.environ.get("SMTP_USE_TLS", "true")).strip().lower() != "false"
    if not host or not to_addr or not from_addr:
        raise RuntimeError("SMTP_HOST/EMAIL_TO/EMAIL_FROM are not configured")
    msg = EmailMessage()
    msg["Subject"] = payload["title"]
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(payload["body"])
    with smtplib.SMTP(host, port, timeout=_TIMEOUT_SEC) as smtp:
        if use_tls:
            smtp.starttls()
        if username and password:
            smtp.login(username, password)
        smtp.send_message(msg)


_CHANNEL_SENDERS = {
    "slack": _send_slack,
    "discord": _send_discord,
    "webhook": _send_webhook,
    "telegram": _send_telegram,
    "email": _send_email,
}


def dispatch_notification(
    *,
    run_id: str | None,
    event_type: str,
    title: str,
    body: str,
    severity: str = "info",
    channels: list[str] | None = None,
    extra_payload: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Persist and attempt delivery for one notification event."""
    enabled_channels = _enabled_channels(channels)
    payload = {
        "run_id": run_id,
        "event_type": event_type,
        "severity": severity,
        "title": title,
        "body": body,
        **(extra_payload or {}),
    }
    if not enabled_channels:
        return []
    results: list[dict[str, Any]] = []
    for channel in enabled_channels:
        fingerprint = _fingerprint(
            run_id=run_id, event_type=event_type, title=title, body=body
        )
        if _is_duplicate(fingerprint, channel):
            notification_id = enqueue_notification(
                run_id=run_id,
                event_type=event_type,
                channel=channel,
                fingerprint=fingerprint,
                payload_json=payload,
                status="duplicate",
                attempts=0,
                last_error=None,
                created_at_utc=_now_iso(),
                updated_at_utc=_now_iso(),
                delivered_at_utc=None,
            )
            results.append(
                {
                    "id": notification_id,
                    "channel": channel,
                    "status": "duplicate",
                }
            )
            continue
        notification_id = enqueue_notification(
            run_id=run_id,
            event_type=event_type,
            channel=channel,
            fingerprint=fingerprint,
            payload_json=payload,
            status="queued",
            attempts=0,
            last_error=None,
            created_at_utc=_now_iso(),
            updated_at_utc=_now_iso(),
            delivered_at_utc=None,
        )
        sender = _CHANNEL_SENDERS.get(channel)
        if sender is None:
            update_notification_status(
                notification_id,
                status="failed",
                attempts=1,
                updated_at_utc=_now_iso(),
                last_error="unknown channel",
            )
            results.append(
                {"id": notification_id, "channel": channel, "status": "failed"}
            )
            continue
        try:
            sender(payload)
        except (RuntimeError, URLError, OSError, smtplib.SMTPException) as exc:
            update_notification_status(
                notification_id,
                status="failed",
                attempts=1,
                updated_at_utc=_now_iso(),
                last_error=str(exc),
            )
            results.append(
                {
                    "id": notification_id,
                    "channel": channel,
                    "status": "failed",
                    "error": str(exc),
                }
            )
            continue
        update_notification_status(
            notification_id,
            status="sent",
            attempts=1,
            updated_at_utc=_now_iso(),
            delivered_at_utc=_now_iso(),
        )
        results.append({"id": notification_id, "channel": channel, "status": "sent"})
    return results


def dispatch_job_notification(config: dict[str, Any]) -> dict[str, Any]:
    """Compatibility adapter for job step notifications."""
    job_status = str(config.get("_job_status", "completed"))
    job_name = str(config.get("_job_name", "quant_ml"))
    run_id = str(config.get("run_id", "")).strip() or None
    error = config.get("_job_error")
    title = f"[{job_name}] Job {'failed' if error else job_status}"
    body = (
        f"Run: {run_id or 'n/a'}\nError: {error}"
        if error
        else f"Run: {run_id or 'n/a'}\nStatus: {job_status}"
    )
    channels_raw = str(config.get("notify_channels", "")).strip()
    explicit_channels = (
        [item.strip().lower() for item in channels_raw.split(",") if item.strip()]
        if channels_raw
        else None
    )
    results = dispatch_notification(
        run_id=run_id,
        event_type=f"job.{job_name}",
        title=title,
        body=body,
        severity="error" if error else "info",
        channels=explicit_channels,
        extra_payload={"job_name": job_name, "job_status": job_status},
    )
    if not results:
        return {"status": "skipped", "message": "No notification channels configured."}
    failed = [item for item in results if item.get("status") == "failed"]
    return {
        "status": "ok" if not failed else "partial_failure",
        "results": results,
    }


def _row_to_response(row: dict[str, Any]) -> NotificationItemResponse:
    raw_payload = row.get("payload_json", {})
    if isinstance(raw_payload, str):
        try:
            payload = json.loads(raw_payload)
        except json.JSONDecodeError:
            payload = {}
    else:
        payload = raw_payload if isinstance(raw_payload, dict) else {}
    return NotificationItemResponse(
        id=int(row.get("id", 0) or 0),
        run_id=(
            str(row.get("run_id")) if row.get("run_id") is not None else None
        ),
        event_type=str(row.get("event_type", "")),
        channel=str(row.get("channel", "")),
        fingerprint=str(row.get("fingerprint", "")),
        status=str(row.get("status", "")),
        payload=payload,
        attempts=int(row.get("attempts", 0) or 0),
        last_error=(
            str(row.get("last_error")) if row.get("last_error") is not None else None
        ),
        created_at=(
            str(row.get("created_at_utc")) if row.get("created_at_utc") else None
        ),
        updated_at=(
            str(row.get("updated_at_utc")) if row.get("updated_at_utc") else None
        ),
        delivered_at=(
            str(row.get("delivered_at_utc"))
            if row.get("delivered_at_utc") is not None
            else None
        ),
    )


def get_notifications_history_response(
    *, limit: int = 100
) -> NotificationsHistoryResponse:
    """Return outbox history."""
    rows = list_notifications(limit=limit)
    return NotificationsHistoryResponse(items=[_row_to_response(row) for row in rows])
