.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Getting data
    </h3>

{{< highlight python >}}
keys.reddit(
    client_id: str,
    client_secret: str,
    password: str,
    username: str,
    useragent: str,
    persist: bool = False,
    show_output: bool = False,
    chart: bool = False,
) -> str
{{< /highlight >}}

.. raw:: html

    <p>
    Set Reddit key
    </p>

* **Parameters**

    client_id: str
        Client ID
    client_secret: str
        Client secret
    password: str
        User assword
    username: str
        User username
    useragent: str
        User useragent
    persist: bool
        If False, api key change will be contained to where it was changed. For example, Jupyter notebook.
        If True, api key change will be global, i.e. it will affect terminal environment variables.
        By default, False.
    show_output: bool
        Display status string or not. By default, False.

* **Returns**

    status: str
