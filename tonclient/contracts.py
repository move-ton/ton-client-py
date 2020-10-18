from tonclient.module import TonModule
from tonclient.types import MessageSource


class TonContracts(TonModule):
    """ Free TON processing SDK API implementation """

    def contracts_run(self, message: MessageSource, send_events: bool):
        """
        :param message: Message source
        :param send_events: Flag for requesting events sending
        :return:
        """
        return self.request(
            method='contracts.run', address=send_events,
            abi=message.dict, send_events=send_events)
