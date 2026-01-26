import tkinter as tk
from screens.menu import MenuScreen
from screens.game import GameScreen
from screens.wallet import WalletScreen


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Guess Game")
        self.geometry("400x300")
        
        
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        
        self.screens = {}
        for Screen in (MenuScreen, GameScreen, WalletScreen):
            screen = Screen(self.container, self)
            self.screens[Screen.__name__] = screen
            screen.grid(row=0, column=0, sticky="nsew")
        
        
        self.show_screen("MenuScreen")
    
    
    def show_screen(self, name):
        screen = self.screens[name]
        screen.tkraise()