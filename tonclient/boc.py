"""BOC module methods"""
from typing import Union, Awaitable

from tonclient.module import TonModule
from tonclient.types import (
    ParamsOfParse,
    ResultOfParse,
    ParamsOfParseShardstate,
    ParamsOfGetBocHash,
    ResultOfGetBocHash,
    ParamsOfGetBlockchainConfig,
    ResultOfGetBlockchainConfig,
    ParamsOfGetCodeFromTvc,
    ResultOfGetCodeFromTvc,
    ParamsOfBocCacheGet,
    ResultOfBocCacheGet,
    ParamsOfBocCacheSet,
    ResultOfBocCacheSet,
    ParamsOfBocCacheUnpin,
    ParamsOfEncodeBoc,
    ResultOfEncodeBoc,
    ParamsOfGetCodeSalt,
    ResultOfGetCodeSalt,
    ParamsOfSetCodeSalt,
    ResultOfSetCodeSalt,
    ParamsOfDecodeTvc,
    ResultOfDecodeTvc,
    ParamsOfEncodeTvc,
    ResultOfEncodeTvc,
    ParamsOfGetCompilerVersion,
    ResultOfGetCompilerVersion,
    ParamsOfGetBocDepth,
    ResultOfGetBocDepth,
    ParamsOfEncodeExternalInMessage,
    ResultOfEncodeExternalInMessage,
)


