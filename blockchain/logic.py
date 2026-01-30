from web3 import Web3
from eth_account import Account
from blockchain.config import RPC_URL, CONTRACT_ADDRESS, CONTRACT_ABI

class Web3Service:
    def __init__(self, rpc_url=RPC_URL):
     #Web3 connection
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.wallet_address = None
        self.key = None
        self.player = None
        self.room = None

        # Contract setup imported from config
        self.contract_address = CONTRACT_ADDRESS
        self.contract_abi = CONTRACT_ABI

        self.contract = self.web3.eth.contract(
            address=self.contract_address,
            abi=self.contract_abi
        )
        
    # -----------------------------
    # Wallet functions
    # -----------------------------
    def connect_wallet(self, wallet_address: str):
        try:
            self.wallet_address = self.web3.to_checksum_address(wallet_address)
            return ""
        except:
            return "Problem with the wallet address"

    def get_balance_eth(self):
        balance = self.web3.eth.get_balance(self.wallet_address)
        return self.web3.from_wei(balance, "ether")

    def check_wallet_connection(self, private_key: str):
        try:
            if not self.web3.is_connected():
                return False, "Cannot connect to blockchain node"
                
            # Create account from private key
            account = Account.from_key(private_key)
    
            # Check address match
            if account.address != self.wallet_address:
                return False, "Private key does not match wallet address"
                
            self.key = private_key
            return True, f"Connected successfully"
    
        except ValueError:
            return False, "Invalid private key or wallet address"
        except Exception as e:
            return False, str(e)
    # -----------------------------
    # Player / Room functions
    # -----------------------------
    def set_player(self, player: int):
        self.player = player
    # -----------------------------
    # Contract interaction examples
    # -----------------------------
    def create_room(self):
        if self.wallet_address is None:
            return False, "Wallet not connected"
    
        try:
            nonce = self.web3.eth.get_transaction_count(self.wallet_address)
            tx = self.contract.functions.createRoom(111).build_transaction({
                "from": self.wallet_address,
                "nonce": nonce,
                "gas": 200000,
                "gasPrice": self.web3.to_wei("20", "gwei")
            })
    
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.key )
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
    
            # Extract the event from the receipt
            events = self.contract.events.RoomCreated().process_receipt(receipt)
            if events:
                room_number = events[0]["args"]["roomNumber"]
                return True, f"Room created! Number: {room_number}, Tx hash: {tx_hash.hex()}"
            else:
                return False, f"Room created but no event found. Tx hash: {tx_hash.hex()}"
    
        except Exception as e:
            return False, str(e)
        


