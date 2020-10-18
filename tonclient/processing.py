from tonclient.decorators import Response
from tonclient.module import TonModule
from tonclient.types import Abi, MessageSource


class TonProcessing(TonModule):
    """ Free TON processing SDK API implementation """
    def process_message(self, message: MessageSource, send_events: bool):
        """
        :param message: Message source
        :param send_events: Flag for requesting events sending
        :return:
        """
        return self.request(
            method='processing.process_message', as_iterable=send_events,
            message=message.dict, send_events=send_events)

    @Response.send_message
    def send_message(
            self, message: str, send_events: bool, abi: Abi = None) -> str:
        """
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
            abi: Abi = None):
        """
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
