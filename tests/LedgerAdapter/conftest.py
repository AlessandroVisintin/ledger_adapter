import json
import os
import pytest

from dotenv import load_dotenv
from pathlib import Path

from LedgerAdapter.connection import Connection
from LedgerAdapter.hash_manager import HashManager
from LedgerAdapter.dag_hash_manager import DagHashManager
from LedgerAdapter.utils import wait_for_liveness


load_dotenv(dotenv_path='/app/.env')


### Keys
@pytest.fixture
def private_key_alice():
    return "0x3f9d4328d47d5aa8b84c4716679a78fc21eab62be253b99315e4fa924d07559f"


@pytest.fixture
def public_key_alice():
    return "0xe4a2e908bf0e1ca4305c1fe6c5f84eba66a98863049a841689b3e2f7e280b110a60ba73122e8051ea61a150c3c7e72b07dcb965f2867981a772e9fb0fc1bd5ee"


@pytest.fixture
def private_key_bob():
    return "0x26e4865f9787ec01bf0f586ac704bd7395262279a119cbadcf14e6336ec8c8a0"


@pytest.fixture
def public_key_bob():
    return "0x36ce7c84bd0015ea1073cd5f7843466156728fa84292e2f48d7ca6e445f46a9b5eaf12aebfef8ebb8913c05d4edd8ea57b26a784ddee42a51646a5cf1e0e2d67"


@pytest.fixture
def test_address():
    return "0xe4a2E908bf0E1ca4305C1fE6C5F84EBA66a98863"


## Nodes
@pytest.fixture
def node_url():
    url = os.getenv("NODE_URL")
    assert url is not None, "NODE_URL env variable is not set"
    return url


@pytest.fixture
def ca_cert_path():
    path = Path("/app/ca-certificate.pem")
    assert path.exists(), f"CA certificate not found: {path}"
    return str(path)


@pytest.fixture
def node_connection(node_url):
    connection = Connection(node_url=node_url)
    wait_for_liveness(connection)
    return connection


@pytest.fixture
def root_connection(node_url):
    connection = Connection(node_url=node_url)
    connection.with_authentication(
        username=os.getenv("USERNAME_ROOT"),
        password=os.getenv("PASSWORD_ROOT")
        )
    wait_for_liveness(connection)
    return connection


@pytest.fixture
def eth_connection(node_url):
    connection = Connection(node_url=node_url)
    connection.with_authentication(
        username=os.getenv("USERNAME_ETH"),
        password=os.getenv("PASSWORD_ETH")
        )
    wait_for_liveness(connection)
    return connection

@pytest.fixture
def public_connection(node_url):
    connection = Connection(node_url=node_url)
    connection.with_authentication(
        username=os.getenv("USERNAME_PUBLIC"),
        password=os.getenv("PASSWORD_PUBLIC")
        )
    wait_for_liveness(connection)
    return connection

@pytest.fixture
def tls_connection(node_url, ca_cert_path):
    connection = Connection(node_url=node_url).with_tls(ca_cert_path=ca_cert_path)
    wait_for_liveness(connection)
    return connection

### Contracts
@pytest.fixture
def genesis_contracts():
    with open('/app/genesis-contracts.json', 'r') as f:
        return json.load(f)


@pytest.fixture
def hash_manager_address(genesis_contracts):
    return genesis_contracts["HashManager"]["address"]


@pytest.fixture
def hash_manager_abi(genesis_contracts):
    return genesis_contracts["HashManager"]["abi"]


@pytest.fixture
def hash_manager(node_connection, hash_manager_address, hash_manager_abi):
    return HashManager(
        node_connection=node_connection,
        contract_address=hash_manager_address,
        contract_abi=hash_manager_abi
    )


@pytest.fixture
def tls_hash_manager(tls_connection, hash_manager_address, hash_manager_abi):
    return HashManager(
        node_connection=tls_connection,
        contract_address=hash_manager_address,
        contract_abi=hash_manager_abi
    )


@pytest.fixture
def root_hash_manager(root_connection, hash_manager_address, hash_manager_abi):
    return HashManager(
        node_connection=root_connection,
        contract_address=hash_manager_address,
        contract_abi=hash_manager_abi
    )

@pytest.fixture
def eth_hash_manager(eth_connection, hash_manager_address, hash_manager_abi):
    return HashManager(
        node_connection=eth_connection,
        contract_address=hash_manager_address,
        contract_abi=hash_manager_abi
    )

@pytest.fixture
def public_hash_manager(public_connection, hash_manager_address, hash_manager_abi):
    return HashManager(
        node_connection=public_connection,
        contract_address=hash_manager_address,
        contract_abi=hash_manager_abi
    )


@pytest.fixture
def dag_hash_manager_address(genesis_contracts):
    return genesis_contracts["DagHashManager"]["address"]


@pytest.fixture
def dag_hash_manager_abi(genesis_contracts):
    return genesis_contracts["DagHashManager"]["abi"]


@pytest.fixture
def dag_hash_manager(node_connection, dag_hash_manager_address, dag_hash_manager_abi):
    return DagHashManager(
        node_connection=node_connection,
        contract_address=dag_hash_manager_address,
        contract_abi=dag_hash_manager_abi
    )
