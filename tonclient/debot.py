from tonclient.module import TonModule
from tonclient.types import DebotAction


class TonDebot(TonModule):
    """ Free TON debot SDK API implementation """
    def start(self, address: str):
        """
        Starts an instance of debot.
        Downloads debot smart contract from blockchain and switches it to
        context zero.
        Returns a debot handle which can be used later in `execute` function.
        This function must be used by Debot Browser to start a dialog with
        debot.
        While the function is executing, several Browser Callbacks can be
        called, since the debot tries to display all actions from the
        context 0 to the user.

        `start` is equivalent to `fetch` + switch to context 0
        :param address: Debot smart contract address
        :return:
        """
        return self.request(
            method='debot.start', address=address, as_iterable=True)

    def fetch(self, address: str):
        """
        Fetches debot from blockchain.
        Downloads debot smart contract (code and data) from blockchain and
        creates an instance of Debot Engine for it.

        It does not switch debot to context 0. Browser Callbacks are not
        called
        :param address: Debot smart contract address
        :return:
        """
        return self.request(
            method='debot.fetch', address=address, as_iterable=True)

    def execute(self, debot_handle: int, action: DebotAction):
        """
        Executes debot action.
        Calls debot engine referenced by debot handle to execute input action.
        Calls Debot Browser Callbacks if needed.

        Chain of actions can be executed if input action generates a list of
        subactions
        :param debot_handle: Debot handle which references an instance of
                debot engine
        :param action: Debot Action that must be executed
        :return:
        """
        return self.request(
            method='debot.execute', debot_handle=debot_handle,
            action=action.dict)

    def remove(self, debot_handle: int):
        """
        Destroys debot handle.
        Removes handle from Client Context and drops debot engine referenced
        by that handle
        :param debot_handle: Debot handle which references an instance of
                debot engine
        :return:
        """
        return self.request(method='debot.remove', debot_handle=debot_handle)
