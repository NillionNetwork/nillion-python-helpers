import os
import sys
import subprocess
import time
import tempfile
import signal
import argparse

# ANSI escape codes for bold red text
BOLD_RED = "\033[1;31m"
GREEN = "\033[0;32m"
RESET = "\033[0m"


def usage():
    print(sys.argv)
    print(f"{GREEN} Usage: {sys.argv[0]} [-v version] {RESET}")
    sys.exit(1)


# Set number of node and user keys to be created
num_node_keys = 5
num_user_keys = 5

# Set env file to update
ENV_TO_UPDATE = ".env"

NILLION_DEVNET = "nillion-devnet"
NILLION_CLI = "nillion"
NILLION_CLI_COMMAND_USER_KEYGEN = "user-key-gen"
NILLION_CLI_COMMAND_NODE_KEYGEN = "node-key-gen"


def run_command(command, shell=False, capture_output=False, check_return_code=True):
    try:
        result = subprocess.run(
            command, shell=shell, capture_output=capture_output, text=True
        )
        if check_return_code and result.returncode != 0:
            print(f"{BOLD_RED}Error: Command failed - {command}{RESET}")
            print(f"{BOLD_RED}ERROR: {result.stderr}{RESET}")
            return None
        else:
            print(f"{GREEN}Command: {command} executed{RESET}")
        return result.stdout if capture_output else None
    except subprocess.CalledProcessError as e:
        print(f"{BOLD_RED}Error: Command failed - {command}{RESET}")
        print(f"Exception: {e}")
        return None


def update_env(key, value, *files):
    for file in files:
        if os.path.exists(file):
            with open(file, "r") as f:
                lines = f.readlines()
            with open(file, "w") as f:
                lines = [line for line in lines if not line.startswith(f"{key}=")]
                lines.append(f"{key}={value}\n")
                f.writelines(lines)
        else:
            with open(file, "w") as f:
                f.write(f"{key}={value}\n")


