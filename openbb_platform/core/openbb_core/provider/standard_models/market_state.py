from datetime import datetime

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field


class MarketStateQueryParams(QueryParams):
    exchange: str = Field(description="Exchange MIC, acronym, or name to check market state for.")


class MarketStateData(Data):
    exchange: str = Field(description="Normalized exchange acronym.")
    mic: str = Field(description="ISO 10383 MIC code for the exchange.")
    status: str = Field(description="Raw market-state status returned by the provider.")
    is_open: bool = Field(description="Fail-closed market state. Only `OPEN` evaluates to `True`.")
    issued_at: datetime | None = Field(default=None, description="Receipt issue timestamp.")
    expires_at: datetime | None = Field(default=None, description="Receipt expiry timestamp.")
    ttl_seconds: int | None = Field(
        default=None,
        description="Receipt time-to-live in seconds when both timestamps are available.",
    )
    issuer: str | None = Field(default=None, description="Receipt issuer.")
    source: str | None = Field(default=None, description="Market-state source.")
    halt_detection: str | None = Field(default=None, description="Halt detection mode reported by the provider.")
    receipt_mode: str | None = Field(default=None, description="Receipt mode reported by the provider.")
    schema_version: str | None = Field(default=None, description="Provider receipt schema version.")
    public_key_id: str | None = Field(default=None, description="Identifier for the signing public key.")
    signature: str | None = Field(default=None, description="Signature attached to the receipt payload.")
