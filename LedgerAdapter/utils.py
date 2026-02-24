import ast
import jcs
import json
import time

from dataclasses import asdict
from hexbytes import HexBytes
from typing import Any, Optional

from .models import BlockchainError, EventData
from .connection import Connection


def bytes_to_0xhex(value):
    if isinstance(value, dict):
        return {bytes_to_0xhex(k): bytes_to_0xhex(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        converted = [bytes_to_0xhex(v) for v in value]
        return type(value)(converted)
    if isinstance(value, (HexBytes, bytes)):
        return '0x' + value.hex()
    return value


def hex0x_to_bytes(value):
    if isinstance(value, dict):
        return {hex0x_to_bytes(k): hex0x_to_bytes(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        converted = [hex0x_to_bytes(v) for v in value]
        return type(value)(converted)
    if isinstance(value, str) and value.startswith('0x'):
        return bytes.fromhex(value[2:])
    return value



def parse_error(error: Exception) -> BlockchainError:
    try:
        error_details = error.args[0]
        if isinstance(error_details, str):
            return BlockchainError(message=error_details, status=0)
        if isinstance(error_details, tuple) and len(error_details) > 0:
            return BlockchainError(message=str(error_details[0]), status=0)

        error_dict = ast.literal_eval(str(error_details))
        if isinstance(error_dict, dict):
            message = error_dict.get('message', str(error))
            return BlockchainError(message=message, status=0)
        
        return BlockchainError(message=str(error_details), status=0)
    except (ValueError, SyntaxError, IndexError):
        return BlockchainError(message=str(error), status=0)


def wait_for_liveness(
        connection: Connection,
        timeout: int = 30,
        poll_interval: float = 1.0
        ) -> None:
    node_url = connection.node_url
    session = connection.session

    liveness_url = f"{node_url.rstrip('/')}/liveness"
    deadline = time.monotonic() + timeout
    last_error: Optional[Exception] = None

    while time.monotonic() < deadline:
        try:
            resp = session.get(liveness_url)
            if 200 <= resp.status_code < 300:
                return
        except Exception as e:
            last_error = e
        time.sleep(poll_interval)

    raise ConnectionError(
        f"Node at {node_url} not live after {timeout}s. "
        f"GET {liveness_url}: {last_error}"
    )

def parse_event_data(log) -> EventData:
    return EventData(
        address=str(log.address),
        block_hash=bytes_to_0xhex(log.blockHash),
        block_number=str(log.blockNumber),
        event_name=log.event,
        event_args={
            k: bytes_to_0xhex(v) if isinstance(v, (bytes, HexBytes)) else v
            for k, v in dict(log.args).items()
        },
        transaction_hash=bytes_to_0xhex(log.transactionHash),
        log_index=str(log.logIndex)
    )

def canonicalize_json(json_data: Any) -> str:
    return jcs.canonicalize(json_data).decode('utf-8')

def pretty(obj) -> str:
    return json.dumps(asdict(obj), indent=2)