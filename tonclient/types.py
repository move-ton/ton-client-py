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
    def __init__(self, abi: Union[Dict, int]):
        self._abi = abi

    @property
    def dict(self):
        if type(self._abi) is dict:
            return {'Serialized': self._abi}
        elif type(self._abi) is int:
            return {'Handle': self._abi}
        raise ValueError('ABI should be a dict or int')

    @staticmethod
    def load(path: str) -> 'Abi':
        with open(path, 'r') as fp:
            return Abi(abi=json.loads(fp.read()))


class Signer(object):
    def __init__(self, data: Union[KeyPair, str, int]):
        """
        :param data:
                - KeyPair: message will be signed using the
                  provided keys;
                - str: message will be signed using external methods. Public
                  key must be provided with 'hex' encoding;
                - int: message will be signed using the provided signing box
        """
        self._data = data

    @property
    def dict(self):
        if type(self._data) is KeyPair:
            return {'WithKeys': self._data.dict}
        elif type(self._data) is str:
            return {'External': self._data}
        elif type(self._data) is int:
            return {'Box': self._data}
        raise ValueError('Signer should be a Keypair, str or int')


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
