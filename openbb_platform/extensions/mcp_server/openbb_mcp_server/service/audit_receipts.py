"""Signed audit receipt service for MCP tool calls."""

# pylint: disable=too-many-arguments

from __future__ import annotations

import base64
import binascii
import hashlib
import json
from typing import Any
from uuid import uuid4

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext

from openbb_mcp_server.models.audit_receipts import (
    AuditReceiptPayload,
    CommitmentStage,
    RetentionMode,
    SignedAuditReceipt,
)
from openbb_mcp_server.models.settings import MCPSettings


def _canonical_json(data: Any) -> bytes:
    """Serialize data into stable JSON bytes for hashing and signing."""
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    ).encode()


def sha256_digest(data: Any) -> str:
    """Return a sha256 hex digest for arbitrary JSON-compatible data."""
    return hashlib.sha256(_canonical_json(data)).hexdigest()


def _b64encode(data: bytes) -> str:
    """Return URL-safe base64 without newlines."""
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _b64decode(data: str) -> bytes:
    """Decode URL-safe or standard base64 with optional padding."""
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded.encode())


def _load_private_key(value: str) -> Ed25519PrivateKey:
    """Load an Ed25519 private key from PEM or base64 raw private bytes."""
    if value.strip().startswith("-----BEGIN"):
        key = serialization.load_pem_private_key(value.encode(), password=None)
        if not isinstance(key, Ed25519PrivateKey):
            raise ValueError("OPENBB_MCP_AUDIT_RECEIPTS_PRIVATE_KEY must be Ed25519.")
        return key

    return Ed25519PrivateKey.from_private_bytes(_b64decode(value))


def public_key_to_b64(public_key: Ed25519PublicKey) -> str:
    """Serialize an Ed25519 public key to base64 raw bytes."""
    return _b64encode(
        public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
    )


class AuditReceiptSigner:
    """Signs and verifies MCP audit receipt payloads."""

    def __init__(self, private_key: Ed25519PrivateKey, key_id: str | None = None):
        """Initialize the signer."""
        self.private_key = private_key
        self.public_key = private_key.public_key()
        self.key_id = key_id

    @classmethod
    def from_private_key_value(
        cls, private_key_value: str, key_id: str | None = None
    ) -> AuditReceiptSigner:
        """Create a signer from a configured private key value."""
        return cls(_load_private_key(private_key_value), key_id=key_id)

    def sign(self, payload: AuditReceiptPayload) -> SignedAuditReceipt:
        """Sign a receipt payload."""
        payload_dict = payload.model_dump(mode="json", exclude_none=True)
        payload_hash = sha256_digest(payload_dict)
        signature = self.private_key.sign(_canonical_json(payload_dict))

        return SignedAuditReceipt(
            payload=payload,
            payload_hash=payload_hash,
            signature=_b64encode(signature),
            key_id=self.key_id,
            public_key=public_key_to_b64(self.public_key),
        )

    @property
    def public_key_value(self) -> str:
        """Return the signer's public key as base64 raw bytes."""
        return public_key_to_b64(self.public_key)

    @staticmethod
    def verify(
        receipt: SignedAuditReceipt,
        *,
        public_key: str | None = None,
        public_keys: dict[str, str] | None = None,
        key_id: str | None = None,
    ) -> bool:
        """Verify a signed audit receipt against trusted public key material."""
        if receipt.signing_algorithm != "ed25519":
            return False

        if key_id is not None and receipt.key_id != key_id:
            return False

        trusted_public_key = public_key
        if public_keys is not None:
            if not receipt.key_id:
                return False
            trusted_public_key = public_keys.get(receipt.key_id)

        if not trusted_public_key:
            return False

        if receipt.public_key != trusted_public_key:
            return False

        payload_dict = receipt.payload.model_dump(mode="json", exclude_none=True)
        if sha256_digest(payload_dict) != receipt.payload_hash:
            return False

        try:
            verifier = Ed25519PublicKey.from_public_bytes(
                _b64decode(trusted_public_key)
            )
            verifier.verify(
                _b64decode(receipt.signature),
                _canonical_json(payload_dict),
            )
        except (binascii.Error, InvalidSignature, TypeError, ValueError):
            return False

        return True


