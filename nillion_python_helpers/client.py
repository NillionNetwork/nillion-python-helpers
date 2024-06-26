import os

import py_nillion_client as nillion


def create_nillion_client(userkey, nodekey):
    """
    Creates and initializes a Nillion client.

    Args:
        userkey: The user key for the Nillion client.
        nodekey: The node key for the Nillion client.

    Returns:
        nillion.NillionClient: The initialized Nillion client instance.
    """
    bootnodes = [os.getenv("NILLION_BOOTNODE_MULTIADDRESS")]

    return nillion.NillionClient(
        nodekey, bootnodes, nillion.ConnectionMode.relay(), userkey
    )