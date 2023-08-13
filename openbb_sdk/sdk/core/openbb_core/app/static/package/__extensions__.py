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
from typing import List, Dict, Union, Optional, Literal, Annotated
from openbb_core.app.utils import df_to_basemodel
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class Extensions(Container):
    @property
    def forex(self):  # route = "/forex"
        from openbb_core.app.static.package import forex

        return forex.CLASS_forex(command_runner_session=self._command_runner_session)

    @property
    def qa(self):  # route = "/qa"
        from openbb_core.app.static.package import qa

        return qa.CLASS_qa(command_runner_session=self._command_runner_session)

    @property
    def crypto(self):  # route = "/crypto"
        from openbb_core.app.static.package import crypto

        return crypto.CLASS_crypto(command_runner_session=self._command_runner_session)

    @property
    def news(self):  # route = "/news"
        from openbb_core.app.static.package import news

        return news.CLASS_news(command_runner_session=self._command_runner_session)

    @property
    def futures(self):  # route = "/futures"
        from openbb_core.app.static.package import futures

        return futures.CLASS_futures(
            command_runner_session=self._command_runner_session
        )

    @property
    def stocks(self):  # route = "/stocks"
        from openbb_core.app.static.package import stocks

        return stocks.CLASS_stocks(command_runner_session=self._command_runner_session)

    @property
    def ta(self):  # route = "/ta"
        from openbb_core.app.static.package import ta

        return ta.CLASS_ta(command_runner_session=self._command_runner_session)

    @property
    def economy(self):  # route = "/economy"
        from openbb_core.app.static.package import economy

        return economy.CLASS_economy(
            command_runner_session=self._command_runner_session
        )

    @property
    def fixedincome(self):  # route = "/fixedincome"
        from openbb_core.app.static.package import fixedincome

        return fixedincome.CLASS_fixedincome(
            command_runner_session=self._command_runner_session
        )
