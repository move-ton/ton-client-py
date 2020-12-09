import json
from io import StringIO
from typing import Dict, Union, Any

DEFAULT_MNEMONIC_DICTIONARY = 1
DEFAULT_MNEMONIC_WORD_COUNT = 12
DEFAULT_HDKEY_DERIVATION_PATH = "m/44'/396'/0'/0/0"


class MnemonicDictionary:
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
    def from_message(message: MessageSource) -> 'StateInitSource':
        """
        :param message: Deploy message
        :return:
        """
        return StateInitSource(source_type='Message', source=message)

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


class AddressStringFormat:
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


class BaseAppCallback(object):
    """ Base class for app callback params or results """
    def __init__(self, type: str):
        self.type = type

    @property
    def dict(self):
        return {'type': self.type}


class ParamsOfAppSigningBox:
    """ Signing box callbacks """
    class GetPublicKey(BaseAppCallback):
        def __init__(self, type: str = 'GetPublicKey'):
            super(ParamsOfAppSigningBox.GetPublicKey, self).__init__(
                type=type)

    class Sign(BaseAppCallback):
        def __init__(self, unsigned: str, type: str = 'Sign'):
            super(ParamsOfAppSigningBox.Sign, self).__init__(type=type)
            self.unsigned = unsigned

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Union[GetPublicKey, Sign]:
        return getattr(ParamsOfAppSigningBox, data['type'])(**data)


class ResultOfAppSigningBox:
    """ Returning values from signing box callbacks """
    class GetPublicKey(BaseAppCallback):
        def __init__(self, public_key: str, type: str = 'GetPublicKey'):
            super(ResultOfAppSigningBox.GetPublicKey, self).__init__(
                type=type)
            self.public_key = public_key

        @property
        def dict(self):
            return {
                **super(ResultOfAppSigningBox.GetPublicKey, self).dict,
                'public_key': self.public_key
            }

    class Sign(BaseAppCallback):
        def __init__(self, signature: str, type: str = 'Sign'):
            super(ResultOfAppSigningBox.Sign, self).__init__(type=type)
            self.signature = signature

        @property
        def dict(self):
            return {
                **super(ResultOfAppSigningBox.Sign, self).dict,
                'signature': self.signature
            }


class ParamsOfAppDebotBrowser:
    """
    UNSTABLE Debot Browser callbacks.
    Called by debot engine to communicate with debot browser
    """
    class Log(BaseAppCallback):
        def __init__(self, msg: str, type: str = 'Log'):
            super(ParamsOfAppDebotBrowser.Log, self).__init__(type=type)
            self.msg = msg

    class Switch(BaseAppCallback):
        def __init__(self, context_id: int, type: str = 'Switch'):
            super(ParamsOfAppDebotBrowser.Switch, self).__init__(type=type)
            self.context_id = context_id

    class ShowAction(BaseAppCallback):
        def __init__(self, action: 'DebotAction', type: str = 'ShowAction'):
            super(ParamsOfAppDebotBrowser.ShowAction, self).__init__(
                type=type)
            self.action = action

    class Input(BaseAppCallback):
        def __init__(self, prompt: str, type: str = 'Input'):
            super(ParamsOfAppDebotBrowser.Input, self).__init__(type=type)
            self.prompt = prompt

    class GetSigningBox(BaseAppCallback):
        def __init__(self, type: str = 'GetSigningBox'):
            super(ParamsOfAppDebotBrowser.GetSigningBox, self).__init__(
                type=type)

    class InvokeDebot(BaseAppCallback):
        def __init__(
                self, debot_addr: str, action: 'DebotAction',
                type: str = 'InvokeDebot'):
            super(ParamsOfAppDebotBrowser.InvokeDebot, self).__init__(
                type=type)
            self.debot_addr = debot_addr
            self.action = action

    @staticmethod
    def from_dict(
            data: Dict[str, Any]
    ) -> Union[Log, Switch, ShowAction, Input, GetSigningBox, InvokeDebot]:
        if data.get('action'):
            data['action'] = DebotAction(**data['action'])
        return getattr(ParamsOfAppDebotBrowser, data['type'])(**data)


class ResultOfAppDebotBrowser(object):
    """
    UNSTABLE
    Returning values from Debot Browser callbacks
    """
    class Input(BaseAppCallback):
        def __init__(self, value: str, type: str = 'Input'):
            super(ResultOfAppDebotBrowser.Input, self).__init__(type=type)
            self.value = value

        @property
        def dict(self):
            return {
                **super(ResultOfAppDebotBrowser.Input, self).dict,
                'value': self.value
            }

    class GetSigningBox(BaseAppCallback):
        def __init__(self, signing_box: int, type: str = 'GetSigningBox'):
            super(ResultOfAppDebotBrowser.GetSigningBox, self).__init__(
                type=type)
            self.signing_box = signing_box

        @property
        def dict(self):
            return {
                **super(ResultOfAppDebotBrowser.GetSigningBox, self).dict,
                'signing_box': self.signing_box
            }

    class InvokeDebot(BaseAppCallback):
        def __init__(self, type: str = 'InvokeDebot'):
            super(ResultOfAppDebotBrowser.InvokeDebot, self).__init__(
                type=type)


class AppRequestResult:
    class Error(object):
        def __init__(self, text: str):
            self.text = text

        @property
        def dict(self):
            return {'type': 'Error', 'text': self.text}

    class Ok(object):
        def __init__(self, result: Any):
            self.result = result

        @property
        def dict(self):
            return {'type': 'Ok', 'result': self.result}


class DebotState:
    ZERO = 0
    CURRENT = 253
    PREV = 254
    EXIT = 255


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
