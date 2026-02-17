import customtkinter as ctk

class HostScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=20)
        self.controller = controller
        
        # Data
        self.rounds_var = ctk.StringVar(value="3")
        self.fee_map = {"3": 0.1, "5": 0.2, "10": 0.5}
        # Setup Frame for creating room
        self.setup_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.setup_frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(self.setup_frame, text="Host Setup", font=("Arial", 20, "bold")).pack(pady=10)
        
        ctk.CTkLabel(self.setup_frame, text="Select Number of Rounds:").pack(pady=5)
        self.round_selector = ctk.CTkSegmentedButton(
            self.setup_frame, values=["3", "5", "10"], 
            variable=self.rounds_var, 
            command=self.update_fee_display
        )
        self.round_selector.pack(pady=10)

        self.fee_label = ctk.CTkLabel(self.setup_frame, text="Entry Fee: 0.1 ETH")
        self.fee_label.pack()

        self.secret_entry = ctk.CTkEntry(self.setup_frame, placeholder_text="Enter secret number (1-100)", width=200)
        self.secret_entry.pack(pady=10)

        ctk.CTkButton(self.setup_frame, text="Create & Pay ETH", command=self.create_room_action).pack(pady=10)

        # Game Frame, feedback buttons and status 
        self.game_frame = ctk.CTkFrame(self, fg_color="transparent")
        
        self.room_label = ctk.CTkLabel(self.game_frame, text="ROOM: --", font=("Arial", 18, "bold"), text_color="green")
        self.room_label.pack(pady=10)

        self.status_label = ctk.CTkLabel(self.game_frame, text="Waiting for guesses...", font=("Arial", 14))
        self.status_label.pack(pady=10)

        # Feedback buttons
        fb_btn_frame = ctk.CTkFrame(self.game_frame, fg_color="transparent")
        fb_btn_frame.pack(pady=10)

        ctk.CTkButton(fb_btn_frame, text="Smaller", width=100, fg_color="#E74C3C", command=lambda: self.send_feedback(2)).pack(side="left", padx=5)
        ctk.CTkButton(fb_btn_frame, text="Equal", width=100, fg_color="#2ECC71", command=lambda: self.send_feedback(0)).pack(side="left", padx=5)
        ctk.CTkButton(fb_btn_frame, text="Greater", width=100, fg_color="#3498DB", command=lambda: self.send_feedback(1)).pack(side="left", padx=5)

        ctk.CTkButton(self, text="Back to Menu", fg_color="transparent", text_color="gray",
                       command=lambda: controller.show_screen("MenuScreen")).pack(pady=20)

    def update_fee_display(self, value):
        fee = self.fee_map[value]
        self.fee_label.configure(text=f"Entry Fee: {fee} ETH")

    def create_room_action(self):
        rounds = int(self.rounds_var.get())
        fee = self.fee_map[str(rounds)]
        secret = self.secret_entry.get()
        
        if not secret.isdigit(): return

        success, msg = self.controller.web3_service.create_room(
            secret_number=int(secret), 
            number_rounds=rounds, 
            entry_fee_eth=fee
        )
        if success:
            # Update room label with actual room number from contract
            self.room_label.configure(text=f"ROOM NUMBER: {self.controller.web3_service.room}")
            
            # Switch Frames from setup to game play
            self.setup_frame.pack_forget()
            self.game_frame.pack(pady=20, fill="both", expand=True)
            print(f"Room Created! {msg}")

    def send_feedback(self, feedback_type):
        """Send feedback to smart contract, 0=Equal, 1=Greater, 2=Smaller"""
        success, tx_hash = self.controller.web3_service.set_user1_feedback(feedback_type)
        if success:
            self.status_label.configure(text=f"Feedback sent! Hash: {tx_hash[:10]}...")
            self.check_game_end()
        else:
            self.status_label.configure(text=f"Error sending feedback: {tx_hash}", text_color="red")

    def check_game_end(self):
        room_data = self.controller.web3_service.contract.functions.rooms(
            self.controller.web3_service.room
        ).call()

        guesses = room_data[4] #ROOM_GUESSES_INDEX
        feedbacks = room_data[5]  #ROOM_FEEDBACKS_INDEX
        max_rounds = room_data[8] # NUMBER_ROUNDS_INDEX

        if len(feedbacks) == max_rounds:
            self.finish_game()

    def finish_game(self):
        secret = int(self.secret_entry.get())
        success, msg = self.controller.web3_service.reveal_secret(secret)
        if success:
            self.status_label.configure(text="Game Finished! Secret revealed.", text_color="green")
        else:
            print("Reveal Error:", msg)