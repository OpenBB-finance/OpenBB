# Congress.gov Provider

This provider integrates with the Congress.gov API and Federal Register API to provide access to U.S. legislative data and presidential documents.

## Features

### Congress Bills
- Fetch bills from the U.S. Congress
- Filter by congress session, bill type, date range
- Sort by update date
- Support for pagination

### Bill Summaries  
- Get summaries for specific bills
- Detailed bill information including action dates and descriptions
- Full text content of bill summaries

### Presidential Documents
- Access presidential documents from the Federal Register
- Filter by president and document type
- Support for executive orders, memoranda, proclamations, and more
- No API key required for this endpoint

## Installation

This provider is part of the OpenBB Platform. Install it using:

```bash
pip install openbb-congress-gov
```

## Configuration

### Congress.gov API Key

To use the Congress Bills and Bill Summaries endpoints, you need a Congress.gov API key:

1. Go to https://api.congress.gov/sign-up/
2. Fill out the registration form
3. Agree to the terms of service  
4. You will receive an API key via email

The API key is free and provides access to all Congress.gov data.

### Setting up credentials

```python
import openbb
openbb.account.credentials.congress_api_key = "YOUR_API_KEY_HERE"
```

## Usage Examples

### Fetching Recent Bills

```python
import openbb

# Get the 10 most recently updated bills
bills = openbb.government.congress_bills(limit=10, sort="updateDate+desc")
```

### Getting Bill Summaries

```python
# Get summaries for a specific bill
summaries = openbb.government.congress_bill_summaries(
    congress=118,
    bill_type="hr", 
    bill_number="1"
)
```

### Presidential Documents

```python
# Get recent executive orders from President Biden
docs = openbb.government.presidential_documents(
    president="joe-biden",
    document_types="executive_order",
    per_page=20
)
```

## API Endpoints

- **Congress Bills**: `https://api.congress.gov/v3/bill`
- **Bill Summaries**: `https://api.congress.gov/v3/bill/{congress}/{type}/{number}/summaries`  
- **Presidential Documents**: `https://www.federalregister.gov/api/v1/documents.json`

## Data Models

### CongressBillsData
- congress: Congress session number
- number: Bill number
- bill_type: Type of bill (HR, S, etc.)
- title: Bill title
- latest_action_date: Date of latest action
- latest_action_text: Description of latest action
- origin_chamber: Chamber where bill originated
- update_date: Last update date
- url: Link to bill on congress.gov

### CongressBillSummariesData  
- action_date: Date of summary action
- action_desc: Description of summary action
- text: Summary text content
- update_date: Date summary was updated
- version_code: Summary version code

### PresidentialDocumentsData
- title: Document title
- document_type: Type of document
- document_number: Document number
- html_url: Link to HTML version
- pdf_url: Link to PDF version
- publication_date: Date published
- abstract: Document abstract
- excerpts: Document excerpts

## Rate Limits

- Congress.gov API: No specific rate limits documented
- Federal Register API: No authentication required, reasonable use expected

## Support

For issues with this provider, please open an issue on the OpenBB Platform repository.
