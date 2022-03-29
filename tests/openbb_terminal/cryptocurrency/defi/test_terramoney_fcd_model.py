# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.cryptocurrency.defi import terramoney_fcd_model


@pytest.mark.vcr
def test_get_staking_account_info(recorder):
    result_tuple = terramoney_fcd_model.get_staking_account_info(
        address="terra1jvwelvs7rdk6j3mqdztq5tya99w8lxk6l9hcqg",
    )
    recorder.capture_list(result_tuple)


@pytest.mark.vcr
def test_get_validators(recorder):
    df = terramoney_fcd_model.get_validators()
    recorder.capture_list(df)


@pytest.mark.vcr
def test_get_proposals(recorder):
    df = terramoney_fcd_model.get_proposals(status="Voting")
    recorder.capture_list(df)


@pytest.mark.vcr
def test_get_account_growth(recorder):
    df = terramoney_fcd_model.get_account_growth(cumulative=True)
    recorder.capture_list(df)


@pytest.mark.vcr
def test_get_staking_ratio_history(recorder):
    df = terramoney_fcd_model.get_staking_ratio_history()
    recorder.capture_list(df)


@pytest.mark.vcr
def test_get_staking_returns_history(recorder):
    df = terramoney_fcd_model.get_staking_returns_history()
    recorder.capture_list(df)
