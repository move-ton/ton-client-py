import json
from io import StringIO
from typing import Dict, Union, Any

DEFAULT_MNEMONIC_DICTIONARY = 1
DEFAULT_MNEMONIC_WORD_COUNT = 12
DEFAULT_HDKEY_DERIVATION_PATH = "m/44'/396'/0'/0/0"


class MnemonicDictionary(object):
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


class Abi(object):
    def __init__(self, abi: Union[Dict, str, int], abi_type: str):
        """
        :param abi: ABI dict, ABI JSON string or handle
        :param abi_type: One of 'Contract', 'Json' 'Handle'
        """
        self.abi = abi
        self.abi_type = abi_type

    @property
    def dict(self):
        return {'type': self.abi_type, 'value': self.abi}

    @staticmethod
    def from_dict(abi: Dict[str, Any]) -> 'Abi':
        return Abi(abi=abi, abi_type='Contract')

    @staticmethod
    def from_string(abi_json: str) -> 'Abi':
        return Abi(abi=abi_json, abi_type='Json')

    @staticmethod
    def from_path(path: str, as_dict: bool = False) -> 'Abi':
        with open(path, 'r') as fp:
            abi = fp.read()
        if as_dict:
            return Abi.from_dict(abi=json.loads(abi))
        return Abi.from_string(abi_json=abi)

    @staticmethod
    def from_handle(handle: int) -> 'Abi':
        return Abi(abi=handle, abi_type='Handle')


class Signer(object):
    def __init__(
            self, keypair: KeyPair = None, public: str = None,
            box_handle: int = None):
        """
        :param keypair: message will be signed using the provided keys
        :param public: message will be signed using external methods.
                Public key must be provided with 'hex' encoding
        :param box_handle: message will be signed using the provided
                signing box
        """
        self.keypair = keypair
        self.public = public
        self.box_handle = box_handle

    @property
    def dict(self):
        if self.keypair:
            return {'type': 'Keys', 'keys': self.keypair.dict}
        elif self.public:
            return {'type': 'External', 'public_key': self.public}
        elif self.box_handle:
            return {'type': 'SigningBox', 'handle': self.box_handle}
        return {'type': 'None'}

    @staticmethod
    def none() -> 'Signer':
        return Signer()

    @staticmethod
    def from_keypair(keypair: KeyPair) -> 'Signer':
        return Signer(keypair=keypair)

    @staticmethod
    def from_external(public: str) -> 'Signer':
        return Signer(public=public)

    @staticmethod
    def from_signing_box(box_handle: int) -> 'Signer':
        return Signer(box_handle=box_handle)


class DeploySet(object):
    def __init__(
            self, tvc: str, workchain_id: int = 0,
            initial_data: Dict[str, Any] = None):
        """
        :param tvc: Base64 encoded TVC file content
        :param workchain_id: Target workchain for destination address
        :param initial_data: Initial values for contract's public variables
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


class CallSet(object):
    def __init__(
            self, function_name: str, header: Dict[str, Any] = None,
            inputs: Dict[str, Any] = None):
        """
        :param function_name: Function name
        :param header: Function header. If an application omit some parameters
                required by the contract's ABI, the library will set the
                default values for it
        :param inputs: Function input according to ABI
        """
        self.function_name = function_name
        self.header = header
        self.input = inputs

    @property
    def dict(self):
        return {
            'function_name': self.function_name,
            'header': self.header,
            'input': self.input
        }


class MessageSource(object):
    def __init__(self, source_type: str, **kwargs):
        """
        :param source_type: One of 'Encoded', 'EncodingParams'
        :param kwargs:
        """
        self.source_type = source_type
        self._kwargs = kwargs
        for name, value in kwargs.items():
            setattr(self, name, value)

    @property
    def dict(self):
        params = {
            key: value.dict if hasattr(value, 'dict') else value
            for key, value in self._kwargs.items()
        }
        return {'type': self.source_type, **params}

    @staticmethod
    def from_encoded(message: str, abi: Abi = None) -> 'MessageSource':
        return MessageSource(source_type='Encoded', message=message, abi=abi)

    @staticmethod
    def from_encoding_params(**kwargs) -> 'MessageSource':
        """
        :param kwargs: The same kwargs as for 'abi.encode_message' method
        :return:
        """
        return MessageSource(source_type='EncodingParams', **kwargs)


class StateInitSource(object):
    def __init__(self, source_type: str, **kwargs):
        """
        :param source_type: One of 'Message', 'StateInit', 'Tvc'
        """
        self.source_type = source_type
        self._kwargs = kwargs

    @property
    def dict(self):
        return {'type': self.source_type, **self._kwargs}

    @staticmethod
    def from_message(message: MessageSource) -> 'StateInitSource':
        """
        :param message: Deploy message
        :return:
        """
        return StateInitSource(source_type='Message', source=message.dict)

    @staticmethod
    def from_state_init(
            code: str, data: str, library: str = None) -> 'StateInitSource':
        """
        :param code: Base64 encoded code BOC
        :param data: Base64 encoded data BOC
        :param library: Base64 encoded library BOC
        :return:
        """
        return StateInitSource(
            source_type='StateInit', code=code, data=data, library=library)

    @staticmethod
    def from_tvc(
            tvc: str, public_key: str = None, abi: Abi = None,
            value: Any = None) -> 'StateInitSource':
        """
        :param tvc: Base64 encoded TVC data
        :param public_key: Hex encoded public key
        :param abi: Contract ABI
        :param value: Value to pass. If provided 'abi' is required
        :return:
        """
        init_params = None
        if abi and value:
            init_params = {'abi': abi.dict, 'value': value}
        return StateInitSource(
            source_type='Tvc', tvc=tvc, public_key=public_key,
            init_params=init_params)


class AddressStringFormat(object):
    AccountId = {'type': 'AccountId'}
    Hex = {'type': 'Hex'}

    @staticmethod
    def base64(
            url: bool = False, test: bool = False, bounce: bool = False
    ) -> Dict[str, Union[str, bool]]:
        return {'type': 'Base64', 'url': url, 'test': test, 'bounce': bounce}


class AccountForExecutor(object):
    def __init__(
            self, uninit: bool = False, boc: str = None,
            unlimited_balance: bool = False):
        self._uninit = uninit
        self._boc = boc
        self._unlimited_balance = unlimited_balance

    @property
    def dict(self) -> Dict[str, Any]:
        if self._uninit:
            return {'type': 'Uninit'}
        elif self._boc:
            return {
                'type': 'Account',
                'boc': self._boc,
                'unlimited_balance': self._unlimited_balance
            }
        return {'type': 'None'}

    @staticmethod
    def none() -> 'AccountForExecutor':
        return AccountForExecutor()

    @staticmethod
    def uninit() -> 'AccountForExecutor':
        """
        Emulate uninitialized account to run deploy message
        :return:
        """
        return AccountForExecutor(uninit=True)

    @staticmethod
    def from_account(
            boc: str, unlimited_balance: bool = False
    ) -> 'AccountForExecutor':
        """
        :param boc: Base64 encoded account BOC
        :param unlimited_balance: Flag for running account with the unlimited
                balance. Can be used to calculate transaction fees without
                balance check
        :return:
        """
        return AccountForExecutor(boc=boc, unlimited_balance=unlimited_balance)
