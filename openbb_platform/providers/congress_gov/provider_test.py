#!/usr/bin/env python3
"""
Simple test for Congress.gov Provider using OpenBB provider system.
"""

import asyncio
import os
from openbb_congress_gov.models.congress_bills import CongressBillsFetcher
from openbb_congress_gov.models.congress_bill_summaries import (
    CongressBillSummariesFetcher,
)
from openbb_congress_gov.models.presidential_documents import (
    PresidentialDocumentsFetcher,
)


async def test_presidential_documents():
    """Test Presidential Documents fetcher (no API key needed)."""
    print("=== Testing Presidential Documents Fetcher ===")
    
    try:
        fetcher = PresidentialDocumentsFetcher()
        
        # Test with basic parameters
        query_data = fetcher.query_data_type(
            limit=3,
            president="joe-biden",
            doc_type="executive_order"
        )
        
        # Make the request
        result = await fetcher.afetch(query_data, {})
        
        if result:
            print(f"✅ Successfully fetched {len(result)} presidential documents")
            if result:
                first_doc = result[0]
                print(f"📋 First document: {first_doc.title[:80]}...")
                print(f"   Type: {first_doc.document_type}")
                print(f"   Publication date: {first_doc.publication_date}")
                if hasattr(first_doc, "pdf_url") and first_doc.pdf_url:
                    print(f"   PDF URL: {first_doc.pdf_url}")
        else:
            print("⚠️  No documents found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_congress_bills():
    """Test Congress Bills fetcher (requires API key)."""
    print("\n=== Testing Congress Bills Fetcher ===")
    
    # Check for API key
    api_key = os.getenv("CONGRESS_API_KEY")
    if not api_key:
        print("⚠️  No API key found. Set CONGRESS_API_KEY environment variable.")
        print("   To get an API key: https://api.congress.gov/sign-up/")
        return
    
    try:
        fetcher = CongressBillsFetcher()
        
        # Test with basic parameters
        query_data = fetcher.query_data_type(
            limit=3,
            sort="updateDate+desc"
        )
        
        # Credentials
        credentials = {"api_key": api_key}
        
        # Make the request
        result = await fetcher.afetch(query_data, credentials)
        
        if result:
            print(f"✅ Successfully fetched {len(result)} bills")
            if result:
                first_bill = result[0]
                print(f"📄 First bill: {first_bill.title[:80]}...")
                print(f"   Congress: {first_bill.congress}")
                print(f"   Type: {first_bill.bill_type}")
                print(f"   Number: {first_bill.number}")
                if hasattr(first_bill, 'latest_action_date') and first_bill.latest_action_date:
                    print(f"   Latest action: {first_bill.latest_action_date}")
        else:
            print("⚠️  No bills found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_bill_summaries():
    """Test Bill Summaries fetcher (requires API key)."""
    print("\n=== Testing Bill Summaries Fetcher ===")
    
    # Check for API key
    api_key = os.getenv("CONGRESS_API_KEY")
    if not api_key:
        print("⚠️  No API key found. Set CONGRESS_API_KEY environment variable.")
        return
    
    try:
        fetcher = CongressBillSummariesFetcher()
        
        # Test with a known bill: HR 1 from 118th Congress
        query_data = fetcher.query_data_type(
            congress=118,
            bill_type="hr",
            bill_number="1",
            limit=2
        )
        
        # Credentials
        credentials = {"api_key": api_key}
        
        # Make the request
        result = await fetcher.afetch(query_data, credentials)
        
        if result:
            print(f"✅ Successfully fetched {len(result)} summaries for HR 1")
            if result:
                first_summary = result[0]
                print(f"📝 First summary action: {first_summary.action_desc}")
                print(f"   Date: {first_summary.action_date}")
                print(f"   Text length: {len(first_summary.text or '')} characters")
                if first_summary.text:
                    print(f"   Text preview: {first_summary.text[:100]}...")
        else:
            print("⚠️  No summaries found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_provider_structure():
    """Test that the provider can be imported."""
    print("Congress.gov Provider Test")
    print("=" * 40)
    print("=== Testing Provider Structure ===")
    
    try:
        print("✅ Provider imports successfully")
        
        # Test model imports
        from openbb_congress_gov.models.congress_bills import (
            CongressBillsFetcher,
        )
        from openbb_congress_gov.models.congress_bill_summaries import (
            CongressBillSummariesFetcher,
        )
        from openbb_congress_gov.models.presidential_documents import (
            PresidentialDocumentsFetcher,
        )
        print("✅ All fetcher models import successfully")
        
        # Test that fetchers can be instantiated
        CongressBillsFetcher()
        CongressBillSummariesFetcher()
        PresidentialDocumentsFetcher()
        print("✅ All fetchers can be instantiated")
        
    except Exception as e:
        print(f"❌ Error testing provider structure: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def main():
    """Main test function."""
    
    # Test provider structure first
    if not test_provider_structure():
        print("\n❌ Provider structure test failed. Stopping.")
        return
    
    # Test API endpoints
    await test_presidential_documents()
    await test_congress_bills()
    await test_bill_summaries()
    
    print("\n" + "=" * 40)
    print("Provider test completed!")
    
    api_key = os.getenv("CONGRESS_API_KEY")
    if not api_key:
        print("\nTo test Congress.gov API endpoints:")
        print("1. Go to: https://api.congress.gov/sign-up/")
        print("2. Fill out the form and agree to terms")
        print("3. Check your email for the API key")
        print("4. Set it: export CONGRESS_API_KEY='your_key'")


if __name__ == "__main__":
    asyncio.run(main()) 