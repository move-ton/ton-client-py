# TON Client
TON SDK Client library Python bindings.
Works for Python 3.6+ 

![TonClient Ubuntu 20.04](https://github.com/move-ton/ton-client-py/workflows/TonClient%20Ubuntu%2020.04/badge.svg) 
![TonClient MacOS Latest](https://github.com/move-ton/ton-client-py/workflows/TonClient%20MacOS%20Latest/badge.svg)  
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ton-client-py?label=Python)
![PyPI](https://img.shields.io/pypi/v/ton-client-py?label=PyPI)
![PyPI - Downloads](https://img.shields.io/pypi/dm/ton-client-py?label=PyPI%20Downloads)  
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
Core client library has sync and async request modes. Some core methods are available only in async request mode and 
this mode is more prefferable, so python client is created with async core requests by default.

Create client
```python
from tonclient.client import TonClient

client = TonClient()

# If you need sync core requests for some reason
client_sync_core = TonClient(is_core_async=False)
```

Client is created with default config
```python
CLIENT_DEFAULT_SETUP = {
    'network': {
        'server_address': 'http://localhost',
        'network_retries_count': 5,
        'message_retries_count': 5,
        'message_processing_timeout': 40000,
        'wait_for_timeout': 40000,
        'out_of_sync_threshold': 15000,
        'access_key': ''
    },
    'crypto': {
        'mnemonic_dictionary': 1,
        'mnemonic_word_count': 12,
        'hdkey_derivation_path': "m/44'/396'/0'/0/0"
    },
    'abi': {
        'workchain': 0,
        'message_expiration_timeout': 40000,
        'message_expiration_timeout_grow_factor': 1.5
    }
}
```

You can override initial config while creating a client
```python
from tonclient.client import TonClient, DEVNET_BASE_URL

client = TonClient(network={'server_address': DEVNET_BASE_URL}, abi={'message_expiration_timeout': 30000})
version = client.version()
```

Client contains all core modules and its' methods. You can get full list of modules and methods here: 
https://github.com/tonlabs/TON-SDK/blob/master/docs/modules.md  
Module method is called by template `client.[module].[method]`
```python
from tonclient.client import TonClient, DEVNET_BASE_URL

client = TonClient(network={'server_address': DEVNET_BASE_URL})

# Generate random signing keys
keypair = client.crypto.generate_random_sign_keys()
# Parse account
parsed = client.boc.parse_account(boc='Account base64 BOC')
```
You always can get information about method and its' arguments in method docstring.

### Methods with events
Some library methods `net.subscribe_collection`, `proccessing.send_message`, `processing.wait_for_transaction`, 
`processing.process_message` may return either result or generator.  

- `net.subscribe_collection` always returns a generator  
- `proccessing.send_message`, `processing.wait_for_transaction`, 
`processing.process_message` return generator only if `send_events` argument is set to `True`

Please, dig in `tonclient/test/test_net.py`, `tonclient/test/test_processing.py` to get example how to work with 
generators.

## Client and asyncio
```python
from tonclient.client import TonClient, DEVNET_BASE_URL

# Create client with `is_async=True` argument.
client = TonClient(network={'server_address': DEVNET_BASE_URL}, is_async=True)

# Get version (simple method with result)
version = await client.version()

# Generators
generator = client.net.subscribe_collection(query=TonQLQuery)
async for event in generator:
    # Work with event
    pass
```

Please, dig in `tonclient/test/test_async.py` to get more info.
