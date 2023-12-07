from openbb_core.app.model.abstract.results import Results
from pydantic import BaseModel


class MockResults(Results):
    pass


def test_results_model():
    res = MockResults()

    assert isinstance(res, BaseModel)
