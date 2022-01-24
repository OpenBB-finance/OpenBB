# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import matplotlib.pyplot as plt
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.economy import cnn_model


@pytest.mark.default_cassette("test_get_feargreed_report")
@pytest.mark.vcr
@pytest.mark.parametrize(
    "indicator",
    [
        None,
        "index",
        "sps",
    ],
)
def test_get_feargreed_report(indicator, mocker, recorder):
    # MOCK IMSHOW
    mocker.patch(target="matplotlib.pyplot.imshow")

    fig = plt.figure(figsize=(8.0, 5.0), dpi=100)

    report, im = cnn_model.get_feargreed_report(indicator=indicator, fig=fig)

    assert report
    assert isinstance(report, str)
    assert im

    recorder.capture(report)
