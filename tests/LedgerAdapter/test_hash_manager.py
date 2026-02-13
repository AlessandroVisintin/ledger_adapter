import time
import pytest

from LedgerAdapter.models import BlockchainResponse, BlockchainValue, BlockchainError


class TestHashManager:

    def test_add_hash(self, hash_manager, private_key_alice):
        test_value = f"test_value_{int(time.time())}"
        response = hash_manager.add(
                                    value=test_value,
                                    private_key=private_key_alice,
                                    synchronous=True
                                )

        print(f"\nBlockchain Response: {response}")

        # assert isinstance(response, BlockchainResponse)
        # assert response.status == '1'
        # assert response.transaction.transaction_hash is not None

    # def test_read_hash(self, hash_manager):
    #     """
    #     Test reading a hash value from the blockchain.
    #     Assumes a value has been added previously.
    #     """
    #     # 1. Add a value first to ensure it exists
    #     unique_val = f"read_test_{int(time.time())}"
    #     add_resp = hash_manager.add(value=unique_val, private_key=TEST_PRIVATE_KEY)
    #     assert isinstance(add_resp, BlockchainResponse)
        
    #     # Wait for block confirmation if necessary (simulate mining delay)
    #     # time.sleep(1) 
        
    #     # 2. Compute the hash (simulating what the contract expects as key)
    #     # Note: HashManager.read takes the 'hashed_value' (hex string)
    #     from web3 import Web3
    #     hashed_key = Web3.keccak(text=unique_val).hex()
        
    #     # 3. Read the value
    #     result = hash_manager.read(hashed_value=hashed_key)
        
    #     assert isinstance(result, BlockchainValue)
    #     # Assert logic depends on what the contract actually returns for 'read'
    #     # Assuming it returns a boolean exists, or the value itself, or metadata.
    #     # Check that we didn't get an error.
    #     assert result.value is not None

    # def test_deprecate_hash(self, hash_manager):
    #     """
    #     Test deprecating a hash on the blockchain.
    #     """
    #     # 1. Add a value
    #     unique_val = f"deprecate_test_{int(time.time())}"
    #     hash_manager.add(value=unique_val, private_key=TEST_PRIVATE_KEY)
        
    #     # 2. Deprecate it
    #     hashed_key = ""
    #     # We need the keccak hash of the value to call deprecate
    #     from web3 import Web3
    #     hashed_key = Web3.keccak(text=unique_val).hex()
        
    #     response = hash_manager.deprecate(hashed_value=hashed_key, private_key=TEST_PRIVATE_KEY)
        
    #     assert isinstance(response, BlockchainResponse)
    #     assert response.status == '1'

    # def test_invalid_operations(self, hash_manager):
    #     """
    #     Test error handling (e.g., calling with invalid key).
    #     """
    #     # Using a clearly invalid private key
    #     invalid_key = "0x0000000000000000000000000000000000000000000000000000000000000001"
    #     test_value = "fail_test"
        
    #     response = hash_manager.add(value=test_value, private_key=invalid_key)
        
    #     # Should return a BlockchainError or a Response with failure status depending on implementation
    #     # The code in Contract.execute catches exceptions and returns BlockchainError or parses it.
    #     if isinstance(response, BlockchainError):
    #         assert response.message is not None
    #     else:
    #         # If it somehow returns a response object for a failed tx (unlikely for invalid key signing)
    #         assert response.status == '0' or response.transaction is None
