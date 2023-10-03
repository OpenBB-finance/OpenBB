"""Test qa extension."""
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
        ({"data": "", "target": "", "return": ""}),
    ],
)
@pytest.mark.integration
def test_qa_normality(params, obb):
    result = obb.qa.normality(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": "", "target": "", "return": ""}),
    ],
)
@pytest.mark.integration
def test_qa_capm(params, obb):
    result = obb.qa.capm(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "",
                "threshold_start": "",
                "threshold_end": "",
                "return": "",
            }
        ),
    ],
)
@pytest.mark.integration
def test_qa_om(params, obb):
    result = obb.qa.om(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": "", "target": "", "window": "", "return": ""}),
    ],
)
@pytest.mark.integration
def test_qa_kurtosis(params, obb):
    result = obb.qa.kurtosis(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": "", "target": "", "fuller_reg": "", "kpss_reg": "", "return": ""}),
    ],
)
@pytest.mark.integration
def test_qa_unitroot(params, obb):
    result = obb.qa.unitroot(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": "", "target": "", "rfr": "", "window": "", "return": ""}),
    ],
)
@pytest.mark.integration
def test_qa_sh(params, obb):
    result = obb.qa.sh(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        (
            {
                "data": "",
                "target": "",
                "target_return": "",
                "window": "",
                "adjusted": "",
                "return": "",
            }
        ),
    ],
)
@pytest.mark.integration
def test_qa_so(params, obb):
    result = obb.qa.so(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": "", "target": "", "window": "", "return": ""}),
    ],
)
@pytest.mark.integration
def test_qa_skew(params, obb):
    result = obb.qa.skew(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": "", "target": "", "window": "", "quantile_pct": "", "return": ""}),
    ],
)
@pytest.mark.integration
def test_qa_quantile(params, obb):
    result = obb.qa.quantile(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0


@pytest.mark.parametrize(
    "params",
    [
        ({"data": "", "target": "", "return": ""}),
    ],
)
@pytest.mark.integration
def test_qa_summary(params, obb):
    result = obb.qa.summary(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
