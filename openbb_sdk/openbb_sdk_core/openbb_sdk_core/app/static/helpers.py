"""Helpers for the OpenBB static generation."""
from openbb_sdk_core.app.provider_interface import get_provider_interface


def get_docstrings(query_mapping: dict) -> dict:
    """Get docstrings from the query mapping.

    Parameter
    ---------
        query_mapping (dict): The query mapping.

    Returns
    -------
        dict: A dictionary with the docstrings.
    """
    for _, provider_mapping in query_mapping.items():
        for _, query_params_mapping in provider_mapping.items():
            query_params_mapping.pop("fields", None)
    return query_mapping


def generate_provider_docstrings(docstring: str, docstring_mapping: dict) -> str:
    """Generate the docstring for the provider.

    Parameter
    ----------
        docstring (str): The docstring.
        docstring_mapping (dict): The docstring mapping.

    Returns
    -------
        str: The final docstring.
    """
    for provider, provider_mapping in docstring_mapping.items():
        docstring += f"\n{provider}"
        docstring += f"\n{'-' * len(provider)}"
        for _, section_docstring in provider_mapping.items():
            # TODO: Clean the provider specific docstring from standard fields
            section_docstring = (
                section_docstring["docstring"]
                if section_docstring["docstring"]
                else "\n    Returns\n-------\n    Documentation not available.\n\n"
            )

            # clean the docstring from its original indentation
            if (
                "\n    Returns\n-------\n    Documentation not available.\n\n"  # noqa: SIM300
                != section_docstring
            ):
                # re
                section_docstring = "\n".join(
                    line[4:] for line in section_docstring.split("\n")[1:]
                )
                section_docstring = "\n".join(
                    f"    {line}" for line in section_docstring.split("\n")
                )
            docstring += f"\n{section_docstring}"

    return docstring


def generate_command_docstring(func, query_name: str):
    """Generate the docstring for the command.

    Parameter
    ----------
        func (function): The command function.
        query_name (str): The query name.

    Returns
    -------
        function: The function with the updated docstring.
    """
    provider_interface_mapping = get_provider_interface().map

    query_mapping = provider_interface_mapping.get(query_name, None)
    if query_mapping:
        # call the get_docstrings function
        docstring_mapping = get_docstrings(query_mapping)

        docstring = func.__doc__ or ""

        available_providers = ", ".join(docstring_mapping.keys())
        available_providers = available_providers.replace("openbb, ", "")

        docstring += f"\n\nAvailable providers: {available_providers}\n"

        docstring_mapping = {
            "Standard": docstring_mapping.pop("openbb", None),  # type: ignore
            **docstring_mapping,
        }

        docstring = generate_provider_docstrings(docstring, docstring_mapping)

        func.__doc__ = docstring
    return func
