### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import Literal, Optional, Union

from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_commodity(Container):
    """/commodity
    petroleum_status_report
    /price
    short_term_energy_outlook
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def petroleum_status_report(
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
            Optional[Literal["eia"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: eia."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """EIA Weekly Petroleum Status Report.

        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['eia']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: eia.
        category : Literal['balance_sheet', 'inputs_and_production', 'refiner_blender_net_production', 'crude_petroleum_stocks', 'gasoline_fuel_stocks', 'total_gasoline_by_sub_padd', 'distillate_fuel_oil_stocks', 'imports', 'imports_by_country', 'weekly_estimates', 'spot_prices_crude_gas_heating', 'spot_prices_diesel_jet_fuel_propane', 'retail_prices']
            The group of data to be returned. The default is the balance sheet. (provider: eia)
        table : Optional[str]
            The specific table element within the category to be returned, default is 'stocks', if the category is 'weekly_estimates', else 'all'.
            Note: Choices represent all available tables from the entire collection and are not all available for every category.
            Invalid choices will raise a ValidationError with a message indicating the valid choices for the selected category.
            Choices are:
                all
                conventional_gas
                crude
                crude_production
                crude_production_avg
                diesel
                ethanol_plant_production
                ethanol_plant_production_avg
                exports
                exports_avg
                heating_oil
                imports
                imports_avg
                imports_by_country
                imports_by_country_avg
                inputs_and_utilization
                inputs_and_utilization_avg
                jet_fuel
                monthly
                net_imports_inc_spr_avg
                net_imports_incl_spr
                net_production
                net_production_avg
                net_production_by_product
                net_production_by_production_avg
                product_by_region
                product_by_region_avg
                product_supplied
                product_supplied_avg
                propane
                rbob
                refiner_blender_net_production
                refiner_blender_net_production_avg
                stocks
                supply
                supply_avg
                ulta_low_sulfur_distillate_reclassification
                ulta_low_sulfur_distillate_reclassification_avg
                weekly
            Multiple comma separated items allowed. (provider: eia)
        use_cache : bool
            Subsequent requests for the same source data are cached for the session using ALRU cache. (provider: eia)

        Returns
        -------
        OBBject
            results : List[PetroleumStatusReport]
                Serializable results.
            provider : Optional[Literal['eia']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        PetroleumStatusReport
        ---------------------
        date : date
            The date of the data.
        table : Optional[str]
            Table name for the data.
        symbol : str
            Symbol representing the entity requested in the data.
        order : Optional[int]
            Presented order of the data, relative to the table.
        title : Optional[str]
            Title of the data.
        value : Union[int, float]
            Value of the data.
        unit : Optional[str]
            Unit or scale of the data.

        Examples
        --------
        >>> from openbb import obb
        >>> # Get the EIA's Weekly Petroleum Status Report.
        >>> obb.commodity.petroleum_status_report(provider='eia')
        >>> # Select the category of data, and filter for a specific table within the report.
        >>> obb.commodity.petroleum_status_report(category='weekly_estimates', table='imports', provider='eia')
        """  # noqa: E501

        return self._run(
            "/commodity/petroleum_status_report",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "commodity.petroleum_status_report",
                        ("eia",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={
                    "category": {
                        "eia": {
                            "multiple_items_allowed": False,
                            "choices": [
                                "balance_sheet",
                                "inputs_and_production",
                                "refiner_blender_net_production",
                                "crude_petroleum_stocks",
                                "gasoline_fuel_stocks",
                                "total_gasoline_by_sub_padd",
                                "distillate_fuel_oil_stocks",
                                "imports",
                                "imports_by_country",
                                "weekly_estimates",
                                "spot_prices_crude_gas_heating",
                                "spot_prices_diesel_jet_fuel_propane",
                                "retail_prices",
                            ],
                        }
                    },
                    "table": {
                        "eia": {
                            "multiple_items_allowed": True,
                            "choices": [
                                "all",
                                "conventional_gas",
                                "crude",
                                "crude_production",
                                "crude_production_avg",
                                "diesel",
                                "ethanol_plant_production",
                                "ethanol_plant_production_avg",
                                "exports",
                                "exports_avg",
                                "heating_oil",
                                "imports",
                                "imports_avg",
                                "imports_by_country",
                                "imports_by_country_avg",
                                "inputs_and_utilization",
                                "inputs_and_utilization_avg",
                                "jet_fuel",
                                "monthly",
                                "net_imports_inc_spr_avg",
                                "net_imports_incl_spr",
                                "net_production",
                                "net_production_avg",
                                "net_production_by_product",
                                "net_production_by_production_avg",
                                "product_by_region",
                                "product_by_region_avg",
                                "product_supplied",
                                "product_supplied_avg",
                                "propane",
                                "rbob",
                                "refiner_blender_net_production",
                                "refiner_blender_net_production_avg",
                                "stocks",
                                "supply",
                                "supply_avg",
                                "ulta_low_sulfur_distillate_reclassification",
                                "ulta_low_sulfur_distillate_reclassification_avg",
                                "weekly",
                            ],
                        }
                    },
                },
            )
        )

    @property
    def price(self):
        # pylint: disable=import-outside-toplevel
        from . import commodity_price

        return commodity_price.ROUTER_commodity_price(
            command_runner=self._command_runner
        )

    @exception_handler
    @validate
    def short_term_energy_outlook(
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
            Optional[Literal["eia"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: eia."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Monthly short term (18 month) projections using EIA's STEO model.

        Source: www.eia.gov/steo/


        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['eia']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: eia.
        symbol : Optional[str]
            Symbol to get data for. If provided, overrides the 'table' parameter to return only the specified symbol from the STEO API. Multiple comma separated items allowed. (provider: eia)
        table : Literal['01', '02', '03a', '03b', '03c', '03d', '03e', '04a', '04b', '04c', '04d', '05a', '05b', '06', '07a', '07b', '07c', '07d1', '07d2', '07e', '08', '09a', '09b', '09c', '10a', '10b']
            The specific table within the STEO dataset. Default is '01'. When 'symbol' is provided, this parameter is ignored.
                01: US Energy Markets Summary
                02: Nominal Energy Prices
                03a: World Petroleum and Other Liquid Fuels Production, Consumption, and Inventories
                03b: Non-OPEC Petroleum and Other Liquid Fuels Production
                03c: World Petroleum and Other Liquid Fuels Production
                03d: World Crude Oil Production
                03e: World Petroleum and Other Liquid Fuels Consumption
                04a: US Petroleum and Other Liquid Fuels Supply, Consumption, and Inventories
                04b: US Hydrocarbon Gas Liquids (HGL) and Petroleum Refinery Balances
                04c: US Regional Motor Gasoline Prices and Inventories
                04d: US Biofuel Supply, Consumption, and Inventories
                05a: US Natural Gas Supply, Consumption, and Inventories
                05b: US Regional Natural Gas Prices
                06: US Coal Supply, Consumption, and Inventories
                07a: US Electricity Industry Overview
                07b: US Regional Electricity Retail Sales
                07c: US Regional Electricity Prices
                07d1: US Regional Electricity Generation, Electric Power Sector
                07d2: US Regional Electricity Generation, Electric Power Sector, continued
                07e: US Electricity Generating Capacity
                08: US Renewable Energy Consumption
                09a: US Macroeconomic Indicators and CO2 Emissions
                09b: US Regional Macroeconomic Data
                09c: US Regional Weather Data
                10a: Drilling Productivity Metrics
                10b: Crude Oil and Natural Gas Production from Shale and Tight Formations (provider: eia)
        frequency : Literal['month', 'quarter', 'annual']
            The frequency of the data. Default is 'month'. (provider: eia)

        Returns
        -------
        OBBject
            results : List[ShortTermEnergyOutlook]
                Serializable results.
            provider : Optional[Literal['eia']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        ShortTermEnergyOutlook
        ----------------------
        date : date
            The date of the data.
        table : Optional[str]
            Table name for the data.
        symbol : str
            Symbol representing the entity requested in the data.
        order : Optional[int]
            Presented order of the data, relative to the table.
        title : Optional[str]
            Title of the data.
        value : Union[int, float]
            Value of the data.
        unit : Optional[str]
            Unit or scale of the data.

        Examples
        --------
        >>> from openbb import obb
        >>> # Get the EIA's Short Term Energy Outlook.
        >>> obb.commodity.short_term_energy_outlook(provider='eia')
        >>> # Select the specific table of data from the STEO. Table 03d is World Crude Oil Production.
        >>> obb.commodity.short_term_energy_outlook(table='03d', provider='eia')
        """  # noqa: E501

        return self._run(
            "/commodity/short_term_energy_outlook",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "commodity.short_term_energy_outlook",
                        ("eia",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={
                    "symbol": {
                        "eia": {"multiple_items_allowed": True, "choices": None}
                    },
                    "table": {
                        "eia": {
                            "multiple_items_allowed": False,
                            "choices": [
                                "01",
                                "02",
                                "03a",
                                "03b",
                                "03c",
                                "03d",
                                "03e",
                                "04a",
                                "04b",
                                "04c",
                                "04d",
                                "05a",
                                "05b",
                                "06",
                                "07a",
                                "07b",
                                "07c",
                                "07d1",
                                "07d2",
                                "07e",
                                "08",
                                "09a",
                                "09b",
                                "09c",
                                "10a",
                                "10b",
                            ],
                        }
                    },
                    "frequency": {
                        "eia": {
                            "multiple_items_allowed": False,
                            "choices": ["month", "quarter", "annual"],
                        }
                    },
                },
            )
        )
