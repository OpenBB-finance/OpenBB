
from openbb_government_us.models.senate_disclosures import USSenateDisclosuresFetcher, USSenateDisclosuresQueryParams
import asyncio


def run_fetcher():
    params = USSenateDisclosuresQueryParams()
    params.num_reports = 5
    return USSenateDisclosuresFetcher.extract_data(params, {})

