"""Create a detailed Map of the Provider Registry."""
from typing import Dict, Tuple

from openbb_provider.registry import provider_registry


def _get_data_type(fetcher) -> str:
    """Get the data type of the fetcher."""
    data_type = (
        str(fetcher.get_data_type())  # pylint: disable=use-maxsplit-arg
        .split(".")[-1]
        .replace("]", "")
        .replace("'>", "")
    )
    return data_type


def _get_query_type(fetcher) -> str:
    """Get the query type of the fetcher."""
    query_type = (
        str(fetcher.get_query_type())  # pylint: disable=use-maxsplit-arg
        .split(".")[-1]
        .replace("'>", "")
    )
    return query_type


def _get_data_fields(fetcher) -> Tuple[Dict, Dict]:
    """Get the standard and provider-specific data fields of the fetcher.

    Parameters
    ----------
    fetcher : Fetcher
        The fetcher to get the data fields from.

    Returns
    -------
    Tuple[Dict, Dict]
        A tuple of the provider-specific and standardized data fields.
    """
    try:
        provider_fields = (fetcher.get_provider_data_type()).__fields__
    except AttributeError:
        provider_fields = (fetcher.get_provider_data_type().__args__[0]).__fields__
    try:
        standard_fields = (fetcher.get_data_type()).__fields__
    except AttributeError:
        standard_fields = (fetcher.get_data_type().__args__[0]).__fields__

    return provider_fields, standard_fields


def _extract_fields(
    provider_fields: Dict,
    standard_fields: Dict,
) -> Tuple[Dict, Dict]:
    """Extract the fields and their details from pydantic models.

    Parameters
    ----------
    provider_fields : Dict
        The fields of the provider pydantic model.
    standard_fields : Dict
        The fields of the standardized pydantic model.

    Returns
    -------
    Tuple[Dict, Dict]
        A tuple of the provider fields and standardized fields.
    """
    provider_dict: Dict = {}
    standard_dict: Dict = {}

    for field in provider_fields:
        provider_dict[provider_fields[field].alias] = {
            "type": provider_fields[field].annotation,
            "default": provider_fields[field].default,
            "required": provider_fields[field].required,
        }

    for field in standard_fields:
        standard_dict[standard_fields[field].alias] = {
            "type": standard_fields[field].annotation,
            "default": standard_fields[field].default,
            "required": standard_fields[field].required,
        }

    return provider_dict, standard_dict


def build_query_params_mapping() -> Dict:
    """Build a mapping of the provider registry QueryParams.

    Returns
    -------
    Dict :
        The mapping is a nested dictionary with the following structure:
        {
            "QueryParamsType": {
                "provider_name": {
                        "param_name": {
                            "type": "param_type",
                            "default": "param_default",
                            "required": "param_required"
                        }
                    }
                "openbb": {
                        "param_name": {
                            "type": "param_type",
                            "default": "param_default",
                            "required": "param_required"
                        }
                    }
            }
        }
    """
    provider_registry_mapping = provider_registry.providers
    mapping = {}
    for provider in provider_registry_mapping.values():
        for fetcher in provider.fetcher_list:
            provider_name = provider.name

            query_type = _get_query_type(fetcher)

            provider_param_fields = (fetcher.get_provider_query_type()).__fields__
            standard_param_fields = (fetcher.get_query_type()).__fields__

            provider_specific_query_params, standardized_query_params = _extract_fields(
                provider_param_fields,
                standard_param_fields,
            )

            if query_type not in mapping:
                mapping[query_type] = {provider_name: provider_specific_query_params}
                mapping[query_type]["openbb"] = standardized_query_params  # type: ignore
            else:
                mapping[query_type][provider_name] = provider_specific_query_params

    return mapping


