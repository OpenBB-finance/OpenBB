.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
crypto.onchain.erc20_tokens() -> pandas.core.frame.DataFrame
{{< /highlight >}}

.. raw:: html

    <p>
    Helper method that loads ~1500 most traded erc20 token.
    [Source: json file]
    </p>

* **Returns**

    pd.DataFrame
        ERC20 tokens with address, symbol and name
