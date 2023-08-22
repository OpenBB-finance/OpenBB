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
import typing_extensions
from openbb_core.app.utils import df_to_basemodel
from openbb_core.app.static.filters import filter_inputs

import openbb_core.app.model.command_context
import openbb_core.app.model.results.empty
import types
import typing


class CLASS_news(Container):
    """/news
    globalnews
    sectornews
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate_arguments
    def globalnews(
        self,
        page: Annotated[
            pydantic.types.NonNegativeInt,
            OpenBBCustomParameter(description="Page of the global news."),
        ] = 0,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Global News.

        Parameters
        ----------
        page : NonNegativeInt
            Page of the global news.
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Optional[Literal['benzinga', 'fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'benzinga' if there is
            no default.
        page_size : int
            Number of results to return per page. (provider: benzinga)
        display_output : Literal['headline', 'summary', 'full', 'all']
            Type of data to return. (provider: benzinga)
        date : Optional[datetime.datetime]
            Date of the news to retrieve. (provider: benzinga)
        date_from : Optional[datetime.datetime]
            Start date of the news to retrieve. (provider: benzinga)
        date_to : Optional[datetime.datetime]
            End date of the news to retrieve. (provider: benzinga)
        updated_since : Optional[int]
            Number of seconds since the news was updated. (provider: benzinga)
        published_since : Optional[int]
            Number of seconds since the news was published. (provider: benzinga)
        sort : Optional[Literal['published_at', 'updated_at', 'title', 'author', 'channel', 'ticker', 'topic', 'content_type']]
            Order in which to sort the news.  (provider: benzinga)
        isin : Optional[str]
            The ISIN of the news to retrieve. (provider: benzinga)
        cusip : Optional[str]
            The CUSIP of the news to retrieve. (provider: benzinga)
        tickers : Optional[str]
            Tickers of the news to retrieve. (provider: benzinga)
        channels : Optional[str]
            Channels of the news to retrieve. (provider: benzinga)
        topics : Optional[str]
            Topics of the news to retrieve. (provider: benzinga)
        authors : Optional[str]
            Authors of the news to retrieve. (provider: benzinga)
        content_types : Optional[str]
            Content types of the news to retrieve. (provider: benzinga)

        Returns
        -------
        OBBject
            results : List[GlobalNews]
                Serializable results.
            provider : Optional[Literal['benzinga', 'fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        GlobalNews
        ----------
        date : Optional[datetime]
            Published date of the news.
        title : Optional[str]
            Title of the news.
        text : Optional[str]
            Text/body of the news.
        url : Optional[str]
            URL of the news.
        images : Optional[List[BenzingaImage]]
            Images associated with the news. (provider: benzinga)
        channels : Optional[List[str]]
            Channels associated with the news. (provider: benzinga)
        stocks : Optional[List[str]]
            Stocks associated with the news. (provider: benzinga)
        tags : Optional[List[str]]
            Tags associated with the news. (provider: benzinga)
        teaser : Optional[str]
            Teaser of the news. (provider: benzinga)
        site : Optional[str]
            Site of the news. (provider: fmp)"""

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "page": page,
            },
            extra_params=kwargs,
            chart=chart,
        )

        return self._command_runner.run(
            "/news/globalnews",
            **inputs,
        )

    @validate_arguments
    def sectornews(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Sector news."""

        inputs = filter_inputs(
            chart=chart,
        )

        return self._command_runner.run(
            "/news/sectornews",
            **inputs,
        )
