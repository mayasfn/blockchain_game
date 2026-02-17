from web3 import Web3
from eth_account import Account
from blockchain.config import RPC_URL, CONTRACT_ADDRESS, CONTRACT_ABI
from eth_abi import encode
from eth_utils import keccak

ROOM_GUESSES_INDEX = 4
ROOM_FEEDBACKS_INDEX = 5
ENTRY_FREE_INDEX = 7

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
        self.room_creation_block = None


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
    def create_room(self, secret_number: int, number_rounds: int = 3, entry_fee_eth: float = 1.0):
        if self.wallet_address is None or self.key is None:
            return False, "Wallet not connected"
        
        try:
            #  Generate the hash (Matches Solidity getHash)
            # Use abi.encodePacked equivalent: encode then hash
            secret_hash = keccak(encode(['uint256'], [secret_number]))

            ## convert eth to wei 
            value_in_wei = self.web3.to_wei(entry_fee_eth, "ether")

            nonce = self.web3.eth.get_transaction_count(self.wallet_address)
            # Pass the hash to the contract
            tx = self.contract.functions.createRoom(
                number_rounds, 
                secret_hash
            ).build_transaction({
                "from": self.wallet_address,
                "nonce": nonce,
                "value": value_in_wei,
                "gas": 300000,
                "gasPrice": self.web3.to_wei("20", "gwei")
            })

            signed_tx = self.web3.eth.account.sign_transaction(tx, self.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            self.room_creation_block = receipt.blockNumber
            events = self.contract.events.RoomCreated().process_receipt(receipt)
            
            if events:
                self.room = events[0]["args"]["roomNumber"]
                return True, f"Room {self.room} created with {entry_fee_eth} ETH bet!"
            return False, "Event not found"
        
        except Exception as e:
            return False, str(e)
            
    def connect_to_room(self, room_id: int):
        """User 2 must match the entry fee found in the room storage"""
        try:
            # Get room details to know the required entry fee
            room_data = self.contract.functions.rooms(room_id).call()
            entry_fee_wei = room_data[ENTRY_FREE_INDEX]
            
            nonce = self.web3.eth.get_transaction_count(self.wallet_address)
            tx = self.contract.functions.connectToRoom(room_id).build_transaction({
                "from": self.wallet_address,
                "nonce": nonce,
                "value": entry_fee_wei, 
                "gas": 250000,
                "gasPrice": self.web3.to_wei("20", "gwei")
            })
            
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            self.web3.eth.wait_for_transaction_receipt(tx_hash)
            self.room = room_id
            return True, tx_hash.hex()
        except Exception as e:
            return False, str(e)
        
    def withdraw_winnings(self):
        """Call the new withdrawal function"""
        try:
            nonce = self.web3.eth.get_transaction_count(self.wallet_address)
            tx = self.contract.functions.withdrawWinnings().build_transaction({
                "from": self.wallet_address,
                "nonce": nonce,
                "gas": 100000,
                "gasPrice": self.web3.to_wei("20", "gwei")
            })
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            return True, tx_hash.hex()
        except Exception as e:
            return False, str(e)


    def delete_room(self):
        if self.wallet_address is None:
            return False, "Wallet not connected"
    
        try:
            nonce = self.web3.eth.get_transaction_count(self.wallet_address)
    
            tx = self.contract.functions.deleteRoom(self.room).build_transaction({
                "from": self.wallet_address,
                "nonce": nonce,
                "gas": 150000,
                "gasPrice": self.web3.to_wei("20", "gwei")
            })
    
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            self.web3.eth.wait_for_transaction_receipt(tx_hash)
    
            return True, tx_hash.hex()
    
        except Exception as e:
            return False, str(e)

    def set_user2_guess(self, guess: int):
        if self.wallet_address is None:
            return False, "Wallet not connected"
    
        try:
            nonce = self.web3.eth.get_transaction_count(self.wallet_address)
    
            tx = self.contract.functions.setUser2Guess(
                self.room, guess
            ).build_transaction({
                "from": self.wallet_address,
                "nonce": nonce,
                "gas": 150000,
                "gasPrice": self.web3.to_wei("20", "gwei")
            })
    
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            self.web3.eth.wait_for_transaction_receipt(tx_hash)
    
            return True, tx_hash.hex()
    
        except Exception as e:
            return False, str(e)

    def get_user2_last_guess(self):
        try:
            room = self.contract.functions.rooms(self.room).call()

            guesses = room[ROOM_GUESSES_INDEX]
            if not guesses:
                return False, "No guesses yet"

            last_guess = guesses[-1]
            round_number = len(guesses)

            return True, {
                "guess": last_guess,
                "round": round_number
            }

        except Exception as e:
            return False, str(e)

            
    def set_user1_feedback(self, feedback: int):
        if self.wallet_address is None:
            return False, "Wallet not connected"
    
        try:
            nonce = self.web3.eth.get_transaction_count(self.wallet_address)
    
            tx = self.contract.functions.setUser1Feedback(
                self.room, feedback
            ).build_transaction({
                "from": self.wallet_address,
                "nonce": nonce,
                "gas": 150000,
                "gasPrice": self.web3.to_wei("20", "gwei")
            })
    
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            self.web3.eth.wait_for_transaction_receipt(tx_hash)
    
            return True, tx_hash.hex()
    
        except Exception as e:
            return False, str(e)

    def get_user1_last_feedback(self):
        try:
            room = self.contract.functions.rooms(self.room).call()

            feedbacks = room[ROOM_FEEDBACKS_INDEX]
            if not feedbacks:
                return False, "No feedback yet"

            last_feedback = feedbacks[-1]
            round_number = len(feedbacks)

            return True, {
                "feedback": last_feedback,
                "round": round_number
            }

        except Exception as e:
            return False, str(e)

    def get_game_result(self):
        try:
            events = self.contract.events.GameFinished().get_logs(
                fromBlock=self.room_creation_block,
                toBlock="latest"
            )

            for e in events[::-1]:
                if e["args"]["roomNumber"] == self.room:
                    return True, {
                        "winner": e["args"]["winner"],
                        "user1Lied": e["args"]["user1Lied"]
                    }

            return False, "No game result yet"

        except Exception as e:
            return False, str(e)

    def reveal_secret(self, secret: int):
        try:
            nonce = self.web3.eth.get_transaction_count(self.wallet_address)

            tx = self.contract.functions.revealSecret(
                self.room,
                secret
            ).build_transaction({
                "from": self.wallet_address,
                "nonce": nonce,
                "gas": 300000,
                "gasPrice": self.web3.to_wei("20", "gwei")
            })

            signed_tx = self.web3.eth.account.sign_transaction(tx, self.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            self.web3.eth.wait_for_transaction_receipt(tx_hash)

            return True, tx_hash.hex()

        except Exception as e:
            return False, str(e)


