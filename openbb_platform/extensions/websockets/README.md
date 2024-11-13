# OpenBB WebSockets Toolkit

At the application/API level, the user does not directly interact with the client, or provider stream.
Connections are established as background tasks, and there are not any direct methods for blocking the main thread and command line.


## Endpoints

The extension creates a new router path from the application base - `obb.websockets`, api/v1/websockets for the API.

Endpoints are for managing the life cycle of one or more provider websocket connections.

```python
from openbb import obb

obb.websockets
```

```sh
/websockets
    clear_results
    create_connection
    get_client # Not included in API
    get_client_status
    get_results
    kill
    restart_connection
    start_broadcasting
    stop_broadcasting
    stop_connection
    subscribe
    unsubscribe
```

> Except for, `get_results`, functions do not return the data or stream. Outputs will be a WebSocketConnectionStatus instance, or a string message.
> All functions, except `create_connection`, assume that a connection has already been establiehd and are referenced by parameters:
>
> |Parameter|Type | Required| Description |
> |:-------|:-----|:--------:|------------:|
> |name |String |Yes |The 'nane' assigned from `create_connection` |
> |auth_token |String |No |The 'auth_token' assigned, if any, from `create_connection` |
>
> Below is an explanation of each function, with `create_connection` representing the bulk of details.

### create_connection

All other endpoints require this to be used first. It is the only function mapping to the Provider Interface, and is used to establish a new connection.

#### Standard Parameters

|Parameter|Type | Required| Description |
|:-------|:-----|:--------:|------------:|
|provider |String |Yes |Name of the provider - i.e, `"polygon"`, `"fmp"`, `"tiingo"` |
|name |String |Yes |Name to assign the connection. This is the 'name' parameter in the other endpoints.|
|auth_token |String |No |When supplied, the same token must be passed for all future interactions with the connection, or to read from the broadcast server. |
|results_file |String |No |Absolute path to the file for continuous writing. Temp file is created by default. Unless 'save_results' is True, discarded on exit. |
|save_results |Boolean |No |Whether to persist the file after the session ends, default is `False` |
|table_name |String |No |Name of the SQL table to write the results to, consisting of an auto-increment ID and a serialized JSON string of the data. Default is `"records"`|
|limit |Integer |No |Maximum number of records to store in the 'results_file', set as `None` to retain all data messages. Default is `1000`|
|sleep_time |Float |No |Does not impact the provider connection. Time, in seconds, to sleep between checking for new records, default is `0.25` |
|broadcast_host |String |No |IP address for running the broadcast server, default is `"127.0.0.1"` |
|broadcast_port |Integer |No |Port number to bind the broadcasat server to, default is `6666` |
|start_broadcast |Boolean |No |Whether to start the broadcast server immediately, default is `False` |
|connect_kwargs |Dictionary |No |Keyword arguments to pass directly to `websockets.connect()` in the provider module. Also accepts a serialized JSON string dictionary. |


#### Provider-Specific Parameters

Other parameters will be specific to the provider, but there may be common ground. Refer to the function's docstring for more detail.
The table below is not intended as a source of truth.

|Parameter|Type | Required| Description |
|:-------|:-----|:--------:|------------:|
|symbol |String |Yes |The ticker symbol for the asset - i.e, `"aapl"`, `"usdjpy"`, `"dogeusd"`, `"btcusd,ethusd"`, `"*"`|
|asset_type |String |Yes |The asset type associated with the 'symbol'. Choices vary by provider, but typically include [`"stock"`, `"fx"`, `"crypto"`] |
|feed |String |No |The particular feed to subscribe to, if available. Choices vary by provider, but might include [`"trade"`, `"quote"`] |

Availability will depend on the access level permitted by the provider's API key.

#### Example

```python
conn = obb.websockets.create_connection(provider="tiingo", asset_type="crypto", symbol="*", feed="trade", start_broadcast=True)

conn
```

```sh
PROVIDER INFO:      WebSocket connection established.

PROVIDER INFO:      Authorization: Success

BROADCAST INFO:     Stream results from ws://127.0.0.1:6666

OBBject[T]

id: 06732d37-fe11-744c-8000-072414ba1cdd
results: {'name': 'crypto_tiingo', 'auth_required': False, 'subscribed_symbols': '*...
provider: tiingo
warnings: None
chart: None
extra: {'metadata': {'arguments': {'provider_choices': {'provider': 'tiingo'}, 'sta...
```

```python
conn.results.model_dump()
```

