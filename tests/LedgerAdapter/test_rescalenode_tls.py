import os
import pytest
import time

from web3 import Web3

from LedgerAdapter.connection import Connection
from LedgerAdapter.models import BlockchainResponse, BlockchainValue
from LedgerAdapter.utils import wait_for_liveness


class TestRescaleNodeTLS:

    def test_with_tls_raises_on_http_url(self):
        connection = Connection(node_url="http://172.29.0.2:8545")
        with pytest.raises(ValueError, match="Cannot enable TLS on non-https url"):
            connection.with_tls()

    def test_with_tls_returns_self(self):
        connection = Connection(node_url="https://127.0.0.1:8545")
        result = connection.with_tls()
        assert result is connection

    def test_with_tls_session_verify_set_to_ca_path(self, ca_cert_path):
        connection = Connection(node_url="https://127.0.0.1:8545")
        connection.with_tls(ca_cert_path=ca_cert_path)
        assert connection.session.verify == ca_cert_path

    def test_with_tls_session_verify_true_when_no_ca_path(self):
        connection = Connection(node_url="https://127.0.0.1:8545")
        connection.with_tls()
        assert connection.session.verify is True

    def test_with_tls_stores_ca_cert_path_attribute(self, ca_cert_path):
        connection = Connection(node_url="https://127.0.0.1:8545")
        connection.with_tls(ca_cert_path=ca_cert_path)
        assert connection.ca_cert_path == ca_cert_path

    def test_with_tls_ca_cert_path_none_by_default(self):
        connection = Connection(node_url="https://127.0.0.1:8545")
        connection.with_tls()
        assert connection.ca_cert_path is None 

    def test_tls_connection_is_live(self, node_url, ca_cert_path):
        connection = Connection(node_url=node_url).with_tls(ca_cert_path=ca_cert_path)
        wait_for_liveness(connection)

    def test_tls_without_ca_cert_fails_ssl(self, node_url):
        connection = Connection(node_url=node_url).with_tls()
        with pytest.raises(Exception) as exc_info:
            wait_for_liveness(connection)
        error_msg = str(exc_info.value).lower()
        assert any(keyword in error_msg for keyword in
                   ["ssl", "certificate", "verify", "tls", "not live"])

    def test_contract_call_works_over_tls(self, tls_hash_manager, private_key_alice):

            test_value = f"tls_contract_test_{int(time.time())}"
            hashed_key = Web3.keccak(text=test_value).hex()

            add_response = tls_hash_manager.add(
                value=test_value,
                private_key=private_key_alice,
                synchronous=True
                )
            assert isinstance(add_response, BlockchainResponse)
            assert add_response.status == '1'
            assert add_response.transaction.transaction_hash is not None

            result = tls_hash_manager.read(hashed_value=hashed_key)
            assert isinstance(result, BlockchainValue)
            assert result.value is not None