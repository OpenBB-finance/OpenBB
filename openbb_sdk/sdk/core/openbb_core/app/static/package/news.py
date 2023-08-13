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


        openbb
        ======

        Parameters
        ----------
        provider: Literal[benzinga, fmp]
            The provider to use for the query.
        page : NonNegativeInt
            The page of the global news.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        GlobalNews
        ----------
        date : datetime
            The published date of the news.
        title : str
            The title of the news.
        text : Optional[str]
            The text/body of the news.
        url : str
            The URL of the news.

        benzinga
        ========

        Parameters
        ----------
        pageSize : int
            The number of results to return per page.
        displayOutput : Literal['headline', 'summary', 'full', 'all']
            The type of data to return.
        date : Optional[datetime]
            The date of the news to retrieve.
        dateFrom : Optional[datetime]
            The start date of the news to retrieve.
        dateTo : Optional[datetime]
            The end date of the news to retrieve.
        updatedSince : Optional[int]
            The number of seconds since the news was updated.
        publishedSince : Optional[int]
            The number of seconds since the news was published.
        sort : Optional[Literal['published_at', 'updated_at', 'title', 'author', 'channel', 'ticker', 'topic', 'content_type']]
            The order in which to sort the news. Options are: published_at, updated_at, title, author, channel, ticker, topic, content_type.
        isin : Optional[str]
            The ISIN of the news to retrieve.
        cusip : Optional[str]
            The CUSIP of the news to retrieve.
        tickers : Optional[str]
            The tickers of the news to retrieve.
        channels : Optional[str]
            The channels of the news to retrieve.
        topics : Optional[str]
            The topics of the news to retrieve.
        authors : Optional[str]
            The authors of the news to retrieve.
        content_types : Optional[str]
            The content types of the news to retrieve.


        GlobalNews
        ----------
        images : List[BenzingaImage]
            The images associated with the news.
        channels : Optional[List[str]]
            The channels associated with the news.
        stocks : Optional[List[str]]
            The stocks associated with the news.
        tags : Optional[List[str]]
            The tags associated with the news.
        teaser : Optional[str]
            The teaser of the news.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        GlobalNews
        ----------
        site : str
            The site of the news."""  # noqa: E501
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
        """Sector news."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/news/sectornews",
            **inputs,
        ).output

        return filter_output(o)
