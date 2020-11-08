from typing import Dict, Any

from tonclient.module import TonModule
from tonclient.types import Abi, Signer, DeploySet, CallSet, StateInitSource


class TonAbi(TonModule):
    """ Free TON abi SDK API implementation """
    def decode_message(self, abi: Abi, message: str) -> Dict[str, Any]:
        """
        Decodes message body using provided message BOC and ABI
        :param abi: Contract ABI
        :param message: Message BOC
        :return:
        """
        return self.request(
            method='abi.decode_message', abi=abi.dict, message=message)

    def decode_message_body(
            self, abi: Abi, body: str, is_internal: bool = False
    ) -> Dict[str, Any]:
        """
        Decodes message body using provided body BOC and ABI
        :param abi: Contract ABI used to decode
        :param body: Message body BOC encoded in `base64`
        :param is_internal: True if the body belongs to the internal message
        :return:
        """
        return self.request(
            method='abi.decode_message_body', abi=abi.dict, body=body,
            is_internal=is_internal)

    def encode_account(
            self, state_init: StateInitSource, balance: int = None,
            last_trans_lt: int = None, last_paid: int = None
    ) -> Dict[str, str]:
        """
        Creates account state BOC
        :param state_init: Source of the account state init
        :param balance: Initial balance
        :param last_trans_lt: Initial value for the `last_trans_lt`
        :param last_paid: Initial value for the `last_paid`
        :return:
        """
        return self.request(
            method='abi.encode_account', state_init=state_init.dict,
            balance=balance, last_trans_lt=last_trans_lt, last_paid=last_paid)

    def encode_message(
            self, abi: Abi, signer: Signer, address: str = None,
            deploy_set: DeploySet = None, call_set: CallSet = None,
            processing_try_index: int = 0) -> Dict[str, str]:
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
            - [SOON] `Signer::SigningBox` Allows using a special interface to
              implement signing without private key disclosure to SDK.
              For instance, in case of using a cold wallet or HSM, when
              application calls some API to sign data.
        :param abi: Contract ABI
        :param address: Target address the message will be sent to. Must be
                specified in case of non-deploy message
        :param deploy_set: Deploy parameters. Must be specified in case of
                deploy message
        :param call_set: Function call parameters. Must be specified in case
                of non-deploy message. In case of deploy message it is optional
                and contains parameters of the functions that will to be
                called upon deploy transaction
        :param signer: Signing parameters
        :param processing_try_index: Processing try index. Used in message
                processing with retries (if contract's ABI includes "expire"
                header). Encoder uses the provided try index to calculate
                message expiration time. The 1st message expiration time is
                specified in client config. Expiration timeouts will grow with
                every retry
        :return:
        """
        deploy_set = deploy_set.dict if deploy_set else deploy_set
        call_set = call_set.dict if call_set else call_set
        return self.request(
            method='abi.encode_message', abi=abi.dict, address=address,
            deploy_set=deploy_set, call_set=call_set, signer=signer.dict,
            processing_try_index=processing_try_index)

    def encode_message_body(
            self, abi: Abi, call_set: CallSet, signer: Signer,
            is_internal: bool, processing_try_index: int = 0
    ) -> Dict[str, str]:
        """
        Encodes message body according to ABI function call
        :param abi: Contract ABI
        :param call_set: Function call parameters. Must be specified in non
                deploy message. In case of deploy message contains parameters
                of constructor
        :param signer: Signing parameters
        :param is_internal: True if internal message body must be encoded
        :param processing_try_index: Processing try index. Used in message
                processing with retries. Encoder uses the provided try index
                to calculate message expiration time. Expiration timeouts will
                grow with every retry
        :return:
        """
        return self.request(
            method='abi.encode_message_body', abi=abi.dict,
            call_set=call_set.dict, signer=signer.dict,
            is_internal=is_internal, processing_try_index=processing_try_index)

    def attach_signature(
            self, abi: Abi, public_key: str, message: str, signature: str
    ) -> Dict[str, str]:
        """
        Combines `hex`-encoded `signature` with `base64`-encoded
        `unsigned_message`
        :param abi: Contract ABI
        :param public_key: Public key encoded in `hex`
        :param message: Unsigned message BOC encoded in `base64`
        :param signature: Signature encoded in `hex`
        :return:
        """
        return self.request(
            method='abi.attach_signature', abi=abi.dict, public_key=public_key,
            message=message, signature=signature)

    def attach_signature_to_message_body(
            self, abi: Abi, public_key: str, message: str, signature: str
    ) -> Dict[str, str]:
        """
        :param abi: Contract ABI
        :param public_key: Public key encoded in `hex`
        :param message: Unsigned message BOC encoded in `base64`
        :param signature: Signature encoded in `hex`
        :return:
        """
        return self.request(
            method='abi.attach_signature_to_message_body', abi=abi.dict,
            public_key=public_key, message=message, signature=signature)
