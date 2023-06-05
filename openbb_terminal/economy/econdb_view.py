""" EconDB View """
__docformat__ = "numpy"
# pylint:disable=too-many-arguments,unused-argument
import logging
import os
from typing import Optional, Union

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy import econdb_model
from openbb_terminal.helper_funcs import export_data, print_rich_table

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
    external_axes: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    limit: int = 10,
) -> Union[OpenBBFigure, None]:
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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
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

    fig = OpenBBFigure(yaxis=dict(side="right"))

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
            fig.add_scatter(
                x=df_rounded.index,
                y=df_rounded[column],
                mode="lines",
                name=f"{country_label} [{parameter_label}, {parameter_units}]",
            )
            fig.set_title(f"Macro data{denomination}")
        elif len(parameters) > 1:
            fig.add_scatter(
                x=df_rounded.index,
                y=df_rounded[column],
                mode="lines",
                name=f"{parameter_label} [{parameter_units}]",
            )
            fig.set_title(f"{country_label}{denomination}")
        elif len(countries) > 1:
            fig.add_scatter(
                x=df_rounded.index,
                y=df_rounded[column],
                mode="lines",
                name=f"{country_label} [{parameter_units}]",
            )
            fig.set_title(f"{parameter_label}{denomination}")
        else:
            fig.add_scatter(
                x=df_rounded.index,
                y=df_rounded[column],
                mode="lines",
                name=f"{country_label} [{parameter_label}, {parameter_units}]",
            )
            fig.set_title(
                f"{parameter_label} of {country_label}{denomination} [{parameter_units}]"
            )

    df_rounded.columns = ["_".join(column) for column in df_rounded.columns]

    if raw:
        # was a -iloc so we need to flip the index as we use head
        df_rounded = df_rounded.sort_index(ascending=False)
        print_rich_table(
            df_rounded.fillna("-"),
            headers=list(df_rounded.columns),
            show_index=True,
            title=f"Macro Data {denomination}",
            export=bool(export),
            limit=limit,
        )

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "macro_data",
            df_rounded,
            sheet_name,
            fig,
        )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
def show_treasuries(
    instruments: Optional[list] = None,
    maturities: Optional[list] = None,
    frequency: str = "monthly",
    start_date: str = "1900-01-01",
    end_date: Optional[str] = None,
    raw: bool = False,
    external_axes: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
    limit: int = 10,
) -> Union[OpenBBFigure, None]:
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
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
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
    fig = OpenBBFigure(
        yaxis=dict(side="right", title="Yield (%)"),
        title="U.S. Treasuries",
    )

    for col in treasury_data.columns:
        col_label = col.split("_")
        fig.add_scatter(
            x=treasury_data.index,
            y=treasury_data[col],
            mode="lines",
            name=f"{col_label[0]} [{col_label[1]}]",
        )

    if raw:
        # was a -iloc so we need to flip the index as we use head
        treasury_data = treasury_data.sort_index(ascending=False)
        print_rich_table(
            treasury_data,
            headers=list(treasury_data.columns),
            show_index=True,
            title="U.S. Treasuries",
            export=bool(export),
            limit=limit,
        )

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "treasuries_data",
            treasury_data / 100,
            sheet_name,
            fig,
        )

    return fig.show(external=raw or external_axes)


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
