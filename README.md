# TON Client
TON SDK Client library Python bindings.
Works for Python 3.6+ 
 
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ton-client-py?label=Python)
![PyPI](https://img.shields.io/pypi/v/ton-client-py?label=PyPI)
![PyPI - Downloads](https://img.shields.io/pypi/dm/ton-client-py?label=PyPI%20Downloads)  
![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/move-ton/ton-client-py/TonClient%20Tests/master?label=Test%20MacOS%7CUbuntu%7CWindows%20-%20Python%203.6%7C3.9)  
[![Chat on Telegram RU](https://img.shields.io/badge/Chat%20on-Telegram%20RU-blue)](https://t.me/MOVETON_SDK_RU)
[![Chat on Telegram EN](https://img.shields.io/badge/Chat%20on-Telegram%20EN-blue)](https://t.me/MOVETON_SDK_EN)

## Installation
Check if Python 3.6+ is installed
##### MacOS/Linux
```
# Using pipenv
pipenv install ton-client-py

# Using pip  
pip install ton-client-py
```
##### Windows
```
# Using pipenv
py -m pipenv install ton-client-py

# Using pip  
py -m pip install ton-client-py
```

## Tests
* Clone repository
```
# Clone repository 
git clone https://github.com/move-ton/ton-client-py.git

# Go to repo directory
cd ton-client-py
```

* Install dev dependencies
##### MacOS/Linux
```
# Using pipenv
pipenv install --dev

# Using pip
pip install pytest
```
##### Windows
```
# Using pipenv
py -m pipenv install --dev

# Using pip
py -m pip install pytest
```

* Running tests
##### MacOS/Linux
```
# Using pipenv
pipenv run pytest  # Display only module name while testing
pipenv run pytest -v  # Display module and method while testing
pipenv run pytest -v -s --log-cli-level=INFO  # Display methods logging while testing

# Without pipenv
python -m pytest
python -m pytest -v
python -m pytest -v -s --log-cli-level=INFO
```
##### Windows
```
# Using pipenv
py -m pipenv run pytest  # Display only module name while testing
py -m pipenv run pytest -v  # Display module and method while testing
py -m pipenv run pytest -v -s --log-cli-level=INFO  # Display methods logging while testing

# Without pipenv
py -m pytest
py -m pytest -v
py -m pytest -v -s --log-cli-level=INFO
```

* Alternative running tests  
If you have problems with installing `pytest` package you can simply run  
```
# For MacOS/Linux
python -m unittest -v

# For Windows
py -m unittest -v
```

## Client
Core client library has sync and async request modes.  
Some core methods are available only in async request mode and 
this mode is more prefferable, so python client is created with async core requests by default.

Create client
```python
from tonclient.types import ClientConfig
from tonclient.client import TonClient

client = TonClient(config=ClientConfig())

# If you need sync core requests for some reason
client_sync_core = TonClient(config=ClientConfig(), is_core_async=False)
```

Client is created with default config
```python
from tonclient.types import NetworkConfig, CryptoConfig, AbiConfig, BocConfig, ClientConfig


# Default network config is below.
# `None` attributes are filled by core with defaults values:
#     `server_address=''`
#     `endpoints=[]`
#     `network_retries_count=5` (DEPRECATED)
#     `message_retries_count=5`
#     `max_reconnect_timeout=120000`
#     `message_processing_timeout=40000`
#     `wait_for_timeout=40000`
#     `out_of_sync_threshold=15000`
#     `sending_endpoint_count=2`
#     `reconnect_timeout=` (DEPRECATED)
#     `access_key=''`
#     `latency_detection_interval=60000`
#     `max_latency=60000`
network = NetworkConfig(
    server_address='http://localhost', endpoints=None, network_retries_count=None, 
    message_retries_count=None, message_processing_timeout=None, reconnect_timeout=None,
    wait_for_timeout=None, out_of_sync_threshold=None, sending_endpoint_count=None, 
    access_key=None, max_reconnect_timeout=None, latency_detection_interval=None,
    max_latency=None)

# Default crypto config is below.
# `None` attributes are filled by core with defaults values: 
#     `mnemonic_dictionary=1` 
#     `mnemonic_word_count=12`
#     `hdkey_derivation_path="m/44'/396'/0'/0/0"`
crypto = CryptoConfig(
    mnemonic_dictionary=None, mnemonic_word_count=None, hdkey_derivation_path=None)

# Default abi config is below.
# `None` attributes are filled by core with defaults values: 
#     `workchain=0` 
#     `message_expiration_timeout=40000`
#     `message_expiration_timeout_grow_factor=1.5`
abi = AbiConfig(
    workchain=None, message_expiration_timeout=None, 
    message_expiration_timeout_grow_factor=None)

# Default boc config is below.
# `None` attributes are filled by core with defaults values: 
#     `cache_max_size=10000` (10MB)
boc = BocConfig(cache_max_size=None)

# Then `ClientConfig` is created
config = ClientConfig(network=network, crypto=crypto, abi=abi, boc=boc)
```

You can override initial config while creating a client
```python
from tonclient.types import ClientConfig
from tonclient.client import TonClient, DEVNET_BASE_URL

config = ClientConfig()
config.network.server_address = DEVNET_BASE_URL
config.abi.message_expiration_timeout = 30000

client = TonClient(config=config)
version = client.version()
```

Client contains all core modules and its methods.  
You can get full list of modules and methods here: 
https://github.com/tonlabs/TON-SDK/blob/master/docs/modules.md  
Module method is called by template `client.[module].[method]`
```python
from tonclient.types import ClientConfig, ParamsOfParse
from tonclient.client import TonClient, DEVNET_BASE_URL

config = ClientConfig()
config.network.server_address = DEVNET_BASE_URL
client = TonClient(config=config)

# Generate random signing keys
keypair = client.crypto.generate_random_sign_keys()

# Parse account
parse_params = ParamsOfParse(boc='Account base64 BOC')
result = client.boc.parse_account(params=parse_params)
```
You always can get information about method and its arguments in method docstring.

### Methods with callbacks
Some library methods accept `callback` argument to pass additional data to it.  
E.g. `net.subscribe_collection`  
```python
import time
from datetime import datetime

from tonclient.errors import TonException
from tonclient.types import ClientConfig, ClientError, SubscriptionResponseType, \
    ParamsOfSubscribeCollection, ResultOfSubscription
from tonclient.client import DEVNET_BASE_URL, TonClient


config = ClientConfig()
config.network.server_address = DEVNET_BASE_URL
client = TonClient(config=config)


def __callback(response_data, response_type, loop):
    """
    `loop` in args is just for example.
    It will have value only with `asyncio` and may be replaced by `_` or `*args` 
    in synchronous requests
    """
    if response_type == SubscriptionResponseType.OK:
        result = ResultOfSubscription(**response_data)
        results.append(result.result)
    if response_type == SubscriptionResponseType.ERROR:
        raise TonException(error=ClientError(**response_data))

results = []
now = int(datetime.now().timestamp())
q_params = ParamsOfSubscribeCollection(collection='messages', result='created_at', filter={'created_at': {'gt': now}})
subscription = client.net.subscribe_collection(params=q_params, callback=__callback)

while True:
    if len(results) > 0 or int(datetime.now().timestamp()) > now + 10:
        client.net.unsubscribe(params=subscription)
        break
    time.sleep(1)
```
Please, dig in `tonclient/test/test_net.py`, `tonclient/test/test_processing.py`, 
`tonclient/test/test_crypto.py`, `tonclient/test/test_debot.py` to get more examples.

## Client and asyncio
```python
from tonclient.types import ClientConfig
from tonclient.client import TonClient, DEVNET_BASE_URL

# Create client with `is_async=True` argument.
config = ClientConfig()
config.network.server_address = DEVNET_BASE_URL
client = TonClient(config=config, is_async=True)

# Get version (simple method with result)
version = await client.version()
```
Please, dig in `tonclient/test/test_async.py` to get more info
