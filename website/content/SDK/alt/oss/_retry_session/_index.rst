.. role:: python(code)
    :language: python
    :class: highlight

|

.. raw:: html

    <h3>
    > Helper methods that retries to make request
    </h3>

{{< highlight python >}}
alt.oss._retry_session(
    url: str,
    retries: int = 3,
    backoff_factor: float = 1.0,
) -> requests.sessions.Session
{{< /highlight >}}

* **Parameters**

    url: *str*
        Url to mount a session
    retries: *int*
        How many retries
    backoff_factor: *float*
        Backoff schema - time periods between retry

    
* **Returns**

    requests.Session
        Mounted session
    