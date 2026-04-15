"""CFTC Commitment of Traders Reports Model."""

# pylint: disable=unused-argument,too-many-lines

from datetime import (
    datetime,
)
from typing import Any, Literal

from openbb_cftc.utils import reports_dict
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.service.system_service import SystemService
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cot import COTData, COTQueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

api_prefix = SystemService().system_settings.api_settings.prefix


class CftcCotQueryParams(COTQueryParams):
    """CFTC Commitment of Traders Reports Query Parameters.

    Source: https://publicreporting.cftc.gov/stories/s/r4w3-av2u
    """

    __json_schema_extra__ = {
        "code": {
            "multiple_items_allowed": False,
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": f"{api_prefix}/cftc/get_cot_choices",
                "style": {"popupWidth": 650},
            },
        },
        "report_type": {
            "multiple_items_allowed": False,
            "choices": ["legacy", "disaggregated", "financial", "supplemental"],
        },
        "measure": {
            "multiple_items_allowed": False,
            "choices": [
                "all",
                "positions",
                "changes",
                "percent_of_oi",
                "traders",
                "concentration",
            ],
        },
    }

    report_type: Literal["legacy", "disaggregated", "financial", "supplemental"] = (
        Field(
            default="legacy",
            description="The type of report to retrieve.",
        )
    )
    measure: Literal[
        "all", "positions", "changes", "percent_of_oi", "traders", "concentration"
    ] = Field(
        default="all",
        description="Filter columns by measure type. Open interest is always included.",
    )
    futures_only: bool = Field(
        default=False,
        description="Returns the futures-only report. Default is False, for the combined report.",
    )
    limit: int | None = Field(
        default=None,
        description="Number of most recent reports to return. Default is all available.",
    )


