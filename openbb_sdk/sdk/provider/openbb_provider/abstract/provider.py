"""Abstract class for providers."""


from typing import Any, Dict, List, Literal, Optional

import pkg_resources


def build_provider_name():
    """Build the provider name Literal from the entry points."""
    extension_names = []

    for entry_point in pkg_resources.iter_entry_points("openbb_provider_extension"):
        extension_names.append(entry_point.name)

    literal_values = ()
    for extension_name in extension_names:
        literal_values += (extension_name,)

    provider_name = Literal[literal_values]  # type: ignore

    return provider_name


ProviderName = build_provider_name()


class ProviderNameType(type):
    """Metaclass for ProviderName."""

    __args__ = ProviderName.__args__
    __str__ = ProviderName.__str__

    def __new__(mcs, value):
        """Override __new__ to check if value is a valid provider name."""
        return value

    def __init__(cls, value):
        if value not in ProviderName.__args__:
            raise ValueError(f"{value} is not a valid provider name.")
        cls.value = value

    def __getstate__(cls):
        """Override __getstate__ to return the value of the provider name."""
        return cls.value

    def __setstate__(cls, state):
        """Override __setstate__ to set the value of the provider name."""
        cls.value = state

    def __repr__(cls):
        """Override __repr__ to return the value of the provider name."""
        return f"ProviderName({cls.value})"


class Provider:
    """Abstract class for providers."""

    QUERIES = ["get_query_type", "get_provider_query_type"]

    def __init__(
        self,
        name: ProviderNameType,
        description: str,
        fetcher_list: List[Any],
        # credentials: bool,
        required_credentials: Optional[List[str]],
    ) -> None:
        self.name = name
        self.description = description
        # self.credentials = credentials
        self.required_credentials = required_credentials
        the_dict: Dict[str, Any] = {}
        for query in self.QUERIES:
            the_dict[query] = {getattr(x, query)().__name__: x for x in fetcher_list}
        self.fetcher_dict = the_dict
        # This is used only for documentation generation
        self.fetcher_list = fetcher_list
