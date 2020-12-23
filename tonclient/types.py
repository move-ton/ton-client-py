import json
from enum import Enum
from io import StringIO
from typing import Dict, Union, Any, List


class BaseTypedType(object):
    """
    Base class for objects which should be sent as dict {'type': '', ...}.
    E.g. `Abi`, `Signer`, `MessageSource`, etc.
    """
    def __init__(self, type: str):
        """
        :param type:
        """
        self.type = type

    @property
    def dict(self):
        return {'type': self.type}


# CLIENT module
class ClientError(object):
    def __init__(self, code: int, message: str, data: Any):
        """
        :param code:
        :param message:
        :param data:
        """
        self.code = code
        self.message = message
        self.data = data

    def __str__(self):
        return f'[{self.code}] {self.message} (Data: {self.data})'


class ClientConfig(object):
    def __init__(
            self, network: 'NetworkConfig' = None,
            crypto: 'CryptoConfig' = None, abi: 'AbiConfig' = None):
        """
        :param network:
        :param crypto:
        :param abi:
        """
        network = network or NetworkConfig(server_address='http://localhost')
        self.network = network
        self.crypto = crypto or CryptoConfig()
        self.abi = abi or AbiConfig()

    @property
    def dict(self):
        return {
            'network': self.network.dict,
            'crypto': self.crypto.dict,
            'abi': self.abi.dict
        }


class NetworkConfig(object):
    def __init__(
            self, server_address: str, network_retries_count: int = None,
            message_retries_count: int = None,
            message_processing_timeout: int = None,
            wait_for_timeout: int = None, out_of_sync_threshold: int = None,
            access_key: str = None):
        """
        :param server_address:
        :param network_retries_count:
        :param message_retries_count:
        :param message_processing_timeout:
        :param wait_for_timeout:
        :param out_of_sync_threshold:
        :param access_key:
        """
        self.server_address = server_address
        self.network_retries_count = network_retries_count
        self.message_retries_count = message_retries_count
        self.message_processing_timeout = message_processing_timeout
        self.wait_for_timeout = wait_for_timeout
        self.out_of_sync_threshold = out_of_sync_threshold
        self.access_key = access_key

    @property
    def dict(self):
        return {
            'server_address': self.server_address,
            'network_retries_count': self.network_retries_count,
            'message_retries_count': self.message_retries_count,
            'message_processing_timeout': self.message_processing_timeout,
            'wait_for_timeout': self.wait_for_timeout,
            'out_of_sync_threshold': self.out_of_sync_threshold,
            'access_key': self.access_key
        }


class CryptoConfig(object):
    def __init__(
            self, mnemonic_dictionary: int = None,
            mnemonic_word_count: int = None,
            hdkey_derivation_path: str = None):
        """
        :param mnemonic_dictionary:
        :param mnemonic_word_count:
        :param hdkey_derivation_path:
        """
        self.mnemonic_dictionary = mnemonic_dictionary
        self.mnemonic_word_count = mnemonic_word_count
        self.hdkey_derivation_path = hdkey_derivation_path

    @property
    def dict(self):
        return {
            'mnemonic_dictionary': self.mnemonic_dictionary,
            'mnemonic_word_count': self.mnemonic_word_count,
            'hdkey_derivation_path': self.hdkey_derivation_path
        }


class AbiConfig(object):
    def __init__(
            self, workchain: int = None,
            message_expiration_timeout: int = None,
            message_expiration_timeout_grow_factor: Union[int, float] = None):
        """
        :param workchain:
        :param message_expiration_timeout:
        :param message_expiration_timeout_grow_factor:
        """
        self.workchain = workchain
        self.message_expiration_timeout = message_expiration_timeout
        self.message_expiration_timeout_grow_factor = \
            message_expiration_timeout_grow_factor

    @property
    def dict(self):
        return {
            'workchain': self.workchain,
            'message_expiration_timeout': self.message_expiration_timeout,
            'message_expiration_timeout_grow_factor':
                self.message_expiration_timeout_grow_factor
        }


class BuildInfoDependency(object):
    def __init__(self, name: str, git_commit: str):
        """
        :param name: Dependency name. Usually it is a crate name
        :param git_commit: Git commit hash of the related repository
        """
        self.name = name
        self.git_commit = git_commit


class ParamsOfAppRequest(object):
    def __init__(self, app_request_id: int, request_data: Any):
        """
        :param app_request_id: Request ID. Should be used in
                `resolve_app_request` call
        :param request_data: Request describing data
        """
        self.app_request_id = app_request_id
        self.request_data = request_data


class AppRequestResult:
    class Error(object):
        """ Error occurred during request processing """
        def __init__(self, text: str):
            """
            :param text: Error description
            """
            self.text = text

        @property
        def dict(self):
            return {'type': 'Error', 'text': self.text}

    class Ok(object):
        """ Request processed successfully """
        def __init__(self, result: Any):
            """
            :param result: Request processing result
            """
            self.result = result

        @property
        def dict(self):
            return {'type': 'Ok', 'result': self.result}


class ResultOfGetApiReference(object):
    def __init__(self, api: Any):
        """
        :param api: API
        """
        self.api = api


class ResultOfVersion(object):
    def __init__(self, version: str):
        """
        :param version: Core Library version
        """
        self.version = version


class ResultOfBuildInfo(object):
    def __init__(
            self, build_number: int,
            dependencies: List['BuildInfoDependency']):
        """
        :param build_number: Build number assigned to this build by the CI
        :param dependencies: Fingerprint of the most important dependencies
        """
        self.build_number = build_number
        self.dependencies = dependencies

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ResultOfBuildInfo':
        if data['dependencies']:
            data['dependencies'] = [
                BuildInfoDependency(**d) for d in data['dependencies']
            ]

        return ResultOfBuildInfo(**data)


class ParamsOfResolveAppRequest(object):
    def __init__(self, app_request_id: int, result: 'AppRequestResultType'):
        """
        :param app_request_id: Request ID received from SDK
        :param result: Result of request processing
        """
        self.app_request_id = app_request_id
        self.result = result

    @property
    def dict(self):
        return {
            'app_request_id': self.app_request_id,
            'result': self.result.dict
        }


# ABI module
AbiHandle = int


class Abi:
    class Contract(BaseTypedType):
        def __init__(self, value: 'AbiContract', type: str = 'Contract'):
            """
            :param value:
            :param type:
            """
            super(Abi.Contract, self).__init__(type=type)
            self.value = value

        @property
        def dict(self):
            return {**super(Abi.Contract, self).dict, 'value': self.value.dict}

    class Json(BaseTypedType):
        def __init__(self, value: str, type: str = 'Json'):
            """
            :param value:
            :param type:
            """
            super(Abi.Json, self).__init__(type=type)
            self.value = value

        @property
        def dict(self):
            return {**super(Abi.Json, self).dict, 'value': self.value}

    class Handle(BaseTypedType):
        def __init__(self, value: 'AbiHandle', type: str = 'Handle'):
            """
            :param value:
            :param type:
            """
            super(Abi.Handle, self).__init__(type=type)
            self.value = value

        @property
        def dict(self):
            return {**super(Abi.Handle, self).dict, 'value': self.value}

    class Serialized(BaseTypedType):
        def __init__(self, value: 'AbiContract', type: str = 'Contract'):
            """
            :param value:
            :param type:
            """
            super(Abi.Serialized, self).__init__(type=type)
            self.value = value

        @property
        def dict(self):
            return {
                **super(Abi.Serialized, self).dict,
                'value': self.value.dict
            }

    @staticmethod
    def from_path(path: str) -> Json:
        with open(path) as fp:
            return Abi.Json(value=fp.read())


class AbiContract(object):
    def __init__(
            self, abi_version: int = None, header: List[str] = None,
            functions: List['AbiFunction'] = None,
            events: List['AbiEvent'] = None, data: List['AbiData'] = None):
        """
        :param abi_version:
        :param header:
        :param functions:
        :param events:
        :param data:
        """
        self.abi_version = abi_version
        self.header = header or []
        self.functions = functions or []
        self.events = events or []
        self.data = data or []

    @property
    def dict(self):
        return {
            'abi_version': self.abi_version,
            'header': self.header,
            'functions': [f.dict for f in self.functions],
            'events': [e.dict for e in self.events],
            'data': [d.dict for d in self.data]
        }


class AbiFunction(object):
    def __init__(
            self, name: str, inputs: List['AbiParam'],
            outputs: List['AbiParam'], id: str = None):
        """
        :param name:
        :param inputs:
        :param outputs:
        :param id:
        """
        self.name = name
        self.inputs = inputs
        self.outputs = outputs
        self.id = id

    @property
    def dict(self):
        return {
            'name': self.name,
            'inputs': [i.dict for i in self.inputs],
            'outputs': [o.dict for o in self.outputs],
            'id': self.id
        }


class AbiEvent(object):
    def __init__(self, name: str, inputs: List['AbiParam'], id: str = None):
        """
        :param name:
        :param inputs:
        :param id:
        """
        self.name = name
        self.inputs = inputs
        self.id = id

    @property
    def dict(self):
        return {
            'name': self.name,
            'inputs': [i.dict for i in self.inputs],
            'id': self.id
        }


class AbiData(object):
    def __init__(
            self, key: int, name: str, type: str,
            components: List['AbiParam'] = None):
        """
        :param key:
        :param name:
        :param type:
        :param components:
        """
        self.key = key
        self.name = name
        self.type = type
        self.components = components

    @property
    def dict(self):
        return {
            'key': self.key,
            'name': self.name,
            'type': self.type,
            'components': [c.dict for c in self.components]
        }


