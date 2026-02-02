import customtkinter as ctk

class MenuScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=20)
        self.controller = controller

        ctk.CTkLabel(self, text="Guess", font=("Arial", 26, "bold")).pack(pady=(40, 5))
        ctk.CTkLabel(self, text="Game", text_color="gray").pack(pady=(0, 30))

        ctk.CTkButton(
            self,
            text="Rejoindre une chambre",
            height=42,
            corner_radius=12,
            command=self.join_room,
        ).pack(pady=6)

        ctk.CTkButton(
            self,
            text="Créer une chambre",
            height=42,
            corner_radius=12,
            command=self.create_room,
        ).pack(pady=6)

        ctk.CTkButton(
            self,
            text="I don’t have friends (Solo)",
            height=42,
            corner_radius=12,
            command=self.solo_mode,
        ).pack(pady=6)

    def join_room(self):
        self.controller.show_screen("WalletScreen")

    def create_room(self):
        self.controller.web3_service.room = 0
        self.controller.show_screen("WalletScreen")

    def solo_mode(self):
        self.controller.web3_service.room = -1
        self.controller.show_screen("WalletScreen")