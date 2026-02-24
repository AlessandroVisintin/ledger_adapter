import json
import os
import time

from LedgerAdapter.connection import Connection
from LedgerAdapter.hash_manager import HashManager
from LedgerAdapter.models import BlockchainError
from LedgerAdapter.utils import canonicalize_json, wait_for_liveness, pretty


RUN_ID = str(int(time.time()))
NODE_URL = os.getenv("NODE_URL")
GENESIS_CONTRACTS_PATH = "/app/genesis-contracts.json"
PRIVATE_KEY_ALICE = "0x3f9d4328d47d5aa8b84c4716679a78fc21eab62be253b99315e4fa924d07559f"
PRIVATE_KEY_BOB   = "0x26e4865f9787ec01bf0f586ac704bd7395262279a119cbadcf14e6336ec8c8a0"


# Identical docs with different ordering
document_a = {
    "status":   "active",
    "version":  1,
    "metadata": {
        "tags":  ["supply-chain", "verified"],
        "owner": "Alice"
    },
    "id": f"item-{RUN_ID}"
}

document_b = {
    "id": f"item-{RUN_ID}",
    "metadata": {
        "owner": "Alice",
        "tags":  ["supply-chain", "verified"]
    },
    "status":  "active",
    "version": 1
}


# Gather contract details
with open(GENESIS_CONTRACTS_PATH, "r") as f:
    genesis = json.load(f)
contract_address = genesis["HashManager"]["address"]
contract_abi     = genesis["HashManager"]["abi"]

# Create connection and check for node liveness
connection = Connection(node_url=NODE_URL)
wait_for_liveness(connection)

# Create the manager
manager = HashManager(
    node_connection=connection,
    contract_address=contract_address,
    contract_abi=contract_abi
)

# Store document A
canonical_a = canonicalize_json(document_a)
try:
    response = manager.add(
        value=canonical_a,
        private_key=PRIVATE_KEY_ALICE,
        synchronous=True
        )
    print(f"\nDocument A added:\n---\n{pretty(response)}\n---")
except BlockchainError as e:
    raise

# Get hashed value
event = [e for e in response.events if e.event_name == "HashAdded"][0]
hashed_value = event.event_results['hashValue']
print(f"\nHash value retrieved:\n---\n{hashed_value}\n---")

# Document B should raise an error because identical to document A
canonical_b = canonicalize_json(document_b)
try:
    response = manager.add(
        value=canonical_b,
        private_key=PRIVATE_KEY_BOB,
        synchronous=True
        )
except BlockchainError as e:
    print(f"\nError adding document B:\n---\n{pretty(e)}\n---")

# Read Document A
try:
    result = manager.read(hashed_value=hashed_value)
    print(f"\nReading returns index and owner:\n---\n{pretty(result)}\n---")
except BlockchainError as e:
    raise

# Deprecate Document A
try:
    response = manager.deprecate(
        hashed_value=hashed_value,
        private_key=PRIVATE_KEY_ALICE,
        synchronous=True
        )
    print(f"\nDeprecating returns index and owner:\n---\n{pretty(result)}\n---")
except BlockchainError as e:
    raise