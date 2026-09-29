import openbb_core.provider.utils.helpers as core_helpers
import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_ecb.models.currency_reference_rates import (
    ECBCurrencyReferenceRatesFetcher as Fetcher,
)

_XML = (
    b'<gesmes:Envelope xmlns:gesmes="http://www.gesmes.org/xml/2002-08-01" '
    b'xmlns="http://www.ecb.int/vocabulary/2002-08-01/eurofxref">'
    b'<Cube><Cube time="2024-01-02">'
    b'<Cube currency="USD" rate="1.08"/><Cube currency="JPY" rate="160"/>'
    b"</Cube></Cube></gesmes:Envelope>"
)


class _FakeResp:
    def __init__(self, status_code=200, content=b""):
        self.status_code = status_code
        self.content = content


def test_extract_and_transform(monkeypatch):
    monkeypatch.setattr(
        core_helpers, "make_request", lambda *a, **k: _FakeResp(200, _XML)
    )
    query = Fetcher.transform_query({})
    raw = Fetcher.extract_data(query, None)
    assert raw == {"time": "2024-01-02", "rates": {"USD": "1.08", "JPY": "160"}}
    record = Fetcher.transform_data(query, raw)
    assert str(record.date) == "2024-01-02"
    assert record.EUR == 1
    assert record.USD == 1.08


def test_extract_non_200_raises(monkeypatch):
    monkeypatch.setattr(core_helpers, "make_request", lambda *a, **k: _FakeResp(503))
    with pytest.raises(OpenBBError):
        Fetcher.extract_data(Fetcher.transform_query({}), None)
