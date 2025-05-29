### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import Literal, Optional, Union

from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_economy_shipping(Container):
    """/economy/shipping
    chokepoint_info
    chokepoint_volume
    port_info
    port_volume
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def chokepoint_info(
        self,
        provider: Annotated[
            Optional[Literal["imf"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: imf."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get general metadata and statistics for all maritime chokepoint locations from a given provider.

        Parameters
        ----------
        provider : str
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: imf.
        theme : Optional[Literal['dark', 'light']]
            Theme for the map. Only valid if `openbb-charting` is installed and `chart` parameter is set to `true`. Default is the 'chart_style' setting in `user_settings.json`, if available, otherwise 'dark'. (provider: imf)

        Returns
        -------
        OBBject
            results : list[MaritimeChokePointInfo]
                Serializable results.
            provider : Optional[str]
                Provider name.
            warnings : Optional[list[Warning_]]
                list of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        MaritimeChokePointInfo
        ----------------------
        chokepoint_code : str
            Unique ID assigned to the chokepoint by the source.
        name : Optional[str]
            Port name. (provider: imf)
        latitude : Optional[float]
            Latitude of the chokepoint location. (provider: imf)
        longitude : Optional[float]
            Longitude of the chokepoint location. (provider: imf)
        vessel_count_total : Optional[int]
            Yearly average number of all ships transiting through the chokepoint. Estimated using AIS data beginning 2019. The total is calculated over the sum of vessel_count_container, vessel_count_dry_bulk, vessel_count_general_cargo, vessel_count_roro and vessel_count_tanker. (provider: imf)
        vessel_count_tanker : Optional[int]
            Yearly average number of tankers transiting through the chokepoint. Estimated using AIS data beginning 2019. (provider: imf)
        vessel_count_container : Optional[int]
            Yearly average number of containers transiting through the chokepoint. Estimated using AIS data beginning 2019. (provider: imf)
        vessel_count_general_cargo : Optional[int]
            Yearly average number of general cargo ships transiting through the chokepoint. Estimated using AIS data beginning 2019. (provider: imf)
        vessel_count_dry_bulk : Optional[int]
            Yearly average number of dry bulk carriers transiting through the chokepoint. Estimated using AIS data beginning 2019. (provider: imf)
        vessel_count_roro : Optional[int]
            Yearly average number of Ro-Ro ships transiting through the chokepoint. Estimated using AIS data beginning 2019. (provider: imf)
        industry_top1 : Optional[str]
            First dominant traded industries based on the volume of goods estimated to flow through the chokepoint. (provider: imf)
        industry_top2 : Optional[str]
            Second dominant traded industries based on the volume of goods estimated to flow through the chokepoint. (provider: imf)
        industry_top3 : Optional[str]
            Third dominant traded industries based on the volume of goods estimated to flow through the chokepoint. (provider: imf)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.shipping.chokepoint_info(provider='imf')
        """  # noqa: E501

        return self._run(
            "/economy/shipping/chokepoint_info",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.shipping.chokepoint_info",
                        ("imf",),
                    )
                },
                standard_params={},
                extra_params=kwargs,
                info={"theme": {"imf": {"x-widget_config": {"show": False}}}},
            )
        )

    @exception_handler
    @validate
    def chokepoint_volume(
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
            Optional[Literal["imf"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: imf."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Daily transit calls and estimates of transit trade volumes for shipping lane chokepoints around the world.

        Parameters
        ----------
        provider : str
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: imf.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        chokepoint : Optional[str]
            Name of the chokepoint. Use `None` for all chokepoints. Choices are:
                - suez_canal
                - panama_canal
                - bosporus_strait
                - bab_el_mandeb_strait
                - malacca_strait
                - strait_of_hormuz
                - cape_of_good_hope
                - gibraltar_strait
                - dover_strait
                - oresund_strait
                - taiwan_strait
                - korea_strait
                - tsugaru_strait
                - luzon_strait
                - lombok_strait
                - ombai_strait
                - bohai_strait
                - torres_strait
                - sunda_strait
                - makassar_strait
                - magellan_strait
                - yucatan_channel
                - windward_passage
                - mona_passage

             Multiple comma separated items allowed. (provider: imf)

        Returns
        -------
        OBBject
            results : list[MaritimeChokePointVolume]
                Serializable results.
            provider : Optional[str]
                Provider name.
            warnings : Optional[list[Warning_]]
                list of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        MaritimeChokePointVolume
        ------------------------
        date : date
            The date of the data.
        chokepoint : Optional[str]
            Name of the chokepoint. (provider: imf)
        vessels_total : Optional[int]
            Number of all ships transiting through the chokepoint on that date. The total is calculated over the sum of vessels_container, vessels_dry_bulk, vessels_general_cargo, vessels_roro and vessels_tanker. (provider: imf)
        vessels_cargo : Optional[int]
            Total number of ships (excluding tankers) transiting through the chokepoint at this date. This is the sum of vessels_container, vessels_dry_bulk, vessels_general_cargo and vessels_roro. (provider: imf)
        vessels_tanker : Optional[int]
            Number of tankers transiting through the chokepoint on that date. (provider: imf)
        vessels_container : Optional[int]
            Number of containers transiting through the chokepoint on that date. (provider: imf)
        vessels_general_cargo : Optional[int]
            Number of general cargo ships transiting through the chokepoint on that date. (provider: imf)
        vessels_dry_bulk : Optional[int]
            Yearly average number of dry bulk carriers transiting through the chokepoint. Estimated using AIS data beginning 2019. (provider: imf)
        vessels_roro : Optional[int]
            Yearly average number of Ro-Ro ships transiting through the chokepoint. Estimated using AIS data beginning 2019. (provider: imf)
        capacity_total : Optional[float]
            Total trade volume (in metric tons) of all ships transiting through the chokepoint at this date. This is the sum of capacity_container, capacity_dry_bulk, capacity_general_cargo, capacity_roro and capacity_tanker. (provider: imf)
        capacity_cargo : Optional[float]
            Total trade volume (in metric tons) of all ships (excluding tankers) transiting through the chokepoint at this date. This is the sum of capacity_container, capacity_dry_bulk, capacity_general_cargo and capacity_roro. (provider: imf)
        capacity_tanker : Optional[float]
            Total trade volume (in metric tons) of tankers transiting through the chokepoint at this date. (provider: imf)
        capacity_container : Optional[float]
            Total trade volume (in metric tons) of containers transiting through the chokepoint at this date. (provider: imf)
        capacity_general_cargo : Optional[float]
            Total trade volume (in metric tons) of general cargo Vessels transiting through the chokepoint at this date. (provider: imf)
        capacity_dry_bulk : Optional[float]
            Total trade volume (in metric tons) of dry bulk carriers transiting through the chokepoint at this date. (provider: imf)
        capacity_roro : Optional[float]
            Total trade volume (in metric tons) of Ro-Ro ships transiting through the chokepoint at this date. (provider: imf)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.shipping.chokepoint_volume(provider='imf')
        >>> obb.economy.shipping.chokepoint_volume(provider='imf', chokepoint='suez_canal,panama_canal')
        """  # noqa: E501

        return self._run(
            "/economy/shipping/chokepoint_volume",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.shipping.chokepoint_volume",
                        ("imf",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={
                    "chokepoint": {
                        "imf": {
                            "multiple_items_allowed": True,
                            "choices": None,
                            "x-widget_config": {
                                "options": [
                                    {"label": "Suez Canal", "value": "chokepoint1"},
                                    {"label": "Panama Canal", "value": "chokepoint2"},
                                    {
                                        "label": "Bosporus Strait",
                                        "value": "chokepoint3",
                                    },
                                    {
                                        "label": "Bab El-Mandeb Strait",
                                        "value": "chokepoint4",
                                    },
                                    {"label": "Malacca Strait", "value": "chokepoint5"},
                                    {
                                        "label": "Strait Of Hormuz",
                                        "value": "chokepoint6",
                                    },
                                    {
                                        "label": "Cape Of Good Hope",
                                        "value": "chokepoint7",
                                    },
                                    {
                                        "label": "Gibraltar Strait",
                                        "value": "chokepoint8",
                                    },
                                    {"label": "Dover Strait", "value": "chokepoint9"},
                                    {
                                        "label": "Oresund Strait",
                                        "value": "chokepoint10",
                                    },
                                    {"label": "Taiwan Strait", "value": "chokepoint11"},
                                    {"label": "Korea Strait", "value": "chokepoint12"},
                                    {
                                        "label": "Tsugaru Strait",
                                        "value": "chokepoint13",
                                    },
                                    {"label": "Luzon Strait", "value": "chokepoint14"},
                                    {"label": "Lombok Strait", "value": "chokepoint15"},
                                    {"label": "Ombai Strait", "value": "chokepoint16"},
                                    {"label": "Bohai Strait", "value": "chokepoint17"},
                                    {"label": "Torres Strait", "value": "chokepoint18"},
                                    {"label": "Sunda Strait", "value": "chokepoint19"},
                                    {
                                        "label": "Makassar Strait",
                                        "value": "chokepoint20",
                                    },
                                    {
                                        "label": "Magellan Strait",
                                        "value": "chokepoint21",
                                    },
                                    {
                                        "label": "Yucatan Channel",
                                        "value": "chokepoint22",
                                    },
                                    {
                                        "label": "Windward Passage",
                                        "value": "chokepoint23",
                                    },
                                    {"label": "Mona Passage", "value": "chokepoint24"},
                                ],
                                "description": "Name of the chokepoint. No selection will return data for all chokepoints.",
                            },
                        }
                    }
                },
            )
        )

    @exception_handler
    @validate
    def port_info(
        self,
        provider: Annotated[
            Optional[Literal["imf"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: imf."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get general metadata and statistics for all ports from a given provider.

        Parameters
        ----------
        provider : str
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: imf.
        continent : Optional[Literal['north_america', 'europe', 'asia_pacific', 'south_america', 'africa']]
            Filter by continent. This parameter is ignored when a `country` is provided. (provider: imf)
        country : Optional[Literal['ABW', 'AGO', 'AIA', 'ALB', 'ARE', 'ARG', 'ASM', 'ATG', 'AUS', 'AZE', 'BEL', 'BEN', 'BES', 'BGD', 'BGR', 'BHR', 'BHS', 'BLM', 'BLZ', 'BRA', 'BRB', 'BRN', 'CAN', 'CHL', 'CHN', 'CIV', 'CMR', 'COD', 'COG', 'COK', 'COL', 'COM', 'CPV', 'CRI', 'CUB', 'CUW', 'CYM', 'CYP', 'DEU', 'DJI', 'DMA', 'DNK', 'DOM', 'DZA', 'ECU', 'EGY', 'ERI', 'ESP', 'EST', 'FIN', 'FJI', 'FRA', 'FRO', 'FSM', 'GAB', 'GBR', 'GEO', 'GHA', 'GIB', 'GIN', 'GLP', 'GMB', 'GNB', 'GNQ', 'GRC', 'GRD', 'GTM', 'GUF', 'GUM', 'GUY', 'HKG', 'HND', 'HRV', 'HTI', 'IDN', 'IND', 'IRL', 'IRN', 'IRQ', 'ISL', 'ISR', 'ITA', 'JAM', 'JOR', 'JPN', 'KAZ', 'KEN', 'KHM', 'KIR', 'KNA', 'KOR', 'KWT', 'LBN', 'LBR', 'LBY', 'LCA', 'LKA', 'LTU', 'LVA', 'MAC', 'MAF', 'MAR', 'MDA', 'MDG', 'MDV', 'MEX', 'MHL', 'MLT', 'MMR', 'MNE', 'MNP', 'MOZ', 'MRT', 'MSR', 'MTQ', 'MUS', 'MYS', 'MYT', 'NAM', 'NCL', 'NGA', 'NIC', 'NLD', 'NOR', 'NRU', 'NZL', 'OMN', 'PAK', 'PAN', 'PER', 'PHL', 'PLW', 'PNG', 'POL', 'PRI', 'PRT', 'PYF', 'QAT', 'REU', 'ROU', 'RUS', 'SAU', 'SDN', 'SEN', 'SGP', 'SLB', 'SLE', 'SLV', 'SOM', 'STP', 'SUR', 'SVN', 'SWE', 'SXM', 'SYC', 'SYR', 'TCA', 'TGO', 'THA', 'TKM', 'TLS', 'TON', 'TTO', 'TUN', 'TUR', 'TUV', 'TWN', 'TZA', 'UKR', 'URY', 'USA', 'VCT', 'VEN', 'VGB', 'VIR', 'VNM', 'VUT', 'WSM', 'YEM', 'ZAF']]
            Country to focus on. Enter as a 3-letter ISO country code. This parameter supercedes `continent` if both are provided. (provider: imf)
        limit : Optional[int]
            Limit the number of results returned. Limit is determined by the annual average number of vessels transiting through the port. If not provided, all ports are returned. (provider: imf)

        Returns
        -------
        OBBject
            results : list[PortInfo]
                Serializable results.
            provider : Optional[str]
                Provider name.
            warnings : Optional[list[Warning_]]
                list of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        PortInfo
        --------
        port_code : str
            Unique ID assigned to the port by the source.
        continent : Optional[str]
            Continent where the port is located. (provider: imf)
        country : Optional[str]
            Country where the port is located. (provider: imf)
        country_code : Optional[str]
            3-letter ISO code of the country where the port is located. (provider: imf)
        port_name : Optional[str]
            Port name. (provider: imf)
        port_full_name : Optional[str]
            Full name of the port. (provider: imf)
        latitude : Optional[float]
            Latitude of the port. (provider: imf)
        longitude : Optional[float]
            Longitude of the port. (provider: imf)
        vessel_count_total : Optional[int]
            Yearly average number of all ships transiting through the port. Estimated using AIS data beginning 2019. The total is calculated over the sum of vessel_count_container, vessel_count_dry_bulk, vessel_count_general_cargo, vessel_count_roro and vessel_count_tanker. (provider: imf)
        vessel_count_tanker : Optional[int]
            Yearly average number of tankers transiting through the port. Estimated using AIS data beginning 2019. (provider: imf)
        vessel_count_container : Optional[int]
            Yearly average number of containers transiting through the port. Estimated using AIS data beginning 2019. (provider: imf)
        vessel_count_general_cargo : Optional[int]
            Yearly average number of general cargo ships transiting through the port. Estimated using AIS data beginning 2019. (provider: imf)
        vessel_count_dry_bulk : Optional[int]
            Yearly average number of dry bulk carriers transiting through the port. Estimated using AIS data beginning 2019. (provider: imf)
        vessel_count_roro : Optional[int]
            Yearly average number of Ro-Ro ships transiting through the port. Estimated using AIS data beginning 2019. (provider: imf)
        industry_top1 : Optional[str]
            First dominant traded industries based on the volume of goods estimated to flow through the port. (provider: imf)
        industry_top2 : Optional[str]
            Second dominant traded industries based on the volume of goods estimated to flow through the port. (provider: imf)
        industry_top3 : Optional[str]
            Third dominant traded industries based on the volume of goods estimated to flow through the port. (provider: imf)
        share_country_maritime_import : Optional[float]
            Share of the total maritime imports of the country that are estimated to flow through the port. (provider: imf)
        share_country_maritime_export : Optional[float]
            Share of the total maritime exports of the country that are estimated to flow through the port. (provider: imf)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.shipping.port_info(provider='imf')
        >>> obb.economy.shipping.port_info(provider='imf', continent='asia_pacific')
        """  # noqa: E501

        return self._run(
            "/economy/shipping/port_info",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.shipping.port_info",
                        ("imf",),
                    )
                },
                standard_params={},
                extra_params=kwargs,
                info={
                    "continent": {
                        "imf": {
                            "x-widget_config": {
                                "options": [
                                    {
                                        "label": "North America",
                                        "value": "north_america",
                                    },
                                    {"label": "Europe", "value": "europe"},
                                    {
                                        "label": "Asia & Pacific",
                                        "value": "asia_pacific",
                                    },
                                    {
                                        "label": "South America",
                                        "value": "south_america",
                                    },
                                    {"label": "Africa", "value": "africa"},
                                ]
                            }
                        }
                    },
                    "country": {
                        "imf": {
                            "x-widget_config": {
                                "options": [
                                    {"label": "Albania", "value": "ALB"},
                                    {"label": "Algeria", "value": "DZA"},
                                    {"label": "American Samoa", "value": "ASM"},
                                    {"label": "Angola", "value": "AGO"},
                                    {"label": "Anguilla", "value": "AIA"},
                                    {"label": "Antigua and Barbuda", "value": "ATG"},
                                    {"label": "Argentina", "value": "ARG"},
                                    {"label": "Aruba", "value": "ABW"},
                                    {"label": "Australia", "value": "AUS"},
                                    {"label": "Azerbaijan", "value": "AZE"},
                                    {"label": "Bahrain", "value": "BHR"},
                                    {"label": "Bangladesh", "value": "BGD"},
                                    {"label": "Barbados", "value": "BRB"},
                                    {"label": "Belgium", "value": "BEL"},
                                    {"label": "Belize", "value": "BLZ"},
                                    {"label": "Benin", "value": "BEN"},
                                    {
                                        "label": "Bonaire, Saint Eustatius and Saba",
                                        "value": "BES",
                                    },
                                    {"label": "Brazil", "value": "BRA"},
                                    {"label": "British Virgin Islands", "value": "VGB"},
                                    {"label": "Brunei Darussalam", "value": "BRN"},
                                    {"label": "Bulgaria", "value": "BGR"},
                                    {"label": "Cabo Verde", "value": "CPV"},
                                    {"label": "Cambodia", "value": "KHM"},
                                    {"label": "Cameroon", "value": "CMR"},
                                    {"label": "Canada", "value": "CAN"},
                                    {"label": "Cayman Islands", "value": "CYM"},
                                    {"label": "Chile", "value": "CHL"},
                                    {"label": "China", "value": "CHN"},
                                    {"label": "Colombia", "value": "COL"},
                                    {"label": "Comoros", "value": "COM"},
                                    {"label": "Cook Islands", "value": "COK"},
                                    {"label": "Costa Rica", "value": "CRI"},
                                    {"label": "Croatia", "value": "HRV"},
                                    {"label": "Cuba", "value": "CUB"},
                                    {"label": "Curaçao", "value": "CUW"},
                                    {"label": "Cyprus", "value": "CYP"},
                                    {"label": "Côte d'Ivoire", "value": "CIV"},
                                    {
                                        "label": "Democratic Republic of the Congo",
                                        "value": "COD",
                                    },
                                    {"label": "Denmark", "value": "DNK"},
                                    {"label": "Djibouti", "value": "DJI"},
                                    {"label": "Dominica", "value": "DMA"},
                                    {"label": "Dominican Republic", "value": "DOM"},
                                    {"label": "Ecuador", "value": "ECU"},
                                    {"label": "Egypt", "value": "EGY"},
                                    {"label": "El Salvador", "value": "SLV"},
                                    {"label": "Equatorial Guinea", "value": "GNQ"},
                                    {"label": "Eritrea", "value": "ERI"},
                                    {"label": "Estonia", "value": "EST"},
                                    {"label": "Faroe Islands", "value": "FRO"},
                                    {"label": "Fiji", "value": "FJI"},
                                    {"label": "Finland", "value": "FIN"},
                                    {"label": "France", "value": "FRA"},
                                    {"label": "French Guiana", "value": "GUF"},
                                    {"label": "French Polynesia", "value": "PYF"},
                                    {"label": "Gabon", "value": "GAB"},
                                    {"label": "Georgia", "value": "GEO"},
                                    {"label": "Germany", "value": "DEU"},
                                    {"label": "Ghana", "value": "GHA"},
                                    {"label": "Gibraltar", "value": "GIB"},
                                    {"label": "Greece", "value": "GRC"},
                                    {"label": "Grenada", "value": "GRD"},
                                    {"label": "Guadeloupe", "value": "GLP"},
                                    {"label": "Guam", "value": "GUM"},
                                    {"label": "Guatemala", "value": "GTM"},
                                    {"label": "Guinea", "value": "GIN"},
                                    {"label": "Guinea-Bissau", "value": "GNB"},
                                    {"label": "Guyana", "value": "GUY"},
                                    {"label": "Haiti", "value": "HTI"},
                                    {"label": "Honduras", "value": "HND"},
                                    {"label": "Hong Kong SAR", "value": "HKG"},
                                    {"label": "Iceland", "value": "ISL"},
                                    {"label": "India", "value": "IND"},
                                    {"label": "Indonesia", "value": "IDN"},
                                    {"label": "Iran", "value": "IRN"},
                                    {"label": "Iraq", "value": "IRQ"},
                                    {"label": "Ireland", "value": "IRL"},
                                    {"label": "Israel", "value": "ISR"},
                                    {"label": "Italy", "value": "ITA"},
                                    {"label": "Jamaica", "value": "JAM"},
                                    {"label": "Japan", "value": "JPN"},
                                    {"label": "Jordan", "value": "JOR"},
                                    {"label": "Kazakhstan", "value": "KAZ"},
                                    {"label": "Kenya", "value": "KEN"},
                                    {"label": "Kiribati", "value": "KIR"},
                                    {"label": "Korea", "value": "KOR"},
                                    {"label": "Kuwait", "value": "KWT"},
                                    {"label": "Latvia", "value": "LVA"},
                                    {"label": "Lebanon", "value": "LBN"},
                                    {"label": "Liberia", "value": "LBR"},
                                    {"label": "Libya", "value": "LBY"},
                                    {"label": "Lithuania", "value": "LTU"},
                                    {"label": "Macao SAR", "value": "MAC"},
                                    {"label": "Madagascar", "value": "MDG"},
                                    {"label": "Malaysia", "value": "MYS"},
                                    {"label": "Maldives", "value": "MDV"},
                                    {"label": "Malta", "value": "MLT"},
                                    {"label": "Marshall Islands", "value": "MHL"},
                                    {"label": "Martinique", "value": "MTQ"},
                                    {"label": "Mauritania", "value": "MRT"},
                                    {"label": "Mauritius", "value": "MUS"},
                                    {"label": "Mayotte", "value": "MYT"},
                                    {"label": "Mexico", "value": "MEX"},
                                    {"label": "Micronesia", "value": "FSM"},
                                    {"label": "Moldova", "value": "MDA"},
                                    {"label": "Montenegro", "value": "MNE"},
                                    {"label": "Montserrat", "value": "MSR"},
                                    {"label": "Morocco", "value": "MAR"},
                                    {"label": "Mozambique", "value": "MOZ"},
                                    {"label": "Myanmar", "value": "MMR"},
                                    {"label": "Namibia", "value": "NAM"},
                                    {"label": "Nauru", "value": "NRU"},
                                    {"label": "New Caledonia", "value": "NCL"},
                                    {"label": "New Zealand", "value": "NZL"},
                                    {"label": "Nicaragua", "value": "NIC"},
                                    {"label": "Nigeria", "value": "NGA"},
                                    {
                                        "label": "Northern Mariana Islands",
                                        "value": "MNP",
                                    },
                                    {"label": "Norway", "value": "NOR"},
                                    {"label": "Oman", "value": "OMN"},
                                    {"label": "Pakistan", "value": "PAK"},
                                    {"label": "Palau", "value": "PLW"},
                                    {"label": "Panama", "value": "PAN"},
                                    {"label": "Papua New Guinea", "value": "PNG"},
                                    {"label": "Peru", "value": "PER"},
                                    {"label": "Philippines", "value": "PHL"},
                                    {"label": "Poland", "value": "POL"},
                                    {"label": "Portugal", "value": "PRT"},
                                    {"label": "Puerto Rico", "value": "PRI"},
                                    {"label": "Qatar", "value": "QAT"},
                                    {"label": "Republic of Congo", "value": "COG"},
                                    {"label": "Romania", "value": "ROU"},
                                    {"label": "Russian Federation", "value": "RUS"},
                                    {"label": "Réunion", "value": "REU"},
                                    {"label": "Saint Martin", "value": "MAF"},
                                    {"label": "Saint-Barthélemy", "value": "BLM"},
                                    {"label": "Samoa", "value": "WSM"},
                                    {"label": "Saudi Arabia", "value": "SAU"},
                                    {"label": "Senegal", "value": "SEN"},
                                    {"label": "Seychelles", "value": "SYC"},
                                    {"label": "Sierra Leone", "value": "SLE"},
                                    {"label": "Singapore", "value": "SGP"},
                                    {"label": "Sint Maarten", "value": "SXM"},
                                    {"label": "Slovenia", "value": "SVN"},
                                    {"label": "Solomon Islands", "value": "SLB"},
                                    {"label": "Somalia", "value": "SOM"},
                                    {"label": "South Africa", "value": "ZAF"},
                                    {"label": "Spain", "value": "ESP"},
                                    {"label": "Sri Lanka", "value": "LKA"},
                                    {"label": "St. Kitts and Nevis", "value": "KNA"},
                                    {"label": "St. Lucia", "value": "LCA"},
                                    {
                                        "label": "St. Vincent and the Grenadines",
                                        "value": "VCT",
                                    },
                                    {"label": "Sudan", "value": "SDN"},
                                    {"label": "Suriname", "value": "SUR"},
                                    {"label": "Sweden", "value": "SWE"},
                                    {"label": "Syria", "value": "SYR"},
                                    {"label": "São Tomé and Príncipe", "value": "STP"},
                                    {
                                        "label": "Taiwan Province of China",
                                        "value": "TWN",
                                    },
                                    {"label": "Tanzania", "value": "TZA"},
                                    {"label": "Thailand", "value": "THA"},
                                    {"label": "The Bahamas", "value": "BHS"},
                                    {"label": "The Gambia", "value": "GMB"},
                                    {"label": "The Netherlands", "value": "NLD"},
                                    {"label": "Timor-Leste", "value": "TLS"},
                                    {"label": "Togo", "value": "TGO"},
                                    {"label": "Tonga", "value": "TON"},
                                    {"label": "Trinidad and Tobago", "value": "TTO"},
                                    {"label": "Tunisia", "value": "TUN"},
                                    {"label": "Turkmenistan", "value": "TKM"},
                                    {
                                        "label": "Turks and Caicos Islands",
                                        "value": "TCA",
                                    },
                                    {"label": "Tuvalu", "value": "TUV"},
                                    {"label": "Türkiye", "value": "TUR"},
                                    {"label": "Ukraine", "value": "UKR"},
                                    {"label": "United Arab Emirates", "value": "ARE"},
                                    {"label": "United Kingdom", "value": "GBR"},
                                    {"label": "United States", "value": "USA"},
                                    {
                                        "label": "United States Virgin Islands",
                                        "value": "VIR",
                                    },
                                    {"label": "Uruguay", "value": "URY"},
                                    {"label": "Vanuatu", "value": "VUT"},
                                    {"label": "Venezuela", "value": "VEN"},
                                    {"label": "Vietnam", "value": "VNM"},
                                    {"label": "World", "value": "WLD"},
                                    {"label": "Yemen", "value": "YEM"},
                                ],
                                "description": "Filter by country. This parameter supercedes `continent` if both are provided.",
                                "style": {"popupWidth": 350},
                            }
                        }
                    },
                },
            )
        )

    @exception_handler
    @validate
    def port_volume(
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
            Optional[Literal["econdb", "imf"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: econdb, imf."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Daily port calls and estimates of trading volumes for ports around the world.

        Parameters
        ----------
        provider : str
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: econdb, imf.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        port_code : Optional[str]
            Port code to filter results by a specific port. This parameter is ignored if `country` parameter is provided. To get a list of available ports, use `obb.economy.shipping.port_info()`. Multiple comma separated items allowed. (provider: imf)
        country : Optional[Literal['ABW', 'AGO', 'AIA', 'ALB', 'ARE', 'ARG', 'ASM', 'ATG', 'AUS', 'AZE', 'BEL', 'BEN', 'BES', 'BGD', 'BGR', 'BHR', 'BHS', 'BLM', 'BLZ', 'BRA', 'BRB', 'BRN', 'CAN', 'CHL', 'CHN', 'CIV', 'CMR', 'COD', 'COG', 'COK', 'COL', 'COM', 'CPV', 'CRI', 'CUB', 'CUW', 'CYM', 'CYP', 'DEU', 'DJI', 'DMA', 'DNK', 'DOM', 'DZA', 'ECU', 'EGY', 'ERI', 'ESP', 'EST', 'FIN', 'FJI', 'FRA', 'FRO', 'FSM', 'GAB', 'GBR', 'GEO', 'GHA', 'GIB', 'GIN', 'GLP', 'GMB', 'GNB', 'GNQ', 'GRC', 'GRD', 'GTM', 'GUF', 'GUM', 'GUY', 'HKG', 'HND', 'HRV', 'HTI', 'IDN', 'IND', 'IRL', 'IRN', 'IRQ', 'ISL', 'ISR', 'ITA', 'JAM', 'JOR', 'JPN', 'KAZ', 'KEN', 'KHM', 'KIR', 'KNA', 'KOR', 'KWT', 'LBN', 'LBR', 'LBY', 'LCA', 'LKA', 'LTU', 'LVA', 'MAC', 'MAF', 'MAR', 'MDA', 'MDG', 'MDV', 'MEX', 'MHL', 'MLT', 'MMR', 'MNE', 'MNP', 'MOZ', 'MRT', 'MSR', 'MTQ', 'MUS', 'MYS', 'MYT', 'NAM', 'NCL', 'NGA', 'NIC', 'NLD', 'NOR', 'NRU', 'NZL', 'OMN', 'PAK', 'PAN', 'PER', 'PHL', 'PLW', 'PNG', 'POL', 'PRI', 'PRT', 'PYF', 'QAT', 'REU', 'ROU', 'RUS', 'SAU', 'SDN', 'SEN', 'SGP', 'SLB', 'SLE', 'SLV', 'SOM', 'STP', 'SUR', 'SVN', 'SWE', 'SXM', 'SYC', 'SYR', 'TCA', 'TGO', 'THA', 'TKM', 'TLS', 'TON', 'TTO', 'TUN', 'TUR', 'TUV', 'TWN', 'TZA', 'UKR', 'URY', 'USA', 'VCT', 'VEN', 'VGB', 'VIR', 'VNM', 'VUT', 'WSM', 'YEM', 'ZAF']]
            Country to focus on. Enter as a 3-letter ISO country code. This parameter supercedes `continent` if both are provided. (provider: imf)

        Returns
        -------
        OBBject
            results : list[PortVolume]
                Serializable results.
            provider : Optional[str]
                Provider name.
            warnings : Optional[list[Warning_]]
                list of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        PortVolume
        ----------
        date : date
            The date of the data.
        port_code : Optional[str]
            Port code.
        port_name : Optional[str]
            Port name.
        country : Optional[str]
            Country where the port is located.
        export_dwell_time : Optional[float]
            EconDB model estimate for the average number of days from when a container enters the terminal gates until it is loaded on a vessel. High dwelling times can indicate vessel delays. (provider: econdb)
        import_dwell_time : Optional[float]
            EconDB model estimate for the average number of days from when a container is discharged from a vessel until it exits the terminal gates. High dwelling times can indicate trucking or port congestion. (provider: econdb)
        import_teu : Optional[int]
            EconDB model estimate for the number of twenty-foot equivalent units (TEUs) of containers imported through the port. (provider: econdb)
        export_teu : Optional[int]
            EconDB model estimate for the number of twenty-foot equivalent units (TEUs) of containers exported through the port. (provider: econdb)
        country_code : Optional[str]
            3-letter ISO country code of the country where the port is located. (provider: imf)
        portcalls : Optional[int]
            Total number of ships entering the port at this date. This is the sum of portcalls_container, portcalls_dry_bulk, portcalls_general_cargo, portcalls_roro and portcalls_tanker. (provider: imf)
        portcalls_tanker : Optional[int]
            Number of tankers transiting through the chokepoint or making a port call. (provider: imf)
        portcalls_container : Optional[int]
            Number of containers transiting through the chokepoint or making a port call. (provider: imf)
        portcalls_general_cargo : Optional[int]
            Number of general cargo ships transiting through the chokepoint or making a port call. (provider: imf)
        portcalls_dry_bulk : Optional[int]
            Number of dry bulk carriers transiting through the chokepoint or making a port call. (provider: imf)
        portcalls_roro : Optional[int]
            Number of Ro-Ro ships transiting through the chokepoint or making a port call. (provider: imf)
        imports : Optional[float]
            Total import volume (in metric tons) of all ships entering the port at this date. This is the sum of import_container, import_dry_bulk, import_general_cargo, import_roro and import_tanker. (provider: imf)
        imports_cargo : Optional[float]
            Total import volume (in metric tons) of all ships (excluding tankers) entering the port at this date. This is the sum of import_container, import_dry_bulk, import_general_cargo and import_roro. (provider: imf)
        imports_tanker : Optional[float]
            Total import volume (in metric tons) of tankers entering the port at this date. (provider: imf)
        imports_container : Optional[float]
            Total import volume (in metric tons) of all container ships entering the port at this date. (provider: imf)
        imports_general_cargo : Optional[float]
            Total import volume (in metric tons) of general cargo ships entering the port at this date. (provider: imf)
        imports_dry_bulk : Optional[float]
            Total import volume (in metric tons) of dry bulk carriers entering the port at this date. (provider: imf)
        imports_roro : Optional[float]
            Total import volume (in metric tons) of Ro-Ro ships entering the port at this date. (provider: imf)
        exports : Optional[float]
            Total export volume (in metric tons) of all ships entering the port at this date. This is the sum of export_container, export_dry_bulk, export_general_cargo, export_roro and export_tanker. (provider: imf)
        exports_cargo : Optional[float]
            Total export volume (in metric tons) of all ships (excluding tankers) entering the port at this date. This is the sum of export_container, export_dry_bulk, export_general_cargo and export_roro. (provider: imf)
        exports_tanker : Optional[float]
            Total export volume (in metric tons) of tankers entering the port at this date. (provider: imf)
        exports_container : Optional[float]
            Total export volume (in metric tons) of all container ships entering the port at this date. (provider: imf)
        exports_general_cargo : Optional[float]
            Total export volume (in metric tons) of general cargo ships entering the port at this date. (provider: imf)
        exports_dry_bulk : Optional[float]
            Total export volume (in metric tons) of dry bulk carriers entering the port at this date. (provider: imf)
        exports_roro : Optional[float]
            Total export volume (in metric tons) of Ro-Ro ships entering the port at this date. (provider: imf)

        Examples
        --------
        >>> from openbb import obb
        >>> # Get average dwelling times and TEU volumes from the top ports.
        >>> obb.economy.shipping.port_volume(provider='econdb')
        >>> # Get daily port calls and estimated trading volumes for specific ports Get the list of available ports with `openbb shipping port_info`
        >>> obb.economy.shipping.port_volume(provider='imf', port_code='rotterdam,singapore')
        >>> # Get data for all ports in a specific country. Use the 3-letter ISO country code.
        >>> obb.economy.shipping.port_volume(provider='imf', country='GBR')
        """  # noqa: E501

        return self._run(
            "/economy/shipping/port_volume",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.shipping.port_volume",
                        ("econdb", "imf"),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={
                    "start_date": {
                        "imf": {
                            "x-widget_config": {"type": "date", "value": "2019-01-01"}
                        }
                    },
                    "port_code": {
                        "imf": {
                            "multiple_items_allowed": True,
                            "choices": None,
                            "x-widget_config": {
                                "options": [
                                    {
                                        "label": "Singapore - Singapore",
                                        "value": "port1201",
                                    },
                                    {
                                        "label": "Rotterdam - The Netherlands",
                                        "value": "port1114",
                                    },
                                    {"label": "Shanghai - China", "value": "port1188"},
                                    {"label": "Antwerp - Belgium", "value": "port57"},
                                    {"label": "Busan - Korea", "value": "port1065"},
                                    {"label": "Ningbo - China", "value": "port824"},
                                    {
                                        "label": "Hong Kong - Hong Kong SAR",
                                        "value": "port474",
                                    },
                                    {
                                        "label": "Nagoya Aichi - Japan",
                                        "value": "port786",
                                    },
                                    {"label": "Yokohama - Japan", "value": "port1417"},
                                    {"label": "Mizushima - Japan", "value": "port752"},
                                    {
                                        "label": "Kaohsiung - Taiwan Province of China",
                                        "value": "port541",
                                    },
                                    {"label": "Chiba - Japan", "value": "port239"},
                                    {
                                        "label": "Tianjin Xin Gang - China",
                                        "value": "port1297",
                                    },
                                    {"label": "Ulsan - Korea", "value": "port1338"},
                                    {"label": "Qingdao - China", "value": "port1069"},
                                    {
                                        "label": "Port Klang - Malaysia",
                                        "value": "port960",
                                    },
                                    {"label": "Kobe - Japan", "value": "port581"},
                                    {
                                        "label": "Sakaisenboku - Japan",
                                        "value": "port1128",
                                    },
                                    {"label": "Guangzhou - China", "value": "port425"},
                                    {"label": "Saigon - Vietnam", "value": "port1291"},
                                    {
                                        "label": "Tanjung Priok - Indonesia",
                                        "value": "port514",
                                    },
                                    {"label": "Tokyo - Japan", "value": "port1305"},
                                    {
                                        "label": "Gwangyang (Kwangyang) - Korea",
                                        "value": "port432",
                                    },
                                    {"label": "Osaka - Japan", "value": "port862"},
                                    {
                                        "label": "Amsterdam - The Netherlands",
                                        "value": "port45",
                                    },
                                    {
                                        "label": "Manila - Philippines",
                                        "value": "port694",
                                    },
                                    {"label": "Istanbul - Turkiye", "value": "port504"},
                                    {
                                        "label": "Taicang (Suzhou) - China",
                                        "value": "port1253",
                                    },
                                    {"label": "Xiamen - China", "value": "port1404"},
                                    {"label": "Oita - Japan", "value": "port846"},
                                    {
                                        "label": "Jebel Ali - United Arab Emirates",
                                        "value": "port744",
                                    },
                                    {
                                        "label": "Houston - United States",
                                        "value": "port481",
                                    },
                                    {"label": "Kawasaki - Japan", "value": "port555"},
                                    {"label": "Yokkaichi - Japan", "value": "port1416"},
                                    {
                                        "label": "Hai Phong - Vietnam",
                                        "value": "port434",
                                    },
                                    {"label": "Tokuyama - Japan", "value": "port1304"},
                                    {"label": "Hamburg - Germany", "value": "port446"},
                                    {"label": "Dalian - China", "value": "port273"},
                                    {"label": "Incheon - Korea", "value": "port494"},
                                    {
                                        "label": "Kashima Ibaraki - Japan",
                                        "value": "port548",
                                    },
                                    {
                                        "label": "Mumbai-Jawaharlal Nehru (Nhava Sheva) - India",
                                        "value": "port776",
                                    },
                                    {"label": "Bangkok - Thailand", "value": "port111"},
                                    {"label": "Zhoushan - China", "value": "port1429"},
                                    {
                                        "label": "Tanjung Perak - Indonesia",
                                        "value": "port1237",
                                    },
                                    {"label": "Tomakomai - Japan", "value": "port1308"},
                                    {
                                        "label": "Immingham - United Kingdom",
                                        "value": "port493",
                                    },
                                    {"label": "Algeciras - Spain", "value": "port31"},
                                    {
                                        "label": "Wakamatsu (Kitakyushu) - Japan",
                                        "value": "port1378",
                                    },
                                    {
                                        "label": "Taichung - Taiwan Province of China",
                                        "value": "port1252",
                                    },
                                    {"label": "Qiwei - China", "value": "port1073"},
                                    {
                                        "label": "Kanda Fukuoka - Japan",
                                        "value": "port538",
                                    },
                                    {"label": "Ghent - Belgium", "value": "port393"},
                                    {"label": "Hakata - Japan", "value": "port439"},
                                    {
                                        "label": "Tanjung Pelepas - Malaysia",
                                        "value": "port1269",
                                    },
                                    {"label": "Piraeus - Greece", "value": "port908"},
                                    {
                                        "label": "Terneuzen - The Netherlands",
                                        "value": "port1284",
                                    },
                                    {
                                        "label": "Pyeongtaek - Korea",
                                        "value": "port1067",
                                    },
                                    {
                                        "label": "New Orleans - United States",
                                        "value": "port812",
                                    },
                                    {
                                        "label": "Yangshan (Shangai) - China",
                                        "value": "port2027",
                                    },
                                    {"label": "Santos - Brazil", "value": "port1160"},
                                    {
                                        "label": "Laem Chabang - Thailand",
                                        "value": "port1197",
                                    },
                                    {
                                        "label": "Fukuyama Kagoshima - Japan",
                                        "value": "port364",
                                    },
                                    {
                                        "label": "Nemrut Bay - Turkiye",
                                        "value": "port805",
                                    },
                                    {"label": "Himeji - Japan", "value": "port465"},
                                    {"label": "Jiangyin - China", "value": "port517"},
                                    {
                                        "label": "Zeebrugge - Belgium",
                                        "value": "port1424",
                                    },
                                    {"label": "Gresik - Indonesia", "value": "port420"},
                                    {"label": "Ube - Japan", "value": "port1335"},
                                    {
                                        "label": "Las Palmas (de Gran Canaria) - Spain",
                                        "value": "port635",
                                    },
                                    {
                                        "label": "Wakayama-Shimotsu - Japan",
                                        "value": "port1379",
                                    },
                                    {
                                        "label": "Shougang Jingtang - China",
                                        "value": "port1195",
                                    },
                                    {"label": "Funabashi - Japan", "value": "port365"},
                                    {"label": "Barcelona - Spain", "value": "port118"},
                                    {
                                        "label": "Cat Lai (Saigon New Port) - Vietnam",
                                        "value": "port2085",
                                    },
                                    {
                                        "label": "Bremerhaven - Germany",
                                        "value": "port168",
                                    },
                                    {
                                        "label": "Novorossiysk - Russian Federation",
                                        "value": "port833",
                                    },
                                    {
                                        "label": "Higashiharima - Japan",
                                        "value": "port463",
                                    },
                                    {
                                        "label": "Saint Petersburg - Russian Federation",
                                        "value": "port1150",
                                    },
                                    {
                                        "label": "Siam Seaport - Thailand",
                                        "value": "port2036",
                                    },
                                    {
                                        "label": "Vlissingen - The Netherlands",
                                        "value": "port1370",
                                    },
                                    {"label": "Cai Mep - Vietnam", "value": "port903"},
                                    {"label": "Johor - Malaysia", "value": "port523"},
                                    {
                                        "label": "Lianyungang - China",
                                        "value": "port644",
                                    },
                                    {"label": "Bohai Bay - China", "value": "port154"},
                                    {"label": "Nantong - China", "value": "port792"},
                                    {
                                        "label": "Vladivostok - Russian Federation",
                                        "value": "port1369",
                                    },
                                    {
                                        "label": "Tangier-Mediterranean - Morocco",
                                        "value": "port1265",
                                    },
                                    {
                                        "label": "Map Ta Phut - Thailand",
                                        "value": "port701",
                                    },
                                    {"label": "Mawan - China", "value": "port2028"},
                                    {"label": "Valencia - Spain", "value": "port1348"},
                                    {
                                        "label": "Diliskelesi - Turkiye",
                                        "value": "port2037",
                                    },
                                    {"label": "Daesan - Korea", "value": "port270"},
                                    {
                                        "label": "New York-New Jersey - United States",
                                        "value": "port815",
                                    },
                                    {
                                        "label": "Colombo - Sri Lanka",
                                        "value": "port254",
                                    },
                                    {
                                        "label": "Los Angeles-Long Beach - United States",
                                        "value": "port664",
                                    },
                                    {"label": "Bayuquan - China", "value": "port133"},
                                    {
                                        "label": "Sendaishiogama - Japan",
                                        "value": "port1180",
                                    },
                                    {"label": "Le Havre - France", "value": "port985"},
                                    {"label": "Iwakuni - Japan", "value": "port508"},
                                    {
                                        "label": "Gothenburg - Sweden",
                                        "value": "port408",
                                    },
                                    {
                                        "label": "Jeddah - Saudi Arabia",
                                        "value": "port518",
                                    },
                                    {"label": "Shimizu - Japan", "value": "port1193"},
                                    {
                                        "label": "Rostov-Na-Donu - Russian Federation",
                                        "value": "port1112",
                                    },
                                    {
                                        "label": "Klaipeda - Lithuania",
                                        "value": "port579",
                                    },
                                    {
                                        "label": "Shekou (Shenzhen) - China",
                                        "value": "port1189",
                                    },
                                    {
                                        "label": "Keelung - Taiwan Province of China",
                                        "value": "port238",
                                    },
                                    {
                                        "label": "Constanta - Romania",
                                        "value": "port260",
                                    },
                                    {"label": "Genova - Italy", "value": "port387"},
                                    {
                                        "label": "Al Fujayrah - United Arab Emirates",
                                        "value": "port362",
                                    },
                                    {
                                        "label": "Tangshan (Jingtang) - China",
                                        "value": "port1266",
                                    },
                                    {
                                        "label": "Cartagena - Colombia",
                                        "value": "port218",
                                    },
                                    {"label": "Qinzhou - China", "value": "port1071"},
                                    {
                                        "label": "Moerdijk - The Netherlands",
                                        "value": "port2283",
                                    },
                                    {"label": "Mersin - Turkiye", "value": "port735"},
                                    {"label": "Ambarli - Turkiye", "value": "port2049"},
                                    {"label": "Yantian - China", "value": "port1414"},
                                    {
                                        "label": "Port Hedland - Australia",
                                        "value": "port955",
                                    },
                                    {"label": "Hiroshima - Japan", "value": "port466"},
                                    {"label": "Kisarazu - Japan", "value": "port578"},
                                    {
                                        "label": "Serangoon Harbor - Singapore",
                                        "value": "port1182",
                                    },
                                    {"label": "Niihama - Japan", "value": "port823"},
                                    {"label": "Alexandria - Egypt", "value": "port23"},
                                    {"label": "Sakaide - Japan", "value": "port1129"},
                                    {
                                        "label": "Ust-Luga - Russian Federation",
                                        "value": "port1095",
                                    },
                                    {
                                        "label": "Lanqiao Port - China",
                                        "value": "port632",
                                    },
                                    {"label": "Rizhao - China", "value": "port1105"},
                                    {"label": "Gdansk - Poland", "value": "port380"},
                                    {
                                        "label": "Qinhuangdao - China",
                                        "value": "port1072",
                                    },
                                    {
                                        "label": "IJmuiden - The Netherlands",
                                        "value": "port487",
                                    },
                                    {"label": "Livorno - Italy", "value": "port655"},
                                    {
                                        "label": "Zhangjiangang (Suzhou) - China",
                                        "value": "port1425",
                                    },
                                    {"label": "Yarimca - Turkiye", "value": "port2034"},
                                    {
                                        "label": "Taipei - Taiwan Province of China",
                                        "value": "port1261",
                                    },
                                    {"label": "Haifa - Israel", "value": "port435"},
                                    {"label": "Riga - Latvia", "value": "port1100"},
                                    {"label": "Mundra - India", "value": "port777"},
                                    {"label": "Yakacik - Turkiye", "value": "port1406"},
                                    {"label": "Fuzhou - China", "value": "port370"},
                                    {"label": "Hachinohe - Japan", "value": "port433"},
                                    {"label": "Samsun - Turkiye", "value": "port1139"},
                                    {"label": "Dumai - Indonesia", "value": "port309"},
                                    {"label": "Marsaxlokk - Malta", "value": "port711"},
                                    {"label": "Mikawa - Japan", "value": "port738"},
                                    {"label": "Tsukumi - Japan", "value": "port1324"},
                                    {"label": "Gdynia - Poland", "value": "port381"},
                                    {
                                        "label": "Durban - South Africa",
                                        "value": "port311",
                                    },
                                    {
                                        "label": "Teesport - United Kingdom",
                                        "value": "port1279",
                                    },
                                    {
                                        "label": "South Louisiana - United States",
                                        "value": "port1214",
                                    },
                                    {
                                        "label": "Casablanca - Morocco",
                                        "value": "port220",
                                    },
                                    {"label": "Zhanjiang - China", "value": "port1426"},
                                    {"label": "Kingston - Jamaica", "value": "port572"},
                                    {"label": "Bilbao - Spain", "value": "port1038"},
                                    {"label": "Dublin - Ireland", "value": "port307"},
                                    {
                                        "label": "Manzanillo - Panama",
                                        "value": "port700",
                                    },
                                    {
                                        "label": "Chittagong - Bangladesh",
                                        "value": "port241",
                                    },
                                    {"label": "Balboa - Panama", "value": "port101"},
                                    {"label": "Zhuhai - China", "value": "port2112"},
                                    {"label": "Xiuyu - China", "value": "port1405"},
                                    {
                                        "label": "Liverpool - United Kingdom",
                                        "value": "port654",
                                    },
                                    {
                                        "label": "Savannah - United States",
                                        "value": "port1170",
                                    },
                                    {
                                        "label": "Porto Di Lido-Venezia - Italy",
                                        "value": "port1005",
                                    },
                                    {
                                        "label": "Port Everglades - United States",
                                        "value": "port951",
                                    },
                                    {"label": "Pohang - Korea", "value": "port915"},
                                    {"label": "Ashdod - Israel", "value": "port73"},
                                    {
                                        "label": "Taboguilla - Panama",
                                        "value": "port2200",
                                    },
                                    {
                                        "label": "Balikpapan - Indonesia",
                                        "value": "port102",
                                    },
                                    {"label": "Ravenna - Italy", "value": "port1004"},
                                    {"label": "Leixoes - Portugal", "value": "port999"},
                                    {
                                        "label": "Newcastle - Australia",
                                        "value": "port816",
                                    },
                                    {
                                        "label": "Jubail - Saudi Arabia",
                                        "value": "port24",
                                    },
                                    {
                                        "label": "London - United Kingdom",
                                        "value": "port658",
                                    },
                                    {
                                        "label": "Dongjiakou - China",
                                        "value": "port1070",
                                    },
                                    {
                                        "label": "Brisbane - Australia",
                                        "value": "port174",
                                    },
                                    {"label": "Damietta - Egypt", "value": "port274"},
                                    {
                                        "label": "Batangas City - Philippines",
                                        "value": "port125",
                                    },
                                    {
                                        "label": "Puerto Del Callao - Peru",
                                        "value": "port1045",
                                    },
                                    {"label": "Dunkirk - France", "value": "port310"},
                                    {"label": "Tarragona - Spain", "value": "port1277"},
                                    {"label": "Rostock - Germany", "value": "port1111"},
                                    {
                                        "label": "Nakhodka - Russian Federation",
                                        "value": "port787",
                                    },
                                    {"label": "Veracruz - Mexico", "value": "port1358"},
                                    {"label": "Zhapu - China", "value": "port1427"},
                                    {
                                        "label": "Gourd Shanzui - China",
                                        "value": "port410",
                                    },
                                    {"label": "Szczecin - Poland", "value": "port1246"},
                                    {
                                        "label": "Khalifa Port - United Arab Emirates",
                                        "value": "port2025",
                                    },
                                    {"label": "Paranagua - Brazil", "value": "port885"},
                                    {
                                        "label": "Lagos-Apapa-Tin Can Island - Nigeria",
                                        "value": "port626",
                                    },
                                    {"label": "Matsuyama - Japan", "value": "port720"},
                                    {"label": "Cebu - Philippines", "value": "port224"},
                                    {"label": "Kagoshima - Japan", "value": "port528"},
                                    {
                                        "label": "Vancouver - Canada",
                                        "value": "port1350",
                                    },
                                    {
                                        "label": "Southampton - United Kingdom",
                                        "value": "port1216",
                                    },
                                    {
                                        "label": "Makassar - Indonesia",
                                        "value": "port1336",
                                    },
                                    {"label": "Hakodate - Japan", "value": "port440"},
                                    {
                                        "label": "Deendayal (Kandla) - India",
                                        "value": "port540",
                                    },
                                    {
                                        "label": "Pengerang - Malaysia",
                                        "value": "port2189",
                                    },
                                    {"label": "Muroran - Japan", "value": "port780"},
                                    {
                                        "label": "Rio De Janeiro - Brazil",
                                        "value": "port1103",
                                    },
                                    {
                                        "label": "Melbourne - Australia",
                                        "value": "port729",
                                    },
                                    {
                                        "label": "Panjang - Indonesia",
                                        "value": "port881",
                                    },
                                    {
                                        "label": "Hull - United Kingdom",
                                        "value": "port573",
                                    },
                                    {
                                        "label": "Manzanillo - Mexico",
                                        "value": "port699",
                                    },
                                    {"label": "Niigata - Japan", "value": "port822"},
                                    {"label": "Sines - Portugal", "value": "port1200"},
                                    {
                                        "label": "London Gateway - United Kingdom",
                                        "value": "port659",
                                    },
                                    {"label": "Itaqui - Brazil", "value": "port506"},
                                    {"label": "Trieste - Italy", "value": "port1318"},
                                    {
                                        "label": "Visakhapatnam - India",
                                        "value": "port1367",
                                    },
                                    {
                                        "label": "Brunsbuettel - Germany",
                                        "value": "port179",
                                    },
                                    {"label": "Fang-Cheng - China", "value": "port339"},
                                    {
                                        "label": "Port of Sohar - Oman",
                                        "value": "port988",
                                    },
                                    {"label": "Yantai - China", "value": "port1410"},
                                    {"label": "Borusan - Turkiye", "value": "port2043"},
                                    {"label": "Marugame - Japan", "value": "port714"},
                                    {
                                        "label": "Guayaquil - Ecuador",
                                        "value": "port426",
                                    },
                                    {"label": "Kinuura - Japan", "value": "port575"},
                                    {
                                        "label": "Davao - Philippines",
                                        "value": "port281",
                                    },
                                    {
                                        "label": "Gladstone - Australia",
                                        "value": "port398",
                                    },
                                    {
                                        "label": "Ras Laffan - Qatar",
                                        "value": "port1090",
                                    },
                                    {
                                        "label": "Kure Hiroshima - Japan",
                                        "value": "port610",
                                    },
                                    {"label": "Mongstad - Norway", "value": "port760"},
                                    {"label": "Penang - Malaysia", "value": "port1062"},
                                    {
                                        "label": "Baltimore - United States",
                                        "value": "port103",
                                    },
                                    {"label": "Eleusis - Greece", "value": "port322"},
                                    {
                                        "label": "Charleston - United States",
                                        "value": "port231",
                                    },
                                    {
                                        "label": "Azov - Russian Federation",
                                        "value": "port2010",
                                    },
                                    {
                                        "label": "Corpus Christi - United States",
                                        "value": "port264",
                                    },
                                    {"label": "Huizhou - China", "value": "port484"},
                                    {"label": "Huelva - Spain", "value": "port483"},
                                    {"label": "Altamira - Mexico", "value": "port38"},
                                    {
                                        "label": "Thessaloniki - Greece",
                                        "value": "port1293",
                                    },
                                    {"label": "Lisbon - Portugal", "value": "port653"},
                                    {
                                        "label": "Belfast - United Kingdom",
                                        "value": "port141",
                                    },
                                    {"label": "Umm Qasr - Iraq", "value": "port1341"},
                                    {
                                        "label": "Zhouliwang - China",
                                        "value": "port1428",
                                    },
                                    {
                                        "label": "Kuantan New Port - Malaysia",
                                        "value": "port603",
                                    },
                                    {
                                        "label": "Gioia Tauro - Italy",
                                        "value": "port395",
                                    },
                                    {"label": "Cartagena - Spain", "value": "port219"},
                                    {
                                        "label": "Tekirdag - Turkiye",
                                        "value": "port1280",
                                    },
                                    {
                                        "label": "Palembang - Indonesia",
                                        "value": "port875",
                                    },
                                    {
                                        "label": "Fawley - United Kingdom",
                                        "value": "port342",
                                    },
                                    {"label": "Salalah - Oman", "value": "port746"},
                                    {"label": "Moji - Japan", "value": "port2017"},
                                    {
                                        "label": "Dubai - United Arab Emirates",
                                        "value": "port306",
                                    },
                                    {"label": "Aarhus - Denmark", "value": "port67"},
                                    {"label": "Kotka - Finland", "value": "port597"},
                                    {
                                        "label": "Rio Grande - Brazil",
                                        "value": "port1104",
                                    },
                                    {"label": "Naha - Japan", "value": "port2040"},
                                    {"label": "Yangpu - China", "value": "port1409"},
                                    {
                                        "label": "Tilbury - United Kingdom",
                                        "value": "port1298",
                                    },
                                    {
                                        "label": "Lazaro Cardenas - Mexico",
                                        "value": "port637",
                                    },
                                    {"label": "Kushiro - Japan", "value": "port611"},
                                    {
                                        "label": "Sekupang - Indonesia",
                                        "value": "port1178",
                                    },
                                    {
                                        "label": "Banjarmasin - Indonesia",
                                        "value": "port112",
                                    },
                                    {"label": "Onahama - Japan", "value": "port850"},
                                    {
                                        "label": "Puerto San Martin - Argentina",
                                        "value": "port1059",
                                    },
                                    {"label": "Porsgrunn - Norway", "value": "port928"},
                                    {
                                        "label": "El Dekheila - Egypt",
                                        "value": "port2044",
                                    },
                                    {
                                        "label": "Dammam - Saudi Arabia",
                                        "value": "port275",
                                    },
                                    {
                                        "label": "Santa Cruz De Tenerife - Spain",
                                        "value": "port1153",
                                    },
                                    {"label": "Burgas - Bulgaria", "value": "port193"},
                                    {
                                        "label": "Derince (Izmit-Kocaeli) - Turkiye",
                                        "value": "port287",
                                    },
                                    {"label": "Hitachi - Japan", "value": "port468"},
                                    {
                                        "label": "Rosario - Argentina",
                                        "value": "port1108",
                                    },
                                    {
                                        "label": "Dung Quat - Vietnam",
                                        "value": "port213",
                                    },
                                    {
                                        "label": "Chennai (Madras) - India",
                                        "value": "port235",
                                    },
                                    {"label": "Changzhou - China", "value": "port228"},
                                    {
                                        "label": "Richards Bay - South Africa",
                                        "value": "port1099",
                                    },
                                    {"label": "Da Nang - Vietnam", "value": "port269"},
                                    {"label": "Dakar - Senegal", "value": "port272"},
                                    {"label": "Banten - Indonesia", "value": "port114"},
                                    {
                                        "label": "Mishima Kawanoe - Japan",
                                        "value": "port749",
                                    },
                                    {"label": "Montoir - France", "value": "port765"},
                                    {"label": "Izmir - Turkiye", "value": "port510"},
                                    {"label": "Sitrah - Bahrain", "value": "port1203"},
                                    {
                                        "label": "Aspropyrgos - Greece",
                                        "value": "port75",
                                    },
                                    {
                                        "label": "Fremantle - Australia",
                                        "value": "port361",
                                    },
                                    {"label": "Napoli - Italy", "value": "port795"},
                                    {
                                        "label": "Hibikinada - Japan",
                                        "value": "port2057",
                                    },
                                    {"label": "Haldia - India", "value": "port442"},
                                    {
                                        "label": "Felixstowe - United Kingdom",
                                        "value": "port343",
                                    },
                                    {
                                        "label": "Jinzhou Wan - China",
                                        "value": "port521",
                                    },
                                    {"label": "Yangon - Myanmar", "value": "port1086"},
                                    {
                                        "label": "Vostochnyy - Russian Federation",
                                        "value": "port1374",
                                    },
                                    {
                                        "label": "King Fahd Port - Saudi Arabia",
                                        "value": "port570",
                                    },
                                    {
                                        "label": "Murmansk - Russian Federation",
                                        "value": "port779",
                                    },
                                    {
                                        "label": "Porto De Suape - Brazil",
                                        "value": "port1002",
                                    },
                                    {
                                        "label": "Abidjan - Cote dIvoire",
                                        "value": "port4",
                                    },
                                    {
                                        "label": "Port Botany - Australia",
                                        "value": "port161",
                                    },
                                    {
                                        "label": "Mina Saqr - United Arab Emirates",
                                        "value": "port747",
                                    },
                                    {"label": "Xiagong - China", "value": "port1403"},
                                    {
                                        "label": "Dampier - Australia",
                                        "value": "port276",
                                    },
                                    {"label": "Mombasa - Kenya", "value": "port757"},
                                    {
                                        "label": "Baku Port - Azerbaijan",
                                        "value": "port100",
                                    },
                                    {"label": "Rouen - France", "value": "port986"},
                                    {"label": "Ako - Japan", "value": "port15"},
                                    {"label": "Rayong - Thailand", "value": "port1093"},
                                    {
                                        "label": "Tanjung Sekong - Indonesia",
                                        "value": "port1271",
                                    },
                                    {
                                        "label": "Jabal Az Zannah-Ruways - United Arab Emirates",
                                        "value": "port512",
                                    },
                                    {"label": "Karachi - Pakistan", "value": "port543"},
                                    {
                                        "label": "Agioi Oil Terminal - Greece",
                                        "value": "port845",
                                    },
                                    {
                                        "label": "Jorf Lasfar - Morocco",
                                        "value": "port319",
                                    },
                                    {
                                        "label": "Setubal - Portugal",
                                        "value": "port1184",
                                    },
                                    {"label": "Lome - Togo", "value": "port657"},
                                    {"label": "Koper - Slovenia", "value": "port592"},
                                    {"label": "Tema - Ghana", "value": "port1282"},
                                    {"label": "Augusta - Italy", "value": "port80"},
                                    {
                                        "label": "Puerto Barrios - Guatemala",
                                        "value": "port1159",
                                    },
                                    {"label": "Kikuma - Japan", "value": "port567"},
                                    {
                                        "label": "Sharjah - United Arab Emirates",
                                        "value": "port72",
                                    },
                                    {
                                        "label": "Puerto Cortes - Honduras",
                                        "value": "port1036",
                                    },
                                    {
                                        "label": "Buenos Aires - Argentina",
                                        "value": "port184",
                                    },
                                    {
                                        "label": "Port Elizabeth - South Africa",
                                        "value": "port948",
                                    },
                                    {
                                        "label": "Haina - Dominican Republic",
                                        "value": "port1042",
                                    },
                                    {"label": "Susaki - Japan", "value": "port1239"},
                                    {
                                        "label": "Kristiansund - Norway",
                                        "value": "port601",
                                    },
                                    {
                                        "label": "Copenhagen - Denmark",
                                        "value": "port582",
                                    },
                                    {
                                        "label": "Longkou Gang - China",
                                        "value": "port661",
                                    },
                                    {"label": "Shuaiba - Kuwait", "value": "port2067"},
                                    {
                                        "label": "Port Jerome - France",
                                        "value": "port958",
                                    },
                                    {
                                        "label": "Jacksonville - United States",
                                        "value": "port513",
                                    },
                                    {
                                        "label": "Port De Salvador - Brazil",
                                        "value": "port944",
                                    },
                                    {"label": "Beirut - Lebanon", "value": "port132"},
                                    {
                                        "label": "Tauranga - New Zealand",
                                        "value": "port1278",
                                    },
                                    {"label": "Paradip - India", "value": "port883"},
                                    {"label": "Gemlik - Turkiye", "value": "port385"},
                                    {"label": "Fos - France", "value": "port351"},
                                    {
                                        "label": "Port of Virginia - United States",
                                        "value": "port2066",
                                    },
                                    {
                                        "label": "Port Arthur - United States",
                                        "value": "port933",
                                    },
                                    {"label": "Hazira - India", "value": "port2039"},
                                    {
                                        "label": "Pontianak - Indonesia",
                                        "value": "port925",
                                    },
                                    {
                                        "label": "Puerto Quetzal - Guatemala",
                                        "value": "port1057",
                                    },
                                    {
                                        "label": "Djibouti - Djibouti",
                                        "value": "port294",
                                    },
                                    {
                                        "label": "V. O. Chidambaranar (Tuticorin) - India",
                                        "value": "port1331",
                                    },
                                    {
                                        "label": "San Juan - Puerto Rico",
                                        "value": "port1143",
                                    },
                                    {
                                        "label": "Tuapse - Russian Federation",
                                        "value": "port1326",
                                    },
                                    {
                                        "label": "Semarang - Indonesia",
                                        "value": "port1179",
                                    },
                                    {"label": "Valletta - Malta", "value": "port1349"},
                                    {
                                        "label": "Hamad Port - Qatar",
                                        "value": "port2026",
                                    },
                                    {
                                        "label": "Belawan - Indonesia",
                                        "value": "port139",
                                    },
                                    {
                                        "label": "Miami - United States",
                                        "value": "port736",
                                    },
                                    {"label": "Stade - Germany", "value": "port2140"},
                                    {
                                        "label": "Point Lisas - Trinidad and Tobago",
                                        "value": "port917",
                                    },
                                    {
                                        "label": "Puerto Moin - Costa Rica",
                                        "value": "port1052",
                                    },
                                    {
                                        "label": "Mailiao - Taiwan Province of China",
                                        "value": "port681",
                                    },
                                    {
                                        "label": "Port Saint Louis Du Rhone - France",
                                        "value": "port976",
                                    },
                                    {
                                        "label": "Harbor Yeweiju - China",
                                        "value": "port453",
                                    },
                                    {
                                        "label": "Gravesend - United Kingdom",
                                        "value": "port416",
                                    },
                                    {
                                        "label": "Fushikitoyama - Japan",
                                        "value": "port369",
                                    },
                                    {"label": "Dongguan - China", "value": "port2019"},
                                    {"label": "Luanda - Angola", "value": "port665"},
                                    {
                                        "label": "Wilhelmshaven - Germany",
                                        "value": "port1396",
                                    },
                                    {
                                        "label": "Beaumont - United States",
                                        "value": "port134",
                                    },
                                    {
                                        "label": "Coatzacoalcos - Mexico",
                                        "value": "port252",
                                    },
                                    {"label": "Oslo - Norway", "value": "port864"},
                                    {
                                        "label": "Buenaventura - Colombia",
                                        "value": "port183",
                                    },
                                    {
                                        "label": "Lubeck-Travemunde - Germany",
                                        "value": "port667",
                                    },
                                    {"label": "Cork - Ireland", "value": "port262"},
                                    {"label": "Liepaja - Latvia", "value": "port646"},
                                    {"label": "Shibushi - Japan", "value": "port1190"},
                                    {"label": "Santander - Spain", "value": "port1155"},
                                    {"label": "Vigo - Spain", "value": "port1363"},
                                    {
                                        "label": "Al Hamriyah LPG Terminal - United Arab Emirates",
                                        "value": "port22",
                                    },
                                    {
                                        "label": "Norfolk - United States",
                                        "value": "port826",
                                    },
                                    {"label": "Montreal - Canada", "value": "port766"},
                                    {
                                        "label": "Freeport - The Bahamas",
                                        "value": "port357",
                                    },
                                    {
                                        "label": "New Mangalore - India",
                                        "value": "port811",
                                    },
                                    {
                                        "label": "Montevideo - Uruguay",
                                        "value": "port764",
                                    },
                                    {
                                        "label": "Iskenderun - Turkiye",
                                        "value": "port503",
                                    },
                                    {
                                        "label": "Mobile - United States",
                                        "value": "port754",
                                    },
                                    {
                                        "label": "Georgetown - Guyana",
                                        "value": "port390",
                                    },
                                    {
                                        "label": "Skoldvik - Finland",
                                        "value": "port1015",
                                    },
                                    {"label": "Yingkou - China", "value": "port1415"},
                                    {"label": "Bremen - Germany", "value": "port167"},
                                    {"label": "Nanjing - China", "value": "port2020"},
                                    {
                                        "label": "Doha-Umm Said - Qatar",
                                        "value": "port1342",
                                    },
                                    {
                                        "label": "Milford Haven - United Kingdom",
                                        "value": "port740",
                                    },
                                    {"label": "Arzew - Algeria", "value": "port70"},
                                    {
                                        "label": "Hay Point - Australia",
                                        "value": "port458",
                                    },
                                    {
                                        "label": "Teluk Bayur - Indonesia",
                                        "value": "port1281",
                                    },
                                    {"label": "Ceuta - Spain", "value": "port267"},
                                    {
                                        "label": "Shidao Newport - China",
                                        "value": "port1191",
                                    },
                                    {
                                        "label": "Oakland - United States",
                                        "value": "port839",
                                    },
                                    {
                                        "label": "Barranquilla - Colombia",
                                        "value": "port120",
                                    },
                                    {
                                        "label": "Bristol - United Kingdom",
                                        "value": "port84",
                                    },
                                    {"label": "Gijon - Spain", "value": "port394"},
                                    {"label": "Salerno - Italy", "value": "port1135"},
                                    {"label": "Bandirma - Turkiye", "value": "port109"},
                                    {
                                        "label": "Vanino - Russian Federation",
                                        "value": "port187",
                                    },
                                    {"label": "Limassol - Cyprus", "value": "port647"},
                                    {"label": "Castellon - Spain", "value": "port317"},
                                    {
                                        "label": "Stavanger - Norway",
                                        "value": "port1225",
                                    },
                                    {
                                        "label": "Port Walcott - Australia",
                                        "value": "port981",
                                    },
                                    {
                                        "label": "Port-De-Bouc - France",
                                        "value": "port990",
                                    },
                                    {"label": "Sagunto - Spain", "value": "port1120"},
                                    {"label": "Halifax - Canada", "value": "port443"},
                                    {
                                        "label": "Freeport - United States",
                                        "value": "port358",
                                    },
                                    {"label": "Golcuk - Turkiye", "value": "port401"},
                                    {"label": "Hanko - Finland", "value": "port450"},
                                    {
                                        "label": "Vila Do Conde - Brazil",
                                        "value": "port2046",
                                    },
                                    {"label": "Alger - Algeria", "value": "port32"},
                                    {
                                        "label": "Philadelphia - United States",
                                        "value": "port901",
                                    },
                                    {
                                        "label": "Cagayan de Oro - Philippines",
                                        "value": "port202",
                                    },
                                    {"label": "Colon - Panama", "value": "port1035"},
                                    {"label": "Donghae - Korea", "value": "port1309"},
                                    {"label": "Tuban - Indonesia", "value": "port1327"},
                                    {
                                        "label": "Puerto Cristobal - Panama",
                                        "value": "port1037",
                                    },
                                    {
                                        "label": "Muuga-Port of Tallinn - Estonia",
                                        "value": "port781",
                                    },
                                    {"label": "Emden - Germany", "value": "port323"},
                                    {
                                        "label": "Muhammad Bin Qasim - Pakistan",
                                        "value": "port775",
                                    },
                                    {
                                        "label": "Cochin (Kochi) - India",
                                        "value": "port583",
                                    },
                                    {
                                        "label": "Puerto San Antonio - Chile",
                                        "value": "port1058",
                                    },
                                    {"label": "Cuxhaven - Germany", "value": "port268"},
                                    {
                                        "label": "Tanjunguban - Indonesia",
                                        "value": "port1273",
                                    },
                                    {
                                        "label": "Caucedo - Dominican Republic",
                                        "value": "port51",
                                    },
                                    {"label": "Bergen - Norway", "value": "port147"},
                                    {"label": "Nagasaki - Japan", "value": "port785"},
                                    {"label": "Gaogang - China", "value": "port375"},
                                    {"label": "Aveiro - Portugal", "value": "port82"},
                                    {
                                        "label": "Aktau Port - Kazakhstan",
                                        "value": "port16",
                                    },
                                    {
                                        "label": "Primorsk - Russian Federation",
                                        "value": "port1020",
                                    },
                                    {"label": "Esbjerg - Denmark", "value": "port328"},
                                    {"label": "Brake - Germany", "value": "port165"},
                                    {
                                        "label": "Garston - United Kingdom",
                                        "value": "port376",
                                    },
                                    {
                                        "label": "Komatsushima - Japan",
                                        "value": "port589",
                                    },
                                    {"label": "Tananger - Norway", "value": "port1263"},
                                    {"label": "Akita - Japan", "value": "port14"},
                                    {
                                        "label": "Cape Town - South Africa",
                                        "value": "port215",
                                    },
                                    {
                                        "label": "Point Noire - Republic of Congo",
                                        "value": "port919",
                                    },
                                    {"label": "Tubarao - Brazil", "value": "port1328"},
                                    {
                                        "label": "Nordenham - Germany",
                                        "value": "port2064",
                                    },
                                    {"label": "Helsinki - Finland", "value": "port460"},
                                    {
                                        "label": "Brofjorden - Sweden",
                                        "value": "port175",
                                    },
                                    {
                                        "label": "Juaymah - Saudi Arabia",
                                        "value": "port526",
                                    },
                                    {
                                        "label": "Bandar Shahid Rajaee - Iran",
                                        "value": "port106",
                                    },
                                    {"label": "Wenzhou - China", "value": "port1390"},
                                    {
                                        "label": "Weifang Port - China",
                                        "value": "port1385",
                                    },
                                    {
                                        "label": "Auckland - New Zealand",
                                        "value": "port79",
                                    },
                                    {"label": "Douala - Cameroon", "value": "port299"},
                                    {
                                        "label": "Fredrikstad - Norway",
                                        "value": "port356",
                                    },
                                    {"label": "Cotonou - Benin", "value": "port265"},
                                    {
                                        "label": "Norrkoping - Sweden",
                                        "value": "port827",
                                    },
                                    {
                                        "label": "Tampa - United States",
                                        "value": "port1259",
                                    },
                                    {"label": "Misrata - Libya", "value": "port750"},
                                    {"label": "Mejillones - Chile", "value": "port728"},
                                    {
                                        "label": "Abu Dhabi - United Arab Emirates",
                                        "value": "port5",
                                    },
                                    {
                                        "label": "Fredericia - Denmark",
                                        "value": "port354",
                                    },
                                    {
                                        "label": "Port Louis - Mauritius",
                                        "value": "port965",
                                    },
                                    {
                                        "label": "Helsingborg - Sweden",
                                        "value": "port459",
                                    },
                                    {
                                        "label": "Porto de Itaguai - Brazil",
                                        "value": "port2045",
                                    },
                                    {"label": "Kochi - Japan", "value": "port584"},
                                    {
                                        "label": "Krishnapatnam Port - India",
                                        "value": "port599",
                                    },
                                    {"label": "Bitung - Indonesia", "value": "port151"},
                                    {
                                        "label": "Dar Es Salaam - Tanzania",
                                        "value": "port278",
                                    },
                                    {"label": "Rauma - Finland", "value": "port1092"},
                                    {"label": "Malamocco - Italy", "value": "port1006"},
                                    {"label": "Pipavav - India", "value": "port907"},
                                    {"label": "La Spezia - Italy", "value": "port622"},
                                    {
                                        "label": "Yeysk - Russian Federation",
                                        "value": "port1413",
                                    },
                                    {
                                        "label": "Tacoma - United States",
                                        "value": "port1248",
                                    },
                                    {"label": "Amagasaki - Japan", "value": "port40"},
                                    {"label": "Port Said - Egypt", "value": "port192"},
                                    {"label": "Floro - Norway", "value": "port349"},
                                    {"label": "Pasajes - Spain", "value": "port1044"},
                                    {"label": "Al Aqabah - Jordan", "value": "port19"},
                                    {
                                        "label": "Bontang LNG Terminal - Indonesia",
                                        "value": "port156",
                                    },
                                    {
                                        "label": "Maputo - Mozambique",
                                        "value": "port702",
                                    },
                                    {
                                        "label": "Puerto Montt - Chile",
                                        "value": "port1053",
                                    },
                                    {"label": "Ishinomaki - Japan", "value": "port502"},
                                    {
                                        "label": "Izhevskoye - Russian Federation",
                                        "value": "port509",
                                    },
                                    {
                                        "label": "Tanjung Geren - Indonesia",
                                        "value": "port1268",
                                    },
                                    {"label": "La Coruna - Spain", "value": "port617"},
                                    {
                                        "label": "Indonesia Morowali Industrial Park - Indonesia",
                                        "value": "port496",
                                    },
                                    {"label": "Weihai - China", "value": "port1386"},
                                    {
                                        "label": "Subic Bay - Philippines",
                                        "value": "port1232",
                                    },
                                    {
                                        "label": "Temryuk - Russian Federation",
                                        "value": "port1283",
                                    },
                                    {"label": "Hofu - Japan", "value": "port471"},
                                    {
                                        "label": "Chornomorsk - Ukraine",
                                        "value": "port489",
                                    },
                                    {"label": "Alesund - Norway", "value": "port30"},
                                    {"label": "Cagliari - Italy", "value": "port203"},
                                    {"label": "Quebec - Canada", "value": "port1075"},
                                    {"label": "Luoyuan - China", "value": "port2118"},
                                    {
                                        "label": "Sihanoukville - Cambodia",
                                        "value": "port535",
                                    },
                                    {"label": "Gebze - Turkiye", "value": "port527"},
                                    {"label": "Itajai - Brazil", "value": "port505"},
                                    {
                                        "label": "King Abdullah Port - Saudi Arabia",
                                        "value": "port2031",
                                    },
                                    {"label": "Poti - Georgia", "value": "port1016"},
                                    {
                                        "label": "Port Ambon - Indonesia",
                                        "value": "port42",
                                    },
                                    {
                                        "label": "Campana - Argentina",
                                        "value": "port210",
                                    },
                                    {
                                        "label": "Kalundborg - Denmark",
                                        "value": "port532",
                                    },
                                    {
                                        "label": "Merak Mas Terminal - Indonesia",
                                        "value": "port731",
                                    },
                                    {
                                        "label": "Botas Natural Gas Terminal - Turkiye",
                                        "value": "port163",
                                    },
                                    {
                                        "label": "Grangemouth - United Kingdom",
                                        "value": "port415",
                                    },
                                    {
                                        "label": "Cilacap - Indonesia",
                                        "value": "port245",
                                    },
                                    {
                                        "label": "Limetree Bay - United States Virgin Islands",
                                        "value": "port649",
                                    },
                                    {"label": "Odesa - Ukraine", "value": "port843"},
                                    {
                                        "label": "Wilmington, DE - United States",
                                        "value": "port1398",
                                    },
                                    {"label": "Karlshamn - Sweden", "value": "port546"},
                                    {
                                        "label": "Port Kembla - Australia",
                                        "value": "port959",
                                    },
                                    {"label": "Sevilla - Spain", "value": "port1185"},
                                    {"label": "Taranto - Italy", "value": "port1275"},
                                    {
                                        "label": "Kamarajar Port - India",
                                        "value": "port534",
                                    },
                                    {"label": "Jiaxing - China", "value": "port2021"},
                                    {
                                        "label": "Port of Spain - Trinidad and Tobago",
                                        "value": "port989",
                                    },
                                    {"label": "Guangao - China", "value": "port2114"},
                                    {"label": "Malmo - Sweden", "value": "port690"},
                                    {
                                        "label": "Swinoujscie - Poland",
                                        "value": "port1242",
                                    },
                                    {
                                        "label": "Gibraltar - Gibraltar",
                                        "value": "port332",
                                    },
                                    {"label": "Buco - Philippines", "value": "port182"},
                                    {"label": "Aliaga - Turkiye", "value": "port33"},
                                    {"label": "Darwin - Australia", "value": "port280"},
                                    {
                                        "label": "Turkmenbashi Port - Turkmenistan",
                                        "value": "port1330",
                                    },
                                    {
                                        "label": "Aberdeen - United Kingdom",
                                        "value": "port3",
                                    },
                                    {
                                        "label": "Port Moresby - Papua New Guinea",
                                        "value": "port970",
                                    },
                                    {
                                        "label": "Yatsushiro - Japan",
                                        "value": "port1411",
                                    },
                                    {
                                        "label": "Delfzijl - The Netherlands",
                                        "value": "port285",
                                    },
                                    {"label": "Aalborg - Denmark", "value": "port29"},
                                    {
                                        "label": "Kaliningrad - Russian Federation",
                                        "value": "port530",
                                    },
                                    {"label": "Cadiz - Spain", "value": "port201"},
                                    {"label": "Kanazawa - Japan", "value": "port537"},
                                    {
                                        "label": "La Pallice - France",
                                        "value": "port620",
                                    },
                                    {
                                        "label": "Bintulu Port - Malaysia",
                                        "value": "port149",
                                    },
                                    {
                                        "label": "Texas City - United States",
                                        "value": "port1285",
                                    },
                                    {"label": "Aratu - Brazil", "value": "port62"},
                                    {"label": "Eregli - Turkiye", "value": "port327"},
                                    {"label": "Tagonoura - Japan", "value": "port1250"},
                                    {
                                        "label": "Korsakov - Russian Federation",
                                        "value": "port594",
                                    },
                                    {"label": "Dahej - India", "value": "port271"},
                                    {
                                        "label": "Ventspils - Latvia",
                                        "value": "port1357",
                                    },
                                    {
                                        "label": "Bahia Quintero (Ventanas) - Chile",
                                        "value": "port90",
                                    },
                                    {"label": "Kakinada - India", "value": "port529"},
                                    {
                                        "label": "Bahia Blanca - Argentina",
                                        "value": "port1048",
                                    },
                                    {
                                        "label": "Port of Sabah - Malaysia",
                                        "value": "port1164",
                                    },
                                    {"label": "Tampico - Mexico", "value": "port1260"},
                                    {"label": "Tunis - Tunisia", "value": "port1329"},
                                    {"label": "Quanzhou - China", "value": "port1074"},
                                    {
                                        "label": "General Santos - Philippines",
                                        "value": "port386",
                                    },
                                    {
                                        "label": "Changshu (Suzhou) - China",
                                        "value": "port227",
                                    },
                                    {
                                        "label": "Pivdennyi - Ukraine",
                                        "value": "port1419",
                                    },
                                    {
                                        "label": "Porto Pecem - Brazil",
                                        "value": "port1010",
                                    },
                                    {
                                        "label": "Santa Marta - Colombia",
                                        "value": "port1154",
                                    },
                                    {"label": "Sete - France", "value": "port1183"},
                                    {
                                        "label": "Pointe A Pitre - Guadeloupe",
                                        "value": "port922",
                                    },
                                    {
                                        "label": "Ras Tanura - Saudi Arabia",
                                        "value": "port1091",
                                    },
                                    {"label": "Gunsan - Korea", "value": "port608"},
                                    {"label": "Yokosuka - Japan", "value": "port1418"},
                                    {
                                        "label": "Philipsburg - Sint Maarten",
                                        "value": "port902",
                                    },
                                    {"label": "Calcutta - India", "value": "port207"},
                                    {"label": "Oran - Algeria", "value": "port856"},
                                    {
                                        "label": "Sao Sebastiao - Brazil",
                                        "value": "port1162",
                                    },
                                    {"label": "Magdalla - India", "value": "port679"},
                                    {
                                        "label": "Port Lyttelton - New Zealand",
                                        "value": "port966",
                                    },
                                    {"label": "Savona - Italy", "value": "port1171"},
                                    {"label": "Wismar - Germany", "value": "port1401"},
                                    {
                                        "label": "Lake Charles - United States",
                                        "value": "port629",
                                    },
                                    {
                                        "label": "Acajutla - El Salvador",
                                        "value": "port6",
                                    },
                                    {"label": "Itapoa - Brazil", "value": "port2035"},
                                    {
                                        "label": "Sarroch Oil Terminal - Italy",
                                        "value": "port1167",
                                    },
                                    {
                                        "label": "Samarinda - Indonesia",
                                        "value": "port1137",
                                    },
                                    {"label": "Hamina - Finland", "value": "port448"},
                                    {"label": "Lumut - Malaysia", "value": "port672"},
                                    {"label": "Hon Gai - Vietnam", "value": "port473"},
                                    {
                                        "label": "Marseilles - France",
                                        "value": "port712",
                                    },
                                    {"label": "Sakai - Japan", "value": "port1127"},
                                    {
                                        "label": "Medway - United Kingdom",
                                        "value": "port726",
                                    },
                                    {
                                        "label": "Paramaribo - Suriname",
                                        "value": "port884",
                                    },
                                    {
                                        "label": "Marcus Hook - United States",
                                        "value": "port2252",
                                    },
                                    {"label": "Kudamatsu - Japan", "value": "port605"},
                                    {
                                        "label": "OnomichiItozaki - Japan",
                                        "value": "port853",
                                    },
                                    {"label": "Mo i Rana - Norway", "value": "port753"},
                                    {"label": "Milazzo - Italy", "value": "port739"},
                                    {
                                        "label": "Sodertalje - Sweden",
                                        "value": "port1209",
                                    },
                                    {"label": "Agadir - Morocco", "value": "port10"},
                                    {
                                        "label": "Duluth - United States",
                                        "value": "port1236",
                                    },
                                    {"label": "Imabari - Japan", "value": "port490"},
                                    {
                                        "label": "Bridgetown - Barbados",
                                        "value": "port171",
                                    },
                                    {
                                        "label": "Saint John - Canada",
                                        "value": "port1219",
                                    },
                                    {"label": "Uno - Japan", "value": "port1343"},
                                    {
                                        "label": "Quy Nhon - Vietnam",
                                        "value": "port1078",
                                    },
                                    {"label": "Shuwaikh - Kuwait", "value": "port25"},
                                    {
                                        "label": "Jaigad Port - India",
                                        "value": "port511",
                                    },
                                    {
                                        "label": "Palm Beach - United States",
                                        "value": "port876",
                                    },
                                    {
                                        "label": "Thathong - Thailand",
                                        "value": "port1288",
                                    },
                                    {
                                        "label": "Wilmington, NC - United States",
                                        "value": "port1399",
                                    },
                                    {
                                        "label": "Lae - Papua New Guinea",
                                        "value": "port624",
                                    },
                                    {
                                        "label": "Astrakhan Port - Russian Federation",
                                        "value": "port76",
                                    },
                                    {
                                        "label": "Galveston - United States",
                                        "value": "port373",
                                    },
                                    {"label": "Conakry - Guinea", "value": "port258"},
                                    {
                                        "label": "Port Au Prince - Haiti",
                                        "value": "port934",
                                    },
                                    {
                                        "label": "Port Akdeniz - Turkiye",
                                        "value": "port54",
                                    },
                                    {
                                        "label": "Ngqura - South Africa",
                                        "value": "port2063",
                                    },
                                    {"label": "Halmstad - Sweden", "value": "port444"},
                                    {
                                        "label": "Pelabuhan Sungai Udang - Malaysia",
                                        "value": "port892",
                                    },
                                    {
                                        "label": "Eemshaven - The Netherlands",
                                        "value": "port316",
                                    },
                                    {"label": "Onoda - Japan", "value": "port852"},
                                    {
                                        "label": "Progreso Yucatan - Mexico",
                                        "value": "port1023",
                                    },
                                    {
                                        "label": "Porto Grande - Cabo Verde",
                                        "value": "port1009",
                                    },
                                    {"label": "Tallinn - Estonia", "value": "port1258"},
                                    {
                                        "label": "Charlotte Amalie - United States Virgin Islands",
                                        "value": "port233",
                                    },
                                    {"label": "Varna - Bulgaria", "value": "port1355"},
                                    {
                                        "label": "Guangxi Beibu Gulf Port - China",
                                        "value": "port424",
                                    },
                                    {"label": "Beira - Mozambique", "value": "port137"},
                                    {
                                        "label": "Guangdong Yangjiang Port - China",
                                        "value": "port423",
                                    },
                                    {"label": "Tromso - Norway", "value": "port1321"},
                                    {
                                        "label": "Fort De France - Martinique",
                                        "value": "port350",
                                    },
                                    {
                                        "label": "Seattle - United States",
                                        "value": "port1175",
                                    },
                                    {"label": "Dafeng - China", "value": "port2116"},
                                    {
                                        "label": "Nassau - The Bahamas",
                                        "value": "port798",
                                    },
                                    {"label": "Male - Maldives", "value": "port689"},
                                    {"label": "Tachibana - Japan", "value": "port1247"},
                                    {
                                        "label": "Skikda (Port Methanier) - Algeria",
                                        "value": "port969",
                                    },
                                    {
                                        "label": "Rouge River - United States",
                                        "value": "port1115",
                                    },
                                    {
                                        "label": "Arkhangelsk - Russian Federation",
                                        "value": "port68",
                                    },
                                    {
                                        "label": "Taman - Russian Federation",
                                        "value": "port978",
                                    },
                                    {"label": "Gulei - China", "value": "port2113"},
                                    {
                                        "label": "Reykjavik - Iceland",
                                        "value": "port1098",
                                    },
                                    {
                                        "label": "Saganoseki - Japan",
                                        "value": "port1119",
                                    },
                                    {"label": "Dandong - China", "value": "port277"},
                                    {"label": "Himekawa - Japan", "value": "port472"},
                                    {"label": "Kokkola - Finland", "value": "port586"},
                                    {"label": "Hososhima - Japan", "value": "port480"},
                                    {"label": "Weipa - Australia", "value": "port1387"},
                                    {"label": "Sarnia - Canada", "value": "port1166"},
                                    {
                                        "label": "Amamapare - Indonesia",
                                        "value": "port41",
                                    },
                                    {
                                        "label": "Freetown - Sierra Leone",
                                        "value": "port360",
                                    },
                                    {"label": "Bejaia - Algeria", "value": "port138"},
                                    {"label": "Shui Dong - China", "value": "port1196"},
                                    {"label": "Aviles - Spain", "value": "port83"},
                                    {"label": "Matsusaka - Japan", "value": "port719"},
                                    {"label": "El Sokhna - Egypt", "value": "port828"},
                                    {
                                        "label": "Vysotsk - Russian Federation",
                                        "value": "port378",
                                    },
                                    {"label": "Midia - Romania", "value": "port737"},
                                    {
                                        "label": "Pointe A Pierre - Trinidad and Tobago",
                                        "value": "port921",
                                    },
                                    {
                                        "label": "Napier - New Zealand",
                                        "value": "port794",
                                    },
                                    {"label": "Odense - Denmark", "value": "port842"},
                                    {
                                        "label": "Saldanha Bay - South Africa",
                                        "value": "port1133",
                                    },
                                    {"label": "Vitoria - Brazil", "value": "port1368"},
                                    {
                                        "label": "Grimsby - United Kingdom",
                                        "value": "port421",
                                    },
                                    {
                                        "label": "Richmond, CA - United States",
                                        "value": "port920",
                                    },
                                    {
                                        "label": "Ishikari Bay New Port - Japan",
                                        "value": "port501",
                                    },
                                    {
                                        "label": "Townsville - Australia",
                                        "value": "port1315",
                                    },
                                    {
                                        "label": "Puerto Caldera - Costa Rica",
                                        "value": "port1032",
                                    },
                                    {
                                        "label": "Noumea - New Caledonia",
                                        "value": "port832",
                                    },
                                    {"label": "Port Sudan - Sudan", "value": "port977"},
                                    {"label": "Gavle - Sweden", "value": "port379"},
                                    {"label": "Shantou - China", "value": "port1187"},
                                    {
                                        "label": "Portland - United States",
                                        "value": "port993",
                                    },
                                    {
                                        "label": "Kristiansand - Norway",
                                        "value": "port600",
                                    },
                                    {"label": "Catania - Italy", "value": "port222"},
                                    {
                                        "label": "Trondheim - Norway",
                                        "value": "port1322",
                                    },
                                    {"label": "Hamilton - Canada", "value": "port447"},
                                    {
                                        "label": "Castries - St.  Lucia",
                                        "value": "port221",
                                    },
                                    {
                                        "label": "Dachan Bay - China",
                                        "value": "port2029",
                                    },
                                    {
                                        "label": "Famagusta - Turkiye",
                                        "value": "port338",
                                    },
                                    {"label": "San Vicente - Chile", "value": "port92"},
                                    {
                                        "label": "Songkhla - Thailand",
                                        "value": "port1211",
                                    },
                                    {
                                        "label": "Walvis Bay - Namibia",
                                        "value": "port1381",
                                    },
                                    {"label": "Maizuru - Japan", "value": "port682"},
                                    {
                                        "label": "Zonguldak - Turkiye",
                                        "value": "port1430",
                                    },
                                    {"label": "Maloy - Norway", "value": "port692"},
                                    {"label": "Paldiski - Estonia", "value": "port874"},
                                    {"label": "Drammen - Norway", "value": "port302"},
                                    {"label": "Mazatlan - Mexico", "value": "port723"},
                                    {
                                        "label": "Marina Di Carrara - Italy",
                                        "value": "port706",
                                    },
                                    {"label": "Benghazi - Libya", "value": "port110"},
                                    {
                                        "label": "Prince Rupert - Canada",
                                        "value": "port1021",
                                    },
                                    {
                                        "label": "Mina Al Ahmadi - Kuwait",
                                        "value": "port743",
                                    },
                                    {"label": "Vassiliko - Cyprus", "value": "port291"},
                                    {
                                        "label": "Geelong - Australia",
                                        "value": "port383",
                                    },
                                    {"label": "Botas - Turkiye", "value": "port162"},
                                    {"label": "Oxelosund - Sweden", "value": "port868"},
                                    {"label": "Bordeaux - France", "value": "port158"},
                                    {"label": "Naantali - Finland", "value": "port783"},
                                    {
                                        "label": "Bandar Khomeini - Iran",
                                        "value": "port108",
                                    },
                                    {"label": "Sikka - India", "value": "port1199"},
                                    {"label": "Varberg - Sweden", "value": "port1353"},
                                    {"label": "Izmail - Ukraine", "value": "port2001"},
                                    {"label": "Brevik - Norway", "value": "port169"},
                                    {
                                        "label": "Uusikaupunki - Finland",
                                        "value": "port2282",
                                    },
                                    {"label": "Masan - Korea", "value": "port715"},
                                    {"label": "Olvia - Ukraine", "value": "port2003"},
                                    {"label": "Tsuruga - Japan", "value": "port1325"},
                                    {"label": "Manaus - Brazil", "value": "port693"},
                                    {
                                        "label": "Amirabad Port - Iran",
                                        "value": "port43",
                                    },
                                    {"label": "Alicante - Spain", "value": "port34"},
                                    {
                                        "label": "Ipswich - United Kingdom",
                                        "value": "port498",
                                    },
                                    {
                                        "label": "Kemaman Harbor - Malaysia",
                                        "value": "port556",
                                    },
                                    {"label": "Basuo - China", "value": "port123"},
                                    {
                                        "label": "Bahia De Valparaiso - Chile",
                                        "value": "port89",
                                    },
                                    {"label": "Saiki - Japan", "value": "port2181"},
                                    {
                                        "label": "Brunswick - United States",
                                        "value": "port180",
                                    },
                                    {
                                        "label": "Taganrog - Russian Federation",
                                        "value": "port1249",
                                    },
                                    {
                                        "label": "New Westminster - Canada",
                                        "value": "port814",
                                    },
                                    {"label": "Batumi - Georgia", "value": "port127"},
                                    {
                                        "label": "Ponta Delgada - Portugal",
                                        "value": "port924",
                                    },
                                    {"label": "Vasteras - Sweden", "value": "port1356"},
                                    {"label": "Volos - Greece", "value": "port1373"},
                                    {
                                        "label": "Al Adabiyah - Egypt",
                                        "value": "port321",
                                    },
                                    {
                                        "label": "Sampit - Indonesia",
                                        "value": "port1138",
                                    },
                                    {"label": "Port Est - Reunion", "value": "port950"},
                                    {
                                        "label": "Sillamae - Estonia",
                                        "value": "port2133",
                                    },
                                    {"label": "Split - Croatia", "value": "port1218"},
                                    {"label": "Tripoli - Lebanon", "value": "port1274"},
                                    {
                                        "label": "Port Owendo - Gabon",
                                        "value": "port973",
                                    },
                                    {"label": "Karsto - Norway", "value": "port547"},
                                    {
                                        "label": "Honolulu - United States",
                                        "value": "port476",
                                    },
                                    {
                                        "label": "Muara Harbor - Brunei Darussalam",
                                        "value": "port774",
                                    },
                                    {"label": "Reni - Ukraine", "value": "port2002"},
                                    {"label": "Pori - Finland", "value": "port698"},
                                    {"label": "Bari - Italy", "value": "port119"},
                                    {"label": "Kamaishi - Japan", "value": "port533"},
                                    {"label": "Ofunato - Japan", "value": "port844"},
                                    {"label": "Trabzon - Turkiye", "value": "port1316"},
                                    {"label": "Koge - Denmark", "value": "port585"},
                                    {
                                        "label": "Porto De Mucuripe - Brazil",
                                        "value": "port1001",
                                    },
                                    {"label": "Tornio - Finland", "value": "port1311"},
                                    {"label": "Ancona - Italy", "value": "port49"},
                                    {"label": "Takamatsu - Japan", "value": "port1254"},
                                    {
                                        "label": "Makhachkala - Russian Federation",
                                        "value": "port684",
                                    },
                                    {"label": "Heraklion - Greece", "value": "port500"},
                                    {
                                        "label": "Pelabuhan Tanjung Wangi - Indonesia",
                                        "value": "port893",
                                    },
                                    {
                                        "label": "Kendari - Indonesia",
                                        "value": "port558",
                                    },
                                    {
                                        "label": "Willemstad - Curacao",
                                        "value": "port1397",
                                    },
                                    {"label": "Aomori - Japan", "value": "port59"},
                                    {
                                        "label": "Port Dickson - Malaysia",
                                        "value": "port945",
                                    },
                                    {"label": "Sfax - Tunisia", "value": "port733"},
                                    {"label": "Randers - Denmark", "value": "port1085"},
                                    {"label": "Rijeka - Croatia", "value": "port1101"},
                                    {"label": "Kamsar - Guinea", "value": "port536"},
                                    {
                                        "label": "Port of Saint Johns - Antigua and Barbuda",
                                        "value": "port1221",
                                    },
                                    {"label": "Ampenan - Indonesia", "value": "port44"},
                                    {
                                        "label": "Bunbury - Australia",
                                        "value": "port190",
                                    },
                                    {
                                        "label": "Thunder Bay - Canada",
                                        "value": "port1295",
                                    },
                                    {"label": "Hannan - Japan", "value": "port452"},
                                    {"label": "Karabiga - Turkiye", "value": "port542"},
                                    {
                                        "label": "Civitavecchia - Italy",
                                        "value": "port247",
                                    },
                                    {
                                        "label": "Port Cartier - Canada",
                                        "value": "port938",
                                    },
                                    {
                                        "label": "Tynemouth - United Kingdom",
                                        "value": "port1334",
                                    },
                                    {"label": "Mokpo - Korea", "value": "port2184"},
                                    {
                                        "label": "Mohammedia - Morocco",
                                        "value": "port756",
                                    },
                                    {"label": "Malaga - Spain", "value": "port686"},
                                    {
                                        "label": "Boston - United States",
                                        "value": "port159",
                                    },
                                    {"label": "Kupang - Indonesia", "value": "port609"},
                                    {
                                        "label": "Nouakchott - Mauritania",
                                        "value": "port831",
                                    },
                                    {
                                        "label": "Kavkaz Oil Terminal - Russian Federation",
                                        "value": "port554",
                                    },
                                    {
                                        "label": "Zarate - Argentina",
                                        "value": "port1422",
                                    },
                                    {
                                        "label": "Bahia De Matarani - Peru",
                                        "value": "port88",
                                    },
                                    {
                                        "label": "Kingstown - St.  Vincent and the Grenadines",
                                        "value": "port574",
                                    },
                                    {
                                        "label": "Donggala - Indonesia",
                                        "value": "port297",
                                    },
                                    {
                                        "label": "Iloilo - Philippines",
                                        "value": "port2055",
                                    },
                                    {
                                        "label": "Newport - United Kingdom",
                                        "value": "port817",
                                    },
                                    {"label": "Mykolaiv - Ukraine", "value": "port782"},
                                    {"label": "Gebig - Brazil", "value": "port382"},
                                    {
                                        "label": "Pichilingue - Mexico",
                                        "value": "port905",
                                    },
                                    {
                                        "label": "Frederiksvaerk - Denmark",
                                        "value": "port359",
                                    },
                                    {"label": "Namikata - Japan", "value": "port2174"},
                                    {
                                        "label": "Kota Baru - Indonesia",
                                        "value": "port595",
                                    },
                                    {"label": "Annaba - Algeria", "value": "port53"},
                                    {"label": "Safi - Morocco", "value": "port1118"},
                                    {"label": "Rorvik - Norway", "value": "port1107"},
                                    {
                                        "label": "Figueira Da Foz - Portugal",
                                        "value": "port345",
                                    },
                                    {
                                        "label": "Corinto - Nicaragua",
                                        "value": "port261",
                                    },
                                    {
                                        "label": "Port Aransas - United States",
                                        "value": "port932",
                                    },
                                    {
                                        "label": "Vado Ligure - Italy",
                                        "value": "port1083",
                                    },
                                    {
                                        "label": "La Libertad - Ecuador",
                                        "value": "port619",
                                    },
                                    {"label": "Tokachi - Japan", "value": "port1303"},
                                    {
                                        "label": "Wellington - New Zealand",
                                        "value": "port1388",
                                    },
                                    {"label": "Guaymas - Mexico", "value": "port427"},
                                    {"label": "Brest - France", "value": "port1084"},
                                    {"label": "Paita - Peru", "value": "port873"},
                                    {
                                        "label": "Stagen - Indonesia",
                                        "value": "port1224",
                                    },
                                    {
                                        "label": "Rabigh - Saudi Arabia",
                                        "value": "port1081",
                                    },
                                    {
                                        "label": "Porto Da Praia - Cabo Verde",
                                        "value": "port998",
                                    },
                                    {
                                        "label": "Newport News - United States",
                                        "value": "port818",
                                    },
                                    {
                                        "label": "Matadi - Democratic Republic of the Congo",
                                        "value": "port717",
                                    },
                                    {"label": "Bayonne - France", "value": "port131"},
                                    {"label": "Kolding - Denmark", "value": "port588"},
                                    {
                                        "label": "Goole - United Kingdom",
                                        "value": "port404",
                                    },
                                    {
                                        "label": "Sao Francisco - Brazil",
                                        "value": "port1161",
                                    },
                                    {"label": "Patras - Greece", "value": "port889"},
                                    {"label": "Anzali - Iran", "value": "port58"},
                                    {"label": "Djupviken - Norway", "value": "port296"},
                                    {
                                        "label": "Pulau Baai - Indonesia",
                                        "value": "port1061",
                                    },
                                    {"label": "Aden - Yemen", "value": "port9"},
                                    {"label": "Lulea - Sweden", "value": "port670"},
                                    {
                                        "label": "Portsmouth Harbour - United Kingdom",
                                        "value": "port1014",
                                    },
                                    {"label": "Tuxpan - Mexico", "value": "port1332"},
                                    {
                                        "label": "Geraldton - Australia",
                                        "value": "port391",
                                    },
                                    {
                                        "label": "Sanshandaocun - China",
                                        "value": "port1151",
                                    },
                                    {
                                        "label": "Thamesport - United Kingdom",
                                        "value": "port1289",
                                    },
                                    {
                                        "label": "Plymouth - United Kingdom",
                                        "value": "port914",
                                    },
                                    {"label": "Kherson - Ukraine", "value": "port2004"},
                                    {
                                        "label": "Longview - United States",
                                        "value": "port2267",
                                    },
                                    {"label": "Takoradi - Ghana", "value": "port1255"},
                                    {
                                        "label": "Pascagoula - United States",
                                        "value": "port888",
                                    },
                                    {"label": "Oulu - Finland", "value": "port867"},
                                    {
                                        "label": "San Pedro - Cote dIvoire",
                                        "value": "port1146",
                                    },
                                    {
                                        "label": "Sept Iles - Canada",
                                        "value": "port1181",
                                    },
                                    {
                                        "label": "Papeete - French Polynesia",
                                        "value": "port882",
                                    },
                                    {
                                        "label": "Whangerei - New Zealand",
                                        "value": "port1393",
                                    },
                                    {
                                        "label": "Tanjung Sangata - Indonesia",
                                        "value": "port1270",
                                    },
                                    {"label": "Chaozhou - China", "value": "port229"},
                                    {"label": "Brindisi - Italy", "value": "port173"},
                                    {
                                        "label": "Djen-Djen - Algeria",
                                        "value": "port293",
                                    },
                                    {"label": "Rades - Tunisia", "value": "port2047"},
                                    {
                                        "label": "Puerto Nuevo - Colombia",
                                        "value": "port1054",
                                    },
                                    {"label": "Ferrol - Spain", "value": "port344"},
                                    {"label": "Bushehr - Iran", "value": "port196"},
                                    {"label": "Kunda - Estonia", "value": "port607"},
                                    {
                                        "label": "La Plata - Argentina",
                                        "value": "port621",
                                    },
                                    {
                                        "label": "Nouadhibou - Mauritania",
                                        "value": "port830",
                                    },
                                    {"label": "Yalova - Turkiye", "value": "port1407"},
                                    {
                                        "label": "Port Hueneme - United States",
                                        "value": "port956",
                                    },
                                    {"label": "Omaezaki - Japan", "value": "port2041"},
                                    {
                                        "label": "Toamasina - Madagascar",
                                        "value": "port1301",
                                    },
                                    {
                                        "label": "Puerto Cabello - Venezuela",
                                        "value": "port1029",
                                    },
                                    {
                                        "label": "Slagentangen - Norway",
                                        "value": "port1208",
                                    },
                                    {"label": "Haimen - China", "value": "port438"},
                                    {"label": "Moss - Sweden", "value": "port770"},
                                    {"label": "Palermo - Italy", "value": "port1008"},
                                    {
                                        "label": "Oranjestad - Bonaire,  Saint Eustatius and Saba",
                                        "value": "port857",
                                    },
                                    {
                                        "label": "Nacala - Mozambique",
                                        "value": "port784",
                                    },
                                    {
                                        "label": "Port Adelaide - Australia",
                                        "value": "port929",
                                    },
                                    {"label": "Bizerte - Tunisia", "value": "port115"},
                                    {
                                        "label": "Dhamra Port - India",
                                        "value": "port290",
                                    },
                                    {"label": "Baubau - Indonesia", "value": "port128"},
                                    {
                                        "label": "Waterford - Ireland",
                                        "value": "port1384",
                                    },
                                    {"label": "Kuching - Malaysia", "value": "port604"},
                                    {
                                        "label": "Abbot Point - Australia",
                                        "value": "port0",
                                    },
                                    {
                                        "label": "Stenungsund - Sweden",
                                        "value": "port1227",
                                    },
                                    {
                                        "label": "Vancouver - United States",
                                        "value": "port1351",
                                    },
                                    {
                                        "label": "Boston - United Kingdom",
                                        "value": "port160",
                                    },
                                    {"label": "Suva - Fiji", "value": "port1240"},
                                    {"label": "Mariel - Cuba", "value": "port704"},
                                    {
                                        "label": "Madre De Deus - Brazil",
                                        "value": "port677",
                                    },
                                    {
                                        "label": "Victoria - Malaysia",
                                        "value": "port1360",
                                    },
                                    {
                                        "label": "Sidi Kerir - Egypt",
                                        "value": "port2129",
                                    },
                                    {"label": "Naoetsu - Japan", "value": "port793"},
                                    {
                                        "label": "Stockholm - Sweden",
                                        "value": "port1228",
                                    },
                                    {"label": "Kiel - Germany", "value": "port564"},
                                    {"label": "Haikou - China", "value": "port437"},
                                    {"label": "Mormugao - India", "value": "port709"},
                                    {
                                        "label": "Saint Georges - Grenada",
                                        "value": "port1223",
                                    },
                                    {"label": "Larnaca - Cyprus", "value": "port633"},
                                    {"label": "Ensenada - Mexico", "value": "port326"},
                                    {
                                        "label": "Sabetta - Russian Federation",
                                        "value": "port2215",
                                    },
                                    {"label": "Sousse - Tunisia", "value": "port1213"},
                                    {"label": "Tripoli - Libya", "value": "port748"},
                                    {"label": "Raahe - Finland", "value": "port1079"},
                                    {
                                        "label": "Haroysundet - Norway",
                                        "value": "port456",
                                    },
                                    {"label": "Kavala - Greece", "value": "port552"},
                                    {"label": "Lautoka - Fiji", "value": "port636"},
                                    {
                                        "label": "Kattupalli - India",
                                        "value": "port2038",
                                    },
                                    {"label": "Monfalcone - Italy", "value": "port758"},
                                    {
                                        "label": "Port of Can Tho - Vietnam",
                                        "value": "port983",
                                    },
                                    {"label": "Kemi - Finland", "value": "port557"},
                                    {"label": "Otaru - Japan", "value": "port866"},
                                    {"label": "Aabenraa - Denmark", "value": "port1"},
                                    {
                                        "label": "Malabo - Equatorial Guinea",
                                        "value": "port685",
                                    },
                                    {
                                        "label": "Manokwari Road - Indonesia",
                                        "value": "port696",
                                    },
                                    {
                                        "label": "Nghe Tinh - Vietnam",
                                        "value": "port819",
                                    },
                                    {
                                        "label": "Vung Tau - Vietnam",
                                        "value": "port1375",
                                    },
                                    {
                                        "label": "Baton Rouge - United States",
                                        "value": "port126",
                                    },
                                    {
                                        "label": "New Holland - United Kingdom",
                                        "value": "port810",
                                    },
                                    {
                                        "label": "Nueva Palmira - Uruguay",
                                        "value": "port2258",
                                    },
                                    {
                                        "label": "Toros Gubre - Turkiye",
                                        "value": "port1313",
                                    },
                                    {
                                        "label": "Nelson - New Zealand",
                                        "value": "port804",
                                    },
                                    {"label": "Jeju - Korea", "value": "port2284"},
                                    {"label": "Kiire - Japan", "value": "port566"},
                                    {"label": "Bonny - Nigeria", "value": "port155"},
                                    {"label": "Sakato - Japan", "value": "port1130"},
                                    {
                                        "label": "Petropavlovsk-Kamchatskiy - Russian Federation",
                                        "value": "port2216",
                                    },
                                    {
                                        "label": "Otago - New Zealand",
                                        "value": "port2011",
                                    },
                                    {"label": "Antofagasta - Chile", "value": "port56"},
                                    {"label": "Duqm - Oman", "value": "port984"},
                                    {
                                        "label": "Ajman - United Arab Emirates",
                                        "value": "port13",
                                    },
                                    {
                                        "label": "Warren Point - United Kingdom",
                                        "value": "port1382",
                                    },
                                    {
                                        "label": "Guaiba Island Terminal - Brazil",
                                        "value": "port422",
                                    },
                                    {
                                        "label": "Port of Yeosu - Korea",
                                        "value": "port2033",
                                    },
                                    {"label": "Sasebo - Japan", "value": "port2175"},
                                    {
                                        "label": "Whiffen Head - Canada",
                                        "value": "port256",
                                    },
                                    {"label": "Apra Harbor - Guam", "value": "port61"},
                                    {"label": "Husum - Sweden", "value": "port486"},
                                    {
                                        "label": "Port Manatee - United States",
                                        "value": "port967",
                                    },
                                    {"label": "Larvik - Norway", "value": "port634"},
                                    {"label": "Hamada - Japan", "value": "port445"},
                                    {"label": "Karatsu - Japan", "value": "port545"},
                                    {
                                        "label": "Padang - Indonesia",
                                        "value": "port2156",
                                    },
                                    {"label": "Mariupol - Ukraine", "value": "port707"},
                                    {"label": "Kalmar - Sweden", "value": "port531"},
                                    {
                                        "label": "Haydarpasa - Turkiye",
                                        "value": "port457",
                                    },
                                    {"label": "Onne - Nigeria", "value": "port851"},
                                    {
                                        "label": "Slavyanka - Russian Federation",
                                        "value": "port2214",
                                    },
                                    {"label": "Almeria - Spain", "value": "port35"},
                                    {"label": "Berbera - Somalia", "value": "port146"},
                                    {
                                        "label": "Timaru - New Zealand",
                                        "value": "port1299",
                                    },
                                    {
                                        "label": "Flekkefjord - Norway",
                                        "value": "port348",
                                    },
                                    {
                                        "label": "Topolobampo - Mexico",
                                        "value": "port1310",
                                    },
                                    {
                                        "label": "Two Harbors - United States",
                                        "value": "port1333",
                                    },
                                    {
                                        "label": "Praia da Vitoria - Portugal",
                                        "value": "port1018",
                                    },
                                    {"label": "Stura - Norway", "value": "port1231"},
                                    {"label": "Suakin - Sudan", "value": "port1172"},
                                    {"label": "Belem - Brazil", "value": "port140"},
                                    {"label": "Benoa - Indonesia", "value": "port145"},
                                    {
                                        "label": "Port Dover - Canada",
                                        "value": "port946",
                                    },
                                    {"label": "Arrecife - Spain", "value": "port69"},
                                    {"label": "Al-hudaydah - Yemen", "value": "port18"},
                                    {
                                        "label": "Sundsvall - Sweden",
                                        "value": "port1235",
                                    },
                                    {
                                        "label": "Quequen - Argentina",
                                        "value": "port1077",
                                    },
                                    {
                                        "label": "Calaca - Philippines",
                                        "value": "port2209",
                                    },
                                    {
                                        "label": "Delta Terminal - Turkiye",
                                        "value": "port286",
                                    },
                                    {
                                        "label": "Londonderry - United Kingdom",
                                        "value": "port660",
                                    },
                                    {"label": "Markenes - Norway", "value": "port708"},
                                    {
                                        "label": "San Diego - United States",
                                        "value": "port1140",
                                    },
                                    {"label": "Skagen - Denmark", "value": "port1204"},
                                    {"label": "Coronel - Chile", "value": "port263"},
                                    {"label": "Iquique - Chile", "value": "port499"},
                                    {
                                        "label": "Shannon Foynes - Ireland",
                                        "value": "port353",
                                    },
                                    {"label": "Takuma - Japan", "value": "port1256"},
                                    {
                                        "label": "Bandar-E Pars Terminal - Iran",
                                        "value": "port105",
                                    },
                                    {
                                        "label": "Rada De Arica - Chile",
                                        "value": "port1082",
                                    },
                                    {"label": "Pitea - Sweden", "value": "port909"},
                                    {
                                        "label": "Hambantota - Sri Lanka",
                                        "value": "port678",
                                    },
                                    {
                                        "label": "Ras Al-Khair - Saudi Arabia",
                                        "value": "port1089",
                                    },
                                    {
                                        "label": "Paarden Baai - (Orangestad) - Aruba",
                                        "value": "port871",
                                    },
                                    {
                                        "label": "Stora Jatterson - Sweden",
                                        "value": "port1230",
                                    },
                                    {
                                        "label": "Umea Hamn - Sweden",
                                        "value": "port1339",
                                    },
                                    {
                                        "label": "Skelleftehamn - Sweden",
                                        "value": "port1205",
                                    },
                                    {"label": "Garrucha - Spain", "value": "port1041"},
                                    {"label": "Puerto Ilo - Peru", "value": "port1047"},
                                    {
                                        "label": "Khor al Fakkan - United Arab Emirates",
                                        "value": "port561",
                                    },
                                    {
                                        "label": "San Nicolas - Argentina",
                                        "value": "port1145",
                                    },
                                    {"label": "Gabes - Tunisia", "value": "port371"},
                                    {"label": "Alvika - Norway", "value": "port39"},
                                    {
                                        "label": "Benicia - United States",
                                        "value": "port144",
                                    },
                                    {
                                        "label": "Puerto Del Rosario - Spain",
                                        "value": "port1046",
                                    },
                                    {
                                        "label": "Bandar Abbas - Iran",
                                        "value": "port107",
                                    },
                                    {
                                        "label": "Villagarcia De Arosa - Spain",
                                        "value": "port1365",
                                    },
                                    {
                                        "label": "Das Island - United Arab Emirates",
                                        "value": "port2237",
                                    },
                                    {
                                        "label": "Heysham - United Kingdom",
                                        "value": "port462",
                                    },
                                    {
                                        "label": "PLTU Semen Tonasa - Indonesia",
                                        "value": "port869",
                                    },
                                    {
                                        "label": "Cleveland - United States",
                                        "value": "port249",
                                    },
                                    {"label": "Parnu - Estonia", "value": "port887"},
                                    {"label": "Imbituba - Brazil", "value": "port492"},
                                    {
                                        "label": "Kalama - United States",
                                        "value": "port2253",
                                    },
                                    {"label": "Motril - Spain", "value": "port772"},
                                    {"label": "Chioggia - Italy", "value": "port1003"},
                                    {
                                        "label": "Poole - United Kingdom",
                                        "value": "port926",
                                    },
                                    {
                                        "label": "San Pedro De Macoris - Dominican Republic",
                                        "value": "port1147",
                                    },
                                    {
                                        "label": "Qushan Island - China",
                                        "value": "port2111",
                                    },
                                    {
                                        "label": "Iligan - Philippines",
                                        "value": "port488",
                                    },
                                    {
                                        "label": "Villanueva - Philippines",
                                        "value": "port1366",
                                    },
                                    {
                                        "label": "Thyboron - Denmark",
                                        "value": "port1296",
                                    },
                                    {"label": "Vikanes - Norway", "value": "port1364"},
                                    {"label": "Durres - Albania", "value": "port312"},
                                    {
                                        "label": "Solvesborg - Sweden",
                                        "value": "port1210",
                                    },
                                    {
                                        "label": "New Plymouth - New Zealand",
                                        "value": "port813",
                                    },
                                    {
                                        "label": "Port Nador - Morocco",
                                        "value": "port971",
                                    },
                                    {"label": "Macau - Macao SAR", "value": "port674"},
                                    {
                                        "label": "Toledo - United States",
                                        "value": "port1306",
                                    },
                                    {
                                        "label": "Pelabuhan Sansakan - Malaysia",
                                        "value": "port891",
                                    },
                                    {
                                        "label": "Cirebon - Indonesia",
                                        "value": "port246",
                                    },
                                    {
                                        "label": "San Giorgio - Italy",
                                        "value": "port1142",
                                    },
                                    {"label": "Fukui - Japan", "value": "port363"},
                                    {"label": "Portocel - Brazil", "value": "port1012"},
                                    {"label": "Warri - Nigeria", "value": "port1383"},
                                    {"label": "Chofu - Japan", "value": "port2179"},
                                    {
                                        "label": "Landskrona - Sweden",
                                        "value": "port2226",
                                    },
                                    {
                                        "label": "Salina Cruz - Mexico",
                                        "value": "port1136",
                                    },
                                    {
                                        "label": "Zanzibar - Tanzania",
                                        "value": "port1421",
                                    },
                                    {
                                        "label": "Thamshamm - Norway",
                                        "value": "port1290",
                                    },
                                    {
                                        "label": "Punta Arenas - Chile",
                                        "value": "port1432",
                                    },
                                    {"label": "Inkoo - Finland", "value": "port497"},
                                    {"label": "Tawau - Malaysia", "value": "port2192"},
                                    {
                                        "label": "Jakobstad - Finland",
                                        "value": "port515",
                                    },
                                    {
                                        "label": "Harlingen - The Netherlands",
                                        "value": "port454",
                                    },
                                    {"label": "Lirquen - Chile", "value": "port652"},
                                    {
                                        "label": "Comodoro Rivadavia - Argentina",
                                        "value": "port257",
                                    },
                                    {
                                        "label": "Van Phong - Vietnam",
                                        "value": "port2262",
                                    },
                                    {"label": "Khoms - Libya", "value": "port562"},
                                    {
                                        "label": "Tg. Sorong - Indonesia",
                                        "value": "port1287",
                                    },
                                    {"label": "Piombino - Italy", "value": "port1013"},
                                    {
                                        "label": "Portland - Australia",
                                        "value": "port992",
                                    },
                                    {
                                        "label": "Port Harcourt - Nigeria",
                                        "value": "port954",
                                    },
                                    {
                                        "label": "Henza Island - Japan",
                                        "value": "port2173",
                                    },
                                    {
                                        "label": "Santo Domingo - Dominican Republic",
                                        "value": "port1158",
                                    },
                                    {"label": "Turku - Finland", "value": "port368"},
                                    {"label": "Bar - Montenegro", "value": "port116"},
                                    {"label": "Funchal - Portugal", "value": "port367"},
                                    {"label": "Narvik - Norway", "value": "port796"},
                                    {
                                        "label": "Anchorage - United States",
                                        "value": "port48",
                                    },
                                    {"label": "Nanao - Japan", "value": "port790"},
                                    {
                                        "label": "Portland Harbour - United Kingdom",
                                        "value": "port994",
                                    },
                                    {"label": "Kaskinen - Finland", "value": "port550"},
                                    {
                                        "label": "Probolinggo - Indonesia",
                                        "value": "port1022",
                                    },
                                    {
                                        "label": "Caleta Patillos - Chile",
                                        "value": "port208",
                                    },
                                    {
                                        "label": "Port De Kribi - Cameroon",
                                        "value": "port943",
                                    },
                                    {"label": "Monrovia - Liberia", "value": "port762"},
                                    {
                                        "label": "Mostaganem - Algeria",
                                        "value": "port771",
                                    },
                                    {"label": "Sauda - Norway", "value": "port1169"},
                                    {
                                        "label": "East London - South Africa",
                                        "value": "port315",
                                    },
                                    {
                                        "label": "Georgetown - Cayman Islands",
                                        "value": "port389",
                                    },
                                    {"label": "Grenaa - Denmark", "value": "port419"},
                                    {
                                        "label": "Mongla - Bangladesh",
                                        "value": "port759",
                                    },
                                    {
                                        "label": "Falkenberg - Sweden",
                                        "value": "port335",
                                    },
                                    {"label": "Nyborg - Denmark", "value": "port837"},
                                    {"label": "Chiwan - China", "value": "port242"},
                                    {
                                        "label": "Bluff Harbor - New Zealand",
                                        "value": "port153",
                                    },
                                    {
                                        "label": "Cherry Point - United States",
                                        "value": "port236",
                                    },
                                    {
                                        "label": "Jayapura - Indonesia",
                                        "value": "port516",
                                    },
                                    {
                                        "label": "Romportmet - Romania",
                                        "value": "port2008",
                                    },
                                    {"label": "Tsingeli - Greece", "value": "port1323"},
                                    {
                                        "label": "Soyo Angola LNG Terminal - Angola",
                                        "value": "port1217",
                                    },
                                    {"label": "Harmac - Canada", "value": "port455"},
                                    {
                                        "label": "Shoreham Harbour - United Kingdom",
                                        "value": "port1194",
                                    },
                                    {
                                        "label": "Giurgiulesti Port - Moldova",
                                        "value": "port2005",
                                    },
                                    {
                                        "label": "Okpo (Geoje) - Korea",
                                        "value": "port2183",
                                    },
                                    {"label": "Cienfuegos - Cuba", "value": "port244"},
                                    {"label": "Onslow - Australia", "value": "port854"},
                                    {
                                        "label": "Providence - United States",
                                        "value": "port1024",
                                    },
                                    {
                                        "label": "Saint-Malo - France",
                                        "value": "port1124",
                                    },
                                    {
                                        "label": "Road Harbor - British Virgin Islands",
                                        "value": "port1106",
                                    },
                                    {"label": "Roseau - Dominica", "value": "port1110"},
                                    {
                                        "label": "La Guaira - Venezuela",
                                        "value": "port618",
                                    },
                                    {
                                        "label": "Port Angeles - Canada",
                                        "value": "port931",
                                    },
                                    {
                                        "label": "Anping - Taiwan Province of China",
                                        "value": "port2229",
                                    },
                                    {
                                        "label": "Palma de Mallorca - Spain",
                                        "value": "port1431",
                                    },
                                    {
                                        "label": "Souda (Chania) - Greece",
                                        "value": "port1212",
                                    },
                                    {"label": "Saida - Lebanon", "value": "port1173"},
                                    {
                                        "label": "Palmeira - Cabo Verde",
                                        "value": "port877",
                                    },
                                    {
                                        "label": "Clifton Pier - The Bahamas",
                                        "value": "port251",
                                    },
                                    {
                                        "label": "Brownsville - United States",
                                        "value": "port177",
                                    },
                                    {"label": "Odda - Norway", "value": "port841"},
                                    {
                                        "label": "Stockton - United States",
                                        "value": "port1229",
                                    },
                                    {
                                        "label": "Porto De Maceio - Brazil",
                                        "value": "port1000",
                                    },
                                    {"label": "Marin - Spain", "value": "port705"},
                                    {
                                        "label": "Santa Panagia - Italy",
                                        "value": "port2167",
                                    },
                                    {"label": "Safaga - Egypt", "value": "port191"},
                                    {
                                        "label": "Puerto Bolivar - Colombia",
                                        "value": "port1027",
                                    },
                                    {
                                        "label": "Puerto Bolivar - Ecuador",
                                        "value": "port1028",
                                    },
                                    {"label": "Lushun - China", "value": "port2117"},
                                    {
                                        "label": "Panama City - United States",
                                        "value": "port879",
                                    },
                                    {
                                        "label": "Hirtshals - Denmark",
                                        "value": "port467",
                                    },
                                    {
                                        "label": "Port Lavaca - United States",
                                        "value": "port963",
                                    },
                                    {
                                        "label": "Mogadishu - Somalia",
                                        "value": "port778",
                                    },
                                    {
                                        "label": "Baltiysk - Russian Federation",
                                        "value": "port104",
                                    },
                                    {
                                        "label": "Gorgon LNG - Australia",
                                        "value": "port406",
                                    },
                                    {
                                        "label": "Swanport - United States",
                                        "value": "port1241",
                                    },
                                    {
                                        "label": "Luanjiakou - China",
                                        "value": "port2115",
                                    },
                                    {
                                        "label": "Degrad Des Cannes - French Guiana",
                                        "value": "port284",
                                    },
                                    {
                                        "label": "Amuay (Bahia De Amuay) - Venezuela",
                                        "value": "port46",
                                    },
                                    {
                                        "label": "Puerto Plata - Dominican Republic",
                                        "value": "port1055",
                                    },
                                    {
                                        "label": "Rabaul - Papua New Guinea",
                                        "value": "port1080",
                                    },
                                    {"label": "Beihai - China", "value": "port136"},
                                    {"label": "Lorient - France", "value": "port663"},
                                    {"label": "Ahus - Sweden", "value": "port11"},
                                    {"label": "La Habana - Cuba", "value": "port86"},
                                    {
                                        "label": "Santiago De Cuba - Cuba",
                                        "value": "port1156",
                                    },
                                    {"label": "Lobito - Angola", "value": "port656"},
                                    {
                                        "label": "Stigsnaes - Denmark",
                                        "value": "port2125",
                                    },
                                    {
                                        "label": "Port Gentil - Gabon",
                                        "value": "port952",
                                    },
                                    {
                                        "label": "Covenas Offshore Term. - Colombia",
                                        "value": "port266",
                                    },
                                    {
                                        "label": "Hualien - Taiwan Province of China",
                                        "value": "port482",
                                    },
                                    {
                                        "label": "Honiara - Solomon Islands",
                                        "value": "port475",
                                    },
                                    {
                                        "label": "Bahia De Las Minas - Panama",
                                        "value": "port87",
                                    },
                                    {"label": "Posorja - Ecuador", "value": "port2032"},
                                    {
                                        "label": "Hammerfest - Norway",
                                        "value": "port449",
                                    },
                                    {
                                        "label": "Sandusky - United States",
                                        "value": "port1149",
                                    },
                                    {"label": "Nynashamn - Sweden", "value": "port838"},
                                    {"label": "Bruges - Belgium", "value": "port178"},
                                    {
                                        "label": "PelabuhanRatuCoalPowerPlant - Indonesia",
                                        "value": "port894",
                                    },
                                    {"label": "Gove - Australia", "value": "port411"},
                                    {
                                        "label": "San Andres - Colombia",
                                        "value": "port2278",
                                    },
                                    {
                                        "label": "Gorontalo - Indonesia",
                                        "value": "port407",
                                    },
                                    {
                                        "label": "Devonport - Australia",
                                        "value": "port288",
                                    },
                                    {
                                        "label": "EL Segundo - United States",
                                        "value": "port314",
                                    },
                                    {"label": "As Suways - Egypt", "value": "port71"},
                                    {
                                        "label": "Basseterre - St.  Kitts and Nevis",
                                        "value": "port122",
                                    },
                                    {
                                        "label": "Sassnitz - Germany",
                                        "value": "port1168",
                                    },
                                    {
                                        "label": "Ardalstangen - Norway",
                                        "value": "port64",
                                    },
                                    {"label": "Salaverry - Peru", "value": "port1132"},
                                    {"label": "Drogheda - Ireland", "value": "port303"},
                                    {"label": "Mackay - Australia", "value": "port675"},
                                    {
                                        "label": "Vyborg - Russian Federation",
                                        "value": "port1376",
                                    },
                                    {"label": "Ploce - Croatia", "value": "port912"},
                                    {
                                        "label": "Canaveral Harbor - United States",
                                        "value": "port212",
                                    },
                                    {
                                        "label": "Davisville Depot - United States",
                                        "value": "port282",
                                    },
                                    {"label": "Nantes - France", "value": "port791"},
                                    {"label": "Calais - France", "value": "port206"},
                                    {
                                        "label": "Kimbe - Papua New Guinea",
                                        "value": "port569",
                                    },
                                    {
                                        "label": "Burns Harbor - United States",
                                        "value": "port195",
                                    },
                                    {
                                        "label": "Esperance - Australia",
                                        "value": "port331",
                                    },
                                    {"label": "Nukualofa - Tonga", "value": "port836"},
                                    {
                                        "label": "Providenciales - Turks and Caicos Islands",
                                        "value": "port1025",
                                    },
                                    {
                                        "label": "Cardiff - United Kingdom",
                                        "value": "port217",
                                    },
                                    {
                                        "label": "La Baie (Port Alfred) - Canada",
                                        "value": "port615",
                                    },
                                    {"label": "Mutsure - Japan", "value": "port2178"},
                                    {
                                        "label": "LNG Tangguh - Indonesia",
                                        "value": "port614",
                                    },
                                    {
                                        "label": "Frederikshavn - Denmark",
                                        "value": "port355",
                                    },
                                    {"label": "Apia - Samoa", "value": "port60"},
                                    {
                                        "label": "Saint Johns - Canada",
                                        "value": "port1220",
                                    },
                                    {
                                        "label": "Stralsund - Germany",
                                        "value": "port2068",
                                    },
                                    {
                                        "label": "Isabel - Philippines",
                                        "value": "port2207",
                                    },
                                    {"label": "Gulluk - Turkiye", "value": "port429"},
                                    {
                                        "label": "Jose Terminal - Venezuela",
                                        "value": "port524",
                                    },
                                    {
                                        "label": "Anacortes - United States",
                                        "value": "port47",
                                    },
                                    {"label": "Lakselv - Norway", "value": "port630"},
                                    {
                                        "label": "Montego Bay - Jamaica",
                                        "value": "port763",
                                    },
                                    {"label": "Gaeta - Italy", "value": "port2170"},
                                    {
                                        "label": "Shijing Longxiang - China",
                                        "value": "port1192",
                                    },
                                    {
                                        "label": "Punta Cardon - Venezuela",
                                        "value": "port1063",
                                    },
                                    {
                                        "label": "Lingkas - Indonesia",
                                        "value": "port651",
                                    },
                                    {
                                        "label": "Eskifjordhur - Iceland",
                                        "value": "port329",
                                    },
                                    {
                                        "label": "Zamboanga - Philippines",
                                        "value": "port1420",
                                    },
                                    {"label": "Noshiro - Japan", "value": "port829"},
                                    {
                                        "label": "Banjul - The Gambia",
                                        "value": "port113",
                                    },
                                    {
                                        "label": "Puerto De Hencan - Honduras",
                                        "value": "port1043",
                                    },
                                    {
                                        "label": "La Pampilla - Peru",
                                        "value": "port2203",
                                    },
                                    {
                                        "label": "Maumere - Indonesia",
                                        "value": "port722",
                                    },
                                    {"label": "Vaasa - Finland", "value": "port1346"},
                                    {"label": "Penglai - China", "value": "port897"},
                                    {
                                        "label": "Kings Lynn - United Kingdom",
                                        "value": "port571",
                                    },
                                    {
                                        "label": "Indiana Harbor - United States",
                                        "value": "port495",
                                    },
                                    {
                                        "label": "Belize City - Belize",
                                        "value": "port142",
                                    },
                                    {"label": "Ronne - Denmark", "value": "port2018"},
                                    {
                                        "label": "Santa Cruz De La Palma - Spain",
                                        "value": "port1152",
                                    },
                                    {
                                        "label": "Les Sables D Olonne - France",
                                        "value": "port642",
                                    },
                                    {
                                        "label": "Puerto Caldera - Chile",
                                        "value": "port1031",
                                    },
                                    {
                                        "label": "Porto Torres - Italy",
                                        "value": "port1011",
                                    },
                                    {"label": "Manta - Ecuador", "value": "port697"},
                                    {
                                        "label": "Bissau - Guinea-Bissau",
                                        "value": "port150",
                                    },
                                    {
                                        "label": "Merauke - Indonesia",
                                        "value": "port732",
                                    },
                                    {
                                        "label": "Lahad Datu - Malaysia",
                                        "value": "port628",
                                    },
                                    {
                                        "label": "Canakkale - Turkiye",
                                        "value": "port2233",
                                    },
                                    {"label": "Burnie - Australia", "value": "port194"},
                                    {"label": "Cairns - Australia", "value": "port204"},
                                    {
                                        "label": "Sunderland - United Kingdom",
                                        "value": "port1234",
                                    },
                                    {
                                        "label": "Portland, ME - United States",
                                        "value": "port995",
                                    },
                                    {"label": "Az Zawiyah - Libya", "value": "port85"},
                                    {"label": "Romano - Albania", "value": "port2092"},
                                    {
                                        "label": "San Ciprian - Spain",
                                        "value": "port2223",
                                    },
                                    {
                                        "label": "Great Yarmouth - United Kingdom",
                                        "value": "port417",
                                    },
                                    {
                                        "label": "Baie Comeau - Canada",
                                        "value": "port93",
                                    },
                                    {
                                        "label": "Qalhat LNG Terminal - Oman",
                                        "value": "port1068",
                                    },
                                    {"label": "Latakia - Syria", "value": "port26"},
                                    {
                                        "label": "New Haven - United States",
                                        "value": "port809",
                                    },
                                    {
                                        "label": "Porto Alegre - Brazil",
                                        "value": "port997",
                                    },
                                    {
                                        "label": "Nowshahr Port - Iran",
                                        "value": "port834",
                                    },
                                    {
                                        "label": "Tanjung Benete - Indonesia",
                                        "value": "port1267",
                                    },
                                    {
                                        "label": "Bata - Equatorial Guinea",
                                        "value": "port124",
                                    },
                                    {"label": "Rumoi - Japan", "value": "port1116"},
                                    {
                                        "label": "Steinkjer - Norway",
                                        "value": "port1226",
                                    },
                                    {
                                        "label": "Medway City - United Kingdom",
                                        "value": "port727",
                                    },
                                    {
                                        "label": "Saipan - Northern Mariana Islands",
                                        "value": "port1126",
                                    },
                                    {"label": "Ortona - Italy", "value": "port861"},
                                    {
                                        "label": "Uturoa - French Polynesia",
                                        "value": "port1344",
                                    },
                                    {
                                        "label": "Victoria - Seychelles",
                                        "value": "port1361",
                                    },
                                    {
                                        "label": "Marigot - Saint Martin",
                                        "value": "port95",
                                    },
                                    {"label": "Glomfjord - Norway", "value": "port400"},
                                    {"label": "Toronto - Canada", "value": "port1312"},
                                    {"label": "Kin - Japan", "value": "port2180"},
                                    {"label": "Kanokawa - Japan", "value": "port2176"},
                                    {"label": "Hobart - Australia", "value": "port469"},
                                    {
                                        "label": "Presque Isle - United States",
                                        "value": "port1019",
                                    },
                                    {"label": "Al Mukalla - Yemen", "value": "port27"},
                                    {
                                        "label": "Waingapu - Indonesia",
                                        "value": "port1377",
                                    },
                                    {
                                        "label": "Kota Kinabalu - Malaysia",
                                        "value": "port596",
                                    },
                                    {"label": "Bakar - Croatia", "value": "port99"},
                                    {
                                        "label": "Glasgow - United Kingdom",
                                        "value": "port399",
                                    },
                                    {
                                        "label": "Yanbu - Saudi Arabia",
                                        "value": "port1408",
                                    },
                                    {
                                        "label": "Bahia San Nicolas - Peru",
                                        "value": "port91",
                                    },
                                    {
                                        "label": "Noro - Solomon Islands",
                                        "value": "port972",
                                    },
                                    {
                                        "label": "Khorramshahr - Iran",
                                        "value": "port563",
                                    },
                                    {
                                        "label": "Bell Bay - Australia",
                                        "value": "port940",
                                    },
                                    {
                                        "label": "Puerto Bayovar - Peru",
                                        "value": "port1026",
                                    },
                                    {
                                        "label": "Chester - United States",
                                        "value": "port237",
                                    },
                                    {
                                        "label": "Suao - Taiwan Province of China",
                                        "value": "port2230",
                                    },
                                    {
                                        "label": "Ormos Aliveriou - Greece",
                                        "value": "port859",
                                    },
                                    {"label": "Chu Lai - Vietnam", "value": "port2042"},
                                    {"label": "Pisco - Peru", "value": "port2202"},
                                    {"label": "Koko - Nigeria", "value": "port587"},
                                    {
                                        "label": "Karimun - Indonesia",
                                        "value": "port2153",
                                    },
                                    {"label": "Chacabuco - Chile", "value": "port2277"},
                                    {
                                        "label": "Pulau Sambu - Indonesia",
                                        "value": "port2158",
                                    },
                                    {"label": "Oristano - Italy", "value": "port1007"},
                                    {
                                        "label": "Kuala Tanjung - Indonesia",
                                        "value": "port2159",
                                    },
                                    {
                                        "label": "Conchan Oil Terminal - Peru",
                                        "value": "port259",
                                    },
                                    {"label": "Calabar - Nigeria", "value": "port205"},
                                    {"label": "Luwuk - Indonesia", "value": "port2163"},
                                    {
                                        "label": "Milner Bay - Australia",
                                        "value": "port741",
                                    },
                                    {"label": "Husum - Germany", "value": "port485"},
                                    {
                                        "label": "Dutch Harbor - United States",
                                        "value": "port2256",
                                    },
                                    {"label": "Aiyion - Greece", "value": "port12"},
                                    {
                                        "label": "Pago Pago Harbor - American Samoa",
                                        "value": "port872",
                                    },
                                    {"label": "Namibe - Angola", "value": "port788"},
                                    {
                                        "label": "Port Blair - India",
                                        "value": "port2152",
                                    },
                                    {"label": "Braila - Romania", "value": "port2009"},
                                    {
                                        "label": "Sal Rei - Cabo Verde",
                                        "value": "port1131",
                                    },
                                    {"label": "Wallhamn - Sweden", "value": "port2070"},
                                    {
                                        "label": "Berdyansk - Ukraine",
                                        "value": "port135",
                                    },
                                    {"label": "Olbia - Italy", "value": "port848"},
                                    {"label": "Lamu - Kenya", "value": "port631"},
                                    {
                                        "label": "Point Fortin - Trinidad and Tobago",
                                        "value": "port916",
                                    },
                                    {"label": "Sapele - Nigeria", "value": "port1165"},
                                    {
                                        "label": "Port de Longoni - Mayotte",
                                        "value": "port982",
                                    },
                                    {
                                        "label": "Itacoatiara - Brazil",
                                        "value": "port2099",
                                    },
                                    {
                                        "label": "Rethymnon - Greece",
                                        "value": "port1096",
                                    },
                                    {
                                        "label": "Carboneras - Spain",
                                        "value": "port1039",
                                    },
                                    {"label": "Rosarito - Mexico", "value": "port1109"},
                                    {
                                        "label": "Gulfport - United States",
                                        "value": "port428",
                                    },
                                    {
                                        "label": "Point Tupper - Canada",
                                        "value": "port2101",
                                    },
                                    {"label": "Lavrion - Greece", "value": "port2142"},
                                    {
                                        "label": "Smalandshamnar - Sweden",
                                        "value": "port863",
                                    },
                                    {
                                        "label": "Tanjung Redeb - Indonesia",
                                        "value": "port1272",
                                    },
                                    {
                                        "label": "Peterhead - United Kingdom",
                                        "value": "port899",
                                    },
                                    {
                                        "label": "Guayanilla - Puerto Rico",
                                        "value": "port910",
                                    },
                                    {
                                        "label": "San Miguel De Cozumel - Mexico",
                                        "value": "port1144",
                                    },
                                    {"label": "Albany - Australia", "value": "port28"},
                                    {
                                        "label": "Canaport (St. John) - Canada",
                                        "value": "port211",
                                    },
                                    {
                                        "label": "Gary - United States",
                                        "value": "port377",
                                    },
                                    {"label": "Imatra - Finland", "value": "port491"},
                                    {"label": "Akureyri - Iceland", "value": "port17"},
                                    {
                                        "label": "St Nazaire - France",
                                        "value": "port1222",
                                    },
                                    {"label": "Cam Pha - Vietnam", "value": "port2051"},
                                    {
                                        "label": "Fuglafjordur - Faroe Islands",
                                        "value": "port2135",
                                    },
                                    {
                                        "label": "Barbors Point - United States",
                                        "value": "port117",
                                    },
                                    {"label": "Halden - Norway", "value": "port441"},
                                    {
                                        "label": "Leith - United Kingdom",
                                        "value": "port639",
                                    },
                                    {
                                        "label": "Cap Haitien - Haiti",
                                        "value": "port214",
                                    },
                                    {
                                        "label": "Morehead City - United States",
                                        "value": "port767",
                                    },
                                    {
                                        "label": "Longyan Port - China",
                                        "value": "port662",
                                    },
                                    {
                                        "label": "Sandnessjoen - Norway",
                                        "value": "port1148",
                                    },
                                    {"label": "Ardal - Norway", "value": "port65"},
                                    {
                                        "label": "Nasipit Port - Philippines",
                                        "value": "port797",
                                    },
                                    {"label": "Talara - Peru", "value": "port1257"},
                                    {
                                        "label": "Sydney - Australia",
                                        "value": "port1243",
                                    },
                                    {
                                        "label": "Jebel Dhanna - United Arab Emirates",
                                        "value": "port2236",
                                    },
                                    {"label": "Horta - Portugal", "value": "port478"},
                                    {
                                        "label": "Kralendijk - Bonaire,  Saint Eustatius and Saba",
                                        "value": "port598",
                                    },
                                    {
                                        "label": "Bajo Grande - Venezuela",
                                        "value": "port98",
                                    },
                                    {
                                        "label": "Nakagusuku - Japan",
                                        "value": "port2177",
                                    },
                                    {"label": "Recife - Brazil", "value": "port1094"},
                                    {
                                        "label": "Port Vila - Vanuatu",
                                        "value": "port980",
                                    },
                                    {
                                        "label": "Gisborne - New Zealand",
                                        "value": "port396",
                                    },
                                    {
                                        "label": "Kulevi Oil Terminal - Georgia",
                                        "value": "port606",
                                    },
                                    {
                                        "label": "Rodeo - United States",
                                        "value": "port2248",
                                    },
                                    {
                                        "label": "Madang - Papua New Guinea",
                                        "value": "port676",
                                    },
                                    {"label": "Zarzis - Tunisia", "value": "port1423"},
                                    {
                                        "label": "Vieux Fort - St.  Lucia",
                                        "value": "port1362",
                                    },
                                    {
                                        "label": "El Palito - Venezuela",
                                        "value": "port320",
                                    },
                                    {
                                        "label": "Brasil Port - Brazil",
                                        "value": "port166",
                                    },
                                    {
                                        "label": "Ghazaouet - Algeria",
                                        "value": "port392",
                                    },
                                    {"label": "Matanzas - Cuba", "value": "port718"},
                                    {"label": "Namsos - Norway", "value": "port789"},
                                    {
                                        "label": "Port Esquivel - Jamaica",
                                        "value": "port949",
                                    },
                                    {
                                        "label": "Zirku Island - United Arab Emirates",
                                        "value": "port2235",
                                    },
                                    {
                                        "label": "Dudinka - Russian Federation",
                                        "value": "port308",
                                    },
                                    {
                                        "label": "Puerto La Cruz - Venezuela",
                                        "value": "port1049",
                                    },
                                    {
                                        "label": "Shoaiba - Saudi Arabia",
                                        "value": "port519",
                                    },
                                    {
                                        "label": "Trincomalee - Sri Lanka",
                                        "value": "port1319",
                                    },
                                    {
                                        "label": "Punta Pereira - Uruguay",
                                        "value": "port2257",
                                    },
                                    {
                                        "label": "Saint Brieuc - France",
                                        "value": "port638",
                                    },
                                    {"label": "Ende - Indonesia", "value": "port325"},
                                    {
                                        "label": "Kirteh Oil Terminal - Malaysia",
                                        "value": "port577",
                                    },
                                    {
                                        "label": "Umm al Qaiwain - United Arab Emirates",
                                        "value": "port1340",
                                    },
                                    {
                                        "label": "Dos Bocas Terminal - Mexico",
                                        "value": "port298",
                                    },
                                    {"label": "Argentia - Canada", "value": "port66"},
                                    {"label": "Karaikal - India", "value": "port544"},
                                    {
                                        "label": "Marsa Tobruk - Libya",
                                        "value": "port734",
                                    },
                                    {"label": "Gela - Italy", "value": "port384"},
                                    {
                                        "label": "Chiriqui Grande - Panama",
                                        "value": "port240",
                                    },
                                    {"label": "Limerick - Ireland", "value": "port648"},
                                    {"label": "Buchanan - Liberia", "value": "port181"},
                                    {
                                        "label": "San Nicolas - Greece",
                                        "value": "port2147",
                                    },
                                    {
                                        "label": "Duba - Saudi Arabia",
                                        "value": "port304",
                                    },
                                    {
                                        "label": "Mina Salman - Bahrain",
                                        "value": "port2060",
                                    },
                                    {
                                        "label": "Mangalia - Romania",
                                        "value": "port2213",
                                    },
                                    {"label": "Skutskar - Sweden", "value": "port1207"},
                                    {"label": "Clarkson - Canada", "value": "port248"},
                                    {
                                        "label": "Western Port - Australia",
                                        "value": "port1391",
                                    },
                                    {"label": "Horten - Norway", "value": "port479"},
                                    {"label": "Dili - Timor-Leste", "value": "port292"},
                                    {
                                        "label": "Almirante - Panama",
                                        "value": "port2048",
                                    },
                                    {
                                        "label": "Yawatahama - Japan",
                                        "value": "port1412",
                                    },
                                    {
                                        "label": "Falmouth Harbour - United Kingdom",
                                        "value": "port337",
                                    },
                                    {
                                        "label": "Trois Rivieres - Canada",
                                        "value": "port1320",
                                    },
                                    {
                                        "label": "Chatham - United Kingdom",
                                        "value": "port234",
                                    },
                                    {
                                        "label": "Everett - United States",
                                        "value": "port333",
                                    },
                                    {
                                        "label": "Port Vale Knights - Cabo Verde",
                                        "value": "port979",
                                    },
                                    {
                                        "label": "Calumet Harbor - United States",
                                        "value": "port209",
                                    },
                                    {
                                        "label": "Majuro - Marshall Islands",
                                        "value": "port683",
                                    },
                                    {
                                        "label": "Put Put - Papua New Guinea",
                                        "value": "port1066",
                                    },
                                    {
                                        "label": "Inverness - United Kingdom",
                                        "value": "port507",
                                    },
                                    {
                                        "label": "Charlestown - St.  Kitts and Nevis",
                                        "value": "port232",
                                    },
                                    {
                                        "label": "Delaware - United States",
                                        "value": "port2247",
                                    },
                                    {
                                        "label": "Wewak Harbor - Papua New Guinea",
                                        "value": "port1392",
                                    },
                                    {"label": "Finnsnes - Norway", "value": "port347"},
                                    {
                                        "label": "Sydney - United States",
                                        "value": "port1245",
                                    },
                                    {
                                        "label": "Charco Azul - Panama",
                                        "value": "port230",
                                    },
                                    {
                                        "label": "Gustavia - Saint-Barthelemy",
                                        "value": "port430",
                                    },
                                    {"label": "Galway - Ireland", "value": "port374"},
                                    {
                                        "label": "Rosslare - Ireland",
                                        "value": "port2022",
                                    },
                                    {"label": "Zadar - Croatia", "value": "port2122"},
                                    {
                                        "label": "Trelleborg - Sweden",
                                        "value": "port1317",
                                    },
                                    {
                                        "label": "Parepare - Indonesia",
                                        "value": "port886",
                                    },
                                    {"label": "Cabedelo - Brazil", "value": "port200"},
                                    {"label": "Oostende - Belgium", "value": "port855"},
                                    {"label": "Hopa - Turkiye", "value": "port477"},
                                    {"label": "Anguilla - Anguilla", "value": "port52"},
                                    {"label": "Caen - France", "value": "port942"},
                                    {
                                        "label": "Fourchon - United States",
                                        "value": "port352",
                                    },
                                    {"label": "Tanga - Tanzania", "value": "port2231"},
                                    {"label": "Acapulco - Mexico", "value": "port7"},
                                    {"label": "Skhira - Tunisia", "value": "port1206"},
                                    {
                                        "label": "Green Bay - United States",
                                        "value": "port418",
                                    },
                                    {
                                        "label": "Orkney - United Kingdom",
                                        "value": "port2075",
                                    },
                                    {"label": "Uwajima - Japan", "value": "port1345"},
                                    {
                                        "label": "Ormoc - Philippines",
                                        "value": "port858",
                                    },
                                    {
                                        "label": "Punta Lobitos - Peru",
                                        "value": "port1064",
                                    },
                                    {
                                        "label": "Dover - United Kingdom",
                                        "value": "port301",
                                    },
                                    {"label": "Moa - Cuba", "value": "port223"},
                                    {
                                        "label": "Thevenard - Australia",
                                        "value": "port1294",
                                    },
                                    {
                                        "label": "Coles Bay Oil Terminal - Sint Maarten",
                                        "value": "port253",
                                    },
                                    {"label": "Kerch - Ukraine", "value": "port559"},
                                    {
                                        "label": "Port Sultan Qaboos - Oman",
                                        "value": "port745",
                                    },
                                    {"label": "Pachi - Greece", "value": "port2141"},
                                    {
                                        "label": "Masao - Philippines",
                                        "value": "port716",
                                    },
                                    {
                                        "label": "Milwaukee - United States",
                                        "value": "port742",
                                    },
                                    {"label": "Massawa - Eritrea", "value": "port751"},
                                    {"label": "Moroni - Comoros", "value": "port769"},
                                    {
                                        "label": "Rio Bueno - Jamaica",
                                        "value": "port1102",
                                    },
                                    {
                                        "label": "Cherbourg - France",
                                        "value": "port2086",
                                    },
                                    {
                                        "label": "Puerto Castilla - Honduras",
                                        "value": "port1033",
                                    },
                                    {"label": "Eilat - Israel", "value": "port2016"},
                                    {
                                        "label": "Kimanis - Malaysia",
                                        "value": "port2190",
                                    },
                                    {
                                        "label": "Sungai Pakning - Indonesia",
                                        "value": "port2155",
                                    },
                                    {
                                        "label": "Kavieng Harbor - Papua New Guinea",
                                        "value": "port553",
                                    },
                                    {
                                        "label": "Fairless Hills - United States",
                                        "value": "port2266",
                                    },
                                    {
                                        "label": "Portmouth - United States",
                                        "value": "port996",
                                    },
                                    {
                                        "label": "Torre Annunziata - Italy",
                                        "value": "port2171",
                                    },
                                    {"label": "Mollendo - Peru", "value": "port2205"},
                                    {
                                        "label": "Jimenez - Philippines",
                                        "value": "port520",
                                    },
                                    {
                                        "label": "Finnart Oil Terminal - United Kingdom",
                                        "value": "port346",
                                    },
                                    {"label": "Pemba - Mozambique", "value": "port896"},
                                    {
                                        "label": "Del Guazu - Argentina",
                                        "value": "port2095",
                                    },
                                    {
                                        "label": "Port of Alotau - Papua New Guinea",
                                        "value": "port37",
                                    },
                                    {
                                        "label": "Nuevitas Bay - Cuba",
                                        "value": "port835",
                                    },
                                    {"label": "Chabahar - Iran", "value": "port226"},
                                    {"label": "Linden - Guyana", "value": "port650"},
                                    {
                                        "label": "Dundee - United Kingdom",
                                        "value": "port2087",
                                    },
                                    {"label": "Bashayer - Sudan", "value": "port2225"},
                                    {
                                        "label": "Workington - United Kingdom",
                                        "value": "port1402",
                                    },
                                    {
                                        "label": "Aberdeen - United States",
                                        "value": "port2",
                                    },
                                    {
                                        "label": "Puerto De Chimbote - Peru",
                                        "value": "port1040",
                                    },
                                    {
                                        "label": "Moutsamoudu - Comoros",
                                        "value": "port773",
                                    },
                                    {
                                        "label": "Chicago - United States",
                                        "value": "port2053",
                                    },
                                    {
                                        "label": "Baie De Prony - New Caledonia",
                                        "value": "port2195",
                                    },
                                    {
                                        "label": "Majunga - Madagascar",
                                        "value": "port680",
                                    },
                                    {
                                        "label": "Bay City - United States",
                                        "value": "port130",
                                    },
                                    {
                                        "label": "Puerto Madryn - Argentina",
                                        "value": "port1050",
                                    },
                                    {
                                        "label": "Sibolga - Indonesia",
                                        "value": "port1198",
                                    },
                                    {"label": "Palua - Venezuela", "value": "port878"},
                                    {"label": "Big Creek - Belize", "value": "port148"},
                                    {"label": "Galati - Romania", "value": "port2007"},
                                    {
                                        "label": "Rosyth - United Kingdom",
                                        "value": "port2088",
                                    },
                                    {"label": "Guayacan - Chile", "value": "port2107"},
                                    {
                                        "label": "Puerto Princesa - Philippines",
                                        "value": "port1056",
                                    },
                                    {"label": "Kaukas - Finland", "value": "port551"},
                                    {
                                        "label": "Amlan - Philippines",
                                        "value": "port2208",
                                    },
                                    {
                                        "label": "Guanta - Venezuela",
                                        "value": "port2281",
                                    },
                                    {
                                        "label": "Port Lincoln - Australia",
                                        "value": "port964",
                                    },
                                    {"label": "Bosaso - Somalia", "value": "port157"},
                                    {
                                        "label": "Ashtabula - United States",
                                        "value": "port2268",
                                    },
                                    {
                                        "label": "Shala Pristan - Russian Federation",
                                        "value": "port1186",
                                    },
                                    {
                                        "label": "Wisbech - United Kingdom",
                                        "value": "port1400",
                                    },
                                    {
                                        "label": "Tanah Merah - Indonesia",
                                        "value": "port1262",
                                    },
                                    {
                                        "label": "Ras Lanuf (Al Burayqah) - Libya",
                                        "value": "port21",
                                    },
                                    {
                                        "label": "Whyalla - Australia",
                                        "value": "port1395",
                                    },
                                    {
                                        "label": "Kharg Island - Iran",
                                        "value": "port2164",
                                    },
                                    {"label": "Falconara - Italy", "value": "port2168"},
                                    {"label": "Chalkis - Greece", "value": "port2143"},
                                    {
                                        "label": "Duba Bulk Plant Tanker Terminal - Saudi Arabia",
                                        "value": "port305",
                                    },
                                    {
                                        "label": "Faradofay - Madagascar",
                                        "value": "port340",
                                    },
                                    {
                                        "label": "Puerto Chanaral - Chile",
                                        "value": "port1034",
                                    },
                                    {
                                        "label": "Port Pirie - Australia",
                                        "value": "port974",
                                    },
                                    {
                                        "label": "New Amsterdam - Guyana",
                                        "value": "port807",
                                    },
                                    {
                                        "label": "Port-La-Nouvelle - France",
                                        "value": "port991",
                                    },
                                    {"label": "Limboh - Cameroon", "value": "port2100"},
                                    {
                                        "label": "Conneaut - United States",
                                        "value": "port2265",
                                    },
                                    {"label": "Phuket - Thailand", "value": "port904"},
                                    {
                                        "label": "Luderitz Bay - Namibia",
                                        "value": "port668",
                                    },
                                    {
                                        "label": "Oro Bay - Papua New Guinea",
                                        "value": "port860",
                                    },
                                    {
                                        "label": "Kondopoga - Russian Federation",
                                        "value": "port590",
                                    },
                                    {"label": "Al Ruwais - Qatar", "value": "port1117"},
                                    {
                                        "label": "Hound Point - United Kingdom",
                                        "value": "port2238",
                                    },
                                    {
                                        "label": "Haifeng power - China",
                                        "value": "port436",
                                    },
                                    {"label": "Nice - France", "value": "port820"},
                                    {
                                        "label": "Brades - Montserrat",
                                        "value": "port164",
                                    },
                                    {"label": "Zhongshan - China", "value": "port2287"},
                                    {"label": "Omisalj - Croatia", "value": "port849"},
                                    {"label": "Mtwara - Tanzania", "value": "port2232"},
                                    {
                                        "label": "Cromarty - United Kingdom",
                                        "value": "port2241",
                                    },
                                    {
                                        "label": "Tg Mani - Malaysia",
                                        "value": "port1286",
                                    },
                                    {
                                        "label": "Monroe - United States",
                                        "value": "port2270",
                                    },
                                    {
                                        "label": "Nikiski - United States",
                                        "value": "port2251",
                                    },
                                    {
                                        "label": "Fairport - United States",
                                        "value": "port2269",
                                    },
                                    {"label": "Monopoli - Italy", "value": "port761"},
                                    {"label": "Ajaccio - France", "value": "port939"},
                                    {
                                        "label": "Luganville (Santo) - Vanuatu",
                                        "value": "port669",
                                    },
                                    {
                                        "label": "Alexandroupoli - Greece",
                                        "value": "port2078",
                                    },
                                    {"label": "Salif - Yemen", "value": "port2219"},
                                    {"label": "Navlakhi - India", "value": "port801"},
                                    {
                                        "label": "Holyhead - United Kingdom",
                                        "value": "port2014",
                                    },
                                    {
                                        "label": "Larne - United Kingdom",
                                        "value": "port2024",
                                    },
                                    {"label": "Tocopilla - Chile", "value": "port1302"},
                                    {
                                        "label": "Port Alma - Australia",
                                        "value": "port930",
                                    },
                                    {
                                        "label": "Golfito - Costa Rica",
                                        "value": "port402",
                                    },
                                    {
                                        "label": "Pohnpei - Micronesia",
                                        "value": "port927",
                                    },
                                    {"label": "Levuka - Fiji", "value": "port643"},
                                    {
                                        "label": "Searsport - United States",
                                        "value": "port1174",
                                    },
                                    {"label": "Trapani - Italy", "value": "port2015"},
                                    {"label": "Karwar - India", "value": "port2151"},
                                    {
                                        "label": "Toliara - Madagascar",
                                        "value": "port1307",
                                    },
                                    {"label": "Dhaka - Bangladesh", "value": "port289"},
                                    {
                                        "label": "Talcahuano - Chile",
                                        "value": "port2106",
                                    },
                                    {
                                        "label": "Antisranana - Madagascar",
                                        "value": "port55",
                                    },
                                    {
                                        "label": "Matthew Town - The Bahamas",
                                        "value": "port721",
                                    },
                                    {"label": "Malakal - Palau", "value": "port688"},
                                    {
                                        "label": "Esmeraldas - Ecuador",
                                        "value": "port330",
                                    },
                                    {
                                        "label": "El Guamache - Venezuela",
                                        "value": "port318",
                                    },
                                    {"label": "Vlora - Albania", "value": "port1371"},
                                    {"label": "Atapupu - Indonesia", "value": "port77"},
                                    {"label": "Ashkelon - Israel", "value": "port74"},
                                    {"label": "Kismayo - Somalia", "value": "port2073"},
                                    {
                                        "label": "Mellitah (Marsa Sabratah) - Libya",
                                        "value": "port710",
                                    },
                                    {
                                        "label": "Kasim Terminal - Indonesia",
                                        "value": "port549",
                                    },
                                    {
                                        "label": "Okaram - Turkmenistan",
                                        "value": "port847",
                                    },
                                    {
                                        "label": "Kali Limenes - Greece",
                                        "value": "port2144",
                                    },
                                    {
                                        "label": "Albany - United States",
                                        "value": "port2254",
                                    },
                                    {
                                        "label": "Pomalaa - Indonesia",
                                        "value": "port923",
                                    },
                                    {
                                        "label": "Empire - United States",
                                        "value": "port324",
                                    },
                                    {
                                        "label": "Grand Haven - United States",
                                        "value": "port412",
                                    },
                                    {
                                        "label": "Nepoui - New Caledonia",
                                        "value": "port806",
                                    },
                                    {
                                        "label": "San Francisco - United States",
                                        "value": "port1141",
                                    },
                                    {
                                        "label": "Cape Flattery - Australia",
                                        "value": "port2052",
                                    },
                                    {"label": "Vasto - Italy", "value": "port2169"},
                                    {"label": "Broome - Australia", "value": "port176"},
                                    {
                                        "label": "Picton - New Zealand",
                                        "value": "port906",
                                    },
                                    {
                                        "label": "Blanglancang - Indonesia",
                                        "value": "port152",
                                    },
                                    {
                                        "label": "Georgetown - The Bahamas",
                                        "value": "port388",
                                    },
                                    {"label": "Joutseno - Finland", "value": "port525"},
                                    {
                                        "label": "Chaguaramas - Trinidad and Tobago",
                                        "value": "port225",
                                    },
                                    {"label": "Coquimbo - Chile", "value": "port2054"},
                                    {"label": "Joensuu - Finland", "value": "port522"},
                                    {
                                        "label": "Vanimo - Papua New Guinea",
                                        "value": "port1352",
                                    },
                                    {"label": "Natal - Brazil", "value": "port799"},
                                    {
                                        "label": "Uleelheue - Indonesia",
                                        "value": "port1337",
                                    },
                                    {"label": "Payra - Bangladesh", "value": "port890"},
                                    {
                                        "label": "Campbeltown - United Kingdom",
                                        "value": "port2246",
                                    },
                                    {
                                        "label": "Brighton - Trinidad and Tobago",
                                        "value": "port172",
                                    },
                                    {
                                        "label": "Guaranao - Venezuela",
                                        "value": "port2280",
                                    },
                                    {
                                        "label": "Betio (Tarawa) - Kiribati",
                                        "value": "port1276",
                                    },
                                    {
                                        "label": "Puerto Yabucoa - Puerto Rico",
                                        "value": "port1060",
                                    },
                                    {
                                        "label": "Paagoumene - New Caledonia",
                                        "value": "port870",
                                    },
                                    {
                                        "label": "Port De Aracaju - Brazil",
                                        "value": "port941",
                                    },
                                    {
                                        "label": "Maracaibo - Venezuela",
                                        "value": "port703",
                                    },
                                    {"label": "Yap - Micronesia", "value": "port255"},
                                    {
                                        "label": "Butinge Oil Terminal - Lithuania",
                                        "value": "port197",
                                    },
                                    {"label": "Malau - Fiji", "value": "port687"},
                                    {"label": "Galle - Sri Lanka", "value": "port2224"},
                                    {"label": "Psakhna - Greece", "value": "port2146"},
                                    {
                                        "label": "Saint-Marc - Haiti",
                                        "value": "port1125",
                                    },
                                    {"label": "Lavan - Iran", "value": "port2165"},
                                    {
                                        "label": "Runavik - Faroe Islands",
                                        "value": "port2134",
                                    },
                                    {"label": "Berre - France", "value": "port2136"},
                                    {"label": "Owase - Japan", "value": "port2182"},
                                    {
                                        "label": "Luba - Equatorial Guinea",
                                        "value": "port666",
                                    },
                                    {"label": "Kunak - Malaysia", "value": "port2191"},
                                    {
                                        "label": "Hilo - United States",
                                        "value": "port464",
                                    },
                                    {"label": "Aamchit - Lebanon", "value": "port2187"},
                                    {"label": "Tartous - Syria", "value": "port2227"},
                                    {
                                        "label": "Puerto Sandino - Nicaragua",
                                        "value": "port2196",
                                    },
                                    {
                                        "label": "Bautino - Kazakhstan",
                                        "value": "port129",
                                    },
                                    {
                                        "label": "Voh - New Caledonia",
                                        "value": "port1372",
                                    },
                                    {
                                        "label": "Lumut - Brunei Darussalam",
                                        "value": "port671",
                                    },
                                    {
                                        "label": "Fray Bentos - Uruguay",
                                        "value": "port2259",
                                    },
                                    {"label": "Madero - Mexico", "value": "port2274"},
                                    {"label": "Arawak - Barbados", "value": "port63"},
                                    {
                                        "label": "Torrevieja - Spain",
                                        "value": "port1314",
                                    },
                                    {"label": "Chuuk - Micronesia", "value": "port755"},
                                    {
                                        "label": "Haugesund - Norway",
                                        "value": "port2198",
                                    },
                                    {"label": "Eten - Peru", "value": "port2204"},
                                    {
                                        "label": "Fernandina - United States",
                                        "value": "port2273",
                                    },
                                    {
                                        "label": "Buka - Papua New Guinea",
                                        "value": "port186",
                                    },
                                    {
                                        "label": "Buffington - United States",
                                        "value": "port185",
                                    },
                                    {
                                        "label": "Grand Turk - Turks and Caicos Islands",
                                        "value": "port414",
                                    },
                                    {
                                        "label": "Kosrae - Micronesia",
                                        "value": "port640",
                                    },
                                    {"label": "Jinhae - Korea", "value": "port2185"},
                                    {
                                        "label": "Barry - United Kingdom",
                                        "value": "port121",
                                    },
                                    {
                                        "label": "Port Latta - Australia",
                                        "value": "port962",
                                    },
                                    {"label": "Neiafu - Tonga", "value": "port803"},
                                    {
                                        "label": "Qianhai Bay - China",
                                        "value": "port2030",
                                    },
                                    {"label": "Hadera - Israel", "value": "port2108"},
                                    {"label": "Chekka - Lebanon", "value": "port2186"},
                                    {"label": "Bula - Indonesia", "value": "port2160"},
                                    {
                                        "label": "Puerto Limon - Costa Rica",
                                        "value": "port2013",
                                    },
                                    {
                                        "label": "Kijing - Indonesia",
                                        "value": "port2161",
                                    },
                                    {"label": "Hobro - Denmark", "value": "port470"},
                                    {
                                        "label": "Lafarge - Indonesia",
                                        "value": "port625",
                                    },
                                    {"label": "Melilla - Spain", "value": "port2059"},
                                    {
                                        "label": "Wyndham - Australia",
                                        "value": "port2096",
                                    },
                                    {
                                        "label": "Deseado - Argentina",
                                        "value": "port2275",
                                    },
                                    {"label": "Pozzuoli - Italy", "value": "port1017"},
                                    {
                                        "label": "Avatiu - Cook Islands",
                                        "value": "port81",
                                    },
                                    {
                                        "label": "Sullom Voe - United Kingdom",
                                        "value": "port2069",
                                    },
                                    {"label": "Nanaimo - Canada", "value": "port2062"},
                                    {
                                        "label": "La Salina - Venezuela",
                                        "value": "port2261",
                                    },
                                    {
                                        "label": "Ez Zueitina - Libya",
                                        "value": "port334",
                                    },
                                    {
                                        "label": "Kirkcaldy - United Kingdom",
                                        "value": "port2089",
                                    },
                                    {"label": "Pula - Croatia", "value": "port2123"},
                                    {"label": "Gaspe - Canada", "value": "port2103"},
                                    {
                                        "label": "Amurang - Indonesia",
                                        "value": "port2162",
                                    },
                                    {
                                        "label": "Daru - Papua New Guinea",
                                        "value": "port279",
                                    },
                                    {
                                        "label": "Port Bonython - Australia",
                                        "value": "port937",
                                    },
                                    {
                                        "label": "Escravos (Oil Terminal) - Nigeria",
                                        "value": "port2076",
                                    },
                                    {
                                        "label": "Ebeye - Marshall Islands",
                                        "value": "port612",
                                    },
                                    {
                                        "label": "Charlottetown - Canada",
                                        "value": "port2104",
                                    },
                                    {
                                        "label": "Banana - Democratic Republic of the Congo",
                                        "value": "port2120",
                                    },
                                    {
                                        "label": "Shuqaiq - Saudi Arabia",
                                        "value": "port2218",
                                    },
                                    {"label": "Koolan - Australia", "value": "port591"},
                                    {
                                        "label": "Helguvik - Iceland",
                                        "value": "port2149",
                                    },
                                    {
                                        "label": "Ushuaia - Argentina",
                                        "value": "port2288",
                                    },
                                    {
                                        "label": "Wallaroo - Australia",
                                        "value": "port1380",
                                    },
                                    {"label": "Tulcea - Romania", "value": "port2006"},
                                    {"label": "Antifer - France", "value": "port2137"},
                                    {
                                        "label": "Catia La Mar - Venezuela",
                                        "value": "port2260",
                                    },
                                    {
                                        "label": "Surigao City - Philippines",
                                        "value": "port1238",
                                    },
                                    {"label": "Nauru - Nauru", "value": "port800"},
                                    {"label": "Supsa - Georgia", "value": "port2139"},
                                    {"label": "Tarbert - Ireland", "value": "port2166"},
                                    {"label": "Supe - Peru", "value": "port2206"},
                                    {
                                        "label": "Kandalaksha - Russian Federation",
                                        "value": "port539",
                                    },
                                    {
                                        "label": "Channel-Port aux Basques - Canada",
                                        "value": "port935",
                                    },
                                    {
                                        "label": "Erie - United States",
                                        "value": "port2249",
                                    },
                                    {
                                        "label": "Nicholls Town - The Bahamas",
                                        "value": "port821",
                                    },
                                    {
                                        "label": "Mourilyan - Australia",
                                        "value": "port2061",
                                    },
                                    {
                                        "label": "Ponce - Puerto Rico",
                                        "value": "port2212",
                                    },
                                    {"label": "Gamba - Gabon", "value": "port2138"},
                                    {
                                        "label": "Balayan - Philippines",
                                        "value": "port2210",
                                    },
                                    {
                                        "label": "Douglas - United Kingdom",
                                        "value": "port2240",
                                    },
                                    {
                                        "label": "Butuan City - Philippines",
                                        "value": "port198",
                                    },
                                    {
                                        "label": "Puerto Miranda - Venezuela",
                                        "value": "port1051",
                                    },
                                    {
                                        "label": "Ocho Rios - Jamaica",
                                        "value": "port840",
                                    },
                                    {"label": "Funafuti - Tuvalu", "value": "port366"},
                                    {
                                        "label": "Methil - United Kingdom",
                                        "value": "port2091",
                                    },
                                    {
                                        "label": "Porto Santo - Portugal",
                                        "value": "port2211",
                                    },
                                    {"label": "Mahon - Spain", "value": "port2222"},
                                    {
                                        "label": "Kieta - Papua New Guinea",
                                        "value": "port565",
                                    },
                                    {
                                        "label": "Bayside Charlotte - Canada",
                                        "value": "port936",
                                    },
                                    {
                                        "label": "Sao Tome - Sao Tome and Principe",
                                        "value": "port1163",
                                    },
                                    {
                                        "label": "Barahona - Dominican Republic",
                                        "value": "port2127",
                                    },
                                    {"label": "Tan Tan - Morocco", "value": "port2194"},
                                    {
                                        "label": "Ras Isa Terminal - Yemen",
                                        "value": "port2245",
                                    },
                                    {
                                        "label": "Flotta - United Kingdom",
                                        "value": "port2239",
                                    },
                                    {
                                        "label": "Pepillo Salcedo (Manzanillo) - Dominican Republic",
                                        "value": "port898",
                                    },
                                    {"label": "Macae - Brazil", "value": "port673"},
                                    {
                                        "label": "Andoany - Madagascar",
                                        "value": "port50",
                                    },
                                    {
                                        "label": "Gomen - New Caledonia",
                                        "value": "port403",
                                    },
                                    {
                                        "label": "Port Giles - Australia",
                                        "value": "port953",
                                    },
                                    {
                                        "label": "La Romana - Dominican Republic",
                                        "value": "port2126",
                                    },
                                    {
                                        "label": "Ras Al Mishab - Saudi Arabia",
                                        "value": "port1088",
                                    },
                                    {"label": "Varkaus - Finland", "value": "port1354"},
                                    {"label": "Tumaco - Colombia", "value": "port2119"},
                                    {
                                        "label": "San Antonio Este - Argentina",
                                        "value": "port2276",
                                    },
                                    {"label": "Goose Bay - Canada", "value": "port405"},
                                    {
                                        "label": "Rota - Northern Mariana Islands",
                                        "value": "port1113",
                                    },
                                    {"label": "Malongo - Angola", "value": "port691"},
                                    {
                                        "label": "Bialla - Papua New Guinea",
                                        "value": "port2201",
                                    },
                                    {
                                        "label": "Lewisporte - Canada",
                                        "value": "port2102",
                                    },
                                    {"label": "Okrika - Nigeria", "value": "port2065"},
                                    {
                                        "label": "Punta Loyola - Argentina",
                                        "value": "port2094",
                                    },
                                    {
                                        "label": "Puerto Viejo - Dominican Republic",
                                        "value": "port2128",
                                    },
                                    {"label": "Chancay - Peru", "value": "port2272"},
                                    {
                                        "label": "Sint Nicolaas Baai - Aruba",
                                        "value": "port1202",
                                    },
                                    {
                                        "label": "Tinian - Northern Mariana Islands",
                                        "value": "port1300",
                                    },
                                    {
                                        "label": "Jazan - Saudi Arabia",
                                        "value": "port2074",
                                    },
                                    {
                                        "label": "Rennell Island - Solomon Islands",
                                        "value": "port2084",
                                    },
                                    {
                                        "label": "Baie De Kouaoua - New Caledonia",
                                        "value": "port94",
                                    },
                                    {"label": "Kirkenes - Norway", "value": "port2199"},
                                    {"label": "Rota - Spain", "value": "port2221"},
                                    {
                                        "label": "Ndora - Solomon Islands",
                                        "value": "port802",
                                    },
                                    {
                                        "label": "Kiritimati - Kiribati",
                                        "value": "port576",
                                    },
                                    {"label": "Seogwipo - Korea", "value": "port2285"},
                                    {
                                        "label": "Baie Ugue - New Caledonia",
                                        "value": "port97",
                                    },
                                    {
                                        "label": "De Kastri - Russian Federation",
                                        "value": "port283",
                                    },
                                    {
                                        "label": "Hera port - Timor-Leste",
                                        "value": "port461",
                                    },
                                    {
                                        "label": "Montserrat - Montserrat",
                                        "value": "port913",
                                    },
                                    {"label": "Pulandian - China", "value": "port2110"},
                                    {"label": "Vizhinjam - India", "value": "port2150"},
                                    {"label": "Kyaukpyu - Myanmar", "value": "port961"},
                                    {
                                        "label": "Punta Morales - Costa Rica",
                                        "value": "port2121",
                                    },
                                    {"label": "Gwadar - Pakistan", "value": "port431"},
                                    {
                                        "label": "Honningsvag - Norway",
                                        "value": "port2197",
                                    },
                                    {"label": "Dhekelia - Cyprus", "value": "port2124"},
                                    {
                                        "label": "Saint-Laurent-du-Maroni - French Guiana",
                                        "value": "port1123",
                                    },
                                    {
                                        "label": "New Bedford - United States",
                                        "value": "port808",
                                    },
                                    {"label": "Sekondi - Ghana", "value": "port1177"},
                                    {
                                        "label": "Bilhorod-Dnistrovskyi - Ukraine",
                                        "value": "port2077",
                                    },
                                    {
                                        "label": "Mbulo - Solomon Islands",
                                        "value": "port724",
                                    },
                                    {
                                        "label": "Bullen Baai - Curacao",
                                        "value": "port189",
                                    },
                                    {
                                        "label": "Rudum Terminal - Yemen",
                                        "value": "port2264",
                                    },
                                    {
                                        "label": "Loch Striven - United Kingdom",
                                        "value": "port2243",
                                    },
                                    {
                                        "label": "Menominee - United States",
                                        "value": "port730",
                                    },
                                    {
                                        "label": "Karumba - Australia",
                                        "value": "port2056",
                                    },
                                    {
                                        "label": "Burntisland - United Kingdom",
                                        "value": "port2090",
                                    },
                                    {"label": "Holyrood - Canada", "value": "port2105"},
                                    {
                                        "label": "Port Kaiser - Jamaica",
                                        "value": "port2172",
                                    },
                                    {"label": "Al Basrah - Iraq", "value": "port20"},
                                    {"label": "Falmouth - Jamaica", "value": "port336"},
                                    {
                                        "label": "Angra Dos Reis - Brazil",
                                        "value": "port2050",
                                    },
                                    {
                                        "label": "Ringgi - Solomon Islands",
                                        "value": "port2080",
                                    },
                                    {"label": "Nabouwalu - Fiji", "value": "port2082"},
                                    {
                                        "label": "Atherinolakos - Greece",
                                        "value": "port2145",
                                    },
                                    {"label": "Garacad - Somalia", "value": "port2271"},
                                    {
                                        "label": "Djupivogur - Iceland",
                                        "value": "port295",
                                    },
                                    {
                                        "label": "Bellingham - United States",
                                        "value": "port143",
                                    },
                                    {
                                        "label": "Bridgeport - United States",
                                        "value": "port170",
                                    },
                                    {
                                        "label": "Seghe - Solomon Islands",
                                        "value": "port1176",
                                    },
                                    {"label": "Zeit Bay - Egypt", "value": "port2131"},
                                    {
                                        "label": "Sabang - Indonesia",
                                        "value": "port2157",
                                    },
                                    {
                                        "label": "Caracas Bay - Curacao",
                                        "value": "port216",
                                    },
                                    {"label": "Savusavu - Fiji", "value": "port2081"},
                                    {"label": "Ash Shihr - Yemen", "value": "port2263"},
                                    {
                                        "label": "Manchester - United States",
                                        "value": "port2255",
                                    },
                                    {
                                        "label": "Launceston - Australia",
                                        "value": "port2058",
                                    },
                                    {
                                        "label": "Key West - United States",
                                        "value": "port2250",
                                    },
                                    {
                                        "label": "Feodosiya - Ukraine",
                                        "value": "port2234",
                                    },
                                    {"label": "Wando - Korea", "value": "port2286"},
                                    {
                                        "label": "Sundaomen Wuz - China",
                                        "value": "port1233",
                                    },
                                    {
                                        "label": "Point Murat - Australia",
                                        "value": "port918",
                                    },
                                    {
                                        "label": "Manitowoc - United States",
                                        "value": "port695",
                                    },
                                    {
                                        "label": "Puerto Cabezas - Nicaragua",
                                        "value": "port1030",
                                    },
                                    {
                                        "label": "Khalifa Bin Salman - Bahrain",
                                        "value": "port2012",
                                    },
                                    {
                                        "label": "Port of Skadovsk - Ukraine",
                                        "value": "port2072",
                                    },
                                    {
                                        "label": "Lughughi - Solomon Islands",
                                        "value": "port2083",
                                    },
                                    {
                                        "label": "Ras Al Khafji - Saudi Arabia",
                                        "value": "port2217",
                                    },
                                    {
                                        "label": "Rosales - Argentina",
                                        "value": "port2093",
                                    },
                                    {
                                        "label": "Hvalfjordur - Iceland",
                                        "value": "port2148",
                                    },
                                    {
                                        "label": "Bijela - Montenegro",
                                        "value": "port2193",
                                    },
                                    {
                                        "label": "Muntok - Indonesia",
                                        "value": "port2154",
                                    },
                                    {
                                        "label": "Dunedin - New Zealand",
                                        "value": "port865",
                                    },
                                    {
                                        "label": "Galeota Point Terminal - Trinidad and Tobago",
                                        "value": "port372",
                                    },
                                    {
                                        "label": "Bantry Bay - Ireland",
                                        "value": "port2023",
                                    },
                                    {
                                        "label": "Ust-Danube - Ukraine",
                                        "value": "port2071",
                                    },
                                    {
                                        "label": "Gizo - Solomon Islands",
                                        "value": "port2079",
                                    },
                                    {
                                        "label": "South Riding Point - The Bahamas",
                                        "value": "port2097",
                                    },
                                    {
                                        "label": "Mossel Bay - South Africa",
                                        "value": "port2220",
                                    },
                                    {"label": "Guamare - Brazil", "value": "port2098"},
                                    {
                                        "label": "Ras Gharib - Egypt",
                                        "value": "port2130",
                                    },
                                    {
                                        "label": "Ras Shukheir - Egypt",
                                        "value": "port2132",
                                    },
                                    {"label": "Derna - Libya", "value": "port2188"},
                                    {"label": "Baniyas - Syria", "value": "port2228"},
                                    {"label": "Mokha - Yemen", "value": "port2109"},
                                    {
                                        "label": "Macduff - United Kingdom",
                                        "value": "port2242",
                                    },
                                    {
                                        "label": "Faslane - United Kingdom",
                                        "value": "port2244",
                                    },
                                    {
                                        "label": "Cumarebo - Venezuela",
                                        "value": "port2279",
                                    },
                                ],
                                "style": {"popupWidth": 350},
                            },
                        }
                    },
                    "country": {
                        "imf": {
                            "x-widget_config": {
                                "options": [
                                    {"label": "Albania", "value": "ALB"},
                                    {"label": "Algeria", "value": "DZA"},
                                    {"label": "American Samoa", "value": "ASM"},
                                    {"label": "Angola", "value": "AGO"},
                                    {"label": "Anguilla", "value": "AIA"},
                                    {"label": "Antigua and Barbuda", "value": "ATG"},
                                    {"label": "Argentina", "value": "ARG"},
                                    {"label": "Aruba", "value": "ABW"},
                                    {"label": "Australia", "value": "AUS"},
                                    {"label": "Azerbaijan", "value": "AZE"},
                                    {"label": "Bahrain", "value": "BHR"},
                                    {"label": "Bangladesh", "value": "BGD"},
                                    {"label": "Barbados", "value": "BRB"},
                                    {"label": "Belgium", "value": "BEL"},
                                    {"label": "Belize", "value": "BLZ"},
                                    {"label": "Benin", "value": "BEN"},
                                    {
                                        "label": "Bonaire, Saint Eustatius and Saba",
                                        "value": "BES",
                                    },
                                    {"label": "Brazil", "value": "BRA"},
                                    {"label": "British Virgin Islands", "value": "VGB"},
                                    {"label": "Brunei Darussalam", "value": "BRN"},
                                    {"label": "Bulgaria", "value": "BGR"},
                                    {"label": "Cabo Verde", "value": "CPV"},
                                    {"label": "Cambodia", "value": "KHM"},
                                    {"label": "Cameroon", "value": "CMR"},
                                    {"label": "Canada", "value": "CAN"},
                                    {"label": "Cayman Islands", "value": "CYM"},
                                    {"label": "Chile", "value": "CHL"},
                                    {"label": "China", "value": "CHN"},
                                    {"label": "Colombia", "value": "COL"},
                                    {"label": "Comoros", "value": "COM"},
                                    {"label": "Cook Islands", "value": "COK"},
                                    {"label": "Costa Rica", "value": "CRI"},
                                    {"label": "Croatia", "value": "HRV"},
                                    {"label": "Cuba", "value": "CUB"},
                                    {"label": "Curaçao", "value": "CUW"},
                                    {"label": "Cyprus", "value": "CYP"},
                                    {"label": "Côte d'Ivoire", "value": "CIV"},
                                    {
                                        "label": "Democratic Republic of the Congo",
                                        "value": "COD",
                                    },
                                    {"label": "Denmark", "value": "DNK"},
                                    {"label": "Djibouti", "value": "DJI"},
                                    {"label": "Dominica", "value": "DMA"},
                                    {"label": "Dominican Republic", "value": "DOM"},
                                    {"label": "Ecuador", "value": "ECU"},
                                    {"label": "Egypt", "value": "EGY"},
                                    {"label": "El Salvador", "value": "SLV"},
                                    {"label": "Equatorial Guinea", "value": "GNQ"},
                                    {"label": "Eritrea", "value": "ERI"},
                                    {"label": "Estonia", "value": "EST"},
                                    {"label": "Faroe Islands", "value": "FRO"},
                                    {"label": "Fiji", "value": "FJI"},
                                    {"label": "Finland", "value": "FIN"},
                                    {"label": "France", "value": "FRA"},
                                    {"label": "French Guiana", "value": "GUF"},
                                    {"label": "French Polynesia", "value": "PYF"},
                                    {"label": "Gabon", "value": "GAB"},
                                    {"label": "Georgia", "value": "GEO"},
                                    {"label": "Germany", "value": "DEU"},
                                    {"label": "Ghana", "value": "GHA"},
                                    {"label": "Gibraltar", "value": "GIB"},
                                    {"label": "Greece", "value": "GRC"},
                                    {"label": "Grenada", "value": "GRD"},
                                    {"label": "Guadeloupe", "value": "GLP"},
                                    {"label": "Guam", "value": "GUM"},
                                    {"label": "Guatemala", "value": "GTM"},
                                    {"label": "Guinea", "value": "GIN"},
                                    {"label": "Guinea-Bissau", "value": "GNB"},
                                    {"label": "Guyana", "value": "GUY"},
                                    {"label": "Haiti", "value": "HTI"},
                                    {"label": "Honduras", "value": "HND"},
                                    {"label": "Hong Kong SAR", "value": "HKG"},
                                    {"label": "Iceland", "value": "ISL"},
                                    {"label": "India", "value": "IND"},
                                    {"label": "Indonesia", "value": "IDN"},
                                    {"label": "Iran", "value": "IRN"},
                                    {"label": "Iraq", "value": "IRQ"},
                                    {"label": "Ireland", "value": "IRL"},
                                    {"label": "Israel", "value": "ISR"},
                                    {"label": "Italy", "value": "ITA"},
                                    {"label": "Jamaica", "value": "JAM"},
                                    {"label": "Japan", "value": "JPN"},
                                    {"label": "Jordan", "value": "JOR"},
                                    {"label": "Kazakhstan", "value": "KAZ"},
                                    {"label": "Kenya", "value": "KEN"},
                                    {"label": "Kiribati", "value": "KIR"},
                                    {"label": "Korea", "value": "KOR"},
                                    {"label": "Kuwait", "value": "KWT"},
                                    {"label": "Latvia", "value": "LVA"},
                                    {"label": "Lebanon", "value": "LBN"},
                                    {"label": "Liberia", "value": "LBR"},
                                    {"label": "Libya", "value": "LBY"},
                                    {"label": "Lithuania", "value": "LTU"},
                                    {"label": "Macao SAR", "value": "MAC"},
                                    {"label": "Madagascar", "value": "MDG"},
                                    {"label": "Malaysia", "value": "MYS"},
                                    {"label": "Maldives", "value": "MDV"},
                                    {"label": "Malta", "value": "MLT"},
                                    {"label": "Marshall Islands", "value": "MHL"},
                                    {"label": "Martinique", "value": "MTQ"},
                                    {"label": "Mauritania", "value": "MRT"},
                                    {"label": "Mauritius", "value": "MUS"},
                                    {"label": "Mayotte", "value": "MYT"},
                                    {"label": "Mexico", "value": "MEX"},
                                    {"label": "Micronesia", "value": "FSM"},
                                    {"label": "Moldova", "value": "MDA"},
                                    {"label": "Montenegro", "value": "MNE"},
                                    {"label": "Montserrat", "value": "MSR"},
                                    {"label": "Morocco", "value": "MAR"},
                                    {"label": "Mozambique", "value": "MOZ"},
                                    {"label": "Myanmar", "value": "MMR"},
                                    {"label": "Namibia", "value": "NAM"},
                                    {"label": "Nauru", "value": "NRU"},
                                    {"label": "New Caledonia", "value": "NCL"},
                                    {"label": "New Zealand", "value": "NZL"},
                                    {"label": "Nicaragua", "value": "NIC"},
                                    {"label": "Nigeria", "value": "NGA"},
                                    {
                                        "label": "Northern Mariana Islands",
                                        "value": "MNP",
                                    },
                                    {"label": "Norway", "value": "NOR"},
                                    {"label": "Oman", "value": "OMN"},
                                    {"label": "Pakistan", "value": "PAK"},
                                    {"label": "Palau", "value": "PLW"},
                                    {"label": "Panama", "value": "PAN"},
                                    {"label": "Papua New Guinea", "value": "PNG"},
                                    {"label": "Peru", "value": "PER"},
                                    {"label": "Philippines", "value": "PHL"},
                                    {"label": "Poland", "value": "POL"},
                                    {"label": "Portugal", "value": "PRT"},
                                    {"label": "Puerto Rico", "value": "PRI"},
                                    {"label": "Qatar", "value": "QAT"},
                                    {"label": "Republic of Congo", "value": "COG"},
                                    {"label": "Romania", "value": "ROU"},
                                    {"label": "Russian Federation", "value": "RUS"},
                                    {"label": "Réunion", "value": "REU"},
                                    {"label": "Saint Martin", "value": "MAF"},
                                    {"label": "Saint-Barthélemy", "value": "BLM"},
                                    {"label": "Samoa", "value": "WSM"},
                                    {"label": "Saudi Arabia", "value": "SAU"},
                                    {"label": "Senegal", "value": "SEN"},
                                    {"label": "Seychelles", "value": "SYC"},
                                    {"label": "Sierra Leone", "value": "SLE"},
                                    {"label": "Singapore", "value": "SGP"},
                                    {"label": "Sint Maarten", "value": "SXM"},
                                    {"label": "Slovenia", "value": "SVN"},
                                    {"label": "Solomon Islands", "value": "SLB"},
                                    {"label": "Somalia", "value": "SOM"},
                                    {"label": "South Africa", "value": "ZAF"},
                                    {"label": "Spain", "value": "ESP"},
                                    {"label": "Sri Lanka", "value": "LKA"},
                                    {"label": "St. Kitts and Nevis", "value": "KNA"},
                                    {"label": "St. Lucia", "value": "LCA"},
                                    {
                                        "label": "St. Vincent and the Grenadines",
                                        "value": "VCT",
                                    },
                                    {"label": "Sudan", "value": "SDN"},
                                    {"label": "Suriname", "value": "SUR"},
                                    {"label": "Sweden", "value": "SWE"},
                                    {"label": "Syria", "value": "SYR"},
                                    {"label": "São Tomé and Príncipe", "value": "STP"},
                                    {
                                        "label": "Taiwan Province of China",
                                        "value": "TWN",
                                    },
                                    {"label": "Tanzania", "value": "TZA"},
                                    {"label": "Thailand", "value": "THA"},
                                    {"label": "The Bahamas", "value": "BHS"},
                                    {"label": "The Gambia", "value": "GMB"},
                                    {"label": "The Netherlands", "value": "NLD"},
                                    {"label": "Timor-Leste", "value": "TLS"},
                                    {"label": "Togo", "value": "TGO"},
                                    {"label": "Tonga", "value": "TON"},
                                    {"label": "Trinidad and Tobago", "value": "TTO"},
                                    {"label": "Tunisia", "value": "TUN"},
                                    {"label": "Turkmenistan", "value": "TKM"},
                                    {
                                        "label": "Turks and Caicos Islands",
                                        "value": "TCA",
                                    },
                                    {"label": "Tuvalu", "value": "TUV"},
                                    {"label": "Türkiye", "value": "TUR"},
                                    {"label": "Ukraine", "value": "UKR"},
                                    {"label": "United Arab Emirates", "value": "ARE"},
                                    {"label": "United Kingdom", "value": "GBR"},
                                    {"label": "United States", "value": "USA"},
                                    {
                                        "label": "United States Virgin Islands",
                                        "value": "VIR",
                                    },
                                    {"label": "Uruguay", "value": "URY"},
                                    {"label": "Vanuatu", "value": "VUT"},
                                    {"label": "Venezuela", "value": "VEN"},
                                    {"label": "Vietnam", "value": "VNM"},
                                    {"label": "World", "value": "WLD"},
                                    {"label": "Yemen", "value": "YEM"},
                                ],
                                "description": "Filter by country. This parameter supercedes `port_code` if both are provided.",
                                "style": {"popupWidth": 350},
                            }
                        }
                    },
                },
            )
        )
