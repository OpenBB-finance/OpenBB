"""Tests for MCP audit receipts."""

import base64
import json
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from openbb_mcp_server.models.audit import AuditReceipt
from openbb_mcp_server.utils.audit import (
    AuditReceiptMiddleware,
    hash_arguments,
    verify_receipt,
)


def _private_key_b64() -> str:
    key = Ed25519PrivateKey.generate()
    raw = key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return base64.b64encode(raw).decode("ascii")


def _context(arguments=None):
    return SimpleNamespace(
        message=SimpleNamespace(
            name="equity_price_historical",
            arguments=arguments or {"symbol": "AAPL", "start_date": "2024-01-01"},
        ),
        timestamp=datetime(2026, 6, 12, tzinfo=timezone.utc),
        session_id="session-1",
        request_id="request-1",
        fastmcp_context=None,
    )


def _read_receipt(path) -> AuditReceipt:
    line = path.read_text(encoding="utf-8").strip()
    return AuditReceipt.model_validate(json.loads(line))


@pytest.mark.asyncio
async def test_audit_receipt_is_written_and_verifiable(tmp_path):
    """A successful tool call writes a signed receipt without raw arguments."""
    receipt_path = tmp_path / "audit.jsonl"
    middleware = AuditReceiptMiddleware.from_settings(
        SimpleNamespace(
            audit_receipts_private_key=_private_key_b64(),
            audit_receipts_path=str(receipt_path),
            audit_receipts_principal="analyst-agent",
            audit_receipts_include_arguments=False,
        )
    )

    async def call_next(context):
        return "ok"

    result = await middleware.on_call_tool(_context(), call_next)

    assert result == "ok"
    receipt = _read_receipt(receipt_path)
    assert receipt.tool_name == "equity_price_historical"
    assert receipt.status == "success"
    assert receipt.policy_decision == "allow"
    assert receipt.principal == "analyst-agent"
    assert receipt.session_id == "session-1"
    assert receipt.request_id == "request-1"
    assert receipt.arguments is None
    assert receipt.arguments_sha256 == hash_arguments({"symbol": "AAPL", "start_date": "2024-01-01"})
    assert verify_receipt(receipt)


@pytest.mark.asyncio
async def test_audit_receipt_records_errors_and_reraises(tmp_path):
    """Failed tool calls still produce a receipt and preserve the error."""
    receipt_path = tmp_path / "audit.jsonl"
    middleware = AuditReceiptMiddleware.from_settings(
        SimpleNamespace(
            audit_receipts_private_key=_private_key_b64(),
            audit_receipts_path=str(receipt_path),
            audit_receipts_principal="analyst-agent",
            audit_receipts_include_arguments=False,
        )
    )

    async def call_next(context):
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        await middleware.on_call_tool(_context(), call_next)

    receipt = _read_receipt(receipt_path)
    assert receipt.status == "error"
    assert receipt.error_type == "RuntimeError"
    assert verify_receipt(receipt)


@pytest.mark.asyncio
async def test_audit_receipt_can_include_arguments_when_enabled(tmp_path):
    """Raw arguments are recorded only when explicitly enabled."""
    receipt_path = tmp_path / "audit.jsonl"
    middleware = AuditReceiptMiddleware.from_settings(
        SimpleNamespace(
            audit_receipts_private_key=_private_key_b64(),
            audit_receipts_path=str(receipt_path),
            audit_receipts_principal="analyst-agent",
            audit_receipts_include_arguments=True,
        )
    )

    async def call_next(context):
        return "ok"

    await middleware.on_call_tool(_context({"symbol": "MSFT"}), call_next)

    receipt = _read_receipt(receipt_path)
    assert receipt.arguments == {"symbol": "MSFT"}
    assert receipt.arguments_sha256 == hash_arguments({"symbol": "MSFT"})
    assert verify_receipt(receipt)
