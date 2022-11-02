.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Get base statistics about Uniswap DEX. [Source: https://thegraph.com/en/]

    uniswapFactory id: 0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f - ethereum address on which Uniswap Factory
    smart contract was deployed. The factory contract is deployed once from the off-chain source code, and it contains
    functions that make it possible to create exchange contracts for any ERC20 token that does not already have one.
    It also functions as a registry of ERC20 tokens that have been added to the system, and the exchange with which they
    are associated. More: https://docs.uniswap.org/protocol/V1/guides/connect-to-uniswap
    We use 0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f address to fetch all smart contracts that were
    created with usage of this factory.
    </h3>

To obtain charts, make sure to add :python:`chart = True` as the last parameter

{{< highlight python >}}
crypto.defi.stats(
    chart: bool = False,
) -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    pd.DataFrame
        Uniswap DEX statistics like liquidity, volume, number of pairs, number of transactions.
   