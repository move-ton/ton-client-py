from typing import Any, Dict, Generator

from tonclient.decorators import Response
from tonclient.module import TonModule


class TonQLQuery(object):
    def __init__(self, collection: str):
        """
        :param collection: Collection name (accounts, blocks, transactions,
                messages, block_signatures)
        """
        self._collection = collection
        self._filter = {}
        self._result = []
        self._order = None
        self._limit = None

    @property
    def collection(self) -> str:
        return self._collection

    @property
    def filter(self) -> Dict:
        return self._filter

    @property
    def result(self):
        return ' '.join(self._result)

    @property
    def order(self):
        return self._order

    @property
    def limit(self):
        return self._limit

    def set_filter(self, **kwargs: Any) -> 'TonQLQuery':
        """
        Generate GraphQL filter from kwargs.
        :param kwargs: kwarg name should be like string with field name
                    and condition, separated by "__".
                    kwarg value may be any accessible your want to filter by.
                    Full kwarg example: id__eq="0:000000"
        :return:
        """
        # Parse kwargs and generate GraphQL filter
        for field, value in kwargs.items():
            try:
                field, condition = field.split('__')
            except ValueError:
                raise ValueError(f"Incorrect '{field}' field syntax")

            if not self._filter.get(field):
                self._filter[field] = {}

            self._filter[field].update({condition: value})

        return self

    def set_result(self, fields: str = None, *args: str) -> 'TonQLQuery':
        """
        :param fields: Field names as a string splitted by space
        :param args: Any amount of table field names you want to include
                    in response
        :return:
        """
        self._result = [fields, *args]
        return self

    def set_order(self, fields: str, *args: str) -> 'TonQLQuery':
        """
        :param fields: Field names as a string splitted by space
                    field name with "-" to make DESC.
                    Example: "id" -> ASC, "-id" -> DESC
        :param args: Filed names as separate args
        :return:
        """
        fields = [*fields.split(' '), *args]
        if fields and not self._order:
            self._order = []

        for field in fields:
            direction = 'ASC'
            if field[0] == '-':
                direction = 'DESC'
                field = field[1:]
            self._order.append({'path': field, 'direction': direction})
        return self

    def set_limit(self, limit: int) -> 'TonQLQuery':
        self._limit = limit
        return self


class TonNet(TonModule):
    """ Free TON net SDK API implementation """
    @Response.query_collection
    def query_collection(self, query: TonQLQuery) -> Any:
        """ Queries collection data """
        return self.request(
            method='net.query_collection', collection=query.collection,
            filter=query.filter, result=query.result, order=query.order,
            limit=query.limit)

    @Response.wait_for_collection
    def wait_for_collection(
            self, query: TonQLQuery, timeout: int = None) -> Any:
        """
        Returns an object that fulfills the conditions or waits for
        its appearance. Triggers only once.
        If object that satisfies the `filter` conditions already exists -
        returns it immediately. If not - waits for insert/update of data
        withing the specified `timeout`, and returns it
        """
        return self.request(
            method='net.wait_for_collection', collection=query.collection,
            filter=query.filter, result=query.result, timeout=timeout)

    @Response.subscribe_collection
    def subscribe_collection(self, query: TonQLQuery) -> Generator:
        """ Creates a subscription """
        return self.request(
            method='net.subscribe_collection', as_iterable=True,
            collection=query.collection, filter=query.filter,
            result=query.result)

    def unsubscribe(self, handle: int):
        """ Cancels a subscription """
        return self.request(method='net.unsubscribe', handle=handle)
