""" Futures Controller """
__docformat__ = "numpy"

# pylint:disable=too-many-lines

import argparse
import logging
from datetime import datetime, timedelta
from typing import List

from openbb_terminal.custom_prompt_toolkit import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.fixedincome import ecb_view, nyfed_view
from openbb_terminal.fixedincome import fred_view

from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    valid_date,
)
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText
from openbb_terminal.menu import session

logger = logging.getLogger(__name__)


class FixedIncomeController(BaseController):
    """Fixed Income Controller class"""

    CHOICES_COMMANDS = [
        "estr",
        "sofr",
        "sonia",
        "ameribor",
        "ffer",
        "fftr",
        "effr",
        "obfr",
        "iorb",
        "projection",
        "oldprojection",
        "dwpcr",
    ]

    PATH = "/fixedincome/"
    CHOICES_GENERATION = True

    estr_parameter_to_fred_id = {
        "volume_weighted_trimmed_mean_rate": "ECBESTRVOLWGTTRMDMNRT",
        "total_volume": "ECBESTRTOTVOL",
        "number_of_transactions": "ECBESTRNUMTRANS",
        "rate_at_75th_percentile_of_volume": "ECBESTRRT75THPCTVOL",
        "number_of_active_banks": "ECBESTRNUMACTBANKS",
        "share_of_volume_of_the_5_largest_active_banks": "ECBESTRSHRVOL5LRGACTBNK",
        "rate_at_25th_percentile_of_volume": "ECBESTRRT25THPCTVOL",
    }
    estr_parameter_to_ecb_id = {
        "volume_weighted_trimmed_mean_rate": "EST.B.EU000A2X2A25.WT",
        "total_volume": "EST.B.EU000A2X2A25.TT",
        "number_of_transactions": "EST.B.EU000A2X2A25.NT",
        "rate_at_75th_percentile_of_volume": "EST.B.EU000A2X2A25.R75",
        "number_of_active_banks": "EST.B.EU000A2X2A25.NB",
        "share_of_volume_of_the_5_largest_active_banks": "EST.B.EU000A2X2A25.VL",
        "rate_at_25th_percentile_of_volume": "EST.B.EU000A2X2A25.R25",
    }
    sofr_parameter_to_fred_id = {
        "overnight": "SOFR",
        "30_day": "SOFR30DAYAVG",
        "90_day": "SOFR90DAYAVG",
        "180_day": "SOFR180DAYAVG",
        "index": "SOFRINDEX",
    }
    sonia_parameter_to_fred_id = {
        "rate": "IUDSOIA",
        "index": "IUDZOS2",
        "10th_percentile": "IUDZLS6",
        "25th_percentile": "IUDZLS7",
        "75th_percentile": "IUDZLS8",
        "90th_percentile": "IUDZLS9",
        "total_nominal_value": "IUDZLT2",
    }
    ameribor_parameter_to_fred_id = {
        "overnight": "AMERIBOR",
        "term_30": "AMBOR30T",
        "term_90": "AMBOR90T",
        "1_week_term_structure": "AMBOR1W",
        "1_month_term_structure": "AMBOR1M",
        "3_month_term_structure": "AMBOR3M",
        "6_month_term_structure": "AMBOR6M",
        "1_year_term_structure": "AMBOR1Y",
        "2_year_term_structure": "AMBOR2Y",
        "30_day_ma": "AMBOR30",
        "90_day_ma": "AMBOR90",
    }
    ffer_parameter_to_fred_id = {
        "monthly": "FEDFUNDS",
        "daily": "DFF",
        "weekly": "FF",
        "daily_excl_weekend": "RIFSPFFNB",
        "annual": "RIFSPFFNA",
        "biweekly": "RIFSPFFNBWAW",
    }
    effr_parameter_to_fred_id = {
        "rate": "EFFR",
        "volume": "EFFRVOL",
        "1th_percentile": "EFFR1",
        "25th_percentile": "EFFR25",
        "75th_percentile": "EFFR75",
        "99th_percentile": "EFFR99",
    }
    effr_parameter_to_nyfed_id = {
        "rate": "percentRate",
        "volume": "volumeInBillions",
        "1th_percentile": "percentPercentile1",
        "25th_percentile": "percentPercentile25",
        "75th_percentile": "percentPercentile75",
        "99th_percentile": "percentPercentile99",
    }
    obfr_parameter_to_fred_id = {
        "rate": "OBFR",
        "volume": "OBFRVOL",
        "1th_percentile": "EFFR1",
        "25th_percentile": "EFFR25",
        "75th_percentile": "EFFR75",
        "99th_percentile": "EFFR99",
    }
    dwpcr_parameter_to_fred_id = {
        "daily_excl_weekend": "DPCREDIT",
        "monthly": "MPCREDIT",
        "weekly": "WPCREDIT",
        "daily": "RIFSRPF02ND",
        "annual": "RIFSRPF02NA",
    }

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        if session and obbff.USE_PROMPT_TOOLKIT:
            self.choices: dict = self.choices_default
            self.completer = NestedCompleter.from_nested_dict(self.choices)  # type: ignore

    def print_help(self):
        """Print help"""
        mt = MenuText("fixedincome/")
        mt.add_info("_reference_rates_")
        mt.add_cmd("estr")
        mt.add_cmd("sofr")
        mt.add_cmd("sonia")
        mt.add_cmd("ameribor")
        mt.add_raw("\n")
        mt.add_info("_central_bank_rates_")
        mt.add_cmd("ffer")
        mt.add_cmd("fftr")
        mt.add_cmd("effr")
        mt.add_cmd("obfr")
        mt.add_cmd("iorb")
        mt.add_cmd("projection")
        mt.add_cmd("oldprojection")
        mt.add_cmd("dwpcr")

        console.print(text=mt.menu_text, menu="Fixed Income")

    @log_start_end(log=logger)
    def call_estr(self, other_args: List[str]):
        """Process estr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="estr",
            description="Get Euro Short-Term Rate data",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Specific Euro Short-Term Rate data to retrieve",
            default="volume_weighted_trimmed_mean_rate",
            choices=list(self.estr_parameter_to_fred_id.keys()),
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
                    self.estr_parameter_to_fred_id[ns_parser.parameter],
                    ns_parser.start_date,
                    ns_parser.end_date,
                    ns_parser.export,
                )
            elif ns_parser.source == "ECB":
                ecb_view.plot_estr(
                    self.estr_parameter_to_ecb_id[ns_parser.parameter],
                    ns_parser.start_date,
                    ns_parser.end_date,
                    ns_parser.export,
                )

    @log_start_end(log=logger)
    def call_sofr(self, other_args: List[str]):
        """Process sofr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sofr",
            description="Get Secured Overnight Financing Rate (SOFR) data",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Specific SOFR data to retrieve",
            default="overnight",
            choices=list(self.sofr_parameter_to_fred_id.keys()),
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
            if ns_parser.source == "FRED":
                fred_view.plot_sofr(
                    self.sofr_parameter_to_fred_id[ns_parser.parameter],
                    ns_parser.start_date,
                    ns_parser.end_date,
                    ns_parser.export,
                )
            elif ns_parser.source == "NYFED":
                nyfed_view.plot_sofr(
                    ns_parser.parameter,
                    ns_parser.start_date,
                    ns_parser.end_date,
                    ns_parser.export,
                )

    @log_start_end(log=logger)
    def call_sonia(self, other_args: List[str]):
        """Process sonia command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sonia",
            description="Get Sterling Overnight Index Average (SONIA) data",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Specific SONIA data to retrieve",
            default="rate",
            choices=list(self.sonia_parameter_to_fred_id.keys()),
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
                self.sonia_parameter_to_fred_id[ns_parser.parameter],
                ns_parser.start_date,
                ns_parser.end_date,
                ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_ameribor(self, other_args: List[str]):
        """Process ameribor command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ameribor",
            description="Get American Interbank Offered Rate (AMERIBOR) data",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Specific AMERIBOR data to retrieve",
            default="overnight",
            choices=list(self.ameribor_parameter_to_fred_id.keys()),
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
                self.ameribor_parameter_to_fred_id[ns_parser.parameter],
                ns_parser.start_date,
                ns_parser.end_date,
                ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_ffer(self, other_args: List[str]):
        """Process ffer command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ffer",
            description="Get Federal Funds Effective Rate data\nA bank rate is the interest rate a nation's central "
            "bank charges to its domestic banks to borrow money. The rates central banks charge are set "
            "to stabilize the economy. In the United States, the Federal Reserve System's Board of "
            "Governors set the bank rate, also known as the discount rate.",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Specific Federal Funds Effective Rate data to retrieve",
            default="monthly",
            choices=list(self.ffer_parameter_to_fred_id.keys()),
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
            fred_view.plot_ffer(
                self.ffer_parameter_to_fred_id[ns_parser.parameter],
                ns_parser.start_date,
                ns_parser.end_date,
                ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_fftr(self, other_args: List[str]):
        """Process fftr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="fftr",
            description="Get Federal Funds Target Range data.\nA bank rate is the interest rate a nation's central "
            "bank charges to its domestic banks to borrow money. The rates central banks charge are set "
            "to stabilize the economy. In the United States, the Federal Reserve System's Board of "
            "Governors set the bank rate, also known as the discount rate.",
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
            if ns_parser.source == "FRED":
                fred_view.plot_fftr(
                    ns_parser.start_date,
                    ns_parser.end_date,
                    ns_parser.export,
                )
            elif ns_parser.source == "NYFED":
                nyfed_view.plot_fftr(
                    ns_parser.start_date,
                    ns_parser.end_date,
                    ns_parser.export,
                )

    @log_start_end(log=logger)
    def call_effr(self, other_args: List[str]):
        """Process effr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="effr",
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
            default="rate",
            choices=list(self.effr_parameter_to_fred_id.keys()),
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
            if ns_parser.source == "FRED":
                fred_view.plot_effr(
                    self.effr_parameter_to_fred_id[ns_parser.parameter],
                    ns_parser.start_date,
                    ns_parser.end_date,
                    ns_parser.export,
                )
            elif ns_parser.source == "NYFED":
                nyfed_view.plot_effr(
                    self.effr_parameter_to_nyfed_id[ns_parser.parameter],
                    ns_parser.start_date,
                    ns_parser.end_date,
                    ns_parser.export,
                )

    @log_start_end(log=logger)
    def call_obfr(self, other_args: List[str]):
        """Process obfr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="obfr",
            description="Get Overnight Bank Funding Rate data.\nA bank rate is the interest rate a nation's central "
            "bank charges to its domestic banks to borrow money. The rates central banks charge are set "
            "to stabilize the economy. In the United States, the Federal Reserve System's Board of "
            "Governors set the bank rate, also known as the discount rate.",
        )
        parser.add_argument(
            "-p",
            "--parameter",
            dest="parameter",
            type=str,
            help="Specific Overnight Bank Funding Rate data to retrieve",
            default="rate",
            choices=list(self.obfr_parameter_to_fred_id.keys()),
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
            if ns_parser.source == "FRED":
                fred_view.plot_obfr(
                    self.obfr_parameter_to_fred_id[ns_parser.parameter],
                    ns_parser.start_date,
                    ns_parser.end_date,
                    ns_parser.export,
                )
            elif ns_parser.source == "NYFED":
                nyfed_view.plot_obfr(
                    self.effr_parameter_to_nyfed_id[ns_parser.parameter],
                    ns_parser.start_date,
                    ns_parser.end_date,
                    ns_parser.export,
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
                ns_parser.start_date,
                ns_parser.end_date,
                ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_projection(self, other_args: List[str]):
        """Process projection command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="projection",
            description="Get FOMC Summary of Economic Projections for the Fed Funds Rate.\nA bank rate is the "
            "interest rate a nation's central bank charges to its domestic banks to borrow money. The "
            "rates central banks charge are set to stabilize the economy. In the United States, "
            "the Federal Reserve System's Board of Governors set the bank rate, also known as the "
            "discount rate.",
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
            fred_view.plot_projection(
                ns_parser.start_date,
                ns_parser.end_date,
                ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_oldprojection(self, other_args: List[str]):
        """Process oldprojection command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="oldprojection",
            description="Get Longer Run FOMC Summary of Economic Projections for the Fed Funds Rate.\nA bank rate is "
            "the interest rate a nation's central bank charges to its domestic banks to borrow money. The "
            "rates central banks charge are set to stabilize the economy. In the United States, "
            "the Federal Reserve System's Board of Governors set the bank rate, also known as the "
            "discount rate.",
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
            fred_view.plot_oldprojection(
                ns_parser.start_date,
                ns_parser.end_date,
                ns_parser.export,
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
            choices=list(self.dwpcr_parameter_to_fred_id.keys()),
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
                self.dwpcr_parameter_to_fred_id[ns_parser.parameter],
                ns_parser.start_date,
                ns_parser.end_date,
                ns_parser.export,
            )
