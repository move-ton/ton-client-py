# def query(
#         self, table: str, filter: Dict, result: str, order: Dict = None,
#         limit: int = None) -> any:
#     """
#     :param table:
#     :param filter: {"field_name": {"rule": "condition"}}
#     :param result:
#     :param order: {"path": str (field name), "direction": str (ASC|DESC)}
#     :param limit:
#     :return:
#     """
#     params = {
#         "table": table,
#         "filter": json.dumps(filter),
#         "result": result,
#         "order": order,
#         "limit": limit
#     }
#     result = self.request(method="queries.query", params=params)
#
#     return result["result"]
#
#
# def query_wait_for(
#         self, table: str, filter: Dict, result: str, order: Dict = None,
#         limit: int = None, timeout: int = None) -> any:
#     """
#     :param table:
#     :param filter:
#     :param result:
#     :param order:
#     :param limit:
#     :param timeout:
#     :return:
#     """
#     params = {
#         "table": table,
#         "filter": json.dumps(filter),
#         "result": result,
#         "order": order,
#         "limit": limit,
#         "timeout": timeout
#     }
#     result = self.request(method="queries.wait.for", params=params)
#
#     return result["result"]
#
#
# def query_subscribe(
#         self, table: str, filter: Dict, result: str) -> int:
#     """
#     :param table:
#     :param filter:
#     :param result:
#     :return: Handle index
#     """
#     params = {
#         "table": table,
#         "filter": json.dumps(filter),
#         "result": result
#     }
#     result = self.request(method="queries.subscribe", params=params)
#
#     return result["handle"]
#
#
# def query_get_next(self, handle: int) -> any:
#     """
#     :param handle:
#     :return:
#     """
#     params = {"handle": handle}
#     result = self.request(method="queries.get.next", params=params)
#
#     return result["result"]
#
#
# def query_unsubscribe(self, handle: int) -> None:
#     """
#     :param handle:
#     :return:
#     """
#     params = {"handle": handle}
#     return self.request(method="queries.unsubscribe", params=params)