class AbiParam(object):
    def __init__(
            self, name: str, type: str, components: List['AbiParam'] = None):
        """
        :param name:
        :param type:
        :param components:
        """
        self.name = name
        self.type = type
        self.components = components or []

    @property
    def dict(self):
        return {
            'name': self.name,
            'type': self.type,
            'components': [c.dict for c in self.components]
        }


class FunctionHeader(object):
    """
    The ABI function header.
    Includes several hidden function parameters that contract uses for
    security, message delivery monitoring and replay protection reasons.
    The actual set of header fields depends on the contract's ABI.
    If a contract's ABI does not include some headers, then they are
    not filled.
    """
    def __init__(
            self, expire: int = None, time: int = None, pubkey: str = None):
        """
        :param expire: Message expiration time in seconds. If not specified -
                calculated automatically from `message_expiration_timeout()`,
                `try_index` and `message_expiration_timeout_grow_factor()`
                (if ABI includes expire header)
        :param time: Message creation time in milliseconds. If not specified,
                now is used (if ABI includes time header)
        :param pubkey: Public key is used by the contract to check the
                signature. Encoded in `hex`. If not specified, method fails
                with exception (if ABI includes pubkey header)
        """
        self.expire = expire
        self.time = time
        self.pubkey = pubkey

    @property
    def dict(self):
        return {
            'expire': self.expire,
            'time': self.time,
            'pubkey': self.pubkey
        }


class CallSet(object):
    def __init__(
            self, function_name: str, header: 'FunctionHeader' = None,
            input: Any = None):
        """
        :param function_name: Function name that is being called
        :param header: Function header. If an application omits some header
                parameters required by the contract's ABI, the library will
                set the default values for them
        :param input: Function input parameters according to ABI
        """
        self.function_name = function_name
        self.header = header or FunctionHeader()
        self.input = input

    @property
    def dict(self):
        return {
            'function_name': self.function_name,
            'header': self.header.dict,
            'input': self.input
        }


class DeploySet(object):
    def __init__(
            self, tvc: str, workchain_id: int = None,
            initial_data: List[Dict[str, Any]] = None):
        """
        :param tvc: Content of TVC file encoded in `base64`
        :param workchain_id: Target workchain for destination address.
                Default is 0
        :param initial_data: List of initial values for contract's public
                variables
        """
        self.tvc = tvc
        self.workchain_id = workchain_id
        self.initial_data = initial_data

    @property
    def dict(self):
        return {
            'tvc': self.tvc,
            'workchain_id': self.workchain_id,
            'initial_data': self.initial_data
        }


class Signer:
    class NoSigner(BaseTypedType):
        """ No keys are provided. Creates an unsigned message """
        def __init__(self, type: str = 'None'):
            """
            :param type:
            """
            super(Signer.NoSigner, self).__init__(type=type)

    class External(BaseTypedType):
        """
        Only public key is provided in unprefixed hex string format to
        generate unsigned message and data_to_sign which can be signed later
        """
        def __init__(self, public_key: str, type: str = 'External'):
            """
            :param public_key:
            :param type:
            """
            super(Signer.External, self).__init__(type=type)
            self.public_key = public_key

        @property
        def dict(self):
            return {
                **super(Signer.External, self).dict,
                'public_key': self.public_key
            }

    class Keys(BaseTypedType):
        """ Key pair is provided for signing """
        def __init__(self, keys: 'KeyPair', type: str = 'Keys'):
            """
            :param keys:
            :param type:
            """
            super(Signer.Keys, self).__init__(type=type)
            self.keys = keys

        @property
        def dict(self):
            return {**super(Signer.Keys, self).dict, 'keys': self.keys.dict}

    class SigningBox(BaseTypedType):
        """
        Signing Box interface is provided for signing, allows DApps to sign
        messages using external APIs, such as HSM, cold wallet, etc.
        """
        def __init__(
                self, handle: 'SigningBoxHandle', type: str = 'SigningBox'):
            """
            :param handle:
            :param type:
            """
            super(Signer.SigningBox, self).__init__(type=type)
            self.handle = handle

        @property
        def dict(self):
            return {
                **super(Signer.SigningBox, self).dict,
                'handle': self.handle
            }


class MessageBodyType(str, Enum):
    # Message contains the input of the ABI function
    INPUT = 'Input'
    # Message contains the output of the ABI function
    OUTPUT = 'Output'
    # Message contains the input of the imported ABI function.
    # Occurs when contract sends an internal message to other
    # contract
    INTERNAL_OUTPUT = 'InternalOutput'
    # Message contains the input of the ABI event
    EVENT = 'Event'


class StateInitSource:
    class Message(BaseTypedType):
        """ Deploy message """
        def __init__(self, source: 'MessageSourceType', type: str = 'Message'):
            """
            :param source:
            :param type:
            """
            super(StateInitSource.Message, self).__init__(type=type)
            self.source = source

        @property
        def dict(self):
            return {
                **super(StateInitSource.Message, self).dict,
                'source': self.source.dict
            }

    class StateInit(BaseTypedType):
        """ State init data """
        def __init__(
                self, code: str, data: str, library: str = None,
                type: str = 'StateInit'):
            """
            :param code: Code BOC. Encoded in `base64`
            :param data: Data BOC. Encoded in `base64`
            :param library: Library BOC. Encoded in `base64`
            :param type:
            """
            super(StateInitSource.StateInit, self).__init__(type=type)
            self.code = code
            self.data = data
            self.library = library

        @property
        def dict(self):
            return {
                **super(StateInitSource.StateInit, self).dict,
                'code': self.code,
                'data': self.data,
                'library': self.library
            }

    class Tvc(BaseTypedType):
        """ Content of the TVC file """
        def __init__(
                self, tvc: str, public_key: str = None,
                init_params: 'StateInitParams' = None, type: str = 'Tvc'):
            """
            :param tvc: Content of the TVC file. Encoded in `base64`
            :param public_key:
            :param init_params:
            :param type:
            """
            super(StateInitSource.Tvc, self).__init__(type=type)
            self.tvc = tvc
            self.public_key = public_key
            self.init_params = init_params

        @property
        def dict(self):
            init_params = self.init_params.dict \
                if self.init_params else self.init_params

            return {
                **super(StateInitSource.Tvc, self).dict,
                'tvc': self.tvc,
                'public_key': self.public_key,
                'init_params': init_params
            }


class StateInitParams(object):
    def __init__(self, abi: 'AbiType', value: Any):
        """
        :param abi: One of Abi.*
        :param value:
        """
        self.abi = abi
        self.value = value

    @property
    def dict(self):
        return {'abi': self.abi.dict, 'value': self.value}


class MessageSource:
    class Encoded(BaseTypedType):
        def __init__(
                self, message: str, abi: 'AbiType' = None,
                type: str = 'Encoded'):
            """
            :param message:
            :param abi:
            :param type:
            """
            super(MessageSource.Encoded, self).__init__(type=type)
            self.message = message
            self.abi = abi

        @property
        def dict(self):
            return {
                **super(MessageSource.Encoded, self).dict,
                'message': self.message,
                'abi': self.abi.dict if self.abi else self.abi
            }

    class EncodingParams(BaseTypedType):
        def __init__(
                self, params: 'ParamsOfEncodeMessage',
                type: str = 'EncodingParams'):
            """
            :param params:
            :param type:
            """
            super(MessageSource.EncodingParams, self).__init__(type=type)
            self.params = params

        @property
        def dict(self):
            return {
                **super(MessageSource.EncodingParams, self).dict,
                **self.params.dict
            }


class ParamsOfEncodeMessageBody(object):
    def __init__(
            self, abi: 'AbiType', call_set: 'CallSet', is_internal: bool,
            signer: 'SignerType', processing_try_index: int = None):
        """
        :param abi: Contract ABI
        :param call_set: Function call parameters. Must be specified in non
                deploy message. In case of deploy message contains parameters
                of constructor
        :param is_internal: True if internal message body must be encoded
        :param signer: Signing parameters
        :param processing_try_index: Processing try index. Used in message
                processing with retries. Encoder uses the provided try index
                to calculate message expiration time. Expiration timeouts will
                grow with every retry. Default value is 0
        """
        self.abi = abi
        self.call_set = call_set
        self.is_internal = is_internal
        self.signer = signer
        self.processing_try_index = processing_try_index

    @property
    def dict(self):
        return {
            'abi': self.abi.dict,
            'call_set': self.call_set.dict,
            'is_internal': self.is_internal,
            'signer': self.signer.dict,
            'processing_try_index': self.processing_try_index
        }


class ResultOfEncodeMessageBody(object):
    def __init__(self, body: str, data_to_sign: str = None):
        """
        :param body: Message body BOC encoded with `base64`
        :param data_to_sign: Optional data to sign. Encoded with `base64`.
                Presents when message is unsigned. Can be used for external
                message signing. Is this case you need to sing this data and
                produce signed message using `abi.attach_signature`
        """
        self.body = body
        self.data_to_sign = data_to_sign


class ParamsOfAttachSignatureToMessageBody(object):
    def __init__(
            self, abi: 'AbiType', public_key: str, message: str,
            signature: str):
        """
        :param abi: Contract ABI
        :param public_key: Public key. Must be encoded with `hex`
        :param message: Unsigned message body BOC. Must be encoded
                with `base64`
        :param signature: Signature. Must be encoded with `hex`
        """
        self.abi = abi
        self.public_key = public_key
        self.message = message
        self.signature = signature

    @property
    def dict(self):
        return {
            'abi': self.abi.dict,
            'public_key': self.public_key,
            'message': self.message,
            'signature': self.signature
        }


