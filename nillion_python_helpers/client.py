import os
import py_nillion_client as nillion


def create_nillion_client(userkey, nodekey, bootnodes=None):
    """
    Creates and initializes a Nillion client.

    Args:
        userkey: The user key for the Nillion client.
        nodekey: The node key for the Nillion client.
        bootnodes: Optional; a list of bootnode addresses. Defaults to the value of
                   the "NILLION_BOOTNODE_MULTIADDRESS" environment variable.

    Returns:
        nillion.NillionClient: The initialized Nillion client instance.
    """
    if bootnodes is None:
        bootnodes = [os.getenv("NILLION_BOOTNODE_MULTIADDRESS")]

    return nillion.NillionClient(
        nodekey,
        bootnodes,
        nillion.ConnectionMode.relay(),
        userkey,
    )
