{%- set provider_class = cookiecutter.provider_name.replace('_', ' ').title().replace(' ', '') -%}
"""{{ cookiecutter.project_name }} provider."""

from openbb_core.provider.abstract.provider import Provider

from {{ cookiecutter.package_name }}.providers.{{ cookiecutter.provider_name }}.models.equity_historical import (
    {{ provider_class }}EquityHistoricalFetcher,
)
from {{ cookiecutter.package_name }}.providers.{{ cookiecutter.provider_name }}.models.example import (
    ExampleFetcher,
)

{{ cookiecutter.provider_name }}_provider = Provider(
    name="{{ cookiecutter.provider_name }}",
    description="Data provider for {{ cookiecutter.project_name }}.",
    website="https://{{ cookiecutter.project_tag }}.com",
    fetcher_dict={
        "EquityHistorical": {{ provider_class }}EquityHistoricalFetcher,
        "Example": ExampleFetcher,
    },
)
