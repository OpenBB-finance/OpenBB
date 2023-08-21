### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Union

import pydantic
import typing_extensions
from pydantic import validate_arguments

import openbb_core.app.model.command_context
import openbb_core.app.model.results.empty
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs


class CLASS_news(Container):
    @validate_arguments
    def globalnews(
        self,
        page: typing_extensions.Annotated[
            pydantic.types.NonNegativeInt,
            OpenBBCustomParameter(description="The page of the global news."),
        ] = 0,
        chart: bool = False,
        provider: Union[Literal["benzinga", "fmp"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """Global News.

        Parameters
        ----------
        page : NonNegativeInt
            The page of the global news.
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Union[Literal['benzinga', 'fmp'], NoneType]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'benzinga' if there is
            no default.
        pageSize : int
            Number of results to return per page. (provider: benzinga)
        displayOutput : Literal['headline', 'summary', 'full', 'all']
            Type of data to return. (provider: benzinga)
        date : Union[datetime.datetime, NoneType]
            Date of the news to retrieve. (provider: benzinga)
        dateFrom : Union[datetime.datetime, NoneType]
            Start date of the news to retrieve. (provider: benzinga)
        dateTo : Union[datetime.datetime, NoneType]
            End date of the news to retrieve. (provider: benzinga)
        updatedSince : Union[int, NoneType]
            Number of seconds since the news was updated. (provider: benzinga)
        publishedSince : Union[int, NoneType]
            Number of seconds since the news was published. (provider: benzinga)
        sort : Union[Literal['published_at', 'updated_at', 'title', 'author', 'channel', 'ticker', 'topic', 'content_type'], NoneType]
            Order in which to sort the news.  (provider: benzinga)
        isin : Union[str, NoneType]
            The ISIN of the news to retrieve. (provider: benzinga)
        cusip : Union[str, NoneType]
            The CUSIP of the news to retrieve. (provider: benzinga)
        tickers : Union[str, NoneType]
            Tickers of the news to retrieve. (provider: benzinga)
        channels : Union[str, NoneType]
            Channels of the news to retrieve. (provider: benzinga)
        topics : Union[str, NoneType]
            Topics of the news to retrieve. (provider: benzinga)
        authors : Union[str, NoneType]
            Authors of the news to retrieve. (provider: benzinga)
        content_types : Union[str, NoneType]
            Content types of the news to retrieve. (provider: benzinga)

        Returns
        -------
        OBBject
            results : List[GlobalNews]
                Serializable results.
            provider : Union[Literal['benzinga', 'fmp'], NoneType]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            error : Optional[Error]
                Caught exceptions.
            chart : Optional[Chart]
                Chart object.

        GlobalNews
        ----------
        date : Optional[datetime]
            The published date of the news.
        title : Optional[str]
            The title of the news.
        text : Optional[str]
            The text/body of the news.
        url : Optional[str]
            The URL of the news.
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
