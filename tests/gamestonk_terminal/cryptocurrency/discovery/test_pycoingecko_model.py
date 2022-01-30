# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.discovery import pycoingecko_model


@pytest.mark.vcr
def test_get_categories_keys(recorder):
    result = pycoingecko_model.get_categories_keys()
    result = list(result)
    recorder.capture(result)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        dict(top=251),
    ],
)
def test_get_coins(kwargs, recorder):
    result = pycoingecko_model.get_coins(**kwargs)
    recorder.capture(result)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "func, kwargs",
    [
        ("get_categories_keys", dict()),
        ("get_coins", dict(category="analytics")),
        ("get_coins", dict(top=251, category="analytics")),
        ("get_gainers_or_losers", dict()),
        ("get_trending_coins", dict()),
        ("get_coin_list", dict()),
        ("get_coins_for_given_exchange", dict()),
        ("get_mapping_matrix_for_exchange", dict(exchange_id="binance")),
    ],
)
def test_call_func(func, kwargs, recorder):
    result = getattr(pycoingecko_model, func)(**kwargs)

    recorder.capture(result)


@pytest.mark.vcr(record_mode="none")
def test_get_gainers_or_losers_value_error():
    with pytest.raises(ValueError) as _:
        pycoingecko_model.get_gainers_or_losers(period="WRONG_PERIOD")


@pytest.mark.vcr(record_mode="none")
def test_read_file_data_type_error():
    with pytest.raises(TypeError) as _:
        pycoingecko_model.read_file_data(file_name="MOCK_WRONG_FILE_NAME.EXTENSION")
