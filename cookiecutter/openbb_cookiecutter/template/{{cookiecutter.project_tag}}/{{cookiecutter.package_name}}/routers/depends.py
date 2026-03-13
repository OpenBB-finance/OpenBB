"""Router dependency injections."""

# pylint: disable=R0903

from typing import Annotated

import requests
from fastapi import Depends
from openbb_core.provider.utils.helpers import get_requests_session

Session = Annotated[requests.Session, Depends(get_requests_session)]
