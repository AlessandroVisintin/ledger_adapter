from typing import Dict
from web3 import Web3

from .contract import Contract
from .connection import Connection
from .models import BlockchainValue, BlockchainResponse, BlockchainError


class DagHashManager(Contract):
    def __init__(self,
                 node_connection: Connection,
                 contract_address: str,
                 contract_abi: Dict):
        super().__init__(
            http_provider=node_connection.get_provider(),
            contract_address=contract_address,
            contract_abi=contract_abi
        )
    
    def add_hash(self,
                 value: str,
                 private_key: str,
                 synchronous: bool = False) -> BlockchainResponse | BlockchainError:
        hashed_value = Web3.keccak(text=value)
        contract_function = self.contract.functions.addHash(hashed_value)
        return self.execute(contract_function, private_key, synchronous)
    
    def read_hash(self,
                  hashed_value: str) -> BlockchainValue | BlockchainError:
        hashed_value_bytes = Web3.to_bytes(hexstr=hashed_value)
        contract_function = self.contract.functions.readHash(hashed_value_bytes)
        return self.call(contract_function)
    
    def deprecate_hash(self,
                       hashed_value: str,
                       private_key: str,
                       synchronous: bool = False) -> BlockchainResponse | BlockchainError:
        hashed_value_bytes = Web3.to_bytes(hexstr=hashed_value)
        contract_function = self.contract.functions.deprecateHash(hashed_value_bytes)
        return self.execute(contract_function, private_key, synchronous)
    
    def delete_hash(self,
                    hashed_value: str,
                    private_key: str,
                    synchronous: bool = False) -> BlockchainResponse | BlockchainError:
        hashed_value_bytes = Web3.to_bytes(hexstr=hashed_value)
        contract_function = self.contract.functions.deleteHash(hashed_value_bytes)
        return self.execute(contract_function, private_key, synchronous)
    
    def add_outgoing_link(self,
                          from_hash: str,
                          to_hash: str,
                          private_key: str,
                          synchronous: bool = False) -> BlockchainResponse | BlockchainError:
        from_hash_bytes = Web3.to_bytes(hexstr=from_hash)
        to_hash_bytes = Web3.to_bytes(hexstr=to_hash)
        contract_function = self.contract.functions.addOutgoingLink(from_hash_bytes, to_hash_bytes)
        return self.execute(contract_function, private_key, synchronous)

    def read_outgoing_links(self,
                            hashed_value: str) -> BlockchainValue | BlockchainError:
        hashed_value_bytes = Web3.to_bytes(hexstr=hashed_value)
        contract_function = self.contract.functions.readOutgoingLinks(hashed_value_bytes)
        return self.call(contract_function)
    
    def delete_outgoing_link(self,
                             from_hash: str,
                             to_hash: str,
                             private_key: str,
                             synchronous: bool = False) -> BlockchainResponse | BlockchainError:
        from_hash_bytes = Web3.to_bytes(hexstr=from_hash)
        to_hash_bytes = Web3.to_bytes(hexstr=to_hash)
        contract_function = self.contract.functions.deleteOutgoingLink(from_hash_bytes, to_hash_bytes)
        return self.execute(contract_function, private_key, synchronous)
