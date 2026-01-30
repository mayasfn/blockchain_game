import customtkinter as ctk


class MenuScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=20)
        self.controller = controller

        ctk.CTkLabel(self, text="Guess", font=("Arial", 26, "bold")).pack(pady=(40, 5))

        ctk.CTkLabel(self, text="Game", text_color="gray").pack(pady=(0, 30))

        buttons = [
            ("Rejoindre une chambre", "WalletScreen"),
            ("Créer une chambre", "WalletScreen"),
            ("Random person", "WalletScreen"),
            ("I don’t have friends (Solo)", "GameScreen"),
        ]

        for text, screen in buttons:
            ctk.CTkButton(
                self,
                text=text,
                height=42,
                corner_radius=12,
                command=lambda s=screen: controller.show_screen(s),
            ).pack(pady=6)