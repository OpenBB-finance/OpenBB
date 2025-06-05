from openbb_core.provider.abstract.provider import Provider
from .supabase_fetchers import SupabaseFetcher

supabase_provider = Provider(
    name="supabase",
    website="https://supabase.io/",
    description="Provider for Supabase, allowing execution of queries against a Supabase backend.",
    credentials=["supabase_url", "supabase_key"], # Standard Supabase credentials
    fetcher_dict={
        "SupabaseQuery": SupabaseFetcher, # Generic fetcher name
    },
)
