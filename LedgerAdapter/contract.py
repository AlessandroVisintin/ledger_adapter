from abc import ABC
from eth_account import Account
from hexbytes import HexBytes
from typing import List, Dict, Union, Optional, Any
from web3 import Web3
from web3.contract.contract import ContractFunction
from web3.exceptions import Web3RPCError, ContractLogicError
from web3.middleware import ExtraDataToPOAMiddleware
from web3.providers import HTTPProvider
from web3.types import TxReceipt

from .models import (
    BlockchainError,
    BlockchainValue,
    BlockchainResponse,
    BlockDetails,
    EventData,
    EventDetails,
    TransactionDetails,
)
from .utils import (
    bytes_to_0xhex,
    hex0x_to_bytes,
    parse_error,
    parse_event_data,
)


class Contract(ABC):

    def __init__(self,
                 http_provider: HTTPProvider,
                 contract_address: str,
                 contract_abi: Dict
                 ):

        self.w3 = Web3(http_provider)
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        self.contract = self.w3.eth.contract(
            address=contract_address,
            abi=contract_abi
        )
    
    def wait_for_receipt(self,
                         tx_hash: str):
        try:
            return self._parse_receipt(
                self.w3.eth.wait_for_transaction_receipt(tx_hash)
            )
        except Web3RPCError as e:
            return parse_error(e)

    def _parse_receipt(self,
                       receipt: TxReceipt) -> BlockchainResponse:        
        return BlockchainResponse(
            status=str(receipt.status),
            block=BlockDetails(
                block_hash=bytes_to_0xhex(receipt.blockHash),
                block_number=str(receipt.blockNumber)
            ),
            transaction=TransactionDetails(
                transaction_hash=bytes_to_0xhex(receipt.transactionHash),
                from_address=str(receipt['from']),
                to_address=str(receipt['to']),
                gas_used=str(receipt.gasUsed)
            ),
            events=self._parse_events(receipt)
        )

    def _parse_events(self,
                      receipt: TxReceipt) -> List[EventDetails]:
        parsed_events = []
        for event_abi in [abi for abi in self.contract.abi if abi['type'] == 'event']:
            event_name = event_abi['name']
            event_processor = getattr(self.contract.events, event_name)
            logs = event_processor().process_receipt(receipt)
            for log in logs:
                event_data = EventDetails(
                    event_name=log.event,
                    event_results={
                        k: bytes_to_0xhex(v) if isinstance(v, (bytes, HexBytes)) else v
                        for k, v in dict(log.args).items()
                    }
                )
                parsed_events.append(event_data)
        return parsed_events

    def call(self,
             contract_function: ContractFunction) -> BlockchainValue | BlockchainError:
        try:
            return BlockchainValue(value=bytes_to_0xhex( contract_function.call() ))
        except Exception as e:
            raise parse_error(e)

    def execute(self, 
                contract_function: ContractFunction,
                private_key: str,
                synchronous: bool = False
                ) -> Union[BlockchainResponse, HexBytes, BlockchainError]:
        try:
            account = Account.from_key(private_key)
            nonce = self.w3.eth.get_transaction_count(account.address)
            tx_params = {
                'from': account.address,
                'chainId': self.w3.eth.chain_id,
                'gasPrice': 0,
                'nonce': nonce
            }
            gas_estimate = contract_function.estimate_gas(tx_params)
            tx_params['gas'] = int(gas_estimate * 1.2)
            tx = contract_function.build_transaction(tx_params)
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

            if synchronous:
                receipt = self.wait_for_receipt(tx_hash)
                return receipt
            
            return bytes_to_0xhex(tx_hash)
        except (Web3RPCError,ContractLogicError) as e:
            raise parse_error(e)

    def get_events(
        self,
        from_block: int = 0,
        to_block: Union[int, str] = 'latest',
        event_name: Optional[str] = None,
        argument_filters: Optional[Dict[str, Any]] = None
    ) -> List[EventData]:

        if argument_filters is not None and event_name is None:
            raise BlockchainError(
                message="argument_filters requires a specific event_name"
            )
        
        try:
            if event_name is not None:
                event_names_in_abi = {
                    entry['name']
                    for entry in self.contract.abi
                    if entry['type'] == 'event'
                }
                if event_name not in event_names_in_abi:
                    raise BlockchainError(
                        message=f"Event '{event_name}' not found in contract ABI"
                    )
                event_processor = getattr(self.contract.events, event_name)
                logs = list(event_processor.get_logs(
                    argument_filters=hex0x_to_bytes(argument_filters),
                    from_block=from_block,
                    to_block=to_block
                ))
            else:
                logs = []
                for abi_entry in self.contract.abi:
                    if abi_entry['type'] == 'event':
                        event_processor = getattr(self.contract.events, abi_entry['name'])
                        logs.extend(event_processor.get_logs(
                            from_block=from_block,
                            to_block=to_block
                        ))
                logs.sort(key=lambda log: (
                    log.blockNumber,
                    log.transactionIndex,
                    log.logIndex
                ))

        except BlockchainError:
            raise
        except Web3RPCError as e:
            raise parse_error(e)  
            
        return [parse_event_data(log) for log in logs]
