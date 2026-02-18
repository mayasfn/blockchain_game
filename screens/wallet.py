import customtkinter as ctk

class WalletScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=20)
        self.controller = controller

        ctk.CTkLabel(self, text="Wallet", font=("Arial", 22, "bold")).pack(pady=(40, 20))
        self.wallet = ctk.CTkEntry(self, placeholder_text="0x... (Wallet Address)", width=260)
        self.wallet.pack(pady=10)

        self.key_entry = ctk.CTkEntry(
            self, 
            placeholder_text="0x... (Private Key)",  
            show="*", 
            width=300
        )
        self.key_entry.pack(pady=10)

        # Status Info Label
        self.info_label = ctk.CTkLabel(
            self, 
            text="Please enter your credentials to continue",
            text_color="gray",
            font=("Arial", 12)
        )
        self.info_label.pack(pady=5)

        # Connect Button
        self.connect_btn = ctk.CTkButton(
            self, 
            text="Connect & Verify", 
            command=self.handle_connection,
            fg_color="#2c3e50",
            hover_color="#34495e"
        )
        self.connect_btn.pack(pady=20)

        # Back to Menu
        ctk.CTkButton(
            self,
            text="Back to Menu",
            fg_color="transparent",
            text_color="gray",
            command=lambda: controller.show_screen("MenuScreen"),
        ).pack()

    def handle_connection(self):
        """Processes the wallet connection and key verification."""
        address = self.wallet.get().strip()
        private_key = self.key_entry.get().strip()

        if not address or not private_key:
            self.update_info("Address and Private Key are required!", "red")
            return

        # 1. Connect the address
        error_msg = self.controller.web3_service.connect_wallet(address)
        if error_msg:
            self.update_info(error_msg, "red")
            return

        # 2. Verify the private key matches the address
        # This is what sets 'self.key' in Web3Service for createRoom/connectToRoom
        success, message = self.controller.web3_service.check_wallet_connection(private_key)

        if success:
            try:
                # Fetch real-time balance from the network (testnet or mainnet)
                balance = self.controller.web3_service.get_balance_eth()
                
                # Navigate to GameScreen and pass dynamic info
                game_screen = self.controller.screens["GameScreen"]
                game_screen.update_wallet_info(
                    balance_eth=f"{balance:.4f}", 
                    game_price_eth="Variable (based on room)"
                )
                
                print(f"Connected to: {address}")
                self.controller.show_screen("GameScreen")
            except Exception as e:
                self.update_info(f"RPC Error: {str(e)}", "red")
        else:
            self.update_info(message, "red")

    def update_info(self, text, color="gray"):
        self.info_label.configure(text=text, text_color=color)