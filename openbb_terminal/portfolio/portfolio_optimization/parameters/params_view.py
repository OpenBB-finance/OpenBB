import pandas as pd

from openbb_terminal.helper_funcs import print_rich_table


def show_arguments(arguments, description=None):
    """
    Show the available arguments and the choices you have for each. If available, also show
    the description of the argument.

    Parameters
    ----------
    arguments: Dictionary
        A dictionary containing the keys and the possible values.
    description: Dictionary
        A dictionary containing the keys equal to arguments and the descriptions.

    Returns
    -------
    A table containing the parameter names, possible values and (if applicable) the description.
    """
    adjusted_arguments = {}

    for variable in arguments:
        if len(arguments[variable]) > 15:
            minimum = min(arguments[variable])
            maximum = max(arguments[variable])
            adjusted_arguments[variable] = (
                f"Between {minimum} and {maximum} in steps of "
                f"{maximum / sum(x > 0 for x in arguments[variable])}"
            )
        else:
            adjusted_arguments[variable] = ", ".join(arguments[variable])

    if description:
        df = pd.DataFrame([adjusted_arguments, description]).T
        columns = ["Options", "Description"]
    else:
        df = pd.DataFrame([adjusted_arguments]).T
        columns = ["Options"]

    df = df[df.index != "technique"]

    print_rich_table(
        df, headers=list(columns), show_index=True, index_name="Parameters"
    )
