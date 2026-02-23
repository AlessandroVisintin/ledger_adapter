import os
import pytest
import time

from web3 import Web3
from LedgerAdapter.connection import Connection
from LedgerAdapter.hash_manager import HashManager
from LedgerAdapter.models import BlockchainResponse, BlockchainValue, BlockchainError


class TestRescaleNodeAuthentication:

    def test_invalid_username(self, node_url):
        connection = Connection(node_url=node_url)
        
        with pytest.raises((ConnectionError, Exception)) as exc_info:
            connection.with_authentication(
                username="nonexistent_user_xyz",
                password="any_password"
            )
        
        error_msg = str(exc_info.value).lower()
        assert any(keyword in error_msg for keyword in 
                   ["authentication", "failed", "invalid", "user", "not found"])

    def test_invalid_credentials(self, node_url):
        connection = Connection(node_url=node_url)
        
        with pytest.raises((ConnectionError, Exception)) as exc_info:
            connection.with_authentication(
                username=os.getenv("USERNAME_ROOT"),
                password="wrong_password_123"
            )
        
        error_msg = str(exc_info.value).lower()
        assert any(keyword in error_msg for keyword in 
                   ["authentication", "failed", "invalid", "unauthorized"])

    def test_missing_authentication_token(self, node_url, test_address):
        connection = Connection(node_url=node_url)
        provider = connection.get_provider()
        w3 = Web3(provider)
        
        with pytest.raises((BlockchainError, Exception)) as exc_info:
            w3.eth.get_balance(test_address)
        
        error_msg = str(exc_info.value).lower()
        assert any(keyword in error_msg for keyword in 
                   ["authentication", "unauthorized", "token", "forbidden"])

    def test_root_wildcard_net_methods(self, root_connection):
        provider = root_connection.get_provider()
        w3 = Web3(provider)
        net_version = w3.net.version
        assert net_version is not None

    def test_root_wildcard_admin_methods(self, root_connection):
        provider = root_connection.get_provider()
        w3 = Web3(provider)
        try:
            result = w3.manager.request_blocking("admin_peers", [])
            assert result is not None or result == []
        except BlockchainError as e:
            assert "permission denied" not in str(e).lower()
            assert "unauthorized" not in str(e).lower()

    def test_eth_namespace_boundary_net_version(self, eth_connection):
        """Verify eth user is blocked from net_version"""
        provider = eth_connection.get_provider()
        w3 = Web3(provider)
        
        with pytest.raises((BlockchainError, Exception)) as exc_info:
            _ = w3.net.version
        
        error_msg = str(exc_info.value).lower()
        assert any(keyword in error_msg for keyword in 
                   ["permission", "unauthorized", "forbidden", "denied"])

    def test_eth_namespace_boundary_admin_methods(self, eth_connection):
        provider = eth_connection.get_provider()
        w3 = Web3(provider)
        
        with pytest.raises((BlockchainError, Exception)) as exc_info:
            w3.manager.request_blocking("admin_peers", [])
        
        error_msg = str(exc_info.value).lower()
        assert any(keyword in error_msg for keyword in 
                   ["permission", "unauthorized", "forbidden", "denied"])

    def test_eth_can_call_eth_getBalance(self, eth_connection, test_address):
        provider = eth_connection.get_provider()
        w3 = Web3(provider)
        balance = w3.eth.get_balance(test_address)
        assert balance is not None
        assert isinstance(balance, int)

    def test_public_blocked_from_eth_getBalance(self, public_connection, test_address):
        provider = public_connection.get_provider()
        w3 = Web3(provider)

        with pytest.raises((BlockchainError, Exception)) as exc_info:
            w3.eth.get_balance(test_address)
        
        error_msg = str(exc_info.value).lower()
        assert any(keyword in error_msg for keyword in 
                   ["permission", "unauthorized", "forbidden", "denied"])

    def test_root_can_add_hash(self, root_hash_manager, private_key_alice):
        test_value = f"root_add_test_{int(time.time())}"
        response = root_hash_manager.add(
            value=test_value,
            private_key=private_key_alice,
            synchronous=True
        )
        
        assert isinstance(response, BlockchainResponse)
        assert response.status == "1"
        assert response.transaction.transaction_hash is not None

    def test_root_can_read_hash(self, root_hash_manager, private_key_alice):
        test_value = f"root_read_test_{int(time.time())}"
        add_response = root_hash_manager.add(
            value=test_value,
            private_key=private_key_alice,
            synchronous=True
        )
    
        assert isinstance(add_response, BlockchainResponse)
        
        hashed_key = Web3.keccak(text=test_value).hex()
        result = root_hash_manager.read(hashed_value=hashed_key)
    
        assert isinstance(result, BlockchainValue)
        assert result.value is not None

    def test_eth_can_add_hash(self, eth_hash_manager, private_key_alice):
        test_value = f"eth_add_test_{int(time.time())}"
        response = eth_hash_manager.add(
            value=test_value,
            private_key=private_key_alice,
            synchronous=True
        )
        
        assert isinstance(response, BlockchainResponse)
        assert response.status == "1"
        assert response.transaction.transaction_hash is not None
    
    def test_eth_can_read_hash(self, eth_hash_manager, private_key_alice):
        test_value = f"eth_read_test_{int(time.time())}"
        
        add_response = eth_hash_manager.add(
            value=test_value,
            private_key=private_key_alice,
            synchronous=True
        )
        assert isinstance(add_response, BlockchainResponse)
        
        hashed_key = Web3.keccak(text=test_value).hex()
        result = eth_hash_manager.read(hashed_value=hashed_key)
        
        assert isinstance(result, BlockchainValue)
        assert result.value is not None
    
    def test_public_can_read_hash(self, public_hash_manager, root_hash_manager, private_key_alice):
        test_value = f"public_read_test_{int(time.time())}"
        
        add_response = root_hash_manager.add(
            value=test_value,
            private_key=private_key_alice,
            synchronous=True
        )
        assert isinstance(add_response, BlockchainResponse)
        
        hashed_key = Web3.keccak(text=test_value).hex()
        result = public_hash_manager.read(hashed_value=hashed_key)
        
        assert isinstance(result, BlockchainValue)
        assert result.value is not None
    
    def test_public_cannot_add_hash(self, public_hash_manager, private_key_alice):
        test_value = f"public_add_fail_{int(time.time())}"
        
        with pytest.raises((BlockchainError, Exception)):
            public_hash_manager.add(
                value=test_value,
                private_key=private_key_alice,
                synchronous=True
            )