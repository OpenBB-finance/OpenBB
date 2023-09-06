### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Optional

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs
from pydantic import validate_arguments
from typing_extensions import Annotated


class CLASS_news(Container):
    """/news
    globalnews
    search
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate_arguments
    def globalnews(
        self,
        page: Annotated[
            int, OpenBBCustomParameter(description="Page of the global news.")
        ] = 0,
        provider: Optional[Literal["benzinga", "biztoc", "fmp", "intrinio"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Global News.

        Parameters
        ----------
        page : int
            Page of the global news.
        provider : Optional[Literal['benzinga', 'biztoc', 'fmp', 'intrinio']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'benzinga' if there is
            no default.
        page_size : int
            Number of results to return per page. (provider: benzinga)
        display_output : Literal['headline', 'summary', 'full', 'all']
            Type of data to return. (provider: benzinga)
        date : Optional[datetime.datetime]
            Date of the news to retrieve. (provider: benzinga)
        date_from : Optional[datetime.datetime]
            Start date of the news to retrieve. (provider: benzinga)
        date_to : Optional[datetime.datetime]
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
        filter : Literal['crypto', 'hot', 'latest', 'main', 'media', 'source', 'tag']
            Filter by type of news. (provider: biztoc)
        source : str
            Filter by a specific publisher. (provider: biztoc)
        tag : str
            Tag, topic, to filter articles by. (provider: biztoc)
        next_page : str
            Token to get the next page of data from a previous API call. (provider: intrinio)
        limit : Optional[int]
            The number of data entries to return. (provider: intrinio)
        all_pages : Optional[bool]
            Returns all pages of data from the API call at once. (provider: intrinio)

        Returns
        -------
        OBBject
            results : List[GlobalNews]
                Serializable results.
            provider : Optional[Literal['benzinga', 'biztoc', 'fmp', 'intrinio']]
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
        favicon : Optional[str]
            Icon image for the source of the article. (provider: biztoc)
        domain : Optional[str]
            Domain base url for the article source. (provider: biztoc)
        id : Optional[str]
            Intrinio ID for the news article. (provider: intrinio)
        company : Optional[Mapping[str, Any]]
            Company details related to the news article. (provider: intrinio)"""  # noqa: E501

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

    @validate_arguments
    def search(
        self,
        term: Annotated[str, OpenBBCustomParameter(description="Search query.")],
        provider: Optional[Literal["biztoc"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Search news by keyword or query string.

        Parameters
        ----------
        term : str
            Search query.
        provider : Optional[Literal['biztoc']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'biztoc' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[NewsSearch]
                Serializable results.
            provider : Optional[Literal['biztoc']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        NewsSearch
        ----------
        date : Optional[datetime]
            Published date and time of the news.
        title : Optional[str]
            Headline of the news.
        text : Optional[str]
            Text/body of the news.
        url : Optional[str]
            URL of the article.
        image : Optional[Any]
            Preview image.
        score : Optional[float]
            Article score. (provider: biztoc)
        domain : Optional[str]
            Base url to the article source. (provider: biztoc)
        tags : Optional[List[str]]
            Tags for the article. (provider: biztoc)"""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "term": term,
            },
            extra_params=kwargs,
        )

        return self._command_runner.run(
            "/news/search",
            **inputs,
        )
