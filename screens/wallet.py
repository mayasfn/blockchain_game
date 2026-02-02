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
            self, placeholder_text="Private key", show="*", width=260
        )
        self.key.pack(pady=10)
        
        self.room_entry = None
        if self.controller.web3_service.room != 0:
            self.room_entry = ctk.CTkEntry(
                self, placeholder_text="Numéro de chambre", width=260
            )
            self.room_entry.pack(pady=10)
        
        self.info_label = ctk.CTkLabel(
            self, text=""
        )
        self.info_label.pack(anchor="w", padx=10, pady=5)
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
        message = self.controller.web3_service.connect_wallet(wallet)
        success, message = self.controller.web3_service.check_wallet_connection(key)
        if success:
            print(message)
            balance = self.controller.web3_service.get_balance_eth()
            if self.controller.web3_service.room != 0:
                room = self.room_entry.get()
                self.controller.web3_service.room = int(room)
                self.controller.web3_service.connect_to_room(123)
                if self.controller.web3_service.player == 1:
                    self.controller.screens["GuessScreen"].set_room_number(self.controller.web3_service.room)
                    self.controller.show_screen("GuessScreen")
                else:
                    self.controller.screens["SetNumberScreen"].set_room_number(self.controller.web3_service.room)
                    self.controller.show_screen("SetNumberScreen")
                    
            else:
                self.controller.web3_service.create_room(321)
                game_screen = self.controller.screens["GameScreen"]
                game_screen.update_wallet_info(
                    balance_eth=str(balance),
                    game_price_eth="0.01"
                )
                self.controller.show_screen("GameScreen")
        else:
            self.update_info(message)
            print("Error:", message)
    
    def update_info(self, message: str):
        self.info_label.configure(text=message)