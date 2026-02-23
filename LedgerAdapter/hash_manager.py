from typing import Dict
from web3 import Web3

from .contract import Contract
from .connection import Connection
from .models import BlockchainValue, BlockchainResponse, BlockchainError


class HashManager(Contract):
    
    def __init__(self,
                 node_connection: Connection,
                 contract_address: str,
                 contract_abi: Dict
                 ):
        super().__init__(
            http_provider=node_connection.get_provider(),
            contract_address=contract_address,
            contract_abi=contract_abi
        )
    
    def add(self, 
            value: str,
            private_key: str,
            synchronous: bool = False) -> BlockchainResponse | BlockchainError:
        hashed_value = Web3.keccak(text=value)
        contract_function = self.contract.functions.add(hashed_value)
        return self.execute(contract_function, private_key, synchronous)

    def read(self,
             hashed_value: str) -> BlockchainValue | BlockchainError:
        hashed_value_bytes = Web3.to_bytes(hexstr=hashed_value)
        contract_function = self.contract.functions.read(hashed_value_bytes)
        return self.call(contract_function)
    
    def deprecate(self,
                  hashed_value: str,
                  private_key: str,
                  synchronous: bool = False) -> BlockchainResponse | BlockchainError:
        hashed_value_bytes = Web3.to_bytes(hexstr=hashed_value)
        contract_function = self.contract.functions.deprecate(hashed_value_bytes)
        return self.execute(contract_function, private_key, synchronous)
