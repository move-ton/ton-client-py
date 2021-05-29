from tonclient.decorators import result_as
from tonclient.module import TonModule
from tonclient.types import ParamsOfRunExecutor, ResultOfRunExecutor, \
    ParamsOfRunTvm, ResultOfRunTvm, ParamsOfRunGet, ResultOfRunGet


class TonTvm(TonModule):
    """ Free TON tvm SDK API implementation """

    @result_as(classname=ResultOfRunGet)
    def run_get(self, params: ParamsOfRunGet) -> ResultOfRunGet:
        """
        Executes a get method of FIFT contract.
        Executes a get method of FIFT contract that fulfills the
        smc-guidelines https://test.ton.org/smc-guidelines.txt and returns
        the result data from TVM's stack

        :param params: See `types.ParamsOfRunGet`
        :return: See `types.ResultOfRunGet`
        """
        return self.request(method='tvm.run_get', **params.dict)

    @result_as(classname=ResultOfRunExecutor)
    def run_executor(
            self, params: ParamsOfRunExecutor) -> ResultOfRunExecutor:
        """
        Emulates all the phases of contract execution locally.

        Performs all the phases of contract execution on Transaction Executor -
        the same component that is used on Validator Nodes.

        Can be used for contract debugging, to find out the reason why a
        message was not delivered successfully. Validators throw away the
        failed external inbound messages (if they failed before `ACCEPT`) in
        the real network. This is why these messages are impossible to debug
        in the real network. With the help of run_executor you can do that.
        In fact, `process_message` function performs local check with
        `run_executor` if there was no transaction as a result of processing
        and returns the error, if there is one.

        Another use case to use `run_executor` is to estimate fees for message
        execution. Set `AccountForExecutor::Account.unlimited_balance` to
        `true` so that emulation will not depend on the actual balance.
        This may be needed to calculate deploy fees for an account that does
        not exist yet. JSON with fees is in `fees` field of the result.

        One more use case - you can produce the sequence of operations,
        thus emulating the sequential contract calls locally. And so on.

        Transaction executor requires account BOC (bag of cells) as a
        parameter. To get the account BOC - use `net.query` method to download
        it from GraphQL API (field `boc` of `account`) or generate it with
        `abi.encode_account method`.

        Also it requires message BOC. To get the message BOC - use
        `abi.encode_message` or `abi.encode_internal_message`.

        If you need this emulation to be as precise as possible
        (for instance - emulate transaction with particular lt in particular
        block or use particular blockchain config, in case you want to
        download it from a particular key block - then specify
        `ParamsOfRunExecutor` parameter.

        If you need to see the aborted transaction as a result, not as an
        error, set `skip_transaction_check` to true.

        :param params: See `types.ParamsOfRunExecutor`
        :return: `types.ResultOfRunExecutor`
        """
        return self.request(method='tvm.run_executor', **params.dict)

    @result_as(classname=ResultOfRunTvm)
    def run_tvm(self, params: ParamsOfRunTvm) -> ResultOfRunTvm:
        """
        Executes get methods of ABI-compatible contracts.

        Performs only a part of compute phase of transaction execution that is
        used to run get-methods of ABI-compatible contracts.

        If you try to run get methods with `run_executor` you will get an
        error, because it checks `ACCEPT` and exits if there is none, which
        is actually true for get methods.

        To get the account boc (bag of cells) - use `net.query` method to
        download it from graphql api (field `boc` of `account`) or generate
        it with `abi.encode_account` method.
        To get the message boc - use `abi.encode_message` or prepare it any
        other way, for instance, with Fift script.

        Attention! Updated account state is produces as well, but only
        `account_state.storage.state.data` part of the boc is updated.

        :param params: See `types.ParamsOfRunTvm`
        :return: See `types.ResultOfRunTvm`
        """
        return self.request(method='tvm.run_tvm', **params.dict)
