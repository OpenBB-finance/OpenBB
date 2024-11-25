"""Biztoc provider module."""

from openbb_biztoc.models.world_news import BiztocWorldNewsFetcher
from openbb_core.provider.abstract.provider import Provider

biztoc_provider = Provider(
    name="biztoc",
    website="https://api.biztoc.com",
    description="""BizToc uses Rapid API for its REST API.
You may sign up for your free account at https://rapidapi.com/thma/api/biztoc.

The Base URL for all requests is:

    https://biztoc.p.rapidapi.com/

If you're not a developer but would still like to use Biztoc outside of the main website,
we've partnered with OpenBB, allowing you to pull in BizToc's news stream in their Terminal.""",
    credentials=["api_key"],
    fetcher_dict={
        "WorldNews": BiztocWorldNewsFetcher,
    },
    repr_name="BizToc",
    deprecated_credentials={"API_BIZTOC_TOKEN": "biztoc_api_key"},
    instructions="The BizToc API is hosted on RapidAPI. To set up, go to: https://rapidapi.com/thma/api/biztoc.\n\n![biztoc0](https://github.com/marban/OpenBBTerminal/assets/18151143/04cdd423-f65e-4ad8-ad5a-4a59b0f5ddda)\n\nIn the top right, select 'Sign Up'. After answering some questions, you will be prompted to select one of their plans.\n\n![biztoc1](https://github.com/marban/OpenBBTerminal/assets/18151143/9f3b72ea-ded7-48c5-aa33-bec5c0de8422)\n\nAfter signing up, navigate back to https://rapidapi.com/thma/api/biztoc. If you are logged in, you will see a header called X-RapidAPI-Key.\n\n![biztoc2](https://github.com/marban/OpenBBTerminal/assets/18151143/0f3b6c91-07e0-447a-90cd-a9e23522929f)",  # noqa: E501  pylint: disable=line-too-long
)
