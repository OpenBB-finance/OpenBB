# flake8: noqa
# pylint: disable=C0301,R0902,R0903
from openbb_terminal.sdk_core.models import crypto_sdk_model as model


class CryptoController(model.CryptoRoot):
    """OpenBB SDK Cryptocurrency Module.

    Submodules:
        `dd`: Due Diligence Module
        `defi`: DeFi Module
        `disc`: Discovery Module
        `nft`: NFT Module
        `onchain`: OnChain Module
        `ov`: Overview Module
        `tools`: Tools Module

    Attributes:
        `candles`: Plot candle chart from dataframe. [Source: Binance]\n
        `chart`: Load data for Technical Analysis\n
        `find`: Find similar coin by coin name,symbol or id.\n
        `load`: Load crypto currency to get data for\n
    """

    @property
    def dd(self):
        """OpenBB SDK Crypto Due Diligence Submodule

        Submodules:
            `dd`: Due Diligence Module

        Attributes:
            `active`: Returns active addresses of a certain symbol\n
            `active_view`: Display active addresses of a certain symbol over time\n
            `balance`: Get account holdings for asset. [Source: Binance]\n
            `balance_view`: Get account holdings for asset. [Source: Binance]\n
            `basic_info`: Basic coin information [Source: CoinPaprika]\n
            `binance_available_quotes_for_each_coin`: Helper methods that for every coin available on Binance add all quote assets. [Source: Binance]\n
            `book`: Get order book for currency. [Source: Binance]\n
            `book_view`: Get order book for currency. [Source: Binance]\n
            `candles`: Get candles for chosen trading pair and time interval. [Source: Coinbase]\n
            `candles_view`: Get candles for chosen trading pair and time interval. [Source: Coinbase]\n
            `cbbook`: Get orders book for chosen trading pair. [Source: Coinbase]\n
            `cbbook_view`: Displays a list of available currency pairs for trading. [Source: Coinbase]\n
            `change`: Returns 30d change of the supply held in exchange wallets of a certain symbol.\n
            `change_view`: Display 30d change of the supply held in exchange wallets.\n
            `check_valid_binance_string`: Check if symbol is in defined binance. [Source: Binance]\n
            `close`: Returns the price of a cryptocurrency\n
            `coin`: Get coin by id [Source: CoinPaprika]\n
            `coin_market_chart`: Get prices for given coin. [Source: CoinGecko]\n
            `eb`: Returns the total amount of coins held on exchange addresses in units and percentage.\n
            `eb_view`: Display total amount of coins held on exchange addresses in units and percentage.\n
            `events`: Get all events related to given coin like conferences, start date of futures trading etc.\n
            `events_view`: Get all events for given coin id. [Source: CoinPaprika]\n
            `ex`: Get all exchanges for given coin id. [Source: CoinPaprika]\n
            `ex_view`: Get all exchanges for given coin id. [Source: CoinPaprika]\n
            `exchanges`: Helper method to get all the exchanges supported by ccxt\n
            `fr`: Returns coin fundraising\n
            `fr_view`: Display coin fundraising\n
            `get_binance_trading_pairs`: Returns all available pairs on Binance in DataFrame format. DataFrame has 3 columns symbol, baseAsset, quoteAsset\n
            `get_mt`: Returns available messari timeseries\n
            `get_mt_view`: Display messari timeseries list\n
            `gh`: Returns  a list of developer activity for a given coin and time interval.\n
            `gh_view`: Returns a list of github activity for a given coin and time interval.\n
            `gov`: Returns coin governance\n
            `gov_view`: Display coin governance\n
            `headlines`: Gets Sentiment analysis provided by FinBrain's API [Source: finbrain]\n
            `headlines_view`: Sentiment analysis from FinBrain for Cryptocurrencies\n
            `inv`: Returns coin investors\n
            `inv_view`: Display coin investors\n
            `links`: Returns asset's links\n
            `links_view`: Display coin links\n
            `mcapdom`: Returns market dominance of a coin over time\n
            `mcapdom_view`: Display market dominance of a coin over time\n
            `mkt`: All markets for given coin and currency [Source: CoinPaprika]\n
            `mkt_view`: Get all markets for given coin id. [Source: CoinPaprika]\n
            `mt`: Returns messari timeseries\n
            `mt_view`: Display messari timeseries\n
            `news`: Get recent posts from CryptoPanic news aggregator platform. [Source: https://cryptopanic.com/]\n
            `news_view`: Display recent posts from CryptoPanic news aggregator platform.\n
            `nonzero`: Returns addresses with non-zero balance of a certain symbol\n
            `nonzero_view`: Display addresses with non-zero balance of a certain symbol\n
            `ohlc_historical`: Open/High/Low/Close values with volume and market_cap. [Source: CoinPaprika]\n
            `oi`: Returns open interest by exchange for a certain symbol\n
            `oi_view`: Displays open interest by exchange for a certain cryptocurrency\n
            `pi`: Returns coin product info\n
            `pi_view`: Display project info\n
            `pr`: Fetch data to calculate potential returns of a certain coin. [Source: CoinGecko]\n
            `pr_view`: Displays potential returns of a certain coin. [Source: CoinGecko]\n
            `ps`: Get all most important ticker related information for given coin id [Source: CoinPaprika]\n
            `ps_view`: Get ticker information for single coin [Source: CoinPaprika]\n
            `rm`: Returns coin roadmap\n
            `rm_view`: Display coin roadmap\n
            `show_available_pairs_for_given_symbol`: Return all available quoted assets for given symbol. [Source: Binance]\n
            `stats`: Get 24 hr stats for the product. Volume is in base currency units.\n
            `stats_view`: Get 24 hr stats for the product. Volume is in base currency units.\n
            `team`: Returns coin team\n
            `team_view`: Display coin team\n
            `tk`: Returns coin tokenomics\n
            `tk_view`: Display coin tokenomics\n
            `tokenomics`: Get tokenomics for given coin. [Source: CoinGecko]\n
            `trades`: Get last N trades for chosen trading pair. [Source: Coinbase]\n
            `trades_view`: Display last N trades for chosen trading pair. [Source: Coinbase]\n
            `trading_pair_info`: Get information about chosen trading pair. [Source: Coinbase]\n
            `trading_pairs`: Helper method that return all trading pairs on binance. Methods ause this data for input for e.g\n
            `twitter`: Get twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]\n
            `twitter_view`: Get twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]\n
        """

        return model.CryptoDueDiligence()

    @property
    def defi(self):
        """OpenBB SDK Crypto DeFi Submodule

        Submodules:
            `defi`: DeFi Module

        Attributes:
            `aterra`: Returns historical data of an asset in a certain terra address\n
            `aterra_view`: Displays the 30-day history of specified asset in terra address\n
            `ayr`: Displays the 30-day history of the Anchor Yield Reserve.\n
            `ayr_view`: Displays the 30-day history of the Anchor Yield Reserve.\n
            `dtvl`: Returns information about historical tvl of a defi protocol.\n
            `dtvl_view`: Displays historical TVL of different dApps\n
            `gacc`: Get terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]\n
            `gacc_view`: Display terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]\n
            `gdapps`: Display top dApps (in terms of TVL) grouped by chain.\n
            `gdapps_view`: Display top dApps (in terms of TVL) grouped by chain.\n
            `gov_proposals`: Get terra blockchain governance proposals list [Source: https://fcd.terra.dev/swagger]\n
            `gov_proposals_view`: Display terra blockchain governance proposals list [Source: https://fcd.terra.dev/swagger]\n
            `ldapps`: Returns information about listed DeFi protocols, their current TVL and changes to it in the last hour/day/week.\n
            `ldapps_view`: Display information about listed DeFi protocols, their current TVL and changes to it in\n
            `luna_supply`: Get supply history of the Terra ecosystem\n
            `luna_supply_view`: Display Luna circulating supply stats\n
            `newsletters`: Scrape all substack newsletters from url list.\n
            `newsletters_view`: Display DeFi related substack newsletters.\n
            `pairs`: Get lastly added trade-able pairs on Uniswap with parameters like:\n
            `pairs_view`: Displays Lastly added pairs on Uniswap DEX.\n
            `pools`: Get uniswap pools by volume. [Source: https://thegraph.com/en/]\n
            `pools_view`: Displays uniswap pools by volume.\n
            `sinfo`: Get staking info for provided terra account [Source: https://fcd.terra.dev/swagger]\n
            `sinfo_view`: Display staking info for provided terra account address [Source: https://fcd.terra.dev/swagger]\n
            `sratio`: Get terra blockchain staking ratio history [Source: https://fcd.terra.dev/swagger]\n
            `sratio_view`: Display terra blockchain staking ratio history [Source: https://fcd.terra.dev/v1]\n
            `sreturn`: Get terra blockchain staking returns history [Source: https://fcd.terra.dev/v1]\n
            `sreturn_view`: Display terra blockchain staking returns history [Source: https://fcd.terra.dev/swagger]\n
            `stats`: Get base statistics about Uniswap DEX. [Source: https://thegraph.com/en/]\n
            `stats_view`: Displays base statistics about Uniswap DEX. [Source: https://thegraph.com/en/]\n
            `stvl`: Returns historical values of the total sum of TVLs from all listed protocols.\n
            `stvl_view`: Displays historical values of the total sum of TVLs from all listed protocols.\n
            `swaps`: Get the last 100 swaps done on Uniswap [Source: https://thegraph.com/en/]\n
            `swaps_view`: Displays last swaps done on Uniswap\n
            `tokens`: Get list of tokens trade-able on Uniswap DEX. [Source: https://thegraph.com/en/]\n
            `tokens_view`: Displays tokens trade-able on Uniswap DEX.\n
            `validators`: Get information about terra validators [Source: https://fcd.terra.dev/swagger]\n
            `validators_view`: Display information about terra validators [Source: https://fcd.terra.dev/swagger]\n
        """

        return model.CryptoDeFi()

    @property
    def disc(self):
        """OpenBB SDK Crypto Discovery Submodule

        Submodules:
            `disc`: Discovery Module

        Attributes:
            `cmctop`: Shows top n coins. [Source: CoinMarketCap]\n
            `cmctop_view`: Shows top n coins. [Source: CoinMarketCap]\n
            `coin_list`: Get list of coins available on CoinGecko [Source: CoinGecko]\n
            `coins`: Get N coins from CoinGecko [Source: CoinGecko]\n
            `coins_view`: Display top coins [Source: CoinGecko]\n
            `coins_for_given_exchange`: Helper method to get all coins available on binance exchange [Source: CoinGecko]\n
            `cpsearch`: Search CoinPaprika. [Source: CoinPaprika]\n
            `cpsearch_view`: Search over CoinPaprika. [Source: CoinPaprika]\n
            `gainers`: Shows Largest Gainers - coins which gain the most in given period. [Source: CoinGecko]\n
            `gainers_view`: Shows Largest Gainers - coins which gain the most in given period. [Source: CoinGecko]\n
            `gainers_or_losers`: Returns data about top gainers - coins which gain the most in given period and\n
            `losers`: Shows Largest Losers - coins which lose the most in given period. [Source: CoinGecko]\n
            `losers_view`: Shows Largest Losers - coins which lost the most in given period of time. [Source: CoinGecko]\n
            `top_dapps`: Get top decentralized applications by daily volume and users [Source: https://dappradar.com/]\n
            `top_dapps_view`: Displays top decentralized exchanges [Source: https://dappradar.com/]\n
            `top_dexes`: Get top dexes by daily volume and users [Source: https://dappradar.com/]\n
            `top_dexes_view`: Displays top decentralized exchanges [Source: https://dappradar.com/]\n
            `top_games`: Get top blockchain games by daily volume and users [Source: https://dappradar.com/]\n
            `top_games_view`: Displays top blockchain games [Source: https://dappradar.com/]\n
            `top_nfts`: Get top nft collections [Source: https://dappradar.com/]\n
            `top_nfts_view`: Displays top nft collections [Source: https://dappradar.com/]\n
            `trending`: Returns trending coins [Source: CoinGecko]\n
            `trending_view`: Display trending coins [Source: CoinGecko]\n
        """

        return model.CryptoDiscovery()

    @property
    def nft(self):
        """OpenBB SDK Crypto NFT Submodule

        Submodules:
            `nft`: NFT Module

        Attributes:
            `collections`: Get nft collections [Source: https://nftpricefloor.com/]\n
            `collections_view`: Display NFT collections. [Source: https://nftpricefloor.com/]\n
            `fp`: Get nft collections [Source: https://nftpricefloor.com/]\n
            `fp_view`: Display NFT collection floor price over time. [Source: https://nftpricefloor.com/]\n
            `stats`: Get stats of a nft collection [Source: opensea.io]\n
            `stats_view`: Display collection stats. [Source: opensea.io]\n
        """

        return model.CryptoNFT()

    @property
    def onchain(self):
        """OpenBB SDK Crypto OnChain Submodule

        Submodules:
            `onchain`: OnChain Module

        Attributes:
            `baas`: Get an average bid and ask prices, average spread for given crypto pair for chosen time period.\n
            `baas_view`: Display an average bid and ask prices, average spread for given crypto pair for chosen\n
            `balance`: Get info about tokens on you ethereum blockchain balance. Eth balance, balance of all tokens which\n
            `balance_view`: Display info about tokens for given ethereum blockchain balance e.g. ETH balance,\n
            `btc_supply`: Returns BTC circulating supply [Source: https://api.blockchain.info/]\n
            `btc_supply_view`: Returns BTC circulating supply [Source: https://api.blockchain.info/]\n
            `btc_transac`: Returns BTC confirmed transactions [Source: https://api.blockchain.info/]\n
            `btc_transac_view`: Returns BTC confirmed transactions [Source: https://api.blockchain.info/]\n
            `dex_trades_monthly`: Get list of trades on Decentralized Exchanges monthly aggregated.\n
            `dvcp`: Get daily volume for given pair [Source: https://graphql.bitquery.io/]\n
            `dvcp_view`: Display daily volume for given pair\n
            `erc20_tokens`: Helper method that loads ~1500 most traded erc20 token.\n
            `gwei`: Returns the most recent Ethereum gas fees in gwei\n
            `gwei_view`: Current gwei fees\n
            `hist`: Get information about balance historical transactions. [Source: Ethplorer]\n
            `hist_view`: Display information about balance historical transactions. [Source: Ethplorer]\n
            `holders`: Get info about top token holders. [Source: Ethplorer]\n
            `holders_view`: Display info about top ERC20 token holders. [Source: Ethplorer]\n
            `hr`: Returns dataframe with mean hashrate of btc or eth blockchain and symbol price\n
            `hr_view`: Display dataframe with mean hashrate of btc or eth blockchain and symbol price.\n
            `info`: Get info about ERC20 token. [Source: Ethplorer]\n
            `info_view`: Display info about ERC20 token. [Source: Ethplorer]\n
            `lt`: Get trades on Decentralized Exchanges aggregated by DEX [Source: https://graphql.bitquery.io/]\n
            `lt_view`: Trades on Decentralized Exchanges aggregated by DEX or Month\n
            `prices`: Get token historical prices with volume and market cap, and average price. [Source: Ethplorer]\n
            `prices_view`: Display token historical prices with volume and market cap, and average price.\n
            `query_graph`: Helper methods for querying graphql api. [Source: https://bitquery.io/]\n
            `th`: Get info about token historical transactions. [Source: Ethplorer]\n
            `th_view`: Display info about token history. [Source: Ethplorer]\n
            `token_decimals`: Helper methods that gets token decimals number. [Source: Ethplorer]\n
            `top`: Get top 50 tokens. [Source: Ethplorer]\n
            `top_view`: Display top ERC20 tokens [Source: Ethplorer]\n
            `ttcp`: Get most traded crypto pairs on given decentralized exchange in chosen time period.\n
            `ttcp_view`: Display most traded crypto pairs on given decentralized exchange in chosen time period.\n
            `tv`: Get token volume on different Decentralized Exchanges. [Source: https://graphql.bitquery.io/]\n
            `tv_view`: Display token volume on different Decentralized Exchanges.\n
            `tx`: Get info about transaction. [Source: Ethplorer]\n
            `tx_view`: Display info about transaction. [Source: Ethplorer]\n
            `ueat`: Get number of unique ethereum addresses which made a transaction in given time interval.\n
            `ueat_view`: Display number of unique ethereum addresses which made a transaction in given time interval\n
            `whales`: Whale Alert's API allows you to retrieve live and historical transaction data from major blockchains.\n
            `whales_view`: Display huge value transactions from major blockchains. [Source: https://docs.whale-alert.io/]\n
        """

        return model.CryptoOnChain()

    @property
    def ov(self):
        """OpenBB SDK Crypto Overview Submodule

        Submodules:
            `ov`: Overview Module

        Attributes:
            `altindex`: Get altcoin index overtime\n
            `altindex_view`: Displays altcoin index overtime\n
            `btcrb`: Get bitcoin price data\n
            `btcrb_view`: Displays bitcoin rainbow chart\n
            `cbpairs`: Get a list of available currency pairs for trading. [Source: Coinbase]\n
            `cbpairs_view`: Displays a list of available currency pairs for trading. [Source: Coinbase]\n
            `cgcategories`: Returns top crypto categories [Source: CoinGecko]\n
            `cgcategories_view`: Shows top cryptocurrency categories by market capitalization\n
            `cgdefi`: Get global statistics about Decentralized Finances [Source: CoinGecko]\n
            `cgdefi_view`: Shows global statistics about Decentralized Finances. [Source: CoinGecko]\n
            `cgderivatives`: Get list of crypto derivatives from CoinGecko API [Source: CoinGecko]\n
            `cgderivatives_view`: Shows  list of crypto derivatives. [Source: CoinGecko]\n
            `cgexrates`: Get list of crypto, fiats, commodity exchange rates from CoinGecko API [Source: CoinGecko]\n
            `cgexrates_view`: Shows  list of crypto, fiats, commodity exchange rates. [Source: CoinGecko]\n
            `cgglobal`: Get global statistics about crypto markets from CoinGecko API like:\n
            `cgglobal_view`: Shows global statistics about crypto. [Source: CoinGecko]\n
            `cgh`: Get N coins from CoinGecko [Source: CoinGecko]\n
            `cgh_view`: Shows cryptocurrencies heatmap [Source: CoinGecko]\n
            `cghold`: Returns public companies that holds ethereum or bitcoin [Source: CoinGecko]\n
            `cghold_view`: Shows overview of public companies that holds ethereum or bitcoin. [Source: CoinGecko]\n
            `cgindexes`: Get list of crypto indexes from CoinGecko API [Source: CoinGecko]\n
            `cgindexes_view`: Shows list of crypto indexes. [Source: CoinGecko]\n
            `cgproducts`: Get list of financial products from CoinGecko API\n
            `cgproducts_view`: Shows list of financial products. [Source: CoinGecko]\n
            `cgstables`: Returns top stable coins [Source: CoinGecko]\n
            `cgstables_view`: Shows stablecoins data [Source: CoinGecko]\n
            `cpcontracts`: Gets all contract addresses for given platform [Source: CoinPaprika]\n
            `cpcontracts_view`: Gets all contract addresses for given platform. [Source: CoinPaprika]\n
            `cpexchanges`: List exchanges from CoinPaprika API [Source: CoinPaprika]\n
            `cpexchanges_view`: List exchanges from CoinPaprika API. [Source: CoinPaprika]\n
            `cpexmarkets`: List markets by exchange ID [Source: CoinPaprika]\n
            `cpexmarkets_view`: Get all markets for given exchange [Source: CoinPaprika]\n
            `cpglobal`: Return data frame with most important global crypto statistics like:\n
            `cpglobal_view`: Return data frame with most important global crypto statistics like:\n
            `cpinfo`: Returns basic coin information for all coins from CoinPaprika API [Source: CoinPaprika]\n
            `cpinfo_view`: Displays basic coin information for all coins from CoinPaprika API. [Source: CoinPaprika]\n
            `cpmarkets`: Returns basic coin information for all coins from CoinPaprika API [Source: CoinPaprika]\n
            `cpmarkets_view`: Displays basic market information for all coins from CoinPaprika API. [Source: CoinPaprika]\n
            `cpplatforms`: List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama ... [Source: CoinPaprika]\n
            `cpplatforms_view`: List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama.\n
            `cr`: Returns crypto {borrow,supply} interest rates for cryptocurrencies across several platforms\n
            `cr_view`: Displays crypto {borrow,supply} interest rates for cryptocurrencies across several platforms\n
            `crypto_hack`: Get crypto hack\n
            `crypto_hack_slugs`: Get all crypto hack slugs\n
            `crypto_hacks`: Get major crypto-related hacks\n
            `crypto_hacks_view`: Display list of major crypto-related hacks. If slug is passed\n
            `ewf`: Scrapes exchange withdrawal fees\n
            `ewf_view`: Exchange withdrawal fees\n
            `exchanges`: Get list of top exchanges from CoinGecko API [Source: CoinGecko]\n
            `exchanges_view`: Shows list of top exchanges from CoinGecko. [Source: CoinGecko]\n
            `global_info`: Get global statistics about crypto from CoinGecko API like:\n
            `list_of_coins`: Get list of all available coins on CoinPaprika  [Source: CoinPaprika]\n
            `news`: Get recent posts from CryptoPanic news aggregator platform. [Source: https://cryptopanic.com/]\n
            `news_view`: Display recent posts from CryptoPanic news aggregator platform.\n
            `platforms`: Get list of financial platforms from CoinGecko API [Source: CoinGecko]\n
            `platforms_view`: Shows list of financial platforms. [Source: CoinGecko]\n
            `wf`: Scrapes top coins withdrawal fees\n
            `wf_view`: Top coins withdrawal fees\n
            `wfpe`: Scrapes coin withdrawal fees per exchange\n
            `wfpe_view`: Coin withdrawal fees per exchange\n
        """

        return model.CryptoOverview()

    @property
    def tools(self):
        """OpenBB SDK Crypto Tools Submodule

        Submodules:
            `tools`: Tools Module

        Attributes:
            `apy`: Converts apr into apy\n
            `apy_view`: Displays APY value converted from APR\n
            `il`: Calculates Impermanent Loss in a custom liquidity pool\n
            `il_view`: Displays Impermanent Loss in a custom liquidity pool\n
        """

        return model.CryptoTools()
