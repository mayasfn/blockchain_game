import customtkinter as ctk
from blockchain.logic import MAX_ROUNDS_INDEX

class HostScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=20)
        self.controller = controller
        
        self.rounds_var = ctk.StringVar(value="3")
        self.fee_map = {"3": 0.01, "5": 0.02, "10": 0.05}
        self._typed_secret = None
        self._game_ended = False

        # --- SETUP FRAME ---
        self.setup_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.setup_frame.pack(pady=10, padx=20, fill="both", expand=True)

        ctk.CTkLabel(self.setup_frame, text="Host Setup", font=("Arial", 20, "bold")).pack(pady=5)
        
        self.round_selector = ctk.CTkSegmentedButton(
            self.setup_frame, values=["3", "5", "10"], 
            variable=self.rounds_var, command=self.update_fee_display
        )
        self.round_selector.pack(pady=5)

        self.fee_label = ctk.CTkLabel(self.setup_frame, text="Entry Fee: 0.1 ETH")
        self.fee_label.pack()
        self.balance_label= ctk.CTkLabel(self.setup_frame, text="")
        self.balance_label.pack()

        self.secret_entry = ctk.CTkEntry(self.setup_frame, placeholder_text="Secret (1-100)", width=200)
        self.secret_entry.pack(pady=5)

        ctk.CTkButton(self.setup_frame, text="Create & Pay ETH", command=self.create_room_action).pack(pady=5)

        ctk.CTkLabel(self.setup_frame, text="-- OR --", text_color="gray").pack(pady=2)
        self.resume_entry = ctk.CTkEntry(self.setup_frame, placeholder_text="Room ID to Resume", width=200)
        self.resume_entry.pack(pady=5)
        
        ctk.CTkButton(self.setup_frame, text="Resume Room", fg_color="#5D6D7E", command=self.resume_room_action).pack(pady=5)

        # --- GAME FRAME ---
        self.game_frame = ctk.CTkFrame(self, fg_color="transparent")
        
        self.room_label = ctk.CTkLabel(self.game_frame, text="ROOM: --", font=("Arial", 18, "bold"), text_color="green")
        self.room_label.pack(pady=10)

        self.round_label = ctk.CTkLabel(self.game_frame, text="", font=("Arial", 12), text_color="gray")
        self.round_label.pack()

        self.status_label = ctk.CTkLabel(self.game_frame, text="Waiting...", font=("Arial", 14))
        self.status_label.pack(pady=10)

        self.fb_btn_frame = ctk.CTkFrame(self.game_frame, fg_color="transparent")
        self.fb_btn_frame.pack(pady=10)

        ctk.CTkButton(self.fb_btn_frame, text="Smaller", width=80, fg_color="#E74C3C", command=lambda: self.send_feedback(2)).pack(side="left", padx=5)
        ctk.CTkButton(self.fb_btn_frame, text="Equal", width=80, fg_color="#2ECC71", command=lambda: self.send_feedback(0)).pack(side="left", padx=5)
        ctk.CTkButton(self.fb_btn_frame, text="Greater", width=80, fg_color="#3498DB", command=lambda: self.send_feedback(1)).pack(side="left", padx=5)

        ctk.CTkButton(self, text="Back to Menu", fg_color="transparent", text_color="gray",
                       command=lambda: (controller.web3_service.reset_game_state(), controller.show_screen("MenuScreen"))).pack(side="bottom", pady=10)

    def update_fee_display(self, value):
        """Update the entry fee label when the user changes the round count."""
        self.fee_label.configure(text=f"Entry Fee: {self.fee_map[value]} ETH")

    def create_room_action(self):
        """Read the secret + round count, call the contract to create a room and pay the entry fee."""
        secret = self.secret_entry.get()
        if not secret.isdigit(): return
        self.controller.loading_out.start()
        self.update()
        success, msg = self.controller.web3_service.create_room(
            secret_number=int(secret), 
            number_rounds=int(self.rounds_var.get()), 
            entry_fee_eth=self.fee_map[self.rounds_var.get()]
        )
        self.controller.loading_out.stop()
        if success:
            self._typed_secret = secret
            self.show_game_ui(self.controller.web3_service.room)
        elif 'insufficient funds' in msg:
            balance = self.controller.web3_service.get_balance_eth()
            self.balance_label.configure(text=f"Insufficient balance: {balance}")
            
            

    def resume_room_action(self):
        """Skip room creation and rejoin an existing room by its ID (no new transaction)."""
        room_id = self.resume_entry.get()
        if not room_id.isdigit(): return
        self.controller.web3_service.room = int(room_id)
        self.show_game_ui(room_id)

    def _reset_for_new_game(self):
        """Destroy any leftover widgets from a previous game and reset in-game state."""
        self._game_ended = False
        for attr in ("reveal_btn", "secret_reveal_entry", "claim_btn"):
            if hasattr(self, attr):
                getattr(self, attr).destroy()
                delattr(self, attr)
        self.fb_btn_frame.pack(pady=10)
        self.round_label.pack()
        self.status_label.configure(text="Waiting...", font=("Arial", 14), text_color="white")

    def show_game_ui(self, room_id):
        """Switch from the setup frame to the in-game frame and begin polling."""
        self._reset_for_new_game()
        self.room_label.configure(text=f"ROOM NUMBER: {room_id}")
        self.setup_frame.pack_forget()
        self.game_frame.pack(pady=20, fill="both", expand=True)
        self.start_polling()

    def start_polling(self):
        """Poll the contract every 5 s to detect guesser join and incoming guesses."""
        if self.controller.current_screen != self or self._game_ended: return

        joined, guesser_addr = self.controller.web3_service.check_guesser_joined()
        success, guess_val = self.controller.web3_service.get_current_round_guess()

        max_r = self.controller.web3_service.max_rounds
        if max_r:
            fc = self.controller.web3_service.get_feedback_count()
            self.round_label.configure(text=f"Round {fc + 1} / {max_r}")

        if success and guess_val is not None:
            self.status_label.configure(text=f"GUESS RECEIVED: {guess_val}", font=("Arial", 14), text_color="cyan")
        elif joined:
            self.status_label.configure(text="GUESS RECEIVED: ---", font=("Arial", 14), text_color="cyan")
        else:
            self.status_label.configure(text="Waiting for Guesser...", font=("Arial", 14), text_color="gray")

        self.after(5000, self.start_polling)
 
    def send_feedback(self, feedback_type):
        """Submit the host's feedback (0=Equal, 1=Greater, 2=Smaller) to the contract."""
        self.controller.loading_out.start()
        self.update()
        success, tx_hash = self.controller.web3_service.set_feedback(feedback_type)
        if success:
            self.controller.web3_service.web3.eth.wait_for_transaction_receipt(tx_hash)
            self.status_label.configure(text="GUESS RECEIVED: ---", font=("Arial", 14), text_color="cyan")
            self.check_game_end(feedback_type)
        self.controller.loading_out.stop()

    def check_game_end(self, last_feedback):
        """After each feedback, decide whether the game is over (Equal guess or max rounds reached)."""
        try:
            room_data = self.controller.web3_service.contract.functions.rooms(self.controller.web3_service.room).call()
            max_rounds = room_data[MAX_ROUNDS_INDEX]
            current_count = self.controller.web3_service.get_feedback_count()
            all_rounds_done = current_count >= max_rounds
            guesser_won = last_feedback == 0  # Equal

            if guesser_won or all_rounds_done:
                self.fb_btn_frame.pack_forget()
                self.show_reveal_button()
        except Exception as e:
            print(f"[check_game_end] error: {e}")

    def show_reveal_button(self):
        """Hide the feedback buttons and show the secret reveal entry + button."""
        if hasattr(self, 'reveal_btn'): return
        self._game_ended = True
        self.round_label.pack_forget()
        self.status_label.configure(text="All rounds done! Reveal your secret.", text_color="white")
        self.secret_reveal_entry = ctk.CTkEntry(self.game_frame, placeholder_text="Your Secret Number", width=200)
        if self._typed_secret:
            self.secret_reveal_entry.insert(0, self._typed_secret)
        self.secret_reveal_entry.pack(pady=5)
        self.reveal_btn = ctk.CTkButton(self.game_frame, text="Reveal Secret", fg_color="green", command=self.finish_game)
        self.reveal_btn.pack(pady=10)

    def finish_game(self):
        """Send the plaintext secret to the contract so it can verify the host was honest."""
        secret = self.secret_reveal_entry.get()
        if not secret.isdigit(): return
        self.controller.loading_out.start()
        self.update()
        success, msg = self.controller.web3_service.reveal_secret(int(secret))
        if success:
            receipt = self.controller.web3_service.web3.eth.wait_for_transaction_receipt(msg)
            if receipt.status == 1:
                self.reveal_btn.destroy()
                del self.reveal_btn
                self.secret_reveal_entry.destroy()
                del self.secret_reveal_entry
                _, result = self.controller.web3_service.get_game_result()
                if result is None:
                    self.status_label.configure(text="Result pending, please wait...", text_color="orange")
                    self.after(3000, self._retry_game_result)
                else:
                    self.check_and_show_withdraw(result)
            else:
                self.status_label.configure(text="Reveal rejected (wrong secret?)", text_color="red")
        self.controller.loading_out.stop()

    def _retry_game_result(self):
        """Retry fetching the GameFinished event if it wasn't indexed immediately after reveal."""
        _, result = self.controller.web3_service.get_game_result()
        if result is None:
            self.status_label.configure(text="Still waiting for result...", text_color="orange")
            self.after(3000, self._retry_game_result)
        else:
            self.check_and_show_withdraw(result)

    def check_and_show_withdraw(self, result):
        """Compare the GameFinished winner address to own wallet to display win/lose result."""
        my_addr = self.controller.web3_service.wallet_address
        i_won = result.get("winner", "").lower() == my_addr.lower()
        if i_won:
            self.status_label.configure(text="YOU WON!", font=("Arial", 20, "bold"), text_color="gold")
            self.claim_btn = ctk.CTkButton(self.game_frame, text="Claim Winnings", fg_color="gold", text_color="black",
                           command=self.withdraw_action)
            self.claim_btn.pack(pady=10)
        else:
            self.status_label.configure(text="YOU LOST.", font=("Arial", 20, "bold"), text_color="red")

    def withdraw_action(self):
        """Call the contract's withdrawWinnings function to transfer the prize to the host's wallet."""
        self.controller.loading_out.start()
        self.update()
        success, tx = self.controller.web3_service.withdraw_winnings()
        if success:
            self.controller.web3_service.web3.eth.wait_for_transaction_receipt(tx)
            self.controller.loading_out.stop()
            self.controller.web3_service.reset_game_state()
            self.controller.show_screen("MenuScreen")
        else:
            self.status_label.configure(text=f"Withdraw failed: {tx}", text_color="red")
            self.controller.loading_out.stop()