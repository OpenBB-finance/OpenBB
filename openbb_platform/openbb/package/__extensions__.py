### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from openbb_core.app.static.container import Container
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
import openbb_provider
import pandas
import datetime
import pydantic
from pydantic import BaseModel
from inspect import Parameter
import typing
from typing import List, Dict, Union, Optional, Literal
from annotated_types import Ge, Le, Gt, Lt
import typing_extensions
from openbb_core.app.utils import df_to_basemodel
from openbb_core.app.static.decorators import validate

from openbb_core.app.static.filters import filter_inputs

from openbb_provider.abstract.data import Data


class Extensions(Container):
    # fmt: off
    """
Routers:
    /crypto
    /econometrics
    /economy
    /etf
    /fixedincome
    /forex
    /futures
    /news
    /qa
    /regulators
    /stocks
    /ta

Extensions:
    - crypto@0.1.0a4
    - econometrics@0.1.0a4
    - economy@0.1.0a4
    - etf@0.1.0a3
    - fixedincome@0.1.0a4
    - forex@0.1.0a4
    - futures@0.1.0a4
    - news@0.1.0a4
    - openbb_charting@0.1.0a4
    - qa@0.1.0a4
    - regulators@0.1.0a4
    - stocks@0.1.0a4
    - ta@0.1.0a4

    - alpha_vantage@0.1.0a4
    - benzinga@0.1.0a4
    - biztoc@0.1.0a4
    - cboe@0.1.0a4
    - fmp@0.1.0a4
    - fred@0.1.0a4
    - intrinio@0.1.0a4
    - nasdaq@0.1.0a4
    - oecd@0.1.0a4
    - polygon@0.1.0a4
    - quandl@0.1.0a4
    - sec@0.1.0a4
    - tradingeconomics@0.1.0a4
    - wsj@0.1.0a4
    - yfinance@0.1.0a4    """
    # fmt: on
    def __repr__(self) -> str:
        return self.__doc__ or ""

    @property
    def crypto(self):  # route = "/crypto"
        from . import crypto

        return crypto.ROUTER_crypto(command_runner=self._command_runner)

    @property
    def econometrics(self):  # route = "/econometrics"
        from . import econometrics

        return econometrics.ROUTER_econometrics(command_runner=self._command_runner)

    @property
    def economy(self):  # route = "/economy"
        from . import economy

        return economy.ROUTER_economy(command_runner=self._command_runner)

    @property
    def etf(self):  # route = "/etf"
        from . import etf

        return etf.ROUTER_etf(command_runner=self._command_runner)

    @property
    def fixedincome(self):  # route = "/fixedincome"
        from . import fixedincome

        return fixedincome.ROUTER_fixedincome(command_runner=self._command_runner)

    @property
    def forex(self):  # route = "/forex"
        from . import forex

        return forex.ROUTER_forex(command_runner=self._command_runner)

    @property
    def futures(self):  # route = "/futures"
        from . import futures

        return futures.ROUTER_futures(command_runner=self._command_runner)

    @property
    def news(self):  # route = "/news"
        from . import news

        return news.ROUTER_news(command_runner=self._command_runner)

    @property
    def qa(self):  # route = "/qa"
        from . import qa

        return qa.ROUTER_qa(command_runner=self._command_runner)

    @property
    def regulators(self):  # route = "/regulators"
        from . import regulators

        return regulators.ROUTER_regulators(command_runner=self._command_runner)

    @property
    def stocks(self):  # route = "/stocks"
        from . import stocks

        return stocks.ROUTER_stocks(command_runner=self._command_runner)

    @property
    def ta(self):  # route = "/ta"
        from . import ta

        return ta.ROUTER_ta(command_runner=self._command_runner)
