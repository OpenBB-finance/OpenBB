from typing import Dict, List

from openbb_terminal.stocks.screener import finviz_view


def finviz_choices(section: str) -> List[str]:
    """Generates the available choices for the given section. Formatted in an argparse friendly way

    Parameters
    ----------
    section: str
        The section to generate the choices for

    Returns
    -------
    List[str]
        The argparse friendly strings
    """
    return [x.replace(" ", "").lower() for x in finviz_view.d_cols_to_sort[section]]


def finviz_map(section: str) -> Dict[str, str]:
    """Generates a mapping of our custom formatted choices to the actual choices

    Parameters
    ----------
    section: str
        The section to generate the choices for

    Returns
    -------
    Dict[str]
        Keys are the arpgarse friendly version, values are the original version
    """
    return {x.replace(" ", "").lower(): x for x in finviz_view.d_cols_to_sort[section]}
