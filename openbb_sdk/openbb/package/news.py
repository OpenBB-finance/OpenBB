### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Union

import pydantic
import typing_extensions
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs
from pydantic import validate_arguments


class CLASS_news(Container):
    """/news
    globalnews
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate_arguments
    def globalnews(
        self,
        page: typing_extensions.Annotated[
            pydantic.types.NonNegativeInt,
            OpenBBCustomParameter(description="Page of the global news."),
        ] = 0,
<<<<<<< HEAD
        chart: bool = False,
        provider: Union[Literal["benzinga", "fmp"], None] = None,
=======
        provider: Optional[Literal["benzinga", "fmp"]] = None,
>>>>>>> feature/openbb-sdk-v4
        **kwargs
    ) -> OBBject[List]:
        """Global News.

        Parameters
        ----------
        page : NonNegativeInt
            Page of the global news.
<<<<<<< HEAD
        chart : bool
            Whether to create a chart or not, by default False.
        provider : Union[Literal['benzinga', 'fmp'], NoneType]
=======
        provider : Optional[Literal['benzinga', 'fmp']]
>>>>>>> feature/openbb-sdk-v4
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'benzinga' if there is
            no default.
        page_size : int
            Number of results to return per page. (provider: benzinga)
        display_output : Literal['headline', 'summary', 'full', 'all']
            Type of data to return. (provider: benzinga)
        date : Union[datetime.datetime, NoneType]
            Date of the news to retrieve. (provider: benzinga)
        date_from : Union[datetime.datetime, NoneType]
            Start date of the news to retrieve. (provider: benzinga)
        date_to : Union[datetime.datetime, NoneType]
            End date of the news to retrieve. (provider: benzinga)
        updated_since : Union[int, NoneType]
            Number of seconds since the news was updated. (provider: benzinga)
        published_since : Union[int, NoneType]
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
            Site of the news. (provider: fmp)"""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "page": page,
            },
            extra_params=kwargs,
        )

        return self._command_runner.run(
            "/news/globalnews",
            **inputs,
        )
