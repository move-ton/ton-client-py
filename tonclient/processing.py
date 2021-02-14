from tonclient.decorators import result_as
from tonclient.module import TonModule
from tonclient.types import ParamsOfSendMessage, ResultOfSendMessage, \
    ParamsOfWaitForTransaction, ResultOfProcessMessage, ResponseHandler, \
    ParamsOfProcessMessage


class TonProcessing(TonModule):
    """ Free TON processing SDK API implementation """
    @result_as(classname=ResultOfProcessMessage)
    def process_message(
            self, params: ParamsOfProcessMessage,
            callback: ResponseHandler = None) -> ResultOfProcessMessage:
        """
        Creates message, sends it to the network and monitors its processing.
        Creates ABI-compatible message, sends it to the network and monitors
        for the result transaction. Decodes the output messages' bodies.

        If contract's ABI includes "expire" header, then SDK implements
        retries in case of unsuccessful message delivery within the expiration
        timeout: SDK recreates the message, sends it and processes it again.

        The intermediate events, such as `WillFetchFirstBlock`, `WillSend`,
        `DidSend`, `WillFetchNextBlock`, etc - are switched on/off by
        `send_events` flag and logged into the supplied callback function.
        The retry configuration parameters are defined in config.

        If contract's ABI does not include "expire" header then, if no
        transaction is found within the network timeout (see config parameter),
        exits with error
        :param params: See `types.ParamsOfProcessMessage`
        :param callback: Additional responses handler
        :return: See `types.ResultOfProcessMessage`
        """
        return self.request(
            method='processing.process_message', callback=callback,
            **params.dict)

    @result_as(classname=ResultOfSendMessage)
    def send_message(
            self, params: ParamsOfSendMessage, callback: ResponseHandler = None
    ) -> ResultOfSendMessage:
        """
        Sends message to the network.
        Sends message to the network and returns the last generated shard
        block of the destination account before the message was sent.
        It will be required later for message processing
        :param params: See `types.ParamsOfSendMessage`
        :param callback: Additional responses handler
        :return: See `types.ResultOfSendMessage`
        """
        return self.request(
            method='processing.send_message', callback=callback, **params.dict)

    @result_as(classname=ResultOfProcessMessage)
    def wait_for_transaction(
            self, params: ParamsOfWaitForTransaction,
            callback: ResponseHandler = None) -> ResultOfProcessMessage:
        """
        Performs monitoring of the network for the result transaction of the
        external inbound message processing.

        `send_events` enables intermediate events, such as
        `WillFetchNextBlock`, `FetchNextBlockFailed` that may be useful for
        logging of new shard blocks creation during message processing.

        Note, that presence of the abi parameter is critical for ABI compliant
        contracts. Message processing uses drastically different strategy for
        processing message for contracts which ABI includes "expire" header.

        When the ABI header expire is present, the processing uses message
        expiration strategy:
            - The maximum block gen time is set to
              `message_expiration_timeout + transaction_wait_timeout`;
            - When maximum block gen time is reached, the processing will be
              finished with `MessageExpired` error.

        When the ABI header expire isn't present or abi parameter isn't
        specified, the processing uses transaction waiting strategy:
            - The maximum block gen time is set to
              `now() + transaction_wait_timeout`.
            - If maximum block gen time is reached and no result transaction
              is found, the processing will exit with an error.
        :param params: See `types.ParamsOfWaitForTransaction`
        :param callback: Additional responses handler
        :return: See `types.ResultOfProcessMessage`
        """
        return self.request(
            method='processing.wait_for_transaction', callback=callback,
            **params.dict)
