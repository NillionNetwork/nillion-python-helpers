import py_nillion_client as nillion
from cosmpy.aerial.client import NetworkConfig
from cosmpy.aerial.client.utils import prepare_and_broadcast_basic_transaction
from cosmpy.aerial.tx import Transaction
from cosmpy.crypto.address import Address


async def get_quote_and_pay(
    client: nillion.NillionClient,
    operation: nillion.Operation,
    payments_wallet,
    payments_client,
    cluster_id,
    memo: str | None = None,
) -> nillion.PaymentReceipt:
    """
    Initiates a payment for the specified operation using the Nillion client.

    Args:
        client (nillion.NillionClient): The Nillion client instance.
        operation (nillion.Operation): The operation for which to request a price quote and make a payment.
        payments_wallet: The wallet to be used for the payment.
        payments_client: The client used to process the payment transaction.
        cluster_id: The cluster identifier for the Nillion network.
        memo (str | None, optional): An optional memo to include with the transaction. Defaults to None.

    Returns:
        nillion.PaymentReceipt: The receipt of the payment containing the quote and transaction hash.
    """
    print("Getting quote for operation...")
    quote = await client.request_price_quote(cluster_id, operation)
    print(f"Quote cost is {quote.cost.total} unil")
    address = str(Address(payments_wallet.public_key(), "nillion"))
    message = nillion.create_payments_message(quote, address)
    tx = Transaction()
    tx.add_message(message)

    # Pass the memo parameter to prepare_and_broadcast_basic_transaction, default to an empty string if memo is None
    submitted_tx = prepare_and_broadcast_basic_transaction(
        payments_client, tx, payments_wallet, gas_limit=1000000, memo=memo
    )

    submitted_tx.wait_to_complete()
    print(
        f"Submitting payment receipt {quote.cost.total} unil, tx hash {submitted_tx.tx_hash}"
    )
    return nillion.PaymentReceipt(quote, submitted_tx.tx_hash)


async def get_quote(
    client: nillion.NillionClient,
    operation: nillion.Operation,
    cluster_id,
):
    """
    Retrieves a price quote for the specified operation using the Nillion client.

    Args:
        client (nillion.NillionClient): The Nillion client instance.
        operation (nillion.Operation): The operation for which to request a price quote.
        cluster_id: The cluster identifier for the Nillion network.

    Returns:
        nillion.PriceQuote: The price quote for the operation.
    """
    print("Getting quote for operation...")
    quote = await client.request_price_quote(cluster_id, operation)
    return quote


async def pay_with_quote(
    quote: nillion.PriceQuote,
    payments_wallet,
    payments_client,
) -> nillion.PaymentReceipt:
    """
    Processes a payment using an existing price quote.

    Args:
        quote (nillion.PriceQuote): The price quote for the operation.
        payments_wallet: The wallet to be used for the payment.
        payments_client: The client used to process the payment transaction.

    Returns:
        nillion.PaymentReceipt: The receipt of the payment containing the quote and transaction hash.
    """
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


def create_payments_config(chain_id, payments_endpoint, scheme="grpc"):
    """
    Creates a network configuration for the payments client.

    Args:
        chain_id: The chain ID of the network.
        payments_endpoint: The http or https endpoint URL for the payments service.
        scheme: The scheme to use for the URL. Defaults to "grpc".

    Returns:
        NetworkConfig: The network configuration object.
    """
    if not payments_endpoint.startswith(("http://", "https://")):
        print(
            "Deprecation warning: payments_endpoint should start with http:// or https://"
        )
        payments_endpoint = f"http://{payments_endpoint}"

    return NetworkConfig(
        chain_id=chain_id,
        url=f"{scheme}+{payments_endpoint}/",
        fee_minimum_gas_price=0,
        fee_denomination="unil",
        staking_denomination="unil",
        faucet_url=None,
    )
