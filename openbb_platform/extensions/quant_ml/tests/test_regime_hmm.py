"""HMM regime classifier tests."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from openbb_quant_ml.service.macro_regime_hmm import fit_hmm_regime


def test_fit_hmm_regime_returns_state_sequence_or_skips() -> None:
    idx = pd.date_range("2023-01-01", periods=80, freq="W")
    rng = np.random.default_rng(42)
    frame = pd.DataFrame(
        {
            "risk_on_score": 50 + rng.normal(0, 8, len(idx)),
            "inflation_score": 50 + rng.normal(0, 6, len(idx)),
            "growth_score": 50 + rng.normal(0, 7, len(idx)),
            "liquidity_score": 50 + rng.normal(0, 5, len(idx)),
            "credit_stress_score": 50 + rng.normal(0, 9, len(idx)),
        },
        index=idx,
    )
    out = fit_hmm_regime(frame, n_states=4)
    if out is None:
        pytest.skip("hmmlearn is not installed")
    assert len(out["states"]) == len(out["index"])
    assert len(out["state_meta"]) == 4
