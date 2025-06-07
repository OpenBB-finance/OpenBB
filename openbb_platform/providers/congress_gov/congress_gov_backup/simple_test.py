"""Simple test for Congress.gov Provider without OpenBB dependencies.

This script tests the API endpoints directly using requests.
"""

import asyncio
import aiohttp
import json
import os


async def test_federal_register_api():
    """Test Federal Register API (Presidential Documents) - no API key needed."""
    print("=== Testing Federal Register API (Presidential Documents) ===")
    
    url = "https://www.federalregister.gov/api/v1/documents.json"
    params = {
        "per_page": 3,
        "page": 1,
        "conditions[president][]": "joe-biden",
        "conditions[type][]": "PRESDOCU",
        "conditions[presidential_document_type][]": "executive_order"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get("results", [])
                    print(f"✅ Successfully fetched {len(results)} presidential documents")
                    
                    if results:
                        first_doc = results[0]
                        print(f"📋 First document: {first_doc.get('title', '')[:80]}...")
                        print(f"   Type: {first_doc.get('type', '')}")
                        print(f"   Publication date: {first_doc.get('publication_date', '')}")
                        print(f"   PDF URL: {first_doc.get('pdf_url', '')}")
                    else:
                        print("⚠️  No documents found")
                else:
                    print(f"❌ HTTP Error: {response.status}")
                    text = await response.text()
                    print(f"   Response: {text[:200]}...")
                    
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_congress_api(api_key=None):
    """Test Congress.gov API (requires API key)."""
    print("\n=== Testing Congress.gov API (Bills) ===")
    
    if not api_key:
        print("⚠️  No API key provided. Skipping Congress API test.")
        print("   To test Congress API, provide API key as environment variable:")
        print("   export CONGRESS_API_KEY='your_key_here'")
        return
    
    url = "https://api.congress.gov/v3/bill"
    params = {
        "api_key": api_key,
        "format": "json",
        "limit": 3,
        "sort": "updateDate+desc"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    bills = data.get("bills", [])
                    print(f"✅ Successfully fetched {len(bills)} bills")
                    
                    if bills:
                        first_bill = bills[0]
                        print(f"📄 First bill: {first_bill.get('title', '')[:80]}...")
                        print(f"   Congress: {first_bill.get('congress', '')}")
                        print(f"   Type: {first_bill.get('type', '')}")
                        print(f"   Number: {first_bill.get('number', '')}")
                        
                        latest_action = first_bill.get('latestAction', {})
                        print(f"   Latest action: {latest_action.get('actionDate', '')} - {latest_action.get('text', '')[:50]}...")
                    else:
                        print("⚠️  No bills found")
                        
                elif response.status == 401:
                    print("❌ Authentication failed. Check your API key.")
                else:
                    print(f"❌ HTTP Error: {response.status}")
                    text = await response.text()
                    print(f"   Response: {text[:200]}...")
                    
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_bill_summaries(api_key=None):
    """Test Bill Summaries API."""
    print("\n=== Testing Bill Summaries API ===")
    
    if not api_key:
        print("⚠️  No API key provided. Skipping Bill Summaries test.")
        return
    
    # Test with a known bill: HR 1 from 118th Congress
    congress = 118
    bill_type = "hr"
    bill_number = "1"
    
    url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type}/{bill_number}/summaries"
    params = {
        "api_key": api_key,
        "format": "json",
        "limit": 2
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    summaries = data.get("summaries", [])
                    print(f"✅ Successfully fetched {len(summaries)} summaries for {bill_type.upper()} {bill_number}")
                    
                    if summaries:
                        first_summary = summaries[0]
                        print(f"📝 First summary action: {first_summary.get('actionDesc', '')}")
                        print(f"   Date: {first_summary.get('actionDate', '')}")
                        text = first_summary.get('text', '') or ''
                        print(f"   Text length: {len(text)} characters")
                        if text:
                            print(f"   Text preview: {text[:100]}...")
                    else:
                        print("⚠️  No summaries found")
                        
                elif response.status == 401:
                    print("❌ Authentication failed. Check your API key.")
                elif response.status == 404:
                    print(f"❌ Bill {bill_type.upper()} {bill_number} not found in Congress {congress}")
                else:
                    print(f"❌ HTTP Error: {response.status}")
                    text = await response.text()
                    print(f"   Response: {text[:200]}...")
                    
    except Exception as e:
        print(f"❌ Error: {e}")


def test_provider_structure():
    """Test that the provider can be imported."""
    print("=== Testing Provider Structure ===")
    
    try:
        # Test basic imports without OpenBB dependencies
        import sys
        import os
        
        # Add current directory to path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        # Test that the provider files exist and have correct structure
        provider_files = [
            "openbb_congress_gov/__init__.py",
            "openbb_congress_gov/models/__init__.py",
            "openbb_congress_gov/models/congress_bills.py",
            "openbb_congress_gov/models/congress_bill_summaries.py",
            "openbb_congress_gov/models/presidential_documents.py",
            "openbb_congress_gov/utils/helpers.py"
        ]
        
        for file_path in provider_files:
            full_path = os.path.join(current_dir, file_path)
            if os.path.exists(full_path):
                print(f"✅ Found: {file_path}")
            else:
                print(f"❌ Missing: {file_path}")
                
        # Test pyproject.toml
        pyproject_path = os.path.join(current_dir, "pyproject.toml")
        if os.path.exists(pyproject_path):
            print("✅ Found: pyproject.toml")
            
            with open(pyproject_path, 'r') as f:
                content = f.read()
                if 'openbb-congress-gov' in content:
                    print("✅ Package name correctly configured")
                if 'congress_gov_provider' in content:
                    print("✅ Provider entry point configured")
        else:
            print("❌ Missing: pyproject.toml")
                
    except Exception as e:
        print(f"❌ Error testing provider structure: {e}")


async def main():
    """Main test function."""
    print("Congress.gov Provider API Test")
    print("=" * 40)
    
    # Test provider structure first
    test_provider_structure()
    
    # Get API key from environment
    api_key = os.getenv("CONGRESS_API_KEY") or os.getenv("API_KEY")
    
    if api_key:
        print(f"\n🔑 Using API key: {api_key[:8]}...")
    else:
        print("\n⚠️  No API key found. Set CONGRESS_API_KEY environment variable to test Congress API.")
        print("   Presidential Documents will still work (no API key needed).")
    
    # Test APIs
    await test_federal_register_api()
    await test_congress_api(api_key)
    await test_bill_summaries(api_key)
    
    print("\n" + "=" * 40)
    print("API Test completed!")
    print("\nTo get a Congress.gov API key:")
    print("1. Go to: https://api.congress.gov/sign-up/")
    print("2. Fill out the form and agree to terms")
    print("3. Check your email for the API key")
    print("4. Set it as environment variable: export CONGRESS_API_KEY='your_key'")


if __name__ == "__main__":
    asyncio.run(main()) 