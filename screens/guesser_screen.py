import customtkinter as ctk

class GuesserScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=20)
        self.controller = controller

        ctk.CTkLabel(self, text="User 2 - Join & Guess", font=("Arial", 18, "bold")).pack(pady=(20,10))

        self.room_entry = ctk.CTkEntry(self, placeholder_text="Enter Room Number", width=200)
        self.room_entry.pack(pady=5)
        
        ctk.CTkButton(self, text="Join Room", command=self.join_room_action).pack(pady=5)

        self.status_label = ctk.CTkLabel(self, text="Status: Not Connected", text_color="gray")
        self.status_label.pack()

        self.guess_entry = ctk.CTkEntry(self, placeholder_text="Enter your guess", width=200)
        self.guess_entry.pack(pady=10)

        ctk.CTkButton(self, text="Send Guess", width=150, command=self.send_guess).pack(pady=10)

        self.feedback_label = ctk.CTkLabel(self, text="Feedback from Host: --", text_color="blue")
        self.feedback_label.pack(pady=10)

        ctk.CTkButton(self, text="Back to Menu", command=lambda: controller.show_screen("MenuScreen")).pack(pady=20)

    def join_room_action(self):
        room_id = self.room_entry.get()
        if not room_id.isdigit():
            self.status_label.configure(text="Invalid Room Number", text_color="red")
            return

        success, msg = self.controller.web3_service.connect_to_room(int(room_id))
        if success:
            self.status_label.configure(text=f"Joined Room {room_id}!", text_color="green")
        else:
            self.status_label.configure(text=f"Error: {msg}", text_color="red")

    def send_guess(self):
        guess = self.guess_entry.get()
        if not guess.isdigit():
            return
            
        success, tx_hash = self.controller.web3_service.set_user2_guess(int(guess))
        if success:
            self.feedback_label.configure(text="Guess sent! Waiting for feedback...")
            print(f"Guess sent: {tx_hash}")
        else:
            self.feedback_label.configure(text=f"Error: {tx_hash}")