"""{{ cookiecutter.package_name }} OpenBB Platform Provider."""

from openbb_core.provider.abstract.provider import Provider
from {{cookiecutter.package_name}}.providers.{{cookiecutter.provider_name}}.models.example import ExampleFetcher
from {{cookiecutter.package_name}}.providers.{{cookiecutter.provider_name}}.models.ohlc_example import {{cookiecutter.provider_name.replace('_', ' ').title().replace(' ', '')}}EquityHistoricalFetcher



{{cookiecutter.provider_name}}_provider = Provider(
    name="{{cookiecutter.provider_name}}",
    description="Data provider for {{cookiecutter.project_name}}.",
    # Only add 'credentials' if they are needed.
    # For multiple login details, list them all here.
    # credentials=["api_key"],
    website="https://{{cookiecutter.project_tag}}.com",
    # Here, we list out the fetchers showing what our provider can get.
    # The dictionary key is the fetcher's name, used in the `../routers/router.py`.
    fetcher_dict={
        "EquityHistorical": {{cookiecutter.provider_name.replace('_', ' ').title().replace(' ', '')}}EquityHistoricalFetcher,
        "Example": ExampleFetcher,
    }
)
