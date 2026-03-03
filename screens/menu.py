import customtkinter as ctk

class MenuScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=20)
        self.controller = controller

        ctk.CTkLabel(self, text="Guess", font=("Arial", 26, "bold")).pack(pady=(40, 5))
        ctk.CTkLabel(self, text="Game", text_color="gray").pack(pady=(0, 30))

        buttons = [
            ("Join a room", "GuesserScreen"),
            ("Create a room", "HostScreen"),
        ]

        for text, destination in buttons:
            ctk.CTkButton(
                self,
                text=text,
                height=42,
                corner_radius=12,
                command=lambda d=destination: self.on_button_click(d)
            ).pack(pady=6)

    def on_button_click(self, destination):
        ws = self.controller.web3_service
        if ws.wallet_address and ws.key:
            self.controller.show_screen(destination)
        else:
            self.controller.next_destination = destination
            self.controller.show_screen("WalletScreen")