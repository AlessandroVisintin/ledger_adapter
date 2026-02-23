from dataclasses import dataclass
from typing import Any


@dataclass
class BlockchainValue:
    value: Any

@dataclass
class BlockDetails:
    block_hash: str
    block_number: str

@dataclass
class TransactionDetails:
    transaction_hash: str
    from_address: str
    to_address: str
    gas_used: str

@dataclass
class EventDetails:
    event_name: str
    event_results: list

@dataclass
class BlockchainResponse:
    status: str
    block: BlockDetails
    transaction: TransactionDetails
    events: list[EventDetails]

@dataclass
class BlockchainError(Exception):
    message: str
    status: int=0

    def __str__(self):
        return self.message

@dataclass
class EventData:
    address: str
    block_hash: str
    block_number: str
    event_name: str
    event_args: list
    transaction_hash: str
