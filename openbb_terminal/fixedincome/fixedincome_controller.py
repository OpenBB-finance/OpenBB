""" Futures Controller """
__docformat__ = "numpy"

# pylint:disable=C0302

# IMPORTATION STANDARD
import argparse
import logging
from typing import List, Optional

# IMPORTATION THIRDPARTY
import pandas as pd

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.fixedincome import (
    ecb_view,
    fred_model,
    fred_view,
    oecd_model,
    oecd_view,
)
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    list_from_str,
    print_rich_table,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)


class FixedIncomeController(BaseController):
    """Fixed Income Controller class"""

    CHOICES_COMMANDS = [
        "estr",
        "sofr",
        "sonia",
        "ameribor",
        "fed",
        "iorb",
        "projection",
        "dwpcr",
        "ecb",
        "treasury",
        "tmc",
        "ffrmc",
        "ycrv",
        "ecbycrv",
        "usrates",
        "icebofa",
        "moody",
        "cp",
        "spot",
        "hqm",
        "icespread",
        "tbffr",
    ]

    PATH = "/fixedincome/"
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            self.choices: dict = self.choices_default

            # These values need to work with multi options which
            # is why they are defined here
            self.choices["treasury"]["--short"] = {
                c: None for c in oecd_model.COUNTRY_TO_CODE_SHORT
            }
            self.choices["treasury"]["--long"] = {
                c: None for c in oecd_model.COUNTRY_TO_CODE_LONG
            }

            self.choices["spot"]["--maturity"] = {
                c: None for c in fred_model.SPOT_TO_OPTIONS["Maturity"]
            }
            self.choices["spot"]["-m"] = "--maturity"
            self.choices["spot"]["--category"] = {
                c: None for c in fred_model.SPOT_TO_OPTIONS["Category"]
            }
            self.choices["spot"]["-c"] = "--category"
            self.completer = NestedCompleter.from_nested_dict(self.choices)  # type: ignore

    def print_help(self):
        """Print help"""
        mt = MenuText("fixedincome/", column_sources=120)
        mt.add_info("_reference_rates_")
        mt.add_cmd("estr")
        mt.add_cmd("sofr")
        mt.add_cmd("sonia")
        mt.add_cmd("ameribor")
        mt.add_raw("\n")
        mt.add_info("_central_bank_rates_")
        mt.add_cmd("fed")
        mt.add_cmd("projection")
        mt.add_cmd("iorb")
        mt.add_cmd("dwpcr")
        mt.add_cmd("ecb")
        mt.add_raw("\n")
        mt.add_info("_government_bonds_")
        mt.add_cmd("treasury")
        mt.add_cmd("usrates")
        mt.add_cmd("ycrv")
        mt.add_cmd("ecbycrv")
        mt.add_raw("\n")
        mt.add_info("_corporate_bonds_")
        mt.add_cmd("icebofa")
        mt.add_cmd("moody")
        mt.add_cmd("cp")
        mt.add_cmd("spot")
        mt.add_cmd("hqm")
        mt.add_raw("\n")
        mt.add_info("_spreads_")
        mt.add_cmd("icespread")
        mt.add_cmd("tmc")
        mt.add_cmd("ffrmc")
        mt.add_cmd("tbffr")

        console.print(text=mt.menu_text, menu="Fixed Income")

    @log_start_end(log=logger)
    def call_estr(self, other_args: List[str]):
        """Process estr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="estr",
            description="The euro short-term rate (€STR) reflects the wholesale euro "
            "unsecured overnight borrowing costs of banks located in the euro area. The "
            "€STR is published on each TARGET2 business day based on transactions conducted "
            "and settled on the previous TARGET2 business day (the reporting date “T”) "
            "with a maturity date of T+1 which are deemed to have been executed at arm’s "
            "length and thus reflect market rates in an unbiased way.",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Specific Euro Short-Term Rate data to retrieve",
            default="volume_weighted_trimmed_mean_rate",
            choices=ecb_view.ESTR_PARAMETER_TO_ECB_ID.keys(),
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            if ns_parser.source == "FRED":
                fred_view.plot_estr(
                    parameter=ns_parser.parameter,
                    start_date=ns_parser.start_date,
                    end_date=ns_parser.end_date,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.source == "ECB":
                ecb_view.plot_estr(
                    parameter=ns_parser.parameter,
                    start_date=ns_parser.start_date,
                    end_date=ns_parser.end_date,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )

    @log_start_end(log=logger)
    def call_sofr(self, other_args: List[str]):
        """Process sofr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sofr",
            description="The Secured Overnight Financing Rate (SOFR) is a "
            "broad measure of the cost of borrowing cash overnight collateralized "
            "by Treasury securities. The SOFR is calculated as a volume-weighted "
            "median of transaction-level tri-party repo data. ",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Specific SOFR data to retrieve",
            default="overnight",
            choices=fred_model.SOFR_PARAMETER_TO_FRED_ID.keys(),
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default="1980-01-01",
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            fred_view.plot_sofr(
                parameter=ns_parser.parameter,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_sonia(self, other_args: List[str]):
        """Process sonia command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sonia",
            description="SONIA (Sterling Overnight Index Average) is an important "
            "interest rate benchmark. SONIA is based on actual transactions and "
            "reflects the average of the interest rates that banks pay to borrow "
            "sterling overnight from other financial institutions and other institutional investors.",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Specific SONIA data to retrieve",
            default="rate",
            choices=fred_model.SONIA_PARAMETER_TO_FRED_ID.keys(),
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            fred_view.plot_sonia(
                parameter=ns_parser.parameter,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_ameribor(self, other_args: List[str]):
        """Process ameribor command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ameribor",
            description="Ameribor (short for the American interbank offered rate) is "
            "a benchmark interest rate that reflects the true cost of short-term interbank borrowing. "
            "This rate is based on transactions in overnight unsecured loans conducted on the American "
            "Financial Exchange (AFX).",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Specific AMERIBOR data to retrieve",
            default="overnight",
            choices=fred_model.AMERIBOR_PARAMETER_TO_FRED_ID.keys(),
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            fred_view.plot_ameribor(
                parameter=ns_parser.parameter,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_fed(self, other_args: List[str]):
        """Process fed command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="fed",
            description="Get Effective Federal Funds Rate data.\nA bank rate is the interest rate a nation's central "
            "bank charges to its domestic banks to borrow money. The rates central banks charge are set "
            "to stabilize the economy. In the United States, the Federal Reserve System's Board of "
            "Governors set the bank rate, also known as the discount rate.",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Specific Effective Federal Funds Rate data to retrieve",
            default="monthly",
            choices=fred_model.FED_PARAMETER_TO_FRED_ID.keys(),
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default="1900-01-01",
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )

        parser.add_argument(
            "-o",
            "--overnight",
            dest="overnight",
            action="store_true",
            help="Gets the Overnight Bank Funding Rate",
            default=False,
        )
        parser.add_argument(
            "-q",
            "--quantiles",
            dest="quantiles",
            action="store_true",
            help="Whether to show 1, 25, 75 and 99 percentiles",
            default=False,
        )
        parser.add_argument(
            "-t",
            "--target",
            dest="target",
            action="store_true",
            help="Whether to show the target range data",
            default=False,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES, raw=True
        )
        if ns_parser:
            if ns_parser.overnight and (ns_parser.target or ns_parser.quantiles):
                console.print(
                    "The Overnight Bank Funding Rate has no target and quantiles data."
                )
            else:
                fred_view.plot_fed(
                    parameter=ns_parser.parameter,
                    start_date=ns_parser.start_date,
                    end_date=ns_parser.end_date,
                    overnight=ns_parser.overnight,
                    quantiles=ns_parser.quantiles,
                    target=ns_parser.target,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )

    @log_start_end(log=logger)
    def call_iorb(self, other_args: List[str]):
        """Process iorb command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="iorb",
            description="Get Interest Rate on Reserve Balances data\nA bank rate is the interest rate a nation's "
            "central bank charges to its domestic banks to borrow money. The rates central banks charge "
            "are set to stabilize the economy. In the United States, the Federal Reserve System's Board "
            "of Governors set the bank rate, also known as the discount rate.",
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            fred_view.plot_iorb(
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_projection(self, other_args: List[str]):
        """Process projection command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="projection",
            description="Get the Federal Reserve's projection of the federal funds rate.",
        )
        parser.add_argument(
            "-l",
            "--long-run",
            dest="long_run",
            action="store_true",
            help="Whether to show the long run projection",
            default=False,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES, raw=True
        )
        if ns_parser:
            fred_view.plot_projection(
                long_run=ns_parser.long_run,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_dwpcr(self, other_args: List[str]):
        """Process dwpcr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="dwpcr",
            description="Get Discount Window Primary Credit Rate data.\nA bank rate is the interest rate a nation's "
            "central bank charges to its domestic banks to borrow money. The rates central banks charge "
            "are set to stabilize the economy. In the United States, the Federal Reserve System's Board "
            "of Governors set the bank rate, also known as the discount rate.",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Specific Discount Window Primary Credit Rate data to retrieve",
            default="daily_excl_weekend",
            choices=fred_model.DWPCR_PARAMETER_TO_FRED_ID.keys(),
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            fred_view.plot_dwpcr(
                parameter=ns_parser.parameter,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_ecb(self, other_args: List[str]):
        """Process ecb command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ecb",
            description="Plot the three interest rates the ECB sets "
            "every six weeks as part of its monetary policy, these are the "
            "interest rate on the main refinancing operations (MRO), the rate on "
            "the deposit facility and the rate on the marginal lending facility.",
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-t",
            "--type",
            dest="type",
            type=str,
            help="Whether to choose the deposit, marginal lending or main refinancing rate",
            choices=["deposit", "lending", "refinancing"],
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES, raw=True
        )
        if ns_parser:
            fred_view.plot_ecb(
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                interest_type=ns_parser.type,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_treasury(self, other_args: List[str]):
        """Process treasury command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="treasury",
            description="Plot short (3 month) and long (10 year) term interest rates from selected countries "
            "including the possibility to plot forecasts for the next years.",
        )

        parser.add_argument(
            "--short",
            type=str,
            dest="short",
            help="Countries to get short term (3 month) interest rates for.",
            default=None,
        )

        parser.add_argument(
            "--long",
            type=str,
            dest="long",
            help="Countries to get long term (10 year) interest rates for.",
            default=None,
        )
        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            help="Start date of data, in YYYY-MM-DD format",
            dest="start_date",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            help="End date of data, in YYYY-MM-DD format",
            dest="end_date",
            default=None,
        )
        parser.add_argument(
            "--forecast",
            action="store_true",
            dest="forecast",
            default=False,
            help="If True, plot forecasts for each interest rate",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
        )
        if ns_parser:
            if ns_parser.short is None and ns_parser.long is None:
                console.print(
                    "[red]Please provide at least one country to plot "
                    "with --short (3 months) and/or --long (10 years).[/red]"
                )
            else:
                short_term_countries = (
                    list_from_str(ns_parser.short.lower()) if ns_parser.short else None
                )
                long_term_countries = (
                    list_from_str(ns_parser.long.lower()) if ns_parser.long else None
                )
                oecd_view.plot_treasuries(
                    short_term=short_term_countries,
                    long_term=long_term_countries,
                    forecast=ns_parser.forecast,
                    start_date=ns_parser.start_date,
                    end_date=ns_parser.end_date,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )

    @log_start_end(log=logger)
    def call_tmc(self, other_args: List[str]):
        """Process tmc command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tmc",
            description="Get 10-Year Treasury Constant Maturity Minus Selected Treasury Constant Maturity data. "
            "Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values "
            "of auctioned U.S. Treasuries. The value is obtained by the U.S. Treasury on a daily basis "
            "through interpolation of the Treasury yield curve which, in turn, is based on closing "
            "bid-yields of actively-traded Treasury securities.",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Selected treasury constant maturity to subtract",
            default="3_month",
            choices=fred_model.TMC_PARAMETER_TO_FRED_ID.keys(),
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            fred_view.plot_tmc(
                parameter=ns_parser.parameter,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_ffrmc(self, other_args: List[str]):
        """Process ffrmc command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ffrmc",
            description="Get Selected Treasury Constant Maturity Minus Federal Funds Rate. "
            "Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values "
            "of auctioned U.S. Treasuries. The value is obtained by the U.S. Treasury on a daily basis "
            "through interpolation of the Treasury yield curve which, in turn, is based on closing "
            "bid-yields of actively-traded Treasury securities.",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Selected Treasury Constant Maturity",
            default="10_year",
            choices=fred_model.FFRMC_PARAMETER_TO_FRED_ID.keys(),
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            fred_view.plot_ffrmc(
                parameter=ns_parser.parameter,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_ycrv(self, other_args: List[str]):
        """Process ycrv command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ycrv",
            description="Generate US yield curve. \nThe yield curve shows the bond rates"
            "at different maturities.\nThe graphic depiction of the relationship between the yield on bonds of the "
            "same credit quality but different maturities is known as the yield curve. In the past, "
            "most market participants have constructed yield curves from the observations of prices and "
            "yields in the Treasury market. Two reasons account for this tendency. First, "
            "Treasury securities are viewed as free of default risk, and differences in creditworthiness "
            "do not affect yield estimates. Second, as the most active bond market, the Treasury market "
            "offers the fewest problems of illiquidity or infrequent trading. The key function of the "
            "Treasury yield curve is to serve as a benchmark for pricing bonds and setting yields in "
            "other sectors of the debt market.\nIt is clear that the market’s expectations of future rate "
            "changes are one important determinant of the yield-curve shape. For example, "
            "a steeply upward-sloping curve may indicate market expectations of near-term Fed tightening "
            "or of rising inflation. However, it may be too restrictive to assume that the yield "
            "differences across bonds with different maturities only reflect the market’s rate "
            "expectations. The well-known pure expectations hypothesis has such an extreme implication. "
            "The pure expectations hypothesis asserts that all government bonds have the same near-term "
            "expected return (as the nominally riskless short-term bond) because the return-seeking "
            "activity of risk-neutral traders removes all expected return differentials across bonds.",
        )
        parser.add_argument(
            "-d",
            "--date",
            type=valid_date,
            help="Date to get data from FRED. If not supplied, the most recent entry will be used.",
            dest="date",
            default=None,
        )
        parser.add_argument(
            "-i",
            "--inflation-adjusted",
            action="store_true",
            help="Whether to plot the inflation adjusted yield curve.",
            dest="inflation_adjusted",
            default=False,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
        )
        if ns_parser:
            fred_view.display_yield_curve(
                date=ns_parser.date.strftime("%Y-%m-%d") if ns_parser.date else "",
                inflation_adjusted=ns_parser.inflation_adjusted,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_ecbycrv(self, other_args: List[str]):
        """Process ecbycrv command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ecbycrv",
            description="Generate euro area yield curve from ECB. \nThe yield curve shows the bond rates"
            "at different maturities.\nThe graphic depiction of the relationship between the yield on bonds of the "
            "same credit quality but different maturities is known as the yield curve. In the past, "
            "most market participants have constructed yield curves from the observations of prices and "
            "yields in the Treasury market. Two reasons account for this tendency. First, "
            "Treasury securities are viewed as free of default risk, and differences in creditworthiness "
            "do not affect yield estimates. Second, as the most active bond market, the Treasury market "
            "offers the fewest problems of illiquidity or infrequent trading. The key function of the "
            "Treasury yield curve is to serve as a benchmark for pricing bonds and setting yields in "
            "other sectors of the debt market.\nIt is clear that the market’s expectations of future rate "
            "changes are one important determinant of the yield-curve shape. For example, "
            "a steeply upward-sloping curve may indicate market expectations of near-term Fed tightening "
            "or of rising inflation. However, it may be too restrictive to assume that the yield "
            "differences across bonds with different maturities only reflect the market’s rate "
            "expectations. The well-known pure expectations hypothesis has such an extreme implication. "
            "The pure expectations hypothesis asserts that all government bonds have the same near-term "
            "expected return (as the nominally riskless short-term bond) because the return-seeking "
            "activity of risk-neutral traders removes all expected return differentials across bonds.",
        )
        parser.add_argument(
            "-d",
            "--date",
            type=valid_date,
            help="Date to get data from ECB. If not supplied, the most recent entry will be used.",
            dest="date",
            default=None,
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Selected type of yield curve",
            default="spot_rate",
            choices=["spot_rate", "instantaneous_forward", "par_yield"],
        )
        parser.add_argument(
            "--detailed",
            action="store_true",
            dest="detailed",
            default=False,
            help="If True, returns detailed data. Note that this is very slow.",
        )
        parser.add_argument(
            "--any-rating",
            action="store_true",
            dest="any_rating",
            default=False,
            help="If False, it only returns rates for AAA rated bonds. If True, it returns rates for all bonds.",
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            raw=True,
        )
        if ns_parser:
            ecb_view.display_ecb_yield_curve(
                date=ns_parser.date.strftime("%Y-%m-%d") if ns_parser.date else "",
                yield_type=ns_parser.parameter,
                detailed=ns_parser.detailed,
                any_rating=ns_parser.any_rating,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_usrates(self, other_args: List[str]):
        """Process usrates command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="usrates",
            description="Plot various rates from the United States. This includes tbill (Treasury Bills), "
            "Constant Maturity treasuries (cmn) and Inflation Protected Treasuries (TIPS)",
        )
        parser.add_argument(
            "-m",
            "--maturity",
            dest="maturity",
            type=str,
            help="Specific Treasury Bill Secondary Market Rate data to plot",
            default="3_month",
            choices=list(fred_model.USARATES_TO_FRED_ID.keys()),
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Choose either tbill (Treasury Bills), Constant Maturity treasuries (cmn) "
            "or Inflation Protected Treasuries (TIPS)",
            default="tbill",
            choices=["tbill", "cmn", "tips"],
        )
        parser.add_argument(
            "-o",
            "--options",
            dest="options",
            action="store_true",
            help="See the available options",
            default=False,
        )

        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default="1980-01-01",
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES, raw=True
        )
        if ns_parser:
            if ns_parser.options:
                print_rich_table(
                    pd.DataFrame.from_dict(fred_model.USARATES_TO_FRED_ID).T.fillna(
                        "-"
                    ),
                    show_index=True,
                    title="Available options including FRED Series name",
                )
            elif (
                ns_parser.parameter
                not in fred_model.USARATES_TO_FRED_ID[ns_parser.maturity]
            ):
                console.print(
                    f"[red]Maturity {ns_parser.maturity.replace('_', ' ')} is not "
                    f"available for {ns_parser.parameter}. Please use 'usrates --options'.[/red]"
                )
            else:
                fred_view.plot_usrates(
                    parameter=ns_parser.parameter,
                    maturity=ns_parser.maturity,
                    start_date=ns_parser.start_date,
                    end_date=ns_parser.end_date,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )

    @log_start_end(log=logger)
    def call_icebofa(self, other_args: List[str]):
        """Process icebofa command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="icebofa",
            description="Plot various rates from the United States. This includes tbill (Treasury Bills), "
            "Constant Maturity treasuries (cmn) and Inflation Protected Treasuries (TIPS)",
        )

        parser.add_argument(
            "-t",
            "--type",
            dest="data_type",
            type=str,
            help="What type you'd like to collect data for",
            default="yield",
            choices=fred_model.ICE_BOFA_TO_OPTIONS["Type"],
        )

        parser.add_argument(
            "-c",
            "--category",
            dest="category",
            type=str,
            help="What category you'd like to collect data for",
            default="all",
            choices=fred_model.ICE_BOFA_TO_OPTIONS["Category"],
        )

        parser.add_argument(
            "-a",
            "--area",
            dest="area",
            type=str,
            help="What region you'd like to collect data for",
            default="us",
            choices=fred_model.ICE_BOFA_TO_OPTIONS["Area"],
        )

        parser.add_argument(
            "-g",
            "--grade",
            dest="grade",
            type=str,
            help="What grade you'd like to collect data for",
            default="non_sovereign",
            choices=fred_model.ICE_BOFA_TO_OPTIONS["Grade"],
        )

        parser.add_argument(
            "-o",
            "--options",
            dest="options",
            action="store_true",
            help="See the available options",
            default=False,
        )

        parser.add_argument(
            "-d",
            "--description",
            dest="description",
            action="store_true",
            help="Whether to provide a description of the data.",
            default=False,
        )

        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default="1980-01-01",
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES, raw=True
        )
        if ns_parser:
            fred_view.plot_icebofa(
                data_type=ns_parser.data_type,
                category=ns_parser.category,
                area=ns_parser.area,
                grade=ns_parser.grade,
                options=ns_parser.options,
                description=ns_parser.description,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_moody(self, other_args: List[str]):
        """Process moody command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="moody",
            description="Moody's Aaa and Baa are investment bonds that acts as an index of "
            "the performance of all bonds given an Aaa or Baa rating by Moody's Investors Service respectively"
            "These corporate bonds often are used in macroeconomics as an alternative to the federal ten-year "
            "Treasury Bill as an indicator of the interest rate.",
        )

        parser.add_argument(
            "-t",
            "--type",
            dest="data_type",
            type=str,
            help="What type you'd like to collect data for",
            default="aaa",
            choices=fred_view.MOODY_TO_OPTIONS["Type"].keys(),
        )

        parser.add_argument(
            "--spread",
            dest="spread",
            type=str,
            help="Whether you want to show the spread",
            default=None,
            choices=fred_view.MOODY_TO_OPTIONS["Spread"],
        )

        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default="1980-01-01",
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES, raw=True
        )
        if ns_parser:
            fred_view.plot_moody(
                data_type=ns_parser.data_type,
                spread=ns_parser.spread,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_cp(self, other_args: List[str]):
        """Process cp command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cp",
            description="Commercial paper (CP) consists of short-term, promissory notes "
            "issued primarily by corporations. Maturities range up to 270 days but average "
            "about 30 days. Many companies use CP to raise cash needed for current "
            "transactions, and many find it to be a lower-cost alternative to bank loans.",
        )

        parser.add_argument(
            "-m",
            "--maturity",
            dest="maturity",
            type=str,
            help="What type you'd like to collect data for",
            default="30d",
            choices=fred_model.CP_TO_OPTIONS["Maturity"],
        )

        parser.add_argument(
            "-c",
            "--category",
            dest="category",
            type=str,
            help="What category you'd like to collect data for",
            default="financial",
            choices=fred_model.CP_TO_OPTIONS["Category"],
        )

        parser.add_argument(
            "-g",
            "--grade",
            dest="grade",
            type=str,
            help="What grade you'd like to collect data for",
            default="aa",
            choices=fred_model.CP_TO_OPTIONS["Grade"],
        )

        parser.add_argument(
            "-o",
            "--options",
            dest="options",
            action="store_true",
            help="See the available options",
            default=False,
        )

        parser.add_argument(
            "-d",
            "--description",
            dest="description",
            action="store_true",
            help="Whether to provide a description of the data.",
            default=False,
        )

        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default="1980-01-01",
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES, raw=True
        )
        if ns_parser:
            fred_view.plot_cp(
                maturity=ns_parser.maturity,
                category=ns_parser.category,
                grade=ns_parser.grade,
                options=ns_parser.options,
                description=ns_parser.description,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_spot(self, other_args: List[str]):
        """Process spot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="spot",
            description="The spot rate for any maturity is the yield on a bond that provides "
            "a single payment at that maturity.  This is a zero coupon bond.  Because each "
            "spot rate pertains to a single cashflow, it is the relevant interest rate "
            "concept for discounting a pension liability at the same maturity.",
        )

        parser.add_argument(
            "-m",
            "--maturity",
            dest="maturity",
            type=str,
            help="What maturity you'd like to collect data for",
            default="10y",
        )

        parser.add_argument(
            "-c",
            "--category",
            dest="category",
            type=str,
            help="What category you'd like to collect data for",
            default="spot_rate",
        )

        parser.add_argument(
            "-d",
            "--description",
            dest="description",
            action="store_true",
            help="Whether to provide a description of the data.",
            default=False,
        )

        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default="1980-01-01",
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES, raw=True
        )
        if ns_parser:
            maturity = [m.replace(".0", "") for m in list_from_str(ns_parser.maturity)]
            category = list_from_str(ns_parser.category)

            fred_view.plot_spot(
                maturity=maturity,
                category=category,
                description=ns_parser.description,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_hqm(self, other_args: List[str]):
        """Process hqdm command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="hqm",
            description="The HQM yield curve represents the high quality corporate bond market, i.e., "
            "corporate bonds rated AAA, AA, or A.  The HQM curve contains two regression terms. These "
            "terms are adjustment factors that blend AAA, AA, and A bonds into a single HQM yield curve "
            "that is the market-weighted average (MWA) quality of high quality bonds.",
        )

        parser.add_argument(
            "-d",
            "--date",
            dest="date",
            type=valid_date,
            help="Define the date of the yield curve.",
            default=None,
        )

        parser.add_argument(
            "-p",
            "--par",
            dest="par",
            action="store_true",
            help="Whether to include the Par Yield.",
            default=False,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES, raw=True
        )
        if ns_parser:
            fred_view.plot_hqm(
                date=ns_parser.date.strftime("%Y-%m-%d") if ns_parser.date else "",
                par=ns_parser.par,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_icespread(self, other_args: List[str]):
        """Process icespread command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="icespread",
            description="Plot various rates from the United States. This includes tbill (Treasury Bills), "
            "Constant Maturity treasuries (cmn) and Inflation Protected Treasuries (TIPS)",
        )

        parser.add_argument(
            "-c",
            "--category",
            dest="category",
            type=str,
            help="What category you'd like to collect data for",
            default="all",
            choices=fred_model.ICE_BOFA_TO_OPTIONS["Category"],
        )

        parser.add_argument(
            "-a",
            "--area",
            dest="area",
            type=str,
            help="What region you'd like to collect data for",
            default="us",
            choices=fred_model.ICE_BOFA_TO_OPTIONS["Area"],
        )

        parser.add_argument(
            "-g",
            "--grade",
            dest="grade",
            type=str,
            help="What grade you'd like to collect data for",
            default="non_sovereign",
            choices=fred_model.ICE_BOFA_TO_OPTIONS["Grade"],
        )

        parser.add_argument(
            "-o",
            "--options",
            dest="options",
            action="store_true",
            help="See the available options",
            default=False,
        )

        parser.add_argument(
            "-d",
            "--description",
            dest="description",
            action="store_true",
            help="Whether to provide a description of the data.",
            default=False,
        )

        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default="1980-01-01",
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES, raw=True
        )
        if ns_parser:
            fred_view.plot_icebofa(
                data_type="spread",
                category=ns_parser.category,
                area=ns_parser.area,
                grade=ns_parser.grade,
                options=ns_parser.options,
                description=ns_parser.description,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                raw=ns_parser.raw,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_tbffr(self, other_args: List[str]):
        """Process tbffr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tbffr",
            description="Get Selected Treasury Bill Minus Federal Funds Rate.",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Selected Treasury Bill",
            default="3_month",
            choices=fred_model.TBFFR_PARAMETER_TO_FRED_ID.keys(),
        )
        parser.add_argument(
            "-s",
            "--start",
            dest="start_date",
            type=valid_date,
            help="Starting date (YYYY-MM-DD) of data",
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            dest="end_date",
            type=valid_date,
            help="Ending date (YYYY-MM-DD) of data",
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            fred_view.plot_tbffr(
                parameter=ns_parser.parameter,
                start_date=ns_parser.start_date,
                end_date=ns_parser.end_date,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )
