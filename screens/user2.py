import customtkinter as ctk

class GuessScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=20)
        self.controller = controller

        # Title
        ctk.CTkLabel(self, text="User 2 - Make a Guess", font=("Arial", 18, "bold")).pack(pady=(30,10))

        # Room number
        self.room_label = ctk.CTkLabel(self, text="Room: --")
        self.room_label.pack(pady=10)

        # Entry for guess
        self.guess_entry = ctk.CTkEntry(self, placeholder_text="Enter your guess", width=200)
        self.guess_entry.pack(pady=10)

        # Send button
        ctk.CTkButton(self, text="Send Guess", width=150, command=self.send_guess).pack(pady=10)

        # Feedback label
        self.feedback_label = ctk.CTkLabel(self, text="Feedback: --")
        self.feedback_label.pack(pady=10)

        # Back button
        ctk.CTkButton(self, text="Back to Menu", fg_color="transparent", text_color="gray",
                       command=lambda: controller.show_screen("MenuScreen")).pack(pady=20)

    def set_room_number(self, room_number):
        self.room_label.configure(text=f"Room: {room_number}")

    def update_feedback(self, feedback_text):
        """Update the feedback label (Smaller / Greater / Equal)"""
        self.feedback_label.configure(text=f"Feedback: {feedback_text}")

    def send_guess(self):
        room_number = self.room_label.cget("text").replace("Room: ", "")
        guess = self.guess_entry.get()

        # Here you can integrate with smart contract or controller
        # Example: self.controller.game.set_user2_guess(room_number, int(guess))
        print(f"Room {room_number} | Guess: {guess}")
