### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from openbb_core.app.static.container import Container
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
import openbb_provider
import pandas
import datetime
import pydantic
from pydantic import validate_arguments, BaseModel
from inspect import Parameter
import typing
from typing import List, Dict, Union, Optional, Literal
from typing_extensions import Annotated
from openbb_core.app.utils import df_to_basemodel
from openbb_core.app.static.filters import filter_inputs


class Extensions(Container):
    """
/crypto
/economy
/fixedincome
/forex
/futures
/news
/qa
/stocks
/ta
    """
    def __repr__(self) -> str:
        return self.__doc__ or ""

    @property
    def crypto(self):  # route = "/crypto"
        from . import crypto
        return crypto.CLASS_crypto(command_runner=self._command_runner)

    @property
    def economy(self):  # route = "/economy"
        from . import economy
        return economy.CLASS_economy(command_runner=self._command_runner)

    @property
    def fixedincome(self):  # route = "/fixedincome"
        from . import fixedincome
        return fixedincome.CLASS_fixedincome(command_runner=self._command_runner)

    @property
    def forex(self):  # route = "/forex"
        from . import forex
        return forex.CLASS_forex(command_runner=self._command_runner)

    @property
    def futures(self):  # route = "/futures"
        from . import futures
        return futures.CLASS_futures(command_runner=self._command_runner)

    @property
    def news(self):  # route = "/news"
        from . import news
        return news.CLASS_news(command_runner=self._command_runner)

    @property
    def qa(self):  # route = "/qa"
        from . import qa
        return qa.CLASS_qa(command_runner=self._command_runner)

    @property
    def stocks(self):  # route = "/stocks"
        from . import stocks
        return stocks.CLASS_stocks(command_runner=self._command_runner)

    @property
    def ta(self):  # route = "/ta"
        from . import ta
        return ta.CLASS_ta(command_runner=self._command_runner)