```sh
{'name': 'crypto_tiingo',
 'auth_required': False,
 'subscribed_symbols': '*',
 'is_running': True,
 'provider_pid': 5810,
 'is_broadcasting': True,
 'broadcast_address': 'ws://127.0.0.1:6666',
 'broadcast_pid': 5813,
 'results_file': '/var/folders/kc/j2lm7bkd5dsfqqnvz259gm6c0000gn/T/tmpwb4jslbg',
 'table_name': 'records',
 'save_results': False}
```

All of the currently captured data can be dumped with the `get_results` endpoint. The return will be the typical data response object.

```python
obb.websockets.get_results("crypto_tiingo").to_df().iloc[-5:]
```

| date                             | symbol   | type   | exchange   |   last_price |   last_size |
|:---------------------------------|:---------|:-------|:-----------|-------------:|------------:|
| 2024-11-11 23:13:19.753398-05:00 | gfiusd   | trade  | gdax       |     1.89012  |    257.12   |
| 2024-11-11 23:13:19.757000-05:00 | ondousdt | trade  | mexc       |     0.930851 |   3508.35   |
| 2024-11-11 23:13:19.760000-05:00 | neousdt  | trade  | huobi      |    12.31     |     13.9489 |
| 2024-11-11 23:13:19.793594-05:00 | xrpusd   | trade  | gdax       |     0.60433  |   4676.46   |
| 2024-11-11 23:13:19.819856-05:00 | xlmusd   | trade  | gdax       |     0.11446  |    120.088  |

#### Listen

Listen to the stream by opening another terminal window and importing the `listen` function.

> Using this function within the same session is not recommended because `ctrl-c` will stop the provider and broadcast servers without properly terminating the processes. When this happens, use the `kill` endpoint to finish the job.


```python
from openbb_websockets.listen import listen

listen("ws://127.0.0.1:6666")
```

```sh
Listening for messages from ws://127.0.0.1:6666

{"date":"2024-11-11T23:51:33.083000-05:00","symbol":"klvusdt","type":"trade","exchange":"huobi","last_price":0.00239,"last_size":8367.4749}

{"date":"2024-11-11T23:51:33.082000-05:00","symbol":"actsolusdt","type":"trade","exchange":"huobi","last_price":0.5837245604964619,"last_size":1070.2939999999999}
...
```

Opening a listener will notify the main thread:

```sh
BROADCAST INFO:     ('127.0.0.1', 59197) - "WebSocket /" [accepted]

BROADCAST INFO:     connection open

BROADCAST INFO:     connection closed
```

The provider connection can be stopped and restarted without disrupting the broadcast server.
The broadcast server can be terminated without stopping the provider connection.


### clear_results

Clears the items written to `results_file`. The connection can be running or stopped and does not terminate writing or reading.

#### Example

```python
obb.websockets.clear_results("crypto_tiingo")
```

```sh
Results cleared from table records in /var/folders/kc/j2lm7bkd5dsfqqnvz259gm6c0000gn/T/tmpwb4jslbg

OBBject[T]

id: 06732ed2-a72c-758e-8000-b7943259f615
results: 1001 results cleared from crypto_tiingo.
provider: None
warnings: None
chart: None
extra: {'metadata': {'arguments': {'provider_choices': {}, 'standard_params': {}, '...
```


### get_client

> Not available from the API.

