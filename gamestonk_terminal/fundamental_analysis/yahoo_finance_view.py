""" Yahoo Finance View """
__docformat__ = "numpy"

import argparse
from typing import List
from datetime import datetime
import yfinance as yf
import pandas as pd

from gamestonk_terminal.fundamental_analysis.fa_helper import clean_df_index
from gamestonk_terminal.helper_funcs import (
    long_number_format,
    parse_known_args_and_warn,
)


def info(other_args: List[str], ticker: str):
    """Yahoo Finance ticker info

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="info",
        description="""
            Print information about the company. The following fields are expected:
            Zip, Sector, Full time employees, Long business summary, City, Phone, State, Country,
            Website, Max age, Address, Industry, Previous close, Regular market open, Two hundred
            day average, Payout ratio, Regular market day high, Average daily volume 10 day,
            Regular market previous close, Fifty day average, Open, Average volume 10 days, Beta,
            Regular market day low, Price hint, Currency, Trailing PE, Regular market volume,
            Market cap, Average volume, Price to sales trailing 12 months, Day low, Ask, Ask size,
            Volume, Fifty two week high, Forward PE, Fifty two week low, Bid, Tradeable, Bid size,
            Day high, Exchange, Short name, Long name, Exchange timezone name, Exchange timezone
            short name, Is esg populated, Gmt off set milliseconds, Quote type, Symbol, Message
            board id, Market, Enterprise to revenue, Profit margins, Enterprise to ebitda, 52 week
            change, Forward EPS, Shares outstanding, Book value, Shares short, Shares percent
            shares out, Last fiscal year end, Held percent institutions, Net income to common,
            Trailing EPS, Sand p52 week change, Price to book, Held percent insiders, Next fiscal
            year end, Most recent quarter, Short ratio, Shares short previous month date, Float
            shares, Enterprise value, Last split date, Last split factor, Earnings quarterly growth,
            Date short interest, PEG ratio, Short percent of float, Shares short prior month,
            Regular market price, Logo_url. [Source: Yahoo Finance]
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        stock = yf.Ticker(ticker)
        df_info = pd.DataFrame(stock.info.items(), columns=["Metric", "Value"])
        df_info = df_info.set_index("Metric")

        clean_df_index(df_info)

        if (
            "Last split date" in df_info.index
            and df_info.loc["Last split date"].values[0]
        ):
            df_info.loc["Last split date"].values[0] = datetime.fromtimestamp(
                df_info.loc["Last split date"].values[0]
            ).strftime("%d/%m/%Y")

        df_info = df_info.mask(df_info["Value"].astype(str).eq("[]")).dropna()
        df_info = df_info.applymap(lambda x: long_number_format(x))

        df_info = df_info.rename(
            index={
                "Address1": "Address",
                "Average daily volume10 day": "Average daily volume 10 day",
                "Average volume10days": "Average volume 10 days",
                "Price to sales trailing12 months": "Price to sales trailing 12 months",
            }
        )
        df_info.index = df_info.index.str.replace("eps", "EPS")
        df_info.index = df_info.index.str.replace("p e", "PE")
        df_info.index = df_info.index.str.replace("Peg", "PEG")

        pd.set_option("display.max_colwidth", None)

        if "Long business summary" in df_info.index:
            print(df_info.drop(index=["Long business summary"]).to_string(header=False))
            print("")
            print(df_info.loc["Long business summary"].values[0])
            print("")
        else:
            print(df_info.to_string(header=False))
            print("")

    except Exception as e:
        print(e, "\n")