class ResultOfAttachSignatureToMessageBody(object):
    def __init__(self, body: str):
        """
        :param body:
        """
        self.body = body


class ParamsOfEncodeMessage(object):
    def __init__(
            self, abi: 'AbiType', signer: 'SignerType', address: str = None,
            deploy_set: 'DeploySet' = None, call_set: 'CallSet' = None,
            processing_try_index: int = None):
        """
        :param abi: Contract ABI
        :param signer: Signing parameters
        :param address: Target address the message will be sent to. Must be
                specified in case of non-deploy message
        :param deploy_set: Deploy parameters. Must be specified in case of
                deploy message
        :param call_set: Function call parameters. Must be specified in case
                of non-deploy message. In case of deploy message it is
                optional and contains parameters of the functions that will
                to be called upon deploy transaction
        :param processing_try_index: Processing try index. Used in message
                processing with retries (if contract's ABI includes
                "expire" header). Encoder uses the provided try index to
                calculate message expiration time. The 1st message expiration
                time is specified in Client config. Expiration timeouts will
                grow with every retry. Default value is 0
        """
        self.abi = abi
        self.signer = signer
        self.address = address
        self.deploy_set = deploy_set
        self.call_set = call_set
        self.processing_try_index = processing_try_index

    @property
    def dict(self):
        deploy_set = self.deploy_set.dict \
            if self.deploy_set else self.deploy_set
        call_set = self.call_set.dict if self.call_set else self.call_set

        return {
            'abi': self.abi.dict,
            'signer': self.signer.dict,
            'address': self.address,
            'deploy_set': deploy_set,
            'call_set': call_set,
            'processing_try_index': self.processing_try_index
        }


class ResultOfEncodeMessage(object):
    def __init__(
            self, message: str, address: str, message_id: str,
            data_to_sign: str = None):
        """
        :param message: Message BOC encoded with `base64`
        :param address:
        :param message_id:
        :param data_to_sign: Optional data to be signed encoded in `base64`.
                Returned in case of Signer::External. Can be used for external
                message signing. Is this case you need to use this data to
                create signature and then produce signed message using
                `abi.attach_signature`
        """
        self.message = message
        self.address = address
        self.message_id = message_id
        self.data_to_sign = data_to_sign


class ParamsOfAttachSignature(object):
    def __init__(
            self, abi: 'AbiType', public_key: str, message: str,
            signature: str):
        """
        :param abi: Contract ABI
        :param public_key: Public key encoded in `hex`
        :param message: Unsigned message BOC encoded in `base64`
        :param signature: Signature encoded in `hex`
        """
        self.abi = abi
        self.public_key = public_key
        self.message = message
        self.signature = signature

    @property
    def dict(self):
        return {
            'abi': self.abi.dict,
            'public_key': self.public_key,
            'message': self.message,
            'signature': self.signature
        }


class ResultOfAttachSignature(object):
    def __init__(self, message: str, message_id: str):
        """
        :param message: Signed message BOC
        :param message_id: Message ID
        """
        self.message = message
        self.message_id = message_id


class ParamsOfDecodeMessage(object):
    def __init__(self, abi: 'AbiType', message: str):
        """
        :param abi: Contract ABI
        :param message: Message BOC
        """
        self.abi = abi
        self.message = message

    @property
    def dict(self):
        return {'abi': self.abi.dict, 'message': self.message}


class DecodedMessageBody(object):
    def __init__(
            self, body_type: 'MessageBodyType', name: str, value: Any = None,
            header: 'FunctionHeader' = None):
        """
        :param body_type: Type of the message body content
        :param name: Function or event name
        :param value: Parameters or result value
        :param header: Function header
        """
        self.body_type = body_type
        self.name = name
        self.value = value
        self.header = header

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DecodedMessageBody':
        if data['header']:
            data['header'] = FunctionHeader(**data['header'])

        return DecodedMessageBody(**data)


class ParamsOfDecodeMessageBody(object):
    def __init__(self, abi: 'AbiType', body: str, is_internal: bool):
        """
        :param abi: Contract ABI used to decode
        :param body: Message body BOC encoded in `base64`
        :param is_internal: True if the body belongs to the internal message
        """
        self.abi = abi
        self.body = body
        self.is_internal = is_internal

    @property
    def dict(self):
        return {
            'abi': self.abi.dict,
            'body': self.body,
            'is_internal': self.is_internal
        }


class ParamsOfEncodeAccount(object):
    def __init__(
            self, state_init: 'StateInitSourceType', balance: int = None,
            last_trans_lt: int = None, last_paid: int = None):
        """
        :param state_init: Source of the account state init
        :param balance: Initial balance
        :param last_trans_lt: Initial value for the `last_trans_lt`
        :param last_paid: Initial value for the `last_paid`
        """
        self.state_init = state_init
        self.balance = balance
        self.last_trans_lt = last_trans_lt
        self.last_paid = last_paid

    @property
    def dict(self):
        return {
            'state_init': self.state_init.dict,
            'balance': self.balance,
            'last_trans_lt': self.last_trans_lt,
            'last_paid': self.last_paid
        }


class ResultOfEncodeAccount(object):
    def __init__(self, account: str, id: str):
        """
        :param account: Account BOC encoded in `base64`
        :param id: Account ID encoded in `hex`
        """
        self.account = account
        self.id = id


# BOC module
class ParamsOfParse(object):
    def __init__(self, boc: str):
        """
        :param boc: BOC encoded as `base64`
        """
        self.boc = boc

    @property
    def dict(self):
        return {'boc': self.boc}


class ResultOfParse(object):
    def __init__(self, parsed: Any):
        """
        :param parsed: JSON containing parsed BOC
        """
        self.parsed = parsed


class ParamsOfParseShardstate(object):
    def __init__(self, boc: str, id: str, workchain_id: int):
        """
        :param boc: BOC encoded as `base64`
        :param id: Shardstate identificator
        :param workchain_id: Workchain shardstate belongs to
        """
        self.boc = boc
        self.id = id
        self.workchain_id = workchain_id

    @property
    def dict(self):
        return {
            'boc': self.boc,
            'id': self.id,
            'workchain_id': self.workchain_id
        }


class ParamsOfGetBlockchainConfig(object):
    def __init__(self, block_boc: str):
        """
        :param block_boc: Key block BOC encoded as `base64`
        """
        self.block_boc = block_boc

    @property
    def dict(self):
        return {'block_boc': self.block_boc}


class ResultOfGetBlockchainConfig(object):
    def __init__(self, config_boc: str):
        """
        :param config_boc: Blockchain config BOC encoded as `base64`
        """
        self.config_boc = config_boc


class ParamsOfGetBocHash(object):
    def __init__(self, boc: str):
        """
        :param boc: BOC encoded as `base64`
        """
        self.boc = boc

    @property
    def dict(self):
        return {'boc': self.boc}


class ResultOfGetBocHash(object):
    def __init__(self, hash: str):
        """
        :param hash: BOC root hash encoded with `hex`
        """
        self.hash = hash


class ParamsOfGetCodeFromTvc(object):
    def __init__(self, tvc: str):
        """
        :param tvc: Contract TVC image encoded as `base64`
        """
        self.tvc = tvc

    @property
    def dict(self):
        return {'tvc': self.tvc}


class ResultOfGetCodeFromTvc(object):
    def __init__(self, code: str):
        """
        :param code: Contract code encoded as `base64`
        """
        self.code = code


# CRYPTO module
SigningBoxHandle = int


class MnemonicDictionary(int, Enum):
    TON = 0
    ENGLISH = 1
    CHINESE_SIMPLIFIED = 2
    CHINESE_TRADITIONAL = 3
    FRENCH = 4
    ITALIAN = 5
    JAPANESE = 6
    KOREAN = 7
    SPANISH = 8


class KeyPair(object):
    """ Keypair object representation """
    def __init__(self, public: str, secret: str):
        """
        :param public: Public key - 64 symbols `hex` string
        :param secret: Private key - 64 symbols `hex` string
        """
        self.public = public
        self.secret = secret

    @property
    def dict(self) -> Dict[str, str]:
        return {'public': self.public, 'secret': self.secret}

    @property
    def binary(self) -> bytes:
        return bytes.fromhex(f'{self.secret}{self.public}')

    @staticmethod
    def load(path: str, is_binary: bool) -> 'KeyPair':
        """ Load keypair from file """
        if is_binary:
            with open(path, 'rb') as fp:
                keys = fp.read().hex()
                keys = {'public': keys[64:], 'secret': keys[:64]}
        else:
            with open(path, 'r') as fp:
                keys = json.loads(fp.read())

        return KeyPair(**keys)

    def dump(self, path: str, as_binary: bool) -> None:
        """ Dump keypair to file """
        if as_binary:
            with open(path, 'wb') as fp:
                fp.write(self.binary)
        else:
            with open(path, 'w') as fp:
                json.dump(self.dict, fp)

    @staticmethod
    def load_io(io: StringIO, as_binary: bool = False) -> 'KeyPair':
        """ Load keypair from StringIO """
        data = io.getvalue()
        keys = json.loads(data) \
            if not as_binary else {'public': data[64:], 'secret': data[:64]}

        return KeyPair(**keys)

    def dump_io(self, io: StringIO, as_binary: bool = False):
        """ Dump keypair to StringIO """
        keys = json.dumps(self.dict) if not as_binary else self.binary.hex()
        io.write(keys)


