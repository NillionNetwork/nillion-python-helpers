import os

import py_nillion_client as nillion
from cosmpy.aerial.client import NetworkConfig
from cosmpy.aerial.client.utils import prepare_and_broadcast_basic_transaction
from cosmpy.aerial.tx import Transaction
from cosmpy.crypto.address import Address


async def pay(
    client: nillion.NillionClient,
    operation: nillion.Operation,
    payments_wallet,
    payments_client,
    cluster_id,
) -> nillion.PaymentReceipt:
    print("Getting quote for operation...")
    quote = await client.request_price_quote(cluster_id, operation)
    print(f"Quote cost is {quote.cost.total} unil")
    address = str(Address(payments_wallet.public_key(), "nillion"))
    message = nillion.create_payments_message(quote, address)
    tx = Transaction()
    tx.add_message(message)
    submitted_tx = prepare_and_broadcast_basic_transaction(
        payments_client, tx, payments_wallet, gas_limit=1000000
    )
    submitted_tx.wait_to_complete()
    print(
        f"Submitting payment receipt {quote.cost.total} unil, tx hash {submitted_tx.tx_hash}"
    )
    return nillion.PaymentReceipt(quote, submitted_tx.tx_hash)


async def quote(
    client: nillion.NillionClient,
    operation: nillion.Operation,
    payments_wallet,
    payments_client,
    cluster_id,
):
    print("Getting quote for operation...")
    quote = await client.request_price_quote(cluster_id, operation)
    return quote


async def pay_with_quote(
    client: nillion.NillionClient,
    quote: nillion.PriceQuote,
    payments_wallet,
    payments_client,
    cluster_id,
) -> nillion.PaymentReceipt:
    address = str(Address(payments_wallet.public_key(), "nillion"))
    message = nillion.create_payments_message(quote, address)
    tx = Transaction()
    tx.add_message(message)
    submitted_tx = prepare_and_broadcast_basic_transaction(
        payments_client, tx, payments_wallet, gas_limit=1000000
    )
    submitted_tx.wait_to_complete()
    print(
        f"Submitting payment receipt {quote.cost.total} unil, tx hash {submitted_tx.tx_hash}"
    )
    return nillion.PaymentReceipt(quote, submitted_tx.tx_hash)


def create_payments_config(chain_id, payments_endpoint):

    return NetworkConfig(
        chain_id=chain_id,
        url=f"grpc+http://{payments_endpoint}/",
        fee_minimum_gas_price=0,
        fee_denomination="unil",
        staking_denomination="unil",
        faucet_url=None,
    )