def shareholders(other_args: List[str], ticker: str):
    """Yahoo Finance ticker shareholders

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="shrs",
        description="""Print Major, institutional and mutualfunds shareholders.
        [Source: Yahoo Finance]""",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        stock = yf.Ticker(ticker)
        pd.set_option("display.max_colwidth", None)

        # Major holders
        print("Major holders")
        df_major_holders = stock.major_holders
        df_major_holders[1] = df_major_holders[1].apply(
            lambda x: x.replace("%", "Percentage")
        )
        print(df_major_holders.to_string(index=False, header=False))
        print("")

        # Institutional holders
        print("Institutional holders")
        df_institutional_shareholders = stock.institutional_holders
        df_institutional_shareholders.columns = (
            df_institutional_shareholders.columns.str.replace("% Out", "Stake")
        )
        df_institutional_shareholders["Shares"] = df_institutional_shareholders[
            "Shares"
        ].apply(lambda x: long_number_format(x))
        df_institutional_shareholders["Value"] = df_institutional_shareholders[
            "Value"
        ].apply(lambda x: long_number_format(x))
        df_institutional_shareholders["Stake"] = df_institutional_shareholders[
            "Stake"
        ].apply(lambda x: str(f"{100 * x:.2f}") + " %")
        print(df_institutional_shareholders.to_string(index=False))
        print("")

        # Mutualfunds holders
        print("Mutualfunds holders")
        df_mutualfund_shareholders = stock.mutualfund_holders
        df_mutualfund_shareholders.columns = (
            df_mutualfund_shareholders.columns.str.replace("% Out", "Stake")
        )
        df_mutualfund_shareholders["Shares"] = df_mutualfund_shareholders[
            "Shares"
        ].apply(lambda x: long_number_format(x))
        df_mutualfund_shareholders["Value"] = df_mutualfund_shareholders["Value"].apply(
            lambda x: long_number_format(x)
        )
        df_mutualfund_shareholders["Stake"] = df_mutualfund_shareholders["Stake"].apply(
            lambda x: str(f"{100 * x:.2f}") + " %"
        )
        print(df_mutualfund_shareholders.to_string(index=False))
        print("")

    except Exception as e:
        print(e, "\n")


def sustainability(other_args: List[str], ticker: str):
    """Yahoo Finance ticker sustainability

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="sust",
        description="""
            Print sustainability values of the company. The following fields are expected:
            Palmoil, Controversialweapons, Gambling, Socialscore, Nuclear, Furleather, Alcoholic,
            Gmo, Catholic, Socialpercentile, Peercount, Governancescore, Environmentpercentile,
            Animaltesting, Tobacco, Totalesg, Highestcontroversy, Esgperformance, Coal, Pesticides,
            Adult, Percentile, Peergroup, Smallarms, Environmentscore, Governancepercentile,
            Militarycontract. [Source: Yahoo Finance]
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        stock = yf.Ticker(ticker)
        pd.set_option("display.max_colwidth", None)

        df_sustainability = stock.sustainability

        if df_sustainability is None:
            print(f"No sustainability information in Yahoo for {ticker}", "\n")
            return

        if df_sustainability.empty:
            print(f"No sustainability information in Yahoo for {ticker}", "\n")
            return

        clean_df_index(df_sustainability)

        df_sustainability = df_sustainability.rename(
            index={
                "Controversialweapons": "Controversial Weapons",
                "Socialpercentile": "Social Percentile",
                "Peercount": "Peer Count",
                "Governancescore": "Governance Score",
                "Environmentpercentile": "Environment Percentile",
                "Animaltesting": "Animal Testing",
                "Highestcontroversy": "Highest Controversy",
                "Environmentscore": "Environment Score",
                "Governancepercentile": "Governance Percentile",
                "Militarycontract": "Military Contract",
            }
        )

        print(df_sustainability.to_string(header=False))
        print("")

    except Exception as e:
        print(e, "\n")


def calendar_earnings(other_args: List[str], ticker: str):
    """Yahoo Finance ticker calendar earnings

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker : str
        Fundamental analysis ticker symbol
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="cal",
        description="""
            Calendar earnings of the company. Including revenue and earnings estimates.
            [Source: Yahoo Finance]
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        stock = yf.Ticker(ticker)
        df_calendar = stock.calendar

        if df_calendar.empty:
            print(f"No earnings calendar information in Yahoo for {ticker}")
            print("")
            return

        df_calendar.iloc[0, 0] = df_calendar.iloc[0, 0].date().strftime("%d/%m/%Y")
        df_calendar.iloc[:, 0] = df_calendar.iloc[:, 0].apply(
            lambda x: long_number_format(x)
        )

        print(f"Earnings Date: {df_calendar.iloc[:, 0]['Earnings Date']}")

        avg = df_calendar.iloc[:, 0]["Earnings Average"]
        low = df_calendar.iloc[:, 0]["Earnings Low"]
        high = df_calendar.iloc[:, 0]["Earnings High"]

        print(f"Earnings Estimate Avg: {avg} [{low}, {high}]")
        print(
            f"Revenue Estimate Avg:  {df_calendar.iloc[:, 0]['Revenue Average']} \
                [{df_calendar.iloc[:, 0]['Revenue Low']}, {df_calendar.iloc[:, 0]['Revenue High']}]"
        )
        print("")

    except Exception as e:
        print(e, "\n")
