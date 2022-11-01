.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get DeFi Vaults Information. DeFi Vaults are pools of funds with an assigned strategy which main goal is to
    maximize returns of its crypto assets. [Source: https://coindix.com/]
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.defi.vaults(
    chain: Optional[str] = None,
    protocol: Optional[str] = None,
    kind: Optional[str] = None,
    ascend: bool = True,
    sortby: str = 'apy',
    chart: bool = False
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Parameters**

    chain: *str*
        Blockchain - one from list [
            'ethereum', 'polygon', 'avalanche', 'bsc', 'terra', 'fantom',
            'moonriver', 'celo', 'heco', 'okex', 'cronos', 'arbitrum', 'eth',
            'harmony', 'fuse', 'defichain', 'solana', 'optimism'
        ]
    protocol: *str*
        DeFi protocol - one from list: [
            'aave', 'acryptos', 'alpaca', 'anchor', 'autofarm', 'balancer', 'bancor',
            'beefy', 'belt', 'compound', 'convex', 'cream', 'curve', 'defichain', 'geist',
            'lido', 'liquity', 'mirror', 'pancakeswap', 'raydium', 'sushi', 'tarot', 'traderjoe',
            'tulip', 'ubeswap', 'uniswap', 'venus', 'yearn'
        ]
    kind: *str*
        Kind/type of vault - one from list: ['lp','single','noimploss','stable']

    
* **Returns**

    pd.DataFrame
        Top 100 DeFi Vaults for given chain/protocol sorted by APY.
    