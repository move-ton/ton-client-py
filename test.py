from lib import TonClient
import time
import asyncio
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ton = TonClient(BASE_DIR)

ton._request(ton._create_context(),'crypto.mnemonic.from.random')


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


ioloop = asyncio.get_event_loop()
ioloop.run_until_complete(test())
ioloop.close()