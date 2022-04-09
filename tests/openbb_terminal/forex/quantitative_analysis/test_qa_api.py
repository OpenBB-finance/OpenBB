# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from openbb_terminal.helper_classes import ModelsNamespace as _models
from openbb_terminal.forex.quantitative_analysis import qa_api


def test_models():
    assert isinstance(qa_api.models, _models)
