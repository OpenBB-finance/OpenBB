"""Messari model"""
__docformat__ = "numpy"
# flake8: noqa
# pylint: disable=C0301,C0302

import logging
from typing import Any, Tuple

import pandas as pd
import requests

from openbb_terminal import config_terminal as cfg
from openbb_terminal.cryptocurrency.dataframe_helpers import (
    lambda_replace_underscores_in_column_names,
)
from openbb_terminal.cryptocurrency.due_diligence.pycoingecko_model import (
    get_coin_tokenomics,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import lambda_long_number_format
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

INTERVALS_TIMESERIES = ["5m", "15m", "30m", "1h", "1d", "1w"]

TIMESERIES = {
    "twitter.followers": {
        "title": "Twitter Followers",
        "description": "The number of followers of the asset's primary Twitter account",
    },
    "addr.bal.100k.ntv.cnt": {
        "title": "Addresses with balance greater than 100K native units",
        "description": "The sum count of unique addresses holding at least 100,000 native units as of the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "exch.bitmex.flow.in": {
        "title": "Bitmex Deposits",
        "description": "The sum USD value sent to Bitmex that interval.",
    },
    "exch.bitmex.flow.out": {
        "title": "Bitmex Withdrawals",
        "description": "The sum in native units withdrawn from Bitmex that interval.",
    },
    "txn.gas.limit": {
        "title": "Total Gas Limit",
        "description": "The sum gas limit of all transactions that interval.",
    },
    "addr.bal.100.cnt": {
        "title": "Addresses with balance greater than $100",
        "description": "The sum count of unique addresses holding at least one hundred dollars' worth of native units as of the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "exch.sply.usd": {
        "title": "Supply on Exchanges",
        "description": "The sum USD value of all native units held in hot or cold exchange wallets that interval.",
    },
    "sply.act.30d": {
        "title": "30 Days Active Supply",
        "description": "The sum of unique native units that transacted at least once in the trailing 30 days up to the end of that interval. Native units that transacted more than once are only counted once.",
    },
    "sply.rvv.180d": {
        "title": "180 Days Active Supply",
        "description": "The sum of all native unit balances last active at least 180 days ago that became active in this interval.",
    },
    "addr.bal.1.cnt": {
        "title": "Addresses with balance greater than $1",
        "description": "The sum count of unique addresses holding at least one dollars' worth of native units as of the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "txn.vol": {
        "title": "Transaction Volume",
        "description": "The sum USD value of all native units transferred (i.e., the aggregate size in USD of all transfers).",
    },
    "sply.addr.bal.100.ntv": {
        "title": "Supply in addresses with balance greater than 100 native units",
        "description": "The sum of all native units being held in addresses whose balance was 100 native units or greater at the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "sply.rvv.4y": {
        "title": "Supply Revived in Last 4 Years",
        "description": "The sum of all native unit balances last active at least 4 years ago that became active in this interval.",
    },
    "sply.top.100": {
        "title": "Supply in top 100 addresses",
        "description": "The sum of all native units held by the richest 100 addresses at the end of that time interval.",
    },
    "cg.sply.circ": {
        "title": "Circulating Supply (CoinGecko)",
        "description": "The circulating supply acknowledges that tokens may be held by projects/foundations which have no intent to sell down their positions, but which have not locked up supply in a formal contract. Thus, circulating supply does not include known project treasury holdings (which can be significant). Note that an investor must carefully consider both liquid and circulating supplies when evaluating an asset, and the two can vary significantly. A risk of depending entirely on circulating supply is that the number can change dramatically based on discretionary sales from project treasuries.",
    },
    "addr.bal.10k.ntv.cnt": {
        "title": "Addresses with balance greater than 10K native units",
        "description": "The sum count of unique addresses holding at least 10,000 native units as of the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "exch.bitfinex.flow.net.ntv": {
        "title": "Bitfinex Net Flows (Native Units)",
        "description": "The net native units value sent or withdrawn to/from Bitfinex that interval.",
    },
    "exch.binance.flow.net": {
        "title": "Binance Net Flows",
        "description": "The net USD value sent or withdrawn to/from Binance that interval.",
    },
    "telegram.users": {
        "title": "Telegram Users",
        "description": "The number of users in the asset's primary Telegram channel",
    },
    "exch.huobi.flow.out": {
        "title": "Huobi Withdrawals",
        "description": "The sum in US dollars withdrawn from Huobi that interval.",
    },
    "hash.rev": {
        "title": "Miner Revenue per Hash",
        "description": "The USD value of the mean miner reward per estimated hash unit performed during the period, also known as hashprice. The unit of hashpower measurement depends on the protocol.",
    },
    "txn.fee.med.ntv": {
        "title": "Median Transaction Fees (Native Units)",
        "description": "The median fee per transaction in native units that interval.",
    },
    "mcap.realized": {
        "title": "Realized Marketcap",
        "description": "The sum USD value based on the USD closing price on the day that a native unit last moved (i.e., last transacted) for all native units.",
    },
    "txn.fee.med": {
        "title": "Median Transaction Fees",
        "description": "The USD value of the median fee per transaction that interval.",
    },
    "sply.rvv.3y": {
        "title": "Supply Revived in Last 3 Years",
        "description": "The sum of all native unit balances last active at least 3 years ago that became active in this interval.",
    },
    "utxo.cnt": {
        "title": "UTXO Count",
        "description": "The sum count of unspent transaction outputs that interval.",
    },
    "utxo.age.avg": {
        "title": "Average UTXO Age",
        "description": "The simple average age in full days of all unspent transaction outputs.",
    },
    "utxo.loss.cnt": {
        "title": "UTXO in Loss Count",
        "description": "The sum count of unspent transaction outputs created on days where the closing price was higher than the closing price at the end of the period.",
    },
    "exch.bitmex.flow.out.ntv": {
        "title": "Bitmex Withdrawals (Native Units)",
        "description": "The sum in native units withdrawn from Bitmex that interval.",
    },
    "exch.kraken.flow.out.ntv": {
        "title": "Kraken Withdrawals (Native Units)",
        "description": "The sum in native units withdrawn from Kraken that interval.",
    },
    "sply.addr.bal.10": {
        "title": "Supply in addresses with balance greater than $10",
        "description": "The sum of all native units being held in addresses whose balance was $10 or greater at the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "sply.addr.bal.10k.ntv": {
        "title": "Supply in addresses with balance greater than 10K native units",
        "description": "The sum of all native units being held in addresses whose balance was 10K native units or greater at the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "addr.bal.0.01.ntv.cnt": {
        "title": "Addresses with balance greater than 0.01 native units",
        "description": "The sum count of unique addresses holding at least 0.01 native units as of the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "exch.flow.in.ntv": {
        "title": "Deposits on Exchanges (Native Units)",
        "description": "The amount of the asset sent to exchanges that interval, excluding exchange to exchange activity.",
    },
    "min.rev.usd": {
        "title": "Miner Revenue",
        "description": "The sum USD value of all miner revenue, which constitutes fees plus newly issued native units, represented as the US dollar amount earned if all native units were sold at the closing price on the same day.",
    },
    "sply.rvv.5y": {
        "title": "Supply Revived in Last 5 Years",
        "description": "The sum of all native unit balances last active at least 5 years ago that became active in this interval.",
    },
    "iss.rate.day": {
        "title": "Daily Issuance Rate",
        "description": "The percentage of new native units (continuous) issued over that interval divided by the current supply at the end of that interval. Also referred to as the daily inflation rate.",
    },
    "txn.fee.avg.ntv": {
        "title": "Average Transaction Fees (Native Units)",
        "description": "The mean fee per transaction in native units that interval.",
    },
    "txn.tfr.val.med": {
        "title": "Median Transfer Value",
        "description": "The median USD value transferred per transfer (i.e., the median size in USD of a transfer) between distinct addresses that interval.",
    },
    "sply.act.2y": {
        "title": "2 Year Active Supply",
        "description": "The sum of unique native units that transacted at least once in the trailing 2 years up to the end of that interval. Native units that transacted more than once are only counted once.",
    },
    "sply.shld": {
        "title": "Supply Shielded",
        "description": "The sum of all native units being held in shielded pool(s).",
    },
    "txn.cont.call.cnt": {
        "title": "Contract Calls Count",
        "description": "The sum count of contract calls executed across all transactions in that interval. A contract call is the invocation of a contract’s code by another contract or non-contract address. Failed invocations are counted. A single transaction can result in multiple contract calls.",
    },
    "txn.fee.avg": {
        "title": "Average Transaction Fees",
        "description": "The USD value of the mean fee per transaction that interval.",
    },
    "addr.act.rcv.cnt": {
        "title": "Active Addresses Count (Received)",
        "description": "The sum count of unique addresses that were active in the network (as a recipient of a ledger change) that interval.",
    },
    "addr.bal.100.ntv.cnt": {
        "title": "Addresses with balance greater than 100 native units",
        "description": "The sum count of unique addresses holding at least 100 native units as of the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "hashrate.30d": {
        "title": "30 day Average Hash Rate",
        "description": "The mean rate at which miners are solving hashes over the last 30 days. Hash rate is the speed at which computations are being completed across all miners in the network. The unit of measurement varies depending on the protocol.",
    },
    "nvt.adj.90d.ma": {
        "title": "Adjusted NVT 90-days MA",
        "description": "The ratio of the network value (or market capitalization, current supply) to the 90-day moving average of the adjusted transfer value. Also referred to as NVT.",
    },
    "sply.addr.bal.10.ntv": {
        "title": "Supply in addresses with balance greater than 10 native units",
        "description": "The sum of all native units being held in addresses whose balance was 10 native units or greater at the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "exch.sply.kraken": {
        "title": "Supply on Kraken",
        "description": "The sum USD value held by Kraken at the end of that interval.",
    },
    "new.iss.usd": {
        "title": "New Issuance",
        "description": "The sum USD value of new native units issued that interval. Only those native units that are issued by a protocol-mandated continuous emission schedule are included (i.e., units manually released from escrow or otherwise disbursed are not included).",
    },
    "sply.addr.bal.100k.ntv": {
        "title": "Supply in addresses with balance greater than 100K native units",
        "description": "The sum of all native units being held in addresses whose balance was 100K native units or greater at the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "sply.cont.usd": {
        "title": "Supply in contracts",
        "description": "The sum USD value being held by smart contracts.",
    },
    "txn.gas.limit.avg": {
        "title": "Average Gas Limit",
        "description": "The mean gas limit per transaction that interval.",
    },
    "txn.tfr.erc721.cnt": {
        "title": "ERC-721 Transfer Count",
        "description": "The sum count of ERC-721 transfers in that interval. Only transfers between two distinct addresses are counted. ERC-165 is used to determine a contract’s compliance with ERC-721.",
    },
    "txn.tfr.val.med.ntv": {
        "title": "Median Transfer Value (Native Units)",
        "description": "The median count of native units transferred per transfer (i.e., the median size of a transfer) between distinct addresses that interval.",
    },
    "addr.bal.10.ntv.cnt": {
        "title": "Addresses with balance greater than 10 native units",
        "description": "The sum count of unique addresses holding at least 10 native units as of the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "exch.bitfinex.flow.out.ntv": {
        "title": "Bitfinex Withdrawals (Native Units)",
        "description": "The sum in native units withdrawn from Bitfinex that interval.",
    },
    "sply.addr.bal.0.1.ntv": {
        "title": "Supply in addresses with balance greater than 0.1 native unit",
        "description": "The sum of all native units being held in addresses whose balance was 0.1 native units or greater at the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "txn.cnt.sec": {
        "title": "Transactions per Second Count",
        "description": "The sum count of transactions divided by the number of seconds that interval.",
    },
    "addr.bal.1k.ntv.cnt": {
        "title": "Addresses with balance greater than 1K native units",
        "description": "The sum count of unique addresses holding at least 1,000 native units as of the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "blk.hgt": {
        "title": "Block Height",
        "description": "The count of blocks from the genesis (first) block to the last block of that interval on the main chain.",
    },
    "exch.bitfinex.flow.net": {
        "title": "Bitfinex Net Flows",
        "description": "The net USD value sent or withdrawn to/from Bitfinex that interval.",
    },
    "exch.bitfinex.flow.in": {
        "title": "Bitfinex Deposits",
        "description": "The sum USD value sent to Bitfinex that interval.",
    },
    "sply.utxo.prof": {
        "title": "Supply in UTXOs in Profit (Native Units)",
        "description": "The sum of all native units held in unspent transaction outputs created on days where the closing price was lower than or equal to the closing price at the end of the period.",
    },
    "exch.huobi.flow.net.ntv": {
        "title": "Huobi Net Flows (Native Units)",
        "description": "The net native units value sent or withdrawn to/from Huobi that interval.",
    },
    "exch.sply.kraken.ntv": {
        "title": "Supply on Kraken (Native Units)",
        "description": "The sum in native units held by Kraken at the end of that interval.",
    },
    "hashrate.rev": {
        "title": "Miner Revenue per Hash per Second",
        "description": "The USD value of the mean miner reward per estimated hash unit performed during the period, also known as hashprice. The unit of hashpower measurement depends on the protocol.",
    },
    "sply.act.90d": {
        "title": "90 Days Active Supply",
        "description": "The sum of unique native units that transacted at least once in the trailing 90 days up to the end of that interval. Native units that transacted more than once are only counted once.",
    },
    "exch.bitfinex.flow.in.ntv": {
        "title": "Bitfinex Deposits (Native Units)",
        "description": "The sum in native units sent to Bitfinex that interval.",
    },
    "mcap.out": {
        "title": "Outstanding Marketcap",
        "description": "The sum USD value of the current supply. Also referred to as network value or market capitalization.",
    },
    "sply.act.1y": {
        "title": "1 Year Active Supply",
        "description": "The sum of unique native units that transacted at least once in the trailing 1 year up to the end of that interval. Native units that transacted more than once are only counted once.",
    },
    "exch.sply.binance.ntv": {
        "title": "Supply on Binance (Native Units)",
        "description": "The sum in native units held by Binance at the end of that interval.",
    },
    "sply.rvv.30d": {
        "title": "Supply Revived in Last 30 Days",
        "description": "The sum of all native unit balances last active at least 30 days ago that became active in this interval.",
    },
    "sply.top.10pct": {
        "title": "Supply in top 10% addresses",
        "description": "The sum of all native units held by the richest 10% of addresses at the end of that interval.",
    },
    "addr.bal.1.ntv.cnt": {
        "title": "Addresses with balance greater than 1 native units",
        "description": "The sum count of unique addresses holding at least 1 native unit as of the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "blk.cnt": {
        "title": "Block Count",
        "description": "The sum count of blocks created each day",
    },
    "txn.gas": {
        "title": "Gas Used",
        "description": "The sum gas used (i.e., paid) across all transactions that interval.",
    },
    "sply.addr.bal.1.ntv": {
        "title": "Supply in addresses with balance greater than 1 native unit",
        "description": "The sum of all native units being held in addresses whose balance was 1 native units or greater at the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "addr.bal.10k.cnt": {
        "title": "Addresses with balance greater than $10K",
        "description": "The sum count of unique addresses holding at least ten thousand dollars' worth of native units as of the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "exch.flow.in.ntv.incl": {
        "title": "Deposits on Exchanges - Inclusive (Native Units)",
        "description": "The amount of the asset sent to exchanges that interval, including exchange to exchange activity.",
    },
    "min.rev.ntv": {
        "title": "Miner Revenue (Native Units)",
        "description": "The sum of all miner revenue, which constitutes fees plus newly issued native units.",
    },
    "sply.act.evr": {
        "title": "Active Supply",
        "description": "The sum of unique native units that transacted at least once from genesis up to the end of that interval. Native units that transacted more than once are only counted once.",
    },
    "exch.kraken.flow.net": {
        "title": "Kraken Net Flows",
        "description": "The net USD value sent or withdrawn to/from Kraken that interval.",
    },
    "exch.gemini.flow.in": {
        "title": "Gemini Deposits",
        "description": "The sum USD value sent to Gemini that interval.",
    },
    "exch.sply.poloniex.ntv": {
        "title": "Supply on Poloniex (Native Units)",
        "description": "The sum in native units held by Poloniex at the end of that interval.",
    },
    "utxo.age.val.avg": {
        "title": "Value-weighted Average UTXO Age",
        "description": "The value-weighted average age in full days of all unspent transaction outputs.",
    },
    "mcap.dom": {
        "title": "Marketcap Dominance",
        "description": "The marketcap dominance is the asset's percentage share of total crypto circulating marketcap",
    },
    "reddit.subscribers": {
        "title": "Reddit Subscribers",
        "description": "The number of subscribers on the asset's primary subreddit",
    },
    "blk.int.avg": {
        "title": "Average Block Interval (seconds)",
        "description": "The mean absolute time (in seconds) between all the blocks created that interval.",
    },
    "blk.unc.rew": {
        "title": "Uncle Rewards",
        "description": "The sum USD value rewarded to miners for creating and including uncle blocks in that interval. This includes the uncle inclusion reward (for the main chain block miner) and the uncle rewards (for the uncle block miners).",
    },
    "sply.act.1d": {
        "title": "1 Day Active Supply",
        "description": "The sum of unique native units that transacted at least once in the trailing 1 days up to the end of that interval. Native units that transacted more than once are only counted once.",
    },
    "daily.shp": {
        "title": "Sharpe Ratio",
        "description": 'The Sharpe ratio (performance of the asset compared to a "risk-free" asset) over a window of time)',
    },
    "addr.bal.1m.cnt": {
        "title": "Addresses with balance greater than $1M",
        "description": "The sum count of unique addresses holding at least one million dollars' worth of native units as of the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "addr.bal.1k.cnt": {
        "title": "Addresses with balance greater than $1K",
        "description": "The sum count of unique addresses holding at least one thousand dollars' worth of native units as of the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "blk.unc.cnt": {
        "title": "Uncle Blocks Count",
        "description": "The sum count of uncle blocks mined in that interval.",
    },
    "sply.rvv.90d": {
        "title": "Supply Revived in Last 90 Days",
        "description": "The sum of all native unit balances last active at least 90 days ago that became active in this interval.",
    },
    "txn.tfr.val.adj.ntv": {
        "title": "Adjusted Transaction Volume (Native Units)",
        "description": "The sum of native units transferred between distinct addresses that interval removing noise and certain artifacts.",
    },
    "txn.tfr.avg.ntv": {
        "title": "Average Transfer Value (Native Units)",
        "description": "The sum value of native units transferred divided by the count of transfers (i.e., the mean size of a transfer) between distinct addresses that interval.",
    },
    "reddit.active.users": {
        "title": "Reddit Active Users",
        "description": "The number of active users on the asset's primary subreddit",
    },
    "exch.bittrex.flow.net.ntv": {
        "title": "Bittrex Net Flows (Native Units)",
        "description": "The net native units value sent or withdrawn to/from Bittrex that interval.",
    },
    "exch.sply.bitfinex": {
        "title": "Supply on Bitfinex",
        "description": "The sum USD value held by Bitfinex at the end of that interval.",
    },
    "sply.act.5y": {
        "title": "5 Year Active Supply",
        "description": "The sum of unique native units that transacted at least once in the trailing 5 years up to the end of that interval. Native units that transacted more than once are only counted once.",
    },
    "sply.act.180d": {
        "title": "180 Days Active Supply",
        "description": "The sum of unique native units that transacted at least once in the trailing 180 days up to the end of that interval. Native units that transacted more than once are only counted once.",
    },
    "sply.addr.bal.1": {
        "title": "Supply in addresses with balance greater than $1",
        "description": "The sum of all native units being held in addresses whose balance was $1 or greater at the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "sply.addr.bal.0.01.ntv": {
        "title": "Supply in addresses with balance greater than 0.01 native unit",
        "description": "The sum of all native units being held in addresses whose balance was 0.01 native units or greater at the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "addr.bal.10.cnt": {
        "title": "Addresses with balance greater than $10",
        "description": "The sum count of unique addresses holding at least ten dollars' worth of native units as of the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "exch.poloniex.flow.in": {
        "title": "Poloniex Deposits",
        "description": "The sum USD value sent to Poloniex that interval.",
    },
    "exch.sply.huobi": {
        "title": "Supply on Huobi",
        "description": "The sum USD value held by Huobi at the end of that interval.",
    },
    "fees.ntv": {
        "title": "Total Fees (Native Units)",
        "description": "The sum of all fees paid to miners in native units. Fees do not include new issuance.",
    },
    "price": {
        "title": "Price",
        "description": "Volume weighted average price computed using Messari Methodology",
    },
    "blk.size.byte": {
        "title": "Block Size (bytes)",
        "description": "The sum of the size (in bytes) of all blocks created each day",
    },
    "txn.cont.call.succ.cnt": {
        "title": "Successful Contract Calls Count",
        "description": "The sum count of contract calls successfully executed across all transactions in that interval. A contract call is the invocation of a contract’s code by another contract or non-contract address. Only successful executions are taken into account.",
    },
    "txn.tsfr.val.adj": {
        "title": "Adjusted Transaction Volume",
        "description": "The sum USD value of all native units transferred removing noise and certain artifacts.",
    },
    "exch.bitstamp.flow.net": {
        "title": "Bitstamp Net Flows",
        "description": "The net USD value sent or withdrawn to/from Bitstamp that interval.",
    },
    "iss.rate": {
        "title": "Annual Issuance Rate",
        "description": "The percentage of new native units (continuous) issued over that interval, extrapolated to one year (i.e., multiplied by 365), and divided by the current supply at the end of that interval. Also referred to as the annual inflation rate.",
    },
    "sply.addr.bal.100k": {
        "title": "Supply in addresses with balance greater than $100K",
        "description": "The sum of all native units being held in addresses whose balance was $100K or greater at the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "exch.sply.bitfinex.ntv": {
        "title": "Supply on Bitfinex (Native Units)",
        "description": "The sum in native units held by Bitfinex at the end of that interval.",
    },
    "sply.addr.bal.1m": {
        "title": "Supply in addresses with balance greater than $1M",
        "description": "The sum of all native units being held in addresses whose balance was $1M or greater at the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "exch.bitfinex.flow.out": {
        "title": "Bitfinex Withdrawals",
        "description": "The sum in US dollars withdrawn from Bitfinex that interval.",
    },
    "fees": {
        "title": "Total Fees",
        "description": "The sum USD value of all fees paid to miners that interval. Fees do not include new issuance.",
    },
    "exch.flow.in.usd.incl": {
        "title": "Deposits on Exchanges - Inclusive",
        "description": "The sum USD value sent to exchanges that interval, including exchange to exchange activity.",
    },
    "exch.bittrex.flow.out.ntv": {
        "title": "Bittrex Withdrawals (Native Units)",
        "description": "The sum in native units withdrawn from Bittrex that interval.",
    },
    "exch.sply.binance": {
        "title": "Supply on Binance",
        "description": "The sum USD value held by Binance at the end of that interval.",
    },
    "txn.tsfr.val.avg": {
        "title": "Average Transfer Value",
        "description": 'The sum USD value of native units transferred divided by the count of transfers (i.e., the mean "size" in USD of a transfer).',
    },
    "utxo.age.med": {
        "title": "Median UTXO Age",
        "description": "The median age in full days of all unspent transaction outputs, rounded down to the nearest day.",
    },
    "exch.huobi.flow.net": {
        "title": "Huobi Net Flows",
        "description": "The net USD value sent or withdrawn to/from Huobi that interval.",
    },
    "exch.huobi.flow.out.ntv": {
        "title": "Huobi Withdrawals (Native Units)",
        "description": "The sum in native units withdrawn from Huobi that interval.",
    },
    "sply.addr.bal.0.001.ntv": {
        "title": "Supply in addresses with balance greater than 0.001 native unit",
        "description": "The sum of all native units being held in addresses whose balance was 0.001 native units or greater at the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "exch.huobi.flow.in.ntv": {
        "title": "Huobi Deposits (Native Units)",
        "description": "The sum in native units sent to Huobi that interval.",
    },
    "exch.sply.bittrex.ntv": {
        "title": "Supply on Bittrex (Native Units)",
        "description": "The sum in native units held by Bittrex at the end of that interval.",
    },
    "fees.pct.rev": {
        "title": "Miner Revenue from Fees (%)",
        "description": "The percentage of miner revenue derived from fees that interval. This is equal to the fees divided by the miner revenue.",
    },
    "sply.addr.bal.10k": {
        "title": "Supply in addresses with balance greater than $10K",
        "description": "The sum of all native units being held in addresses whose balance was $10K or greater at the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "sply.act.10y": {
        "title": "10 Year Active Supply",
        "description": "The sum of unique native units that transacted at least once in the trailing 10 years up to the end of that interval. Native units that transacted more than once are only counted once.",
    },
    "exch.bitmex.flow.net": {
        "title": "Bitmex Net Flows",
        "description": "The net USD value sent or withdrawn to/from Bitmex that interval.",
    },
    "diff.avg": {
        "title": "Average Difficulty",
        "description": "The mean difficulty of finding a hash that meets the protocol-designated requirement (i.e., the difficulty of finding a new block) that interval. The requirement is unique to each applicable cryptocurrency protocol.",
    },
    "sply.out": {
        "title": "Outstanding Supply",
        "description": "The sum of all native units ever created and visible on the ledger (i.e., issued) at the end of that interval. For account-based protocols, only accounts with positive balances are counted.",
    },
    "sply.rvv.2y": {
        "title": "Supply Revived in Last 2 Years",
        "description": "The sum of all native unit balances last active at least 2 years ago that became active in this interval.",
    },
    "txn.tsfr.cnt": {
        "title": "Transactions Transfer Count",
        "description": "The sum count of transfers that interval. Transfers represent movements of native units from one ledger entity to another distinct ledger entity. Only transfers that are the result of a transaction and that have a positive (non-zero) value are counted.",
    },
    "exch.bitstamp.flow.out": {
        "title": "Bitstamp Withdrawals",
        "description": "The sum in US dollars withdrawn from Bitstamp that interval.",
    },
    "miner.sply.ntv": {
        "title": "Miner Supply (Native Units)",
        "description": "The sum of the balances of all mining entities. A mining entity is defined as an address that has been credited from a transaction debiting the 'FEES' or 'ISSUANCE' accounts.",
    },
    "sply.act.7d": {
        "title": "7 Days Active Supply",
        "description": "The sum of unique native units that transacted at least once in the trailing 7 days up to the end of that interval. Native units that transacted more than once are only counted once.",
    },
    "txn.cont.cnt": {
        "title": "Contracts Transactions Count",
        "description": "The sum count of transactions that invoked a contract in that interval. Failed transactions are counted but internal transactions are not (i.e., only the parent transaction is counted). A contract is a special address that contains and can execute code.",
    },
    "addr.bal.0.001.ntv.cnt": {
        "title": "Addresses with balance greater than 0.001 native units",
        "description": "The sum count of unique addresses holding at least 0.001 native units as of the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "blk.gas.limit.avg": {
        "title": "Average Gas Limit per Block",
        "description": "The mean gas limit of all blocks that interval.",
    },
    "exch.bitmex.flow.in.ntv": {
        "title": "Bitmex Deposits (Native Units)",
        "description": "The sum in native units sent to Bitmex that interval.",
    },
    "hashrate.rev.ntv": {
        "title": "Miner Revenue per Hash per Second (Native Units)",
        "description": "The mean daily miner reward per estimated hash unit per second performed during the period, in native units. The unit of hashpower measurement depends on the protocol.",
    },
    "exch.kraken.flow.in.ntv": {
        "title": "Kraken Deposits (Native Units)",
        "description": "The sum in native units sent to Kraken that interval.",
    },
    "sply.addr.bal.1k": {
        "title": "Supply in addresses with balance greater than $1K",
        "description": "The sum of all native units being held in addresses whose balance was $1K or greater at the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "txn.cont.dest.cnt": {
        "title": "Contract Destructions Count",
        "description": "The sum count of contracts successfully destroyed across all transactions in that interval. A contract is a special address that contains and can execute code.",
    },
    "exch.sply.bitstamp.ntv": {
        "title": "Supply on Bitstamp (Native Units)",
        "description": "The sum in native units held by Bitstamp at the end of that interval.",
    },
    "nvt.adj": {
        "title": "Adjusted NVT",
        "description": "The ratio of the network value (or market capitalization, current supply) divided by the adjusted transfer value. Also referred to as NVT.",
    },
    "sply.act.4y": {
        "title": "4 Year Active Supply",
        "description": "The sum of unique native units that transacted at least once in the trailing 4 years up to the end of that interval. Native units that transacted more than once are only counted once.",
    },
    "sply.rvv.7d": {
        "title": "Supply Revived in Last 7 Days",
        "description": "The sum of all native unit balances last active at least 7 days ago that became active in this interval.",
    },
    "txn.erc721.cnt": {
        "title": "ERC-721 Transactions Count",
        "description": "The sum count of transactions that resulted in any ERC-721 activity in that interval. Only transfers between two distinct addresses are counted. ERC-165 is used to determine a contract’s compliance with ERC-721. Only Transfer or Approval events are counted as activity. If a transaction results in more than 1 transfer or approval, it’s only counted once.",
    },
    "act.addr.cnt": {
        "title": "Active Addresses Count",
        "description": "The sum count of unique addresses that were active in the network (either as a recipient or originator of a ledger change) that interval. All parties in a ledger change action (recipients and originators) are counted. Individual addresses are not double-counted.",
    },
    "exch.poloniex.flow.net": {
        "title": "Poloniex Net Flows",
        "description": "The net USD value sent or withdrawn to/from Poloniex that interval.",
    },
    "exch.huobi.flow.in": {
        "title": "Huobi Deposits",
        "description": "The sum USD value sent to Huobi that interval.",
    },
    "exch.flow.out.ntv.incl": {
        "title": "Withdrawals from Exchanges - Inclusive (Native Units)",
        "description": "The amount of the asset withdrawn from exchanges that interval, including exchange to exchange activity.",
    },
    "exch.flow.in.usd": {
        "title": "Deposits on Exchanges",
        "description": "The sum USD value sent to exchanges that interval, excluding exchange to exchange activity.",
    },
    "miner.sply": {
        "title": "Miner Supply",
        "description": "The sum of the balances of all mining entities in USD. A mining entity is defined as an address that has been credited from a transaction debiting the 'FEES' or 'ISSUANCE' accounts.",
    },
    "sply.addr.bal.100": {
        "title": "Supply in addresses with balance greater than $100",
        "description": "The sum of all native units being held in addresses whose balance was $100 or greater at the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "sply.addr.bal.1k.ntv": {
        "title": "Supply in addresses with balance greater than 1K native units",
        "description": "The sum of all native units being held in addresses whose balance was 1K native units or greater at the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "exch.kraken.flow.net.ntv": {
        "title": "Kraken Net Flows (Native Units)",
        "description": "The net native units value sent or withdrawn to/from Kraken that interval.",
    },
    "exch.binance.flow.in": {
        "title": "Binance Deposits",
        "description": "The sum USD value sent to Binance that interval.",
    },
    "exch.poloniex.flow.in.ntv": {
        "title": "Poloniex Deposits (Native Units)",
        "description": "The sum in native units sent to Poloniex that interval.",
    },
    "exch.sply.poloniex": {
        "title": "Supply on Poloniex",
        "description": "The sum USD value held by Poloniex at the end of that interval.",
    },
    "exch.bitmex.flow.net.ntv": {
        "title": "Bitmex Net Flows (Native Units)",
        "description": "The net native units value sent or withdrawn to/from Bitmex that interval.",
    },
    "sply.act.pct.1y": {
        "title": "1 Year Active Supply (%)",
        "description": "The percentage of the current supply that has been active in the trailing 1 year up to the end of that interval.",
    },
    "exch.bittrex.flow.in.ntv": {
        "title": "Bittrex Deposits (Native Units)",
        "description": "The sum in native units sent to Bittrex that interval.",
    },
    "exch.poloniex.flow.out.ntv": {
        "title": "Poloniex Withdrawals (Native Units)",
        "description": "The sum in native units withdrawn from Poloniex that interval.",
    },
    "sply.total.iss.ntv": {
        "title": "Total Issuance (Native Units)",
        "description": "The sum of all new native units issued that interval.",
    },
    "addr.bal.10m.cnt": {
        "title": "Addresses with balance greater than $10M",
        "description": "The sum count of unique addresses holding at least ten million dollars' worth of native units as of the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "exch.binance.flow.net.ntv": {
        "title": "Binance Net Flows (Native Units)",
        "description": "The net native units value sent or withdrawn to/from Binance that interval.",
    },
    "exch.gemini.flow.net.ntv": {
        "title": "Gemini Net Flows (Native Units)",
        "description": "The net native units value sent or withdrawn to/from Gemini that interval.",
    },
    "exch.binance.flow.in.ntv": {
        "title": "Binance Deposits (Native Units)",
        "description": "The sum in native units sent to Binance that interval.",
    },
    "exch.gemini.flow.out": {
        "title": "Gemini Withdrawals",
        "description": "The sum in US dollars withdrawn from Gemini that interval.",
    },
    "txn.erc20.cnt": {
        "title": "ERC-20 Transactions Count",
        "description": "The sum count of transactions that resulted in any ERC-20 activity in that interval. Contracts that contain all of the following are considered to be ERC-20 contracts: the balanceOf function, the transfer function, and the Transfer event hash. Only Transfer or Approval events are counted as activity. If a transaction results in more than 1 transfer or approval, it’s only counted once.",
    },
    "txn.tfr.val.ntv": {
        "title": "Transaction Volume (Native Units)",
        "description": "The sum of native units transferred (i.e., the aggregate size of all transfers) between distinct addresses that interval.",
    },
    "real.vol": {
        "title": "Real Volume",
        "description": 'It is well known that many exchanges conduct wash trading practices in order to inflate trading volume. They are incentivized to report inflated volumes in order to attract traders. "Real Volume" refers to the total volume on the exchanges that we believe with high level of confidence are free of wash trading activities. However, that does not necessarily mean that the volume reported by other exchanges is 100% wash trades. As such, the Messari "Real Volume" applies a penalty to these exchanges to discount the volume believed to come from wash trading activity. For more information, see our methodology page.',
    },
    "exch.sply.bitmex": {
        "title": "Supply on Bitmex",
        "description": "The sum USD value held by Bitmex at the end of that interval.",
    },
    "sply.cont.ntv": {
        "title": "Supply in contracts (Native Units)",
        "description": "The sum of all native units being held by smart contracts.",
    },
    "txn.cont.creat.cnt": {
        "title": "Contract Creations Count",
        "description": "The sum count of new contracts successfully created across all transactions in that interval. A contract is a special address that contains and can execute code.",
    },
    "txn.tfr.erc20.cnt": {
        "title": "ERC-20 Transfer Count",
        "description": "The sum count of ERC-20 transfers in that interval. Only non-zero transfers between two distinct addresses are counted. Contracts that contain all of the following are considered to be ERC-20 contracts: the balanceOf function, the transfer function, and the Transfer event hash.",
    },
    "addr.bal.0.1.ntv.cnt": {
        "title": "Addresses with balance greater than 0.1 native units",
        "description": "The sum count of unique addresses holding at least 0.1 native units as of the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "exch.sply.bitstamp": {
        "title": "Supply on Bitstamp",
        "description": "The sum USD value held by Bitstamp at the end of that interval.",
    },
    "miner.rev.total": {
        "title": "Total Miner Revenue",
        "description": "The sum USD value of all miner revenue (fees plus newly issued native units) for all time from genesis up to the end of that interval.",
    },
    "sply.act.3y": {
        "title": "3 Year Active Supply",
        "description": "The sum of unique native units that transacted at least once in the trailing 3 years up to the end of that interval. Native units that transacted more than once are only counted once.",
    },
    "addr.act.sent.cnt": {
        "title": "Active Addresses Count (Sent)",
        "description": "The sum count of unique addresses that were active in the network (as an originator of a ledger change) that interval.",
    },
    "exch.poloniex.flow.net.ntv": {
        "title": "Poloniex Net Flows (Native Units)",
        "description": "The net native units value sent or withdrawn to/from Poloniex that interval.",
    },
    "exch.bitstamp.flow.in.ntv": {
        "title": "Bitstamp Deposits (Native Units)",
        "description": "The sum in native units sent to Bitstamp that interval.",
    },
    "exch.sply.bittrex": {
        "title": "Supply on Bittrex",
        "description": "The sum USD value held by Bittrex at the end of that interval.",
    },
    "hash.rev.ntv": {
        "title": "Miner Revenue per Hash (Native Units)",
        "description": "The mean miner reward per estimated hash unit performed during the period, in native units. The unit of hashpower measurement depends on the protocol.",
    },
    "sply.liquid": {
        "title": "Liquid Supply",
        "description": "The liquid supply of an asset is the number of units that currently exist on-chain and which are not known to be encumbered by any contracts.",
    },
    "exch.bittrex.flow.net": {
        "title": "Bittrex Net Flows",
        "description": "The net USD value sent or withdrawn to/from Bittrex that interval.",
    },
    "exch.gemini.flow.net": {
        "title": "Gemini Net Flows",
        "description": "The net USD value sent or withdrawn to/from Gemini that interval.",
    },
    "exch.bittrex.flow.out": {
        "title": "Bittrex Withdrawals",
        "description": "The sum in US dollars withdrawn from Bittrex that interval.",
    },
    "sply.addr.bal.10m": {
        "title": "Supply in addresses with balance greater than $10M",
        "description": "The sum of all native units being held in addresses whose balance was $10M or greater at the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "sply.utxo.loss": {
        "title": "Supply in UTXOs in Loss (Native Units)",
        "description": "The sum of all native units held in unspent transaction outputs created on days when the closing price was higher than the closing price at the end of the period.",
    },
    "txn.gas.avg": {
        "title": "Average Gas Used",
        "description": "The mean gas used (i.e., paid) across all transactions that interval.",
    },
    "exch.bitstamp.flow.net.ntv": {
        "title": "Bitstamp Net Flows (Native Units)",
        "description": "The net native units value sent or withdrawn to/from Bitstamp that interval.",
    },
    "exch.binance.flow.out": {
        "title": "Binance Withdrawals",
        "description": "The sum in US dollars withdrawn from Binance that interval.",
    },
    "miner.1hop.sply": {
        "title": "Supply One Hop from Miners",
        "description": "The sum of the balances of all addresses within one hop of a mining entity in USD. An address within one hop of a mining entity is defined as an address that has been credited from a transaction debiting the 'FEES' or 'ISSUANCE' accounts, or any address that has been credited in a transaction sent by such an address.",
    },
    "rvt.adj.90d.ma": {
        "title": "Adjusted RVT 90-days MA",
        "description": "The ratio of the network's realized value to the 90-day moving average of the adjusted transfer value. Also referred to as RVT.",
    },
    "blk.wght.avg": {
        "title": "Average Block Weight",
        "description": "The mean weight of all blocks created that day. Weight is a dimensionless measure of a block’s “size”. It is only applicable for chains that use SegWit (segregated witness).",
    },
    "exch.gemini.flow.out.ntv": {
        "title": "Gemini Withdrawals (Native Units)",
        "description": "The sum in native units withdrawn from Gemini that interval.",
    },
    "new.iss.ntv": {
        "title": "New Issuance (Native Units)",
        "description": "The sum of new native units issued that interval. Only those native units that are issued by a protocol-mandated continuous emission schedule are included (i.e., units manually released from escrow or otherwise disbursed are not included).",
    },
    "sply.rvv.1y": {
        "title": "Supply Revived in Last 1 Year",
        "description": "The sum of all native unit balances last active at least 1 year ago that became active in this interval.",
    },
    "sply.circ": {
        "title": "Circulating Supply",
        "description": "The circulating supply acknowledges that tokens may be held by projects/foundations which have no intent to sell down their positions, but which have not locked up supply in a formal contract. Thus, circulating supply does not include known project treasury holdings (which can be significant). Note that an investor must carefully consider both liquid and circulating supplies when evaluating an asset, and the two can vary significantly. A risk of depending entirely on circulating supply is that the number can change dramatically based on discretionary sales from project treasuries.",
    },
    "exch.flow.out.usd.incl": {
        "title": "Withdrawals from Exchanges - Inclusive",
        "description": "The sum USD value withdrawn from exchanges that interval, including exchange to exchange activity.",
    },
    "exch.flow.out.ntv": {
        "title": "Withdrawals from Exchanges (Native Units)",
        "description": "The amount of the asset withdrawn from exchanges that interval, excluding exchange to exchange activity.",
    },
    "blk.unc.rew.ntv": {
        "title": "Uncle Rewards (Native Units)",
        "description": "The sum of native units rewarded to miners for creating and including uncle blocks in thatinterval. This includes the uncle inclusion reward (for the main chain block miner) and the uncle rewards(for the uncle block miners).",
    },
    "daily.vol": {
        "title": "Volatility",
        "description": "The annualized standard-deviation of daily returns over a window of time",
    },
    "addr.bal.1m.ntv.cnt": {
        "title": "Addresses with balance greater than 1M native units",
        "description": "The sum count of unique addresses holding at least 1,000,000 native units as of the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "exch.sply.bitmex.ntv": {
        "title": "Supply on Bitmex (Native Units)",
        "description": "The sum in native units held by Bitmex at the end of that interval.",
    },
    "rvt.adj": {
        "title": "Adjusted RVT",
        "description": "The ratio of the network's realized value to the adjusted transfer value. Also referred to as RVT.",
    },
    "blk.size.bytes.avg": {
        "title": "Average Block Size (bytes)",
        "description": "The mean size (in bytes) of all blocks created",
    },
    "exch.binance.flow.out.ntv": {
        "title": "Binance Withdrawals (Native Units)",
        "description": "The sum in native units withdrawn from Binance that interval.",
    },
    "exch.poloniex.flow.out": {
        "title": "Poloniex Withdrawals",
        "description": "The sum in US dollars withdrawn from Poloniex that interval.",
    },
    "mcap.circ": {
        "title": "Circulating Marketcap",
        "description": "The circulating marketcap is the price of the asset multiplied by the circulating supply. If no price is found for an asset because no trades occurred, the last price of the last trade is used. After 30 days with no trades, a marketcap of 0 is reported until trading resumes.",
    },
    "exch.sply.huobi.ntv": {
        "title": "Supply on Huobi (Native Units)",
        "description": "The sum in native units held by Huobi at the end of that interval.",
    },
    "miner.1hop.sply.ntv": {
        "title": "Supply One Hop from Miners (Native Units)",
        "description": "The sum of the balances of all addresses within one hop of a mining entity. An address within one hop of a mining entity is defined as an address that has been credited from a transaction debiting the 'FEES' or 'ISSUANCE' accounts, or any address that has been credited in a transaction sent by such an address.",
    },
    "txn.cnt": {
        "title": "Transactions Count",
        "description": "The sum count of transactions that interval. Transactions represent a bundle of intended actions to alter the ledger initiated by a user (human or machine). Transactions are counted whether they execute or not and whether they result in the transfer of native units.",
    },
    "hashrate": {
        "title": "Hash Rate",
        "description": "The mean rate at which miners are solving hashes that interval.",
    },
    "sply.addr.bal.1m.ntv": {
        "title": "Supply in addresses with balance greater than 1M native units",
        "description": "The sum of all native units being held in addresses whose balance was 1M native units or greater at the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "txn.tkn.cnt": {
        "title": "Token Transactions Count",
        "description": "The sum count of transactions that resulted in any token (ERC-20 or ERC-721) activity in that interval. Only Transfer or Approval events are counted as activity. If a transaction results in more than 1 transfer or approval, it’s only counted once.",
    },
    "addr.cnt": {
        "title": "Addresses Count",
        "description": "The sum count of unique addresses holding any amount of native units as of the end of that interval. Only native units are considered (e.g., a 0 ETH balance address with ERC-20 tokens would not be considered).",
    },
    "exch.bitstamp.flow.in": {
        "title": "Bitstamp Deposits",
        "description": "The sum USD value sent to Bitstamp that interval.",
    },
    "exch.gemini.flow.in.ntv": {
        "title": "Gemini Deposits (Native Units)",
        "description": "The sum in native units sent to Gemini that interval.",
    },
    "exch.flow.out.usd": {
        "title": "Withdrawals from Exchanges",
        "description": "The sum USD value withdrawn from exchanges that interval, excluding exchange to exchange activity.",
    },
    "exch.kraken.flow.in": {
        "title": "Kraken Deposits",
        "description": "The sum USD value sent to Kraken that interval.",
    },
    "exch.bitstamp.flow.out.ntv": {
        "title": "Bitstamp Withdrawals (Native Units)",
        "description": "The sum in native units withdrawn from Bitstamp that interval.",
    },
    "sply.total.iss": {
        "title": "Total Issuance",
        "description": "The sum USD value of all new native units issued that interval.",
    },
    "blk.unc.rew.pct": {
        "title": "Miner Revenue from Uncle Blocks (%)",
        "description": "The percentage of miner revenue derived from creating and including uncle blocks in that interval. This is equal to the sum of the uncle inclusion reward (for the main chain block miner) and the uncle rewards (for the uncle block miners) divided by the miner revenue.",
    },
    "blk.wght.total": {
        "title": "Block Weight",
        "description": "The sum of the weights of all blocks created in that interval. Weight is a dimensionless measure of a block’s “size”. It is only applicable for chains that use SegWit (segregated witness).",
    },
    "exch.sply.gemini": {
        "title": "Supply on Gemini",
        "description": "The sum USD value held by Gemini at the end of that interval.",
    },
    "exch.sply.gemini.ntv": {
        "title": "Supply on Gemini (Native Units)",
        "description": "The sum in native units held by Gemini at the end of that interval.",
    },
    "sply.top.1pct": {
        "title": "Supply in top 1% addresses",
        "description": "The sum of all native units held by the richest 1% of addresses at the end of that interval.",
    },
    "utxo.prof.cnt": {
        "title": "UTXO in Profit Count",
        "description": "The sum count of unspent transaction outputs created on days where the closing price was lower than or equal to the closing price at the end of the period.",
    },
    "addr.bal.100k.cnt": {
        "title": "Addresses with balance greater than $100K",
        "description": "The sum count of unique addresses holding at least one hundred thousand dollars' worth of native units as of the end of that interval. Only native units are considered (e.g., an address with less than X ETH but with more than X in ERC-20 tokens would not be considered).",
    },
    "exch.sply": {
        "title": "Supply on Exchanges (Native Units)",
        "description": "The sum of all native units held in hot or cold exchange wallets that interval.",
    },
    "exch.bittrex.flow.in": {
        "title": "Bittrex Deposits",
        "description": "The sum USD value sent to Bittrex that interval.",
    },
    "exch.kraken.flow.out": {
        "title": "Kraken Withdrawals",
        "description": "The sum in US dollars withdrawn from Kraken that interval.",
    },
}

base_url = "https://data.messari.io/api/v1/"
base_url2 = "https://data.messari.io/api/v2/"


@log_start_end(log=logger)
def get_marketcap_dominance(
    coin: str, interval: str, start: str, end: str
) -> pd.DataFrame:
    """Returns market dominance of a coin over time
    [Source: https://messari.io/]

    Parameters
    ----------
    coin : str
        Crypto symbol to check market cap dominance
    start : int
        Initial date like string (e.g., 2021-10-01)
    end : int
        End date like string (e.g., 2021-10-01)
    interval : str
        Interval frequency (e.g., 1d)

    Returns
    -------
    pd.DataFrame
        market dominance percentage over time
    """

    df, _, _ = get_messari_timeseries(
        coin=coin, end=end, start=start, interval=interval, timeseries_id="mcap.dom"
    )
    return df


@log_start_end(log=logger)
def get_messari_timeseries(
    coin: str, timeseries_id: str, interval: str, start: str, end: str
) -> Tuple[pd.DataFrame, str, str]:
    """Returns messari timeseries
    [Source: https://messari.io/]

    Parameters
    ----------
    coin : str
        Crypto symbol to check messari timeseries
    timeseries_id : str
        Messari timeserie id
    start : int
        Initial date like string (e.g., 2021-10-01)
    end : int
        End date like string (e.g., 2021-10-01)
    interval : str
        Interval frequency (e.g., 1d)

    Returns
    -------
    pd.DataFrame
        messari timeserie over time
    """

    url = base_url + f"assets/{coin}/metrics/{timeseries_id}/time-series"

    headers = {"x-messari-api-key": cfg.API_MESSARI_KEY}

    parameters = {
        "start": start,
        "end": end,
        "interval": interval,
    }

    r = requests.get(url, params=parameters, headers=headers)

    df = pd.DataFrame()
    title = ""
    y_axis = ""

    if r.status_code == 200:
        data = r.json()["data"]
        title = data["schema"]["name"]

        df = pd.DataFrame(data["values"], columns=["timestamp", "values"])
        schema_values = data["schema"]["values_schema"]
        for key in schema_values.keys():
            if key != "timestamp":
                y_axis = schema_values[key]

        if df.empty:
            console.print(f"No data found for {coin}.\n")
        else:
            df = df.set_index("timestamp")
            df.index = pd.to_datetime(df.index, unit="ms")

    elif r.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    else:
        console.print(r.text)

    return df, title, y_axis


@log_start_end(log=logger)
def get_links(symbol: str) -> pd.DataFrame:
    """Returns asset's links
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check links

    Returns
    -------
    pd.DataFrame
        asset links
    """

    url = base_url2 + f"assets/{symbol}/profile"

    headers = {"x-messari-api-key": cfg.API_MESSARI_KEY}

    params = {"fields": "profile/general/overview/official_links"}

    r = requests.get(url, headers=headers, params=params)

    df = pd.DataFrame()

    if r.status_code == 200:
        data = r.json()["data"]
        df = pd.DataFrame(data["profile"]["general"]["overview"]["official_links"])
        df.columns = map(str.capitalize, df.columns)
    if r.status_code == 401:
        print("[red]Invalid API Key[/red]\n")
    else:
        print(r.text)
    return pd.DataFrame()


@log_start_end(log=logger)
def get_roadmap(symbol: str) -> pd.DataFrame:
    """Returns coin roadmap
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check roadmap

    Returns
    -------
    pd.DataFrame
        roadmap
    """

    url = base_url2 + f"assets/{symbol}/profile"

    headers = {"x-messari-api-key": cfg.API_MESSARI_KEY}

    params = {"fields": "profile/general/roadmap"}

    r = requests.get(url, headers=headers, params=params)

    df = pd.DataFrame()

    if r.status_code == 200:
        data = r.json()["data"]
        df = pd.DataFrame(data["profile"]["general"]["roadmap"])
        df["date"] = pd.to_datetime(df["date"])
        df.columns = map(str.capitalize, df.columns)
        df = df.dropna(axis=1, how="all")
    elif r.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    else:
        console.print(r.text)

    return df


@log_start_end(log=logger)
def get_tokenomics(
    symbol: str, coingecko_symbol: str, circ_supply_src: str
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Returns coin tokenomics
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check tokenomics
    coingecko_symbol : str
        Coingecko crypto symbol to check tokenomics
    Returns
    -------
    pd.DataFrame
        Metric Value tokenomics
    pd.DataFrame
        Circulating supply overtime
    """

    url = base_url2 + f"assets/{symbol}/profile"

    headers = {"x-messari-api-key": ""}

    params = {"fields": "profile/economics/consensus_and_emission"}

    r = requests.get(url, headers=headers, params=params)

    df = pd.DataFrame()
    circ_df = pd.DataFrame()
    if r.status_code == 200:
        data = r.json()["data"]
        tokenomics_data = data["profile"]["economics"]["consensus_and_emission"]
        df = pd.DataFrame(
            {
                "Metric": [
                    "Emission Type",
                    "Consensus Mechanism",
                    "Consensus Details",
                    "Mining Algorithm",
                    "Block Reward",
                ],
                "Value": [
                    tokenomics_data["supply"]["general_emission_type"],
                    tokenomics_data["consensus"]["general_consensus_mechanism"],
                    tokenomics_data["consensus"]["consensus_details"],
                    tokenomics_data["consensus"]["mining_algorithm"],
                    tokenomics_data["consensus"]["block_reward"],
                ],
            }
        )
        cg_df = get_coin_tokenomics(coingecko_symbol)
        df = pd.concat([df, cg_df], ignore_index=True, sort=False)
        circ_df, _, _ = get_messari_timeseries(
            coin=symbol,
            timeseries_id="sply.circ" if circ_supply_src == "mes" else "cg.sply.circ",
            interval="1d",
            start="",
            end="",
        )
    elif r.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    else:
        console.print(r.text)

    return df, circ_df


@log_start_end(log=logger)
def get_project_product_info(
    symbol: str,
) -> Tuple[str, str, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Returns coin product info
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check product info

    Returns
    -------
    str
        project details
    str
        technology details
    pd.DataFrame
        coin public repos
    pd.DataFrame
        coin audits
    pd.DataFrame
        coin known exploits/vulns
    """

    url = base_url2 + f"assets/{symbol}/profile"

    headers = {"x-messari-api-key": ""}

    params = {"fields": "profile/general/overview/project_details,profile/technology"}

    r = requests.get(url, headers=headers, params=params)

    df = pd.DataFrame()
    if r.status_code == 200:
        data = r.json()["data"]
        project_details = data["profile"]["general"]["overview"]["project_details"]
        technology_data = data["profile"]["technology"]
        technology_details = technology_data["overview"]["technology_details"]
        df_repos = pd.DataFrame(technology_data["overview"]["client_repositories"])
        df_audits = pd.DataFrame(technology_data["security"]["audits"])
        if not df_audits.empty:
            df_audits["date"] = pd.to_datetime(df_audits["date"])
        df_vulns = pd.DataFrame(
            technology_data["security"]["known_exploits_and_vulnerabilities"]
        )
        if not df_vulns.empty:
            df_vulns["date"] = pd.to_datetime(df_vulns["date"])
        return project_details, technology_details, df_repos, df_audits, df_vulns
    if r.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    else:
        console.print(r.text)

    return "", "", df, df, df


@log_start_end(log=logger)
def get_team(symbol: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Returns coin team
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check team

    Returns
    -------
    pd.DataFrame
        individuals
    pd.DataFrame
        organizations
    """

    url = base_url2 + f"assets/{symbol}/profile"

    headers = {"x-messari-api-key": cfg.API_MESSARI_KEY}

    params = {"fields": "profile/contributors"}

    r = requests.get(url, headers=headers, params=params)

    df = pd.DataFrame()
    if r.status_code == 200:
        data = r.json()["data"]
        df_individual_contributors = pd.DataFrame(
            data["profile"]["contributors"]["individuals"]
        )
        df_individual_contributors.fillna("-")
        df_individual_contributors.insert(
            0,
            "Name",
            df_individual_contributors[["first_name", "last_name"]].apply(
                lambda x: " ".join(x), axis=1
            ),
        )
        df_individual_contributors.drop(
            ["slug", "avatar_url", "first_name", "last_name"],
            axis=1,
            inplace=True,
            errors="ignore",
        )
        df_individual_contributors.columns = map(
            str.capitalize, df_individual_contributors.columns
        )
        df_individual_contributors.replace(to_replace=[None], value="-", inplace=True)
        df_organizations_contributors = pd.DataFrame(
            data["profile"]["contributors"]["organizations"]
        )
        df_organizations_contributors.drop(
            ["slug", "logo"], axis=1, inplace=True, errors="ignore"
        )
        df_organizations_contributors.columns = map(
            str.capitalize, df_organizations_contributors.columns
        )
        df_organizations_contributors.replace(
            to_replace=[None], value="-", inplace=True
        )
        return df_individual_contributors, df_organizations_contributors
    if r.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    else:
        console.print(r.text)

    return df, df


@log_start_end(log=logger)
def get_investors(symbol: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Returns coin investors
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check investors

    Returns
    -------
    pd.DataFrame
        individuals
    pd.DataFrame
        organizations
    """

    url = base_url2 + f"assets/{symbol}/profile"

    headers = {"x-messari-api-key": cfg.API_MESSARI_KEY}

    params = {"fields": "profile/investors"}

    r = requests.get(url, headers=headers, params=params)

    df = pd.DataFrame()
    if r.status_code == 200:
        data = r.json()["data"]
        df_individual_investors = pd.DataFrame(
            data["profile"]["investors"]["individuals"]
        )
        df_individual_investors.fillna("-")
        df_individual_investors.insert(
            0,
            "Name",
            df_individual_investors[["first_name", "last_name"]].apply(
                lambda x: " ".join(x), axis=1
            ),
        )
        df_individual_investors.drop(
            ["slug", "avatar_url", "first_name", "last_name"],
            axis=1,
            inplace=True,
            errors="ignore",
        )
        df_individual_investors.columns = map(
            str.capitalize, df_individual_investors.columns
        )
        df_individual_investors.replace(to_replace=[None], value="-", inplace=True)
        df_organizations_investors = pd.DataFrame(
            data["profile"]["investors"]["organizations"]
        )
        df_organizations_investors.drop(
            ["slug", "logo"], axis=1, inplace=True, errors="ignore"
        )
        df_organizations_investors.columns = map(
            str.capitalize, df_organizations_investors.columns
        )
        df_organizations_investors.replace(to_replace=[None], value="-", inplace=True)
        return df_individual_investors, df_organizations_investors
    if r.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    else:
        console.print(r.text)

    return df, df


@log_start_end(log=logger)
def get_governance(symbol: str) -> Tuple[str, pd.DataFrame]:
    """Returns coin governance
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check governance

    Returns
    -------
    str
        governance summary
    pd.DataFrame
        Metric Value with governance details
    """

    url = base_url2 + f"assets/{symbol}/profile"

    headers = {"x-messari-api-key": cfg.API_MESSARI_KEY}

    params = {"fields": "profile/governance"}

    r = requests.get(url, headers=headers, params=params)

    df = pd.DataFrame()
    if r.status_code == 200:
        data = r.json()["data"]
        governance_data = data["profile"]["governance"]
        if (
            governance_data["onchain_governance"]["onchain_governance_type"] is not None
            and governance_data["onchain_governance"]["onchain_governance_details"]
            is not None
        ):
            return (
                governance_data["governance_details"],
                pd.DataFrame(
                    {
                        "Metric": ["Type", "Details"],
                        "Value": [
                            governance_data["onchain_governance"][
                                "onchain_governance_type"
                            ],
                            governance_data["onchain_governance"][
                                "onchain_governance_details"
                            ],
                        ],
                    }
                ),
            )
        return governance_data["governance_details"], df
    if r.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    else:
        console.print(r.text)

    return "", df


def format_addresses(x: Any):
    final_str = ""
    for address in x:
        final_str += f"{address['name']}: {address['link']}"
    return final_str


@log_start_end(log=logger)
def get_fundraising(
    symbol: str,
) -> Tuple[str, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Returns coin fundraising
    [Source: https://messari.io/]

    Parameters
    ----------
    symbol : str
        Crypto symbol to check fundraising

    Returns
    -------
    str
        launch summary
    pd.DataFrame
        Sales rounds
    pd.DataFrame
        Treasury Accounts
    pd.DataFrame
        Metric Value launch details
    """

    url = base_url2 + f"assets/{symbol}/profile"

    headers = {"x-messari-api-key": cfg.API_MESSARI_KEY}

    params = {"fields": "profile/economics/launch"}

    r = requests.get(url, headers=headers, params=params)

    df = pd.DataFrame()
    if r.status_code == 200:
        data = r.json()["data"]
        launch_data = data["profile"]["economics"]["launch"]
        launch_details = launch_data["general"]["launch_details"]
        launch_type = launch_data["general"]["launch_style"]
        launch_fundraising_rounds = pd.DataFrame(
            launch_data["fundraising"]["sales_rounds"]
        )
        if not launch_fundraising_rounds.empty:
            launch_fundraising_rounds.drop(
                [
                    "details",
                    "asset_collected",
                    "price_per_token_in_asset",
                    "amount_collected_in_asset",
                    "is_kyc_required",
                    "restricted_jurisdictions",
                ],
                axis=1,
                inplace=True,
                errors="ignore",
            )
            launch_fundraising_rounds.columns = [
                lambda_replace_underscores_in_column_names(val)
                for val in launch_fundraising_rounds.columns
            ]
            launch_fundraising_rounds["Start Date"] = launch_fundraising_rounds.apply(
                lambda x: x["Start Date"].split("T")[0], axis=1
            )
            launch_fundraising_rounds["End Date"] = launch_fundraising_rounds.apply(
                lambda x: x["End Date"].split("T")[0], axis=1
            )
            launch_fundraising_rounds.rename(
                columns={
                    "Native Tokens Allocated": "Tokens Allocated",
                    "Equivalent Price Per Token In Usd": "Price [$]",
                    "Amount Collected In Usd": "Amount Collected [$]",
                },
                inplace=True,
            )
            launch_fundraising_rounds.fillna("-", inplace=True)

        launch_fundraising_accounts = pd.DataFrame(
            launch_data["fundraising"]["sales_treasury_accounts"]
        )
        if not launch_fundraising_accounts.empty:
            launch_fundraising_accounts.columns = [
                lambda_replace_underscores_in_column_names(val)
                for val in launch_fundraising_accounts.columns
            ]
            launch_fundraising_accounts.drop(
                ["Asset Held", "Security"], inplace=True, axis=1
            )
            launch_fundraising_accounts["Addresses"] = launch_fundraising_accounts[
                "Addresses"
            ].map(format_addresses)
        launch_distribution = pd.DataFrame(
            {
                "Metric": [
                    "Genesis Date",
                    "Type",
                    "Total Supply",
                    "Investors [%]",
                    "Organization/Founders [%]",
                    "Rewards/Airdrops [%]",
                ],
                "Value": [
                    launch_data["initial_distribution"]["genesis_block_date"].split(
                        "T"
                    )[0],
                    launch_type,
                    lambda_long_number_format(
                        launch_data["initial_distribution"]["initial_supply"]
                    ),
                    launch_data["initial_distribution"]["initial_supply_repartition"][
                        "allocated_to_investors_percentage"
                    ],
                    launch_data["initial_distribution"]["initial_supply_repartition"][
                        "allocated_to_organization_or_founders_percentage"
                    ],
                    launch_data["initial_distribution"]["initial_supply_repartition"][
                        "allocated_to_premined_rewards_or_airdrops_percentage"
                    ],
                ],
            }
        )
        return (
            launch_details,
            launch_fundraising_rounds,
            launch_fundraising_accounts,
            launch_distribution,
        )
    if r.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    else:
        console.print(r.text)

    return "", df, df, df
