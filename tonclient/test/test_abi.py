import base64
import os
import unittest

from tonclient.errors import TonException
from tonclient.test.helpers import SAMPLES_DIR, async_core_client, \
    sync_core_client
from tonclient.types import Abi, KeyPair, DeploySet, CallSet, Signer, \
    MessageSource, StateInitSource, FunctionHeader, ParamsOfEncodeMessageBody, \
    ParamsOfDecodeMessage, MessageBodyType, ParamsOfParse, \
    ParamsOfDecodeMessageBody, ParamsOfEncodeMessage, ParamsOfSign, \
    ParamsOfAttachSignature, ParamsOfEncodeAccount


class TestTonAbiAsyncCore(unittest.TestCase):
    def setUp(self) -> None:
        # Events contract params
        self.events_abi = Abi.from_path(
            path=os.path.join(SAMPLES_DIR, 'Events.abi.json'))
        self.keypair = KeyPair(
            public='4c7c408ff1ddebb8d6405ee979c716a14fdd6cc08124107a61d3c25597099499',
            secret='cc8929d635719612a9478b9cd17675a39cfad52d8959e8a177389b8c0b9122a7')
        with open(os.path.join(SAMPLES_DIR, 'Events.tvc'), 'rb') as fp:
            self.events_tvc = base64.b64encode(fp.read()).decode()
        self.events_time = 1599458364291
        self.events_expire = 1599458404

    def test_decode_message(self):
        message = 'te6ccgEBAwEAvAABRYgAC31qq9KF9Oifst6LU9U6FQSQQRlCSEMo+A3LN5MvphIMAQHhrd/b+MJ5Za+AygBc5qS/dVIPnqxCsM9PvqfVxutK+lnQEKzQoRTLYO6+jfM8TF4841bdNjLQwIDWL4UVFdxIhdMfECP8d3ruNZAXul5xxahT91swIEkEHph08JVlwmUmQAAAXRnJcuDX1XMZBW+LBKACAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=='
        params = ParamsOfDecodeMessage(abi=self.events_abi, message=message)
        decoded = async_core_client.abi.decode_message(params=params)
        self.assertEqual(MessageBodyType.INPUT, decoded.body_type)
        self.assertEqual(0, int(decoded.value['id'], 16))
        self.assertEqual(self.events_expire, decoded.header.expire)
        self.assertEqual(self.events_time, decoded.header.time)
        self.assertEqual(self.keypair.public, decoded.header.pubkey)

        message = 'te6ccgEBAQEAVQAApeACvg5/pmQpY4m61HmJ0ne+zjHJu3MNG8rJxUDLbHKBu/AAAAAAAAAMJL6z6ro48sYvAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABA'
        params = ParamsOfDecodeMessage(abi=self.events_abi, message=message)
        decoded = async_core_client.abi.decode_message(params=params)
        self.assertEqual(MessageBodyType.EVENT, decoded.body_type)
        self.assertEqual(0, int(decoded.value['id'], 16))
        self.assertIsNone(decoded.header)

        message = 'te6ccgEBAQEAVQAApeACvg5/pmQpY4m61HmJ0ne+zjHJu3MNG8rJxUDLbHKBu/AAAAAAAAAMKr6z6rxK3xYJAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABA'
        params = ParamsOfDecodeMessage(abi=self.events_abi, message=message)
        decoded = async_core_client.abi.decode_message(params=params)
        self.assertEqual(MessageBodyType.OUTPUT, decoded.body_type)
        self.assertEqual(0, int(decoded.value['value0'], 16))
        self.assertIsNone(decoded.header)

        with self.assertRaises(TonException):
            params = ParamsOfDecodeMessage(abi=self.events_abi, message='0x0')
            async_core_client.abi.decode_message(params=params)

    def test_decode_message_body(self):
        message = 'te6ccgEBAwEAvAABRYgAC31qq9KF9Oifst6LU9U6FQSQQRlCSEMo+A3LN5MvphIMAQHhrd/b+MJ5Za+AygBc5qS/dVIPnqxCsM9PvqfVxutK+lnQEKzQoRTLYO6+jfM8TF4841bdNjLQwIDWL4UVFdxIhdMfECP8d3ruNZAXul5xxahT91swIEkEHph08JVlwmUmQAAAXRnJcuDX1XMZBW+LBKACAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=='
        boc = async_core_client.boc.parse_message(
            params=ParamsOfParse(boc=message))

        decode_params = ParamsOfDecodeMessageBody(
            abi=self.events_abi, body=boc.parsed['body'], is_internal=False)
        decoded = async_core_client.abi.decode_message_body(
            params=decode_params)
        self.assertEqual(MessageBodyType.INPUT, decoded.body_type)
        self.assertEqual(0, int(decoded.value['id'], 16))
        self.assertEqual(self.events_expire, decoded.header.expire)
        self.assertEqual(self.events_time, decoded.header.time)
        self.assertEqual(self.keypair.public, decoded.header.pubkey)

    def test_encode_message(self):
        deploy_set = DeploySet(tvc=self.events_tvc)
        call_set = CallSet(
            function_name='constructor',
            header=FunctionHeader(
                pubkey=self.keypair.public, time=self.events_time,
                expire=self.events_expire))
        signer = Signer.External(public_key=self.keypair.public)

        # Create unsigned deployment message
        params = ParamsOfEncodeMessage(
            abi=self.events_abi, signer=signer, deploy_set=deploy_set,
            call_set=call_set)
        unsigned = async_core_client.abi.encode_message(params=params)
        self.assertEqual(
            'te6ccgECFwEAA2gAAqeIAAt9aqvShfTon7Lei1PVOhUEkEEZQkhDKPgNyzeTL6YSEZTHxAj/Hd67jWQF7peccWoU/dbMCBJBB6YdPCVZcJlJkAAAF0ZyXLg19VzGRotV8/gGAQEBwAICA88gBQMBAd4EAAPQIABB2mPiBH+O713GsgL3S844tQp+62YECSCD0w6eEqy4TKTMAib/APSkICLAAZL0oOGK7VNYMPShCQcBCvSkIPShCAAAAgEgDAoByP9/Ie1E0CDXScIBjhDT/9M/0wDRf/hh+Gb4Y/hijhj0BXABgED0DvK91wv/+GJw+GNw+GZ/+GHi0wABjh2BAgDXGCD5AQHTAAGU0/8DAZMC+ELiIPhl+RDyqJXTAAHyeuLTPwELAGqOHvhDIbkgnzAg+COBA+iogggbd0Cgud6S+GPggDTyNNjTHwH4I7zyudMfAfAB+EdukvI83gIBIBINAgEgDw4AvbqLVfP/hBbo417UTQINdJwgGOENP/0z/TANF/+GH4Zvhj+GKOGPQFcAGAQPQO8r3XC//4YnD4Y3D4Zn/4YeLe+Ebyc3H4ZtH4APhCyMv/+EPPCz/4Rs8LAMntVH/4Z4AgEgERAA5biABrW/CC3Rwn2omhp/+mf6YBov/ww/DN8Mfwxb30gyupo6H0gb+j8IpA3SRg4b3whXXlwMnwAZGT9ghBkZ8KEZ0aCBAfQAAAAAAAAAAAAAAAAACBni2TAgEB9gBh8IWRl//wh54Wf/CNnhYBk9qo//DPAAxbmTwqLfCC3Rwn2omhp/+mf6YBov/ww/DN8Mfwxb2uG/8rqaOhp/+/o/ABkRe4AAAAAAAAAAAAAAAAIZ4tnwOfI48sYvRDnhf/kuP2AGHwhZGX//CHnhZ/8I2eFgGT2qj/8M8AIBSBYTAQm4t8WCUBQB/PhBbo4T7UTQ0//TP9MA0X/4Yfhm+GP4Yt7XDf+V1NHQ0//f0fgAyIvcAAAAAAAAAAAAAAAAEM8Wz4HPkceWMXohzwv/yXH7AMiL3AAAAAAAAAAAAAAAABDPFs+Bz5JW+LBKIc8L/8lx+wAw+ELIy//4Q88LP/hGzwsAye1UfxUABPhnAHLccCLQ1gIx0gAw3CHHAJLyO+Ah1w0fkvI84VMRkvI74cEEIoIQ/////byxkvI84AHwAfhHbpLyPN4=',
            unsigned.message)
        self.assertEqual(
            'KCGM36iTYuCYynk+Jnemis+mcwi3RFCke95i7l96s4Q=',
            unsigned.data_to_sign)

        # Create detached signature
        sign_params = ParamsOfSign(
            unsigned=unsigned.data_to_sign, keys=self.keypair)
        signature = async_core_client.crypto.sign(params=sign_params)
        self.assertEqual(
            '6272357bccb601db2b821cb0f5f564ab519212d242cf31961fe9a3c50a30b236012618296b4f769355c0e9567cd25b366f3c037435c498c82e5305622adbc70e',
            signature.signature)

        # Attach signature to unsigned message
        attach_params = ParamsOfAttachSignature(
            abi=self.events_abi, public_key=self.keypair.public,
            message=unsigned.message, signature=signature.signature)
        signed = async_core_client.abi.attach_signature(params=attach_params)
        self.assertEqual(
            'te6ccgECGAEAA6wAA0eIAAt9aqvShfTon7Lei1PVOhUEkEEZQkhDKPgNyzeTL6YSEbAHAgEA4bE5Gr3mWwDtlcEOWHr6slWoyQlpIWeYyw/00eKFGFkbAJMMFLWnu0mq4HSrPmktmzeeAboa4kxkFymCsRVt44dTHxAj/Hd67jWQF7peccWoU/dbMCBJBB6YdPCVZcJlJkAAAF0ZyXLg19VzGRotV8/gAQHAAwIDzyAGBAEB3gUAA9AgAEHaY+IEf47vXcayAvdLzji1Cn7rZgQJIIPTDp4SrLhMpMwCJv8A9KQgIsABkvSg4YrtU1gw9KEKCAEK9KQg9KEJAAACASANCwHI/38h7UTQINdJwgGOENP/0z/TANF/+GH4Zvhj+GKOGPQFcAGAQPQO8r3XC//4YnD4Y3D4Zn/4YeLTAAGOHYECANcYIPkBAdMAAZTT/wMBkwL4QuIg+GX5EPKoldMAAfJ64tM/AQwAao4e+EMhuSCfMCD4I4ED6KiCCBt3QKC53pL4Y+CANPI02NMfAfgjvPK50x8B8AH4R26S8jzeAgEgEw4CASAQDwC9uotV8/+EFujjXtRNAg10nCAY4Q0//TP9MA0X/4Yfhm+GP4Yo4Y9AVwAYBA9A7yvdcL//hicPhjcPhmf/hh4t74RvJzcfhm0fgA+ELIy//4Q88LP/hGzwsAye1Uf/hngCASASEQDluIAGtb8ILdHCfaiaGn/6Z/pgGi//DD8M3wx/DFvfSDK6mjofSBv6PwikDdJGDhvfCFdeXAyfABkZP2CEGRnwoRnRoIEB9AAAAAAAAAAAAAAAAAAIGeLZMCAQH2AGHwhZGX//CHnhZ/8I2eFgGT2qj/8M8ADFuZPCot8ILdHCfaiaGn/6Z/pgGi//DD8M3wx/DFva4b/yupo6Gn/7+j8AGRF7gAAAAAAAAAAAAAAAAhni2fA58jjyxi9EOeF/+S4/YAYfCFkZf/8IeeFn/wjZ4WAZPaqP/wzwAgFIFxQBCbi3xYJQFQH8+EFujhPtRNDT/9M/0wDRf/hh+Gb4Y/hi3tcN/5XU0dDT/9/R+ADIi9wAAAAAAAAAAAAAAAAQzxbPgc+Rx5YxeiHPC//JcfsAyIvcAAAAAAAAAAAAAAAAEM8Wz4HPklb4sEohzwv/yXH7ADD4QsjL//hDzws/+EbPCwDJ7VR/FgAE+GcActxwItDWAjHSADDcIccAkvI74CHXDR+S8jzhUxGS8jvhwQQighD////9vLGS8jzgAfAB+EdukvI83g==',
            signed.message)

        # Create initially signed message
        signer = Signer.Keys(keys=self.keypair)
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi, signer=signer, deploy_set=deploy_set,
            call_set=call_set)
        signed = async_core_client.abi.encode_message(params=encode_params)
        self.assertEqual(
            'te6ccgECGAEAA6wAA0eIAAt9aqvShfTon7Lei1PVOhUEkEEZQkhDKPgNyzeTL6YSEbAHAgEA4bE5Gr3mWwDtlcEOWHr6slWoyQlpIWeYyw/00eKFGFkbAJMMFLWnu0mq4HSrPmktmzeeAboa4kxkFymCsRVt44dTHxAj/Hd67jWQF7peccWoU/dbMCBJBB6YdPCVZcJlJkAAAF0ZyXLg19VzGRotV8/gAQHAAwIDzyAGBAEB3gUAA9AgAEHaY+IEf47vXcayAvdLzji1Cn7rZgQJIIPTDp4SrLhMpMwCJv8A9KQgIsABkvSg4YrtU1gw9KEKCAEK9KQg9KEJAAACASANCwHI/38h7UTQINdJwgGOENP/0z/TANF/+GH4Zvhj+GKOGPQFcAGAQPQO8r3XC//4YnD4Y3D4Zn/4YeLTAAGOHYECANcYIPkBAdMAAZTT/wMBkwL4QuIg+GX5EPKoldMAAfJ64tM/AQwAao4e+EMhuSCfMCD4I4ED6KiCCBt3QKC53pL4Y+CANPI02NMfAfgjvPK50x8B8AH4R26S8jzeAgEgEw4CASAQDwC9uotV8/+EFujjXtRNAg10nCAY4Q0//TP9MA0X/4Yfhm+GP4Yo4Y9AVwAYBA9A7yvdcL//hicPhjcPhmf/hh4t74RvJzcfhm0fgA+ELIy//4Q88LP/hGzwsAye1Uf/hngCASASEQDluIAGtb8ILdHCfaiaGn/6Z/pgGi//DD8M3wx/DFvfSDK6mjofSBv6PwikDdJGDhvfCFdeXAyfABkZP2CEGRnwoRnRoIEB9AAAAAAAAAAAAAAAAAAIGeLZMCAQH2AGHwhZGX//CHnhZ/8I2eFgGT2qj/8M8ADFuZPCot8ILdHCfaiaGn/6Z/pgGi//DD8M3wx/DFva4b/yupo6Gn/7+j8AGRF7gAAAAAAAAAAAAAAAAhni2fA58jjyxi9EOeF/+S4/YAYfCFkZf/8IeeFn/wjZ4WAZPaqP/wzwAgFIFxQBCbi3xYJQFQH8+EFujhPtRNDT/9M/0wDRf/hh+Gb4Y/hi3tcN/5XU0dDT/9/R+ADIi9wAAAAAAAAAAAAAAAAQzxbPgc+Rx5YxeiHPC//JcfsAyIvcAAAAAAAAAAAAAAAAEM8Wz4HPklb4sEohzwv/yXH7ADD4QsjL//hDzws/+EbPCwDJ7VR/FgAE+GcActxwItDWAjHSADDcIccAkvI74CHXDR+S8jzhUxGS8jvhwQQighD////9vLGS8jzgAfAB+EdukvI83g==',
            signed.message)

        # Sign with signing box
        sbox = async_core_client.crypto.get_signing_box(params=self.keypair)
        signer_sbox = Signer.SigningBox(handle=sbox.handle)
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi, signer=signer_sbox, deploy_set=deploy_set,
            call_set=call_set)
        signed_sbox = async_core_client.abi.encode_message(
            params=encode_params)
        async_core_client.crypto.remove_signing_box(params=sbox)
        self.assertEqual(signed.message, signed_sbox.message)

        # Create run unsigned message
        address = '0:05beb555e942fa744fd96f45a9ea9d0a8248208ca12421947c06e59bc997d309'
        call_set = CallSet(
            function_name='returnValue', input={'id': '0'},
            header=FunctionHeader(**{
                'pubkey': self.keypair.public,
                'time': self.events_time,
                'expire': self.events_expire
            }))
        signer = Signer.External(public_key=self.keypair.public)
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi, signer=signer, address=address,
            call_set=call_set)
        unsigned = async_core_client.abi.encode_message(params=encode_params)
        self.assertEqual(
            'te6ccgEBAgEAeAABpYgAC31qq9KF9Oifst6LU9U6FQSQQRlCSEMo+A3LN5MvphIFMfECP8d3ruNZAXul5xxahT91swIEkEHph08JVlwmUmQAAAXRnJcuDX1XMZBW+LBKAQBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=',
            unsigned.message)
        self.assertEqual(
            'i4Hs3PB12QA9UBFbOIpkG3JerHHqjm4LgvF4MA7TDsY=',
            unsigned.data_to_sign)

        # Create detached signature
        sign_params = ParamsOfSign(
            unsigned=unsigned.data_to_sign, keys=self.keypair)
        signature = async_core_client.crypto.sign(params=sign_params)
        self.assertEqual(
            '5bbfb7f184f2cb5f019400b9cd497eeaa41f3d5885619e9f7d4fab8dd695f4b3a02159a1422996c1dd7d1be67898bc79c6adba6c65a18101ac5f0a2a2bb8910b',
            signature.signature)

        # Attach signature
        attach_params = ParamsOfAttachSignature(
            abi=self.events_abi, public_key=self.keypair.public,
            message=unsigned.message, signature=signature.signature)
        signed = async_core_client.abi.attach_signature(params=attach_params)
        self.assertEqual(
            'te6ccgEBAwEAvAABRYgAC31qq9KF9Oifst6LU9U6FQSQQRlCSEMo+A3LN5MvphIMAQHhrd/b+MJ5Za+AygBc5qS/dVIPnqxCsM9PvqfVxutK+lnQEKzQoRTLYO6+jfM8TF4841bdNjLQwIDWL4UVFdxIhdMfECP8d3ruNZAXul5xxahT91swIEkEHph08JVlwmUmQAAAXRnJcuDX1XMZBW+LBKACAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==',
            signed.message)

        # Create initially signed message
        signer = Signer.Keys(keys=self.keypair)
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi, signer=signer, address=address,
            call_set=call_set)
        signed = async_core_client.abi.encode_message(params=encode_params)
        self.assertEqual(
            'te6ccgEBAwEAvAABRYgAC31qq9KF9Oifst6LU9U6FQSQQRlCSEMo+A3LN5MvphIMAQHhrd/b+MJ5Za+AygBc5qS/dVIPnqxCsM9PvqfVxutK+lnQEKzQoRTLYO6+jfM8TF4841bdNjLQwIDWL4UVFdxIhdMfECP8d3ruNZAXul5xxahT91swIEkEHph08JVlwmUmQAAAXRnJcuDX1XMZBW+LBKACAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==',
            signed.message)

    def test_encode_message_body(self):
        header = FunctionHeader(
            expire=self.events_expire, time=self.events_time,
            pubkey=self.keypair.public)
        call_set = CallSet(
            function_name='returnValue', header=header, input={'id': '0'})
        signer = Signer.Keys(keys=self.keypair)
        params = ParamsOfEncodeMessageBody(
            abi=self.events_abi, call_set=call_set, is_internal=False,
            signer=signer)
        encoded = async_core_client.abi.encode_message_body(params=params)

        self.assertIsNone(encoded.data_to_sign)

    def test_encode_account(self):
        # Encode account from encoded deploy message
        encoded_deploy_message = 'te6ccgECFwEAA2gAAqeIAAt9aqvShfTon7Lei1PVOhUEkEEZQkhDKPgNyzeTL6YSEZTHxAj/Hd67jWQF7peccWoU/dbMCBJBB6YdPCVZcJlJkAAAF0ZyXLg19VzGRotV8/gGAQEBwAICA88gBQMBAd4EAAPQIABB2mPiBH+O713GsgL3S844tQp+62YECSCD0w6eEqy4TKTMAib/APSkICLAAZL0oOGK7VNYMPShCQcBCvSkIPShCAAAAgEgDAoByP9/Ie1E0CDXScIBjhDT/9M/0wDRf/hh+Gb4Y/hijhj0BXABgED0DvK91wv/+GJw+GNw+GZ/+GHi0wABjh2BAgDXGCD5AQHTAAGU0/8DAZMC+ELiIPhl+RDyqJXTAAHyeuLTPwELAGqOHvhDIbkgnzAg+COBA+iogggbd0Cgud6S+GPggDTyNNjTHwH4I7zyudMfAfAB+EdukvI83gIBIBINAgEgDw4AvbqLVfP/hBbo417UTQINdJwgGOENP/0z/TANF/+GH4Zvhj+GKOGPQFcAGAQPQO8r3XC//4YnD4Y3D4Zn/4YeLe+Ebyc3H4ZtH4APhCyMv/+EPPCz/4Rs8LAMntVH/4Z4AgEgERAA5biABrW/CC3Rwn2omhp/+mf6YBov/ww/DN8Mfwxb30gyupo6H0gb+j8IpA3SRg4b3whXXlwMnwAZGT9ghBkZ8KEZ0aCBAfQAAAAAAAAAAAAAAAAACBni2TAgEB9gBh8IWRl//wh54Wf/CNnhYBk9qo//DPAAxbmTwqLfCC3Rwn2omhp/+mf6YBov/ww/DN8Mfwxb2uG/8rqaOhp/+/o/ABkRe4AAAAAAAAAAAAAAAAIZ4tnwOfI48sYvRDnhf/kuP2AGHwhZGX//CHnhZ/8I2eFgGT2qj/8M8AIBSBYTAQm4t8WCUBQB/PhBbo4T7UTQ0//TP9MA0X/4Yfhm+GP4Yt7XDf+V1NHQ0//f0fgAyIvcAAAAAAAAAAAAAAAAEM8Wz4HPkceWMXohzwv/yXH7AMiL3AAAAAAAAAAAAAAAABDPFs+Bz5JW+LBKIc8L/8lx+wAw+ELIy//4Q88LP/hGzwsAye1UfxUABPhnAHLccCLQ1gIx0gAw3CHHAJLyO+Ah1w0fkvI84VMRkvI74cEEIoIQ/////byxkvI84AHwAfhHbpLyPN4='
        message_source = MessageSource.Encoded(
            message=encoded_deploy_message, abi=self.events_abi)
        state_init_source = StateInitSource.Message(source=message_source)

        encode_params = ParamsOfEncodeAccount(state_init=state_init_source)
        encoded = async_core_client.abi.encode_account(params=encode_params)
        self.assertEqual(
            '05beb555e942fa744fd96f45a9ea9d0a8248208ca12421947c06e59bc997d309',
            encoded.id)

        # Encode account from encoding params
        deploy_set = DeploySet(tvc=self.events_tvc)
        call_set = CallSet(
            function_name='constructor',
            header=FunctionHeader(**{
                'pubkey': self.keypair.public,
                'time': self.events_time,
                'expire': self.events_expire
            }))
        signer = Signer.Keys(keys=self.keypair)
        encoding_params = ParamsOfEncodeMessage(
            abi=self.events_abi, signer=signer, deploy_set=deploy_set,
            call_set=call_set)
        message_source = MessageSource.EncodingParams(params=encoding_params)
        state_init_source = StateInitSource.Message(source=message_source)
        encode_params = ParamsOfEncodeAccount(state_init=state_init_source)
        encoded = async_core_client.abi.encode_account(params=encode_params)
        self.assertEqual(
            '05beb555e942fa744fd96f45a9ea9d0a8248208ca12421947c06e59bc997d309',
            encoded.id)

        # Test exception (external signer)
        with self.assertRaises(TonException):
            signer = Signer.External(public_key=self.keypair.public)
            encoding_params = ParamsOfEncodeMessage(
                abi=self.events_abi, signer=signer, deploy_set=deploy_set,
                call_set=call_set)
            message_source = MessageSource.EncodingParams(
                params=encoding_params)
            state_init_source = StateInitSource.Message(source=message_source)
            encode_params = ParamsOfEncodeAccount(state_init=state_init_source)
            async_core_client.abi.encode_account(params=encode_params)

        # Encode account from TVC
        state_init_source = StateInitSource.Tvc(tvc=self.events_tvc)
        encode_params = ParamsOfEncodeAccount(state_init=state_init_source)
        encoded = async_core_client.abi.encode_account(params=encode_params)
        self.assertNotEqual(
            '05beb555e942fa744fd96f45a9ea9d0a8248208ca12421947c06e59bc997d309',
            encoded.id)

        state_init_source = StateInitSource.Tvc(
            tvc=self.events_tvc, public_key=self.keypair.public)
        encode_params = ParamsOfEncodeAccount(state_init=state_init_source)
        encoded = async_core_client.abi.encode_account(params=encode_params)
        self.assertEqual(
            '05beb555e942fa744fd96f45a9ea9d0a8248208ca12421947c06e59bc997d309',
            encoded.id)


