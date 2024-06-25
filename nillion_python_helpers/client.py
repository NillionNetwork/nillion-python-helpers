import os

import py_nillion_client as nillion


def create_nillion_client(userkey, nodekey):
    bootnodes = [os.getenv("NILLION_BOOTNODE_MULTIADDRESS")]

    return nillion.NillionClient(
        nodekey, bootnodes, nillion.ConnectionMode.relay(), userkey
    )
