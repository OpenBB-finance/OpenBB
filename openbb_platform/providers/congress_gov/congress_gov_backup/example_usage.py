"""Example usage of the Congress.gov Provider.

This script demonstrates how to use the Congress.gov provider
to fetch bills, bill summaries, and presidential documents.
"""

import asyncio

# Note: In a real environment, you would import from the installed package
# from openbb_congress_gov.models.congress_bills import CongressBillsFetcher
# from openbb_congress_gov.models.congress_bill_summaries import (
#     CongressBillSummariesFetcher
# )
# from openbb_congress_gov.models.presidential_documents import (
#     PresidentialDocumentsFetcher
# )


async def example_congress_bills():
    """Example of fetching Congress bills."""
    print("=== Congress Bills Example ===")
    
    # Example query parameters
    query_params = {
        "limit": 10,
        "sort": "updateDate+desc"
    }
    
    print("Query parameters:", query_params)
    print("This would fetch the latest 10 bills from Congress.gov")
    print("Credentials needed: congress_api_key")
    print()


async def example_bill_summaries():
    """Example of fetching bill summaries."""
    print("=== Bill Summaries Example ===")
    
    # Example query parameters for a specific bill
    query_params = {
        "congress": 118,
        "bill_type": "hr",
        "bill_number": "1",
        "limit": 5
    }
    
    print("Query parameters:", query_params)
    print("This would fetch summaries for HR 1 from the 118th Congress")
    print("Credentials needed: congress_api_key")
    print()


async def example_presidential_documents():
    """Example of fetching presidential documents."""
    print("=== Presidential Documents Example ===")
    
    # Example query parameters
    query_params = {
        "president": "joe-biden",
        "document_types": "executive_order,memorandum",
        "per_page": 10,
        "page": 1
    }
    
    print("Query parameters:", query_params)
    print("This would fetch executive orders and memoranda from Biden")
    print("Credentials needed: None (Federal Register API)")
    print()


async def main():
    """Run all examples."""
    print("Congress.gov Provider Usage Examples")
    print("=" * 40)
    print()
    
    await example_congress_bills()
    await example_bill_summaries()
    await example_presidential_documents()
    
    print("API Endpoints Used:")
    print("- Congress Bills: https://api.congress.gov/v3/bill")
    print("- Bill Summaries: https://api.congress.gov/v3/bill/"
          "{congress}/{type}/{number}/summaries")
    print("- Presidential Documents: "
          "https://www.federalregister.gov/api/v1/documents.json")
    print()
    print("To get a Congress.gov API key, visit: "
          "https://api.congress.gov/sign-up/")


if __name__ == "__main__":
    asyncio.run(main()) 