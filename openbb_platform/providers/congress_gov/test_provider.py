"""Test script for Congress.gov Provider.

This script allows you to test the provider functionality directly.
Run this in a Python terminal to verify the provider works.
"""

import asyncio
import sys
import os

# Add the current directory to Python path so we can import the provider
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from openbb_congress_gov.models.congress_bills import CongressBillsFetcher
    from openbb_congress_gov.models.congress_bill_summaries import CongressBillSummariesFetcher
    from openbb_congress_gov.models.presidential_documents import PresidentialDocumentsFetcher
    print("✅ Successfully imported all fetchers")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


async def test_congress_bills(api_key=None):
    """Test Congress Bills fetcher."""
    print("\n=== Testing Congress Bills ===")
    
    # Test query parameters
    query_params = {
        "limit": 5,
        "sort": "updateDate+desc"
    }
    
    credentials = {"api_key": api_key} if api_key else None
    
    try:
        fetcher = CongressBillsFetcher()
        
        # Transform query
        query = fetcher.transform_query(query_params)
        print(f"✅ Query transformation successful: {query}")
        
        if api_key:
            # Extract data (only if API key provided)
            print("🔄 Fetching data from Congress API...")
            data = await fetcher.aextract_data(query, credentials)
            print(f"✅ Successfully fetched {len(data)} bills")
            
            # Transform data
            transformed = fetcher.transform_data(query, data)
            print(f"✅ Successfully transformed data: {len(transformed)} bills")
            
            # Show first bill
            if transformed:
                first_bill = transformed[0]
                print(f"📄 First bill: {first_bill.title[:100]}...")
                print(f"   Congress: {first_bill.congress}")
                print(f"   Type: {first_bill.bill_type}")
                print(f"   Number: {first_bill.number}")
        else:
            print("⚠️  No API key provided, skipping data fetch")
            
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_bill_summaries(api_key=None):
    """Test Bill Summaries fetcher."""
    print("\n=== Testing Bill Summaries ===")
    
    # Test query parameters for a known bill
    query_params = {
        "congress": 118,
        "bill_type": "hr",
        "bill_number": "1",
        "limit": 3
    }
    
    credentials = {"api_key": api_key} if api_key else None
    
    try:
        fetcher = CongressBillSummariesFetcher()
        
        # Transform query
        query = fetcher.transform_query(query_params)
        print(f"✅ Query transformation successful: {query}")
        
        if api_key:
            # Extract data (only if API key provided)
            print("🔄 Fetching summaries from Congress API...")
            data = await fetcher.aextract_data(query, credentials)
            print(f"✅ Successfully fetched {len(data)} summaries")
            
            # Transform data
            transformed = fetcher.transform_data(query, data)
            print(f"✅ Successfully transformed data: {len(transformed)} summaries")
            
            # Show first summary
            if transformed:
                first_summary = transformed[0]
                print(f"📝 First summary action: {first_summary.action_desc}")
                print(f"   Date: {first_summary.action_date}")
                print(f"   Text length: {len(first_summary.text or '')} characters")
        else:
            print("⚠️  No API key provided, skipping data fetch")
            
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_presidential_documents():
    """Test Presidential Documents fetcher."""
    print("\n=== Testing Presidential Documents ===")
    
    # Test query parameters
    query_params = {
        "president": "joe-biden",
        "document_types": "executive_order",
        "per_page": 3,
        "page": 1
    }
    
    # No credentials needed for Federal Register API
    credentials = None
    
    try:
        fetcher = PresidentialDocumentsFetcher()
        
        # Transform query
        query = fetcher.transform_query(query_params)
        print(f"✅ Query transformation successful: {query}")
        
        # Extract data
        print("🔄 Fetching data from Federal Register API...")
        data = await fetcher.aextract_data(query, credentials)
        print(f"✅ Successfully fetched {len(data)} documents")
        
        # Transform data
        transformed = fetcher.transform_data(query, data)
        print(f"✅ Successfully transformed data: {len(transformed)} documents")
        
        # Show first document
        if transformed:
            first_doc = transformed[0]
            print(f"📋 First document: {first_doc.title[:100]}...")
            print(f"   Type: {first_doc.document_type}")
            print(f"   Publication date: {first_doc.publication_date}")
            print(f"   PDF URL: {first_doc.pdf_url}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Main test function."""
    print("Congress.gov Provider Test Suite")
    print("=" * 40)
    
    # Check if API key is provided
    api_key = os.getenv("CONGRESS_API_KEY") or os.getenv("API_KEY")
    
    if api_key:
        print(f"🔑 Using API key: {api_key[:8]}...")
    else:
        print("⚠️  No API key found in environment variables")
        print("   Set CONGRESS_API_KEY or API_KEY to test Congress API endpoints")
        print("   Presidential Documents will still work (no API key needed)")
    
    # Run tests
    await test_congress_bills(api_key)
    await test_bill_summaries(api_key)
    await test_presidential_documents()
    
    print("\n" + "=" * 40)
    print("Test suite completed!")


def run_tests():
    """Run the test suite."""
    asyncio.run(main())


if __name__ == "__main__":
    run_tests() 