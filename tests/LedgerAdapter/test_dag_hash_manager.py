import time
import pytest

from web3 import Web3

from LedgerAdapter.models import BlockchainResponse, BlockchainValue, BlockchainError


class TestDagHashManager:

    def test_add_hash(self, dag_hash_manager, private_key_alice):
        test_value = f"test_value_{int(time.time())}"
        response = dag_hash_manager.add_hash(value=test_value, private_key=private_key_alice, synchronous=True)

        assert isinstance(response, BlockchainResponse)
        assert response.status == "1"
        assert response.transaction.transaction_hash is not None

    def test_read_hash(self, dag_hash_manager, private_key_alice):
        unique_val = f"read_test_{int(time.time())}"
        add_resp = dag_hash_manager.add_hash(value=unique_val, private_key=private_key_alice, synchronous=True)
        assert isinstance(add_resp, BlockchainResponse)

        hashed_key = Web3.keccak(text=unique_val).hex()
        result = dag_hash_manager.read_hash(hashed_value=hashed_key)

        assert isinstance(result, BlockchainValue)
        assert result.value is not None

    def test_deprecate_hash(self, dag_hash_manager, private_key_alice):
        unique_val = f"deprecate_test_{int(time.time())}"
        dag_hash_manager.add_hash(value=unique_val, private_key=private_key_alice, synchronous=True)

        hashed_key = Web3.keccak(text=unique_val).hex()
        response = dag_hash_manager.deprecate_hash(hashed_value=hashed_key, private_key=private_key_alice, synchronous=True)

        assert isinstance(response, BlockchainResponse)
        assert response.status == "1"
        assert response.transaction.transaction_hash is not None

    def test_delete_hash(self, dag_hash_manager, private_key_alice):
        unique_val = f"delete_test_{int(time.time())}"
        dag_hash_manager.add_hash(value=unique_val, private_key=private_key_alice, synchronous=True)

        hashed_key = Web3.keccak(text=unique_val).hex()
        dag_hash_manager.deprecate_hash(hashed_value=hashed_key, private_key=private_key_alice, synchronous=True)
        response = dag_hash_manager.delete_hash(hashed_value=hashed_key, private_key=private_key_alice, synchronous=True)

        assert isinstance(response, BlockchainResponse)
        assert response.status == "1"
        assert response.transaction.transaction_hash is not None

    def test_add_outgoing_link(self, dag_hash_manager, private_key_alice):
        from_value = f"from_node_{int(time.time())}"
        to_value = f"to_node_{int(time.time())}"

        dag_hash_manager.add_hash(value=from_value, private_key=private_key_alice, synchronous=True)
        dag_hash_manager.add_hash(value=to_value, private_key=private_key_alice, synchronous=True)

        from_hash = Web3.keccak(text=from_value).hex()
        to_hash = Web3.keccak(text=to_value).hex()

        response = dag_hash_manager.add_outgoing_link(
            from_hash=from_hash,
            to_hash=to_hash,
            private_key=private_key_alice,
            synchronous=True
        )

        assert isinstance(response, BlockchainResponse)
        assert response.status == "1"
        assert response.transaction.transaction_hash is not None

    def test_read_outgoing_links(self, dag_hash_manager, private_key_alice):
        from_value = f"from_node_read_{int(time.time())}"
        to_value = f"to_node_read_{int(time.time())}"

        dag_hash_manager.add_hash(value=from_value, private_key=private_key_alice, synchronous=True)
        dag_hash_manager.add_hash(value=to_value, private_key=private_key_alice, synchronous=True)

        from_hash = Web3.keccak(text=from_value).hex()
        to_hash = Web3.keccak(text=to_value).hex()

        dag_hash_manager.add_outgoing_link(
            from_hash=from_hash,
            to_hash=to_hash,
            private_key=private_key_alice,
            synchronous=True
        )

        result = dag_hash_manager.read_outgoing_links(hashed_value=from_hash)

        assert isinstance(result, BlockchainValue)
        assert result.value is not None

    def test_delete_outgoing_link(self, dag_hash_manager, private_key_alice):
        from_value = f"from_node_read_{int(time.time())}"
        to_value = f"to_node_read_{int(time.time())}"

        dag_hash_manager.add_hash(value=from_value, private_key=private_key_alice, synchronous=True)
        dag_hash_manager.add_hash(value=to_value, private_key=private_key_alice, synchronous=True)

        from_hash = Web3.keccak(text=from_value).hex()
        to_hash = Web3.keccak(text=to_value).hex()

        dag_hash_manager.add_outgoing_link(
            from_hash=from_hash,
            to_hash=to_hash,
            private_key=private_key_alice,
            synchronous=True
        )

        response = dag_hash_manager.delete_outgoing_link(
            from_hash=from_hash,
            to_hash=to_hash,
            private_key=private_key_alice,
            synchronous=True
        )

        assert isinstance(response, BlockchainResponse)
        assert response.status == "1"
        assert response.transaction.transaction_hash is not None

    def test_multiple_outgoing_links(self, dag_hash_manager, private_key_alice):
        from_value = f"multi_from_{int(time.time())}"
        to_values = [f"multi_to_{i}_{int(time.time())}" for i in range(3)]

        dag_hash_manager.add_hash(value=from_value, private_key=private_key_alice, synchronous=True)
        for to_val in to_values:
            dag_hash_manager.add_hash(value=to_val, private_key=private_key_alice, synchronous=True)

        from_hash = Web3.keccak(text=from_value).hex()
        for to_val in to_values:
            to_hash = Web3.keccak(text=to_val).hex()
            response = dag_hash_manager.add_outgoing_link(
                from_hash=from_hash,
                to_hash=to_hash,
                private_key=private_key_alice,
                synchronous=True
            )
            assert isinstance(response, BlockchainResponse)
            assert response.status == "1"

        result = dag_hash_manager.read_outgoing_links(hashed_value=from_hash)
        assert isinstance(result, BlockchainValue)
        assert result.value is not None

    def test_add_hash_already_exists(self, dag_hash_manager, private_key_alice):
        value = f"dup_{int(time.time())}"
        dag_hash_manager.add_hash(value=value, private_key=private_key_alice, synchronous=True)

        with pytest.raises(BlockchainError, match="Hash already exists"):
            dag_hash_manager.add_hash(value=value, private_key=private_key_alice, synchronous=True)

    def test_read_hash_does_not_exist(self, dag_hash_manager):
        missing_value = f"missing_{int(time.time())}"
        missing_hash = Web3.keccak(text=missing_value).hex()

        with pytest.raises(BlockchainError, match="Hash does not exist"):
            dag_hash_manager.read_hash(hashed_value=missing_hash)

    def test_deprecate_hash_caller_not_owner(self, dag_hash_manager, private_key_alice, private_key_bob):
        value = f"owner_{int(time.time())}"
        dag_hash_manager.add_hash(value=value, private_key=private_key_alice, synchronous=True)
        h = Web3.keccak(text=value).hex()

        with pytest.raises(BlockchainError, match="Caller is not the owner"):
            dag_hash_manager.deprecate_hash(hashed_value=h, private_key=private_key_bob, synchronous=True)

    def test_deprecate_hash_already_deprecated(self, dag_hash_manager, private_key_alice):
        value = f"already_depr_{int(time.time())}"
        dag_hash_manager.add_hash(value=value, private_key=private_key_alice, synchronous=True)
        h = Web3.keccak(text=value).hex()

        dag_hash_manager.deprecate_hash(hashed_value=h, private_key=private_key_alice, synchronous=True)
        with pytest.raises(BlockchainError, match="Hash is already deprecated"):
            dag_hash_manager.deprecate_hash(hashed_value=h, private_key=private_key_alice, synchronous=True)

    def test_delete_hash_must_be_deprecated(self, dag_hash_manager, private_key_alice):
        value = f"del_not_depr_{int(time.time())}"
        dag_hash_manager.add_hash(value=value, private_key=private_key_alice, synchronous=True)
        h = Web3.keccak(text=value).hex()

        with pytest.raises(BlockchainError, match="Hash must be deprecated before deletion"):
            dag_hash_manager.delete_hash(hashed_value=h, private_key=private_key_alice, synchronous=True)

    def test_add_outgoing_link_cannot_link_hash_to_itself(self, dag_hash_manager, private_key_alice):
        value = f"self_link_{int(time.time())}"
        dag_hash_manager.add_hash(value=value, private_key=private_key_alice, synchronous=True)
        h = Web3.keccak(text=value).hex()

        with pytest.raises(BlockchainError, match="Cannot link hash to itself"):
            dag_hash_manager.add_outgoing_link(
                from_hash=h, to_hash=h, private_key=private_key_alice, synchronous=True
            )

    def test_add_outgoing_link_source_hash_not_active(self, dag_hash_manager, private_key_alice):
        a = f"src_inactive_a_{int(time.time())}"
        b = f"src_inactive_b_{int(time.time())}"
        dag_hash_manager.add_hash(value=a, private_key=private_key_alice, synchronous=True)
        dag_hash_manager.add_hash(value=b, private_key=private_key_alice, synchronous=True)

        ha = Web3.keccak(text=a).hex()
        hb = Web3.keccak(text=b).hex()

        dag_hash_manager.deprecate_hash(hashed_value=ha, private_key=private_key_alice, synchronous=True)

        with pytest.raises(BlockchainError, match="Source hash is not active"):
            dag_hash_manager.add_outgoing_link(
                from_hash=ha, to_hash=hb, private_key=private_key_alice, synchronous=True
            )

    def test_add_outgoing_link_target_hash_not_active(self, dag_hash_manager, private_key_alice):
        a = f"tgt_inactive_a_{int(time.time())}"
        b = f"tgt_inactive_b_{int(time.time())}"
        dag_hash_manager.add_hash(value=a, private_key=private_key_alice, synchronous=True)
        dag_hash_manager.add_hash(value=b, private_key=private_key_alice, synchronous=True)

        ha = Web3.keccak(text=a).hex()
        hb = Web3.keccak(text=b).hex()

        dag_hash_manager.deprecate_hash(hashed_value=hb, private_key=private_key_alice, synchronous=True)

        with pytest.raises(BlockchainError, match="Target hash is not active"):
            dag_hash_manager.add_outgoing_link(
                from_hash=ha, to_hash=hb, private_key=private_key_alice, synchronous=True
            )

    def test_add_outgoing_link_already_exists(self, dag_hash_manager, private_key_alice):
        a = f"link_exists_a_{int(time.time())}"
        b = f"link_exists_b_{int(time.time())}"
        dag_hash_manager.add_hash(value=a, private_key=private_key_alice, synchronous=True)
        dag_hash_manager.add_hash(value=b, private_key=private_key_alice, synchronous=True)

        ha = Web3.keccak(text=a).hex()
        hb = Web3.keccak(text=b).hex()

        dag_hash_manager.add_outgoing_link(from_hash=ha, to_hash=hb, private_key=private_key_alice, synchronous=True)

        with pytest.raises(BlockchainError, match="Link already exists"):
            dag_hash_manager.add_outgoing_link(
                from_hash=ha, to_hash=hb, private_key=private_key_alice, synchronous=True
            )

    def test_add_outgoing_link_would_create_cycle(self, dag_hash_manager, private_key_alice):

        a = f"cycle_a_{int(time.time())}"
        b = f"cycle_b_{int(time.time())}"
        c = f"cycle_c_{int(time.time())}"
        dag_hash_manager.add_hash(value=a, private_key=private_key_alice, synchronous=True)
        dag_hash_manager.add_hash(value=b, private_key=private_key_alice, synchronous=True)
        dag_hash_manager.add_hash(value=c, private_key=private_key_alice, synchronous=True)

        ha = Web3.keccak(text=a).hex()
        hb = Web3.keccak(text=b).hex()
        hc = Web3.keccak(text=c).hex()

        dag_hash_manager.add_outgoing_link(from_hash=ha, to_hash=hb, private_key=private_key_alice, synchronous=True)
        dag_hash_manager.add_outgoing_link(from_hash=hb, to_hash=hc, private_key=private_key_alice, synchronous=True)

        with pytest.raises(BlockchainError, match="Link would create a cycle"):
            dag_hash_manager.add_outgoing_link(
                from_hash=hc, to_hash=ha, private_key=private_key_alice, synchronous=True
            )

    def test_delete_outgoing_link_does_not_exist(self, dag_hash_manager, private_key_alice):
        a = f"no_link_a_{int(time.time())}"
        b = f"no_link_b_{int(time.time())}"
        dag_hash_manager.add_hash(value=a, private_key=private_key_alice, synchronous=True)
        dag_hash_manager.add_hash(value=b, private_key=private_key_alice, synchronous=True)

        ha = Web3.keccak(text=a).hex()
        hb = Web3.keccak(text=b).hex()

        with pytest.raises(BlockchainError, match="Link does not exist"):
            dag_hash_manager.delete_outgoing_link(
                from_hash=ha, to_hash=hb, private_key=private_key_alice, synchronous=True
            )
