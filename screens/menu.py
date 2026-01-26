import tkinter as tk


class MenuScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        
        tk.Label(self, text="First test").pack(pady=10)
        
        
        tk.Button(self, text="Rejoindre une chambre",
        command=lambda: controller.show_screen("WalletScreen")).pack()
        
        
        tk.Button(self, text="Créer une chambre",
        command=lambda: controller.show_screen("WalletScreen")).pack()
        
        
        tk.Button(self, text="Random person",
        command=lambda: controller.show_screen("WalletScreen")).pack()
        
        
        tk.Button(self, text="I don’t have friends (Solo)",
        command=lambda: controller.show_screen("GameScreen")).pack(pady=10)