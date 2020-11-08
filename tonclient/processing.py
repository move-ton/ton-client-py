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
        :param address: Target address the message will be sent to. Must be
                specified in case of non-deploy message
        :param deploy_set: Deploy parameters. Must be specified in case of
                deploy message
        :param call_set: Function call parameters. Must be specified in case
                of non-deploy message. In case of deploy message it is optional
                and contains parameters of the functions that will to be
                called upon deploy transaction
        :param processing_try_index: Processing try index. Used in message
                processing with retries (if contract's ABI includes "expire"
                header). Encoder uses the provided try index to calculate
                message expiration time. The 1st message expiration time is
                specified in client config. Expiration timeouts will grow with
                every retry
        :param send_events: Flag for requesting events sending
        :return:
        """
        message_source = MessageSource.from_encoding_params(
            abi=abi, signer=signer, address=address, deploy_set=deploy_set,
            call_set=call_set, processing_try_index=processing_try_index)
        return self.request(
            method='processing.process_message', as_iterable=send_events,
            message_encode_params=message_source.dict, send_events=send_events)

    @Response.send_message
    def send_message(
            self, message: str, send_events: bool, abi: Abi = None
    ) -> Union[str, Generator]:
        """
        Sends message to the network
        :param message: Message BOC. Encoded with `base64`
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
        :param message: Message BOC. Encoded with `base64`
        :param shard_block_id: The last generated block id of the destination
                account shard before the message was sent. You must provide
                the same value as the `send_message` has returned
        :param send_events: Flag for requesting events sending
        :param abi: Optional ABI for decoding transaction results. If it is
                specified then the output messages bodies will be decoded
                according to this ABI. The `abi_decoded` result field will be
                filled out
        :return:
        """
        abi = abi.dict if abi else abi
        return self.request(
            method='processing.wait_for_transaction', message=message,
            shard_block_id=shard_block_id, send_events=send_events, abi=abi,
            as_iterable=send_events)
