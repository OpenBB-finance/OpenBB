# OBBject Store Extension

`openbb-store` is an OBBject extension for storing and retrieving OBBjects, Data, DataFrames, dictionaries, lists, and strings.

Each entry is stored as a compressed pickle, with SHA1 signature, using the LZMA module with the "xz" algorithm set to maximum compression.

## Installation

Install this extension by navigating into the directory and entering:

```console
pip install -e .
```

Then, rebuild the Python interface:

```console
python -c "import openbb;openbb.build()"
```

## Store Class

Within the OpenBB Platform, the extension acts as a Global class with methods to add, retrieve, and save groups of data objects to memory or file in a transportable and compressed format.

When used as standalone, the `user_data_directory` property (preference) should be set to the desired read/write directory
upon initialization. Alternatively, specify the complete path to the file when using the IO methods' `filename` parameter.
```

## Usage

Every output from the OpenBB Platform Python interface will have the `store` attribute.

### Supported Data Types

The following is a list of supported data objects:

- OBBject
- Data (generic OpenBB Data class)
- DataFrame
- List
- Dictionary
- String

The contents of any object being added must be serializable.

### Add Data

```python
from openbb import obb

data = obb.equity.price.historical("NVDA", provider="yfinance", start_date="2023-01-01", end_date="2023-12-31")
data.store.add_store(data=data, name="nvda2023")
```

A confirmation will display unless the "verbose" property is set to `False`.

```console
"Data store 'nvda2023' added successfully."
```

Additional data can be added to the collection, and then exported as a single package.

```python
data = obb.equity.fundamental.metrics("NVDA", provider="yfinance")
data.store.add_store(data = data.to_df().set_index("symbol").T, name="nvdaMetrics", description="Key Valuation Metrics for NVDA.")
```

```console
"Data store 'nvdaMetrics' added successfully."
```

### Directory Of Objects

An inventory of stored objects is displayed with the 'directory' property.

```python
data.store.directory
```

```console
{'nvda2023': {'description': None,
  'data_class': 'OBBject',
  'schema_preview': "{'length': 250, 'fields_set': ['open', 'high', 'low', 'close', 'volume', 'split_..."},
 'nvdaMetrics': {'description': 'Key Valuation Metrics for NVDA.',
  'data_class': 'DataFrame',
  'schema_preview': "{'length': 34, 'width': 1, 'columns': Index(['NVDA'], dtype='object', name='symb..."}}
```

### Schemas

Metadata related to the schema are stored independent of the actual data store.
Schemas are retrieved with the `get_schema` method, using the assigned 'name' as the key.

Example DataFrame schema:

```python
data.store.get_schema("nvdaMetrics")
```

```console
{'length': 34,
 'width': 1,
 'columns': Index(['NVDA'], dtype='object', name='symbol'),
 'index': Index(['market_cap', 'pe_ratio', 'forward_pe', 'peg_ratio', 'peg_ratio_ttm',
        'enterprise_to_ebitda', 'earnings_growth', 'earnings_growth_quarterly',
        'revenue_per_share', 'revenue_growth', 'enterprise_to_revenue',
        'quick_ratio', 'current_ratio', 'debt_to_equity', 'gross_margin',
        'operating_margin', 'ebitda_margin', 'profit_margin',
        'return_on_assets', 'return_on_equity', 'dividend_yield',
        'dividend_yield_5y_avg', 'payout_ratio', 'book_value', 'price_to_book',
        'enterprise_value', 'overall_risk', 'audit_risk', 'board_risk',
        'compensation_risk', 'shareholder_rights_risk', 'beta',
        'price_return_1y', 'currency'],
       dtype='object'),
 'types_map': symbol
 NVDA    object
 dtype: object}
