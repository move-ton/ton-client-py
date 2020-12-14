from typing import Any, Dict, Generator, List

from tonclient.decorators import Response
from tonclient.module import TonModule


class TonNet(TonModule):
    """ Free TON net SDK API implementation """
    @Response.query_collection
    def query_collection(
            self, collection: str, result: str, filter: Dict[str, Any] = None,
            order: List[Dict[str, str]] = None, limit: int = None) -> Any:
        """
        Queries collection data
        :param collection: Collection name
        :param result: Projection (result) string
        :param filter: Collection filter
        :param order: Sorting order.
                List of dict(s) {'path': field, 'direction': 'ASC'|'DESC'}
        :param limit: Number of documents to return
        """
        return self.request(
            method='net.query_collection', collection=collection,
            filter=filter, result=result, order=order, limit=limit)

    @Response.wait_for_collection
    def wait_for_collection(
            self, collection: str, result: str, filter: Dict[str, Any] = None,
            timeout: int = None) -> Any:
        """
        Returns an object that fulfills the conditions or waits for
        its appearance. Triggers only once.
        If object that satisfies the `filter` conditions already exists -
        returns it immediately. If not - waits for insert/update of data
        withing the specified `timeout`, and returns it
        """
        return self.request(
            method='net.wait_for_collection', collection=collection,
            filter=filter, result=result, timeout=timeout)

    @Response.subscribe_collection
    def subscribe_collection(
            self, collection: str, result: str,
            filter: Dict[str, Any] = None) -> Generator:
        """ Creates a subscription """
        return self.request(
            method='net.subscribe_collection', as_iterable=True,
            collection=collection, filter=filter, result=result)

    def unsubscribe(self, handle: int):
        """
        Cancels a subscription specified by its handle
        :param handle: Subscription handle
        """
        return self.request(method='net.unsubscribe', handle=handle)

    @Response.query
    def query(self, query: str, variables: Dict[str, Any] = None):
        """
        Performs DAppServer GraphQL query
        :param query: GraphQL query text
        :param variables: Variables used in query. Must be a map with named
                values that can be used in query
        :return:
        """
        return self.request(
            method='net.query', query=query, variables=variables)

    def suspend(self):
        """ Suspends network module to stop any network activity """
        return self.request(method='net.suspend')

    def resume(self):
        """ Resumes network module to enable network activity """
        return self.request(method='net.resume')
