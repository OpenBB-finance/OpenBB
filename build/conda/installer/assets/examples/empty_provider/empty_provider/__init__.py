"""Empty Provider Module."""

# Import the fetchers from each model.
from openbb_core.provider.abstract.provider import Provider

from empty_provider.models.empty_model import EmptyFetcher

empty_provider = Provider(
    name="empty",
    website="http://empty.io",
    description="""The empty provider is a supplier of promises.""",
    # credentials=["api_key"],  # Credentials added here are mapped to `user_settings.json` in the `credentials` key.
    fetcher_dict={
        "Empty": EmptyFetcher  # The key is the name of the model defined in the @router decorator.
    },
)

# Every provider follows this same pattern, so it is possible to import the fetchers from other providers
# and map them to the fetcher_dict above.
# from openbb_yfinance import yfinance_provider
# yfinance_fetchers = yfinance_provider.fetcher_dict.copy()
