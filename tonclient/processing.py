"""Processing module methods"""
from typing import Union, Awaitable

from tonclient.module import TonModule
from tonclient.types import (
    ParamsOfSendMessage,
    ResultOfSendMessage,
    ParamsOfWaitForTransaction,
    ResultOfProcessMessage,
    ResponseHandler,
    ParamsOfProcessMessage,
    ParamsOfMonitorMessages,
    ParamsOfGetMonitorInfo,
    MonitoringQueueInfo,
    ParamsOfFetchNextMonitorResults,
    ResultOfFetchNextMonitorResults,
    ParamsOfCancelMonitor,
    ParamsOfSendMessages,
    ResultOfSendMessages,
)


class TonProcessing(TonModule):
    """Free TON processing SDK API implementation"""

    def process_message(
        self, params: ParamsOfProcessMessage, callback: ResponseHandler = None
    ) -> Union[ResultOfProcessMessage, Awaitable[ResultOfProcessMessage]]:
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
        response = self.request(
            method='processing.process_message', callback=callback, **params.dict
        )
        return self.response(classname=ResultOfProcessMessage, response=response)

    def send_message(
        self, params: ParamsOfSendMessage, callback: ResponseHandler = None
    ) -> Union[ResultOfSendMessage, Awaitable[ResultOfSendMessage]]:
        """
        Sends message to the network.
        Sends message to the network and returns the last generated shard
        block of the destination account before the message was sent.
        It will be required later for message processing

        :param params: See `types.ParamsOfSendMessage`
        :param callback: Additional responses handler
        :return: See `types.ResultOfSendMessage`
        """
        response = self.request(
            method='processing.send_message', callback=callback, **params.dict
        )
        return self.response(classname=ResultOfSendMessage, response=response)

    def wait_for_transaction(
        self, params: ParamsOfWaitForTransaction, callback: ResponseHandler = None
    ) -> Union[ResultOfProcessMessage, Awaitable[ResultOfProcessMessage]]:
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
        response = self.request(
            method='processing.wait_for_transaction', callback=callback, **params.dict
        )
        return self.response(classname=ResultOfProcessMessage, response=response)

    def monitor_messages(
        self, params: ParamsOfMonitorMessages
    ) -> Union[None, Awaitable[None]]:
        """
        Starts monitoring for the processing results of the specified messages.

        Message monitor performs background monitoring for a message processing
        results for the specified set of messages.

        Message monitor can serve several isolated monitoring queues.
        Each monitor queue has a unique application defined identifier (or name)
        used to separate several queue's.

        There are two important lists inside of the monitoring queue:
            unresolved messages: contains messages requested by the application
                    for monitoring and not yet resolved;
            resolved results: contains resolved processing results for monitored
                    messages.

        Each monitoring queue tracks own unresolved and resolved lists.
        Application can add more messages to the monitoring queue at any time.

        Message monitor accumulates resolved results. Application should fetch this
        results with fetchNextMonitorResults function.

        When both unresolved and resolved lists becomes empty, monitor stops any
        background activity and frees all allocated internal memory.

        If monitoring queue with specified name already exists then messages will be
        added to the unresolved list.

        If monitoring queue with specified name does not exist then monitoring queue
        will be created with specified unresolved messages.

        :param params: See `types.ParamsOfMonitorMessages`
        """
        return self.request(method='processing.monitor_messages', **params.dict)

    def get_monitor_info(
        self, params: ParamsOfGetMonitorInfo
    ) -> Union[MonitoringQueueInfo, Awaitable[MonitoringQueueInfo]]:
        """
        Returns summary information about current state of the specified
        monitoring queue

        :param params: See `types.ParamsOfGetMonitorInfo`
        :return: See `types.MonitoringQueueInfo`
        """
        response = self.request(method='processing.get_monitor_info', **params.dict)
        return self.response(classname=MonitoringQueueInfo, response=response)

    def fetch_next_monitor_results(
        self, params: ParamsOfFetchNextMonitorResults
    ) -> Union[
        ResultOfFetchNextMonitorResults, Awaitable[ResultOfFetchNextMonitorResults]
    ]:
        """
        Fetches next resolved results from the specified monitoring queue.
        Results and waiting options are depends on the `wait` parameter.
        All returned results will be removed from the queue's resolved list

        :param params: See `types.ParamsOfFetchNextMonitorResults`
        :return: See `types.ResultOfFetchNextMonitorResults`
        """
        response = self.request(
            method='processing.fetch_next_monitor_results', **params.dict
        )
        return self.response(
            classname=ResultOfFetchNextMonitorResults, response=response
        )

    def cancel_monitor(
        self, params: ParamsOfCancelMonitor
    ) -> Union[None, Awaitable[None]]:
        """
        Cancels all background activity and releases all allocated system
        resources for the specified monitoring queue

        :param params: See `types.ParamsOfCancelMonitor`
        """
        return self.request(method='processing.cancel_monitor', **params.dict)

    def send_messages(
        self, params: ParamsOfSendMessages
    ) -> Union[ResultOfSendMessages, Awaitable[ResultOfSendMessages]]:
        """
        Sends specified messages to the blockchain

        :param params: See `types.ParamsOfSendMessages`
        :return: See `types.ResultOfSendMessages`
        """
        response = self.request(method='processing.send_messages', **params.dict)
        return self.response(classname=ResultOfSendMessages, response=response)
