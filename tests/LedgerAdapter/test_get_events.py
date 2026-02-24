import time
import pytest
from web3 import Web3
from LedgerAdapter.models import BlockchainResponse, BlockchainError, EventData


class TestGetEvents:

    def test_get_events_hash_added_event(self, hash_manager, private_key_alice):
        unique_val = f"evt_add_{int(time.time())}"
        expected_hash = "0x" + Web3.keccak(text=unique_val).hex()

        response = hash_manager.add(
            value=unique_val, private_key=private_key_alice, synchronous=True
        )
        assert isinstance(response, BlockchainResponse)
        block_number = int(response.block.block_number)

        events = hash_manager.get_events(
            from_block=block_number,
            to_block=block_number,
            event_name="HashAdded",
        )

        assert len(events) >= 1
        assert all(isinstance(e, EventData) for e in events)
        assert all(e.event_name == "HashAdded" for e in events)

        tx_hash = response.transaction.transaction_hash
        matching = [e for e in events if e.transaction_hash == tx_hash]
        assert len(matching) == 1, "Expected exactly one HashAdded event for our tx"

        evt = matching[0]
        assert evt.event_args.get("hashValue") == expected_hash
        assert "owner" in evt.event_args
        assert evt.event_args["owner"] is not None

    def test_get_events_hash_deprecated_event(self, hash_manager, private_key_alice):
        unique_val = f"evt_dep_{int(time.time())}"
        expected_hash = "0x" + Web3.keccak(text=unique_val).hex()
        
        hash_manager.add(value=unique_val, private_key=private_key_alice, synchronous=True)
        hashed = "0x" + Web3.keccak(text=unique_val).hex()

        dep_response = hash_manager.deprecate(
            hashed_value=hashed, private_key=private_key_alice, synchronous=True
        )
        assert isinstance(dep_response, BlockchainResponse)
        block_number = int(dep_response.block.block_number)

        events = hash_manager.get_events(
            from_block=block_number,
            to_block=block_number,
            event_name="HashDeprecated",
        )

        assert len(events) >= 1
        assert all(e.event_name == "HashDeprecated" for e in events)

        tx_hash = dep_response.transaction.transaction_hash
        matching = [e for e in events if e.transaction_hash == tx_hash]
        assert len(matching) == 1

        evt = matching[0]
        assert evt.event_args.get("hashValue") == expected_hash


    def test_get_events_no_event_name_returns_all_event_types(self, hash_manager, private_key_alice):
        unique_val = f"evt_all_{int(time.time())}"
        add_resp = hash_manager.add(
            value=unique_val, private_key=private_key_alice, synchronous=True
        )
        hashed = "0x" + Web3.keccak(text=unique_val).hex()
        dep_resp = hash_manager.deprecate(
            hashed_value=hashed, private_key=private_key_alice, synchronous=True
        )

        from_block = int(add_resp.block.block_number)
        to_block = int(dep_resp.block.block_number)

        events = hash_manager.get_events(from_block=from_block, to_block=to_block)
        event_names = {e.event_name for e in events}

        assert "HashAdded" in event_names
        assert "HashDeprecated" in event_names

    def test_get_events_block_range_excludes_blocks(self, hash_manager, private_key_alice):
        val_early = f"evt_early_{int(time.time())}"
        resp_early = hash_manager.add(
            value=val_early, private_key=private_key_alice, synchronous=True
        )
        block_early = int(resp_early.block.block_number)

        val_late = f"evt_late_{int(time.time())}"
        resp_late = hash_manager.add(
            value=val_late, private_key=private_key_alice, synchronous=True
        )
        block_late = int(resp_late.block.block_number)

        events = hash_manager.get_events(
            from_block=block_early,
            to_block=block_early,
            event_name="HashAdded",
        )

        tx_hashes = {e.transaction_hash for e in events}
        assert resp_early.transaction.transaction_hash in tx_hashes
        assert resp_late.transaction.transaction_hash not in tx_hashes

        events = hash_manager.get_events(
            from_block=block_late,
            to_block=block_late,
            event_name="HashAdded",
        )

        tx_hashes = {e.transaction_hash for e in events}
        assert resp_late.transaction.transaction_hash in tx_hashes
        assert resp_early.transaction.transaction_hash not in tx_hashes

    def test_get_events_argument_filters_match_specific_hash(self, hash_manager, private_key_alice):
        val_a = f"evt_flt_a_{int(time.time())}"
        val_b = f"evt_flt_b_{int(time.time())}"

        resp_a = hash_manager.add(
            value=val_a, private_key=private_key_alice, synchronous=True
        )
        resp_b = hash_manager.add(
            value=val_b, private_key=private_key_alice, synchronous=True
        )

        target_hash_bytes = Web3.keccak(text=val_a)  # bytes32 for the filter
        from_block = int(resp_a.block.block_number)
        to_block = int(resp_b.block.block_number)

        events = hash_manager.get_events(
            from_block=from_block,
            to_block=to_block,
            event_name="HashAdded",
            argument_filters={"hashValue": target_hash_bytes},
        )

        assert len(events) >= 1
        tx_hashes = {e.transaction_hash for e in events}
        assert resp_a.transaction.transaction_hash in tx_hashes
        assert resp_b.transaction.transaction_hash not in tx_hashes

    def test_get_events_argument_filters_without_event_name_raises(self, hash_manager):
        with pytest.raises(
            BlockchainError, match="argument_filters requires a specific event_name"
        ):
            hash_manager.get_events(
                from_block=0,
                argument_filters={"hashValue": Web3.keccak(text="any")},
            )

    def test_get_events_unknown_event_name_raises(self, hash_manager):
        with pytest.raises(BlockchainError, match="not found in contract ABI"):
            hash_manager.get_events(event_name="NonExistentEvent")

    def test_get_events_event_data_fields_are_populated(self, hash_manager, private_key_alice):
        unique_val = f"evt_fields_{int(time.time())}"
        response = hash_manager.add(
            value=unique_val, private_key=private_key_alice, synchronous=True
        )
        block_number = int(response.block.block_number)

        events = hash_manager.get_events(
            from_block=block_number,
            to_block=block_number,
            event_name="HashAdded",
        )
        assert len(events) >= 1

        evt = next(
            e for e in events if e.transaction_hash == response.transaction.transaction_hash
        )
        assert isinstance(evt, EventData)
        assert evt.address and isinstance(evt.address, str)
        assert evt.block_hash and evt.block_hash.startswith("0x")
        assert evt.block_number == str(block_number)
        assert evt.event_name == "HashAdded"
        assert isinstance(evt.event_args, dict) and len(evt.event_args) > 0
        assert evt.transaction_hash and evt.transaction_hash.startswith("0x")
        assert evt.log_index is not None


    def test_get_events_results_are_sorted_chronologically(self, hash_manager, private_key_alice):
        val1 = f"evt_ord1_{int(time.time())}"
        resp1 = hash_manager.add(
            value=val1, private_key=private_key_alice, synchronous=True
        )
        val2 = f"evt_ord2_{int(time.time())}"
        resp2 = hash_manager.add(
            value=val2, private_key=private_key_alice, synchronous=True
        )

        from_block = int(resp1.block.block_number)
        to_block = int(resp2.block.block_number)

        events = hash_manager.get_events(from_block=from_block, to_block=to_block)

        for i in range(len(events) - 1):
            curr_bn = int(events[i].block_number)
            next_bn = int(events[i + 1].block_number)
            assert curr_bn <= next_bn, (
                f"Events not sorted: block {curr_bn} appears before {next_bn}"
            )