class ParamsOfFactorize(object):
    def __init__(self, composite: str):
        """
        :param composite: Hexadecimal representation of u64 composite number
        """
        self.composite = composite

    @property
    def dict(self):
        return {'composite': self.composite}


class ResultOfFactorize(object):
    def __init__(self, factors: List[str]):
        """
        :param factors: Two factors of composite or empty if composite
                can't be factorized
        """
        self.factors = factors


class ParamsOfModularPower(object):
    def __init__(self, base: str, exponent: str, modulus: str):
        """
        :param base: `base` argument of calculation
        :param exponent: `exponent` argument of calculation
        :param modulus: `modulus` argument of calculation
        """
        self.base = base
        self.exponent = exponent
        self.modulus = modulus

    @property
    def dict(self):
        return {
            'base': self.base,
            'exponent': self.exponent,
            'modulus': self.modulus
        }


class ResultOfModularPower(object):
    def __init__(self, modular_power: str):
        """
        :param modular_power: Result of modular exponentiation
        """
        self.modular_power = modular_power


class ParamsOfTonCrc16(object):
    def __init__(self, data: str):
        """
        :param data: Input data for CRC calculation. Encoded with `base64`
        """
        self.data = data

    @property
    def dict(self):
        return {'data': self.data}


class ResultOfTonCrc16(object):
    def __init__(self, crc: int):
        """
        :param crc: Calculated CRC for input data
        """
        self.crc = crc


class ParamsOfGenerateRandomBytes(object):
    def __init__(self, length: int):
        """
        :param length: Size of random byte array
        """
        self.length = length

    @property
    def dict(self):
        return {'length': self.length}


class ResultOfGenerateRandomBytes(object):
    def __init__(self, bytes: str):
        """
        :param bytes: Generated bytes encoded in `base64`
        """
        self.bytes = bytes


class ParamsOfConvertPublicKeyToTonSafeFormat(object):
    def __init__(self, public_key: str):
        """
        :param public_key: Public key - 64 symbols `hex` string
        """
        self.public_key = public_key

    @property
    def dict(self):
        return {'public_key': self.public_key}


class ResultOfConvertPublicKeyToTonSafeFormat(object):
    def __init__(self, ton_public_key: str):
        """
        :param ton_public_key: Public key represented in TON safe format
        """
        self.ton_public_key = ton_public_key


class ParamsOfSign(object):
    def __init__(self, unsigned: str, keys: 'KeyPair'):
        """
        :param unsigned: Data that must be signed encoded in `base64`
        :param keys: Sign keys
        """
        self.unsigned = unsigned
        self.keys = keys

    @property
    def dict(self):
        return {'unsigned': self.unsigned, 'keys': self.keys.dict}


class ResultOfSign(object):
    def __init__(self, signed: str, signature: str):
        """
        :param signed: Signed data combined with signature encoded in `base64`
        :param signature: Signature encoded in `hex`
        """
        self.signed = signed
        self.signature = signature


class ParamsOfVerifySignature(object):
    def __init__(self, signed: str, public: str):
        """
        :param signed: Signed data that must be verified encoded in `base64`
        :param public: Signer's public key - 64 symbols `hex` string
        """
        self.signed = signed
        self.public = public

    @property
    def dict(self):
        return {'signed': self.signed, 'public': self.public}


class ResultOfVerifySignature(object):
    def __init__(self, unsigned: str):
        """
        :param unsigned: Unsigned data encoded in `base64`
        """
        self.unsigned = unsigned


class ParamsOfHash(object):
    def __init__(self, data: str):
        """
        :param data: Input data for hash calculation. Encoded with `base64`
        """
        self.data = data

    @property
    def dict(self):
        return {'data': self.data}


class ResultOfHash(object):
    def __init__(self, hash: str):
        """
        :param hash: Hash of input data
        """
        self.hash = hash


class ParamsOfScrypt(object):
    def __init__(
            self, password: str, salt: str, log_n: int, r: int, p: int,
            dk_len: int):
        """
        :param password: The password bytes to be hashed. Must be encoded
                with `base64`
        :param salt: Salt bytes that modify the hash to protect against
                Rainbow table attacks. Must be encoded with `base64`
        :param log_n: CPU/memory cost parameter
        :param r: The block size parameter, which fine-tunes sequential
                memory read size and performance
        :param p: Parallelization parameter
        :param dk_len: Intended output length in octets of the derived key
        """
        self.password = password
        self.salt = salt
        self.log_n = log_n
        self.r = r
        self.p = p
        self.dk_len = dk_len

    @property
    def dict(self):
        return {
            'password': self.password,
            'salt': self.salt,
            'log_n': self.log_n,
            'r': self.r,
            'p': self.p,
            'dk_len': self.dk_len
        }


class ResultOfScrypt(object):
    def __init__(self, key: str):
        """
        :param key: Derived key. Encoded with `hex`
        """
        self.key = key


class ParamsOfNaclSignKeyPairFromSecret(object):
    def __init__(self, secret: str):
        """
        :param secret: Secret key - unprefixed 0-padded to 64
                symbols `hex` string
        """
        self.secret = secret

    @property
    def dict(self):
        return {'secret': self.secret}


class ParamsOfNaclSign(object):
    def __init__(self, unsigned: str, secret: str):
        """
        :param unsigned: Data that must be signed encoded in `base64`
        :param secret: Signer's secret key - unprefixed 0-padded to 64
                symbols `hex` string
        """
        self.unsigned = unsigned
        self.secret = secret

    @property
    def dict(self):
        return {'unsigned': self.unsigned, 'secret': self.secret}


class ResultOfNaclSign(object):
    def __init__(self, signed: str):
        """
        :param signed: Signed data, encoded in `base64`
        """
        self.signed = signed


class ParamsOfNaclSignOpen(object):
    def __init__(self, signed: str, public: str):
        """
        :param signed: Signed data that must be unsigned. Encoded with `base64`
        :param public: Signer's public key - unprefixed 0-padded to 64
                symbols `hex` string
        """
        self.signed = signed
        self.public = public

    @property
    def dict(self):
        return {'signed': self.signed, 'public': self.public}


class ResultOfNaclSignOpen(object):
    def __init__(self, unsigned: str):
        """
        :param unsigned: Unsigned data, encoded in `base64`
        """
        self.unsigned = unsigned


class ResultOfNaclSignDetached(object):
    def __init__(self, signature: str):
        """
        :param signature: Signature encoded in `hex`
        """
        self.signature = signature


class ParamsOfNaclBoxKeyPairFromSecret(object):
    def __init__(self, secret: str):
        """
        :param secret: Secret key - unprefixed 0-padded to 64
                symbols `hex` string
        """
        self.secret = secret

    @property
    def dict(self):
        return {'secret': self.secret}


class ParamsOfNaclBox(object):
    def __init__(
            self, decrypted: str, nonce: str, their_public: str, secret: str):
        """
        :param decrypted: Data that must be encrypted encoded in `base64`
        :param nonce: Nonce, encoded in `hex`
        :param their_public: Receiver's public key - unprefixed 0-padded
                to 64 symbols `hex` string
        :param secret: Sender's private key - unprefixed 0-padded to 64
                symbols `hex` string
        """
        self.decrypted = decrypted
        self.nonce = nonce
        self.their_public = their_public
        self.secret = secret

    @property
    def dict(self):
        return {
            'decrypted': self.decrypted,
            'nonce': self.nonce,
            'their_public': self.their_public,
            'secret': self.secret
        }


class ResultOfNaclBox(object):
    def __init__(self, encrypted: str):
        """
        :param encrypted: Encrypted data encoded in `base64`
        """
        self.encrypted = encrypted


class ParamsOfNaclBoxOpen(object):
    def __init__(
            self, encrypted: str, nonce: str, their_public: str, secret: str):
        """
        :param encrypted: Data that must be decrypted. Encoded with `base64`
        :param nonce: Nonce, encoded in `hex`
        :param their_public: Sender's public key - unprefixed 0-padded to 64
                symbols `hex` string
        :param secret: Receiver's private key - unprefixed 0-padded to 64
                symbols `hex` string
        """
        self.encrypted = encrypted
        self.nonce = nonce
        self.their_public = their_public
        self.secret = secret

    @property
    def dict(self):
        return {
            'encrypted': self.encrypted,
            'nonce': self.nonce,
            'their_public': self.their_public,
            'secret': self.secret
        }


class ResultOfNaclBoxOpen(object):
    def __init__(self, decrypted: str):
        """
        :param decrypted: Decrypted data encoded in `base64`
        """
        self.decrypted = decrypted


class ParamsOfNaclSecretBox(object):
    def __init__(self, decrypted: str, nonce: str, key: str):
        """
        :param decrypted:  Data that must be encrypted. Encoded with `base64`
        :param nonce: Nonce in `hex`
        :param key: Secret key - unprefixed 0-padded to 64 symbols `hex` string
        """
        self.decrypted = decrypted
        self.nonce = nonce
        self.key = key

    @property
    def dict(self):
        return {
            'decrypted': self.decrypted,
            'nonce': self.nonce,
            'key': self.key
        }


class ParamsOfNaclSecretBoxOpen(object):
    def __init__(self, encrypted: str, nonce: str, key: str):
        """
        :param encrypted: Data that must be decrypted. Encoded with `base64`
        :param nonce: Nonce in `hex`
        :param key: Public key - unprefixed 0-padded to 64 symbols `hex` string
        """
        self.encrypted = encrypted
        self.nonce = nonce
        self.key = key

    @property
    def dict(self):
        return {
            'encrypted': self.encrypted,
            'nonce': self.nonce,
            'key': self.key
        }


