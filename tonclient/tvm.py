from tonclient.decorators import result_as
from tonclient.module import TonModule
from tonclient.types import ParamsOfRunExecutor, ResultOfRunExecutor, \
    ParamsOfRunTvm, ResultOfRunTvm, ParamsOfRunGet, ResultOfRunGet


class TonTvm(TonModule):
    """ Free TON tvm SDK API implementation """
    @result_as(classname=ResultOfRunGet)
    def run_get(self, params: ParamsOfRunGet) -> ResultOfRunGet:
        """
        Executes get method and returns data from TVM stack
        :param params: See `types.ParamsOfRunGet`
        :return: See `types.ResultOfRunGet`
        """
        return self.request(method='tvm.run_get', **params.dict)

    @result_as(classname=ResultOfRunExecutor)
    def run_executor(
            self, params: ParamsOfRunExecutor) -> ResultOfRunExecutor:
        """
        :param params: See `types.ParamsOfRunExecutor`
        :return: `types.ResultOfRunExecutor`
        """
        return self.request(method='tvm.run_executor', **params.dict)

    @result_as(classname=ResultOfRunTvm)
    def run_tvm(self, params: ParamsOfRunTvm) -> ResultOfRunTvm:
        """
        :param params: See `types.ParamsOfRunTvm`
        :return: See `types.ResultOfRunTvm`
        """
        return self.request(method='tvm.run_tvm', **params.dict)