class AuditReceiptMiddleware(Middleware):
    """Attach signed audit receipts to MCP tool results."""

    def __init__(
        self,
        signer: AuditReceiptSigner,
        *,
        principal: str,
        retention_mode: RetentionMode = "hash_only",
        commitment_stage: CommitmentStage = "post_normalization",
        policy_hash: str | None = None,
        catalog_version: str | None = None,
        allowed_scope: list[str] | None = None,
        withheld_scope: list[dict[str, Any]] | None = None,
    ):
        """Initialize audit receipt middleware."""
        self.signer = signer
        self.principal = principal
        self.retention_mode = retention_mode
        self.commitment_stage = commitment_stage
        self.policy_hash = policy_hash
        self.catalog_version = catalog_version
        self.allowed_scope = allowed_scope
        self.withheld_scope = withheld_scope

    async def on_call_tool(
        self,
        context: MiddlewareContext[Any],
        call_next: CallNext[Any, Any],
    ) -> Any:
        """Sign successful MCP tool-call results and attach them to result metadata."""
        result = await call_next(context)

        tool_name = getattr(context.message, "name", "unknown_tool")
        arguments = getattr(context.message, "arguments", None) or {}
        result_dict = (
            result.model_dump(mode="json", exclude_none=True)
            if hasattr(result, "model_dump")
            else result
        )
        decision = "deny" if getattr(result, "is_error", False) else "allow"

        payload = AuditReceiptPayload(
            receipt_id=str(uuid4()),
            tool_name=tool_name,
            principal=self.principal,
            timestamp=context.timestamp.isoformat(),
            decision=decision,
            request_hash=sha256_digest(
                {
                    "tool_name": tool_name,
                    "arguments": arguments,
                }
            ),
            normalized_view_hash=sha256_digest(result_dict),
            retention_mode=self.retention_mode,
            commitment_stage=self.commitment_stage,
            policy_hash=self.policy_hash,
            catalog_version=self.catalog_version,
            allowed_scope=self.allowed_scope,
            withheld_scope=self.withheld_scope,
        )
        receipt = self.signer.sign(payload)

        meta = dict(getattr(result, "meta", None) or {})
        meta["openbb_audit_receipt"] = receipt.model_dump(
            mode="json",
            exclude_none=True,
        )

        return (
            result.model_copy(update={"meta": meta})
            if hasattr(result, "model_copy")
            else result
        )


def create_audit_receipt_middleware(settings: MCPSettings) -> AuditReceiptMiddleware:
    """Create audit receipt middleware from MCP settings."""
    if (
        not settings.audit_receipts_private_key
        or not settings.audit_receipts_private_key.get_secret_value()
    ):
        raise ValueError(
            "OPENBB_MCP_AUDIT_RECEIPTS_PRIVATE_KEY is required when "
            "OPENBB_MCP_AUDIT_RECEIPTS_ENABLED is true."
        )

    private_key_value = settings.audit_receipts_private_key.get_secret_value()
    signer = AuditReceiptSigner.from_private_key_value(
        private_key_value,
        key_id=settings.audit_receipts_key_id,
    )

    return AuditReceiptMiddleware(
        signer,
        principal=settings.audit_receipts_principal,
        retention_mode=settings.audit_receipts_retention_mode,
        commitment_stage=settings.audit_receipts_commitment_stage,
        policy_hash=settings.audit_receipts_policy_hash,
        catalog_version=settings.audit_receipts_catalog_version,
        allowed_scope=settings.audit_receipts_allowed_scope,
        withheld_scope=settings.audit_receipts_withheld_scope,
    )
