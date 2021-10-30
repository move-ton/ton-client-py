from tonclient.decorators import result_as
from tonclient.module import TonModule
from tonclient.types import ParamsOfParse, ResultOfParse, \
    ParamsOfParseShardstate, ParamsOfGetBocHash, ResultOfGetBocHash, \
    ParamsOfGetBlockchainConfig, ResultOfGetBlockchainConfig, \
    ParamsOfGetCodeFromTvc, ResultOfGetCodeFromTvc, ParamsOfBocCacheGet, \
    ResultOfBocCacheGet, ParamsOfBocCacheSet, ResultOfBocCacheSet, \
    ParamsOfBocCacheUnpin, ParamsOfEncodeBoc, ResultOfEncodeBoc, \
    ParamsOfGetCodeSalt, ResultOfGetCodeSalt, ParamsOfSetCodeSalt, \
    ResultOfSetCodeSalt, ParamsOfDecodeTvc, ResultOfDecodeTvc, \
    ParamsOfEncodeTvc, ResultOfEncodeTvc, ParamsOfGetCompilerVersion, \
    ResultOfGetCompilerVersion, ParamsOfGetBocDepth, ResultOfGetBocDepth


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
        Encodes bag of cells (BOC) with builder operations.
        This method provides the same functionality as Solidity TvmBuilder.
        Resulting BOC of this method can be passed into Solidity and C++
        contracts as TvmCell type

        :param params: See `types.ParamsOfEncodeBoc`
        :return: See `types.ResultOfEncodeBoc`
        """
        return self.request(method='boc.encode_boc', **params.dict)

    @result_as(classname=ResultOfGetCodeSalt)
    def get_code_salt(
            self, params: ParamsOfGetCodeSalt) -> ResultOfGetCodeSalt:
        """
        Returns the contract code's salt if it is present

        :param params: See `types.ParamsOfGetCodeSalt`
        :return: See `types.ResultOfGetCodeSalt`
        """
        return self.request(method='boc.get_code_salt', **params.dict)

    @result_as(classname=ResultOfSetCodeSalt)
    def set_code_salt(
            self, params: ParamsOfSetCodeSalt) -> ResultOfSetCodeSalt:
        """
        Sets new salt to contract code.
        Returns the new contract code with salt

        :param params: See `types.ParamsOfSetCodeSalt`
        :return: See `types.ResultOfSetCodeSalt`
        """
        return self.request(method='boc.set_code_salt', **params.dict)

    @result_as(classname=ResultOfDecodeTvc)
    def decode_tvc(self, params: ParamsOfDecodeTvc) -> ResultOfDecodeTvc:
        """
        Decodes tvc into code, data, libraries and special options

        :param params: See `types.ParamsOfDecodeTvc`
        :return: See `types.ResultOfDecodeTvc`
        """
        return self.request(method='boc.decode_tvc', **params.dict)

    @result_as(classname=ResultOfEncodeTvc)
    def encode_tvc(self, params: ParamsOfEncodeTvc) -> ResultOfEncodeTvc:
        """
        Encodes tvc from code, data, libraries ans special options
        (see input params)

        :param params: See `types.ParamsOfEncodeTvc`
        :return: See `types.ResultOfEncodeTvc`
        """
        return self.request(method='boc.encode_tvc', **params.dict)

    @result_as(classname=ResultOfGetCompilerVersion)
    def get_compiler_version(
            self, params: ParamsOfGetCompilerVersion
    ) -> ResultOfGetCompilerVersion:
        """
        Returns the compiler version used to compile the code

        :param params: See `types.ParamsOfGetCompilerVersion`
        :return: See `types.ResultOfGetCompilerVersion`
        """
        return self.request(method='boc.get_compiler_version', **params.dict)

    @result_as(classname=ResultOfGetBocDepth)
    def get_boc_depth(
            self, params: ParamsOfGetBocDepth) -> ResultOfGetBocDepth:
        """
        Calculates BOC depth

        :param params: See `types.ParamsOfGetBocDepth`
        :return: See `types.ResultOfGetBocDepth`
        """
        return self.request(method='boc.get_boc_depth', **params.dict)
