from typing import Union, Dict, Any, Generator

from tonclient.decorators import Response
from tonclient.module import TonModule
from tonclient.types import Abi, MessageSource, Signer, DeploySet, CallSet


class TonProcessing(TonModule):
    """ Free TON processing SDK API implementation """
    def process_message(
            self, abi: Abi, signer: Signer, send_events: bool,
            address: str = None, deploy_set: DeploySet = None,
            call_set: CallSet = None, processing_try_index: int = 0
    ) -> Union[Dict[str, Any], Generator]:
        """
        Creates message, sends it to the network and monitors its processing
        :param abi: Contract ABI
        :param signer: Signing parameters
        :param address: Contract address. Must be specified in case of
                non deploy message
        :param deploy_set: Deploy parameters. Must be specified in case of
                deploy message
        :param call_set: Function call parameters. Must be specified in
                non deploy message. In case of deploy message contains
                parameters of constructor
        :param processing_try_index: Processing try index. Used in message
                processing with retries. Encoder uses the provided try index
                to calculate message expiration time. Expiration timeouts will
                grow with every retry
        :param send_events: Flag for requesting events sending
        :return:
        """
        message_source = MessageSource.from_encoding_params(
            abi=abi, signer=signer, address=address, deploy_set=deploy_set,
            call_set=call_set, processing_try_index=processing_try_index)
        return self.request(
            method='processing.process_message', as_iterable=send_events,
            message_encode_params=message_source.dict,
            send_events=send_events)

    @Response.send_message
    def send_message(
            self, message: str, send_events: bool, abi: Abi = None
    ) -> Union[str, Generator]:
        """
        Sends message to the network
        :param message: Message BOC
        :param send_events: Flag for requesting events sending
        :param abi: Optional message ABI. If this parameter is specified and
                the message has the 'expire' header then expiration time will
                be checked against the current time to prevent an unnecessary
                sending.
                The `message already expired` error will be returned in this
                case.
                Note that specifying `abi` for ABI compliant contracts is
                strongly recommended due to choosing proper processing strategy
        :return:
        """
        abi = abi.dict if abi else abi
        return self.request(
            method='processing.send_message', message=message,
            send_events=send_events, abi=abi, as_iterable=send_events)

    def wait_for_transaction(
            self, message: str, shard_block_id: str, send_events: bool,
            abi: Abi = None) -> Union[Dict[str, Any], Generator]:
        """
        Performs monitoring of the network for the result transaction
        :param message: Base64 encoded message BOC
        :param shard_block_id: Dst account shard block id before the message
                had been sent. You must provide the same value as the
                'send_message' has returned
        :param send_events: Flag for requesting events sending
        :param abi: Optional ABI for decoding transaction results. If it is
                specified then the output messages bodies will be decoded
                according to this ABI.
        :return:
        """
        abi = abi.dict if abi else abi
        return self.request(
            method='processing.wait_for_transaction', message=message,
            shard_block_id=shard_block_id, send_events=send_events, abi=abi,
            as_iterable=send_events)
