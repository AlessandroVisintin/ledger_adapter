import ast
import time

from hexbytes import HexBytes
from requests import Session
from typing import Optional
from web3.providers import HTTPProvider

from .models import (
    BlockchainError,
)


def to_0xhex(value):
    if isinstance(value, HexBytes):
        return '0x' + value.hex()
    if isinstance(value, bytes):
        return '0x' + value.hex()
    if isinstance(value, str) and not value.startswith('0x'):
        return '0x' + value
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


def wait_for_liveness(provider: HTTPProvider, timeout: int = 30, poll_interval: float = 1.0) -> None:
    node_url = provider.endpoint_uri

    session: Optional[Session] = getattr(provider, 'session', None) or getattr(provider, '_request_session', None)
    if session is None:
        session = Session()
    
    request_kwargs = getattr(provider, 'request_kwargs', {}) or {}
    request_timeout = request_kwargs.get('timeout')

    liveness_url = f"{node_url.rstrip('/')}/liveness"
    deadline = time.monotonic() + timeout
    last_error: Optional[Exception] = None

    while time.monotonic() < deadline:
        try:
            get_kwargs = {}
            if request_timeout is not None:
                get_kwargs['timeout'] = request_timeout

            resp = session.get(liveness_url, **get_kwargs)
            if 200 <= resp.status_code < 300:
                return
        except Exception as e:
            last_error = e
        
        time.sleep(poll_interval)
    
    raise ConnectionError(
        f"Node at {node_url} not live after {timeout}s (GET {liveness_url}): : {last_error}"
    )

# def parse_event_data(resp) -> EventData:
#     return EventData(
#         address=str(resp.address),
#         block_hash=to_0xhex(resp.blockHash),
#         block_number=str(resp.blockNumber),
#         event_name=resp.event,
#         event_args=dict(resp.args),
#         transaction_hash=to_0xhex(resp.transactionHash) 
#     )