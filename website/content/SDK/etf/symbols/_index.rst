.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Gets all etf names and symbols
    </h3>

{{< highlight python >}}
etf.symbols(
    ) -> Tuple[List[str], List[str]]
{{< /highlight >}}

* **Returns**

    etf\_symbols: List[str]:
        List of all available etf symbols
    etf\_names: List[str]
        List of all available etf names
    