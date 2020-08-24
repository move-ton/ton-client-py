import json
from typing import Any, Union, Awaitable, Dict

from tonclient.module import TonModule


class TonQueryBuilder(object):
    def __init__(self, table: str):
        self._table = table
        self._filter = {}
        self._result = []
        self._order = None
        self._limit = None

    @property
    def ql_table(self) -> str:
        return self._table

    @property
    def ql_filter(self) -> str:
        return json.dumps(self._filter)

    @property
    def ql_result(self):
        return " ".join(self._result)

    @property
    def ql_order(self):
        return self._order

    @property
    def ql_limit(self):
        return self._limit

    def filter(self, **kwargs: Any) -> "TonQueryBuilder":
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
                field, condition = field.split("__")
            except ValueError:
                raise ValueError(f"Incorrect '{field}' field syntax")

            if not self._filter.get(field):
                self._filter[field] = {}

            self._filter[field].update({condition: value})

        return self

    def result(self, fields: str = None, *args: str) -> "TonQueryBuilder":
        """
        :param fields: Fields as str or fields splitted by space
        :param args: Any amount of table field names you want to include
                    in response
        :return:
        """
        self._result = [fields, *args]
        return self

    def order(self, field: str) -> "TonQueryBuilder":
        """
        :param field: Field name to order by. Default will be ASC, prepend
                    field name with "-" to make DESC.
                    Example: "id" -> ASC, "-id" -> DESC
        :return:
        """
        direction = "ASC"
        if field[0] == "-":
            direction = "DESC"
            field = field[1:]

        self._order = {"path": field, "direction": direction}
        return self

    def limit(self, limit: int) -> "TonQueryBuilder":
        self._limit = limit
        return self


class TonQuery(TonModule):
    """ Free TON queries SDK API implementation """
    def query(self, query: TonQueryBuilder) -> Union[Any, Awaitable]:
        """
        :param query:
        :return:
        """
        def __result_cb(data: Dict) -> Any:
            return data["result"]

        return self.request(
            method="queries.query", table=query.ql_table,
            filter=query.ql_filter, result=query.ql_result,
            order=query.ql_order, limit=query.ql_limit, result_cb=__result_cb)

    def wait_for(
                self, query: TonQueryBuilder, timeout: int = None
            ) -> Union[Any, Awaitable]:
        """
        :param query:
        :param timeout:
        :return:
        """
        def __result_cb(data: Dict) -> Any:
            return data["result"]

        return self.request(
            method="queries.wait.for", table=query.ql_table,
            filter=query.ql_filter, result=query.ql_result,
            order=query.ql_order, limit=query.ql_limit, timeout=timeout,
            result_cb=__result_cb)

    def subscribe(self, query: TonQueryBuilder) -> Union[int, Awaitable]:
        """
        Notice that query 'order_by' and 'limit' are not working for this
        method.
        :param query:
        :return: Handle index
        """
        def __result_cb(data: Dict) -> Any:
            return data["handle"]

        return self.request(
            method="queries.subscribe", table=query.ql_table,
            filter=query.ql_filter, result=query.ql_result,
            result_cb=__result_cb)

    def get_next(self, handle: int) -> Union[Any, Awaitable]:
        """
        :param handle:
        :return:
        """
        def __result_cb(data: Dict) -> Any:
            return data["result"]

        return self.request(
            method="queries.get.next", handle=handle, result_cb=__result_cb)

    def unsubscribe(self, handle: int) -> Union[None, Awaitable]:
        """
        :param handle:
        :return:
        """
        return self.request(method="queries.unsubscribe", handle=handle)
