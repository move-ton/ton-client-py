from tonclient.decorators import result_as
from tonclient.module import TonModule
from tonclient.types import ParamsOfParse, ResultOfParse, \
    ParamsOfParseShardstate, ParamsOfGetBocHash, ResultOfGetBocHash, \
    ParamsOfGetBlockchainConfig, ResultOfGetBlockchainConfig, \
    ParamsOfGetCodeFromTvc, ResultOfGetCodeFromTvc, ParamsOfBocCacheGet, \
    ResultOfBocCacheGet, ParamsOfBocCacheSet, ResultOfBocCacheSet, \
    ParamsOfBocCacheUnpin, ParamsOfEncodeBoc, ResultOfEncodeBoc


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
        Extract blockchain configuration from key block and also from
        zero state

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

    @result_as(classname=ResultOfBocCacheGet)
    def cache_get(self, params: ParamsOfBocCacheGet) -> ResultOfBocCacheGet:
        """
        Get BOC from cache

        :param params: See `types.ParamsOfBocCacheGet`
        :return: See `types.ResultOfBocCacheGet`
        """
        return self.request(method='boc.cache_get', **params.dict)

    @result_as(classname=ResultOfBocCacheSet)
    def cache_set(self, params: ParamsOfBocCacheSet) -> ResultOfBocCacheSet:
        """
        Save BOC into cache

        :param params: See `types.ParamsOfBocCacheSet`
        :return: See `types.ResultOfBocCacheSet`
        """
        return self.request(method='boc.cache_set', **params.dict)

    def cache_unpin(self, params: ParamsOfBocCacheUnpin):
        """
        Unpin BOCs with specified pin.
        BOCs which don't have another pins will be removed from cache

        :param params: See `types.ParamsOfBocCacheUnpin`
        :return:
        """
        return self.request(method='boc.cache_unpin', **params.dict)

    @result_as(classname=ResultOfEncodeBoc)
    def encode_boc(self, params: ParamsOfEncodeBoc) -> ResultOfEncodeBoc:
        """
        Encodes BOC from builder operations

        :param params: See `types.ParamsOfEncodeBoc`
        :return: See `types.ResultOfEncodeBoc`
        """
        return self.request(method='boc.encode_boc', **params.dict)
