### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union

from annotated_types import Ge
from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_news(Container):
    """/news
    company
    world
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def company(
        self,
        symbol: Annotated[
            Union[str, None, List[Optional[str]]],
            OpenBBField(
                description="Symbol to get data for. Multiple comma separated items allowed for provider(s): benzinga, fmp, intrinio, polygon, tiingo, yfinance."
            ),
        ] = None,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        limit: Annotated[
            Optional[Annotated[int, Ge(ge=0)]],
            OpenBBField(description="The number of data entries to return."),
        ] = 2500,
        provider: Annotated[
            Optional[
                Literal["benzinga", "fmp", "intrinio", "polygon", "tiingo", "yfinance"]
            ],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'benzinga' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Company News. Get news for one or more companies.

        Parameters
        ----------
        symbol : Union[str, None, List[Optional[str]]]
            Symbol to get data for. Multiple comma separated items allowed for provider(s): benzinga, fmp, intrinio, polygon, tiingo, yfinance.
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        limit : Optional[Annotated[int, Ge(ge=0)]]
            The number of data entries to return.
        provider : Optional[Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'tiing...
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'benzinga' if there is
            no default.
        date : Optional[datetime.date]
            A specific date to get data for. (provider: benzinga)
        display : Literal['headline', 'abstract', 'full']
            Specify headline only (headline), headline + teaser (abstract), or headline + full body (full). (provider: benzinga)
        updated_since : Optional[int]
            Number of seconds since the news was updated. (provider: benzinga)
        published_since : Optional[int]
            Number of seconds since the news was published. (provider: benzinga)
        sort : Literal['id', 'created', 'updated']
            Key to sort the news by. (provider: benzinga)
        order : Optional[Literal['asc', 'desc']]
            Order to sort the news by. (provider: benzinga);
            Sort order of the articles. (provider: polygon)
        isin : Optional[str]
            The company's ISIN. (provider: benzinga)
        cusip : Optional[str]
            The company's CUSIP. (provider: benzinga)
        channels : Optional[str]
            Channels of the news to retrieve. (provider: benzinga)
        topics : Optional[str]
            Topics of the news to retrieve. (provider: benzinga)
        authors : Optional[str]
            Authors of the news to retrieve. (provider: benzinga)
        content_types : Optional[str]
            Content types of the news to retrieve. (provider: benzinga)
        page : Optional[int]
            Page number of the results. Use in combination with limit. (provider: fmp)
        offset : Optional[int]
            Page offset, used in conjunction with limit. (provider: tiingo)
        source : Optional[str]
            A comma-separated list of the domains requested. (provider: tiingo)

        Returns
        -------
        OBBject
            results : List[CompanyNews]
                Serializable results.
            provider : Optional[Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'tiingo', 'yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CompanyNews
        -----------
        date : datetime
            The date of the data. Here it is the published date of the article.
        title : str
            Title of the article.
        text : Optional[str]
            Text/body of the article.
        images : Optional[List[Dict[str, str]]]
            Images associated with the article.
        url : str
            URL to the article.
        symbols : Optional[str]
            Symbols associated with the article.
        id : Optional[str]
            Article ID. (provider: benzinga, intrinio, polygon)
        author : Optional[str]
            Author of the article. (provider: benzinga)
        teaser : Optional[str]
            Teaser of the news. (provider: benzinga)
        channels : Optional[str]
            Channels associated with the news. (provider: benzinga)
        stocks : Optional[str]
            Stocks associated with the news. (provider: benzinga)
        tags : Optional[str]
            Tags associated with the news. (provider: benzinga, polygon, tiingo)
        updated : Optional[datetime]
            Updated date of the news. (provider: benzinga)
        source : Optional[str]
            Name of the news source. (provider: fmp);
            Source of the article. (provider: polygon);
            News source. (provider: tiingo);
            Source of the news article (provider: yfinance)
        amp_url : Optional[str]
            AMP URL. (provider: polygon)
        publisher : Optional[PolygonPublisher]
            Publisher of the article. (provider: polygon)
        article_id : Optional[int]
            Unique ID of the news article. (provider: tiingo)
        crawl_date : Optional[datetime]
            Date the news article was crawled. (provider: tiingo)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.news.company(provider='benzinga')
        >>> obb.news.company(limit=100, provider='benzinga')
        >>> # Get news on the specified dates.
        >>> obb.news.company(symbol='AAPL', start_date='2024-02-01', end_date='2024-02-07', provider='intrinio')
        >>> # Display the headlines of the news.
        >>> obb.news.company(symbol='AAPL', display='headline', provider='benzinga')
        >>> # Get news for multiple symbols.
        >>> obb.news.company(symbol='aapl,tsla', provider='fmp')
        >>> # Get news company's ISIN.
        >>> obb.news.company(symbol='NVDA', isin='US0378331005', provider='benzinga')
        """  # noqa: E501

        return self._run(
            "/news/company",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/news/company",
                        (
                            "benzinga",
                            "fmp",
                            "intrinio",
                            "polygon",
                            "tiingo",
                            "yfinance",
                        ),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                    "limit": limit,
                },
                extra_params=kwargs,
                info={
                    "symbol": {
                        "multiple_items_allowed": [
                            "benzinga",
                            "fmp",
                            "intrinio",
                            "polygon",
                            "tiingo",
                            "yfinance",
                        ]
                    }
                },
            )
        )

    @exception_handler
    @validate
    def world(
        self,
        limit: Annotated[
            int,
            OpenBBField(
                description="The number of data entries to return. The number of articles to return."
            ),
        ] = 2500,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        provider: Annotated[
            Optional[Literal["benzinga", "fmp", "intrinio", "tiingo"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'benzinga' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """World News. Global news data.

        Parameters
        ----------
        limit : int
            The number of data entries to return. The number of articles to return.
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['benzinga', 'fmp', 'intrinio', 'tiingo']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'benzinga' if there is
            no default.
        date : Optional[datetime.date]
            A specific date to get data for. (provider: benzinga)
        display : Literal['headline', 'abstract', 'full']
            Specify headline only (headline), headline + teaser (abstract), or headline + full body (full). (provider: benzinga)
        updated_since : Optional[int]
            Number of seconds since the news was updated. (provider: benzinga)
        published_since : Optional[int]
            Number of seconds since the news was published. (provider: benzinga)
        sort : Literal['id', 'created', 'updated']
            Key to sort the news by. (provider: benzinga)
        order : Literal['asc', 'desc']
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
        offset : Optional[int]
            Page offset, used in conjunction with limit. (provider: tiingo)
        source : Optional[str]
            A comma-separated list of the domains requested. (provider: tiingo)

        Returns
        -------
        OBBject
            results : List[WorldNews]
                Serializable results.
            provider : Optional[Literal['benzinga', 'fmp', 'intrinio', 'tiingo']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        WorldNews
        ---------
        date : datetime
            The date of the data. The published date of the article.
        title : str
            Title of the article.
        images : Optional[List[Dict[str, str]]]
            Images associated with the article.
        text : Optional[str]
            Text/body of the article.
        url : Optional[str]
            URL to the article.
        id : Optional[str]
            Article ID. (provider: benzinga, intrinio)
        author : Optional[str]
            Author of the news. (provider: benzinga)
        teaser : Optional[str]
            Teaser of the news. (provider: benzinga)
        channels : Optional[str]
            Channels associated with the news. (provider: benzinga)
        stocks : Optional[str]
            Stocks associated with the news. (provider: benzinga)
        tags : Optional[str]
            Tags associated with the news. (provider: benzinga, tiingo)
        updated : Optional[datetime]
            Updated date of the news. (provider: benzinga)
        site : Optional[str]
            News source. (provider: fmp, tiingo)
        company : Optional[Dict[str, Any]]
            Company details related to the news article. (provider: intrinio)
        symbols : Optional[str]
            Ticker tagged in the fetched news. (provider: tiingo)
        article_id : Optional[int]
            Unique ID of the news article. (provider: tiingo)
        crawl_date : Optional[datetime]
            Date the news article was crawled. (provider: tiingo)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.news.world(provider='fmp')
        >>> obb.news.world(limit=100, provider='intrinio')
        >>> # Get news on the specified dates.
        >>> obb.news.world(start_date='2024-02-01', end_date='2024-02-07', provider='intrinio')
        >>> # Display the headlines of the news.
        >>> obb.news.world(display='headline', provider='benzinga')
        >>> # Get news by topics.
        >>> obb.news.world(topics='finance', provider='benzinga')
        >>> # Get news by source using 'tingo' as provider.
        >>> obb.news.world(provider='tiingo', source='bloomberg')
        """  # noqa: E501

        return self._run(
            "/news/world",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/news/world",
                        ("benzinga", "fmp", "intrinio", "tiingo"),
                    )
                },
                standard_params={
                    "limit": limit,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )
