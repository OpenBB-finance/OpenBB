import os
import pytest

from gamestonk_terminal.custom import custom_model


@pytest.mark.vcr()
@pytest.mark.parametrize(
    "file",
    [
        "test.csv",
    ],
)
def test_test_load(recorder, file):
    result_df = custom_model.load(os.path.join("custom_imports", file))
    assert not result_df.empty
    recorder.capture(result_df)


@pytest.mark.vcr()
def test_test_empty_load(recorder):
    result_df = custom_model.load("")
    assert result_df.empty
    recorder.capture(result_df)
