from web3 import Web3
from eth_account import Account

class Web3Service:
    def __init__(self, rpc_url):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.wallet_address = None

    def connect_wallet(self, wallet_address):
        self.wallet_address = self.web3.to_checksum_address(wallet_address)

    def get_balance_eth(self):
        balance = self.web3.eth.get_balance(self.wallet_address)
        return self.web3.from_wei(balance, 'ether')

    def check_wallet_connection(self, private_key: str):
        try:
            if not self.web3.is_connected():
                return False, "Cannot connect to blockchain node"
                
            # Create account from private key
            account = Account.from_key(private_key)
    
            # Check address match
            if account.address != self.wallet_address:
                return False, "Private key does not match wallet address"
    
            return True, f"Connected successfully"
    
        except ValueError:
            return False, "Invalid private key or wallet address"
        except Exception as e:
            return False, str(e)
