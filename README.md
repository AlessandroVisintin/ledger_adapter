# LedgerAdapter

LedgerAdapter is a Python package that talks to two Ethereum-style smart contracts—`HashManager` and `DagHashManager`—through a JSON-RPC node URL, so you can register document hashes, manage their lifecycle, and (optionally) link them in a directed acyclic graph (DAG).
It is designed to run against a Besu-based “RescaleNode” container via Docker Compose (see `docker/docker-compose.test.yml`) and includes runnable examples plus a pytest suite.

## Key features

- Canonicalizes JSON (stable key ordering and formatting) before hashing, so equivalent JSON produces the same hash.
- `HashManager` client: add, read, and deprecate hashes via the on-chain contract methods.
- `DagHashManager` client: add/read/deprecate/delete hashes plus create/delete/read outgoing links between hashes (cycle prevention is enforced by the contract).
- Query on-chain events over block ranges, with optional event-name filtering and argument filters.
- Supports node liveness checks (`/liveness`), optional RPC authentication (`/login` bearer token), and TLS (HTTPS with CA verification).
- Docker-based test runner and example scripts under `examples/`.

## What you need

- Python (the Docker test image uses `python:3.12-slim`).
- Docker + Docker Compose (used by `docker/docker-compose.test.yml` and the scripts in `sh/`).
- A running RescaleNode/Besu image that exposes JSON-RPC and a `/liveness` endpoint (the adapter waits for `GET {NODE_URL}/liveness`).
- A `genesis-contracts.json` file containing contract addresses and ABIs for `HashManager` and `DagHashManager` (examples and tests read `/app/genesis-contracts.json`).

Related repositories (useful context): LedgerInfrastructure is a Docker toolkit for building/testing Besu setups with optional JSON-RPC auth and TLS, and it also generates a `genesis-contracts.json` registry during its “genesis contracts” steps.
SmartContractsDev contains Solidity implementations and tests for `HashManager` and `DagHashManager` using Foundry in Docker.

## Quick start

### Install

1. Clone this repository and ensure Docker is running (the quickest path uses the Docker runner in `docker/docker-compose.test.yml`).
2. Bootstrap local config by copying the root `.env.docker.example` to `.env.docker` (the scripts expect `.env.docker` at the repo root).

```sh
cp .env.docker.example .env.docker
```

### Configure

Edit `.env.docker` so the scripts and Compose file can run.
At minimum you will need values for the environment variables consumed by `docker/docker-compose.test.yml` and `sh/*.sh` (examples below).

- `MODULE_ROOT_FLD`: absolute path to this repo on your machine (mounted into the `tester` container).
- `COMPOSE_TEST_FILE`: path to `docker/docker-compose.test.yml` (used by `sh/hash-manager-run.sh`, `sh/dag-hash-manager-run.sh`, `sh/events-run.sh`).
- `RESCALE_NODE_IMAGE`: Docker image for the node services (`rescale-onlykey`, `rescale-auth`, `rescale-tls`) in `docker/docker-compose.test.yml`.
- `BESU_NODE_IP`, `BESU_NODE_PORT`: used by scripts to export `NODE_URL="http://$BESU_NODE_IP:$BESU_NODE_PORT"`.
- `GENESIS_CONTRACTS_PATH`: host path to your `genesis-contracts.json` (mounted to `/app/genesis-contracts.json`).
- `CA_CERTIFICATE_PATH`: host path to a CA cert (mounted to `/app/ca-certificate.pem`, used by TLS tests).
- Auth users (used by tests): `USERNAME_ROOT`, `PASSWORD_ROOT`, `USERNAME_ETH`, `PASSWORD_ETH`, `USERNAME_PUBLIC`, `PASSWORD_PUBLIC`.

### Run

Run one of the provided Docker-backed example scripts:

```sh
sh sh/hash-manager-run.sh
sh sh/dag-hash-manager-run.sh
sh sh/events-run.sh
```  
These scripts start the node service `rescale-onlykey`, run the Python example inside the `tester` container, then tear down the Compose stack.

## How to use it

### Typical flow

1. Load `HashManager` address + ABI from `genesis-contracts.json`.
2. Create a `Connection(node_url=NODE_URL)` and wait for liveness with `wait_for_liveness(connection)`.
3. Create `HashManager(node_connection=connection, contract_address=..., contract_abi=...)` and call `add()`, `read()`, and `deprecate()`.

Minimal example (based on `examples/hash_manager.py`):

```python
import json
import os

from LedgerAdapter.connection import Connection
from LedgerAdapter.hash_manager import HashManager
from LedgerAdapter.utils import canonicalize_json, wait_for_liveness

NODE_URL = os.getenv("NODE_URL")  # set by sh/*.sh or your environment

with open("/app/genesis-contracts.json", "r") as f:
    genesis = json.load(f)

connection = Connection(node_url=NODE_URL)
wait_for_liveness(connection)

hm = HashManager(
    node_connection=connection,
    contract_address=genesis["HashManager"]["address"],
    contract_abi=genesis["HashManager"]["abi"],
)

value = canonicalize_json({"id": "example", "status": "active"})
receipt = hm.add(value=value, private_key="0x<your-private-key>", synchronous=True)
```

