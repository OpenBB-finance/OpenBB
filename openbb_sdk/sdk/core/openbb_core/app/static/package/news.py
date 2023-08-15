### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import Annotated, List, Literal, Optional

import pydantic
from pydantic import validate_arguments

import openbb_core.app.model.command_context
import openbb_core.app.model.results.empty
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class CLASS_news(Container):
    @filter_call
    @validate_arguments
    def globalnews(
        self,
        page: Annotated[
            pydantic.types.NonNegativeInt,
            OpenBBCustomParameter(description="The page of the global news."),
        ] = 0,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Global News.

        Parameters
        ----------
        page : NonNegativeInt
            The page of the global news.
        chart : bool
            Wether to create a chart or not, by default False.
        provider : Optional[Literal['benzinga', 'fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'benzinga' if there is
            no default.
        pageSize : int
            The number of results to return per page. (provider: benzinga)
        displayOutput : Literal['headline', 'summary', 'full', 'all']
            The type of data to return. (provider: benzinga)
        date : Optional[datetime.datetime]
            The date of the news to retrieve. (provider: benzinga)
        dateFrom : Optional[datetime.datetime]
            The start date of the news to retrieve. (provider: benzinga)
        dateTo : Optional[datetime.datetime]
            The end date of the news to retrieve. (provider: benzinga)
        updatedSince : Optional[int]
            The number of seconds since the news was updated. (provider: benzinga)
        publishedSince : Optional[int]
            The number of seconds since the news was published. (provider: benzinga)
        sort : Optional[Literal['published_at', 'updated_at', 'title', 'author', 'channel', 'ticker', 'topic', 'content_type']]
            The order in which to sort the news. Options are: published_at, updated_at, title, author, channel, ticker, topic, content_type. (provider: benzinga)
        isin : Optional[str]
            The ISIN of the news to retrieve. (provider: benzinga)
        cusip : Optional[str]
            The CUSIP of the news to retrieve. (provider: benzinga)
        tickers : Optional[str]
            The tickers of the news to retrieve. (provider: benzinga)
        channels : Optional[str]
            The channels of the news to retrieve. (provider: benzinga)
        topics : Optional[str]
            The topics of the news to retrieve. (provider: benzinga)
        authors : Optional[str]
            The authors of the news to retrieve. (provider: benzinga)
        content_types : Optional[str]
            The content types of the news to retrieve. (provider: benzinga)

        Returns
        -------
        OBBject
            results : List[GlobalNews]
                Serializable results.
            provider : Optional[Literal['benzinga', 'fmp']]
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
            The images associated with the news. (provider: benzinga)
        channels : Optional[List[str]]
            The channels associated with the news. (provider: benzinga)
        stocks : Optional[List[str]]
            The stocks associated with the news. (provider: benzinga)
        tags : Optional[List[str]]
            The tags associated with the news. (provider: benzinga)
        teaser : Optional[str]
            The teaser of the news. (provider: benzinga)
        site : Optional[str]
            The site of the news. (provider: fmp)"""

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

        o = self._command_runner_session.run(
            "/news/globalnews",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def sectornews(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Sector news."""

        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/news/sectornews",
            **inputs,
        ).output

        return filter_output(o)
