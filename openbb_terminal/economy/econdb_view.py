""" EconDB View """
__docformat__ = "numpy"
# pylint:disable=too-many-arguments
import logging
import os
from textwrap import fill
from typing import List, Optional

from matplotlib import pyplot as plt

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy import econdb_model
from openbb_terminal.helper_funcs import export_data, plot_autoscale, print_rich_table

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def show_macro_data(
    parameters: Optional[list] = None,
    countries: Optional[list] = None,
    transform: str = "",
    start_date: str = "1900-01-01",
    end_date: Optional[str] = None,
    symbol: str = "",
    raw: bool = False,
    external_axes: Optional[List[plt.axes]] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Show the received macro data about a company [Source: EconDB]

    Parameters
    ----------
    parameters: list
        The type of data you wish to display. Available parameters can be accessed through get_macro_parameters().
    countries : list
        The selected country or countries. Available countries can be accessed through get_macro_countries().
    transform : str
        select data transformation from:
            '' - no transformation
            'TPOP' - total percentage change on period,
            'TOYA' - total percentage since 1 year ago,
            'TUSD' - level USD,
            'TPGP' - Percentage of GDP,
            'TNOR' - Start = 100
    start_date : str
        The starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31.
    end_date : Optional[str]
        The end date, format "YEAR-MONTH-DAY", i.e. 2020-06-05.
    symbol : str
        In what currency you wish to convert all values.
    raw : bool
        Whether to display the raw output.
    external_axes: Optional[List[plt.axes]]
        External axes to plot on
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file

    Returns
    -------
    Plots the Series.
    """

    if parameters is None:
        parameters = ["CPI"]
    if countries is None:
        countries = ["United_States"]

    df_rounded, units, denomination = econdb_model.get_aggregated_macro_data(
        parameters, countries, transform, start_date, end_date, symbol
    )

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        ax = external_axes[0]

    legend = []
    for column in df_rounded.columns:
        if transform:
            if transform in ["TPOP", "TOYA", "TPGP"]:
                parameter_units = "Units: %"
            elif transform in ["TUSD", "TNOR"]:
                parameter_units = "Units: Level"
        else:
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
            [fill(label.title(), 45) for label in legend],
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
            sheet_name,
        )

    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()


@log_start_end(log=logger)
def show_treasuries(
    instruments: Optional[list] = None,
    maturities: Optional[list] = None,
    frequency: str = "monthly",
    start_date: str = "1900-01-01",
    end_date: Optional[str] = None,
    raw: bool = False,
    external_axes: Optional[List[plt.axes]] = None,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Display U.S. Treasury rates [Source: EconDB]

    Parameters
    ----------
    instruments: list
        Type(s) of treasuries, nominal, inflation-adjusted or secondary market.
        Available options can be accessed through economy.treasury_maturities().
    maturities : list
        Treasury maturities to display. Available options can be accessed through economy.treasury_maturities().
    frequency : str
        Frequency of the data, this can be daily, weekly, monthly or annually
    start_date : str
        Starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31.
    end_date : Optional[str]
        End date, format "YEAR-MONTH-DAY", i.e. 2020-06-05.
    raw : bool
        Whether to display the raw output.
    external_axes: Optional[List[plt.axes]]
        External axes to plot on
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file

    Returns
    -------
    Plots the Treasury Series.
    """

    if instruments is None:
        instruments = ["nominal"]
    if maturities is None:
        maturities = ["10y"]

    treasury_data = econdb_model.get_treasuries(
        instruments, maturities, frequency, start_date, end_date
    )

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        ax = external_axes[0]

    for col in treasury_data.columns:
        col_label = col.split("_")
        ax.plot(treasury_data[col], label=f"{col_label[0]} [{col_label[1]}]")

    ax.set_title("U.S. Treasuries")
    ax.set_ylabel("Yield (%)")
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

    if raw:
        print_rich_table(
            treasury_data.iloc[-10:],
            headers=list(treasury_data.columns),
            show_index=True,
            title="U.S. Treasuries",
        )

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "treasuries_data",
            treasury_data / 100,
            sheet_name,
        )


@log_start_end(log=logger)
def show_treasury_maturities():
    """Get treasury maturity options [Source: EconDB]

    Returns
    -------
    A table containing the instruments and maturities.
    """

    instrument_maturities = econdb_model.get_treasury_maturities()

    print_rich_table(
        instrument_maturities,
        headers=list(["Maturities"]),
        show_index=True,
        index_name="Instrument",
        title="Maturity options per instrument",
    )
