### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_regulators_sec(Container):
    """/regulators/sec
    cik_map
    institutions_search
    rss_litigation
    schema_files
    sic_search
    symbol_map
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
    def cik_map(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Symbol to get data for. Multiple items allowed: intrinio, yfinance."
            ),
        ],
        provider: Optional[Literal["sec"]] = None,
        **kwargs
    ) -> OBBject:
        """Map a ticker symbol to a CIK number.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple items allowed: intrinio, yfinance.
        provider : Optional[Literal['sec']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'sec' if there is
            no default.

        Returns
        -------
        OBBject
            results : CikMap
                Serializable results.
            provider : Optional[Literal['sec']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        CikMap
        ------
        cik : Optional[Union[str, int]]
            Central Index Key (provider: sec)

        Example
        -------
        >>> from openbb import obb
        >>> obb.regulators.sec.cik_map(symbol="MSFT").results.cik
        >>>     0000789019
        """  # noqa: E501

        return self._run(
            "/regulators/sec/cik_map",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/regulators/sec/cik_map",
                        ("sec",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
                extra_info={
                    "symbol": {"multiple_items_allowed": ["intrinio", "yfinance"]}
                },
            )
        )

    @validate
    def institutions_search(
        self,
        query: Annotated[str, OpenBBCustomParameter(description="Search query.")] = "",
        use_cache: Annotated[
            Optional[bool],
            OpenBBCustomParameter(
                description="Whether or not to use cache. If True, cache will store for seven days."
            ),
        ] = True,
        provider: Optional[Literal["sec"]] = None,
        **kwargs
    ) -> OBBject:
        """Search SEC-regulated institutions by name and return a list of results with CIK numbers.

        Parameters
        ----------
        query : str
            Search query.
        use_cache : Optional[bool]
            Whether or not to use cache. If True, cache will store for seven days.
        provider : Optional[Literal['sec']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'sec' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[InstitutionsSearch]
                Serializable results.
            provider : Optional[Literal['sec']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        InstitutionsSearch
        ------------------
        name : Optional[str]
            The name of the institution. (provider: sec)
        cik : Optional[Union[str, int]]
            Central Index Key (CIK) (provider: sec)

        Example
        -------
        >>> from openbb import obb
        >>> obb.regulators.sec.institutions_search(query="blackstone real estate").to_df()
        """  # noqa: E501

        return self._run(
            "/regulators/sec/institutions_search",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/regulators/sec/institutions_search",
                        ("sec",),
                    )
                },
                standard_params={
                    "query": query,
                    "use_cache": use_cache,
                },
                extra_params=kwargs,
            )
        )

    @validate
    def rss_litigation(
        self, provider: Optional[Literal["sec"]] = None, **kwargs
    ) -> OBBject:
        """The RSS feed provides links to litigation releases concerning civil lawsuits brought by the Commission in federal court.

        Parameters
        ----------
        provider : Optional[Literal['sec']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'sec' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[RssLitigation]
                Serializable results.
            provider : Optional[Literal['sec']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        RssLitigation
        -------------
        published : Optional[datetime]
            The date of publication. (provider: sec)
        title : Optional[str]
            The title of the release. (provider: sec)
        summary : Optional[str]
            Short summary of the release. (provider: sec)
        id : Optional[str]
            The identifier associated with the release. (provider: sec)
        link : Optional[str]
            URL to the release. (provider: sec)

        Example
        -------
        >>> from openbb import obb
        >>> obb.regulators.sec.rss_litigation().to_dict("records")[0]
        """  # noqa: E501

        return self._run(
            "/regulators/sec/rss_litigation",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/regulators/sec/rss_litigation",
                        ("sec",),
                    )
                },
                standard_params={},
                extra_params=kwargs,
            )
        )

    @validate
    def schema_files(
        self,
        query: Annotated[str, OpenBBCustomParameter(description="Search query.")] = "",
        use_cache: Annotated[
            Optional[bool],
            OpenBBCustomParameter(
                description="Whether or not to use cache. If True, cache will store for seven days."
            ),
        ] = True,
        provider: Optional[Literal["sec"]] = None,
        **kwargs
    ) -> OBBject:
        """A tool for navigating the directory of SEC XML schema files by year.

        Parameters
        ----------
        query : str
            Search query.
        use_cache : Optional[bool]
            Whether or not to use cache. If True, cache will store for seven days.
        provider : Optional[Literal['sec']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'sec' if there is
            no default.
        url : Optional[str]
            Enter an optional URL path to fetch the next level. (provider: sec)

        Returns
        -------
        OBBject
            results : SchemaFiles
                Serializable results.
            provider : Optional[Literal['sec']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        SchemaFiles
        -----------
        files : Optional[List]
            Dictionary of URLs to SEC Schema Files (provider: sec)

        Example
        -------
        >>> from openbb import obb
        >>> data = obb.regulators.sec.schema_files()
        >>> data.files[0]
        >>>     https://xbrl.fasb.org/us-gaap/
        >>> #### The directory structure can be navigated by constructing a URL from the 'results' list. ####
        >>> url = data.files[0]+data.files[-1]
        >>> #### The URL base will always be the 0 position in the list, feed  the URL back in as a parameter. ####
        >>> obb.regulators.sec.schema_files(url=url).results.files
        >>>     ['https://xbrl.fasb.org/us-gaap/2024/'
        >>>     'USGAAP2024FileList.xml'
        >>>     'dis/'
        >>>     'dqcrules/'
        >>>     'ebp/'
        >>>     'elts/'
        >>>     'entire/'
        >>>     'meta/'
        >>>     'stm/'
        >>>     'us-gaap-2024.zip']
        """  # noqa: E501

        return self._run(
            "/regulators/sec/schema_files",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/regulators/sec/schema_files",
                        ("sec",),
                    )
                },
                standard_params={
                    "query": query,
                    "use_cache": use_cache,
                },
                extra_params=kwargs,
            )
        )

    @validate
    def sic_search(
        self,
        query: Annotated[str, OpenBBCustomParameter(description="Search query.")] = "",
        use_cache: Annotated[
            Optional[bool],
            OpenBBCustomParameter(
                description="Whether or not to use cache. If True, cache will store for seven days."
            ),
        ] = True,
        provider: Optional[Literal["sec"]] = None,
        **kwargs
    ) -> OBBject:
        """Search for Industry Titles, Reporting Office, and SIC Codes. An empty query string returns all results.

        Parameters
        ----------
        query : str
            Search query.
        use_cache : Optional[bool]
            Whether or not to use cache. If True, cache will store for seven days.
        provider : Optional[Literal['sec']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'sec' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[SicSearch]
                Serializable results.
            provider : Optional[Literal['sec']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        SicSearch
        ---------
        sic : Optional[int]
            Sector Industrial Code (SIC) (provider: sec)
        industry : Optional[str]
            Industry title. (provider: sec)
        office : Optional[str]
            Reporting office within the Corporate Finance Office (provider: sec)

        Example
        -------
        >>> from openbb import obb
        >>> obb.regulators.sec.sic_search("real estate investment trusts").results
        """  # noqa: E501

        return self._run(
            "/regulators/sec/sic_search",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/regulators/sec/sic_search",
                        ("sec",),
                    )
                },
                standard_params={
                    "query": query,
                    "use_cache": use_cache,
                },
                extra_params=kwargs,
            )
        )

    @validate
    def symbol_map(
        self,
        query: Annotated[str, OpenBBCustomParameter(description="Search query.")] = "",
        use_cache: Annotated[
            Optional[bool],
            OpenBBCustomParameter(
                description="Whether or not to use cache. If True, cache will store for seven days."
            ),
        ] = True,
        provider: Optional[Literal["sec"]] = None,
        **kwargs
    ) -> OBBject:
        """Map a CIK number to a ticker symbol, leading 0s can be omitted or included.

        Parameters
        ----------
        query : str
            Search query.
        use_cache : Optional[bool]
            Whether or not to use cache. If True, cache will store for seven days.
        provider : Optional[Literal['sec']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'sec' if there is
            no default.

        Returns
        -------
        OBBject
            results : SymbolMap
                Serializable results.
            provider : Optional[Literal['sec']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        SymbolMap
        ---------
        symbol : Optional[str]
            Symbol representing the entity requested in the data. (provider: sec)

        Example
        -------
        >>> from openbb import obb
        >>> obb.regulators.sec.symbol_map("0000789019").results.symbol
        >>>     MSFT
        """  # noqa: E501

        return self._run(
            "/regulators/sec/symbol_map",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/regulators/sec/symbol_map",
                        ("sec",),
                    )
                },
                standard_params={
                    "query": query,
                    "use_cache": use_cache,
                },
                extra_params=kwargs,
            )
        )