def build_data_mapping() -> Dict:
    """Build a mapping of the provider registry Data.

    Returns
    -------
    Dict :
        The mapping is a nested dictionary with the following structure:
        {
            "DataType": {
                "provider_name": {
                        "data_field_name": {
                            "type": "param_type",
                            "default": "param_default",
                            "required": "param_required"
                        }
                    }
                "openbb": {
                        "data_field_name": {
                            "type": "param_type",
                            "default": "param_default",
                            "required": "param_required"
                        }
                    }
            }
        }
    """
    provider_registry_mapping = provider_registry.providers
    mapping = {}
    for provider in provider_registry_mapping.values():
        for fetcher in provider.fetcher_list:
            provider_name = provider.name

            data_type = _get_data_type(fetcher)

            provider_data_fields, standard_data_fields = _get_data_fields(fetcher)

            provider_specific_data_fields, standardized_data_fields = _extract_fields(
                provider_data_fields,
                standard_data_fields,
            )

            if data_type not in mapping:
                mapping[data_type] = {provider_name: provider_specific_data_fields}
                mapping[data_type]["openbb"] = standardized_data_fields  # type: ignore
            else:
                mapping[data_type][provider_name] = provider_specific_data_fields

    return mapping


def _get_data_docstring(fetcher) -> Tuple[str, str]:
    """Get the data docstring of the fetcher for the provider and standardized data.

    Parameters
    ----------
    fetcher : Fetcher
        The fetcher to get the data docstring from.

    Returns
    -------
    Tuple[str, str]
        A tuple of the provider and standardized data docstrings.
    """
    provider_data_docstring = (fetcher.get_provider_data_type()).__doc__
    if not provider_data_docstring:
        try:
            provider_data_docstring = (
                fetcher.get_provider_data_type().__args__[0]
            ).__doc__
        except AttributeError:
            provider_data_docstring = ""

    standard_data_docstring = (fetcher.get_data_type()).__doc__
    if not standard_data_docstring:
        try:
            standard_data_docstring = (fetcher.get_data_type().__args__[0]).__doc__
        except AttributeError:
            standard_data_docstring = ""

    return provider_data_docstring, standard_data_docstring


def build_docstring_mapping() -> Dict:
    """Build a mapping of the provider registry docstrings.

    Returns
    -------
    Dict :
        The mapping is a nested dictionary with the following structure:
        {
            "DataType": {
                "provider_name": "docstring",
                "openbb": "docstring"
            },
            "QueryParamsType": {
                "provider_name": "docstring",
                "openbb": "docstring"
            }
        }
    """
    mapping = {}
    provider_registry_mapping = provider_registry.providers
    for provider in provider_registry_mapping.values():
        for fetcher in provider.fetcher_list:
            provider_name = provider.name

            data_type = _get_data_type(fetcher)
            query_type = _get_query_type(fetcher)

            provider_query_docstring = (fetcher.get_provider_query_type()).__doc__
            standard_query_docstring = (fetcher.get_query_type()).__doc__

            provider_data_docstring, standard_data_docstring = _get_data_docstring(
                fetcher
            )

            if data_type not in mapping:
                mapping[data_type] = {
                    provider_name: provider_data_docstring,
                    "openbb": standard_data_docstring,
                }
            else:
                mapping[data_type][provider_name] = provider_data_docstring

            if query_type not in mapping:
                mapping[query_type] = {
                    provider_name: provider_query_docstring,
                    "openbb": standard_query_docstring,
                }
            else:
                mapping[query_type][provider_name] = provider_query_docstring

    return mapping


def build_provider_mapping() -> Dict:
    """Build a mapping of the provider registry.

    Returns
    -------
    Dict :
        The mapping is a nested dictionary of data and query mappings.
    """
    mapping: Dict = {}
    data_mapping = build_data_mapping()
    query_mapping = build_query_params_mapping()
    docstring_mapping = build_docstring_mapping()

    for query_type, providers in query_mapping.items():
        query_type_name = query_type.replace("QueryParams", "")
        mapping[query_type_name] = {}
        for provider, fields in providers.items():
            mapping[query_type_name][provider] = {
                "QueryParams": {},
                "Data": {},
            }
            mapping[query_type_name][provider]["QueryParams"] = {
                "fields": fields,
                "docstring": docstring_mapping[query_type][provider],
            }

    for data_type, providers in data_mapping.items():
        data_type_name = data_type.replace("Data", "")

        for provider, fields in providers.items():
            mapping[data_type_name][provider]["Data"] = {
                "fields": fields,
                "docstring": docstring_mapping[data_type][provider],
            }

    return mapping


provider_mapping = build_provider_mapping()
