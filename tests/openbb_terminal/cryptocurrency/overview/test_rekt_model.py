import pytest

from openbb_terminal.cryptocurrency.overview import rekt_model


@pytest.mark.vcr
def test_get_crypto_hacks(recorder):
    df = rekt_model.get_crypto_hacks()
    recorder.capture(df)


@pytest.mark.vcr
def test_get_crypto_hack_slugs(recorder):
    slugs = rekt_model.get_crypto_hack_slugs()
    recorder.capture(slugs)


@pytest.mark.vcr
@pytest.mark.parametrize(
    "slug",
    [
        "bitmart-rekt",
        "polynetwork-rekt",
        "cryptocom-rekt",
    ],
)
def test_get_crypto_hack(slug, recorder):
    df = rekt_model.get_crypto_hack(slug)
    recorder.capture(df)
