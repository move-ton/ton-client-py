from tonclient.decorators import result_as
from tonclient.module import TonModule
from tonclient.types import ParamsOfParse, ResultOfParse, \
    ParamsOfParseShardstate, ParamsOfGetBocHash, ResultOfGetBocHash, \
    ParamsOfGetBlockchainConfig, ResultOfGetBlockchainConfig, \
    ParamsOfGetCodeFromTvc, ResultOfGetCodeFromTvc


class TonBoc(TonModule):
    """ Free TON boc SDK API implementation """
    @result_as(classname=ResultOfParse)
    def parse_message(self, params: ParamsOfParse) -> ResultOfParse:
        """
        Parses message boc into a JSON.
        JSON structure is compatible with GraphQL API message object
        :param params: See `types.ParamsOfParse`
        :return: See `types.ResultOfParse`
        """
        return self.request(method='boc.parse_message', **params.dict)

    @result_as(classname=ResultOfParse)
    def parse_transaction(self, params: ParamsOfParse) -> ResultOfParse:
        """
        Parses transaction boc into a JSON.
        JSON structure is compatible with GraphQL API transaction object
        :param params: See `types.ParamsOfParse`
        :return: See `types.ResultOfParse`
        """
        return self.request(method='boc.parse_transaction', **params.dict)

    @result_as(classname=ResultOfParse)
    def parse_account(self, params: ParamsOfParse) -> ResultOfParse:
        """
        Parses account boc into a JSON.
        JSON structure is compatible with GraphQL API account object
        :param params: See `types.ParamsOfParse`
        :return: See `types.ResultOfParse`
        """
        return self.request(method='boc.parse_account', **params.dict)

    @result_as(classname=ResultOfParse)
    def parse_block(self, params: ParamsOfParse) -> ResultOfParse:
        """
        Parses block boc into a JSON.
        JSON structure is compatible with GraphQL API block object
        :param params: See `types.ParamsOfParse`
        :return: See `types.ResultOfParse`
        """
        return self.request(method='boc.parse_block', **params.dict)

    @result_as(classname=ResultOfParse)
    def parse_shardstate(
            self, params: ParamsOfParseShardstate) -> ResultOfParse:
        """
        Parses shardstate boc into a JSON.
        JSON structure is compatible with GraphQL API shardstate object
        :param params: See `ParamsOfParseShardstate`
        :return: See `ResultOfParse`
        """
        return self.request(method='boc.parse_shardstate', **params.dict)

    @result_as(classname=ResultOfGetBocHash)
    def get_boc_hash(self, params: ParamsOfGetBocHash) -> ResultOfGetBocHash:
        """
        Calculates BOC root hash
        :param params: See `ParamsOfGetBocHash`
        :return: See `ResultOfGetBocHash`
        """
        return self.request(method='boc.get_boc_hash', **params.dict)

    @result_as(classname=ResultOfGetBlockchainConfig)
    def get_blockchain_config(
            self, params: ParamsOfGetBlockchainConfig
    ) -> ResultOfGetBlockchainConfig:
        """
        :param params: See `ParamsOfGetBlockchainConfig`
        :return: See `ResultOfGetBlockchainConfig`
        """
        return self.request(
            method='boc.get_blockchain_config', **params.dict)

    @result_as(classname=ResultOfGetCodeFromTvc)
    def get_code_from_tvc(
            self, params: ParamsOfGetCodeFromTvc) -> ResultOfGetCodeFromTvc:
        """
        Extracts code from TVC contract image
        :param params: See `types.ParamsOfGetCodeFromTvc`
        :return: See `types.ResultOfGetCodeFromTvc`
        """
        return self.request(method='boc.get_code_from_tvc', **params.dict)
