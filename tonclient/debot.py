"""DeBot module methods"""
from typing import Union, Awaitable

from tonclient.module import TonModule
from tonclient.types import (
    ParamsOfStart,
    RegisteredDebot,
    ParamsOfFetch,
    ParamsOfExecute,
    ParamsOfSend,
    ResponseHandler,
    ParamsOfInit,
    ResultOfFetch,
    ParamsOfRemove,
)


class TonDebot(TonModule):
    """Free TON debot SDK API implementation"""

    def init(
        self, params: ParamsOfInit, callback: ResponseHandler
    ) -> Union[RegisteredDebot, Awaitable[RegisteredDebot]]:
        """
        Creates and instance of DeBot.
        Downloads debot smart contract (code and data) from blockchain and
        creates an instance of Debot Engine for it

        :param params: See `types.ParamsOfInit`
        :param callback: Callback for debot events
        :return: See `types.RegisteredDebot`
        """
        response = self.request(method='debot.init', callback=callback, **params.dict)
        return self.response(classname=RegisteredDebot, response=response)

    def start(self, params: ParamsOfStart) -> Union[None, Awaitable[None]]:
        """
        Starts the DeBot.
        Downloads debot smart contract from blockchain and switches it to
        context zero.
        This function must be used by Debot Browser to start a dialog with
        debot. While the function is executing, several Browser Callbacks can
        be called, since the debot tries to display all actions from the
        context 0 to the user.
        When the debot starts SDK registers `BrowserCallbacks` AppObject.
        Therefore when `debot.remove` is called the debot is being deleted and
        the callback is called with `finish=true` which indicates that it will
        never be used again

        :param params: See `types.ParamsOfStart`
        :return:
        """
        return self.request(method='debot.start', **params.dict)

    def fetch(
        self, params: ParamsOfFetch
    ) -> Union[ResultOfFetch, Awaitable[ResultOfFetch]]:
        """
        Fetches DeBot metadata from blockchain.
        Downloads DeBot from blockchain and creates and fetches its metadata

        :param params: See `types.ParamsOfFetch`
        :return: See `types.ResultOfFetch`
        """
        response = self.request(method='debot.fetch', **params.dict)
        return self.response(classname=ResultOfFetch, response=response)

    def execute(self, params: ParamsOfExecute) -> Union[None, Awaitable[None]]:
        """
        Executes debot action.
        Calls debot engine referenced by debot handle to execute input action.
        Calls Debot Browser Callbacks if needed.

        Chain of actions can be executed if input action generates a list of
        subactions

        :param params: See `types.ParamsOfExecute`
        :return:
        """
        return self.request(method='debot.execute', **params.dict)

    def send(self, params: ParamsOfSend) -> Union[None, Awaitable[None]]:
        """
        Sends message to Debot.
        Used by Debot Browser to send response on DInterface call or from
        other Debots

        :param params: See `types.ParamsOfSend`
        :return:
        """
        return self.request(method='debot.send', **params.dict)

    def remove(self, params: ParamsOfRemove) -> Union[None, Awaitable[None]]:
        """
        Destroys debot handle.
        Removes handle from Client Context and drops debot engine referenced
        by that handle

        :param params: See `types.ParamsOfRemove`
        :return:
        """
        return self.request(method='debot.remove', **params.dict)
