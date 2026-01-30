import customtkinter as ctk
from blockchain.logic import check_wallet_connection

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
            self, text="Continuer", command=self.connect_wallet
        ).pack(pady=15)

        ctk.CTkButton(
            self,
            text="Retour menu",
            fg_color="transparent",
            text_color="gray",
            command=lambda: controller.show_screen("MenuScreen"),
        ).pack()
    def connect_wallet(self):
        wallet = self.wallet.get()
        key = self.key.get()
    
        success, message = check_wallet_connection(
            wallet_address=wallet,
            private_key=key,
            rpc_url='https://ethereum-sepolia-rpc.publicnode.com'
        )
    
        if success:
            print(message)
            self.controller.show_screen("GameScreen")
        else:
            print("Error:", message)
