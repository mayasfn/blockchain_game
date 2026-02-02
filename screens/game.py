import customtkinter as ctk


class GameScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=20)
        self.controller = controller

        # Title
        ctk.CTkLabel(
            self,
            text="Guess the Number",
            font=("Arial", 22, "bold")
        ).pack(pady=(30, 10))

        # Wallet info frame
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(pady=10, padx=20, fill="x")

        self.balance_label = ctk.CTkLabel(
            info_frame, text="Balance: -- ETH"
        )
        self.balance_label.pack(anchor="w", padx=10, pady=5)

        self.price_label = ctk.CTkLabel(
            info_frame, text="Game price: 0.01 ETH"
        )
        self.price_label.pack(anchor="w", padx=10, pady=5)

        # Action buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20)

        ctk.CTkButton(
            button_frame,
            text="🎯 Guess the number",
            width=200,
            height=40,
            command=self.guess_number
        ).pack(pady=10)

        ctk.CTkButton(
            button_frame,
            text="🔢 Set the number",
            width=200,
            height=40,
            command=self.set_number
        ).pack(pady=10)

        # Back button
        ctk.CTkButton(
            self,
            text="Retour menu",
            fg_color="transparent",
            text_color="gray",
            command=lambda: controller.show_screen("MenuScreen"),
        ).pack(pady=20)

    # ----------------------------
    # Button callbacks
    # ----------------------------

    def guess_number(self):
        self.controller.web3_service.set_player(1)
        self.controller.screens["GuessScreen"].set_room_number(self.controller.web3_service.room)
        self.controller.show_screen("GuessScreen")

    def set_number(self):
        self.controller.web3_service.set_player(2)
        self.controller.screens["SetNumberScreen"].set_room_number(self.controller.web3_service.room)
        self.controller.show_screen("SetNumberScreen")

    # ----------------------------
    # Update info (called after wallet connect)
    # ----------------------------

    def update_wallet_info(self, balance_eth: str, game_price_eth: str):
        self.balance_label.configure(text=f"Balance: {balance_eth} ETH")
        self.price_label.configure(text=f"Game price: {game_price_eth} ETH")
