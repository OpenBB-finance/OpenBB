import unittest
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.options.pipeline_options import PipelineOptions
import asyncio
import apache_beam as beam
from openbb_yfinance.models.equity_quote import YFinanceEquityQuoteFetcher as quote_fetcher
from openbb_yfinance.models.equity_profile import YFinanceEquityProfileFetcher as profile_fetcher
from openbb_yfinance.models.company_news import YFinanceCompanyNewsFetcher as news_fetcher


class AsyncProcess(beam.DoFn):

    def __init__(self, credentials, fetcher):
        self.credentials = credentials
        self.fetcher = fetcher

    async def fetch_data(self, element: str):
        params = dict(symbol=element)
        data = await self.fetcher.fetch_data(params, self.credentials)
        return [d.model_dump(exclude_none=True) for d in data]

    def process(self, element: str):
        return asyncio.run(self.fetch_data(element))

class MyTestCase(unittest.TestCase):


    def test_sample_pipeline(self):
        credentials = {} # Running OBB endpoints which do not require credentials
        debug_sink = beam.Map(print)
        ticker = 'AAPL'

        with TestPipeline(options=PipelineOptions()) as p:
            quote = (p | 'Start Quote' >> beam.Create([ticker])
                     | 'Run Quote' >> beam.ParDo(AsyncProcess(credentials, quote_fetcher))
                     | 'Print quote' >> debug_sink)

            profile = (p | 'Start Profile' >> beam.Create([ticker])
                     | 'Run Profile' >> beam.ParDo(AsyncProcess(credentials, profile_fetcher))
                     | 'Print profile' >> debug_sink)

            news = (p | 'Start News' >> beam.Create([ticker])
                       | 'Run News' >> beam.ParDo(AsyncProcess(credentials, news_fetcher))
                       | 'Print nes' >> debug_sink)


if __name__ == '__main__':
    unittest.main()
