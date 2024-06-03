"""Pyth2 Provider Helpers"""


from openbb_providers.models.cftc import CommitmentOfTradersAnalysisFetcher
from openbb_providers.models.cftc_contracts import CommitmentOfTradersReportFetcher
from openbb_providers.models.cramer import CramerFetcher
import random
import logging
import asyncio
from openbb_core.app.service.user_service import UserService

def get_cramer():
    credentials = UserService().default_user_settings.credentials.model_dump(
        mode="json"
    )
    fetcher =CramerFetcher()
    params = {'lookback' : 10}
    res = fetcher.fetch_data(params, credentials)
    loop = asyncio.get_event_loop()
    data = loop.run_until_complete(asyncio.gather(*[res]))
    logging.info(f'Obtained:{data}')
    return data






