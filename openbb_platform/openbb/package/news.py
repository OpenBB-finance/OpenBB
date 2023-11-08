### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Union

import typing_extensions
from annotated_types import Ge
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.decorators import validate
from openbb_core.app.static.filters import filter_inputs
from openbb_provider.abstract.data import Data


class ROUTER_news(Container):
    """/news
    company
    world
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
    def company(
        self,
        symbols: typing_extensions.Annotated[
            str,
            OpenBBCustomParameter(
                description=" Here it is a separated list of symbols."
            ),
        ],
        limit: typing_extensions.Annotated[
            Union[typing_extensions.Annotated[int, Ge(ge=0)], None],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 20,
        provider: Union[
            Literal["benzinga", "fmp", "intrinio", "polygon", "ultima", "yfinance"],
            None,
        ] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Company News. Get news for one or more companies.

        Parameters
        ----------
        symbols : str
             Here it is a separated list of symbols.
        limit : Union[typing_extensions.Annotated[int, Ge(ge=0)], None]
            The number of data entries to return.
        provider : Union[Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'ultima',...
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'benzinga' if there is
            no default.
        display : Literal['headline', 'abstract', 'full']
            Specify headline only (headline), headline + teaser (abstract), or headline + full body (full). (provider: benzinga)
        date : Optional[Union[str]]
            Date of the news to retrieve. (provider: benzinga)
        start_date : Optional[Union[str]]
            Start date of the news to retrieve. (provider: benzinga)
        end_date : Optional[Union[str]]
            End date of the news to retrieve. (provider: benzinga)
        updated_since : Optional[Union[int]]
            Number of seconds since the news was updated. (provider: benzinga)
        published_since : Optional[Union[int]]
            Number of seconds since the news was published. (provider: benzinga)
        sort : Optional[Union[Literal['id', 'created', 'updated']]]
            Key to sort the news by. (provider: benzinga)
        order : Optional[Union[Literal['asc', 'desc']]]
            Order to sort the news by. (provider: benzinga); Sort order of the articles. (provider: polygon)
        isin : Optional[Union[str]]
            The ISIN of the news to retrieve. (provider: benzinga)
        cusip : Optional[Union[str]]
            The CUSIP of the news to retrieve. (provider: benzinga)
        channels : Optional[Union[str]]
            Channels of the news to retrieve. (provider: benzinga)
        topics : Optional[Union[str]]
            Topics of the news to retrieve. (provider: benzinga)
        authors : Optional[Union[str]]
            Authors of the news to retrieve. (provider: benzinga)
        content_types : Optional[Union[str]]
            Content types of the news to retrieve. (provider: benzinga)
        page : Optional[Union[int]]
            Page number of the results. Use in combination with limit. (provider: fmp)
        published_utc : Optional[Union[str]]
            Date query to fetch articles. Supports operators <, <=, >, >= (provider: polygon)

        Returns
        -------
        OBBject
            results : Union[List[CompanyNews]]
                Serializable results.
            provider : Union[Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'ultima', 'yfinance'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        CompanyNews
        -----------
        date : datetime
            The date of the data. Here it is the date of the news.
        title : str
            Title of the news.
        image : Optional[Union[str]]
            Image URL of the news.
        text : Optional[Union[str]]
            Text/body of the news.
        url : str
            URL of the news.
        id : Optional[Union[str]]
            ID of the news. (provider: benzinga); Intrinio ID for the article. (provider: intrinio); Article ID. (provider: polygon)
        author : Optional[Union[str]]
            Author of the news. (provider: benzinga); Author of the article. (provider: polygon)
        teaser : Optional[Union[str]]
            Teaser of the news. (provider: benzinga)
        images : Optional[Union[List[Dict[str, str]], List[str], str]]
            Images associated with the news. (provider: benzinga); URL to the images of the news. (provider: fmp)
        channels : Optional[Union[str]]
            Channels associated with the news. (provider: benzinga)
        stocks : Optional[Union[str]]
            Stocks associated with the news. (provider: benzinga)
        tags : Optional[Union[str]]
            Tags associated with the news. (provider: benzinga)
        updated : Optional[Union[datetime]]
            Updated date of the news. (provider: benzinga)
        symbol : Optional[Union[str]]
            Ticker of the fetched news. (provider: fmp)
        site : Optional[Union[str]]
            Name of the news source. (provider: fmp)
        amp_url : Optional[Union[str]]
            AMP URL. (provider: polygon)
        image_url : Optional[Union[str]]
            Image URL. (provider: polygon)
        keywords : Optional[Union[List[str]]]
            Keywords in the article (provider: polygon)
        publisher : Optional[Union[openbb_polygon.models.company_news.PolygonPublisher, str]]
            Publisher of the article. (provider: polygon, ultima, yfinance)
        tickers : Optional[Union[List[str]]]
            Tickers covered in the article. (provider: polygon)
        ticker : Optional[Union[str]]
            Ticker associated with the news. (provider: ultima)
        risk_category : Optional[Union[str]]
            Risk category of the news. (provider: ultima)
        uuid : Optional[Union[str]]
            Unique identifier for the news article (provider: yfinance)
        type : Optional[Union[str]]
            Type of the news article (provider: yfinance)
        thumbnail : Optional[Union[List]]
            Thumbnail related data to the ticker news article. (provider: yfinance)
        related_tickers : Optional[Union[str]]
            Tickers related to the news article. (provider: yfinance)

        Example
        -------
        >>> from openbb import obb
        >>> obb.news.company(symbols="AAPL,MSFT", limit=20)
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbols": symbols,
                "limit": limit,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/news/company",
            **inputs,
        )

    @validate
    def world(
        self,
        limit: typing_extensions.Annotated[
            int,
            OpenBBCustomParameter(
                description="The number of data entries to return. Here its the no. of articles to return."
            ),
        ] = 20,
        provider: Union[Literal["benzinga", "biztoc", "fmp", "intrinio"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Global News. Global news data.

        Parameters
        ----------
        limit : int
            The number of data entries to return. Here its the no. of articles to return.
        provider : Union[Literal['benzinga', 'biztoc', 'fmp', 'intrinio'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'benzinga' if there is
            no default.
        display : Literal['headline', 'abstract', 'full']
            Specify headline only (headline), headline + teaser (abstract), or headline + full body (full). (provider: benzinga)
        date : Optional[Union[str]]
            Date of the news to retrieve. (provider: benzinga)
        start_date : Optional[Union[str]]
            Start date of the news to retrieve. (provider: benzinga)
        end_date : Optional[Union[str]]
            End date of the news to retrieve. (provider: benzinga)
        updated_since : Optional[Union[int]]
            Number of seconds since the news was updated. (provider: benzinga)
        published_since : Optional[Union[int]]
            Number of seconds since the news was published. (provider: benzinga)
        sort : Optional[Union[Literal['id', 'created', 'updated']]]
            Key to sort the news by. (provider: benzinga)
        order : Optional[Union[Literal['asc', 'desc']]]
            Order to sort the news by. (provider: benzinga)
        isin : Optional[Union[str]]
            The ISIN of the news to retrieve. (provider: benzinga)
        cusip : Optional[Union[str]]
            The CUSIP of the news to retrieve. (provider: benzinga)
        channels : Optional[Union[str]]
            Channels of the news to retrieve. (provider: benzinga)
        topics : Optional[Union[str]]
            Topics of the news to retrieve. (provider: benzinga)
        authors : Optional[Union[str]]
            Authors of the news to retrieve. (provider: benzinga)
        content_types : Optional[Union[str]]
            Content types of the news to retrieve. (provider: benzinga)
        filter : Literal['crypto', 'hot', 'latest', 'main', 'media', 'source', 'tag']
            Filter by type of news. (provider: biztoc)
        source : str
            Filter by a specific publisher. Only valid when filter is set to source. (provider: biztoc)
        tag : Optional[Union[str]]
            Tag, topic, to filter articles by. Only valid when filter is set to tag. (provider: biztoc)
        term : Optional[Union[str]]
            Search term to filter articles by. This overrides all other filters. (provider: biztoc)

        Returns
        -------
        OBBject
            results : Union[List[GlobalNews]]
                Serializable results.
            provider : Union[Literal['benzinga', 'biztoc', 'fmp', 'intrinio'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        GlobalNews
        ----------
        date : datetime
            The date of the data. Here it is the published date of the news.
        title : str
            Title of the news.
        images : Optional[Union[List[Dict[str, str]]]]
            Images associated with the news.
        text : Optional[Union[str]]
            Text/body of the news.
        url : Optional[Union[str]]
            URL of the news.
        id : Optional[Union[str]]
            ID of the news. (provider: benzinga); Unique Article ID. (provider: biztoc); Article ID. (provider: intrinio)
        author : Optional[Union[str]]
            Author of the news. (provider: benzinga)
        teaser : Optional[Union[str]]
            Teaser of the news. (provider: benzinga)
        channels : Optional[Union[str]]
            Channels associated with the news. (provider: benzinga)
        stocks : Optional[Union[str]]
            Stocks associated with the news. (provider: benzinga)
        tags : Optional[Union[str, List[str]]]
            Tags associated with the news. (provider: benzinga); Tags for the article. (provider: biztoc)
        updated : Optional[Union[datetime]]
            None
        favicon : Optional[Union[str]]
            Icon image for the source of the article. (provider: biztoc)
        score : Optional[Union[float]]
            Search relevance score for the article. (provider: biztoc)
        site : Optional[Union[str]]
            Site of the news. (provider: fmp)
        company : Optional[Union[Dict[str, Any]]]
            Company details related to the news article. (provider: intrinio)

        Example
        -------
        >>> from openbb import obb
        >>> obb.news.world(limit=20)
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "limit": limit,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/news/world",
            **inputs,
        )
