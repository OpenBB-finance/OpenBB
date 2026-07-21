"""Audit receipt models for MCP tool calls."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class AuditReceipt(BaseModel):
    """Tamper-evident receipt for a single MCP tool call."""

    receipt_id: str = Field(description="Unique receipt identifier.")
    issued_at: str = Field(description="UTC timestamp when the receipt was issued.")
    tool_name: str = Field(description="MCP tool name that was called.")
    arguments_sha256: str = Field(description="SHA-256 digest of canonical arguments.")
    status: Literal["success", "error"] = Field(description="Tool call outcome.")
    policy_decision: str = Field(default="allow", description="Policy decision.")
    duration_ms: float = Field(description="Tool call duration in milliseconds.")
    principal: str = Field(description="Agent or user principal identifier.")
    public_key: str = Field(description="Base64-encoded Ed25519 public key.")
    signature: str = Field(description="Base64-encoded Ed25519 signature.")
    session_id: str | None = Field(default=None, description="MCP session id, if known.")
    request_id: str | None = Field(default=None, description="Request id, if known.")
    error_type: str | None = Field(default=None, description="Exception type on failure.")
    arguments: dict[str, Any] | None = Field(
        default=None,
        description="Canonical arguments, included only when explicitly configured.",
    )
