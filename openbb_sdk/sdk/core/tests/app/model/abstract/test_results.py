from openbb_core.app.model.abstract.results import Results
from pydantic import BaseModel


def test_results_model():
    res = Results()

    assert isinstance(res, BaseModel)
