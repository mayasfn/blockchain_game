import tkinter as tk


class WalletScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        
        tk.Label(self, text="Wallet Address").pack(pady=5)
        self.wallet_entry = tk.Entry(self)
        self.wallet_entry.pack()
        
        
        tk.Label(self, text="Private Key (optionnel)").pack(pady=5)
        self.key_entry = tk.Entry(self, show="*")
        self.key_entry.pack()
        
        
        tk.Button(self, text="Continuer",
        command=lambda: controller.show_screen("GameScreen")).pack(pady=10)
        
        
        tk.Button(self, text="Retour menu",
        command=lambda: controller.show_screen("MenuScreen")).pack()