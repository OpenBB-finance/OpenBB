To obtain charts, make sure to add `chart=True` as the last parameter

## Get underlying data 
### crypto.defi.stats() -> pandas.core.frame.DataFrame

Get base statistics about Uniswap DEX. [Source: https://thegraph.com/en/]

    uniswapFactory id: 0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f - ethereum address on which Uniswap Factory
    smart contract was deployed. The factory contract is deployed once from the off-chain source code, and it contains
    functions that make it possible to create exchange contracts for any ERC20 token that does not already have one.
    It also functions as a registry of ERC20 tokens that have been added to the system, and the exchange with which they
    are associated. More: https://docs.uniswap.org/protocol/V1/guides/connect-to-uniswap
    We use 0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f address to fetch all smart contracts that were
    created with usage of this factory.


    Returns
    -------
    pd.DataFrame
        Uniswap DEX statistics like liquidity, volume, number of pairs, number of transactions.

## Getting charts 
### crypto.defi.stats(export: str = '', chart=True) -> None

Displays base statistics about Uniswap DEX. [Source: https://thegraph.com/en/]
    [Source: https://thegraph.com/en/]

    Parameters
    ----------

    export : str
        Export dataframe data to csv,json,xlsx file