`DagHashManager` is used similarly, but it also exposes outgoing-link operations `add_outgoing_link()` and `read_outgoing_links()` (see `examples/dag_hash_manager.py` and `LedgerAdapter/dag_hash_manager.py`).

### Getting events

Use `get_events(from_block=..., to_block=..., event_name=..., argument_filters=...)` on any manager.
If you pass `argument_filters`, you must also pass a specific `event_name` or the adapter raises `BlockchainError(message="argument_filters requires a specific event_name")`.

## Configuration

### Environment variables

These variables are read by Docker Compose (`docker/docker-compose.test.yml`) and/or the helper scripts in `sh/`.

| Name | What it does |
|---|---|
| `MODULE_ROOT_FLD` | Host path mounted into the `tester` container at `/app/module` so the code can be installed editable (`pip install -e /app/module`).  |
| `COMPOSE_TEST_FILE` | Path used by the scripts when running `docker compose -f "$COMPOSE_TEST_FILE" ...`.  |
| `COMPOSE_BUILD_FILE` | Path used by `sh/tests-build.sh` (`docker compose -f "$COMPOSE_BUILD_FILE" build`).  |
| `RESCALE_NODE_IMAGE` | Docker image used for the node services `rescale-onlykey`, `rescale-auth`, and `rescale-tls`.  |
| `BESU_NODE_IP` / `BESU_NODE_PORT` | Used by scripts to set `NODE_URL` and by Compose to pin the node container IP on `adapter-net`.  |
| `NODE_URL` | JSON-RPC base URL consumed by the Python code (exported by scripts like `sh/hash-manager-run.sh`).  |
| `P2P_DISCOVERY` | Passed into the node container environment (`P2P_DISCOVERY=${BESU_NODE_IP}`) in `docker/docker-compose.test.yml`.  |
| `GENESIS_CONTRACTS_PATH` | Host path mounted to `/app/genesis-contracts.json` (examples/tests read this file).  |
| `CA_CERTIFICATE_PATH` | Host path mounted to `/app/ca-certificate.pem` (TLS tests expect this file).  |
| `TEST_FILE` | The pytest file name to run inside the `tester` container (`pytest ... /tests/LedgerAdapter/$TEST_FILE`).  |
| `USERNAME_ROOT`, `PASSWORD_ROOT` | Credentials used by tests with `Connection.with_authentication()`.  |
| `USERNAME_ETH`, `PASSWORD_ETH` | Credentials used by tests with `Connection.with_authentication()`.  |
| `USERNAME_PUBLIC`, `PASSWORD_PUBLIC` | Credentials used by tests with `Connection.with_authentication()`.  |

### `genesis-contracts.json` format

The Python examples and tests expect a JSON file at `/app/genesis-contracts.json` whose top-level keys include `HashManager` and `DagHashManager`, each with an `address` and an `abi`.
Here is an example structure (values are placeholders):

```json
{
  "HashManager": {
    "address": "0x0123456789abcdef0123456789abcdef01234567",
    "abi": ["..."]
  },
  "DagHashManager": {
    "address": "0x89abcdef0123456789abcdef0123456789abcdef",
    "abi": ["..."]
  }
}
```

The ABI entries above are illustrative; in practice you should use the full ABI arrays for both contracts, because LedgerAdapter passes `contract_abi` directly into `web3.eth.contract(address=..., abi=...)`.
Users are expected to generate the real `genesis-contracts.json` using the **LedgerInfrastructure** repository’s “genesis contracts registry” step, which writes a `genesis-contracts.json` file as part of its artifact generation flow.


## Project structure

- `LedgerAdapter/`: the Python package (connection/auth/TLS, contract wrapper, managers, models, utils).
- `examples/`: runnable scripts that demonstrate `HashManager`, `DagHashManager`, and event retrieval.
- `tests/`: pytest suite covering canonicalization, hash manager, DAG manager, event retrieval, authentication, and TLS behaviors.
- `docker/`: Docker Compose file used to run tests and examples against a node container.
- `sh/`: helper scripts to run examples and to build/run tests via Docker Compose.

## Development

### Install dev deps

This is a standard setuptools package (`setup.py`), so you can install it in editable mode locally if you prefer not to use Docker.
Runtime/test dependencies are pinned in `setup.py`.

### Tests

- Docker-based: `sh/tests-build.sh` builds the `tester` image, and `sh/tests-run.sh` runs pytest in the container using `docker/docker-compose.test.yml`.
- Test files live under `tests/LedgerAdapter/`.

## License

MIT License.
See `LICENSE`.
