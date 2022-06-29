"""ABI module methods"""
from typing import Union, Awaitable

from tonclient.module import TonModule
from tonclient.types import (
    ParamsOfCalcFunctionId,
    ParamsOfEncodeMessageBody,
    DecodedMessageBody,
    ResultOfCalcFunctionId,
    ResultOfEncodeMessageBody,
    ParamsOfAttachSignatureToMessageBody,
    ResultOfAttachSignatureToMessageBody,
    ParamsOfEncodeMessage,
    ResultOfEncodeMessage,
    ParamsOfAttachSignature,
    ResultOfAttachSignature,
    ParamsOfDecodeMessage,
    ParamsOfDecodeMessageBody,
    ParamsOfEncodeAccount,
    ResultOfEncodeAccount,
    ParamsOfEncodeInternalMessage,
    ResultOfEncodeInternalMessage,
    ParamsOfDecodeAccountData,
    ResultOfDecodeData,
    ParamsOfUpdateInitialData,
    ResultOfUpdateInitialData,
    ParamsOfDecodeInitialData,
    ResultOfDecodeInitialData,
    ParamsOfDecodeBoc,
    ResultOfDecodeBoc,
    ParamsOfEncodeInitialData,
    ResultOfEncodeInitialData,
    ParamsOfAbiEncodeBoc,
    ResultOfAbiEncodeBoc,
)


