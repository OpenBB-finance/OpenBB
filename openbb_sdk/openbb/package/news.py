### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Optional

import pydantic
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs
from pydantic import validate_arguments
from typing_extensions import Annotated


class ROUTER_news(Container):
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
        display : Literal['headline', 'abstract', 'full']
            Specify headline only (headline), headline + teaser (abstract), or headline + full body (full). (provider: benzinga)
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
        sort : Optional[Literal['id', 'created', 'updated']]
            Key to sort the news by. (provider: benzinga)
        order : Optional[Literal['asc', 'desc']]
            Order to sort the news by. (provider: benzinga)
        isin : Optional[str]
            The ISIN of the news to retrieve. (provider: benzinga)
        cusip : Optional[str]
            The CUSIP of the news to retrieve. (provider: benzinga)
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
        image : Optional[str]
            Image URL of the news.
        text : Optional[str]
            Text/body of the news.
        url : Optional[str]
            URL of the news.
        id : Optional[str]
            ID of the news. (provider: benzinga); Article ID. (provider: intrinio)
        author : Optional[str]
            Author of the news. (provider: benzinga)
        updated : Optional[datetime]
            Updated date of the news. (provider: benzinga)
        teaser : Optional[str]
            Teaser of the news. (provider: benzinga)
        channels : Optional[str]
            Channels associated with the news. (provider: benzinga)
        stocks : Optional[str]
            Stocks associated with the news. (provider: benzinga)
        tags : Optional[str]
            Tags associated with the news. (provider: benzinga)
        site : Optional[str]
            Site of the news. (provider: fmp)
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
