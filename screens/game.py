import tkinter as tk
from blockchain.logic import GuessGame


class GameScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.game = GuessGame()
        
        
        tk.Label(self, text="Devine le nombre (1-100)").pack(pady=10)
        
        
        self.entry = tk.Entry(self)
        self.entry.pack()
        
        
        self.result = tk.Label(self, text="")
        self.result.pack(pady=5)
        
        
        tk.Button(self, text="Valider", command=self.check).pack()
        tk.Button(self, text="Retour menu",
            command=lambda: controller.show_screen("MenuScreen")).pack(pady=10)
    
    
    def check(self):
        try:
            value = int(self.entry.get())
            msg = self.game.check(value)
            self.result.config(text=msg)
        except ValueError:
            self.result.config(text="Entre un nombre valide")