class TonAbi(TonModule):
    """Free TON abi SDK API implementation"""

    def decode_message(
        self, params: ParamsOfDecodeMessage
    ) -> Union[DecodedMessageBody, Awaitable[DecodedMessageBody]]:
        """
        Decodes message body using provided message BOC and ABI

        :param params: See `types.ParamsOfDecodeMessage`
        :return: See `types.DecodedMessageBody`
        """
        response = self.request(method="abi.decode_message", **params.dict)
        return self.response(classname=DecodedMessageBody, response=response)

    def decode_message_body(
        self, params: ParamsOfDecodeMessageBody
    ) -> Union[DecodedMessageBody, Awaitable[DecodedMessageBody]]:
        """
        Decodes message body using provided body BOC and ABI

        :param params: See `types.ParamsOfDecodeMessageBody`
        :return: See `types.DecodedMessageBody`
        """
        response = self.request(method="abi.decode_message_body", **params.dict)
        return self.response(classname=DecodedMessageBody, response=response)

    def encode_account(
        self, params: ParamsOfEncodeAccount
    ) -> Union[ResultOfEncodeAccount, Awaitable[ResultOfEncodeAccount]]:
        """
        Creates account state BOC.
        Creates account state provided with one of these sets of data:
            - BOC of code, BOC of data, BOC of library
            - TVC (string in base64), keys, init params

        :param params: See `types.ParamsOfEncodeAccount`
        :return: See `types.ResultOfEncodeAccount`
        """
        response = self.request(method="abi.encode_account", **params.dict)
        return self.response(classname=ResultOfEncodeAccount, response=response)

    def encode_message(
        self, params: ParamsOfEncodeMessage
    ) -> Union[ResultOfEncodeMessage, Awaitable[ResultOfEncodeMessage]]:
        """
        Encodes an ABI-compatible message.
        Allows encoding deploy and function call messages, both signed and
        unsigned.
        Use cases include messages of any possible type:
            - deploy with initial function call (i.e. `constructor` or any
              other function that is used for some kind of initialization);
            - deploy without initial function call;
            - signed/unsigned + data for signing.

        `Signer` defines how the message should or shouldn't be signed:
            - `Signer::None` creates an unsigned message. This may be needed
               in case of some public methods, that do not require
               authorization by pubkey;
            - `Signer::External` takes public key and returns `data_to_sign`
               for later signing.
               Use `attach_signature` method with the result signature to get
               the signed message;
            - `Signer::Keys` creates a signed message with provided key pair;
            - `Signer::SigningBox` Allows using a special interface to
              implement signing without private key disclosure to SDK.
              For instance, in case of using a cold wallet or HSM, when
              application calls some API to sign data.

        :param params: See `types.ParamsOfEncodeMessage`
        :return: See `types.ResultOfEncodeMessage`
        """
        response = self.request(method="abi.encode_message", **params.dict)
        return self.response(classname=ResultOfEncodeMessage, response=response)

    def encode_message_body(
        self, params: ParamsOfEncodeMessageBody
    ) -> Union[ResultOfEncodeMessageBody, Awaitable[ResultOfEncodeMessageBody]]:
        """
        Encodes message body according to ABI function call

        :param params: See `types.ParamsOfEncodeMessageBody`
        :return: See `types.ResultOfEncodeMessageBody`
        """
        response = self.request(method="abi.encode_message_body", **params.dict)
        return self.response(classname=ResultOfEncodeMessageBody, response=response)

    def attach_signature(
        self, params: ParamsOfAttachSignature
    ) -> Union[ResultOfAttachSignature, Awaitable[ResultOfAttachSignature]]:
        """
        Combines `hex`-encoded `signature` with `base64`-encoded
        `unsigned_message`. Returns signed message encoded in `base64`

        :param params: See `types.ParamsOfAttachSignature`
        :return: See `types.ResultOfAttachSignature`
        """
        response = self.request(method="abi.attach_signature", **params.dict)
        return self.response(classname=ResultOfAttachSignature, response=response)

    def attach_signature_to_message_body(
        self, params: ParamsOfAttachSignatureToMessageBody
    ) -> Union[
        ResultOfAttachSignatureToMessageBody,
        Awaitable[ResultOfAttachSignatureToMessageBody],
    ]:
        """
        :param params: See `types.ParamsOfAttachSignatureToMessageBody`
        :return: See `types.ResultOfAttachSignatureToMessageBody`
        """
        response = self.request(
            method="abi.attach_signature_to_message_body", **params.dict
        )
        return self.response(
            classname=ResultOfAttachSignatureToMessageBody, response=response
        )

    def encode_internal_message(
        self, params: ParamsOfEncodeInternalMessage
    ) -> Union[ResultOfEncodeInternalMessage, Awaitable[ResultOfEncodeInternalMessage]]:
        """
        Encodes an internal ABI-compatible message.
        Allows encoding deploy and function call messages.
        Use cases include messages of any possible type:
          - deploy with initial function call (i.e. constructor or any other
            function that is used for some kind of initialization);
          - deploy without initial function call;
          - simple function call

        There is an optional public key can be provided in deploy set in
        order to substitute one in TVM file.
        Public key resolving priority:
          - public key from deploy set;
          - public key, specified in TVM file

        :param params: See `types.ParamsOfEncodeInternalMessage`
        :return: See `types.ResultOfEncodeInternalMessage`
        """
        response = self.request(method="abi.encode_internal_message", **params.dict)
        return self.response(classname=ResultOfEncodeInternalMessage, response=response)

    def decode_account_data(
        self, params: ParamsOfDecodeAccountData
    ) -> Union[ResultOfDecodeData, Awaitable[ResultOfDecodeData]]:
        """
        Decodes account data using provided data BOC and ABI.
        Note: this feature requires ABI 2.1 or higher

        :param params: See `types.ParamsOfDecodeAccountData`
        :return: See `types.ResultOfDecodeData`
        """
        response = self.request(method="abi.decode_account_data", **params.dict)
        return self.response(classname=ResultOfDecodeData, response=response)

    def encode_initial_data(
        self, params: ParamsOfEncodeInitialData
    ) -> Union[ResultOfEncodeInitialData, Awaitable[ResultOfEncodeInitialData]]:
        """
        Encodes initial account data with initial values for the contract's
        static variables and owner's public key into a data BOC that can be
        passed to encode_tvc function afterwards.

        This function is analogue of `tvm.buildDataInit` function in Solidity

        :param params:
        :return:
        """
        response = self.request(method="abi.encode_initial_data", **params.dict)
        return self.response(classname=ResultOfEncodeInitialData, response=response)

    def update_initial_data(
        self, params: ParamsOfUpdateInitialData
    ) -> Union[ResultOfUpdateInitialData, Awaitable[ResultOfUpdateInitialData]]:
        """
        Updates initial account data with initial values for the contract's
        static variables and owner's public key.
        This operation is applicable only for initial account data
        (before deploy).
        If the contract is already deployed, its data doesn't contain this
        data section anymore

        :param params: See `types.ParamsOfUpdateInitialData`
        :return: See `types.ResultOfUpdateInitialData`
        """
        response = self.request(method="abi.update_initial_data", **params.dict)
        return self.response(classname=ResultOfUpdateInitialData, response=response)

    def decode_initial_data(
        self, params: ParamsOfDecodeInitialData
    ) -> Union[ResultOfDecodeInitialData, Awaitable[ResultOfDecodeInitialData]]:
        """
        Decodes initial values of a contract's static variables and owner's
        public key from account initial data.
        This operation is applicable only for initial account data
        (before deploy).
        If the contract is already deployed, its data doesn't contain this
        data section anymore

        :param params: See `types.ParamsOfDecodeInitialData`
        :return: See `types.ResultOfDecodeInitialData`
        """
        response = self.request(method="abi.decode_initial_data", **params.dict)
        return self.response(classname=ResultOfDecodeInitialData, response=response)

    def decode_boc(
        self, params: ParamsOfDecodeBoc
    ) -> Union[ResultOfDecodeBoc, Awaitable[ResultOfDecodeBoc]]:
        """
        Decodes BOC into JSON as a set of provided parameters.
        Solidity functions use ABI types for builder encoding. The simplest
        way to decode such a BOC is to use ABI decoding. ABI has it own rules
        for fields layout in cells so manually encoded BOC can not be
        described in terms of ABI rules.

        To solve this problem we introduce a new ABI type `Ref(<ParamType>)`
        which allows store `ParamType` ABI parameter in cell reference and,
        thus, decode manually encoded BOCs. This type is available only in
        `decode_boc` function and will not be available in ABI messages
        encoding until it is included into some ABI revision.

        Such BOC descriptions covers most users needs. If someone wants to
        decode some BOC which can not be described by these rules (i.e. BOC
        with TLB containing constructors of flags defining some parsing
        conditions) then they can decode the fields up to fork condition,
        check the parsed data manually, expand the parsing schema and then
        decode the whole BOC with the full schema

        :param params: See `types.ParamsOfDecodeBoc`
        :return: See `types.ResultOfDecodeBoc`
        """
        response = self.request(method="abi.decode_boc", **params.dict)
        return self.response(classname=ResultOfDecodeBoc, response=response)

    def encode_boc(
        self, params: ParamsOfAbiEncodeBoc
    ) -> Union[ResultOfAbiEncodeBoc, Awaitable[ResultOfAbiEncodeBoc]]:
        """
        Encodes given parameters in JSON into a BOC using param types from ABI.

        :param params: See `types.ParamsOfAbiEncodeBoc`
        :return: See `types.ResultOfAbiEncodeBoc`
        """
        response = self.request(method="abi.encode_boc", **params.dict)
        return self.response(classname=ResultOfAbiEncodeBoc, response=response)

    def calc_function_id(
        self, params: ParamsOfCalcFunctionId
    ) -> Union[ResultOfCalcFunctionId, Awaitable[ResultOfCalcFunctionId]]:
        """
        Calculates contract function ID by contract ABI

        :param params: See `types.ParamsOfCalcFunctionId`
        :return: See `types.ResultOfCalcFunctionId`
        """
        response = self.request(method="abi.calc_function_id", **params.dict)
        return self.response(classname=ResultOfCalcFunctionId, response=response)
