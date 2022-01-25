# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.economy import cnn_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_get_feargreed_report(mocker):
    # MOCK GTFF
    mocker.patch.object(target=cnn_view.gtff, attribute="USE_ION", new=True)

    # MOCK IMSHOW
    mocker.patch(target="matplotlib.pyplot.imshow")

    # MOCK PLOT_AUTOSCALE
    mocker.patch(
        target="gamestonk_terminal.economy.cnn_view.plot_autoscale",
        return_value=(8.0, 5.0),
    )

    # MOCK PLOT_DPI
    mocker.patch(
        target="gamestonk_terminal.economy.cnn_view.PLOT_DPI",
        new=100,
    )

    # MOCK EXPORT_DATA
    mocker.patch(target="gamestonk_terminal.economy.cnn_view.export_data")

    cnn_view.fear_and_greed_index(indicator="sps", export="")
