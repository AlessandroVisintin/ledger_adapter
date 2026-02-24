import json
import os
import time

from web3 import Web3

from LedgerAdapter.connection import Connection
from LedgerAdapter.dag_hash_manager import DagHashManager
from LedgerAdapter.models import BlockchainError
from LedgerAdapter.utils import canonicalize_json, wait_for_liveness, pretty


RUN_ID = str(int(time.time()))
NODE_URL = os.getenv("NODE_URL")
GENESIS_CONTRACTS_PATH = "/app/genesis-contracts.json"
PRIVATE_KEY_ALICE = "0x3f9d4328d47d5aa8b84c4716679a78fc21eab62be253b99315e4fa924d07559f"
PRIVATE_KEY_BOB   = "0x26e4865f9787ec01bf0f586ac704bd7395262279a119cbadcf14e6336ec8c8a0"


# Three distinct documents
document_a = {
    "status":   "active",
    "version":  1,
    "metadata": {
        "tags":  ["supply-chain", "verified"],
        "owner": "Alice"
    },
    "id": f"record-{RUN_ID}-a"
}

document_b = {
    "status":   "active",
    "version":  1,
    "metadata": {
        "tags":  ["supply-chain", "verified"],
        "owner": "Bob"
    },
    "id": f"record-{RUN_ID}-b"
}

document_c = {
    "status":   "active",
    "version":  2,
    "metadata": {
        "tags":  ["supply-chain", "verified"],
        "owner": "Alice"
    },
    "id": f"record-{RUN_ID}-c"
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


# --- Build up contract history ---

# Add document A (Alice)
canonical_a = canonicalize_json(document_a)
resp_a = manager.add_hash(
    value=canonical_a,
    private_key=PRIVATE_KEY_ALICE,
    synchronous=True
    )
print(f"\nDocument A added:\n---\n{pretty(resp_a)}\n---")

first_block = int(resp_a.block.block_number)
event = [e for e in resp_a.events if e.event_name == "HashAdded"][0]
hash_a = event.event_results["hashValue"]
print(f"\nHash A:\n---\n{hash_a}\n---")

# Add document B (Bob)
canonical_b = canonicalize_json(document_b)
resp_b = manager.add_hash(
    value=canonical_b,
    private_key=PRIVATE_KEY_BOB,
    synchronous=True
    )
print(f"\nDocument B added:\n---\n{pretty(resp_b)}\n---")

event = [e for e in resp_b.events if e.event_name == "HashAdded"][0]
hash_b = event.event_results["hashValue"]

# Add document C (Alice)
canonical_c = canonicalize_json(document_c)
resp_c = manager.add_hash(
    value=canonical_c,
    private_key=PRIVATE_KEY_ALICE,
    synchronous=True
    )
print(f"\nDocument C added:\n---\n{pretty(resp_c)}\n---")

event = [e for e in resp_c.events if e.event_name == "HashAdded"][0]
hash_c = event.event_results["hashValue"]

# Link A → C
resp_link_ac = manager.add_outgoing_link(
    from_hash=hash_a,
    to_hash=hash_c,
    private_key=PRIVATE_KEY_ALICE,
    synchronous=True
    )
print(f"\nLink A → C added:\n---\n{pretty(resp_link_ac)}\n---")

# Link B → C
resp_link_bc = manager.add_outgoing_link(
    from_hash=hash_b,
    to_hash=hash_c,
    private_key=PRIVATE_KEY_BOB,
    synchronous=True
    )
print(f"\nLink B → C added:\n---\n{pretty(resp_link_bc)}\n---")

# Deprecate document A
resp_dep_a = manager.deprecate_hash(
    hashed_value=hash_a,
    private_key=PRIVATE_KEY_ALICE,
    synchronous=True
    )
print(f"\nDocument A deprecated:\n---\n{pretty(resp_dep_a)}\n---")

# Delete document A
resp_del_a = manager.delete_hash(
    hashed_value=hash_a,
    private_key=PRIVATE_KEY_ALICE,
    synchronous=True
    )
print(f"\nDocument A deleted:\n---\n{pretty(resp_del_a)}\n---")

last_block = int(resp_del_a.block.block_number)

# --- Reconstruct contract history using get_events ---

# 1. All event types across the full block range, returned in chronological order
print(f"\n\n=== Full contract history (blocks {first_block}–{last_block}) ===")
all_events = manager.get_events(
    from_block=first_block,
    to_block=last_block
    )
for evt in all_events:
    print(f"  block {evt.block_number} | {evt.event_name:30s} | {evt.event_args}")

# 2. Filter to a single event type
print("\n\n=== HashAdded events only ===")
added_events = manager.get_events(
    from_block=first_block,
    to_block=last_block,
    event_name="HashAdded"
    )
for evt in added_events:
    print(f"  block {evt.block_number} | owner: {evt.event_args.get('owner'):10s} | hash: {evt.event_args.get('hashValue')}")

# 3. Filter to a single event type for a specific hash (argument_filters)
print(f"\n\n=== Full lifecycle of hash A via argument_filters ===")
for event_name in ("HashAdded", "HashDeprecated", "HashDeleted"):
    events = manager.get_events(
        from_block=first_block,
        to_block=last_block,
        event_name=event_name,
        argument_filters={"hashValue": hash_a}
        )
    for evt in events:
        print(f"  block {evt.block_number} | {evt.event_name} | {evt.event_args}")

# 4. Narrow the block range to a single known block
dep_block = int(resp_dep_a.block.block_number)
print(f"\n\n=== HashDeprecated events at block {dep_block} only ===")
dep_events = manager.get_events(
    from_block=dep_block,
    to_block=dep_block,
    event_name="HashDeprecated"
    )
for evt in dep_events:
    print(f"  block {evt.block_number} | {evt.event_name} | {evt.event_args}")
