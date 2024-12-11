import asyncio

from web3 import AsyncWeb3, AsyncHTTPProvider
from web3.contract import AsyncContract
from web3.exceptions import TransactionNotFound
from config import RPC_URLS, EXPLORERS_URL, L2_PASS_ABI, L2PASS_CONTRACTS


class Client:
    def __init__(self, private_key, chain_name):
        self.private_key = private_key
        # request_kwargs = {'proxy': f'http://{proxy}'}
        rpc_url = RPC_URLS[chain_name]
        self.chain_name = chain_name
        # self.proxy = proxy
        self.eip_1559 = True
        self.explorer_url = EXPLORERS_URL[chain_name]
        self.w3 = AsyncWeb3(AsyncHTTPProvider(rpc_url))
        self.address = self.w3.to_checksum_address(self.w3.eth.account.from_key(self.private_key).address)


    def get_contract_nft(self) -> AsyncContract:
        return self.w3.eth.contract(
            address=AsyncWeb3.to_checksum_address(L2PASS_CONTRACTS[self.chain_name]),
            abi=L2_PASS_ABI
        )

    def get_estimate_gas(self) -> AsyncContract:
        return self.w3.eth.contract(
            address=AsyncWeb3.to_checksum_address(L2PASS_CONTRACTS[self.chain_name]),
            abi=L2_PASS_ABI
        )

    async def get_balance(self):
        return await self.w3.eth.get_balance(self.address)

    async def get_priotiry_fee(self) -> int:
        fee_history = await self.w3.eth.fee_history(5, 'latest', [80.0])
        non_empty_block_priority_fees = [fee[0] for fee in fee_history["reward"] if fee[0] != 0]

        divisor_priority = max(len(non_empty_block_priority_fees), 1)
        priority_fee = int(round(sum(non_empty_block_priority_fees) / divisor_priority))

        return priority_fee

    async def prepare_tx(self, value: int = 0):
        transaction = {
            'chainId': await self.w3.eth.chain_id,
            'nonce': await self.w3.eth.get_transaction_count(self.address),
            'from': self.address,
            'value': value,
            'gasPrice': int((await self.w3.eth.gas_price) * 1.25)
        }

        if self.eip_1559:
            del transaction['gasPrice']

            base_fee = await self.w3.eth.gas_price
            max_priority_fee_per_gas = await self.get_priotiry_fee()

            if max_priority_fee_per_gas == 0:
                max_priority_fee_per_gas = base_fee

            max_fee_per_gas = int(base_fee * 1.25 + max_priority_fee_per_gas)

            transaction['maxPriorityFeePerGas'] = max_priority_fee_per_gas
            transaction['maxFeePerGas'] = max_fee_per_gas
            transaction['type'] = '0x2'

        return transaction

    async def send_transaction(
            self, transaction=None, without_gas: bool = False, need_hash: bool = False, ready_tx: bytes = None, logger = None
    ):
        if ready_tx:
            tx_hash_bytes = await self.w3.eth.send_raw_transaction(ready_tx)
            logger.info('Successfully sent transaction!')

            tx_hash_hex = self.w3.to_hex(tx_hash_bytes)
        else:

            if not without_gas:
                transaction['gas'] = int((await self.w3.eth.estimate_gas(transaction)) * 1.5)

            signed_raw_tx = self.w3.eth.account.sign_transaction(transaction, self.private_key).rawTransaction
            logger.info('Successfully signed transaction!')

            tx_hash_bytes = await self.w3.eth.send_raw_transaction(signed_raw_tx)
            logger.info('Successfully sent transaction!')

            tx_hash_hex = self.w3.to_hex(tx_hash_bytes)

        if need_hash:
            await self.wait_tx(tx_hash_hex, logger)
            return tx_hash_hex

        return await self.wait_tx(tx_hash_hex, logger)

    async def wait_tx(self, tx_hash, logger):
        total_time = 0
        timeout = 120
        poll_latency = 10
        while True:
            try:
                receipts = await self.w3.eth.get_transaction_receipt(tx_hash)
                status = receipts.get("status")
                if status == 1:
                    logger.info(f'Transaction was successful: {self.explorer_url}tx/{tx_hash}')
                    return True
                elif status is None:
                    await asyncio.sleep(poll_latency)
                else:
                    logger.error(f'Transaction failed: {self.explorer_url}tx/{tx_hash}')
                    return False
            except TransactionNotFound:
                if total_time > timeout:
                    logger.warning(f"Transaction is not in the chain after {timeout} seconds")
                    return False
                total_time += poll_latency
                await asyncio.sleep(poll_latency)
