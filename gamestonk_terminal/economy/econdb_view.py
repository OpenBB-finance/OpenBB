""" EconDB View """
__docformat__ = "numpy"

import logging
from typing import Optional, List, Dict, Any

import pandas as pd
from matplotlib import pyplot as plt

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.economy import econdb_model
from gamestonk_terminal.helper_funcs import plot_autoscale, print_rich_table
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def show_macro_data(
    parameters: list,
    countries: list,
    start_date: int = None,
    end_date: int = None,
    convert_currency: str = "USD",
    raw: bool = False,
    external_axes: Optional[List[plt.axes]] = None,
    export: str = "",
):
    """Show the received nacro data about a company [Source: EconDB]

    Parameters
    ----------
    parameters: list
        The type of data you wish to acquire
    countries : list
       the selected country or countries
    start_date : str
        The starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31.
    end_date : str
        The end date, format "YEAR-MONTH-DAY", i.e. 2020-06-05.
    convert_currency : str
        In what currency you wish to convert all values.
    raw : bool
        Whether to display the raw output.
    external_axes: Optional[List[plt.axes]]
        External axes to plot on
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file

    Returns
    ----------
    Plots the Series.
    """
    country_data: Dict[Any, Dict[Any, pd.Series]] = {}

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        ax = external_axes[0]

    for country in countries:
        country_data[country] = {}
        for parameter in parameters:
            country_data[country][parameter] = econdb_model.get_macro_data(
                parameter, country, convert_currency
            )

            if country_data[country][parameter] is not None and start_date or end_date:
                country_data[country][parameter] = country_data[country][parameter].loc[
                    start_date:end_date
                ]

    df = pd.DataFrame.from_dict(country_data, orient="index").stack().to_frame()
    df = pd.DataFrame(df[0].values.tolist(), index=df.index).T

    maximum_value = df.max().max()

    if maximum_value > 1_000_000_000:
        df_rounded = df / 1_000_000_000
        denomination = f"[{convert_currency} Billions]"
    elif maximum_value > 1_000_000:
        df_rounded = df / 1_000_000
        denomination = f"[{convert_currency} Millions]"
    elif maximum_value > 1_000:
        df_rounded = df / 1_000
        denomination = f"[{convert_currency} Thousands]"
    else:
        df_rounded = df
        denomination = f"[{convert_currency}]"

    for column in df_rounded.columns:
        country_label = column[0].replace("_", " ")
        parameter_label = econdb_model.PARAMETERS[column[1]]
        if len(parameters) > 1 and len(countries) > 1:
            ax.plot(df_rounded[column], label=f"{country_label} [{parameter_label}]")
            ax.set_title(f"Macro data {denomination}")
            ax.legend()
        elif len(parameters) > 1:
            ax.plot(df_rounded[column], label=parameter_label)
            ax.set_title(f"{country_label} {denomination}")
            ax.legend()
        elif len(countries) > 1:
            ax.plot(df_rounded[column], label=column[0])
            ax.set_title(f"{parameter_label} {denomination}")
            ax.legend()
        else:
            ax.plot(df_rounded[column])
            ax.set_title(f"{parameter_label} of {country_label} {denomination}")

    if raw:
        print_rich_table(
            df_rounded.fillna("-").iloc[-10:],
            headers=list(df_rounded.columns),
            show_index=True,
            title=f"Macro Data {denomination}",
        )

    if export:
        print("Doing nothing!")

    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()


@log_start_end(log=logger)
def show_treasuries(
    types: list,
    maturities: list,
    frequency: str,
    start_date: str = None,
    end_date: str = None,
    raw: bool = False,
    external_axes: Optional[List[plt.axes]] = None,
    export: str = "",
):
    """Obtain U.S. Treasury Rates [Source: EconDB]

    Parameters
    ----------
    types: list
        The type(s) of treasuries, nominal, inflation-adjusted or secondary market.
    maturities : list
       the maturities you wish to view.
    frequency : str
        The frequency of the data, this can be daily, weekly, monthly or annually
    start_date : str
        The starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31.
    end_date : str
        The end date, format "YEAR-MONTH-DAY", i.e. 2020-06-05.
    raw : bool
        Whether to display the raw output.
    external_axes: Optional[List[plt.axes]]
        External axes to plot on
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file

    Returns
    ----------
    Plots the Treasury Series.
    """
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        ax = external_axes[0]

    treasury_data = econdb_model.get_treasuries(
        types, maturities, frequency, start_date, end_date
    )

    for treasury, maturities_data in treasury_data.items():
        for maturity in maturities_data:
            ax.plot(maturities_data[maturity], label=f"{treasury} [{maturity}]")

    ax.set_title("U.S. Treasuries")
    ax.legend()

    if raw:
        df = pd.DataFrame.from_dict(treasury_data, orient="index").stack().to_frame()
        df = pd.DataFrame(df[0].values.tolist(), index=df.index).T

        print_rich_table(
            df.iloc[-10:],
            headers=list(df.columns),
            show_index=True,
            title="U.S. Treasuries",
        )

    if export:
        print("Doing nothing!")

    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()


@log_start_end(log=logger)
def show_treasury_maturities(treasuries: Dict):
    """Obtain treasury maturity options [Source: EconDB]

    Parameters
    ----------
    treasuries: dict
        A dictionary containing the options structured {instrument : {maturities: {abbreviation : name}}}

    Returns
    ----------
    A table containing the instruments and maturities.
    """

    instrument_maturities = econdb_model.obtain_treasury_maturities(treasuries)

    print_rich_table(
        instrument_maturities,
        headers=list(["Maturities"]),
        show_index=True,
        index_name="Instrument",
        title="Maturity options per instrument",
    )

    console.print()
