from typing import Dict, Any

from tonclient.module import TonModule
from tonclient.types import Abi, Signer, DeploySet, CallSet


class TonAbi(TonModule):
    """ Free TON abi SDK API implementation """
    def decode_message(self, abi: Abi, message: str) -> Dict[str, Any]:
        """
        :param abi: Contract ABI
        :param message: Message BOC
        :return:
        """
        return self.request(
            function_name='abi.decode_message', abi=abi.dict, message=message)

    # TODO: Implement method and test
    def encode_account(self):
        pass

    def encode_message(
            self, abi: Abi, signer: Signer, address: str = None,
            deploy_set: DeploySet = None, call_set: CallSet = None,
            processing_try_index: int = 0) -> Dict[str, str]:
        """
        :param abi: Contract ABI
        :param address: Contract address. Must be specified in case of
                non deploy message
        :param deploy_set: Deploy parameters. Must be specified in case of
                deploy message
        :param call_set: Function call parameters. Must be specified in
                non deploy message. In case of deploy message contains
                parameters of constructor
        :param signer: Signing parameters
        :param processing_try_index: Processing try index. Used in message
                processing with retries. Encoder uses the provided try index
                to calculate message expiration time. Expiration timeouts will
                grow with every retry
        :return:
        """
        deploy_set = deploy_set.dict if deploy_set else deploy_set
        call_set = call_set.dict if call_set else call_set
        return self.request(
            function_name='abi.encode_message', abi=abi.dict,
            address=address, deploy_set=deploy_set, call_set=call_set,
            signer=signer.dict, processing_try_index=processing_try_index)

    def attach_signature(
            self, abi: Abi, public_key: str, message: str, signature: str
    ) -> Dict[str, str]:
        """
        :param abi: Contract ABI
        :param public_key: Hex encoded public key
        :param message: Base64 encoded unsigned message BOC
        :param signature: Hex encoded signature
        :return:
        """
        return self.request(
            function_name='abi.attach_signature', abi=abi.dict,
            public_key=public_key, message=message, signature=signature)
