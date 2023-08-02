import base64
import os
import unittest

from tonclient.errors import TonException
from tonclient.test.helpers import SAMPLES_DIR, async_core_client, sync_core_client
from tonclient.types import (
    Abi,
    DataLayout,
    KeyPair,
    DeploySet,
    CallSet,
    ParamsOfCalcFunctionId,
    ParamsOfGetSignatureData,
    Signer,
    MessageSource,
    StateInitSource,
    FunctionHeader,
    ParamsOfEncodeMessageBody,
    ParamsOfDecodeMessage,
    MessageBodyType,
    ParamsOfParse,
    ParamsOfDecodeMessageBody,
    ParamsOfEncodeMessage,
    ParamsOfSign,
    ParamsOfAttachSignature,
    ParamsOfEncodeAccount,
    ParamsOfEncodeInternalMessage,
    ParamsOfGetBocHash,
    ParamsOfGetCodeFromTvc,
    ParamsOfDecodeAccountData,
    ParamsOfDecodeStateInit,
    ParamsOfDecodeInitialData,
    ParamsOfUpdateInitialData,
    AbiParam,
    ParamsOfDecodeBoc,
    ParamsOfEncodeInitialData,
    ParamsOfAbiEncodeBoc,
)


class TestTonAbiAsyncCore(unittest.TestCase):
    def setUp(self) -> None:
        # Events contract params
        self.events_abi = Abi.from_path(
            path=os.path.join(SAMPLES_DIR, 'Events.abi.json')
        )
        self.keypair = KeyPair(
            public='4c7c408ff1ddebb8d6405ee979c716a14fdd6cc08124107a61d3c25597099499',
            secret='cc8929d635719612a9478b9cd17675a39cfad52d8959e8a177389b8c0b9122a7',
        )
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
        boc = async_core_client.boc.parse_message(params=ParamsOfParse(boc=message))

        decode_params = ParamsOfDecodeMessageBody(
            abi=self.events_abi, body=boc.parsed['body'], is_internal=False
        )
        decoded = async_core_client.abi.decode_message_body(params=decode_params)
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
                pubkey=self.keypair.public,
                time=self.events_time,
                expire=self.events_expire,
            ),
        )
        signer = Signer.External(public_key=self.keypair.public)

        # Create unsigned deployment message
        params = ParamsOfEncodeMessage(
            abi=self.events_abi, signer=signer, deploy_set=deploy_set, call_set=call_set
        )
        unsigned = async_core_client.abi.encode_message(params=params)
        self.assertEqual(
            'te6ccgECFwEAA2gAAqeIAAt9aqvShfTon7Lei1PVOhUEkEEZQkhDKPgNyzeTL6YSEZTHxAj/Hd67jWQF7peccWoU/dbMCBJBB6YdPCVZcJlJkAAAF0ZyXLg19VzGRotV8/gGAQEBwAICA88gBQMBAd4EAAPQIABB2mPiBH+O713GsgL3S844tQp+62YECSCD0w6eEqy4TKTMAib/APSkICLAAZL0oOGK7VNYMPShCQcBCvSkIPShCAAAAgEgDAoByP9/Ie1E0CDXScIBjhDT/9M/0wDRf/hh+Gb4Y/hijhj0BXABgED0DvK91wv/+GJw+GNw+GZ/+GHi0wABjh2BAgDXGCD5AQHTAAGU0/8DAZMC+ELiIPhl+RDyqJXTAAHyeuLTPwELAGqOHvhDIbkgnzAg+COBA+iogggbd0Cgud6S+GPggDTyNNjTHwH4I7zyudMfAfAB+EdukvI83gIBIBINAgEgDw4AvbqLVfP/hBbo417UTQINdJwgGOENP/0z/TANF/+GH4Zvhj+GKOGPQFcAGAQPQO8r3XC//4YnD4Y3D4Zn/4YeLe+Ebyc3H4ZtH4APhCyMv/+EPPCz/4Rs8LAMntVH/4Z4AgEgERAA5biABrW/CC3Rwn2omhp/+mf6YBov/ww/DN8Mfwxb30gyupo6H0gb+j8IpA3SRg4b3whXXlwMnwAZGT9ghBkZ8KEZ0aCBAfQAAAAAAAAAAAAAAAAACBni2TAgEB9gBh8IWRl//wh54Wf/CNnhYBk9qo//DPAAxbmTwqLfCC3Rwn2omhp/+mf6YBov/ww/DN8Mfwxb2uG/8rqaOhp/+/o/ABkRe4AAAAAAAAAAAAAAAAIZ4tnwOfI48sYvRDnhf/kuP2AGHwhZGX//CHnhZ/8I2eFgGT2qj/8M8AIBSBYTAQm4t8WCUBQB/PhBbo4T7UTQ0//TP9MA0X/4Yfhm+GP4Yt7XDf+V1NHQ0//f0fgAyIvcAAAAAAAAAAAAAAAAEM8Wz4HPkceWMXohzwv/yXH7AMiL3AAAAAAAAAAAAAAAABDPFs+Bz5JW+LBKIc8L/8lx+wAw+ELIy//4Q88LP/hGzwsAye1UfxUABPhnAHLccCLQ1gIx0gAw3CHHAJLyO+Ah1w0fkvI84VMRkvI74cEEIoIQ/////byxkvI84AHwAfhHbpLyPN4=',
            unsigned.message,
        )
        self.assertEqual(
            'KCGM36iTYuCYynk+Jnemis+mcwi3RFCke95i7l96s4Q=', unsigned.data_to_sign
        )

        # Create detached signature
        sign_params = ParamsOfSign(unsigned=unsigned.data_to_sign, keys=self.keypair)
        signature = async_core_client.crypto.sign(params=sign_params)
        self.assertEqual(
            '6272357bccb601db2b821cb0f5f564ab519212d242cf31961fe9a3c50a30b236012618296b4f769355c0e9567cd25b366f3c037435c498c82e5305622adbc70e',
            signature.signature,
        )

        # Attach signature to unsigned message
        attach_params = ParamsOfAttachSignature(
            abi=self.events_abi,
            public_key=self.keypair.public,
            message=unsigned.message,
            signature=signature.signature,
        )
        signed = async_core_client.abi.attach_signature(params=attach_params)
        self.assertEqual(
            'te6ccgECGAEAA6wAA0eIAAt9aqvShfTon7Lei1PVOhUEkEEZQkhDKPgNyzeTL6YSEbAHAgEA4bE5Gr3mWwDtlcEOWHr6slWoyQlpIWeYyw/00eKFGFkbAJMMFLWnu0mq4HSrPmktmzeeAboa4kxkFymCsRVt44dTHxAj/Hd67jWQF7peccWoU/dbMCBJBB6YdPCVZcJlJkAAAF0ZyXLg19VzGRotV8/gAQHAAwIDzyAGBAEB3gUAA9AgAEHaY+IEf47vXcayAvdLzji1Cn7rZgQJIIPTDp4SrLhMpMwCJv8A9KQgIsABkvSg4YrtU1gw9KEKCAEK9KQg9KEJAAACASANCwHI/38h7UTQINdJwgGOENP/0z/TANF/+GH4Zvhj+GKOGPQFcAGAQPQO8r3XC//4YnD4Y3D4Zn/4YeLTAAGOHYECANcYIPkBAdMAAZTT/wMBkwL4QuIg+GX5EPKoldMAAfJ64tM/AQwAao4e+EMhuSCfMCD4I4ED6KiCCBt3QKC53pL4Y+CANPI02NMfAfgjvPK50x8B8AH4R26S8jzeAgEgEw4CASAQDwC9uotV8/+EFujjXtRNAg10nCAY4Q0//TP9MA0X/4Yfhm+GP4Yo4Y9AVwAYBA9A7yvdcL//hicPhjcPhmf/hh4t74RvJzcfhm0fgA+ELIy//4Q88LP/hGzwsAye1Uf/hngCASASEQDluIAGtb8ILdHCfaiaGn/6Z/pgGi//DD8M3wx/DFvfSDK6mjofSBv6PwikDdJGDhvfCFdeXAyfABkZP2CEGRnwoRnRoIEB9AAAAAAAAAAAAAAAAAAIGeLZMCAQH2AGHwhZGX//CHnhZ/8I2eFgGT2qj/8M8ADFuZPCot8ILdHCfaiaGn/6Z/pgGi//DD8M3wx/DFva4b/yupo6Gn/7+j8AGRF7gAAAAAAAAAAAAAAAAhni2fA58jjyxi9EOeF/+S4/YAYfCFkZf/8IeeFn/wjZ4WAZPaqP/wzwAgFIFxQBCbi3xYJQFQH8+EFujhPtRNDT/9M/0wDRf/hh+Gb4Y/hi3tcN/5XU0dDT/9/R+ADIi9wAAAAAAAAAAAAAAAAQzxbPgc+Rx5YxeiHPC//JcfsAyIvcAAAAAAAAAAAAAAAAEM8Wz4HPklb4sEohzwv/yXH7ADD4QsjL//hDzws/+EbPCwDJ7VR/FgAE+GcActxwItDWAjHSADDcIccAkvI74CHXDR+S8jzhUxGS8jvhwQQighD////9vLGS8jzgAfAB+EdukvI83g==',
            signed.message,
        )

        # Create initially signed message
        signer = Signer.Keys(keys=self.keypair)
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi, signer=signer, deploy_set=deploy_set, call_set=call_set
        )
        signed = async_core_client.abi.encode_message(params=encode_params)
        self.assertEqual(
            'te6ccgECGAEAA6wAA0eIAAt9aqvShfTon7Lei1PVOhUEkEEZQkhDKPgNyzeTL6YSEbAHAgEA4bE5Gr3mWwDtlcEOWHr6slWoyQlpIWeYyw/00eKFGFkbAJMMFLWnu0mq4HSrPmktmzeeAboa4kxkFymCsRVt44dTHxAj/Hd67jWQF7peccWoU/dbMCBJBB6YdPCVZcJlJkAAAF0ZyXLg19VzGRotV8/gAQHAAwIDzyAGBAEB3gUAA9AgAEHaY+IEf47vXcayAvdLzji1Cn7rZgQJIIPTDp4SrLhMpMwCJv8A9KQgIsABkvSg4YrtU1gw9KEKCAEK9KQg9KEJAAACASANCwHI/38h7UTQINdJwgGOENP/0z/TANF/+GH4Zvhj+GKOGPQFcAGAQPQO8r3XC//4YnD4Y3D4Zn/4YeLTAAGOHYECANcYIPkBAdMAAZTT/wMBkwL4QuIg+GX5EPKoldMAAfJ64tM/AQwAao4e+EMhuSCfMCD4I4ED6KiCCBt3QKC53pL4Y+CANPI02NMfAfgjvPK50x8B8AH4R26S8jzeAgEgEw4CASAQDwC9uotV8/+EFujjXtRNAg10nCAY4Q0//TP9MA0X/4Yfhm+GP4Yo4Y9AVwAYBA9A7yvdcL//hicPhjcPhmf/hh4t74RvJzcfhm0fgA+ELIy//4Q88LP/hGzwsAye1Uf/hngCASASEQDluIAGtb8ILdHCfaiaGn/6Z/pgGi//DD8M3wx/DFvfSDK6mjofSBv6PwikDdJGDhvfCFdeXAyfABkZP2CEGRnwoRnRoIEB9AAAAAAAAAAAAAAAAAAIGeLZMCAQH2AGHwhZGX//CHnhZ/8I2eFgGT2qj/8M8ADFuZPCot8ILdHCfaiaGn/6Z/pgGi//DD8M3wx/DFva4b/yupo6Gn/7+j8AGRF7gAAAAAAAAAAAAAAAAhni2fA58jjyxi9EOeF/+S4/YAYfCFkZf/8IeeFn/wjZ4WAZPaqP/wzwAgFIFxQBCbi3xYJQFQH8+EFujhPtRNDT/9M/0wDRf/hh+Gb4Y/hi3tcN/5XU0dDT/9/R+ADIi9wAAAAAAAAAAAAAAAAQzxbPgc+Rx5YxeiHPC//JcfsAyIvcAAAAAAAAAAAAAAAAEM8Wz4HPklb4sEohzwv/yXH7ADD4QsjL//hDzws/+EbPCwDJ7VR/FgAE+GcActxwItDWAjHSADDcIccAkvI74CHXDR+S8jzhUxGS8jvhwQQighD////9vLGS8jzgAfAB+EdukvI83g==',
            signed.message,
        )

        # Sign with signing box
        sbox = async_core_client.crypto.get_signing_box(params=self.keypair)
        signer_sbox = Signer.SigningBox(handle=sbox.handle)
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi,
            signer=signer_sbox,
            deploy_set=deploy_set,
            call_set=call_set,
        )
        signed_sbox = async_core_client.abi.encode_message(params=encode_params)
        async_core_client.crypto.remove_signing_box(params=sbox)
        self.assertEqual(signed.message, signed_sbox.message)

        # Create run unsigned message
        address = '0:05beb555e942fa744fd96f45a9ea9d0a8248208ca12421947c06e59bc997d309'
        call_set = CallSet(
            function_name='returnValue',
            input={'id': '0'},
            header=FunctionHeader(
                **{
                    'pubkey': self.keypair.public,
                    'time': self.events_time,
                    'expire': self.events_expire,
                }
            ),
        )
        signer = Signer.External(public_key=self.keypair.public)
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi, signer=signer, address=address, call_set=call_set
        )
        unsigned = async_core_client.abi.encode_message(params=encode_params)
        self.assertEqual(
            'te6ccgEBAgEAeAABpYgAC31qq9KF9Oifst6LU9U6FQSQQRlCSEMo+A3LN5MvphIFMfECP8d3ruNZAXul5xxahT91swIEkEHph08JVlwmUmQAAAXRnJcuDX1XMZBW+LBKAQBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=',
            unsigned.message,
        )
        self.assertEqual(
            'i4Hs3PB12QA9UBFbOIpkG3JerHHqjm4LgvF4MA7TDsY=', unsigned.data_to_sign
        )

        # Create detached signature
        sign_params = ParamsOfSign(unsigned=unsigned.data_to_sign, keys=self.keypair)
        signature = async_core_client.crypto.sign(params=sign_params)
        self.assertEqual(
            '5bbfb7f184f2cb5f019400b9cd497eeaa41f3d5885619e9f7d4fab8dd695f4b3a02159a1422996c1dd7d1be67898bc79c6adba6c65a18101ac5f0a2a2bb8910b',
            signature.signature,
        )

        # Attach signature
        attach_params = ParamsOfAttachSignature(
            abi=self.events_abi,
            public_key=self.keypair.public,
            message=unsigned.message,
            signature=signature.signature,
        )
        signed = async_core_client.abi.attach_signature(params=attach_params)
        self.assertEqual(
            'te6ccgEBAwEAvAABRYgAC31qq9KF9Oifst6LU9U6FQSQQRlCSEMo+A3LN5MvphIMAQHhrd/b+MJ5Za+AygBc5qS/dVIPnqxCsM9PvqfVxutK+lnQEKzQoRTLYO6+jfM8TF4841bdNjLQwIDWL4UVFdxIhdMfECP8d3ruNZAXul5xxahT91swIEkEHph08JVlwmUmQAAAXRnJcuDX1XMZBW+LBKACAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==',
            signed.message,
        )

        # Get signature data
        data_params = ParamsOfGetSignatureData(
            abi=self.events_abi, message=signed.message
        )
        data = async_core_client.abi.get_signature_data(params=data_params)
        self.assertEqual(unsigned.data_to_sign, data.unsigned)
        self.assertEqual(signature.signature, data.signature)

        # Create initially signed message
        signer = Signer.Keys(keys=self.keypair)
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi, signer=signer, address=address, call_set=call_set
        )
        signed = async_core_client.abi.encode_message(params=encode_params)
        self.assertEqual(
            'te6ccgEBAwEAvAABRYgAC31qq9KF9Oifst6LU9U6FQSQQRlCSEMo+A3LN5MvphIMAQHhrd/b+MJ5Za+AygBc5qS/dVIPnqxCsM9PvqfVxutK+lnQEKzQoRTLYO6+jfM8TF4841bdNjLQwIDWL4UVFdxIhdMfECP8d3ruNZAXul5xxahT91swIEkEHph08JVlwmUmQAAAXRnJcuDX1XMZBW+LBKACAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==',
            signed.message,
        )

    def test_encode_message_body(self):
        header = FunctionHeader(
            expire=self.events_expire, time=self.events_time, pubkey=self.keypair.public
        )
        call_set = CallSet(
            function_name='returnValue', header=header, input={'id': '0'}
        )
        signer = Signer.Keys(keys=self.keypair)
        params = ParamsOfEncodeMessageBody(
            abi=self.events_abi, call_set=call_set, is_internal=False, signer=signer
        )
        encoded = async_core_client.abi.encode_message_body(params=params)

        self.assertIsNone(encoded.data_to_sign)

    def test_encode_account(self):
        # Encode account from encoded deploy message
        encoded_deploy_message = 'te6ccgECFwEAA2gAAqeIAAt9aqvShfTon7Lei1PVOhUEkEEZQkhDKPgNyzeTL6YSEZTHxAj/Hd67jWQF7peccWoU/dbMCBJBB6YdPCVZcJlJkAAAF0ZyXLg19VzGRotV8/gGAQEBwAICA88gBQMBAd4EAAPQIABB2mPiBH+O713GsgL3S844tQp+62YECSCD0w6eEqy4TKTMAib/APSkICLAAZL0oOGK7VNYMPShCQcBCvSkIPShCAAAAgEgDAoByP9/Ie1E0CDXScIBjhDT/9M/0wDRf/hh+Gb4Y/hijhj0BXABgED0DvK91wv/+GJw+GNw+GZ/+GHi0wABjh2BAgDXGCD5AQHTAAGU0/8DAZMC+ELiIPhl+RDyqJXTAAHyeuLTPwELAGqOHvhDIbkgnzAg+COBA+iogggbd0Cgud6S+GPggDTyNNjTHwH4I7zyudMfAfAB+EdukvI83gIBIBINAgEgDw4AvbqLVfP/hBbo417UTQINdJwgGOENP/0z/TANF/+GH4Zvhj+GKOGPQFcAGAQPQO8r3XC//4YnD4Y3D4Zn/4YeLe+Ebyc3H4ZtH4APhCyMv/+EPPCz/4Rs8LAMntVH/4Z4AgEgERAA5biABrW/CC3Rwn2omhp/+mf6YBov/ww/DN8Mfwxb30gyupo6H0gb+j8IpA3SRg4b3whXXlwMnwAZGT9ghBkZ8KEZ0aCBAfQAAAAAAAAAAAAAAAAACBni2TAgEB9gBh8IWRl//wh54Wf/CNnhYBk9qo//DPAAxbmTwqLfCC3Rwn2omhp/+mf6YBov/ww/DN8Mfwxb2uG/8rqaOhp/+/o/ABkRe4AAAAAAAAAAAAAAAAIZ4tnwOfI48sYvRDnhf/kuP2AGHwhZGX//CHnhZ/8I2eFgGT2qj/8M8AIBSBYTAQm4t8WCUBQB/PhBbo4T7UTQ0//TP9MA0X/4Yfhm+GP4Yt7XDf+V1NHQ0//f0fgAyIvcAAAAAAAAAAAAAAAAEM8Wz4HPkceWMXohzwv/yXH7AMiL3AAAAAAAAAAAAAAAABDPFs+Bz5JW+LBKIc8L/8lx+wAw+ELIy//4Q88LP/hGzwsAye1UfxUABPhnAHLccCLQ1gIx0gAw3CHHAJLyO+Ah1w0fkvI84VMRkvI74cEEIoIQ/////byxkvI84AHwAfhHbpLyPN4='
        message_source = MessageSource.Encoded(
            message=encoded_deploy_message, abi=self.events_abi
        )
        state_init_source = StateInitSource.Message(source=message_source)

        encode_params = ParamsOfEncodeAccount(state_init=state_init_source)
        encoded = async_core_client.abi.encode_account(params=encode_params)
        self.assertEqual(
            '05beb555e942fa744fd96f45a9ea9d0a8248208ca12421947c06e59bc997d309',
            encoded.id,
        )

        # Encode account from encoding params
        deploy_set = DeploySet(tvc=self.events_tvc)
        call_set = CallSet(
            function_name='constructor',
            header=FunctionHeader(
                **{
                    'pubkey': self.keypair.public,
                    'time': self.events_time,
                    'expire': self.events_expire,
                }
            ),
        )
        signer = Signer.Keys(keys=self.keypair)
        encoding_params = ParamsOfEncodeMessage(
            abi=self.events_abi, signer=signer, deploy_set=deploy_set, call_set=call_set
        )
        message_source = MessageSource.EncodingParams(params=encoding_params)
        state_init_source = StateInitSource.Message(source=message_source)
        encode_params = ParamsOfEncodeAccount(state_init=state_init_source)
        encoded = async_core_client.abi.encode_account(params=encode_params)
        self.assertEqual(
            '05beb555e942fa744fd96f45a9ea9d0a8248208ca12421947c06e59bc997d309',
            encoded.id,
        )

        # Test exception (external signer)
        with self.assertRaises(TonException):
            signer = Signer.External(public_key=self.keypair.public)
            encoding_params = ParamsOfEncodeMessage(
                abi=self.events_abi,
                signer=signer,
                deploy_set=deploy_set,
                call_set=call_set,
            )
            message_source = MessageSource.EncodingParams(params=encoding_params)
            state_init_source = StateInitSource.Message(source=message_source)
            encode_params = ParamsOfEncodeAccount(state_init=state_init_source)
            async_core_client.abi.encode_account(params=encode_params)

        # Encode account from TVC
        state_init_source = StateInitSource.Tvc(tvc=self.events_tvc)
        encode_params = ParamsOfEncodeAccount(state_init=state_init_source)
        encoded = async_core_client.abi.encode_account(params=encode_params)
        self.assertNotEqual(
            '05beb555e942fa744fd96f45a9ea9d0a8248208ca12421947c06e59bc997d309',
            encoded.id,
        )

        state_init_source = StateInitSource.Tvc(
            tvc=self.events_tvc, public_key=self.keypair.public
        )
        encode_params = ParamsOfEncodeAccount(state_init=state_init_source)
        encoded = async_core_client.abi.encode_account(params=encode_params)
        self.assertEqual(
            '05beb555e942fa744fd96f45a9ea9d0a8248208ca12421947c06e59bc997d309',
            encoded.id,
        )

    def test_encode_internal_message_run(self):
        address = '0:1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
        abi = Abi.from_path(path=os.path.join(SAMPLES_DIR, 'Hello.abi.json'))

        result = async_core_client.abi.encode_internal_message(
            params=ParamsOfEncodeInternalMessage(
                abi=abi,
                value='1000000000',
                address=address,
                call_set=CallSet(function_name='sayHello'),
                bounce=True,
            )
        )
        self.assertEqual(address, result.address)
        self.assertEqual(
            'te6ccgEBAQEAOgAAcGIACRorPEhV5veJGis8SFXm94kaKzxIVeb3iRorPEhV5veh3NZQAAAAAAAAAAAAAAAAAABQy+0X',
            result.message,
        )

        boc_hash = async_core_client.boc.get_boc_hash(
            params=ParamsOfGetBocHash(boc=result.message)
        )
        self.assertEqual(result.message_id, boc_hash.hash)

        parsed = async_core_client.boc.parse_message(
            params=ParamsOfParse(boc=result.message)
        )
        self.assertEqual('internal', parsed.parsed['msg_type_name'])
        self.assertEqual('', parsed.parsed['src'])
        self.assertEqual(address, parsed.parsed['dst'])
        self.assertEqual('0x3b9aca00', parsed.parsed['value'])
        self.assertEqual(True, parsed.parsed['bounce'])
        self.assertEqual(True, parsed.parsed['ihr_disabled'])

    def test_encode_internal_message_deploy(self):
        abi = Abi.from_path(path=os.path.join(SAMPLES_DIR, 'Hello.abi.json'))
        with open(os.path.join(SAMPLES_DIR, 'Hello.tvc'), 'rb') as fp:
            tvc = base64.b64encode(fp.read()).decode()

        result = async_core_client.abi.encode_internal_message(
            params=ParamsOfEncodeInternalMessage(
                abi=abi,
                value='0',
                deploy_set=DeploySet(tvc=tvc),
                call_set=CallSet(function_name='constructor'),
            )
        )
        self.assertEqual(
            'te6ccgECHAEABG0AAmliADYO5IoxskLmUfURre2fOB04OmP32VjPwA/lDM/Cpvh8AAAAAAAAAAAAAAAAAAIxotV8/gYBAQHAAgIDzyAFAwEB3gQAA9AgAEHYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQCJv8A9KQgIsABkvSg4YrtU1gw9KEJBwEK9KQg9KEIAAACASAMCgHo/38h0wABjiaBAgDXGCD5AQFw7UTQ9AWAQPQO8orXC/8B7Ucib3XtVwMB+RDyqN7tRNAg10nCAY4W9ATTP9MA7UcBb3EBb3YBb3MBb3LtV44Y9AXtRwFvcnBvc3BvdsiAIM9AydBvce1X4tM/Ae1HbxMhuSALAGCfMCD4I4ED6KiCCBt3QKC53pntRyFvUyDtVzCUgDTy8OIw0x8B+CO88rnTHwHxQAECASAYDQIBIBEOAQm6i1Xz+A8B+u1Hb2FujjvtRNAg10nCAY4W9ATTP9MA7UcBb3EBb3YBb3MBb3LtV44Y9AXtRwFvcnBvc3BvdsiAIM9AydBvce1X4t7tR28WkvIzl+1HcW9W7VfiAPgA0fgjtR/tRyBvETAByMsfydBvUe1X7UdvEsj0AO1HbxPPCz/tR28WEAAczwsA7UdvEc8Wye1UcGoCAWoVEgEJtAAa1sATAfztR29hbo477UTQINdJwgGOFvQE0z/TAO1HAW9xAW92AW9zAW9y7VeOGPQF7UcBb3Jwb3Nwb3bIgCDPQMnQb3HtV+Le7UdvZSBukjBw3nDtR28SgED0DvKK1wv/uvLgZPgA+kDRIMjJ+wSBA+hwgQCAyHHPCwEizwoAcc9A+CgUAI7PFiTPFiP6AnHPQHD6AnD6AoBAz0D4I88LH3LPQCDJIvsAXwUw7UdvEsj0AO1HbxPPCz/tR28WzwsA7UdvEc8Wye1UcGrbMAEJtGX2i8AWAfjtR29hbo477UTQINdJwgGOFvQE0z/TAO1HAW9xAW92AW9zAW9y7VeOGPQF7UcBb3Jwb3Nwb3bIgCDPQMnQb3HtV+Le0e1HbxHXCx/IghBQy+0XghCAAAAAsc8LHyHPCx/Ic88LAfgozxZyz0D4Jc8LP4Ahz0AgzzUizzG8FwB4lnHPQCHPF5Vxz0EhzeIgyXH7AFshwP+OHu1HbxLI9ADtR28Tzws/7UdvFs8LAO1HbxHPFsntVN5xatswAgEgGxkBCbtzEuRYGgD47UdvYW6OO+1E0CDXScIBjhb0BNM/0wDtRwFvcQFvdgFvcwFvcu1Xjhj0Be1HAW9ycG9zcG92yIAgz0DJ0G9x7Vfi3vgA0fgjtR/tRyBvETAByMsfydBvUe1X7UdvEsj0AO1HbxPPCz/tR28WzwsA7UdvEc8Wye1UcGrbMADK3XAh10kgwSCOKyDAAI4cI9Bz1yHXCwAgwAGW2zBfB9swltswXwfbMOME2ZbbMF8G2zDjBNngItMfNCB0uyCOFTAgghD/////uiCZMCCCEP////6639+W2zBfB9sw4CMh8UABXwc=',
            result.message,
        )

        boc_hash = async_core_client.boc.get_boc_hash(
            params=ParamsOfGetBocHash(boc=result.message)
        )
        self.assertEqual(result.message_id, boc_hash.hash)

        parsed = async_core_client.boc.parse_message(
            params=ParamsOfParse(boc=result.message)
        )
        code = async_core_client.boc.get_code_from_tvc(
            params=ParamsOfGetCodeFromTvc(tvc=tvc)
        )
        self.assertEqual(code.code, parsed.parsed['code'])

    def test_decode_account_data(self):
        data = 'te6ccgEBBwEA8AAEWeix2Dmr4nsqu51KKUOpFDqcfirgZ5m9JN7B16iJGuXdAAABeqRZIJYAAAAW4AYEAwEBQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPAgAAABRJIGxpa2UgaXQuAcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIFAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKSGVsbG8='
        abi = Abi.Json(
            value='{"ABI version":2,"version":"2.1","header":["time"],"functions":[],"data":[],"events":[],"fields":[{"name":"__pubkey","type":"uint256"},{"name":"__timestamp","type":"uint64"},{"name":"fun","type":"uint32"},{"name":"opt","type":"optional(bytes)"},{"name":"big","type":"optional(tuple)","components":[{"name":"value0","type":"uint256"},{"name":"value1","type":"uint256"},{"name":"value2","type":"uint256"},{"name":"value3","type":"uint256"}]},{"name":"a","type":"bytes"},{"name":"b","type":"bytes"},{"name":"length","type":"uint256"}]}'
        )

        params = ParamsOfDecodeAccountData(abi=abi, data=data)
        decoded = async_core_client.abi.decode_account_data(params=params)
        self.assertEqual(
            '0xe8b1d839abe27b2abb9d4a2943a9143a9c7e2ae06799bd24dec1d7a8891ae5dd',
            decoded.data['__pubkey'],
        )

    def test_decode_update_initial_data(self):
        # Get contract abi, tvc
        abi = Abi.from_path(path=os.path.join(SAMPLES_DIR, 't24_initdata.abi.json'))
        with open(os.path.join(SAMPLES_DIR, 't24_initdata.tvc'), 'rb') as fp:
            tvc = base64.b64encode(fp.read()).decode()

        # Get and decode contract initial data
        params = ParamsOfDecodeStateInit(state_init=tvc)
        data = async_core_client.boc.decode_state_init(params).data
        params = ParamsOfDecodeInitialData(data=data, abi=abi)
        decoded = async_core_client.abi.decode_initial_data(params)
        self.assertEqual('00' * 32, decoded.initial_pubkey)
        self.assertEqual({}, decoded.initial_data)

        # Encode initial data
        initial_data = {'a': 123, 's': 'some string'}
        initial_pubkey = '22' * 32
        encoded_initial_data = 'te6ccgEBBwEARwABAcABAgPPoAQCAQFIAwAWc29tZSBzdHJpbmcCASAGBQADHuAAQQiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIoA=='
        params = ParamsOfEncodeInitialData(
            abi=abi, initial_data=initial_data, initial_pubkey=initial_pubkey
        )
        encoded = async_core_client.abi.encode_initial_data(params)
        self.assertEqual(encoded_initial_data, encoded.data)

        # Update initial data
        params = ParamsOfUpdateInitialData(
            data=data, abi=abi, initial_data=initial_data, initial_pubkey=initial_pubkey
        )
        data_updated = async_core_client.abi.update_initial_data(params).data
        self.assertEqual(encoded_initial_data, data_updated)

        # Decode updated data
        params = ParamsOfDecodeInitialData(data=data_updated, abi=abi)
        decoded = async_core_client.abi.decode_initial_data(params)
        self.assertEqual(initial_data['a'], int(decoded.initial_data['a']))
        self.assertEqual(initial_data['s'], decoded.initial_data['s'])
        self.assertEqual(initial_pubkey, decoded.initial_pubkey)

    def test_decode_boc(self):
        boc = 'te6ccgEBAgEAEgABCQAAAADAAQAQAAAAAAAAAHs='
        p = [
            AbiParam(name='a', type='uint32'),
            AbiParam(name='b', type='ref(int64)'),
            AbiParam(name='c', type='bool'),
        ]
        params = ParamsOfDecodeBoc(params=p, boc=boc, allow_partial=True)
        decoded = async_core_client.abi.decode_boc(params)
        self.assertEqual({'a': '0', 'b': '123', 'c': True}, decoded.data)

        params.params.pop()
        decoded = async_core_client.abi.decode_boc(params)
        self.assertEqual({'a': '0', 'b': '123'}, decoded.data)

    def test_encode_boc(self):
        _params = [
            AbiParam(name='dest', type='address'),
            AbiParam(name='value', type='uint128'),
            AbiParam(name='bounce', type='bool'),
        ]
        _data = {
            'dest': '-1:3333333333333333333333333333333333333333333333333333333333333333',
            'value': 1234567,
            'bounce': True,
        }
        params = ParamsOfAbiEncodeBoc(params=_params, data=_data)
        encoded = async_core_client.abi.encode_boc(params)
        self.assertEqual(
            'te6ccgEBAQEANAAAY5/mZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmAAAAAAAAAAAAAAAAACWtD4',
            encoded.boc,
        )

    def test_calc_function_id(self):
        abi = Abi.from_path(path=os.path.join(SAMPLES_DIR, 'Giver-v2.abi.json'))
        params = ParamsOfCalcFunctionId(abi=abi, function_name='getMessages')
        result = async_core_client.abi.calc_function_id(params)
        self.assertEqual('0x7744c7e2', hex(result.function_id))

        params = ParamsOfCalcFunctionId(
            abi=abi, function_name='getMessages', output=True
        )
        result = async_core_client.abi.calc_function_id(params)
        self.assertEqual('0xf744c7e2', hex(result.function_id))

    def test_decode_responsible(self):
        body = 'te6ccgEBAgEAsQAB0IAAAAAAAABnAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABDnTBYAAAAAAAAAAAAAAAAAO5rKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAQCHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGAD9YhN79S7hQOnrVCizdlF32dvf9Wk8XgGP1lsYvH/14AYHg='
        abi = Abi.from_path(path=os.path.join(SAMPLES_DIR, 'PriceXchg.abi.json'))
        params = ParamsOfDecodeMessageBody(
            abi=abi,
            body=body,
            function_name='onTip3LendOwnership',
            data_layout=DataLayout.OUTPUT,
            is_internal=True,
        )
        result = async_core_client.abi.decode_message_body(params)
        self.assertEqual(103, int(result.value['err_code']))
        self.assertEqual(
            '0:7eb109bdfa9770a074f5aa1459bb28bbecedeffab49e2f00c7eb2d8c5e3ffaf0',
            result.value['pair'],
        )
        self.assertTrue(result.value['sell'])