class ParamsOfMnemonicWords(object):
    def __init__(self, dictionary: 'MnemonicDictionary' = None):
        """
        :param dictionary: Dictionary identifier
        """
        self.dictionary = dictionary

    @property
    def dict(self):
        return {'dictionary': self.dictionary}


class ResultOfMnemonicWords(object):
    def __init__(self, words: str):
        """
        :param words: The list of mnemonic words
        """
        self.words = words


class ParamsOfMnemonicFromRandom(object):
    def __init__(
            self, dictionary: 'MnemonicDictionary' = None,
            word_count: int = None):
        """
        :param dictionary: Dictionary identifier
        :param word_count: Mnemonic word count
        """
        self.dictionary = dictionary
        self.word_count = word_count

    @property
    def dict(self):
        return {'dictionary': self.dictionary, 'word_count': self.word_count}


class ResultOfMnemonicFromRandom(object):
    def __init__(self, phrase: str):
        """
        :param phrase: String of mnemonic words
        """
        self.phrase = phrase


class ParamsOfMnemonicFromEntropy(object):
    def __init__(
            self, entropy: str, dictionary: 'MnemonicDictionary' = None,
            word_count: int = None):
        """
        :param entropy: Entropy bytes. `Hex` encoded
        :param dictionary: Dictionary identifier
        :param word_count: Mnemonic word count
        """
        self.entropy = entropy
        self.dictionary = dictionary
        self.word_count = word_count

    @property
    def dict(self):
        return {
            'entropy': self.entropy,
            'dictionary': self.dictionary,
            'word_count': self.word_count
        }


class ResultOfMnemonicFromEntropy(object):
    def __init__(self, phrase: str):
        """
        :param phrase: String of mnemonic words
        """
        self.phrase = phrase


class ParamsOfMnemonicVerify(object):
    def __init__(
            self, phrase: str, dictionary: 'MnemonicDictionary' = None,
            word_count: int = None):
        """
        :param phrase: Phrase to be verified
        :param dictionary: Dictionary identifier
        :param word_count: Word count
        """
        self.phrase = phrase
        self.dictionary = dictionary
        self.word_count = word_count

    @property
    def dict(self):
        return {
            'phrase': self.phrase,
            'dictionary': self.dictionary,
            'word_count': self.word_count
        }


class ResultOfMnemonicVerify(object):
    def __init__(self, valid: bool):
        """
        :param valid: Flag indicating if the mnemonic is valid or not
        """
        self.valid = valid


class ParamsOfMnemonicDeriveSignKeys(object):
    def __init__(
            self, phrase: str, path: str = None,
            dictionary: 'MnemonicDictionary' = None, word_count: int = None):
        """
        :param phrase: String of mnemonic words
        :param path: Derivation path, for instance "m/44'/396'/0'/0/0"
        :param dictionary: Dictionary identifier
        :param word_count: Word count
        """
        self.phrase = phrase
        self.path = path
        self.dictionary = dictionary
        self.word_count = word_count

    @property
    def dict(self):
        return {
            'phrase': self.phrase,
            'path': self.path,
            'dictionary': self.dictionary,
            'word_count': self.word_count
        }


class ParamsOfHDKeyXPrvFromMnemonic(object):
    def __init__(
            self, phrase: str, dictionary: 'MnemonicDictionary' = None,
            word_count: int = None):
        """
        :param phrase: String of mnemonic words
        :param dictionary: Dictionary identifier
        :param word_count: Mnemonic word count
        """
        self.phrase = phrase
        self.dictionary = dictionary
        self.word_count = word_count

    @property
    def dict(self):
        return {
            'phrase': self.phrase,
            'dictionary': self.dictionary,
            'word_count': self.word_count
        }


class ResultOfHDKeyXPrvFromMnemonic(object):
    def __init__(self, xprv: str):
        """
        :param xprv: Serialized extended master private key
        """
        self.xprv = xprv


class ParamsOfHDKeyDeriveFromXPrv(object):
    def __init__(self, xprv: str, child_index: int, hardened: bool):
        """
        :param xprv: Serialized extended private key
        :param child_index: Child index (see BIP-0032)
        :param hardened: Indicates the derivation of hardened/not-hardened
                key (see BIP-0032)
        """
        self.xprv = xprv
        self.child_index = child_index
        self.hardened = hardened

    @property
    def dict(self):
        return {
            'xprv': self.xprv,
            'child_index': self.child_index,
            'hardened': self.hardened
        }


class ResultOfHDKeyDeriveFromXPrv(object):
    def __init__(self, xprv: str):
        """
        :param xprv: Serialized extended private key
        """
        self.xprv = xprv


class ParamsOfHDKeyDeriveFromXPrvPath(object):
    def __init__(self, xprv: str, path: str):
        """
        :param xprv: Serialized extended private key
        :param path: Derivation path, for instance "m/44'/396'/0'/0/0"
        """
        self.xprv = xprv
        self.path = path

    @property
    def dict(self):
        return {'xprv': self.xprv, 'path': self.path}


class ResultOfHDKeyDeriveFromXPrvPath(object):
    def __init__(self, xprv: str):
        """
        :param xprv: Derived serialized extended private key
        """
        self.xprv = xprv


class ParamsOfHDKeySecretFromXPrv(object):
    def __init__(self, xprv: str):
        """
        :param xprv: Serialized extended private key
        """
        self.xprv = xprv

    @property
    def dict(self):
        return {'xprv': self.xprv}


class ResultOfHDKeySecretFromXPrv(object):
    def __init__(self, secret: str):
        """
        :param secret: Private key - 64 symbols `hex` string
        """
        self.secret = secret


class ParamsOfHDKeyPublicFromXPrv(object):
    def __init__(self, xprv: str):
        """
        :param xprv: Serialized extended private key
        """
        self.xprv = xprv

    @property
    def dict(self):
        return {'xprv': self.xprv}


class ResultOfHDKeyPublicFromXPrv(object):
    def __init__(self, public: str):
        """
        :param public: Public key - 64 symbols `hex` string
        """
        self.public = public


class ParamsOfChaCha20(object):
    def __init__(self, data: str, key: str, nonce: str):
        """
        :param data: Source data to be encrypted or decrypted.
                Must be encoded with `base64`
        :param key: 256-bit key. Must be encoded with `hex`
        :param nonce: 96-bit nonce. Must be encoded with `hex`
        """
        self.data = data
        self.key = key
        self.nonce = nonce

    @property
    def dict(self):
        return {'data': self.data, 'key': self.key, 'nonce': self.nonce}


class ResultOfChaCha20(object):
    def __init__(self, data: str):
        """
        :param data: Encrypted/decrypted data. Encoded with `base64`
        """
        self.data = data


class RegisteredSigningBox(object):
    def __init__(self, handle: 'SigningBoxHandle'):
        """
        :param handle: Handle of the signing box
        """
        self.handle = handle

    @property
    def dict(self):
        return {'handle': self.handle}


class ParamsOfAppSigningBox:
    class GetPublicKey(BaseTypedType):
        """ Get signing box public key """
        def __init__(self, type: str = 'GetPublicKey'):
            """
            :param type:
            """
            super(ParamsOfAppSigningBox.GetPublicKey, self).__init__(type=type)

    class Sign(BaseTypedType):
        """ Sign data """
        def __init__(self, unsigned: str, type: str = 'Sign'):
            """
            :param unsigned: Data to sign encoded as `base64`
            :param type:
            """
            super(ParamsOfAppSigningBox.Sign, self).__init__(type=type)
            self.unsigned = unsigned

        @property
        def dict(self):
            return {
                **super(ParamsOfAppSigningBox.Sign, self).dict,
                'unsigned': self.unsigned
            }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Union[GetPublicKey, Sign]:
        return getattr(ParamsOfAppSigningBox, data['type'])(**data)


class ResultOfAppSigningBox:
    class GetPublicKey(BaseTypedType):
        """ Result of getting public key """
        def __init__(self, public_key: str, type: str = 'GetPublicKey'):
            """
            :param public_key: Signing box public key
            :param type:
            """
            super(ResultOfAppSigningBox.GetPublicKey, self).__init__(type=type)
            self.public_key = public_key

        @property
        def dict(self):
            return {
                **super(ResultOfAppSigningBox.GetPublicKey, self).dict,
                'public_key': self.public_key
            }

    class Sign(BaseTypedType):
        """ Result of signing data """
        def __init__(self, signature: str, type: str = 'Sign'):
            """
            :param signature: Data signature encoded as `hex`
            :param type:
            """
            super(ResultOfAppSigningBox.Sign, self).__init__(type=type)
            self.signature = signature

        @property
        def dict(self):
            return {
                **super(ResultOfAppSigningBox.Sign, self).dict,
                'signature': self.signature
            }


class ResultOfSigningBoxGetPublicKey(object):
    def __init__(self, pubkey: str):
        """
        :param pubkey: Public key of signing box
        """
        self.pubkey = pubkey


class ParamsOfSigningBoxSign(object):
    def __init__(self, signing_box: 'SigningBoxHandle', unsigned: str):
        """
        :param signing_box: Signing Box handle
        :param unsigned: Unsigned user data. Must be encoded with `base64`
        """
        self.signing_box = signing_box
        self.unsigned = unsigned

    @property
    def dict(self):
        return {'signing_box': self.signing_box, 'unsigned': self.unsigned}


