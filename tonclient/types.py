"""
Everscale binding types.
https://github.com/tonlabs/TON-SDK/tree/master/docs/reference/types-and-methods
"""
import json
from asyncio.selector_events import BaseSelectorEventLoop
from enum import Enum
from io import StringIO
from typing import Dict, Union, Any, List, Callable


class BaseTypedType:
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
        """Dict from object"""
        return {'type': self.type}


ResponseHandler = Callable[[Any, int, Union[BaseSelectorEventLoop, None]], None]


# CLIENT module
class ClientErrorCode(int, Enum):
    """Client module error codes"""

    NOT_IMPLEMENTED = 1
    INVALID_HEX = 2
    INVALID_BASE64 = 3
    INVALID_ADDRESS = 4
    CALLBACK_PARAMS_CANT_BE_CONVERTED_TO_JSON = 5
    WEBSOCKET_CONNECT_ERROR = 6
    WEBSOCKET_RECEIVE_ERROR = 7
    WEBSOCKET_SEND_ERROR = 8
    HTTP_CLIENT_CREATE_ERROR = 9
    HTTP_REQUEST_CREATE_ERROR = 10
    HTTP_REQUEST_SEND_ERROR = 11
    HTTP_REQUEST_PARSE_ERROR = 12
    CALLBACK_NOT_REGISTERED = 13
    NET_MODULE_NOT_INIT = 14
    INVALID_CONFIG = 15
    CANNOT_CREATE_RUNTIME = 16
    INVALID_CONTEXT_HANDLE = 17
    CANNOT_SERIALIZE_RESULT = 18
    CANNOT_SERIALIZE_ERROR = 19
    CANNOT_CONVERT_JS_VALUE_TO_JSON = 20
    CANNOT_RECEIVE_SPAWNED_RESULT = 21
    SET_TIMER_ERROR = 22
    INVALID_PARAMS = 23
    CONTRACTS_ADDRESS_CONVERSION_FAILED = 24
    UNKNOWN_FUNCTION = 25
    APP_REQUEST_ERROR = 26
    NO_SUCH_REQUEST = 27
    CANNOT_SEND_REQUEST_RESULT = 28
    CANNOT_RECEIVE_REQUEST_RESULT = 29
    CANNOT_PARSE_REQUEST_RESULT = 30
    UNEXPECTED_CALLBACK_RESPONSE = 31
    CANNOT_PARSE_NUMBER = 32
    INTERNAL_ERROR = 33
    INVALID_HANDLE = 34
    LOCAL_STORAGE_ERROR = 35


class ClientError:
    """Client error object"""

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


