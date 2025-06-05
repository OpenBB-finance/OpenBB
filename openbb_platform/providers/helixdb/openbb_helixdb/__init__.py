from openbb_core.provider.abstract.provider import Provider
from .helix_fetchers import HelixDBFetcher # Adjusted import

helixdb_provider = Provider(
    name="helixdb",
    website="https://www.helix-db.com/", # Placeholder
    description="Provider for HelixDB, allowing execution of generic database queries.",
    credentials=["helixdb_api_key", "helixdb_database_url"], # Example credentials
    fetcher_dict={
        "HelixDBQuery": HelixDBFetcher, # Generic fetcher name
    },
)
