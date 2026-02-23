import customtkinter as ctk

class MenuScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=20)
        self.controller = controller

        ctk.CTkLabel(self, text="Guess", font=("Arial", 26, "bold")).pack(pady=(40, 5))
        ctk.CTkLabel(self, text="Game", text_color="gray").pack(pady=(0, 30))

        buttons = [
            ("Join a room", "WalletScreen"),
            ("Create a room", "HostScreen"),
            ("Random person", "WalletScreen"),
            ("I don’t have friends (Solo)", "GameScreen"),
        ]

        for text, screen_name in buttons:
                    ctk.CTkButton(
                        self,
                        text=text,
                        height=42,
                        corner_radius=12,
                        command=lambda s=screen_name, t=text: self.on_button_click(s, t)
                    ).pack(pady=6)

    def on_button_click(self, screen_name, button_text):
        if "Host" in button_text:
            self.controller.next_destination = "HostScreen"
        elif "Join" in button_text:
            self.controller.next_destination = "GuesserScreen"
        else:
            self.controller.next_destination = screen_name
            
        if "Solo" in button_text:
            self.controller.show_screen("GameScreen")
        else:
            self.controller.show_screen("WalletScreen")