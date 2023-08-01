"""Provider helpers."""


import json
import re
from io import StringIO
from typing import Callable, Dict, List, Optional, Type, Union

from openbb_provider.abstract.fetcher import DataType, ProviderDataType


def get_querystring(items: dict, exclude: List[str]) -> str:
    """Turns a dictionary into a querystring, excluding the keys in the exclude list.

    Parameters:
    -----------
    items: dict
        The dictionary to be turned into a querystring.

    exclude: List[str]
        The keys to be excluded from the querystring.

    Returns:
    --------
    str
        The querystring.

    """
    for item in exclude:
        items.pop(item)
    params = {k: v for k, v in items.items() if v is not None}
    return "&".join([f"{k}={v}" for k, v in params.items()])


def process(
    row: ProviderDataType, key: str, processors: Optional[Dict[str, Callable]] = None
):
    if not processors:
        return getattr(row, key)
    if key not in processors:
        return getattr(row, key)
    return processors[key](getattr(row, key))


def camel_to_snake(name: str) -> str:
    "Converts a camelCase string to snake_case."
    pattern = re.compile(r"(?<!^)(?=[A-Z])")
    return pattern.sub("_", name).lower()


def convert_schema(
    row: ProviderDataType,
    new_schema: Type[DataType],
    mapping: Dict[str, str],
    processors: Optional[Dict[str, Callable]] = None,
):
    mapped_fields = {
        value: process(row, key, processors) for key, value in mapping.items()
    }
    return new_schema.parse_obj(mapped_fields)


def check_alias(field) -> bool:
    "Checks if a field has an alias."
    alias = getattr(field, "alias")
    name = getattr(field, "name")
    return alias != name


def data_transformer(
    data: Union[List[ProviderDataType], ProviderDataType],
    new_schema: Type[DataType],
    processors: Optional[Dict[str, Callable]] = None,
) -> List[DataType]:
    """Converts a specific data into the standardised version

    Parameters:
    -----------
    data: Union[List[ProviderDataType], ProviderDataType]
        A list of pydantic schemas

    new_schema: DataType
        The standardised pydantic schema

    processors: Optional[Dict[str, str]]
        A dictionary with fields and custom processing functions

    Returns:
    --------
    List[DataType]
        A list of the newly formatted schemas

    """
    the_data = data[0] if isinstance(data, list) else data
    fields = the_data.__dict__.keys()
    final_mapping = {x: camel_to_snake(x) for x in fields}
    mapping = {
        attr: field.alias
        for attr, field in the_data.__fields__.items()
        if check_alias(field)
    }
    if mapping:
        for key, value in mapping.items():
            final_mapping[key] = value
    if not isinstance(data, list):
        return convert_schema(data, new_schema, final_mapping, processors)
    new_data = []
    for row in data:
        schema = convert_schema(row, new_schema, final_mapping, processors)
        new_data.append(schema)
    return new_data


class BasicResponse:
    def __init__(self, response: StringIO):
        # Find a way to get the status code
        self.status_code = 200
        response.seek(0)
        self.text = response.read()

    def json(self) -> dict:
        return json.loads(self.text)


def request(url: str) -> BasicResponse:
    """
    Request function for PyScript. Pass in Method and make sure to await!
    Parameters:
    -----------
    url: str
        URL to make request to

    Return:
    -------
    response: BasicRequest
        BasicRequest object with status_code and text attributes
    """
    # pylint: disable=import-outside-toplevel
    from pyodide.http import open_url

    response = open_url(url)
    return BasicResponse(response)
