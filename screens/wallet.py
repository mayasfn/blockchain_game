import customtkinter as ctk


class WalletScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=20)
        self.controller = controller

        ctk.CTkLabel(self, text="Wallet", font=("Arial", 22, "bold")).pack(
            pady=(40, 20)
        )

        self.wallet = ctk.CTkEntry(self, placeholder_text="Wallet address", width=260)
        self.wallet.pack(pady=10)

        self.key = ctk.CTkEntry(
            self, placeholder_text="Private key (optionnel)", show="*", width=260
        )
        self.key.pack(pady=10)

        ctk.CTkButton(
            self, text="Continuer", command=lambda: controller.show_screen("GameScreen")
        ).pack(pady=15)

        ctk.CTkButton(
            self,
            text="Retour menu",
            fg_color="transparent",
            text_color="gray",
            command=lambda: controller.show_screen("MenuScreen"),
        ).pack()
