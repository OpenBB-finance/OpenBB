""" EconDB View """
__docformat__ = "numpy"
# pylint:disable=too-many-arguments
from datetime import datetime
import logging
import os
from textwrap import fill
from typing import Optional, List, Dict

import pandas as pd
from matplotlib import pyplot as plt

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.economy import econdb_model
from gamestonk_terminal.helper_funcs import (
    plot_autoscale,
    print_rich_table,
    export_data,
)
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def show_macro_data(
    parameters: list,
    countries: list,
    start_date: str = "1900-01-01",
    end_date=datetime.today().date(),
    convert_currency=False,
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
    country_data_df, units = econdb_model.get_aggregated_macro_data(
        parameters, countries, start_date, end_date, convert_currency
    )

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        ax = external_axes[0]

    maximum_value = country_data_df.max().max()

    if maximum_value > 1_000_000_000_000:
        df_rounded = country_data_df / 1_000_000_000_000
        denomination = " [in Trillions]"
    elif maximum_value > 1_000_000_000:
        df_rounded = country_data_df / 1_000_000_000
        denomination = " [in Billions]"
    elif maximum_value > 1_000_000:
        df_rounded = country_data_df / 1_000_000
        denomination = " [in Millions]"
    elif maximum_value > 1_000:
        df_rounded = country_data_df / 1_000
        denomination = " [in Thousands]"
    else:
        df_rounded = country_data_df
        denomination = ""

    legend = []
    for column in df_rounded.columns:
        parameter_units = f"Units: {units[column[0]][column[1]]}"
        country_label = column[0].replace("_", " ")
        parameter_label = econdb_model.PARAMETERS[column[1]]["name"]
        if len(parameters) > 1 and len(countries) > 1:
            ax.plot(df_rounded[column])
            ax.set_title(f"Macro data{denomination}", wrap=True, fontsize=12)
            legend.append(f"{country_label} [{parameter_label}, {parameter_units}]")
        elif len(parameters) > 1:
            ax.plot(df_rounded[column])
            ax.set_title(f"{country_label}{denomination}", wrap=True, fontsize=12)
            legend.append(f"{parameter_label} [{parameter_units}]")
        elif len(countries) > 1:
            ax.plot(df_rounded[column])
            ax.set_title(f"{parameter_label}{denomination}", wrap=True, fontsize=12)
            legend.append(f"{country_label} [{parameter_units}]")
        else:
            ax.plot(df_rounded[column])
            ax.set_title(
                f"{parameter_label} of {country_label}{denomination} [{parameter_units}]",
                wrap=True,
                fontsize=12,
            )

    if len(parameters) > 1 or len(countries) > 1:
        ax.legend(
            [fill(label, 45) for label in legend],
            bbox_to_anchor=(0, 0.40, 1, -0.52),
            loc="upper right",
            mode="expand",
            prop={"size": 9},
            ncol=2,
        )

    df_rounded.columns = ["_".join(column) for column in df_rounded.columns]

    if raw:
        print_rich_table(
            df_rounded.fillna("-").iloc[-10:],
            headers=list(df_rounded.columns),
            show_index=True,
            title=f"Macro Data {denomination}",
        )

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "macro_data",
            df_rounded,
        )

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
    store : bool
        Whether to prevent plotting the data.
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

    treasury_data = econdb_model.get_treasuries(
        types, maturities, frequency, start_date, end_date
    )

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        ax = external_axes[0]

    for treasury, maturities_data in treasury_data.items():
        for maturity in maturities_data:
            ax.plot(maturities_data[maturity], label=f"{treasury} [{maturity}]")

    ax.set_title("U.S. Treasuries")
    ax.legend(
        bbox_to_anchor=(0, 0.40, 1, -0.52),
        loc="upper right",
        mode="expand",
        borderaxespad=0,
        prop={"size": 9},
        ncol=3,
    )

    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()

    df = pd.DataFrame.from_dict(treasury_data, orient="index").stack().to_frame()
    df = pd.DataFrame(df[0].values.tolist(), index=df.index).T
    df.columns = ["_".join(column) for column in df.columns]

    if raw:
        print_rich_table(
            df.iloc[-10:],
            headers=list(df.columns),
            show_index=True,
            title="U.S. Treasuries",
        )

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "treasuries_data",
            df,
        )


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
