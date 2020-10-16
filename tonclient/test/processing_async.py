import base64
import os
import unittest

from tonclient.client import TonClient, DEVNET_BASE_URL
from tonclient.test.abi import SAMPLES_DIR
from tonclient.types import Abi, DeploySet, CallSet, Signer, KeyPair, \
    MessageSource

client = TonClient(network={'server_address': DEVNET_BASE_URL}, is_async=True)


class TestTonProcessingAsync(unittest.TestCase):
    # TODO: Implement after method fix
    def test_send_message(self):
        events_abi = Abi.from_json_path(
            path=os.path.join(SAMPLES_DIR, 'Events.abi.json'))
        with open(os.path.join(SAMPLES_DIR, 'Events.tvc'), 'rb') as fp:
            events_tvc = base64.b64encode(fp.read()).decode()
        keypair = KeyPair.load(
            path=os.path.join(SAMPLES_DIR, 'keys_raw.json'), is_binary=False)

        signer = Signer.from_keypair(keypair=keypair)
        deploy_set = DeploySet(tvc=events_tvc)
        call_set = CallSet(
            function_name='constructor', header={'pubkey': keypair.public})
        # encoded = client.abi.encode_message(
        #     abi=events_abi, signer=signer, deploy_set=deploy_set,
        #     call_set=call_set)
        message = 'te6ccgECGAEAA6wAA0eIAbVKIRHSKNcmDZ3dT/ajTXTI0SX0W3bNJr2kXvHj509wEbAHAgEA4ZV4ErmUJsLXMnI4kugd5Lm0XLoSPRZt7Gi3vSTfChm/Kji1iLBeWr63NDQ1KOE/A7rTkYust6NeQaioqZVfigRwHj7/2pNrtirjXjSNxqZd4xKOgWP1OQHngk+Whm0RyIAAAF1LXZwRV+IkSpotV8/gAQHAAwIDzyAGBAEB3gUAA9AgAEHeA8ff+1JtdsVca8aRuNTLvGJR0Cx+pyA88Eny0M2iORQCJv8A9KQgIsABkvSg4YrtU1gw9KEKCAEK9KQg9KEJAAACASANCwHI/38h7UTQINdJwgGOENP/0z/TANF/+GH4Zvhj+GKOGPQFcAGAQPQO8r3XC//4YnD4Y3D4Zn/4YeLTAAGOHYECANcYIPkBAdMAAZTT/wMBkwL4QuIg+GX5EPKoldMAAfJ64tM/AQwAao4e+EMhuSCfMCD4I4ED6KiCCBt3QKC53pL4Y+CANPI02NMfAfgjvPK50x8B8AH4R26S8jzeAgEgEw4CASAQDwC9uotV8/+EFujjXtRNAg10nCAY4Q0//TP9MA0X/4Yfhm+GP4Yo4Y9AVwAYBA9A7yvdcL//hicPhjcPhmf/hh4t74RvJzcfhm0fgA+ELIy//4Q88LP/hGzwsAye1Uf/hngCASASEQDluIAGtb8ILdHCfaiaGn/6Z/pgGi//DD8M3wx/DFvfSDK6mjofSBv6PwikDdJGDhvfCFdeXAyfABkZP2CEGRnwoRnRoIEB9AAAAAAAAAAAAAAAAAAIGeLZMCAQH2AGHwhZGX//CHnhZ/8I2eFgGT2qj/8M8ADFuZPCot8ILdHCfaiaGn/6Z/pgGi//DD8M3wx/DFva4b/yupo6Gn/7+j8AGRF7gAAAAAAAAAAAAAAAAhni2fA58jjyxi9EOeF/+S4/YAYfCFkZf/8IeeFn/wjZ4WAZPaqP/wzwAgFIFxQBCbi3xYJQFQH8+EFujhPtRNDT/9M/0wDRf/hh+Gb4Y/hi3tcN/5XU0dDT/9/R+ADIi9wAAAAAAAAAAAAAAAAQzxbPgc+Rx5YxeiHPC//JcfsAyIvcAAAAAAAAAAAAAAAAEM8Wz4HPklb4sEohzwv/yXH7ADD4QsjL//hDzws/+EbPCwDJ7VR/FgAE+GcActxwItDWAjHSADDcIccAkvI74CHXDR+S8jzhUxGS8jvhwQQighD////9vLGS8jzgAfAB+EdukvI83g=='

        generator = client.processing.send_message(
            message=message, send_events=True, abi=events_abi)
        for item in generator:
            print(item)

    # TODO: Implement after method fix
    def test_process_message(self):
        events_abi = Abi.from_json_path(
            path=os.path.join(SAMPLES_DIR, 'Events.abi.json'))
        message = 'te6ccgECGAEAA6wAA0eIAbVKIRHSKNcmDZ3dT/ajTXTI0SX0W3bNJr2kXvHj509wEbAHAgEA4ZV4ErmUJsLXMnI4kugd5Lm0XLoSPRZt7Gi3vSTfChm/Kji1iLBeWr63NDQ1KOE/A7rTkYust6NeQaioqZVfigRwHj7/2pNrtirjXjSNxqZd4xKOgWP1OQHngk+Whm0RyIAAAF1LXZwRV+IkSpotV8/gAQHAAwIDzyAGBAEB3gUAA9AgAEHeA8ff+1JtdsVca8aRuNTLvGJR0Cx+pyA88Eny0M2iORQCJv8A9KQgIsABkvSg4YrtU1gw9KEKCAEK9KQg9KEJAAACASANCwHI/38h7UTQINdJwgGOENP/0z/TANF/+GH4Zvhj+GKOGPQFcAGAQPQO8r3XC//4YnD4Y3D4Zn/4YeLTAAGOHYECANcYIPkBAdMAAZTT/wMBkwL4QuIg+GX5EPKoldMAAfJ64tM/AQwAao4e+EMhuSCfMCD4I4ED6KiCCBt3QKC53pL4Y+CANPI02NMfAfgjvPK50x8B8AH4R26S8jzeAgEgEw4CASAQDwC9uotV8/+EFujjXtRNAg10nCAY4Q0//TP9MA0X/4Yfhm+GP4Yo4Y9AVwAYBA9A7yvdcL//hicPhjcPhmf/hh4t74RvJzcfhm0fgA+ELIy//4Q88LP/hGzwsAye1Uf/hngCASASEQDluIAGtb8ILdHCfaiaGn/6Z/pgGi//DD8M3wx/DFvfSDK6mjofSBv6PwikDdJGDhvfCFdeXAyfABkZP2CEGRnwoRnRoIEB9AAAAAAAAAAAAAAAAAAIGeLZMCAQH2AGHwhZGX//CHnhZ/8I2eFgGT2qj/8M8ADFuZPCot8ILdHCfaiaGn/6Z/pgGi//DD8M3wx/DFva4b/yupo6Gn/7+j8AGRF7gAAAAAAAAAAAAAAAAhni2fA58jjyxi9EOeF/+S4/YAYfCFkZf/8IeeFn/wjZ4WAZPaqP/wzwAgFIFxQBCbi3xYJQFQH8+EFujhPtRNDT/9M/0wDRf/hh+Gb4Y/hi3tcN/5XU0dDT/9/R+ADIi9wAAAAAAAAAAAAAAAAQzxbPgc+Rx5YxeiHPC//JcfsAyIvcAAAAAAAAAAAAAAAAEM8Wz4HPklb4sEohzwv/yXH7ADD4QsjL//hDzws/+EbPCwDJ7VR/FgAE+GcActxwItDWAjHSADDcIccAkvI74CHXDR+S8jzhUxGS8jvhwQQighD////9vLGS8jzgAfAB+EdukvI83g=='
        message_source = MessageSource.from_encoded(
            message=message, abi=events_abi)

        generator = client.processing.process_message(
            message=message_source, send_events=True)
        for item in generator:
            print(item)

    # TODO: Implement after method fix
    def test_wait_for_transaction(self):
        pass