class ResultOfSigningBoxSign(object):
    def __init__(self, signature: str):
        """
        :param signature: Data signature. Encoded with `base64`
        """
        self.signature = signature


# NET module
class SortDirection(str, Enum):
    ASC = 'ASC'
    DESC = 'DESC'


class OrderBy(object):
    def __init__(self, path: str, direction: 'SortDirection'):
        """
        :param path:
        :param direction:
        """
        self.path = path
        self.direction = direction

    @property
    def dict(self):
        return {'path': self.path, 'direction': self.direction}


class ParamsOfQuery(object):
    def __init__(self, query: str, variables: Dict[str, Any] = None):
        """
        :param query: GraphQL query text
        :param variables: Variables used in query. Must be a map with named
                values that can be used in query
        """
        self.query = query
        self.variables = variables

    @property
    def dict(self):
        return {'query': self.query, 'variables': self.variables}


class ResultOfQuery(object):
    def __init__(self, result: Any):
        """
        :param result: Result provided by DAppServer
        """
        self.result = result


class ParamsOfQueryCollection(object):
    def __init__(
            self, collection: str, result: str, filter: Dict[str, Any] = None,
            order: List['OrderBy'] = None, limit: int = None):
        """
        :param collection: Collection name (accounts, blocks, transactions,
                messages, block_signatures)
        :param result: Projection (result) string
        :param filter: Collection filter
        :param order: Sorting order
        :param limit: Number of documents to return
        """
        self.collection = collection
        self.result = result
        self.filter = filter
        self.order = order or []
        self.limit = limit

    @property
    def dict(self):
        return {
            'collection': self.collection,
            'result': self.result,
            'filter': self.filter,
            'order': [o.dict for o in self.order],
            'limit': self.limit
        }


class ResultOfQueryCollection(object):
    def __init__(self, result: List[Any]):
        """
        :param result: Objects that match the provided criteria
        """
        self.result = result


class ParamsOfWaitForCollection(object):
    def __init__(
            self, collection: str, result: str, filter: Dict[str, Any] = None,
            timeout: int = None):
        """
        :param collection: Collection name (accounts, blocks, transactions,
                messages, block_signatures)
        :param result: Projection (result) string
        :param filter: Collection filter
        :param timeout: Query timeout
        """
        self.collection = collection
        self.result = result
        self.filter = filter
        self.timeout = timeout

    @property
    def dict(self):
        return {
            'collection': self.collection,
            'result': self.result,
            'filter': self.filter,
            'timeout': self.timeout
        }


class ResultOfWaitForCollection(object):
    def __init__(self, result: Any):
        """
        :param result: First found object that matches the provided criteria
        """
        self.result = result


class ParamsOfSubscribeCollection(object):
    def __init__(self, collection: str, result: str, filter: Dict[str, Any]):
        """
        :param collection: Collection name (accounts, blocks, transactions,
                messages, block_signatures)
        :param result: Projection (result) string
        :param filter: Collection filter
        """
        self.collection = collection
        self.result = result
        self.filter = filter

    @property
    def dict(self):
        return {
            'collection': self.collection,
            'result': self.result,
            'filter': self.filter
        }


class ResultOfSubscribeCollection(object):
    def __init__(self, handle: int):
        """
        :param handle: Subscription handle. Must be closed with `unsubscribe`
        """
        self.handle = handle

    @property
    def dict(self):
        return {'handle': self.handle}


class SubscriptionResponseType(int, Enum):
    OK = 100
    ERROR = 101


class ResultOfSubscription(object):
    def __init__(self, result: Dict[str, Any]):
        """
        :param result: First appeared object that matches the provided criteria
        """
        self.result = result


class ParamsOfFindLastShardBlock(object):
    def __init__(self, address: str):
        """
        :param address: Account address
        """
        self.address = address

    @property
    def dict(self):
        return {'address': self.address}


class ResultOfFindLastShardBlock(object):
    def __init__(self, block_id: str):
        """
        :param block_id: Account shard last block ID
        """
        self.block_id = block_id


# PROCESSING module
class ProcessingEvent:
    class WillFetchFirstBlock(BaseTypedType):
        """
        Notifies the app that the current shard block will be fetched from
        the network. Fetched block will be used later in waiting phase
        """
        def __init__(self, type: str = 'WillFetchFirstBlock'):
            """
            :param type:
            """
            super(ProcessingEvent.WillFetchFirstBlock, self).__init__(
                type=type)

    class FetchFirstBlockFailed(BaseTypedType):
        """
        Notifies the app that the client has failed to fetch current shard
        block. Message processing has finished
        """
        def __init__(
                self, error: 'ClientError',
                type: str = 'FetchFirstBlockFailed'):
            """
            :param error:
            :param type:
            """
            super(ProcessingEvent.FetchFirstBlockFailed, self).__init__(
                type=type)
            self.error = error

    class WillSend(BaseTypedType):
        """ Notifies the app that the message will be sent to the network """
        def __init__(
                self, shard_block_id: str, message_id: str, message: str,
                type: str = 'WillSend'):
            """
            :param shard_block_id:
            :param message_id:
            :param message:
            :param type:
            """
            super(ProcessingEvent.WillSend, self).__init__(type=type)
            self.shard_block_id = shard_block_id
            self.message_id = message_id
            self.message = message

    class DidSend(BaseTypedType):
        """ Notifies the app that the message was sent to the network """
        def __init__(
                self, shard_block_id: str, message_id: str, message: str,
                type: str = 'DidSend'):
            """
            :param shard_block_id:
            :param message_id:
            :param message:
            :param type:
            """
            super(ProcessingEvent.DidSend, self).__init__(type=type)
            self.shard_block_id = shard_block_id
            self.message_id = message_id
            self.message = message

    class SendFailed(BaseTypedType):
        """
        Notifies the app that the sending operation was failed with network
        error. Nevertheless the processing will be continued at the waiting
        phase because the message possibly has been delivered to the node
        """
        def __init__(
                self, shard_block_id: str, message_id: str, message: str,
                error: 'ClientError', type: str = 'SendFailed'):
            """
            :param shard_block_id:
            :param message_id:
            :param message:
            :param error:
            :param type:
            """
            super(ProcessingEvent.SendFailed, self).__init__(type=type)
            self.shard_block_id = shard_block_id
            self.message_id = message_id
            self.message = message
            self.error = error

    class WillFetchNextBlock(BaseTypedType):
        """
        Notifies the app that the next shard block will be fetched from the
        network. Event can occurs more than one time due to block walking
        procedure
        """
        def __init__(
                self, shard_block_id: str, message_id: str, message: str,
                type: str = 'WillFetchNextBlock'):
            """
            :param shard_block_id:
            :param message_id:
            :param message:
            :param type:
            """
            super(ProcessingEvent.WillFetchNextBlock, self).__init__(type=type)
            self.shard_block_id = shard_block_id
            self.message_id = message_id
            self.message = message

    class FetchNextBlockFailed(BaseTypedType):
        """
        Notifies the app that the next block can't be fetched due to error.
        Processing will be continued after `network_resume_timeout`
        """
        def __init__(
                self, shard_block_id: str, message_id: str, message: str,
                error: 'ClientError', type: str = 'FetchNextBlockFailed'):
            """
            :param shard_block_id:
            :param message_id:
            :param message:
            :param error:
            :param type:
            """
            super(ProcessingEvent.FetchNextBlockFailed, self).__init__(
                type=type)
            self.shard_block_id = shard_block_id
            self.message_id = message_id
            self.message = message
            self.error = error

    class MessageExpired(BaseTypedType):
        """
        Notifies the app that the message was expired.
        Event occurs for contracts which ABI includes header "expire"
        Processing will be continued from encoding phase after
        `expiration_retries_timeout`
        """
        def __init__(
                self, message_id: str, message: str, error: 'ClientError',
                type: str = 'MessageExpired'):
            """
            :param message_id:
            :param message:
            :param error:
            :param type:
            """
            super(ProcessingEvent.MessageExpired, self).__init__(type=type)
            self.message_id = message_id
            self.message = message
            self.error = error

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ProcessingEventType':
        return getattr(ProcessingEvent, data['type'])(**data)


class ProcessingResponseType(int, Enum):
    PROCESSING_EVENT = 100


class ResultOfProcessMessage(object):
    def __init__(
            self, transaction: Dict[str, Any], out_messages: List[str],
            fees: 'TransactionFees', decoded: 'DecodedOutput' = None):
        """
        :param transaction: Parsed transaction. In addition to the regular
                transaction fields there is a boc field encoded with `base64`
                which contains source transaction BOC
        :param out_messages: List of output messages' BOCs. Encoded as `base64`
        :param fees: Transaction fees
        :param decoded: Optional decoded message bodies according to the
                optional `abi` parameter
        """
        self.transaction = transaction
        self.out_messages = out_messages
        self.fees = fees
        self.decoded = decoded

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ResultOfProcessMessage':
        data['fees'] = TransactionFees(**data['fees'])
        if data['decoded']:
            data['decoded'] = DecodedOutput.from_dict(data=data['decoded'])

        return ResultOfProcessMessage(**data)


class DecodedOutput(object):
    def __init__(
            self, out_messages: List['DecodedMessageBody'],
            output: Any = None):
        """
        :param out_messages: Decoded bodies of the out messages. If the
                message can't be decoded, then None will be stored in the
                appropriate position
        :param output: Decoded body of the function output message
        """
        self.out_messages = out_messages
        self.output = output

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DecodedOutput':
        if data['out_messages']:
            data['out_messages'] = [
                DecodedMessageBody.from_dict(data=m)
                for m in data['out_messages'] if m
            ]

        return DecodedOutput(**data)


