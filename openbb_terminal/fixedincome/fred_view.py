""" FRED view """
__docformat__ = "numpy"

# IMPORTATION STANDARD
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

# IMPORTATION THIRDPARTY
import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.fixedincome import fred_model
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

# pylint: disable=C0302,R0913,W0102

ice_bofa_path = (Path(__file__).parent / "ice_bofa_indices.csv").resolve()
commercial_paper_path = (Path(__file__).parent / "commercial_paper.csv").resolve()
spot_rates_path = (Path(__file__).parent / "corporate_spot_rates.csv").resolve()

ID_TO_NAME_ESTR = {
    "ECBESTRVOLWGTTRMDMNRT": "Euro Short-Term Rate: Volume-Weighted Trimmed Mean Rate",
    "ECBESTRTOTVOL": "Euro Short-Term Rate: Total Volume",
    "ECBESTRNUMTRANS": "Euro Short-Term Rate: Number of Transactions",
    "ECBESTRRT75THPCTVOL": "Euro Short-Term Rate: Rate at 75th Percentile of Volume",
    "ECBESTRNUMACTBANKS": "Euro Short-Term Rate: Number of Active Banks",
    "ECBESTRSHRVOL5LRGACTBNK": "Euro Short-Term Rate: Share of Volume of the 5 Largest Active Bank",
    "ECBESTRRT25THPCTVOL": "Euro Short-Term Rate: Rate at 25th Percentile of Volume",
}
ID_TO_NAME_SOFR = {
    "SOFR": "Secured Overnight Financing Rate (SOFR)",
    "SOFR30DAYAVG": "30-Day Average SOFR",
    "SOFR90DAYAVG": "90-Day Average SOFR",
    "SOFR180DAYAVG": "180-Day Average SOFR",
    "SOFRINDEX": "SOFR Index",
}
ID_TO_NAME_SONIA = {
    "IUDSOIA": "Daily Sterling Overnight Index Average (SONIA) Rate",
    "IUDZOS2": "SONIA Compounded Index",
    "IUDZLS6": "SONIA Rate: 10th percentile",
    "IUDZLS7": "SONIA Rate: 25th percentile",
    "IUDZLS8": "SONIA Rate: 75th percentile",
    "IUDZLS9": "SONIA Rate: 90th percentile",
    "IUDZLT2": "SONIA Rate Total Nominal Value",
}
ID_TO_NAME_AMERIBOR = {
    "AMERIBOR": "Overnight Unsecured AMERIBOR Benchmark Interest Rate",
    "AMBOR30T": "AMERIBOR Term-30 Derived Interest Rate Index",
    "AMBOR90T": "AMERIBOR Term-90 Derived Interest Rate Index",
    "AMBOR1W": "1-Week AMERIBOR Term Structure of Interest Rates",
    "AMBOR1M": "1-Month AMERIBOR Term Structure of Interest Rates",
    "AMBOR3M": "3-Month AMERIBOR Term Structure of Interest Rates",
    "AMBOR6M": "6-Month AMERIBOR Term Structure of Interest Rates",
    "AMBOR1Y": "1-Year AMERIBOR Term Structure of Interest Rates",
    "AMBOR2Y": "2-Year AMERIBOR Term Structure of Interest Rates",
    "AMBOR30": "30-Day Moving Average AMERIBOR Benchmark Interest Rate",
    "AMBOR90": "90-Day Moving Average AMERIBOR Benchmark Interest Rate",
}
ID_TO_NAME_FED = {
    "FEDFUNDS": "Monthly Effective Federal Funds Rate",
    "EFFR": "Daily Effective Federal Funds Rate",
    "DFF": "Daily Effective Federal Funds Rate",
    "OBFR": "Daily Overnight Bank Funding Rate",
    "FF": "Weekly Effective Federal Funds Rate",
    "RIFSPFFNB": "Daily (Excl. Weekends) Effective Federal Funds Rate",
    "RIFSPFFNA": "Annual Effective Federal Funds Rate",
    "RIFSPFFNBWAW": "Biweekly Effective Federal Funds Rate",
    "EFFRVOL": "Effective Federal Funds Volume",
    "OBFRVOL": "Overnight Bank Funding Volume",
}

ID_TO_NAME_DWPCR = {
    "MPCREDIT": "Monthly",
    "RIFSRPF02ND": "Daily (incl. Weekends)",
    "WPCREDIT": "Weekly",
    "DPCREDIT": "Daily (excl. Weekends)",
    "RIFSRPF02NA": "Annual",
}
ID_TO_NAME_TMC = {
    "T10Y3M": "3-Month",
    "T10Y2Y": "2-Year",
}
ID_TO_NAME_FFRMC = {
    "T10YFF": "10-Year",
    "T5YFF": "5-Year",
    "T1YFF": "1-Year",
    "T6MFF": "6-Month",
    "T3MFF": "3-Month",
}
ID_TO_NAME_SECONDARY = {
    "TB3MS": "3-Month",
    "DTB4WK": "4-Week",
    "DTB1YR": "1-Year",
    "DTB6": "6-Month",
}
ID_TO_NAME_TIPS = {
    "DFII5": "5-Year",
    "DFII7": "7-Year",
    "DFII10": "10-Year",
    "DFII20": "20-Year",
    "DFII30": "30-Year",
}
ID_TO_NAME_CMN = {
    "DGS1MO": "1 Month",
    "DGS3MO": "3 Month",
    "DGS6MO": "6 Month",
    "DGS1": "1 Year",
    "DGS2": "2 Year",
    "DGS3": "3 Year",
    "DGS5": "5 Year",
    "DGS7": "7 Year",
    "DGS10": "10 Year",
    "DGS20": "20 Year",
    "DGS30": "30 Year",
}
ID_TO_NAME_TBFFR = {
    "TB3SMFFM": "3 Month",
    "TB6SMFFM": "6 Month",
}

