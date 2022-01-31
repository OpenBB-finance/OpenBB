# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY

# IMPORTATION INTERNAL
from gamestonk_terminal.helper_classes import ModelsNamespace as _models
from gamestonk_terminal.cryptocurrency.due_diligence import due_diligence_api


def test_models():
    assert isinstance(due_diligence_api.models, _models)
