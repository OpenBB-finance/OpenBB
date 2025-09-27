# OpenBB e-Stat Provider

## Overview

The e-Stat provider integrates Japan's official government statistical portal API into OpenBB, providing access to comprehensive economic, demographic, and social statistics from Japanese government ministries and agencies.

**Attribution Notice**: This service uses API functions from e-Stat, however its contents are not guaranteed by government.

## What is e-Stat?

[e-Stat](https://www.e-stat.go.jp/en) is the official portal site of Japanese government statistics, operated by the Ministry of Internal Affairs and Communications. It provides access to statistical data from all Japanese government ministries and agencies in a centralized location.

### Available Data Categories

The e-Stat API provides access to 28+ statistical databases including:

- **Population & Households**: Population Census, Vital Statistics, Population Estimates
- **Labor & Wages**: Labour Force Survey, Employment Status Survey, Basic Wage Structure
- **Economic Data**: Economic Census, Consumer Price Index, Retail Price Survey
- **Trade Statistics**: Import/Export data, Trade indices
- **Industry**: Industrial Production Index, Manufacturing data
- **Regional Data**: Prefecture and municipality-level statistics
- **Social Statistics**: Education, Health, Housing, and more

## Setup Instructions

To use the e-Stat provider, you need to register for a free API key:

### Step 1: Register for e-Stat Account

1. Visit: https://www.e-stat.go.jp/en/mypage/user/preregister
2. Complete registration with your email
3. Confirm your email and log in

### Step 2: Get Your Application ID (API Key)

1. After logging in, go to "My Page" (top right corner)
2. Click on "API functions" section
3. Fill in the simple form:
   - **Name**: Your app name
   - **URL**: Your URL (use `http://test.localhost/` if not public)
   - **Overview**: Brief description (optional)
4. Click "Issue" button
5. Your Application ID will be displayed immediately

![e-Stat Application ID Dashboard](./appId.png)
*Example of the API functions dashboard showing Application IDs*

### Step 3: Configure Your Personal API Key

```python
from openbb import obb

# Override the default with your personal API key
obb.account.credentials.estat_api_key = "your_application_id_here"
```

## Usage Examples

### Basic Statistical Data Query

```python
from openbb import obb

# First, set your API key (required)
obb.account.credentials.estat_api_key = "your_application_id_here"

# Get Japanese population census data
data = obb.economy.statistical_data(
    provider="estat",
    symbol="0003433219",  # Population Census dataset ID
)

# Get data with specific parameters
data = obb.economy.statistical_data(
    provider="estat",
    symbol="0003433219",
    area_code="13000",  # Tokyo
    start_date="2020-01",
    end_date="2023-12"
)
```

### Query Parameters

- `symbol` / `stats_data_id`: Statistical dataset ID (required)
- `stats_code`: Statistical survey code (e.g., "00200521" for Population Census)
- `area_code`: Area code for specific regions
- `category_code`: Category filter
- `search_kind`: "1" for standard statistics, "2" for regional mesh statistics
- `collect_area`: Collection area for aggregated data
- `start_date` / `end_date`: Date range for time series data

### Finding Dataset IDs

To find specific dataset IDs:
1. Browse available databases: https://www.e-stat.go.jp/en/stat-search/database
2. Use the API's `getStatsList` endpoint to search programmatically
3. Common dataset examples:
   - Population Census: Various IDs starting with "0003..."
   - Consumer Price Index: IDs vary by category
   - Labour Force Survey: Check current catalog

## API Documentation

- **API Guide**: https://www.e-stat.go.jp/api/api/index.php/en/api-info/api-guide
- **API Specification**: https://www.e-stat.go.jp/api/api/index.php/en/api-info/api-spec
- **Data Overview**: https://www.e-stat.go.jp/api/api/index.php/en/api-info/api-data
- **Database Search**: https://www.e-stat.go.jp/en/stat-search/database

### Technical Details

- **Base URL**: `https://api.e-stat.go.jp/rest/3.0/app/`
- **Formats**: JSON (default), XML, CSV
- **Language**: English supported with `lang=E` parameter
- **Rate Limits**: Not explicitly documented, use responsibly
- **HTTPS**: Supported
- **Compression**: gzip supported

## Development

### Running Tests

```bash
cd openbb_platform/providers/estat
poetry install
poetry run pytest tests/
```

### Test Coverage

The test suite includes:
- Parameter validation
- Data transformation
- Error handling (authentication, data not found, server errors)
- Helper function tests
- Edge case handling

## Troubleshooting

### Common Issues

1. **"Invalid Application ID" Error**
   - Verify your API key is correct
   - Ensure you're using the Application ID from the API functions page

2. **"Statistical data not found" Error**
   - Check the dataset ID is valid
   - Some datasets may require specific parameter combinations

3. **Japanese Text in Responses**
   - The provider sets `lang=E` for English
   - Some metadata may still contain Japanese text
   - Use browser translation tools when browsing the e-Stat website

### Support

- e-Stat Support (Japanese): https://www.e-stat.go.jp/contact
- OpenBB Issues: https://github.com/OpenBB-finance/OpenBB/issues

## License & Attribution

When using this provider, you must acknowledge:

> This service uses API functions from e-Stat, however its contents are not guaranteed by government.

This attribution is required by e-Stat's terms of use: https://www.e-stat.go.jp/api/api/index.php/en/api-info/credit

## Contributing

Contributions are welcome! Areas for improvement:
- Additional data fetchers for specific statistical categories
- Support for CSV/XML response formats
- Caching for frequently accessed metadata
- Enhanced date parsing for various Japanese fiscal periods

Please ensure all contributions maintain the attribution notice and comply with e-Stat's terms of use.