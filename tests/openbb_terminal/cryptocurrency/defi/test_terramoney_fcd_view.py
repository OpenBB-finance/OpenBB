# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency.defi import terramoney_fcd_view


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "func, kwargs",
    [
        (
            "display_account_staking_info",
            dict(
                address="terra1jvwelvs7rdk6j3mqdztq5tya99w8lxk6l9hcqg"  # pragma: allowlist secret
            ),
        ),
        ("display_validators", dict()),
        # ("display_gov_proposals", dict()), Can't reach node
        ("display_account_growth", dict()),
        # ("display_staking_ratio_history", dict()), Can't reach node
        ("display_staking_returns_history", dict()),
    ],
)
def test_call_func(func, kwargs, mocker):
    # MOCK EXPORT_DATA
    mocker.patch(
        target="openbb_terminal.cryptocurrency.defi.terramoney_fcd_view.export_data"
    )

    getattr(terramoney_fcd_view, func)(**kwargs)