class CftcCotData(COTData):
    """CFTC Commitment of Traders Reports Data.

    Fields are populated based on the report type selected. The Legacy report has
    non-commercial and commercial classifications. The Disaggregated report has
    producer/merchant, swap dealer, managed money, and other reportable classifications.
    The Financial (TFF) report has dealer, asset manager, leveraged money, and other
    reportable classifications. The Supplemental report adds commodity index trader (CIT)
    and non-CIT breakdowns. Position data is reported for all contracts, with old crop year
    and other crop year splits where applicable (Legacy and Disaggregated only).
    """

    __alias_dict__ = {
        "asset_manager_positions_long": "asset_mgr_positions_long",
        "asset_manager_positions_short": "asset_mgr_positions_short",
        "asset_manager_positions_spread": "asset_mgr_positions_spread",
        "change_commercial_long_all_non_cit": "change_comm_long_all_nocit",
        "change_commercial_short_all_non_cit": "change_comm_short_all_nocit",
        "change_in_asset_manager_long": "change_in_asset_mgr_long",
        "change_in_asset_manager_short": "change_in_asset_mgr_short",
        "change_in_asset_manager_spread": "change_in_asset_mgr_spread",
        "change_in_commercial_long_all": "change_in_comm_long_all",
        "change_in_commercial_short_all": "change_in_comm_short_all",
        "change_in_leveraged_funds_long": "change_in_lev_money_long",
        "change_in_leveraged_funds_short": "change_in_lev_money_short",
        "change_in_leveraged_funds_spread": "change_in_lev_money_spread",
        "change_in_managed_money_long_all": "change_in_m_money_long_all",
        "change_in_managed_money_short_all": "change_in_m_money_short_all",
        "change_in_managed_money_spread": "change_in_m_money_spread",
        "change_in_non_commercial_long_all": "change_in_noncomm_long_all",
        "change_in_non_commercial_short_all": "change_in_noncomm_short_all",
        "change_in_non_commercial_spread_all": "change_in_noncomm_spead_all",
        "change_in_non_reportable_long_all": "change_in_nonrept_long_all",
        "change_in_non_reportable_short_all": "change_in_nonrept_short_all",
        "change_in_other_reportable_long": "change_in_other_rept_long",
        "change_in_other_reportable_short": "change_in_other_rept_short",
        "change_in_other_reportable_spread": "change_in_other_rept_spread",
        "change_in_producer_merchant_long": "change_in_prod_merc_long",
        "change_in_producer_merchant_short": "change_in_prod_merc_short",
        "change_in_total_reportable_long_all": "change_in_tot_rept_long_all",
        "change_in_total_reportable_short": "change_in_tot_rept_short",
        "change_non_commercial_long_all_non_cit": "change_noncomm_long_all_nocit",
        "change_non_commercial_short_all_non_cit": "change_noncomm_short_all_nocit",
        "change_non_commercial_spread_all_non_cit": "change_noncomm_spead_all_nocit",
        "change_non_reportable_long_all": "change_nonrept_long_all",
        "change_non_reportable_short_all": "change_nonrept_short_all",
        "change_total_reportable_long_all": "change_tot_rept_long_all",
        "change_total_reportable_short_all": "change_tot_rept_short_all",
        "commercial_positions_long_all": "comm_positions_long_all",
        "commercial_positions_long_all_non_cit": "comm_positions_long_all_nocit",
        "commercial_positions_long_old": "comm_positions_long_old",
        "commercial_positions_long_other": "comm_positions_long_other",
        "commercial_positions_short_all": "comm_positions_short_all",
        "commercial_positions_short_all_non_cit": "comm_positions_short_all_nocit",
        "commercial_positions_short_old": "comm_positions_short_old",
        "commercial_positions_short_other": "comm_positions_short_other",
        "commodity": "commodity_name",
        "commodity_group": "commodity_group_name",
        "commodity_subgroup": "commodity_subgroup_name",
        "concentration_gross_top_4_traders_long": "conc_gross_le_4_tdr_long",
        "concentration_gross_top_4_traders_long_1": "conc_gross_le_4_tdr_long_1",
        "concentration_gross_top_4_traders_long_2": "conc_gross_le_4_tdr_long_2",
        "concentration_gross_top_4_traders_short": "conc_gross_le_4_tdr_short",
        "concentration_gross_top_4_traders_short_1": "conc_gross_le_4_tdr_short_1",
        "concentration_gross_top_4_traders_short_2": "conc_gross_le_4_tdr_short_2",
        "concentration_gross_top_8_traders_long": "conc_gross_le_8_tdr_long",
        "concentration_gross_top_8_traders_long_1": "conc_gross_le_8_tdr_long_1",
        "concentration_gross_top_8_traders_long_2": "conc_gross_le_8_tdr_long_2",
        "concentration_gross_top_8_traders_short": "conc_gross_le_8_tdr_short",
        "concentration_gross_top_8_traders_short_1": "conc_gross_le_8_tdr_short_1",
        "concentration_gross_top_8_traders_short_2": "conc_gross_le_8_tdr_short_2",
        "concentration_net_top_4_traders_long_all": "conc_net_le_4_tdr_long_all",
        "concentration_net_top_4_traders_long_old": "conc_net_le_4_tdr_long_old",
        "concentration_net_top_4_traders_long_other": "conc_net_le_4_tdr_long_other",
        "concentration_net_top_4_traders_short_all": "conc_net_le_4_tdr_short_all",
        "concentration_net_top_4_traders_short_old": "conc_net_le_4_tdr_short_old",
        "concentration_net_top_4_traders_short_other": "conc_net_le_4_tdr_short_other",
        "concentration_net_top_8_traders_long_all": "conc_net_le_8_tdr_long_all",
        "concentration_net_top_8_traders_long_old": "conc_net_le_8_tdr_long_old",
        "concentration_net_top_8_traders_long_other": "conc_net_le_8_tdr_long_other",
        "concentration_net_top_8_traders_short_all": "conc_net_le_8_tdr_short_all",
        "concentration_net_top_8_traders_short_old": "conc_net_le_8_tdr_short_old",
        "concentration_net_top_8_traders_short_other": "conc_net_le_8_tdr_short_other",
        "date": "report_date_as_yyyy_mm_dd",
        "leveraged_funds_positions_long": "lev_money_positions_long",
        "leveraged_funds_positions_short": "lev_money_positions_short",
        "leveraged_funds_positions_spread": "lev_money_positions_spread",
        "managed_money_positions_long_all": "m_money_positions_long_all",
        "managed_money_positions_long_old": "m_money_positions_long_old",
        "managed_money_positions_long_other": "m_money_positions_long_other",
        "managed_money_positions_short_all": "m_money_positions_short_all",
        "managed_money_positions_short_old": "m_money_positions_short_old",
        "managed_money_positions_short_other": "m_money_positions_short_other",
        "managed_money_positions_spread": "m_money_positions_spread",
        "managed_money_positions_spread_1": "m_money_positions_spread_1",
        "managed_money_positions_spread_2": "m_money_positions_spread_2",
        "non_commercial_positions_long_all": "noncomm_positions_long_all",
        "non_commercial_positions_long_all_non_cit": "ncomm_postions_long_all_nocit",
        "non_commercial_positions_long_old": "noncomm_positions_long_old",
        "non_commercial_positions_long_other": "noncomm_positions_long_other",
        "non_commercial_positions_short_all": "noncomm_positions_short_all",
        "non_commercial_positions_short_all_non_cit": "ncomm_postions_short_all_nocit",
        "non_commercial_positions_short_old": "noncomm_positions_short_old",
        "non_commercial_positions_short_other": "noncomm_positions_short_other",
        "non_commercial_positions_spread": "noncomm_positions_spread",
        "non_commercial_positions_spread_1": "noncomm_positions_spread_1",
        "non_commercial_positions_spread_all": "noncomm_postions_spread_all",
        "non_commercial_positions_spread_all_non_cit": "ncomm_postions_spread_all_nocit",
        "non_reportable_positions_long_all": "nonrept_positions_long_all",
        "non_reportable_positions_long_old": "nonrept_positions_long_old",
        "non_reportable_positions_long_other": "nonrept_positions_long_other",
        "non_reportable_positions_short_all": "nonrept_positions_short_all",
        "non_reportable_positions_short_old": "nonrept_positions_short_old",
        "non_reportable_positions_short_other": "nonrept_positions_short_other",
        "other_reportable_positions_long": "other_rept_positions_long",
        "other_reportable_positions_long_1": "other_rept_positions_long_1",
        "other_reportable_positions_long_2": "other_rept_positions_long_2",
        "other_reportable_positions_short": "other_rept_positions_short",
        "other_reportable_positions_short_1": "other_rept_positions_short_1",
        "other_reportable_positions_short_2": "other_rept_positions_short_2",
        "other_reportable_positions_spread": "other_rept_positions_spread",
        "other_reportable_positions_spread_1": "other_rept_positions_spread_1",
        "other_reportable_positions_spread_2": "other_rept_positions_spread_2",
        "open_interest_pct_all": "pct_of_open_interest_all",
        "open_interest_pct_asset_manager_long": "pct_of_oi_asset_mgr_long",
        "open_interest_pct_asset_manager_short": "pct_of_oi_asset_mgr_short",
        "open_interest_pct_asset_manager_spread": "pct_of_oi_asset_mgr_spread",
        "open_interest_pct_commercial_long_all": "pct_of_oi_comm_long_all",
        "open_interest_pct_commercial_long_old": "pct_of_oi_comm_long_old",
        "open_interest_pct_commercial_long_other": "pct_of_oi_comm_long_other",
        "open_interest_pct_commercial_short_all": "pct_of_oi_comm_short_all",
        "open_interest_pct_commercial_short_old": "pct_of_oi_comm_short_old",
        "open_interest_pct_commercial_short_other": "pct_of_oi_comm_short_other",
        "open_interest_pct_dealer_long_all": "pct_of_oi_dealer_long_all",
        "open_interest_pct_dealer_short_all": "pct_of_oi_dealer_short_all",
        "open_interest_pct_dealer_spread_all": "pct_of_oi_dealer_spread_all",
        "open_interest_pct_leveraged_funds_long": "pct_of_oi_lev_money_long",
        "open_interest_pct_leveraged_funds_short": "pct_of_oi_lev_money_short",
        "open_interest_pct_leveraged_funds_spread": "pct_of_oi_lev_money_spread",
        "open_interest_pct_managed_money_long_all": "pct_of_oi_m_money_long_all",
        "open_interest_pct_managed_money_long_old": "pct_of_oi_m_money_long_old",
        "open_interest_pct_managed_money_long_other": "pct_of_oi_m_money_long_other",
        "open_interest_pct_managed_money_short_all": "pct_of_oi_m_money_short_all",
        "open_interest_pct_managed_money_short_old": "pct_of_oi_m_money_short_old",
        "open_interest_pct_managed_money_short_other": "pct_of_oi_m_money_short_other",
        "open_interest_pct_managed_money_spread": "pct_of_oi_m_money_spread",
        "open_interest_pct_managed_money_spread_1": "pct_of_oi_m_money_spread_1",
        "open_interest_pct_managed_money_spread_2": "pct_of_oi_m_money_spread_2",
        "open_interest_pct_non_commercial_long_all": "pct_of_oi_noncomm_long_all",
        "open_interest_pct_non_commercial_long_old": "pct_of_oi_noncomm_long_old",
        "open_interest_pct_non_commercial_long_other": "pct_of_oi_noncomm_long_other",
        "open_interest_pct_non_commercial_short_all": "pct_of_oi_noncomm_short_all",
        "open_interest_pct_non_commercial_short_old": "pct_of_oi_noncomm_short_old",
        "open_interest_pct_non_commercial_short_other": "pct_of_oi_noncomm_short_other",
        "open_interest_pct_non_commercial_spread": "pct_of_oi_noncomm_spread",
        "open_interest_pct_non_commercial_spread_1": "pct_of_oi_noncomm_spread_1",
        "open_interest_pct_non_commercial_spread_2": "pct_of_oi_noncomm_spread_2",
        "open_interest_pct_non_reportable_long_all": "pct_of_oi_nonrept_long_all",
        "open_interest_pct_non_reportable_long_old": "pct_of_oi_nonrept_long_old",
        "open_interest_pct_non_reportable_long_other": "pct_of_oi_nonrept_long_other",
        "open_interest_pct_non_reportable_short_all": "pct_of_oi_nonrept_short_all",
        "open_interest_pct_non_reportable_short_old": "pct_of_oi_nonrept_short_old",
        "open_interest_pct_non_reportable_short_other": "pct_of_oi_nonrept_short_other",
        "open_interest_pct_other_reportable_long": "pct_of_oi_other_rept_long",
        "open_interest_pct_other_reportable_long_1": "pct_of_oi_other_rept_long_1",
        "open_interest_pct_other_reportable_long_2": "pct_of_oi_other_rept_long_2",
        "open_interest_pct_other_reportable_short": "pct_of_oi_other_rept_short",
        "open_interest_pct_other_reportable_short_1": "pct_of_oi_other_rept_short_1",
        "open_interest_pct_other_reportable_short_2": "pct_of_oi_other_rept_short_2",
        "open_interest_pct_other_reportable_spread": "pct_of_oi_other_rept_spread",
        "open_interest_pct_other_reportable_spread_1": "pct_of_oi_other_rept_spread_1",
        "open_interest_pct_other_reportable_spread_2": "pct_of_oi_other_rept_spread_2",
        "open_interest_pct_producer_merchant_long": "pct_of_oi_prod_merc_long",
        "open_interest_pct_producer_merchant_long_1": "pct_of_oi_prod_merc_long_1",
        "open_interest_pct_producer_merchant_long_2": "pct_of_oi_prod_merc_long_2",
        "open_interest_pct_producer_merchant_short": "pct_of_oi_prod_merc_short",
        "open_interest_pct_producer_merchant_short_1": "pct_of_oi_prod_merc_short_1",
        "open_interest_pct_producer_merchant_short_2": "pct_of_oi_prod_merc_short_2",
        "open_interest_pct_swap_long_all": "pct_of_oi_swap_long_all",
        "open_interest_pct_swap_long_old": "pct_of_oi_swap_long_old",
        "open_interest_pct_swap_long_other": "pct_of_oi_swap_long_other",
        "open_interest_pct_swap_short_all": "pct_of_oi_swap_short_all",
        "open_interest_pct_swap_short_old": "pct_of_oi_swap_short_old",
        "open_interest_pct_swap_short_other": "pct_of_oi_swap_short_other",
        "open_interest_pct_swap_spread_all": "pct_of_oi_swap_spread_all",
        "open_interest_pct_swap_spread_old": "pct_of_oi_swap_spread_old",
        "open_interest_pct_swap_spread_other": "pct_of_oi_swap_spread_other",
        "open_interest_pct_total_reportable_long_all": "pct_of_oi_tot_rept_long_all",
        "open_interest_pct_total_reportable_long_old": "pct_of_oi_tot_rept_long_old",
        "open_interest_pct_total_reportable_long_other": "pct_of_oi_tot_rept_long_other",
        "open_interest_pct_total_reportable_short": "pct_of_oi_tot_rept_short",
        "open_interest_pct_total_reportable_short_1": "pct_of_oi_tot_rept_short_1",
        "open_interest_pct_total_reportable_short_2": "pct_of_oi_tot_rept_short_2",
        "open_interest_pct_commercial_long_all_non_cit": "pct_oi_comm_long_all_nocit",
        "open_interest_pct_commercial_short_all_non_cit": "pct_oi_comm_short_all_nocit",
        "open_interest_pct_non_commercial_long_all_non_cit": "pct_oi_noncomm_long_all_nocit",
        "open_interest_pct_non_commercial_short_all_non_cit": "pct_oi_noncomm_short_all_nocit",
        "open_interest_pct_non_commercial_spread_all_non_cit": "pct_oi_noncomm_spread_all_nocit",
        "open_interest_pct_non_reportable_long_all_non_cit": "pct_oi_nonrept_long_all_nocit",
        "open_interest_pct_non_reportable_short_all_non_cit": "pct_oi_nonrept_short_all_nocit",
        "open_interest_pct_total_reportable_long_all_non_cit": "pct_oi_tot_rept_long_all_nocit",
        "open_interest_pct_total_reportable_short_all_non_cit": "pct_oi_tot_rept_short_all_nocit",
        "producer_merchant_positions_long": "prod_merc_positions_long",
        "producer_merchant_positions_long_1": "prod_merc_positions_long_1",
        "producer_merchant_positions_long_2": "prod_merc_positions_long_2",
        "producer_merchant_positions_short": "prod_merc_positions_short",
        "producer_merchant_positions_short_1": "prod_merc_positions_short_1",
        "producer_merchant_positions_short_2": "prod_merc_positions_short_2",
        "report_week": "yyyy_report_week_ww",
        "total_reportable_positions_long_all": "tot_rept_positions_long_all",
        "total_reportable_positions_long_old": "tot_rept_positions_long_old",
        "total_reportable_positions_long_other": "tot_rept_positions_long_other",
        "total_reportable_positions_short": "tot_rept_positions_short",
        "total_reportable_positions_short_1": "tot_rept_positions_short_1",
        "total_reportable_positions_short_2": "tot_rept_positions_short_2",
        "traders_asset_manager_long_all": "traders_asset_mgr_long_all",
        "traders_asset_manager_short_all": "traders_asset_mgr_short_all",
        "traders_asset_manager_spread": "traders_asset_mgr_spread",
        "traders_commercial_long_all": "traders_comm_long_all",
        "traders_commercial_long_all_non_cit": "traders_comm_long_all_nocit",
        "traders_commercial_long_old": "traders_comm_long_old",
        "traders_commercial_long_other": "traders_comm_long_other",
        "traders_commercial_short_all": "traders_comm_short_all",
        "traders_commercial_short_all_non_cit": "traders_comm_short_all_nocit",
        "traders_commercial_short_old": "traders_comm_short_old",
        "traders_commercial_short_other": "traders_comm_short_other",
        "traders_leveraged_funds_long_all": "traders_lev_money_long_all",
        "traders_leveraged_funds_short_all": "traders_lev_money_short_all",
        "traders_leveraged_funds_spread": "traders_lev_money_spread",
        "traders_managed_money_long_all": "traders_m_money_long_all",
        "traders_managed_money_long_old": "traders_m_money_long_old",
        "traders_managed_money_long_other": "traders_m_money_long_other",
        "traders_managed_money_short_all": "traders_m_money_short_all",
        "traders_managed_money_short_old": "traders_m_money_short_old",
        "traders_managed_money_short_other": "traders_m_money_short_other",
        "traders_managed_money_spread_all": "traders_m_money_spread_all",
        "traders_managed_money_spread_old": "traders_m_money_spread_old",
        "traders_managed_money_spread_other": "traders_m_money_spread_other",
        "traders_non_commercial_long_all": "traders_noncomm_long_all",
        "traders_non_commercial_long_all_non_cit": "traders_noncomm_long_all_nocit",
        "traders_non_commercial_long_old": "traders_noncomm_long_old",
        "traders_non_commercial_long_other": "traders_noncomm_long_other",
        "traders_non_commercial_short_all": "traders_noncomm_short_all",
        "traders_non_commercial_short_all_non_cit": "traders_noncomm_short_all_nocit",
        "traders_non_commercial_short_old": "traders_noncomm_short_old",
        "traders_non_commercial_short_other": "traders_noncomm_short_other",
        "traders_non_commercial_spread_all": "traders_noncomm_spread_all",
        "traders_non_commercial_spread_all_non_cit": "traders_noncomm_spread_all_nocit",
        "traders_non_commercial_spread_old": "traders_noncomm_spead_old",
        "traders_non_commercial_spread_other": "traders_noncomm_spread_other",
        "traders_other_reportable_long_all": "traders_other_rept_long_all",
        "traders_other_reportable_long_old": "traders_other_rept_long_old",
        "traders_other_reportable_long_other": "traders_other_rept_long_other",
        "traders_other_reportable_short": "traders_other_rept_short",
        "traders_other_reportable_short_1": "traders_other_rept_short_1",
        "traders_other_reportable_short_2": "traders_other_rept_short_2",
        "traders_other_reportable_spread": "traders_other_rept_spread",
        "traders_other_reportable_spread_1": "traders_other_rept_spread_1",
        "traders_other_reportable_spread_2": "traders_other_rept_spread_2",
        "traders_producer_merchant_long_all": "traders_prod_merc_long_all",
        "traders_producer_merchant_long_old": "traders_prod_merc_long_old",
        "traders_producer_merchant_long_other": "traders_prod_merc_long_other",
        "traders_producer_merchant_short_all": "traders_prod_merc_short_all",
        "traders_producer_merchant_short_old": "traders_prod_merc_short_old",
        "traders_producer_merchant_short_other": "traders_prod_merc_short_other",
        "traders_total_all": "traders_tot_all",
        "traders_total_old": "traders_tot_old",
        "traders_total_other": "traders_tot_other",
        "traders_total_reportable_long_all": "traders_tot_rept_long_all",
        "traders_total_reportable_long_all_non_cit": "traders_tot_rept_long_all_nocit",
        "traders_total_reportable_long_old": "traders_tot_rept_long_old",
        "traders_total_reportable_long_other": "traders_tot_rept_long_other",
        "traders_total_reportable_short_all": "traders_tot_rept_short_all",
        "traders_total_reportable_short_all_non_cit": "traders_tot_rept_short_all_nocit",
        "traders_total_reportable_short_old": "traders_tot_rept_short_old",
        "traders_total_reportable_short_other": "traders_tot_rept_short_other",
    }
    __alias_dict__.update(
        {
            "open_interest_pct_old": "pct_of_open_interest_old",
            "open_interest_pct_other": "pct_of_open_interest_other",
            "open_interest_pct_cit_long_all": "pct_oi_cit_long_all",
            "open_interest_pct_cit_short_all": "pct_oi_cit_short_all",
        }
    )

    contract_market_name: str | None = Field(
        default=None, description="Short contract market name."
    )

    # -- Open Interest --

    open_interest_all: int | None = Field(
        default=None, description="Total open interest, all contracts."
    )
    open_interest_old: int | None = Field(
        default=None,
        description="Total open interest, old crop year. Legacy/Disaggregated reports.",
    )
    open_interest_other: int | None = Field(
        default=None,
        description="Total open interest, other crop year. Legacy/Disaggregated reports.",
    )

    # -- Legacy Report: Non-Commercial Positions --

    non_commercial_positions_long_all: int | None = Field(
        default=None,
        description="Non-commercial long positions, all contracts. Legacy report.",
    )
    non_commercial_positions_short_all: int | None = Field(
        default=None,
        description="Non-commercial short positions, all contracts. Legacy report.",
    )
    non_commercial_positions_spread_all: int | None = Field(
        default=None,
        description="Non-commercial spreading positions, all contracts. Legacy report.",
    )
    non_commercial_positions_long_old: int | None = Field(
        default=None,
        description="Non-commercial long positions, old crop year. Legacy report.",
    )
    non_commercial_positions_short_old: int | None = Field(
        default=None,
        description="Non-commercial short positions, old crop year. Legacy report.",
    )
    non_commercial_positions_spread: int | None = Field(
        default=None,
        description="Non-commercial spreading positions, old crop year. Legacy report.",
    )
    non_commercial_positions_long_other: int | None = Field(
        default=None,
        description="Non-commercial long positions, other crop year. Legacy report.",
    )
    non_commercial_positions_short_other: int | None = Field(
        default=None,
        description="Non-commercial short positions, other crop year. Legacy report.",
    )
    non_commercial_positions_spread_1: int | None = Field(
        default=None,
        description="Non-commercial spreading positions, other crop year. Legacy report.",
    )

    # -- Legacy Report: Commercial Positions --

    commercial_positions_long_all: int | None = Field(
        default=None,
        description="Commercial long positions, all contracts. Legacy report.",
    )
    commercial_positions_short_all: int | None = Field(
        default=None,
        description="Commercial short positions, all contracts. Legacy report.",
    )
    commercial_positions_long_old: int | None = Field(
        default=None,
        description="Commercial long positions, old crop year. Legacy report.",
    )
    commercial_positions_short_old: int | None = Field(
        default=None,
        description="Commercial short positions, old crop year. Legacy report.",
    )
    commercial_positions_long_other: int | None = Field(
        default=None,
        description="Commercial long positions, other crop year. Legacy report.",
    )
    commercial_positions_short_other: int | None = Field(
        default=None,
        description="Commercial short positions, other crop year. Legacy report.",
    )

    # -- Disaggregated Report: Producer/Merchant/Processor/User Positions --

    producer_merchant_positions_long: int | None = Field(
        default=None,
        description="Producer/merchant long positions, all contracts. Disaggregated report.",
    )
    producer_merchant_positions_short: int | None = Field(
        default=None,
        description="Producer/merchant short positions, all contracts. Disaggregated report.",
    )
    producer_merchant_positions_long_1: int | None = Field(
        default=None,
        description="Producer/merchant long positions, old crop year. Disaggregated report.",
    )
    producer_merchant_positions_short_1: int | None = Field(
        default=None,
        description="Producer/merchant short positions, old crop year. Disaggregated report.",
    )
    producer_merchant_positions_long_2: int | None = Field(
        default=None,
        description="Producer/merchant long positions, other crop year. Disaggregated report.",
    )
    producer_merchant_positions_short_2: int | None = Field(
        default=None,
        description="Producer/merchant short positions, other crop year. Disaggregated report.",
    )

    # -- Disaggregated Report: Swap Dealer Positions --

    swap_positions_long_all: int | None = Field(
        default=None,
        description="Swap dealer long positions, all contracts. Disaggregated report.",
    )
    swap_positions_short_all: int | None = Field(
        default=None,
        description="Swap dealer short positions, all contracts. Disaggregated report.",
    )
    swap_positions_spread_all: int | None = Field(
        default=None,
        description="Swap dealer spreading positions, all contracts. Disaggregated report.",
    )
    swap_positions_long_old: int | None = Field(
        default=None,
        description="Swap dealer long positions, old crop year. Disaggregated report.",
    )
    swap_positions_short_old: int | None = Field(
        default=None,
        description="Swap dealer short positions, old crop year. Disaggregated report.",
    )
    swap_positions_spread_old: int | None = Field(
        default=None,
        description="Swap dealer spreading positions, old crop year. Disaggregated report.",
    )
    swap_positions_long_other: int | None = Field(
        default=None,
        description="Swap dealer long positions, other crop year. Disaggregated report.",
    )
    swap_positions_short_other: int | None = Field(
        default=None,
        description="Swap dealer short positions, other crop year. Disaggregated report.",
    )
    swap_positions_spread_other: int | None = Field(
        default=None,
        description="Swap dealer spreading positions, other crop year. Disaggregated report.",
    )

    # -- Disaggregated Report: Managed Money Positions --

    managed_money_positions_long_all: int | None = Field(
        default=None,
        description="Managed money long positions, all contracts. Disaggregated report.",
    )
    managed_money_positions_short_all: int | None = Field(
        default=None,
        description="Managed money short positions, all contracts. Disaggregated report.",
    )
    managed_money_positions_spread: int | None = Field(
        default=None,
        description="Managed money spreading positions, all contracts. Disaggregated report.",
    )
    managed_money_positions_long_old: int | None = Field(
        default=None,
        description="Managed money long positions, old crop year. Disaggregated report.",
    )
    managed_money_positions_short_old: int | None = Field(
        default=None,
        description="Managed money short positions, old crop year. Disaggregated report.",
    )
    managed_money_positions_spread_1: int | None = Field(
        default=None,
        description="Managed money spreading positions, old crop year. Disaggregated report.",
    )
    managed_money_positions_long_other: int | None = Field(
        default=None,
        description="Managed money long positions, other crop year. Disaggregated report.",
    )
    managed_money_positions_short_other: int | None = Field(
        default=None,
        description="Managed money short positions, other crop year. Disaggregated report.",
    )
    managed_money_positions_spread_2: int | None = Field(
        default=None,
        description="Managed money spreading positions, other crop year. Disaggregated report.",
    )

    # -- Financial (TFF) Report: Dealer/Intermediary Positions --

    dealer_positions_long_all: int | None = Field(
        default=None,
        description="Dealer/intermediary long positions, all contracts. TFF report.",
    )
    dealer_positions_short_all: int | None = Field(
        default=None,
        description="Dealer/intermediary short positions, all contracts. TFF report.",
    )
    dealer_positions_spread_all: int | None = Field(
        default=None,
        description="Dealer/intermediary spreading positions, all contracts. TFF report.",
    )

    # -- Financial (TFF) Report: Asset Manager/Institutional Positions --

    asset_manager_positions_long: int | None = Field(
        default=None,
        description="Asset manager/institutional long positions, all contracts. TFF report.",
    )
    asset_manager_positions_short: int | None = Field(
        default=None,
        description="Asset manager/institutional short positions, all contracts. TFF report.",
    )
    asset_manager_positions_spread: int | None = Field(
        default=None,
        description="Asset manager/institutional spreading positions, all contracts. TFF report.",
    )

    # -- Financial (TFF) Report: Leveraged Funds Positions --

    leveraged_funds_positions_long: int | None = Field(
        default=None,
        description="Leveraged funds long positions, all contracts. TFF report.",
    )
    leveraged_funds_positions_short: int | None = Field(
        default=None,
        description="Leveraged funds short positions, all contracts. TFF report.",
    )
    leveraged_funds_positions_spread: int | None = Field(
        default=None,
        description="Leveraged funds spreading positions, all contracts. TFF report.",
    )

    # -- Disaggregated + Financial (TFF): Other Reportable Positions --

    other_reportable_positions_long: int | None = Field(
        default=None,
        description="Other reportable long positions, all contracts. Disaggregated/TFF reports.",
    )
    other_reportable_positions_short: int | None = Field(
        default=None,
        description="Other reportable short positions, all contracts. Disaggregated/TFF reports.",
    )
    other_reportable_positions_spread: int | None = Field(
        default=None,
        description="Other reportable spreading positions, all contracts. Disaggregated/TFF reports.",
    )
    other_reportable_positions_long_1: int | None = Field(
        default=None,
        description="Other reportable long positions, old crop year. Disaggregated report.",
    )
    other_reportable_positions_short_1: int | None = Field(
        default=None,
        description="Other reportable short positions, old crop year. Disaggregated report.",
    )
    other_reportable_positions_spread_1: int | None = Field(
        default=None,
        description="Other reportable spreading positions, old crop year. Disaggregated report.",
    )
    other_reportable_positions_long_2: int | None = Field(
        default=None,
        description="Other reportable long positions, other crop year. Disaggregated report.",
    )
    other_reportable_positions_short_2: int | None = Field(
        default=None,
        description="Other reportable short positions, other crop year. Disaggregated report.",
    )
    other_reportable_positions_spread_2: int | None = Field(
        default=None,
        description="Other reportable spreading positions, other crop year. Disaggregated report.",
    )

    # -- Supplemental Report: Non-Commercial (Excluding CIT) Positions --

    non_commercial_positions_long_all_non_cit: int | None = Field(
        default=None,
        description="Non-commercial long positions excluding CIT, all contracts. Supplemental report.",
    )
    non_commercial_positions_short_all_non_cit: int | None = Field(
        default=None,
        description="Non-commercial short positions excluding CIT, all contracts. Supplemental report.",
    )
    non_commercial_positions_spread_all_non_cit: int | None = Field(
        default=None,
        description="Non-commercial spreading positions excluding CIT, all contracts. Supplemental report.",
    )

    # -- Supplemental Report: Commercial (Excluding CIT) Positions --

    commercial_positions_long_all_non_cit: int | None = Field(
        default=None,
        description="Commercial long positions excluding CIT, all contracts. Supplemental report.",
    )
    commercial_positions_short_all_non_cit: int | None = Field(
        default=None,
        description="Commercial short positions excluding CIT, all contracts. Supplemental report.",
    )

    # -- Supplemental Report: Commodity Index Trader (CIT) Positions --

    cit_positions_long_all: int | None = Field(
        default=None,
        description="Commodity index trader (CIT) long positions, all contracts. Supplemental report.",
    )
    cit_positions_short_all: int | None = Field(
        default=None,
        description="Commodity index trader (CIT) short positions, all contracts. Supplemental report.",
    )

    # -- Total Reportable Positions --

    total_reportable_positions_long_all: int | None = Field(
        default=None, description="Total reportable long positions, all contracts."
    )
    total_reportable_positions_short: int | None = Field(
        default=None, description="Total reportable short positions, all contracts."
    )
    total_reportable_positions_long_old: int | None = Field(
        default=None,
        description="Total reportable long positions, old crop year. Legacy/Disaggregated reports.",
    )
    total_reportable_positions_short_1: int | None = Field(
        default=None,
        description="Total reportable short positions, old crop year. Legacy/Disaggregated reports.",
    )
    total_reportable_positions_long_other: int | None = Field(
        default=None,
        description="Total reportable long positions, other crop year. Legacy/Disaggregated reports.",
    )
    total_reportable_positions_short_2: int | None = Field(
        default=None,
        description="Total reportable short positions, other crop year. Legacy/Disaggregated reports.",
    )

    # -- Non-Reportable Positions --

    non_reportable_positions_long_all: int | None = Field(
        default=None, description="Non-reportable long positions, all contracts."
    )
    non_reportable_positions_short_all: int | None = Field(
        default=None, description="Non-reportable short positions, all contracts."
    )
    non_reportable_positions_long_old: int | None = Field(
        default=None,
        description="Non-reportable long positions, old crop year. Legacy/Disaggregated reports.",
    )
    non_reportable_positions_short_old: int | None = Field(
        default=None,
        description="Non-reportable short positions, old crop year. Legacy/Disaggregated reports.",
    )
    non_reportable_positions_long_other: int | None = Field(
        default=None,
        description="Non-reportable long positions, other crop year. Legacy/Disaggregated reports.",
    )
    non_reportable_positions_short_other: int | None = Field(
        default=None,
        description="Non-reportable short positions, other crop year. Legacy/Disaggregated reports.",
    )

    # -- Changes: Open Interest --

    change_in_open_interest_all: int | None = Field(
        default=None, description="Weekly change in total open interest, all contracts."
    )
    change_open_interest_all: int | None = Field(
        default=None,
        description="Weekly change in total open interest, all contracts. Supplemental report.",
    )

    # -- Changes: Legacy Non-Commercial --

    change_in_non_commercial_long_all: int | None = Field(
        default=None,
        description="Weekly change in non-commercial long positions. Legacy report.",
    )
    change_in_non_commercial_short_all: int | None = Field(
        default=None,
        description="Weekly change in non-commercial short positions. Legacy report.",
    )
    change_in_non_commercial_spread_all: int | None = Field(
        default=None,
        description="Weekly change in non-commercial spreading positions. Legacy report.",
    )

    # -- Changes: Legacy Commercial --

    change_in_commercial_long_all: int | None = Field(
        default=None,
        description="Weekly change in commercial long positions. Legacy report.",
    )
    change_in_commercial_short_all: int | None = Field(
        default=None,
        description="Weekly change in commercial short positions. Legacy report.",
    )

    # -- Changes: Disaggregated Producer/Merchant --

    change_in_producer_merchant_long: int | None = Field(
        default=None,
        description="Weekly change in producer/merchant long positions. Disaggregated report.",
    )
    change_in_producer_merchant_short: int | None = Field(
        default=None,
        description="Weekly change in producer/merchant short positions. Disaggregated report.",
    )

    # -- Changes: Disaggregated Swap Dealer --

    change_in_swap_long_all: int | None = Field(
        default=None,
        description="Weekly change in swap dealer long positions. Disaggregated report.",
    )
    change_in_swap_short_all: int | None = Field(
        default=None,
        description="Weekly change in swap dealer short positions. Disaggregated report.",
    )
    change_in_swap_spread_all: int | None = Field(
        default=None,
        description="Weekly change in swap dealer spreading positions. Disaggregated report.",
    )

    # -- Changes: Disaggregated Managed Money --

    change_in_managed_money_long_all: int | None = Field(
        default=None,
        description="Weekly change in managed money long positions. Disaggregated report.",
    )
    change_in_managed_money_short_all: int | None = Field(
        default=None,
        description="Weekly change in managed money short positions. Disaggregated report.",
    )
    change_in_managed_money_spread: int | None = Field(
        default=None,
        description="Weekly change in managed money spreading positions. Disaggregated report.",
    )

    # -- Changes: Financial (TFF) Dealer --

    change_in_dealer_long_all: int | None = Field(
        default=None,
        description="Weekly change in dealer/intermediary long positions. TFF report.",
    )
    change_in_dealer_short_all: int | None = Field(
        default=None,
        description="Weekly change in dealer/intermediary short positions. TFF report.",
    )
    change_in_dealer_spread_all: int | None = Field(
        default=None,
        description="Weekly change in dealer/intermediary spreading positions. TFF report.",
    )

    # -- Changes: Financial (TFF) Asset Manager --

    change_in_asset_manager_long: int | None = Field(
        default=None,
        description="Weekly change in asset manager/institutional long positions. TFF report.",
    )
    change_in_asset_manager_short: int | None = Field(
        default=None,
        description="Weekly change in asset manager/institutional short positions. TFF report.",
    )
    change_in_asset_manager_spread: int | None = Field(
        default=None,
        description="Weekly change in asset manager/institutional spreading positions. TFF report.",
    )

    # -- Changes: Financial (TFF) Leveraged Funds --

    change_in_leveraged_funds_long: int | None = Field(
        default=None,
        description="Weekly change in leveraged funds long positions. TFF report.",
    )
    change_in_leveraged_funds_short: int | None = Field(
        default=None,
        description="Weekly change in leveraged funds short positions. TFF report.",
    )
    change_in_leveraged_funds_spread: int | None = Field(
        default=None,
        description="Weekly change in leveraged funds spreading positions. TFF report.",
    )

    # -- Changes: Other Reportable --

    change_in_other_reportable_long: int | None = Field(
        default=None,
        description="Weekly change in other reportable long positions. Disaggregated/TFF reports.",
    )
    change_in_other_reportable_short: int | None = Field(
        default=None,
        description="Weekly change in other reportable short positions. Disaggregated/TFF reports.",
    )
    change_in_other_reportable_spread: int | None = Field(
        default=None,
        description="Weekly change in other reportable spreading positions. Disaggregated/TFF reports.",
    )

    # -- Changes: Supplemental Non-Commercial NoCIT --

    change_non_commercial_long_all_non_cit: int | None = Field(
        default=None,
        description="Weekly change in non-commercial long positions excluding CIT. Supplemental report.",
    )
    change_non_commercial_short_all_non_cit: int | None = Field(
        default=None,
        description="Weekly change in non-commercial short positions excluding CIT. Supplemental report.",
    )
    change_non_commercial_spread_all_non_cit: int | None = Field(
        default=None,
        description="Weekly change in non-commercial spreading positions excluding CIT. Supplemental report.",
    )

    # -- Changes: Supplemental Commercial NoCIT --

    change_commercial_long_all_non_cit: int | None = Field(
        default=None,
        description="Weekly change in commercial long positions excluding CIT. Supplemental report.",
    )
    change_commercial_short_all_non_cit: int | None = Field(
        default=None,
        description="Weekly change in commercial short positions excluding CIT. Supplemental report.",
    )

    # -- Changes: Supplemental CIT --

    change_cit_long_all: int | None = Field(
        default=None,
        description="Weekly change in commodity index trader long positions. Supplemental report.",
    )
    change_cit_short_all: int | None = Field(
        default=None,
        description="Weekly change in commodity index trader short positions. Supplemental report.",
    )

    # -- Changes: Total Reportable --

    change_in_total_reportable_long_all: int | None = Field(
        default=None, description="Weekly change in total reportable long positions."
    )
    change_in_total_reportable_short: int | None = Field(
        default=None, description="Weekly change in total reportable short positions."
    )
    change_total_reportable_long_all: int | None = Field(
        default=None,
        description="Weekly change in total reportable long positions. Supplemental report.",
    )
    change_total_reportable_short_all: int | None = Field(
        default=None,
        description="Weekly change in total reportable short positions. Supplemental report.",
    )

    # -- Changes: Non-Reportable --

    change_in_non_reportable_long_all: int | None = Field(
        default=None, description="Weekly change in non-reportable long positions."
    )
    change_in_non_reportable_short_all: int | None = Field(
        default=None, description="Weekly change in non-reportable short positions."
    )
    change_non_reportable_long_all: int | None = Field(
        default=None,
        description="Weekly change in non-reportable long positions. Supplemental report.",
    )
    change_non_reportable_short_all: int | None = Field(
        default=None,
        description="Weekly change in non-reportable short positions. Supplemental report.",
    )

    # -- Percent of Open Interest: Totals --

    open_interest_pct_all: float | None = Field(
        default=None,
        description="Percent of total open interest, all contracts.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_old: float | None = Field(
        default=None,
        description="Percent of total open interest, old crop year. Legacy/Disaggregated reports.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_other: float | None = Field(
        default=None,
        description="Percent of total open interest, other crop year. Legacy/Disaggregated reports.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    # -- Percent of OI: Legacy Non-Commercial --

    open_interest_pct_non_commercial_long_all: float | None = Field(
        default=None,
        description="Non-commercial long as percent of open interest, all contracts. Legacy report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_non_commercial_short_all: float | None = Field(
        default=None,
        description="Non-commercial short as percent of open interest, all contracts. Legacy report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_non_commercial_spread: float | None = Field(
        default=None,
        description="Non-commercial spreading as percent of open interest, all contracts. Legacy report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_non_commercial_long_old: float | None = Field(
        default=None,
        description="Non-commercial long as percent of open interest, old crop year. Legacy report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_non_commercial_short_old: float | None = Field(
        default=None,
        description="Non-commercial short as percent of open interest, old crop year. Legacy report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_non_commercial_spread_1: float | None = Field(
        default=None,
        description="Non-commercial spreading as percent of open interest, old crop year. Legacy report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_non_commercial_long_other: float | None = Field(
        default=None,
        description="Non-commercial long as percent of open interest, other crop year. Legacy report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_non_commercial_short_other: float | None = Field(
        default=None,
        description="Non-commercial short as percent of open interest, other crop year. Legacy report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_non_commercial_spread_2: float | None = Field(
        default=None,
        description="Non-commercial spreading as percent of open interest, other crop year. Legacy report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    # -- Percent of OI: Legacy Commercial --

    open_interest_pct_commercial_long_all: float | None = Field(
        default=None,
        description="Commercial long as percent of open interest, all contracts. Legacy report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_commercial_short_all: float | None = Field(
        default=None,
        description="Commercial short as percent of open interest, all contracts. Legacy report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_commercial_long_old: float | None = Field(
        default=None,
        description="Commercial long as percent of open interest, old crop year. Legacy report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_commercial_short_old: float | None = Field(
        default=None,
        description="Commercial short as percent of open interest, old crop year. Legacy report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_commercial_long_other: float | None = Field(
        default=None,
        description="Commercial long as percent of open interest, other crop year. Legacy report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_commercial_short_other: float | None = Field(
        default=None,
        description="Commercial short as percent of open interest, other crop year. Legacy report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    # -- Percent of OI: Disaggregated Producer/Merchant --

    open_interest_pct_producer_merchant_long: float | None = Field(
        default=None,
        description="Producer/merchant long as percent of open interest, all contracts. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_producer_merchant_short: float | None = Field(
        default=None,
        description="Producer/merchant short as percent of open interest, all contracts. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_producer_merchant_long_1: float | None = Field(
        default=None,
        description="Producer/merchant long as percent of open interest, old crop year. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_producer_merchant_short_1: float | None = Field(
        default=None,
        description="Producer/merchant short as percent of open interest, old crop year. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_producer_merchant_long_2: float | None = Field(
        default=None,
        description="Producer/merchant long as percent of open interest, other crop year. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_producer_merchant_short_2: float | None = Field(
        default=None,
        description="Producer/merchant short as percent of open interest, other crop year. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    # -- Percent of OI: Disaggregated Swap Dealer --

    open_interest_pct_swap_long_all: float | None = Field(
        default=None,
        description="Swap dealer long as percent of open interest, all contracts. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_swap_short_all: float | None = Field(
        default=None,
        description="Swap dealer short as percent of open interest, all contracts. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_swap_spread_all: float | None = Field(
        default=None,
        description="Swap dealer spreading as percent of open interest, all contracts. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_swap_long_old: float | None = Field(
        default=None,
        description="Swap dealer long as percent of open interest, old crop year. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_swap_short_old: float | None = Field(
        default=None,
        description="Swap dealer short as percent of open interest, old crop year. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_swap_spread_old: float | None = Field(
        default=None,
        description="Swap dealer spreading as percent of open interest, old crop year. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_swap_long_other: float | None = Field(
        default=None,
        description="Swap dealer long as percent of open interest, other crop year. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_swap_short_other: float | None = Field(
        default=None,
        description="Swap dealer short as percent of open interest, other crop year. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_swap_spread_other: float | None = Field(
        default=None,
        description="Swap dealer spreading as percent of open interest, other crop year. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    # -- Percent of OI: Disaggregated Managed Money --

    open_interest_pct_managed_money_long_all: float | None = Field(
        default=None,
        description="Managed money long as percent of open interest, all contracts. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_managed_money_short_all: float | None = Field(
        default=None,
        description="Managed money short as percent of open interest, all contracts. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_managed_money_spread: float | None = Field(
        default=None,
        description="Managed money spreading as percent of open interest, all contracts. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_managed_money_long_old: float | None = Field(
        default=None,
        description="Managed money long as percent of open interest, old crop year. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_managed_money_short_old: float | None = Field(
        default=None,
        description="Managed money short as percent of open interest, old crop year. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_managed_money_spread_1: float | None = Field(
        default=None,
        description="Managed money spreading as percent of open interest, old crop year. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_managed_money_long_other: float | None = Field(
        default=None,
        description="Managed money long as percent of open interest, other crop year. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_managed_money_short_other: float | None = Field(
        default=None,
        description="Managed money short as percent of open interest, other crop year. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_managed_money_spread_2: float | None = Field(
        default=None,
        description="Managed money spreading as percent of open interest, other crop year. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    # -- Percent of OI: Financial (TFF) Dealer --

    open_interest_pct_dealer_long_all: float | None = Field(
        default=None,
        description="Dealer/intermediary long as percent of open interest, all contracts. TFF report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_dealer_short_all: float | None = Field(
        default=None,
        description="Dealer/intermediary short as percent of open interest, all contracts. TFF report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_dealer_spread_all: float | None = Field(
        default=None,
        description="Dealer/intermediary spreading as percent of open interest, all contracts. TFF report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    # -- Percent of OI: Financial (TFF) Asset Manager --

    open_interest_pct_asset_manager_long: float | None = Field(
        default=None,
        description="Asset manager/institutional long as percent of open interest, all contracts. TFF report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_asset_manager_short: float | None = Field(
        default=None,
        description="Asset manager/institutional short as percent of open interest, all contracts. TFF report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_asset_manager_spread: float | None = Field(
        default=None,
        description="Asset manager/institutional spreading as percent of open interest, all contracts. TFF report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    # -- Percent of OI: Financial (TFF) Leveraged Funds --

    open_interest_pct_leveraged_funds_long: float | None = Field(
        default=None,
        description="Leveraged funds long as percent of open interest, all contracts. TFF report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_leveraged_funds_short: float | None = Field(
        default=None,
        description="Leveraged funds short as percent of open interest, all contracts. TFF report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_leveraged_funds_spread: float | None = Field(
        default=None,
        description="Leveraged funds spreading as percent of open interest, all contracts. TFF report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    # -- Percent of OI: Other Reportable --

    open_interest_pct_other_reportable_long: float | None = Field(
        default=None,
        description="Other reportable long as percent of open interest, all contracts. Disaggregated/TFF reports.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_other_reportable_short: float | None = Field(
        default=None,
        description="Other reportable short as percent of open interest, all contracts. Disaggregated/TFF reports.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_other_reportable_spread: float | None = Field(
        default=None,
        description="Other reportable spreading as percent of open interest, all contracts. Disaggregated/TFF reports.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_other_reportable_long_1: float | None = Field(
        default=None,
        description="Other reportable long as percent of open interest, old crop year. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_other_reportable_short_1: float | None = Field(
        default=None,
        description="Other reportable short as percent of open interest, old crop year. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_other_reportable_spread_1: float | None = Field(
        default=None,
        description="Other reportable spreading as percent of open interest, old crop year. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_other_reportable_long_2: float | None = Field(
        default=None,
        description="Other reportable long as percent of open interest, other crop year. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_other_reportable_short_2: float | None = Field(
        default=None,
        description="Other reportable short as percent of open interest, other crop year. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_other_reportable_spread_2: float | None = Field(
        default=None,
        description="Other reportable spreading as percent of open interest, other crop year. Disaggregated report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    # -- Percent of OI: Supplemental NoCIT --

    open_interest_pct_non_commercial_long_all_non_cit: float | None = Field(
        default=None,
        description="Non-commercial long excluding CIT as percent of open interest. Supplemental report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_non_commercial_short_all_non_cit: float | None = Field(
        default=None,
        description="Non-commercial short excluding CIT as percent of open interest. Supplemental report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_non_commercial_spread_all_non_cit: float | None = Field(
        default=None,
        description="Non-commercial spreading excluding CIT as percent of open interest. Supplemental report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_commercial_long_all_non_cit: float | None = Field(
        default=None,
        description="Commercial long excluding CIT as percent of open interest. Supplemental report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_commercial_short_all_non_cit: float | None = Field(
        default=None,
        description="Commercial short excluding CIT as percent of open interest. Supplemental report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    # -- Percent of OI: Supplemental CIT --

    open_interest_pct_cit_long_all: float | None = Field(
        default=None,
        description="Commodity index trader long as percent of open interest. Supplemental report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_cit_short_all: float | None = Field(
        default=None,
        description="Commodity index trader short as percent of open interest. Supplemental report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    # -- Percent of OI: Supplemental Totals NoCIT --

    open_interest_pct_total_reportable_long_all_non_cit: float | None = Field(
        default=None,
        description="Total reportable long excluding CIT as percent of open interest. Supplemental report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_total_reportable_short_all_non_cit: float | None = Field(
        default=None,
        description="Total reportable short excluding CIT as percent of open interest. Supplemental report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_non_reportable_long_all_non_cit: float | None = Field(
        default=None,
        description="Non-reportable long excluding CIT as percent of open interest. Supplemental report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_non_reportable_short_all_non_cit: float | None = Field(
        default=None,
        description="Non-reportable short excluding CIT as percent of open interest. Supplemental report.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    # -- Percent of OI: Total Reportable --

    open_interest_pct_total_reportable_long_all: float | None = Field(
        default=None,
        description="Total reportable long as percent of open interest, all contracts.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_total_reportable_short: float | None = Field(
        default=None,
        description="Total reportable short as percent of open interest, all contracts.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_total_reportable_long_old: float | None = Field(
        default=None,
        description="Total reportable long as percent of open interest, old crop year. Legacy/Disaggregated reports.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_total_reportable_short_1: float | None = Field(
        default=None,
        description="Total reportable short as percent of open interest, old crop year. Legacy/Disaggregated reports.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_total_reportable_long_other: float | None = Field(
        default=None,
        description="Total reportable long as percent of open interest, other crop year. Legacy/Disaggregated reports.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_total_reportable_short_2: float | None = Field(
        default=None,
        description="Total reportable short as percent of open interest, other crop year. Legacy/Disaggregated reports.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    # -- Percent of OI: Non-Reportable --

    open_interest_pct_non_reportable_long_all: float | None = Field(
        default=None,
        description="Non-reportable long as percent of open interest, all contracts.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_non_reportable_short_all: float | None = Field(
        default=None,
        description="Non-reportable short as percent of open interest, all contracts.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_non_reportable_long_old: float | None = Field(
        default=None,
        description="Non-reportable long as percent of open interest, old crop year. Legacy/Disaggregated reports.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_non_reportable_short_old: float | None = Field(
        default=None,
        description="Non-reportable short as percent of open interest, old crop year. Legacy/Disaggregated reports.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_non_reportable_long_other: float | None = Field(
        default=None,
        description="Non-reportable long as percent of open interest, other crop year. Legacy/Disaggregated reports.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    open_interest_pct_non_reportable_short_other: float | None = Field(
        default=None,
        description="Non-reportable short as percent of open interest, other crop year. Legacy/Disaggregated reports.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )

    # -- Number of Traders: Totals --

    traders_total_all: int | None = Field(
        default=None, description="Total number of reportable traders, all contracts."
    )
    traders_total_old: int | None = Field(
        default=None,
        description="Total number of reportable traders, old crop year. Legacy/Disaggregated reports.",
    )
    traders_total_other: int | None = Field(
        default=None,
        description="Total number of reportable traders, other crop year. Legacy/Disaggregated reports.",
    )

    # -- Number of Traders: Legacy Non-Commercial --

    traders_non_commercial_long_all: int | None = Field(
        default=None,
        description="Number of non-commercial long traders, all contracts. Legacy report.",
    )
    traders_non_commercial_short_all: int | None = Field(
        default=None,
        description="Number of non-commercial short traders, all contracts. Legacy report.",
    )
    traders_non_commercial_spread_all: int | None = Field(
        default=None,
        description="Number of non-commercial spreading traders, all contracts. Legacy report.",
    )
    traders_non_commercial_long_old: int | None = Field(
        default=None,
        description="Number of non-commercial long traders, old crop year. Legacy report.",
    )
    traders_non_commercial_short_old: int | None = Field(
        default=None,
        description="Number of non-commercial short traders, old crop year. Legacy report.",
    )
    traders_non_commercial_spread_old: int | None = Field(
        default=None,
        description="Number of non-commercial spreading traders, old crop year. Legacy report.",
    )
    traders_non_commercial_long_other: int | None = Field(
        default=None,
        description="Number of non-commercial long traders, other crop year. Legacy report.",
    )
    traders_non_commercial_short_other: int | None = Field(
        default=None,
        description="Number of non-commercial short traders, other crop year. Legacy report.",
    )
    traders_non_commercial_spread_other: int | None = Field(
        default=None,
        description="Number of non-commercial spreading traders, other crop year. Legacy report.",
    )

    # -- Number of Traders: Legacy Commercial --

    traders_commercial_long_all: int | None = Field(
        default=None,
        description="Number of commercial long traders, all contracts. Legacy report.",
    )
    traders_commercial_short_all: int | None = Field(
        default=None,
        description="Number of commercial short traders, all contracts. Legacy report.",
    )
    traders_commercial_long_old: int | None = Field(
        default=None,
        description="Number of commercial long traders, old crop year. Legacy report.",
    )
    traders_commercial_short_old: int | None = Field(
        default=None,
        description="Number of commercial short traders, old crop year. Legacy report.",
    )
    traders_commercial_long_other: int | None = Field(
        default=None,
        description="Number of commercial long traders, other crop year. Legacy report.",
    )
    traders_commercial_short_other: int | None = Field(
        default=None,
        description="Number of commercial short traders, other crop year. Legacy report.",
    )

    # -- Number of Traders: Disaggregated Producer/Merchant --

    traders_producer_merchant_long_all: int | None = Field(
        default=None,
        description="Number of producer/merchant long traders, all contracts. Disaggregated report.",
    )
    traders_producer_merchant_short_all: int | None = Field(
        default=None,
        description="Number of producer/merchant short traders, all contracts. Disaggregated report.",
    )
    traders_producer_merchant_long_old: int | None = Field(
        default=None,
        description="Number of producer/merchant long traders, old crop year. Disaggregated report.",
    )
    traders_producer_merchant_short_old: int | None = Field(
        default=None,
        description="Number of producer/merchant short traders, old crop year. Disaggregated report.",
    )
    traders_producer_merchant_long_other: int | None = Field(
        default=None,
        description="Number of producer/merchant long traders, other crop year. Disaggregated report.",
    )
    traders_producer_merchant_short_other: int | None = Field(
        default=None,
        description="Number of producer/merchant short traders, other crop year. Disaggregated report.",
    )

    # -- Number of Traders: Disaggregated Swap Dealer --

    traders_swap_long_all: int | None = Field(
        default=None,
        description="Number of swap dealer long traders, all contracts. Disaggregated report.",
    )
    traders_swap_short_all: int | None = Field(
        default=None,
        description="Number of swap dealer short traders, all contracts. Disaggregated report.",
    )
    traders_swap_spread_all: int | None = Field(
        default=None,
        description="Number of swap dealer spreading traders, all contracts. Disaggregated report.",
    )
    traders_swap_long_old: int | None = Field(
        default=None,
        description="Number of swap dealer long traders, old crop year. Disaggregated report.",
    )
    traders_swap_short_old: int | None = Field(
        default=None,
        description="Number of swap dealer short traders, old crop year. Disaggregated report.",
    )
    traders_swap_spread_old: int | None = Field(
        default=None,
        description="Number of swap dealer spreading traders, old crop year. Disaggregated report.",
    )
    traders_swap_long_other: int | None = Field(
        default=None,
        description="Number of swap dealer long traders, other crop year. Disaggregated report.",
    )
    traders_swap_short_other: int | None = Field(
        default=None,
        description="Number of swap dealer short traders, other crop year. Disaggregated report.",
    )
    traders_swap_spread_other: int | None = Field(
        default=None,
        description="Number of swap dealer spreading traders, other crop year. Disaggregated report.",
    )

    # -- Number of Traders: Disaggregated Managed Money --

    traders_managed_money_long_all: int | None = Field(
        default=None,
        description="Number of managed money long traders, all contracts. Disaggregated report.",
    )
    traders_managed_money_short_all: int | None = Field(
        default=None,
        description="Number of managed money short traders, all contracts. Disaggregated report.",
    )
    traders_managed_money_spread_all: int | None = Field(
        default=None,
        description="Number of managed money spreading traders, all contracts. Disaggregated report.",
    )
    traders_managed_money_long_old: int | None = Field(
        default=None,
        description="Number of managed money long traders, old crop year. Disaggregated report.",
    )
    traders_managed_money_short_old: int | None = Field(
        default=None,
        description="Number of managed money short traders, old crop year. Disaggregated report.",
    )
    traders_managed_money_spread_old: int | None = Field(
        default=None,
        description="Number of managed money spreading traders, old crop year. Disaggregated report.",
    )
    traders_managed_money_long_other: int | None = Field(
        default=None,
        description="Number of managed money long traders, other crop year. Disaggregated report.",
    )
    traders_managed_money_short_other: int | None = Field(
        default=None,
        description="Number of managed money short traders, other crop year. Disaggregated report.",
    )
    traders_managed_money_spread_other: int | None = Field(
        default=None,
        description="Number of managed money spreading traders, other crop year. Disaggregated report.",
    )

    # -- Number of Traders: Financial (TFF) Dealer --

    traders_dealer_long_all: int | None = Field(
        default=None,
        description="Number of dealer/intermediary long traders, all contracts. TFF report.",
    )
    traders_dealer_short_all: int | None = Field(
        default=None,
        description="Number of dealer/intermediary short traders, all contracts. TFF report.",
    )
    traders_dealer_spread_all: int | None = Field(
        default=None,
        description="Number of dealer/intermediary spreading traders, all contracts. TFF report.",
    )

    # -- Number of Traders: Financial (TFF) Asset Manager --

    traders_asset_manager_long_all: int | None = Field(
        default=None,
        description="Number of asset manager/institutional long traders, all contracts. TFF report.",
    )
    traders_asset_manager_short_all: int | None = Field(
        default=None,
        description="Number of asset manager/institutional short traders, all contracts. TFF report.",
    )
    traders_asset_manager_spread: int | None = Field(
        default=None,
        description="Number of asset manager/institutional spreading traders, all contracts. TFF report.",
    )

    # -- Number of Traders: Financial (TFF) Leveraged Funds --

    traders_leveraged_funds_long_all: int | None = Field(
        default=None,
        description="Number of leveraged funds long traders, all contracts. TFF report.",
    )
    traders_leveraged_funds_short_all: int | None = Field(
        default=None,
        description="Number of leveraged funds short traders, all contracts. TFF report.",
    )
    traders_leveraged_funds_spread: int | None = Field(
        default=None,
        description="Number of leveraged funds spreading traders, all contracts. TFF report.",
    )

    # -- Number of Traders: Other Reportable --

    traders_other_reportable_long_all: int | None = Field(
        default=None,
        description="Number of other reportable long traders, all contracts. Disaggregated/TFF reports.",
    )
    traders_other_reportable_short: int | None = Field(
        default=None,
        description="Number of other reportable short traders, all contracts. Disaggregated/TFF reports.",
    )
    traders_other_reportable_spread: int | None = Field(
        default=None,
        description="Number of other reportable spreading traders, all contracts. Disaggregated report.",
    )
    traders_other_reportable_long_old: int | None = Field(
        default=None,
        description="Number of other reportable long traders, old crop year. Disaggregated report.",
    )
    traders_other_reportable_short_1: int | None = Field(
        default=None,
        description="Number of other reportable short traders, old crop year. Disaggregated report.",
    )
    traders_other_reportable_spread_1: int | None = Field(
        default=None,
        description="Number of other reportable spreading traders, old crop year. Disaggregated report.",
    )
    traders_other_reportable_long_other: int | None = Field(
        default=None,
        description="Number of other reportable long traders, other crop year. Disaggregated report.",
    )
    traders_other_reportable_short_2: int | None = Field(
        default=None,
        description="Number of other reportable short traders, other crop year. Disaggregated report.",
    )
    traders_other_reportable_spread_2: int | None = Field(
        default=None,
        description="Number of other reportable spreading traders, other crop year. Disaggregated report.",
    )

    # -- Number of Traders: Supplemental NoCIT --

    traders_non_commercial_long_all_non_cit: int | None = Field(
        default=None,
        description="Number of non-commercial long traders excluding CIT. Supplemental report.",
    )
    traders_non_commercial_short_all_non_cit: int | None = Field(
        default=None,
        description="Number of non-commercial short traders excluding CIT. Supplemental report.",
    )
    traders_non_commercial_spread_all_non_cit: int | None = Field(
        default=None,
        description="Number of non-commercial spreading traders excluding CIT. Supplemental report.",
    )
    traders_commercial_long_all_non_cit: int | None = Field(
        default=None,
        description="Number of commercial long traders excluding CIT. Supplemental report.",
    )
    traders_commercial_short_all_non_cit: int | None = Field(
        default=None,
        description="Number of commercial short traders excluding CIT. Supplemental report.",
    )

    # -- Number of Traders: Supplemental CIT --

    traders_cit_long_all: int | None = Field(
        default=None,
        description="Number of commodity index trader long traders. Supplemental report.",
    )
    traders_cit_short_all: int | None = Field(
        default=None,
        description="Number of commodity index trader short traders. Supplemental report.",
    )

    # -- Number of Traders: Supplemental Totals NoCIT --

    traders_total_reportable_long_all_non_cit: int | None = Field(
        default=None,
        description="Total reportable long traders excluding CIT. Supplemental report.",
    )
    traders_total_reportable_short_all_non_cit: int | None = Field(
        default=None,
        description="Total reportable short traders excluding CIT. Supplemental report.",
    )

    # -- Number of Traders: Total Reportable --

    traders_total_reportable_long_all: int | None = Field(
        default=None,
        description="Total number of reportable long traders, all contracts.",
    )
    traders_total_reportable_short_all: int | None = Field(
        default=None,
        description="Total number of reportable short traders, all contracts.",
    )
    traders_total_reportable_long_old: int | None = Field(
        default=None,
        description="Total number of reportable long traders, old crop year. Legacy/Disaggregated reports.",
    )
    traders_total_reportable_short_old: int | None = Field(
        default=None,
        description="Total number of reportable short traders, old crop year. Legacy/Disaggregated reports.",
    )
    traders_total_reportable_long_other: int | None = Field(
        default=None,
        description="Total number of reportable long traders, other crop year. Legacy/Disaggregated reports.",
    )
    traders_total_reportable_short_other: int | None = Field(
        default=None,
        description="Total number of reportable short traders, other crop year. Legacy/Disaggregated reports.",
    )

    # -- Concentration Ratios: All Contracts --

    concentration_gross_top_4_traders_long: float | None = Field(
        default=None,
        description="Gross long position concentration of top 4 traders, all contracts.",
    )
    concentration_gross_top_4_traders_short: float | None = Field(
        default=None,
        description="Gross short position concentration of top 4 traders, all contracts.",
    )
    concentration_gross_top_8_traders_long: float | None = Field(
        default=None,
        description="Gross long position concentration of top 8 traders, all contracts.",
    )
    concentration_gross_top_8_traders_short: float | None = Field(
        default=None,
        description="Gross short position concentration of top 8 traders, all contracts.",
    )
    concentration_net_top_4_traders_long_all: float | None = Field(
        default=None,
        description="Net long position concentration of top 4 traders, all contracts.",
    )
    concentration_net_top_4_traders_short_all: float | None = Field(
        default=None,
        description="Net short position concentration of top 4 traders, all contracts.",
    )
    concentration_net_top_8_traders_long_all: float | None = Field(
        default=None,
        description="Net long position concentration of top 8 traders, all contracts.",
    )
    concentration_net_top_8_traders_short_all: float | None = Field(
        default=None,
        description="Net short position concentration of top 8 traders, all contracts.",
    )

    # -- Concentration Ratios: Old Crop Year --

    concentration_gross_top_4_traders_long_1: float | None = Field(
        default=None,
        description="Gross long position concentration of top 4 traders, old crop year. Legacy/Disaggregated reports.",
    )
    concentration_gross_top_4_traders_short_1: float | None = Field(
        default=None,
        description="Gross short position concentration of top 4 traders, old crop year. Legacy/Disaggregated reports.",
    )
    concentration_gross_top_8_traders_long_1: float | None = Field(
        default=None,
        description="Gross long position concentration of top 8 traders, old crop year. Legacy/Disaggregated reports.",
    )
    concentration_gross_top_8_traders_short_1: float | None = Field(
        default=None,
        description="Gross short position concentration of top 8 traders, old crop year. Legacy/Disaggregated reports.",
    )
    concentration_net_top_4_traders_long_old: float | None = Field(
        default=None,
        description="Net long position concentration of top 4 traders, old crop year. Legacy/Disaggregated reports.",
    )
    concentration_net_top_4_traders_short_old: float | None = Field(
        default=None,
        description="Net short position concentration of top 4 traders, old crop year. Legacy/Disaggregated reports.",
    )
    concentration_net_top_8_traders_long_old: float | None = Field(
        default=None,
        description="Net long position concentration of top 8 traders, old crop year. Legacy/Disaggregated reports.",
    )
    concentration_net_top_8_traders_short_old: float | None = Field(
        default=None,
        description="Net short position concentration of top 8 traders, old crop year. Legacy/Disaggregated reports.",
    )

    # -- Concentration Ratios: Other Crop Year --

    concentration_gross_top_4_traders_long_2: float | None = Field(
        default=None,
        description="Gross long position concentration of top 4 traders, other crop year. Legacy/Disaggregated reports.",
    )
    concentration_gross_top_4_traders_short_2: float | None = Field(
        default=None,
        description="Gross short position concentration of top 4 traders, other crop year. Legacy/Disaggregated reports.",
    )
    concentration_gross_top_8_traders_long_2: float | None = Field(
        default=None,
        description="Gross long position concentration of top 8 traders, other crop year. Legacy/Disaggregated reports.",
    )
    concentration_gross_top_8_traders_short_2: float | None = Field(
        default=None,
        description="Gross short position concentration of top 8 traders, other crop year. Legacy/Disaggregated reports.",
    )
    concentration_net_top_4_traders_long_other: float | None = Field(
        default=None,
        description="Net long position concentration of top 4 traders, other crop year. Legacy/Disaggregated reports.",
    )
    concentration_net_top_4_traders_short_other: float | None = Field(
        default=None,
        description="Net short position concentration of top 4 traders, other crop year. Legacy/Disaggregated reports.",
    )
    concentration_net_top_8_traders_long_other: float | None = Field(
        default=None,
        description="Net long position concentration of top 8 traders, other crop year. Legacy/Disaggregated reports.",
    )
    concentration_net_top_8_traders_short_other: float | None = Field(
        default=None,
        description="Net short position concentration of top 8 traders, other crop year. Legacy/Disaggregated reports.",
    )


class CftcCotFetcher(Fetcher[CftcCotQueryParams, list[CftcCotData]]):
    """CFTC Commitment of Traders Reports Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CftcCotQueryParams:
        """Transform query parameters."""
        return CftcCotQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CftcCotQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the CFTC API."""
        # pylint: disable=import-outside-toplevel
        import os  # noqa
        from datetime import timedelta
        from openbb_core.provider.utils.helpers import amake_request

        app_token = (
            credentials.get("cftc_app_token")
            if credentials
            else os.getenv("CFTC_APP_TOKEN") or ""
        )

        today = datetime.now()

        _id = "" if query.code == "all" else query.code  # type: ignore
        if _id.startswith("CFTC_"):
            _id = _id[5:]

        is_code = _id and _id[:3].isdigit()
        _start = (
            "1995-01-01"
            if is_code
            else (
                (today - timedelta(days=(today.weekday() - 1) % 7)).strftime("%Y-%m-%d")
            )
        )
        start_date = (
            query.start_date.strftime("%Y-%m-%d") if query.start_date else _start
        )
        end_date = (
            query.end_date.strftime("%Y-%m-%d")
            if query.end_date
            else f"{today.year}-12-31"
        )
        date_range = (
            "$where=Report_Date_as_YYYY_MM_DD"
            f" between '{start_date}' AND '{end_date}'"
        )
        report_type = query.report_type.replace("financial", "tff")

        if query.futures_only is True and report_type != "supplemental":
            report_type += "_futures_only"
        elif query.futures_only is False and report_type != "supplemental":
            report_type += "_combined"

        if not is_code and _id:
            _id = f"%{_id}%"

        _id = _id.replace("+", "%2B").replace("&", "%26")
        base_url = f"https://publicreporting.cftc.gov/resource/{reports_dict[report_type]}.json?$limit=1000000&{date_range}"
        order = "&$order=Report_Date_as_YYYY_MM_DD ASC"
        url = (
            (
                f"{base_url}"
                f" AND (UPPER(contract_market_name) like UPPER('{_id}') "
                f"OR UPPER(commodity) like UPPER('{_id}') "
                f"OR UPPER(cftc_contract_market_code) like UPPER('{_id}') "
                f"OR UPPER(commodity_group_name) like UPPER('{_id}') "
                f"OR UPPER(commodity_subgroup_name) like UPPER('{_id}'))"
            )
            if _id
            else base_url
        )
        url = f"{url}{order}"

        if app_token:
            url += f"&$$app_token={app_token}"

        try:
            response = await amake_request(url, **kwargs)
        except OpenBBError as error:
            raise error from error

        if not response:
            raise EmptyDataError(f"No data found for {_id.replace('%', '')}.")

        return response  # type: ignore

    @staticmethod
    def transform_data(
        query: CftcCotQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[CftcCotData]:
        """Transform and validate the data."""
        response = data.copy()
        string_cols = [
            "market_and_exchange_names",
            "cftc_contract_market_code",
            "cftc_market_code",
            "cftc_region_code",
            "cftc_commodity_code",
            "cftc_contract_market_code_quotes",
            "cftc_market_code_quotes",
            "cftc_commodity_code_quotes",
            "cftc_subgroup_code",
            "commodity_group_name",
            "commodity",
            "commodity_name",
            "commodity_subgroup_name",
            "contract_units",
            "yyyy_report_week_ww",
            "id",
            "futonly_or_combined",
        ]
        results: list[CftcCotData] = []
        for values in response:
            new_values: dict = {}
            for key, value in values.items():
                if key == "report_date_as_yyyy_mm_dd" and value:
                    new_values["report_date_as_yyyy_mm_dd"] = value.split("T")[0]
                elif key in string_cols and value:
                    v = str(value)
                    if key == "contract_units":
                        v = v.strip("()")
                    new_values[key.lower()] = v
                elif key.lower().startswith("pct_") and value:
                    new_values[key.lower().replace("__", "_")] = float(value) / 100
                elif key.lower().startswith("conc_") and value:
                    new_values[key.lower().replace("__", "_")] = float(value)
                elif value:
                    try:
                        new_values[key.lower().replace("__", "_")] = int(value)
                    except ValueError:
                        new_values[key.lower().replace("__", "_")] = value

            if new_values:
                results.append(CftcCotData.model_validate(new_values))

        if results:
            dup_fields: set[str] = set()
            sample = results[0].model_dump()
            for fname in list(sample):
                base: str | None = None
                if fname.endswith("_old") or fname.endswith("_other"):
                    base = fname.rsplit("_", 1)[0] + "_all"
                elif fname.endswith("_1") or fname.endswith("_2"):
                    base = fname[:-2]
                if base is None or base not in sample:
                    continue
                pairs = [
                    (getattr(r, base, None), getattr(r, fname, None)) for r in results
                ]
                paired = [(a, b) for a, b in pairs if a is not None and b is not None]
                if paired and all(a == b for a, b in paired):
                    dup_fields.add(fname)
            if dup_fields:
                for r in results:
                    for col in dup_fields:
                        object.__setattr__(r, col, None)

        measure = query.measure
        if measure != "all" and results:
            _metadata = {
                "market_and_exchange_names",
                "cftc_contract_market_code",
                "cftc_market_code",
                "cftc_region_code",
                "cftc_commodity_code",
                "cftc_contract_market_code_quotes",
                "cftc_market_code_quotes",
                "cftc_commodity_code_quotes",
                "cftc_subgroup_code",
                "commodity",
                "commodity_group",
                "commodity_subgroup",
                "futonly_or_combined",
                "contract_units",
                "contract_market_name",
                "report_week",
                "id",
            }
            measure_prefixes = {
                "changes": "change_",
                "percent_of_oi": "open_interest_pct_",
                "traders": "traders_",
                "concentration": "concentration_",
            }

            def _keep(field_name: str) -> bool:
                if field_name in ("date", "open_interest_all"):
                    return True
                if field_name in _metadata:
                    return False
                if measure == "positions":
                    return not any(
                        field_name.startswith(p) for p in measure_prefixes.values()
                    )
                return field_name.startswith(measure_prefixes[measure])

            keep_fields = {
                f
                for r in results
                for f, v in r.model_dump().items()
                if _keep(f) and v is not None and v != 0
            }
            keep_fields.add("date")
            keep_fields.add("open_interest_all")

            filtered: list[CftcCotData] = []
            for r in results:
                d = {k: v for k, v in r.model_dump().items() if k in keep_fields}
                filtered.append(CftcCotData.model_validate(d))
            results = filtered

        results.sort(key=lambda r: r.date)
        if query.limit is not None and query.limit > 0:
            results = results[-query.limit :]

        return results
