""" OECD view """
__docformat__ = "numpy"

# IMPORTATION STANDARD
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy import oecd_model
from openbb_terminal.helper_funcs import console, export_data, print_rich_table

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments, too-many-function-args


YAXIS_TITLES = {
    "AGRWTH": "Annual Growth Rate (%)",
    "IDX": "Index (Base = 2015)",
    "IDX2015": "Index (Base = 2015)",
    "USD": "Nominal Value in USD",
    "PC_CHGPY": "Same Quarter of the Previous Year (% Change)",
    "PC_CHGPP": "Previous Quarter (% Change)",
    "PC_GDP": "Percentage of GDP (%)",
    "THND_USD_CAP": "Thousands of USD per Capita",
    "USD_CAP": "USD per Capita",
}


@log_start_end(log=logger)
def plot_gdp(
    countries: Optional[str] = "united_states",
    units: str = "USD",
    start_date: str = "",
    end_date: str = "",
    raw: bool = False,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """
    Gross domestic product (GDP) is the standard measure of the value added created
    through the production of goods and services in a country during a certain period.
    As such, it also measures the income earned from that production, or the total amount
    spent on final goods and services (less imports). While GDP is the single most important
    indicator to capture economic activity, it falls short of providing a suitable measure of
    people's material well-being for which alternative indicators may be more appropriate.
    This indicator is based on nominal GDP (also called GDP at current prices or GDP in value)
    and is available in different measures: US dollars and US dollars per capita (current PPPs).
    All OECD countries compile their data according to the 2008 System of National Accounts (SNA).
    This indicator is less suited for comparisons over time, as developments are not only caused
    by real growth, but also by changes in prices and PPPs. [Source: OECD]

    Parameters
    ----------
    countries: list
        List of countries to get data for
    units: str
        Units to get data in. Either 'USD' or 'USD_CAP'.
        Default is US dollars per capita.
    start_date: str
        Start date of data, in YYYY-MM-DD format
    end_date: str
        End date of data, in YYYY-MM-DD format
    raw: bool
        Whether to display raw data in a table
    export: str
        Format to export data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    external_axes: bool, optional
        Whether to return the figure object or not, by default False

    Returns
    -------
    Union[OpenBBFigure, None]
        OpenBBFigure object if external_axes is True, else None (opens plot in a window)
    """
    countries = [countries] if isinstance(countries, str) else countries  # type: ignore[assignment]

    if units not in ["USD", "USD_CAP"]:
        console.print(
            "Invalid choice, choices are either USD or USD_CAP. Defaulting to USD."
        )
        units = "USD"

    df = oecd_model.get_gdp(countries, units, start_date, end_date)

    if df.empty:
        return None

    fig = OpenBBFigure(yaxis_title=YAXIS_TITLES[units])

    for country in df.columns:
        fig.add_scatter(
            x=df.index,
            y=df[country],
            name=country.replace("_", " ").title(),
            mode="lines",
            line_width=2.5,
            showlegend=True,
        )

    title = "Nominal Gross Domestic Product (USD)"
    title = title + " Per Capita" if units == "USD_CAP" else title
    fig.set_title(title)

    if raw:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=True,
            title=title,
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"nominal_gdp_{units}",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
def plot_real_gdp(
    countries: Optional[List[str]],
    units: str = "PC_CHGPY",
    start_date: str = "",
    end_date: str = "",
    raw: bool = False,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """
    Gross domestic product (GDP) is the standard measure of the value added
    created through the production of goods and services in a country during
    a certain period. As such, it also measures the income earned from that
    production, or the total amount spent on final goods and services (less imports).
    While GDP is the single most important indicator to capture economic activity, it
    falls short of providing a suitable measure of people's material well-being for
    which alternative indicators may be more appropriate. This indicator is based on
    real GDP (also called GDP at constant prices or GDP in volume), i.e. the developments
    over time are adjusted for price changes. The numbers are also adjusted for seasonal
    influences. The indicator is available in different measures: percentage change from
    the previous quarter, percentage change from the same quarter of the previous year and
    volume index (2015=100). All OECD countries compile their data according to the 2008
    System of National Accounts (SNA). [Source: OECD]

    Parameters
    ----------
    countries: list
        List of countries to get data for
    units: str
        Units to get data in. Either 'PC_CHGPP', 'PC_CHGPY' or 'IDX.
        Default is percentage change from the same quarter of the previous year.
    start_date: str
        Start date of data, in YYYY-MM-DD format
    end_date: str
        End date of data, in YYYY-MM-DD format
    raw: bool
        Whether to display raw data in a table
    export: str
        Format to export data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    external_axes: bool, optional
        Whether to return the figure object or not, by default False

    Returns
    -------
    Union[OpenBBFigure, None]
        OpenBBFigure object if external_axes is True, else None (opens plot in a window)
    """
    if units not in ["PC_CHGPP", "PC_CHGPY", "IDX"]:
        return console.print(
            "Use either PC_CHGPP (percentage change previous quarter), "
            "PC_CHGPY (percentage change from the same quarter of the "
            "previous year) or IDX (index with base at 2015) "
            "for units"
        )

    df = oecd_model.get_real_gdp(countries, units, start_date, end_date)

    if df.empty:
        return None

    kwargs: Dict[str, Any] = {"yaxis_title": YAXIS_TITLES[units]}

    if units == "PC_CHGPY":
        kwargs["yaxis_title_font_size"] = 14

    fig = OpenBBFigure(**kwargs)

    for country in df.columns:
        fig.add_scatter(
            x=df.index,
            y=df[country],
            name=country.replace("_", " ").title(),
            mode="lines",
            line_width=2.5,
            showlegend=True,
        )

    title = "Real Gross Domestic Product (GDP)"
    fig.set_title(title)

    if raw:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=True,
            title=title,
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"real_gdp_{units}",
        df if units == "IDX" else df / 100,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
def plot_gdp_forecast(
    countries: Optional[List[str]],
    types: str = "real",
    quarterly: bool = False,
    start_date: str = "",
    end_date: str = "",
    raw: bool = False,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """
    Real gross domestic product (GDP) is GDP given in constant prices and
    refers to the volume level of GDP. Constant price estimates of GDP are
    obtained by expressing values of all goods and services produced in a
    given year, expressed in terms of a base period. Forecast is based on an
    assessment of the economic climate in individual countries and the world economy,
    using a combination of model-based analyses and expert judgement. This indicator
    is measured in growth rates compared to previous year. [Source: OECD]

    Parameters
    ----------
    countries: list
        List of countries to get data for
    type: str
        Type of GDP to get data for. Either 'real' or 'nominal'.
        Default s real GDP (real).
    quarterly: bool
        Whether to get quarterly results.
    start_date: str
        Start date of data, in YYYY-MM-DD format
    end_date: str
        End date of data, in YYYY-MM-DD format
    raw: bool
        Whether to display raw data in a table
    export: str
        Format to export data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    external_axes: bool, optional
        Whether to return the figure object or not, by default False

    Returns
    -------
    Union[OpenBBFigure, None]
        OpenBBFigure object if external_axes is True, else None (opens plot in a window)
    """
    if types not in ["real", "nominal"]:
        return console.print("Use either 'real' or 'nominal' for type")

    units = "Q" if quarterly else "A"
    df = oecd_model.get_gdp_forecast(countries, types, units, start_date, end_date)

    if df.empty:
        return None

    fig = OpenBBFigure(yaxis_title="Growth rates Compared to Previous Year (%)")

    future_dates = df[
        df.index > str(datetime.now()) if units == "Q" else df.index >= datetime.now()
    ]
    for country in df.columns:
        fig.add_scatter(
            x=df.index,
            y=df[country],
            name=country.replace("_", " ").title(),
            mode="lines",
            line_width=2.5,
            showlegend=True,
        )

    if not future_dates.empty:
        fig.add_vrect(
            x0=future_dates.index[0],
            x1=future_dates.index[-1],
            annotation_text="Forecast",
            fillcolor="yellow",
            opacity=0.20,
            line_width=0,
        )

    title = (
        f"Forecast of {'Quarterly' if units == 'Q' else 'Annual'} "
        f"{'Real' if types == 'real' else 'Nominal'} Gross Domestic Product (GDP)"
    )
    fig.set_title(title, font_size=20)

    if raw:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=True,
            title=title,
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "forecast_gdp",
        df / 100,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
def plot_cpi(
    countries: Optional[List[str]],
    perspective: str = "TOT",
    frequency: str = "Q",
    units: str = "AGRWTH",
    start_date: str = "",
    end_date: str = "",
    raw: bool = False,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """
    Inflation measured by consumer price index (CPI) is defined as the change in the prices
    of a basket of goods and services that are typically purchased by specific groups of
    households. Inflation is measured in terms of the annual growth rate and in index,
    2015 base year with a breakdown for food, energy and total excluding food and energy.
    Inflation measures the erosion of living standards. A consumer price index is estimated
    as a series of summary measures of the period-to-period proportional change in the
    prices of a fixed set of consumer goods and services of constant quantity and
    characteristics, acquired, used or paid for by the reference population. Each summary
    measure is constructed as a weighted average of a large number of elementary aggregate indices.
    Each of the elementary aggregate indices is estimated using a sample of prices for a defined
    set of goods and services obtained in, or by residents of, a specific region from a given
    set of outlets or other sources of consumption goods and services. [Source: OECD]

    Parameters
    ----------
    countries: list
        List of countries to get data for
    perspective: str
        Type of CPI you wish to obtain. This can be ENRG (energy), FOOD (food),
        TOT (total) or TOT_FOODENRG (total excluding food and energy)
        Default is Total CPI.
    frequency: str
        Frequency to get data in. Either 'M', 'Q' or 'A.
        Default is Quarterly (Q).
    units: str
        Units to get data in. Either 'AGRWTH' (annual growth rate) or IDX2015 (base = 2015).
        Default is Annual Growth Rate (AGRWTH).
    start_date: str
        Start date of data, in YYYY-MM-DD format
    end_date: str
        End date of data, in YYYY-MM-DD format
    raw: bool
        Whether to display raw data in a table
    export: str
        Format to export data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    external_axes: bool, optional
        Whether to return the figure object or not, by default False

    Returns
    -------
    Union[OpenBBFigure, None]
        OpenBBFigure object if external_axes is True, else None (opens plot in a window)
    """
    df = oecd_model.get_cpi(
        countries, perspective, frequency, units, start_date, end_date
    )

    if df.empty:
        return None

    fig = OpenBBFigure(yaxis_title=YAXIS_TITLES[units])

    for country in df.columns:
        fig.add_scatter(
            x=df.index,
            y=df[country],
            name=country.replace("_", " ").title(),
            mode="lines",
            line_width=2.5,
            showlegend=True,
        )

    perspective_naming = {
        "FOOD": "Food",
        "ENRG": "Energy",
        "TOT": "Total",
        "TOT_FOODENRG": "Total Excluding Food and Energy",
    }

    title = f"Consumer Price Index (CPI) ({perspective_naming[perspective]})"
    fig.set_title(title)

    if raw:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=True,
            title=title,
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cpi",
        df / 100 if units == "AGRWTH" else df,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
def plot_balance(
    countries: Optional[List[str]],
    start_date: str = "",
    end_date: str = "",
    raw: bool = False,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """
    General government balance is defined as the balance of income and expenditure of government,
    including capital income and capital expenditures. "Net lending" means that governmen
    has a surplus, and is providing financial resources to other sectors, while
    "net borrowing" means that government has a deficit, and requires financial
    esources from other sectors. This indicator is measured as a percentage of GDP.
    All OECD countries compile their data according to the
    2008 System of National Accounts (SNA 2008). [Source: OECD]

    Parameters
    ----------
    countries: list
        List of countries to get data for
    start_date: str
        Start date of data, in YYYY-MM-DD format
    end_date: str
        End date of data, in YYYY-MM-DD format
    raw: bool
        Whether to display raw data in a table
    export: str
        Format to export data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    external_axes: bool, optional
        Whether to return the figure object or not, by default False

    Returns
    -------
    Union[OpenBBFigure, None]
        OpenBBFigure object if external_axes is True, else None (opens plot in a window)
    """
    df = oecd_model.get_balance(countries, start_date, end_date)

    if df.empty:
        return None

    fig = OpenBBFigure(yaxis_title="Percentage of GDP (%)")

    for country in df.columns:
        fig.add_scatter(
            x=df.index,
            y=df[country],
            name=country.replace("_", " ").title(),
            mode="lines",
            line_width=2.5,
            showlegend=True,
        )

    title = "Government Deficit"
    fig.set_title(title)

    if raw:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=True,
            title=title,
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "balance_percentage_gdp",
        df / 100,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
def plot_revenue(
    countries: Optional[List[str]],
    units: str = "PC_GDP",
    start_date: str = "",
    end_date: str = "",
    raw: bool = False,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """
    Governments collect revenues mainly for two purposes: to finance the goods
    and services they provide to citizens and businesses, and to fulfil their
    redistributive role. Comparing levels of government revenues across
    countries provides an indication of the importance of the government
    sector in the economy in terms of available financial resources.
    The total amount of revenues collected by governments is determined
    by past and current political decisions. This indicator is measured
    in terms of thousand USD per capita, and as a percentage of GDP. All
    OECD countries compile their data according to the 2008 System of
    National Accounts (SNA 2008). [Source: OECD]

    Parameters
    ----------
    countries: list
        List of countries to get data for
    units: str
        Units to get data in. Either 'PC_GDP' or 'THND_USD_CAP'.
        Default is Percentage of GDP.
    start_date: str
        Start date of data, in YYYY-MM-DD format
    end_date: str
        End date of data, in YYYY-MM-DD format
    raw: bool
        Whether to display raw data in a table
    export: str
        Format to export data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    external_axes: bool, optional
        Whether to return the figure object or not, by default False

    Returns
    -------
    Union[OpenBBFigure, None]
        OpenBBFigure object if external_axes is True, else None (opens plot in a window)
    """
    if units not in ["THND_USD_CAP", "PC_GDP"]:
        return console.print(
            "Use either THND_USD_CAP (thousands of USD per capity) "
            "or PC_GDP (percentage of GDP) for units"
        )

    df = oecd_model.get_revenue(countries, units, start_date, end_date)

    if df.empty:
        return None

    fig = OpenBBFigure(yaxis_title=YAXIS_TITLES[units])

    for country in df.columns:
        fig.add_scatter(
            x=df.index,
            y=df[country],
            name=country.replace("_", " ").title(),
            mode="lines",
            line_width=2.5,
            showlegend=True,
        )

    title = "Government Revenue"
    fig.set_title(title)

    if raw:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=True,
            title=title,
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"revenue_{units}",
        df / 100 if units == "PC_GDP" else df,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
def plot_spending(
    countries: Optional[List[str]],
    perspective: str = "TOT",
    units: str = "PC_GDP",
    start_date: str = "",
    end_date: str = "",
    raw: bool = False,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """
    General government spending provides an indication of the size
    of government across countries. The large variation in this indicator
    highlights the variety of countries' approaches to delivering public
    goods and services and providing social protection, not necessarily
    differences in resources spent. This indicator is measured in terms of
    thousand USD per capita, and as percentage of GDP. All OECD countries
    compile their data according to the 2008 System of
    National Accounts (SNA). [Source: OECD]

    Parameters
    ----------
    countries: list
        List of countries to get data for
    units: str
        Units to get data in. Either 'PC_GDP' or 'THND_USD_CAP'.
        Default is Percentage of GDP.
    start_date: str
        Start date of data, in YYYY-MM-DD format
    end_date: str
        End date of data, in YYYY-MM-DD format
    raw: bool
        Whether to display raw data in a table
    export: str
        Format to export data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    external_axes: bool, optional
        Whether to return the figure object or not, by default False

    Returns
    -------
    Union[OpenBBFigure, None]
        OpenBBFigure object if external_axes is True, else None (opens plot in a window)
    """
    df = oecd_model.get_spending(countries, perspective, units, start_date, end_date)

    if df.empty:
        return None

    fig = OpenBBFigure(yaxis_title=YAXIS_TITLES[units])

    for country in df.columns:
        fig.add_scatter(
            x=df.index,
            y=df[country],
            name=country.replace("_", " ").title(),
            mode="lines",
            line_width=2.5,
            showlegend=True,
        )

    perspective_naming = {
        "TOT": "Total",
        "RECULTREL": "Recreation, culture and religion)",
        "HOUCOMM": "Housing and community amenities",
        "PUBORD": "Public order and safety)",
        "EDU": "Education",
        "ENVPROT": "Environmental protection",
        "GRALPUBSER": "General public services)",
        "SOCPROT": "Social protection",
        "ECOAFF": "Economic affairs",
        "DEF": "Defence",
        "HEALTH": "Health",
    }

    title = f"Government Spending ({perspective_naming[perspective]})"
    fig.set_title(title)

    if raw:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=True,
            title=title,
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"spending_{units}_{perspective}",
        df / 100 if units == "PC_GDP" else df,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
def plot_debt(
    countries: Optional[List[str]],
    start_date: str = "",
    end_date: str = "",
    raw: bool = False,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """
    General government debt-to-GDP ratio measures the gross debt of the general
    government as a percentage of GDP. It is a key indicator for the sustainability
    of government finance. Debt is calculated as the sum of the following liability
    categories (as applicable): currency and deposits; debt securities, loans; insurance,
    pensions and standardised guarantee schemes, and other accounts payable. Changes in
    government debt over time primarily reflect the impact of past government deficits. [Source: OECD]

    Parameters
    ----------
    countries: list
        List of countries to get data for
    start_date: str
        Start date of data, in YYYY-MM-DD format
    end_date: str
        End date of data, in YYYY-MM-DD format
    raw: bool
        Whether to display raw data in a table
    export: str
        Format to export data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    external_axes: bool, optional
        Whether to return the figure object or not, by default False

    Returns
    -------
    Union[OpenBBFigure, None]
        OpenBBFigure object if external_axes is True, else None (opens plot in a window)
    """
    df = oecd_model.get_debt(countries, start_date, end_date)

    if df.empty:
        return None

    fig = OpenBBFigure(yaxis_title="Percentage of GDP (%)")

    for country in df.columns:
        fig.add_scatter(
            x=df.index,
            y=df[country],
            name=country.replace("_", " ").title(),
            mode="lines",
            line_width=2.5,
            showlegend=True,
        )

    title = "Government Debt-to-GDP Ratio"
    fig.set_title(title)

    if raw:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=True,
            title=title,
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "debt_to_gdp",
        df / 100,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
def plot_trust(
    countries: Optional[List[str]],
    start_date: str = "",
    end_date: str = "",
    raw: bool = False,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """
    Trust in government refers to the share of people who report having confidence in
    the national government. The data shown reflect the share of respondents answering
    “yes” (the other response categories being “no”, and “don’t know”) to the
    survey question: “In this country, do you have confidence in national
    government? Due to small sample sizes, country averages for horizontal inequalities
    (by age, gender and education) are pooled between 2010-18 to improve the accuracy
    of the estimates. The sample is ex ante designed to be nationally representative of
    the population aged 15 and over. This indicator is measured as a percentage
    of all survey respondents.  [Source: OECD]

    Parameters
    ----------
    countries: list
        List of countries to get data for
    start_date: str
        Start date of data, in YYYY-MM-DD format
    end_date: str
        End date of data, in YYYY-MM-DD format
    raw: bool
        Whether to display raw data in a table
    export: str
        Format to export data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    external_axes: bool, optional
        Whether to return the figure object or not, by default False

    Returns
    -------
    Union[OpenBBFigure, None]
        OpenBBFigure object if external_axes is True, else None (opens plot in a window)
    """
    df = oecd_model.get_trust(countries, start_date, end_date)

    if df.empty:
        return None

    fig = OpenBBFigure(yaxis_title="Percentage of all Survey Respondents (%)")

    for country in df.columns:
        fig.add_scatter(
            x=df.index,
            y=df[country],
            name=country.replace("_", " ").title(),
            mode="lines",
            line_width=2.5,
            showlegend=True,
        )

    title = "Trust in the Government"
    fig.set_title(title)

    if raw:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=True,
            title=title,
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "trust",
        df / 100,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)
