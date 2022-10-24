To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.defi.vaults(chain: Optional[str] = None, protocol: Optional[str] = None, kind: Optional[str] = None, ascend: bool = True, sortby: str = 'apy') -> pandas.core.frame.DataFrame

Get DeFi Vaults Information. DeFi Vaults are pools of funds with an assigned strategy which main goal is to
    maximize returns of its crypto assets. [Source: https://coindix.com/]

    Parameters
    ----------
    chain: str
        Blockchain - one from list [
            'ethereum', 'polygon', 'avalanche', 'bsc', 'terra', 'fantom',
            'moonriver', 'celo', 'heco', 'okex', 'cronos', 'arbitrum', 'eth',
            'harmony', 'fuse', 'defichain', 'solana', 'optimism'
        ]
    protocol: str
        DeFi protocol - one from list: [
            'aave', 'acryptos', 'alpaca', 'anchor', 'autofarm', 'balancer', 'bancor',
            'beefy', 'belt', 'compound', 'convex', 'cream', 'curve', 'defichain', 'geist',
            'lido', 'liquity', 'mirror', 'pancakeswap', 'raydium', 'sushi', 'tarot', 'traderjoe',
            'tulip', 'ubeswap', 'uniswap', 'venus', 'yearn'
        ]
    kind: str
        Kind/type of vault - one from list: ['lp','single','noimploss','stable']

    Returns
    -------
    pd.DataFrame
        Top 100 DeFi Vaults for given chain/protocol sorted by APY.

## Getting charts 
### crypto.defi.vaults(chain: Optional[str] = None, protocol: Optional[str] = None, kind: Optional[str] = None, limit: int = 10, sortby: str = 'apy', ascend: bool = True, link: bool = False, export: str = '', chart=True) -> None

Display Top DeFi Vaults - pools of funds with an assigned strategy which main goal is to
    maximize returns of its crypto assets. [Source: https://coindix.com/]

    Parameters
    ----------
    chain: str
        Blockchain - one from list [
            'ethereum', 'polygon', 'avalanche', 'bsc', 'terra', 'fantom',
            'moonriver', 'celo', 'heco', 'okex', 'cronos', 'arbitrum', 'eth',
            'harmony', 'fuse', 'defichain', 'solana', 'optimism'
        ]
    protocol: str
        DeFi protocol - one from list: [
            'aave', 'acryptos', 'alpaca', 'anchor', 'autofarm', 'balancer', 'bancor',
            'beefy', 'belt', 'compound', 'convex', 'cream', 'curve', 'defichain', 'geist',
            'lido', 'liquity', 'mirror', 'pancakeswap', 'raydium', 'sushi', 'tarot', 'traderjoe',
            'tulip', 'ubeswap', 'uniswap', 'venus', 'yearn'
        ]
    kind: str
        Kind/type of vault - one from list: ['lp','single','noimploss','stable']
    limit: int
        Number of records to display
    sortby: str
        Key by which to sort data
    ascend: bool
        Flag to sort data descending
    link: bool
        Flag to show links
    export : str
        Export dataframe data to csv,json,xlsx file
