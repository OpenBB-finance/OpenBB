.. role:: python(code)
    :language: python
    :class: highlight

|

To obtain charts, make sure to add :python:`chart = True` as the last parameter.

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.defi.vaults(
    chain: Optional[str] = None,
    protocol: Optional[str] = None,
    kind: Optional[str] = None,
    ascend: bool = True,
    sortby: str = 'apy',
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Get DeFi Vaults Information. DeFi Vaults are pools of funds with an assigned strategy which main goal is to
    maximize returns of its crypto assets. [Source: https://coindix.com/]
    </p>

* **Parameters**

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
    chart: bool
       Flag to display chart


* **Returns**

    pd.DataFrame
        Top 100 DeFi Vaults for given chain/protocol sorted by APY.

|

.. raw:: html

    <h3>
    > Getting charts
    </h3>

{{< highlight python >}}
crypto.defi.vaults(
    chain: Optional[str] = None,
    protocol: Optional[str] = None,
    kind: Optional[str] = None,
    limit: int = 10,
    sortby: str = 'apy',
    ascend: bool = True,
    link: bool = False,
    export: str = '',
    chart: bool = False,
) -> None
{{< /highlight >}}

.. raw:: html

    <p>
    Display Top DeFi Vaults - pools of funds with an assigned strategy which main goal is to
    maximize returns of its crypto assets. [Source: https://coindix.com/]
    </p>

* **Parameters**

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
    chart: bool
       Flag to display chart

