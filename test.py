from lib import TonClient
import time
import asyncio
import os
import json
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ton = TonClient(BASE_DIR)

class TonJsonSettings:
    # Hint
    base_url = "net.ton.dev"#Url node
    message_retries_count = 5 
    message_expiration_timeout = 10000
    message_expiration_timeout_grow_factor = 1.5
    message_processing_timeout = 40000
    message_processing_timeout_grow_factor = 1.5
    wait_for_timeout = 40000
    access_key = ""
    def __init__(self,**kwargs):
        pass
        #self.__dict__.update(kwargs)

giver_abi = '{"ABI version":1,"functions":[{"name":"constructor","inputs":[],"outputs":[]},{"name": "sendGrams","inputs": [{"name":"dest","type":"address"},{"name":"amount","type":"uint64"}],"outputs":[]}],"events":[],"data":[]}'
print(giver_abi )

ton._request(ton._create_context(),'crypto.mnemonic.from.random')
print(ton._request(ton._create_context(),'version').result_json)
te = ton._create_context()
a = ton._request(te,"setup",TonJsonSettings().__dict__)
print(a.result_json)
print(ton._request(te,'queries.query',dict(table="accounts",filter='{}',result="id")).result_json)
print(ton._request(te,"contracts.run",dict(address="0:4dbb3fc26c775e88c040d76cc14b8e996b5b2e1fa2a632cd839784edd5845298",abi=(giver_abi),functionName="sendGrams",input=json.dumps(dict(dest="0:7521327f18e2696a4a97d556361d0e5025472a00d9c4d3573508f508f2bff152",amount=100)))).result_json)

async def test():
    start = time.time()
    futures = [ton._request_async(ton._create_context(),i,'crypto.mnemonic.from.random') for i in range(1, 5)]
    for i, future in enumerate(asyncio.as_completed(futures)):
        result = await future
        print('{} {}'.format(">>" * (i + 1), result))

    print("Process took: {:.2f} seconds".format(time.time() - start))
    # print(await ton._request_async(ton._create_context(),1,'crypto.mnemonic.from.random'))
    # print(await ton._request_async(ton._create_context(),2,'crypto.mnemonic.from.random'))
    # print(await ton._request_async(ton._create_context(),3,'crypto.mnemonic.from.random'))



# ioloop = asyncio.get_event_loop()
# ioloop.run_until_complete(test())
# ioloop.close()