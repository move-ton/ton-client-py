import base64
import json
from typing import Dict

from tonsdk.lib import TonClient


class TonContract(object):
    """
    Work with TON contracts.
    https://github.com/tonlabs/TON-SDK/wiki/Core-Library-JSON-API
    """
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
        :returns: Dict
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
        :returns: Dict
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
