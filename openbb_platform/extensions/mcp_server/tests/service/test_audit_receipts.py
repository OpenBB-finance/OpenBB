"""Unit tests for signed MCP audit receipts."""

import base64
import json
from asyncio import run

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastmcp.server.middleware import MiddlewareContext
from fastmcp.tools.tool import ToolResult
from mcp.types import CallToolRequestParams
from openbb_mcp_server.models.audit_receipts import (
    AuditReceiptPayload,
    SignedAuditReceipt,
)
from openbb_mcp_server.models.settings import MCPSettings
from openbb_mcp_server.service.audit_receipts import (
    AuditReceiptSigner,
    create_audit_receipt_middleware,
)


def _private_key_b64() -> str:
    """Return a base64 raw Ed25519 private key for tests."""
    private_key = Ed25519PrivateKey.generate()
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return base64.urlsafe_b64encode(private_bytes).decode().rstrip("=")


def test_audit_receipt_sign_and_verify():
    """Sign and verify an audit receipt payload."""
    signer = AuditReceiptSigner.from_private_key_value(
        _private_key_b64(),
        key_id="test-key",
    )
    payload = AuditReceiptPayload(
        receipt_id="receipt-1",
        tool_name="equity_price_historical",
        principal="agent-1",
        timestamp="2026-06-17T00:00:00+00:00",
        decision="allow",
        request_hash="request-hash",
        normalized_view_hash="view-hash",
        policy_hash="policy-hash",
        allowed_scope=["equity.prices"],
        withheld_scope=[{"scope": "portfolio.private", "reason": "client_pii"}],
    )

    receipt = signer.sign(payload)

    assert receipt.key_id == "test-key"
    assert (
        AuditReceiptSigner.verify(
            receipt, public_keys={"test-key": signer.public_key_value}
        )
        is True
    )
    assert AuditReceiptSigner.verify(receipt) is False

    tampered = receipt.model_copy(deep=True)
    tampered.payload.tool_name = "equity_price_quote"

    assert (
        AuditReceiptSigner.verify(
            tampered, public_keys={"test-key": signer.public_key_value}
        )
        is False
    )


def test_audit_receipt_verify_rejects_untrusted_or_malformed_receipts():
    """Verify only succeeds against trusted key material."""
    trusted_signer = AuditReceiptSigner.from_private_key_value(
        _private_key_b64(),
        key_id="test-key",
    )
    rogue_signer = AuditReceiptSigner.from_private_key_value(
        _private_key_b64(),
        key_id="test-key",
    )
    payload = AuditReceiptPayload(
        receipt_id="receipt-1",
        tool_name="equity_price_historical",
        principal="agent-1",
        timestamp="2026-06-17T00:00:00+00:00",
        decision="allow",
        request_hash="request-hash",
    )
    rogue_receipt = rogue_signer.sign(payload)

    assert (
        AuditReceiptSigner.verify(
            rogue_receipt,
            public_keys={"test-key": trusted_signer.public_key_value},
        )
        is False
    )

    malformed = trusted_signer.sign(payload).model_copy(update={"signature": "not-b64"})

    assert (
        AuditReceiptSigner.verify(
            malformed,
            public_keys={"test-key": trusted_signer.public_key_value},
        )
        is False
    )

    wrong_algorithm = trusted_signer.sign(payload).model_copy(
        update={"signing_algorithm": "rsa"}
    )

    assert (
        AuditReceiptSigner.verify(
            wrong_algorithm,
            public_keys={"test-key": trusted_signer.public_key_value},
        )
        is False
    )


def test_audit_receipt_middleware_attaches_receipt_to_tool_result():
    """Attach a signed audit receipt to tool result metadata."""
    settings = MCPSettings(
        audit_receipts_enabled=True,
        audit_receipts_private_key=_private_key_b64(),
        audit_receipts_key_id="test-key",
        audit_receipts_principal="agent-1",
        audit_receipts_policy_hash="policy-hash",
        audit_receipts_allowed_scope=["equity.prices"],
        audit_receipts_withheld_scope=[
            {"scope": "portfolio.private", "reason": "client_pii"}
        ],
    )
    middleware = create_audit_receipt_middleware(settings)
    context = MiddlewareContext(
        message=CallToolRequestParams(
            name="equity_price_historical",
            arguments={"symbol": "AAPL", "provider": "fmp"},
        ),
        method="tools/call",
    )

    async def call_next(_context):
        return ToolResult(structured_content={"results": [{"close": 200.0}]})

    result = run(middleware.on_call_tool(context, call_next))
    receipt = SignedAuditReceipt.model_validate(result.meta["openbb_audit_receipt"])

    assert (
        AuditReceiptSigner.verify(
            receipt,
            public_keys={"test-key": middleware.signer.public_key_value},
        )
        is True
    )
    assert receipt.payload.tool_name == "equity_price_historical"
    assert receipt.payload.principal == "agent-1"
    assert receipt.payload.decision == "allow"
    assert receipt.payload.policy_hash == "policy-hash"
    assert receipt.payload.allowed_scope == ["equity.prices"]
    assert receipt.payload.normalized_view_hash


def test_audit_receipt_middleware_marks_error_tool_results_as_denied():
    """Attach a denial receipt to completed error tool results."""
    settings = MCPSettings(
        audit_receipts_enabled=True,
        audit_receipts_private_key=_private_key_b64(),
        audit_receipts_key_id="test-key",
        audit_receipts_principal="agent-1",
    )
    middleware = create_audit_receipt_middleware(settings)
    context = MiddlewareContext(
        message=CallToolRequestParams(
            name="equity_price_historical",
            arguments={"symbol": "AAPL", "provider": "fmp"},
        ),
        method="tools/call",
    )

    async def call_next(_context):
        return ToolResult(content=[], is_error=True)

    result = run(middleware.on_call_tool(context, call_next))
    receipt = SignedAuditReceipt.model_validate(result.meta["openbb_audit_receipt"])

    assert receipt.payload.decision == "deny"
    assert (
        AuditReceiptSigner.verify(
            receipt,
            public_key=middleware.signer.public_key_value,
            key_id="test-key",
        )
        is True
    )


def test_audit_receipt_private_key_is_redacted_from_settings_dump():
    """Ensure signing key material is not persisted in plaintext settings dumps."""
    private_key = _private_key_b64()
    settings = MCPSettings(
        audit_receipts_private_key=private_key,
        audit_receipts_public_keys='{"test-key":"public-key"}',
    )

    dumped = settings.model_dump(mode="json")

    assert private_key not in json.dumps(dumped)
    assert dumped["audit_receipts_private_key"] == "**********"
    assert settings.audit_receipts_public_keys == {"test-key": "public-key"}
