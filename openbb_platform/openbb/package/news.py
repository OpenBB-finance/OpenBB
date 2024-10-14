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
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: benzinga, fmp, intrinio, polygon, tiingo, yfinance."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Company News. Get news for one or more companies.

        Parameters
        ----------
        symbol : Union[str, None, List[Optional[str]]]
            Symbol to get data for. Multiple comma separated items allowed for provider(s): benzinga, fmp, intrinio, polygon, tiingo, yfinance.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        limit : Optional[Annotated[int, Ge(ge=0)]]
            The number of data entries to return.
        provider : Optional[Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'tiingo', 'yfinance']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: benzinga, fmp, intrinio, polygon, tiingo, yfinance.
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
        source : Optional[Union[Literal['yahoo', 'moody', 'moody_us_news', 'moody_us_press_releases'], str]]
            The source of the news article. (provider: intrinio);
            A comma-separated list of the domains requested. (provider: tiingo)
        sentiment : Optional[Literal['positive', 'neutral', 'negative']]
            Return news only from this source. (provider: intrinio)
        language : Optional[str]
            Filter by language. Unsupported for yahoo source. (provider: intrinio)
        topic : Optional[str]
            Filter by topic. Unsupported for yahoo source. (provider: intrinio)
        word_count_greater_than : Optional[int]
            News stories will have a word count greater than this value. Unsupported for yahoo source. (provider: intrinio)
        word_count_less_than : Optional[int]
            News stories will have a word count less than this value. Unsupported for yahoo source. (provider: intrinio)
        is_spam : Optional[bool]
            Filter whether it is marked as spam or not. Unsupported for yahoo source. (provider: intrinio)
        business_relevance_greater_than : Optional[float]
            News stories will have a business relevance score more than this value. Unsupported for yahoo source. Value is a decimal between 0 and 1. (provider: intrinio)
        business_relevance_less_than : Optional[float]
            News stories will have a business relevance score less than this value. Unsupported for yahoo source. Value is a decimal between 0 and 1. (provider: intrinio)
        offset : Optional[int]
            Page offset, used in conjunction with limit. (provider: tiingo)

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
            The source of the news article. (provider: intrinio);
            Source of the article. (provider: polygon);
            News source. (provider: tiingo);
            Source of the news article (provider: yfinance)
        summary : Optional[str]
            The summary of the news article. (provider: intrinio)
        topics : Optional[str]
            The topics related to the news article. (provider: intrinio)
        word_count : Optional[int]
            The word count of the news article. (provider: intrinio)
        business_relevance : Optional[float]
                How strongly correlated the news article is to the business (provider: intrinio)
        sentiment : Optional[str]
            The sentiment of the news article - i.e, negative, positive. (provider: intrinio)
        sentiment_confidence : Optional[float]
            The confidence score of the sentiment rating. (provider: intrinio)
        language : Optional[str]
            The language of the news article. (provider: intrinio)
        spam : Optional[bool]
            Whether the news article is spam. (provider: intrinio)
        copyright : Optional[str]
            The copyright notice of the news article. (provider: intrinio)
        security : Optional[IntrinioSecurity]
            The Intrinio Security object. Contains the security details related to the news article. (provider: intrinio)
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
                        "news.company",
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
                        "benzinga": {"multiple_items_allowed": True, "choices": None},
                        "fmp": {"multiple_items_allowed": True, "choices": None},
                        "intrinio": {"multiple_items_allowed": True, "choices": None},
                        "polygon": {"multiple_items_allowed": True, "choices": None},
                        "tiingo": {"multiple_items_allowed": True, "choices": None},
                        "yfinance": {"multiple_items_allowed": True, "choices": None},
                    },
                    "order": {
                        "polygon": {
                            "multiple_items_allowed": False,
                            "choices": ["asc", "desc"],
                        }
                    },
                    "source": {
                        "intrinio": {
                            "multiple_items_allowed": False,
                            "choices": [
                                "yahoo",
                                "moody",
                                "moody_us_news",
                                "moody_us_press_releases",
                            ],
                        }
                    },
                    "sentiment": {
                        "intrinio": {
                            "multiple_items_allowed": False,
                            "choices": ["positive", "neutral", "negative"],
                        }
                    },
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
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: benzinga, fmp, intrinio, tiingo."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """World News. Global news data.

        Parameters
        ----------
        limit : int
            The number of data entries to return. The number of articles to return.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['benzinga', 'fmp', 'intrinio', 'tiingo']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: benzinga, fmp, intrinio, tiingo.
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
        source : Optional[Union[Literal['yahoo', 'moody', 'moody_us_news', 'moody_us_press_releases'], str]]
            The source of the news article. (provider: intrinio);
            A comma-separated list of the domains requested. (provider: tiingo)
        sentiment : Optional[Literal['positive', 'neutral', 'negative']]
            Return news only from this source. (provider: intrinio)
        language : Optional[str]
            Filter by language. Unsupported for yahoo source. (provider: intrinio)
        topic : Optional[str]
            Filter by topic. Unsupported for yahoo source. (provider: intrinio)
        word_count_greater_than : Optional[int]
            News stories will have a word count greater than this value. Unsupported for yahoo source. (provider: intrinio)
        word_count_less_than : Optional[int]
            News stories will have a word count less than this value. Unsupported for yahoo source. (provider: intrinio)
        is_spam : Optional[bool]
            Filter whether it is marked as spam or not. Unsupported for yahoo source. (provider: intrinio)
        business_relevance_greater_than : Optional[float]
            News stories will have a business relevance score more than this value. Unsupported for yahoo source. Value is a decimal between 0 and 1. (provider: intrinio)
        business_relevance_less_than : Optional[float]
            News stories will have a business relevance score less than this value. Unsupported for yahoo source. Value is a decimal between 0 and 1. (provider: intrinio)
        offset : Optional[int]
            Page offset, used in conjunction with limit. (provider: tiingo)

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
        source : Optional[str]
            The source of the news article. (provider: intrinio)
        summary : Optional[str]
            The summary of the news article. (provider: intrinio)
        topics : Optional[str]
            The topics related to the news article. (provider: intrinio)
        word_count : Optional[int]
            The word count of the news article. (provider: intrinio)
        business_relevance : Optional[float]
                How strongly correlated the news article is to the business (provider: intrinio)
        sentiment : Optional[str]
            The sentiment of the news article - i.e, negative, positive. (provider: intrinio)
        sentiment_confidence : Optional[float]
            The confidence score of the sentiment rating. (provider: intrinio)
        language : Optional[str]
            The language of the news article. (provider: intrinio)
        spam : Optional[bool]
            Whether the news article is spam. (provider: intrinio)
        copyright : Optional[str]
            The copyright notice of the news article. (provider: intrinio)
        company : Optional[IntrinioCompany]
            The Intrinio Company object. Contains details company reference data. (provider: intrinio)
        security : Optional[IntrinioSecurity]
            The Intrinio Security object. Contains the security details related to the news article. (provider: intrinio)
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
                        "news.world",
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
