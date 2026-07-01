from __future__ import annotations

from typing import Any

import pytest


@pytest.fixture(autouse=True)
def _ecb_test_env(monkeypatch) -> Any:
    from openbb_ecb.utils.metadata import EcbMetadata

    monkeypatch.setenv("OPENBB_ECB_NO_CACHE", "1")
    EcbMetadata._reset()
    yield
    EcbMetadata._reset()
