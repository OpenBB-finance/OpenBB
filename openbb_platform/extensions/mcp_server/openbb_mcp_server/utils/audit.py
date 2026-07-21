"""Signed audit receipts for MCP tool calls."""

from __future__ import annotations

import base64
import hashlib
import json
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from fastmcp.server.middleware import Middleware, MiddlewareContext

from openbb_mcp_server.models.audit import AuditReceipt
from openbb_mcp_server.models.settings import MCPSettings


def _jsonable(value: Any) -> Any:
    """Return a stable JSON-compatible representation."""
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, dict):
        return {
            str(k): _jsonable(v)
            for k, v in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, list | tuple | set):
        return [_jsonable(v) for v in value]
    if hasattr(value, "model_dump"):
        return _jsonable(value.model_dump(mode="json"))
    return repr(value)


def canonical_json(data: dict[str, Any]) -> bytes:
    """Serialize data into canonical JSON bytes."""
    return json.dumps(
        _jsonable(data),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def hash_arguments(arguments: dict[str, Any] | None) -> str:
    """Return the SHA-256 hash of canonical tool arguments."""
    return hashlib.sha256(canonical_json(arguments or {})).hexdigest()


def _b64encode(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _b64decode(value: str) -> bytes:
    return base64.b64decode(value.encode("ascii"), validate=True)


def load_ed25519_private_key(value: str) -> Ed25519PrivateKey:
    """Load an Ed25519 private key from PEM, base64 raw bytes, or hex raw bytes."""
    value = value.strip()
    if not value:
        raise ValueError("Ed25519 private key is required.")

    if value.startswith("-----BEGIN"):
        key = serialization.load_pem_private_key(value.encode("utf-8"), password=None)
        if not isinstance(key, Ed25519PrivateKey):
            raise ValueError("Private key must be an Ed25519 key.")
        return key

    try:
        raw = bytes.fromhex(value)
    except ValueError:
        raw = _b64decode(value)

    if len(raw) != 32:
        raise ValueError("Ed25519 raw private key must be exactly 32 bytes.")
    return Ed25519PrivateKey.from_private_bytes(raw)


def public_key_base64(private_key: Ed25519PrivateKey) -> str:
    """Return the base64-encoded raw public key for an Ed25519 private key."""
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return _b64encode(public_key)


def sign_receipt_payload(
    payload: dict[str, Any], private_key: Ed25519PrivateKey
) -> AuditReceipt:
    """Sign a receipt payload and return an AuditReceipt model."""
    signed_payload = {k: v for k, v in payload.items() if v is not None}
    signed_payload["public_key"] = public_key_base64(private_key)
    signature = private_key.sign(canonical_json(signed_payload))
    return AuditReceipt(**signed_payload, signature=_b64encode(signature))


def verify_receipt(receipt: AuditReceipt | dict[str, Any]) -> bool:
    """Verify an audit receipt signature."""
    receipt_model = (
        receipt if isinstance(receipt, AuditReceipt) else AuditReceipt.model_validate(receipt)
    )
    payload = receipt_model.model_dump(exclude={"signature"}, exclude_none=True)
    public_key = Ed25519PublicKey.from_public_bytes(_b64decode(receipt_model.public_key))
    try:
        public_key.verify(_b64decode(receipt_model.signature), canonical_json(payload))
    except InvalidSignature:
        return False
    return True


class JSONLAuditReceiptWriter:
    """Append signed audit receipts to a JSON Lines file."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser()
        self._lock = threading.Lock()

    def write(self, receipt: AuditReceipt) -> None:
        """Write one receipt as a JSONL record."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        line = receipt.model_dump_json(exclude_none=True)
        with self._lock, self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")


def _context_attr(context: MiddlewareContext, name: str) -> str | None:
    fastmcp_context = getattr(context, "fastmcp_context", None)
    for source in (context, fastmcp_context):
        value = getattr(source, name, None)
        if value:
            return str(value)
    return None


def _issued_at(context: MiddlewareContext) -> str:
    timestamp = getattr(context, "timestamp", None)
    if isinstance(timestamp, datetime):
        return timestamp.astimezone(timezone.utc).isoformat()
    return datetime.now(timezone.utc).isoformat()


class AuditReceiptMiddleware(Middleware):
    """FastMCP middleware that emits signed receipts for tool calls."""

    def __init__(
        self,
        *,
        private_key: Ed25519PrivateKey,
        receipt_path: str | Path,
        principal: str = "unknown",
        include_arguments: bool = False,
    ) -> None:
        self.private_key = private_key
        self.writer = JSONLAuditReceiptWriter(receipt_path)
        self.principal = principal or "unknown"
        self.include_arguments = include_arguments

    @classmethod
    def from_settings(cls, settings: MCPSettings) -> AuditReceiptMiddleware:
        """Create audit middleware from MCP settings."""
        if not settings.audit_receipts_private_key:
            raise ValueError(
                "OPENBB_MCP_AUDIT_RECEIPTS_PRIVATE_KEY is required when "
                "audit receipts are enabled."
            )
        if not settings.audit_receipts_path:
            raise ValueError(
                "OPENBB_MCP_AUDIT_RECEIPTS_PATH is required when audit receipts "
                "are enabled."
            )
        return cls(
            private_key=load_ed25519_private_key(settings.audit_receipts_private_key),
            receipt_path=settings.audit_receipts_path,
            principal=settings.audit_receipts_principal,
            include_arguments=settings.audit_receipts_include_arguments,
        )

    async def on_call_tool(self, context: MiddlewareContext, call_next: Any) -> Any:
        """Record a signed receipt after each tool call."""
        message = getattr(context, "message", None)
        tool_name = getattr(message, "name", "unknown")
        arguments = _jsonable(getattr(message, "arguments", {}) or {})
        started = time.perf_counter()
        status = "success"
        error_type = None

        try:
            return await call_next(context)
        except Exception as exc:
            status = "error"
            error_type = exc.__class__.__name__
            raise
        finally:
            payload: dict[str, Any] = {
                "receipt_id": str(uuid.uuid4()),
                "issued_at": _issued_at(context),
                "tool_name": tool_name,
                "arguments_sha256": hash_arguments(arguments),
                "status": status,
                "policy_decision": "allow",
                "duration_ms": round((time.perf_counter() - started) * 1000, 3),
                "principal": self.principal,
                "session_id": _context_attr(context, "session_id"),
                "request_id": _context_attr(context, "request_id"),
                "error_type": error_type,
            }
            if self.include_arguments:
                payload["arguments"] = arguments

            self.writer.write(sign_receipt_payload(payload, self.private_key))
