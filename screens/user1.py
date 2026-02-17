import customtkinter as ctk

class SetNumberScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=20)
        self.controller = controller

        # Title
        ctk.CTkLabel(self, text="User 1 - Set Secret Number", font=("Arial", 18, "bold")).pack(pady=(30,10))

        # Room number
        self.room_label = ctk.CTkLabel(self, text="Room: --")
        self.room_label.pack(pady=10)

        # Entry for secret number
        self.secret_entry = ctk.CTkEntry(self, placeholder_text="Enter secret number (1-100)", width=200)
        self.secret_entry.pack(pady=10)

        # Feedback buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=15)

        ctk.CTkButton(button_frame, text="Smaller", width=100, command=lambda: self.send_feedback(2)).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Equal", width=100, command=lambda: self.send_feedback(0)).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Greater", width=100, command=lambda: self.send_feedback(1)).pack(side="left", padx=5)

        # Back button
        ctk.CTkButton(self, text="Back to Menu", fg_color="transparent", text_color="gray",
                       command=lambda: controller.show_screen("MenuScreen")).pack(pady=20)

    def set_room_number(self, room_number):
        """Update the room label"""
        self.room_label.configure(text=f"Room: {room_number}")

    def send_feedback(self, feedback):
        """Send feedback to smart contract"""
        success, tx_hash = self.controller.web3_service.set_user1_feedback(feedback)
        
        if success:
            print(f"Feedback sent: {tx_hash}")
            # Check if this was the last round to trigger reveal
            self.check_game_end()
        else:
            print(f"Error: {tx_hash}")

    def check_game_end(self):
        room = self.controller.web3_service.contract.functions.rooms(
            self.controller.web3_service.room
        ).call()

        guesses = room[4]   # ROOM_GUESSES_INDEX
        feedbacks = room[5] # ROOM_FEEDBACKS_INDEX
        max_rounds = room[6] 

        if len(feedbacks) == max_rounds and len(guesses) == max_rounds:
            self.finish_game()

    def finish_game(self):
        secret = self.secret_entry.get()
        if not secret.isdigit():
            print("Invalid secret")
            return

        secret = int(secret)
        success, msg = self.controller.web3_service.reveal_secret(secret)
        if not success:
            print("Reveal error:", msg)
            return

        success, result = self.controller.web3_service.get_game_result()
        if not success:
            print("Result not ready:", result)
            return

        winner = result["winner"]
        lied = result["user1Lied"]

        if winner == 2:
            text = "User 2 won!"
        else:
            text = "User 1 won!"

        if lied:
            text += " (User 1 lied)"

        print(text)

    def create_room_action(self):
        """Initial action to start the game as Host"""
        secret = self.secret_entry.get()
        if not secret.isdigit():
            return
        
        # pass the integer secret to logic.py 
        success, msg = self.controller.web3_service.create_room(int(secret), number_rounds=3)
        if success:
            self.set_room_number(self.controller.web3_service.room)
            print(msg)
