### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import typing
from typing import Literal, Optional

import pydantic
from pydantic import validate_arguments

import openbb_core.app.model.command_context
import openbb_core.app.model.results.empty
from openbb_core.app.model.command_output import CommandOutput
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class CLASS_news(Container):
    @filter_call
    @validate_arguments
    def globalnews(
        self,
        page: pydantic.types.NonNegativeInt = 0,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Global News.

        Available providers: benzinga, fmp

        Standard
        ========

        Parameter
        ---------
        page : NonNegativeInt
            The page of the global news to be retrieved.


        Returns
        -------
        date : datetime
            The published date of the news.
        title : str
            The title of the news.
        image : Optional[str]
            The image URL of the news.
        text : str
            The text/body of the news.
        url : str
            The URL of the news.

        benzinga
        ========

        Source: https://docs.benzinga.io/benzinga/newsfeed-v2.html

        Parameter
        ---------
        pageSize : int (default: 15)
            The number of results to return per page.
        displayOutput : str (default: "headline")
            The type of data to return. Options are "headline", "summary", "full", "all".
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
        sort : Optional[str]
            The order in which to sort the news. Options are:
            "published_at", "updated_at", "title", "author", "channel", "ticker", "topic", "content_type".
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


        Returns
        -------
        Documentation not available.


        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/general-news-api/

        Parameter
        ---------
        All fields are standardized.


        Returns
        -------
        Documentation not available.
        """
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Sector news."""
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/news/sectornews",
            **inputs,
        ).output

        return filter_output(o)
