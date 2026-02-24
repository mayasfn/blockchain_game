import customtkinter as ctk
from blockchain.logic import MAX_ROUNDS_INDEX

class HostScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=20)
        self.controller = controller
        
        self.rounds_var = ctk.StringVar(value="3")
        self.fee_map = {"3": 0.1, "5": 0.2, "10": 0.5}

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

        self.status_label = ctk.CTkLabel(self.game_frame, text="Waiting...", font=("Arial", 14))
        self.status_label.pack(pady=10)

        self.fb_btn_frame = ctk.CTkFrame(self.game_frame, fg_color="transparent")
        self.fb_btn_frame.pack(pady=10)

        ctk.CTkButton(self.fb_btn_frame, text="Smaller", width=80, fg_color="#E74C3C", command=lambda: self.send_feedback(2)).pack(side="left", padx=5)
        ctk.CTkButton(self.fb_btn_frame, text="Equal", width=80, fg_color="#2ECC71", command=lambda: self.send_feedback(0)).pack(side="left", padx=5)
        ctk.CTkButton(self.fb_btn_frame, text="Greater", width=80, fg_color="#3498DB", command=lambda: self.send_feedback(1)).pack(side="left", padx=5)

        ctk.CTkButton(self, text="Back to Menu", fg_color="transparent", text_color="gray",
                       command=lambda: controller.show_screen("MenuScreen")).pack(side="bottom", pady=10)

    def update_fee_display(self, value):
        self.fee_label.configure(text=f"Entry Fee: {self.fee_map[value]} ETH")

    def create_room_action(self):
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
            self.show_game_ui(self.controller.web3_service.room)

    def resume_room_action(self):
        """Skip creation and jump to game state for a specific Room ID"""
        room_id = self.resume_entry.get()
        if not room_id.isdigit(): return
        self.controller.web3_service.room = int(room_id)
        self.show_game_ui(room_id)

    def show_game_ui(self, room_id):
        self.room_label.configure(text=f"ROOM NUMBER: {room_id}")
        self.setup_frame.pack_forget()
        self.game_frame.pack(pady=20, fill="both", expand=True)
        self.start_polling()

    def start_polling(self):
        if self.controller.current_screen != self: return
        joined, _ = self.controller.web3_service.check_guesser_joined()
        success, guess_val = self.controller.web3_service.get_current_round_guess()

        if success and guess_val is not None:
            self.status_label.configure(text=f"GUESS RECEIVED: {guess_val}", text_color="cyan")
        elif joined:
            self.status_label.configure(text="Guesser Joined! Waiting for guess...", text_color="green")
        else:
            self.status_label.configure(text="Waiting for Guesser...", text_color="gray")
        self.after(5000, self.start_polling)
 
    def send_feedback(self, feedback_type):
        """Send feedback to smart contract, 0=Equal, 1=Greater, 2=Smaller"""
        success, tx_hash = self.controller.web3_service.set_feedback(feedback_type)
        if success:
            self.controller.web3_service.web3.eth.wait_for_transaction_receipt(tx_hash)
            self.status_label.configure(text="Feedback confirmed!")
            self.check_game_end()
        self.controller.loading_out.stop()

    def check_game_end(self):
        current_count = self.controller.web3_service.get_feedback_count()
        try:
            room_data = self.controller.web3_service.contract.functions.rooms(self.controller.web3_service.room).call()
            if current_count >= room_data[MAX_ROUNDS_INDEX]:
                self.fb_btn_frame.pack_forget() # Hide feedback buttons
                self.show_reveal_button()
        except Exception as e:
            print(f"Sync error: {e}")

    def show_reveal_button(self):
        if hasattr(self, 'reveal_btn'): return
        self.reveal_btn = ctk.CTkButton(self.game_frame, text="Reveal Secret", fg_color="green", command=self.finish_game)
        self.reveal_btn.pack(pady=10)

    def finish_game(self):
        secret = self.secret_entry.get()
        self.controller.loading_out.start()
        success, msg = self.controller.web3_service.reveal_secret(int(secret))
        if success:
            self.controller.web3_service.web3.eth.wait_for_transaction_receipt(msg)
            self.reveal_btn.destroy()
            self.check_and_show_withdraw()
        self.controller.loading_out.stop()

    def check_and_show_withdraw(self):
        if self.controller.web3_service.get_pending_balance():
            ctk.CTkButton(self.game_frame, text="Withdraw Winnings", fg_color="gold", text_color="black", 
                           command=self.withdraw_action).pack(pady=10)
            self.status_label.configure(text="YOU WON!", text_color="gold")
        else:
            self.status_label.configure(text="Game Over. Host Lost.", text_color="gray")

    def withdraw_action(self):
        self.controller.loading_out.start()
        success, tx = self.controller.web3_service.withdraw_winnings()
        if success: self.status_label.configure(text="Winnings Claimed!")
        self.controller.loading_out.stop()