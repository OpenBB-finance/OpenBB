
from openbb_government_us.models.senate_disclosures import (
    USSenateDisclosuresFetcher,
    USSenateDisclosuresQueryParams
)
import asyncio


async def fetch_data():
    params = USSenateDisclosuresQueryParams()
    params.num_reports = 5
    data = await USSenateDisclosuresFetcher.extract_data(params, {})

    return [d for d in data]


def run_fetcher():
    with asyncio.Runner() as runner:
        data = runner.run(fetch_data())
        print(f'senate data is:{data}')
