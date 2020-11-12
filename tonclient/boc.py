from typing import Dict, Any

from tonclient.decorators import Response
from tonclient.module import TonModule


class TonBoc(TonModule):
    """ Free TON boc SDK API implementation """
    @Response.parse_message
    def parse_message(self, boc: str) -> Dict[str, Any]:
        """
        Parses message BOC into a JSON
        :param boc: BOC encoded as `base64`
        :return: JSON containing parsed BOC
        """
        return self.request(method='boc.parse_message', boc=boc)

    @Response.parse_transaction
    def parse_transaction(self, boc: str) -> Dict[str, Any]:
        """
        Parses transaction BOC into a JSON
        :param boc: BOC encoded as `base64`
        :return: JSON containing parsed BOC
        """
        return self.request(method='boc.parse_transaction', boc=boc)

    @Response.parse_account
    def parse_account(self, boc: str) -> Dict[str, Any]:
        """
        Parses account BOC into a JSON
        :param boc: BOC encoded as `base64`
        :return: JSON containing parsed BOC
        """
        return self.request(method='boc.parse_account', boc=boc)

    @Response.parse_block
    def parse_block(self, boc: str) -> Dict[str, Any]:
        """
        Parses block BOC into a JSON
        :param boc: BOC encoded as `base64`
        :return: JSON containing parsed BOC
        """
        return self.request(method='boc.parse_block', boc=boc)

    @Response.parse_shardstate
    def parse_shardstate(
            self, boc: str, state_id: str, workchain_id: int
    ) -> Dict[str, Any]:
        """
        Parses shardstate boc into a JSON.
        JSON structure is compatible with GraphQL API shardstate object
        :param boc: BOC encoded as `base64`
        :param state_id: Shardstate identificator
        :param workchain_id: Workchain shardstate belongs to
        :return: JSON containing parsed BOC
        """
        return self.request(
            method='boc.parse_shardstate', boc=boc, id=state_id,
            workchain_id=workchain_id)

    @Response.get_boc_hash
    def get_boc_hash(self, boc: str) -> str:
        """
        Calculates BOC root hash
        :param boc: BOC encoded as `base64`
        :return: BOC root hash encoded with `hex`
        """
        return self.request(method='boc.get_boc_hash', boc=boc)

    @Response.get_blockchain_config
    def get_blockchain_config(self, block_boc: str) -> str:
        """
        :param block_boc: Key block BOC encoded as `base64`
        :return: Blockchain config BOC encoded as `base64`
        """
        return self.request(
            method='boc.get_blockchain_config', block_boc=block_boc)