class ParamsOfSendMessage(object):
    def __init__(self, message: str, send_events: bool, abi: 'AbiType' = None):
        """
        :param message: Message BOC
        :param send_events: Flag for requesting events sending
        :param abi: Optional message ABI. If this parameter is specified and
                the message has the expire header then expiration time will
                be checked against the current time to prevent unnecessary
                sending of already expired message. The message already
                expired error will be returned in this case. Note, that
                specifying abi for ABI compliant contracts is strongly
                recommended, so that proper processing strategy can be chosen
        """
        self.message = message
        self.send_events = send_events
        self.abi = abi

    @property
    def dict(self):
        abi = self.abi.dict if self.abi else self.abi
        return {
            'message': self.message,
            'send_events': self.send_events,
            'abi': abi
        }


class ResultOfSendMessage(object):
    def __init__(self, shard_block_id: str):
        """
        :param shard_block_id: The last generated shard block of the message
                destination account before the message was sent. This block id
                must be used as a parameter of the `wait_for_transaction`
        """
        self.shard_block_id = shard_block_id


class ParamsOfWaitForTransaction(object):
    def __init__(
            self, message: str, shard_block_id: str, send_events: bool,
            abi: 'AbiType' = None):
        """
        :param message: Message BOC. Encoded with base64
        :param shard_block_id: The last generated block id of the destination
                account shard before the message was sent. You must provide
                the same value as the `send_message` has returned
        :param send_events: Flag that enables/disables intermediate events
        :param abi: Optional ABI for decoding the transaction result.
                If it is specified, then the output messages' bodies will be
                decoded according to this ABI. The `abi_decoded` result field
                will be filled out
        """
        self.message = message
        self.shard_block_id = shard_block_id
        self.send_events = send_events
        self.abi = abi

    @property
    def dict(self):
        abi = self.abi.dict if self.abi else self.abi
        return {
            'message': self.message,
            'shard_block_id': self.shard_block_id,
            'send_events': self.send_events,
            'abi': abi
        }


class ParamsOfProcessMessage(object):
    def __init__(
            self, message_encode_params: 'ParamsOfEncodeMessage',
            send_events: bool):
        """
        :param message_encode_params: Message encode parameters
        :param send_events: Flag for requesting events sending
        """
        self.message_encode_params = message_encode_params
        self.send_events = send_events

    @property
    def dict(self):
        return {
            'message_encode_params': self.message_encode_params.dict,
            'send_events': self.send_events
        }


# TVM module
class TransactionFees(object):
    def __init__(
            self, in_msg_fwd_fee: int, storage_fee: int, gas_fee: int,
            out_msgs_fwd_fee: int, total_account_fees: int, total_output: int):
        """
        :param in_msg_fwd_fee:
        :param storage_fee:
        :param gas_fee:
        :param out_msgs_fwd_fee:
        :param total_account_fees:
        :param total_output:
        """
        self.in_msg_fwd_fee = in_msg_fwd_fee
        self.storage_fee = storage_fee
        self.gas_fee = gas_fee
        self.out_msgs_fwd_fee = out_msgs_fwd_fee
        self.total_account_fees = total_account_fees
        self.total_output = total_output


class ExecutionOptions(object):
    def __init__(
            self, blockchain_config: str, block_time: int, block_lt: int,
            transaction_lt: int):
        """
        :param blockchain_config: boc with config
        :param block_time: time that is used as transaction time
        :param block_lt: block logical time
        :param transaction_lt: transaction logical time
        """
        self.blockchain_config = blockchain_config
        self.block_time = block_time
        self.block_lt = block_lt
        self.transaction_lt = transaction_lt

    @property
    def dict(self):
        return {
            'blockchain_config': self.blockchain_config,
            'block_time': self.block_time,
            'block_lt': self.block_lt,
            'transaction_lt': self.transaction_lt
        }


class AccountForExecutor:
    class NoAccount(BaseTypedType):
        """
        Non-existing account to run a creation internal message.
        Should be used with `skip_transaction_check = true` if the message
        has no deploy data since transactions on the uninitialized account
        are always aborted
        """
        def __init__(self, type: str = 'None'):
            """
            :param type:
            """
            super(AccountForExecutor.NoAccount, self).__init__(type=type)

    class Uninit(BaseTypedType):
        """ Emulate uninitialized account to run deploy message """
        def __init__(self, type: str = 'Uninit'):
            """
            :param type:
            """
            super(AccountForExecutor.Uninit, self).__init__(type=type)

    class Account(BaseTypedType):
        def __init__(
                self, boc: str, unlimited_balance: bool = None,
                type: str = 'Account'):
            """
            :param boc: Account BOC. Encoded as `base64`
            :param unlimited_balance: Flag for running account with the
                    unlimited balance. Can be used to calculate transaction
                    fees without balance check
            :param type:
            """
            super(AccountForExecutor.Account, self).__init__(type=type)
            self.boc = boc
            self.unlimited_balance = unlimited_balance

        @property
        def dict(self):
            return {
                **super(AccountForExecutor.Account, self).dict,
                'boc': self.boc,
                'unlimited_balance': self.unlimited_balance
            }


class ParamsOfRunExecutor(object):
    def __init__(
            self, message: str, account: 'AccountForExecutorType',
            execution_options: 'ExecutionOptions' = None,
            abi: 'AbiType' = None, skip_transaction_check: bool = None):
        """
        :param message: Input message BOC. Must be encoded as `base64`
        :param account: Account to run on executor
        :param execution_options: Execution options
        :param abi: Contract ABI for decoding output messages
        :param skip_transaction_check: Skip transaction check flag
        """
        self.message = message
        self.account = account
        self.execution_options = execution_options
        self.abi = abi
        self.skip_transaction_check = skip_transaction_check

    @property
    def dict(self):
        execution_options = self.execution_options.dict \
            if self.execution_options else self.execution_options
        abi = self.abi.dict if self.abi else self.abi

        return {
            'message': self.message,
            'account': self.account.dict,
            'execution_options': execution_options,
            'abi': abi,
            'skip_transaction_check': self.skip_transaction_check
        }


class ResultOfRunExecutor(object):
    def __init__(
            self, transaction: Dict[str, Any], out_messages: List[str],
            account: str, fees: 'TransactionFees',
            decoded: 'DecodedOutput' = None):
        """
        :param transaction: Parsed transaction. In addition to the regular
                transaction fields there is a boc field encoded with `base64`
                which contains source transaction BOC
        :param out_messages: List of output messages' BOCs. Encoded as `base64`
        :param account: Updated account state BOC. Encoded as `base64`
        :param fees: Transaction fees
        :param decoded: Optional decoded message bodies according to the
                optional `abi` parameter
        """
        self.transaction = transaction
        self.out_messages = out_messages
        self.account = account
        self.fees = fees
        self.decoded = decoded

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ResultOfRunExecutor':
        data['fees'] = TransactionFees(**data['fees'])
        if data['decoded']:
            data['decoded'] = DecodedOutput.from_dict(data=data['decoded'])

        return ResultOfRunExecutor(**data)


class ParamsOfRunTvm(object):
    def __init__(
            self, message: str, account: str, abi: 'AbiType' = None,
            execution_options: 'ExecutionOptions' = None):
        """
        :param message: Input message BOC. Must be encoded as `base64`
        :param account: Account BOC. Must be encoded as `base64`
        :param abi: Contract ABI for dedcoding output messages
        :param execution_options: Execution options
        """
        self.message = message
        self.account = account
        self.abi = abi
        self.execution_options = execution_options

    @property
    def dict(self):
        execution_options = self.execution_options.dict \
            if self.execution_options else self.execution_options
        abi = self.abi.dict if self.abi else self.abi

        return {
            'message': self.message,
            'account': self.account,
            'execution_options': execution_options,
            'abi': abi
        }


class ResultOfRunTvm(object):
    def __init__(
            self, out_messages: List[str], account: str,
            decoded: 'DecodedOutput' = None):
        """
        :param out_messages: List of output messages' BOCs. Encoded as `base64`
        :param account: Updated account state BOC. Encoded as `base64`.
                Attention! Only data in account state is updated
        :param decoded: Optional decoded message bodies according to the
                optional `abi` parameter
        """
        self.out_messages = out_messages
        self.account = account
        self.decoded = decoded

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ResultOfRunTvm':
        if data['decoded']:
            data['decoded'] = DecodedOutput.from_dict(data=data['decoded'])

        return ResultOfRunTvm(**data)


class ParamsOfRunGet(object):
    def __init__(
            self, account: str, function_name: str, input: Any = None,
            execution_options: 'ExecutionOptions' = None):
        """
        :param account: Account BOC in `base64`
        :param function_name: Function name
        :param input: Input parameters
        :param execution_options: Execution options
        """
        self.account = account
        self.function_name = function_name
        self.input = input
        self.execution_options = execution_options

    @property
    def dict(self):
        execution_options = self.execution_options.dict \
            if self.execution_options else self.execution_options

        return {
            'account': self.account,
            'function_name': self.function_name,
            'input': self.input,
            'execution_options': execution_options
        }


class ResultOfRunGet(object):
    def __init__(self, output: Any):
        """
        :param output: Values returned by getmethod on stack
        """
        self.output = output


