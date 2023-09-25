### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Union

import pydantic
import typing_extensions
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs
from pydantic import validate_arguments


class ROUTER_news(Container):
    """/news
    globalnews
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate_arguments
    def globalnews(
        self,
        limit: typing_extensions.Annotated[
            pydantic.types.NonNegativeInt,
            OpenBBCustomParameter(description="Number of articles to return."),
        ] = 20,
        provider: Union[Literal["benzinga", "fmp", "intrinio"], None] = None,
        **kwargs
    ) -> OBBject[List]:
        """Global News.

        Parameters
        ----------
        limit : NonNegativeInt
            Number of articles to return.
        provider : Union[Literal['benzinga', 'fmp', 'intrinio'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'benzinga' if there is
            no default.
        display : Literal['headline', 'abstract', 'full']
            Specify headline only (headline), headline + teaser (abstract), or headline + full body (full). (provider: benzinga)
        date : Union[str, None]
            Date of the news to retrieve. (provider: benzinga)
        start_date : Union[str, None]
            Start date of the news to retrieve. (provider: benzinga)
        end_date : Union[str, None]
            End date of the news to retrieve. (provider: benzinga)
        updated_since : Union[int, None]
            Number of seconds since the news was updated. (provider: benzinga)
        published_since : Union[int, None]
            Number of seconds since the news was published. (provider: benzinga)
        sort : Union[Literal['id', 'created', 'updated'], None]
            Key to sort the news by. (provider: benzinga)
        order : Union[Literal['asc', 'desc'], None]
            Order to sort the news by. (provider: benzinga)
        isin : Union[str, None]
            The ISIN of the news to retrieve. (provider: benzinga)
        cusip : Union[str, None]
            The CUSIP of the news to retrieve. (provider: benzinga)
        channels : Union[str, None]
            Channels of the news to retrieve. (provider: benzinga)
        topics : Union[str, None]
            Topics of the news to retrieve. (provider: benzinga)
        authors : Union[str, None]
            Authors of the news to retrieve. (provider: benzinga)
        content_types : Union[str, None]
            Content types of the news to retrieve. (provider: benzinga)

        Returns
        -------
        OBBject
            results : List[GlobalNews]
                Serializable results.
            provider : Union[Literal['benzinga', 'fmp', 'intrinio'], None]
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
