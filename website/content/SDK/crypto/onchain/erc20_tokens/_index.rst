.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Helper method that loads ~1500 most traded erc20 token.
    [Source: json file]
    </h3>

{{< highlight python >}}
crypto.onchain.erc20_tokens() -> pandas.core.frame.DataFrame
{{< /highlight >}}

* **Returns**

    pd.DataFrame
        ERC20 tokens with address, symbol and name
    