from typing import Dict, Any

from tonclient.decorators import Response
from tonclient.module import TonModule
from tonclient.types import Abi, AccountForExecutor


class TonTvm(TonModule):
    """ Free TON tvm SDK API implementation """
    @Response.run_get
    def run_get(
            self, account: str, function_name: str,
            inputs: Any = None, blockchain_config: str = None,
            block_time: int = None, block_lt: int = None,
            transaction_lt: int = None) -> Any:
        """
        Executes get method and returns data from TVM stack
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
            method='tvm.run_get', account=account,
            function_name=function_name, input=inputs,
            execution_options=execution_options)

    def run_executor(
            self, message: str, account: AccountForExecutor, abi: Abi = None,
            skip_transaction_check: bool = False,
            blockchain_config: str = None, block_time: int = None,
            block_lt: int = None, transaction_lt: int = None
    ) -> Dict[str, Any]:
        """
        :param message: Base64 encoded message BOC
        :param account: Account to run on executor
        :param abi: Contract ABI for decoding output messages
        :param skip_transaction_check: Skip transaction check flag
        :param blockchain_config: Execution options: blockchain config BOC
        :param block_time: Execution options: time that is used as
                transaction time
        :param block_lt: Execution options: block logical time
        :param transaction_lt: Execution options: transaction logical time
        :return:
        """
        abi = abi.dict if abi else abi
        execution_options = {
            'blockchain_config': blockchain_config,
            'block_time': block_time,
            'block_lt': block_lt,
            'transaction_lt': transaction_lt
        }
        return self.request(
            method='tvm.run_executor', message=message, account=account.dict,
            abi=abi, skip_transaction_check=skip_transaction_check,
            execution_options=execution_options)

    def run_tvm(
            self, message: str, account: str, abi: Abi = None,
            blockchain_config: str = None, block_time: int = None,
            block_lt: int = None, transaction_lt: int = None
    ) -> Dict[str, Any]:
        """
        :param message: Base64 encoded message BOC
        :param account: Base64 encoded account BOC
        :param abi: Contract ABI for decoding output messages
        :param blockchain_config: Execution options: blockchain config BOC
        :param block_time: Execution options: time that is used as
                transaction time
        :param block_lt: Execution options: block logical time
        :param transaction_lt: Execution options: transaction logical time
        :return:
        """
        abi = abi.dict if abi else abi
        execution_options = {
            'blockchain_config': blockchain_config,
            'block_time': block_time,
            'block_lt': block_lt,
            'transaction_lt': transaction_lt
        }
        return self.request(
            method='tvm.run_tvm', message=message, account=account, abi=abi,
            execution_options=execution_options)
