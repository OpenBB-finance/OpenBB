### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Optional

import pydantic
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs
from pydantic import validate_arguments
from typing_extensions import Annotated


class CLASS_news(Container):
    """/news
    globalnews
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate_arguments
    def globalnews(
        self,
        limit: Annotated[
            pydantic.types.NonNegativeInt,
            OpenBBCustomParameter(description="Number of articles to return."),
        ] = 20,
        provider: Optional[Literal["benzinga", "fmp", "intrinio"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Global News.

        Parameters
        ----------
        limit : NonNegativeInt
            Number of articles to return.
        provider : Optional[Literal['benzinga', 'fmp', 'intrinio']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'benzinga' if there is
            no default.
        display : Literal['headline', 'summary', 'full', 'all']
            Type of segments to return. (provider: benzinga)
        date : Optional[str]
            Date of the news to retrieve. (provider: benzinga)
        start_date : Optional[str]
            Start date of the news to retrieve. (provider: benzinga)
        end_date : Optional[str]
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
            provider : Optional[Literal['benzinga', 'fmp', 'intrinio']]
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
            Site of the news. (provider: fmp)
        id : Optional[str]
            Article ID. (provider: intrinio)
        company : Optional[Mapping[str, Any]]
            Company details related to the news article. (provider: intrinio)"""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "limit": limit,
            },
            extra_params=kwargs,
        )

        return self._command_runner.run(
            "/news/globalnews",
            **inputs,
        )
