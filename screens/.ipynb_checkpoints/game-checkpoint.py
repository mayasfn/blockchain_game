import customtkinter as ctk
from blockchain.logic import GuessGame


class GameScreen(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, corner_radius=20)
        self.controller = controller
        self.game = GuessGame()
        
        
        ctk.CTkLabel(
        self, text="Devine le nombre", font=("Arial", 22, "bold")).pack(pady=(40, 10))
        
        
        self.entry = ctk.CTkEntry(
        self, placeholder_text="Entre un nombre (1-100)", width=200, height=40)
        self.entry.pack(pady=10)
        
        
        self.result = ctk.CTkLabel(self, text="")
        self.result.pack(pady=10)
        
        
        ctk.CTkButton(self, text="Valider", command=self.check).pack(pady=5)
        
        
        ctk.CTkButton(self, text="Retour menu", fg_color="transparent", text_color="gray", command=lambda: controller.show_screen("MenuScreen")).pack(pady=20)
        
    
    def check(self):
        try:
            value = int(self.entry.get())
            self.result.configure(text=self.game.check(value))
        except ValueError:
            self.result.configure(text="Entre un nombre valide")