import base64
import json
from typing import Dict

from tonsdk.lib import TonClient


class TonContract(object):
    """
    Work with TON contracts.
    https://github.com/tonlabs/TON-SDK/wiki/Core-Library-JSON-API
    """
    TYPE_ADDRESS_B64 = "Base64"
    TYPE_ADDRESS_HEX = "Hex"
    TYPE_ADDRESS_ID = "AccountId"

    def __init__(self):
        self.abi = None
        self.image = None
        self.keypair = None
        self.address = None

        self._client: (TonClient, None) = None

    @property
    def image_b64(self) -> str:
        """ Base64 contract image representation """
        return base64.b64encode(self.image).decode("utf8")

    def set_client(self, client: TonClient):
        """ Set client for contract """
        self._client = client

    def setup_client(self, settings: dict):
        """ Setup client with custom settings """
        self._client.setup(settings)

    def load_abi(self, path: str):
        """ Load contract ABI from file """
        with open(path, 'r') as fp:
            abi = fp.read()
            self.abi = json.loads(abi)

    def load_image(self, path: str):
        """ Load contract from code file """
        with open(path, 'rb') as fp:
            self.image = fp.read()

    def load_keypair(self, path: str, binary: bool):
        """ Load keys from json or binary file """
        if binary:
            with open(path, 'rb') as fp:
                keys = fp.read().hex()
                self.keypair = {"public": keys[64:], "secret": keys[:64]}
        else:
            with open(path, 'r') as fp:
                keys = fp.read()
                self.keypair = json.loads(keys)

    def deploy_address(
            self, init_params: Dict = None, workchain_id: int = 0) -> str:
        """
        Get contract address.

        :param init_params:
        :param workchain_id:
        :return: address
        """
        params = {
            "abi": self.abi,
            "initParams": init_params or {},
            "imageBase64": self.image_b64,
            "keyPair": self.keypair,
            "workchainId": workchain_id
        }

        address = self._client.request(
            method="contracts.deploy.address", params=params)
        self.address = address

        return address

    def convert_address(self, to: str, b64_params: dict = None) -> str:
        """
        :param to: Convert to. One of 'AccountId', 'Hex', 'Base64'
        :param b64_params: Convert params when converting to base64.
                           {url: bool, test: bool, bounce: bool}
        :return:
        """
        params = {
            "address": self.address,
            "convertTo": to,
            "base64Params": b64_params
        }

        result = self._client.request(
            method="contracts.address.convert", params=params)

        return result["address"]

    def deploy_message(
            self, constructor_params: Dict = None, constructor_header: Dict = None,
            init_params: Dict = None, workchain_id: int = None) -> Dict:
        """
        This method is a part of the standard deploy script and is used to
        create a message to the blockchain to get a contract address before
        an actual deploy.
        It has the same parameters as the general deploy method.
        It returns an address in raw format. In TON you need contract
        address before an actual deploy to send [test] tokens to it.
        Given the gas logic, you cannot deploy a contract with zero balance.

        :param constructor_params: Contract constructor arguments
        :param constructor_header: Contract constructor header
        :param init_params: Additional parameters in a form of an
                object that are saved right to the Persistent Storage (c4)
                during deployment. This field determines the contract address
                (in combination with the contract code). In previous versions
                it only included the public key, but now it can store
                additional data.
        :param workchain_id: Default will be 0
        :return: Dict
        """
        params = {
            "constructorParams": constructor_params or {},
            "constructorHeader": constructor_header or {},
            "initParams": init_params or {},
            "abi": self.abi,
            "imageBase64": self.image_b64,
            "keyPair": self.keypair,
            "workchainId": workchain_id
        }

        result = self._client.request(
            method="contracts.deploy.message", params=params)
        self.address = result["address"]

        return result

    def deploy_message_unsigned(
            self, constructor_params: Dict = None, init_params: Dict = None) \
            -> Dict:
        """
        This function allows creating a separate deploy message
        without a signature.
        You may need this function if in your architecture signing is
        performed at an HSM or some kind of offline hardware wallet where
        the private key is stored.
        The method creates a byte block that has to be signed via a specific
        cryptographic method.

        :param constructor_params:
        :param init_params:
        :return:
        """
        params = {
            "abi": self.abi,
            "constructorParams": constructor_params or {},
            "initParams": init_params or {},
            "imageBase64": self.image_b64,
            "publicKeyHex": self.keypair["public"]
        }

        return self._client.request(
            method="contracts.deploy.encode_unsigned_message", params=params)

    def deploy_data(
            self, init_params: Dict = None, workchain_id: int = 0) -> Dict:
        """
        :param init_params:
        :param workchain_id:
        :return:
        """
        params = {
            "abi": self.abi or {},
            "initParams": init_params or {},
            "imageBase64": self.image_b64,
            "publicKeyHex": self.keypair["public"],
            "workchainId": workchain_id
        }

        return self._client.request(
            method="contracts.deploy.data", params=params)

    def deploy(
            self, constructor_params: Dict = None,
            constructor_header: Dict = None, init_params: Dict = None,
            workchain_id: int = None, try_index: str = None) -> Dict:
        """
        Deploy contract to blockchain

        :param constructor_params: Contract constructor arguments
        :param constructor_header: Contract constructor header
        :param init_params: Additional parameters in a form of an
                object that are saved right to the Persistent Storage (c4)
                during deployment. This field determines the contract address
                (in combination with the contract code). In previous versions
                it only included the public key, but now it can store
                additional data.
        :param workchain_id: Default will be 0
        :param try_index:
        :return: Dict
        """
        params = {
            "constructorParams": constructor_params or {},
            "constructorHeader": constructor_header or {},
            "initParams": init_params or {},
            "abi": self.abi,
            "imageBase64": self.image_b64,
            "keyPair": self.keypair,
            "workchainId": workchain_id,
            "tryIndex": try_index
        }

        result = self._client.request(method="contracts.deploy", params=params)
        self.address = result["address"]

        return result

    def run_message(self, function_name: str, inputs: Dict = None) -> Dict:
        """
        This method is similar to 'deploy_message' but it applies to active
        contracts.
        It yields a TONContractMessage message body and the ID of public
        contract function that was called, not the contract address.

        :param function_name: Contract function name (ABI function)
        :param inputs: Contract function arguments (ABI inputs)
        :return: Dict
        """
        params = {
            "address": self.address,
            "abi": self.abi,
            "functionName": function_name,
            "input": inputs or {},
            "keyPair": self.keypair
        }

        return self._client.request(
            method="contracts.run.message", params=params)

    def run_message_unsigned(
            self, function_name: str, inputs: Dict = None) -> Dict:
        """
        This method works similarly to the 'deploy_message_unsigned', but
        it is designed to create a message returning the ID of the public
        contract function that is called without a signature.
        This method is another one that can be used in a distributed
        architecture (when messages are signed externally).

        :param function_name:
        :param inputs:
        :return:
        """
        params = {
            "address": self.address,
            "abi": self.abi,
            "functionName": function_name,
            "input": inputs or {}
        }

        return self._client.request(
            method="contracts.run.encode_unsigned_message", params=params)

    def run_body(
            self, function_name: str, internal: bool = False,
            inputs: Dict = None) -> str:
        """
        Creates only a message body with parameters encoded according
        to the ABI.

        :param function_name:
        :param internal:
        :param inputs:
        :return:
        """
        params = {
            "abi": self.abi,
            "function": function_name,
            "params": inputs or {},
            "internal": internal,
            "keyPair": self.keypair or {}
        }

        result = self._client.request(
            method="contracts.run.body", params=params)

        return result["bodyBase64"]

    def run(self, function_name: str, inputs: Dict = None) -> Dict:
        """
        This method is used to call contract methods within the blockchain.
        Calling run creates a message with the following serialized parameters
        and sends it to the blockchain. Message is serialized according to the
        ABI rules.
        After the message is sent run waits for it to be executed and returns
        a JSON-object with the resulting parameters.

        :param function_name: Contract function name (ABI function)
        :param inputs: Contract function arguments (ABI inputs)
        :return: Dict
        """
        params = {
            "address": self.address,
            "abi": self.abi,
            "functionName": function_name,
            "input": inputs or {},
            "keyPair": self.keypair
        }

        return self._client.request(method="contracts.run", params=params)

    def run_local(
            self, function_name: str, inputs: Dict = None,
            full_run: bool = False, time: int = None) -> Dict:
        """
        :param function_name:
        :param inputs:
        :param full_run:
        :param time:
        :return:
        """
        params = {
            "address": self.address,
            "abi": self.abi,
            "functionName": function_name,
            "input": inputs or {},
            "keyPair": self.keypair or {},
            "fullRun": full_run,
            "time": time
        }

        return self._client.request(
            method="contracts.run.local", params=params)

    def run_local_message(
            self, function_name: str, message: str, full_run: bool = False,
            time: int = None) -> Dict:
        """
        :param function_name:
        :param message: Message base64
        :param full_run:
        :param time:
        :return:
        """
        params = {
            "address": self.address,
            "abi": self.abi,
            "functionName": function_name,
            "messageBase64": message,
            "fullRun": full_run,
            "time": time
        }

        return self._client.request(
            method="contracts.run.local.msg", params=params)

    def run_output(
            self, function_name: str, body: str, internal: bool = False) -> Dict:
        """
        Decode a response message from a called contract.

        :param function_name:
        :param body: Base64 body
        :param internal:
        :return:
        """
        params = {
            "abi": self.abi,
            "functionName": function_name,
            "bodyBase64": body,
            "internal": internal
        }

        result = self._client.request(
            method="contracts.run.output", params=params)

        return result["output"]

    def run_fee(self, function_name: str, inputs: Dict = None) -> Dict:
        """
        :param function_name:
        :param inputs:
        :return:
        """
        params = {
            "address": self.address,
            "abi": self.abi,
            "functionName": function_name,
            "input": inputs or {}
        }

        return self._client.request(method="contracts.run.fee", params=params)

    def run_fee_message(self, message: str) -> dict:
        """
        :param message: Message base64
        :return:
        """
        params = {
            "address": self.address,
            "messageBase64": message
        }

        return self._client.request(
            method="contracts.run.fee.msg", params=params)

    def run_unknown_input(self, body: str, internal: bool = False) -> Dict:
        """
        :param body: Body base64
        :param internal:
        :return:
        """
        params = {
            "abi": self.abi,
            "bodyBase64": body,
            "internal": internal
        }

        return self._client.request(
            method="contracts.run.unknown.input", params=params)

    def run_unknown_output(self, body: str, internal: bool = False) -> Dict:
        """
        :param body: Body base64
        :param internal:
        :return:
        """
        params = {
            "abi": self.abi,
            "bodyBase64": body,
            "internal": internal
        }

        return self._client.request(
            method="contracts.run.unknown.output", params=params)

    def sign_message(
            self, unsigned_base64: str, sign_base64: str, expire: int = None) \
            -> Dict:
        """
        This method can also be used used in distributed architectures
        where message signing is carried out externally.

        :param unsigned_base64:
        :param sign_base64:
        :param expire:
        :return:
        """
        params = {
            "abi": self.abi,
            "unsignedBytesBase64": unsigned_base64,
            "signBytesBase64": sign_base64,
            "publicKeyHex": self.keypair["public"],
            "expire": expire
        }

        return self._client.request(
            method="contracts.encode_message_with_sign", params=params)

    def parse_message(self, message_boc: str) -> Dict:
        """
        Parse message from BOC

        :param message_boc: Message BOC base64
        :return:
        """
        params = {"bocBase64": message_boc}
        return self._client.request(
            method="contracts.parse.message", params=params)
