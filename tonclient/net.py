"""Net module methods"""
from typing import Union, Awaitable

from tonclient.module import TonModule
from tonclient.types import (
    ParamsOfQuery,
    ResultOfQuery,
    ParamsOfQueryCollection,
    ResultOfQueryCollection,
    ParamsOfWaitForCollection,
    ResultOfWaitForCollection,
    ResultOfSubscribeCollection,
    ParamsOfSubscribeCollection,
    ParamsOfFindLastShardBlock,
    ResultOfFindLastShardBlock,
    EndpointsSet,
    ParamsOfAggregateCollection,
    ResultOfAggregateCollection,
    ParamsOfBatchQuery,
    ResultOfBatchQuery,
    ResponseHandler,
    ParamsOfQueryCounterparties,
    ResultOfGetEndpoints,
    ParamsOfQueryTransactionTree,
    ResultOfQueryTransactionTree,
    ParamsOfCreateBlockIterator,
    RegisteredIterator,
    ParamsOfResumeBlockIterator,
    ParamsOfCreateTransactionIterator,
    ParamsOfResumeTransactionIterator,
    ParamsOfIteratorNext,
    ResultOfIteratorNext,
    ParamsOfSubscribe,
)


class TonNet(TonModule):
    """Free TON net SDK API implementation"""

    def query_collection(
        self, params: ParamsOfQueryCollection
    ) -> Union[ResultOfQueryCollection, Awaitable[ResultOfQueryCollection]]:
        """
        Queries collection data.
        Queries data that satisfies the `filter` conditions, limits the number
        of returned records and orders them. The projection fields are limited
        to result fields

        :param params: See `types.ParamsOfQueryCollection`
        :return: See `types.ResultOfQueryCollection`
        """
        response = self.request(method='net.query_collection', **params.dict)
        return self.response(classname=ResultOfQueryCollection, response=response)

    def wait_for_collection(
        self, params: ParamsOfWaitForCollection
    ) -> Union[ResultOfWaitForCollection, Awaitable[ResultOfWaitForCollection]]:
        """
        Returns an object that fulfills the conditions or waits for its
        appearance. Triggers only once.
        If object that satisfies the `filter` conditions already exists -
        returns it immediately. If not - waits for insert/update of data
        within the specified `timeout`, and returns it. The projection fields
        are limited to `result` fields

        :param params: See `types.ParamsOfWaitForCollection`
        :return: See `types.ResultOfWaitForCollection`
        """
        response = self.request(method='net.wait_for_collection', **params.dict)
        return self.response(classname=ResultOfWaitForCollection, response=response)

    def subscribe(
        self, params: ParamsOfSubscribe, callback: ResponseHandler = None
    ) -> Union[ResultOfSubscribeCollection, Awaitable[ResultOfSubscribeCollection]]:
        """
        Creates a subscription.
        The subscription is a persistent communication channel between client and
        Everscale Network.

        Important Notes on Subscriptions.
        Unfortunately sometimes the connection with the network brakes down.
        In this situation the library attempts to reconnect to the network.
        This reconnection sequence can take significant time. All of this time
        the client is disconnected from the network.

        Bad news is that all changes that happened while the client was
        disconnected are lost.

        Good news is that the client report errors to the callback when it
        loses and resumes connection.

        So, if the lost changes are important to the application then the application
        must handle these error reports.
        Library reports errors with responseType == 101 and the error object passed
        via params.

        When the library has successfully reconnected the application receives callback
        with responseType == 101 and params.code == 614 (NetworkModuleResumed).

        Application can use several ways to handle this situation:
            - If application monitors changes for the single object
              (for example specific account): application can perform a query for this
              object and handle actual data as a regular data from the subscription.
            - If application monitors sequence of some objects (for example
              transactions of the specific account): application must refresh all
              cached (or visible to user) lists where this sequences presents.

        :param params: See `types.ParamsOfSubscribe`
        :param callback: Additional responses handler
        :return: See `types.ResultOfSubscribeCollection`
        """
        response = self.request(
            method='net.subscribe', callback=callback, **params.dict
        )
        return self.response(classname=ResultOfSubscribeCollection, response=response)

    def subscribe_collection(
        self, params: ParamsOfSubscribeCollection, callback: ResponseHandler = None
    ) -> Union[ResultOfSubscribeCollection, Awaitable[ResultOfSubscribeCollection]]:
        """
        Creates a subscription.
        Triggers for each insert/update of data that satisfies the `filter`
        conditions. The projection fields are limited to `result` fields

        :param params: See `types.ParamsOfSubscribeCollection`
        :param callback: Additional responses handler
        :return:
        """
        response = self.request(
            method='net.subscribe_collection', callback=callback, **params.dict
        )
        return self.response(classname=ResultOfSubscribeCollection, response=response)

    def unsubscribe(
        self, params: ResultOfSubscribeCollection
    ) -> Union[None, Awaitable[None]]:
        """
        Cancels a subscription.
        Cancels a subscription specified by its handle

        :param params: See `types.ResultOfSubscribeCollection`
        """
        return self.request(method='net.unsubscribe', **params.dict)

    def query(
        self, params: ParamsOfQuery
    ) -> Union[ResultOfQuery, Awaitable[ResultOfQuery]]:
        """
        Performs DAppServer GraphQL query

        :param params: See `types.ResultOfQuery`
        :return: See `types.ResultOfQuery`
        """
        response = self.request(method='net.query', **params.dict)
        return self.response(classname=ResultOfQuery, response=response)

    def suspend(self) -> Union[None, Awaitable[None]]:
        """Suspends network module to stop any network activity"""
        return self.request(method='net.suspend')

    def resume(self) -> Union[None, Awaitable[None]]:
        """Resumes network module to enable network activity"""
        return self.request(method='net.resume')

    def find_last_shard_block(
        self, params: ParamsOfFindLastShardBlock
    ) -> Union[ResultOfFindLastShardBlock, Awaitable[ResultOfFindLastShardBlock]]:
        """
        :param params: See `types.ParamsOfFindLastShardBlock`
        :return: See `types.ResultOfFindLastShardBlock`
        """
        response = self.request(method='net.find_last_shard_block', **params.dict)
        return self.response(classname=ResultOfFindLastShardBlock, response=response)

    def fetch_endpoints(self) -> Union[EndpointsSet, Awaitable[EndpointsSet]]:
        """
        Requests the list of alternative endpoints from server

        :return: See `types.EndpointsSet`
        """
        response = self.request(method='net.fetch_endpoints')
        return self.response(classname=EndpointsSet, response=response)

    def set_endpoints(self, params: EndpointsSet) -> Union[None, Awaitable[None]]:
        """
        Sets the list of endpoints to use on re-init

        :param params: See `types.EndpointsSet`
        :return:
        """
        return self.request(method='net.set_endpoints', **params.dict)

    def get_endpoints(
        self,
    ) -> Union[ResultOfGetEndpoints, Awaitable[ResultOfGetEndpoints]]:
        """
        Requests the list of alternative endpoints from server

        :return: See `types.ResultOfGetEndpoints`
        """
        response = self.request(method='net.get_endpoints')
        return self.response(classname=ResultOfGetEndpoints, response=response)

    def aggregate_collection(
        self, params: ParamsOfAggregateCollection
    ) -> Union[ResultOfAggregateCollection, Awaitable[ResultOfAggregateCollection]]:
        """
        Aggregates collection data.
        Aggregates values from the specified `fields` for records that
        satisfies the `filter` conditions

        :param params: See `types.ParamsOfAggregateCollection`
        :return: See `types.ResultOfAggregateCollection`
        """
        response = self.request(method='net.aggregate_collection', **params.dict)
        return self.response(classname=ResultOfAggregateCollection, response=response)

    def batch_query(
        self, params: ParamsOfBatchQuery
    ) -> Union[ResultOfBatchQuery, Awaitable[ResultOfBatchQuery]]:
        """
        Performs multiple queries per single fetch

        :param params: See `types.ParamsOfBatchQuery`
        :return: See `types.ResultOfBatchQuery`
        """
        response = self.request(method='net.batch_query', **params.dict)
        return self.response(classname=ResultOfBatchQuery, response=response)

    def query_counterparties(
        self, params: ParamsOfQueryCounterparties
    ) -> Union[ResultOfQueryCollection, Awaitable[ResultOfQueryCollection]]:
        """
        Allows query and paginate through the list of accounts that the
        specified account has interacted with, sorted by the time of the last
        internal message between accounts.

        Attention: this query retrieves data from 'Counterparties' service
        which is not supported in the opensource version of DApp Server
        (and will not be supported) as well as in TON OS SE
        (will be supported in SE in future), but is always accessible via
        TON OS Devnet/Mainnet Clouds

        :param params: See `types.ParamsOfQueryCounterparties`
        :return: See `types.ResultOfQueryCollection`
        """
        response = self.request(method='net.query_counterparties', **params.dict)
        return self.response(classname=ResultOfQueryCollection, response=response)

    def query_transaction_tree(
        self, params: ParamsOfQueryTransactionTree
    ) -> Union[ResultOfQueryTransactionTree, Awaitable[ResultOfQueryTransactionTree]]:
        """
        Returns transactions tree for specific message.
        Performs recursive retrieval of the transactions tree produced by
        the specific message:
            in_msg -> dst_transaction -> out_messages -> dst_transaction -> ...
        All retrieved messages and transactions will be included into
        `result.messages` and `result.transactions` respectively.
        The retrieval process will stop when the retrieved transaction count
        is more than 50.
        It is guaranteed that each message in `result.messages` has the
        corresponding transaction in the `result.transactions`.
        But there are no guaranties that all messages from transactions
        `out_msgs` are presented in `result.messages`. So the application have
        to continue retrieval for missing messages if it requires.

        :param params: See `types.ParamsOfQueryTransactionTree`
        :return: See `types.ResultOfQueryTransactionTree`
        """
        response = self.request(method='net.query_transaction_tree', **params.dict)
        return self.response(classname=ResultOfQueryTransactionTree, response=response)

    def create_block_iterator(
        self, params: ParamsOfCreateBlockIterator
    ) -> Union[RegisteredIterator, Awaitable[RegisteredIterator]]:
        """
        Creates block iterator.
        Block iterator uses robust iteration methods that guaranties that
        every block in the specified range isn't missed or iterated twice.

        Items iterated is a JSON objects with block data.
        The minimal set of returned fields is:
        ```
            id
            gen_utime
            workchain_id
            shard
            after_split
            after_merge
            prev_ref {
                root_hash
            }
            prev_alt_ref {
                root_hash
            }
        ```

        Application should call the `remove_iterator` when iterator is no
        longer required

        :param params: See `types.ParamsOfCreateBlockIterator`
        :return: See `types.RegisteredIterator`
        """
        response = self.request(method='net.create_block_iterator', **params.dict)
        return self.response(classname=RegisteredIterator, response=response)

    def resume_block_iterator(
        self, params: ParamsOfResumeBlockIterator
    ) -> Union[RegisteredIterator, Awaitable[RegisteredIterator]]:
        """
        Resumes block iterator.
        The iterator stays exactly at the same position where the
        `resume_state` was caught.
        Application should call the `remove_iterator` when iterator is no
        longer required

        :param params: See `types.ParamsOfResumeBlockIterator`
        :return: See `types.RegisteredIterator`
        """
        response = self.request(method='net.resume_block_iterator', **params.dict)
        return self.response(classname=RegisteredIterator, response=response)

    def create_transaction_iterator(
        self, params: ParamsOfCreateTransactionIterator
    ) -> Union[RegisteredIterator, Awaitable[RegisteredIterator]]:
        """
        Creates transaction iterator.
        Transaction iterator uses robust iteration methods that guaranty
        that every transaction in the specified range isn't missed or
        iterated twice.

        Iterated item is a JSON objects with transaction data.
        The minimal set of returned fields is:
        ```
            id
            account_addr
            now
            balance_delta(format:DEC)
            bounce { bounce_type }
            in_message {
                id
                value(format:DEC)
                msg_type
                src
            }
            out_messages {
                id
                value(format:DEC)
                msg_type
                dst
            }
        ```

        Application should call the `remove_iterator` when iterator is no
        longer required

        :param params: See `types.ParamsOfCreateTransactionIterator`
        :return: See `types.RegisteredIterator`
        """
        response = self.request(method='net.create_transaction_iterator', **params.dict)
        return self.response(classname=RegisteredIterator, response=response)

    def resume_transaction_iterator(
        self, params: ParamsOfResumeTransactionIterator
    ) -> Union[RegisteredIterator, Awaitable[RegisteredIterator]]:
        """
        Resumes transaction iterator.
        The iterator stays exactly at the same position where the
        `resume_state` was caught.

        Note that `resume_state` doesn't store the account filter.
        If the application requires to use the same account filter as it was
        when the iterator was created then the application must pass the
        account filter again in `accounts_filter` parameter.

        Application should call the `remove_iterator` when iterator is no
        longer required

        :param params: See `types.ParamsOfResumeTransactionIterator`
        :return: See `types.RegisteredIterator`
        """
        response = self.request(method='net.resume_transaction_iterator', **params.dict)
        return self.response(classname=RegisteredIterator, response=response)

    def iterator_next(
        self, params: ParamsOfIteratorNext
    ) -> Union[ResultOfIteratorNext, Awaitable[ResultOfIteratorNext]]:
        """
        Returns next available items

        :param params: See `types.ParamsOfIteratorNext`
        :return: See `types.ResultOfIteratorNext`
        """
        response = self.request(method='net.iterator_next', **params.dict)
        return self.response(classname=ResultOfIteratorNext, response=response)

    def remove_iterator(
        self, params: RegisteredIterator
    ) -> Union[None, Awaitable[None]]:
        """
        Removes an iterator.
        Frees all resources allocated in library to serve iterator.
        Application always should call the `remove_iterator` when iterator is
        no longer required

        :param params: See `types.RegisteredIterator`
        """
        return self.request(method='net.remove_iterator', **params.dict)
