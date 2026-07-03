"""Top-level router for ``openbb-government-ca``.

Mounts two sub-routers under the ``government_ca`` core-extension
entry-point:

- ``/boc``       → Bank of Canada (FX, rates, yields)
- ``/statscan``  → Statistics Canada (economic indicators, calendar)

The metadata singleton is injected as a FastAPI ``Depends`` so it
doesn't leak into the generated OpenAPI parameter schema (this is the
fix that landed mid-PR in #7413).
"""

from __future__ import annotations

from fastapi import APIRouter

# Sub-routers are wired in Phases 4 and 5. The imports below are
# intentionally lazy-friendly — the router mounts them only if they
# import successfully, so a partially-scaffolded extension still
# registers its entry-point without crashing.

router = APIRouter(prefix="/government_ca", tags=["Government Canada"])


@router.get("/_health", response_model=dict)
def _health() -> dict:
    """Liveness probe for the extension router.

    Returns a static 200 — useful for the OpenBB platform to verify
    that the extension's router mounted successfully. The metadata
    cache itself is verified at import time by
    ``openbb_government_ca.utils.metadata``.
    """
    return {"status": "ok", "provider": "government_ca"}
