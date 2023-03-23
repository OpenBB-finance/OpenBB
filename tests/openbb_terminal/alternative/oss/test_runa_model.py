# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.alternative.oss import runa_model


@pytest.mark.record_http
def test_get_startups(record):
    df = runa_model.get_startups()
    record.add_verify(obj=df)
    assert not df.empty