class ClientConfig:
    """Client config object"""

    def __init__(
        self,
        network: 'NetworkConfig' = None,
        boc: 'BocConfig' = None,
        crypto: 'CryptoConfig' = None,
        abi: 'AbiConfig' = None,
        proofs: 'ProofsConfig' = None,
        local_storage_path: str = None,
    ):
        """
        :param network:
        :param crypto:
        :param abi:
        :param boc:
        :param proofs:
        :param local_storage_path: For file based storage is a folder name
            where SDK will store its data. For browser based is a browser
            async storage key prefix.
            Default (recommended) value is "~/.tonclient" for native environments
            and ".tonclient" for web-browser
        """
        self.network = network or NetworkConfig(server_address='http://localhost')
        self.crypto = crypto or CryptoConfig()
        self.abi = abi or AbiConfig()
        self.boc = boc or BocConfig()
        self.proofs = proofs or ProofsConfig()
        self.local_storage_path = local_storage_path

    @property
    def dict(self):
        """Dict from object"""
        return {
            'network': self.network.dict,
            'crypto': self.crypto.dict,
            'abi': self.abi.dict,
            'boc': self.boc.dict,
            'proofs': self.proofs.dict,
            'local_storage_path': self.local_storage_path,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ClientConfig':
        """Object from dict"""
        return ClientConfig(
            network=NetworkConfig(**data['network']),
            crypto=CryptoConfig(**data['crypto']),
            abi=AbiConfig(**data['abi']),
            boc=BocConfig(**data['boc']),
            proofs=ProofsConfig(**data['proofs']),
            local_storage_path=data['local_storage_path'],
        )


class NetworkQueriesProtocol(str, Enum):
    """
    Network protocol used to perform GraphQL queries
        HTTP - Each GraphQL query uses separate HTTP request
        WS - All GraphQL queries will be served using single web socket connection
    """

    HTTP = 'HTTP'
    WS = 'WS'


class NetworkConfig:
    """Network config object"""

    def __init__(
        self,
        server_address: str = None,
        endpoints: List[str] = None,
        network_retries_count: int = None,
        reconnect_timeout: int = None,
        max_reconnect_timeout: int = None,
        message_retries_count: int = None,
        message_processing_timeout: int = None,
        query_timeout: int = None,
        wait_for_timeout: int = None,
        out_of_sync_threshold: int = None,
        sending_endpoint_count: int = None,
        access_key: str = None,
        latency_detection_interval: int = None,
        max_latency: int = None,
        queries_protocol: 'NetworkQueriesProtocol' = None,
        first_remp_status_timeout: int = None,
        next_remp_status_timeout: int = None,
    ):
        """
        :param server_address: DApp Server public address. For instance,
                for `net.ton.dev/graphql` GraphQL endpoint the server
                address will be net.ton.dev
        :param endpoints: List of DApp Server addresses. Any correct URL
                format can be specified, including IP addresses.
                This parameter is prevailing over `server_address`
        :param network_retries_count: (DEPRECATED) The number of automatic
                network retries that SDK performs in case of connection
                problems. The default value is 5
        :param reconnect_timeout: (DEPRECATED) Timeout between reconnect
                attempts
        :param max_reconnect_timeout: Maximum time for sequential reconnections
                in ms. Default value is 120000 (2 min)
        :param message_retries_count: The number of automatic message
                processing retries that SDK performs in case of
                `Message Expired (507)` error - but only for those messages
                which local emulation was successful or failed with replay
                protection error. The default value is 5
        :param message_processing_timeout: Timeout that is used to process
                message delivery for the contracts which ABI does not include
                "expire" header. If the message is not delivered within the
                specified timeout the appropriate error occurs
        :param wait_for_timeout: Maximum timeout that is used for query
                response in ms. The default value is 40000 (40 sec)
        :param out_of_sync_threshold: Maximum time difference between server
                and client. If client's device time is out of sync and
                difference is more than the threshold then error will occur.
                Also, the error will occur if the specified threshold is more
                than `message_processing_timeout / 2`.
                The default value is 15000 (15 sec)
        :param sending_endpoint_count: Maximum number of randomly chosen
                endpoints the library uses to send message.
                The default value is 2 endpoints
        :param access_key: Access key to GraphQL API. At the moment is not
                used in production
        :param latency_detection_interval: Frequency of sync latency detection.
                Library periodically checks the current endpoint for blockchain
                data synchronization latency. If the latency (time-lag) is
                less than `NetworkConfig.max_latency` then library selects
                another endpoint.
                Must be specified in milliseconds. Default is 60000 (1 min)
        :param max_latency: Maximum value for the endpoint's blockchain data
                synchronization latency (time-lag). Library periodically checks
                the current endpoint for blockchain data synchronization
                latency. If the latency (time-lag) is less than
                `NetworkConfig.max_latency` then library selects another
                endpoint.
                Must be specified in milliseconds. Default is 60000 (1 min)
        :param query_timeout: Default timeout for http requests.
                It is used when no timeout specified for the request to limit
                the answer waiting time. If no answer received during the
                timeout requests ends with error.
                Must be specified in milliseconds. Default is 60000 (1 min)
        :param queries_protocol: Queries protocol
        :param first_remp_status_timeout: First REMP status awaiting timeout.
                If no status recieved during the timeout than fallback transaction
                scenario is activated
        :param next_remp_status_timeout: Subsequent REMP status awaiting timeout.
                If no status recieved during the timeout than fallback transaction
                scenario is activated
        """
        self.server_address = server_address
        self.endpoints = endpoints
        self.network_retries_count = network_retries_count
        self.max_reconnect_timeout = max_reconnect_timeout
        self.message_retries_count = message_retries_count
        self.message_processing_timeout = message_processing_timeout
        self.wait_for_timeout = wait_for_timeout
        self.out_of_sync_threshold = out_of_sync_threshold
        self.reconnect_timeout = reconnect_timeout
        self.sending_endpoint_count = sending_endpoint_count
        self.access_key = access_key
        self.latency_detection_interval = latency_detection_interval
        self.max_latency = max_latency
        self.query_timeout = query_timeout
        self.queries_protocol = queries_protocol
        self.first_remp_status_timeout = first_remp_status_timeout
        self.next_remp_status_timeout = next_remp_status_timeout

    @property
    def dict(self):
        """Dict from object"""
        return {
            'server_address': self.server_address,
            'endpoints': self.endpoints,
            'network_retries_count': self.network_retries_count,
            'max_reconnect_timeout': self.max_reconnect_timeout,
            'message_retries_count': self.message_retries_count,
            'message_processing_timeout': self.message_processing_timeout,
            'wait_for_timeout': self.wait_for_timeout,
            'out_of_sync_threshold': self.out_of_sync_threshold,
            'reconnect_timeout': self.reconnect_timeout,
            'sending_endpoint_count': self.sending_endpoint_count,
            'access_key': self.access_key,
            'latency_detection_interval': self.latency_detection_interval,
            'max_latency': self.max_latency,
            'query_timeout': self.query_timeout,
            'queries_protocol': self.queries_protocol,
            'first_remp_status_timeout': self.first_remp_status_timeout,
            'next_remp_status_timeout': self.next_remp_status_timeout,
        }


class CryptoConfig:
    """Crypto config object"""

    def __init__(
        self,
        mnemonic_dictionary: int = None,
        mnemonic_word_count: int = None,
        hdkey_derivation_path: str = None,
    ):
        """
        :param mnemonic_dictionary: Mnemonic dictionary that will be used by
                default in crypto functions. If not specified, 1 dictionary
                will be used
        :param mnemonic_word_count: Mnemonic word count that will be used by
                default in crypto functions. If not specified the default
                value will be 12
        :param hdkey_derivation_path: Derivation path that will be used by
                default in crypto functions. If not specified
                `m/44'/396'/0'/0/0` will be used
        """
        self.mnemonic_dictionary = mnemonic_dictionary
        self.mnemonic_word_count = mnemonic_word_count
        self.hdkey_derivation_path = hdkey_derivation_path

    @property
    def dict(self):
        """Dict from object"""
        return {
            'mnemonic_dictionary': self.mnemonic_dictionary,
            'mnemonic_word_count': self.mnemonic_word_count,
            'hdkey_derivation_path': self.hdkey_derivation_path,
        }


class AbiConfig:
    """ABI config object"""

    def __init__(
        self,
        workchain: int = None,
        message_expiration_timeout: int = None,
        message_expiration_timeout_grow_factor: Union[int, float] = None,
    ):
        """
        :param workchain: Workchain id that is used by default in DeploySet
        :param message_expiration_timeout: Message lifetime for contracts
                which ABI includes "expire" header. The default value is 40 sec
        :param message_expiration_timeout_grow_factor: Factor that increases
                the expiration timeout for each retry. The default value is 1.5
        """
        self.workchain = workchain
        self.message_expiration_timeout = message_expiration_timeout
        self.message_expiration_timeout_grow_factor = (
            message_expiration_timeout_grow_factor
        )

    @property
    def dict(self):
        """Dict from object"""
        return {
            'workchain': self.workchain,
            'message_expiration_timeout': self.message_expiration_timeout,
            'message_expiration_timeout_grow_factor': self.message_expiration_timeout_grow_factor,
        }


class BocConfig:
    """BOC config object"""

    def __init__(self, cache_max_size: int = None):
        """
        :param cache_max_size: Maximum BOC cache size in kilobytes.
                Default is 10 MB
        """
        self.cache_max_size = cache_max_size

    @property
    def dict(self):
        """Dict from object"""
        return {'cache_max_size': self.cache_max_size}


class ProofsConfig:
    """Proofs config object"""

    def __init__(self, cache_in_local_storage: bool = None):
        """
        :param cache_in_local_storage: Cache proofs in the local storage.
            Default is `true`. If this value is set to `true`, downloaded
            proofs and master-chain BOCs are saved into the persistent
            local storage (e.g. file system for native environments or browser's
            IndexedDB for the web); otherwise all the data is cached only in memory
            in current client's context and will be lost after destruction of the client
        """
        self.cache_in_local_storage = cache_in_local_storage

    @property
    def dict(self):
        """Dict from object"""
        return {'cache_in_local_storage': self.cache_in_local_storage}


class BuildInfoDependency:
    """BuildInfoDependency"""

    def __init__(self, name: str, git_commit: str):
        """
        :param name: Dependency name. Usually it is a crate name
        :param git_commit: Git commit hash of the related repository
        """
        self.name = name
        self.git_commit = git_commit


class ParamsOfAppRequest:
    """ParamsOfAppRequest"""

    def __init__(self, app_request_id: int, request_data: Any):
        """
        :param app_request_id: Request ID. Should be used in
                `resolve_app_request` call
        :param request_data: Request describing data
        """
        self.app_request_id = app_request_id
        self.request_data = request_data


class AppRequestResult:
    """AppRequestResult"""

    class Error:
        """Error occurred during request processing"""

        def __init__(self, text: str):
            """
            :param text: Error description
            """
            self.text = text

        @property
        def dict(self):
            """Dict from object"""
            return {'type': 'Error', 'text': self.text}

    class Ok:
        """Request processed successfully"""

        def __init__(self, result: Any):
            """
            :param result: Request processing result
            """
            self.result = result

        @property
        def dict(self):
            """Dict from object"""
            return {'type': 'Ok', 'result': self.result}


class ResultOfGetApiReference:
    """ResultOfGetApiReference"""

    def __init__(self, api: Any):
        """
        :param api: API
        """
        self.api = api


class ResultOfVersion:
    """ResultOfVersion"""

    def __init__(self, version: str):
        """
        :param version: Core Library version
        """
        self.version = version


class ResultOfBuildInfo:
    """ResultOfBuildInfo"""

    def __init__(self, build_number: int, dependencies: List['BuildInfoDependency']):
        """
        :param build_number: Build number assigned to this build by the CI
        :param dependencies: Fingerprint of the most important dependencies
        """
        self.build_number = build_number
        self.dependencies = dependencies

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ResultOfBuildInfo':
        """Object from dict"""
        if data['dependencies']:
            data['dependencies'] = [
                BuildInfoDependency(**d) for d in data['dependencies']
            ]
        return ResultOfBuildInfo(**data)


class ParamsOfResolveAppRequest:
    """ParamsOfResolveAppRequest"""

    def __init__(self, app_request_id: int, result: 'AppRequestResultType'):
        """
        :param app_request_id: Request ID received from SDK
        :param result: Result of request processing
        """
        self.app_request_id = app_request_id
        self.result = result

    @property
    def dict(self):
        """Dict from object"""
        return {'app_request_id': self.app_request_id, 'result': self.result.dict}


# ABI module
AbiHandle = int


class AbiErrorCode(int, Enum):
    """ABI error codes"""

    REQUIRED_ADDRESS_MISSING_FOR_ENCODE_MESSAGE = 301
    REQUIRED_CALL_SET_MISSING_FOR_ENCODE_MESSAGE = 302
    INVALID_JSON = 303
    INVALID_MESSAGE = 304
    ENCODE_DEPLOY_MESSAGE_FAILED = 305
    ENCODE_RUN_MESSAGE_FAILED = 306
    ATTACH_SIGNATURE_FAILED = 307
    INVALID_TVC_IMAGE = 308
    REQUIRED_PUBLIC_KEY_MISSING_FOR_FUNCTION_HEADER = 309
    INVALID_SIGNER = 310
    INVALID_ABI = 311
    INVALID_FUNCTION_ID = 312
    INVALID_DATA = 313
    ENCODE_INITIAL_DATA_FAILED = 314


class Abi:
    """Abi"""

    class Contract(BaseTypedType):
        """Abi.Contract"""

        def __init__(self, value: 'AbiContract'):
            """
            :param value:
            """
            super(Abi.Contract, self).__init__(type='Contract')
            self.value = value

        @property
        def dict(self):
            return {**super(Abi.Contract, self).dict, 'value': self.value.dict}

    class Json(BaseTypedType):
        """Abi.Json"""

        def __init__(self, value: str):
            """
            :param value:
            """
            super(Abi.Json, self).__init__(type='Json')
            self.value = value

        @property
        def dict(self):
            return {**super(Abi.Json, self).dict, 'value': self.value}

    class Handle(BaseTypedType):
        """Abi.Handle"""

        def __init__(self, value: 'AbiHandle'):
            """
            :param value:
            """
            super(Abi.Handle, self).__init__(type='Handle')
            self.value = value

        @property
        def dict(self):
            return {**super(Abi.Handle, self).dict, 'value': self.value}

    class Serialized(BaseTypedType):
        """Abi.Serialized"""

        def __init__(self, value: 'AbiContract'):
            """
            :param value:
            """
            super(Abi.Serialized, self).__init__(type='Contract')
            self.value = value

        @property
        def dict(self):
            return {**super(Abi.Serialized, self).dict, 'value': self.value.dict}

    @staticmethod
    def from_path(path: str) -> Json:
        """Create Abi object from path"""
        with open(path, encoding='utf8') as fp:
            return Abi.Json(value=fp.read())


class AbiContract:
    """AbiContract"""

    def __init__(
        self,
        abi_version: int = None,
        version: str = None,
        header: List[str] = None,
        functions: List['AbiFunction'] = None,
        events: List['AbiEvent'] = None,
        data: List['AbiData'] = None,
        fields: List['AbiParam'] = None,
    ):
        """
        :param abi_version:
        :param version:
        :param header:
        :param functions:
        :param events:
        :param data:
        :param fields:
        """
        self.abi_version = abi_version
        self.version = version
        self.header = header or []
        self.functions = functions or []
        self.events = events or []
        self.data = data or []
        self.fields = fields or []

    @property
    def dict(self):
        """Dict from object"""
        return {
            'abi_version': self.abi_version,
            'version': self.version,
            'header': self.header,
            'functions': [f.dict for f in self.functions],
            'events': [e.dict for e in self.events],
            'data': [d.dict for d in self.data],
            'fields': [f.dict for f in self.fields],
        }


class AbiFunction:
    """AbiFunction"""

    def __init__(
        self,
        name: str,
        inputs: List['AbiParam'],
        outputs: List['AbiParam'],
        id: str = None,
    ):
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
        """Dict from object"""
        return {
            'name': self.name,
            'inputs': [i.dict for i in self.inputs],
            'outputs': [o.dict for o in self.outputs],
            'id': self.id,
        }


class AbiEvent:
    """AbiEvent"""

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
        """Dict from object"""
        return {
            'name': self.name,
            'inputs': [i.dict for i in self.inputs],
            'id': self.id,
        }


class AbiData:
    """AbiData"""

    def __init__(
        self, key: int, name: str, type: str, components: List['AbiParam'] = None
    ):
        """
        :param key:
        :param name:
        :param type:
        :param components:
        """
        self.key = key
        self.name = name
        self.type = type
        self.components = components or []

    @property
    def dict(self):
        """Dict from object"""
        return {
            'key': self.key,
            'name': self.name,
            'type': self.type,
            'components': [c.dict for c in self.components],
        }


class AbiParam:
    """AbiParam"""

    def __init__(self, name: str, type: str, components: List['AbiParam'] = None):
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
        """Dict from object"""
        return {
            'name': self.name,
            'type': self.type,
            'components': [c.dict for c in self.components],
        }


class FunctionHeader:
    """
    The ABI function header.
    Includes several hidden function parameters that contract uses for
    security, message delivery monitoring and replay protection reasons.
    The actual set of header fields depends on the contract's ABI.
    If a contract's ABI does not include some headers, then they are
    not filled.
    """

    def __init__(self, expire: int = None, time: int = None, pubkey: str = None):
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
        """Dict from object"""
        return {'expire': self.expire, 'time': self.time, 'pubkey': self.pubkey}


class CallSet:
    """CallSet"""

    def __init__(
        self, function_name: str, header: 'FunctionHeader' = None, input: Any = None
    ):
        """
        :param function_name: Function name that is being called.
                Or function id encoded as string in `hex` (starting with 0x)
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
        """Dict from object"""
        return {
            'function_name': self.function_name,
            'header': self.header.dict,
            'input': self.input,
        }


class DeploySet:
    """DeploySet"""

    def __init__(
        self,
        tvc: str,
        workchain_id: int = None,
        initial_data: List[Dict[str, Any]] = None,
        initial_pubkey: str = None,
    ):
        """
        :param tvc: Content of TVC file encoded in `base64`
        :param workchain_id: Target workchain for destination address.
                Default is 0
        :param initial_data: List of initial values for contract's public
                variables
        :param initial_pubkey: Optional public key that can be provided in
                deploy set in order to substitute one in TVM file or provided
                by Signer.
                Public key resolving priority:
                    1. Public key from deploy set;
                    2. Public key, specified in TVM file;
                    3. Public key, provided by Signer
        """
        self.tvc = tvc
        self.workchain_id = workchain_id
        self.initial_data = initial_data
        self.initial_pubkey = initial_pubkey

    @property
    def dict(self):
        """Dict from object"""
        return {
            'tvc': self.tvc,
            'workchain_id': self.workchain_id,
            'initial_data': self.initial_data,
            'initial_pubkey': self.initial_pubkey,
        }


class Signer:
    """Signer"""

    class NoSigner(BaseTypedType):
        """No keys are provided. Creates an unsigned message"""

        def __init__(self):
            super(Signer.NoSigner, self).__init__(type='None')

    class External(BaseTypedType):
        """
        Only public key is provided in unprefixed hex string format to
        generate unsigned message and data_to_sign which can be signed later
        """

        def __init__(self, public_key: str):
            """
            :param public_key:
            """
            super(Signer.External, self).__init__(type='External')
            self.public_key = public_key

        @property
        def dict(self):
            return {**super(Signer.External, self).dict, 'public_key': self.public_key}

    class Keys(BaseTypedType):
        """Key pair is provided for signing"""

        def __init__(self, keys: 'KeyPair'):
            """
            :param keys:
            """
            super(Signer.Keys, self).__init__(type='Keys')
            self.keys = keys

        @property
        def dict(self):
            return {**super(Signer.Keys, self).dict, 'keys': self.keys.dict}

    class SigningBox(BaseTypedType):
        """
        Signing Box interface is provided for signing, allows DApps to sign
        messages using external APIs, such as HSM, cold wallet, etc.
        """

        def __init__(self, handle: 'SigningBoxHandle'):
            """
            :param handle:
            """
            super(Signer.SigningBox, self).__init__(type='SigningBox')
            self.handle = handle

        @property
        def dict(self):
            return {**super(Signer.SigningBox, self).dict, 'handle': self.handle}


class MessageBodyType(str, Enum):
    """Message body types"""

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
    """StateInitSource"""

    class Message(BaseTypedType):
        """Deploy message"""

        def __init__(self, source: 'MessageSourceType'):
            """
            :param source:
            """
            super(StateInitSource.Message, self).__init__(type='Message')
            self.source = source

        @property
        def dict(self):
            return {
                **super(StateInitSource.Message, self).dict,
                'source': self.source.dict,
            }

    class StateInit(BaseTypedType):
        """State init data"""

        def __init__(self, code: str, data: str, library: str = None):
            """
            :param code: Code BOC. Encoded in `base64`
            :param data: Data BOC. Encoded in `base64`
            :param library: Library BOC. Encoded in `base64`
            """
            super(StateInitSource.StateInit, self).__init__(type='StateInit')
            self.code = code
            self.data = data
            self.library = library

        @property
        def dict(self):
            return {
                **super(StateInitSource.StateInit, self).dict,
                'code': self.code,
                'data': self.data,
                'library': self.library,
            }

    class Tvc(BaseTypedType):
        """Content of the TVC file"""

        def __init__(
            self,
            tvc: str,
            public_key: str = None,
            init_params: 'StateInitParams' = None,
        ):
            """
            :param tvc: Content of the TVC file. Encoded in `base64`
            :param public_key:
            :param init_params:
            """
            super(StateInitSource.Tvc, self).__init__(type='Tvc')
            self.tvc = tvc
            self.public_key = public_key
            self.init_params = init_params

        @property
        def dict(self):
            init_params = (
                self.init_params.dict if self.init_params else self.init_params
            )

            return {
                **super(StateInitSource.Tvc, self).dict,
                'tvc': self.tvc,
                'public_key': self.public_key,
                'init_params': init_params,
            }


class StateInitParams:
    """StateInitParams"""

    def __init__(self, abi: 'AbiType', value: Any):
        """
        :param abi: One of Abi.*
        :param value:
        """
        self.abi = abi
        self.value = value

    @property
    def dict(self):
        """Dict from object"""
        return {'abi': self.abi.dict, 'value': self.value}


class MessageSource:
    """MessageSource"""

    class Encoded(BaseTypedType):
        """MessageSource.Encoded"""

        def __init__(self, message: str, abi: 'AbiType' = None):
            """
            :param message:
            :param abi:
            """
            super(MessageSource.Encoded, self).__init__(type='Encoded')
            self.message = message
            self.abi = abi

        @property
        def dict(self):
            return {
                **super(MessageSource.Encoded, self).dict,
                'message': self.message,
                'abi': self.abi.dict if self.abi else self.abi,
            }

    class EncodingParams(BaseTypedType):
        """MessageSource.EncodingParams"""

        def __init__(self, params: 'ParamsOfEncodeMessage'):
            """
            :param params:
            """
            super(MessageSource.EncodingParams, self).__init__(type='EncodingParams')
            self.params = params

        @property
        def dict(self):
            return {
                **super(MessageSource.EncodingParams, self).dict,
                **self.params.dict,
            }


class ParamsOfEncodeMessageBody:
    """ParamsOfEncodeMessageBody"""

    def __init__(
        self,
        abi: 'AbiType',
        call_set: 'CallSet',
        is_internal: bool,
        signer: 'SignerType',
        processing_try_index: int = None,
    ):
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
        """Dict from object"""
        return {
            'abi': self.abi.dict,
            'call_set': self.call_set.dict,
            'is_internal': self.is_internal,
            'signer': self.signer.dict,
            'processing_try_index': self.processing_try_index,
        }


class ResultOfEncodeMessageBody:
    """ResultOfEncodeMessageBody"""

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


class ParamsOfAttachSignatureToMessageBody:
    """ParamsOfAttachSignatureToMessageBody"""

    def __init__(self, abi: 'AbiType', public_key: str, message: str, signature: str):
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
        """Dict from object"""
        return {
            'abi': self.abi.dict,
            'public_key': self.public_key,
            'message': self.message,
            'signature': self.signature,
        }


class ResultOfAttachSignatureToMessageBody:
    """ResultOfAttachSignatureToMessageBody"""

    def __init__(self, body: str):
        """
        :param body:
        """
        self.body = body


class ParamsOfEncodeMessage:
    """ParamsOfEncodeMessage"""

    def __init__(
        self,
        abi: 'AbiType',
        signer: 'SignerType',
        address: str = None,
        deploy_set: 'DeploySet' = None,
        call_set: 'CallSet' = None,
        processing_try_index: int = None,
    ):
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
        """Dict from object"""
        deploy_set = self.deploy_set.dict if self.deploy_set else self.deploy_set
        call_set = self.call_set.dict if self.call_set else self.call_set

        return {
            'abi': self.abi.dict,
            'signer': self.signer.dict,
            'address': self.address,
            'deploy_set': deploy_set,
            'call_set': call_set,
            'processing_try_index': self.processing_try_index,
        }


class ResultOfEncodeMessage:
    """ResultOfEncodeMessage"""

    def __init__(
        self, message: str, address: str, message_id: str, data_to_sign: str = None
    ):
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


class ParamsOfAttachSignature:
    """ParamsOfAttachSignature"""

    def __init__(self, abi: 'AbiType', public_key: str, message: str, signature: str):
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
        """Dict from object"""
        return {
            'abi': self.abi.dict,
            'public_key': self.public_key,
            'message': self.message,
            'signature': self.signature,
        }


class ResultOfAttachSignature:
    """ResultOfAttachSignature"""

    def __init__(self, message: str, message_id: str):
        """
        :param message: Signed message BOC
        :param message_id: Message ID
        """
        self.message = message
        self.message_id = message_id


class ParamsOfDecodeMessage:
    """ParamsOfDecodeMessage"""

    def __init__(self, abi: 'AbiType', message: str, allow_partial: bool = False):
        """
        :param abi: Contract ABI
        :param message: Message BOC
        :param allow_partial: Flag allowing partial BOC decoding when ABI doesn't
                describe the full body BOC. Controls decoder behaviour when after
                decoding all described in ABI params there are some data left in BOC:
                `true` - return decoded values
                `false` - return error of incomplete BOC deserialization (default)

        """
        self.abi = abi
        self.message = message
        self.allow_partial = allow_partial

    @property
    def dict(self):
        """Dict from object"""
        return {
            'abi': self.abi.dict,
            'message': self.message,
            'allow_partial': self.allow_partial,
        }


class DecodedMessageBody:
    """DecodedMessageBody"""

    def __init__(
        self,
        body_type: 'MessageBodyType',
        name: str,
        value: Any = None,
        header: 'FunctionHeader' = None,
    ):
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
        """Object from dict"""
        if data['header']:
            data['header'] = FunctionHeader(**data['header'])

        return DecodedMessageBody(**data)


class ParamsOfDecodeMessageBody:
    """ParamsOfDecodeMessageBody"""

    def __init__(
        self, abi: 'AbiType', body: str, is_internal: bool, allow_partial: bool = False
    ):
        """
        :param abi: Contract ABI used to decode
        :param body: Message body BOC encoded in `base64`
        :param is_internal: True if the body belongs to the internal message
        :param allow_partial: Flag allowing partial BOC decoding when ABI doesn't
                describe the full body BOC. Controls decoder behaviour when after
                decoding all described in ABI params there are some data left in BOC:
                `true` - return decoded values
                `false` - return error of incomplete BOC deserialization (default)
        """
        self.abi = abi
        self.body = body
        self.is_internal = is_internal
        self.allow_partial = allow_partial

    @property
    def dict(self):
        """Dict from object"""
        return {
            'abi': self.abi.dict,
            'body': self.body,
            'is_internal': self.is_internal,
            'allow_partial': self.allow_partial,
        }


class ParamsOfEncodeAccount:
    """ParamsOfEncodeAccount"""

    def __init__(
        self,
        state_init: 'StateInitSourceType',
        balance: int = None,
        last_trans_lt: int = None,
        last_paid: int = None,
        boc_cache: 'BocCacheTypeType' = None,
    ):
        """
        :param state_init: Source of the account state init
        :param balance: Initial balance
        :param last_trans_lt: Initial value for the `last_trans_lt`
        :param last_paid: Initial value for the `last_paid`
        :param boc_cache: Cache type to put the result. The BOC itself
                returned if no cache type provided
        """
        self.state_init = state_init
        self.balance = balance
        self.last_trans_lt = last_trans_lt
        self.last_paid = last_paid
        self.boc_cache = boc_cache

    @property
    def dict(self):
        """Dict from object"""
        return {
            'state_init': self.state_init.dict,
            'balance': self.balance,
            'last_trans_lt': self.last_trans_lt,
            'last_paid': self.last_paid,
            'boc_cache': self.boc_cache,
        }


class ResultOfEncodeAccount:
    """ResultOfEncodeAccount"""

    def __init__(self, account: str, id: str):
        """
        :param account: Account BOC encoded in `base64`
        :param id: Account ID encoded in `hex`
        """
        self.account = account
        self.id = id


class ParamsOfEncodeInternalMessage:
    """ParamsOfEncodeInternalMessage"""

    def __init__(
        self,
        value: str,
        abi: 'AbiType' = None,
        address: str = None,
        deploy_set: 'DeploySet' = None,
        call_set: 'CallSet' = None,
        bounce: bool = None,
        enable_ihr: bool = None,
        src_address: str = None,
    ):
        """
        :param abi: Contract ABI. Can be None if both `deploy_set`
                and `call_set` are None
        :param value: Value in nanograms to be sent with message
        :param address: Target address the message will be sent to. Must be
                specified in case of non-deploy message
        :param deploy_set: Deploy parameters. Must be specified in case of
                deploy message
        :param call_set: Function call parameters. Must be specified in case
                of non-deploy message. In case of deploy message it is
                optional and contains parameters of the functions that will
                to be called upon deploy transaction
        :param bounce: Flag of bounceable message. Default is true
        :param enable_ihr: Enable Instant Hypercube Routing for the message.
                Default is false
        :param src_address: Source address of the message
        """
        self.abi = abi
        self.value = value
        self.address = address
        self.deploy_set = deploy_set
        self.call_set = call_set
        self.bounce = bounce
        self.enable_ihr = enable_ihr
        self.src_address = src_address

    @property
    def dict(self):
        """Dict from object"""
        abi = self.abi.dict if self.abi else self.abi
        deploy_set = self.deploy_set.dict if self.deploy_set else self.deploy_set
        call_set = self.call_set.dict if self.call_set else self.call_set

        return {
            'abi': abi,
            'value': self.value,
            'address': self.address,
            'deploy_set': deploy_set,
            'call_set': call_set,
            'bounce': self.bounce,
            'enable_ihr': self.enable_ihr,
            'src_address': self.src_address,
        }


class ResultOfEncodeInternalMessage:
    """ResultOfEncodeInternalMessage"""

    def __init__(self, message: str, address: str, message_id: str):
        """
        :param message: Message BOC encoded with `base64`
        :param address: Destination address
        :param message_id: Message id
        """
        self.message = message
        self.address = address
        self.message_id = message_id


class ParamsOfDecodeAccountData:
    """ParamsOfDecodeAccountData"""

    def __init__(self, abi: 'AbiType', data: str, allow_partial: bool = False):
        """
        :param abi: Contract ABI
        :param data: Data BOC or BOC handle
        :param allow_partial: Flag allowing partial BOC decoding when ABI doesn't
                describe the full body BOC. Controls decoder behaviour when after
                decoding all described in ABI params there are some data left in BOC:
                `true` - return decoded values
                `false` - return error of incomplete BOC deserialization (default)
        """
        self.abi = abi
        self.data = data
        self.allow_partial = allow_partial

    @property
    def dict(self):
        """Dict from object"""
        return {
            'abi': self.abi.dict,
            'data': self.data,
            'allow_partial': self.allow_partial,
        }


class ResultOfDecodeData:
    """ResultOfDecodeData"""

    def __init__(self, data: Dict[str, Any]):
        """
        :param data: Decoded data as a JSON structure
        """
        self.data = data


class ParamsOfUpdateInitialData:
    """ParamsOfUpdateInitialData"""

    def __init__(
        self,
        data: str,
        abi: 'AbiType' = None,
        initial_data: Any = None,
        initial_pubkey: str = None,
        boc_cache: 'BocCacheTypeType' = None,
    ):
        """
        :param data: Data BOC or BOC handle
        :param abi: Contract ABI
        :param initial_data: List of initial values for contract's static
                variables.
                `abi` parameter should be provided to set initial data
        :param initial_pubkey: Initial account owner's public key to set
                into account data
        :param boc_cache: Cache type to put the result.
                The BOC itself returned if no cache type provided
        """
        self.data = data
        self.abi = abi
        self.initial_data = initial_data
        self.initial_pubkey = initial_pubkey
        self.boc_cache = boc_cache

    @property
    def dict(self):
        """Dict from object"""
        abi = self.abi.dict if self.abi else self.abi
        boc_cache = self.boc_cache.dict if self.boc_cache else self.boc_cache
        return {
            'data': self.data,
            'abi': abi,
            'initial_data': self.initial_data,
            'initial_pubkey': self.initial_pubkey,
            'boc_cache': boc_cache,
        }


class ResultOfUpdateInitialData:
    """ResultOfUpdateInitialData"""

    def __init__(self, data: str):
        """
        :param data: Updated data BOC or BOC handle
        """
        self.data = data


class ParamsOfDecodeInitialData:
    """ParamsOfDecodeInitialData"""

    def __init__(self, data: str, abi: 'AbiType' = None, allow_partial: bool = False):
        """
        :param data: Data BOC or BOC handle
        :param abi: Contract ABI.
                Initial data is decoded if this parameter is provided
        :param allow_partial: Flag allowing partial BOC decoding when ABI doesn't
                describe the full body BOC. Controls decoder behaviour when after
                decoding all described in ABI params there are some data left in BOC:
                `true` - return decoded values
                `false` - return error of incomplete BOC deserialization (default)
        """
        self.data = data
        self.abi = abi
        self.allow_partial = allow_partial

    @property
    def dict(self):
        """Dict from object"""
        abi = self.abi.dict if self.abi else self.abi
        return {
            'data': self.data,
            'abi': abi,
            'allow_partial': self.allow_partial,
        }


class ParamsOfEncodeInitialData:
    """ParamsOfEncodeInitialData"""

    def __init__(
        self,
        abi: 'AbiType' = None,
        initial_data: Dict[str, Any] = None,
        initial_pubkey: str = None,
        boc_cache: 'BocCacheTypeType' = None,
    ):
        """
        :param abi: Contract ABI
        :param initial_data: Initial values for contract's static variables.
                `abi` parameter should be provided to set initial data
        :param initial_pubkey: Initial account owner's public key to set
                into account data
        :param boc_cache: Cache type to put the result.
                The BOC itself returned, if no cache type provided
        """
        self.abi = abi
        self.initial_data = initial_data
        self.initial_pubkey = initial_pubkey
        self.boc_cache = boc_cache

    @property
    def dict(self):
        """Dict from object"""
        abi = self.abi.dict if self.abi else self.abi
        boc_cache = self.boc_cache.dict if self.boc_cache else self.boc_cache
        return {
            'abi': abi,
            'initial_data': self.initial_data,
            'initial_pubkey': self.initial_pubkey,
            'boc_cache': boc_cache,
        }


class ResultOfEncodeInitialData:
    """ResultOfEncodeInitialData"""

    def __init__(self, data: str):
        """
        :param data: Updated data BOC or BOC handle
        """
        self.data = data


class ResultOfDecodeInitialData:
    """ResultOfDecodeInitialData"""

    def __init__(self, initial_pubkey: str, initial_data: Any = None):
        """
        :param initial_pubkey: Initial account owner's public key
        :param initial_data: List of initial values of contract's public
                variables. Initial data is decoded if `abi` input parameter
                is provided
        """
        self.initial_pubkey = initial_pubkey
        self.initial_data = initial_data


class ParamsOfDecodeBoc:
    """ParamsOfDecodeBoc"""

    def __init__(self, params: List['AbiParam'], boc: str, allow_partial: bool):
        """
        :param params: Parameters to decode from BOC
        :param boc: Data BOC or BOC handle
        :param allow_partial:
        """
        self.params = params
        self.boc = boc
        self.allow_partial = allow_partial

    @property
    def dict(self):
        """Dict from object"""
        return {
            'params': [p.dict for p in self.params],
            'boc': self.boc,
            'allow_partial': self.allow_partial,
        }


class ResultOfDecodeBoc:
    """ResultOfDecodeBoc"""

    def __init__(self, data: Any):
        """
        :param data: Decoded data as a JSON structure
        """
        self.data = data


class ParamsOfAbiEncodeBoc:
    """ParamsOfAbiEncodeBoc"""

    def __init__(
        self, params: List['AbiParam'], data: Any, boc_cache: 'BocCacheTypeType' = None
    ):
        """
        :param params: Parameters to encode into BOC
        :param data: Parameters and values as a JSON structure
        :param boc_cache: Cache type to put the result.
                The BOC itself returned if no cache type provided
        """
        self.params = params
        self.data = data
        self.boc_cache = boc_cache

    @property
    def dict(self):
        """Dict from object"""
        boc_cache = self.boc_cache.dict if self.boc_cache else self.boc_cache
        return {
            'params': [p.dict for p in self.params],
            'data': self.data,
            'boc_cache': boc_cache,
        }


class ResultOfAbiEncodeBoc:
    """ResultOfAbiEncodeBoc"""

    def __init__(self, boc: str):
        """
        :param boc: BOC encoded as `base64`
        """
        self.boc = boc


# BOC module
class BocErrorCode(int, Enum):
    """BOC module error codes"""

    INVALID_BOC = 201
    SERIALIZATION_ERROR = 202
    INAPPROPRIATE_BLOCK = 203
    MISSING_SOURCE_BOC = 204
    INSUFFICIENT_CACHE_SIZE = (205,)
    BOC_REF_NOT_FOUND = (206,)
    INVALID_BOC_REF = 207


class ParamsOfParse:
    """ParamsOfParse"""

    def __init__(self, boc: str):
        """
        :param boc: BOC encoded as `base64`
        """
        self.boc = boc

    @property
    def dict(self):
        """Dict from object"""
        return {'boc': self.boc}


class ResultOfParse:
    """ResultOfParse"""

    def __init__(self, parsed: Any):
        """
        :param parsed: JSON containing parsed BOC
        """
        self.parsed = parsed


class ParamsOfParseShardstate:
    """ParamsOfParseShardstate"""

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
        """Dict from object"""
        return {'boc': self.boc, 'id': self.id, 'workchain_id': self.workchain_id}


class ParamsOfGetBlockchainConfig:
    """ParamsOfGetBlockchainConfig"""

    def __init__(self, block_boc: str):
        """
        :param block_boc: Key block BOC or zero state BOC encoded as `base64`
        """
        self.block_boc = block_boc

    @property
    def dict(self):
        """Dict from object"""
        return {'block_boc': self.block_boc}


class ResultOfGetBlockchainConfig:
    """ResultOfGetBlockchainConfig"""

    def __init__(self, config_boc: str):
        """
        :param config_boc: Blockchain config BOC encoded as `base64`
        """
        self.config_boc = config_boc


class ParamsOfGetBocHash:
    """ParamsOfGetBocHash"""

    def __init__(self, boc: str):
        """
        :param boc: BOC encoded as `base64`
        """
        self.boc = boc

    @property
    def dict(self):
        """Dict from object"""
        return {'boc': self.boc}


class ResultOfGetBocHash:
    """ResultOfGetBocHash"""

    def __init__(self, hash: str):
        """
        :param hash: BOC root hash encoded with `hex`
        """
        self.hash = hash


class ParamsOfGetCodeFromTvc:
    """ParamsOfGetCodeFromTvc"""

    def __init__(self, tvc: str):
        """
        :param tvc: Contract TVC image encoded as `base64`
        """
        self.tvc = tvc

    @property
    def dict(self):
        """Dict from object"""
        return {'tvc': self.tvc}


class ResultOfGetCodeFromTvc:
    """ResultOfGetCodeFromTvc"""

    def __init__(self, code: str):
        """
        :param code: Contract code encoded as `base64`
        """
        self.code = code


class BocCacheType:
    """BocCacheType"""

    class Pinned(BaseTypedType):
        """BocCacheType.Pinned"""

        def __init__(self, pin: str):
            """
            :param pin: Pin the BOC with `pin` name. Such BOC will not be
                    removed from cache until it is unpinned
            """
            super(BocCacheType.Pinned, self).__init__(type='Pinned')
            self.pin = pin

        @property
        def dict(self):
            return {**super(BocCacheType.Pinned, self).dict, 'pin': self.pin}

    class Unpinned(BaseTypedType):
        """BocCacheType.Unpinned"""

        def __init__(self):
            super(BocCacheType.Unpinned, self).__init__(type='Unpinned')


class ParamsOfBocCacheGet:
    """ParamsOfBocCacheGet"""

    def __init__(self, boc_ref: str):
        """
        :param boc_ref: Reference to the cached BOC
        """
        self.boc_ref = boc_ref

    @property
    def dict(self):
        """Dict from object"""
        return {'boc_ref': self.boc_ref}


class ResultOfBocCacheGet:
    """ResultOfBocCacheGet"""

    def __init__(self, boc: str = None):
        """
        :param boc: BOC encoded as `base64`
        """
        self.boc = boc


class ParamsOfBocCacheSet:
    """ParamsOfBocCacheSet"""

    def __init__(self, boc: str, cache_type: 'BocCacheTypeType'):
        """
        :param boc: BOC encoded as `base64` or BOC reference
        :param cache_type: Cache type
        """
        self.boc = boc
        self.cache_type = cache_type

    @property
    def dict(self):
        """Dict from object"""
        return {'boc': self.boc, 'cache_type': self.cache_type.dict}


class ResultOfBocCacheSet:
    """ResultOfBocCacheSet"""

    def __init__(self, boc_ref: str):
        """
        :param boc_ref: Reference to the cached BOC
        """
        self.boc_ref = boc_ref


class ParamsOfBocCacheUnpin:
    """ParamsOfBocCacheUnpin"""

    def __init__(self, pin: str, boc_ref: str = None):
        """
        :param pin: Pinned name
        :param boc_ref: Reference to the cached BOC. If it is provided then
                only referenced BOC is unpinned
        """
        self.pin = pin
        self.boc_ref = boc_ref

    @property
    def dict(self):
        """Dict from object"""
        return {'pin': self.pin, 'boc_ref': self.boc_ref}


class BuilderOp:
    """BuilderOp"""

    class Integer(BaseTypedType):
        """BuilderOp.Integer"""

        def __init__(self, size: int, value: Any):
            """
            Append integer to cell data
            :param size: Bit size of the value
            :param value: Number containing integer number, e.g. 123, -123.
                    - Decimal string. e.g. "123", "-123".
                    - 0x prefixed hexadecimal string, e.g 0x123, 0X123, -0x123
            """
            super(BuilderOp.Integer, self).__init__(type='Integer')
            self.size = size
            self.value = value

        @property
        def dict(self):
            return {
                **super(BuilderOp.Integer, self).dict,
                'size': self.size,
                'value': self.value,
            }

    class BitString(BaseTypedType):
        """BuilderOp.BitString"""

        def __init__(self, value: str):
            """
            Append bit string to cell data
            :param value: Bit string content using bitstring notation.
                    See `TON VM specification 1.0`.
                    Contains hexadecimal string representation:
                        - Can end with `_` tag;
                        - Can be prefixed with `x` or `X`;
                        - Can be prefixed with `x{` or `X{` and ended with `}`.

                    Contains binary string represented as a sequence
                    of `0` and `1` prefixed with `n` or `N`.
                    Examples:
                        `1AB`, `x1ab`, `X1AB`, `x{1abc}`, `X{1ABC}`
                        `2D9_`, `x2D9_`, `X2D9_`, `x{2D9_}`, `X{2D9_}`
                        `n00101101100`, `N00101101100`
            """
            super(BuilderOp.BitString, self).__init__(type='BitString')
            self.value = value

        @property
        def dict(self):
            return {**super(BuilderOp.BitString, self).dict, 'value': self.value}

    class Cell(BaseTypedType):
        """BuilderOp.Cell"""

        def __init__(self, builder: List['BuilderOpType']):
            """
            Append ref to nested cells
            :param builder: Nested cell builder
            """
            super(BuilderOp.Cell, self).__init__(type='Cell')
            self.builder = builder

        @property
        def dict(self):
            return {
                **super(BuilderOp.Cell, self).dict,
                'builder': [b.dict for b in self.builder],
            }

    class CellBoc(BaseTypedType):
        """BuilderOp.CellBoc"""

        def __init__(self, boc: str):
            """
            Append ref to nested cell
            :param boc: Nested cell BOC encoded with `base64` or BOC cache key
            """
            super(BuilderOp.CellBoc, self).__init__(type='CellBoc')
            self.boc = boc

        @property
        def dict(self):
            return {**super(BuilderOp.CellBoc, self).dict, 'boc': self.boc}

    class Address(BaseTypedType):
        """BuilderOp.Address"""

        def __init__(self, address: str):
            """
            :params address: Address in a common `workchain:account` or `base64` format
            """
            super().__init__(type='Address')
            self.address = address

        @property
        def dict(self):
            return {**super(BuilderOp.Address, self).dict, 'address': self.address}


class ParamsOfEncodeBoc:
    """ParamsOfEncodeBoc"""

    def __init__(
        self, builder: List['BuilderOpType'], boc_cache: 'BocCacheTypeType' = None
    ):
        """
        :param builder: Cell builder operations
        :param boc_cache: Cache type to put the result. The BOC itself
                returned if no cache type provided
        """
        self.builder = builder
        self.boc_cache = boc_cache

    @property
    def dict(self):
        """Dict from object"""
        boc_cache = self.boc_cache.dict if self.boc_cache else self.boc_cache
        return {'builder': [b.dict for b in self.builder], 'boc_cache': boc_cache}


class ResultOfEncodeBoc:
    """ResultOfEncodeBoc"""

    def __init__(self, boc: str):
        """
        :param boc: Encoded cell BOC or BOC cache key
        """
        self.boc = boc


class ParamsOfGetCodeSalt:
    """ParamsOfGetCodeSalt"""

    def __init__(self, code: str, boc_cache: 'BocCacheTypeType' = None):
        """
        :param code: Contract code BOC encoded as `base64` or code BOC handle
        :param boc_cache: Cache type to put the result.
                The BOC itself returned if no cache type provided
        """
        self.code = code
        self.boc_cache = boc_cache

    @property
    def dict(self):
        """Dict from object"""
        boc_cache = self.boc_cache.dict if self.boc_cache else self.boc_cache
        return {'code': self.code, 'boc_cache': boc_cache}


class ResultOfGetCodeSalt:
    """ResultOfGetCodeSalt"""

    def __init__(self, salt: str = None):
        """
        :param salt: Contract code salt if present
        """
        self.salt = salt


class ParamsOfSetCodeSalt:
    """ParamsOfSetCodeSalt"""

    def __init__(self, code: str, salt: str, boc_cache: 'BocCacheTypeType' = None):
        """
        :param code: Contract code BOC encoded as `base64` or code BOC handle
        :param salt: Code salt to set
        :param boc_cache: Cache type to put the result.
                The BOC itself returned if no cache type provided.
        """
        self.code = code
        self.salt = salt
        self.boc_cache = boc_cache

    @property
    def dict(self):
        """Dict from object"""
        boc_cache = self.boc_cache.dict if self.boc_cache else self.boc_cache
        return {'code': self.code, 'salt': self.salt, 'boc_cache': boc_cache}


class ResultOfSetCodeSalt:
    """ResultOfSetCodeSalt"""

    def __init__(self, code: str):
        """
        :param code: Contract code with salt set
        """
        self.code = code


class ParamsOfDecodeTvc:
    """ParamsOfDecodeTvc"""

    def __init__(self, tvc: str, boc_cache: 'BocCacheTypeType' = None):
        """
        :param tvc: Contract TVC image BOC encoded as `base64` or BOC handle
        :param boc_cache: Cache type to put the result.
                The BOC itself returned if no cache type provided
        """
        self.tvc = tvc
        self.boc_cache = boc_cache

    @property
    def dict(self):
        """Dict from object"""
        boc_cache = self.boc_cache.dict if self.boc_cache else self.boc_cache
        return {'tvc': self.tvc, 'boc_cache': boc_cache}


class ResultOfDecodeTvc:
    """ResultOfDecodeTvc"""

    def __init__(
        self,
        code: str = None,
        code_hash: str = None,
        code_depth: int = None,
        data: str = None,
        data_hash: str = None,
        data_depth: int = None,
        library: str = None,
        tick: bool = None,
        tock: bool = None,
        split_depth: int = None,
        compiler_version: str = None,
    ):
        """
        :param code: Contract code BOC encoded as `base64` or BOC handle
        :param code_hash: Contract code hash
        :param code_depth: Contract code depth
        :param data: Contract data BOC encoded as `base64` or BOC handle
        :param data_hash: Contract data hash
        :param data_depth: Contract data depth
        :param library: Contract library BOC encoded as `base64` or BOC handle
        :param tick: `special.tick` field.
                Specifies the contract ability to handle tick transactions
        :param tock: `special.tock` field.
                Specifies the contract ability to handle tock transactions
        :param split_depth: Is present and non-zero only in instances
                of large smart contracts
        :param compiler_version: Compiler version, for example `sol 0.49.0`
        """
        self.code = code
        self.code_hash = code_hash
        self.code_depth = code_depth
        self.data = data
        self.data_hash = data_hash
        self.data_depth = data_depth
        self.library = library
        self.tick = tick
        self.tock = tock
        self.split_depth = split_depth
        self.compiler_version = compiler_version


class ParamsOfEncodeTvc:
    """ParamsOfEncodeTvc"""

    def __init__(
        self,
        code: str = None,
        data: str = None,
        library: str = None,
        tick: bool = None,
        tock: bool = None,
        split_depth: int = None,
        boc_cache: 'BocCacheTypeType' = None,
    ):
        """
        :param code: Contract code BOC encoded as `base64` or BOC handle
        :param data: Contract data BOC encoded as `base64` or BOC handle
        :param library: Contract library BOC encoded as `base64` or BOC handle
        :param tick: `special.tick` field.
                Specifies the contract ability to handle tick transactions
        :param tock: `special.tock` field.
                Specifies the contract ability to handle tock transactions
        :param split_depth:  Is present and non-zero only in instances
                of large smart contracts
        :param boc_cache: Cache type to put the result.
                The BOC itself returned if no cache type provided
        """
        self.code = code
        self.data = data
        self.library = library
        self.tick = tick
        self.tock = tock
        self.split_depth = split_depth
        self.boc_cache = boc_cache

    @property
    def dict(self):
        """Dict from object"""
        boc_cache = self.boc_cache.dict if self.boc_cache else self.boc_cache
        return {
            'code': self.code,
            'data': self.data,
            'library': self.library,
            'tick': self.tick,
            'tock': self.tock,
            'split_depth': self.split_depth,
            'boc_cache': boc_cache,
        }


class ResultOfEncodeTvc:
    """ResultOfEncodeTvc"""

    def __init__(self, tvc: str):
        """
        :param tvc: Contract TVC image BOC encoded as `base64` or
                BOC handle of boc_cache parameter was specified
        """
        self.tvc = tvc


class ParamsOfGetCompilerVersion:
    """ParamsOfGetCompilerVersion"""

    def __init__(self, code: str):
        """
        :param code: Contract code BOC encoded as `base64` or code BOC handle
        """
        self.code = code

    @property
    def dict(self):
        """Dict from object"""
        return {'code': self.code}


class ResultOfGetCompilerVersion:
    """ResultOfGetCompilerVersion"""

    def __init__(self, version: str = None):
        """
        :param version: Compiler version, e.g. `sol 0.49.0`
        """
        self.version = version


class ParamsOfGetBocDepth:
    """ParamsOfGetBocDepth"""

    def __init__(self, boc: str):
        """
        :param boc: BOC encoded as `base64` or BOC handle
        """
        self.boc = boc

    @property
    def dict(self):
        """Dict from object"""
        return {'boc': self.boc}


class ResultOfGetBocDepth:
    """ResultOfGetBocDepth"""

    def __init__(self, depth: int):
        """
        :param depth: BOC root cell depth
        """
        self.depth = depth


class ParamsOfEncodeExternalInMessage:
    """ParamsOfEncodeExternalInMessage"""

    def __init__(
        self,
        dst: str,
        src: str = None,
        init: str = None,
        body: str = None,
        boc_cache: 'BocCacheTypeType' = None,
    ):
        """
        :param dst: Destination address
        :param src: Source address
        :param init: Bag of cells with state init (used in deploy messages)
        :param body: Bag of cells with the message body encoded as `base64`
        :param boc_cache: Cache type to put the result.
                The BOC itself returned if no cache type provided
        """
        self.dst = dst
        self.src = src
        self.init = init
        self.body = body
        self.boc_cache = boc_cache

    @property
    def dict(self):
        """Dict from object"""
        boc_cache = self.boc_cache.dict if self.boc_cache else self.boc_cache
        return {
            'dst': self.dst,
            'src': self.src,
            'init': self.init,
            'body': self.body,
            'boc_cache': boc_cache,
        }


class ResultOfEncodeExternalInMessage:
    """ResultOfEncodeExternalInMessage"""

    def __init__(self, message: str, message_id: str):
        """
        :param message: Message BOC encoded with `base64`
        :param message_id: Message id
        """
        self.message = message
        self.message_id = message_id


# CRYPTO module
SigningBoxHandle = int

EncryptionBoxHandle = int

CryptoBoxHandle = int


class CryptoErrorCode(int, Enum):
    """Crypto module error codes"""

    INVALID_PUBLIC_KEY = 100
    INVALID_SECRET_KEY = 101
    INVALID_KEY = 102
    INVALID_FACTORIZE_CHALLENGE = 106
    INVALID_BIGINT = 107
    SCRYPT_FAILED = 108
    INVALID_KEY_SIZE = 109
    NACL_SECRET_BOX_FAILED = 110
    NACL_BOX_FAILED = 111
    NACL_SIGN_FAILED = 112
    BIP39_INVALID_ENTROPY = 113
    BIP39_INVALID_PHRASE = 114
    BIP32_INVALID_KEY = 115
    BIP32_INVALID_DERIVE_PATH = 116
    BIP39_INVALID_DICTIONARY = 117
    BIP39_INVALID_WORD_COUNT = 118
    MNEMONIC_GENERATION_FAILED = 119
    MNEMONIC_FROM_ENTROPY_FAILED = 120
    SIGNING_BOX_NOT_REGISTERED = 121
    INVALID_SIGNATURE = 122
    ENCRYPTION_BOX_NOT_REGISTERED = 123
    INVALID_IV_SIZE = 124
    UNSUPPORTED_CIPHER_MODE = 125
    CANNOT_CREATE_CIPHER = 126
    ENCRYPT_DATA_ERROR = 127
    DECRYPT_DATA_ERROR = 128
    IV_REQUIRED = 129
    CRYPTO_BOX_NOT_REGISTERED = 130
    INVALID_CRYPTO_BOX_TYPE = 131
    CRYPTO_BOX_SECRET_SERIALIZATION_ERROR = 132
    CRYPTO_BOX_SECRET_DESERIALIZATION_ERROR = 133
    INVALID_NONCE_SIZE = 134


class MnemonicDictionary(int, Enum):
    """Mnemonic dictionary types"""

    TON = 0
    ENGLISH = 1
    CHINESE_SIMPLIFIED = 2
    CHINESE_TRADITIONAL = 3
    FRENCH = 4
    ITALIAN = 5
    JAPANESE = 6
    KOREAN = 7
    SPANISH = 8


class KeyPair:
    """Keypair object representation"""

    def __init__(self, public: str, secret: str):
        """
        :param public: Public key - 64 symbols `hex` string
        :param secret: Private key - 64 symbols `hex` string
        """
        self.public = public
        self.secret = secret

    @property
    def dict(self) -> Dict[str, str]:
        """Dict from keypair"""
        return {'public': self.public, 'secret': self.secret}

    @property
    def binary(self) -> bytes:
        """Keypair in binary format"""
        return bytes.fromhex(f'{self.secret}{self.public}')

    @staticmethod
    def load(path: str, is_binary: bool) -> 'KeyPair':
        """Load keypair from file"""
        if is_binary:
            with open(path, 'rb') as fp:
                keys = fp.read().hex()
                keys = {'public': keys[64:], 'secret': keys[:64]}
        else:
            with open(path, 'r') as fp:
                keys = json.loads(fp.read())

        return KeyPair(**keys)

    def dump(self, path: str, as_binary: bool) -> None:
        """Dump keypair to file"""
        if as_binary:
            with open(path, 'wb') as fp:
                fp.write(self.binary)
        else:
            with open(path, 'w') as fp:
                json.dump(self.dict, fp)

    @staticmethod
    def load_io(io: StringIO, as_binary: bool = False) -> 'KeyPair':
        """Load keypair from StringIO"""
        data = io.getvalue()
        keys = (
            json.loads(data)
            if not as_binary
            else {'public': data[64:], 'secret': data[:64]}
        )

        return KeyPair(**keys)

    def dump_io(self, io: StringIO, as_binary: bool = False):
        """Dump keypair to StringIO"""
        keys = json.dumps(self.dict) if not as_binary else self.binary.hex()
        io.write(keys)


class ParamsOfFactorize:
    """ParamsOfFactorize"""

    def __init__(self, composite: str):
        """
        :param composite: Hexadecimal representation of u64 composite number
        """
        self.composite = composite

    @property
    def dict(self):
        """Dict from object"""
        return {'composite': self.composite}


class ResultOfFactorize:
    """ResultOfFactorize"""

    def __init__(self, factors: List[str]):
        """
        :param factors: Two factors of composite or empty if composite
                can't be factorized
        """
        self.factors = factors


class ParamsOfModularPower:
    """ParamsOfModularPower"""

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
        """Dict from object"""
        return {'base': self.base, 'exponent': self.exponent, 'modulus': self.modulus}


class ResultOfModularPower:
    """ResultOfModularPower"""

    def __init__(self, modular_power: str):
        """
        :param modular_power: Result of modular exponentiation
        """
        self.modular_power = modular_power


class ParamsOfTonCrc16:
    """ParamsOfTonCrc16"""

    def __init__(self, data: str):
        """
        :param data: Input data for CRC calculation. Encoded with `base64`
        """
        self.data = data

    @property
    def dict(self):
        """Dict from object"""
        return {'data': self.data}


class ResultOfTonCrc16:
    """ResultOfTonCrc16"""

    def __init__(self, crc: int):
        """
        :param crc: Calculated CRC for input data
        """
        self.crc = crc


class ParamsOfGenerateRandomBytes:
    """ParamsOfGenerateRandomBytes"""

    def __init__(self, length: int):
        """
        :param length: Size of random byte array
        """
        self.length = length

    @property
    def dict(self):
        """Dict from object"""
        return {'length': self.length}


class ResultOfGenerateRandomBytes:
    """ResultOfGenerateRandomBytes"""

    def __init__(self, bytes: str):
        """
        :param bytes: Generated bytes encoded in `base64`
        """
        self.bytes = bytes


class ParamsOfConvertPublicKeyToTonSafeFormat:
    """ParamsOfConvertPublicKeyToTonSafeFormat"""

    def __init__(self, public_key: str):
        """
        :param public_key: Public key - 64 symbols `hex` string
        """
        self.public_key = public_key

    @property
    def dict(self):
        """Dict from object"""
        return {'public_key': self.public_key}


class ResultOfConvertPublicKeyToTonSafeFormat:
    """ResultOfConvertPublicKeyToTonSafeFormat"""

    def __init__(self, ton_public_key: str):
        """
        :param ton_public_key: Public key represented in TON safe format
        """
        self.ton_public_key = ton_public_key


class ParamsOfSign:
    """ParamsOfSign"""

    def __init__(self, unsigned: str, keys: 'KeyPair'):
        """
        :param unsigned: Data that must be signed encoded in `base64`
        :param keys: Sign keys
        """
        self.unsigned = unsigned
        self.keys = keys

    @property
    def dict(self):
        """Dict from object"""
        return {'unsigned': self.unsigned, 'keys': self.keys.dict}


class ResultOfSign:
    """ResultOfSign"""

    def __init__(self, signed: str, signature: str):
        """
        :param signed: Signed data combined with signature encoded in `base64`
        :param signature: Signature encoded in `hex`
        """
        self.signed = signed
        self.signature = signature


class ParamsOfVerifySignature:
    """ParamsOfVerifySignature"""

    def __init__(self, signed: str, public: str):
        """
        :param signed: Signed data that must be verified encoded in `base64`
        :param public: Signer's public key - 64 symbols `hex` string
        """
        self.signed = signed
        self.public = public

    @property
    def dict(self):
        """Dict from object"""
        return {'signed': self.signed, 'public': self.public}


class ResultOfVerifySignature:
    """ResultOfVerifySignature"""

    def __init__(self, unsigned: str):
        """
        :param unsigned: Unsigned data encoded in `base64`
        """
        self.unsigned = unsigned


class ParamsOfHash:
    """ParamsOfHash"""

    def __init__(self, data: str):
        """
        :param data: Input data for hash calculation. Encoded with `base64`
        """
        self.data = data

    @property
    def dict(self):
        """Dict from object"""
        return {'data': self.data}


class ResultOfHash:
    """ResultOfHash"""

    def __init__(self, hash: str):
        """
        :param hash: Hash of input data
        """
        self.hash = hash


class ParamsOfScrypt:
    """ParamsOfScrypt"""

    def __init__(
        self, password: str, salt: str, log_n: int, r: int, p: int, dk_len: int
    ):
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
        """Dict from object"""
        return {
            'password': self.password,
            'salt': self.salt,
            'log_n': self.log_n,
            'r': self.r,
            'p': self.p,
            'dk_len': self.dk_len,
        }


class ResultOfScrypt:
    """ResultOfScrypt"""

    def __init__(self, key: str):
        """
        :param key: Derived key. Encoded with `hex`
        """
        self.key = key


class ParamsOfNaclSignKeyPairFromSecret:
    """ParamsOfNaclSignKeyPairFromSecret"""

    def __init__(self, secret: str):
        """
        :param secret: Secret key - unprefixed 0-padded to 64
                symbols `hex` string
        """
        self.secret = secret

    @property
    def dict(self):
        """Dict from object"""
        return {'secret': self.secret}


class ParamsOfNaclSign:
    """ParamsOfNaclSign"""

    def __init__(self, unsigned: str, secret: str):
        """
        :param unsigned: Data that must be signed encoded in `base64`
        :param secret: Signer's secret key.
                Unprefixed 0-padded to 128 symbols hex string (concatenation
                of 64 symbols secret and 64 symbols public keys).
                See `nacl_sign_keypair_from_secret_key`
        """
        self.unsigned = unsigned
        self.secret = secret

    @property
    def dict(self):
        """Dict from object"""
        return {'unsigned': self.unsigned, 'secret': self.secret}


class ResultOfNaclSign:
    """ResultOfNaclSign"""

    def __init__(self, signed: str):
        """
        :param signed: Signed data, encoded in `base64`
        """
        self.signed = signed


class ParamsOfNaclSignOpen:
    """ParamsOfNaclSignOpen"""

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
        """Dict from object"""
        return {'signed': self.signed, 'public': self.public}


class ResultOfNaclSignOpen:
    """ResultOfNaclSignOpen"""

    def __init__(self, unsigned: str):
        """
        :param unsigned: Unsigned data, encoded in `base64`
        """
        self.unsigned = unsigned


class ResultOfNaclSignDetached:
    """ResultOfNaclSignDetached"""

    def __init__(self, signature: str):
        """
        :param signature: Signature encoded in `hex`
        """
        self.signature = signature


class ParamsOfNaclBoxKeyPairFromSecret:
    """ParamsOfNaclBoxKeyPairFromSecret"""

    def __init__(self, secret: str):
        """
        :param secret: Secret key - unprefixed 0-padded to 64
                symbols `hex` string
        """
        self.secret = secret

    @property
    def dict(self):
        """Dict from object"""
        return {'secret': self.secret}


class ParamsOfNaclBox:
    """ParamsOfNaclBox"""

    def __init__(self, decrypted: str, nonce: str, their_public: str, secret: str):
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
        """Dict from object"""
        return {
            'decrypted': self.decrypted,
            'nonce': self.nonce,
            'their_public': self.their_public,
            'secret': self.secret,
        }


class ResultOfNaclBox:
    """ResultOfNaclBox"""

    def __init__(self, encrypted: str):
        """
        :param encrypted: Encrypted data encoded in `base64`
        """
        self.encrypted = encrypted


class ParamsOfNaclBoxOpen:
    """ParamsOfNaclBoxOpen"""

    def __init__(self, encrypted: str, nonce: str, their_public: str, secret: str):
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
        """Dict from object"""
        return {
            'encrypted': self.encrypted,
            'nonce': self.nonce,
            'their_public': self.their_public,
            'secret': self.secret,
        }


class ResultOfNaclBoxOpen:
    """ResultOfNaclBoxOpen"""

    def __init__(self, decrypted: str):
        """
        :param decrypted: Decrypted data encoded in `base64`
        """
        self.decrypted = decrypted


class ParamsOfNaclSecretBox:
    """ParamsOfNaclSecretBox"""

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
        """Dict from object"""
        return {'decrypted': self.decrypted, 'nonce': self.nonce, 'key': self.key}


class ParamsOfNaclSecretBoxOpen:
    """ParamsOfNaclSecretBoxOpen"""

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
        """Dict from object"""
        return {'encrypted': self.encrypted, 'nonce': self.nonce, 'key': self.key}


class ParamsOfMnemonicWords:
    """ParamsOfMnemonicWords"""

    def __init__(self, dictionary: 'MnemonicDictionary' = None):
        """
        :param dictionary: Dictionary identifier
        """
        self.dictionary = dictionary

    @property
    def dict(self):
        """Dict from object"""
        return {'dictionary': self.dictionary}


class ResultOfMnemonicWords:
    """ResultOfMnemonicWords"""

    def __init__(self, words: str):
        """
        :param words: The list of mnemonic words
        """
        self.words = words


class ParamsOfMnemonicFromRandom:
    """ParamsOfMnemonicFromRandom"""

    def __init__(self, dictionary: 'MnemonicDictionary' = None, word_count: int = None):
        """
        :param dictionary: Dictionary identifier
        :param word_count: Mnemonic word count
        """
        self.dictionary = dictionary
        self.word_count = word_count

    @property
    def dict(self):
        """Dict from object"""
        return {'dictionary': self.dictionary, 'word_count': self.word_count}


class ResultOfMnemonicFromRandom:
    """ResultOfMnemonicFromRandom"""

    def __init__(self, phrase: str):
        """
        :param phrase: String of mnemonic words
        """
        self.phrase = phrase


class ParamsOfMnemonicFromEntropy:
    """ParamsOfMnemonicFromEntropy"""

    def __init__(
        self,
        entropy: str,
        dictionary: 'MnemonicDictionary' = None,
        word_count: int = None,
    ):
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
        """Dict from object"""
        return {
            'entropy': self.entropy,
            'dictionary': self.dictionary,
            'word_count': self.word_count,
        }


class ResultOfMnemonicFromEntropy:
    """ResultOfMnemonicFromEntropy"""

    def __init__(self, phrase: str):
        """
        :param phrase: String of mnemonic words
        """
        self.phrase = phrase


class ParamsOfMnemonicVerify:
    """ParamsOfMnemonicVerify"""

    def __init__(
        self,
        phrase: str,
        dictionary: 'MnemonicDictionary' = None,
        word_count: int = None,
    ):
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
        """Dict from object"""
        return {
            'phrase': self.phrase,
            'dictionary': self.dictionary,
            'word_count': self.word_count,
        }


class ResultOfMnemonicVerify:
    """ResultOfMnemonicVerify"""

    def __init__(self, valid: bool):
        """
        :param valid: Flag indicating if the mnemonic is valid or not
        """
        self.valid = valid


class ParamsOfMnemonicDeriveSignKeys:
    """ParamsOfMnemonicDeriveSignKeys"""

    def __init__(
        self,
        phrase: str,
        path: str = None,
        dictionary: 'MnemonicDictionary' = None,
        word_count: int = None,
    ):
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
        """Dict from object"""
        return {
            'phrase': self.phrase,
            'path': self.path,
            'dictionary': self.dictionary,
            'word_count': self.word_count,
        }


class ParamsOfHDKeyXPrvFromMnemonic:
    """ParamsOfHDKeyXPrvFromMnemonic"""

    def __init__(
        self,
        phrase: str,
        dictionary: 'MnemonicDictionary' = None,
        word_count: int = None,
    ):
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
        """Dict from object"""
        return {
            'phrase': self.phrase,
            'dictionary': self.dictionary,
            'word_count': self.word_count,
        }


class ResultOfHDKeyXPrvFromMnemonic:
    """ResultOfHDKeyXPrvFromMnemonic"""

    def __init__(self, xprv: str):
        """
        :param xprv: Serialized extended master private key
        """
        self.xprv = xprv


class ParamsOfHDKeyDeriveFromXPrv:
    """ParamsOfHDKeyDeriveFromXPrv"""

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
        """Dict from object"""
        return {
            'xprv': self.xprv,
            'child_index': self.child_index,
            'hardened': self.hardened,
        }


class ResultOfHDKeyDeriveFromXPrv:
    """ResultOfHDKeyDeriveFromXPrv"""

    def __init__(self, xprv: str):
        """
        :param xprv: Serialized extended private key
        """
        self.xprv = xprv


class ParamsOfHDKeyDeriveFromXPrvPath:
    """ParamsOfHDKeyDeriveFromXPrvPath"""

    def __init__(self, xprv: str, path: str):
        """
        :param xprv: Serialized extended private key
        :param path: Derivation path, for instance "m/44'/396'/0'/0/0"
        """
        self.xprv = xprv
        self.path = path

    @property
    def dict(self):
        """Dict from object"""
        return {'xprv': self.xprv, 'path': self.path}


class ResultOfHDKeyDeriveFromXPrvPath:
    """ResultOfHDKeyDeriveFromXPrvPath"""

    def __init__(self, xprv: str):
        """
        :param xprv: Derived serialized extended private key
        """
        self.xprv = xprv


class ParamsOfHDKeySecretFromXPrv:
    """ParamsOfHDKeySecretFromXPrv"""

    def __init__(self, xprv: str):
        """
        :param xprv: Serialized extended private key
        """
        self.xprv = xprv

    @property
    def dict(self):
        """Dict from object"""
        return {'xprv': self.xprv}


class ResultOfHDKeySecretFromXPrv:
    """ResultOfHDKeySecretFromXPrv"""

    def __init__(self, secret: str):
        """
        :param secret: Private key - 64 symbols `hex` string
        """
        self.secret = secret


class ParamsOfHDKeyPublicFromXPrv:
    """ParamsOfHDKeyPublicFromXPrv"""

    def __init__(self, xprv: str):
        """
        :param xprv: Serialized extended private key
        """
        self.xprv = xprv

    @property
    def dict(self):
        """Dict from object"""
        return {'xprv': self.xprv}


class ResultOfHDKeyPublicFromXPrv:
    """ResultOfHDKeyPublicFromXPrv"""

    def __init__(self, public: str):
        """
        :param public: Public key - 64 symbols `hex` string
        """
        self.public = public


class ParamsOfChaCha20:
    """ParamsOfChaCha20"""

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
        """Dict from object"""
        return {'data': self.data, 'key': self.key, 'nonce': self.nonce}


class ResultOfChaCha20:
    """ResultOfChaCha20"""

    def __init__(self, data: str):
        """
        :param data: Encrypted/decrypted data. Encoded with `base64`
        """
        self.data = data


class RegisteredSigningBox:
    """RegisteredSigningBox"""

    def __init__(self, handle: 'SigningBoxHandle'):
        """
        :param handle: Handle of the signing box
        """
        self.handle = handle

    @property
    def dict(self):
        """Dict from object"""
        return {'handle': self.handle}


class ParamsOfAppSigningBox:
    """ParamsOfAppSigningBox"""

    class GetPublicKey(BaseTypedType):
        """Get signing box public key"""

        def __init__(self):
            super(ParamsOfAppSigningBox.GetPublicKey, self).__init__(
                type='GetPublicKey'
            )

    class Sign(BaseTypedType):
        """Sign data"""

        def __init__(self, unsigned: str):
            """
            :param unsigned: Data to sign encoded as `base64`
            """
            super(ParamsOfAppSigningBox.Sign, self).__init__(type='Sign')
            self.unsigned = unsigned

        @property
        def dict(self):
            return {
                **super(ParamsOfAppSigningBox.Sign, self).dict,
                'unsigned': self.unsigned,
            }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ParamsOfAppSigningBoxType':
        """Object from dict"""
        kwargs = {k: v for k, v in data.items() if k != 'type'}
        return getattr(ParamsOfAppSigningBox, data['type'])(**kwargs)


class ResultOfAppSigningBox:
    """ResultOfAppSigningBox"""

    class GetPublicKey(BaseTypedType):
        """Result of getting public key"""

        def __init__(self, public_key: str):
            """
            :param public_key: Signing box public key
            """
            super(ResultOfAppSigningBox.GetPublicKey, self).__init__(
                type='GetPublicKey'
            )
            self.public_key = public_key

        @property
        def dict(self):
            return {
                **super(ResultOfAppSigningBox.GetPublicKey, self).dict,
                'public_key': self.public_key,
            }

    class Sign(BaseTypedType):
        """Result of signing data"""

        def __init__(self, signature: str):
            """
            :param signature: Data signature encoded as `hex`
            """
            super(ResultOfAppSigningBox.Sign, self).__init__(type='Sign')
            self.signature = signature

        @property
        def dict(self):
            return {
                **super(ResultOfAppSigningBox.Sign, self).dict,
                'signature': self.signature,
            }


class ResultOfSigningBoxGetPublicKey:
    """ResultOfSigningBoxGetPublicKey"""

    def __init__(self, pubkey: str):
        """
        :param pubkey: Public key of signing box
        """
        self.pubkey = pubkey


class ParamsOfSigningBoxSign:
    """ParamsOfSigningBoxSign"""

    def __init__(self, signing_box: 'SigningBoxHandle', unsigned: str):
        """
        :param signing_box: Signing Box handle
        :param unsigned: Unsigned user data. Must be encoded with `base64`
        """
        self.signing_box = signing_box
        self.unsigned = unsigned

    @property
    def dict(self):
        """Dict from object"""
        return {'signing_box': self.signing_box, 'unsigned': self.unsigned}


class ResultOfSigningBoxSign:
    """ResultOfSigningBoxSign"""

    def __init__(self, signature: str):
        """
        :param signature: Data signature. Encoded with `base64`
        """
        self.signature = signature


class ParamsOfNaclSignDetachedVerify:
    """ParamsOfNaclSignDetachedVerify"""

    def __init__(self, unsigned: str, signature: str, public: str):
        """
        :param unsigned: Unsigned data that must be verified.
                Encoded with `base64`
        :param signature: Signature that must be verified. Encoded with `hex`
        :param public: Signer's public key - unprefixed 0-padded to 64 symbols
                `hex` string
        """
        self.unsigned = unsigned
        self.signature = signature
        self.public = public

    @property
    def dict(self):
        """Dict from object"""
        return {
            'unsigned': self.unsigned,
            'signature': self.signature,
            'public': self.public,
        }


class ResultOfNaclSignDetachedVerify:
    """ResultOfNaclSignDetachedVerify"""

    def __init__(self, succeeded: bool):
        """
        :param succeeded: true if verification succeeded or false if it failed
        """
        self.succeeded = succeeded


class EncryptionBoxInfo:
    """Encryption box information"""

    def __init__(
        self,
        hdpath: str = None,
        algorithm: str = None,
        options: Any = None,
        public: Any = None,
    ):
        """
        :param hdpath: Derivation path, for instance "m/44'/396'/0'/0/0"
        :param algorithm: Cryptographic algorithm, used by this encryption box
        :param options: Options, depends on algorithm and specific encryption
                box implementation
        :param public: Public information, depends on algorithm
        """
        self.hdpath = hdpath
        self.algorithm = algorithm
        self.options = options
        self.public = public

    @property
    def dict(self):
        """Dict from object"""
        return {
            'hdpath': self.hdpath,
            'algorithm': self.algorithm,
            'options': self.options,
            'public': self.public,
        }


class RegisteredEncryptionBox:
    """RegisteredEncryptionBox"""

    def __init__(self, handle: 'EncryptionBoxHandle'):
        """
        :param handle: Handle of the encryption box
        """
        self.handle = handle

    @property
    def dict(self):
        """Dict from object"""
        return {'handle': self.handle}


class ParamsOfAppEncryptionBox:
    """Encryption box callbacks"""

    class GetInfo(BaseTypedType):
        """ParamsOfAppEncryptionBox.GetInfo"""

        def __init__(self):
            super(ParamsOfAppEncryptionBox.GetInfo, self).__init__(type='GetInfo')

    class Encrypt(BaseTypedType):
        """ParamsOfAppEncryptionBox.Encrypt"""

        def __init__(self, data: str):
            """
            :param data: Data, encoded in `base64`
            """
            super(ParamsOfAppEncryptionBox.Encrypt, self).__init__(type='Encrypt')
            self.data = data

        @property
        def dict(self):
            return {
                **super(ParamsOfAppEncryptionBox.Encrypt, self).dict,
                'data': self.data,
            }

    class Decrypt(BaseTypedType):
        """ParamsOfAppEncryptionBox.Decrypt"""

        def __init__(self, data: str):
            """
            :param data: Data, encoded in `base64`
            """
            super(ParamsOfAppEncryptionBox.Decrypt, self).__init__(type='Decrypt')
            self.data = data

        @property
        def dict(self):
            return {
                **super(ParamsOfAppEncryptionBox.Decrypt, self).dict,
                'data': self.data,
            }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ParamsOfAppEncryptionBoxType':
        """Object from dict"""
        kwargs = {k: v for k, v in data.items() if k != 'type'}
        return getattr(ParamsOfAppEncryptionBox, data['type'])(**kwargs)


class ResultOfAppEncryptionBox:
    """Returning values from signing box callbacks"""

    class GetInfo(BaseTypedType):
        """ResultOfAppEncryptionBox.GetInfo"""

        def __init__(self, info: 'EncryptionBoxInfo'):
            super(ResultOfAppEncryptionBox.GetInfo, self).__init__(type='GetInfo')
            self.info = info

        @property
        def dict(self):
            return {
                **super(ResultOfAppEncryptionBox.GetInfo, self).dict,
                'info': self.info.dict,
            }

    class Encrypt(BaseTypedType):
        """ResultOfAppEncryptionBox.Encrypt"""

        def __init__(self, data: str):
            """
            :param data: Encrypted data, encoded in `base64`
            """
            super(ResultOfAppEncryptionBox.Encrypt, self).__init__(type='Encrypt')
            self.data = data

        @property
        def dict(self):
            return {
                **super(ResultOfAppEncryptionBox.Encrypt, self).dict,
                'data': self.data,
            }

    class Decrypt(BaseTypedType):
        """ResultOfAppEncryptionBox.Decrypt"""

        def __init__(self, data: str):
            """
            :param data: Decrypted data, encoded in `base64`
            """
            super(ResultOfAppEncryptionBox.Decrypt, self).__init__(type='Decrypt')
            self.data = data

        @property
        def dict(self):
            return {
                **super(ResultOfAppEncryptionBox.Decrypt, self).dict,
                'data': self.data,
            }


class ParamsOfEncryptionBoxGetInfo:
    """ParamsOfEncryptionBoxGetInfo"""

    def __init__(self, encryption_box: 'EncryptionBoxHandle'):
        self.encryption_box = encryption_box

    @property
    def dict(self):
        """Dict from object"""
        return {'encryption_box': self.encryption_box}


class ResultOfEncryptionBoxGetInfo:
    """ResultOfEncryptionBoxGetInfo"""

    def __init__(self, info: 'EncryptionBoxInfo'):
        self.info = info

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ResultOfEncryptionBoxGetInfo':
        """Object from dict"""
        data['info'] = EncryptionBoxInfo(**data['info'])
        return ResultOfEncryptionBoxGetInfo(**data)


class ParamsOfEncryptionBoxEncrypt:
    """ParamsOfEncryptionBoxEncrypt"""

    def __init__(self, encryption_box: 'EncryptionBoxHandle', data: str):
        """
        :param encryption_box: Encryption box handle
        :param data: Data to be encrypted, encoded in `base64`
        """
        self.encryption_box = encryption_box
        self.data = data

    @property
    def dict(self):
        """Dict from object"""
        return {'encryption_box': self.encryption_box, 'data': self.data}


class ResultOfEncryptionBoxEncrypt:
    """ResultOfEncryptionBoxEncrypt"""

    def __init__(self, data: str):
        """
        :param data: Encrypted data, encoded in `base64`
        """
        self.data = data


class ParamsOfEncryptionBoxDecrypt:
    """ParamsOfEncryptionBoxDecrypt"""

    def __init__(self, encryption_box: 'EncryptionBoxHandle', data: str):
        """
        :param encryption_box: Encryption box handle
        :param data: Data to be decrypted, encoded in `base64`
        """
        self.encryption_box = encryption_box
        self.data = data

    @property
    def dict(self):
        """Dict from object"""
        return {'encryption_box': self.encryption_box, 'data': self.data}


class ResultOfEncryptionBoxDecrypt:
    """ResultOfEncryptionBoxDecrypt"""

    def __init__(self, data: str):
        """
        :param data: Decrypted data, encoded in `base64`
        """
        self.data = data


class CipherMode(str, Enum):
    """Cipher mode types"""

    CBC = 'CBC'
    CFB = 'CFB'
    CTR = 'CTR'
    ECB = 'ECB'
    OFB = 'OFB'


class EncryptionAlgorithm:
    """EncryptionAlgorithm"""

    class Aes(BaseTypedType):
        """EncryptionAlgorithm.Aes"""

        def __init__(self, mode: 'CipherMode', key: str, iv: str = None):
            super(EncryptionAlgorithm.Aes, self).__init__(type='AES')
            self.mode = mode
            self.key = key
            self.iv = iv

        @property
        def dict(self):
            return {
                **super(EncryptionAlgorithm.Aes, self).dict,
                'value': {'mode': self.mode, 'key': self.key, 'iv': self.iv},
            }

    class AesInfo:
        """EncryptionAlgorithm.AesInfo"""

        def __init__(self, cipher: 'CipherMode', iv: str = None):
            self.cipher = cipher
            self.iv = iv


class ParamsOfCreateEncryptionBox:
    """ParamsOfCreateEncryptionBox"""

    def __init__(self, algorithm: 'EncryptionAlgorithmType'):
        """
        :param algorithm: Encryption algorithm specifier including
                cipher parameters (key, IV, etc)
        """
        self.algorithm = algorithm

    @property
    def dict(self):
        """Dict from object"""
        return {'algorithm': self.algorithm.dict}


class CryptoBoxSecret:
    """CryptoBoxSecret types"""

    class RandomSeedPhrase(BaseTypedType):
        """
        Creates Crypto Box from a random seed phrase.
        This option can be used if a developer doesn't want the seed phrase
        to leave the core library's memory, where it is stored encrypted.

        This type should be used upon the first wallet initialization, all
        further initializations should use `EncryptedSecret` type instead.

        Get `encrypted_secret` with `get_crypto_box_info` function and store it
        on your side.
        """

        def __init__(self, dictionary: 'MnemonicDictionary', wordcount: int):
            super(CryptoBoxSecret.RandomSeedPhrase, self).__init__(
                type='RandomSeedPhrase'
            )
            self.dictionary = dictionary
            self.wordcount = wordcount

        @property
        def dict(self):
            return {
                **super(CryptoBoxSecret.RandomSeedPhrase, self).dict,
                'dictionary': self.dictionary,
                'wordcount': self.wordcount,
            }

    class PredefinedSeedPhrase(BaseTypedType):
        """
        Restores crypto box instance from an existing seed phrase.
        This type should be used when Crypto Box is initialized from a seed
        phrase, entered by a user.

        This type should be used only upon the first wallet initialization, all
        further initializations should use `EncryptedSecret` type instead.

        Get `encrypted_secret` with `get_crypto_box_info` function and store it on
        your side.
        """

        def __init__(
            self, phrase: str, dictionary: 'MnemonicDictionary', wordcount: int
        ):
            super(CryptoBoxSecret.PredefinedSeedPhrase, self).__init__(
                type='PredefinedSeedPhrase'
            )
            self.phrase = phrase
            self.dictionary = dictionary
            self.wordcount = wordcount

        @property
        def dict(self):
            return {
                **super(CryptoBoxSecret.PredefinedSeedPhrase, self).dict,
                'phrase': self.phrase,
                'dictionary': self.dictionary,
                'wordcount': self.wordcount,
            }

    class EncryptedSecret(BaseTypedType):
        """
        Use this type for wallet reinitializations, when you already have
        `encrypted_secret` on hands.
        To get `encrypted_secret`, use `get_crypto_box_info` function after you
        initialized your crypto box for the first time.

        It is an object, containing seed phrase or private key
        (now we support only seed phrase), encrypted with `secret_encryption_salt`
        and password from `password_provider`.

        Note that if you want to change salt or password provider, then you need
        to reinitialize the wallet with `PredefinedSeedPhrase`, then get
        `EncryptedSecret` via `get_crypto_box_info`, store it somewhere, and only
        after that initialize the wallet with `EncryptedSecret` type.
        """

        def __init__(self, encrypted_secret: str):
            super(CryptoBoxSecret.EncryptedSecret, self).__init__(
                type='EncryptedSecret'
            )
            self.encrypted_secret = encrypted_secret

        @property
        def dict(self):
            return {
                **super(CryptoBoxSecret.EncryptedSecret, self).dict,
                'encrypted_secret': self.encrypted_secret,
            }


class BoxEncryptionAlgorithm:
    """BoxEncryptionAlgorithm types"""

    class ChaCha20(BaseTypedType):
        """BoxEncryptionAlgorithm.ChaCha20"""

        def __init__(self, nonce: str):
            """
            :param nonce: 96-bit nonce. Must be encoded with `hex`
            """
            super(BoxEncryptionAlgorithm.ChaCha20, self).__init__(type='ChaCha20')
            self.nonce = nonce

        @property
        def dict(self):
            return {
                **super(BoxEncryptionAlgorithm.ChaCha20, self).dict,
                'value': {
                    'nonce': self.nonce,
                },
            }

    class NaclBox(BaseTypedType):
        """BoxEncryptionAlgorithm.NaclBox"""

        def __init__(self, their_public: str, nonce: str):
            """
            :param their_public: 256-bit key. Must be encoded with `hex`
            :param nonce: 96-bit nonce. Must be encoded with `hex`
            """
            super(BoxEncryptionAlgorithm.NaclBox, self).__init__(type='NaclBox')
            self.their_public = their_public
            self.nonce = nonce

        @property
        def dict(self):
            return {
                **super(BoxEncryptionAlgorithm.NaclBox, self).dict,
                'value': {
                    'their_public': self.their_public,
                    'nonce': self.nonce,
                },
            }

    class NaclSecretBox(BaseTypedType):
        """BoxEncryptionAlgorithm.NaclSecretBox"""

        def __init__(self, nonce: str):
            """
            :param nonce: Nonce in `hex`
            """
            super(BoxEncryptionAlgorithm.NaclSecretBox, self).__init__(
                type='NaclSecretBox'
            )
            self.nonce = nonce

        @property
        def dict(self):
            return {
                **super(BoxEncryptionAlgorithm.NaclSecretBox, self).dict,
                'value': {
                    'nonce': self.nonce,
                },
            }


class RegisteredCryptoBox:
    """RegisteredCryptoBox"""

    def __init__(self, handle: 'CryptoBoxHandle'):
        self.handle = handle

    @property
    def dict(self):
        return {'handle': self.handle}


class ParamsOfCreateCryptoBox:
    """ParamsOfCreateCryptoBox"""

    def __init__(self, secret_encryption_salt: str, secret: 'CryptoBoxSecretType'):
        """
        :param secret_encryption_salt: Salt used for secret encryption.
                For example, a mobile device can use device ID as salt
        :param secret: Cryptobox secret
        """
        self.secret_encryption_salt = secret_encryption_salt
        self.secret = secret

    @property
    def dict(self):
        return {
            'secret_encryption_salt': self.secret_encryption_salt,
            'secret': self.secret.dict,
        }


class ResultOfGetCryptoBoxInfo:
    """ResultOfGetCryptoBoxInfo"""

    def __init__(self, encrypted_secret: str):
        """
        :param encrypted_secret: Secret (seed phrase) encrypted
                with salt and password
        """
        self.encrypted_secret = encrypted_secret


class ResultOfGetCryptoBoxSeedPhrase:
    """ResultOfGetCryptoBoxSeedPhrase"""

    def __init__(self, phrase: str, dictionary: 'MnemonicDictionary', wordcount: int):
        """
        :param phrase:
        :param dictionary:
        :param wordcount:
        """
        self.phrase = phrase
        self.dictionary = dictionary
        self.wordcount = wordcount

    @property
    def dict(self):
        return {
            'phrase': self.phrase,
            'dictionary': self.dictionary,
            'wordcount': self.wordcount,
        }


class ParamsOfGetSigningBoxFromCryptoBox:
    """ParamsOfGetSigningBoxFromCryptoBox"""

    def __init__(
        self, handle: 'CryptoBoxHandle', hdpath: str = None, secret_lifetime: int = None
    ):
        """
        :param handle: Crypto Box Handle
        :param hdpath: HD key derivation path.
                By default, Everscale HD path is used
        :param secret_lifetime: Store derived secret for this lifetime (in ms).
                The timer starts after each signing box operation.
                Secrets will be deleted immediately after each
                signing box operation, if this value is not set
        """
        self.handle = handle
        self.hdpath = hdpath
        self.secret_lifetime = secret_lifetime

    @property
    def dict(self):
        return {
            'handle': self.handle,
            'hdpath': self.hdpath,
            'secret_lifetime': self.secret_lifetime,
        }


class ParamsOfGetEncryptionBoxFromCryptoBox:
    """ParamsOfGetEncryptionBoxFromCryptoBox"""

    def __init__(
        self,
        handle: 'CryptoBoxHandle',
        algorithm: 'BoxEncryptionAlgorithmType',
        hdpath: str = None,
        secret_lifetime: int = None,
    ):
        """
        :param handle: Crypto Box Handle
        :param algorithm: Encryption algorithm
        :param hdpath: HD key derivation path.
                By default, Everscale HD path is used
        :param secret_lifetime: Store derived secret for encryption algorithm
                for this lifetime (in ms). The timer starts after each
                encryption box operation. Secrets will be deleted
                (overwritten with zeroes) after each encryption operation,
                if this value is not set
        """
        self.handle = handle
        self.algorithm = algorithm
        self.hdpath = hdpath
        self.secret_lifetime = secret_lifetime

    @property
    def dict(self):
        return {
            'handle': self.handle,
            'algorithm': self.algorithm.dict,
            'hdpath': self.hdpath,
            'secret_lifetime': self.secret_lifetime,
        }


class ParamsOfAppPasswordProvider:
    """AppPasswordProvided callbacks"""

    class GetPassword(BaseTypedType):
        """ParamsOfAppPasswordProvider.GetPassword"""

        def __init__(self, encryption_public_key: str):
            """
            :param encryption_public_key: Temporary library pubkey, that is
                    used on application side for password encryption, along
                    with application temporary private key and nonce.
                    Used for password decryption on library side
            """
            super(ParamsOfAppPasswordProvider.GetPassword, self).__init__(
                type='GetPassword'
            )
            self.encryption_public_key = encryption_public_key

        @property
        def dict(self):
            return {
                **super(ParamsOfAppPasswordProvider.GetPassword, self).dict,
                'encryption_public_key': self.encryption_public_key,
            }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ParamsOfAppPasswordProviderType':
        """Object from dict"""
        kwargs = {k: v for k, v in data.items() if k != 'type'}
        return getattr(ParamsOfAppPasswordProvider, data['type'])(**kwargs)


class ResultOfAppPasswordProvider:
    """Returning values from AppPasswordProvider"""

    class GetPassword(BaseTypedType):
        """ResultOfAppPasswordProvider.GetPassword"""

        def __init__(self, encrypted_password: str, app_encryption_pubkey: str):
            """
            :param encrypted_password: Password, encrypted and encoded to `base64`.
                    Crypto box uses this password to decrypt its secret (seed phrase)
            :param app_encryption_pubkey: Hex encoded public key of a temporary
                    key pair, used for password encryption on application side.
                    Used together with `encryption_public_key` to decode
                    `encrypted_password`.
            """
            super(ResultOfAppPasswordProvider.GetPassword, self).__init__(
                type='GetPassword'
            )
            self.encrypted_password = encrypted_password
            self.app_encryption_pubkey = app_encryption_pubkey

        @property
        def dict(self):
            return {
                **super(ResultOfAppPasswordProvider.GetPassword, self).dict,
                'encrypted_password': self.encrypted_password,
                'app_encryption_pubkey': self.app_encryption_pubkey,
            }


# NET module
class NetErrorCode(int, Enum):
    """Net module error codes"""

    QUERY_FAILED = 601
    SUBSCRIBE_FAILED = 602
    WAIT_FOR_FAILED = 603
    GET_SUBSCRIPTION_RESULT_FAILED = 604
    INVALID_SERVER_RESPONSE = 605
    CLOCK_OUT_OF_SYNC = 606
    WAIT_FOR_TIMEOUT = 607
    GRAPHQL_ERROR = 608
    NETWORK_MODULE_SUSPENDED = 609
    WEBSOCKET_DISCONNECTED = 610
    NOT_SUPPORTED = 611
    NO_ENDPOINTS_PROVIDED = 612
    GRAPHQL_WEBSOCKET_INIT_ERROR = 613
    NETWORK_MODULE_RESUMED = 614


class SortDirection(str, Enum):
    """Sord direction types"""

    ASC = 'ASC'
    DESC = 'DESC'


class OrderBy:
    """OrderBy"""

    def __init__(self, path: str, direction: 'SortDirection'):
        """
        :param path:
        :param direction:
        """
        self.path = path
        self.direction = direction

    @property
    def dict(self):
        """Dict from object"""
        return {'path': self.path, 'direction': self.direction}


class ParamsOfQuery:
    """ParamsOfQuery"""

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
        """Dict from object"""
        return {'query': self.query, 'variables': self.variables}


class ResultOfQuery:
    """ResultOfQuery"""

    def __init__(self, result: Any):
        """
        :param result: Result provided by DAppServer
        """
        self.result = result


class ParamsOfQueryCollection:
    """ParamsOfQueryCollection"""

    def __init__(
        self,
        collection: str,
        result: str,
        filter: Dict[str, Any] = None,
        order: List['OrderBy'] = None,
        limit: int = None,
    ):
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
        """Dict from object"""
        return {
            'collection': self.collection,
            'result': self.result,
            'filter': self.filter,
            'order': [o.dict for o in self.order],
            'limit': self.limit,
        }


class ResultOfQueryCollection:
    """ResultOfQueryCollection"""

    def __init__(self, result: List[Any]):
        """
        :param result: Objects that match the provided criteria
        """
        self.result = result


class ParamsOfWaitForCollection:
    """ParamsOfWaitForCollection"""

    def __init__(
        self,
        collection: str,
        result: str,
        filter: Dict[str, Any] = None,
        timeout: int = None,
    ):
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
        """Dict from object"""
        return {
            'collection': self.collection,
            'result': self.result,
            'filter': self.filter,
            'timeout': self.timeout,
        }


class ResultOfWaitForCollection:
    """ResultOfWaitForCollection"""

    def __init__(self, result: Any):
        """
        :param result: First found object that matches the provided criteria
        """
        self.result = result


class ParamsOfSubscribe:
    """ParamsOfSubscribe"""

    def __init__(self, subscription: str, variables: Dict[str, Any] = None):
        """
        :param subscription: GraphQL subscription text
        :param variables: Variables used in subscription.
                Must be a map with named values that can be used in query.
        """
        self.subscription = subscription
        self.variables = variables

    @property
    def dict(self):
        """Dict from object"""
        return {'subscription': self.subscription, 'variables': self.variables}


class ParamsOfSubscribeCollection:
    """ParamsOfSubscribeCollection"""

    def __init__(self, collection: str, result: str, filter: Dict[str, Any] = None):
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
        """Dict from object"""
        return {
            'collection': self.collection,
            'result': self.result,
            'filter': self.filter,
        }


class ResultOfSubscribeCollection:
    """ResultOfSubscribeCollection"""

    def __init__(self, handle: int):
        """
        :param handle: Subscription handle. Must be closed with `unsubscribe`
        """
        self.handle = handle

    @property
    def dict(self):
        """Dict from object"""
        return {'handle': self.handle}


class SubscriptionResponseType(int, Enum):
    """Subscription response types"""

    OK = 100
    ERROR = 101


class ResultOfSubscription:
    """ResultOfSubscription"""

    def __init__(self, result: Dict[str, Any]):
        """
        :param result: First appeared object that matches the provided criteria
        """
        self.result = result


class ParamsOfFindLastShardBlock:
    """ParamsOfFindLastShardBlock"""

    def __init__(self, address: str):
        """
        :param address: Account address
        """
        self.address = address

    @property
    def dict(self):
        """Dict from object"""
        return {'address': self.address}


class ResultOfFindLastShardBlock:
    """ResultOfFindLastShardBlock"""

    def __init__(self, block_id: str):
        """
        :param block_id: Account shard last block ID
        """
        self.block_id = block_id


class EndpointsSet:
    """EndpointsSet"""

    def __init__(self, endpoints: List[str]):
        """
        :param endpoints: List of endpoints provided by server
        """
        self.endpoints = endpoints

    @property
    def dict(self):
        """Dict from object"""
        return {'endpoints': self.endpoints}


class AggregationFn(str, Enum):
    """Aggregate functions"""

    COUNT = 'COUNT'
    MIN = 'MIN'
    MAX = 'MAX'
    SUM = 'SUM'
    AVERAGE = 'AVERAGE'


class FieldAggregation:
    """FieldAggregation"""

    def __init__(self, field: str, fn: 'AggregationFn'):
        """
        :param field: Dot separated path to the field
        :param fn: Aggregation function that must be applied to field values
        """
        self.field = field
        self.fn = fn

    @property
    def dict(self):
        """Dict from object"""
        return {'field': self.field, 'fn': self.fn}


class ParamsOfAggregateCollection:
    """ParamsOfAggregateCollection"""

    def __init__(
        self,
        collection: str,
        filter: Dict[str, Any] = None,
        fields: List['FieldAggregation'] = None,
    ):
        """
        :param collection: Collection name (accounts, blocks, transactions,
                messages, block_signatures)
        :param filter: Collection filter
        :param fields: Projection (result) string
        """
        self.collection = collection
        self.filter = filter
        self.fields = fields

    @property
    def dict(self):
        """Dict from object"""
        return {
            'collection': self.collection,
            'filter': self.filter,
            'fields': [f.dict for f in self.fields],
        }


class ResultOfAggregateCollection:
    """ResultOfAggregateCollection"""

    def __init__(self, values: List[str]):
        """
        :param values: Values for requested fields.
                Returns an array of strings. Each string refers to the
                corresponding fields item.
                Numeric value is returned as a decimal string representations
        """
        self.values = values


class ParamsOfQueryOperation:
    """ParamsOfQueryOperation"""

    class QueryCollection(BaseTypedType):
        """ParamsOfQueryOperation.QueryCollection"""

        def __init__(self, params: 'ParamsOfQueryCollection'):
            """
            :param params: ParamsOfQueryCollection
            """
            super(ParamsOfQueryOperation.QueryCollection, self).__init__(
                type='QueryCollection'
            )
            self.params = params

        @property
        def dict(self):
            return {
                **super(ParamsOfQueryOperation.QueryCollection, self).dict,
                **self.params.dict,
            }

    class WaitForCollection(BaseTypedType):
        """ParamsOfQueryOperation.WaitForCollection"""

        def __init__(self, params: 'ParamsOfWaitForCollection'):
            """
            :param params: ParamsOfWaitForCollection
            """
            super(ParamsOfQueryOperation.WaitForCollection, self).__init__(
                type='WaitForCollection'
            )
            self.params = params

        @property
        def dict(self):
            return {
                **super(ParamsOfQueryOperation.WaitForCollection, self).dict,
                **self.params.dict,
            }

    class AggregateCollection(BaseTypedType):
        """ParamsOfQueryOperation.AggregateCollection"""

        def __init__(self, params: 'ParamsOfAggregateCollection'):
            """
            :param params: ParamsOfAggregateCollection
            """
            super(ParamsOfQueryOperation.AggregateCollection, self).__init__(
                type='AggregateCollection'
            )
            self.params = params

        @property
        def dict(self):
            return {
                **super(ParamsOfQueryOperation.AggregateCollection, self).dict,
                **self.params.dict,
            }

    class QueryCounterparties(BaseTypedType):
        """ParamsOfQueryOperation.QueryCounterparties"""

        def __init__(self, params: 'ParamsOfQueryCounterparties'):
            """
            :param params: ParamsOfQueryCounterparties
            """
            super(ParamsOfQueryOperation.QueryCounterparties, self).__init__(
                type='QueryCounterparties'
            )
            self.params = params

        @property
        def dict(self):
            return {
                **super(ParamsOfQueryOperation.QueryCounterparties, self).dict,
                **self.params.dict,
            }


class ParamsOfBatchQuery:
    """ParamsOfBatchQuery"""

    def __init__(self, operations: List['ParamsOfQueryOperationType']):
        """
        :param operations: List of query operations that must be performed
                per single fetch
        """
        self.operations = operations

    @property
    def dict(self):
        """Dict from object"""
        return {'operations': [o.dict for o in self.operations]}


class ResultOfBatchQuery:
    """ResultOfBatchQuery"""

    def __init__(self, results: List[Any]):
        """
        :param results: Result values for batched queries. Returns an array
                of values. Each value corresponds to queries item
        """
        self.results = results


class ParamsOfQueryCounterparties:
    """ParamsOfQueryCounterparties"""

    def __init__(self, account: str, result: str, first: int = None, after: str = None):
        """
        :param account: Account address
        :param result: Projection (result) string
        :param first: Number of counterparties to return
        :param after: `cursor` field of the last received result
        """
        self.account = account
        self.result = result
        self.first = first
        self.after = after

    @property
    def dict(self):
        """Dict from object"""
        return {
            'account': self.account,
            'result': self.result,
            'first': self.first,
            'after': self.after,
        }


class ResultOfGetEndpoints:
    """ResultOfGetEndpoints"""

    def __init__(self, query: str, endpoints: List[str]):
        """
        :param query: Current query endpoint
        :param endpoints: List of all endpoints used by client
        """
        self.query = query
        self.endpoints = endpoints


class MessageNode:
    """MessageNode"""

    def __init__(
        self,
        id: str,
        bounce: bool,
        src_transaction_id: str = None,
        dst_transaction_id: str = None,
        src: str = None,
        dst: str = None,
        value: str = None,
        decoded_body: 'DecodedMessageBody' = None,
    ):
        """
        :param id: Message id
        :param bounce: Bounce flag
        :param src_transaction_id: Source transaction id. This field is
                missing for an external inbound messages
        :param dst_transaction_id: Destination transaction id. This field is
                missing for an external outbound messages
        :param src: Source address
        :param dst: Destination address
        :param value: Transferred tokens value
        :param decoded_body: Decoded body. Library tries to decode message
                body using provided `params.abi_registry`. This field will be
                missing if none of the provided abi can be used to decode
        """
        self.id = id
        self.bounce = bounce
        self.src_transaction_id = src_transaction_id
        self.dst_transaction_id = dst_transaction_id
        self.src = src
        self.dst = dst
        self.value = value
        self.decoded_body = decoded_body

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'MessageNode':
        """Object from dict"""
        if data['decoded_body']:
            data['decoded_body'] = DecodedMessageBody.from_dict(
                data=data['decoded_body']
            )

        return MessageNode(**data)


class TransactionNode:
    """TransactionNode"""

    def __init__(
        self,
        id: str,
        in_msg: str,
        out_msgs: List[str],
        account_addr: str,
        total_fees: str,
        aborted: bool,
        exit_code: int = None,
    ):
        """
        :param id: Transaction id
        :param in_msg: In message id
        :param out_msgs: Out message ids
        :param account_addr: Account address
        :param total_fees: Transactions total fees
        :param aborted: Aborted flag
        :param exit_code: Compute phase exit code
        """
        self.id = id
        self.in_msg = in_msg
        self.out_msgs = out_msgs
        self.account_addr = account_addr
        self.total_fees = total_fees
        self.aborted = aborted
        self.exit_code = exit_code


class ParamsOfQueryTransactionTree:
    """ParamsOfQueryTransactionTree"""

    def __init__(
        self, in_msg: str, abi_registry: List['AbiType'] = None, timeout: int = None
    ):
        """
        :param in_msg: Input message id
        :param abi_registry:  List of contract ABIs that will be used to
                decode message bodies. Library will try to decode each
                returned message body using any ABI from the registry
        :param timeout: Timeout used to limit waiting time for the missing
                messages and transaction. If some of the following messages
                and transactions are missing yet. The maximum waiting time is
                regulated by this option. Default value is 60000 (1 min)
        """
        self.in_msg = in_msg
        self.abi_registry = abi_registry
        self.timeout = timeout

    @property
    def dict(self):
        """Dict from object"""
        abi_registry = (
            [abi.dict for abi in self.abi_registry]
            if self.abi_registry
            else self.abi_registry
        )

        return {
            'in_msg': self.in_msg,
            'abi_registry': abi_registry,
            'timeout': self.timeout,
        }


class ResultOfQueryTransactionTree:
    """ResultOfQueryTransactionTree"""

    def __init__(
        self, messages: List['MessageNode'], transactions: List['TransactionNode']
    ):
        """
        :param messages: Messages
        :param transactions: Transactions
        """
        self.messages = messages
        self.transactions = transactions

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ResultOfQueryTransactionTree':
        """Object from dict"""
        data['messages'] = [MessageNode.from_dict(msg) for msg in data['messages']]
        data['transactions'] = [TransactionNode(**tx) for tx in data['transactions']]

        return ResultOfQueryTransactionTree(**data)


class RegisteredIterator:
    """RegisteredIterator"""

    def __init__(self, handle: int):
        """
        :param handle: Iterator handle. Must be removed using remove_iterator
                when it is no more needed for the application
        """
        self.handle = handle

    @property
    def dict(self):
        """Dict from object"""
        return {'handle': self.handle}


class ParamsOfCreateBlockIterator:
    """ParamsOfCreateBlockIterator"""

    def __init__(
        self,
        start_time: int = None,
        end_time: int = None,
        shard_filter: List[str] = None,
        result: str = None,
    ):
        """
        :param start_time: Starting time to iterate from.
                If the application specifies this parameter then the iteration
                includes blocks with `gen_utime` >= `start_time`.
                Otherwise the iteration starts from zero state.
                Must be specified in seconds
        :param end_time: Optional end time to iterate for.
                If the application specifies this parameter then the iteration
                includes blocks with `gen_utime` < `end_time`.
                Otherwise the iteration never stops.
                Must be specified in seconds.
        :param shard_filter: Shard prefix filter.
                If the application specifies this parameter and it is not
                the empty array then the iteration will include items related
                to accounts that belongs to the specified shard prefixes.
                Shard prefix must be represented as a string
                "workchain:prefix". Where `workchain` is a signed integer and
                the `prefix` is a hexadecimal representation if the 64-bit
                unsigned integer with tagged shard prefix.
                For example: "0:3800000000000000"
        :param result: Projection (result) string.
                List of the fields that must be returned for iterated items.
                This field is the same as the `result` parameter of the
                `query_collection` function. Note that iterated items can
                contains additional fields that are not requested in the result
        """
        self.start_time = start_time
        self.end_time = end_time
        self.shard_filter = shard_filter
        self.result = result

    @property
    def dict(self):
        """Dict from object"""
        return {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'shard_filter': self.shard_filter,
            'result': self.result,
        }


class ParamsOfResumeBlockIterator:
    """ParamsOfResumeBlockIterator"""

    def __init__(self, resume_state: Any):
        """
        :param resume_state: Iterator state from which to resume.
                Same as value returned from `iterator_next`
        """
        self.resume_state = resume_state

    @property
    def dict(self):
        """Dict from object"""
        return {'resume_state': self.resume_state}


class ParamsOfCreateTransactionIterator:
    """ParamsOfCreateTransactionIterator"""

    def __init__(
        self,
        start_time: int = None,
        end_time: int = None,
        shard_filter: List[str] = None,
        accounts_filter: List[str] = None,
        result: str = None,
        include_transfers: bool = None,
    ):
        """
        :param start_time: Starting time to iterate from.
                If the application specifies this parameter then the iteration
                includes blocks with `gen_utime` >= `start_time`.
                Otherwise the iteration starts from zero state.
                Must be specified in seconds
        :param end_time: Optional end time to iterate for.
                If the application specifies this parameter then the iteration
                includes blocks with `gen_utime` < `end_time`.
                Otherwise the iteration never stops.
                Must be specified in seconds
        :param shard_filter: Shard prefix filters.
                If the application specifies this parameter and it is not an
                empty array then the iteration will include items related to
                accounts that belongs to the specified shard prefixes.
                Shard prefix must be represented as a string
                "workchain:prefix". Where `workchain` is a signed integer
                and the `prefix` if a hexadecimal representation if the 64-bit
                unsigned integer with tagged shard prefix.
                For example: "0:3800000000000000".
                Account address conforms to the shard filter if it belongs to
                the filter workchain and the first bits of address match to
                the shard prefix. Only transactions with suitable account
                addresses are iterated
        :param accounts_filter: Account address filter.
                Application can specify the list of accounts for which it
                wants to iterate transactions.
                If this parameter is missing or an empty list then the library
                iterates transactions for all accounts that pass the shard
                filter.
                Note that the library doesn't detect conflicts between the
                account filter and the shard filter if both are specified.
                So it is an application responsibility to specify the correct
                filter combination
        :param result: Projection (result) string.
                List of the fields that must be returned for iterated items.
                This field is the same as the `result` parameter of the
                `query_collection` function.
                Note that iterated items can contain additional fields that
                are not requested in the `result`
        :param include_transfers: Include `transfers` field in iterated
                transactions. If this parameter is `true` then each
                transaction contains field `transfers` with list of transfer.

                Each transfer is calculated from the particular message
                related to the transaction and has the following structure:
                    * message source message identifier;
                    * isBounced indicates that the transaction is bounced,
                            which means the value will be returned back to the
                            sender;
                    * isDeposit indicates that this transfer is the
                            deposit (true) or withdraw (false);
                    * counterparty account address of the transfer source or
                            destination depending on isDeposit;
                    * value amount of nano tokens transferred.
                            The value is represented as a decimal string
                            because the actual value can be more precise than
                            the JSON number can represent. Application must
                            use this string carefully conversion to number
                            can follow to loose of precision.
        """
        self.start_time = start_time
        self.end_time = end_time
        self.shard_filter = shard_filter
        self.accounts_filter = accounts_filter
        self.result = result
        self.include_transfers = include_transfers

    @property
    def dict(self):
        """Dict from object"""
        return {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'shard_filter': self.shard_filter,
            'accounts_filter': self.accounts_filter,
            'result': self.result,
            'include_transfers': self.include_transfers,
        }


class ParamsOfResumeTransactionIterator:
    """ParamsOfResumeTransactionIterator"""

    def __init__(self, resume_state: Any, accounts_filter: List[str] = None):
        """
        :param resume_state:  Iterator state from which to resume.
                Same as value returned from `iterator_next`
        :param accounts_filter: Account address filter.
                Application can specify the list of accounts for which
                it wants to iterate transactions.
                If this parameter is missing or an empty list then the
                library iterates transactions for all accounts that passes
                the shard filter.
                Note that the library doesn't detect conflicts between the
                account filter and the shard filter if both are specified.
                So it is the application's responsibility to specify the
                correct filter combination.
        """
        self.resume_state = resume_state
        self.accounts_filter = accounts_filter

    @property
    def dict(self):
        """Dict from object"""
        return {
            'resume_state': self.resume_state,
            'accounts_filter': self.accounts_filter,
        }


class ParamsOfIteratorNext:
    """ParamsOfIteratorNext"""

    def __init__(
        self, iterator: int, limit: int = None, return_resume_state: bool = None
    ):
        """
        :param iterator: Iterator handle
        :param limit: Maximum count of the returned items.
                If value is missing or is less than 1 the library uses 1
        :param return_resume_state: Indicates that function must return the
                iterator state that can be used for resuming iteration
        """
        self.iterator = iterator
        self.limit = limit
        self.return_resume_state = return_resume_state

    @property
    def dict(self):
        """Dict from object"""
        return {
            'iterator': self.iterator,
            'limit': self.limit,
            'return_resume_state': self.return_resume_state,
        }


class ResultOfIteratorNext:
    """ResultOfIteratorNext"""

    def __init__(self, items: List[Any], has_more: bool, resume_state: Any = None):
        """
        :param items: Next available items.
                Note that `iterator_next` can return an empty items and
                `has_more` equals to `true`.
                In this case the application have to continue iteration.
                Such situation can take place when there is no data yet but
                the requested `end_time` is not reached
        :param has_more: Indicates that there are more available items in
                iterated range
        :param resume_state: Optional iterator state that can be used for
                resuming iteration. This field is returned only if the
                `return_resume_state` parameter is specified.
                Note that `resume_state` corresponds to the iteration position
                after the returned items
        """
        self.items = items
        self.has_more = has_more
        self.resume_state = resume_state


# PROCESSING module
class ProcessingErrorCode(int, Enum):
    """Processing module error codes"""

    MESSAGE_ALREADY_EXPIRED = 501
    MESSAGE_HAS_NO_DESTINATION_ADDRESS = 502
    CANNOT_BUILD_MESSAGE_CELL = 503
    FETCH_BLOCK_FAILED = 504
    SEND_MESSAGE_FAILED = 505
    INVALID_MESSAGE_BOC = 506
    MESSAGE_EXPIRED = 507
    TRANSACTION_WAIT_TIMEOUT = 508
    INVALID_BLOCK_RECEIVED = 509
    CANNOT_CHECK_BLOCK_SHARD = 510
    BLOCK_NOT_FOUND = 511
    INVALID_DATA = 512
    EXTERNAL_SIGNER_MUST_NOT_BE_USED = 513
    MESSAGE_REJECTED = 514
    INVALID_REMP_STATUS = 515
    NEXT_REMP_STATUS_TIMEOUT = 516


class ProcessingEvent:
    """ProcessingEvent"""

    class WillFetchFirstBlock(BaseTypedType):
        """
        Notifies the application that the account's current shard block
        will be fetched from the network. This step is performed before
        the message sending so that sdk knows starting from which block
        it will search for the transaction.
        Fetched block will be used later in waiting phase
        """

        def __init__(self):
            super(ProcessingEvent.WillFetchFirstBlock, self).__init__(
                type='WillFetchFirstBlock'
            )

    class FetchFirstBlockFailed(BaseTypedType):
        """
        Notifies the app that the client has failed to fetch the account's
        current shard block.
        This may happen due to the network issues. Receiving this event
        means that message processing will not proceed - message was not
        sent, and Developer can try to run `process_message` again, in the
        hope that the connection is restored
        """

        def __init__(self, error: 'ClientError'):
            """
            :param error:
            """
            super(ProcessingEvent.FetchFirstBlockFailed, self).__init__(
                type='FetchFirstBlockFailed'
            )
            self.error = error

    class WillSend(BaseTypedType):
        """
        Notifies the app that the message will be sent to the network.
        This event means that the account's current shard block was
        successfully fetched and the message was successfully created
        (`abi.encode_message` function was executed successfully)
        """

        def __init__(self, shard_block_id: str, message_id: str, message: str):
            """
            :param shard_block_id:
            :param message_id:
            :param message:
            """
            super(ProcessingEvent.WillSend, self).__init__(type='WillSend')
            self.shard_block_id = shard_block_id
            self.message_id = message_id
            self.message = message

    class DidSend(BaseTypedType):
        """
        Notifies the app that the message was sent to the network,
        i.e `processing.send_message` was successfully executed.
        Now, the message is in the blockchain.
        If Application exits at this phase, Developer needs to proceed
        with processing after the application is restored with
        `wait_for_transaction` function, passing `shard_block_id` and
        `message` from this event.
        Do not forget to specify `abi` of your contract as well, it is
        crucial for processing
        """

        def __init__(self, shard_block_id: str, message_id: str, message: str):
            """
            :param shard_block_id:
            :param message_id:
            :param message:
            """
            super(ProcessingEvent.DidSend, self).__init__(type='DidSend')
            self.shard_block_id = shard_block_id
            self.message_id = message_id
            self.message = message

    class SendFailed(BaseTypedType):
        """
        Notifies the app that the sending operation was failed with
        network error.
        Nevertheless the processing will be continued at the waiting phase
        because the message possibly has been delivered to the node.
        If Application exits at this phase, Developer needs to proceed
        with processing after the application is restored with
        `wait_for_transaction` function, passing `shard_block_id` and
        `message` from this event.
        Do not forget to specify `abi` of your contract as well, it is
        crucial for processing
        """

        def __init__(
            self,
            shard_block_id: str,
            message_id: str,
            message: str,
            error: 'ClientError',
        ):
            """
            :param shard_block_id:
            :param message_id:
            :param message:
            :param error:
            """
            super(ProcessingEvent.SendFailed, self).__init__(type='SendFailed')
            self.shard_block_id = shard_block_id
            self.message_id = message_id
            self.message = message
            self.error = error

    class WillFetchNextBlock(BaseTypedType):
        """
        Notifies the app that the next shard block will be fetched
        from the network.
        Event can occurs more than one time due to block walking procedure.
        If Application exits at this phase, Developer needs to proceed with
        processing after the application is restored with
        `wait_for_transaction` function, passing `shard_block_id` and
        `message` from this event.
        Do not forget to specify `abi` of your contract as well, it is
        crucial for processing
        """

        def __init__(self, shard_block_id: str, message_id: str, message: str):
            """
            :param shard_block_id:
            :param message_id:
            :param message:
            """
            super(ProcessingEvent.WillFetchNextBlock, self).__init__(
                type='WillFetchNextBlock'
            )
            self.shard_block_id = shard_block_id
            self.message_id = message_id
            self.message = message

    class FetchNextBlockFailed(BaseTypedType):
        """
        Notifies the app that the next block can't be fetched.
        If no block was fetched within `NetworkConfig.wait_for_timeout`
        then processing stops.
        This may happen when the shard stops, or there are other network
        issues. In this case Developer should resume message processing with
        `wait_for_transaction`, passing `shard_block_id`, `message` and
        contract `abi` to it.
        Note that passing ABI is crucial, because it will influence the
        processing strategy.
        Another way to tune this is to specify long timeout in
        `NetworkConfig.wait_for_timeout`
        """

        def __init__(
            self,
            shard_block_id: str,
            message_id: str,
            message: str,
            error: 'ClientError',
        ):
            """
            :param shard_block_id:
            :param message_id:
            :param message:
            :param error:
            """
            super(ProcessingEvent.FetchNextBlockFailed, self).__init__(
                type='FetchNextBlockFailed'
            )
            self.shard_block_id = shard_block_id
            self.message_id = message_id
            self.message = message
            self.error = error

    class MessageExpired(BaseTypedType):
        """
        Notifies the app that the message was not executed within expire
        timeout on-chain and will never be because it is already expired.
        The expiration timeout can be configured with `AbiConfig` parameters.
        This event occurs only for the contracts which ABI includes
        "expire" header.
        If Application specifies `NetworkConfig.message_retries_count > 0`,
        then `process_message` will perform retries: will create a new
        message and send it again and repeat it until it reaches the maximum
        retries count or receives a successful result.
        All the processing events will be repeated
        """

        def __init__(self, message_id: str, message: str, error: 'ClientError'):
            """
            :param message_id:
            :param message:
            :param error:
            """
            super(ProcessingEvent.MessageExpired, self).__init__(type='MessageExpired')
            self.message_id = message_id
            self.message = message
            self.error = error

    class RempSentToValidators(BaseTypedType):
        """
        Notifies the app that the message has been delivered to the thread's validators
        """

        def __init__(self, message_id: str, timestamp: int, json: Any):
            """
            :param message_id:
            :param timestamp:
            :param json:
            """
            super(ProcessingEvent.RempSentToValidators, self).__init__(
                type='RempSentToValidators'
            )
            self.message_id = message_id
            self.timestamp = timestamp
            self.json = json

    class RempIncludedIntoBlock(BaseTypedType):
        """
        Notifies the app that the message has been successfully included into a block
        candidate by the thread's collator
        """

        def __init__(self, message_id: str, timestamp: int, json: Any):
            """
            :param message_id:
            :param timestamp:
            :param json:
            """
            super(ProcessingEvent.RempIncludedIntoBlock, self).__init__(
                type='RempIncludedIntoBlock'
            )
            self.message_id = message_id
            self.timestamp = timestamp
            self.json = json

    class RempIncludedIntoAcceptedBlock(BaseTypedType):
        """
        Notifies the app that the block candicate with the message has been
        accepted by the thread's validators
        """

        def __init__(self, message_id: str, timestamp: int, json: Any):
            """
            :param message_id:
            :param timestamp:
            :param json:
            """
            super(ProcessingEvent.RempIncludedIntoAcceptedBlock, self).__init__(
                type='RempIncludedIntoAcceptedBlock'
            )
            self.message_id = message_id
            self.timestamp = timestamp
            self.json = json

    class RempOther(BaseTypedType):
        """
        Notifies the app about some other minor REMP statuses occurring during
        message processing
        """

        def __init__(self, message_id: str, timestamp: int, json: Any):
            """
            :param message_id:
            :param timestamp:
            :param json:
            """
            super(ProcessingEvent.RempOther, self).__init__(type='RempOther')
            self.message_id = message_id
            self.timestamp = timestamp
            self.json = json

    class RempError(BaseTypedType):
        """
        Notifies the app about any problem that has occured in REMP
        processing - in this case library switches to the fallback transaction awaiting
        scenario (sequential block reading)
        """

        def __init__(self, error: 'ClientError'):
            """
            :param message_id:
            :param timestamp:
            :param json:
            """
            super(ProcessingEvent.RempError, self).__init__(type='RempError')
            self.error = error

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ProcessingEventType':
        """Object from dict"""
        kwargs = {k: v for k, v in data.items() if k != 'type'}
        return getattr(ProcessingEvent, data['type'])(**kwargs)


class ProcessingResponseType(int, Enum):
    """Processing response types"""

    PROCESSING_EVENT = 100


class ResultOfProcessMessage:
    """ResultOfProcessMessage"""

    def __init__(
        self,
        transaction: Dict[str, Any],
        out_messages: List[str],
        fees: 'TransactionFees',
        decoded: 'DecodedOutput' = None,
    ):
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
        """Object from dict"""
        data['fees'] = TransactionFees(**data['fees'])
        if data['decoded']:
            data['decoded'] = DecodedOutput.from_dict(data=data['decoded'])

        return ResultOfProcessMessage(**data)


class DecodedOutput:
    """DecodedOutput"""

    def __init__(
        self, out_messages: List[Union['DecodedMessageBody', None]], output: Any = None
    ):
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
        """Object from dict"""
        if data['out_messages']:
            data['out_messages'] = [
                DecodedMessageBody.from_dict(data=m) if m else None
                for m in data['out_messages']
            ]

        return DecodedOutput(**data)


class ParamsOfSendMessage:
    """ParamsOfSendMessage"""

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
        """Dict from object"""
        abi = self.abi.dict if self.abi else self.abi
        return {'message': self.message, 'send_events': self.send_events, 'abi': abi}


class ResultOfSendMessage:
    """ResultOfSendMessage"""

    def __init__(self, shard_block_id: str, sending_endpoints: List[str]):
        """
        :param shard_block_id: The last generated shard block of the message
                destination account before the message was sent. This block id
                must be used as a parameter of the `wait_for_transaction`
        :param sending_endpoints: The list of endpoints to which the message
                was sent. This list id must be used as a parameter of the
                `wait_for_transaction`
        """
        self.shard_block_id = shard_block_id
        self.sending_endpoints = sending_endpoints


class ParamsOfWaitForTransaction:
    """ParamsOfWaitForTransaction"""

    def __init__(
        self,
        message: str,
        shard_block_id: str,
        send_events: bool,
        abi: 'AbiType' = None,
        sending_endpoints: List[str] = None,
    ):
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
        :param sending_endpoints: The list of endpoints to which the message
                was sent. You must provide the same value as the `send_message`
                has returned
        """
        self.message = message
        self.shard_block_id = shard_block_id
        self.send_events = send_events
        self.abi = abi
        self.sending_endpoints = sending_endpoints

    @property
    def dict(self):
        """Dict from object"""
        abi = self.abi.dict if self.abi else self.abi
        return {
            'message': self.message,
            'shard_block_id': self.shard_block_id,
            'send_events': self.send_events,
            'abi': abi,
            'sending_endpoints': self.sending_endpoints,
        }


class ParamsOfProcessMessage:
    """ParamsOfProcessMessage"""

    def __init__(
        self, message_encode_params: 'ParamsOfEncodeMessage', send_events: bool
    ):
        """
        :param message_encode_params: Message encode parameters
        :param send_events: Flag for requesting events sending
        """
        self.message_encode_params = message_encode_params
        self.send_events = send_events

    @property
    def dict(self):
        """Dict from object"""
        return {
            'message_encode_params': self.message_encode_params.dict,
            'send_events': self.send_events,
        }


# TVM module
class TvmErrorCode(int, Enum):
    """TVM module error codes"""

    CANNOT_READ_TRANSACTION = 401
    CANNOT_READ_BLOCKCHAIN_CONFIG = 402
    TRANSACTION_ABORTED = 403
    INTERNAL_ERROR = 404
    ACTION_PHASE_FAILED = 405
    ACCOUNT_CODE_MISSING = 406
    LOW_BALANCE = 407
    ACCOUNT_FROZEN_OR_DELETED = 408
    ACCOUNT_MISSING = 409
    UNKNOWN_EXECUTION_ERROR = 410
    INVALID_INPUT_STACK = 411
    INVALID_ACCOUNT_BOC = 412
    INVALID_MESSAGE_TYPE = 413
    CONTRACT_EXECUTION_ERROR = 414


class TransactionFees:
    """TransactionFees"""

    def __init__(
        self,
        in_msg_fwd_fee: int,
        storage_fee: int,
        gas_fee: int,
        out_msgs_fwd_fee: int,
        total_account_fees: int,
        total_output: int,
        ext_in_msg_fee: int,
        total_fwd_fees: int,
        account_fees: int,
    ):
        """
        :param in_msg_fwd_fee:
        :param storage_fee:
        :param gas_fee:
        :param out_msgs_fwd_fee:
        :param total_account_fees:
        :param total_output:
        :param ext_in_msg_fee:
        :param total_fwd_fees:
        :param account_fees:
        """
        self.in_msg_fwd_fee = in_msg_fwd_fee
        self.storage_fee = storage_fee
        self.gas_fee = gas_fee
        self.out_msgs_fwd_fee = out_msgs_fwd_fee
        self.total_account_fees = total_account_fees
        self.total_output = total_output
        self.ext_in_msg_fee = ext_in_msg_fee
        self.total_fwd_fees = total_fwd_fees
        self.account_fees = account_fees


class ExecutionOptions:
    """ExecutionOptions"""

    def __init__(
        self,
        blockchain_config: str = None,
        block_time: int = None,
        block_lt: int = None,
        transaction_lt: int = None,
    ):
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
        """Dict from object"""
        return {
            'blockchain_config': self.blockchain_config,
            'block_time': self.block_time,
            'block_lt': self.block_lt,
            'transaction_lt': self.transaction_lt,
        }


class AccountForExecutor:
    """AccountForExecutor"""

    class NoAccount(BaseTypedType):
        """
        Non-existing account to run a creation internal message.
        Should be used with `skip_transaction_check = true` if the message
        has no deploy data since transactions on the uninitialized account
        are always aborted
        """

        def __init__(self):
            super(AccountForExecutor.NoAccount, self).__init__(type='None')

    class Uninit(BaseTypedType):
        """Emulate uninitialized account to run deploy message"""

        def __init__(self):
            super(AccountForExecutor.Uninit, self).__init__(type='Uninit')

    class Account(BaseTypedType):
        """AccountForExecutor.Account"""

        def __init__(self, boc: str, unlimited_balance: bool = None):
            """
            :param boc: Account BOC. Encoded as `base64`
            :param unlimited_balance: Flag for running account with the
                    unlimited balance. Can be used to calculate transaction
                    fees without balance check
            """
            super(AccountForExecutor.Account, self).__init__(type='Account')
            self.boc = boc
            self.unlimited_balance = unlimited_balance

        @property
        def dict(self):
            return {
                **super(AccountForExecutor.Account, self).dict,
                'boc': self.boc,
                'unlimited_balance': self.unlimited_balance,
            }


class ParamsOfRunExecutor:
    """ParamsOfRunExecutor"""

    def __init__(
        self,
        message: str,
        account: 'AccountForExecutorType',
        execution_options: 'ExecutionOptions' = None,
        abi: 'AbiType' = None,
        skip_transaction_check: bool = None,
        boc_cache: 'BocCacheTypeType' = None,
        return_updated_account: bool = None,
    ):
        """
        :param message: Input message BOC. Must be encoded as `base64`
        :param account: Account to run on executor
        :param execution_options: Execution options
        :param abi: Contract ABI for decoding output messages
        :param skip_transaction_check: Skip transaction check flag
        :param boc_cache: Cache type to put the result. The BOC itself
                returned if no cache type provided
        :param return_updated_account: Return updated account flag. Empty
                string is returned if the flag is `false`
        """
        self.message = message
        self.account = account
        self.execution_options = execution_options
        self.abi = abi
        self.skip_transaction_check = skip_transaction_check
        self.boc_cache = boc_cache
        self.return_updated_account = return_updated_account

    @property
    def dict(self):
        """Dict from object"""
        execution_options = (
            self.execution_options.dict
            if self.execution_options
            else self.execution_options
        )
        abi = self.abi.dict if self.abi else self.abi
        boc_cache = self.boc_cache.dict if self.boc_cache else self.boc_cache

        return {
            'message': self.message,
            'account': self.account.dict,
            'execution_options': execution_options,
            'abi': abi,
            'skip_transaction_check': self.skip_transaction_check,
            'boc_cache': boc_cache,
            'return_updated_account': self.return_updated_account,
        }


class ResultOfRunExecutor:
    """ResultOfRunExecutor"""

    def __init__(
        self,
        transaction: Dict[str, Any],
        out_messages: List[str],
        account: str,
        fees: 'TransactionFees',
        decoded: 'DecodedOutput' = None,
    ):
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
        """Object from dict"""
        data['fees'] = TransactionFees(**data['fees'])
        if data['decoded']:
            data['decoded'] = DecodedOutput.from_dict(data=data['decoded'])

        return ResultOfRunExecutor(**data)


class ParamsOfRunTvm:
    """ParamsOfRunTvm"""

    def __init__(
        self,
        message: str,
        account: str,
        abi: 'AbiType' = None,
        execution_options: 'ExecutionOptions' = None,
        boc_cache: 'BocCacheTypeType' = None,
        return_updated_account: bool = None,
    ):
        """
        :param message: Input message BOC. Must be encoded as `base64`
        :param account: Account BOC. Must be encoded as `base64`
        :param abi: Contract ABI for decoding output messages
        :param execution_options: Execution options
        :param boc_cache: Cache type to put the result. The BOC itself
                returned if no cache type provided
        :param return_updated_account: Return updated account flag. Empty
                string is returned if the flag is `false`
        """
        self.message = message
        self.account = account
        self.abi = abi
        self.execution_options = execution_options
        self.boc_cache = boc_cache
        self.return_updated_account = return_updated_account

    @property
    def dict(self):
        """Dict from object"""
        execution_options = (
            self.execution_options.dict
            if self.execution_options
            else self.execution_options
        )
        abi = self.abi.dict if self.abi else self.abi
        boc_cache = self.boc_cache.dict if self.boc_cache else self.boc_cache

        return {
            'message': self.message,
            'account': self.account,
            'execution_options': execution_options,
            'abi': abi,
            'boc_cache': boc_cache,
            'return_updated_account': self.return_updated_account,
        }


class ResultOfRunTvm:
    """ResultOfRunTvm"""

    def __init__(
        self, out_messages: List[str], account: str, decoded: 'DecodedOutput' = None
    ):
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
        """Object from dict"""
        if data['decoded']:
            data['decoded'] = DecodedOutput.from_dict(data=data['decoded'])

        return ResultOfRunTvm(**data)


class ParamsOfRunGet:
    """ParamsOfRunGet"""

    def __init__(
        self,
        account: str,
        function_name: str,
        input: Any = None,
        execution_options: 'ExecutionOptions' = None,
        tuple_list_as_array: bool = None,
    ):
        """
        :param account: Account BOC in `base64`
        :param function_name: Function name
        :param input: Input parameters
        :param execution_options: Execution options
        :param tuple_list_as_array: Convert lists based on nested tuples in
                the result into plain arrays. Default is false.
                Input parameters may use any of lists representations.
                If you receive this error on Web: "Runtime error. Unreachable
                code should not be executed...", set this flag to true.
                This may happen, for example, when elector contract contains
                too many participants
        """
        self.account = account
        self.function_name = function_name
        self.input = input
        self.execution_options = execution_options
        self.tuple_list_as_array = tuple_list_as_array

    @property
    def dict(self):
        """Dict from object"""
        execution_options = (
            self.execution_options.dict
            if self.execution_options
            else self.execution_options
        )

        return {
            'account': self.account,
            'function_name': self.function_name,
            'input': self.input,
            'execution_options': execution_options,
            'tuple_list_as_array': self.tuple_list_as_array,
        }


class ResultOfRunGet:
    """ResultOfRunGet"""

    def __init__(self, output: Any):
        """
        :param output: Values returned by getmethod on stack
        """
        self.output = output


# UTILS module
class AccountAddressType(str, Enum):
    """Account address types"""

    ACCOUNT_ID = 'AccountId'
    HEX = 'Hex'
    BASE64 = 'Base64'


class AddressStringFormat:
    """AddressStringFormat"""

    class AccountId(BaseTypedType):
        """AddressStringFormat.AccountId"""

        def __init__(self):
            super(AddressStringFormat.AccountId, self).__init__(
                type=AccountAddressType.ACCOUNT_ID
            )

    class Hex(BaseTypedType):
        """AddressStringFormat.Hex"""

        def __init__(self):
            super(AddressStringFormat.Hex, self).__init__(type=AccountAddressType.HEX)

    class Base64(BaseTypedType):
        """AddressStringFormat.Base64"""

        def __init__(self, url: bool, test: bool, bounce: bool):
            """
            :param url:
            :param test:
            :param bounce:
            """
            super(AddressStringFormat.Base64, self).__init__(
                type=AccountAddressType.BASE64
            )
            self.url = url
            self.test = test
            self.bounce = bounce

        @property
        def dict(self):
            return {
                **super(AddressStringFormat.Base64, self).dict,
                'url': self.url,
                'test': self.test,
                'bounce': self.bounce,
            }


class ParamsOfConvertAddress:
    """ParamsOfConvertAddress"""

    def __init__(self, address: str, output_format: 'AddressStringFormatType'):
        """
        :param address: Account address in any TON format
        :param output_format: Specify the format to convert to
        """
        self.address = address
        self.output_format = output_format

    @property
    def dict(self):
        """Dict from object"""
        return {'address': self.address, 'output_format': self.output_format.dict}


class ResultOfConvertAddress:
    """ResultOfConvertAddress"""

    def __init__(self, address: str):
        """
        :param address: Address in the specified format
        """
        self.address = address


class ParamsOfCalcStorageFee:
    """ParamsOfCalcStorageFee"""

    def __init__(self, account: str, period: int):
        """
        :param account:
        :param period:
        """
        self.account = account
        self.period = period

    @property
    def dict(self):
        """Dict from object"""
        return {'account': self.account, 'period': self.period}


class ResultOfCalcStorageFee:
    """ResultOfCalcStorageFee"""

    def __init__(self, fee: str):
        """
        :param fee:
        """
        self.fee = fee


class ParamsOfCompressZstd:
    """ParamsOfCompressZstd"""

    def __init__(self, uncompressed: str, level: int = None):
        """
        :param uncompressed: Uncompressed data. Must be encoded as `base64`
        :param level: Compression level, from 1 to 21.
                Where:
                    1 - lowest compression level (fastest compression);
                    21 - highest compression level (slowest compression).
                If level is omitted, the default compression level is used
                (currently 3)
        """
        self.uncompressed = uncompressed
        self.level = level

    @property
    def dict(self):
        """Dict from object"""
        return {'uncompressed': self.uncompressed, 'level': self.level}


class ResultOfCompressZstd:
    """ResultOfCompressZstd"""

    def __init__(self, compressed: str):
        """
        :param compressed: Compressed data. Encoded as `base64`
        """
        self.compressed = compressed


class ParamsOfDecompressZstd:
    """ParamsOfDecompressZstd"""

    def __init__(self, compressed: str):
        """
        :param compressed: Compressed data. Must be encoded as `base64`
        """
        self.compressed = compressed

    @property
    def dict(self):
        """Dict from object"""
        return {'compressed': self.compressed}


class ResultOfDecompressZstd:
    """ResultOfDecompressZstd"""

    def __init__(self, decompressed: str):
        """
        :param decompressed: Decompressed data. Encoded as `base64`
        """
        self.decompressed = decompressed


class ParamsOfGetAddressType:
    """ParamsOfGetAddressType"""

    def __init__(self, address: str):
        """
        :param address: Account address in any TON format
        """
        self.address = address

    @property
    def dict(self):
        """Dict from object"""
        return {'address': self.address}


class ResultOfGetAddressType:
    """ResultOfGetAddressType"""

    def __init__(self, address_type: 'AccountAddressType'):
        """
        :param address_type: Account address type
        """
        self.address_type = address_type


# DEBOT module
DebotHandle = int


class DebotErrorCode(int, Enum):
    """DeBot module error codes"""

    DEBOT_START_FAILED = 801
    DEBOT_FETCH_FAILED = 802
    DEBOT_EXECUTION_FAILED = 803
    DEBOT_INVALID_HANDLE = 804
    DEBOT_INVALID_JSON_PARAMS = 805
    DEBOT_INVALID_FUNCTION_ID = 806
    DEBOT_INVALID_ABI = 807
    DEBOT_GET_METHOD_FAILED = 808
    DEBOT_INVALID_MSG = 809
    DEBOT_EXTERNAL_CALL_FAILED = 810
    DEBOT_BROWSER_CALLBACK_FAILED = 811
    DEBOT_OPERATION_REJECTED = 812


class DebotAction:
    """DebotAction"""

    def __init__(
        self,
        description: str,
        name: str,
        action_type: int,
        to: int,
        attributes: str,
        misc: str,
    ):
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
        """Dict from object"""
        return {
            'description': self.description,
            'name': self.name,
            'action_type': self.action_type,
            'to': self.to,
            'attributes': self.attributes,
            'misc': self.misc,
        }

    def __str__(self):
        return self.description


class DebotInfo:
    """DebotInfo"""

    def __init__(
        self,
        interfaces: List[str],
        name: str = None,
        version: str = None,
        publisher: str = None,
        caption: str = None,
        author: str = None,
        support: str = None,
        hello: str = None,
        language: str = None,
        dabi: str = None,
        icon: str = None,
    ):
        """
        :param interfaces: Vector with IDs of DInterfaces used by DeBot
        :param name: DeBot short name
        :param version: DeBot semantic version
        :param publisher: The name of DeBot deployer
        :param caption: Short info about DeBot
        :param author: The name of DeBot developer
        :param support: TON address of author for questions and donations
        :param hello: String with the first message from DeBot
        :param language: String with DeBot interface language (ISO-639)
        :param dabi: String with DeBot ABI
        :param icon: DeBot icon
        """
        self.interfaces = interfaces
        self.name = name
        self.version = version
        self.publisher = publisher
        self.caption = caption
        self.author = author
        self.support = support
        self.hello = hello
        self.language = language
        self.dabi = dabi
        self.icon = icon

    @property
    def dict(self):
        """Dict from object"""
        return {
            'interfaces': self.interfaces,
            'name': self.name,
            'version': self.version,
            'publisher': self.publisher,
            'caption': self.caption,
            'author': self.author,
            'support': self.support,
            'hello': self.hello,
            'language': self.language,
            'dabi': self.dabi,
            'icon': self.icon,
        }


class DebotActivity:
    """Describes the operation that the DeBot wants to perform"""

    class Transaction(BaseTypedType):
        """DebotActivity.Transaction"""

        def __init__(
            self,
            msg: str,
            dst: str,
            out: List['Spending'],
            fee: int,
            setcode: bool,
            signkey: str,
            signing_box_handle: int,
        ):
            """
            :param msg: External inbound message BOC
            :param dst: Target smart contract address
            :param out: List of spending as a result of transaction
            :param fee: Transaction total fee
            :param setcode: Indicates if target smart contract updates its code
            :param signkey: Public key from keypair that was used to sign
                    external message
            :param signing_box_handle: Signing box handle used to sign
                    external message
            """
            super(DebotActivity.Transaction, self).__init__(type='Transaction')
            self.msg = msg
            self.dst = dst
            self.out = out
            self.fee = fee
            self.setcode = setcode
            self.signkey = signkey
            self.signing_box_handle = signing_box_handle

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DebotActivityType':
        """Object from dict"""
        if data.get('out'):
            data['out'] = [Spending(**item) for item in data['out']]
        kwargs = {k: v for k, v in data.items() if k != 'type'}
        return getattr(DebotActivity, data['type'])(**kwargs)


class Spending:
    """Spending"""

    def __init__(self, amount: int, dst: str):
        """
        Describes how much funds will be debited from the target contract
        balance as a result of the transaction
        :param amount: Amount of nano tokens that will be sent to `dst` address
        :param dst: Destination address of recipient of funds
        """
        self.amount = amount
        self.dst = dst


class ParamsOfInit:
    """Parameters to init DeBot"""

    def __init__(self, address: str):
        """
        :param address: Debot smart contract address
        """
        self.address = address

    @property
    def dict(self):
        """Dict from object"""
        return {'address': self.address}


class RegisteredDebot:
    """
    Structure for storing debot handle returned from `start` and `fetch`
    functions
    """

    def __init__(self, debot_handle: 'DebotHandle', debot_abi: str, info: 'DebotInfo'):
        """
        :param debot_handle: Debot handle which references an instance of
                debot engine
        :param debot_abi: Debot abi as json string
        :param info: Debot metadata
        """
        self.debot_handle = debot_handle
        self.debot_abi = debot_abi
        self.info = info

    @property
    def dict(self):
        """Dict from object"""
        return {
            'debot_handle': self.debot_handle,
            'debot_abi': self.debot_abi,
            'info': self.info.dict,
        }


class ParamsOfAppDebotBrowser:
    """
    Debot Browser callbacks.
    Called by debot engine to communicate with debot browser
    """

    class Log(BaseTypedType):
        """Print message to user"""

        def __init__(self, msg: str):
            """
            :param msg: A string that must be printed to user
            """
            super(ParamsOfAppDebotBrowser.Log, self).__init__(type='Log')
            self.msg = msg

    class Switch(BaseTypedType):
        """Switch debot to another context (menu)"""

        def __init__(self, context_id: int):
            """
            :param context_id: Debot context ID to which debot is switched
            """
            super(ParamsOfAppDebotBrowser.Switch, self).__init__(type='Switch')
            self.context_id = context_id

    class SwitchCompleted(BaseTypedType):
        """Notify browser that all context actions are shown"""

        def __init__(self):
            super(ParamsOfAppDebotBrowser.SwitchCompleted, self).__init__(
                type='SwitchCompleted'
            )

    class ShowAction(BaseTypedType):
        """
        Show action to the user.
        Called after switch for each action in context
        """

        def __init__(self, action: 'DebotAction'):
            """
            :param action: Debot action that must be shown to user as menu
                    item. At least description property must be shown from
                    `DebotAction` structure
            """
            super(ParamsOfAppDebotBrowser.ShowAction, self).__init__(type='ShowAction')
            self.action = action

    class Input(BaseTypedType):
        """Request user input"""

        def __init__(self, prompt: str):
            """
            :param prompt: A prompt string that must be printed to user
                    before input request
            """
            super(ParamsOfAppDebotBrowser.Input, self).__init__(type='Input')
            self.prompt = prompt

    class GetSigningBox(BaseTypedType):
        """
        Get signing box to sign data.
        Signing box returned is owned and disposed by debot engine
        """

        def __init__(self):
            super(ParamsOfAppDebotBrowser.GetSigningBox, self).__init__(
                type='GetSigningBox'
            )

    class InvokeDebot(BaseTypedType):
        """Execute action of another debot"""

        def __init__(self, debot_addr: str, action: 'DebotAction'):
            """
            :param debot_addr: Address of debot in blockchain
            :param action: Debot action to execute
            """
            super(ParamsOfAppDebotBrowser.InvokeDebot, self).__init__(
                type='InvokeDebot'
            )
            self.debot_addr = debot_addr
            self.action = action

    class Send(BaseTypedType):
        """Used by Debot to call DInterface implemented by Debot Browser"""

        def __init__(self, message: str):
            """
            :param message: Internal message to DInterface address. Message
                    body contains interface function and parameters
            """
            super(ParamsOfAppDebotBrowser.Send, self).__init__(type='Send')
            self.message = message

    class Approve(BaseTypedType):
        """
        Requests permission from DeBot Browser to execute DeBot operation
        """

        def __init__(self, activity: 'DebotActivityType'):
            """
            :param activity: DeBot activity details
            """
            super(ParamsOfAppDebotBrowser.Approve, self).__init__(type='Approve')
            self.activity = activity

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ParamsOfAppDebotBrowserType':
        """Object from dict"""
        if data.get('action'):
            data['action'] = DebotAction(**data['action'])
        if data.get('activity'):
            data['activity'] = DebotActivity.from_dict(data=data['activity'])
        kwargs = {k: v for k, v in data.items() if k != 'type'}
        return getattr(ParamsOfAppDebotBrowser, data['type'])(**kwargs)


class ResultOfAppDebotBrowser:
    """Returning values from Debot Browser callbacks"""

    class Input(BaseTypedType):
        """Result of user input"""

        def __init__(self, value: str):
            """
            :param value: String entered by user
            """
            super(ResultOfAppDebotBrowser.Input, self).__init__(type='Input')
            self.value = value

        @property
        def dict(self):
            return {
                **super(ResultOfAppDebotBrowser.Input, self).dict,
                'value': self.value,
            }

    class GetSigningBox(BaseTypedType):
        """Result of getting signing box"""

        def __init__(self, signing_box: 'SigningBoxHandle'):
            """
            :param signing_box: Signing box for signing data requested by
                    debot engine. Signing box is owned and disposed by debot
                    engine
            """
            super(ResultOfAppDebotBrowser.GetSigningBox, self).__init__(
                type='GetSigningBox'
            )
            self.signing_box = signing_box

        @property
        def dict(self):
            return {
                **super(ResultOfAppDebotBrowser.GetSigningBox, self).dict,
                'signing_box': self.signing_box,
            }

    class InvokeDebot(BaseTypedType):
        """Result of debot invoking"""

        def __init__(self):
            super(ResultOfAppDebotBrowser.InvokeDebot, self).__init__(
                type='InvokeDebot'
            )

    class Approve(BaseTypedType):
        """Result of approve callback"""

        def __init__(self, approved: bool):
            """
            :param approved: Indicates whether the DeBot is allowed to
                    perform the specified operation
            """
            super(ResultOfAppDebotBrowser.Approve, self).__init__(type='Approve')
            self.approved = approved

        @property
        def dict(self):
            return {
                **super(ResultOfAppDebotBrowser.Approve, self).dict,
                'approved': self.approved,
            }


class ParamsOfStart:
    """Parameters to start debot"""

    def __init__(self, debot_handle: 'DebotHandle'):
        """
        :param debot_handle: Debot handle which references an instance of
                debot engine
        """
        self.debot_handle = debot_handle

    @property
    def dict(self):
        """Dict from object"""
        return {'debot_handle': self.debot_handle}


class ParamsOfFetch:
    """Parameters to fetch debot"""

    def __init__(self, address: str):
        """
        :param address: Debot smart contract address
        """
        self.address = address

    @property
    def dict(self):
        """Dict from object"""
        return {'address': self.address}


class ResultOfFetch:
    """ResultOfFetch"""

    def __init__(self, info: 'DebotInfo'):
        """
        :param info: Debot metadata
        """
        self.info = info


class ParamsOfExecute:
    """Parameters for executing debot action"""

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
        """Dict from object"""
        return {'debot_handle': self.debot_handle, 'action': self.action.dict}


class ParamsOfSend:
    """Parameters of send function"""

    def __init__(self, debot_handle: 'DebotHandle', message: str):
        """
        :param debot_handle: Debot handle which references an instance of
                debot engine
        :param message: BOC of internal message to debot encoded in `base64`
        """
        self.debot_handle = debot_handle
        self.message = message

    @property
    def dict(self):
        """Dict from object"""
        return {'debot_handle': self.debot_handle, 'message': self.message}


class ParamsOfRemove:
    """ParamsOfRemove"""

    def __init__(self, debot_handle: 'DebotHandle'):
        """
        :param debot_handle: Debot handle which references an instance of
                debot engine
        """
        self.debot_handle = debot_handle

    @property
    def dict(self):
        """Dict from object"""
        return {'debot_handle': self.debot_handle}


class DebotState(int, Enum):
    """Debot state types"""

    ZERO = 0
    CURRENT = 253
    PREV = 254
    EXIT = 255


# PROOFS module
class ProofsErrorCode(int, Enum):
    """Proofs module error codes"""

    INVALID_DATA = 901
    PROOF_CHECK_FAILED = 902
    INTERNAL_ERROR = 903
    DATA_DIFFERS_FROM_PROVEN = 904


class ParamsOfProofBlockData:
    """ParamsOfProofBlockData"""

    def __init__(self, block: Dict[str, Any]):
        """
        :param block: Single block's data, retrieved from TONOS API,
                that needs proof. Required fields are `id` and/or
                top-level `boc` (for block identification), others are optional
        """
        self.block = block

    @property
    def dict(self):
        """Dict from object"""
        return {'block': self.block}


class ParamsOfProofTransactionData:
    """ParamsOfProofTransactionData"""

    def __init__(self, transaction: Dict[str, Any]):
        """
        :param transaction: Single transaction's data as queried from DApp
                server, without modifications. The required fields are `id`
                and/or top-level `boc`, others are optional. In order to
                reduce network requests count, it is recommended to provide
                `block_id` and `boc` of transaction
        """
        self.transaction = transaction

    @property
    def dict(self):
        """Dict from object"""
        return {'transaction': self.transaction}


class ParamsOfProofMessageData:
    """ParamsOfProofMessageData"""

    def __init__(self, message: Dict[str, Any]):
        """
        :param message: Single message's data as queried from DApp server,
                without modifications. The required fields are id and/or
                top-level `boc`, others are optional.
                In order to reduce network requests count, it is recommended
                to provide at least `boc` of message and non-null
                `src_transaction.id` or `dst_transaction.id`
        """
        self.message = message

    @property
    def dict(self):
        """Dict from object"""
        return {'message': self.message}


# Aggregated types
AbiType = Union[Abi.Contract, Abi.Json, Abi.Handle, Abi.Serialized]
SignerType = Union[Signer.NoSigner, Signer.External, Signer.Keys, Signer.SigningBox]
AppRequestResultType = Union[AppRequestResult.Ok, AppRequestResult.Error]
MessageSourceType = Union[MessageSource.Encoded, MessageSource.EncodingParams]
StateInitSourceType = Union[
    StateInitSource.Message, StateInitSource.StateInit, StateInitSource.Tvc
]
ProcessingEventType = Union[
    ProcessingEvent.WillFetchFirstBlock,
    ProcessingEvent.FetchNextBlockFailed,
    ProcessingEvent.WillSend,
    ProcessingEvent.DidSend,
    ProcessingEvent.SendFailed,
    ProcessingEvent.WillFetchNextBlock,
    ProcessingEvent.FetchNextBlockFailed,
    ProcessingEvent.MessageExpired,
]
AccountForExecutorType = Union[
    AccountForExecutor.NoAccount, AccountForExecutor.Uninit, AccountForExecutor.Account
]
AddressStringFormatType = Union[
    AddressStringFormat.AccountId, AddressStringFormat.Hex, AddressStringFormat.Base64
]
DebotActivityType = DebotActivity.Transaction
ParamsOfAppDebotBrowserType = Union[
    ParamsOfAppDebotBrowser.Log,
    ParamsOfAppDebotBrowser.Switch,
    ParamsOfAppDebotBrowser.SwitchCompleted,
    ParamsOfAppDebotBrowser.ShowAction,
    ParamsOfAppDebotBrowser.Input,
    ParamsOfAppDebotBrowser.GetSigningBox,
    ParamsOfAppDebotBrowser.InvokeDebot,
    ParamsOfAppDebotBrowser.Send,
    ParamsOfAppDebotBrowser.Approve,
]
ParamsOfQueryOperationType = Union[
    ParamsOfQueryOperation.QueryCollection,
    ParamsOfQueryOperation.WaitForCollection,
    ParamsOfQueryOperation.AggregateCollection,
    ParamsOfQueryOperation.QueryCounterparties,
]
BocCacheTypeType = Union[BocCacheType.Pinned, BocCacheType.Unpinned]
BuilderOpType = Union[
    BuilderOp.Integer,
    BuilderOp.BitString,
    BuilderOp.Cell,
    BuilderOp.CellBoc,
    BuilderOp.Address,
]
ParamsOfAppSigningBoxType = Union[
    ParamsOfAppSigningBox.GetPublicKey, ParamsOfAppSigningBox.Sign
]
ParamsOfAppEncryptionBoxType = Union[
    ParamsOfAppEncryptionBox.GetInfo,
    ParamsOfAppEncryptionBox.Encrypt,
    ParamsOfAppEncryptionBox.Decrypt,
]
EncryptionAlgorithmType = EncryptionAlgorithm.Aes
ParamsOfAppPasswordProviderType = ParamsOfAppPasswordProvider.GetPassword
CryptoBoxSecretType = Union[
    CryptoBoxSecret.RandomSeedPhrase,
    CryptoBoxSecret.PredefinedSeedPhrase,
    CryptoBoxSecret.EncryptedSecret,
]
BoxEncryptionAlgorithmType = Union[
    BoxEncryptionAlgorithm.ChaCha20,
    BoxEncryptionAlgorithm.NaclBox,
    BoxEncryptionAlgorithm.NaclSecretBox,
]
