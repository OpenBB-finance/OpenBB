"""Quick test for Congress.gov Provider using standard library only."""

import urllib.request
import urllib.parse
import json
import os


def test_federal_register_api():
    """Test Federal Register API (Presidential Documents) - no API key needed."""
    print("=== Testing Federal Register API (Presidential Documents) ===")
    
    base_url = "https://www.federalregister.gov/api/v1/documents.json"
    params = {
        "per_page": "3",
        "page": "1",
        "conditions[president][]": "joe-biden",
        "conditions[type][]": "PRESDOCU",
        "conditions[presidential_document_type][]": "executive_order"
    }
    
    # Build URL with parameters
    query_string = urllib.parse.urlencode(params, doseq=True)
    url = f"{base_url}?{query_string}"
    
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                results = data.get("results", [])
                print(f"✅ Successfully fetched {len(results)} presidential documents")
                
                if results:
                    first_doc = results[0]
                    title = first_doc.get('title', '')
                    print(f"📋 First document: {title[:80]}...")
                    print(f"   Type: {first_doc.get('type', '')}")
                    print(f"   Publication date: {first_doc.get('publication_date', '')}")
                    print(f"   PDF URL: {first_doc.get('pdf_url', '')}")
                else:
                    print("⚠️  No documents found")
            else:
                print(f"❌ HTTP Error: {response.status}")
                
    except Exception as e:
        print(f"❌ Error: {e}")


def test_congress_api(api_key=None):
    """Test Congress.gov API (requires API key)."""
    print("\n=== Testing Congress.gov API (Bills) ===")
    
    if not api_key:
        print("⚠️  No API key provided. Skipping Congress API test.")
        print("   To test Congress API, provide API key as environment variable:")
        print("   export CONGRESS_API_KEY='your_key_here'")
        return
    
    base_url = "https://api.congress.gov/v3/bill"
    params = {
        "api_key": api_key,
        "format": "json",
        "limit": "3",
        "sort": "updateDate+desc"
    }
    
    query_string = urllib.parse.urlencode(params)
    url = f"{base_url}?{query_string}"
    
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                bills = data.get("bills", [])
                print(f"✅ Successfully fetched {len(bills)} bills")
                
                if bills:
                    first_bill = bills[0]
                    title = first_bill.get('title', '')
                    print(f"📄 First bill: {title[:80]}...")
                    print(f"   Congress: {first_bill.get('congress', '')}")
                    print(f"   Type: {first_bill.get('type', '')}")
                    print(f"   Number: {first_bill.get('number', '')}")
                    
                    latest_action = first_bill.get('latestAction', {})
                    action_date = latest_action.get('actionDate', '')
                    action_text = latest_action.get('text', '')
                    print(f"   Latest action: {action_date} - {action_text[:50]}...")
                else:
                    print("⚠️  No bills found")
                    
            else:
                print(f"❌ HTTP Error: {response.status}")
                if response.status == 401:
                    print("   Authentication failed. Check your API key.")
                
    except Exception as e:
        print(f"❌ Error: {e}")


def test_provider_structure():
    """Test that the provider files exist."""
    print("=== Testing Provider Structure ===")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Test that the provider files exist
    provider_files = [
        "openbb_congress_gov/__init__.py",
        "openbb_congress_gov/models/__init__.py", 
        "openbb_congress_gov/models/congress_bills.py",
        "openbb_congress_gov/models/congress_bill_summaries.py",
        "openbb_congress_gov/models/presidential_documents.py",
        "openbb_congress_gov/utils/helpers.py",
        "pyproject.toml"
    ]
    
    for file_path in provider_files:
        full_path = os.path.join(current_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
    
    # Check pyproject.toml content
    pyproject_path = os.path.join(current_dir, "pyproject.toml")
    if os.path.exists(pyproject_path):
        with open(pyproject_path, 'r') as f:
            content = f.read()
            if 'openbb-congress-gov' in content:
                print("✅ Package name correctly configured")
            if 'congress_gov_provider' in content:
                print("✅ Provider entry point configured")


def main():
    """Main test function."""
    print("Congress.gov Provider Quick Test")
    print("=" * 40)
    
    # Test provider structure first
    test_provider_structure()
    
    # Get API key from environment
    api_key = os.getenv("CONGRESS_API_KEY") or os.getenv("API_KEY")
    
    if api_key:
        print(f"\n🔑 Using API key: {api_key[:8]}...")
    else:
        print("\n⚠️  No API key found. Set CONGRESS_API_KEY environment variable.")
        print("   Presidential Documents will still work (no API key needed).")
    
    # Test APIs
    test_federal_register_api()
    test_congress_api(api_key)
    
    print("\n" + "=" * 40)
    print("Quick Test completed!")
    
    if not api_key:
        print("\nTo get a Congress.gov API key:")
        print("1. Go to: https://api.congress.gov/sign-up/")
        print("2. Fill out the form and agree to terms")
        print("3. Check your email for the API key")
        print("4. Set it: export CONGRESS_API_KEY='your_key'")


if __name__ == "__main__":
    main() 