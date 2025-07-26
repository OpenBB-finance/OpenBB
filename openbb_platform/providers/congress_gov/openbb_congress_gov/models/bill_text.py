"""Congress Gov Bills Text Model."""

from typing import Annotated, Optional
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import ConfigDict, Field, model_validator
from openbb_platform.providers.congress_gov.openbb_congress_gov.utils.constants import (
    BillType,
    BillTypes,
    base_url,
)
