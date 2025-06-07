"""Congress.gov Provider Module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_congress_gov.models.congress_bills import CongressBillsFetcher
from openbb_congress_gov.models.congress_bill_summaries import (
    CongressBillSummariesFetcher,
)
from openbb_congress_gov.models.presidential_documents import (
    PresidentialDocumentsFetcher,
)

congress_gov_provider = Provider(
    name="congress_gov",
    website="https://api.congress.gov",
    description="""The Congress.gov API provides legislative data from the U.S. 
Congress, including bills, summaries, and related information. The Federal 
Register API provides access to presidential documents and regulations.""",
    credentials=["api_key"],
    fetcher_dict={
        "CongressBills": CongressBillsFetcher,
        "CongressBillSummaries": CongressBillSummariesFetcher,
        "PresidentialDocuments": PresidentialDocumentsFetcher,
    },
    repr_name="Congress.gov",
    instructions="""To get a Congress.gov API key:

1. Go to https://api.congress.gov/sign-up/
2. Fill out the registration form with your information
3. Agree to the terms of service
4. You will receive an API key via email

The API key is free and provides access to all Congress.gov data.

For Presidential Documents, no API key is required as it uses the 
Federal Register API.""",
)
