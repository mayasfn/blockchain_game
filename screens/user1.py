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
        """Send feedback to smart contract or controller"""
        room_number = self.room_label.cget("text").replace("Room: ", "")
        secret_number = self.secret_entry.get()

        # Here you can integrate with smart contract, e.g.
        # self.controller.game.set_user1_feedback(room_number, feedback)

        print(f"Room {room_number} | Secret: {secret_number} | Feedback: {feedback}")
