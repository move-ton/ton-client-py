from tonclient.decorators import result_as
from tonclient.module import TonModule
from tonclient.types import ParamsOfQuery, ResultOfQuery, \
    ParamsOfQueryCollection, ResultOfQueryCollection, \
    ParamsOfWaitForCollection, ResultOfWaitForCollection, \
    ResultOfSubscribeCollection, ParamsOfSubscribeCollection, \
    ParamsOfFindLastShardBlock, ResultOfFindLastShardBlock, EndpointsSet, \
    ParamsOfAggregateCollection, ResultOfAggregateCollection, \
    ParamsOfBatchQuery, ResultOfBatchQuery, ResponseHandler, \
    ParamsOfQueryCounterparties, ResultOfGetEndpoints, \
    ParamsOfQueryTransactionTree, ResultOfQueryTransactionTree


class TonNet(TonModule):
    """ Free TON net SDK API implementation """

    @result_as(classname=ResultOfQueryCollection)
    def query_collection(
            self, params: ParamsOfQueryCollection) -> ResultOfQueryCollection:
        """
        Queries collection data.
        Queries data that satisfies the `filter` conditions, limits the number
        of returned records and orders them. The projection fields are limited
        to result fields

        :param params: See `types.ParamsOfQueryCollection`
        :return: See `types.ResultOfQueryCollection`
        """
        return self.request(method='net.query_collection', **params.dict)

    @result_as(classname=ResultOfWaitForCollection)
    def wait_for_collection(
            self, params: ParamsOfWaitForCollection
    ) -> ResultOfWaitForCollection:
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
        return self.request(method='net.wait_for_collection', **params.dict)

    @result_as(classname=ResultOfSubscribeCollection)
    def subscribe_collection(
            self, params: ParamsOfSubscribeCollection,
            callback: ResponseHandler = None
    ) -> ResultOfSubscribeCollection:
        """
        Creates a subscription.
        Triggers for each insert/update of data that satisfies the `filter`
        conditions. The projection fields are limited to `result` fields

        :param params: See `types.ParamsOfSubscribeCollection`
        :param callback: Additional responses handler
        :return:
        """
        return self.request(
            method='net.subscribe_collection', callback=callback,
            **params.dict)

    def unsubscribe(self, params: ResultOfSubscribeCollection):
        """
        Cancels a subscription.
        Cancels a subscription specified by its handle

        :param params: See `types.ResultOfSubscribeCollection`
        """
        return self.request(method='net.unsubscribe', **params.dict)

    @result_as(classname=ResultOfQuery)
    def query(self, params: ParamsOfQuery) -> ResultOfQuery:
        """
        Performs DAppServer GraphQL query

        :param params: See `types.ResultOfQuery`
        :return: See `types.ResultOfQuery`
        """
        return self.request(method='net.query', **params.dict)

    def suspend(self):
        """ Suspends network module to stop any network activity """
        return self.request(method='net.suspend')

    def resume(self):
        """ Resumes network module to enable network activity """
        return self.request(method='net.resume')

    @result_as(classname=ResultOfFindLastShardBlock)
    def find_last_shard_block(
            self, params: ParamsOfFindLastShardBlock
    ) -> ResultOfFindLastShardBlock:
        """
        :param params: See `types.ParamsOfFindLastShardBlock`
        :return: See `types.ResultOfFindLastShardBlock`
        """
        return self.request(method='net.find_last_shard_block', **params.dict)

    @result_as(classname=EndpointsSet)
    def fetch_endpoints(self) -> EndpointsSet:
        """
        Requests the list of alternative endpoints from server

        :return: See `types.EndpointsSet`
        """
        return self.request(method='net.fetch_endpoints')

    def set_endpoints(self, params: EndpointsSet):
        """
        Sets the list of endpoints to use on re-init

        :param params: See `types.EndpointsSet`
        :return:
        """
        return self.request(method='net.set_endpoints', **params.dict)

    @result_as(classname=ResultOfGetEndpoints)
    def get_endpoints(self) -> ResultOfGetEndpoints:
        """
        Requests the list of alternative endpoints from server

        :return: See `types.ResultOfGetEndpoints`
        """
        return self.request(method='net.get_endpoints')

    @result_as(classname=ResultOfAggregateCollection)
    def aggregate_collection(
            self, params: ParamsOfAggregateCollection
    ) -> ResultOfAggregateCollection:
        """
        Aggregates collection data.
        Aggregates values from the specified `fields` for records that
        satisfies the `filter` conditions

        :param params: See `types.ParamsOfAggregateCollection`
        :return: See `types.ResultOfAggregateCollection`
        """
        return self.request(method='net.aggregate_collection', **params.dict)

    @result_as(classname=ResultOfBatchQuery)
    def batch_query(self, params: ParamsOfBatchQuery) -> ResultOfBatchQuery:
        """
        Performs multiple queries per single fetch

        :param params: See `types.ParamsOfBatchQuery`
        :return: See `types.ResultOfBatchQuery`
        """
        return self.request(method='net.batch_query', **params.dict)

    @result_as(classname=ResultOfQueryCollection)
    def query_counterparties(
            self, params: ParamsOfQueryCounterparties
    ) -> ResultOfQueryCollection:
        """
        Allows to query and paginate through the list of accounts that the
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
        return self.request(method='net.query_counterparties', **params.dict)

    @result_as(classname=ResultOfQueryTransactionTree)
    def query_transaction_tree(
            self, params: ParamsOfQueryTransactionTree
    ) -> ResultOfQueryTransactionTree:
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
        return self.request(method='net.query_transaction_tree', **params.dict)