```

Example Pydantic model schema:

```python
data.store.get_schema("nvda2023")
```

```console
{'length': 250,
 'fields_set': ['open',
  'high',
  'low',
  'close',
  'volume',
  'split_ratio',
  'dividend'],
 'data_model': {'additionalProperties': True,
  'description': 'Yahoo Finance Equity Historical Price Data.',
  'properties': {'date': {'anyOf': [{'format': 'date', 'type': 'string'},
     {'format': 'date-time', 'type': 'string'}],
    'description': 'The date of the data.',
    'title': 'Date'},
   'open': {'description': 'The open price.',
    'title': 'Open',
    'type': 'number'},
   'high': {'description': 'The high price.',
    'title': 'High',
    'type': 'number'},
   'low': {'description': 'The low price.', 'title': 'Low', 'type': 'number'},
   'close': {'description': 'The close price.',
    'title': 'Close',
    'type': 'number'},
   'volume': {'anyOf': [{'type': 'number'},
     {'type': 'integer'},
     {'type': 'null'}],
    'default': None,
    'description': 'The trading volume.',
    'title': 'Volume'},
   'vwap': {'anyOf': [{'type': 'number'}, {'type': 'null'}],
    'default': None,
    'description': 'Volume Weighted Average Price over the period.',
    'title': 'Vwap'},
   'split_ratio': {'anyOf': [{'type': 'number'}, {'type': 'null'}],
    'default': None,
    'description': 'Ratio of the equity split, if a split occurred.',
    'title': 'Split Ratio'},
   'dividend': {'anyOf': [{'type': 'number'}, {'type': 'null'}],
    'default': None,
    'description': 'Dividend amount (split-adjusted), if a dividend was paid.',
    'title': 'Dividend'}},
  'required': ['date', 'open', 'high', 'low', 'close'],
  'title': 'YFinanceEquityHistoricalData',
  'type': 'object'},
 'created_at': '2024-06-18 13:08:44.778360',
 'uid': '06671e94-d271-7d4f-8000-43094acbb703'}
```

### Restore Data

Restore data from the Store extension by using the `get_store` method. Each archive and pickled object are validated against a signature before opening.

```python
data.store.get_store("nvdaMetrics")
```

|                           | NVDA            |
|:--------------------------|:----------------|
| market_cap                | 7.0             |
| pe_ratio                  | 1.694           |
| forward_pe                | 10.0            |
| peg_ratio                 | 1.998           |
| peg_ratio_ttm             | 1.0             |
| enterprise_to_ebitda      | USD             |
| earnings_growth           | 3.529           |
| earnings_growth_quarterly | 22.866          |
| revenue_per_share         | 0.00029999999   |
| revenue_growth            | 0.0012          |
| enterprise_to_revenue     | 6.5             |
| quick_ratio               | 6.284           |
| current_ratio             | 0.61768         |
| debt_to_equity            | 64.98           |
| gross_margin              | 40.137          |
| operating_margin          | 3201907032064   |
| ebitda_margin             | 37.661114       |
| profit_margin             | 0.75286         |
| return_on_assets          | 3335037648896.0 |
| return_on_equity          | 0.64925003      |
| dividend_yield            | 7.0             |
| dividend_yield_5y_avg     | 0.0094          |
| payout_ratio              | 79.75294        |
| book_value                | 1.04            |
| price_to_book             | 1.5013          |
| enterprise_value          | 1.9898648       |
| overall_risk              | 67.85786        |
| audit_risk                | 0.53398         |
| board_risk                | 2.877           |
| compensation_risk         | 0.49103         |
| shareholder_rights_risk   | 1.15658         |
| beta                      | 2.621           |
| price_return_1y           | 3.234           |
| currency                  | 6.0             |

When the stored object is an instance of `OBBject`, the element to retrieve can be isolated with the `element` parameter.
By default, it is "dataframe". When set as "OBBject", the object is restored in its original form.

```python
data.store.get_store("nvda2023", element="OBBject")
```

```console
OBBject

id: 06671e94-d271-7d4f-8000-43094acbb703
results: [{'date': datetime.date(2023, 1, 3), 'open': 14.85099983215332, 'high': 14...
provider: yfinance
warnings: None
chart: None
extra: {'metadata': {'arguments': {'provider_choices': {'provider': 'yfinance'}, 's...
```

### Exporting/Importing

Any item(s) loaded into the extension can be exported to file as a ".xz" archive.
A list of "names" isolates specific objects for writing to disk. Without supplying names,
all entries are exported.

```python
data.store.save_store_to_file(filename="nvda")
```

Importing works the same way, and a list of "names" can also be included to load only the desired elements.

```python
data.store.load_store_from_file(filename="nvda")
```

The default path can be overridden by including the complete path, beginning with "/", in the filename.
Do not include the file extension with the name.
