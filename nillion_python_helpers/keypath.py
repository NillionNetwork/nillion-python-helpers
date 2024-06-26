import py_nillion_client as nillion


def getUserKeyFromFile(userkey_filepath):
    """
    Retrieves a UserKey object from a file.

    Args:
        userkey_filepath (str): The file path to the user key.

    Returns:
        nillion.UserKey: The UserKey object loaded from the file.
    """
    return nillion.UserKey.from_file(userkey_filepath)


def getNodeKeyFromFile(nodekey_filepath):
    """
    Retrieves a NodeKey object from a file.

    Args:
        nodekey_filepath (str): The file path to the node key.

    Returns:
        nillion.NodeKey: The NodeKey object loaded from the file.
    """
    return nillion.NodeKey.from_file(nodekey_filepath)
