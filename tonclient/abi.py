from tonclient.decorators import result_as
from tonclient.module import TonModule
from tonclient.types import ParamsOfEncodeMessageBody, DecodedMessageBody, \
    ResultOfEncodeMessageBody, ParamsOfAttachSignatureToMessageBody, \
    ResultOfAttachSignatureToMessageBody, ParamsOfEncodeMessage, \
    ResultOfEncodeMessage, ParamsOfAttachSignature, ResultOfAttachSignature, \
    ParamsOfDecodeMessage, ParamsOfDecodeMessageBody, ParamsOfEncodeAccount, \
    ResultOfEncodeAccount, ParamsOfEncodeInternalMessage, \
    ResultOfEncodeInternalMessage


class TonAbi(TonModule):
    """ Free TON abi SDK API implementation """
    @result_as(classname=DecodedMessageBody)
    def decode_message(
            self, params: ParamsOfDecodeMessage) -> DecodedMessageBody:
        """
        Decodes message body using provided message BOC and ABI
        :param params: See `types.ParamsOfDecodeMessage`
        :return: See `types.DecodedMessageBody`
        """
        return self.request(method='abi.decode_message', **params.dict)

    @result_as(classname=DecodedMessageBody)
    def decode_message_body(
            self, params: ParamsOfDecodeMessageBody) -> DecodedMessageBody:
        """
        Decodes message body using provided body BOC and ABI
        :param params: See `types.ParamsOfDecodeMessageBody`
        :return: See `types.DecodedMessageBody`
        """
        return self.request(
            method='abi.decode_message_body', **params.dict)

    @result_as(classname=ResultOfEncodeAccount)
    def encode_account(
            self, params: ParamsOfEncodeAccount) -> ResultOfEncodeAccount:
        """
        Creates account state BOC.
        Creates account state provided with one of these sets of data:
            - BOC of code, BOC of data, BOC of library
            - TVC (string in base64), keys, init params
        :param params: See `types.ParamsOfEncodeAccount`
        :return: See `types.ResultOfEncodeAccount`
        """
        return self.request(method='abi.encode_account', **params.dict)

    @result_as(classname=ResultOfEncodeMessage)
    def encode_message(
            self, params: ParamsOfEncodeMessage) -> ResultOfEncodeMessage:
        """
        Encodes an ABI-compatible message.
        Allows to encode deploy and function call messages, both signed and
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
        return self.request(method='abi.encode_message', **params.dict)

    @result_as(classname=ResultOfEncodeMessageBody)
    def encode_message_body(
            self, params: ParamsOfEncodeMessageBody
    ) -> ResultOfEncodeMessageBody:
        """
        Encodes message body according to ABI function call
        :param params: See `types.ParamsOfEncodeMessageBody`
        :return: See `types.ResultOfEncodeMessageBody`
        """
        return self.request(
            method='abi.encode_message_body', **params.dict)

    @result_as(classname=ResultOfAttachSignature)
    def attach_signature(
            self, params: ParamsOfAttachSignature) -> ResultOfAttachSignature:
        """
        Combines `hex`-encoded `signature` with `base64`-encoded
        `unsigned_message`. Returns signed message encoded in `base64`
        :param params: See `types.ParamsOfAttachSignature`
        :return: See `types.ResultOfAttachSignature`
        """
        return self.request(method='abi.attach_signature', **params.dict)

    @result_as(classname=ResultOfAttachSignatureToMessageBody)
    def attach_signature_to_message_body(
            self, params: ParamsOfAttachSignatureToMessageBody
    ) -> ResultOfAttachSignatureToMessageBody:
        """
        :param params: See `types.ParamsOfAttachSignatureToMessageBody`
        :return: See `types.ResultOfAttachSignatureToMessageBody`
        """
        return self.request(
            method='abi.attach_signature_to_message_body', **params.dict)

    @result_as(classname=ResultOfEncodeInternalMessage)
    def encode_internal_message(
            self, params: ParamsOfEncodeInternalMessage
    ) -> ResultOfEncodeInternalMessage:
        """
        Encodes an internal ABI-compatible message.
        Allows to encode deploy and function call messages.
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
        return self.request(
            method='abi.encode_internal_message', **params.dict)
