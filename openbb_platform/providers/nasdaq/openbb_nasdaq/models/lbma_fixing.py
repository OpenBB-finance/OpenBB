"""Nasdaq LBMA Fixing Model."""

# pylint: disable=unused-argument
from typing import Any, Dict, List, Optional

import nasdaqdatalink
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.lbma_fixing import (
    LbmaFixingData,
    LbmaFixingQueryParams,
)
from openbb_nasdaq.utils.query_params import DataLinkQueryParams


class NasdaqLbmaFixingQueryParams(LbmaFixingQueryParams, DataLinkQueryParams):
    """Nasdaq Data Link LBMA Fixing Query.

    Source: https://data.nasdaq.com/data/LBMA-london-bullion-market-association/documentation
    """


class NasdaqLbmaFixingData(LbmaFixingData):
    """Nasdaq Data Link LBMA Fixing Data."""

    __alias_dict__ = {
        "date": "Date",
        "usd_am": "USD (AM)",
        "usd_pm": "USD (PM)",
        "gbp_am": "GBP (AM)",
        "gbp_pm": "GBP (PM)",
        "eur_am": "EURO (AM)",
        "eur_pm": "EURO (PM)",
        "usd": "USD",
        "gbp": "GBP",
        "eur": "EURO",
    }


class NasdaqLbmaFixingFetcher(
    Fetcher[NasdaqLbmaFixingQueryParams, List[NasdaqLbmaFixingData]]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> NasdaqLbmaFixingQueryParams:
        """Transform the query params."""
        return NasdaqLbmaFixingQueryParams(**params)

    @staticmethod
    def extract_data(
        query: NasdaqLbmaFixingQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data from Nasdaq Data Link."""
        api_key = credentials.get("nasdaq_api_key") if credentials else ""

        dataset_dict = {
            "gold": "LBMA/GOLD",
            "silver": "LBMA/SILVER",
        }
        results = nasdaqdatalink.get(
            dataset_dict[query.asset],  # type: ignore
            start_date=query.start_date,
            end_date=query.end_date,
            collapse=query.collapse,
            transform=query.transform,
            api_key=api_key,
        )

        return results.fillna(0).replace(0, None).reset_index().to_dict("records")

    @staticmethod
    def transform_data(
        query: NasdaqLbmaFixingQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[NasdaqLbmaFixingData]:
        """Transform the data."""
        return [NasdaqLbmaFixingData.model_validate(d) for d in data]