class TestTonAbiSyncCore(unittest.TestCase):
    """ Sync core is not recommended to use, so make just a couple of tests """
    def setUp(self) -> None:
        # Events contract params
        self.events_abi = Abi.from_path(
            path=os.path.join(SAMPLES_DIR, 'Events.abi.json'))
        self.keypair = KeyPair(
            public='4c7c408ff1ddebb8d6405ee979c716a14fdd6cc08124107a61d3c25597099499',
            secret='cc8929d635719612a9478b9cd17675a39cfad52d8959e8a177389b8c0b9122a7')
        with open(os.path.join(SAMPLES_DIR, 'Events.tvc'), 'rb') as fp:
            self.events_tvc = base64.b64encode(fp.read()).decode()
        self.events_time = 1599458364291
        self.events_expire = 1599458404

    def test_decode_message(self):
        message = 'te6ccgEBAwEAvAABRYgAC31qq9KF9Oifst6LU9U6FQSQQRlCSEMo+A3LN5MvphIMAQHhrd/b+MJ5Za+AygBc5qS/dVIPnqxCsM9PvqfVxutK+lnQEKzQoRTLYO6+jfM8TF4841bdNjLQwIDWL4UVFdxIhdMfECP8d3ruNZAXul5xxahT91swIEkEHph08JVlwmUmQAAAXRnJcuDX1XMZBW+LBKACAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=='
        params = ParamsOfDecodeMessage(abi=self.events_abi, message=message)
        decoded = sync_core_client.abi.decode_message(params=params)
        self.assertEqual('Input', decoded.body_type)
        self.assertEqual(0, int(decoded.value['id'], 16))
        self.assertEqual(self.events_expire, decoded.header.expire)
        self.assertEqual(self.events_time, decoded.header.time)
        self.assertEqual(self.keypair.public, decoded.header.pubkey)

        message = 'te6ccgEBAQEAVQAApeACvg5/pmQpY4m61HmJ0ne+zjHJu3MNG8rJxUDLbHKBu/AAAAAAAAAMJL6z6ro48sYvAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABA'
        params = ParamsOfDecodeMessage(abi=self.events_abi, message=message)
        decoded = sync_core_client.abi.decode_message(params=params)
        self.assertEqual('Event', decoded.body_type)
        self.assertEqual(0, int(decoded.value['id'], 16))
        self.assertIsNone(decoded.header)

        message = 'te6ccgEBAQEAVQAApeACvg5/pmQpY4m61HmJ0ne+zjHJu3MNG8rJxUDLbHKBu/AAAAAAAAAMKr6z6rxK3xYJAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABA'
        params = ParamsOfDecodeMessage(abi=self.events_abi, message=message)
        decoded = sync_core_client.abi.decode_message(params=params)
        self.assertEqual('Output', decoded.body_type)
        self.assertEqual(0, int(decoded.value['value0'], 16))
        self.assertIsNone(decoded.header)

        with self.assertRaises(TonException):
            params = ParamsOfDecodeMessage(abi=self.events_abi, message='0x0')
            sync_core_client.abi.decode_message(params=params)
