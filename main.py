import asyncio
import logging

from web3.contract import AsyncContract

from client import Client
from config import L2PASS_CONTRACTS

# Настройка логгера
logging.basicConfig(filename='myapp.log',level=logging.INFO)
logger = logging.getLogger(__name__)

def init_chain_by_input():
    while True:
        chain_name = input("Available blockchains for mint: \"Base\", \"Arbitrum\", \"Optimism\"\n"
                      "Enter blockchain for mint: ")
        if chain_name in L2PASS_CONTRACTS.keys():
            logger.info("Blockchain correctly!")
            return chain_name
        else:
            print("Blockchain not correctly! Please try again!\n")
            logger.warning("input blockchain not correctly!")

def init_pk_by_input():
    while True:
        pk = input("Enter private key: ")
        logger.info("Private  key correctly")
        if len(pk) == 66 or len(pk) == 64:
            return pk
        else:
            print("Private key not correctly!")
            logger.warning("input private key not correctly!")

async def init_amount_nft_by_input(client: Client):
    while True:
        try:
            amount_nft = int(input("\nEnter required amount of nft: "))
            if await check_balance_for_mint_by_amount(client, amount_nft):
                logger.info(f"check_balance_for_mint_by_amount for {amount_nft} is True")
                return amount_nft
            else:
                print("\nNot enough balance for this amount! Please change amount!\n")
                logger.warning("Balance not enough for input amount nft!")
        except ValueError:
            print("Amount not number! Please try again!\n")
            logger.warning("input amount nft not correctly!")


async def check_balance_for_mint_by_amount(client, count_nft):
    gas_estimate = await client.w3.eth.estimate_gas(await client.prepare_tx())
    logger.info(f"gas_estimate: {gas_estimate} WEI")
    nft_cost = await get_nft_cost(client.get_contract_nft())
    logger.info(f"nft_cost: {nft_cost} WEI")

    full_estimate_cost_nft_by_amount = gas_estimate + count_nft * nft_cost
    logger.info(f"client balance: {await client.get_balance()} WEI")

    if await client.get_balance() > full_estimate_cost_nft_by_amount:
        return True

    return False

async def mint_nft(client : Client, amount : int):
    nft_contract = client.get_contract_nft()

    transaction = await nft_contract.functions.mint(
        amount
    ).build_transaction(
        await client.prepare_tx(value=await get_nft_cost(nft_contract))
    )

    logger.info(f"build_transaction_for_mint: {transaction}")
    return await client.send_transaction(transaction, logger=logger)

async def get_nft_cost(nft_contract : AsyncContract):
    return await nft_contract.functions.mintPrice().call()


async def main():
    pk = init_pk_by_input()
    chain_name = init_chain_by_input()

    client = Client(pk, chain_name)

    amount = await init_amount_nft_by_input(client)

    await mint_nft(client, amount)

if __name__ == "__main__":
    asyncio.run(main())
