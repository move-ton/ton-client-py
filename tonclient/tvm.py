from typing import Dict, Any

from tonclient.decorators import Response
from tonclient.module import TonModule
from tonclient.types import MessageSource


class TonTvm(TonModule):
    """ Free TON tvm SDK API implementation """
    def execute_message(
            self, message: MessageSource, account: str, mode: str,
            blockchain_config: str = None, block_time: int = None,
            block_lt: int = None, transaction_lt: int = None
    ) -> Dict[str, Any]:
        """
        :param message: Input message
        :param account: Base64 encoded account BOC
        :param mode: Execution mode. 'types.ExecutionMode' class may help
        :param blockchain_config: Execution options: blockchain config BOC
        :param block_time: Execution options: time that is used as
                transaction time
        :param block_lt: Execution options: block logical time
        :param transaction_lt: Execution options: transaction logical time
        :return:
        """
        execution_options = {
            'blockchain_config': blockchain_config,
            'block_time': block_time,
            'block_lt': block_lt,
            'transaction_lt': transaction_lt
        }
        return self.request(
            method='tvm.execute_message', message=message.dict,
            account=account, mode=mode, execution_options=execution_options)

    @Response.execute_get
    def execute_get(
            self, account: str, function_name: str,
            inputs: Any = None, blockchain_config: str = None,
            block_time: int = None, block_lt: int = None,
            transaction_lt: int = None) -> Any:
        """
        :param account: Base64 encoded account BOC
        :param function_name:
        :param inputs:
        :param blockchain_config: Execution options: blockchain config BOC
        :param block_time: Execution options: time that is used as
                transaction time
        :param block_lt: Execution options: block logical time
        :param transaction_lt: Execution options: transaction logical time
        :return:
        """
        execution_options = {
            'blockchain_config': blockchain_config,
            'block_time': block_time,
            'block_lt': block_lt,
            'transaction_lt': transaction_lt
        }
        return self.request(
            method='tvm.execute_get', account=account,
            function_name=function_name, input=inputs,
            execution_options=execution_options)
