import json
import os
import time

from LedgerAdapter.connection import Connection
from LedgerAdapter.dag_hash_manager import DagHashManager
from LedgerAdapter.models import BlockchainError
from LedgerAdapter.utils import canonicalize_json, wait_for_liveness, pretty


RUN_ID = str(int(time.time()))
NODE_URL = os.getenv("NODE_URL")
GENESIS_CONTRACTS_PATH = "/app/genesis-contracts.json"
PRIVATE_KEY_ALICE = "0x3f9d4328d47d5aa8b84c4716679a78fc21eab62be253b99315e4fa924d07559f"
PRIVATE_KEY_BOB   = "0x26e4865f9787ec01bf0f586ac704bd7395262279a119cbadcf14e6336ec8c8a0"


# Identical docs with different key ordering — same canonical hash
document_a = {
    "status":   "active",
    "version":  1,
    "metadata": {
        "tags":  ["supply-chain", "verified"],
        "owner": "Alice"
    },
    "id": f"step-{RUN_ID}"
}

document_b = {
    "id": f"step-{RUN_ID}",
    "metadata": {
        "owner": "Alice",
        "tags":  ["supply-chain", "verified"]
    },
    "status":  "active",
    "version": 1
}

# A distinct downstream document — represents the next node in the DAG
document_c = {
    "status":   "active",
    "version":  1,
    "metadata": {
        "tags":  ["supply-chain", "verified"],
        "owner": "Alice"
    },
    "id": f"step-{RUN_ID}-next"
}


# Gather contract details
with open(GENESIS_CONTRACTS_PATH, "r") as f:
    genesis = json.load(f)
contract_address = genesis["DagHashManager"]["address"]
contract_abi     = genesis["DagHashManager"]["abi"]

# Create connection and check for node liveness
connection = Connection(node_url=NODE_URL)
wait_for_liveness(connection)

# Create the manager
manager = DagHashManager(
    node_connection=connection,
    contract_address=contract_address,
    contract_abi=contract_abi
)

# Store document A
canonical_a = canonicalize_json(document_a)
try:
    response = manager.add_hash(
        value=canonical_a,
        private_key=PRIVATE_KEY_ALICE,
        synchronous=True
        )
    print(f"\nDocument A added:\n---\n{pretty(response)}\n---")
except BlockchainError as e:
    raise

# Get hashed value for document A
event = [e for e in response.events if e.event_name == "HashAdded"][0]
hash_a = event.event_results['hashValue']
print(f"\nHash A value retrieved:\n---\n{hash_a}\n---")

# Document B should raise an error because identical to document A
canonical_b = canonicalize_json(document_b)
try:
    response = manager.add_hash(
        value=canonical_b,
        private_key=PRIVATE_KEY_BOB,
        synchronous=True
        )
except BlockchainError as e:
    print(f"\nError adding document B:\n---\n{pretty(e)}\n---")

# Read document A
try:
    result = manager.read_hash(hashed_value=hash_a)
    print(f"\nReading returns index and owner:\n---\n{pretty(result)}\n---")
except BlockchainError as e:
    raise

# Store document C (a distinct downstream node)
canonical_c = canonicalize_json(document_c)
try:
    response = manager.add_hash(
        value=canonical_c,
        private_key=PRIVATE_KEY_ALICE,
        synchronous=True
        )
    print(f"\nDocument C added:\n---\n{pretty(response)}\n---")
except BlockchainError as e:
    raise

event = [e for e in response.events if e.event_name == "HashAdded"][0]
hash_c = event.event_results['hashValue']
print(f"\nHash C value retrieved:\n---\n{hash_c}\n---")

# Add a DAG link from A to C
try:
    response = manager.add_outgoing_link(
        from_hash=hash_a,
        to_hash=hash_c,
        private_key=PRIVATE_KEY_ALICE,
        synchronous=True
        )
    print(f"\nOutgoing link A → C added:\n---\n{pretty(response)}\n---")
except BlockchainError as e:
    raise

# Read outgoing links of A
try:
    result = manager.read_outgoing_links(hashed_value=hash_a)
    print(f"\nOutgoing links of A:\n---\n{pretty(result)}\n---")
except BlockchainError as e:
    raise

# Deprecate document A
try:
    response = manager.deprecate_hash(
        hashed_value=hash_a,
        private_key=PRIVATE_KEY_ALICE,
        synchronous=True
        )
    print(f"\nDocument A deprecated:\n---\n{pretty(response)}\n---")
except BlockchainError as e:
    raise

# Delete document A (only possible after deprecation)
try:
    response = manager.delete_hash(
        hashed_value=hash_a,
        private_key=PRIVATE_KEY_ALICE,
        synchronous=True
        )
    print(f"\nDocument A deleted:\n---\n{pretty(response)}\n---")
except BlockchainError as e:
    raise
