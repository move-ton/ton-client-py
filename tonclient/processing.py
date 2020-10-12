from tonclient.module import TonModule


class TonProcessing(TonModule):
    """ Free TON processing SDK API implementation """
    def process_message(self):
        return self.request(function_name='processing.process_message')
