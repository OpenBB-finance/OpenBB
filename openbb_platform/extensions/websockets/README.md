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

The Python interface and Fast API endpoints are built with importable components that can be used independently of the application.


### WebSocketClient

#### Import

This is the client used for bidirectional communication with both, the provider connection, and, the broadcast server.

```python
from openbb_websockets.client import WebSocketClient
```



...tbc