class TonBoc(TonModule):
    """Free TON boc SDK API implementation"""

    def parse_message(
        self, params: ParamsOfParse
    ) -> Union[ResultOfParse, Awaitable[ResultOfParse]]:
        """
        Parses message boc into a JSON.
        JSON structure is compatible with GraphQL API message object

        :param params: See `types.ParamsOfParse`
        :return: See `types.ResultOfParse`
        """
        response = self.request(method='boc.parse_message', **params.dict)
        return self.response(classname=ResultOfParse, response=response)

    def parse_transaction(
        self, params: ParamsOfParse
    ) -> Union[ResultOfParse, Awaitable[ResultOfParse]]:
        """
        Parses transaction boc into a JSON.
        JSON structure is compatible with GraphQL API transaction object

        :param params: See `types.ParamsOfParse`
        :return: See `types.ResultOfParse`
        """
        response = self.request(method='boc.parse_transaction', **params.dict)
        return self.response(classname=ResultOfParse, response=response)

    def parse_account(
        self, params: ParamsOfParse
    ) -> Union[ResultOfParse, Awaitable[ResultOfParse]]:
        """
        Parses account boc into a JSON.
        JSON structure is compatible with GraphQL API account object

        :param params: See `types.ParamsOfParse`
        :return: See `types.ResultOfParse`
        """
        response = self.request(method='boc.parse_account', **params.dict)
        return self.response(classname=ResultOfParse, response=response)

    def parse_block(
        self, params: ParamsOfParse
    ) -> Union[ResultOfParse, Awaitable[ResultOfParse]]:
        """
        Parses block boc into a JSON.
        JSON structure is compatible with GraphQL API block object

        :param params: See `types.ParamsOfParse`
        :return: See `types.ResultOfParse`
        """
        response = self.request(method='boc.parse_block', **params.dict)
        return self.response(classname=ResultOfParse, response=response)

    def parse_shardstate(
        self, params: ParamsOfParseShardstate
    ) -> Union[ResultOfParse, Awaitable[ResultOfParse]]:
        """
        Parses shardstate boc into a JSON.
        JSON structure is compatible with GraphQL API shardstate object

        :param params: See `ParamsOfParseShardstate`
        :return: See `ResultOfParse`
        """
        response = self.request(method='boc.parse_shardstate', **params.dict)
        return self.response(classname=ResultOfParse, response=response)

    def get_boc_hash(
        self, params: ParamsOfGetBocHash
    ) -> Union[ResultOfGetBocHash, Awaitable[ResultOfGetBocHash]]:
        """
        Calculates BOC root hash

        :param params: See `ParamsOfGetBocHash`
        :return: See `ResultOfGetBocHash`
        """
        response = self.request(method='boc.get_boc_hash', **params.dict)
        return self.response(classname=ResultOfGetBocHash, response=response)

    def get_blockchain_config(
        self, params: ParamsOfGetBlockchainConfig
    ) -> Union[ResultOfGetBlockchainConfig, Awaitable[ResultOfGetBlockchainConfig]]:
        """
        Extract blockchain configuration from key block and also from
        zero state

        :param params: See `ParamsOfGetBlockchainConfig`
        :return: See `ResultOfGetBlockchainConfig`
        """
        response = self.request(method='boc.get_blockchain_config', **params.dict)
        return self.response(classname=ResultOfGetBlockchainConfig, response=response)

    def get_code_from_tvc(
        self, params: ParamsOfGetCodeFromTvc
    ) -> Union[ResultOfGetCodeFromTvc, Awaitable[ResultOfGetCodeFromTvc]]:
        """
        Extracts code from TVC contract image

        :param params: See `types.ParamsOfGetCodeFromTvc`
        :return: See `types.ResultOfGetCodeFromTvc`
        """
        response = self.request(method='boc.get_code_from_tvc', **params.dict)
        return self.response(classname=ResultOfGetCodeFromTvc, response=response)

    def cache_get(
        self, params: ParamsOfBocCacheGet
    ) -> Union[ResultOfBocCacheGet, Awaitable[ResultOfBocCacheGet]]:
        """
        Get BOC from cache

        :param params: See `types.ParamsOfBocCacheGet`
        :return: See `types.ResultOfBocCacheGet`
        """
        response = self.request(method='boc.cache_get', **params.dict)
        return self.response(classname=ResultOfBocCacheGet, response=response)

    def cache_set(
        self, params: ParamsOfBocCacheSet
    ) -> Union[ResultOfBocCacheSet, Awaitable[ResultOfBocCacheSet]]:
        """
        Save BOC into cache

        :param params: See `types.ParamsOfBocCacheSet`
        :return: See `types.ResultOfBocCacheSet`
        """
        response = self.request(method='boc.cache_set', **params.dict)
        return self.response(classname=ResultOfBocCacheSet, response=response)

    def cache_unpin(
        self, params: ParamsOfBocCacheUnpin
    ) -> Union[None, Awaitable[None]]:
        """
        Unpin BOCs with specified pin.
        BOCs which don't have another pins will be removed from cache

        :param params: See `types.ParamsOfBocCacheUnpin`
        :return:
        """
        return self.request(method='boc.cache_unpin', **params.dict)

    def encode_boc(
        self, params: ParamsOfEncodeBoc
    ) -> Union[ResultOfEncodeBoc, Awaitable[ResultOfEncodeBoc]]:
        """
        Encodes bag of cells (BOC) with builder operations.
        This method provides the same functionality as Solidity TvmBuilder.
        Resulting BOC of this method can be passed into Solidity and C++
        contracts as TvmCell type

        :param params: See `types.ParamsOfEncodeBoc`
        :return: See `types.ResultOfEncodeBoc`
        """
        response = self.request(method='boc.encode_boc', **params.dict)
        return self.response(classname=ResultOfEncodeBoc, response=response)

    def get_code_salt(
        self, params: ParamsOfGetCodeSalt
    ) -> Union[ResultOfGetCodeSalt, Awaitable[ResultOfGetCodeSalt]]:
        """
        Returns the contract code's salt if it is present

        :param params: See `types.ParamsOfGetCodeSalt`
        :return: See `types.ResultOfGetCodeSalt`
        """
        response = self.request(method='boc.get_code_salt', **params.dict)
        return self.response(classname=ResultOfGetCodeSalt, response=response)

    def set_code_salt(
        self, params: ParamsOfSetCodeSalt
    ) -> Union[ResultOfSetCodeSalt, Awaitable[ResultOfSetCodeSalt]]:
        """
        Sets new salt to contract code.
        Returns the new contract code with salt

        :param params: See `types.ParamsOfSetCodeSalt`
        :return: See `types.ResultOfSetCodeSalt`
        """
        response = self.request(method='boc.set_code_salt', **params.dict)
        return self.response(classname=ResultOfSetCodeSalt, response=response)

    def decode_tvc(
        self, params: ParamsOfDecodeTvc
    ) -> Union[ResultOfDecodeTvc, Awaitable[ResultOfDecodeTvc]]:
        """
        Decodes tvc into code, data, libraries and special options

        :param params: See `types.ParamsOfDecodeTvc`
        :return: See `types.ResultOfDecodeTvc`
        """
        response = self.request(method='boc.decode_tvc', **params.dict)
        return self.response(classname=ResultOfDecodeTvc, response=response)

    def encode_tvc(
        self, params: ParamsOfEncodeTvc
    ) -> Union[ResultOfEncodeTvc, Awaitable[ResultOfEncodeTvc]]:
        """
        Encodes tvc from code, data, libraries ans special options
        (see input params)

        :param params: See `types.ParamsOfEncodeTvc`
        :return: See `types.ResultOfEncodeTvc`
        """
        response = self.request(method='boc.encode_tvc', **params.dict)
        return self.response(classname=ResultOfEncodeTvc, response=response)

    def get_compiler_version(
        self, params: ParamsOfGetCompilerVersion
    ) -> Union[ResultOfGetCompilerVersion, Awaitable[ResultOfGetCompilerVersion]]:
        """
        Returns the compiler version used to compile the code

        :param params: See `types.ParamsOfGetCompilerVersion`
        :return: See `types.ResultOfGetCompilerVersion`
        """
        response = self.request(method='boc.get_compiler_version', **params.dict)
        return self.response(classname=ResultOfGetCompilerVersion, response=response)

    def get_boc_depth(
        self, params: ParamsOfGetBocDepth
    ) -> Union[ResultOfGetBocDepth, Awaitable[ResultOfGetBocDepth]]:
        """
        Calculates BOC depth

        :param params: See `types.ParamsOfGetBocDepth`
        :return: See `types.ResultOfGetBocDepth`
        """
        response = self.request(method='boc.get_boc_depth', **params.dict)
        return self.response(classname=ResultOfGetBocDepth, response=response)

    def encode_external_in_message(
        self, params: ParamsOfEncodeExternalInMessage
    ) -> Union[
        ResultOfEncodeExternalInMessage, Awaitable[ResultOfEncodeExternalInMessage]
    ]:
        """
        Encodes a message.
        Allows to encode any external inbound message.

        :params params: See `types.ParamsOfEncodeExternalInMessage`
        :return: See `types.ResultOfEncodeExternalInMessage`
        """
        response = self.request(method='boc.encode_external_in_message', **params.dict)
        return self.response(
            classname=ResultOfEncodeExternalInMessage, response=response
        )
