# ######### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ######### #
# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.core.sdk.models import crypto_sdk_model as model


class CryptoController(model.CryptoRoot):
    """Cryptocurrency Module.

    Submodules:
        `dd`: Due Diligence Module
        `defi`: DeFi Module
        `disc`: Discovery Module
        `nft`: NFT Module
        `onchain`: OnChain Module
        `ov`: Overview Module
        `tools`: Tools Module

    Attributes:
        `candle`: Plot candle chart from dataframe. [Source: Binance]\n
        `chart`: Load data for Technical Analysis\n
        `find`: Find similar coin by coin name,symbol or id.\n
        `load`: Load crypto currency to get data for\n
        `price`: Displays live price from pyth live feed [Source: https://pyth.network/]\n
    """

    @property
    def dd(self):
        """Cryptocurrency Due Diligence Submodule

        Attributes:
            `active`: Returns active addresses of a certain symbol\n
            `active_chart`: Plots active addresses of a certain symbol over time\n
            `all_binance_trading_pairs`: Returns all available pairs on Binance in DataFrame format. DataFrame has 3 columns symbol, baseAsset, quoteAsset\n
            `ath`: Get all time high for a coin in a given currency\n
            `atl`: Get all time low for a coin in a given currency\n
            `balance`: Get account holdings for asset. [Source: Binance]\n
            `balance_chart`: Prints table showing account holdings for asset. [Source: Binance]\n
            `basic`: Basic coin information [Source: CoinPaprika]\n
            `basic_chart`: Prints table showing basic information for coin. Like:\n
            `binance_available_quotes_for_each_coin`: Helper methods that for every coin available on Binance add all quote assets. [Source: Binance]\n
            `candle`: Get candles for chosen trading pair and time interval. [Source: Coinbase]\n
            `change`: Returns 30d change of the supply held in exchange wallets of a certain symbol.\n
            `change_chart`: Plots 30d change of the supply held in exchange wallets.\n
            `check_valid_binance_str`: Check if symbol is in defined binance. [Source: Binance]\n
            `close`: Returns the price of a cryptocurrency\n
            `coin`: Get coin by id [Source: CoinPaprika]\n
            `coin_market_chart`: Get prices for given coin. [Source: CoinGecko]\n
            `dev`: Get developer stats for a coin\n
            `eb`: Returns the total amount of coins held on exchange addresses in units and percentage.\n
            `eb_chart`: Plots total amount of coins held on exchange addresses in units and percentage.\n
            `events`: Get all events related to given coin like conferences, start date of futures trading etc.\n
            `events_chart`: Prints table showing all events for given coin id. [Source: CoinPaprika]\n
            `ex`: Get all exchanges for given coin id. [Source: CoinPaprika]\n
            `ex_chart`: Prints table showing all exchanges for given coin id. [Source: CoinPaprika]\n
            `exchanges`: Helper method to get all the exchanges supported by ccxt\n
            `fr`: Returns coin fundraising\n
            `fr_chart`: Display coin fundraising\n
            `get_mt`: Returns available messari timeseries\n
            `get_mt_chart`: Prints table showing messari timeseries list\n
            `gh`: Returns  a list of developer activity for a given coin and time interval.\n
            `gh_chart`: Returns a list of github activity for a given coin and time interval.\n
            `gov`: Returns coin governance\n
            `gov_chart`: Prints table showing coin governance\n
            `headlines`: Gets Sentiment analysis provided by FinBrain's API [Source: finbrain].\n
            `headlines_chart`: Sentiment analysis from FinBrain for Cryptocurrencies\n
            `inv`: Returns coin investors\n
            `inv_chart`: Prints table showing coin investors\n
            `links`: Returns asset's links\n
            `links_chart`: Prints table showing coin links\n
            `mcapdom`: Returns market dominance of a coin over time\n
            `mcapdom_chart`: Plots market dominance of a coin over time\n
            `mkt`: All markets for given coin and currency [Source: CoinPaprika]\n
            `mkt_chart`: Prints table showing all markets for given coin id. [Source: CoinPaprika]\n
            `mt`: Returns messari timeseries\n
            `mt_chart`: Plots messari timeseries\n
            `news`: Get recent posts from CryptoPanic news aggregator platform. [Source: https://cryptopanic.com/]\n
            `news_chart`: Prints table showing recent posts from CryptoPanic news aggregator platform.\n
            `nonzero`: Returns addresses with non-zero balance of a certain symbol\n
            `nonzero_chart`: Plots addresses with non-zero balance of a certain symbol\n
            `ob`: Returns orderbook for a coin in a given exchange\n
            `ob_chart`: Plots order book for a coin in a given exchange\n
            `oi`: Returns open interest by exchange for a certain symbol\n
            `oi_chart`: Plots open interest by exchange for a certain cryptocurrency\n
            `pi`: Returns coin product info\n
            `pi_chart`: Prints table showing project info\n
            `pr`: Fetch data to calculate potential returns of a certain coin. [Source: CoinGecko]\n
            `pr_chart`: Prints table showing potential returns of a certain coin. [Source: CoinGecko]\n
            `ps`: Get all most important ticker related information for given coin id [Source: CoinPaprika]\n
            `ps_chart`: Prints table showing ticker information for single coin [Source: CoinPaprika]\n
            `rm`: Returns coin roadmap\n
            `rm_chart`: Plots coin roadmap\n
            `score`: Get scores for a coin from CoinGecko\n
            `show_available_pairs_for_given_symbol`: Return all available quoted assets for given symbol. [Source: Coinbase]\n
            `social`: Get social media stats for a coin\n
            `stats`: Get 24 hr stats for the product. Volume is in base currency units.\n
            `stats_chart`: Prints table showing 24 hr stats for the product. Volume is in base currency units.\n
            `team`: Returns coin team\n
            `team_chart`: Prints table showing coin team\n
            `tk`: Returns coin tokenomics\n
            `tk_chart`: Plots coin tokenomics\n
            `tokenomics`: Get tokenomics for given coin. [Source: CoinGecko]\n
            `trades`: Returns trades for a coin in a given exchange\n
            `trades_chart`: Prints table showing trades for a coin in a given exchange\n
            `trading_pair_info`: Get information about chosen trading pair. [Source: Coinbase]\n
            `trading_pairs`: Helper method that return all trading pairs on binance. Methods ause this data for input for e.g\n
            `twitter`: Get twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]\n
            `twitter_chart`: Prints table showing twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]\n
        """

        return model.CryptoDueDiligence()

    @property
    def defi(self):
        """Cryptocurrency DeFi Submodule

        Attributes:
            `anchor_data`: Returns anchor protocol earnings data of a certain terra address\n
            `anchor_data_chart`: Plots anchor protocol earnings data of a certain terra address\n
            `aterra`: Returns historical data of an asset in a certain terra address\n
            `aterra_chart`: Plots the 30-day history of specified asset in terra address\n
            `ayr`: Displays the 30-day history of the Anchor Yield Reserve.\n
            `ayr_chart`: Plots the 30-day history of the Anchor Yield Reserve.\n
            `dtvl`: Returns information about historical tvl of a defi protocol.\n
            `dtvl_chart`: Plots historical TVL of different dApps\n
            `gacc`: Get terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]\n
            `gacc_chart`: Plots terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]\n
            `gdapps`: Display top dApps (in terms of TVL) grouped by chain.\n
            `gdapps_chart`: Plots top dApps (in terms of TVL) grouped by chain.\n
            `gov_proposals`: Get terra blockchain governance proposals list [Source: https://fcd.terra.dev/swagger]\n
            `gov_proposals_chart`: Prints table showing terra blockchain governance proposals list [Source: https://fcd.terra.dev/swagger]\n
            `ldapps`: Returns information about listed DeFi protocols, their current TVL and changes to it in the last hour/day/week.\n
            `ldapps_chart`: Prints table showing information about listed DeFi protocols, their current TVL and changes to it in\n
            `luna_supply`: Get supply history of the Terra ecosystem\n
            `luna_supply_chart`: Plots and prints table showing Luna circulating supply stats\n
            `newsletters`: Scrape all substack newsletters from url list.\n
            `newsletters_chart`: Prints table showing DeFi related substack newsletters.\n
            `sinfo`: Get staking info for provided terra account [Source: https://fcd.terra.dev/swagger]\n
            `sinfo_chart`: Prints table showing staking info for provided terra account address [Source: https://fcd.terra.dev/swagger]\n
            `sratio`: Get terra blockchain staking ratio history [Source: https://fcd.terra.dev/swagger]\n
            `sratio_chart`: Plots terra blockchain staking ratio history [Source: https://fcd.terra.dev/v1]\n
            `sreturn`: Get terra blockchain staking returns history [Source: https://fcd.terra.dev/v1]\n
            `sreturn_chart`: Plots terra blockchain staking returns history [Source: https://fcd.terra.dev/swagger]\n
            `stvl`: Returns historical values of the total sum of TVLs from all listed protocols.\n
            `stvl_chart`: Plots historical values of the total sum of TVLs from all listed protocols.\n
            `validators`: Get information about terra validators [Source: https://fcd.terra.dev/swagger]\n
            `validators_chart`: Prints table showing information about terra validators [Source: https://fcd.terra.dev/swagger]\n
            `vaults`: Get DeFi Vaults Information. DeFi Vaults are pools of funds with an assigned strategy which main goal is to\n
            `vaults_chart`: Prints table showing Top DeFi Vaults - pools of funds with an assigned strategy which main goal is to\n
        """

        return model.CryptoDeFi()

    @property
    def disc(self):
        """Cryptocurrency Discovery Submodule

        Attributes:
            `categories_keys`: Get list of categories keys\n
            `coin_list`: Get list of coins available on CoinGecko [Source: CoinGecko]\n
            `coins`: Get N coins from CoinGecko [Source: CoinGecko]\n
            `coins_chart`: Prints table showing top coins [Source: CoinGecko]\n
            `coins_for_given_exchange`: Helper method to get all coins available on binance exchange [Source: CoinGecko]\n
            `cpsearch`: Search CoinPaprika. [Source: CoinPaprika]\n
            `cpsearch_chart`: Prints table showing Search over CoinPaprika. [Source: CoinPaprika]\n
            `dapp_categories`: Get dapp categories [Source: https://dappradar.com/]\n
            `dapp_categories_chart`: Prints table showing dapp categories [Source: https://dappradar.com/]\n
            `dapp_chains`: Get dapp chains [Source: https://dappradar.com/]\n
            `dapp_chains_chart`: Prints table showing dapp chains [Source: https://dappradar.com/]\n
            `dapp_metrics`: Get dapp metrics [Source: https://dappradar.com/]\n
            `dapp_metrics_chart`: Prints table showing dapp metrics [Source: https://dappradar.com/]\n
            `dapps`: Get dapps [Source: https://dappradar.com/]\n
            `dapps_chart`: Prints table showing dapps [Source: https://dappradar.com/]\n
            `defi_chains`: Get defi chains [Source: https://dappradar.com/]\n
            `defi_chains_chart`: Prints table showing defi chains [Source: https://dappradar.com/]\n
            `fees`: Show cryptos with most fees. [Source: CryptoStats]\n
            `fees_chart`: Display crypto with most fees paid [Source: CryptoStats]\n
            `gainers`: Shows Largest Gainers - coins which gain the most in given period. [Source: CoinGecko]\n
            `gainers_chart`: Prints table showing Largest Gainers - coins which gain the most in given period. [Source: CoinGecko]\n
            `losers`: Shows Largest Losers - coins which lose the most in given period. [Source: CoinGecko]\n
            `losers_chart`: Prints table showing Largest Losers - coins which lost the most in given period of time. [Source: CoinGecko]\n
            `nft_mktp`: Get top nft collections [Source: https://dappradar.com/]\n
            `nft_mktp_chart`: Prints table showing nft marketplaces [Source: https://dappradar.com/]\n
            `nft_mktp_chains`: Get nft marketplaces chains [Source: https://dappradar.com/]\n
            `nft_mktp_chains_chart`: Prints table showing nft marketplaces chains [Source: https://dappradar.com/]\n
            `tokens`: Get chains that support tokens [Source: https://dappradar.com/]\n
            `tokens_chart`: Prints table showing chains that support tokens [Source: https://dappradar.com/]\n
            `top_coins`: Get top cryptp coins.\n
            `trending`: Returns trending coins [Source: CoinGecko]\n
            `trending_chart`: Prints table showing trending coins [Source: CoinGecko]\n
        """

        return model.CryptoDiscovery()

    @property
    def nft(self):
        """Cryptocurrency NFT Submodule

        Attributes:
            `collections`: Get nft collections [Source: https://nftpricefloor.com/]\n
            `collections_chart`: Display NFT collections. [Source: https://nftpricefloor.com/]\n
            `fp`: Get nft collections [Source: https://nftpricefloor.com/]\n
            `fp_chart`: Display NFT collection floor price over time. [Source: https://nftpricefloor.com/]\n
            `stats`: Get stats of a nft collection [Source: opensea.io]\n
            `stats_chart`: Prints table showing collection stats. [Source: opensea.io]\n
        """

        return model.CryptoNFT()

    @property
    def onchain(self):
        """Cryptocurrency OnChain Submodule

        Attributes:
            `baas`: Get an average bid and ask prices, average spread for given crypto pair for chosen time period.\n
            `baas_chart`: Prints table showing an average bid and ask prices, average spread for given crypto pair for chosen\n
            `balance`: Get info about tokens on you ethereum blockchain balance. Eth balance, balance of all tokens which\n
            `balance_chart`: Display info about tokens for given ethereum blockchain balance e.g. ETH balance,\n
            `btc_supply`: Returns BTC circulating supply [Source: https://api.blockchain.info/]\n
            `btc_supply_chart`: Returns BTC circulating supply [Source: https://api.blockchain.info/]\n
            `btc_transac`: Returns BTC confirmed transactions [Source: https://api.blockchain.info/]\n
            `btc_transac_chart`: Returns BTC confirmed transactions [Source: https://api.blockchain.info/]\n
            `btcsingleblock`: Returns BTC block data in json format. [Source: https://blockchain.info/]\n
            `btcsingleblock_chart`: Returns BTC block data. [Source: https://api.blockchain.info/]\n
            `dex_trades_monthly`: Get list of trades on Decentralized Exchanges monthly aggregated.\n
            `dvcp`: Get daily volume for given pair [Source: https://graphql.bitquery.io/]\n
            `dvcp_chart`: Prints table showing daily volume for given pair\n
            `erc20_tokens`: Helper method that loads ~1500 most traded erc20 token.\n
            `gwei`: Returns the most recent Ethereum gas fees in gwei\n
            `gwei_chart`: Current gwei fees\n
            `hist`: Get information about balance historical transactions. [Source: Ethplorer]\n
            `hist_chart`: Display information about balance historical transactions. [Source: Ethplorer]\n
            `holders`: Get info about top token holders. [Source: Ethplorer]\n
            `holders_chart`: Display info about top ERC20 token holders. [Source: Ethplorer]\n
            `hr`: Returns dataframe with mean hashrate of btc or eth blockchain and symbol price\n
            `hr_chart`: Plots dataframe with mean hashrate of btc or eth blockchain and symbol price.\n
            `info`: Get info about ERC20 token. [Source: Ethplorer]\n
            `info_chart`: Display info about ERC20 token. [Source: Ethplorer]\n
            `lt`: Get trades on Decentralized Exchanges aggregated by DEX [Source: https://graphql.bitquery.io/]\n
            `lt_chart`: Prints table showing Trades on Decentralized Exchanges aggregated by DEX or Month\n
            `prices`: Get token historical prices with volume and market cap, and average price. [Source: Ethplorer]\n
            `prices_chart`: Display token historical prices with volume and market cap, and average price.\n
            `query_graph`: Helper methods for querying graphql api. [Source: https://bitquery.io/]\n
            `th`: Get info about token historical transactions. [Source: Ethplorer]\n
            `th_chart`: Display info about token history. [Source: Ethplorer]\n
            `token_decimals`: Helper methods that gets token decimals number. [Source: Ethplorer]\n
            `top`: Get top 50 tokens. [Source: Ethplorer]\n
            `top_chart`: Display top ERC20 tokens [Source: Ethplorer]\n
            `topledger`: Returns Topledger's Data for the given Organization's Slug[org_slug] based\n
            `topledger_chart`: Display on-chain data from Topledger. [Source: Topledger]\n
            `ttcp`: Get most traded crypto pairs on given decentralized exchange in chosen time period.\n
            `ttcp_chart`: Prints table showing most traded crypto pairs on given decentralized exchange in chosen time period.\n
            `tv`: Get token volume on different Decentralized Exchanges. [Source: https://graphql.bitquery.io/]\n
            `tv_chart`: Prints table showing token volume on different Decentralized Exchanges.\n
            `tx`: Get info about transaction. [Source: Ethplorer]\n
            `tx_chart`: Display info about transaction. [Source: Ethplorer]\n
            `ueat`: Get number of unique ethereum addresses which made a transaction in given time interval.\n
            `ueat_chart`: Prints table showing number of unique ethereum addresses which made a transaction in given time interval\n
            `whales`: Whale Alert's API allows you to retrieve live and historical transaction data from major blockchains.\n
            `whales_chart`: Display huge value transactions from major blockchains. [Source: https://docs.whale-alert.io/]\n
        """

        return model.CryptoOnChain()

    @property
    def ov(self):
        """Cryptocurrency Overview Submodule

        Attributes:
            `altindex`: Get altcoin index overtime\n
            `altindex_chart`: Displays altcoin index overtime\n
            `btcrb`: Get bitcoin price data\n
            `btcrb_chart`: Displays bitcoin rainbow chart\n
            `categories`: Returns top crypto categories [Source: CoinGecko]\n
            `categories_chart`: Shows top cryptocurrency categories by market capitalization\n
            `cbpairs`: Get a list of available currency pairs for trading. [Source: Coinbase]\n
            `cbpairs_chart`: Displays a list of available currency pairs for trading. [Source: Coinbase]\n
            `coin_list`: Get list of all available coins on CoinPaprika  [Source: CoinPaprika]\n
            `contracts`: Gets all contract addresses for given platform [Source: CoinPaprika]\n
            `contracts_chart`: Gets all contract addresses for given platform. [Source: CoinPaprika]\n
            `cr`: Returns crypto {borrow,supply} interest rates for cryptocurrencies across several platforms\n
            `cr_chart`: Displays crypto {borrow,supply} interest rates for cryptocurrencies across several platforms\n
            `crypto_hack`: Get crypto hack\n
            `crypto_hack_slugs`: Get all crypto hack slugs\n
            `crypto_hacks`: Get major crypto-related hacks\n
            `crypto_hacks_chart`: Display list of major crypto-related hacks. If slug is passed\n
            `defi`: Get global statistics about Decentralized Finances [Source: CoinGecko]\n
            `defi_chart`: Shows global statistics about Decentralized Finances. [Source: CoinGecko]\n
            `derivatives`: Get list of crypto derivatives from CoinGecko API [Source: CoinGecko]\n
            `derivatives_chart`: Shows  list of crypto derivatives. [Source: CoinGecko]\n
            `ewf`: Scrapes exchange withdrawal fees\n
            `ewf_chart`: Exchange withdrawal fees\n
            `exchanges`: Show top crypto exchanges.\n
            `exmarkets`: List markets by exchange ID [Source: CoinPaprika]\n
            `exmarkets_chart`: Get all markets for given exchange [Source: CoinPaprika]\n
            `exrates`: Get list of crypto, fiats, commodity exchange rates from CoinGecko API [Source: CoinGecko]\n
            `exrates_chart`: Shows  list of crypto, fiats, commodity exchange rates. [Source: CoinGecko]\n
            `globe`: Get global crypto market data.\n
            `hm`: Get N coins from CoinGecko [Source: CoinGecko]\n
            `hm_chart`: Shows cryptocurrencies heatmap [Source: CoinGecko]\n
            `hold`: Returns public companies that holds ethereum or bitcoin [Source: CoinGecko]\n
            `hold_chart`: Shows overview of public companies that holds ethereum or bitcoin. [Source: CoinGecko]\n
            `indexes`: Get list of crypto indexes from CoinGecko API [Source: CoinGecko]\n
            `indexes_chart`: Shows list of crypto indexes. [Source: CoinGecko]\n
            `info`: Returns basic coin information for all coins from CoinPaprika API [Source: CoinPaprika]\n
            `info_chart`: Displays basic coin information for all coins from CoinPaprika API. [Source: CoinPaprika]\n
            `markets`: Returns basic coin information for all coins from CoinPaprika API [Source: CoinPaprika]\n
            `markets_chart`: Displays basic market information for all coins from CoinPaprika API. [Source: CoinPaprika]\n
            `news`: Get recent posts from CryptoPanic news aggregator platform. [Source: https://cryptopanic.com/]\n
            `news_chart`: Display recent posts from CryptoPanic news aggregator platform.\n
            `platforms`: List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama ... [Source: CoinPaprika]\n
            `platforms_chart`: List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama.\n
            `products`: Get list of financial products from CoinGecko API\n
            `products_chart`: Shows list of financial products. [Source: CoinGecko]\n
            `stables`: Returns top stable coins [Source: CoinGecko]\n
            `stables_chart`: Shows stablecoins data [Source: CoinGecko]\n
            `wf`: Scrapes top coins withdrawal fees\n
            `wf_chart`: Top coins withdrawal fees\n
            `wfpe`: Scrapes coin withdrawal fees per exchange\n
            `wfpe_chart`: Coin withdrawal fees per exchange\n
        """

        return model.CryptoOverview()

    @property
    def tools(self):
        """Cryptocurrency Tools Submodule

        Attributes:
            `apy`: Converts apr into apy\n
            `apy_chart`: Displays APY value converted from APR\n
            `il`: Calculates Impermanent Loss in a custom liquidity pool\n
            `il_chart`: Displays Impermanent Loss in a custom liquidity pool\n
        """

        return model.CryptoTools()
