import os
import time
from web3 import Web3
from eth_account import Account
from blockchain.config import RPC_URL, CONTRACT_ADDRESS, CONTRACT_ABI
from eth_abi import encode
from eth_utils import keccak

CONNECTED_USER_NUMBER = 2
SECRET_HASH_INDEX = 3
USER_COUNT_INDEX = 4
EXISTS_INDEX = 5
MAX_ROUNDS_INDEX = 6
ENTRY_FEE_INDEX = 7
REVEAL_DEADLINE_INDEX = 8

class Web3Service:
    def __init__(self, rpc_url=RPC_URL):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.wallet_address = None
        self.key = None
        self.player = None
        self.room = None
        self.contract_address = CONTRACT_ADDRESS
        self.contract_abi = CONTRACT_ABI
        self.room_creation_block = None

        self.contract = self.web3.eth.contract(
            address=self.contract_address,
            abi=self.contract_abi
        )
        
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
            account = Account.from_key(private_key)
            if account.address != self.wallet_address:
                return False, "Private key does not match wallet address"
            self.key = private_key
            return True, "Connected successfully"
        except Exception as e:
            return False, str(e)

    def send_transaction(self, contract_func, value_wei=0):
        """Helper to handle nonces and aggressive gas pricing for Sepolia."""
        try:
            # 'pending' tis o avoid nonce collisions during rapid UI actions
            nonce = self.web3.eth.get_transaction_count(self.wallet_address, 'pending')

            # 2x the current gas price to ensure it mines in the next block
            gas_price = int(self.web3.eth.gas_price * 2.0) 

            tx = contract_func.build_transaction({
                "from": self.wallet_address,
                "nonce": nonce,
                "value": value_wei,
                "gas": 400000,
                "gasPrice": gas_price
            })

            signed_tx = self.web3.eth.account.sign_transaction(tx, self.key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            return True, tx_hash.hex()
        except Exception as e:
            return False, str(e)
    # -----------------------------
    # Player / Room functions
    # -----------------------------
    def set_player(self, player: int):
        self.player = player

    def create_room(self, secret_number: int, number_rounds: int = 3, entry_fee_eth: float = 1.0):
        if self.wallet_address is None or self.key is None:
            return False, "Wallet not connected"
        
        secret_hash = keccak(encode(['uint256'], [secret_number]))
        value_in_wei = self.web3.to_wei(entry_fee_eth, "ether")
        
        func = self.contract.functions.createRoom(number_rounds, secret_hash)
        success, result = self.send_transaction(func, value_wei=value_in_wei)
        
        if success:
            receipt = self.web3.eth.wait_for_transaction_receipt(result)
            self.room_creation_block = receipt.blockNumber
            events = self.contract.events.RoomCreated().process_receipt(receipt)
            if events:
                self.room = events[0]["args"]["roomNumber"]
                return True, f"Room {self.room} created!"
            return True, "Room created (ID scan failed)"
        return False, result

    def connect_to_room(self, room_id: int):
        """Strictly fetches entry fee and sets room state upon success."""
        if self.wallet_address is None or self.key is None:
            return False, "Wallet not connected"

        # Fetch precise entry fee or fail early to save gas
        try:
            room_data = self.contract.functions.rooms(room_id).call()
            if not room_data[EXISTS_INDEX]:
                return False, f"Room {room_id} does not exist"
            entry_fee_wei = room_data[ENTRY_FEE_INDEX]
        except Exception as e:
            return False, f"Failed to fetch room fee: {str(e)}"

        func = self.contract.functions.connectToRoom(room_id)
        success, result = self.send_transaction(func, value_wei=entry_fee_wei)
        
        if success:
            self.room = room_id
            return True, result
        return False, result

    def set_guess(self, guess: int):
        if self.wallet_address is None or self.room is None:
            return False, "No active room detected."
        func = self.contract.functions.setUser2Guess(self.room, guess)
        return self.send_transaction(func)

    def set_feedback(self, feedback: int):
        if self.wallet_address is None or self.room is None:
            return False, "No active room detected."
        func = self.contract.functions.setUser1Feedback(self.room, feedback)
        return self.send_transaction(func)

    def reveal_secret(self, secret: int):
        if self.wallet_address is None or self.room is None:
            return False, "No active room detected."
        func = self.contract.functions.revealSecret(self.room, secret)
        return self.send_transaction(func)

    def withdraw_winnings(self):
        if self.wallet_address is None or self.key is None:
            return False, "Wallet not connected"
        func = self.contract.functions.withdrawWinnings()
        return self.send_transaction(func)

    def delete_room(self):
        if self.wallet_address is None or self.room is None:
            return False, "No active room to delete"
        func = self.contract.functions.deleteRoom(self.room)
        success, result = self.send_transaction(func)
        if success:
            self.room = None # Reset state
        return success, result

    def get_feedback_count(self):
        """Scans events to count feedbacks since dynamic arrays are excluded from the mapping."""
        if not self.room:
            return 0
        try:
            events = self.contract.events.FeedbackSent().get_logs(
                fromBlock=self.room_creation_block or "earliest",
                toBlock="latest"
            )
            this_room_feedbacks = [e for e in events if e.args.roomNumber == self.room]
            return len(this_room_feedbacks)
        except Exception as e:
            print(f"Error fetching feedback count: {e}")
            return 0

    def get_game_result(self, tx_hash=None):
        """Instant decoding of GameFinished event via receipt or fallback scan."""
        try:
            if tx_hash:
                receipt = self.web3.eth.get_transaction_receipt(tx_hash)
                logs = self.contract.events.GameFinished().process_receipt(receipt)
                if logs:
                    return True, {
                        "winner": logs[0]["args"]["winner"],
                        "user1Lied": logs[0]["args"]["user1Lied"]
                    }
            
            events = self.contract.events.GameFinished().get_logs(
                fromBlock=self.room_creation_block or "earliest",
                toBlock="latest"
            )
            for e in events[::-1]:
                if e["args"]["roomNumber"] == self.room:
                    return True, {
                        "winner": e["args"]["winner"],
                        "user1Lied": e["args"]["user1Lied"]
                    }
            return False, "No result yet"
        except Exception as e:
            return False, str(e)