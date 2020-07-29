import logging

from lib import TonClient, TON_CLIENT_DEFAULT_SETUP
import time
import asyncio

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

ton = TonClient()

giver_abi = {
    'ABI version': 1,
    'functions': [
        {
            'name': 'constructor',
            'inputs': [],
            'outputs': []
        }, 
        {
            'name': 'sendGrams',
            'inputs': [
                {'name': 'dest', 'type': 'address'},
                {'name': 'amount', 'type': 'uint64'}
            ],
            'outputs': []
        }
    ],
    'events': [],
    'data': []
}
print(ton.version())



mnemo = (ton._request('crypto.mnemonic.from.random', {}))
mnemo = "machine logic master small before pole ramp ankle stage trash pepper success oxygen unhappy engine muscle party oblige situate cement fame keep inform lemon"

keys = ton._request("crypto.ed25519.keypair",{})
print(keys)

keys = ton._request('crypto.mnemonic.derive.sign.keys',dict(phrase=mnemo))
print(keys["result"]["public"])
address = ton._request('crypto.ton_public_key_string',"4da8a4af5a794e6c70671ad9de4ec7a3d3a8ea04d9b6610db23df2519f31bfde")
print(address)
print(ton._request('version', {}))
print(ton._request('setup', TON_CLIENT_DEFAULT_SETUP))

print(ton._request('queries.query', {
    'table': 'accounts',
    'filter': '{}',
    'result': 'balance(format:DEC)'
}))

run_contract_params = {
    'address': '0:653b9a6452c7a982c6dc92b2da9eba832ade1c467699ebb3b43dca6d77b780dd',
    'abi': giver_abi,
    'functionName': 'sendGrams',
    'input': {
        'dest': '0:7521327f18e2696a4a97d556361d0e5025472a00d9c4d3573508f508f2bff152',
        'amount': 100
    }
}
print(ton._request('contracts.run', run_contract_params))