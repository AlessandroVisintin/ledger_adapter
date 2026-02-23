import time
import pytest

from web3 import Web3

from LedgerAdapter.models import BlockchainResponse, BlockchainValue, BlockchainError


class TestHashManager:

    def test_add_hash(self, hash_manager, private_key_alice):
        test_value = f"test_value_{int(time.time())}"
        response = hash_manager.add(value=test_value, private_key=private_key_alice, synchronous=True)

        assert isinstance(response, BlockchainResponse)
        assert response.status == '1'
        assert response.transaction.transaction_hash is not None

    def test_read_hash(self, hash_manager, private_key_alice):
        unique_val = f"read_test_{int(time.time())}"
        add_resp = hash_manager.add(value=unique_val, private_key=private_key_alice, synchronous=True)
        assert isinstance(add_resp, BlockchainResponse)
        
        hashed_key = Web3.keccak(text=unique_val).hex()
        result = hash_manager.read(hashed_value=hashed_key)
        assert isinstance(result, BlockchainValue)
        assert result.value is not None

    def test_deprecate_hash(self, hash_manager, private_key_alice):
        unique_val = f"deprecate_test_{int(time.time())}"
        hash_manager.add(value=unique_val, private_key=private_key_alice, synchronous=True)
        
        hashed_key = Web3.keccak(text=unique_val).hex()
        response = hash_manager.deprecate(hashed_value=hashed_key, private_key=private_key_alice, synchronous=True)

        assert isinstance(response, BlockchainResponse)
        assert response.status == '1'
        assert response.transaction.transaction_hash is not None

    def test_add_hash_already_exists(self, hash_manager, private_key_alice):
        test_value = f"duplicate_test_{int(time.time())}"
        hash_manager.add(value=test_value, private_key=private_key_alice, synchronous=True)
        
        with pytest.raises(BlockchainError, match="Hash already exists"):
            hash_manager.add(value=test_value, private_key=private_key_alice, synchronous=True)

    def test_read_hash_does_not_exist(self, hash_manager):
        non_existent_value = f"non_existent_{int(time.time())}"
        hashed_key = Web3.keccak(text=non_existent_value).hex()
        
        with pytest.raises(BlockchainError, match="Hash does not exist"):
            hash_manager.read(hashed_value=hashed_key)

    def test_deprecate_hash_does_not_exist(self, hash_manager, private_key_alice):
        non_existent_value = f"delete_missing_{int(time.time())}"
        hashed_key = Web3.keccak(text=non_existent_value).hex()
        
        with pytest.raises(BlockchainError, match="Hash does not exist"):
            hash_manager.deprecate(hashed_value=hashed_key, private_key=private_key_alice, synchronous=True)

    def test_deprecate_caller_not_owner(self, hash_manager, private_key_alice, private_key_bob):
        unique_val = f"owner_check_{int(time.time())}"
        hash_manager.add(value=unique_val, private_key=private_key_alice, synchronous=True)
        hashed_key = Web3.keccak(text=unique_val).hex()
        
        with pytest.raises(BlockchainError, match="Caller is not the owner"):
            hash_manager.deprecate(hashed_value=hashed_key, private_key=private_key_bob, synchronous=True)