class TestTonAbiSyncCore(unittest.TestCase):
    """Sync core is not recommended to use, so make just a couple of tests"""

    def setUp(self) -> None:
        # Events contract params
        self.events_abi = Abi.from_path(
            path=os.path.join(SAMPLES_DIR, 'Events.abi.json')
        )
        self.keypair = KeyPair(
            public='4c7c408ff1ddebb8d6405ee979c716a14fdd6cc08124107a61d3c25597099499',
            secret='cc8929d635719612a9478b9cd17675a39cfad52d8959e8a177389b8c0b9122a7',
        )
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

    def test_encode_internal_message_run(self):
        address = '0:1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
        abi = Abi.from_path(path=os.path.join(SAMPLES_DIR, 'Hello.abi.json'))

        result = sync_core_client.abi.encode_internal_message(
            params=ParamsOfEncodeInternalMessage(
                abi=abi,
                value='1000000000',
                address=address,
                call_set=CallSet(function_name='sayHello'),
                bounce=True,
            )
        )
        self.assertEqual(address, result.address)
        self.assertEqual(
            'te6ccgEBAQEAOgAAcGIACRorPEhV5veJGis8SFXm94kaKzxIVeb3iRorPEhV5veh3NZQAAAAAAAAAAAAAAAAAABQy+0X',
            result.message,
        )

        boc_hash = sync_core_client.boc.get_boc_hash(
            params=ParamsOfGetBocHash(boc=result.message)
        )
        self.assertEqual(result.message_id, boc_hash.hash)

        parsed = sync_core_client.boc.parse_message(
            params=ParamsOfParse(boc=result.message)
        )
        self.assertEqual('internal', parsed.parsed['msg_type_name'])
        self.assertEqual('', parsed.parsed['src'])
        self.assertEqual(address, parsed.parsed['dst'])
        self.assertEqual('0x3b9aca00', parsed.parsed['value'])
        self.assertEqual(True, parsed.parsed['bounce'])
        self.assertEqual(True, parsed.parsed['ihr_disabled'])

    def test_decode_message_body(self):
        message = 'te6ccgEBAwEAvAABRYgAC31qq9KF9Oifst6LU9U6FQSQQRlCSEMo+A3LN5MvphIMAQHhrd/b+MJ5Za+AygBc5qS/dVIPnqxCsM9PvqfVxutK+lnQEKzQoRTLYO6+jfM8TF4841bdNjLQwIDWL4UVFdxIhdMfECP8d3ruNZAXul5xxahT91swIEkEHph08JVlwmUmQAAAXRnJcuDX1XMZBW+LBKACAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=='
        boc = sync_core_client.boc.parse_message(params=ParamsOfParse(boc=message))

        decode_params = ParamsOfDecodeMessageBody(
            abi=self.events_abi, body=boc.parsed['body'], is_internal=False
        )
        decoded = sync_core_client.abi.decode_message_body(params=decode_params)
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
                pubkey=self.keypair.public,
                time=self.events_time,
                expire=self.events_expire,
            ),
        )
        signer = Signer.External(public_key=self.keypair.public)

        # Create unsigned deployment message
        params = ParamsOfEncodeMessage(
            abi=self.events_abi, signer=signer, deploy_set=deploy_set, call_set=call_set
        )
        unsigned = sync_core_client.abi.encode_message(params=params)
        self.assertEqual(
            'te6ccgECFwEAA2gAAqeIAAt9aqvShfTon7Lei1PVOhUEkEEZQkhDKPgNyzeTL6YSEZTHxAj/Hd67jWQF7peccWoU/dbMCBJBB6YdPCVZcJlJkAAAF0ZyXLg19VzGRotV8/gGAQEBwAICA88gBQMBAd4EAAPQIABB2mPiBH+O713GsgL3S844tQp+62YECSCD0w6eEqy4TKTMAib/APSkICLAAZL0oOGK7VNYMPShCQcBCvSkIPShCAAAAgEgDAoByP9/Ie1E0CDXScIBjhDT/9M/0wDRf/hh+Gb4Y/hijhj0BXABgED0DvK91wv/+GJw+GNw+GZ/+GHi0wABjh2BAgDXGCD5AQHTAAGU0/8DAZMC+ELiIPhl+RDyqJXTAAHyeuLTPwELAGqOHvhDIbkgnzAg+COBA+iogggbd0Cgud6S+GPggDTyNNjTHwH4I7zyudMfAfAB+EdukvI83gIBIBINAgEgDw4AvbqLVfP/hBbo417UTQINdJwgGOENP/0z/TANF/+GH4Zvhj+GKOGPQFcAGAQPQO8r3XC//4YnD4Y3D4Zn/4YeLe+Ebyc3H4ZtH4APhCyMv/+EPPCz/4Rs8LAMntVH/4Z4AgEgERAA5biABrW/CC3Rwn2omhp/+mf6YBov/ww/DN8Mfwxb30gyupo6H0gb+j8IpA3SRg4b3whXXlwMnwAZGT9ghBkZ8KEZ0aCBAfQAAAAAAAAAAAAAAAAACBni2TAgEB9gBh8IWRl//wh54Wf/CNnhYBk9qo//DPAAxbmTwqLfCC3Rwn2omhp/+mf6YBov/ww/DN8Mfwxb2uG/8rqaOhp/+/o/ABkRe4AAAAAAAAAAAAAAAAIZ4tnwOfI48sYvRDnhf/kuP2AGHwhZGX//CHnhZ/8I2eFgGT2qj/8M8AIBSBYTAQm4t8WCUBQB/PhBbo4T7UTQ0//TP9MA0X/4Yfhm+GP4Yt7XDf+V1NHQ0//f0fgAyIvcAAAAAAAAAAAAAAAAEM8Wz4HPkceWMXohzwv/yXH7AMiL3AAAAAAAAAAAAAAAABDPFs+Bz5JW+LBKIc8L/8lx+wAw+ELIy//4Q88LP/hGzwsAye1UfxUABPhnAHLccCLQ1gIx0gAw3CHHAJLyO+Ah1w0fkvI84VMRkvI74cEEIoIQ/////byxkvI84AHwAfhHbpLyPN4=',
            unsigned.message,
        )
        self.assertEqual(
            'KCGM36iTYuCYynk+Jnemis+mcwi3RFCke95i7l96s4Q=', unsigned.data_to_sign
        )

        # Create detached signature
        sign_params = ParamsOfSign(unsigned=unsigned.data_to_sign, keys=self.keypair)
        signature = sync_core_client.crypto.sign(params=sign_params)
        self.assertEqual(
            '6272357bccb601db2b821cb0f5f564ab519212d242cf31961fe9a3c50a30b236012618296b4f769355c0e9567cd25b366f3c037435c498c82e5305622adbc70e',
            signature.signature,
        )

        # Attach signature to unsigned message
        attach_params = ParamsOfAttachSignature(
            abi=self.events_abi,
            public_key=self.keypair.public,
            message=unsigned.message,
            signature=signature.signature,
        )
        signed = sync_core_client.abi.attach_signature(params=attach_params)
        self.assertEqual(
            'te6ccgECGAEAA6wAA0eIAAt9aqvShfTon7Lei1PVOhUEkEEZQkhDKPgNyzeTL6YSEbAHAgEA4bE5Gr3mWwDtlcEOWHr6slWoyQlpIWeYyw/00eKFGFkbAJMMFLWnu0mq4HSrPmktmzeeAboa4kxkFymCsRVt44dTHxAj/Hd67jWQF7peccWoU/dbMCBJBB6YdPCVZcJlJkAAAF0ZyXLg19VzGRotV8/gAQHAAwIDzyAGBAEB3gUAA9AgAEHaY+IEf47vXcayAvdLzji1Cn7rZgQJIIPTDp4SrLhMpMwCJv8A9KQgIsABkvSg4YrtU1gw9KEKCAEK9KQg9KEJAAACASANCwHI/38h7UTQINdJwgGOENP/0z/TANF/+GH4Zvhj+GKOGPQFcAGAQPQO8r3XC//4YnD4Y3D4Zn/4YeLTAAGOHYECANcYIPkBAdMAAZTT/wMBkwL4QuIg+GX5EPKoldMAAfJ64tM/AQwAao4e+EMhuSCfMCD4I4ED6KiCCBt3QKC53pL4Y+CANPI02NMfAfgjvPK50x8B8AH4R26S8jzeAgEgEw4CASAQDwC9uotV8/+EFujjXtRNAg10nCAY4Q0//TP9MA0X/4Yfhm+GP4Yo4Y9AVwAYBA9A7yvdcL//hicPhjcPhmf/hh4t74RvJzcfhm0fgA+ELIy//4Q88LP/hGzwsAye1Uf/hngCASASEQDluIAGtb8ILdHCfaiaGn/6Z/pgGi//DD8M3wx/DFvfSDK6mjofSBv6PwikDdJGDhvfCFdeXAyfABkZP2CEGRnwoRnRoIEB9AAAAAAAAAAAAAAAAAAIGeLZMCAQH2AGHwhZGX//CHnhZ/8I2eFgGT2qj/8M8ADFuZPCot8ILdHCfaiaGn/6Z/pgGi//DD8M3wx/DFva4b/yupo6Gn/7+j8AGRF7gAAAAAAAAAAAAAAAAhni2fA58jjyxi9EOeF/+S4/YAYfCFkZf/8IeeFn/wjZ4WAZPaqP/wzwAgFIFxQBCbi3xYJQFQH8+EFujhPtRNDT/9M/0wDRf/hh+Gb4Y/hi3tcN/5XU0dDT/9/R+ADIi9wAAAAAAAAAAAAAAAAQzxbPgc+Rx5YxeiHPC//JcfsAyIvcAAAAAAAAAAAAAAAAEM8Wz4HPklb4sEohzwv/yXH7ADD4QsjL//hDzws/+EbPCwDJ7VR/FgAE+GcActxwItDWAjHSADDcIccAkvI74CHXDR+S8jzhUxGS8jvhwQQighD////9vLGS8jzgAfAB+EdukvI83g==',
            signed.message,
        )

        # Create initially signed message
        signer = Signer.Keys(keys=self.keypair)
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi, signer=signer, deploy_set=deploy_set, call_set=call_set
        )
        signed = sync_core_client.abi.encode_message(params=encode_params)
        self.assertEqual(
            'te6ccgECGAEAA6wAA0eIAAt9aqvShfTon7Lei1PVOhUEkEEZQkhDKPgNyzeTL6YSEbAHAgEA4bE5Gr3mWwDtlcEOWHr6slWoyQlpIWeYyw/00eKFGFkbAJMMFLWnu0mq4HSrPmktmzeeAboa4kxkFymCsRVt44dTHxAj/Hd67jWQF7peccWoU/dbMCBJBB6YdPCVZcJlJkAAAF0ZyXLg19VzGRotV8/gAQHAAwIDzyAGBAEB3gUAA9AgAEHaY+IEf47vXcayAvdLzji1Cn7rZgQJIIPTDp4SrLhMpMwCJv8A9KQgIsABkvSg4YrtU1gw9KEKCAEK9KQg9KEJAAACASANCwHI/38h7UTQINdJwgGOENP/0z/TANF/+GH4Zvhj+GKOGPQFcAGAQPQO8r3XC//4YnD4Y3D4Zn/4YeLTAAGOHYECANcYIPkBAdMAAZTT/wMBkwL4QuIg+GX5EPKoldMAAfJ64tM/AQwAao4e+EMhuSCfMCD4I4ED6KiCCBt3QKC53pL4Y+CANPI02NMfAfgjvPK50x8B8AH4R26S8jzeAgEgEw4CASAQDwC9uotV8/+EFujjXtRNAg10nCAY4Q0//TP9MA0X/4Yfhm+GP4Yo4Y9AVwAYBA9A7yvdcL//hicPhjcPhmf/hh4t74RvJzcfhm0fgA+ELIy//4Q88LP/hGzwsAye1Uf/hngCASASEQDluIAGtb8ILdHCfaiaGn/6Z/pgGi//DD8M3wx/DFvfSDK6mjofSBv6PwikDdJGDhvfCFdeXAyfABkZP2CEGRnwoRnRoIEB9AAAAAAAAAAAAAAAAAAIGeLZMCAQH2AGHwhZGX//CHnhZ/8I2eFgGT2qj/8M8ADFuZPCot8ILdHCfaiaGn/6Z/pgGi//DD8M3wx/DFva4b/yupo6Gn/7+j8AGRF7gAAAAAAAAAAAAAAAAhni2fA58jjyxi9EOeF/+S4/YAYfCFkZf/8IeeFn/wjZ4WAZPaqP/wzwAgFIFxQBCbi3xYJQFQH8+EFujhPtRNDT/9M/0wDRf/hh+Gb4Y/hi3tcN/5XU0dDT/9/R+ADIi9wAAAAAAAAAAAAAAAAQzxbPgc+Rx5YxeiHPC//JcfsAyIvcAAAAAAAAAAAAAAAAEM8Wz4HPklb4sEohzwv/yXH7ADD4QsjL//hDzws/+EbPCwDJ7VR/FgAE+GcActxwItDWAjHSADDcIccAkvI74CHXDR+S8jzhUxGS8jvhwQQighD////9vLGS8jzgAfAB+EdukvI83g==',
            signed.message,
        )

        # Sign with signing box
        sbox = sync_core_client.crypto.get_signing_box(params=self.keypair)
        signer_sbox = Signer.SigningBox(handle=sbox.handle)
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi,
            signer=signer_sbox,
            deploy_set=deploy_set,
            call_set=call_set,
        )
        signed_sbox = sync_core_client.abi.encode_message(params=encode_params)
        sync_core_client.crypto.remove_signing_box(params=sbox)
        self.assertEqual(signed.message, signed_sbox.message)

        # Create run unsigned message
        address = '0:05beb555e942fa744fd96f45a9ea9d0a8248208ca12421947c06e59bc997d309'
        call_set = CallSet(
            function_name='returnValue',
            input={'id': '0'},
            header=FunctionHeader(
                **{
                    'pubkey': self.keypair.public,
                    'time': self.events_time,
                    'expire': self.events_expire,
                }
            ),
        )
        signer = Signer.External(public_key=self.keypair.public)
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi, signer=signer, address=address, call_set=call_set
        )
        unsigned = sync_core_client.abi.encode_message(params=encode_params)
        self.assertEqual(
            'te6ccgEBAgEAeAABpYgAC31qq9KF9Oifst6LU9U6FQSQQRlCSEMo+A3LN5MvphIFMfECP8d3ruNZAXul5xxahT91swIEkEHph08JVlwmUmQAAAXRnJcuDX1XMZBW+LBKAQBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=',
            unsigned.message,
        )
        self.assertEqual(
            'i4Hs3PB12QA9UBFbOIpkG3JerHHqjm4LgvF4MA7TDsY=', unsigned.data_to_sign
        )

        # Create detached signature
        sign_params = ParamsOfSign(unsigned=unsigned.data_to_sign, keys=self.keypair)
        signature = sync_core_client.crypto.sign(params=sign_params)
        self.assertEqual(
            '5bbfb7f184f2cb5f019400b9cd497eeaa41f3d5885619e9f7d4fab8dd695f4b3a02159a1422996c1dd7d1be67898bc79c6adba6c65a18101ac5f0a2a2bb8910b',
            signature.signature,
        )

        # Attach signature
        attach_params = ParamsOfAttachSignature(
            abi=self.events_abi,
            public_key=self.keypair.public,
            message=unsigned.message,
            signature=signature.signature,
        )
        signed = sync_core_client.abi.attach_signature(params=attach_params)
        self.assertEqual(
            'te6ccgEBAwEAvAABRYgAC31qq9KF9Oifst6LU9U6FQSQQRlCSEMo+A3LN5MvphIMAQHhrd/b+MJ5Za+AygBc5qS/dVIPnqxCsM9PvqfVxutK+lnQEKzQoRTLYO6+jfM8TF4841bdNjLQwIDWL4UVFdxIhdMfECP8d3ruNZAXul5xxahT91swIEkEHph08JVlwmUmQAAAXRnJcuDX1XMZBW+LBKACAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==',
            signed.message,
        )

        # Get signature data
        data_params = ParamsOfGetSignatureData(
            abi=self.events_abi, message=signed.message
        )
        data = sync_core_client.abi.get_signature_data(params=data_params)
        self.assertEqual(unsigned.data_to_sign, data.unsigned)
        self.assertEqual(signature.signature, data.signature)

        # Create initially signed message
        signer = Signer.Keys(keys=self.keypair)
        encode_params = ParamsOfEncodeMessage(
            abi=self.events_abi, signer=signer, address=address, call_set=call_set
        )
        signed = sync_core_client.abi.encode_message(params=encode_params)
        self.assertEqual(
            'te6ccgEBAwEAvAABRYgAC31qq9KF9Oifst6LU9U6FQSQQRlCSEMo+A3LN5MvphIMAQHhrd/b+MJ5Za+AygBc5qS/dVIPnqxCsM9PvqfVxutK+lnQEKzQoRTLYO6+jfM8TF4841bdNjLQwIDWL4UVFdxIhdMfECP8d3ruNZAXul5xxahT91swIEkEHph08JVlwmUmQAAAXRnJcuDX1XMZBW+LBKACAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==',
            signed.message,
        )

    def test_encode_message_body(self):
        header = FunctionHeader(
            expire=self.events_expire, time=self.events_time, pubkey=self.keypair.public
        )
        call_set = CallSet(
            function_name='returnValue', header=header, input={'id': '0'}
        )
        signer = Signer.Keys(keys=self.keypair)
        params = ParamsOfEncodeMessageBody(
            abi=self.events_abi, call_set=call_set, is_internal=False, signer=signer
        )
        encoded = sync_core_client.abi.encode_message_body(params=params)

        self.assertIsNone(encoded.data_to_sign)

    def test_encode_account(self):
        # Encode account from encoded deploy message
        encoded_deploy_message = 'te6ccgECFwEAA2gAAqeIAAt9aqvShfTon7Lei1PVOhUEkEEZQkhDKPgNyzeTL6YSEZTHxAj/Hd67jWQF7peccWoU/dbMCBJBB6YdPCVZcJlJkAAAF0ZyXLg19VzGRotV8/gGAQEBwAICA88gBQMBAd4EAAPQIABB2mPiBH+O713GsgL3S844tQp+62YECSCD0w6eEqy4TKTMAib/APSkICLAAZL0oOGK7VNYMPShCQcBCvSkIPShCAAAAgEgDAoByP9/Ie1E0CDXScIBjhDT/9M/0wDRf/hh+Gb4Y/hijhj0BXABgED0DvK91wv/+GJw+GNw+GZ/+GHi0wABjh2BAgDXGCD5AQHTAAGU0/8DAZMC+ELiIPhl+RDyqJXTAAHyeuLTPwELAGqOHvhDIbkgnzAg+COBA+iogggbd0Cgud6S+GPggDTyNNjTHwH4I7zyudMfAfAB+EdukvI83gIBIBINAgEgDw4AvbqLVfP/hBbo417UTQINdJwgGOENP/0z/TANF/+GH4Zvhj+GKOGPQFcAGAQPQO8r3XC//4YnD4Y3D4Zn/4YeLe+Ebyc3H4ZtH4APhCyMv/+EPPCz/4Rs8LAMntVH/4Z4AgEgERAA5biABrW/CC3Rwn2omhp/+mf6YBov/ww/DN8Mfwxb30gyupo6H0gb+j8IpA3SRg4b3whXXlwMnwAZGT9ghBkZ8KEZ0aCBAfQAAAAAAAAAAAAAAAAACBni2TAgEB9gBh8IWRl//wh54Wf/CNnhYBk9qo//DPAAxbmTwqLfCC3Rwn2omhp/+mf6YBov/ww/DN8Mfwxb2uG/8rqaOhp/+/o/ABkRe4AAAAAAAAAAAAAAAAIZ4tnwOfI48sYvRDnhf/kuP2AGHwhZGX//CHnhZ/8I2eFgGT2qj/8M8AIBSBYTAQm4t8WCUBQB/PhBbo4T7UTQ0//TP9MA0X/4Yfhm+GP4Yt7XDf+V1NHQ0//f0fgAyIvcAAAAAAAAAAAAAAAAEM8Wz4HPkceWMXohzwv/yXH7AMiL3AAAAAAAAAAAAAAAABDPFs+Bz5JW+LBKIc8L/8lx+wAw+ELIy//4Q88LP/hGzwsAye1UfxUABPhnAHLccCLQ1gIx0gAw3CHHAJLyO+Ah1w0fkvI84VMRkvI74cEEIoIQ/////byxkvI84AHwAfhHbpLyPN4='
        message_source = MessageSource.Encoded(
            message=encoded_deploy_message, abi=self.events_abi
        )
        state_init_source = StateInitSource.Message(source=message_source)

        encode_params = ParamsOfEncodeAccount(state_init=state_init_source)
        encoded = sync_core_client.abi.encode_account(params=encode_params)
        self.assertEqual(
            '05beb555e942fa744fd96f45a9ea9d0a8248208ca12421947c06e59bc997d309',
            encoded.id,
        )

        # Encode account from encoding params
        deploy_set = DeploySet(tvc=self.events_tvc)
        call_set = CallSet(
            function_name='constructor',
            header=FunctionHeader(
                **{
                    'pubkey': self.keypair.public,
                    'time': self.events_time,
                    'expire': self.events_expire,
                }
            ),
        )
        signer = Signer.Keys(keys=self.keypair)
        encoding_params = ParamsOfEncodeMessage(
            abi=self.events_abi, signer=signer, deploy_set=deploy_set, call_set=call_set
        )
        message_source = MessageSource.EncodingParams(params=encoding_params)
        state_init_source = StateInitSource.Message(source=message_source)
        encode_params = ParamsOfEncodeAccount(state_init=state_init_source)
        encoded = sync_core_client.abi.encode_account(params=encode_params)
        self.assertEqual(
            '05beb555e942fa744fd96f45a9ea9d0a8248208ca12421947c06e59bc997d309',
            encoded.id,
        )

        # Test exception (external signer)
        with self.assertRaises(TonException):
            signer = Signer.External(public_key=self.keypair.public)
            encoding_params = ParamsOfEncodeMessage(
                abi=self.events_abi,
                signer=signer,
                deploy_set=deploy_set,
                call_set=call_set,
            )
            message_source = MessageSource.EncodingParams(params=encoding_params)
            state_init_source = StateInitSource.Message(source=message_source)
            encode_params = ParamsOfEncodeAccount(state_init=state_init_source)
            sync_core_client.abi.encode_account(params=encode_params)

        # Encode account from TVC
        state_init_source = StateInitSource.Tvc(tvc=self.events_tvc)
        encode_params = ParamsOfEncodeAccount(state_init=state_init_source)
        encoded = sync_core_client.abi.encode_account(params=encode_params)
        self.assertNotEqual(
            '05beb555e942fa744fd96f45a9ea9d0a8248208ca12421947c06e59bc997d309',
            encoded.id,
        )

        state_init_source = StateInitSource.Tvc(
            tvc=self.events_tvc, public_key=self.keypair.public
        )
        encode_params = ParamsOfEncodeAccount(state_init=state_init_source)
        encoded = sync_core_client.abi.encode_account(params=encode_params)
        self.assertEqual(
            '05beb555e942fa744fd96f45a9ea9d0a8248208ca12421947c06e59bc997d309',
            encoded.id,
        )

    def test_encode_internal_message_deploy(self):
        abi = Abi.from_path(path=os.path.join(SAMPLES_DIR, 'Hello.abi.json'))
        with open(os.path.join(SAMPLES_DIR, 'Hello.tvc'), 'rb') as fp:
            tvc = base64.b64encode(fp.read()).decode()

        result = sync_core_client.abi.encode_internal_message(
            params=ParamsOfEncodeInternalMessage(
                abi=abi,
                value='0',
                deploy_set=DeploySet(tvc=tvc),
                call_set=CallSet(function_name='constructor'),
            )
        )
        self.assertEqual(
            'te6ccgECHAEABG0AAmliADYO5IoxskLmUfURre2fOB04OmP32VjPwA/lDM/Cpvh8AAAAAAAAAAAAAAAAAAIxotV8/gYBAQHAAgIDzyAFAwEB3gQAA9AgAEHYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQCJv8A9KQgIsABkvSg4YrtU1gw9KEJBwEK9KQg9KEIAAACASAMCgHo/38h0wABjiaBAgDXGCD5AQFw7UTQ9AWAQPQO8orXC/8B7Ucib3XtVwMB+RDyqN7tRNAg10nCAY4W9ATTP9MA7UcBb3EBb3YBb3MBb3LtV44Y9AXtRwFvcnBvc3BvdsiAIM9AydBvce1X4tM/Ae1HbxMhuSALAGCfMCD4I4ED6KiCCBt3QKC53pntRyFvUyDtVzCUgDTy8OIw0x8B+CO88rnTHwHxQAECASAYDQIBIBEOAQm6i1Xz+A8B+u1Hb2FujjvtRNAg10nCAY4W9ATTP9MA7UcBb3EBb3YBb3MBb3LtV44Y9AXtRwFvcnBvc3BvdsiAIM9AydBvce1X4t7tR28WkvIzl+1HcW9W7VfiAPgA0fgjtR/tRyBvETAByMsfydBvUe1X7UdvEsj0AO1HbxPPCz/tR28WEAAczwsA7UdvEc8Wye1UcGoCAWoVEgEJtAAa1sATAfztR29hbo477UTQINdJwgGOFvQE0z/TAO1HAW9xAW92AW9zAW9y7VeOGPQF7UcBb3Jwb3Nwb3bIgCDPQMnQb3HtV+Le7UdvZSBukjBw3nDtR28SgED0DvKK1wv/uvLgZPgA+kDRIMjJ+wSBA+hwgQCAyHHPCwEizwoAcc9A+CgUAI7PFiTPFiP6AnHPQHD6AnD6AoBAz0D4I88LH3LPQCDJIvsAXwUw7UdvEsj0AO1HbxPPCz/tR28WzwsA7UdvEc8Wye1UcGrbMAEJtGX2i8AWAfjtR29hbo477UTQINdJwgGOFvQE0z/TAO1HAW9xAW92AW9zAW9y7VeOGPQF7UcBb3Jwb3Nwb3bIgCDPQMnQb3HtV+Le0e1HbxHXCx/IghBQy+0XghCAAAAAsc8LHyHPCx/Ic88LAfgozxZyz0D4Jc8LP4Ahz0AgzzUizzG8FwB4lnHPQCHPF5Vxz0EhzeIgyXH7AFshwP+OHu1HbxLI9ADtR28Tzws/7UdvFs8LAO1HbxHPFsntVN5xatswAgEgGxkBCbtzEuRYGgD47UdvYW6OO+1E0CDXScIBjhb0BNM/0wDtRwFvcQFvdgFvcwFvcu1Xjhj0Be1HAW9ycG9zcG92yIAgz0DJ0G9x7Vfi3vgA0fgjtR/tRyBvETAByMsfydBvUe1X7UdvEsj0AO1HbxPPCz/tR28WzwsA7UdvEc8Wye1UcGrbMADK3XAh10kgwSCOKyDAAI4cI9Bz1yHXCwAgwAGW2zBfB9swltswXwfbMOME2ZbbMF8G2zDjBNngItMfNCB0uyCOFTAgghD/////uiCZMCCCEP////6639+W2zBfB9sw4CMh8UABXwc=',
            result.message,
        )

        boc_hash = sync_core_client.boc.get_boc_hash(
            params=ParamsOfGetBocHash(boc=result.message)
        )
        self.assertEqual(result.message_id, boc_hash.hash)

        parsed = sync_core_client.boc.parse_message(
            params=ParamsOfParse(boc=result.message)
        )
        code = sync_core_client.boc.get_code_from_tvc(
            params=ParamsOfGetCodeFromTvc(tvc=tvc)
        )
        self.assertEqual(code.code, parsed.parsed['code'])

    def test_decode_account_data(self):
        data = 'te6ccgEBBwEA8AAEWeix2Dmr4nsqu51KKUOpFDqcfirgZ5m9JN7B16iJGuXdAAABeqRZIJYAAAAW4AYEAwEBQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPAgAAABRJIGxpa2UgaXQuAcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIFAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKSGVsbG8='
        abi = Abi.Json(
            value='{"ABI version":2,"version":"2.1","header":["time"],"functions":[],"data":[],"events":[],"fields":[{"name":"__pubkey","type":"uint256"},{"name":"__timestamp","type":"uint64"},{"name":"fun","type":"uint32"},{"name":"opt","type":"optional(bytes)"},{"name":"big","type":"optional(tuple)","components":[{"name":"value0","type":"uint256"},{"name":"value1","type":"uint256"},{"name":"value2","type":"uint256"},{"name":"value3","type":"uint256"}]},{"name":"a","type":"bytes"},{"name":"b","type":"bytes"},{"name":"length","type":"uint256"}]}'
        )

        params = ParamsOfDecodeAccountData(abi=abi, data=data)
        decoded = sync_core_client.abi.decode_account_data(params=params)
        self.assertEqual(
            '0xe8b1d839abe27b2abb9d4a2943a9143a9c7e2ae06799bd24dec1d7a8891ae5dd',
            decoded.data['__pubkey'],
        )

    def test_decode_update_initial_data(self):
        # Get contract abi, tvc
        abi = Abi.from_path(path=os.path.join(SAMPLES_DIR, 't24_initdata.abi.json'))
        with open(os.path.join(SAMPLES_DIR, 't24_initdata.tvc'), 'rb') as fp:
            tvc = base64.b64encode(fp.read()).decode()

        # Get and decode contract initial data
        params = ParamsOfDecodeStateInit(state_init=tvc)
        data = sync_core_client.boc.decode_state_init(params).data
        params = ParamsOfDecodeInitialData(data=data, abi=abi)
        decoded = sync_core_client.abi.decode_initial_data(params)
        self.assertEqual('00' * 32, decoded.initial_pubkey)
        self.assertEqual({}, decoded.initial_data)

        # Encode initial data
        initial_data = {'a': 123, 's': 'some string'}
        initial_pubkey = '22' * 32
        encoded_initial_data = 'te6ccgEBBwEARwABAcABAgPPoAQCAQFIAwAWc29tZSBzdHJpbmcCASAGBQADHuAAQQiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIoA=='
        params = ParamsOfEncodeInitialData(
            abi=abi, initial_data=initial_data, initial_pubkey=initial_pubkey
        )
        encoded = sync_core_client.abi.encode_initial_data(params)
        self.assertEqual(encoded_initial_data, encoded.data)

        # Update initial data
        params = ParamsOfUpdateInitialData(
            data=data, abi=abi, initial_data=initial_data, initial_pubkey=initial_pubkey
        )
        data_updated = sync_core_client.abi.update_initial_data(params).data
        self.assertEqual(encoded_initial_data, data_updated)

        # Decode updated data
        params = ParamsOfDecodeInitialData(data=data_updated, abi=abi)
        decoded = sync_core_client.abi.decode_initial_data(params)
        self.assertEqual(initial_data['a'], int(decoded.initial_data['a']))
        self.assertEqual(initial_data['s'], decoded.initial_data['s'])
        self.assertEqual(initial_pubkey, decoded.initial_pubkey)

    def test_decode_boc(self):
        boc = 'te6ccgEBAgEAEgABCQAAAADAAQAQAAAAAAAAAHs='
        p = [
            AbiParam(name='a', type='uint32'),
            AbiParam(name='b', type='ref(int64)'),
            AbiParam(name='c', type='bool'),
        ]
        params = ParamsOfDecodeBoc(params=p, boc=boc, allow_partial=True)
        decoded = sync_core_client.abi.decode_boc(params)
        self.assertEqual({'a': '0', 'b': '123', 'c': True}, decoded.data)

        params.params.pop()
        decoded = sync_core_client.abi.decode_boc(params)
        self.assertEqual({'a': '0', 'b': '123'}, decoded.data)

    def test_encode_boc(self):
        _params = [
            AbiParam(name='dest', type='address'),
            AbiParam(name='value', type='uint128'),
            AbiParam(name='bounce', type='bool'),
        ]
        _data = {
            'dest': '-1:3333333333333333333333333333333333333333333333333333333333333333',
            'value': 1234567,
            'bounce': True,
        }
        params = ParamsOfAbiEncodeBoc(params=_params, data=_data)
        encoded = sync_core_client.abi.encode_boc(params)
        self.assertEqual(
            'te6ccgEBAQEANAAAY5/mZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmZmAAAAAAAAAAAAAAAAACWtD4',
            encoded.boc,
        )

    def test_calc_function_id(self):
        abi = Abi.from_path(path=os.path.join(SAMPLES_DIR, 'Giver-v2.abi.json'))
        params = ParamsOfCalcFunctionId(abi=abi, function_name='getMessages')
        result = sync_core_client.abi.calc_function_id(params)
        self.assertEqual('0x7744c7e2', hex(result.function_id))

        params = ParamsOfCalcFunctionId(
            abi=abi, function_name='getMessages', output=True
        )
        result = sync_core_client.abi.calc_function_id(params)
        self.assertEqual('0xf744c7e2', hex(result.function_id))

    def test_decode_responsible(self):
        body = 'te6ccgEBAgEAsQAB0IAAAAAAAABnAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABDnTBYAAAAAAAAAAAAAAAAAO5rKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAQCHAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGAD9YhN79S7hQOnrVCizdlF32dvf9Wk8XgGP1lsYvH/14AYHg='
        abi = Abi.from_path(path=os.path.join(SAMPLES_DIR, 'PriceXchg.abi.json'))
        params = ParamsOfDecodeMessageBody(
            abi=abi,
            body=body,
            function_name='onTip3LendOwnership',
            data_layout=DataLayout.OUTPUT,
            is_internal=True,
        )
        result = sync_core_client.abi.decode_message_body(params)
        self.assertEqual(103, int(result.value['err_code']))
        self.assertEqual(
            '0:7eb109bdfa9770a074f5aa1459bb28bbecedeffab49e2f00c7eb2d8c5e3ffaf0',
            result.value['pair'],
        )
        self.assertTrue(result.value['sell'])
