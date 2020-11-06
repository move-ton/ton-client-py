# TON Client
TON SDK Client library Python bindings.
Works for Python 3.6+ 

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ton-client-py?label=Python)
![PyPI](https://img.shields.io/pypi/v/ton-client-py?label=PyPI)
![PyPI - Downloads](https://img.shields.io/pypi/dm/ton-client-py?label=PyPI%20Downloads)
![TonClient Ubuntu 20.04](https://github.com/move-ton/ton-client-py/workflows/TonClient%20Ubuntu%2020.04/badge.svg) 
![TonClient MacOS Latest](https://github.com/move-ton/ton-client-py/workflows/TonClient%20MacOS%20Latest/badge.svg)

## Installation
1. Create python virtual environment using `pipenv` or `virtualenv`
2. Activate created environment
3. Run `pip install ton-client-py`

## Tests
1. Create python virtual environment using `pipenv` or `virtualenv` and activate it
2. Clone git repository and enter it
3. Run `python -m unittest`

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
```
{
    'network': {
        'server_address': 'http://localhost',
        'message_retries_count': 5,
        'message_processing_timeout': 40000,
        'wait_for_timeout': 40000,
        'out_of_sync_threshold': 15000,
        'access_key': ''
    },
    'crypto': {
        'fish_param': ''
    },
    'abi': {
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

### Net module and GraphQL queries
To create GraphQL query for net module methods use builtin factory.  
`collection` and `result` are required for all queries, other filters are optional.
```python
from tonclient.net import TonQLQuery

# Create query collection
query = TonQLQuery(collection='messages')

# Set filter
# `set_filter` methods accepts any number of kwargs for filtering data.
# kwarg name contains field name and condition separated by __.
# E.g. field__gt=111 is equal to GraphQL {'field': {'gt': 111}}
query = query.set_filter(field__gt=111, field__eq='0:')

# Set result
query = query.set_result('id boc')
# or you can set result fields as separate args
query = query.set_result('id', 'boc')
# or you can combine all of this
query = query.set_result('id boc', 'field')

# Set order (you can pass arguments in the same way as for `set_result`)
query = query.set_order('created_at')  # ASC sorting
query = query.set_order('-created_at')  # DESC sorting

# Set limit
query = query.set_limit(5)
```

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
