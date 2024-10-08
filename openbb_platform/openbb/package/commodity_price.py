### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import Literal, Optional, Union

from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_commodity_price(Container):
    """/commodity/price
    spot
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def spot(
        self,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        provider: Annotated[
            Optional[Literal["fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Commodity Spot Prices.

        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        commodity : Literal['wti', 'brent', 'natural_gas', 'jet_fuel', 'propane', 'heating_oil', 'diesel_gulf_coast', 'diesel_ny_harbor', 'diesel_la', 'gasoline_ny_harbor', 'gasoline_gulf_coast', 'rbob', 'all']
            Commodity name associated with the EIA spot price commodity data, default is 'all'. (provider: fred)
        frequency : Optional[Literal['a', 'q', 'm', 'w', 'd', 'wef', 'weth', 'wew', 'wetu', 'wem', 'wesu', 'wesa', 'bwew', 'bwem']]
            Frequency aggregation to convert high frequency data to lower frequency.
                None = No change
                a = Annual
                q = Quarterly
                m = Monthly
                w = Weekly
                d = Daily
                wef = Weekly, Ending Friday
                weth = Weekly, Ending Thursday
                wew = Weekly, Ending Wednesday
                wetu = Weekly, Ending Tuesday
                wem = Weekly, Ending Monday
                wesu = Weekly, Ending Sunday
                wesa = Weekly, Ending Saturday
                bwew = Biweekly, Ending Wednesday
                bwem = Biweekly, Ending Monday
                 (provider: fred)
        aggregation_method : Literal['avg', 'sum', 'eop']
            A key that indicates the aggregation method used for frequency aggregation.
                This parameter has no affect if the frequency parameter is not set.
                avg = Average
                sum = Sum
                eop = End of Period
                 (provider: fred)
        transform : Optional[Literal['chg', 'ch1', 'pch', 'pc1', 'pca', 'cch', 'cca', 'log']]
            Transformation type
                None = No transformation
                chg = Change
                ch1 = Change from Year Ago
                pch = Percent Change
                pc1 = Percent Change from Year Ago
                pca = Compounded Annual Rate of Change
                cch = Continuously Compounded Rate of Change
                cca = Continuously Compounded Annual Rate of Change
                log = Natural Log
                 (provider: fred)

        Returns
        -------
        OBBject
            results : List[CommoditySpotPrices]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CommoditySpotPrices
        -------------------
        date : date
            The date of the data.
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        commodity : Optional[str]
            Commodity name.
        price : float
            Price of the commodity.
        unit : Optional[str]
            Unit of the commodity price.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.commodity.price.spot(provider='fred')
        >>> obb.commodity.price.spot(provider='fred', commodity='wti')
        """  # noqa: E501

        return self._run(
            "/commodity/price/spot",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "commodity.price.spot",
                        ("fred",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={
                    "commodity": {
                        "fred": {
                            "multiple_items_allowed": False,
                            "choices": [
                                "wti",
                                "brent",
                                "natural_gas",
                                "jet_fuel",
                                "propane",
                                "heating_oil",
                                "diesel_gulf_coast",
                                "diesel_ny_harbor",
                                "diesel_la",
                                "gasoline_ny_harbor",
                                "gasoline_gulf_coast",
                                "rbob",
                                "all",
                            ],
                        }
                    },
                    "frequency": {
                        "fred": {
                            "multiple_items_allowed": False,
                            "choices": [
                                "a",
                                "q",
                                "m",
                                "w",
                                "d",
                                "wef",
                                "weth",
                                "wew",
                                "wetu",
                                "wem",
                                "wesu",
                                "wesa",
                                "bwew",
                                "bwem",
                            ],
                        }
                    },
                    "aggregation_method": {
                        "fred": {
                            "multiple_items_allowed": False,
                            "choices": ["avg", "sum", "eop"],
                        }
                    },
                    "transform": {
                        "fred": {
                            "multiple_items_allowed": False,
                            "choices": [
                                "chg",
                                "ch1",
                                "pch",
                                "pc1",
                                "pca",
                                "cch",
                                "cca",
                                "log",
                            ],
                        }
                    },
                },
            )
        )
