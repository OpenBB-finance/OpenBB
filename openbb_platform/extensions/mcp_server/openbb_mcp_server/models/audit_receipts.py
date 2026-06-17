"""Audit receipt models for MCP tool calls."""

from typing import Any, Literal

from pydantic import BaseModel, Field

RetentionMode = Literal[
    "raw_retained",
    "redacted_only",
    "hash_only",
    "unavailable",
]
CommitmentStage = Literal[
    "pre_redaction",
    "post_redaction",
    "post_normalization",
    "model_facing",
]
PolicyDecision = Literal["allow", "deny"]


class AuditReceiptPayload(BaseModel):
    """Canonical payload covered by the audit receipt signature."""

    receipt_version: str = Field(default="openbb.mcp.audit_receipt.v1")
    receipt_id: str
    tool_name: str
    principal: str
    timestamp: str
    decision: PolicyDecision
    request_hash: str
    normalized_view_hash: str | None = None
    provider_payload_hash: str | None = None
    model_input_hash: str | None = None
    retention_mode: RetentionMode = "hash_only"
    commitment_stage: CommitmentStage = "post_normalization"
    policy_hash: str | None = None
    catalog_version: str | None = None
    allowed_scope: list[str] | None = None
    withheld_scope: list[dict[str, Any]] | None = None


class SignedAuditReceipt(BaseModel):
    """Signed audit receipt returned in MCP tool result metadata."""

    payload: AuditReceiptPayload
    payload_hash: str
    signature: str
    signing_algorithm: Literal["ed25519"] = "ed25519"
    key_id: str | None = None
    public_key: str
