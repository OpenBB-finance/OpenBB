"""Test econometrics extension."""
import pytest
from openbb_core.app.model.obbject import OBBject

@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""

    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb
    

@pytest.mark.parametrize(
    "params",
    [
        ({'data': '', 'return': ''}),

    ],
)
@pytest.mark.integration
def test_econometrics_corr(params, obb):
    result = obb.econometrics.corr(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({'data': '', 'y_column': '', 'x_columns': '', 'return': ''}),

    ],
)
@pytest.mark.integration
def test_econometrics_ols(params, obb):
    result = obb.econometrics.ols(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({'data': '', 'y_column': '', 'x_columns': '', 'return': ''}),

    ],
)
@pytest.mark.integration
def test_econometrics_ols_summary(params, obb):
    result = obb.econometrics.ols_summary(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({'data': '', 'y_column': '', 'x_columns': '', 'return': ''}),

    ],
)
@pytest.mark.integration
def test_econometrics_dwat(params, obb):
    result = obb.econometrics.dwat(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({'data': '', 'y_column': '', 'x_columns': '', 'lags': '', 'return': ''}),

    ],
)
@pytest.mark.integration
def test_econometrics_bgot(params, obb):
    result = obb.econometrics.bgot(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({'data': '', 'columns': '', 'return': ''}),

    ],
)
@pytest.mark.integration
def test_econometrics_coint(params, obb):
    result = obb.econometrics.coint(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({'data': '', 'y_column': '', 'x_column': '', 'lag': '', 'return': ''}),

    ],
)
@pytest.mark.integration
def test_econometrics_granger(params, obb):
    result = obb.econometrics.granger(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({'data': '', 'column': '', 'regression': '', 'return': ''}),

    ],
)
@pytest.mark.integration
def test_econometrics_unitroot(params, obb):
    result = obb.econometrics.unitroot(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({'data': '', 'y_column': '', 'x_columns': '', 'return': ''}),

    ],
)
@pytest.mark.integration
def test_econometrics_panelre(params, obb):
    result = obb.econometrics.panelre(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({'data': '', 'y_column': '', 'x_columns': '', 'return': ''}),

    ],
)
@pytest.mark.integration
def test_econometrics_panelbols(params, obb):
    result = obb.econometrics.panelbols(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({'data': '', 'y_column': '', 'x_columns': '', 'return': ''}),

    ],
)
@pytest.mark.integration
def test_econometrics_panelpols(params, obb):
    result = obb.econometrics.panelpols(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({'data': '', 'y_column': '', 'x_columns': '', 'return': ''}),

    ],
)
@pytest.mark.integration
def test_econometrics_panelols(params, obb):
    result = obb.econometrics.panelols(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({'data': '', 'y_column': '', 'x_columns': '', 'return': ''}),

    ],
)
@pytest.mark.integration
def test_econometrics_panelfd(params, obb):
    result = obb.econometrics.panelfd(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({'data': '', 'y_column': '', 'x_columns': '', 'return': ''}),

    ],
)
@pytest.mark.integration
def test_econometrics_panelfmac(params, obb):
    result = obb.econometrics.panelfmac(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
