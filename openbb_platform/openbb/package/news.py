### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Optional

from annotated_types import Ge
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.decorators import validate
from openbb_core.app.static.filters import filter_inputs
from openbb_core.provider.abstract.data import Data
from typing_extensions import Annotated


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
        symbols: Annotated[
            str,
            OpenBBCustomParameter(
                description=" Here it is a separated list of symbols."
            ),
        ],
        limit: Annotated[
            Optional[Annotated[int, Ge(ge=0)]],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 20,
        provider: Optional[
            Literal["benzinga", "fmp", "intrinio", "polygon", "tiingo"]
        ] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Company News. Get news for one or more companies.

        Parameters
        ----------
        symbols : str
             Here it is a separated list of symbols.
        limit : Optional[Annotated[int, Ge(ge=0)]]
            The number of data entries to return.
        provider : Optional[Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'tiing...
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
        sort : Literal['id', 'created', 'updated']
            Key to sort the news by. (provider: benzinga)
        order : Optional[Literal['asc', 'desc']]
            Order to sort the news by. (provider: benzinga);
            Sort order of the articles. (provider: polygon)
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
        page : Optional[int]
            Page number of the results. Use in combination with limit. (provider: fmp)
        published_utc : Optional[str]
            Date query to fetch articles. Supports operators <, <=, >, >= (provider: polygon)
        source : Optional[str]
            A comma-separated list of the domains requested. (provider: tiingo)

        Returns
        -------
        OBBject
            results : List[CompanyNews]
                Serializable results.
            provider : Optional[Literal['benzinga', 'fmp', 'intrinio', 'polygon', 'tiingo']]
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
        image : Optional[str]
            Image URL of the news.
        text : Optional[str]
            Text/body of the news.
        url : str
            URL of the news.
        id : Optional[str]
            ID of the news. (provider: benzinga);
            Intrinio ID for the article. (provider: intrinio);
            Article ID. (provider: polygon)
        author : Optional[str]
            Author of the news. (provider: benzinga);
            Author of the article. (provider: polygon)
        teaser : Optional[str]
            Teaser of the news. (provider: benzinga)
        images : Optional[Union[List[Dict[str, str]], List[str], str]]
            Images associated with the news. (provider: benzinga);
            URL to the images of the news. (provider: fmp)
        channels : Optional[str]
            Channels associated with the news. (provider: benzinga)
        stocks : Optional[str]
            Stocks associated with the news. (provider: benzinga)
        tags : Optional[str]
            Tags associated with the news. (provider: benzinga, tiingo)
        updated : Optional[datetime]
            Updated date of the news. (provider: benzinga)
        symbol : Optional[str]
            Ticker of the fetched news. (provider: fmp)
        site : Optional[str]
            Name of the news source. (provider: fmp, tiingo)
        amp_url : Optional[str]
            AMP URL. (provider: polygon)
        image_url : Optional[str]
            Image URL. (provider: polygon)
        keywords : Optional[List[str]]
            Keywords in the article (provider: polygon)
        publisher : Optional[openbb_polygon.models.company_news.PolygonPublisher]
            Publisher of the article. (provider: polygon)
        tickers : Optional[List[str]]
            Tickers covered in the article. (provider: polygon)
        symbols : Optional[str]
            Ticker tagged in the fetched news. (provider: tiingo)
        article_id : Optional[int]
            Unique ID of the news article. (provider: tiingo)
        crawl_date : Optional[datetime]
            Date the news article was crawled. (provider: tiingo)

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
        limit: Annotated[
            int,
            OpenBBCustomParameter(
                description="The number of data entries to return. Here its the no. of articles to return."
            ),
        ] = 20,
        provider: Optional[Literal["benzinga", "fmp", "intrinio", "tiingo"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """World News. Global news data.

        Parameters
        ----------
        limit : int
            The number of data entries to return. Here its the no. of articles to return.
        provider : Optional[Literal['benzinga', 'fmp', 'intrinio', 'tiingo']]
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
            extra: Dict[str, Any]
                Extra info.

        WorldNews
        ---------
        date : datetime
            The date of the data. Here it is the published date of the news.
        title : str
            Title of the news.
        images : Optional[List[Dict[str, str]]]
            Images associated with the news.
        text : Optional[str]
            Text/body of the news.
        url : Optional[str]
            URL of the news.
        id : Optional[str]
            ID of the news. (provider: benzinga);
            Article ID. (provider: intrinio)
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
            Site of the news. (provider: fmp);
            Name of the news source. (provider: tiingo)
        company : Optional[Dict[str, Any]]
            Company details related to the news article. (provider: intrinio)
        symbols : Optional[str]
            Ticker tagged in the fetched news. (provider: tiingo)
        article_id : Optional[int]
            Unique ID of the news article. (provider: tiingo)
        crawl_date : Optional[datetime]
            Date the news article was crawled. (provider: tiingo)

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