NAME_TO_ID_PROJECTION = {
    "Range High": ["FEDTARRH", "FEDTARRHLR"],
    "Central tendency High": ["FEDTARCTH", "FEDTARCTHLR"],
    "Median": ["FEDTARMD", "FEDTARMDLR"],
    "Range Midpoint": ["FEDTARRM", "FEDTARRMLR"],
    "Central tendency Midpoint": ["FEDTARCTM", "FEDTARCTMLR"],
    "Range Low": ["FEDTARRL", "FEDTARRLLR"],
    "Central tendency Low": ["FEDTARCTL", "FEDTARCTLLR"],
}

NAME_TO_ID_ECB = {"deposit": "ECBDFR", "lending": "ECBMLFR", "refinancing": "ECBMRRFR"}

MOODY_TO_OPTIONS: Dict[str, Dict] = {
    "Type": {
        "aaa": {
            "index": {
                "id": "DAAA",
                "name": "Moody's Seasoned Aaa Corporate Bond Yield",
            },
            "treasury": {
                "id": "AAA10Y",
                "name": "Moody's Seasoned Aaa Corporate Bond Yield Relative to Yield "
                "on 10-Year Treasury Constant Maturity",
            },
            "fed_funds": {
                "id": "AAAFF",
                "name": "Moody's Seasoned Aaa Corporate Bond Minus Federal Funds Rate",
            },
        },
        "baa": {
            "index": {
                "id": "DBAA",
                "name": "Moody's Seasoned Baa Corporate Bond Yield",
            },
            "treasury": {
                "id": "BAA10Y",
                "name": "Moody's Seasoned Baa Corporate Bond Yield Relative "
                "to Yield on 10-Year Treasury Constant Maturity",
            },
            "fed_funds": {
                "id": "BAAFF",
                "name": "Moody's Seasoned Baa Corporate Bond Minus Federal Funds Rate",
            },
        },
    },
    "Spread": ["treasury", "fed_funds"],  # type: ignore
}


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_estr(
    parameter: str = "volume_weighted_trimmed_mean_rate",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
):
    """Plot Euro Short-Term Rate (ESTR)

    Parameters
    ----------
    parameter: str
        FRED ID of ESTR data to plot, options: ['ECBESTRVOLWGTTRMDMNRT',
        'ECBESTRTOTVOL', 'ECBESTRNUMTRANS', 'ECBESTRRT75THPCTVOL',
        'ECBESTRNUMACTBANKS', 'ECBESTRSHRVOL5LRGACTBNK', 'ECBESTRRT25THPCTVOL']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Export data to csv or excel file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df = fred_model.get_estr(parameter, start_date, end_date)
    series_id = fred_model.ESTR_PARAMETER_TO_ECB_ID[parameter]

    ylabel_dict = {
        "ECBESTRTOTVOL": "Millions in EUR",
        "ECBESTRNUMACTBANKS": "Number of Banks",
        "ECBESTRNUMTRANS": "Number of Transactions",
    }

    fig = OpenBBFigure(yaxis_title=ylabel_dict.get(series_id, "Yield (%)"))
    fig.set_title(ID_TO_NAME_ESTR[series_id])

    fig.add_scatter(
        x=df.index, y=df[series_id], mode="lines", name=series_id, line_width=2
    )

    if export:
        if series_id not in ["ECBESTRTOTVOL", "ECBESTRNUMACTBANKS", "ECBESTRNUMTRANS"]:
            # Check whether it is a percentage, relevant for exporting
            df_transformed = pd.DataFrame(df, columns=[series_id])
        else:
            df_transformed = pd.DataFrame(df, columns=[series_id])

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            series_id,
            df_transformed,
            sheet_name,
            fig,
        )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_sofr(
    parameter: str = "overnight",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
):
    """Plot Secured Overnight Financing Rate (SOFR)

    Parameters
    ----------
    parameter: str
        FRED ID of SOFR data to plot, options: ['SOFR', 'SOFR30DAYAVG', 'SOFR90DAYAVG', 'SOFR180DAYAVG', 'SOFRINDEX']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Export data to csv or excel file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    series_id = fred_model.SOFR_PARAMETER_TO_FRED_ID[parameter]

    df = fred_model.get_sofr(
        parameter=parameter, start_date=start_date, end_date=end_date
    )

    fig = OpenBBFigure(
        yaxis_title="Yield (%)"
        if series_id != "SOFRINDEX"
        else "Index [Base = 04-2018]"
    )
    fig.set_title(ID_TO_NAME_SOFR[series_id])

    fig.add_scatter(x=df.index, y=df[series_id], mode="lines", name=series_id)

    if export:
        if series_id != "SOFRINDEX":
            # Check whether it is a percentage, relevant for exporting
            df_transformed = pd.DataFrame(df, columns=[series_id])
        else:
            df_transformed = pd.DataFrame(df, columns=[series_id])

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            series_id,
            df_transformed,
            sheet_name,
            fig,
        )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_sonia(
    parameter: str = "rate",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
):
    """Plot Sterling Overnight Index Average (SONIA)

    Parameters
    ----------
    parameter: str
        FRED ID of SONIA data to plot, options: ['IUDSOIA', 'IUDZOS2',
        'IUDZLS6', 'IUDZLS7', 'IUDZLS8', 'IUDZLS9', 'IUDZLT2']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    series_id = fred_model.SONIA_PARAMETER_TO_FRED_ID[parameter]

    df = fred_model.get_sonia(
        parameter=parameter, start_date=start_date, end_date=end_date
    )

    ylabel_dict = {
        "IUDZLT2": "Millions of GDP",
        "IUDZOS2": "Index [Base = 04-2018]",
    }

    fig = OpenBBFigure(yaxis_title=ylabel_dict.get(series_id, "Yield (%)"))
    fig.set_title(ID_TO_NAME_SONIA[series_id])

    fig.add_scatter(x=df.index, y=df[series_id], mode="lines", name=series_id)

    if export:
        if series_id not in ["IUDZOS2", "IUDZLT2"]:
            # Check whether it is a percentage, relevant for exporting
            df_transformed = pd.DataFrame(df, columns=[series_id])
        else:
            df_transformed = pd.DataFrame(df, columns=[series_id])

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            series_id,
            df_transformed,
            sheet_name,
            fig,
        )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_ameribor(
    parameter: str = "overnight",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
):
    """Plot American Interbank Offered Rate (AMERIBOR)

    Parameters
    ----------
    parameter: str
        FRED ID of AMERIBOR data to plot, options: ['AMERIBOR', 'AMBOR30T',
        'AMBOR90T', 'AMBOR1W', 'AMBOR1M', 'AMBOR3M', 'AMBOR6M', 'AMBOR1Y',
        'AMBOR2Y', 'AMBOR30', 'AMBOR90']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    series_id = fred_model.AMERIBOR_PARAMETER_TO_FRED_ID[parameter]

    df = fred_model.get_ameribor(
        parameter=parameter, start_date=start_date, end_date=end_date
    )

    fig = OpenBBFigure(
        yaxis_title="Index" if series_id in ["AMBOR30T", "AMBOR90T"] else "Yield (%)"
    )
    fig.set_title(ID_TO_NAME_AMERIBOR[series_id])

    fig.add_scatter(x=df.index, y=df[series_id], mode="lines", name=series_id)

    if export:
        if series_id not in ["AMBOR30T", "AMBOR90T"]:
            # Check whether it is a percentage, relevant for exporting
            df_transformed = pd.DataFrame(df, columns=[series_id])
        else:
            df_transformed = pd.DataFrame(df, columns=[series_id])

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            series_id,
            df_transformed,
            sheet_name,
            fig,
        )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_fftr(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
):
    """Plot Federal Funds Target Range.

    A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money. The rates
    central banks charge are set to stabilize the economy. In the United States, the Federal Reserve System's Board
    of Governors set the bank rate, also known as the discount rate.

    Parameters
    ----------
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df_upper = fred_model.get_series_data(
        series_id="DFEDTARU", start_date=start_date, end_date=end_date
    )
    df_lower = fred_model.get_series_data(
        series_id="DFEDTARL", start_date=start_date, end_date=end_date
    )
    df = pd.DataFrame([df_upper, df_lower]).transpose()

    fig = OpenBBFigure(yaxis_title="Yield (%)")
    fig.set_title("Federal Funds Target Range")

    for series in df.columns:
        fig.add_scatter(x=df.index, y=df[series], name=series)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "fftr",
        pd.DataFrame(df, columns=["FFTR"]),
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_fed(
    parameter: str = "monthly",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    overnight: bool = False,
    quantiles: bool = False,
    target: bool = False,
    raw: bool = False,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
    limit: int = 10,
):
    """Plot Effective Federal Funds Rate.

    A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money. The rates
    central banks charge are set to stabilize the economy. In the United States, the Federal Reserve System's Board
    of Governors set the bank rate, also known as the discount rate.

    Parameters
    ----------
    parameter: str
        FRED ID of EFFER data to plot, options: ['EFFR', 'EFFRVOL', 'EFFR1', 'EFFR25', 'EFFR75', 'EFFR99']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    overnight: bool
        Whether you want to plot the Overnight Banking Federal Rate
    quantiles: bool
        Whether you want to see the 1, 25, 75 and 99 percentiles
    target: bool
        Whether you want to see the high and low target range
    raw : bool
        Show raw data
    export: str
        Export data to csv or excel file
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    series_id = fred_model.FED_PARAMETER_TO_FRED_ID[parameter]

    if overnight:
        # This piece of code adjusts the series id when the user wants to plot the overnight rate
        if series_id == "DFF":
            series_id = "OBFR"
        elif series_id == "EFFRVOL":
            series_id = "OBFRVOL"
        else:
            console.print(
                "The Overnight Banking Federal Rate only supports Daily data."
            )
            series_id = "OBFR"

    fig = OpenBBFigure()

    if quantiles or target and not overnight:
        series_id = series_id if series_id != "EFFRVOL" else "EFFR"

        df = fred_model.get_fed(
            parameter, start_date, end_date, overnight, quantiles, target
        )

        for column in df.columns:
            fig.add_scatter(
                x=df.index,
                y=df[column],
                name=column,
                line_width=3 if column == series_id else 1.3,
                mode="lines",
            )
        fig.set_title(ID_TO_NAME_FED[series_id])
        fig.set_yaxis_title("Yield (%)")

    else:
        df = fred_model.get_fed(
            parameter, start_date, end_date, overnight, quantiles, target
        )

        fig.add_scatter(
            x=df.index, y=df[series_id], name=series_id, line_width=2.5, mode="lines"
        )
        fig.set_yaxis_title(
            "Yield (%)"
            if series_id not in ["EFFRVOL", "OBFRVOL"]
            else "Billions in USD"
        )

        fig.set_title(ID_TO_NAME_FED[series_id])

    if export or raw:
        if not quantiles and not target:
            if series_id != "EFFRVOL":
                # Check whether it is a percentage, relevant for exporting
                df_transformed = pd.DataFrame(df, columns=[series_id])
            else:
                df_transformed = pd.DataFrame(df, columns=[series_id])
        else:
            df_transformed = df

    if raw:
        # was a -iloc so we need to flip the index as we use head
        df_transformed = df_transformed.sort_index(ascending=False)
        print_rich_table(
            df_transformed,
            headers=list(df_transformed.columns),
            show_index=True,
            title=ID_TO_NAME_FED[series_id],
            floatfmt=".3f",
            export=bool(export),
            limit=limit,
        )

    if export:
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            series_id,
            df_transformed,
            sheet_name,
            fig,
        )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_iorb(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
):
    """Plot Interest Rate on Reserve Balances.

    Parameters
    ----------
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df = fred_model.get_iorb(start_date=start_date, end_date=end_date)

    fig = OpenBBFigure(yaxis_title="Yield (%)")
    fig.set_title("Interest Rate on Reserve Balances")

    fig.add_scatter(x=df.index, y=df["IORB"], name="IORB", line_width=2, mode="lines")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "iorb",
        pd.DataFrame(df, columns=["IORB"]),
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_projection(
    long_run: bool = False,
    raw: bool = False,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
):
    """Plot the Federal Reserve's projection of the federal funds rate.

    Parameters
    ----------
    long_run: str
        Whether to plot the long run projection.
    export: str
        Export data to csv or excel file
    raw : bool
        Show raw data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    data_series_df = fred_model.get_projection(long_run=long_run)

    fig = OpenBBFigure(yaxis_title="Yield (%)")
    fig.set_title(
        f"FOMC {'Long Run ' if long_run else ''}Summary of Economic Projections\n"
        "for the Federal Funds Rate"
    )

    for legend, df in data_series_df.items():
        fig.add_scatter(
            x=df.index,
            y=df.values,
            name=legend,
            line_width=1.3 if legend != "Median" else 2,
            line_dash="dash" if legend != "Median" else "solid",
            mode="lines",
        )

    fig.update_layout(
        legend=dict(x=0.01, y=0.01, xanchor="left", yanchor="bottom"),
        xaxis=dict(tickformat="%Y-%m-%d"),
    )

    if raw:
        print_rich_table(
            data_series_df,
            headers=list(data_series_df.columns),
            show_index=True,
            title=f"FOMC {'Long Run ' if long_run else ''}Summary of "
            "Economic Projections for the Federal Funds Rate",
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "projection",
        data_series_df,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_dwpcr(
    parameter: str = "DPCREDIT",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
):
    """Plot Discount Window Primary Credit Rate.

    Parameters
    ----------
    parameter: str
        FRED ID of DWPCR data to plot, options: ['MPCREDIT', 'RIFSRPF02ND', 'WPCREDIT', 'DPCREDIT', 'RIFSRPF02NA']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    series_id = fred_model.DWPCR_PARAMETER_TO_FRED_ID[parameter]

    df = fred_model.get_dwpcr(
        parameter=parameter, start_date=start_date, end_date=end_date
    )

    fig = OpenBBFigure()
    fig.set_title(f"Discount Window Primary Credit Rate {ID_TO_NAME_DWPCR[series_id]}")

    fig.add_scatter(x=df.index, y=df[series_id], name=series_id, mode="lines")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        series_id,
        pd.DataFrame(df, columns=[series_id]),
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_ecb(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    interest_type: Optional[str] = None,
    raw: bool = False,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
    limit: int = 10,
):
    """Plot the key ECB interest rates.

    The Governing Council of the ECB sets the key interest rates for the euro area:

    - The interest rate on the main refinancing operations (MRO), which provide
    the bulk of liquidity to the banking system.
    - The rate on the deposit facility, which banks may use to make overnight deposits with the Eurosystem.
    - The rate on the marginal lending facility, which offers overnight credit to banks from the Eurosystem.

    Parameters
    ----------
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    interest_type: Optional[str]
        The ability to decide what interest rate to plot
    export: str
        Export data to csv or excel file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    df = fred_model.get_ecb(
        interest_type=interest_type, start_date=start_date, end_date=end_date
    )

    title = (
        f"ECB {interest_type.title()} Rate for Euro Area"
        if interest_type
        else "ECB Interest Rates for Euro Area"
    )

    fig = OpenBBFigure()
    fig.set_title(title)

    for series in df:
        fig.add_scatter(x=df.index, y=df[series], name=series.title(), mode="lines")

    fig.update_layout(legend=dict(x=0.01, y=0.01, xanchor="left", yanchor="bottom"))

    if raw:
        # was a -iloc so we need to flip the index as we use head
        df = df.sort_index(ascending=False)
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=True,
            title=title,
            floatfmt=".3f",
            export=bool(export),
            limit=limit,
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ecbdfr",
        pd.DataFrame(df, columns=df.columns),
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_tmc(
    parameter: str = "3_month",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
):
    """Plot 10-Year Treasury Constant Maturity Minus Selected Treasury Constant Maturity data.

    Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of auctioned U.S.
    Treasuries. The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury
    yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.

    Parameters
    ----------
    parameter: str
        FRED ID of TMC data to plot, options: ['T10Y3M', 'T10Y3M']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    series_id = fred_model.TMC_PARAMETER_TO_FRED_ID[parameter]

    df = fred_model.get_tmc(
        parameter=parameter, start_date=start_date, end_date=end_date
    )

    fig = OpenBBFigure(yaxis_title="Yield (%)")
    fig.set_title(
        f"10-Year Treasury Constant Maturity Minus {ID_TO_NAME_TMC[series_id]}"
        "  Treasury Constant Maturity"
    )

    fig.add_scatter(x=df.index, y=df[series_id], name=series_id, mode="lines")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        series_id,
        pd.DataFrame(df, columns=[series_id]),
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_ffrmc(
    parameter: str = "10_year",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
):
    """Plot Selected Treasury Constant Maturity Minus Federal Funds Rate data.

    Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of auctioned U.S.
    Treasuries. The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury
    yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.

    Parameters
    ----------
    parameter: str
        FRED ID of FFRMC data to plot
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    series_id = fred_model.FFRMC_PARAMETER_TO_FRED_ID[parameter]

    df = fred_model.get_ffrmc(parameter, start_date, end_date)

    fig = OpenBBFigure()
    fig.set_title(
        f"{ID_TO_NAME_FFRMC[series_id]} Treasury Constant Maturity Minus Federal Funds Rate"
    )

    fig.add_scatter(x=df.index, y=df[series_id], name=series_id, mode="lines")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        series_id,
        pd.DataFrame(df, columns=[series_id]),
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def display_yield_curve(
    date: str = "",
    inflation_adjusted: bool = False,
    raw: bool = False,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
):
    """Display yield curve based on US Treasury rates for a specified date.

    The graphic depiction of the relationship between the yield on bonds of the same credit quality but different
    maturities is known as the yield curve. In the past, most market participants have constructed yield curves from
    the observations of prices and yields in the Treasury market. Two reasons account for this tendency. First,
    Treasury securities are viewed as free of default risk, and differences in creditworthiness do not affect yield
    estimates. Second, as the most active bond market, the Treasury market offers the fewest problems of illiquidity
    or infrequent trading. The key function of the Treasury yield curve is to serve as a benchmark for pricing bonds
    and setting yields in other sectors of the debt market.

    It is clear that the market’s expectations of future rate changes are one important determinant of the
    yield-curve shape. For example, a steeply upward-sloping curve may indicate market expectations of near-term Fed
    tightening or of rising inflation. However, it may be too restrictive to assume that the yield differences across
    bonds with different maturities only reflect the market’s rate expectations. The well-known pure expectations
    hypothesis has such an extreme implication. The pure expectations hypothesis asserts that all government bonds
    have the same near-term expected return (as the nominally riskless short-term bond) because the return-seeking
    activity of risk-neutral traders removes all expected return differentials across bonds.

    Parameters
    ----------
    date: str
        Date to get curve for. If None, gets most recent date (format yyyy-mm-dd)
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    raw : bool
        Output only raw data
    export : str
        Export data to csv,json,xlsx or png,jpg,pdf,svg file
    """
    rates, date_of_yield = fred_model.get_yield_curve(date, True, inflation_adjusted)
    if rates.empty:
        return console.print(f"[red]Yield data not found for {date_of_yield}.[/red]\n")

    fig = OpenBBFigure(xaxis_title="Maturity", yaxis_title="Yield (%)")
    fig.set_title(
        f"US {'Real' if inflation_adjusted else 'Nominal'} Yield Curve for {date_of_yield} "
    )

    fig.add_scatter(x=rates["Maturity"], y=rates["Rate"], name="Yield")

    if raw:
        print_rich_table(
            rates,
            headers=list(rates.columns),
            show_index=False,
            title=f"United States {'Real' if inflation_adjusted else 'Nominal'} Yield Curve for {date_of_yield}",
            floatfmt=".3f",
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ycrv",
        rates.set_index("Maturity"),
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_usrates(
    parameter: str = "tbills",
    maturity: str = "3_months",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    raw: bool = False,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
    limit: int = 10,
):
    """Plot various treasury rates from the United States

    A Treasury Bill (T-Bill) is a short-term U.S. government debt obligation backed by the Treasury Department with a
    maturity of one year or less. Treasury bills are usually sold in denominations of $1,000. However, some can reach
    a maximum denomination of $5 million in non-competitive bids. These securities are widely regarded as low-risk
    and secure investments.

    Yields on Treasury nominal securities at “constant maturity” are interpolated by the U.S. Treasury from the daily
    yield curve for non-inflation-indexed Treasury securities. This curve, which relates the yield on a security to
    its time to maturity, is based on the closing market bid yields on actively traded Treasury securities in the
    over-the-counter market. These market yields are calculated from composites of quotations obtained by the Federal
    Reserve Bank of New York. The constant maturity yield values are read from the yield curve at fixed maturities,
    currently 1, 3, and 6 months and 1, 2, 3, 5, 7, 10, 20, and 30 years. This method provides a yield for a 10-year
    maturity, for example, even if no outstanding security has exactly 10 years remaining to maturity. Similarly,
    yields on inflation-indexed securities at “constant maturity” are interpolated from the daily yield curve for
    Treasury inflation protected securities in the over-the-counter market. The inflation-indexed constant maturity
    yields are read from this yield curve at fixed maturities, currently 5, 7, 10, 20, and 30 years.

    Parameters
    ----------
    parameter: str
        Either "tbills", "cmn", or "tips".
    maturity: str
        Depending on the chosen parameter, a set of maturities is available.
    series_id: str
        FRED ID of Treasury Bill Secondary Market Rate data to plot, options: ['TB3MS', 'DTB4WK', 'DTB1YR', 'DTB6']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    series_id = fred_model.USARATES_TO_FRED_ID[maturity][parameter]
    df = fred_model.get_usrates(
        parameter=parameter, maturity=maturity, start_date=start_date, end_date=end_date
    )

    if df.empty:
        return console.print(f"[red]No data found for {parameter} {maturity}[/red]\n")

    title_dict = {
        "tbills": "Treasury Bill Secondary Market Rate, Discount Basis",
        "cmn": "Treasury Constant Maturity Nominal Market Yield",
        "tips": "Yields on Treasury inflation protected securities (TIPS)"
        " adjusted to constant maturities",
    }
    title = f"{maturity.replace('_', ' ').title()} {title_dict.get(parameter, '')}"

    fig = OpenBBFigure(yaxis_title="Yield (%)")
    fig.set_title(title)

    fig.add_scatter(x=df.index, y=df[series_id], name="Yield")

    if raw:
        # was a -iloc so we need to flip the index as we use head
        df = pd.DataFrame(df, columns=[series_id])
        df = df.sort_index(ascending=False)
        print_rich_table(
            df,
            title=title,
            show_index=True,
            floatfmt=".3f",
            export=bool(export),
            limit=limit,
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        series_id,
        pd.DataFrame(df, columns=[series_id]),
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_tbffr(
    parameter: str = "TB3SMFFM",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
):
    """Plot Selected Treasury Bill Minus Federal Funds Rate data.

    Parameters
    ----------
    parameter: str
        FRED ID of TBFFR data to plot, options: ['TB3SMFFM', 'TB6SMFFM']
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    export: str
        Export data to csv or excel file
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    series_id = fred_model.TBFFR_PARAMETER_TO_FRED_ID[parameter]

    df = fred_model.get_tbffr(
        parameter=parameter, start_date=start_date, end_date=end_date
    )

    if df.empty:
        return console.print(
            f"[red]No data found for {ID_TO_NAME_TBFFR[series_id]}[/red]"
        )

    fig = OpenBBFigure(yaxis_title="Yield (%)")
    fig.set_title(
        f"{ID_TO_NAME_TBFFR[series_id]} Treasury Bill Minus Federal Funds Rate"
    )

    fig.add_scatter(x=df.index, y=df[series_id], name="Yield")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        series_id,
        pd.DataFrame(df, columns=["TBFFR"]),
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_icebofa(
    data_type: str = "yield",
    category: str = "all",
    area: str = "us",
    grade: str = "non_sovereign",
    options: bool = False,
    description: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    raw: bool = False,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
    limit: int = 10,
):
    """Plot ICE BofA US Corporate Bond Index data.

    Parameters
    ----------
    data_type: str
        The type of data you want to see, either "yield", "yield_to_worst", "total_return", or "spread"
    category: str
        The type of category you want to see, either "all", "duration", "eur" or "usd".
    area: str
        The type of area you want to see, either "asia", "emea", "eu", "ex_g10", "latin_america" or "us"
    grade: str
        The type of grade you want to see, either "a", "aa", "aaa", "b", "bb", "bbb", "ccc", "crossover",
        "high_grade", "high_yield", "non_financial", "non_sovereign", "private_sector", "public_sector"
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    raw: bool
        Show raw data
    export: str
        Export data to csv or excel file
    sheet_name: str
        Name of the sheet to export to
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    if data_type == "total_return":
        units = "index"
    elif data_type in ["yield", "yield_to_worst", "spread"]:
        units = "percent"

    series = pd.read_csv(ice_bofa_path)

    if options:
        return print_rich_table(
            series.drop(
                ["Frequency", "Units", "Asset Class", "FRED Series ID", "Description"],
                axis=1,
            )[
                series["Type"].isin(
                    ["yield", "yield_to_worst", "total_return"]
                    if data_type != "spread"
                    else ["spread"]
                )
            ],
            export=bool(export),
        )

    df = fred_model.get_icebofa(
        data_type=data_type,
        category=category,
        area=area,
        grade=grade,
        start_date=start_date,
        end_date=end_date,
    )

    if df.empty:
        return console.print()

    title = (
        ""
        if df.empty
        else "ICE BofA Bond Benchmark Indices"
        if len(df.columns) > 1
        else df.columns[0]
    )

    fig = OpenBBFigure(yaxis_title="Yield (%)" if units == "percent" else "Index")
    fig.set_title(title)

    for column in df.columns:
        fig.add_scatter(
            x=df.index,
            y=df[column].values,
            name=column,
            showlegend=True,
            connectgaps=True,
        )

    if raw:
        # was a -iloc so we need to flip the index as we use head
        df = df.sort_index(ascending=False)
        print_rich_table(
            df,
            title=title,
            show_index=True,
            floatfmt=".3f",
            export=bool(export),
            limit=limit,
        )

    if description and title:
        for index_title in df.columns:
            description_text = series[series["Title"] == index_title][
                "Description"
            ].values[0]
            console.print(f"\n[bold]{title}[/bold]")
            console.print(description_text)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ICEBOFA",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_moody(
    data_type: str = "aaa",
    spread: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    raw: bool = False,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
    limit: int = 10,
):
    """Plot Moody Corporate Bond Index data
    Parameters
    ----------
    data_type: str
        The type of data you want to see, either "aaa" or "baa"
    spread: Optional[str]
        Whether you want to show the spread for treasury or fed_funds
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    raw: bool
        Show raw data
    export: str
        Export data to csv or excel file
    sheet_name: str
        Name of the sheet to export to
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    name = fred_model.MOODY_TO_OPTIONS["Type"][data_type][
        spread if spread else "index"
    ]["name"]

    df = fred_model.get_moody(
        data_type=data_type, spread=spread, start_date=start_date, end_date=end_date
    )

    if df.empty:
        return console.print(f"[bold red]No data found for {name}[/bold red]")

    fig = OpenBBFigure(yaxis_title="Yield (%)")
    fig.set_title(name)

    for series in df.columns:
        fig.add_scatter(x=df.index, y=df[series], name=series)

    if raw:
        # was a -iloc so we need to flip the index as we use head
        df = df.sort_index(ascending=False)
        print_rich_table(
            df,
            title=name,
            show_index=True,
            floatfmt=".3f",
            export=bool(export),
            limit=limit,
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "MOODY",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_cp(
    maturity: str = "30d",
    category: str = "financial",
    grade: str = "aa",
    options: bool = False,
    description: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    raw: bool = False,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
    limit: int = 10,
):
    """Plot Commercial Paper

    Parameters
    ----------
    maturity: str
        The maturity you want to see, either "overnight", "7d", "15d", "30d", "60d" or "90d"
    category: str
        The category you want to see, either "asset_backed", "financial" or "non_financial"
    grade: str
        The type of grade you want to see, either "a2_p2" or "aa"
    description: bool
        Whether you wish to obtain a description of the data.
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    raw: bool
        Show raw data
    export: str
        Export data to csv or excel file
    sheet_name: str
        Name of the sheet to export to
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    if grade == "a2_p2" and category != "non_financial":
        console.print(
            "Setting category to 'non_financial' given "
            f"the chosen {grade} grade only has data for 'non_financial'."
        )
        category = "non_financial"

    series = pd.read_csv(commercial_paper_path)

    if options:
        return print_rich_table(
            series.drop(["Description", "FRED Series ID"], axis=1), export=bool(export)
        )

    df = fred_model.get_cp(
        maturity=maturity,
        category=category,
        grade=grade,
        start_date=start_date,
        end_date=end_date,
    )

    if df.empty:
        return console.print()

    title = "Commercial Paper Interest Rates" if len(df.columns) > 1 else df.columns[0]

    fig = OpenBBFigure(yaxis_title="Yield (%)")
    fig.set_title(title)

    for column in df.columns:
        fig.add_scatter(
            x=df.index, y=df[column].values, name=column, showlegend=len(df.columns) > 1
        )

    if raw:
        # was a -iloc so we need to flip the index as we use head
        df = df.sort_index(ascending=False)
        print_rich_table(
            df,
            title=title,
            show_index=True,
            floatfmt=".3f",
            export=bool(export),
            limit=limit,
        )

    if description:
        message = (
            "To calculate CP interest rate indexes, the Federal Reserve Board uses DTCC's data for certain trades"
            " to estimate a relation between interest rates on the traded securities and their maturities. In this"
            " calculation, the trades represent sales of CP by dealers or direct issuers to investors (that is,"
            " the offer side) and are weighted according to the face value of the CP so that larger trades have"
            " a greater effect on the resulting index. With the relation between interest rates and maturities"
            " established, the reported interest rates represent the estimated interest rates for the specified"
            " maturities.\n\n"
            "Interest rates calculated through the process described above are a statistical aggregation"
            " of numerous data reflecting many trades for different issuers, maturities, and so forth."
            " Accordingly, the reported interest rates purport to reflect activity in certain segments"
            " of the market, but they may not equal interest rates for any specific trade. As with other"
            " statistical processes, this one is designed to minimize the difference between the interest"
            " rates at which actual trades occur and the estimated interest rates.\n\n"
            "CP trades included in the calculation are chosen according to the specifications listed in the"
            " table below. Data to assess CP trades relative to these criteria are updated daily from numerous"
            " publicly available sources. Standard Industrial Classification (SIC) code classifications are"
            " taken from the Securities and Exchange Commission (SEC) Directory of Companies Required to File"
            ' Annual Reports with the SEC. When an issuer"s primary SIC code is not reported in the SEC'
            ' directory, the primary SIC code reported in the issuer"s financial reports is used; otherwise,'
            " SIC codes are determined upon consultation with the Office of Management and Budget's Standard "
            "Industrial Classification Manual or its Supplement.\n\n"
            "For a discussion of econometric techniques for fitting the term structure of interest rates, including"
            ' bibliographic information, see, for example, William S. Cleveland, 1979, "Robust Locally'
            ' Weighted Regression and Smoothing Scatterplots," Journal of the American Statistical Association,'
            " 74, 829-36, or William S. Cleveland, Susan J. Devlin, and Eric Grosse, 1988,"
            ' "Regression by Local Fitting," Journal of Econometrics, 37, 87-114.\n\n'
            "Source: https://www.federalreserve.gov/releases/cp/about.htm"
        )
        console.print(message)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "CP",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_spot(
    maturity: List = ["10y"],
    category: List = ["spot_rate"],
    description: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    raw: bool = False,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
    limit: int = 10,
):
    """Plot Spot Rates for a given maturity

    The spot rate for any maturity is the yield on a bond that provides
    a single payment at that maturity. This is a zero coupon bond. Because each
    spot rate pertains to a single cashflow, it is the relevant interest rate
    concept for discounting a pension liability at the same maturity.

    Parameters
    ----------
    maturity: str
        The maturity you want to see (ranging from '1y' to '100y')
    category: list
        The category you want to see ('par_yield' and/or 'spot_rate')
    description: bool
        Whether you wish to obtain a description of the data.
    start_date: Optional[str]
        Start date, formatted YYYY-MM-DD
    end_date: Optional[str]
        End date, formatted YYYY-MM-DD
    raw: bool
        Show raw data
    export: str
        Export data to csv or excel file
    sheet_name: str
        Name of the sheet to export to
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    df = fred_model.get_spot(
        maturity=maturity, category=category, start_date=start_date, end_date=end_date
    )

    if df.empty:
        return console.print(
            f"[bold red]No data found for maturity {maturity} and category {category}[/bold red]"
        )

    title = (
        "High Quality Market (HQM) Corporate Bond Rates"
        if len(df.columns) > 1
        else df.columns[0]
    )

    fig = OpenBBFigure(yaxis_title="Yield (%)")
    fig.set_title(title)

    for column in df.columns:
        fig.add_scatter(
            x=df.index, y=df[column].values, name=column, showlegend=len(df.columns) > 1
        )

    if raw:
        # was a -iloc so we need to flip the index as we use head
        df = df.sort_index(ascending=False)
        print_rich_table(
            df,
            title=title,
            show_index=True,
            floatfmt=".3f",
            export=bool(export),
            limit=limit,
        )

    if description:
        header1 = "T-Year High Quality Market (HQM) Corporate Bond Spot Rate"
        message1 = (
            "The spot rate for T-Year High Quality Market (HQM) Corporate Bond Spot Rate"
            " is defined as the yield on a bond that gives a single payment after T year."
            " This is called a zero coupon bond. Because high quality zero coupon bonds are"
            " not generally available, the HQM methodology computes the spot rates so as to"
            " make them consistent with the yields on other high quality bonds. The HQM"
            " yield curve uses data from a set of high quality corporate bonds rated AAA"
            ", AA, or A that accurately represent the high quality corporate bond market."
        )
        header2 = "T-Year High Quality Market (HQM) Corporate Bond Par Yield"
        message2 = (
            "The par yield for T-Year High Quality Market (HQM) Corporate Bond Par"
            " Yield is the coupon rate at which bond prices are zero."
        )
        console.print(f"\n[bold]{header1}[/bold]")
        console.print(message1)
        console.print(f"\n[bold]{header2}[/bold]")
        console.print(message2)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "SPOT",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)


@log_start_end(log=logger)
@check_api_key(["API_FRED_KEY"])
def plot_hqm(
    date: Optional[str] = None,
    par: bool = False,
    raw: bool = False,
    export: str = "",
    sheet_name: str = "",
    external_axes: bool = False,
):
    """Plot the HQM yield curve

    The HQM yield curve represents the high quality corporate bond market, i.e.,
    corporate bonds rated AAA, AA, or A.  The HQM curve contains two regression terms. These
    terms are adjustment factors that blend AAA, AA, and A bonds into a single HQM yield curve
    that is the market-weighted average (MWA) quality of high quality bonds.

    Parameters
    ----------
    date: str
        The date of the yield curve you wish to plot
    par: bool
        Whether you wish to plot the par yield curve as well
    raw: bool
        Show raw data
    export: str
        Export data to csv or excel file
    sheet_name: str
        Name of the sheet to export to
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    data_types = ["spot", "par"] if par else ["spot"]

    df, date_of_yield = fred_model.get_hqm(date=date, par=par)

    if df.empty:
        return console.print()

    fig = OpenBBFigure(xaxis_title="Maturity", yaxis_title="Yield (%)")
    fig.set_title(f"Spot{'and Par' if par else ''} Yield Curve for {date_of_yield}")

    for types in data_types:
        fig.add_scatter(x=df.index, y=df[types], name=f"{types.title()} Yield")

    if raw:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=True,
            index_name="Maturity",
            title=f"Spot {'and Par' if par else ''} Yield Curve for {date_of_yield}",
            floatfmt=".3f",
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cycrv",
        df,
        sheet_name,
        fig,
    )

    return fig.show(external=raw or external_axes)