This returns the `WebSocketClient` object, and the provider client can be controlled directly as a Python object. Refer to the [Development](README.md#development) section for a detailed explanation of this class.

#### Example

```python
client = obb.websockets.get_client("crypto_tiingo").results
```

```sh
WebSocketClient(module=['/Users/someuser/miniconda3/envs/obb/bin/python', '-m', 'openbb_tiingo.utils.websocket_client'], symbol=*, is_running=True, provider_pid: 7125, is_broadcasting=True, broadcast_address=ws://127.0.0.1:6666, broadcast_pid: 7128, results_file=/var/folders/kc/j2lm7bkd5dsfqqnvz259gm6c0000gn/T/tmpwb4jslbg, table_name=records, save_results=False)
```

```python
print(client.is_running)
client.disconnect()
print(client.is_running)
```

```sh
True
Disconnected from the provider WebSocket.
False
```

### get_client_status

Get the current status of an initialized WebSocketConnection.

#### Example

```python
obb.websockets.get_client_status("all").to_dict("records")
```

```sh
[{'name': 'crypto_tiingo',
  'auth_required': False,
  'subscribed_symbols': '*',
  'is_running': False,
  'provider_pid': None
  'is_broadcasting': True,
  'broadcast_address': 'ws://127.0.0.1:6666',
  'broadcast_pid': 7723,
  'results_file': '/var/folders/kc/j2lm7bkd5dsfqqnvz259gm6c0000gn/T/tmpup7zd_uu',
  'table_name': 'records',
  'save_results': False},
 {'name': 'fx_polygon',
  'auth_required': False,
  'subscribed_symbols': '*',
  'is_running': True,
  'provider_pid': 7773}
  'is_broadcasting': False,
  'broadcast_address': None,
  'broadcast_pid': None,
  'results_file': '/var/folders/kc/j2lm7bkd5dsfqqnvz259gm6c0000gn/T/tmpzs6of15g',
  'table_name': 'records',
  'save_results': False]
```

### get_results

Get the captured records in the `results_file`.

```python
obb.websockets.get_results("fx_polygon").to_dict("records")[-1]
```

```sh
{'date': Timestamp('2024-11-12 01:41:03-0500', tz='UTC-05:00'),
 'symbol': 'CAD/SGD',
 'type': 'C',
 'exchange': 'Currency Banks 1',
 'bid': 0.958360440227192,
 'ask': 0.958407631503548}
```

### kill

Terminate a connection and all of its processes.

#### Example

```python
obb.websockets.kill("fx_polygon")
```

```sh
Disconnected from the provider WebSocket.

OBBject[T]

id: 06732fa3-1df8-7d82-8000-b492686a1b8b
results: Clients fx_polygon killed.
provider: None
warnings: None
chart: None
extra: {'metadata': {'arguments': {'provider_choices': {}, 'standard_params': {}, '...
```

### restart_connection

Restart a connection after running `stop_connection`.

#### Example

```python
obb.websockets.restart_connection("crypto_tiingo").results.model_dump()
```

```sh
PROVIDER INFO:      WebSocket connection established.

PROVIDER INFO:      Authorization: Success

{'name': 'crypto_tiingo',
 'auth_required': False,
 'subscribed_symbols': '*',
 'is_running': True,
 'provider_pid': 7939,
 'is_broadcasting': True,
 'broadcast_address': 'ws://127.0.0.1:6666',
 'broadcast_pid': 7723,
 'results_file': '/var/folders/kc/j2lm7bkd5dsfqqnvz259gm6c0000gn/T/tmpup7zd_uu',
 'table_name': 'records',
 'save_results': False}
```

### start_broadcasting

Start the broadcast server.

#### Additional Parameters

|Parameter|Type | Required| Description |
|:-------|:-----|:--------:|------------:|
|host |String |No |IP address to run the server over, default is `"127.0.0.1"` |
|port |Interger |No |Port to bind the server to, default is `6666` |
|uvicorn_kwargs| Dictionary |No |Additional keyword arguments to pass directly to `uvicorn.run()`. |

#### Example

```python
obb.websockets.start_broadcasting("crypto_tiingo").results
```

```sh
BROADCAST INFO:     Stream results from ws://127.0.0.1:6666

WebSocketConnectionStatus(name=crypto_tiingo, auth_required=False, subscribed_symbols=*, is_running=True, provider_pid=7939, is_broadcasting=True, broadcast_address=ws://127.0.0.1:6666, broadcast_pid=8080, results_file=/var/folders/kc/j2lm7bkd5dsfqqnvz259gm6c0000gn/T/tmpup7zd_uu, table_name=records, save_results=False)
```

### stop_broadcasting

Stop the broadcast server.

#### Example

```python
obb.websockets.stop_broadcasting("crypto_tiingo").results.model_dump()
```

```sh
Stopped broadcasting to: ws://127.0.0.1:6666

{'name': 'crypto_tiingo',
 'auth_required': False,
 'subscribed_symbols': '*',
 'is_running': True,
 'provider_pid': 7939,
 'is_broadcasting': False,
 'broadcast_address': None,
 'broadcast_pid': None,
 'results_file': '/var/folders/kc/j2lm7bkd5dsfqqnvz259gm6c0000gn/T/tmpup7zd_uu',
 'table_name': 'records',
 'save_results': False}
```

### stop_connection

Stop the provider websocket connection.

#### Example

```python
obb.websockets.stop_connection("crypto_tiingo").results.model_dump()
```

```sh
Disconnected from the provider WebSocket.

{'name': 'crypto_tiingo',
 'auth_required': False,
 'subscribed_symbols': '*',
 'is_running': False,
 'provider_pid': None,
 'is_broadcasting': False,
 'broadcast_address': None,
 'broadcast_pid': None,
 'results_file': '/var/folders/kc/j2lm7bkd5dsfqqnvz259gm6c0000gn/T/tmpup7zd_uu',
 'table_name': 'records',
 'save_results': False}
```

### subscribe

Subscribe to a new symbol(s). Enter multiple symbols as a comma-seperated string.

#### Example

```python
obb.websockets.subscribe("fx_polygon", symbol="xauusd")
```

```sh
PROVIDER INFO:      subscribed to: C.XAU/USD

OBBject[T]

id: 06733025-a43d-71ed-8000-981ec3cfb697
results: {'name': 'fx_polygon', 'auth_required': False, 'subscribed_symbols': 'EURU...
provider: None
warnings: None
chart: None
extra: {'metadata': {'arguments': {'provider_choices': {}, 'standard_params': {}, '...
```

### unsubscribe

Unsubscribe from a symbol(s)

#### Example

```python
obb.websockets.unsubscribe("fx_polygon", symbol="xauusd").results.model_dump()
```

```sh
PROVIDER INFO:      unsubscribed to: C.XAU/USD

{'name': 'fx_polygon',
 'auth_required': False,
 'subscribed_symbols': 'EURUSD',
 'is_running': True,
 'provider_pid': 8582,
 'is_broadcasting': False,
 'broadcast_address': None,
 'broadcast_pid': None,
 'results_file': '/var/folders/kc/j2lm7bkd5dsfqqnvz259gm6c0000gn/T/tmp1z70a3fw',
 'table_name': 'records',
 'save_results': False}
```



## Development


### Provider Interface

Providers can be added to the `create_connection` endpoint by following a slightly modified pattern.
This section outlines the adaptations, but does not contain any code for actually connecting to the provider's websocket.
For details on that part, go to [websocket_client](README.md###websocket_client) section below.


Here, the Fetcher is used to start the provider client module (in a separate file) and return the client to the router, where it is intercepted and kept alive.

> The provider client is not returned to the user, only its status.

In the provider's "/models" folder, we need a file, `my_provider_websoccket_connection.py`, and it will layout nearly the same as any other provider model.

We will create one additional model, `WebSocketConnection`, which has only one inherited field, 'client', and no other fields are permitted. This is what gets returned to the router.

We also need another file, in the `utils` folder, `websocket_client.py`.

Creating the QueryParams and Data models will be in the same style as all the other models, name it 'websocket_connection.py'.

#### WebSocketQueryParams

```python
"""FMP WebSocket model."""

from datetime import datetime
from typing import Any, Literal, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_websockets.client import WebSocketClient
from openbb_websockets.models import (
    WebSocketConnection,
    WebSocketData,
    WebSocketQueryParams,
)
from pydantic import Field, field_validator

URL_MAP = {
    "stock": "wss://websockets.financialmodelingprep.com",
    "fx": "wss://forex.financialmodelingprep.com",
    "crypto": "wss://crypto.financialmodelingprep.com",
}


class FmpWebSocketQueryParams(WebSocketQueryParams):
    """FMP WebSocket query parameters."""

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
        "asset_type": {
            "multiple_items_allowed": False,
            "choices": ["stock", "fx", "crypto"],
        },
    }

    symbol: str = Field(
        description="The FMP symbol to get data for.",
    )
    asset_type: Literal["stock", "fx", "crypto"] = Field(
        default="crypto",
        description="The asset type, required for the provider URI.",
    )
```

#### WebSocketData

```python
class FmpWebSocketData(WebSocketData):
    """FMP WebSocket data model."""

    __alias_dict__ = {
        "symbol": "s",
        "date": "t",
        "exchange": "e",
        "type": "type",
        "bid_size": "bs",
        "bid_price": "bp",
        "ask_size": "as",
        "ask_price": "ap",
        "last_price": "lp",
        "last_size": "ls",
    }

    exchange: Optional[str] = Field(
        default=None,
        description="The exchange of the data.",
    )
    type: Literal["quote", "trade", "break"] = Field(
        description="The type of data.",
    )
    bid_size: Optional[float] = Field(
        default=None,
        description="The size of the bid.",
    )
    bid_price: Optional[float] = Field(
        default=None,
        description="The price of the bid.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    ask_price: Optional[float] = Field(
        default=None,
        description="The price of the ask.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    ask_size: Optional[float] = Field(
        default=None,
        description="The size of the ask.",
    )
    last_price: Optional[float] = Field(
        default=None,
        description="The last trade price.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    last_size: Optional[float] = Field(
        default=None,
        description="The size of the trade.",
    )

    @field_validator("symbol", mode="before")
    def _validate_symbol(cls, v):
        """Validate the symbol."""
        return v.upper()

    @field_validator("type", mode="before", check_fields=False)
    def _valiidate_data_type(cls, v):
        """Validate the data type."""
        return (
            "quote" if v == "Q" else "trade" if v == "T" else "break" if v == "B" else v
        )

    @field_validator("date", mode="before", check_fields=False)
    def _validate_date(cls, v):
        """Validate the date."""
        # pylint: disable=import-outside-toplevel
        from pytz import timezone

        if isinstance(v, str):
            dt = datetime.fromisoformat(v)
        try:
            dt = datetime.fromtimestamp(v / 1000)
        except Exception:  # pylint: disable=broad-except
            if isinstance(v, (int, float)):
                # Check if the timestamp is in nanoseconds and convert to seconds
                if v > 1e12:
                    v = v / 1e9  # Convert nanoseconds to seconds
                dt = datetime.fromtimestamp(v)

        return dt.astimezone(timezone("America/New_York"))
```

#### WebSocketConnection

This model is what we return from the `FmpWebSocketFetcher`.


```python
class FmpWebSocketConnection(WebSocketConnection):
    """FMP WebSocket connection model."""
```

#### WebSocketFetcher

This is where things diverge slightly. Instead of returning `FmpWebSocketData`, we will pass it to the client connection insteadd, for validating records as they are received. What gets returned by the Fetcher is the `WebSocketConnection`.

```python
class FmpWebSocketFetcher(Fetcher[FmpWebSocketQueryParams, FmpWebSocketConnection]):
    """FMP WebSocket model."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FmpWebSocketQueryParams:
        """Transform the query parameters."""
        return FmpWebSocketQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FmpWebSocketQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> WebSocketClient:
        """Extract data from the WebSocket."""
        # pylint: disable=import-outside-toplevel
        import asyncio

        api_key = credentials.get("fmp_api_key") if credentials else ""
        url = URL_MAP[query.asset_type]

        symbol = query.symbol.lower()

        # Arrange a dictionary of parameters that will be passed to the client connection.
        kwargs = {
            "url": url,
            "api_key": api_key,
            "connect_kwargs": query.connect_kwargs, # Pass custom parameters to `websockets.connect()`
        }

        # The object to be returned. Everything the provider client thread needs to know is in this instance.
        client = WebSocketClient(
            name=query.name,
            module="openbb_fmp.utils.websocket_client",  # This is the file with the client connection that gets run as a script.
            symbol=symbol,
            limit=query.limit,
            results_file=query.results_file,
            table_name=query.table_name,
            save_results=query.save_results,
            data_model=FmpWebSocketData,  # WebSocketDataModel goes here.
            sleep_time=query.sleep_time,
            broadcast_host=query.broadcast_host,
            broadcast_port=query.broadcast_port,
            auth_token=query.auth_token,
            **kwargs,
        )

        # Start the client thread, give it a moment to startup and check for exceptions.
        try:
            client.connect()
            await asyncio.sleep(2)
            # Exceptions are triggered from the stdout reader and are converted
            # to a Python Exception that gets stored here.
            # If an exception was caught and the connection failed, we catch it here.
            # They may not have raised yet, and it will be checked again further down.
            if client._exception:
                raise client._exception
        # Everything caught gets raised as an OpenBBError, we catch those.
        except OpenBBError as e:
            if client.is_running:
                client.disconnect()
            raise e from e
        # Check if the process is still running before returning.
        if client.is_running:
            return client

        raise OpenBBError("Failed to connect to the WebSocket.")

    @staticmethod
    def transform_data(
        data: WebSocketClient,
        query: FmpWebSocketQueryParams,
        **kwargs: Any,
    ) -> FmpWebSocketConnection:
        """Return the client as an instance of Data."""
        # All we need to do here is return our client wrapped in the WebSocketConnection class.
        return FmpWebSocketConnection(client=data)
```

#### Map To Router

Map the new fetcher in the provider's `__init__.py` file by adding it to the `fetcher_dict`.

```python
"WebSocketConnection": FmpWebSocketFetcher
```

Assuming the communication with `websocket_client` is all in order, it will be ready-to-go as a `provider` to the `create_connection` endpoint.

### websocket_client

This is the file where all the action happens. It receives subscribe/unsubscribe events, writes records to the `results_file`, and returns info and error messages to the main application thread.

Some components are importable, but variances between providers require some localized solutions. They will be similar, but not 100% repeatable.

#### Imports:

```python
import asyncio
import json
import os
import signal
import sys

import websockets
import websockets.exceptions
from openbb_fmp.models.websocket_connection import FmpWebSocketData # Import the data model that was created in the 'websocket_connection' file.
from openbb_websockets.helpers import (
    MessageQueue,
    get_logger,
    handle_termination_signal,
    handle_validation_error,
    parse_kwargs,
    write_to_db,
)
from pydantic import ValidationError
```

#### `parse_kwargs`

This function converts the keyword arguments passed at the time of launch. It should be run at the top of the file, with the global constants.

```python
kwargs = parse_kwargs()
```

The dictionary will have all the parameters needed to establish the connection, and the instructions for where to record the results.


#### `get_logger`

This function creates a logger instance with a unique name, configured to the INFO level, with a new line break between messages.
The logger is used to communicate information and errors back to the main application.

> Only pass non-data messages and errors to the logger.

Create the logger after the import section.

```python
logger = get_logger("openbb.websocket.fmp") # A UUID gets attached to the name so multiple instances of the script do not initialize the same logger.
```

#### `MessageQueue`

This is an async Queue with an input for the message handler. Create a second instance if a separate queue is required for the subscibe events.

Define your async message handler function, and create a task to run in the main event loop.

```python

# At the top with the `logger`
queue = MessageQueue()


# This goes right before the `websockets.connect` code.
handler_task = asyncio.create_task(
    queue.process_queue(
        lambda message: process_message(message, results_path, table_name, limit)
    )
)
```

The queue can also be dequeued manually.

```python
message = await queue.dequeue()
```

#### `handle_validation_error`

Before submitting the record to `write_to_db`, validate and transform the data with the WebSocketData that was created and imported. Use this function right before transmission, a failure will trigger a termination signal from the main application.

```python
# code above confirms that the message being processed is a data message and not an info message or error.

  try:
      result = FmpWebSocketData.model_validate(message).model_dump_json(
          exclude_none=True, exclude_unset=True
      )
  except ValidationError as e:
      try:
          handle_validation_error(logger, e)
      except ValidationError:
          raise e from e
  if result:
      await write_to_db(result, results_path, table_name, limit)

```


#### `write_to_db`

This function is responsible for recording the data message to the `results_file`, and will be used in the message handler.

The inputs are all positional arguments, and aside from `message`, are in the `kwargs` dictionary and were supplied during the initialization of `WebSocketClient` in the provider's Fetcher.


```python
results_path = os.path.abspath(kwargs.get("results_file"))
table_name = kwargs.get("table_name")
limit = kwargs.get("limit")

await write_to_db(message, results_path, table_name, limit)
```

#### `handle_termination_signal`

Simple function, that triggers `sys.exit(0)` with a message, for use in `loop.add_signal_handler`.

```python
if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, handle_termination_signal, logger)

      # asyncio.run_coroutine_threadsafe(some_connect_and_stream_function, loop)
      # loop.run_forever()
...
```

#### To-Build

The missing pieces that get created locally include:

- Read `stdin` function for receiving subscribe/unsubscribe events while the connection is running.
  - Messages to handle will always have the same format: `'{"event": "subscribe", "symbol": ticker}'`
  - Converting for the symbology used by the provider needs to happen here.
  - Implementation depends on the requirements of the provider - i.e, how to structure send events.
  - Create the task before the initial `websockets.connect` block.

- Initial login event, the `api_key` will be included in the `kwargs` dictionary, if required.
  - This event might need to happen before a subscribe event, handle any custom messages before entering the `while True` block.
  - `UnauthorizedError` is raised by sending a `logger.error()` that begins with "UnauthorizedError -> %s".

- Message Handler
  - This is the handler task that reads the message queue and determines where to send the message, database or logger.
  - If the message is a row of data, send it to `write_to_db`. Else, send it back to the main application via:
    - `logger.info("PROVIDER INFO:      %s", message.get('message'))`
  - Raise the message as an unexpected error:
    - `logger.error("Unexpected error -> %s", message.get('message'))`