def log_file_contents(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read()
    else:
        print(f"File {file_path} does not exist.")
        return None


def kill_nillion_devnet():
    # Kill any other nillion-devnet processes
    run_command(
        f"pkill -9 -f {NILLION_DEVNET}", shell=True, check_return_code=False
    )  # We don't check as it returns 1 if no process is found
    run_command(
        f"pkill -9 -f anvil", shell=True, check_return_code=False
    )  # We don't check as it returns 1 if no process is found
    print(f"{GREEN}ℹ️ Killed any existing nillion-devnet and anvil processes{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Script to manage the dependency.")
    parser.add_argument(
        "-k",
        "--kill",
        action="store_true",
        help="Kill the nillion-devnet and anvil process if it is running.",
    )
    args = parser.parse_args()

    kill_nillion_devnet()
    if args.kill:
        sys.exit(0)

    # for var in [NILLION_DEVNET, NILLION_CLI]:
    #     print(f"ℹ️ found bin {var:<18} -> [{os.getenv(var, f'Failed to discover {var}')}]")

    outfile = tempfile.mktemp()
    pidfile = tempfile.mktemp()
    print("OUTFILE", outfile)
    print("PIDFILE", pidfile)

    os.system(f"{NILLION_DEVNET} > {outfile} & echo $! > {pidfile}")
    print("--------------------")
    print(
        f"Updating your {ENV_TO_UPDATE} files with nillion-devnet environment info... This may take a minute."
    )
    print("--------------------")

    time_limit = 160
    start_time = time.time()

    while True:
        with open(outfile, "r") as f:
            if "cluster is running, bootnode is at" in f.read():
                break

        if time.time() - start_time >= time_limit:
            print(
                f"Timeout reached while waiting for cluster to be ready in '{outfile}'",
                file=sys.stderr,
            )
            exit(1)

        time.sleep(5)

    print(f"ℹ️ Cluster has been STARTED (see {outfile})")
    print(log_file_contents(outfile))

    with open(outfile, "r") as f:
        lines = f.readlines()

    cluster_id = next(
        (line.split()[3] for line in lines if "cluster id is" in line), None
    )
    websocket = next((line.split()[1] for line in lines if "websocket:" in line), None)
    boot_multiaddr = next(
        (
            line.split()[6]
            for line in lines
            if "cluster is running, bootnode is at" in line
        ),
        None,
    )
    payments_config_file = next(
        (
            line.split()[4]
            for line in lines
            if "payments configuration written to" in line
        ),
        None,
    )
    wallet_keys_file = next(
        (line.split()[4] for line in lines if "wallet keys written to" in line), None
    )

    with open(payments_config_file, "r") as f:
        payments_lines = f.readlines()

    payments_rpc = next(
        (
            line.split()[1]
            for line in payments_lines
            if "blockchain_rpc_endpoint:" in line
        ),
        None,
    )
    payments_chain = next(
        (line.split()[1] for line in payments_lines if "chain_id:" in line), None
    )
    payments_sc_addr = next(
        (line.split()[1] for line in payments_lines if "payments_sc_address:" in line),
        None,
    )
    payments_bf_addr = next(
        (
            line.split()[1]
            for line in payments_lines
            if "blinding_factors_manager_sc_address:" in line
        ),
        None,
    )
    wallet_private_key = log_file_contents(wallet_keys_file).strip().splitlines()[-1]

    # Generate node keys and add to .env
    for i in range(1, num_node_keys + 1):
        nodekey_file = tempfile.mktemp()
        run_command([NILLION_CLI, NILLION_CLI_COMMAND_NODE_KEYGEN, nodekey_file])
        update_env(f"NILLION_NODEKEY_PATH_PARTY_{i}", nodekey_file, ENV_TO_UPDATE)
        update_env(
            f"NILLION_NODEKEY_TEXT_PARTY_{i}",
            log_file_contents(nodekey_file),
            ENV_TO_UPDATE,
        )

    # Generate user keys and add to .env
    for i in range(1, num_user_keys + 1):
        userkey_file = tempfile.mktemp()
        run_command([NILLION_CLI, NILLION_CLI_COMMAND_USER_KEYGEN, userkey_file])
        update_env(f"NILLION_USERKEY_PATH_PARTY_{i}", userkey_file, ENV_TO_UPDATE)
        update_env(
            f"NILLION_USERKEY_TEXT_PARTY_{i}",
            log_file_contents(userkey_file),
            ENV_TO_UPDATE,
        )

    print("🔑 Node key and user keys have been generated and added to .env")

    # Add environment variables to .env
    update_env("NILLION_WEBSOCKETS", websocket, ENV_TO_UPDATE)
    update_env("NILLION_CLUSTER_ID", cluster_id, ENV_TO_UPDATE)
    update_env("NILLION_BLOCKCHAIN_RPC_ENDPOINT", payments_rpc, ENV_TO_UPDATE)
    update_env(
        "NILLION_BLINDING_FACTORS_MANAGER_SC_ADDRESS", payments_bf_addr, ENV_TO_UPDATE
    )
    update_env("NILLION_PAYMENTS_SC_ADDRESS", payments_sc_addr, ENV_TO_UPDATE)
    update_env("NILLION_CHAIN_ID", payments_chain, ENV_TO_UPDATE)
    update_env("NILLION_WALLET_PRIVATE_KEY", wallet_private_key, ENV_TO_UPDATE)
    update_env("NILLION_BOOTNODE_MULTIADDRESS", boot_multiaddr, ENV_TO_UPDATE)

    print(
        f"Running at process pid: {run_command(f'pgrep -f {NILLION_DEVNET}', shell=True, capture_output=True).strip()}"
    )

    print("-------------------------------------------------------")
    print("                   7MM   7MM                           ")
    print("                    MM    MM                           ")
    print("              db    MM    MM    db                     ")
    print("                    MM    MM                           ")
    print(".7MMpMMMb.   7MM    MM    MM   7MM  ,pW-Wq. 7MMpMMMb.  ")
    print("  MM    MM    MM    MM    MM    MM 6W'    Wb MM    MM  ")
    print("  MM    MM    MM    MM    MM    MM 8M     M8 MM    MM  ")
    print("  MM    MM    MM    MM    MM    MM YA.   ,A9 MM    MM  ")
    print(".JMML  JMML..JMML..JMML..JMML..JMML. Ybmd9 .JMML  JMML.")
    print("-------------------------------------------------------")
    print("-------------------------------------------------------")
    print("-----------🦆 CONNECTED TO NILLION-DEVNET 🦆-----------")
    print("-------------------------------------------------------")

    print(
        f"ℹ️ Your {ENV_TO_UPDATE} file configurations were updated with nillion-devnet connection variables: websocket, cluster id, keys, blockchain info"
    )
    print(
        "💻 The Nillion devnet is still running behind the scenes; to spin down the Nillion devnet at any time, run 'yarn nillion-devnet-stop'"
    )

    print("--------------------")
    print(
        f"💻 Your Nillion local cluster is still running - process pid: {run_command(f'pgrep -f {NILLION_DEVNET}', shell=True, capture_output=True).strip()}"
    )
    print(
        "ℹ️  Updated your .env file configuration variables: bootnode, cluster id, keys, blockchain info"
    )
    print(
        "📋 Next, compile all Nada programs in the 'programs' folder with 'bash compile_programs.sh'"
    )


if __name__ == "__main__":
    main()