# UTILS module
class AddressStringFormat:
    class AccountId(BaseTypedType):
        def __init__(self, type: str = 'AccountId'):
            """
            :param type:
            """
            super(AddressStringFormat.AccountId, self).__init__(type=type)

    class Hex(BaseTypedType):
        def __init__(self, type: str = 'Hex'):
            """
            :param type:
            """
            super(AddressStringFormat.Hex, self).__init__(type=type)

    class Base64(BaseTypedType):
        def __init__(
                self, url: bool, test: bool, bounce: bool,
                type: str = 'Base64'):
            """
            :param url:
            :param test:
            :param bounce:
            """
            super(AddressStringFormat.Base64, self).__init__(type=type)
            self.url = url
            self.test = test
            self.bounce = bounce

        @property
        def dict(self):
            return {
                **super(AddressStringFormat.Base64, self).dict,
                'url': self.url,
                'test': self.test,
                'bounce': self.bounce
            }


class ParamsOfConvertAddress(object):
    def __init__(self, address: str, output_format: 'AddressStringFormatType'):
        """
        :param address: Account address in any TON format
        :param output_format: Specify the format to convert to
        """
        self.address = address
        self.output_format = output_format

    @property
    def dict(self):
        return {
            'address': self.address,
            'output_format': self.output_format.dict
        }


class ResultOfConvertAddress(object):
    def __init__(self, address: str):
        """
        :param address: Address in the specified format
        """
        self.address = address


# DEBOT module
DebotHandle = int


class DebotAction(object):
    def __init__(
            self, description: str, name: str, action_type: int, to: int,
            attributes: str, misc: str):
        """
        :param description: A short action description. Should be used by
                Debot Browser as name of menu item
        :param name: Depends on action type. Can be a debot function name or
                a print string (for Print Action)
        :param action_type: Action type
        :param to: ID of debot context to switch after action execution
        :param attributes: Action attributes. In the form of "param=value,flag"
                Attribute example: instant, args, fargs, sign
        :param misc: Some internal action data. Used by debot only
        """
        self.description = description
        self.name = name
        self.action_type = action_type
        self.to = to
        self.attributes = attributes
        self.misc = misc

    @property
    def dict(self):
        return {
            'description': self.description,
            'name': self.name,
            'action_type': self.action_type,
            'to': self.to,
            'attributes': self.attributes,
            'misc': self.misc
        }

    def __str__(self):
        return self.description


class ParamsOfStart(object):
    """ Parameters to start debot """
    def __init__(self, address: str):
        """
        :param address: Debot smart contract address
        """
        self.address = address

    @property
    def dict(self):
        return {'address': self.address}


class RegisteredDebot(object):
    """
    Structure for storing debot handle returned from `start` and `fetch`
    functions
    """
    def __init__(self, debot_handle: 'DebotHandle'):
        """
        :param debot_handle: Debot handle which references an instance of
                debot engine
        """
        self.debot_handle = debot_handle

    @property
    def dict(self):
        return {'debot_handle': self.debot_handle}


class ParamsOfAppDebotBrowser:
    """
    Debot Browser callbacks.
    Called by debot engine to communicate with debot browser
    """
    class Log(BaseTypedType):
        """ Print message to user """
        def __init__(self, msg: str, type: str = 'Log'):
            """
            :param msg: A string that must be printed to user
            :param type:
            """
            super(ParamsOfAppDebotBrowser.Log, self).__init__(type=type)
            self.msg = msg

    class Switch(BaseTypedType):
        """ Switch debot to another context (menu) """
        def __init__(self, context_id: int, type: str = 'Switch'):
            """
            :param context_id: Debot context ID to which debot is switched
            :param type:
            """
            super(ParamsOfAppDebotBrowser.Switch, self).__init__(type=type)
            self.context_id = context_id

    class SwitchCompleted(BaseTypedType):
        """ Notify browser that all context actions are shown """
        def __init__(self, type: str = 'SwitchCompleted'):
            """
            :param type:
            """
            super(ParamsOfAppDebotBrowser.SwitchCompleted, self).__init__(
                type=type)

    class ShowAction(BaseTypedType):
        """
        Show action to the user.
        Called after switch for each action in context
        """
        def __init__(self, action: 'DebotAction', type: str = 'ShowAction'):
            """
            :param action: Debot action that must be shown to user as menu
                    item. At least description property must be shown from
                    `DebotAction` structure
            :param type:
            """
            super(ParamsOfAppDebotBrowser.ShowAction, self).__init__(
                type=type)
            self.action = action

    class Input(BaseTypedType):
        """ Request user input """
        def __init__(self, prompt: str, type: str = 'Input'):
            """
            :param prompt: A prompt string that must be printed to user
                    before input request
            :param type:
            """
            super(ParamsOfAppDebotBrowser.Input, self).__init__(type=type)
            self.prompt = prompt

    class GetSigningBox(BaseTypedType):
        """
        Get signing box to sign data.
        Signing box returned is owned and disposed by debot engine
        """
        def __init__(self, type: str = 'GetSigningBox'):
            """
            :param type:
            """
            super(ParamsOfAppDebotBrowser.GetSigningBox, self).__init__(
                type=type)

    class InvokeDebot(BaseTypedType):
        """ Execute action of another debot """
        def __init__(
                self, debot_addr: str, action: 'DebotAction',
                type: str = 'InvokeDebot'):
            """
            :param debot_addr: Address of debot in blockchain
            :param action: Debot action to execute
            :param type:
            """
            super(ParamsOfAppDebotBrowser.InvokeDebot, self).__init__(
                type=type)
            self.debot_addr = debot_addr
            self.action = action

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ParamsOfAppDebotBrowserType':
        if data.get('action'):
            data['action'] = DebotAction(**data['action'])
        return getattr(ParamsOfAppDebotBrowser, data['type'])(**data)


class ResultOfAppDebotBrowser(object):
    """ Returning values from Debot Browser callbacks """
    class Input(BaseTypedType):
        """ Result of user input """
        def __init__(self, value: str, type: str = 'Input'):
            """
            :param value: String entered by user
            :param type:
            """
            super(ResultOfAppDebotBrowser.Input, self).__init__(type=type)
            self.value = value

        @property
        def dict(self):
            return {
                **super(ResultOfAppDebotBrowser.Input, self).dict,
                'value': self.value
            }

    class GetSigningBox(BaseTypedType):
        """ Result of getting signing box """
        def __init__(
                self, signing_box: 'SigningBoxHandle',
                type: str = 'GetSigningBox'):
            """
            :param signing_box: Signing box for signing data requested by
                    debot engine. Signing box is owned and disposed by debot
                    engine
            :param type:
            """
            super(ResultOfAppDebotBrowser.GetSigningBox, self).__init__(
                type=type)
            self.signing_box = signing_box

        @property
        def dict(self):
            return {
                **super(ResultOfAppDebotBrowser.GetSigningBox, self).dict,
                'signing_box': self.signing_box
            }

    class InvokeDebot(BaseTypedType):
        """ Result of debot invoking """
        def __init__(self, type: str = 'InvokeDebot'):
            """
            :param type:
            """
            super(ResultOfAppDebotBrowser.InvokeDebot, self).__init__(
                type=type)


class ParamsOfFetch(object):
    """ Parameters to fetch debot """
    def __init__(self, address: str):
        """
        :param address: Debot smart contract address
        """
        self.address = address

    @property
    def dict(self):
        return {'address': self.address}


class ParamsOfExecute(object):
    """ Parameters for executing debot action """
    def __init__(self, debot_handle: 'DebotHandle', action: 'DebotAction'):
        """
        :param debot_handle: Debot handle which references an instance of
                debot engine
        :param action: Debot Action that must be executed
        """
        self.debot_handle = debot_handle
        self.action = action

    @property
    def dict(self):
        return {'debot_handle': self.debot_handle, 'action': self.action.dict}


class DebotState(int, Enum):
    ZERO = 0
    CURRENT = 253
    PREV = 254
    EXIT = 255


# Aggregated types
AbiType = Union[Abi.Contract, Abi.Json, Abi.Handle, Abi.Serialized]
SignerType = Union[
    Signer.NoSigner, Signer.External, Signer.Keys, Signer.SigningBox]
AppRequestResultType = Union[AppRequestResult.Ok, AppRequestResult.Error]
MessageSourceType = Union[MessageSource.Encoded, MessageSource.EncodingParams]
StateInitSourceType = Union[
    StateInitSource.Message, StateInitSource.StateInit, StateInitSource.Tvc]
ProcessingEventType = Union[
    ProcessingEvent.WillFetchFirstBlock, ProcessingEvent.FetchNextBlockFailed,
    ProcessingEvent.WillSend, ProcessingEvent.DidSend,
    ProcessingEvent.SendFailed, ProcessingEvent.WillFetchNextBlock,
    ProcessingEvent.FetchNextBlockFailed, ProcessingEvent.MessageExpired]
AccountForExecutorType = Union[
    AccountForExecutor.NoAccount, AccountForExecutor.Uninit,
    AccountForExecutor.Account]
AddressStringFormatType = Union[
    AddressStringFormat.AccountId, AddressStringFormat.Hex,
    AddressStringFormat.Base64]
ParamsOfAppDebotBrowserType = Union[
    ParamsOfAppDebotBrowser.Log, ParamsOfAppDebotBrowser.Switch,
    ParamsOfAppDebotBrowser.SwitchCompleted,
    ParamsOfAppDebotBrowser.ShowAction, ParamsOfAppDebotBrowser.Input,
    ParamsOfAppDebotBrowser.GetSigningBox, ParamsOfAppDebotBrowser.InvokeDebot]
