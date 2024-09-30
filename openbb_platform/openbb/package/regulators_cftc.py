### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import Literal, Optional, Union

from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_regulators_cftc(Container):
    """/regulators/cftc
    cot
    cot_search
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def cot(
        self,
        id: Annotated[str, OpenBBField(description="A string with the CFTC market code or other identifying string, such as the contract market name, commodity name, or commodity group - i.e, 'gold' or 'japanese yen'.Default report is Fed Funds Futures. Use the 'cftc_market_code' for an exact match.")] = "045601",
        start_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="Start date of the data, in YYYY-MM-DD format. Default is the most recent report.")] = None,
        end_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="End date of the data, in YYYY-MM-DD format.")] = None,
        provider: Annotated[Optional[Literal["cftc"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: cftc.")] = None,
        **kwargs
    ) -> OBBject:
        """Get Commitment of Traders Reports.

        Parameters
        ----------
        id : str
            A string with the CFTC market code or other identifying string, such as the contract market name, commodity name, or commodity group - i.e, 'gold' or 'japanese yen'.Default report is Fed Funds Futures. Use the 'cftc_market_code' for an exact match.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format. Default is the most recent report.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['cftc']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: cftc.
        report_type : Literal['legacy', 'disaggregated', 'financial', 'supplemental']
            The type of report to retrieve. Set `id` as 'all' to return all items in the report
                    type (default date range returns the latest report). The Legacy report is broken down by exchange
                    with reported open interest further broken down into three trader classifications: commercial,
                    non-commercial and non-reportable. The Disaggregated reports are broken down by Agriculture and
                    Natural Resource contracts. The Disaggregated reports break down reportable open interest positions
                    into four classifications: Producer/Merchant, Swap Dealers, Managed Money and Other Reportables.
                    The Traders in Financial Futures (TFF) report includes financial contracts. The TFF report breaks
                    down the reported open interest into five classifications: Dealer, Asset Manager, Leveraged Money,
                    Other Reportables and Non-Reportables. (provider: cftc)
        futures_only : bool
            Returns the futures-only report. Default is False, for the combined report. (provider: cftc)

        Returns
        -------
        OBBject
            results : List[COT]
                Serializable results.
            provider : Optional[Literal['cftc']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        COT
        ---
        date : date
            The date of the data. 
        report_week : Optional[str]
            Report week for the year. 
        market_and_exchange_names : Optional[str]
            Market and exchange names. 
        cftc_contract_market_code : Optional[str]
            CFTC contract market code. 
        cftc_market_code : Optional[str]
            CFTC market code. 
        cftc_region_code : Optional[str]
            CFTC region code. 
        cftc_commodity_code : Optional[str]
            CFTC commodity code. 
        cftc_contract_market_code_quotes : Optional[str]
            CFTC contract market code quotes. 
        cftc_market_code_quotes : Optional[str]
            CFTC market code quotes. 
        cftc_commodity_code_quotes : Optional[str]
            CFTC commodity code quotes. 
        cftc_subgroup_code : Optional[str]
            CFTC subgroup code. 
        commodity : Optional[str]
            Commodity. 
        commodity_group : Optional[str]
            Commodity group name. 
        commodity_subgroup : Optional[str]
            Commodity subgroup name. 
        futonly_or_combined : Optional[str]
            If the report is futures-only or combined. 
        contract_units : Optional[str]
            Contract units. 

        Examples
        --------
        >>> from openbb import obb
        >>> # Get the latest report for all items classified as, GOLD.
        >>> obb.regulators.cftc.cot(id='gold', provider='cftc')
        >>> # Enter the entire history for a single CFTC Market Contract Code.
        >>> obb.regulators.cftc.cot(id='088691', provider='cftc')
        >>> # Get the report for futures only.
        >>> obb.regulators.cftc.cot(id='088691', futures_only=True, provider='cftc')
        >>> # Get the most recent Commodity Index Traders Supplemental Report.
        >>> obb.regulators.cftc.cot(id='all', report_type='supplemental', provider='cftc')
        """  # noqa: E501

        return self._run(
            "/regulators/cftc/cot",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "regulators.cftc.cot",
                        ("cftc",),
                    )
                },
                standard_params={
                    "id": id,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={"report_type": {"cftc": {"multiple_items_allowed": False, "choices": ["legacy", "disaggregated", "financial", "supplemental"]}}},
            )
        )

    @exception_handler
    @validate
    def cot_search(
        self,
        query: Annotated[str, OpenBBField(description="Search query.")] = "",
        provider: Annotated[Optional[Literal["cftc"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: cftc.")] = None,
        **kwargs
    ) -> OBBject:
        """Get the current Commitment of Traders Reports.

        Search a list of the current Commitment of Traders Reports series information.
        

        Parameters
        ----------
        query : str
            Search query.
        provider : Optional[Literal['cftc']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: cftc.

        Returns
        -------
        OBBject
            results : List[COTSearch]
                Serializable results.
            provider : Optional[Literal['cftc']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        COTSearch
        ---------
        code : str
            CFTC market contract code of the report. 
        name : str
            Name of the underlying asset. 
        category : Optional[str]
            Category of the underlying asset. 
        subcategory : Optional[str]
            Subcategory of the underlying asset. 
        units : Optional[str]
            The units for one contract. 
        symbol : Optional[str]
            Symbol representing the entity requested in the data. 
        commodity : Optional[str]
            Name of the commodity. (provider: cftc)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.regulators.cftc.cot_search(provider='cftc')
        >>> obb.regulators.cftc.cot_search(query='gold', provider='cftc')
        """  # noqa: E501

        return self._run(
            "/regulators/cftc/cot_search",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "regulators.cftc.cot_search",
                        ("cftc",),
                    )
                },
                standard_params={
                    "query": query,
                },
                extra_params=kwargs,
            )
        )
