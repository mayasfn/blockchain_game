from web3 import Web3
from eth_account import Account
from blockchain.config import RPC_URL, CONTRACT_ADDRESS, CONTRACT_ABI
from eth_abi import encode
from eth_utils import keccak

EXISTS_INDEX = 5
ENTRY_FEE_INDEX = 7
MAX_ROUNDS_INDEX = 6

class Web3Service:
    def __init__(self, rpc_url=RPC_URL):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.wallet_address = None
        self.key = None
        self.room = None
        self.contract_address = CONTRACT_ADDRESS
        self.contract_abi = CONTRACT_ABI
        self.room_creation_block = None
        self.max_rounds = None

        self.contract = self.web3.eth.contract(
            address=self.contract_address,
            abi=self.contract_abi
        )
        
    def connect_wallet(self, wallet_address: str):
        """Validate and store the wallet address in checksum format."""
        try:
            self.wallet_address = self.web3.to_checksum_address(wallet_address)
            return ""
        except:
            return "Problem with the wallet address"

    def get_balance_eth(self):
        """Return the current ETH balance of the connected wallet."""
        balance = self.web3.eth.get_balance(self.wallet_address)
        return self.web3.from_wei(balance, "ether")

    def check_wallet_connection(self, private_key: str):
        """Verify that the private key matches the stored wallet address and save it."""
        try:
            if not private_key.startswith('0x'):
                private_key = '0x' + private_key
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
            nonce = self.web3.eth.get_transaction_count(self.wallet_address, 'pending')

            # 2x the current gas price to ensure it mines in the next block
            gas_price = int(self.web3.eth.gas_price * 2.0) 

            tx = contract_func.build_transaction({
                "from": self.wallet_address,
                "nonce": nonce,
                "value": value_wei,
                "gas": 500000,
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
    def create_room(self, secret_number: int, number_rounds: int = 3, entry_fee_eth: float = 0.1):
        """Hash the secret, deploy a new room on-chain, and store the assigned room number."""
        secret_hash = keccak(encode(['uint256'], [secret_number]))
        value_in_wei = self.web3.to_wei(entry_fee_eth, "ether")
        
        func = self.contract.functions.createRoom(number_rounds, secret_hash)
        success, result = self.send_transaction(func, value_wei=value_in_wei)
        
        if success:
            receipt = self.web3.eth.wait_for_transaction_receipt(result)
            events = self.contract.events.RoomCreated().process_receipt(receipt)
            if events:
                self.room = events[0]["args"]["roomNumber"]
                self.max_rounds = number_rounds
                return True, f"Room {self.room} created!"
        return success, result

    def connect_to_room(self, room_id: int):
        """Strictly fetches entry fee and sets room state upon success."""
        if self.wallet_address is None or self.key is None:
            return False, "Wallet not connected"

        try:
            room_data = self.contract.functions.rooms(room_id).call()
            if not room_data[EXISTS_INDEX]:
                return False, f"Room {room_id} does not exist"

            self.max_rounds = room_data[MAX_ROUNDS_INDEX]
            entry_fee_wei = room_data[ENTRY_FEE_INDEX]
            func = self.contract.functions.connectToRoom(room_id)
            success, tx = self.send_transaction(func, value_wei=entry_fee_wei)
            if success:
                self.room = room_id
            return success, tx
        except Exception as e:
            return False, str(e)

    def set_guess(self, guess: int):
        """Submit the guesser's number to the contract for the current round."""
        if self.room is None:
            return False, "No active room ID. Please join a room first."
        func = self.contract.functions.setUser2Guess(self.room, guess)
        return self.send_transaction(func)

    def set_feedback(self, feedback: int):
        """Send the host's feedback (0=Equal, 1=Greater, 2=Smaller) to the contract."""
        func = self.contract.functions.setUser1Feedback(self.room, feedback)
        return self.send_transaction(func)

    def reveal_secret(self, secret: int):
        """Send the plaintext secret so the contract can verify the host's hash and settle the game."""
        func = self.contract.functions.revealSecret(self.room, secret)
        return self.send_transaction(func)

    def get_current_round_guess(self):
        """Used by the Host to see if the Guesser has moved yet."""
        try:
            current_block = self.web3.eth.block_number
            events = self.contract.events.GuessSent().get_logs(from_block=current_block - 100)
            
            relevant = [e for e in events if e.args.roomNumber == self.room]
            
            if not relevant: 
                return False, None
            
            return True, relevant[-1].args.guess
        except Exception as e:
            print(f"Polling error: {e}")
            return False, None

    def get_feedback_count(self):
        """Count how many FeedbackSent events exist for the current room (= rounds played so far)."""
        try:
            current_block = self.web3.eth.block_number
            events = self.contract.events.FeedbackSent().get_logs(from_block=current_block - 2000)
            relevant = [e for e in events if e.args.roomNumber == self.room]
            return len(relevant)
        except Exception as e:
            print(f"Sync Error: {e}")
            return 0

    def check_guesser_joined(self):
        """Return whether a guesser has joined the room by checking the guest_player address on-chain."""
        try:
            room_data = self.contract.functions.rooms(self.room).call()
            guesser = room_data[0]   # [0] = guess_player (guesser/User2)
            host    = room_data[1]   # [1] = feedback_player (host/User1)
            is_joined = guesser != "0x0000000000000000000000000000000000000000"
            return is_joined, guesser
        except Exception as e:
            print(f"[check_guesser_joined] ERROR: {e}")
            return False, None

    def get_last_feedback_event(self):
        """Fetch the most recent FeedbackSent event for the current room to display to the guesser."""
        try:
            current_block = self.web3.eth.block_number
            start_block = current_block - 200
            
            events = self.contract.events.FeedbackSent().get_logs(from_block=start_block)
            
            relevant = [e for e in events if e.args.roomNumber == self.room]
            if not relevant:
                return False, "No feedback yet"

            last_event = relevant[-1]
            return True, {"feedback": last_event.args.feedback}
        except Exception as e:
            print(f"Feedback Log Error: {e}")
            return False, str(e)
        
    def withdraw_winnings(self):
        """Calls the withdrawWinnings function on the smart contract."""
        if self.wallet_address is None or self.key is None:
            return False, "Wallet not connected"
        
        func = self.contract.functions.withdrawWinnings()
        return self.send_transaction(func)

    def get_game_result(self):
        """Checks for the GameFinished event to see if the host has revealed."""
        try:
            current_block = self.web3.eth.block_number
            events = self.contract.events.GameFinished().get_logs(from_block=current_block - 2000)
            
            for e in events:
                if e.args.roomNumber == self.room:
                    return True, {
                        "winner": e.args.winner, 
                        "user1Lied": e.args.user1Lied
                    }
            return False, None
        except Exception as e:
            print(f"Result Sync Error: {e}")
            return False, str(e)

    def get_pending_balance(self):
        """Checks the contract to see if this wallet has ETH to claim."""
        try:
            balance_wei = self.contract.functions.pendingWithdrawals(self.wallet_address).call()
            return balance_wei > 0
        except Exception as e:
            print(f"Error checking pending balance: {e}")
            return False

    def reset_game_state(self):
        """Clear all game-specific state after a game ends, ready for a new game."""
        self.room = None
        self.max_rounds = None
        self.room_creation_block = None