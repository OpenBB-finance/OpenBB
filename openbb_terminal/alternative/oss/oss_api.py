"""OSS API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from openbb_terminal.alternative.oss.github_view import display_repo_summary as summary
from openbb_terminal.alternative.oss.github_view import display_star_history as history
from openbb_terminal.alternative.oss.github_view import display_top_repos as top
from openbb_terminal.alternative.oss.runa_view import display_rossindex as ross


# Models
models = _models(os.path.abspath(os.path.dirname(__file__)))
