from typing import Dict, Any, List, Union

from tonsdk.module import TonModule
from tonsdk.types import KeyPair, TonMessage, TonMessageUnsigned


class TonContract(TonModule):
    """
    Free TON contracts SDK API implementation
    https://github.com/tonlabs/TON-SDK/wiki/
    """
    def load(self, address: str) -> Dict[str, str]:
        """
        Load contract
        :param address:
        :return:
        """
        return self.request(method="contracts.load", address=address)

    def deploy_address(
                self, abi: Dict[str, Any], image_b64: str, keypair: KeyPair,
                init_params: Dict[str, Any] = None, workchain_id: int = None
            ) -> str:
        """
        Get contract address
        :param abi:
        :param image_b64:
        :param keypair:
        :param init_params:
        :param workchain_id:
        :return: Address
        """
        return self.request(
            method="contracts.deploy.address", abi=abi,
            initParams=init_params or {}, imageBase64=image_b64,
            keyPair=keypair.dict, workchainId=workchain_id)

    def address_convert(
            self, address: str, to: str,
            b64_params: Dict[str, bool] = None) -> str:
        """
        :param address:
        :param to: Convert to. One of 'AccountId', 'Hex', 'Base64'
        :param b64_params: Convert params when converting to base64.
                           Example: {url: bool, test: bool, bounce: bool}
                           All keys must be specified.
        :return:
        """
        response = self.request(
            method="contracts.address.convert", address=address, convertTo=to,
            base64Params=b64_params)
        return response["address"]

    def deploy_message(
            self, abi: Dict[str, Any], image_b64: str, keypair: KeyPair,
            constructor_params: Dict[str, Any] = None,
            constructor_header: Dict[str, Any] = None,
            init_params: Dict[str, Any] = None,
            workchain_id: int = None, try_index: int = None) -> TonMessage:
        """
        This method is a part of the standard deploy script and is used to
        create a message to the blockchain to get a contract address before
        an actual deploy.
        It has the same parameters as the general deploy method.
        It returns an address in raw format. In TON you need contract
        address before an actual deploy to send [test] tokens to it.
        Given the gas logic, you cannot deploy a contract with zero balance.
        :param abi:
        :param image_b64:
        :param keypair:
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
        :return:
        """
        return self.request(
            method="contracts.deploy.message", abi=abi, imageBase64=image_b64,
            keyPair=keypair.dict, constructorParams=constructor_params or {},
            constructorHeader=constructor_header, initParams=init_params,
            workchainId=workchain_id, tryIndex=try_index)

    def deploy_encode_unsigned_message(
            self, abi: Dict[str, Any], image_b64: str, public: str,
            constructor_header: Dict[str, Any] = None,
            constructor_params: Dict[str, Any] = None,
            init_params: Dict = None, workchain_id: int = None,
            try_index: int = None) -> (TonMessageUnsigned, str):
        """
        This function allows creating a separate deploy message
        without a signature.
        You may need this function if in your architecture signing is
        performed at an HSM or some kind of offline hardware wallet where
        the private key is stored.
        The method creates a byte block that has to be signed via a specific
        cryptographic method.
        :param abi:
        :param image_b64:
        :param public: Public key as hex string
        :param constructor_header:
        :param constructor_params:
        :param init_params:
        :param workchain_id:
        :param try_index:
        :return:
        """
        response = self.request(
            method="contracts.deploy.encode_unsigned_message", abi=abi,
            imageBase64=image_b64, publicKeyHex=public,
            constructorHeader=constructor_header,
            constructorParams=constructor_params or {}, initParams=init_params,
            workchainId=workchain_id, tryIndex=try_index)
        return response["encoded"], response["addressHex"]

    def deploy_data(
            self, public: str, abi: Dict[str, Any] = None,
            image_b64: str = None, init_params: Dict[str, Any] = None,
            workchain_id: int = None) -> Dict[str, Any]:
        """
        :param abi:
        :param image_b64:
        :param public: Public key as hex string
        :param init_params:
        :param workchain_id:
        :return:
        """
        return self.request(
            method="contracts.deploy.data", abi=abi, imageBase64=image_b64,
            publicKeyHex=public, initParams=init_params,
            workchainId=workchain_id)

    def deploy(
            self, abi: Dict[str, Any], image_b64: str, keypair: KeyPair,
            constructor_params: Dict[str, Any] = None,
            constructor_header: Dict[str, Any] = None,
            init_params: Dict[str, Any] = None, workchain_id: int = None,
            try_index: str = None) -> Dict[str, Any]:
        """
        Deploy contract to blockchain
        :param abi:
        :param image_b64:
        :param keypair:
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
        :return:
        """
        return self.request(
            method="contracts.deploy", abi=abi, imageBase64=image_b64,
            keyPair=keypair.dict, constructorParams=constructor_params or {},
            constructorHeader=constructor_header, initParams=init_params,
            workchainId=workchain_id, tryIndex=try_index)

    def run_message(
            self, address: str, abi: Dict[str, Any], function_name: str,
            headers: Dict[str, Any] = None, inputs: Dict[str, Any] = None,
            keypair: KeyPair = None, try_index: int = None) -> TonMessage:
        """
        This method is similar to 'deploy_message' but it applies to active
        contracts.
        It yields a TONContractMessage message body and the ID of public
        contract function that was called, not the contract address.
        :param abi:
        :param address:
        :param keypair:
        :param function_name: Contract function name (ABI function)
        :param inputs: Contract function arguments (ABI inputs)
        :param headers:
        :param try_index:
        :return:
        """
        if keypair:
            keypair = keypair.dict

        return self.request(
            method="contracts.run.message", address=address, abi=abi,
            functionName=function_name, header=headers, input=inputs or {},
            keypair=keypair, tryIndex=try_index)

    def run_encode_unsigned_message(
            self, address: str, abi: Dict[str, Any], function_name: str,
            headers: Dict[str, Any] = None, inputs: Dict[str, Any] = None,
            try_index: int = None) -> TonMessageUnsigned:
        """
        This method works similarly to the 'deploy_message_unsigned', but
        it is designed to create a message returning the ID of the public
        contract function that is called without a signature.
        This method is another one that can be used in a distributed
        architecture (when messages are signed externally).
        :param abi:
        :param address:
        :param function_name:
        :param inputs:
        :param headers:
        :param try_index:
        :return:
        """
        return self.request(
            method="contracts.run.encode_unsigned_message", address=address,
            abi=abi, functionName=function_name, header=headers,
            input=inputs or {}, tryIndex=try_index)

    def run_body(
            self, abi: Dict[str, Any], function_name: str,
            headers: Dict[str, Any] = None, inputs: Dict[str, Any] = None,
            keypair: KeyPair = None, internal: bool = False) -> str:
        """
        Creates only a message body with parameters encoded according
        to the ABI.
        :param abi:
        :param keypair:
        :param function_name:
        :param internal:
        :param inputs:
        :param headers:
        :return:
        """
        if keypair:
            keypair = keypair.dict

        result = self.request(
            method="contracts.run.body", abi=abi, function=function_name,
            header=headers, params=inputs or {}, internal=internal,
            keyPair=keypair)
        return result["bodyBase64"]

    def run(
            self, address: str, abi: Dict[str, Any], function_name: str,
            headers: Dict[str, Any] = None, inputs: Dict[str, Any] = None,
            keypair: KeyPair = None, try_index: int = None) -> Dict[str, Any]:
        """
        This method is used to call contract methods within the blockchain.
        Calling run creates a message with the following serialized parameters
        and sends it to the blockchain. Message is serialized according to the
        ABI rules.
        After the message is sent run waits for it to be executed and returns
        a JSON-object with the resulting parameters.
        :param abi:
        :param address:
        :param keypair:
        :param function_name: Contract function name (ABI function)
        :param inputs: Contract function arguments (ABI inputs)
        :param headers:
        :param try_index:
        :return:
        """
        if keypair:
            keypair = keypair.dict

        return self.request(
            method="contracts.run", address=address, abi=abi,
            functionName=function_name, header=headers, input=inputs or {},
            keyPair=keypair, tryIndex=try_index)

    def run_local_message(
            self, address: str, message_b64: str, account: str = None,
            abi: Dict[str, Any] = None, function_name: str = None,
            full_run: bool = False, time: int = None) -> Dict[str, Any]:
        """
        :param abi:
        :param address:
        :param account:
        :param function_name: This attr is required, if 'abi' was provided
        :param message_b64: Message body base64
        :param full_run:
        :param time:
        :return:
        """
        return self.request(
            method="contracts.run.local.msg", address=address,
            messageBase64=message_b64, account=account, abi=abi,
            functionName=function_name, fullRun=full_run, time=time)

    def run_local(
            self, address: str, abi: str, function_name: str,
            headers: Dict[str, Any] = None, inputs: Dict[str, Any] = None,
            account: str = None, keypair: KeyPair = None,
            full_run: bool = False, time: int = None) -> Dict[str, Any]:
        """
        :param address:
        :param abi:
        :param function_name:
        :param headers:
        :param inputs:
        :param account:
        :param keypair:
        :param full_run:
        :param time:
        :return:
        """
        if keypair:
            keypair = keypair.dict

        return self.request(
            method="contracts.run.local", address=address, abi=abi,
            functionName=function_name, header=headers, input=inputs or {},
            account=account, keyPair=keypair, fullRun=full_run, time=time)

    def run_output(
            self, abi: Dict[str, Any], function_name: str, body_b64: str,
            internal: bool = False) -> Dict[str, Any]:
        """
        Decode a response message from a called contract.
        :param abi:
        :param function_name:
        :param body_b64: Message base64 body
        :param internal:
        :return:
        """
        result = self.request(
            method="contracts.run.output", abi=abi, functionName=function_name,
            bodyBase64=body_b64, internal=internal)
        return result["output"]

    def run_fee(
            self, address: str, abi: Dict[str, Any], function_name: str,
            headers: Dict[str, Any] = None, inputs: Dict[str, Any] = None,
            keypair: KeyPair = None, try_index: int = None) -> Dict[str, Any]:
        """
        :param address:
        :param abi:
        :param function_name:
        :param headers:
        :param inputs:
        :param keypair:
        :param try_index:
        :return:
        """
        if keypair:
            keypair = keypair.dict

        return self.request(
            method="contracts.run.fee", address=address, abi=abi,
            functionName=function_name, header=headers, input=inputs or {},
            keyPair=keypair, tryIndex=try_index)

    def run_fee_message(
            self, address: str, message_b64: str, account: str = None,
            abi: [str, Dict] = None, function_name: str = None,
            full_run: bool = False, time: int = None) -> Dict[str, Any]:
        """
        :param address:
        :param message_b64: Message body base64
        :param account:
        :param abi:
        :param function_name:
        :param full_run:
        :param time:
        :return:
        """
        return self.request(
            method="contracts.run.fee.msg", address=address,
            messageBase64=message_b64, account=account, abi=abi,
            functionName=function_name, fullRun=full_run, time=time)

    def run_unknown_input(
            self, abi: Dict[str, Any], body_b64: str,
            internal: bool = False) -> Dict[str, Any]:
        """
        :param abi:
        :param body_b64: Body base64
        :param internal:
        :return:
        """
        return self.request(
            method="contracts.run.unknown.input", abi=abi, bodyBase64=body_b64,
            internal=internal)

    def run_unknown_output(
            self, abi: Dict[str, Any], body_b64: str,
            internal: bool = False) -> Dict[str, Any]:
        """
        :param abi:
        :param body_b64: Body base64
        :param internal:
        :return:
        """
        return self.request(
            method="contracts.run.unknown.output", abi=abi,
            bodyBase64=body_b64, internal=internal)

    def encode_message_with_sign(
            self, abi: Dict[str, Any], message: TonMessageUnsigned,
            public: str = None) -> TonMessage:
        """
        This method can also be used used in distributed architectures
        where message signing is carried out externally.
        :param abi:
        :param message:
        :param public: Public key as hex string
        :return:
        """
        if message.get("bytesToSignBase64"):
            message["signBytesBase64"] = message["bytesToSignBase64"]
            del message["bytesToSignBase64"]

        return self.request(
            method="contracts.encode_message_with_sign", abi=abi,
            publicKeyHex=public, **message)

    def parse_message(self, boc_b64: str) -> Dict[str, Any]:
        """
        Parse message from BOC
        :param boc_b64: Message BOC base64
        :return:
        """
        return self.request(
            method="contracts.parse.message", bocBase64=boc_b64)

    def function_id(
            self, abi: Dict[str, Any], function_name: str,
            inputs: bool = False) -> int:
        """
        Get contract function id.
        :param abi:
        :param function_name:
        :param inputs:
        :return:
        """
        result = self.request(
            method="contracts.function.id", abi=abi, function=function_name,
            input=inputs)
        return result["id"]

    def find_shard(
                self, address: str, shards: List[Dict[str, Union[int, str]]]
            ) -> Dict[str, Any]:
        """
        :param address:
        :param shards: Shard dict is {"workchain_id": int, "shard": str}
        :return:
        """
        return self.request(
            method="contracts.find.shard", address=address, shards=shards)

    def send_message(self, message: TonMessage) -> Dict[str, Any]:
        """
        Method sends messages to the node without waiting for the result.
        :param message:
        :return:
        """
        return self.request(
            method="contracts.send.message", **message)

    def process_message(
                self, message: TonMessage, abi: Dict[str, Any] = None,
                function_name: str = None, infinite_wait: bool = False
            ) -> Dict[str, Any]:
        """
        Method sends messages to the node and waits for the result.
        :param function_name: Required if argument 'abi' was provided
        :param message:
        :param abi:
        :param infinite_wait:
        :return:
        """
        return self.request(
            method="contracts.process.message", abi=abi,
            functionName=function_name, infiniteWait=infinite_wait,
            message=message)

    def process_transaction(
                self, address: str, transaction: Dict[str, Any],
                abi: Dict[str, Any] = None, function_name: str = None
            ) -> Dict[str, Any]:
        """
        :param address:
        :param abi:
        :param function_name: Required if argument 'abi' was provided
        :param transaction: Transaction dict. Can be retrieved from key
                    'transaction' of dict, which is returned by
                    'run', 'process_message' methods.
        :return:
        """
        return self.request(
            method="contracts.process.transaction", address=address,
            transaction=transaction, abi=abi, functionName=function_name)

    def wait_transaction(
            self, message: TonMessage, state: Dict[str, Union[str, int]],
            abi: Dict[str, Any] = None, function_name: str = None,
            infinite_wait: bool = False) -> Dict[str, Any]:
        """
        :param message: Message dict is
                {"address": str, "messageId": str, "messageBodyBase64": str,
                "expire": int|None}
        :param state: Message processing state dict. It is returned from
                    'send_message' method.
                    Example: {"lastBlockId": str, "sendingTime": int}
        :param function_name: Required if argument 'abi' was provided
        :param abi:
        :param infinite_wait:
        :return:
        """
        return self.request(
            method="contracts.wait.transaction", message=message,
            messageProcessingState=state, abi=abi, functionName=function_name,
            infiniteWait=infinite_wait)

    def tvm_get(
            self, function_name: str, boc_b64: str = None,
            code_b64: str = None, data_b64: str = None,
            inputs: Dict[str, Any] = None, address: str = None,
            balance: str = None, last_paid: int = None) -> Dict[str, Any]:
        """
        :param function_name:
        :param boc_b64: BOC base64
        :param code_b64: Code base64
        :param data_b64: Data base64
        :param inputs:
        :param address:
        :param balance:
        :param last_paid:
        :return:
        """
        return self.request(
            method="tvm.get", functionName=function_name, bocBase64=boc_b64,
            codeBase64=code_b64, dataBase64=data_b64, input=inputs or {},
            address=address, balance=balance, lastPaid=last_paid)

    def resolve_error(self):
        # TODO: Implement this method
        raise NotImplementedError
