import logging
import time
from datetime import datetime

import unittest

from tonclient.bindings.types import TCResponseType
from tonclient.errors import TonException
from tonclient.net import TonQLQuery
from tonclient.test.helpers import async_core_client, sync_core_client


class TestTonNetAsyncCore(unittest.TestCase):
    def test_query_collection(self):
        query = TonQLQuery(collection='blocks_signatures') \
            .set_result('id').set_limit(1)
        result = async_core_client.net.query_collection(query=query)
        self.assertGreater(len(result), 0)

        query = TonQLQuery(collection='accounts').set_result('id', 'balance') \
            .set_limit(5)
        result = async_core_client.net.query_collection(query=query)
        self.assertEqual(5, len(result))

        query = TonQLQuery(collection='messages') \
            .set_filter(created_at__gt=1562342740) \
            .set_result('body created_at').set_order('created_at') \
            .set_limit(10)
        result = async_core_client.net.query_collection(query=query)
        self.assertGreater(result[0]['created_at'], 1562342740)

        with self.assertRaises(TonException):
            query = TonQLQuery(collection='messages')
            async_core_client.net.query_collection(query=query)

    def test_wait_for_collection(self):
        now = int(datetime.now().timestamp())
        query = TonQLQuery(collection='transactions') \
            .set_filter(now__gt=now).set_result('id now')
        result = async_core_client.net.wait_for_collection(query=query)
        self.assertGreater(result['now'], now)

        with self.assertRaises(TonException):
            async_core_client.net.wait_for_collection(query=query, timeout=1)

    def test_subscribe_collection(self):
        # Prepare query
        now = int(datetime.now().timestamp())
        query = TonQLQuery(collection='messages') \
            .set_filter(created_at__gt=now).set_result('created_at')

        # Create generator
        generator = async_core_client.net.subscribe_collection(query=query)
        handle = None
        results = []
        for response in generator:
            logging.info(f'[Response] {response}')
            results.append(response)
            data = response['response_data']
            if not data:
                continue

            if response['response_type'] == TCResponseType.Success:
                handle = data['handle']

            if (int(datetime.now().timestamp()) > now + 5 or
                    response['response_type'] > TCResponseType.Custom) and \
                    handle:
                async_core_client.net.unsubscribe(handle=handle)
                handle = None

        self.assertGreater(len(results), 0)

    def test_query(self):
        result = async_core_client.net.query(
            query='query($time: Float){messages(filter:{created_at:{ge:$time}}limit:5){id}}',
            variables={'time': int(datetime.now().timestamp()) - 60})
        self.assertGreater(len(result['data']['messages']), 0)

    def test_suspend_resume(self):
        # Prepare query
        now = int(datetime.now().timestamp())
        query = TonQLQuery(collection='messages') \
            .set_filter(created_at__gt=now).set_result('created_at id') \
            .set_order('created_at')

        # Create generator
        generator = async_core_client.net.subscribe_collection(query=query)
        handle = None
        results = {'current': 'before', 'before': [], 'after': []}
        for response in generator:
            logging.info(f'[Response] {response}')
            results[results['current']].append(response)
            data = response['response_data']
            if not data:
                continue

            if response['response_type'] == TCResponseType.Success:
                handle = data['handle']
            if not handle:
                continue

            if results['current'] == 'before' and \
                    len(results[results['current']]) == 2:
                async_core_client.net.suspend()
                time.sleep(5)
                self.assertEqual(0, len(results['after']))
                async_core_client.net.resume()
                results['current'] = 'after'

            if (int(datetime.now().timestamp()) > now + 15 or
                response['response_type'] > TCResponseType.Custom) and \
                    handle:
                async_core_client.net.unsubscribe(handle=handle)
                handle = None

        self.assertEqual(2, len(results['before']))
        self.assertGreater(len(results['after']), 0)


class TestTonNetSyncCore(unittest.TestCase):
    """ Sync core is not recommended to use, so make just a couple of tests """
    def test_query_collection(self):
        query = TonQLQuery(collection='blocks_signatures') \
            .set_result('id').set_limit(1)
        result = sync_core_client.net.query_collection(query=query)
        self.assertGreater(len(result), 0)

        query = TonQLQuery(collection='accounts').set_result('id', 'balance') \
            .set_limit(5)
        result = sync_core_client.net.query_collection(query=query)
        self.assertEqual(5, len(result))

        query = TonQLQuery(collection='messages') \
            .set_filter(created_at__gt=1562342740) \
            .set_result('body created_at').set_order('created_at') \
            .set_limit(10)
        result = sync_core_client.net.query_collection(query=query)
        self.assertGreater(result[0]['created_at'], 1562342740)

        with self.assertRaises(TonException):
            query = TonQLQuery(collection='messages')
            sync_core_client.net.query_collection(query=query)

    def test_wait_for_collection(self):
        now = int(datetime.now().timestamp())
        query = TonQLQuery(collection='transactions') \
            .set_filter(now__gt=now).set_result('id now')
        result = sync_core_client.net.wait_for_collection(query=query)
        self.assertGreater(result['now'], now)

        with self.assertRaises(TonException):
            sync_core_client.net.wait_for_collection(query=query, timeout=1)
